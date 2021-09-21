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
import itertools
import pathlib
import textwrap
import typing
from itertools import filterfalse

from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import delegateto

import mtg_proxy_printer.app_dirs
from mtg_proxy_printer.model.carddb_helpers import migrate_card_database
from mtg_proxy_printer.natsort import natural_sorted
import mtg_proxy_printer.sqlite_helpers
import mtg_proxy_printer.meta_data
import mtg_proxy_printer.settings
from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger

StringList = typing.List[str]
OptionalString = typing.Optional[str]
DEFAULT_DATABASE_LOCATION = pathlib.Path(
    mtg_proxy_printer.app_dirs.data_directories.user_cache_dir,
    "CardDataCache.sqlite3"
)

# The card data is mostly stable, Scryfall recommends fetching the card bulk data only in larger intervals, like
# once per month or so.
MINIMUM_REFRESH_DELAY = datetime.timedelta(days=14)

__all__ = [
    "CardIdentificationData",
    "MTGSet",
    "Card",
    "CardDatabase",
]


@dataclasses.dataclass
class CardIdentificationData:
    language: OptionalString = None
    name: OptionalString = None
    set_code: OptionalString = None
    collector_number: OptionalString = None
    scryfall_id: OptionalString = None
    is_front: typing.Optional[bool] = None


@dataclasses.dataclass(frozen=True)
class MTGSet:
    code: str
    name: str

    def data(self, role: int):
        """data getter used for Qt Model API based access"""
        if role == Qt.EditRole:
            return self.code
        elif role == Qt.DisplayRole:
            return f"{self.name} ({self.code.upper()})"
        elif role == Qt.ToolTipRole:
            return self.name
        else:
            return None


@dataclasses.dataclass(unsafe_hash=True)
class Card:
    name: str = dataclasses.field(compare=True)
    set: MTGSet = dataclasses.field(compare=True)
    collector_number: str = dataclasses.field(compare=True)
    language: str = dataclasses.field(compare=True)
    scryfall_id: str = dataclasses.field(compare=True)
    is_front: bool = dataclasses.field(compare=True)
    oracle_id: str = dataclasses.field(compare=True)
    image_uri: str = dataclasses.field(compare=False)
    highres_image: bool = dataclasses.field(compare=False)
    is_oversized: bool = dataclasses.field(compare=False)
    face_number: int = dataclasses.field(compare=False)
    image_file: typing.Optional[QPixmap] = dataclasses.field(default=None, compare=False)


OptionalCard = typing.Optional[Card]
CardList = typing.List[Card]


