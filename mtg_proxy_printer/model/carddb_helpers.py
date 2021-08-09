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
    "migrate_card_database",
]
MigrationScript = typing.Callable[[sqlite3.Connection], None]


def _migrate_9_to_10(db: sqlite3.Connection):
    # It wasn’t stored if a card was a front or back face. This information can only be obtained by re-populating
    # the database using fresh data from Scryfall.
    tables_to_clear = [
        "CardFace",
        "FaceName",
        "Card",
        '"Set"',
        "PrintLanguage",
        "UsedDownloadSettings",
    ]
    for table in tables_to_clear:
        db.execute(f"DELETE FROM {table}")
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
    db.execute(r"CREATE INDEX CardFace_scryfall_id_index ON CardFace (scryfall_id, is_front)")


def _migrate_14_to_15(db: sqlite3.Connection):
    db.execute(textwrap.dedent(r"""
        ALTER TABLE LastDatabaseUpdate ADD COLUMN
        newest_card_timestamp TIMESTAMP WITH TIME ZONE NULL;
        """))
    # Re-use the update timestamp. This is good enough for this purpose.
    db.execute("UPDATE LastDatabaseUpdate SET newest_card_timestamp = substr(update_timestamp, 0, 11)")


def _migrate_15_to_16(db: sqlite3.Connection):
    # These two indices were useless indices containing a UNIQUE column plus the integer primary key.
    # The UNIQUE constraint is already implemented by a UNIQUE INDEX, the PK is implicitly always part of the index.
    db.execute(r"DROP INDEX LanguageIndex")
    db.execute(r"DROP INDEX SetAbbreviationIndex")


def _migrate_16_to_17(db: sqlite3.Connection):
    db.execute(r"DROP INDEX CardFace_card_id_index")
    # Index was recommended by SQLite’s expert mode, so extend index CardFace_card_id_index with column is_front
    db.execute(r"CREATE INDEX CardFace_card_id_index ON CardFace (card_id, is_front)")


def _migrate_17_to_18(db: sqlite3.Connection):
    db.executescript(textwrap.dedent(r"""
        PRAGMA foreign_keys = OFF;
        BEGIN TRANSACTION;
        CREATE TABLE NewFaceName (
          -- The name of a card face in a given language. Cards are not renamed,
          -- so all Card entries share the same names across all reprints for a given language.
          face_name_id INTEGER PRIMARY KEY NOT NULL,
          card_name    TEXT NOT NULL,
          language_id  INTEGER NOT NULL REFERENCES PrintLanguage(language_id) ON UPDATE CASCADE ON DELETE CASCADE,
          UNIQUE (card_name, language_id)
        );
        CREATE TABLE NewCardFace (
          -- The printable card face of a specific card in a specific language. Is the front most of the time, 
          -- but can be the back face for double-faced cards.
          card_face_id INTEGER NOT NULL PRIMARY KEY,
          card_id INTEGER NOT NULL REFERENCES Card(card_id) ON UPDATE CASCADE ON DELETE CASCADE,
          set_id INTEGER NOT NULL REFERENCES "Set"(set_id) ON UPDATE CASCADE ON DELETE CASCADE,
          face_name_id INTEGER NOT NULL REFERENCES FaceName(face_name_id) ON UPDATE CASCADE ON DELETE CASCADE,
          is_front INTEGER NOT NULL CHECK (is_front IN (0, 1)) DEFAULT 1,
          collector_number TEXT NOT NULL,
          scryfall_id TEXT NOT NULL,
          highres_image INTEGER NOT NULL,  -- Boolean indicating that the card has high resolution images.
          png_image_uri TEXT NOT NULL,  -- URI pointing to the high resolution PNG image
          UNIQUE(face_name_id, set_id, card_id, is_front, collector_number)  -- Order important: Used to find matching sets
        );
        INSERT INTO NewFaceName (face_name_id, card_name, language_id) 
          SELECT face_name_id, card_name, language_id
          FROM FaceName;
        INSERT INTO NewCardFace 
          (card_face_id, card_id, set_id, face_name_id, is_front, collector_number, scryfall_id, highres_image, png_image_uri) 
        SELECT 
           card_face_id, card_id, set_id, face_name_id, is_front, collector_number, scryfall_id, highres_image, png_image_uri
        FROM CardFace;
        DROP VIEW AllPrintings;
        DROP TABLE FaceName;
        DROP TABLE CardFace;
        ALTER TABLE NewFaceName RENAME TO FaceName;
        ALTER TABLE NewCardFace RENAME TO CardFace;
        CREATE VIEW AllPrintings AS
          SELECT card_name, "set" AS set_code, set_name, "language", collector_number, scryfall_id,
            highres_image, is_front, png_image_uri, oracle_id
          FROM CardFace
          JOIN FaceName USING(face_name_id)
          JOIN "Set" USING (set_id)
          JOIN Card USING (card_id)
          JOIN PrintLanguage USING(language_id)
        ;
        -- Re-create some of the automatically deleted indexes.
        -- Now redundant indexes FaceNameCardNameToLanguageIndex and CardFaceIDLookup remain dropped.
        CREATE INDEX FaceNameLanguageToCardNameIndex ON FaceName(language_id, card_name COLLATE NOCASE);
        CREATE INDEX CardFaceToCollectorNumberIndex ON CardFace (face_name_id, set_id, collector_number);
        CREATE INDEX CardFace_card_id_index ON CardFace (card_id, is_front);
        CREATE INDEX CardFace_scryfall_id_index ON CardFace (scryfall_id, is_front);
        PRAGMA foreign_key_check;
        ANALYZE;
        PRAGMA foreign_keys = ON;
        COMMIT;
        VACUUM;
        BEGIN TRANSACTION;
        """))


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
        _migrate_14_to_15,
        _migrate_15_to_16,
        _migrate_16_to_17,
        _migrate_17_to_18,
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
