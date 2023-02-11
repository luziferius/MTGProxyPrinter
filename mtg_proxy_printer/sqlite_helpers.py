# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>

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

import pathlib
import pkg_resources
import re
import sqlite3
import typing

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

__all__ = [
    "open_database",
    "check_database_schema_version",
    "create_in_memory_database",
]

SCHEMA_PRAGMA_USER_VERSION_MATCHER = re.compile(r"PRAGMA\s+user_version\s+=\s+(?P<version>\d+)\s*;", re.ASCII)


def create_in_memory_database(
        schema_name: str, min_supported_sqlite_version: typing.Tuple[int, int, int],
        check_same_thread: bool = True) -> sqlite3.Connection:
    if sqlite3.sqlite_version_info < min_supported_sqlite_version:
        raise sqlite3.NotSupportedError(
            f"This program uses functionality added in SQLite "
            f"{'.'.join(map(str, min_supported_sqlite_version))}. Your system has {sqlite3.sqlite_version}. "
            f"Please update your SQLite3 installation or point your Python installation to a supported version "
            f"of the SQLite3 library."
        )
    logger.info(f"Creating in-memory database using schema {schema_name}.")
    db = sqlite3.connect(":memory:", check_same_thread=check_same_thread)
    # These settings are volatile, thus have to be set for each opened connection
    db.executescript("PRAGMA foreign_keys = ON; PRAGMA analysis_limit=1000; PRAGMA trusted_schema = OFF;")
    populate_database_schema(db, schema_name)
    return db


def open_database(
        db_path: typing.Union[str, pathlib.Path], schema_name: str,
        min_supported_sqlite_version: typing.Tuple[int, int, int],
        check_same_thread: bool = True) -> sqlite3.Connection:
    if isinstance(db_path, str) and db_path != ":memory:":
        db_path = pathlib.Path(db_path)
    if sqlite3.sqlite_version_info < min_supported_sqlite_version:
        raise sqlite3.NotSupportedError(
            f"This program uses functionality added in SQLite "
            f"{'.'.join(map(str, min_supported_sqlite_version))}. Your system has {sqlite3.sqlite_version}. "
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
    db = sqlite3.connect(db_path, check_same_thread=check_same_thread)
    logger.debug(f"Connected SQLite database {location}.")
    # These settings are volatile, thus have to be set for each opened connection
    db.executescript("PRAGMA foreign_keys = ON; PRAGMA analysis_limit=1000; PRAGMA trusted_schema = OFF;")
    logger.debug("Enabled SQLite3 foreign keys support.")
    if should_create_schema:
        populate_database_schema(db, schema_name)

    check_database_schema_version(db, schema_name)
    return db


def populate_database_schema(db: sqlite3.Connection, schema_name: str):
    logger.info("Creating database schema.")
    if user_version := db.execute("PRAGMA user_version\n").fetchone()[0]:
        raise RuntimeError(f"Cannot perform this on a non-empty database: {user_version=}.")
    else:
        schema = pkg_resources.resource_string("mtg_proxy_printer.model",  f"{schema_name}.sql").decode("utf-8")
        db.executescript(schema)
    logger.debug("Created database schema.")


def check_database_schema_version(db: sqlite3.Connection, schema_name: str) -> int:
    """
    Returns the difference between the latest database schema version and the connected database schema version.

    :returns: - Positive integer, if the database is outdated
              - Zero if it is up-to-date
              - Negative integer, if the database was created by a later version that created a newer schema.

    """
    database_user_version: int = db.execute("PRAGMA user_version\n").fetchone()[0]
    latest_user_version = _read_current_database_schema_version(schema_name)
    if database_user_version != latest_user_version:
        message = f"Schema version mismatch in the opened database. " \
                  f"Expected schema version {latest_user_version}, got {database_user_version}."
        logger.warning(message)
    return latest_user_version - database_user_version


def _read_current_database_schema_version(schema_name: str) -> int:
    schema = pkg_resources.resource_string("mtg_proxy_printer.model", f"{schema_name}.sql").decode("utf-8")
    latest_user_version = int(SCHEMA_PRAGMA_USER_VERSION_MATCHER.search(schema)["version"])
    return latest_user_version
