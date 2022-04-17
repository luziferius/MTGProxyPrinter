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
import configparser
import dataclasses
import datetime
import itertools
import functools
import pathlib
import textwrap
import typing

from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import delegateto

import mtg_proxy_printer.app_dirs
from mtg_proxy_printer.model.carddb_migrations import migrate_card_database
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

try:
    # Profiling decorator, injected into globals by line-profiler. Because the injection does funky stuff, this
    # is the easiest way to test if the profile() function is defined.
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    profile
except NameError:
    # If not defined, use this identity decorator as a replacement
    def profile(func):
        return func


# The card data is mostly stable, Scryfall recommends fetching the card bulk data only in larger intervals, like
# once per month or so.
MINIMUM_REFRESH_DELAY = datetime.timedelta(days=14)

__all__ = [
    "CardIdentificationData",
    "MTGSet",
    "Card",
    "CardDatabase",
    "cached_dedent",
]


@dataclasses.dataclass
class CardIdentificationData:
    language: OptionalString = None
    name: OptionalString = None
    set_code: OptionalString = None
    collector_number: OptionalString = None
    scryfall_id: OptionalString = None
    is_front: typing.Optional[bool] = None
    oracle_id: OptionalString = None


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


@functools.lru_cache(None)
def cached_dedent(text: str):
    """Wraps textwrap.dedent() in an LRU cache."""
    return textwrap.dedent(text)


