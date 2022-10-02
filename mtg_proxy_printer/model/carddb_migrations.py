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

"""
This module contains the database migration logic that is used to upgrade the schema of existing card databases
to the newest schema version supported.

To add a new migration function:
- Write function _migrate_{source_version}_to_{target_version} that performs the schema migration
- Append an entry with a reference to the added function to the MIGRATION_SCRIPTS tuple
"""

import datetime
import socket
import sqlite3
import textwrap
import time
import typing
import urllib.error
import urllib.parse


import mtg_proxy_printer.sqlite_helpers
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

__all__ = [
    "migrate_card_database",
    "migrate_card_database_location",
]

MigrationScript = typing.Callable[[sqlite3.Connection], None]
MigrationScriptListing = typing.Tuple[typing.Tuple[int, MigrationScript], ...]


def _migrate_9_to_10(db: sqlite3.Connection):
    # Schema version 9 did not store if a card was a front or back face.
    # This information can only be obtained by re-populating
    # the database using fresh data from Scryfall.
    tables_to_clear = [
        "CardFace",
        "FaceName",
        "Card",
        '"Set"',
        "PrintLanguage",
    ]
    for table in tables_to_clear:
        db.execute(f"DELETE FROM {table};\n")
    db.execute("ALTER TABLE CardFace ADD COLUMN is_front INTEGER NOT NULL CHECK (is_front IN (0, 1)) DEFAULT 1;\n")
    db.execute("DROP VIEW AllPrintings;\n")
    db.execute(textwrap.dedent("""\
    CREATE VIEW AllPrintings AS
      SELECT card_name, "set", "language", collector_number, scryfall_id, highres_image, is_front, png_image_uri
      FROM CardFace
      JOIN FaceName USING(face_name_id)
      JOIN "Set" USING (set_id)
      JOIN Card USING (card_id)
      JOIN PrintLanguage USING(language_id)
    ;"""))


def _migrate_10_to_11(db: sqlite3.Connection):
    db.execute("DROP VIEW AllPrintings;\n")
    db.execute(textwrap.dedent("""\
    CREATE VIEW AllPrintings AS
      SELECT card_name, "set", set_name, "language", collector_number, scryfall_id, highres_image,
          is_front, png_image_uri, oracle_id
      FROM CardFace
      JOIN FaceName USING(face_name_id)
      JOIN "Set" USING (set_id)
      JOIN Card USING (card_id)
      JOIN PrintLanguage USING(language_id)
    ;"""))
    db.execute("CREATE INDEX CardFace_card_id_index ON CardFace (card_id);\n")


def _migrate_11_to_12(db: sqlite3.Connection):
    db.execute(textwrap.dedent("""\
    CREATE TABLE UsedDownloadSettings (
      -- This table contains the download filter settings used during the card data import
      setting TEXT NOT NULL PRIMARY KEY,
      "value" INTEGER NOT NULL CHECK ("value" IN (0, 1)) DEFAULT 1
    );
    """))


def _migrate_12_to_13(db: sqlite3.Connection):
    db.execute(textwrap.dedent("""\
    CREATE TABLE LastImageUseTimestamps (
      -- Used to store the last image use timestamp and usage count of each image.
      -- The usage count measures how often an image was part of a printed or exported document. Printing multiple
      -- copies in a document still counts as a single use. Saving/loading is not enough to count as a "use". 
      scryfall_id TEXT NOT NULL,
      is_front INTEGER NOT NULL CHECK (is_front in (0, 1)),
      usage_count INTEGER NOT NULL CHECK (usage_count > 0) DEFAULT 1,
      last_use_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (scryfall_id, is_front)
      -- No foreign key relation here. This table should be persistent across card data downloads
    );
    """))


def _migrate_13_to_14(db: sqlite3.Connection):
    db.execute("CREATE INDEX CardFace_scryfall_id_index ON CardFace (scryfall_id, is_front);\n")


def _migrate_14_to_15(db: sqlite3.Connection):
    db.execute(textwrap.dedent(r"""
        ALTER TABLE LastDatabaseUpdate ADD COLUMN
        newest_card_timestamp TIMESTAMP WITH TIME ZONE NULL;
        """))
    # Re-use the update timestamp. This is good enough for this purpose.
    db.execute("UPDATE LastDatabaseUpdate SET newest_card_timestamp = substr(update_timestamp, 0, 11);\n")


