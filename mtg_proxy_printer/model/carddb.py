# Copyright (C) 2020, 2021 Thomas Hess <thomas.hess@udo.edu>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import atexit
import dataclasses
import datetime
import pathlib
import sqlite3
import textwrap
import typing

from PyQt5.QtGui import QPixmap

from mtg_proxy_printer.natsort import natural_sorted
import mtg_proxy_printer.sqlite_helpers
import mtg_proxy_printer.meta_data
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

StringList = typing.List[str]
OptionalString = typing.Optional[str]
DEFAULT_DATABASE_LOCATION = pathlib.Path(
    mtg_proxy_printer.meta_data.data_directories.user_cache_dir,
    "CardDataCache.sqlite3"
)

# The card data is mostly stable, Scryfall recommends fetching the card bulk data only in larger intervals, like
# once per month or so.
MINIMUM_REFRESH_DELAY = datetime.timedelta(days=14)

__all__ = [
    "Card",
    "CardDatabase",
    "clear_database"
]


@dataclasses.dataclass(unsafe_hash=True)
class Card:
    name: OptionalString
    set_abbr: OptionalString
    collector_number: OptionalString
    language: str
    is_front: typing.Optional[bool] = None
    image_uri: OptionalString = None
    scryfall_id: OptionalString = None
    image_file: typing.Optional[QPixmap] = None
    set_name: OptionalString = None


