# Copyright (C) 2020 Thomas Hess <thomas.hess@udo.edu>

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
import typing

from PyQt5.QtGui import QPixmap

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


@dataclasses.dataclass()
class Card:
    name: OptionalString
    set_abbr: OptionalString
    collector_number: OptionalString
    language: str
    is_front: typing.Optional[bool] = None
    image_uri: OptionalString = None
    scryfall_id: OptionalString = None
    image_file: typing.Optional[QPixmap] = None


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
        result: typing.Tuple[str] = self.db.execute(query).fetchone()
        if result:
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

    def get_card_names(self, language: str) -> StringList:
        """Returns a list with all card names in the given language."""
        query = self.db.execute(
            r"""SELECT card_name -- get_card_names()
            FROM FaceName
            JOIN PrintLanguage USING (language_id)
            WHERE language = ?
            ORDER BY card_name ASC
            """,
            (language,))
        result = [language for language, in query]
        return result

    def get_sets(self) -> StringList:
        """Returns a list with all set names."""
        query = self.db.execute(
            r"""SELECT "set"
            FROM "Set"
            """
        )
        result = [set_abbr for set_abbr, in query]
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
        query = 'SELECT card_name, "set", collector_number, png_image_uri, scryfall_id, is_front ' \
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
        card.name, card.set_abbr, card.collector_number, card.image_uri, card.scryfall_id, card.is_front = result

    def find_collector_numbers_matching(self, card: Card) -> StringList:
        query = 'SELECT DISTINCT collector_number -- find_collector_numbers_matching()\n' \
                'FROM CardFace\n' \
                'JOIN FaceName USING (face_name_id)\n' \
                'JOIN PrintLanguage USING (language_id)\n'
        join_clause = ''
        where_clause = 'WHERE "language" = ?\n'
        parameters = [card.language]
        if card.name:
            where_clause += 'AND card_name LIKE ?\n'
            parameters.append(f"{card.name}%")
        if card.set_abbr:
            join_clause += 'JOIN "Set" USING (set_id)\n'
            where_clause += 'AND "set" LIKE ?\n'
            parameters.append(f"{card.set_abbr}%")
        if card.collector_number:
            where_clause += 'AND collector_number LIKE ?\n'
            parameters.append(f"{card.collector_number}%")
        query += join_clause + where_clause
        query += """ORDER BY collector_number ASC\n"""
        cursor = self.db.execute(
            query,
            parameters
        )
        result = [number for number, in cursor]
        return result

    def find_card_names_matching(self, card: Card) -> StringList:
        """
        Finds all cards given the language, set name prefix and collector number prefix.

        :returns: List of card names
        """
        query = "SELECT DISTINCT card_name -- find_card_names_matching()\n" \
                "FROM FaceName\n" \
                "JOIN CardFace USING (face_name_id)\n" \
                "JOIN PrintLanguage USING (language_id)\n"
        join_clause = ''
        where_clause = 'WHERE "language" = ?\n'
        parameters = [card.language]
        if card.set_abbr:
            join_clause += 'JOIN "Set" USING (set_id)\n'
            where_clause += 'AND "set" LIKE ?\n'
            parameters.append(f"{card.set_abbr}%")
        if card.collector_number:
            where_clause += 'AND collector_number LIKE ?\n'
            parameters.append(f"{card.collector_number}%")
        query += join_clause + where_clause
        query += "ORDER BY card_name ASC\n"
        try:
            cursor = self.db.execute(
                query,
                parameters
            )
        except sqlite3.OperationalError:
            print("JOIN-CLAUSE:")
            print(join_clause)
            print("WHERE-CLAUSE:")
            print(where_clause)
            print(query)
            raise
        result = [name for name, in cursor]
        return result

    def find_sets_matching(self, card: Card) -> StringList:
        """
        Finds all sets given the language, card name prefix and collector number prefix
        """
        query = 'SELECT DISTINCT "set" -- find_sets_matching()\n' \
                'FROM "Set"\n' \
                'JOIN CardFace USING (set_id)\n' \
                'JOIN FaceName USING (face_name_id)\n' \
                'JOIN PrintLanguage USING (language_id)\n'
        where_clause = 'WHERE "language" = ?\n'
        parameters = [card.language]
        if card.name:
            where_clause += 'AND card_name LIKE ?\n'
            parameters.append(f"{card.name}%")
        if card.set_abbr:
            where_clause += 'AND "set" LIKE ?\n'
            parameters.append(f"{card.set_abbr}%")
        if card.collector_number:
            where_clause += 'AND collector_number LIKE ?\n'
            parameters.append(f"{card.collector_number}%")
        query += where_clause + 'ORDER BY "set" ASC\n'
        cursor = self.db.execute(
            query,
            parameters
        )
        result = [set_abbr for set_abbr, in cursor]
        return result

    def is_scryfall_id_known(self, scryfall_id: str, is_front: bool) -> bool:
        query = 'SELECT EXISTS (SELECT scryfall_id FROM CardFace WHERE scryfall_id = ? and is_front = ?)'
        result, = self.db.execute(query, (scryfall_id, is_front)).fetchone()
        return bool(result)

    def get_card_with_scryfall_id(self, scryfall_id: str, is_front: bool) -> Card:
        query = 'SELECT card_name, "set", collector_number, "language", png_image_uri\n' \
                'FROM AllPrintings\n' \
                'WHERE scryfall_id = ? AND is_front = ?'
        name, set_abbr, collector_number, language, image_uri = self.db.execute(
            query, (scryfall_id, is_front)
        ).fetchone()
        return Card(name, set_abbr, collector_number, language, is_front, image_uri, scryfall_id)


def migrate_card_database(db: sqlite3.Connection):
    if db.execute("PRAGMA user_version").fetchone()[0] == 9:
        # It wasn’t stored if a card was a front or back face. This information can only be obtained by re-populating
        # the database using fresh data from Scryfall.
        clear_database(db)
        db.execute("ALTER TABLE CardFace ADD COLUMN is_front INTEGER NOT NULL CHECK (is_front IN (0, 1)) DEFAULT 1")
        db.execute("PRAGMA user_version = ?", (10,))


def clear_database(db: sqlite3.Connection):
    """
    Clears all cards in the database. This allows re-populating with fresh data from Scryfall.
    This does not clear the LastDatabaseUpdate table to keep the history of performed updates.
    """
    # Implementation note: Specify all tables by hand, traversing the FOREIGN KEY constraint inducing DAG from
    # leaves to roots. This allows SQLite to use the TRUNCATE optimization
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