def _migrate_15_to_16(db: sqlite3.Connection):
    # These two indices were useless indices containing a UNIQUE column plus the integer primary key.
    # The UNIQUE constraint is already implemented by a UNIQUE INDEX, the PK is implicitly always part of the index.
    db.execute("DROP INDEX LanguageIndex;\n")
    db.execute("DROP INDEX SetAbbreviationIndex;\n")


def _migrate_16_to_17(db: sqlite3.Connection):
    db.execute("DROP INDEX CardFace_card_id_index;\n")
    # Index was recommended by SQLite’s expert mode, so extend index CardFace_card_id_index with column is_front
    db.execute("CREATE INDEX CardFace_card_id_index ON CardFace (card_id, is_front);\n")


def _migrate_17_to_18(db: sqlite3.Connection):
    db.executescript(textwrap.dedent("""\
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
      (card_face_id, card_id, set_id, face_name_id, is_front,
       collector_number, scryfall_id, highres_image, png_image_uri) 
    SELECT 
       card_face_id, card_id, set_id, face_name_id, is_front,
       collector_number, scryfall_id, highres_image, png_image_uri
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


def _migrate_18_to_19(db: sqlite3.Connection):
    db.executescript(textwrap.dedent("""\
    PRAGMA foreign_keys = OFF;
    BEGIN TRANSACTION;
    
    CREATE TABLE Printing (
      -- A specific printing of a card
      printing_id INTEGER PRIMARY KEY NOT NULL,
      card_id INTEGER NOT NULL REFERENCES Card(card_id) ON UPDATE CASCADE ON DELETE CASCADE,
      set_id INTEGER NOT NULL REFERENCES "Set"(set_id) ON UPDATE CASCADE ON DELETE CASCADE,
      collector_number TEXT NOT NULL,
      scryfall_id TEXT NOT NULL UNIQUE,
      -- Over-sized card indicator. Over-sized cards (value TRUE) are mostly useless for play,
      -- so store this to be able to warn the user
      is_oversized INTEGER NOT NULL CHECK (is_oversized IN (TRUE, FALSE)),
      -- Indicates if the card has high resolution images.
      highres_image INTEGER NOT NULL CHECK (highres_image IN (TRUE, FALSE))
    );
    CREATE INDEX Printing_Index_Find_Printing_From_Card_Data 
      ON Printing(card_id, set_id, collector_number);
      
    CREATE TABLE NewCardFace (
      -- The printable card face of a specific card in a specific language. Is the front most of the time,
      -- but can be the back face for double-faced cards.
      card_face_id INTEGER NOT NULL PRIMARY KEY,
      printing_id INTEGER NOT NULL REFERENCES Printing(printing_id) ON UPDATE CASCADE ON DELETE CASCADE,
      face_name_id INTEGER NOT NULL REFERENCES FaceName(face_name_id) ON UPDATE CASCADE ON DELETE CASCADE,
      is_front INTEGER NOT NULL CHECK (is_front IN (TRUE, FALSE)),
      png_image_uri TEXT NOT NULL,  -- URI pointing to the high resolution PNG image
      UNIQUE(face_name_id, printing_id, is_front)
    );
    DROP VIEW AllPrintings;
    
    -- Ignore duplicates based on the scryfall id. This is UNIQUE in the new schema, and duplicates based on that
    -- can be safely ignored. In the previous schema, all relevant fields for this query are equal, if the 
    -- scryfall id is equal.
    INSERT OR IGNORE INTO Printing(card_id, set_id, collector_number, scryfall_id, highres_image, is_oversized)
      SELECT card_id, set_id, collector_number, scryfall_id, highres_image,
        -- The patterns below match sets containing oversized cards.
        -- Note: Scryfall serves regularly sized images for the "% Championship" sets 
        -- despite being marked as "oversized". Thus those are explicitly not matched.  
        set_name LIKE '% Oversized' OR set_name LIKE '% Schemes' OR set_name LIKE '% Planes'
      FROM CardFace JOIN "Set" USING (set_id)
    ;
    
    -- Joining USING (scryfall_id) is fine, because that is UNIQUE in Printing, therefore not creating additional
    -- rows.
    INSERT OR IGNORE INTO NewCardFace (printing_id, face_name_id, is_front, png_image_uri)
      SELECT printing_id, face_name_id, is_front, png_image_uri
      FROM CardFace JOIN Printing USING (scryfall_id)
    ;
    
    DROP TABLE CardFace;
    ALTER TABLE NewCardFace RENAME TO CardFace;
    CREATE VIEW AllPrintings AS
      SELECT card_name, "set" AS set_code, set_name, "language", collector_number, scryfall_id,
        highres_image, is_front, is_oversized, png_image_uri, oracle_id
      FROM Card
      JOIN Printing USING (card_id)
      JOIN "Set" USING (set_id)
      JOIN CardFace USING (printing_id)
      JOIN FaceName USING(face_name_id)
      JOIN PrintLanguage USING(language_id)
    ;
    PRAGMA foreign_key_check;
    ANALYZE;
    PRAGMA foreign_keys = ON;
    COMMIT;
    VACUUM;
    BEGIN TRANSACTION;
    """))


def _migrate_19_to_20(db: sqlite3.Connection):
    db.execute(
        "CREATE INDEX CardFace_Index_for_card_lookup_by_scryfall_id_and_is_front ON CardFace(is_front, printing_id);"
    )


def _migrate_20_to_21(db: sqlite3.Connection):
    db.executescript(textwrap.dedent("""\
    PRAGMA foreign_keys = OFF;
    BEGIN TRANSACTION;
    DROP VIEW AllPrintings;
    CREATE TABLE CardFaceNew (
      -- The printable card face of a specific card in a specific language. Is the front most of the time,
      -- but can be the back face for double-faced cards.
      card_face_id INTEGER NOT NULL PRIMARY KEY,
      printing_id INTEGER NOT NULL REFERENCES Printing(printing_id) ON UPDATE CASCADE ON DELETE CASCADE,
      face_name_id INTEGER NOT NULL REFERENCES FaceName(face_name_id) ON UPDATE CASCADE ON DELETE CASCADE,
      is_front INTEGER NOT NULL CHECK (is_front IN (TRUE, FALSE)),
      png_image_uri TEXT NOT NULL,  -- URI pointing to the high resolution PNG image
      -- Enumerates the face on a card. Used to match the exact same face across translated, multi-faced cards
      face_number INTEGER NOT NULL CHECK (face_number >= 0),
      UNIQUE(face_name_id, printing_id, is_front)
    );
    INSERT INTO CardFaceNew (card_face_id, printing_id, face_name_id, is_front, png_image_uri, face_number)
    SELECT card_face_id, printing_id, face_name_id, is_front, png_image_uri, 
           row_number() over (partition by printing_id ORDER BY card_face_id) -1 as face_number
    FROM FaceName JOIN CardFace USING (face_name_id) JOIN Printing USING (printing_id);
    DROP TABLE CardFace;
    ALTER TABLE CardFaceNew RENAME TO CardFace;
    
    CREATE INDEX CardFace_Index_for_card_lookup_by_scryfall_id_and_is_front ON CardFace(is_front, printing_id);
    
    CREATE VIEW AllPrintings AS
      SELECT card_name, "set" AS set_code, set_name, "language", collector_number, scryfall_id,
        highres_image, face_number, is_front, is_oversized, png_image_uri, oracle_id
      FROM Card
      JOIN Printing USING (card_id)
      JOIN "Set" USING (set_id)
      JOIN CardFace USING (printing_id)
      JOIN FaceName USING(face_name_id)
      JOIN PrintLanguage USING(language_id)
    ;
    PRAGMA foreign_key_check;
    ANALYZE;
    PRAGMA foreign_keys = ON;
    COMMIT;
    VACUUM;
    BEGIN TRANSACTION;
    """))


def _migrate_21_to_22(db: sqlite3.Connection):
    # Full edit procedure not needed here, because the table has no indices or foreign keys associated

    class CardDatabaseMock(typing.NamedTuple):
        db: sqlite3.Connection

        def commit_transaction(self):
            self.db.commit()

    # Import locally to break a cyclic dependency
    import mtg_proxy_printer.card_info_downloader
    dw = mtg_proxy_printer.card_info_downloader.CardInfoDatabaseImportWorker(CardDatabaseMock(db))
    updates = db.execute("SELECT update_id, update_timestamp FROM LastDatabaseUpdate;\n")
    data = []
    for id_, timestamp in updates:
        url_parameters = urllib.parse.urlencode({
            "include_multilingual": "true",
            "include_variations": "true",
            "include_extras": "true",
            "unique": "prints",
            "q": f"date>1970-01-01 date<={datetime.datetime.fromisoformat(timestamp).date()}"
        })
        try:
            card_count = next(dw.read_json_card_data_from_url(
                f'https://api.scryfall.com/cards/search?{url_parameters}', 'total_cards'
            ))
        except (urllib.error.URLError, socket.error):
            card_count = 0
        data.append((id_, timestamp, card_count))
        time.sleep(0.1)  # Rate limit the requests to 10 per second, according to the Scryfall API usage recommendations

    logger.info(f"Acquired data for upgrade to schema version 22: {data}")
    db.execute(textwrap.dedent("""\
    CREATE TABLE LastDatabaseUpdateNew (
      -- Contains the history of all performed card data updates
      update_id             INTEGER NOT NULL PRIMARY KEY,
      update_timestamp      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP),
      reported_card_count   INTEGER NOT NULL CHECK (reported_card_count >= 0)
    );
    """))
    db.executemany(
        "INSERT INTO LastDatabaseUpdateNew (update_id, update_timestamp, reported_card_count) VALUES (?, ?, ?);\n",
        data
    )
    db.execute("DROP TABLE LastDatabaseUpdate;\n")
    db.execute(" ALTER TABLE LastDatabaseUpdateNew RENAME TO LastDatabaseUpdate;\n")


def _migrate_22_to_23(db: sqlite3.Connection):
    db.execute(textwrap.dedent("""\
    CREATE TABLE RemovedPrintings (
      scryfall_id TEXT NOT NULL PRIMARY KEY,
      -- Required to keep the language when migrating a card to a known printing, because it is otherwise unknown.
      language TEXT NOT NULL,
      oracle_id TEXT NOT NULL
    );
    """))


def _migrate_23_to_24(db: sqlite3.Connection):
    db.executescript(textwrap.dedent("""\
    BEGIN TRANSACTION;
    ALTER TABLE Printing ADD COLUMN is_hidden INTEGER NOT NULL CHECK (is_hidden IN (TRUE, FALSE)) DEFAULT FALSE;
    ALTER TABLE FaceName ADD COLUMN is_hidden INTEGER NOT NULL CHECK (is_hidden IN (TRUE, FALSE)) DEFAULT FALSE;
    CREATE TABLE DisplayFilters (
      filter_id INTEGER NOT NULL PRIMARY KEY,
      filter_name TEXT NOT NULL UNIQUE,
      filter_active INTEGER NOT NULL CHECK (filter_active IN (TRUE, FALSE))
    );
    DROP TABLE UsedDownloadSettings;
    CREATE TABLE PrintingDisplayFilter (
      printing_id    INTEGER NOT NULL REFERENCES Printing (printing_id) ON DELETE CASCADE,
      filter_id      INTEGER NOT NULL REFERENCES DisplayFilters (filter_id) ON DELETE CASCADE,
      filter_applies INTEGER NOT NULL CHECK (filter_applies IN (TRUE, FALSE)),
      PRIMARY KEY (printing_id, filter_id)
    );
    CREATE VIEW HiddenPrintings AS
      SELECT printing_id, sum(filter_applies * filter_active) > 0 AS should_be_hidden
      FROM PrintingDisplayFilter
      JOIN DisplayFilters USING (filter_id)
      GROUP BY printing_id
    ;
    DROP VIEW AllPrintings;
    CREATE VIEW AllPrintings AS
      SELECT card_name, "set" AS set_code, set_name, "language", collector_number, scryfall_id,
             highres_image, face_number, is_front, is_oversized, png_image_uri, oracle_id
      FROM Card
      JOIN Printing USING (card_id)
      JOIN "Set" USING (set_id)
      JOIN CardFace USING (printing_id)
      JOIN FaceName USING (face_name_id)
      JOIN PrintLanguage USING (language_id)
      WHERE Printing.is_hidden IS FALSE
        AND FaceName.is_hidden IS FALSE
    ;
    CREATE INDEX Printing_is_hidden
      ON Printing(printing_id, is_hidden);
    DROP INDEX FaceNameLanguageToCardNameIndex;
    CREATE INDEX FaceNameLanguageToCardNameIndex ON FaceName(language_id, is_hidden, card_name COLLATE NOCASE);
    ANALYZE;
    """))


def _migrate_24_to_25(db: sqlite3.Connection):
    db.executescript(textwrap.dedent("""\
    BEGIN TRANSACTION;
    DROP VIEW HiddenPrintings;
    CREATE TABLE PrintingDisplayFilter2 (
      -- Stores which filter applies to which printing.
      printing_id    INTEGER NOT NULL REFERENCES Printing (printing_id) ON DELETE CASCADE,
      filter_id      INTEGER NOT NULL REFERENCES DisplayFilters (filter_id) ON DELETE CASCADE,
      filter_applies INTEGER NOT NULL CHECK (filter_applies IN (TRUE, FALSE)),
      PRIMARY KEY (printing_id, filter_id)
    ) WITHOUT ROWID;
    INSERT INTO PrintingDisplayFilter2 (printing_id, filter_id, filter_applies)
      SELECT printing_id, filter_id, filter_applies
      FROM PrintingDisplayFilter;
    DROP TABLE PrintingDisplayFilter;
    ALTER TABLE PrintingDisplayFilter2 RENAME TO PrintingDisplayFilter;
    CREATE VIEW HiddenPrintings AS
      SELECT printing_id, sum(filter_applies * filter_active) > 0 AS should_be_hidden
      FROM PrintingDisplayFilter
      JOIN DisplayFilters USING (filter_id)
      GROUP BY printing_id
    ;
    COMMIT;
    VACUUM;
    BEGIN TRANSACTION;
    """))


def _migrate_25_to_26(db: sqlite3.Connection):
    db.executescript(textwrap.dedent("""\
    PRAGMA foreign_keys = OFF;
    BEGIN TRANSACTION;
    CREATE TABLE "Set2" (
      set_id   INTEGER PRIMARY KEY NOT NULL,
      set_code TEXT NOT NULL UNIQUE,
      set_name TEXT NOT NULL,
      set_uri  TEXT NOT NULL,
      release_date TEXT NOT NULL,
      wackiness_score INTEGER NOT NULL CHECK (wackiness_score >= 0)
    );
    INSERT INTO "Set2" (set_id, set_code, set_name, set_uri, release_date, wackiness_score)
      -- Default to neutral values for new columns. Subsequent card data updates will update the values accordingly.
      -- Use a date far in the future, because the importer can only date sets back.
      SELECT set_id, "set", set_name, set_uri, '9999-01-01', 0
      FROM "Set";
    DROP VIEW AllPrintings;
    -- Rename the old table first, to update the FOREIGN KEY relation in the Printing table. Then drop and replace
    -- it with the new table definition. Without this, the Printing table will still hold a reference to the old name.
    ALTER TABLE "Set" RENAME TO MTGSet;
    DROP TABLE MTGSet;
    ALTER TABLE "Set2" RENAME TO MTGSet;
    CREATE VIEW  AllPrintings AS
      SELECT card_name, set_code, set_name, "language", collector_number, scryfall_id,
             highres_image, face_number, is_front, is_oversized, png_image_uri, oracle_id, release_date, wackiness_score
      FROM Card
      JOIN Printing USING (card_id)
      JOIN MTGSet   USING (set_id)
      JOIN CardFace USING (printing_id)
      JOIN FaceName USING (face_name_id)
      JOIN PrintLanguage USING (language_id)
      WHERE Printing.is_hidden IS FALSE
        AND FaceName.is_hidden IS FALSE
    ;
    PRAGMA foreign_key_check;
    COMMIT;
    PRAGMA foreign_keys = ON;
    ANALYZE;
    VACUUM;
    BEGIN TRANSACTION;
    """))


def _migrate_26_to_27(db: sqlite3.Connection):
    for statement in [
        "UPDATE MTGSet SET release_date = '9999-01-01' WHERE release_date = '1970-01-01'",
        "CREATE INDEX FaceName_for_translation ON FaceName(language_id, card_name DESC)",
        "CREATE INDEX CardFace_for_translation ON CardFace(face_name_id, face_number, printing_id)",
        "ANALYZE",
        "DROP VIEW AllPrintings",
        textwrap.dedent("""\
        CREATE VIEW VisiblePrintings AS
          SELECT card_name, set_code, set_name, "language", collector_number, scryfall_id,
                 highres_image, face_number, is_front, is_oversized, png_image_uri, oracle_id, release_date, wackiness_score
          FROM Card
          JOIN Printing USING (card_id)
          JOIN MTGSet   USING (set_id)
          JOIN CardFace USING (printing_id)
          JOIN FaceName USING (face_name_id)
          JOIN PrintLanguage USING (language_id)
          WHERE Printing.is_hidden IS FALSE
            AND FaceName.is_hidden IS FALSE"""),
        textwrap.dedent("""\
        CREATE VIEW AllPrintings AS
          SELECT card_name, set_code, set_name, "language", collector_number, scryfall_id, highres_image, face_number,
                is_front, is_oversized, png_image_uri, oracle_id, release_date, wackiness_score, Printing.is_hidden
          FROM Card
          JOIN Printing USING (card_id)
          JOIN MTGSet   USING (set_id)
          JOIN CardFace USING (printing_id)
          JOIN FaceName USING (face_name_id)
          JOIN PrintLanguage USING (language_id)"""),
    ]:
        db.execute(f"{statement};\n")


def _migrate_27_to_28(db: sqlite3.Connection):
    for statement in [
        "DROP VIEW AllPrintings",
        "DROP VIEW VisiblePrintings",
        textwrap.dedent("""\
        CREATE VIEW VisiblePrintings AS
          SELECT card_name, set_code, set_name, "language", collector_number, scryfall_id, highres_image, face_number,
                 is_front, is_oversized, png_image_uri, oracle_id, release_date, wackiness_score, release_date
          FROM Card
          JOIN Printing USING (card_id)
          JOIN MTGSet   USING (set_id)
          JOIN CardFace USING (printing_id)
          JOIN FaceName USING (face_name_id)
          JOIN PrintLanguage USING (language_id)
          WHERE Printing.is_hidden IS FALSE
            AND FaceName.is_hidden IS FALSE"""),
        textwrap.dedent("""\
        CREATE VIEW AllPrintings AS
          SELECT card_name, set_code, set_name, "language", collector_number, scryfall_id, highres_image, face_number,
                 is_front, is_oversized, png_image_uri, oracle_id, release_date, wackiness_score, Printing.is_hidden,
                 release_date
          FROM Card
          JOIN Printing USING (card_id)
          JOIN MTGSet   USING (set_id)
          JOIN CardFace USING (printing_id)
          JOIN FaceName USING (face_name_id)
          JOIN PrintLanguage USING (language_id)"""),
    ]:
        db.execute(statement)


def _migrate_28_to_29(db: sqlite3.Connection):
    db.execute("DROP VIEW HiddenPrintings\n")
    db.execute(textwrap.dedent("""\
    CREATE TABLE PrintingDisplayFilter2 (
      -- Stores which filter applies to which printing.
      printing_id    INTEGER NOT NULL REFERENCES Printing (printing_id) ON DELETE CASCADE,
      filter_id      INTEGER NOT NULL REFERENCES DisplayFilters (filter_id) ON DELETE CASCADE,
      PRIMARY KEY (printing_id, filter_id)
    ) WITHOUT ROWID;
    """))
    db.execute(textwrap.dedent("""\
    INSERT INTO PrintingDisplayFilter2 (printing_id, filter_id)
      SELECT printing_id, filter_id
      FROM PrintingDisplayFilter
      WHERE filter_applies IS TRUE
    """))
    db.execute("DROP TABLE PrintingDisplayFilter\n")
    db.execute("ALTER TABLE PrintingDisplayFilter2 RENAME TO PrintingDisplayFilter\n")
    db.execute(textwrap.dedent("""\
    CREATE VIEW HiddenPrintingIDs AS
      SELECT printing_id
        FROM PrintingDisplayFilter
        JOIN DisplayFilters USING (filter_id)
        WHERE filter_active IS TRUE
        GROUP BY printing_id
    ;
    """))
    db.execute("DROP VIEW AllPrintings\n")
    db.execute(textwrap.dedent("""\
    CREATE VIEW AllPrintings AS
      SELECT card_name, set_code, set_name, "language", collector_number, scryfall_id, highres_image, face_number,
             is_front, is_oversized, png_image_uri, oracle_id, release_date, wackiness_score, Printing.is_hidden
      FROM Card
      JOIN Printing USING (card_id)
      JOIN MTGSet   USING (set_id)
      JOIN CardFace USING (printing_id)
      JOIN FaceName USING (face_name_id)
      JOIN PrintLanguage USING (language_id)
    ;
    """))


MIGRATION_SCRIPTS: MigrationScriptListing = (
    # First component of each tuple contains the source schema version, second contains the migration script function.
    # These MUST be ordered by source schema version, otherwise the migration logic breaks. In other words: APPEND only.
    (9, _migrate_9_to_10),
    (10, _migrate_10_to_11),
    (11, _migrate_11_to_12),
    (12, _migrate_12_to_13),
    (13, _migrate_13_to_14),
    (14, _migrate_14_to_15),
    (15, _migrate_15_to_16),
    (16, _migrate_16_to_17),
    (17, _migrate_17_to_18),
    (18, _migrate_18_to_19),
    (19, _migrate_19_to_20),
    (20, _migrate_20_to_21),
    (21, _migrate_21_to_22),
    (22, _migrate_22_to_23),
    (23, _migrate_23_to_24),
    (24, _migrate_24_to_25),
    (25, _migrate_25_to_26),
    (26, _migrate_26_to_27),
    (27, _migrate_27_to_28),
    (28, _migrate_28_to_29),
)


def migrate_card_database_location():
    from mtg_proxy_printer.model.carddb import DEFAULT_DATABASE_LOCATION, OLD_DATABASE_LOCATION
    if DEFAULT_DATABASE_LOCATION.exists() and OLD_DATABASE_LOCATION.exists():
        logger.warning(f"A card database at both the new location '{DEFAULT_DATABASE_LOCATION}' and the old location "
                       f"'{OLD_DATABASE_LOCATION}' was found. Doing nothing")
        return
    if not DEFAULT_DATABASE_LOCATION.exists() and OLD_DATABASE_LOCATION.exists():
        logger.info(f"Migrating card database location from '{OLD_DATABASE_LOCATION}' to '{DEFAULT_DATABASE_LOCATION}'")
        DEFAULT_DATABASE_LOCATION.parent.mkdir(exist_ok=True, parents=True)
        OLD_DATABASE_LOCATION.rename(DEFAULT_DATABASE_LOCATION)


def migrate_card_database(db: sqlite3.Connection, migration_scripts: MigrationScriptListing = MIGRATION_SCRIPTS):
    """
    Upgrades the database schema of the given Card Database to the latest supported schema version.

    Given migration scripts are only executed, if their associated starting schema version matches the current database
    schema version right before it is executed. Each migration script must upgrade to the next schema version. Functions
    that combine multiple version upgrades in one SQL script are not supported.

    :param db: card database, given as a plain sqlite3 database connection object
    :param migration_scripts: List of migration script functions to run, if applicable. Defaults to a built-in list of
      migration scripts. Should only be passed explicitly for testing purposes.
    """
    begin_schema_version = db.execute("PRAGMA user_version\n").fetchone()[0]
    if mtg_proxy_printer.sqlite_helpers.check_database_schema_version(db, "carddb") > 0:
        logger.info(f"Database schema outdated, running database migrations. {begin_schema_version=}")
        if migration_scripts is not MIGRATION_SCRIPTS:
            logger.debug(f"Custom migration scripts passed: {migration_scripts}")
    else:
        logger.info("Database schema recent, not running any database migrations")
        return
    for source_version, migration_script in migration_scripts:
        if db.execute("PRAGMA user_version\n").fetchone()[0] == source_version:
            logger.info(f"Running migration task for schema version {source_version}")
            db.execute("BEGIN TRANSACTION\n")
            migration_script(db)
            db.execute(f"PRAGMA user_version = {source_version + 1}\n")
            db.commit()
    current_schema_version = db.execute("PRAGMA user_version\n").fetchone()[0]
    logger.info(f"Finished database migrations, rebuilding database. {current_schema_version=}")
    db.execute("VACUUM\n")
    logger.info("Rebuild done.")
