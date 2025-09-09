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
import pathlib
import socket
import sqlite3
import textwrap
import unittest.mock
import urllib.error

from hamcrest import *
import pytest

import mtg_proxy_printer.sqlite_helpers
from mtg_proxy_printer.sqlite_helpers import get_target_database_schema_version
from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.carddb_migrations import DatabaseMigrationTask, MIGRATION_SCRIPTS

# Pulled from check-in [43d8e4f754efc85d7f52ce9f8c87e93a6ed31e39de862a44a18d28b0590c113c].
# NOTE: Removed all SQL comments present in the original file.
OLDEST_SUPPORTED_SCHEMA = """\
PRAGMA user_version = 0000009;
PRAGMA foreign_keys = on;
BEGIN TRANSACTION;
CREATE TABLE PrintLanguage (
  language_id INTEGER PRIMARY KEY NOT NULL,
  "language" TEXT NOT NULL UNIQUE
);
CREATE INDEX LanguageIndex ON PrintLanguage ("language", language_id);
CREATE TABLE Card (
  card_id INTEGER PRIMARY KEY NOT NULL,
  oracle_id TEXT NOT NULL UNIQUE
);
CREATE TABLE FaceName (
  face_name_id INTEGER PRIMARY KEY NOT NULL,
  card_name    TEXT NOT NULL,
  language_id  INTEGER NOT NULL REFERENCES PrintLanguage(language_id) ON UPDATE CASCADE ON DELETE CASCADE
);
CREATE INDEX FaceNameLanguageToCardNameIndex ON FaceName(language_id, card_name COLLATE NOCASE);
CREATE INDEX FaceNameCardNameToLanguageIndex ON FaceName(card_name, language_id);
CREATE TABLE CardFace (
  card_face_id INTEGER NOT NULL PRIMARY KEY,
  card_id INTEGER NOT NULL REFERENCES Card(card_id) ON UPDATE CASCADE ON DELETE CASCADE,
  set_id INTEGER NOT NULL REFERENCES "Set"(set_id) ON UPDATE CASCADE ON DELETE CASCADE,
  face_name_id INTEGER NOT NULL REFERENCES FaceName(face_name_id) ON UPDATE CASCADE ON DELETE CASCADE,
  collector_number TEXT NOT NULL,
  scryfall_id TEXT NOT NULL,
  highres_image INTEGER NOT NULL,
  png_image_uri TEXT NOT NULL
);
CREATE INDEX CardFaceIDLookup ON CardFace (face_name_id, set_id, card_id);
CREATE INDEX CardFaceToCollectorNumberIndex ON CardFace (face_name_id, collector_number);
CREATE TABLE "Set" (
  set_id INTEGER PRIMARY KEY NOT NULL,
  "set" TEXT NOT NULL UNIQUE,
  set_name TEXT NOT NULL,
  set_uri TEXT NOT NULL
);
CREATE INDEX SetAbbreviationIndex ON "Set" ("set", set_id);
CREATE TABLE LastDatabaseUpdate (
  update_id        INTEGER NOT NULL PRIMARY KEY,
  update_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);
CREATE VIEW AllPrintings AS
  SELECT card_name, "set", "language", collector_number, scryfall_id, highres_image, png_image_uri
  FROM CardFace
  JOIN FaceName USING(face_name_id)
  JOIN "Set" USING (set_id)
  JOIN Card USING (card_id)
  JOIN PrintLanguage USING(language_id)
;
COMMIT;
"""


@pytest.fixture()
def old_db(tmp_path: pathlib.Path) -> pathlib.Path:
    target_path = tmp_path/"CardDatabase.sqlite3"
    db = sqlite3.Connection(target_path)
    db.executescript(OLDEST_SUPPORTED_SCHEMA)
    return target_path


