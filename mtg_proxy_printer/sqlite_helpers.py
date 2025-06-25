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

import datetime
import functools
import importlib.resources
import pathlib
import re
import sqlite3
import sys
import textwrap
import typing
try:
    from typing import LiteralString
except ImportError:
    from typing_extensions import LiteralString

from hamcrest import assert_that, contains_exactly

from mtg_proxy_printer.units_and_sizes import unit_registry
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

__all__ = [
    "open_database",
    "check_database_schema_version",
    "create_in_memory_database",
    "read_resource_text",
    "cached_dedent",
    "validate_database_schema"
]

MIN_SUPPORTED_SQLITE_VERSION = (3, 35, 0)
SCHEMA_PRAGMA_USER_VERSION_MATCHER = re.compile(r"PRAGMA\s+user_version\s+=\s+(?P<version>\d+)\s*;", re.ASCII)
sqlite3.register_adapter(pathlib.PosixPath, str)
sqlite3.register_adapter(pathlib.WindowsPath, str)
sqlite3.register_adapter(type(1*unit_registry.mm), str)
sqlite3.register_converter("TEXT_QUANTITY", lambda b: unit_registry.parse_expression(b.decode("utf-8")))
sqlite3.register_converter("BOOLEAN_INTEGER", lambda b: bool(int(b)))
sqlite3.register_converter("TIMESTAMP", lambda b: datetime.datetime.fromisoformat(b.decode("utf-8")))


if sqlite3.sqlite_version_info < MIN_SUPPORTED_SQLITE_VERSION:
    raise sqlite3.NotSupportedError(
        f"This program uses functionality added in SQLite "
        f"{'.'.join(map(str, MIN_SUPPORTED_SQLITE_VERSION))}. Your system has {sqlite3.sqlite_version}. "
        f"Please update your SQLite3 installation or point your Python installation to a supported version "
        f"of the SQLite3 library."
    )


def read_resource_text(package: str, resource: str, encoding: str = "utf-8") -> str:
    """Reads the given package data resource and returns it as a string"""
    if sys.version_info >= (3, 9):
        # New and preferred way for Python 3.9+
        return importlib.resources.files(package).joinpath(resource).read_text(encoding)
    # Backwards compatibility with Python 3.8
    return importlib.resources.read_text(package, resource, encoding)


def create_in_memory_database(schema_name: str, check_same_thread: bool = True) -> sqlite3.Connection:
    logger.info(f"Creating in-memory database using schema {schema_name}.")
    db = sqlite3.connect(":memory:", check_same_thread=check_same_thread, detect_types=sqlite3.PARSE_DECLTYPES)
    # These settings are volatile, thus have to be set for each opened connection
    db.execute("PRAGMA foreign_keys = ON\n")
    db.execute("PRAGMA trusted_schema = OFF\n")
    db.execute("PRAGMA analysis_limit=1000\n")
    populate_database_schema(db, schema_name)
    return db


def open_database(
        db_path: typing.Union[str, pathlib.Path], schema_name: str,
        check_same_thread: bool = True) -> sqlite3.Connection:
    if isinstance(db_path, str) and db_path != ":memory:":
        db_path = pathlib.Path(db_path)
    if not isinstance(db_path, str) and not (parent_dir := db_path.parent).exists():
        logger.info(f"Parent directory '{parent_dir}' does not exist, creating it…")
        parent_dir.mkdir(parents=True)
    location = "in memory" if db_path == ":memory:" else f"at {db_path}"
    logger.debug(f"Opening Database {location}.")
    # This has to be determined before the connection is opened and the file is created on disk.
    should_create_schema = db_path == ":memory:" or not db_path.exists()
    db = sqlite3.connect(db_path, check_same_thread=check_same_thread, detect_types=sqlite3.PARSE_DECLTYPES)
    logger.debug(f"Connected SQLite database {location}.")
    # These settings are volatile, thus have to be set for each opened connection
    db.execute("PRAGMA foreign_keys = ON\n")
    db.execute("PRAGMA trusted_schema = OFF\n")
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
        schema = read_resource_text("mtg_proxy_printer.model",  f"{schema_name}.sql")
        db.executescript(schema)
    logger.debug("Created database schema.")


