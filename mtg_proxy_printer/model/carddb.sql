-- Copyright (C) 2020, 2021 Thomas Hess <thomas.hess@udo.edu>

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


PRAGMA user_version = 0000019;
PRAGMA foreign_keys = on;
BEGIN TRANSACTION;


CREATE TABLE PrintLanguage (
  language_id INTEGER PRIMARY KEY NOT NULL,
  "language" TEXT NOT NULL UNIQUE
);

CREATE TABLE Card (
  -- An abstract card, all prints, variations and languages are
  -- considered the same Card for ruling purposes.
  card_id INTEGER PRIMARY KEY NOT NULL,
  -- Uniquely identified by the oracle_id provided by Scryfall.
  -- Some cards from Un-Sets do not have unique English names,
  -- thus identification using an abstract ID value is required.
  oracle_id TEXT NOT NULL UNIQUE
);

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

CREATE TABLE FaceName (
  -- The name of a card face in a given language. Cards are not renamed,
  -- so all Card entries share the same names across all reprints for a given language.
  face_name_id INTEGER PRIMARY KEY NOT NULL,
  card_name    TEXT NOT NULL,
  language_id  INTEGER NOT NULL REFERENCES PrintLanguage(language_id) ON UPDATE CASCADE ON DELETE CASCADE,
  UNIQUE (card_name, language_id)
);
-- Speeds up LIKE matches against card names, used by the Card name search
CREATE INDEX FaceNameLanguageToCardNameIndex ON FaceName(language_id, card_name COLLATE NOCASE);

CREATE TABLE CardFace (
  -- The printable card face of a specific card in a specific language. Is the front most of the time,
  -- but can be the back face for double-faced cards.
  card_face_id INTEGER NOT NULL PRIMARY KEY,
  printing_id INTEGER NOT NULL REFERENCES Printing(printing_id) ON UPDATE CASCADE ON DELETE CASCADE,
  face_name_id INTEGER NOT NULL REFERENCES FaceName(face_name_id) ON UPDATE CASCADE ON DELETE CASCADE,
  is_front INTEGER NOT NULL CHECK (is_front IN (TRUE, FALSE)),
  png_image_uri TEXT NOT NULL,  -- URI pointing to the high resolution PNG image
  UNIQUE(face_name_id, printing_id, is_front)
);

CREATE TABLE "Set" (
  set_id   INTEGER PRIMARY KEY NOT NULL,
  "set"    TEXT NOT NULL UNIQUE,
  set_name TEXT NOT NULL,
  set_uri  TEXT NOT NULL
);


CREATE TABLE LastDatabaseUpdate (
  -- Contains the history of all performed card data updates
  update_id             INTEGER NOT NULL PRIMARY KEY,
  update_timestamp      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  newest_card_timestamp TIMESTAMP WITH TIME ZONE NULL
);

CREATE TABLE UsedDownloadSettings (
  -- This table contains the download filter settings used during the card data import
  setting TEXT NOT NULL PRIMARY KEY,
  "value" INTEGER NOT NULL CHECK ("value" IN (0, 1)) DEFAULT 1
);

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

COMMIT;
