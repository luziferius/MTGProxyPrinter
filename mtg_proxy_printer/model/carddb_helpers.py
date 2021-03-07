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

import sqlite3
import textwrap
import typing

import mtg_proxy_printer.sqlite_helpers
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

__all__ = [
    "clear_database",
    "migrate_card_database",
]
MigrationScript = typing.Callable[[sqlite3.Connection], None]


def _migrate_9_to_10(db: sqlite3.Connection):
    # It wasn’t stored if a card was a front or back face. This information can only be obtained by re-populating
    # the database using fresh data from Scryfall.
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


def _migrate_10_to_11(db: sqlite3.Connection):
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


def _migrate_11_to_12(db: sqlite3.Connection):
    db.execute(textwrap.dedent(r"""
    CREATE TABLE UsedDownloadSettings (
      -- This table contains the download filter settings used during the card data import
      setting TEXT NOT NULL PRIMARY KEY,
      "value" INTEGER NOT NULL CHECK ("value" IN (0, 1)) DEFAULT 1
    );
    """))
    # Import now to avoid a cyclic import. This function is only required during this specific migration task
    from mtg_proxy_printer.card_info_downloader import store_download_settings
    # Guess the used settings based on the current ones. This is good enough for this migration task
    store_download_settings(db)


def _migrate_12_to_13(db: sqlite3.Connection):
    db.execute(textwrap.dedent(r"""
    CREATE TABLE LastImageUseTimestamps (
      -- Used to store the last image use timestamp and usage count of each image.
      -- The usage count measures how often an image was part of a printed or exported document. Printing multiple copies
      -- in a document still counts as a single use. Saving/loading is not enough to count as a "use". 
      scryfall_id TEXT NOT NULL,
      is_front INTEGER NOT NULL CHECK (is_front in (0, 1)),
      usage_count INTEGER NOT NULL CHECK (usage_count > 0) DEFAULT 1,
      last_use_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (scryfall_id, is_front)
      -- No foreign key relation here. This table should be persistent across card data downloads
    );
    """))


def _migrate_13_to_14(db: sqlite3.Connection):
    db.execute(textwrap.dedent(r"CREATE INDEX CardFace_scryfall_id_index ON CardFace (scryfall_id, is_front);"))


def migrate_card_database(db: sqlite3.Connection):
    current_schema_version = db.execute("PRAGMA user_version").fetchone()[0]
    needs_update = mtg_proxy_printer.sqlite_helpers.check_database_schema_version(db, "carddb") > 0
    if needs_update:
        logger.info(f"Database schema outdated, running database migrations. {current_schema_version=}")
    else:
        logger.info("Database schema recent, not running any database migrations")
        return
    migration_scripts: typing.List[MigrationScript] = [
        _migrate_9_to_10,
        _migrate_10_to_11,
        _migrate_11_to_12,
        _migrate_12_to_13,
        _migrate_13_to_14,
    ]
    for source_version, migrator_script in enumerate(migration_scripts, start=9):
        if db.execute("PRAGMA user_version").fetchone()[0] == source_version:
            logger.info(f"Running migration task for schema version {source_version}")
            db.execute("BEGIN TRANSACTION")
            migrator_script(db)
            db.commit()
            db.execute(f"PRAGMA user_version = {source_version+1}")

    if needs_update:
        current_schema_version = db.execute("PRAGMA user_version").fetchone()[0]
        logger.info(f"Finished database migrations. {current_schema_version=}")


def clear_database(db: sqlite3.Connection, parent=None):
    """
    Clears all cards in the database. This allows re-populating with fresh data from Scryfall.
    This does not clear the LastDatabaseUpdate table to keep the history of performed updates.
    """
    # Implementation note: Specify all tables by hand, traversing the FOREIGN KEY constraint inducing DAG from
    # leaves to roots. This allows SQLite to possibly use the TRUNCATE optimization
    # (https://sqlite.org/lang_delete.html#the_truncate_optimization) and not spend a whole minute clearing
    # the tables in a way that doesn’t break foreign keys during the process.
    logger.info("Clearing current database content")
    tables_to_clear = [
        "CardFace",
        "FaceName",
        "Card",
        '"Set"',
        "PrintLanguage",
        "UsedDownloadSettings",
    ]
    for table in tables_to_clear:
        logger.debug(f"Clearing table {table}")
        db.execute(f"DELETE FROM {table}\n")
        if parent is not None:
            if not parent.should_run:
                logger.info("Aborting clear_database()")
                break