def check_database_schema_version(db: sqlite3.Connection, schema_name: str) -> int:
    """
    Returns the difference between the latest database schema version and the connected database schema version.

    :returns: - Positive integer, if the database is outdated
              - Zero if it is up-to-date
              - Negative integer, if the database was created by a later version that created a newer schema.

    """
    connected_database_schema_version: int = db.execute("PRAGMA user_version\n").fetchone()[0]
    target_schema_version = get_target_database_schema_version(schema_name)
    if connected_database_schema_version != target_schema_version:
        message = f"Schema version mismatch in the opened database. " \
                  f"Expected schema version {target_schema_version}, got {connected_database_schema_version}."
        logger.warning(message)
    return target_schema_version - connected_database_schema_version


def get_target_database_schema_version(schema_name: str) -> int:
    schema = read_resource_text("mtg_proxy_printer.model", f"{schema_name}.sql")
    latest_user_version = int(SCHEMA_PRAGMA_USER_VERSION_MATCHER.search(schema)["version"])
    return latest_user_version


def validate_database_schema(
        db_unsafe: sqlite3.Connection, file_magic: int, schema_name: str,
        magic_mismatch_error_msg: str, is_untrusted_db: bool = True) -> int:
    """
    Validates the database schema of the user-provided file against a known-good schema.

    :raises AssertionError: If the provided file contains an invalid schema
    :param db_unsafe: Arbitrary SQLite3 database connection
    :param file_magic: Expected Application ID
    :param schema_name: Expected database schema
    :param magic_mismatch_error_msg: UI-presentable error message returned on mismatching application id
    :param is_untrusted_db: Perform additional validation logic.
      Can be turned off, since these can take a long time on the CardDatabase file.
    :returns: Database schema version
    """
    assert_that(
        db_unsafe.execute("PRAGMA application_id\n").fetchone(),
        contains_exactly(file_magic),
        magic_mismatch_error_msg
    )
    if is_untrusted_db:
        # https://www.sqlite.org/security.html
        db_unsafe.execute("PRAGMA mmap_size=0\n")
        db_unsafe.execute("PRAGMA cell_size_check=ON\n")
        db_unsafe.execute("PRAGMA integrity_check\n")

    user_schema_version = db_unsafe.execute("PRAGMA user_version\n").fetchone()[0]
    try:
        db_known_good = create_in_memory_database(schema_name)
    except FileNotFoundError as e:
        raise AssertionError(f"Unknown database schema version: {user_schema_version}") from e
    tables_and_views_query = textwrap.dedent("""\
        SELECT   s.type, s.name,
                 p.cid AS column_id, p.name AS column_name, p.type AS column_type,
                 p."notnull" AS column_not_null_constraint_enabled, p.dflt_value AS column_default_value,
                 p.pk AS column_primary_key_component
          FROM   sqlite_schema AS s
          JOIN   pragma_table_info(s.name) AS p
         WHERE   s.type IN ('table', 'view')
           AND   s.name NOT LIKE 'sqlite_%'
        ORDER BY s.name, column_id
        ;""")
    indices_query = textwrap.dedent("""\
        -- Note: Also include the “sqlite_autoindex*” indices that are
        -- automatically created for UNIQUE and PRIMARY KEY constraints.
        SELECT   s.name AS index_name,
                 p.seqno AS index_column_sequence_number,
                 p.cid AS column_id,
                 p.name AS column_name
          FROM   sqlite_schema AS s
          JOIN   pragma_index_info(s.name) AS p
         WHERE   s.type = 'index'
        ORDER BY index_name ASC, index_column_sequence_number ASC
        ;""")
    with db_known_good:
        assert_that(
            db_unsafe.execute(tables_and_views_query).fetchall(),
            contains_exactly(*db_known_good.execute(tables_and_views_query).fetchall()),
            "Given file inconsistent: Unexpected tables or views")
        assert_that(
            db_unsafe.execute(indices_query).fetchall(),
            contains_exactly(*db_known_good.execute(indices_query).fetchall()),
            "Given file inconsistent: Unexpected indices")
    return user_schema_version


S = typing.TypeVar("S", LiteralString, str)

if hasattr(functools, "cache"):
    @functools.cache
    def cached_dedent(text: S) -> S:
        """Wraps textwrap.dedent() in a cache."""
        return textwrap.dedent(text)
else:  # Python 3.8 compatibility
    @functools.lru_cache(None)
    def cached_dedent(text: S) -> S:
        """Wraps textwrap.dedent() in an LRU cache."""
        return textwrap.dedent(text)
