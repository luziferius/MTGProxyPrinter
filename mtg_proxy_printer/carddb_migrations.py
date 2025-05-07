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


"""
This module contains the database migration logic that is used to upgrade the schema of existing card databases
to the newest schema version supported.

To add a new migration, place a MigrationScript instance in the MIGRATION_SCRIPTS dict,
using the source schema version as the dict key.
"""

import dataclasses
import datetime
import socket
import sqlite3
import time
import typing
import urllib.error
import urllib.parse
from textwrap import dedent
from typing import List, Dict, Union, Tuple, Any, Generator, Callable, Iterable

from PyQt5.QtCore import QCoreApplication, Qt

try:
    from typing import LiteralString
except ImportError:
    from typing_extensions import LiteralString

from mtg_proxy_printer.progress_meter import ProgressMeter
from mtg_proxy_printer.runner import Runnable, ProgressSignalContainer
import mtg_proxy_printer.sqlite_helpers
from mtg_proxy_printer.logger import get_logger
from mtg_proxy_printer.model.carddb import CardDatabase, with_database_write_lock

if typing.TYPE_CHECKING:
    from mtg_proxy_printer.ui.main_window import MainWindow


logger = get_logger(__name__)
del get_logger
QueuedConnection = Qt.ConnectionType.QueuedConnection

__all__ = [
    "DatabaseMigrationRunner",
    "migrate_card_database_location",
]
# Overwrite the dedent signature for type hinting purposes.
# Original dedent is annotated as str -> str, so overwrite that with LiteralString -> LiteralString,
# allowing the type checker to detect SQL injections
dedent: Callable[[LiteralString], LiteralString]
Statement = Union[LiteralString, Tuple[LiteralString, List[Tuple[Any, ...]]]]


@dataclasses.dataclass
class MigrationScript:
    script: List[Statement] = None

    def get_script(self, db: sqlite3.Connection, suffix: LiteralString, progress_meter: ProgressMeter) -> List[Statement]:
        """Returns the script to run. Can be overridden by subclasses to allow dynamic behavior"""
        if self.script is None:
            raise RuntimeError("BUG: Migration script is None. Either not provided or this function wasn't overridden")
        return self.script

    def script_length(self, db: sqlite3.Connection, suffix: LiteralString) -> int:
        """
        Returns the number of statements in the script. Defaults to the passed script length.

        Non-static migration scripts can return a custom number that includes non-statement tasks that consume time
        """
        return len(self.script)


class Migrate_21_to_22(MigrationScript):

    def get_script(
            self, db: sqlite3.Connection, suffix: LiteralString, progress_meter: ProgressMeter) -> List[Statement]:
        return list(self._migrate_21_to_22(db, suffix, progress_meter))

    @staticmethod
    def _migrate_21_to_22(
            db: sqlite3.Connection, suffix: LiteralString, progress_meter: ProgressMeter
    ) -> Generator[Statement, None, None]:
        # Full edit procedure not needed here, because the table has no indices or foreign keys associated
        # Import locally to break a cyclic dependency
        import mtg_proxy_printer.card_info_downloader
        aw = mtg_proxy_printer.card_info_downloader.ApiStreamWorker()
        updates: Iterable[Tuple[int, datetime.datetime]] = db.execute(
            "SELECT update_id, update_timestamp FROM LastDatabaseUpdate"+suffix)
        data = []
        for id_, timestamp in updates:
            url_parameters = urllib.parse.urlencode({
                "include_multilingual": "true",
                "include_variations": "true",
                "include_extras": "true",
                "unique": "prints",
                "q": f"date>1970-01-01 date<={timestamp.date()}"
            })
            try:
                card_count = next(aw.read_json_card_data_from_url(
                    f'https://api.scryfall.com/cards/search?{url_parameters}', 'total_cards'
                ))
            except (urllib.error.URLError, socket.error):
                card_count = 0
            data.append((id_, timestamp.isoformat(), card_count))
            # Rate limit the requests to 10 per second, according to the Scryfall API usage recommendations
            time.sleep(0.1)
            progress_meter.advance()

        logger.info(f"Acquired data for upgrade to schema version 22: {data}")
        yield dedent("""\
        CREATE TABLE LastDatabaseUpdateNew (
          -- Contains the history of all performed card data updates
          update_id             INTEGER NOT NULL PRIMARY KEY,
          update_timestamp      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP),
          reported_card_count   INTEGER NOT NULL CHECK (reported_card_count >= 0)
        )""")
        yield (
            "INSERT INTO LastDatabaseUpdateNew (update_id, update_timestamp, reported_card_count) VALUES (?, ?, ?)",
            data
        )
        yield "DROP TABLE LastDatabaseUpdate"
        yield "ALTER TABLE LastDatabaseUpdateNew RENAME TO LastDatabaseUpdate"

    def script_length(self, db: sqlite3.Connection, suffix: LiteralString) -> int:
        api_call_count = db.execute("SELECT count(42) FROM LastDatabaseUpdate" + suffix).fetchone()[0]
        return 4 + api_call_count  # 4 SQL statements in the script