@delegateto.delegate("db", "commit", "rollback")
class CardDatabase:

    MIN_SUPPORTED_SQLITE_VERSION = (3, 31, 0)

    def __init__(self, db_path: typing.Union[str, pathlib.Path] = DEFAULT_DATABASE_LOCATION):
        logger.info(f"Creating {self.__class__.__name__} instance.")
        db = mtg_proxy_printer.sqlite_helpers.open_database(
            db_path, "carddb", self.MIN_SUPPORTED_SQLITE_VERSION, False)
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
            self.rollback()
            logger.debug("Running SQLite PRAGMA optimize.")
            # Running query planner optimization prior to closing the connection, as recommended by the SQLite devs.
            # See also: https://www.sqlite.org/lang_analyze.html
            self.db.execute("PRAGMA optimize")
            self.db.close()
            logger.info("Closed database.")

        atexit.register(close_db)
        self._exit_hook = close_db

    def begin_transaction(self):
        self.db.execute("BEGIN TRANSACTION")

    def check_if_download_settings_changed(self) -> bool:
        section = mtg_proxy_printer.settings.settings["downloads"]

        currently_disabled_settings = set(filterfalse(section.getboolean, section.keys()))
        database_disabled_settings = set(item for item, in self.db.execute(
            'SELECT setting FROM UsedDownloadSettings WHERE "value" = ?',
            (False,)
        ))
        result = currently_disabled_settings != database_disabled_settings
        logger.debug(
            f"Checked, if the current download filter settings differ from the previously used. Result: {result}")
        return result

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
            return allow_update or self.check_if_download_settings_changed()
        else:
            return True

    def get_all_languages(self) -> StringList:
        """Returns the list of all known languages, sorted ascending."""
        logger.debug("Reading all known languages")
        result = [lang for lang, in self.db.execute(
            "SELECT language FROM PrintLanguage ORDER BY language ASC -- get_all_languages()\n")]
        return result

    def get_card_names(self, language: str, card_name_filter: str = None) -> StringList:
        """Returns a list with all card names in the given language."""
        logger.debug(f'Finding matching card names for language "{language}" and name filter "{card_name_filter}"')
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

    def is_valid_and_unique_card(self, card: CardIdentificationData) -> bool:
        """Checks, if the given card data represents a unique card printing"""
        query = 'SELECT COUNT(*) = 1 AS is_unique -- is_valid_and_unique_card()\n' \
                'FROM CardFace\n' \
                'JOIN Printing USING (printing_id)\n' \
                'JOIN "Set" USING (set_id)\n' \
                'JOIN FaceName USING (face_name_id)\n' \
                'JOIN PrintLanguage USING (language_id)\n' \


        where_clause = 'WHERE "language" = ?\n'
        parameters = [card.language]
        if card.name:
            where_clause += 'AND card_name = ?\n'
            parameters.append(card.name)
        if card.set_code:
            where_clause += 'AND "set" = ?\n'
            parameters.append(card.set_code)
        if card.collector_number:
            where_clause += 'AND collector_number = ?\n'
            parameters.append(card.collector_number)
        if card.is_front is not None:
            where_clause += 'AND is_front = ?\n'
            parameters.append(card.is_front)
        query += where_clause
        result = self._read_optional_scalar_from_db(query, parameters)
        return bool(result)

    def get_cards_from_data(self, card: CardIdentificationData) -> CardList:
        """
        Called with some card identification data and returns all matching cards.
        Returns a list with Card objects, each containing complete information, except for the image pixmap.
        Returns an empty list, if the given data does not match any known card.
        """
        query = 'SELECT card_name, "set", set_name, collector_number, png_image_uri, scryfall_id, is_front, ' \
                'oracle_id, highres_image, is_oversized, face_number -- get_cards_from_data()\n' \
                'FROM CardFace\n' \
                'JOIN Printing USING (printing_id)\n' \
                'JOIN FaceName USING (face_name_id)\n' \
                'JOIN PrintLanguage USING (language_id)\n' \
                'JOIN "Set" USING (set_id)\n' \
                'JOIN Card USING (card_id)\n'

        where_clause = 'WHERE "language" = ?\n'
        parameters = [card.language]
        if card.name:
            where_clause += 'AND card_name = ?\n'
            parameters.append(card.name)
        if card.set_code:
            where_clause += 'AND "set" = ?\n'
            parameters.append(card.set_code)
        if card.collector_number:
            where_clause += 'AND collector_number = ?\n'
            parameters.append(card.collector_number)
        if card.is_front is not None:
            where_clause += 'AND is_front = ?\n'
            parameters.append(card.is_front)
        if card.scryfall_id:
            where_clause += 'AND scryfall_id = ?\n'
            parameters.append(card.scryfall_id)
        query += where_clause
        cursor = self.db.execute(
            query,
            parameters
        )
        result = [
            Card(
                name, MTGSet(set_code, set_name), collector_number,
                card.language, scryfall_id, bool(is_front), oracle_id, image_uri,
                highres_image, bool(is_oversized), face_number,
            )
            for name, set_code, set_name, collector_number, image_uri, scryfall_id, is_front, oracle_id, highres_image,
            is_oversized, face_number in cursor
        ]
        return result

    def find_collector_numbers_matching(self, card_name: str, set_abbr: str, language: str) -> StringList:
        """
        Finds all collector numbers matching the given filter. The result contains multiple elements, if the card
        had multiple variants with distinct collector numbers in the given set.

        :param card_name: Card name, matched exactly
        :param set_abbr: Set abbreviation, matched exactly
        :param language: Card language, matched exactly
        :return: Naturally sorted list of collector numbers, i.e. "2" before "10".
        """
        # Implementation note: DISTINCT is required for double-faced cards where both sides have the same name.
        # This can be art-series cards or double-faced tokens (e.g. from C16). Without this, selecting such card
        # in the AddCardWidget results in a duplicated entry in the collector number selection list.
        query = 'SELECT DISTINCT collector_number -- find_collector_numbers_matching()\n' \
                'FROM CardFace\n' \
                'JOIN Printing USING (printing_id)\n' \
                'JOIN FaceName USING (face_name_id)\n' \
                'JOIN PrintLanguage USING (language_id)\n' \
                'JOIN "Set" USING (set_id)\n' \
                'WHERE "language" = ?\n' \
                'AND "set" = ?\n' \
                'AND card_name = ?\n'
        return natural_sorted(item for item, in self.db.execute(query, (language, set_abbr, card_name)))

    def find_sets_matching(
            self, card_name: str, language: str, set_name_filter: str = None) -> typing.List[MTGSet]:
        """
        Finds all matching sets that the given card was printed in.

        :param card_name: Card name, matched exactly
        :param language: card language, matched exactly
        :param set_name_filter: If provided, only return sets with set code or full name beginning with this.
          Used as a LIKE pattern, supporting SQLite wildcards.
        :return: List of matching sets, as tuples (set_abbreviation, full_english_set_name)
        """
        query = 'SELECT DISTINCT "set", set_name  -- find_sets_matching()\n' \
                'FROM CardFace\n' \
                'JOIN Printing USING (printing_id)\n' \
                'JOIN "Set" USING (set_id)\n' \
                'JOIN FaceName USING (face_name_id)\n' \
                'JOIN PrintLanguage USING (language_id)\n' \
                'WHERE "language" = ?\n' \
                'AND card_name = ?\n'
        parameters = [language, card_name]
        if set_name_filter:
            query += 'AND ("set" LIKE ?\n' \
                     '    OR set_name LIKE ?)\n'
            parameters += [f"{set_name_filter}%"] * 2

        query += 'ORDER BY set_name ASC\n'
        return list(itertools.starmap(MTGSet, self.db.execute(query, parameters)))

    def is_scryfall_id_known(self, scryfall_id: str, is_front: bool) -> bool:
        query = 'SELECT EXISTS (' \
                'SELECT scryfall_id FROM Printing JOIN CardFace USING(printing_id) ' \
                'WHERE scryfall_id = ? AND is_front = ?)'
        result = self._read_optional_scalar_from_db(query, (scryfall_id, is_front))
        return bool(result)

    def get_card_with_scryfall_id(self, scryfall_id: str, is_front: bool) -> OptionalCard:
        query = 'SELECT card_name, set_code, set_name, collector_number, "language", png_image_uri, oracle_id, ' \
                'highres_image, is_oversized, face_number\n' \
                'FROM AllPrintings\n' \
                'WHERE scryfall_id = ? AND is_front = ?'
        result = self.db.execute(query, (scryfall_id, is_front)).fetchone()
        if result is None:
            return None
        else:
            name, set_abbr, set_name, collector_number, language, image_uri, oracle_id, highres_image,\
                is_oversized, face_number = result
            return Card(
                name, MTGSet(set_abbr, set_name), collector_number,
                language, scryfall_id, bool(is_front), oracle_id, image_uri,
                highres_image, bool(is_oversized), face_number
            )

    def get_opposing_face(self, card) -> OptionalCard:
        """
        Returns the opposing face for double faced cards, or None for single-faced cards.
        """
        other_side = not card.is_front
        if self.is_scryfall_id_known(card.scryfall_id, other_side):
            return self.get_card_with_scryfall_id(card.scryfall_id, other_side)
        else:
            return None

    def guess_language_from_name(self, name: str) -> typing.Optional[str]:
        """Guesses the card language from the card name. Returns None, if no result was found."""
        query = 'SELECT "language"\n' \
                'FROM FaceName\n' \
                'JOIN PrintLanguage USING (language_id)\n' \
                'WHERE card_name LIKE ?'
        return self._read_optional_scalar_from_db(query, (name,))

    def is_known_language(self, language: str) -> bool:
        """Returns true, if the given two-letter code is a known language. Returns False otherwise."""
        query = 'SELECT EXISTS(\n' \
                'SELECT *\n' \
                'FROM PrintLanguage\n' \
                'WHERE "language" = ?)'
        return bool(self._read_optional_scalar_from_db(query, (language,)))

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
        JOIN Printing USING (printing_id)
        JOIN Card USING (card_id)
        WHERE "language" = ?
        AND (oracle_id, face_number) IN (
            SELECT oracle_id, face_number
            FROM FaceName
            JOIN PrintLanguage USING(language_id)
            JOIN CardFace USING (face_name_id)
            JOIN Printing USING (printing_id)
            JOIN Card USING (card_id)
            WHERE card_name = ? AND "language" = ?
        )"""
        return self._read_optional_scalar_from_db(query, (target_language, name, source_language))

    def _read_optional_scalar_from_db(self, query: str, parameters: typing.Iterable[typing.Any]):
        if result := self.db.execute(query, parameters).fetchone():
            return result[0]
        else:
            return None

    def cards_not_used_since(self, keys: typing.List[typing.Tuple[str, bool]], date: datetime.date) -> typing.List[int]:
        """
        Filters the given list of card keys (tuple scryfall_id, is_front). Returns a new list containing the keys
        from the input list that correspond to cards that were not used since the given date.
        """
        query = textwrap.dedent("""
            SELECT last_use_date < ? AS last_use_was_before_threshold
            FROM LastImageUseTimestamps
            WHERE scryfall_id = ?
              AND is_front = ?""")
        cards_not_used_since = []
        for index, (scryfall_id, is_front) in enumerate(keys):
            result = self._read_optional_scalar_from_db(query, (date.isoformat(), scryfall_id, is_front))
            if result is None or result:
                cards_not_used_since.append(index)
        return cards_not_used_since

    def cards_used_less_often_then(self,  keys: typing.List[typing.Tuple[str, bool]], count: int) -> typing.List[int]:
        """
        Filters the given list of card keys (tuple scryfall_id, is_front). Returns a new list containing the keys
        from the input list that correspond to cards that are used less often than count.
        If count is zero or less, returns an empty list.
        """
        if count <= 0:
            return []
        query = textwrap.dedent("""
            SELECT NOT EXISTS (
              SELECT scryfall_id
              FROM LastImageUseTimestamps
              WHERE scryfall_id = ?
                AND is_front = ?
                AND usage_count >= ?
            ) AS hit""")
        result = []
        for index, (scryfall_id, is_front) in enumerate(keys):
            if self._read_optional_scalar_from_db(query, (scryfall_id, is_front, count)):
                result.append(index)
        return result

    def get_newest_card_date_in_database(self) -> datetime.date:
        """
        Returns the latest card timestamp from the LastDatabaseUpdate table.
        Returns today(), if the table is empty.
        """
        query = textwrap.dedent("""
            SELECT newest_card_timestamp
            FROM LastDatabaseUpdate
            WHERE update_id = (
              SELECT MAX(update_id)
              FROM LastDatabaseUpdate
            )""")
        result = [datetime.date.fromisoformat(date) for date, in self.db.execute(query)]
        if result:
            return result[0]
        else:
            return datetime.date.today()

    def translate_card(self, to_translate: Card, target_language: str = None) -> Card:
        """
        Returns a new card object representing the card translated into the target language.
        If no translation is available, or the target language is equal to the source language, returns the given
        card instance unaltered.
        """
        if target_language is None or target_language == to_translate.language:
            return to_translate
        if (result := self._translate_card(to_translate, target_language)) is not None:
            return result
        return to_translate

    def _translate_card(self, card: Card, language_override: str) -> OptionalCard:
        """
        Tries to translate the given card into the given language.
        If the card is not available in the requested language, None is returned.

        Uses the Oracle ID to identify all cards and returns the most similar card.
        """
        # Implementation note: This query contains the max() aggregate function and bare columns.
        # See https://sqlite.org/lang_select.html. In this case, the bare columns are taken from a row for which the
        # computed similarity is equal to the maximum similarity encountered. This avoids creating a B-Tree required
        # for the alternative "ORDER BY similarity DESC LIMIT 1"
        query = textwrap.dedent("""
            SELECT card_name, set_code, set_name, collector_number, scryfall_id, png_image_uri, highres_image,
              is_oversized, face_number, MAX((set_code = ?) + (collector_number = ?)) AS similarity
              FROM AllPrintings
              WHERE oracle_id = ? AND language = ? AND is_front = ?
            """)
        parameters = [card.set.code, card.collector_number, card.oracle_id, language_override, card.is_front]
        # Because of the aggregate function used, no hit will result in a single row consisting of only NULL values.
        result = self.db.execute(query, parameters).fetchone()
        name, set_code, set_name, collector_number, scryfall_id, image_uri, highres_image, \
            is_oversized, face_number, similarity = result
        if similarity is None:
            logger.debug(f"Found no translations to {language_override} for card '{card.name}'.")
            return None
        return Card(
            name, MTGSet(set_code, set_name), collector_number,
            language_override, scryfall_id, card.is_front, card.oracle_id, image_uri,
            highres_image, bool(is_oversized), face_number
        )

    def find_all_translated_printings(self, card: Card, language: str) -> CardList:
        """Returns all printings of the given card in the given language."""
        query = textwrap.dedent("""
            SELECT card_name, set_code, set_name, collector_number, scryfall_id, png_image_uri,
              highres_image, is_oversized, face_number
            FROM AllPrintings
            WHERE oracle_id = ? AND language = ? AND is_front = ?
        """)
        parameters = [card.oracle_id, language, card.is_front]
        result = [
            Card(
                name, MTGSet(set_code, set_name), collector_number,
                language, scryfall_id, card.is_front, card.oracle_id, image_uri,
                highres_image, bool(is_oversized), face_number
            )
            for name, set_code, set_name, collector_number, scryfall_id, image_uri,
                highres_image, is_oversized, face_number
            in self.db.execute(query, parameters)
        ]
        return result
