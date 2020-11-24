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
import pathlib
import pkg_resources
import re
import sqlite3
import typing

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
SCHEMA_PRAGMA_USER_VERSION_MATCHER = re.compile(r"PRAGMA\s+user_version\s+=\s+(?P<version>[0-9]+)\s*;", re.ASCII)


@dataclasses.dataclass()
class Card:
    name: OptionalString
    set_abbr: OptionalString
    collector_number: OptionalString
    language: str
    image_uri: OptionalString = None


class CardDatabase:

    MIN_SUPPORTED_SQLITE_VERSION = (3, 33, 0)

    def __init__(self, db_path: typing.Union[str, pathlib.Path] = DEFAULT_DATABASE_LOCATION):
        logger.info(f"Creating {self.__class__.__name__} instance.")
        if isinstance(db_path, str) and db_path != ":memory:":
            db_path = pathlib.Path(db_path)
        if sqlite3.sqlite_version_info < self.MIN_SUPPORTED_SQLITE_VERSION:
            raise sqlite3.NotSupportedError(
                f"This program uses functionality added in SQLite "
                f"{'.'.join(map(str, self.MIN_SUPPORTED_SQLITE_VERSION))}. Your system has {sqlite3.sqlite_version}. "
                f"Please update your SQLite3 installation or point your Python installation to a supported version "
                f"of the SQLite3 library."
            )
        if not isinstance(db_path, str) and not (parent_dir := db_path.parent).exists():
            logger.info(f"Parent directory '{parent_dir}' does not exist, creating it…")
            parent_dir.mkdir(parents=True)
        location = "in memory" if db_path == ":memory:" else f"at {db_path}"
        logger.debug(f"Opening Database {location}.")
        # This has to be determined before the connection is opened and the file is created on disk.
        should_create_schema = db_path == ":memory:" or not db_path.exists()
        self.db: sqlite3.Connection = sqlite3.connect(db_path)
        logger.debug(f"Connected SQLite database {location}.")
        # Both settings are volatile, thus have to be set for each opened connection
        self.db.executescript("PRAGMA foreign_keys = ON; PRAGMA analysis_limit=1000;")
        logger.debug("Enabled SQLite3 foreign keys support.")
        if db_path == ":memory:":
            logger.debug("Skipping registering cleanup hooks for in-memory databases.")
            self.populate_database_schema()
        else:
            if should_create_schema:
                self.populate_database_schema()
            logger.debug("Registering cleanup hooks that close the database on exit.")

            def close_db():
                logger.debug("Rolling back active transactions.")
                self.db.rollback()
                logger.debug("Running SQLite PRAGMA optimize.")
                # Running query planner optimization prior to closing the connection, as recommended by the SQLite devs.
                # See also: https://www.sqlite.org/lang_analyze.html
                self.db.execute("PRAGMA optimize")
                self.db.close()
                del self.db
                logger.info("Closed database.")

            atexit.register(close_db)
        self.check_database_schema_version()

    def populate_database_schema(self):
        logger.info("Creating database schema.")
        if user_version := self.db.execute("PRAGMA user_version").fetchone()[0]:
            raise RuntimeError(f"Cannot perform this on a non-empty database: {user_version=}.")
        else:
            schema = pkg_resources.resource_string(__name__, 'carddb.sql').decode("utf-8")
            self.db.executescript(schema)
        logger.debug("Created database schema.")

    def check_database_schema_version(self) -> bool:
        database_user_version: int = self.db.execute("PRAGMA user_version").fetchone()[0]
        schema = pkg_resources.resource_string(__name__, 'carddb.sql').decode("utf-8")
        latest_user_version = int(SCHEMA_PRAGMA_USER_VERSION_MATCHER.search(schema)["version"])
        if database_user_version != latest_user_version:
            message = f"Schema version mismatch in the opened database. " \
                      f"Expected schema version {latest_user_version}, got {database_user_version}."
            logger.warning(message)
            print(f"WARNING: {message}")
        return database_user_version != latest_user_version

    def commit(self):
        self.db.execute("COMMIT")

    def has_data(self) -> bool:
        result, = self.db.execute("SELECT EXISTS(SELECT * FROM Card)").fetchone()
        return bool(result)

    def get_all_languages(self) -> StringList:
        result = [lang for (lang,) in self.db.execute("SELECT DISTINCT language FROM Card ORDER BY language ASC")]
        return result

    def get_card_names(self, language: str) -> StringList:
        """Returns a list with all card names in the given language."""
        query = self.db.execute(
            r"""SELECT DISTINCT card_name
            FROM Card
            JOIN CardFace USING(scryfall_id)
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
        query = r"""SELECT COUNT(*) = 1
            FROM Card JOIN CardFace USING (scryfall_id)
            WHERE "language" = ?
            """
        parameters = [card.language]
        if card.name:
            query += "\n AND card_name = ?"
            parameters.append(card.name)
        if card.set_abbr:
            query += """\n AND "set" = ?"""
            parameters.append(card.set_abbr)
        if card.collector_number:
            query += """\n AND collector_number = ?"""
            parameters.append(card.collector_number)
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
        query = r"""SELECT card_name, "set", collector_number, png_image_uri
            FROM Card JOIN CardFace USING (scryfall_id)
            WHERE "language" = ?
            """
        parameters = [card.language]
        if card.name:
            query += "\n AND card_name = ?"
            parameters.append(card.name)
        if card.set_abbr:
            query += """\n AND "set" = ?"""
            parameters.append(card.set_abbr)
        if card.collector_number:
            query += """\n AND collector_number = ?"""
            parameters.append(card.collector_number)
        cursor = self.db.execute(
            query,
            parameters
        )
        result = cursor.fetchone()
        if not result or cursor.fetchone():
            raise RuntimeError(f"CardDatabase.add_missing_information() called on non-unique card information: {card}")
        card.name, card.set_abbr, card.collector_number, card.image_uri = result

    def find_collector_numbers_matching(self, card: Card) -> StringList:
        query = r"""SELECT DISTINCT collector_number
            FROM Card JOIN CardFace USING (scryfall_id)
            WHERE "language" = ?
            """
        parameters = [card.language]
        if card.name:
            query += "\n AND card_name = ?"
            parameters.append(card.name)
        if card.set_abbr:
            query += """\n AND "set" LIKE ?"""
            parameters.append(f"%{card.set_abbr}")

        query += """\n ORDER BY collector_number ASC"""
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
        query = r"""SELECT DISTINCT card_name
            FROM Card JOIN CardFace USING (scryfall_id)
            WHERE "language" = ?
            """
        parameters = [card.language]
        if card.set_abbr:
            query += """\n AND "set" LIKE ?"""
            parameters.append(f"%{card.set_abbr}")
        if card.collector_number:
            query += """\n AND collector_number LIKE ?"""
            parameters.append(f"%{card.collector_number}")
        query += """\n ORDER BY card_name ASC"""
        cursor = self.db.execute(
            query,
            parameters
        )
        result = [name for name, in cursor]
        return result

    def find_sets_matching(self, card: Card) -> StringList:
        """
        Finds all sets given the language, card name prefix and collector number prefix
        """
        pass
        query = r"""SELECT DISTINCT "set"
            FROM Card JOIN CardFace USING (scryfall_id)
            WHERE "language" = ?
            """
        parameters = [card.language]
        if card.name:
            query += """\n AND card_name LIKE ?"""
            parameters.append(f"%{card.name}")
        if card.collector_number:
            query += """\n AND collector_number LIKE ?"""
            parameters.append(f"%{card.collector_number}")
        query += """\n ORDER BY "set" ASC"""
        cursor = self.db.execute(
            query,
            parameters
        )
        result = [set_abbr for set_abbr, in cursor]
        return result