MIGRATION_SCRIPTS: Dict[int, MigrationScript] = {
    9: MigrationScript([
        # Schema version 9 did not store if a card was a front or back face.
        # This information can only be obtained by re-populating
        # the database using fresh data from Scryfall.
        "DELETE FROM CardFace",
        "DELETE FROM FaceName",
        "DELETE FROM Card",
        'DELETE FROM "Set"',
        "DELETE FROM PrintLanguage",
        "ALTER TABLE CardFace ADD COLUMN is_front INTEGER NOT NULL CHECK (is_front IN (0, 1)) DEFAULT 1",
        "DROP VIEW AllPrintings",
        dedent("""\
        CREATE VIEW AllPrintings AS
          SELECT card_name, "set", "language", collector_number, scryfall_id, highres_image, is_front, png_image_uri
          FROM CardFace
          JOIN FaceName USING(face_name_id)
          JOIN "Set" USING (set_id)
          JOIN Card USING (card_id)
          JOIN PrintLanguage USING(language_id)"""),
    ]),
    10: MigrationScript([
        "DROP VIEW AllPrintings",
        dedent("""\
        CREATE VIEW AllPrintings AS
          SELECT card_name, "set", set_name, "language", collector_number, scryfall_id, highres_image,
              is_front, png_image_uri, oracle_id
          FROM CardFace
          JOIN FaceName USING(face_name_id)
          JOIN "Set" USING (set_id)
          JOIN Card USING (card_id)
          JOIN PrintLanguage USING(language_id)"""),
        "CREATE INDEX CardFace_card_id_index ON CardFace (card_id)",
    ]),
    11: MigrationScript([
        dedent("""\
        CREATE TABLE UsedDownloadSettings (
          -- This table contains the download filter settings used during the card data import
          setting TEXT NOT NULL PRIMARY KEY,
          "value" INTEGER NOT NULL CHECK ("value" IN (0, 1)) DEFAULT 1
        )"""),
    ]),
    12: MigrationScript([
        dedent("""\
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
        )"""),
    ]),
    13: MigrationScript([
        "CREATE INDEX CardFace_scryfall_id_index ON CardFace (scryfall_id, is_front)",
    ]),
    14: MigrationScript([
        "ALTER TABLE LastDatabaseUpdate ADD COLUMN newest_card_timestamp TIMESTAMP WITH TIME ZONE NULL",
        # Re-use the update timestamp. This is good enough for this purpose.
        "UPDATE LastDatabaseUpdate SET newest_card_timestamp = substr(update_timestamp, 0, 11)",
    ]),
    15: MigrationScript([
        # These two indices were useless indices containing a UNIQUE column plus the integer primary key.
        # The UNIQUE constraint is already implemented by a UNIQUE INDEX, the PK is implicitly always part of the index.
        "DROP INDEX LanguageIndex",
        "DROP INDEX SetAbbreviationIndex",
    ]),
    16: MigrationScript([
        "DROP INDEX CardFace_card_id_index",
        # Index was recommended by SQLite’s expert mode, so extend index CardFace_card_id_index with column is_front
        "CREATE INDEX CardFace_card_id_index ON CardFace (card_id, is_front)",
    ]),
    17: MigrationScript([
        "PRAGMA foreign_keys = OFF",
        dedent("""\
        CREATE TABLE NewFaceName (
          -- The name of a card face in a given language. Cards are not renamed,
          -- so all Card entries share the same names across all reprints for a given language.
          face_name_id INTEGER PRIMARY KEY NOT NULL,
          card_name    TEXT NOT NULL,
          language_id  INTEGER NOT NULL REFERENCES PrintLanguage(language_id) ON UPDATE CASCADE ON DELETE CASCADE,
          UNIQUE (card_name, language_id)
        )"""),
        dedent("""\
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
        )"""),
        dedent("""\
        INSERT INTO NewFaceName (face_name_id, card_name, language_id) 
          SELECT face_name_id, card_name, language_id
          FROM FaceName"""),
        dedent("""\
        INSERT INTO NewCardFace 
          (card_face_id, card_id, set_id, face_name_id, is_front,
           collector_number, scryfall_id, highres_image, png_image_uri) 
        SELECT 
           card_face_id, card_id, set_id, face_name_id, is_front,
           collector_number, scryfall_id, highres_image, png_image_uri
        FROM CardFace"""),
        "DROP VIEW AllPrintings",
        "DROP TABLE FaceName",
        "DROP TABLE CardFace",
        "ALTER TABLE NewFaceName RENAME TO FaceName",
        "ALTER TABLE NewCardFace RENAME TO CardFace",
        dedent("""\
        CREATE VIEW AllPrintings AS
          SELECT card_name, "set" AS set_code, set_name, "language", collector_number, scryfall_id,
            highres_image, is_front, png_image_uri, oracle_id
          FROM CardFace
          JOIN FaceName USING(face_name_id)
          JOIN "Set" USING (set_id)
          JOIN Card USING (card_id)
          JOIN PrintLanguage USING(language_id)
        """),
        # Re-create some of the automatically deleted indexes.
        # Now redundant indexes FaceNameCardNameToLanguageIndex and CardFaceIDLookup remain dropped.
        "CREATE INDEX FaceNameLanguageToCardNameIndex ON FaceName(language_id, card_name COLLATE NOCASE)",
        "CREATE INDEX CardFaceToCollectorNumberIndex ON CardFace (face_name_id, set_id, collector_number)",
        "CREATE INDEX CardFace_card_id_index ON CardFace (card_id, is_front)",
        "CREATE INDEX CardFace_scryfall_id_index ON CardFace (scryfall_id, is_front)",
        "PRAGMA foreign_key_check",
        "PRAGMA foreign_keys = ON",
    ]),
    18: MigrationScript([
        "PRAGMA foreign_keys = OFF",
        dedent("""\
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
        )"""),
        "CREATE INDEX Printing_Index_Find_Printing_From_Card_Data ON Printing(card_id, set_id, collector_number)",
        dedent("""\
        CREATE TABLE NewCardFace (
          -- The printable card face of a specific card in a specific language. Is the front most of the time,
          -- but can be the back face for double-faced cards.
          card_face_id INTEGER NOT NULL PRIMARY KEY,
          printing_id INTEGER NOT NULL REFERENCES Printing(printing_id) ON UPDATE CASCADE ON DELETE CASCADE,
          face_name_id INTEGER NOT NULL REFERENCES FaceName(face_name_id) ON UPDATE CASCADE ON DELETE CASCADE,
          is_front INTEGER NOT NULL CHECK (is_front IN (TRUE, FALSE)),
          png_image_uri TEXT NOT NULL,  -- URI pointing to the high resolution PNG image
          UNIQUE(face_name_id, printing_id, is_front)
        )"""),
        "DROP VIEW AllPrintings",
        # Ignore duplicates based on the scryfall id. This is UNIQUE in the new schema, and duplicates based on that
        # can be safely ignored. In the previous schema, all relevant fields for this query are equal, if the
        # scryfall id is equal.
        dedent("""\
        INSERT OR IGNORE INTO Printing(card_id, set_id, collector_number, scryfall_id, highres_image, is_oversized)
          SELECT card_id, set_id, collector_number, scryfall_id, highres_image,
            -- The patterns below match sets containing oversized cards.
            -- Note: Scryfall serves regularly sized images for the "% Championship" sets 
            -- despite being marked as "oversized". Thus those are explicitly not matched.  
            set_name LIKE '% Oversized' OR set_name LIKE '% Schemes' OR set_name LIKE '% Planes'
          FROM CardFace JOIN "Set" USING (set_id)"""),
        # Joining USING (scryfall_id) is fine, because that is UNIQUE in Printing,
        # therefore not creating additional rows.
        dedent("""\
        INSERT OR IGNORE INTO NewCardFace (printing_id, face_name_id, is_front, png_image_uri)
          SELECT printing_id, face_name_id, is_front, png_image_uri
          FROM CardFace JOIN Printing USING (scryfall_id)"""),
        "DROP TABLE CardFace",
        "ALTER TABLE NewCardFace RENAME TO CardFace",
        dedent("""\
        CREATE VIEW AllPrintings AS
          SELECT card_name, "set" AS set_code, set_name, "language", collector_number, scryfall_id,
            highres_image, is_front, is_oversized, png_image_uri, oracle_id
          FROM Card
          JOIN Printing USING (card_id)
          JOIN "Set" USING (set_id)
          JOIN CardFace USING (printing_id)
          JOIN FaceName USING(face_name_id)
          JOIN PrintLanguage USING(language_id)"""),
        "PRAGMA foreign_key_check",
        "PRAGMA foreign_keys = ON",
    ]),
    19: MigrationScript([
        "CREATE INDEX CardFace_Index_for_card_lookup_by_scryfall_id_and_is_front ON CardFace(is_front, printing_id)"
    ]),
    20: MigrationScript([
        "PRAGMA foreign_keys = OFF",
        "DROP VIEW AllPrintings",
        dedent("""\
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
        )"""),
        dedent("""\
        INSERT INTO CardFaceNew (card_face_id, printing_id, face_name_id, is_front, png_image_uri, face_number)
          SELECT card_face_id, printing_id, face_name_id, is_front, png_image_uri, 
               row_number() over (partition by printing_id ORDER BY card_face_id) -1 as face_number
            FROM FaceName JOIN CardFace USING (face_name_id) JOIN Printing USING (printing_id)"""),
        "DROP TABLE CardFace",
        "ALTER TABLE CardFaceNew RENAME TO CardFace",
        "CREATE INDEX CardFace_Index_for_card_lookup_by_scryfall_id_and_is_front ON CardFace(is_front, printing_id)",
        dedent("""\
        CREATE VIEW AllPrintings AS
          SELECT card_name, "set" AS set_code, set_name, "language", collector_number, scryfall_id,
            highres_image, face_number, is_front, is_oversized, png_image_uri, oracle_id
          FROM Card
          JOIN Printing USING (card_id)
          JOIN "Set" USING (set_id)
          JOIN CardFace USING (printing_id)
          JOIN FaceName USING(face_name_id)
          JOIN PrintLanguage USING(language_id)"""),
        "PRAGMA foreign_key_check",
        "PRAGMA foreign_keys = ON",
    ]),
    21: Migrate_21_to_22(),
    22: MigrationScript([
        dedent("""\
        CREATE TABLE RemovedPrintings (
          scryfall_id TEXT NOT NULL PRIMARY KEY,
          -- Required to keep the language when migrating a card to a known printing, because it is otherwise unknown.
          language TEXT NOT NULL,
          oracle_id TEXT NOT NULL
        )"""),
    ]),
    23: MigrationScript([
        "ALTER TABLE Printing ADD COLUMN is_hidden INTEGER NOT NULL CHECK (is_hidden IN (TRUE, FALSE)) DEFAULT FALSE",
        "ALTER TABLE FaceName ADD COLUMN is_hidden INTEGER NOT NULL CHECK (is_hidden IN (TRUE, FALSE)) DEFAULT FALSE",
        dedent("""\
        CREATE TABLE DisplayFilters (
          filter_id INTEGER NOT NULL PRIMARY KEY,
          filter_name TEXT NOT NULL UNIQUE,
          filter_active INTEGER NOT NULL CHECK (filter_active IN (TRUE, FALSE))
        )"""),
        "DROP TABLE UsedDownloadSettings",
        dedent("""\
        CREATE TABLE PrintingDisplayFilter (
          printing_id    INTEGER NOT NULL REFERENCES Printing (printing_id) ON DELETE CASCADE,
          filter_id      INTEGER NOT NULL REFERENCES DisplayFilters (filter_id) ON DELETE CASCADE,
          filter_applies INTEGER NOT NULL CHECK (filter_applies IN (TRUE, FALSE)),
          PRIMARY KEY (printing_id, filter_id)
        )"""),
        dedent("""\
        CREATE VIEW HiddenPrintings AS
          SELECT printing_id, sum(filter_applies * filter_active) > 0 AS should_be_hidden
          FROM PrintingDisplayFilter
          JOIN DisplayFilters USING (filter_id)
          GROUP BY printing_id"""),
        "DROP VIEW AllPrintings",
        dedent("""\
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
            AND FaceName.is_hidden IS FALSE"""),
        "CREATE INDEX Printing_is_hidden ON Printing(printing_id, is_hidden)",
        "DROP INDEX FaceNameLanguageToCardNameIndex",
        "CREATE INDEX FaceNameLanguageToCardNameIndex ON FaceName(language_id, is_hidden, card_name COLLATE NOCASE)",
    ]),
    24: MigrationScript([
        "DROP VIEW HiddenPrintings",
        dedent("""\
        CREATE TABLE PrintingDisplayFilter2 (
          -- Stores which filter applies to which printing.
          printing_id    INTEGER NOT NULL REFERENCES Printing (printing_id) ON DELETE CASCADE,
          filter_id      INTEGER NOT NULL REFERENCES DisplayFilters (filter_id) ON DELETE CASCADE,
          filter_applies INTEGER NOT NULL CHECK (filter_applies IN (TRUE, FALSE)),
          PRIMARY KEY (printing_id, filter_id)
        ) WITHOUT ROWID"""),
        dedent("""\
        INSERT INTO PrintingDisplayFilter2 (printing_id, filter_id, filter_applies)
          SELECT printing_id, filter_id, filter_applies
          FROM PrintingDisplayFilter"""),
        "DROP TABLE PrintingDisplayFilter",
        "ALTER TABLE PrintingDisplayFilter2 RENAME TO PrintingDisplayFilter",
        dedent("""\
        CREATE VIEW HiddenPrintings AS
          SELECT printing_id, sum(filter_applies * filter_active) > 0 AS should_be_hidden
          FROM PrintingDisplayFilter
          JOIN DisplayFilters USING (filter_id)
          GROUP BY printing_id"""),
    ]),
    25: MigrationScript([
        "PRAGMA foreign_keys = OFF",
        dedent("""\
        CREATE TABLE "Set2" (
          set_id   INTEGER PRIMARY KEY NOT NULL,
          set_code TEXT NOT NULL UNIQUE,
          set_name TEXT NOT NULL,
          set_uri  TEXT NOT NULL,
          release_date TEXT NOT NULL,
          wackiness_score INTEGER NOT NULL CHECK (wackiness_score >= 0)
        )"""),
        # Default to neutral values for new columns. Subsequent card data updates will update the values accordingly.
        # Use a date far in the future, because the importer can only date sets back.
        dedent('''\
        INSERT INTO "Set2" (set_id, set_code, set_name, set_uri, release_date, wackiness_score)
          SELECT set_id, "set", set_name, set_uri, '9999-01-01', 0
          FROM "Set"'''),
        "DROP VIEW AllPrintings",
        # Rename the old table first, to update the FOREIGN KEY relation in the Printing table. Then drop and replace
        # it with the new table definition. Without this, the Printing table will still hold a reference to the old name.
        'ALTER TABLE "Set" RENAME TO MTGSet',
        "DROP TABLE MTGSet",
        'ALTER TABLE "Set2" RENAME TO MTGSet',
        dedent("""\
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
            AND FaceName.is_hidden IS FALSE"""),
        "PRAGMA foreign_key_check",
        "PRAGMA foreign_keys = ON",
    ]),
    26: MigrationScript([
        "UPDATE MTGSet SET release_date = '9999-01-01' WHERE release_date = '1970-01-01'",
        "CREATE INDEX FaceName_for_translation ON FaceName(language_id, card_name DESC)",
        "CREATE INDEX CardFace_for_translation ON CardFace(face_name_id, face_number, printing_id)",
        "ANALYZE",
        "DROP VIEW AllPrintings",
        dedent("""\
        CREATE VIEW VisiblePrintings AS
          SELECT card_name, set_code, set_name, "language", collector_number, scryfall_id,
                 highres_image, face_number, is_front, is_oversized, png_image_uri, oracle_id,
                 release_date, wackiness_score
          FROM Card
          JOIN Printing USING (card_id)
          JOIN MTGSet   USING (set_id)
          JOIN CardFace USING (printing_id)
          JOIN FaceName USING (face_name_id)
          JOIN PrintLanguage USING (language_id)
          WHERE Printing.is_hidden IS FALSE
            AND FaceName.is_hidden IS FALSE"""),
        dedent("""\
        CREATE VIEW AllPrintings AS
          SELECT card_name, set_code, set_name, "language", collector_number, scryfall_id, highres_image, face_number,
                is_front, is_oversized, png_image_uri, oracle_id, release_date, wackiness_score, Printing.is_hidden
          FROM Card
          JOIN Printing USING (card_id)
          JOIN MTGSet   USING (set_id)
          JOIN CardFace USING (printing_id)
          JOIN FaceName USING (face_name_id)
          JOIN PrintLanguage USING (language_id)"""),
    ]),
    27: MigrationScript([
        "DROP VIEW AllPrintings",
        "DROP VIEW VisiblePrintings",
        dedent("""\
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
        dedent("""\
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
    ]),
    28: MigrationScript([
        "DROP VIEW HiddenPrintings",
        dedent("""\
        CREATE TABLE PrintingDisplayFilter2 (
          -- Stores which filter applies to which printing.
          printing_id    INTEGER NOT NULL REFERENCES Printing (printing_id) ON DELETE CASCADE,
          filter_id      INTEGER NOT NULL REFERENCES DisplayFilters (filter_id) ON DELETE CASCADE,
          PRIMARY KEY (printing_id, filter_id)
        ) WITHOUT ROWID"""),
        dedent("""\
        INSERT INTO PrintingDisplayFilter2 (printing_id, filter_id)
          SELECT printing_id, filter_id
          FROM PrintingDisplayFilter
          WHERE filter_applies IS TRUE"""),
        "DROP TABLE PrintingDisplayFilter",
        "ALTER TABLE PrintingDisplayFilter2 RENAME TO PrintingDisplayFilter",
        dedent("""\
        CREATE VIEW HiddenPrintingIDs AS
          SELECT printing_id
            FROM PrintingDisplayFilter
            JOIN DisplayFilters USING (filter_id)
            WHERE filter_active IS TRUE
            GROUP BY printing_id"""),
        "DROP VIEW AllPrintings",
        dedent("""\
        CREATE VIEW AllPrintings AS
          SELECT card_name, set_code, set_name, "language", collector_number, scryfall_id, highres_image, face_number,
                 is_front, is_oversized, png_image_uri, oracle_id, release_date, wackiness_score, Printing.is_hidden
          FROM Card
          JOIN Printing USING (card_id)
          JOIN MTGSet   USING (set_id)
          JOIN CardFace USING (printing_id)
          JOIN FaceName USING (face_name_id)
          JOIN PrintLanguage USING (language_id)"""),
    ]),
    29: MigrationScript([
        dedent("""\
        CREATE TABLE RelatedPrintings (
          card_id INTEGER NOT NULL REFERENCES Card(card_id) ON UPDATE CASCADE ON DELETE CASCADE,
          related_id INTEGER NOT NULL REFERENCES Card(card_id) ON UPDATE CASCADE ON DELETE CASCADE,
          PRIMARY KEY (card_id, related_id),
          CONSTRAINT 'No self-reference' CHECK (card_id <> related_id)
        ) WITHOUT ROWID""")
    ]),
    30: MigrationScript([
        "DROP VIEW VisiblePrintings",
        "DROP VIEW AllPrintings",
        dedent("""\
        CREATE VIEW VisiblePrintings AS
        WITH double_faced_printings(printing_id, is_dfc) AS (
            SELECT DISTINCT printing_id, TRUE as is_dfc
                FROM CardFace
                WHERE is_front IS FALSE)
          SELECT card_name, set_code, set_name, "language", collector_number, scryfall_id, highres_image, face_number,
                 is_front, is_oversized, png_image_uri, oracle_id, release_date, wackiness_score, release_date,
                 coalesce(double_faced_printings.is_dfc, FALSE) as is_dfc
          FROM Card
          JOIN Printing USING (card_id)
          JOIN MTGSet   USING (set_id)
          JOIN CardFace USING (printing_id)
          JOIN FaceName USING (face_name_id)
          JOIN PrintLanguage USING (language_id)
          LEFT OUTER JOIN double_faced_printings USING (printing_id)
          WHERE Printing.is_hidden IS FALSE
            AND FaceName.is_hidden IS FALSE"""),
        dedent("""\
        CREATE VIEW AllPrintings AS
        WITH double_faced_printings(printing_id, is_dfc) AS (
            SELECT DISTINCT printing_id, TRUE as is_dfc
                FROM CardFace
                WHERE is_front IS FALSE)
          SELECT card_name, set_code, set_name, "language", collector_number, scryfall_id, highres_image, face_number,
                 is_front, is_oversized, png_image_uri, oracle_id, release_date, wackiness_score, Printing.is_hidden,
                 coalesce(double_faced_printings.is_dfc, FALSE) as is_dfc
          FROM Card
          JOIN Printing USING (card_id)
          JOIN MTGSet   USING (set_id)
          JOIN CardFace USING (printing_id)
          JOIN FaceName USING (face_name_id)
          JOIN PrintLanguage USING (language_id)
          LEFT OUTER JOIN double_faced_printings USING (printing_id)"""),
    ]),
    31: MigrationScript([
        dedent("""\
        CREATE VIEW CurrentlyEnabledSetCodeFilters AS
          -- Returns the set codes that are currently explicitly hidden by the hidden-sets filter.
          SELECT DISTINCT set_code
          FROM MTGSet
          JOIN Printing USING (set_id)
          JOIN PrintingDisplayFilter USING (printing_id)
          JOIN DisplayFilters USING (filter_id)
          WHERE filter_name = 'hidden-sets'"""),
        "CREATE INDEX LookupPrintingBySet ON Printing(set_id)",
        "PRAGMA journal_mode = 'wal'",
    ]),
    32: MigrationScript([
        "CREATE INDEX CardFace_idx_for_translation ON CardFace(printing_id)",
    ]),
    33: MigrationScript([
        "DROP VIEW VisiblePrintings",
        "DROP VIEW AllPrintings",
        "CREATE INDEX PrintingDisplayFilter_Printing_from_filter_lookup ON PrintingDisplayFilter(filter_id)",
        dedent("""\
        CREATE VIEW VisiblePrintings AS
        WITH 
          double_faced_printings(printing_id, is_dfc) AS (
          SELECT DISTINCT printing_id, TRUE as is_dfc
            FROM CardFace
            WHERE is_front IS FALSE),
            
          token_printings(printing_id, is_token) AS (
          SELECT printing_id, TRUE AS is_token
            FROM DisplayFilters
            JOIN PrintingDisplayFilter USING (filter_id)
            WHERE filter_name = 'hide-token')
          
          SELECT card_name, set_code, set_name, "language", collector_number, scryfall_id, highres_image, face_number,
            is_front, is_oversized, png_image_uri, oracle_id, release_date, wackiness_score, release_date,
            coalesce(double_faced_printings.is_dfc, FALSE) as is_dfc,
            coalesce(token_printings.is_token, FALSE) as is_token
          FROM Card
          JOIN Printing USING (card_id)
          JOIN MTGSet   USING (set_id)
          JOIN CardFace USING (printing_id)
          JOIN FaceName USING (face_name_id)
          JOIN PrintLanguage USING (language_id)
          LEFT OUTER JOIN double_faced_printings USING (printing_id)
          LEFT OUTER JOIN token_printings USING (printing_id)
          WHERE Printing.is_hidden IS FALSE
            AND FaceName.is_hidden IS FALSE"""),
        dedent("""\
        CREATE VIEW AllPrintings AS
        WITH 
        double_faced_printings(printing_id, is_dfc) AS (
          SELECT DISTINCT printing_id, TRUE as is_dfc
            FROM CardFace
            WHERE is_front IS FALSE),
        
        token_printings(printing_id, is_token) AS (
          SELECT printing_id, TRUE AS is_token
            FROM DisplayFilters
            JOIN PrintingDisplayFilter USING (filter_id)
            WHERE filter_name = 'hide-token')
        
          SELECT card_name, set_code, set_name, "language", collector_number, scryfall_id, highres_image, face_number,
             is_front, is_oversized, png_image_uri, oracle_id, release_date, wackiness_score, Printing.is_hidden,
             coalesce(double_faced_printings.is_dfc, FALSE) as is_dfc,
             coalesce(token_printings.is_token, FALSE) as is_token
          FROM Card
          JOIN Printing USING (card_id)
          JOIN MTGSet   USING (set_id)
          JOIN CardFace USING (printing_id)
          JOIN FaceName USING (face_name_id)
          JOIN PrintLanguage USING (language_id)
          LEFT OUTER JOIN double_faced_printings USING (printing_id)
          LEFT OUTER JOIN token_printings USING (printing_id)"""),
    ]),
}


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


class DatabaseMigrationRunner(Runnable):
    """
    Upgrades the database schema of the given Card Database to the latest supported schema version.

    Given migration scripts are only executed, if their associated starting schema version matches the current database
    schema version right before it is executed. Each migration script must upgrade to the next schema version.
    Scripts combining multiple version upgrades in one SQL script are not supported.
    """

    def __init__(self, card_db: CardDatabase, migration_scripts: Dict[int, MigrationScript] = None):
        super().__init__()
        self.total_update_signals = ProgressSignalContainer()
        self.script_update_signals = ProgressSignalContainer()
        self.db_path = card_db.db_path
        self.migration_scripts = migration_scripts or MIGRATION_SCRIPTS
        logger.debug(f"Created {self.__class__.__name__} instance.")

    def connect_main_window_signals(self, main_window: "MainWindow"):
        progress_bars = main_window.progress_bars
        self.connect_progress_signals(
            self.total_update_signals,
            progress_bars.begin_outer_progress,
            progress_bars.set_outer_progress,
            progress_bars.end_outer_progress,
        )
        self.connect_progress_signals(
            self.script_update_signals,
            progress_bars.begin_inner_progress,
            progress_bars.set_inner_progress,
            progress_bars.end_inner_progress
        )

    @staticmethod
    def connect_progress_signals(signals: ProgressSignalContainer, begin_signal, progress_signal, end_signal):
        signals.begin_update.connect(begin_signal, QueuedConnection)
        signals.progress.connect(progress_signal, QueuedConnection)
        signals.update_completed.connect(end_signal, QueuedConnection)

    @with_database_write_lock()
    def run(self):
        """
        Run the database update.
        """
        db = mtg_proxy_printer.sqlite_helpers.open_database(self.db_path, "carddb")
        begin_schema_version = self._get_schema_version(db)
        target_version = max(self.migration_scripts.keys())+1
        if begin_schema_version >= target_version:
            self.total_update_signals.update_completed.emit()
            self.release_instance()
            return
        if self.migration_scripts is not MIGRATION_SCRIPTS:
            logger.debug(f"Custom migration scripts passed: {self.migration_scripts}")
        logger.info(f"Migrating database from version {begin_schema_version} to {target_version}. "
                    f"About to run {target_version-begin_schema_version} migration scripts.")
        top_level_progress_meter = self._create_top_level_progress_meter(begin_schema_version, target_version)
        for source_version in range(begin_schema_version, target_version):
            script = self.migration_scripts[source_version]
            self._migrate_version(db, source_version, script)
            top_level_progress_meter.advance()
        current_schema_version = self._get_schema_version(db)
        logger.info(f"Finished database migrations, rebuilding database. {current_schema_version=}")
        db.execute("ANALYZE\n")
        top_level_progress_meter.advance()
        db.execute("VACUUM\n")
        top_level_progress_meter.advance()
        top_level_progress_meter.finish()
        logger.info("Rebuild done.")
        self.release_instance()

    def _create_top_level_progress_meter(self, begin_schema_version: int, target_version: int) -> ProgressMeter:
        signals = self.total_update_signals
        msg = QCoreApplication.translate("DatabaseMigrationRunner", "Running database migrations:", "")
        progress_meter = ProgressMeter(
            target_version-begin_schema_version+2, msg,  # ANALYZE and VACUUM (2 steps) are run as top-level tasks
            signals.begin_update.emit, signals.progress.emit, signals.update_completed.emit)
        return progress_meter

    @staticmethod
    def _get_schema_version(db: sqlite3.Connection) -> int:
        return db.execute("PRAGMA user_version; -- DatabaseMigrationRunner\n").fetchone()[0]

    def _migrate_version(self, db: sqlite3.Connection, source_version: int, script: MigrationScript):
        next_version = source_version + 1
        suffix = f";  -- Migrate {source_version} to {next_version}\n"
        signals = self.script_update_signals
        steps = script.script_length(db, suffix) + 1  # Add 1 for the call to db.commit()

        msg = QCoreApplication.translate(
            "DatabaseMigrationRunner", "Migrate to version %n:",
            "The numeric parameter is a version number, and not countable.", source_version)
        meter = ProgressMeter(
            steps, msg,
            signals.begin_update.emit, signals.progress.emit, signals.update_completed.emit)

        logger.debug(f"Starting migration from {source_version}")
        db.execute("BEGIN IMMEDIATE TRANSACTION" + suffix)
        for statement in script.get_script(db, suffix, meter):  # type: Statement
            if isinstance(statement, str):
                if is_pragma := statement.startswith("PRAGMA"):
                    db.execute("COMMIT" + suffix)
                db.execute(statement + suffix)
                if is_pragma:
                    db.execute("BEGIN IMMEDIATE TRANSACTION" + suffix)
            else:
                statement, parameters = statement
                db.executemany(statement + suffix, parameters)
            meter.advance()
        db.execute(f"PRAGMA user_version = {next_version}" + suffix)
        db.commit()
        logger.debug(f"Migrated to {next_version}")
        meter.advance()
        meter.finish()
