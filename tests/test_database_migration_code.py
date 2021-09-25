# Copyright (C) 2021 Thomas Hess <thomas.hess@udo.edu>

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

from hamcrest import *

from mtg_proxy_printer.sqlite_helpers import _read_current_database_schema_version
from mtg_proxy_printer.model.carddb_helpers import migrate_card_database

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


def test_migrate_card_database():
    db = sqlite3.connect(":memory:")
    db.executescript(OLDEST_SUPPORTED_SCHEMA)
    migrate_card_database(db)
    assert_that(
        db.execute("PRAGMA user_version").fetchone()[0],
        is_(equal_to(_read_current_database_schema_version("carddb"))),
    )
    # TODO: Validate the table columns and indices.
