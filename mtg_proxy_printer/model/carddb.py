#  Copyright © 2020-2025  Thomas Hess <thomas.hess@udo.edu>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.


import atexit
import dataclasses
import datetime
from itertools import starmap
import functools
from pathlib import Path
import sqlite3
import threading
try:
    from typing import LiteralString
except ImportError:
    from typing_extensions import LiteralString
from typing import NamedTuple, TypeVar, Set, Optional, Dict, Literal, List, Sequence, Any, Union, Tuple

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal as Signal, pyqtSlot as Slot

from mtg_proxy_printer.model.card import MTGSet, Card, CheckCard, OptionalCard, CardList, CustomCard
from mtg_proxy_printer.model.imagedb_files import CacheContent
import mtg_proxy_printer.app_dirs
from mtg_proxy_printer.natsort import natural_sorted
import mtg_proxy_printer.meta_data
from mtg_proxy_printer.sqlite_helpers import cached_dedent, open_database, validate_database_schema
import mtg_proxy_printer.settings
from mtg_proxy_printer.units_and_sizes import StringList, OptStr, CardSizes, CardSize, UUID
from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger

OLD_DATABASE_LOCATION = mtg_proxy_printer.app_dirs.data_directories.user_cache_path / "CardDataCache.sqlite3"
DEFAULT_DATABASE_LOCATION = mtg_proxy_printer.app_dirs.data_directories.user_data_path / "CardDatabase.sqlite3"
SCHEMA_NAME = "carddb"
# The card data is mostly stable, Scryfall recommends fetching the card bulk data only in larger intervals, like
# once per month or so.
MINIMUM_REFRESH_DELAY = datetime.timedelta(days=14)
T = TypeVar("T", Card, CheckCard, CustomCard)
ParameterList = List[Union[str, bool]]
write_semaphore = threading.BoundedSemaphore()

__all__ = [
    "CardIdentificationData",
    "CardDatabase",
    "OLD_DATABASE_LOCATION",
    "DEFAULT_DATABASE_LOCATION",
    "with_database_write_lock",
    "SCHEMA_NAME",
]


@dataclasses.dataclass
class CardIdentificationData:
    language: OptStr = None
    name: OptStr = None
    set_code: OptStr = None
    collector_number: OptStr = None
    scryfall_id: OptStr = None
    is_front: Optional[bool] = None
    oracle_id: OptStr = None


class ImageDatabaseCards(NamedTuple):
    visible: List[Tuple[Card, CacheContent]] = []
    hidden: List[Tuple[Card, CacheContent]] = []
    unknown: List[CacheContent] = []