class CardDatabase:

    MIN_SUPPORTED_SQLITE_VERSION = (3, 31, 0)

    def __init__(self, db_path: typing.Union[str, pathlib.Path] = DEFAULT_DATABASE_LOCATION):
        logger.info(f"Creating {self.__class__.__name__} instance.")
        db = mtg_proxy_printer.sqlite_helpers.open_database(db_path, "carddb", self.MIN_SUPPORTED_SQLITE_VERSION)
        migrate_card_database(db)
        self.db = db
        self._exit_hook = None
        if db_path != ":memory:":
            self._register_exit_hook()

    def _register_exit_hook(self):
        logger.debug("Registering cleanup hooks that close the database on exit.")
        if self._exit_hook is not None:
            logger.debug("Unregister previously installed hook")
            atexit.unregister(self._exit_hook)

        def close_db():
            logger.debug("Rolling back active transactions.")
            self.db.rollback()
            logger.debug("Running SQLite PRAGMA optimize.")
            # Running query planner optimization prior to closing the connection, as recommended by the SQLite devs.
            # See also: https://www.sqlite.org/lang_analyze.html
            self.db.execute("PRAGMA optimize")
            self.db.close()
            logger.info("Closed database.")

        atexit.register(close_db)
        self._exit_hook = close_db

    def commit(self):
        self.db.commit()

    def has_data(self) -> bool:
        result, = self.db.execute("SELECT EXISTS(SELECT * FROM Card)\n").fetchone()
        return bool(result)

    def allow_updating_card_data(self) -> bool:
        query = "SELECT update_timestamp FROM LastDatabaseUpdate ORDER BY update_timestamp DESC LIMIT 1\n"
        if result := self.db.execute(query).fetchone():
            last_timestamp_str, = result
            last_timestamp = datetime.datetime.fromisoformat(last_timestamp_str).date()
            now = datetime.datetime.now().date()
            allow_update = (last_timestamp + MINIMUM_REFRESH_DELAY) <= now
            return allow_update
        else:
            return True

    def get_all_languages(self) -> StringList:
        result = [lang for (lang,) in self.db.execute(
            "SELECT language FROM PrintLanguage ORDER BY language ASC -- get_all_languages()\n")]
        return result

    def get_card_names(self, language: str, card_name_filter: str = None) -> StringList:
        """Returns a list with all card names in the given language."""
        query = r"""SELECT card_name -- get_card_names()
            FROM FaceName
            JOIN PrintLanguage USING (language_id)
            """
        where_clause = 'WHERE "language" = ?\n'
        order_clause = 'ORDER BY card_name ASC'
        parameters = [language]
        if card_name_filter:
            where_clause += 'AND card_name LIKE ?\n'
            parameters.append(f"{card_name_filter}%")
        query += where_clause + order_clause
        result = [
            language for language, in
            self.db.execute(
                query, parameters
            )
        ]
        return result

    def is_valid_and_unique_card(self, card: Card) -> bool:
        """Checks, if the given card data represents a unique card printing"""
        query = 'SELECT COUNT(*) = 1 AS is_unique -- is_valid_and_unique_card()\n' \
                'FROM CardFace\n' \
                'JOIN FaceName USING (face_name_id)\n' \
                'JOIN PrintLanguage USING (language_id)\n' \
                'JOIN "Set" USING (set_id)\n'

        where_clause = 'WHERE "language" = ?\n'
        parameters = [card.language]
        if card.name:
            where_clause += 'AND card_name = ?\n'
            parameters.append(card.name)
        if card.set_abbr:
            where_clause += 'AND "set" = ?\n'
            parameters.append(card.set_abbr)
        if card.collector_number:
            where_clause += 'AND collector_number = ?\n'
            parameters.append(card.collector_number)
        query += where_clause
        result, = self.db.execute(
            query,
            parameters
        ).fetchone()
        return bool(result)

    def add_missing_information(self, card: Card):
        """
        Called with a unique printing in card and
        fills in all missing information by modifying the Card object in-place.

        A unique card may be

        - A card name in the given language (if there were no re-prints or multiple printings in the same set)
        - A card name and collector number (if all re-prints have different numbers)
        - A card name and set (if there were no multiple printings in the same set)
        - Set, language and collector number
        - A collector number (if that is globally unique, because of some special character.
          Some online sets have thousands of cards, so the largest of these has a bunch
          of cards that can be uniquely identified by their large collector number.)
        - Language (some promo cards are one-of a kind and have a unique language,
          like a single card in traditional Greek)
        """
        query = 'SELECT card_name, "set", set_name, collector_number, png_image_uri, scryfall_id, is_front ' \
                '-- add_missing_information()\n' \
                'FROM CardFace\n' \
                'JOIN FaceName USING (face_name_id)\n' \
                'JOIN PrintLanguage USING (language_id)\n' \
                'JOIN "Set" USING (set_id)\n'

        where_clause = 'WHERE "language" = ?\n'
        parameters = [card.language]
        if card.name:
            where_clause += 'AND card_name = ?\n'
            parameters.append(card.name)
        if card.set_abbr:
            where_clause += 'AND "set" = ?\n'
            parameters.append(card.set_abbr)
        if card.collector_number:
            where_clause += 'AND collector_number = ?\n'
            parameters.append(card.collector_number)
        query += where_clause
        cursor = self.db.execute(
            query,
            parameters
        )
        result = cursor.fetchone()
        if not result or cursor.fetchone():
            raise RuntimeError(f"CardDatabase.add_missing_information() called on non-unique card information: {card}")
        card.name, card.set_abbr, card.set_name, card.collector_number, \
            card.image_uri, card.scryfall_id, card.is_front = result

    def find_collector_numbers_matching(self, card_name: str, set_abbr: str, language: str) -> StringList:
        """
        Finds all collector numbers matching the given card. The result contains multiple elements, if the card
        had multiple variants with distinct collector numbers in the given set.

        :param card_name: Card name, matched exactly
        :param set_abbr: Set abbreviation, matched exactly
        :param language: Card language, matched exactly
        :return: Naturally sorted list of collector numbers, i.e. "2" before "10".
        """
        query = 'SELECT collector_number -- find_collector_numbers_matching()\n' \
                'FROM CardFace\n' \
                'JOIN FaceName USING (face_name_id)\n' \
                'JOIN PrintLanguage USING (language_id)\n' \
                'JOIN "Set" USING (set_id)\n' \
                'WHERE "language" = ?\n' \
                'AND "set" = ?\n' \
                'AND card_name = ?\n'
        return natural_sorted(item for item, in self.db.execute(query, (language, set_abbr, card_name)))

    def find_sets_matching(
            self, card_name: str, language: str, set_name_filter: str = None) -> typing.List[typing.Tuple[str, str]]:
        """
        Finds all matching sets that the given card was printed in.

        :param card_name: Card name, matched exactly
        :param language: card language, matched exactly
        :param set_name_filter: If provided, only return sets with set code or full name beginning with this.
          Used as a LIKE pattern, supporting SQLite wildcards.
        :return: List of matching sets, as tuples (set_abbreviation, full_english_set_name)
        """
        query = 'SELECT DISTINCT "set", set_name  -- find_sets_matching()\n' \
                'FROM "Set"\n' \
                'JOIN CardFace USING (set_id)\n' \
                'JOIN FaceName USING (face_name_id)\n' \
                'JOIN PrintLanguage USING (language_id)\n' \
                'WHERE "language" = ?\n' \
                'AND card_name = ?\n'
        parameters = [language, card_name]
        if set_name_filter:
            query += 'AND ("set" LIKE ?\n' \
                     '    OR set_name LIKE ?\n)'
            parameters += [f"{set_name_filter}%"] * 2

        query += 'ORDER BY set_name ASC\n'
        return self.db.execute(query, parameters).fetchall()

    def is_scryfall_id_known(self, scryfall_id: str, is_front: bool) -> bool:
        query = 'SELECT EXISTS (SELECT scryfall_id FROM CardFace WHERE scryfall_id = ? and is_front = ?)'
        result, = self.db.execute(query, (scryfall_id, is_front)).fetchone()
        return bool(result)

    def get_card_with_scryfall_id(self, scryfall_id: str, is_front: bool) -> Card:
        query = 'SELECT card_name, "set", set_name, collector_number, "language", png_image_uri\n' \
                'FROM AllPrintings\n' \
                'WHERE scryfall_id = ? AND is_front = ?'
        name, set_abbr, set_name, collector_number, language, image_uri = self.db.execute(
            query, (scryfall_id, is_front)
        ).fetchone()
        return Card(name, set_abbr, collector_number, language, is_front, image_uri, scryfall_id, set_name=set_name)

    def get_opposing_face(self, card) -> typing.Optional[Card]:
        """
        Returns the opposing face for double faced cards, or None for single-faced cards.
        """
        other_side = not card.is_front
        if self.is_scryfall_id_known(card.scryfall_id, other_side):
            return self.get_card_with_scryfall_id(card.scryfall_id, other_side)
        else:
            return None

    def guess_language_from_name(self, name: str) -> typing.Optional[str]:
        query = 'SELECT "language"\n' \
                'FROM FaceName\n' \
                'JOIN PrintLanguage USING (language_id)\n' \
                'WHERE card_name LIKE ?'
        return self._read_optional_scalar_from_db(query, (f"{name}%",))

    def is_known_language(self, language: str) -> bool:
        query = 'SELECT EXISTS(\n' \
                'SELECT *\n' \
                'FROM PrintLanguage\n' \
                'WHERE "language" = ?)'
        return bool(self.db.execute(query, (language,)).fetchone()[0])

    def translate_card_name(self, name: str, target_language: str, source_language: str = None) -> OptionalString:
        """
        Translates a card from a source language into the target_language.
        If the source language is not given, try to guess it, or use English, if that also fails.

        :return: String with the translated card name, or None, if either unknown or unavailable in the target language.
        """
        # Implementation note: This approach using a subquery performs better than a
        # self-join of AllPrintings USING(oracle_id) for cards with many reprints, like basic lands.
        # On a populated database (of February 2021), using this query to translate a Forest to "de" takes 20ms,
        # while the self-join of AllPrintings takes full 6 seconds.
        if not source_language:
            source_language = self.guess_language_from_name(name) or "en"
        query = r"""SELECT DISTINCT card_name
        FROM FaceName
        JOIN PrintLanguage USING(language_id)
        JOIN CardFace USING (face_name_id)
        JOIN Card USING (card_id)
        WHERE "language" = ? 
        AND oracle_id IN (
            SELECT oracle_id
            FROM FaceName
            JOIN PrintLanguage USING(language_id)
            JOIN CardFace USING (face_name_id)
            JOIN Card USING (card_id)
            WHERE card_name = ? AND "language" = ?
        )"""
        return self._read_optional_scalar_from_db(query, (target_language, name, source_language))

    def _read_optional_scalar_from_db(self, query: str, parameters: typing.Iterable[typing.Any]):
        if result := self.db.execute(query, parameters).fetchone():
            return result[0]
        else:
            return None


