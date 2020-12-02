-- Copyright (C) 2020 Thomas Hess <thomas.hess@udo.edu>

-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.

-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.

-- You should have received a copy of the GNU General Public License
-- along with this program. If not, see <http://www.gnu.org/licenses/>.


PRAGMA user_version = 0000005;
PRAGMA foreign_keys = on;
BEGIN TRANSACTION;


CREATE TABLE PrintLanguage (
  language_id INTEGER PRIMARY KEY NOT NULL,
  "language" TEXT NOT NULL UNIQUE
);

CREATE INDEX LanguageIndex ON PrintLanguage("language", language_id);


CREATE TABLE Card (
  -- An abstract card, all prints, variations and languages are considered the same Card for ruling purposes.
  card_id INTEGER PRIMARY KEY NOT NULL,
  -- Uniquely identified by the oracle_id provided by Scryfall. Some cards from Un-Sets do not have unique English names,
  -- thus identification using an abstract ID value is required.
  oracle_id TEXT NOT NULL UNIQUE
);


CREATE TABLE FaceName (
  -- The name of a card face in a given language. Cards are not renamed, so all Card entries share the same names
  -- across all reprints for a given language.
  face_name_id INTEGER PRIMARY KEY NOT NULL,
  card_name    TEXT NOT NULL,
  language_id  INTEGER NOT NULL REFERENCES PrintLanguage(language_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX FaceNameIndex ON FaceName (CARD_NAME, language_id, face_name_id);


CREATE TABLE CardFace (
  -- The printable card face of a specific card in a specific language. Is the front most of the time, but can be the
  -- back face for double-faced cards.
  card_face_id INTEGER NOT NULL PRIMARY KEY,
  card_id INTEGER NOT NULL REFERENCES Card(card_id) ON UPDATE CASCADE ON DELETE CASCADE,  -- The card to which this face belongs
  set_id INTEGER NOT NULL REFERENCES "Set"(set_id) ON UPDATE CASCADE ON DELETE CASCADE,
  face_name_id INTEGER NOT NULL REFERENCES FaceName(face_name_id) ON UPDATE CASCADE ON DELETE CASCADE,
  scryfall_id TEXT NOT NULL,
  png_image_uri TEXT NOT NULL  -- URI pointing to the high resolution PNG image
);


CREATE TABLE "Set" (
  set_id INTEGER PRIMARY KEY NOT NULL,
  "set" TEXT NOT NULL UNIQUE,
  set_name TEXT NOT NULL,
  set_uri TEXT NOT NULL
);


CREATE TABLE LastDatabaseUpdate (
  update_id        INTEGER NOT NULL PRIMARY KEY,
  update_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);


CREATE VIEW AllPrintings AS
  SELECT *
  FROM CardFace
  JOIN FaceName USING(face_name_id)
  JOIN "Set" USING (set_id)
  JOIN Card USING (card_id)
  JOIN PrintLanguage USING(language_id)
;

COMMIT;