@delegateto.delegate("db", "commit", "rollback")
class CardDatabase:
    """
    Holds the connection to the local SQLite database that contains the relevant card data.
    Provides methods for data access.
    """
    MIN_SUPPORTED_SQLITE_VERSION = (3, 35, 0)

    def __init__(self, db_path: typing.Union[str, pathlib.Path] = DEFAULT_DATABASE_LOCATION):
        """
        :param db_path: Path to the database file. May be “:memory:” to create an in-memory database for testing
            purposes.
        """
        logger.info(f"Creating {self.__class__.__name__} instance.")
        db = mtg_proxy_printer.sqlite_helpers.open_database(
            db_path, "carddb", self.MIN_SUPPORTED_SQLITE_VERSION, False)
        migrate_card_database(db)
        self.db = db
        self._exit_hook = None
        if db_path != ":memory:":
            self._register_exit_hook()
        self.store_current_printing_filters()

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

    def has_data(self) -> bool:
        result, = self.db.execute("SELECT EXISTS(SELECT * FROM Card)\n").fetchone()
        return bool(result)

    def allow_updating_card_data(self) -> bool:
        """
        Returns True, if it should be allowed to update the internal card database, False otherwise.
        This is determined by the timestamp of the last database update performed.
        If the database is empty, downloading the card data is always allowed.
        """
        # The MAX aggregate returns NULL on an empty database. So use a timestamp in 1970 to return True then.
        query = "SELECT COALESCE(MAX(update_timestamp), '1970-01-01 00:00:00') FROM LastDatabaseUpdate\n"
        result, = self.db.execute(query).fetchone()
        last_timestamp = datetime.datetime.fromisoformat(result).date()
        allow_update = (last_timestamp + MINIMUM_REFRESH_DELAY) <= datetime.date.today()
        return allow_update

    @profile
    def get_all_languages(self) -> StringList:
        """Returns the list of all known and visible languages, sorted ascending."""
        logger.debug("Reading all known languages")
        result = [lang for lang, in self.db.execute(cached_dedent('''\
        SELECT language -- get_all_languages()
            FROM PrintLanguage
            ORDER BY language ASC
        '''))]
        return result

    @profile
    def get_card_names(self, language: str, card_name_filter: str = None) -> StringList:
        """Returns a list with all card names in the given language."""
        logger.debug(f'Finding matching card names for language "{language}" and name filter "{card_name_filter}"')
        query = cached_dedent('''\
        SELECT card_name
            FROM FaceName
            JOIN PrintLanguage USING (language_id)
            WHERE FaceName.is_hidden IS FALSE
              AND language = ?
              {name_filter}
            GROUP BY card_name
            ORDER BY card_name ASC
        ''')
        parameters = [language]
        if card_name_filter:
            query = query.format(name_filter='AND card_name LIKE ?')
            parameters.append(f"{card_name_filter}%")
        else:
            query = query.format(name_filter='')
        result = [
            language for language, in
            self.db.execute(
                query, parameters
            )
        ]
        return result

    @profile
    def is_valid_and_unique_card(self, card: CardIdentificationData) -> bool:
        """Checks, if the given card data represents a unique card printing"""
        query = cached_dedent('''\
        SELECT COUNT(*) = 1 AS is_unique -- is_valid_and_unique_card()
            FROM CardFace
            JOIN Printing USING (printing_id)
            JOIN "Set" USING (set_id)
            JOIN FaceName USING (face_name_id)
            JOIN PrintLanguage USING (language_id)
            WHERE Printing.is_hidden IS FALSE
        ''')

        where_clause = '    AND "language" = ?\n'
        parameters = [card.language]
        if card.name:
            where_clause += '    AND card_name = ?\n'
            parameters.append(card.name)
        if card.set_code:
            where_clause += '    AND "set" = ?\n'
            parameters.append(card.set_code)
        if card.collector_number:
            where_clause += '    AND collector_number = ?\n'
            parameters.append(card.collector_number)
        if card.is_front is not None:
            where_clause += '    AND is_front = ?\n'
            parameters.append(card.is_front)
        query += where_clause
        result = self._read_optional_scalar_from_db(query, parameters)
        return bool(result)

    @profile
    def get_cards_from_data(self, card: CardIdentificationData, /, *, order_by_print_count: bool = False) -> CardList:
        """
        Called with some card identification data and returns all matching cards.
        Returns a list with Card objects, each containing complete information, except for the image pixmap.
        Returns an empty list, if the given data does not match any known card.

         :param card: card identification data container that contains values to find cards
         :param order_by_print_count: Enable sorting the result list by the recorded print count. Defaults to False
        """
        query = cached_dedent('''\
        SELECT card_name, "set", set_name, collector_number, png_image_uri, scryfall_id, is_front,
                oracle_id, highres_image, is_oversized, face_number, language -- get_cards_from_data()
            FROM CardFace
            JOIN Printing USING (printing_id)
            JOIN FaceName USING (face_name_id)
            JOIN PrintLanguage USING (language_id)
            JOIN "Set" USING (set_id)
            JOIN Card USING (card_id)
        ''')
        if order_by_print_count:
            query += '    LEFT OUTER JOIN LastImageUseTimestamps USING (scryfall_id, is_front)\n'
        where_clause = ['WHERE Printing.is_hidden IS FALSE']
        where_parameters = []
        if card.language:
            where_clause.append(f'AND "language" = ?')
            where_parameters.append(card.language)
        if card.name:
            where_clause.append(f'AND card_name = ?')
            where_parameters.append(card.name)
        if card.set_code:
            where_clause.append(f'AND "set" = ?')
            where_parameters.append(card.set_code)
        if card.collector_number:
            where_clause.append(f'AND collector_number = ?')
            where_parameters.append(card.collector_number)
        if card.is_front is not None:
            where_clause.append(f'AND is_front = ?')
            where_parameters.append(card.is_front)
        if card.scryfall_id:
            where_clause.append(f'AND scryfall_id = ?')
            where_parameters.append(card.scryfall_id)
        if card.oracle_id:
            where_clause.append(f'AND oracle_id = ?')
            where_parameters.append(card.oracle_id)
        where_clause.append("")  # Insert final newline after joining
        query += "\n    ".join(where_clause)
        if order_by_print_count:
            query += 'ORDER BY LastImageUseTimestamps.usage_count DESC NULLS LAST\n'
        result = self._get_cards_from_data(query, where_parameters)
        return result

    @profile
    def get_replacement_card_for_unknown_printing(
            self, card: CardIdentificationData, /, *, order_by_print_count: bool = False):
        preferred_language = mtg_proxy_printer.settings.settings["images"]["preferred-language"]
        query = cached_dedent('''\
        SELECT card_name, set_code, set_name, collector_number, png_image_uri,
               AllPrintings.scryfall_id, is_front, oracle_id, highres_image,
               is_oversized, face_number, AllPrintings.language -- get_replacement_card_for_unknown_printing()
            FROM RemovedPrintings
            JOIN AllPrintings USING (oracle_id)
            LEFT OUTER JOIN LastImageUseTimestamps USING (scryfall_id, is_front)
            WHERE RemovedPrintings.scryfall_id = ?
            AND is_front = ?
            ORDER BY 
                -- Match with original language first, fall back to preferred language, then fall back to English
               (4*(AllPrintings.language == RemovedPrintings.language) +
                2*(AllPrintings.language == ?) +
                  (AllPrintings.language == 'en')) DESC NULLS LAST
        ''')
        if order_by_print_count:
            query += '        , LastImageUseTimestamps.usage_count DESC NULLS LAST\n'
        # Break any remaining ties by preferring high resolution images over low resolution images
        query += '        , AllPrintings.highres_image DESC\n'
        return self._get_cards_from_data(query, [card.scryfall_id, card.is_front, preferred_language])

    @profile
    def _get_cards_from_data(self, query, parameters):
        cursor = self.db.execute(query, parameters)
        result = [
            Card(
                name, MTGSet(set_code, set_name), collector_number,
                language, scryfall_id, bool(is_front), oracle_id, image_uri,
                bool(highres_image), bool(is_oversized), face_number,
            )
            for name, set_code, set_name, collector_number, image_uri, scryfall_id, is_front, oracle_id, highres_image,
                is_oversized, face_number, language in cursor
        ]
        return result

    @profile
    def find_collector_numbers_matching(self, card_name: str, set_abbr: str, language: str) -> StringList:
        """
        Finds all collector numbers matching the given filter. The result contains multiple elements, if the card
        had multiple variants with distinct collector numbers in the given set.

        :param card_name: Card name, matched exactly
        :param set_abbr: Set abbreviation, matched exactly
        :param language: Card language, matched exactly
        :return: Naturally sorted list of collector numbers, i.e. ["2", "10"]
        """
        # Implementation note: DISTINCT is required for double-faced cards where both sides have the same name.
        # This can be art-series cards or double-faced tokens (e.g. from C16). Without this, selecting such card
        # in the AddCardWidget results in a duplicated entry in the collector number selection list.
        query = cached_dedent('''\
        SELECT DISTINCT collector_number -- find_collector_numbers_matching()
            FROM CardFace
            JOIN Printing USING (printing_id)
            JOIN FaceName USING (face_name_id)
            JOIN PrintLanguage USING (language_id)
            JOIN "Set" USING (set_id)
            WHERE Printing.is_hidden IS FALSE
              AND FaceName.is_hidden IS FALSE
              AND "language" = ?
              AND "set" = ?
              AND card_name = ?
        ''')
        return natural_sorted(item for item, in self.db.execute(query, (language, set_abbr, card_name)))

    @profile
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
        query = cached_dedent('''\
        SELECT DISTINCT "set", set_name  -- find_sets_matching()
            FROM CardFace
            JOIN Printing USING (printing_id)
            JOIN "Set" USING (set_id)
            JOIN FaceName USING (face_name_id)
            JOIN PrintLanguage USING (language_id)
            WHERE Printing.is_hidden IS FALSE
              AND FaceName.is_hidden IS FALSE
              AND "language" = ?
              AND card_name = ?
        ''')
        parameters = [language, card_name]
        if set_name_filter:
            query += '      AND ("set" LIKE ? OR set_name LIKE ?)\n'
            parameters += [f"{set_name_filter}%"] * 2

        query += '    ORDER BY set_name ASC\n'
        return list(itertools.starmap(MTGSet, self.db.execute(query, parameters)))

    @profile
    def is_scryfall_id_known(self, scryfall_id: str, is_front: bool) -> bool:
        query = cached_dedent('''\
        SELECT EXISTS ( -- is_scryfall_id_known()
            SELECT scryfall_id
            FROM Printing 
            JOIN CardFace USING (printing_id)
            WHERE Printing.is_hidden IS FALSE
              AND scryfall_id = ?
              AND is_front = ?)
        ''')
        result = self._read_optional_scalar_from_db(query, (scryfall_id, is_front))
        return bool(result)

    @profile
    def get_card_with_scryfall_id(self, scryfall_id: str, is_front: bool) -> OptionalCard:
        query = cached_dedent('''\
        SELECT card_name, set_code, set_name, collector_number, "language", png_image_uri, oracle_id,
            highres_image, is_oversized, face_number -- get_card_with_scryfall_id()
            FROM AllPrintings
            WHERE scryfall_id = ? AND is_front = ?
        ''')
        result = self.db.execute(query, (scryfall_id, is_front)).fetchone()
        if result is None:
            return None
        else:
            name, set_abbr, set_name, collector_number, language, image_uri, oracle_id, highres_image,\
                is_oversized, face_number = result
            return Card(
                name, MTGSet(set_abbr, set_name), collector_number,
                language, scryfall_id, bool(is_front), oracle_id, image_uri,
                bool(highres_image), bool(is_oversized), face_number
            )

    @profile
    def get_opposing_face(self, card) -> OptionalCard:
        """
        Returns the opposing face for double faced cards, or None for single-faced cards.
        """
        return self.get_card_with_scryfall_id(card.scryfall_id, not card.is_front)

    @profile
    def guess_language_from_name(self, name: str) -> typing.Optional[str]:
        """Guesses the card language from the card name. Returns None, if no result was found."""
        query = cached_dedent('''\
        SELECT "language" -- guess_language_from_name()
            FROM FaceName
            JOIN PrintLanguage USING (language_id)
            WHERE card_name LIKE ?
        ''')
        return self._read_optional_scalar_from_db(query, (name,))

    @profile
    def is_known_language(self, language: str) -> bool:
        """Returns true, if the given two-letter code is a known language. Returns False otherwise."""
        query = cached_dedent('''
        SELECT EXISTS( -- is_known_language()
            SELECT *
            FROM PrintLanguage
            WHERE "language" = ?
        )
        ''')
        return bool(self._read_optional_scalar_from_db(query, (language,)))

    @profile
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
        query = cached_dedent("""\
        SELECT DISTINCT card_name -- translate_card_name()
            FROM FaceName
            JOIN PrintLanguage USING (language_id)
            JOIN CardFace USING (face_name_id)
            JOIN Printing USING (printing_id)
            JOIN Card USING (card_id)
            WHERE Printing.is_hidden IS FALSE
              AND FaceName.is_hidden IS FALSE
              AND "language" = ?
              AND (oracle_id, face_number) IN (
                SELECT oracle_id, face_number
                FROM FaceName
                JOIN PrintLanguage USING(language_id)
                JOIN CardFace USING (face_name_id)
                JOIN Printing USING (printing_id)
                JOIN Card USING (card_id)
                WHERE card_name = ? AND "language" = ?
                LIMIT 1
            )
        """)
        return self._read_optional_scalar_from_db(query, (target_language, name, source_language))

    def _read_optional_scalar_from_db(self, query: str, parameters: typing.Iterable[typing.Any]):
        if result := self.db.execute(query, parameters).fetchone():
            return result[0]
        else:
            return None

    @profile
    def is_removed_printing(self, scryfall_id: str) -> OptionalString:
        logger.debug(f"Query RemovedPrintings table for scryfall id {scryfall_id}")
        parameters = scryfall_id,
        query = cached_dedent("""\
        SELECT oracle_id
            FROM RemovedPrintings
            WHERE scryfall_id = ?
        """)
        return self._read_optional_scalar_from_db(query, parameters)

    @profile
    def cards_not_used_since(self, keys: typing.List[typing.Tuple[str, bool]], date: datetime.date) -> typing.List[int]:
        """
        Filters the given list of card keys (tuple scryfall_id, is_front). Returns a new list containing the indices
        into the input list that correspond to cards that were not used since the given date.
        """
        query = cached_dedent("""\
        SELECT last_use_date < ? AS last_use_was_before_threshold -- cards_not_used_since()
            FROM LastImageUseTimestamps
            WHERE scryfall_id = ?
              AND is_front = ?
        """)
        cards_not_used_since = []
        for index, (scryfall_id, is_front) in enumerate(keys):
            result = self._read_optional_scalar_from_db(query, (date.isoformat(), scryfall_id, is_front))
            if result is None or result:
                cards_not_used_since.append(index)
        return cards_not_used_since

    @profile
    def cards_used_less_often_then(self,  keys: typing.List[typing.Tuple[str, bool]], count: int) -> typing.List[int]:
        """
        Filters the given list of card keys (tuple scryfall_id, is_front). Returns a new list containing the indices
        into the input list that correspond to cards that are used less often than the given count.
        If count is zero or less, returns an empty list.
        """
        if count <= 0:
            return []
        query = cached_dedent("""\
        SELECT NOT EXISTS ( -- cards_used_less_often_then()
            SELECT scryfall_id
            FROM LastImageUseTimestamps
            WHERE scryfall_id = ?
              AND is_front = ?
              AND usage_count >= ?
            ) AS hit
        """)
        result = []
        for index, (scryfall_id, is_front) in enumerate(keys):
            if self._read_optional_scalar_from_db(query, (scryfall_id, is_front, count)):
                result.append(index)
        return result

    def get_total_cards_in_last_update(self) -> int:
        """
        Returns the latest card timestamp from the LastDatabaseUpdate table.
        Returns today(), if the table is empty.
        """
        query = cached_dedent("""\
        SELECT MAX(update_id), reported_card_count -- get_total_cards_in_last_update()
            FROM LastDatabaseUpdate
        """)
        id_, total_cards_in_last_update = self.db.execute(query).fetchone()
        return 0 if id_ is None else total_cards_in_last_update

    def translate_card(self, to_translate: Card, target_language: str = None) -> Card:
        """
        Returns a new card object representing the card translated into the target language.

        The translation step tries to be as faithful as possible to the original printing by matching as many
        properties as possible, but may have to choose a printing another Magic set, if the source set does not
        contain the card in the desired language. For example, translating an Alpha printing of a card will always
        yield a Card in a different set. Also, multi-language support for printings of promotional cards in the Scryfall
        database is limited.

        If no translation is available, or the target language is equal to the source language, returns the given
        card instance unaltered.
        """
        if target_language is None or target_language == to_translate.language:
            return to_translate
        if (result := self._translate_card(to_translate, target_language)) is not None:
            return result
        return to_translate

    @profile
    def _translate_card(self, card: Card, language_override: str) -> OptionalCard:
        """
        Tries to translate the given card into the given language.
        If the card is not available in the requested language, None is returned.

        Uses the Oracle ID to identify all cards and returns the most similar card.
        """
        # Implementation note: This query contains the max() aggregate function and bare columns.
        # See https://sqlite.org/lang_select.html. In this case, the bare columns are taken from a row for which the
        # computed similarity is equal to the maximum similarity encountered. This avoids creating a B-Tree required
        # for the alternative, appending a clause like "ORDER BY similarity DESC LIMIT 1"
        # This was chosen as a performance optimization,
        # because card translation can take considerable time during a deck list import.
        query = cached_dedent("""\
        SELECT card_name, set_code, set_name, collector_number, -- _translate_card()
               scryfall_id, png_image_uri, highres_image,
               is_oversized, face_number,
               MAX((set_code = ?) + (collector_number = ?)) AS similarity
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
            bool(highres_image), bool(is_oversized), face_number
        )

    @profile
    def find_all_translated_printings(
            self, card: Card, language: str, /, *, order_by_print_count: bool = False) -> CardList:
        """Returns all printings of the given card in the given language."""
        query = cached_dedent("""\
        SELECT card_name, set_code, set_name, collector_number, scryfall_id, png_image_uri,
               highres_image, is_oversized, face_number -- find_all_translated_printings()
            FROM AllPrintings
            {join_clause}
            WHERE oracle_id = ? AND language = ? AND is_front = ?
            {order_by_clause}
        """)
        if order_by_print_count:
            join_clause = "LEFT OUTER JOIN LastImageUseTimestamps USING (scryfall_id, is_front)"
            order_by_clause = "ORDER BY LastImageUseTimestamps.usage_count DESC NULLS LAST"
        else:
            join_clause = order_by_clause = ""
        # format in both cases to always replace the format specifiers
        query = query.format(join_clause=join_clause, order_by_clause=order_by_clause)
        parameters = [card.oracle_id, language, card.is_front]
        result = [
            Card(
                name, MTGSet(set_code, set_name), collector_number,
                language, scryfall_id, card.is_front, card.oracle_id, image_uri,
                bool(highres_image), bool(is_oversized), face_number
            )
            for name, set_code, set_name, collector_number, scryfall_id, image_uri,
            highres_image, is_oversized, face_number
            in self.db.execute(query, parameters)
        ]
        return result

    @profile
    def store_current_printing_filters(self, use_transaction: bool = True, *, force_update_hidden_column: bool = False):
        section = mtg_proxy_printer.settings.settings["downloads"]
        if use_transaction:
            self.db.execute("BEGIN TRANSACTION;\n")
        old_filter_removed = self._remove_old_printing_filters(section)
        filters_need_update = self._filters_in_db_differ_from_settings(section)
        if filters_need_update:
            logger.info("Printing filters changed in the settings, update the database.")
            self.db.executemany(
                cached_dedent("""\
                    INSERT INTO DisplayFilters (filter_name, filter_active)
                      VALUES (?, ?)
                      ON CONFLICT (filter_name) DO UPDATE
                        SET filter_active = excluded.filter_active
                        WHERE filter_active <> excluded.filter_active
                    """),
                ((key, not section.getboolean(key)) for key in section.keys())  # TODO: Invert storage logic, remove not
            )
        if filters_need_update or old_filter_removed or force_update_hidden_column:
            self._update_printing_is_hidden_column()
        if use_transaction:
            self.db.commit()

    def _filters_in_db_differ_from_settings(self, section: configparser.SectionProxy) -> bool:
        filters_in_db: typing.Dict[str, bool] = {
            key: bool(value) for key, value
            in self.db.execute("SELECT filter_name, filter_active FROM DisplayFilters").fetchall()
        }
        # TODO: Invert storage logic, remove not below
        filters_in_settings: typing.Dict[str, bool] = {key: not section.getboolean(key) for key in section.keys()}
        return filters_in_settings != filters_in_db

    @profile
    def _remove_old_printing_filters(self, section) -> bool:
        stored_filters = {
            filter_name for filter_name, in self.db.execute("SELECT filter_name FROM DisplayFilters").fetchall()
        }
        known_filters = set(section.keys())
        old_filters = stored_filters - known_filters
        if old_filters:
            logger.info(f"Removing old printing filters from the database: {old_filters}")
            self.db.executemany(
                "DELETE FROM DisplayFilters WHERE filter_name = ?",
                ((filter_name,) for filter_name in old_filters)
            )
        return bool(old_filters)

    @profile
    def _update_printing_is_hidden_column(self):
        logger.debug("Update the Printing.is_hidden column")
        self.db.execute(cached_dedent("""\
        UPDATE Printing
            SET is_hidden = HiddenPrintings.should_be_hidden
            FROM HiddenPrintings
            WHERE Printing.printing_id = HiddenPrintings.printing_id
              AND Printing.is_hidden <> HiddenPrintings.should_be_hidden
        ;
        """))
        logger.debug("Update the FaceName.is_hidden column")
        self.db.execute(cached_dedent("""\
        WITH FaceNameShouldBeHidden (face_name_id, should_be_hidden) AS (
          -- A FaceName should be hidden, iff all uses by printings are hidden,
          -- i.e. the total use count is equal to the hidden use count
          SELECT face_name_id, COUNT() = sum(Printing.is_hidden) AS should_be_hidden
          FROM Printing
          JOIN CardFace USING (printing_id)
          JOIN FaceName USING (face_name_id)
          GROUP BY card_name, language_id
        )
        UPDATE FaceName
          SET is_hidden = FaceNameShouldBeHidden.should_be_hidden
          FROM FaceNameShouldBeHidden
          WHERE FaceName.face_name_id = FaceNameShouldBeHidden.face_name_id
          AND FaceName.is_hidden <> FaceNameShouldBeHidden.should_be_hidden
        ;
        """))