def migrate_card_database(db: sqlite3.Connection):
    schema_version = db.execute("PRAGMA user_version").fetchone()[0]
    needs_update = mtg_proxy_printer.sqlite_helpers.check_database_schema_version(db, "carddb") > 0
    if db.execute("PRAGMA user_version").fetchone()[0] == 9:
        # It wasn’t stored if a card was a front or back face. This information can only be obtained by re-populating
        # the database using fresh data from Scryfall.
        db.execute("BEGIN TRANSACTION")
        clear_database(db)
        db.execute("ALTER TABLE CardFace ADD COLUMN is_front INTEGER NOT NULL CHECK (is_front IN (0, 1)) DEFAULT 1")
        db.execute("DROP VIEW AllPrintings")
        db.execute(textwrap.dedent(r"""
        CREATE VIEW AllPrintings AS
          SELECT card_name, "set", "language", collector_number, scryfall_id, highres_image, is_front, png_image_uri
          FROM CardFace
          JOIN FaceName USING(face_name_id)
          JOIN "Set" USING (set_id)
          JOIN Card USING (card_id)
          JOIN PrintLanguage USING(language_id)
        ;"""))
        db.commit()
        db.execute("PRAGMA user_version = 10")
    if db.execute("PRAGMA user_version").fetchone()[0] == 10:
        db.execute("BEGIN TRANSACTION")
        db.execute("DROP VIEW AllPrintings")
        db.execute(textwrap.dedent(r"""
        CREATE VIEW AllPrintings AS
          SELECT card_name, "set", set_name, "language", collector_number, scryfall_id, highres_image,
              is_front, png_image_uri, oracle_id
          FROM CardFace
          JOIN FaceName USING(face_name_id)
          JOIN "Set" USING (set_id)
          JOIN Card USING (card_id)
          JOIN PrintLanguage USING(language_id)
        ;"""))

        db.execute('CREATE INDEX CardFace_card_id_index ON CardFace (card_id)')
        db.commit()
        db.execute("PRAGMA user_version = 11")


def clear_database(db: sqlite3.Connection):
    """
    Clears all cards in the database. This allows re-populating with fresh data from Scryfall.
    This does not clear the LastDatabaseUpdate table to keep the history of performed updates.
    """
    # Implementation note: Specify all tables by hand, traversing the FOREIGN KEY constraint inducing DAG from
    # leaves to roots. This allows SQLite to possibly use the TRUNCATE optimization
    # (https://sqlite.org/lang_delete.html#the_truncate_optimization) and not spend a whole minute clearing
    # the tables in a way that doesn’t break foreign keys during the process.
    tables_to_clear = [
        "CardFace",
        "FaceName",
        "Card",
        '"Set"',
        "PrintLanguage",
    ]
    for table in tables_to_clear:
        db.execute(f"DELETE FROM {table}\n")