def with_database_write_lock(semaphore: threading.BoundedSemaphore = write_semaphore):
    """Decorator managing the database lock. Used to serialize database write transactions."""
    def decorator(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            semaphore.acquire()
            logger.debug(f"Obtained database write lock, about to run task {func}")
            try:
                # The instance used by unit tests does not have the should_run attribute.
                # In that case, run tasks regardless
                if getattr(QApplication.instance(), "should_run", True):
                    return func(*args, **kwargs)
                else:
                    logger.warning(f"Not running enqueued task {func}, because the application is about to exit.")
            finally:
                logger.debug(f"Releasing database write lock for task {func}")
                semaphore.release()
        return wrapped
    return decorator


class CardDatabase(QObject):
    """
    Holds the connection to the local SQLite database that contains the relevant card data.
    Provides methods for data access.
    """
    card_data_updated = Signal()
    custom_cards: Dict[UUID, CustomCard] = {}

    def __init__(self, db_path: Union[Literal[":memory:"], Path] = DEFAULT_DATABASE_LOCATION, parent: QObject = None,
                 check_same_thread: bool = True, register_exit_hooks: bool = True):
        """
        :param db_path: Path to the database file. May be “:memory:” to create an in-memory database for testing
            purposes.
        """
        super().__init__(parent)
        logger.info(f"Creating {self.__class__.__name__} instance.")
        self._db_check_same_thread = check_same_thread
        self.db_path = db_path
        self.db: sqlite3.Connection = None
        self._db_is_temporary = False
        self.reopen_database()
        self._exit_hook = None
        if db_path != ":memory:" and register_exit_hooks:
            self._register_exit_hook()

    @Slot()
    def reopen_database(self) -> None:
        logger.info(f"About to open card database from {self.db_path}")
        db = open_database(self.db_path, SCHEMA_NAME, check_same_thread=self._db_check_same_thread)
        outdated_on_disk = mtg_proxy_printer.sqlite_helpers.check_database_schema_version(db, SCHEMA_NAME) > 0
        if outdated_on_disk:
            logger.warning(
                "Refusing to load outdated database schema. Use empty in-memory database until migrations complete.")
            db = open_database(":memory:", SCHEMA_NAME, check_same_thread=self._db_check_same_thread)
        logger.debug("Validating schema of the opened database")
        try:
            validate_database_schema(
                db, 0, SCHEMA_NAME, "Card database has unknown application id.", False)
        except AssertionError:
            logger.exception("Card database schema validation failed. Trying to continue, but expect crashes")
        else:
            logger.debug("Card database schema valid")
        if reopened := (self.db is not None):
            self.db.rollback()
            self.db.close()
        self.db = db
        self._db_is_temporary = outdated_on_disk
        self.begin_transaction()
        if reopened:
            self.card_data_updated.emit()

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
            self.db.execute("PRAGMA optimize; -- close_db()\n")
            self.db.close()
            logger.info("Closed database.")

        atexit.register(close_db)
        self._exit_hook = close_db

    def restart_transaction(self):
        logger.info("Rolling back active read transaction")
        self.db.rollback()
        self.begin_transaction()

    def begin_transaction(self):
        logger.info("Starting new read transaction")
        self.db.execute("BEGIN DEFERRED TRANSACTION; --begin_transaction()\n")

    def has_data(self) -> bool:
        return bool(self._read_optional_scalar_from_db("SELECT EXISTS(SELECT * FROM Card) -- has_data()\n"))

    def get_last_card_data_update_timestamp(self) -> Optional[datetime.datetime]:
        """Returns the last card data update timestamp, or None, if no card data was ever imported"""
        query: LiteralString = "SELECT MAX(update_timestamp) FROM LastDatabaseUpdate -- get_last_card_data_update_timestamp\n"
        result: str = self._read_optional_scalar_from_db(query)
        return datetime.datetime.fromisoformat(result) if result else None

    def allow_updating_card_data(self) -> bool:
        """
        Returns True, if it should be allowed to update the internal card database, False otherwise.
        This is determined by the timestamp of the last database update performed.
        If the database is empty, downloading the card data is always allowed.
        """
        last_timestamp = self.get_last_card_data_update_timestamp()
        return (last_timestamp + MINIMUM_REFRESH_DELAY) <= datetime.datetime.today() if last_timestamp else True

    def get_all_languages(self) -> StringList:
        """Returns the list of all known and visible languages, sorted ascendingly."""
        logger.debug("Reading all known languages")
        query: LiteralString = "SELECT language FROM PrintLanguage ORDER BY language ASC -- get_all_languages()\n"
        return self._read_scalar_list_from_db(query)

    def get_card_names(self, language: str, card_name_filter: str = None) -> StringList:
        """Returns a sorted list with all card names in the given language that match the given filter."""
        logger.debug(f'Finding matching card names for language "{language}" and name filter "{card_name_filter}"')
        query: LiteralString = cached_dedent('''\
        SELECT card_name -- get_card_names()
            FROM FaceName
            JOIN PrintLanguage USING (language_id)
            WHERE FaceName.is_hidden IS FALSE
              AND language = ?
              {name_filter}
            ORDER BY card_name ASC
        ''')
        name_filter: LiteralString = 'AND card_name LIKE ?' if card_name_filter else ''
        query = query.format(name_filter=name_filter)

        parameters: ParameterList = [language]
        if card_name_filter:
            parameters.append(f"{card_name_filter}%")

        return self._read_scalar_list_from_db(query, parameters)

    def get_basic_land_oracle_ids(
            self, include_wastes: bool = False, include_snow_basics: bool = False) -> Set[str]:
        """Returns the oracle ids of all Basic lands."""
        names = ['Plains', 'Island', 'Swamp', 'Mountain', 'Forest']
        # Ordering matters: This order also supports Snow-Covered Wastes
        if include_wastes:
            names.append("Wastes")
        if include_snow_basics:
            names += [f"Snow-Covered {name}" for name in names]
        query = cached_dedent(f'''\
            SELECT DISTINCT oracle_id -- get_basic_land_oracle_ids()
              FROM AllPrintings
              WHERE language = 'en'
              AND card_name IN 
                ({", ".join("?"*len(names))})
        ''')
        return {item for item, in self.db.execute(query, names)}

    def is_valid_and_unique_card(self, card: CardIdentificationData) -> bool:
        """Checks, if the given card data represents a unique card printing"""
        query = cached_dedent('''\
        SELECT COUNT(*) = 1 AS is_unique -- is_valid_and_unique_card()
            FROM CardFace
            JOIN Printing USING (printing_id)
            JOIN MTGSet USING (set_id)
            JOIN FaceName USING (face_name_id)
            JOIN PrintLanguage USING (language_id)
            WHERE Printing.is_hidden IS FALSE
        ''')

        where_clause = '    AND "language" = ?\n'
        parameters: ParameterList = [card.language]
        if card.name:
            where_clause += '    AND card_name = ?\n'
            parameters.append(card.name)
        if card.set_code:
            where_clause += '    AND set_code = ?\n'
            parameters.append(card.set_code)
        if card.collector_number:
            where_clause += '    AND collector_number = ?\n'
            parameters.append(card.collector_number)
        if card.is_front is not None:
            where_clause += '    AND is_front = ?\n'
            parameters.append(card.is_front)
        query += where_clause
        return bool(self._read_optional_scalar_from_db(query, parameters))

    def get_cards_from_data(self, card: CardIdentificationData, /, *, order_by_print_count: bool = False) -> CardList:
        """
        Called with some card identification data and returns all matching cards.
        Returns a list with Card objects, each containing complete information, except for the image pixmap.
        Returns an empty list, if the given data does not match any known card.

         :param card: card identification data container that contains values to find cards
         :param order_by_print_count: Enable sorting the result list by the recorded print count. Defaults to False
        """
        query = cached_dedent('''\
        SELECT card_name, set_code, set_name, collector_number, png_image_uri, scryfall_id, is_front,
                oracle_id, highres_image, is_oversized, face_number, language, is_dfc -- get_cards_from_data()
            FROM VisiblePrintings
        ''')
        if order_by_print_count:
            query += '    LEFT OUTER JOIN LastImageUseTimestamps USING (scryfall_id, is_front)\n'
        where_clause = ['    WHERE TRUE']
        where_parameters = []
        if card.language:
            where_clause.append(f'AND "language" = ?')
            where_parameters.append(card.language)
        if card.name:
            where_clause.append(f'AND card_name = ?')
            where_parameters.append(card.name)
        if card.set_code:
            where_clause.append(f'AND set_code = ?')
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
        order_by_terms = ["is_token ASC"]
        if order_by_print_count:
            order_by_terms.append("LastImageUseTimestamps.usage_count DESC NULLS LAST")
        order_by_terms.append("wackiness_score ASC")
        order_by_terms.append("highres_image DESC")
        order_by_terms.append("release_date DESC")
        query += "ORDER BY " + "\n    ,".join(order_by_terms)
        return self._get_cards_from_data(query, where_parameters)

    def get_replacement_card_for_unknown_printing(
            self, card: CardIdentificationData, /, *, order_by_print_count: bool = False) -> CardList:
        preferred_language = mtg_proxy_printer.settings.settings["cards"]["preferred-language"]
        query = cached_dedent('''\
        -- get_replacement_card_for_unknown_printing()
        SELECT card_name, set_code, set_name, collector_number, png_image_uri,
               VisiblePrintings.scryfall_id, is_front, oracle_id, highres_image,
               is_oversized, face_number, VisiblePrintings.language, is_dfc
            FROM RemovedPrintings
            JOIN VisiblePrintings USING (oracle_id)
            LEFT OUTER JOIN LastImageUseTimestamps USING (scryfall_id, is_front)
            WHERE RemovedPrintings.scryfall_id = ?
            AND is_front = ?
            ORDER BY 
                -- Match with original language first, fall back to preferred language, then fall back to English
               (4*(VisiblePrintings.language == RemovedPrintings.language) +
                2*(VisiblePrintings.language == ?) +
                  (VisiblePrintings.language == 'en')) DESC NULLS LAST,
                wackiness_score ASC,
                release_date DESC
        ''')
        if order_by_print_count:
            query += '        , LastImageUseTimestamps.usage_count DESC NULLS LAST\n'
        # Break any remaining ties by preferring high resolution images over low resolution images
        query += '        , VisiblePrintings.highres_image DESC\n'
        return self._get_cards_from_data(query, [card.scryfall_id, card.is_front, preferred_language])

    def _get_cards_from_data(self, query, parameters) -> CardList:
        cursor = self.db.execute(query, parameters)
        return [
            Card(
                name, MTGSet(set_code, set_name), collector_number,
                language, scryfall_id, bool(is_front), oracle_id, image_uri,
                bool(highres_image), CardSizes.from_bool(is_oversized), face_number, bool(is_dfc),
            )
            for name, set_code, set_name, collector_number, image_uri, scryfall_id, is_front, oracle_id, highres_image,
                is_oversized, face_number, language, is_dfc in cursor
        ]

    def find_related_cards(self, card: Card) -> CardList:
        """
        Recursively finds all cards related to the given card.
        This may be cards referenced by name in either direction, or token cards created.
        The search never returns the identity, i.e. the input card is never part of the output list.

        Non-token cards may find anything, including other cards, tokens, emblems, dungeons, planes, etc.

        Non-regular cards may not find non-token cards as that would create potentially huge graphs due to
        evergreen tokens like Treasures, Food, Clues, 2/2 Zombies, The Ring emblem, etc.
        """
        query = cached_dedent("""\
        WITH RECURSIVE   -- find_related_cards()
          source_oracle_id (card_id) AS (
            SELECT card_id
            FROM Card
            WHERE oracle_id = ?),
          related_oracle_ids(related_id) AS (
            SELECT related_id
              FROM RelatedPrintings
              JOIN source_oracle_id USING (card_id)
            UNION  -- Deduplicate to break infinite recursion on cross-referenced cards
            SELECT RelatedPrintings.related_id
              FROM RelatedPrintings
              JOIN related_oracle_ids ON RelatedPrintings.card_id = related_oracle_ids.related_id
              -- Do not include the initial input card in the output dataset
              WHERE RelatedPrintings.related_id NOT IN (SELECT source_oracle_id.card_id FROM source_oracle_id)
        )
        SELECT oracle_id
          FROM Card
          JOIN related_oracle_ids ON Card.card_id = related_oracle_ids.related_id
        """)
        cards = []
        for related_oracle_id in self._read_scalar_list_from_db(query, (card.oracle_id,)):
            # Prefer same set over other sets, which is important for multi-component cards like Meld cards. If it
            # isn't available, take from any other set. As a last-ditch fallback, resort to English printings.
            # The last case is most likely hit with non-English token-producing cards,
            # as long as Scryfall does not provide localized tokens.
            related_cards = \
                self.get_cards_from_data(
                    CardIdentificationData(card.language, set_code=card.set_code, oracle_id=related_oracle_id),
                    order_by_print_count=True) or \
                self.get_cards_from_data(
                    CardIdentificationData(card.language, oracle_id=related_oracle_id),
                    order_by_print_count=True) or \
                self.get_cards_from_data(
                    CardIdentificationData("en", oracle_id=related_oracle_id),
                    order_by_print_count=True)
            if related_cards:
                cards.append(related_cards[0])
        return cards

    def find_collector_numbers_matching(self, card_name: str, set_code: str, language: str) -> StringList:
        """
        Finds all collector numbers matching the given filter. The result contains multiple elements, if the card
        had multiple variants with distinct collector numbers in the given set.

        :param card_name: Card name, matched exactly
        :param set_code: Set abbreviation, matched exactly
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
            JOIN MTGSet USING (set_id)
            WHERE Printing.is_hidden IS FALSE
              AND FaceName.is_hidden IS FALSE
              AND "language" = ?
              AND set_code = ?
              AND card_name = ?
        ''')
        return natural_sorted(item for item, in self.db.execute(query, (language, set_code, card_name)))

    def find_sets_matching(
            self, card_name: str, language: str, set_name_filter: str = None,
            *, is_front: bool = None) -> List[MTGSet]:
        """
        Finds all matching sets that the given card was printed in.

        :param card_name: Card name, matched exactly
        :param language: card language, matched exactly
        :param set_name_filter: If provided, only return sets with set code or full name beginning with this.
          Used as a LIKE pattern, supporting SQLite wildcards.
        :param is_front: Match by front/back. Only relevant when switching printings of SLD reversible cards.
        :return: List of matching sets, as tuples (set_abbreviation, full_english_set_name)
        """
        query = cached_dedent('''\
        SELECT DISTINCT set_code, set_name  -- find_sets_matching()
            FROM CardFace
            JOIN Printing USING (printing_id)
            JOIN MTGSet USING (set_id)
            JOIN FaceName USING (face_name_id)
            JOIN PrintLanguage USING (language_id)
            WHERE Printing.is_hidden IS FALSE
              AND FaceName.is_hidden IS FALSE
              AND "language" = ?
              AND card_name = ?
              AND COALESCE(is_front = ?, TRUE)
        ''')
        parameters: ParameterList = [language, card_name, is_front]
        if set_name_filter:
            query += '      AND (set_code LIKE ? OR set_name LIKE ?)\n'
            parameters += [f"{set_name_filter}%"] * 2

        query += '    ORDER BY set_name ASC\n'
        return list(starmap(MTGSet, self.db.execute(query, parameters)))

    def get_card_with_scryfall_id(self, scryfall_id: str, is_front: bool) -> OptionalCard:
        query = cached_dedent('''\
        SELECT card_name, set_code, set_name, collector_number, "language", png_image_uri, oracle_id,
            highres_image, is_oversized, face_number, is_dfc -- get_card_with_scryfall_id()
            FROM VisiblePrintings
            WHERE scryfall_id = ? AND is_front = ?
        ''')
        result = self.db.execute(query, (scryfall_id, is_front)).fetchone()
        if result is None:
            return None
        else:
            name, set_code, set_name, collector_number, language, image_uri, oracle_id, highres_image, \
                is_oversized, face_number, is_dfc = result
            size = CardSizes.from_bool(is_oversized)
            return Card(
                name, MTGSet(set_code, set_name), collector_number,
                language, scryfall_id, bool(is_front), oracle_id, image_uri,
                bool(highres_image), size, face_number, bool(is_dfc),
            )

    def get_all_cards_from_image_cache(self, cache_content: List[CacheContent]) -> ImageDatabaseCards:
        """
        Partitions the content of the ImageDatabase disk cache into three lists:
        - All visible card printings
        - All hidden card printings
        - All unknown images

        Visible and invisible printings are returned as lists containing tuples (Card, CacheContent),
        unknown images are returned as a list with plain CacheContent instances.
        """
        db = self.db
        db.execute("SAVEPOINT 'partition_image_cache' -- get_all_cards_from_image_cache()\n")
        db.execute(cached_dedent('''\
            CREATE TEMP TABLE ImagesOnDisk ( -- get_all_cards_from_image_cache()
              scryfall_id TEXT NOT NULL,
              is_front INTEGER NOT NULL,
              highres_on_disk INTEGER NOT NULL,
              absolute_path TEXT NOT NULL
            )
        '''))
        db.executemany(
            cached_dedent("""\
            INSERT INTO ImagesOnDisk -- get_all_cards_from_image_cache()
              (scryfall_id, is_front, highres_on_disk, absolute_path)
              VALUES (?, ?, ?, ?)"""),
            map(dataclasses.astuple, cache_content)
        )
        known_images_query = cached_dedent('''\
        SELECT scryfall_id, is_front, highres_on_disk, absolute_path, -- get_all_cards_from_image_cache()
            card_name, set_code, set_name, collector_number, "language", png_image_uri, oracle_id,
            is_oversized, face_number, is_dfc, is_hidden -- get_all_cards_from_image_cache()
            FROM AllPrintings
            NATURAL JOIN ImagesOnDisk
        ''')
        # Using an EXCEPT compound query in the subquery is faster (~80ms) than a NOT IN () subquery (~700ms)
        unknown_images_query = cached_dedent('''\
        SELECT scryfall_id, is_front, highres_on_disk, absolute_path -- get_all_cards_from_image_cache()
          FROM ImagesOnDisk
          WHERE (scryfall_id, is_front) IN (
            SELECT scryfall_id, is_front
              FROM ImagesOnDisk
            EXCEPT
            SELECT scryfall_id, is_front
              FROM Printing
              JOIN CardFace USING (printing_id)
          )
        ''')
        cards = ImageDatabaseCards([], [], [])
        cards.unknown[:] = (
            CacheContent(scryfall_id, bool(is_front), bool(highres_on_disk), Path(abs_path))
            for scryfall_id, is_front, highres_on_disk, abs_path
            in db.execute(unknown_images_query))
        for scryfall_id, is_front, highres_on_disk, abs_path, \
                name, set_code, set_name, collector_number, language, image_uri, oracle_id, \
                is_oversized, face_number, is_dfc, is_hidden \
                in db.execute(known_images_query):
            cache_item = CacheContent(scryfall_id, bool(is_front), bool(highres_on_disk), Path(abs_path))
            size = CardSizes.from_bool(is_oversized)
            card = Card(
                name, MTGSet(set_code, set_name), collector_number,
                language, cache_item.scryfall_id, cache_item.is_front, oracle_id, image_uri,
                bool(highres_on_disk), size, face_number, is_dfc
            )
            if is_hidden:
                cards.hidden.append((card, cache_item))
            else:
                cards.visible.append((card, cache_item))
        db.execute("ROLLBACK TRANSACTION TO SAVEPOINT 'partition_image_cache' -- get_all_cards_from_image_cache()\n")
        return cards

    def get_opposing_face(self, card) -> OptionalCard:
        """
        Returns the opposing face for double faced cards, or None for single-faced cards.
        """
        return self.get_card_with_scryfall_id(card.scryfall_id, not card.is_front)

    def guess_language_from_name(self, name: str) -> Optional[str]:
        """Guesses the card language from the card name. Returns None, if no result was found."""
        query = cached_dedent('''\
        SELECT "language" -- guess_language_from_name()
            FROM FaceName
            JOIN PrintLanguage USING (language_id)
            WHERE card_name = ?
            -- Assume English by default to not match other languages in case their entry misses the proper
            -- localisation and uses the English name as a fallback.
            ORDER BY "language" = 'en' DESC;
        ''')
        return self._read_optional_scalar_from_db(query, (name,))

    def is_known_language(self, language: str) -> bool:
        """Returns True, if the given two-letter code is a known language. Returns False otherwise."""
        query = cached_dedent('''
        SELECT EXISTS( -- is_known_language()
            SELECT *
            FROM PrintLanguage
            WHERE "language" = ?
        )
        ''')
        return bool(self._read_optional_scalar_from_db(query, (language,)))

    def is_dfc(self, scryfall_id: str) -> bool:
        """Returns True, if the given card is a DFC, False otherwise."""
        # This query returns two values for DFC cards, but that does not pose any issue
        query = cached_dedent('''
        SELECT is_dfc -- is_dfc()
          FROM AllPrintings
          WHERE "scryfall_id" = ?
        ''')
        return bool(self._read_optional_scalar_from_db(query, (scryfall_id,)))

    def translate_card_name(self, card_data: Union[CardIdentificationData, Card], target_language: str,
                            include_hidden_names: bool = False) -> OptStr:
        """
        Translates a card into the target_language. Uses the language in the card data as the source language, if given.
        If not, card names across all languages are searched.

        :return: String with the translated card name, or None, if either unknown or unavailable in the target language.
        """
        # Implementation note: First two query parameters may be None/NULL and can be used as a disambiguation in case
        # that a translation is ambiguous. As an example, “Duress” is translated to “Zwang” in German, except for
        # the one time in the 6th Edition set, where the English “Coercion” was also translated to “Zwang”.
        # So given “Zwang” in German without further context, it may mean one of two cards.
        # So if no context is given, this query performs a majority vote, because that is the most likely expected
        # result. But if context is given, either by the scryfall id or the set code, the exact, set-specific
        # translation is returned.
        card_view: LiteralString = "AllPrintings" if include_hidden_names else "VisiblePrintings"
        query = cached_dedent("""\
        WITH  -- translate_card_name()
          source_context (source_scryfall_id, source_set_code) AS (SELECT ?, ?),
          source_oracle_id (oracle_id, face_number, source_score, source_set_code) AS (
            SELECT oracle_id, face_number,
                (SELECT count() FROM Card)
                  * (COALESCE(scryfall_id = source_scryfall_id, 0)
                     OR COALESCE(set_code = source_set_code, 0))
                  + count(oracle_id) AS source_score,
                set_code AS source_set_code
            FROM FaceName
            JOIN PrintLanguage USING (language_id)
            JOIN CardFace USING (face_name_id)
            JOIN Printing USING (printing_id)
            JOIN Card USING (card_id)
            JOIN MTGSet USING (set_id)
            JOIN source_context ON (
               COALESCE(set_code = source_set_code, TRUE) AND
               COALESCE(scryfall_id = source_scryfall_id, TRUE))
            WHERE card_name = ? AND COALESCE("language" = ?, TRUE)
            GROUP BY oracle_id, face_number
            )
        SELECT card_name
          FROM source_oracle_id
          JOIN {card_view} USING (oracle_id, face_number)
          WHERE language = ?
          GROUP BY card_name
          -- Some localized names were updated to fix typos and similar, so prefer the newest, matched name
          ORDER BY source_score DESC, set_code = source_set_code DESC, release_date DESC
          LIMIT 1
        ;
        """).format(card_view=card_view)
        parameters: ParameterList = [
            card_data.scryfall_id, card_data.set_code, card_data.name, card_data.language, target_language]
        return self._read_optional_scalar_from_db(query, parameters)

    def get_available_languages_for_card(self, card: Card) -> StringList:
        """
        Returns the sorted list of languages the given card is available in.
        This is used as the data source for the ComboBoxItemDelegate model
        to generate the choices for translating cards in the document.
        """
        query = cached_dedent("""\
        SELECT DISTINCT language FROM ( -- get_available_languages_for_card()
          SELECT ? AS language
          UNION ALL
          SELECT language
            FROM Card
            JOIN Printing USING (card_id)
            JOIN CardFace USING (printing_id)
            JOIN FaceName USING (face_name_id)
            JOIN PrintLanguage USING (language_id)
            WHERE oracle_id = ?
              AND Printing.is_hidden IS FALSE
          )
          ORDER BY language ASC;
        """)
        parameters: ParameterList = [card.language, card.oracle_id]
        return self._read_scalar_list_from_db(query, parameters)

    def get_available_sets_for_card(self, card: Card) -> List[MTGSet]:
        """
        Returns a list of MTG sets the card with the given Oracle ID is in, ordered by release date from old to new.
        """
        query = cached_dedent("""\
        SELECT DISTINCT set_code, set_name FROM ( -- get_available_sets_for_card()
          SELECT set_code, set_name, release_date
          FROM MTGSet
          JOIN Printing USING (set_id)
          JOIN Card USING (card_id)
          JOIN CardFace USING (printing_id)
          JOIN FaceName USING (face_name_id)
          JOIN PrintLanguage USING (language_id)
          WHERE Printing.is_hidden IS FALSE
            AND FaceName.is_hidden IS FALSE
            AND oracle_id = ? 
            AND language = ?
          UNION ALL
          SELECT set_code, set_name, release_date
            FROM MTGSet
            WHERE set_code = ?
          )
          ORDER BY release_date ASC
        """)
        parameters: ParameterList = [card.oracle_id, card.language, card.set_code]
        result = list(starmap(MTGSet, self.db.execute(query, parameters)))
        if not result:
            result.append(card.set)
        return result

    def get_available_collector_numbers_for_card_in_set(self, card: Card) -> StringList:
        query = cached_dedent("""\
        SELECT DISTINCT collector_number FROM ( -- get_available_collector_numbers_for_card_in_set()
          SELECT ? AS collector_number
          UNION ALL
          SELECT collector_number
            FROM MTGSet
            JOIN Printing USING (set_id)
            JOIN Card USING (card_id)
            JOIN CardFace USING (printing_id)
            JOIN FaceName USING (face_name_id)
            JOIN PrintLanguage USING (language_id)
            WHERE Printing.is_hidden IS FALSE
              AND FaceName.is_hidden IS FALSE
              AND oracle_id = ?
              AND set_code = ?
              AND language = ?
          )
        """)
        parameters: ParameterList = [card.collector_number, card.oracle_id, card.set_code, card.language]
        return natural_sorted((number for number, in self.db.execute(query, parameters)))

    def _read_optional_scalar_from_db(self, query: LiteralString, parameters: Sequence[Any] = ()):
        """
        Runs the query with the given parameters that is expected to return either a singular value or None,
        and returns the result
        """
        if result := self.db.execute(query, parameters).fetchone():
            return result[0]
        else:
            return None

    def _read_scalar_list_from_db(
            self, query: LiteralString, parameters: Sequence[Any] = ()) -> List[Any]:
        """Runs the query with the given parameters, returning a list of singular items"""
        return [item for item, in self.db.execute(query, parameters)]

    def is_removed_printing(self, scryfall_id: str) -> bool:
        logger.debug(f"Query RemovedPrintings table for scryfall id {scryfall_id}")
        parameters: ParameterList = [scryfall_id,]
        query = cached_dedent("""\
        SELECT oracle_id -- is_removed_printing()
            FROM RemovedPrintings
            WHERE scryfall_id = ?
        """)
        return bool(self._read_optional_scalar_from_db(query, parameters))

    def cards_not_used_since(self, keys: List[Tuple[str, bool]], date: datetime.date) -> List[int]:
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

    def cards_used_less_often_then(self, keys: List[Tuple[str, bool]], count: int) -> List[int]:
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
        return [
            index
            for index, (scryfall_id, is_front) in enumerate(keys)
            if self._read_optional_scalar_from_db(query, (scryfall_id, is_front, count))
        ]

    def translate_card(self, to_translate: T, target_language: str = None) -> T:
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
        if isinstance(to_translate, CheckCard):
            return CheckCard(
                (front := self.translate_card(to_translate.front, target_language)),
                self.get_opposing_face(front)
            )
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
        # for the alternative, appending a clause like "ORDER BY similarity DESC LIMIT 1"
        # This was chosen as a performance optimization,
        # because card translation can take considerable time during a deck list import.
        query = cached_dedent("""\
        SELECT card_name, set_code, set_name, collector_number, -- _translate_card()
               scryfall_id, png_image_uri, highres_image,
               is_oversized, face_number, is_dfc,
               MAX((set_code = ?) + (collector_number = ?)) AS similarity
            FROM VisiblePrintings
            WHERE oracle_id = ? AND language = ? AND is_front = ?
        """)
        parameters: ParameterList = [card.set.code, card.collector_number, card.oracle_id, language_override, card.is_front]
        # Because of the aggregate function used, no hit will result in a single row consisting of only NULL values.
        result = self.db.execute(query, parameters).fetchone()
        name, set_code, set_name, collector_number, scryfall_id, image_uri, highres_image, \
            is_oversized, face_number, is_dfc, similarity = result
        if similarity is None:
            logger.debug(f"Found no translations to {language_override} for card '{card.name}'.")
            return None
        size = CardSizes.from_bool(is_oversized)
        return Card(
            name, MTGSet(set_code, set_name), collector_number,
            language_override, scryfall_id, card.is_front, card.oracle_id, image_uri,
            bool(highres_image), size, face_number, bool(is_dfc),
        )

    def get_custom_card(
            self, name: str, set_code: str, set_name: str, collector_number: str,
            size: CardSize, is_front: bool, image: bytes) -> CustomCard:
        card = CustomCard(
            name, MTGSet(set_code, set_name), collector_number, "en",
            is_front, "", True, size, 1 + (not is_front), False, image)
        custom_card_id = card.scryfall_id
        card = self.custom_cards.get(custom_card_id, card)
        self.custom_cards[custom_card_id] = card
        return card