def test_migrated_card_database_contains_expected_tables_and_views(old_db: pathlib.Path):
    card_db = CardDatabase(old_db)
    runner = DatabaseMigrationTask(card_db)
    runner.run()
    migrated_db = card_db.db
    fresh_db = mtg_proxy_printer.sqlite_helpers.open_database(":memory:", "carddb")
    assert_that(
        migrated_db.execute("PRAGMA user_version").fetchone()[0],
        is_(equal_to(get_target_database_schema_version("carddb"))),
    )
    # Query the table and view definitions.
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
    ;
    """)
    # Verify that the migrated database contains exactly the same columns as a database created from the newest schema.
    assert_that(
        migrated_db.execute(tables_and_views_query).fetchall(),
        contains_exactly(
            *fresh_db.execute(tables_and_views_query).fetchall()
        ))


def test_migrated_card_database_contains_expected_indices(old_db: pathlib.Path):
    card_db = CardDatabase(old_db)
    runner = DatabaseMigrationTask(card_db)
    runner.run()
    migrated_db = card_db.db
    fresh_db = mtg_proxy_printer.sqlite_helpers.open_database(":memory:", "carddb")
    assert_that(
        migrated_db.execute("PRAGMA user_version").fetchone()[0],
        is_(equal_to(get_target_database_schema_version("carddb"))),
    )
    # Note: Also include the “sqlite_autoindex*” indices that are
    # automatically created for UNIQUE and PRIMARY KEY constraints.
    indices_query = textwrap.dedent("""\
    SELECT   s.name AS index_name,
             p.seqno AS index_column_sequence_number,
             p.cid AS column_id,
             p.name AS column_name
      FROM   sqlite_schema AS s
      JOIN   pragma_index_info(s.name) AS p
     WHERE   s.type = 'index'
    ORDER BY index_name ASC, index_column_sequence_number ASC
    ;""")
    assert_that(
        migrated_db.execute(indices_query).fetchall(),
        contains_exactly(
            *fresh_db.execute(indices_query).fetchall()
        ))


@pytest.fixture
def card_db_at_version_21(old_db) -> pathlib.Path:
    card_db = CardDatabase(old_db)
    runner = DatabaseMigrationTask(card_db, {src: script for src, script in MIGRATION_SCRIPTS.items() if src < 21})
    runner.run()
    db = mtg_proxy_printer.sqlite_helpers.open_database(old_db, "carddb")
    assert_that(db.execute("PRAGMA user_version").fetchone()[0], is_(equal_to(21)), "Setup failed")
    today_tuple = str(datetime.date.today()),
    db.execute("INSERT INTO LastDatabaseUpdate (newest_card_timestamp) values (?)", today_tuple)
    db.commit()
    return old_db


@pytest.mark.parametrize("possible_error", [urllib.error.URLError("Test case"), socket.error()])
def test_patch_21_to_22_applies_correctly_without_network_access_using_dummy_values(
        card_db_at_version_21: pathlib.Path, possible_error: BaseException):
    card_db = CardDatabase(card_db_at_version_21)
    with unittest.mock.patch(
            "mtg_proxy_printer.async_tasks.card_info_downloader.ApiStreamTask.read_json_card_data_from") as mock:
        mock.side_effect = possible_error
        runner = DatabaseMigrationTask(card_db, {21: MIGRATION_SCRIPTS[21]})
        runner.run()
    db = mtg_proxy_printer.sqlite_helpers.open_database(card_db.db_path, "carddb")
    assert_that(db.execute("PRAGMA user_version").fetchone()[0], is_(equal_to(22)))
    mock.assert_called_once()
    assert_that(
        db.execute("SELECT MAX(update_id), reported_card_count FROM LastDatabaseUpdate").fetchall(),
        contains_exactly((1, 0))
    )


@pytest.mark.parametrize("expected", [1, 300000])
def test_patch_21_to_22_applies_with_network_access_and_requests_card_count_from_api(
        card_db_at_version_21: pathlib.Path, expected):
    card_db = CardDatabase(card_db_at_version_21)
    with unittest.mock.patch(
            "mtg_proxy_printer.async_tasks.card_info_downloader.ApiStreamTask.read_json_card_data_from") as mock:
        mock.return_value = iter((expected,))
        runner = DatabaseMigrationTask(card_db, {21: MIGRATION_SCRIPTS[21]})
        runner.run()
    db = mtg_proxy_printer.sqlite_helpers.open_database(card_db.db_path, "carddb")
    assert_that(db.execute("PRAGMA user_version").fetchone()[0], is_(equal_to(22)))
    mock.assert_called_once()
    assert_that(
        db.execute("SELECT MAX(update_id), reported_card_count FROM LastDatabaseUpdate").fetchall(),
        contains_exactly((1, expected))
    )
