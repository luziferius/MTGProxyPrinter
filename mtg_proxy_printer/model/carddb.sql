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


PRAGMA user_version = 0000029;
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
  set_id INTEGER NOT NULL REFERENCES MTGSet(set_id) ON UPDATE CASCADE ON DELETE CASCADE,
  collector_number TEXT NOT NULL,
  scryfall_id TEXT NOT NULL UNIQUE,
  -- Over-sized card indicator. Over-sized cards (value TRUE) are mostly useless for play,
  -- so store this to be able to warn the user
  is_oversized INTEGER NOT NULL CHECK (is_oversized IN (TRUE, FALSE)),
  -- Indicates if the card has high resolution images.
  highres_image INTEGER NOT NULL CHECK (highres_image IN (TRUE, FALSE)),
  is_hidden INTEGER NOT NULL CHECK (is_hidden IN (TRUE, FALSE)) DEFAULT FALSE
);

CREATE INDEX Printing_Index_Find_Printing_From_Card_Data
  ON Printing(card_id, set_id, collector_number);
CREATE INDEX Printing_is_hidden
  ON Printing(printing_id, is_hidden);

CREATE TABLE FaceName (
  -- The name of a card face in a given language. Cards are not renamed,
  -- so all Card entries share the same names across all reprints for a given language.
  face_name_id INTEGER PRIMARY KEY NOT NULL,
  card_name    TEXT NOT NULL,
  language_id  INTEGER NOT NULL REFERENCES PrintLanguage(language_id) ON UPDATE CASCADE ON DELETE CASCADE,
  is_hidden INTEGER NOT NULL CHECK (is_hidden IN (TRUE, FALSE)) DEFAULT FALSE,
  UNIQUE (card_name, language_id)
);
-- Speeds up LIKE matches against card names, used by the Card name search
CREATE INDEX FaceNameLanguageToCardNameIndex ON FaceName(language_id, is_hidden, card_name COLLATE NOCASE);


CREATE TABLE CardFace (
  -- The printable card face of a specific card in a specific language. Is the front most of the time,
  -- but can be the back face for double-faced cards.
  card_face_id INTEGER NOT NULL PRIMARY KEY,
  printing_id INTEGER NOT NULL REFERENCES Printing(printing_id) ON UPDATE CASCADE ON DELETE CASCADE,
  face_name_id INTEGER NOT NULL REFERENCES FaceName(face_name_id) ON UPDATE CASCADE ON DELETE CASCADE,
  is_front INTEGER NOT NULL CHECK (is_front IN (TRUE, FALSE)),
  png_image_uri TEXT NOT NULL, -- URI pointing to the high resolution PNG image
  -- Enumerates the face on a card. Used to match the exact same face across translated, multi-faced cards
  face_number INTEGER NOT NULL CHECK (face_number >= 0),
  UNIQUE(face_name_id, printing_id, is_front)
);
CREATE INDEX CardFace_Index_for_card_lookup_by_scryfall_id_and_is_front ON CardFace(is_front, printing_id);


CREATE TABLE MTGSet (
  set_id   INTEGER PRIMARY KEY NOT NULL,
  set_code TEXT NOT NULL UNIQUE,
  set_name TEXT NOT NULL,
  set_uri  TEXT NOT NULL,
  release_date TEXT NOT NULL,
  wackiness_score INTEGER NOT NULL CHECK (wackiness_score >= 0)
);

CREATE TABLE LastDatabaseUpdate (
  -- Contains the history of all performed card data updates
  update_id             INTEGER NOT NULL PRIMARY KEY,
  update_timestamp      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  reported_card_count   INTEGER NOT NULL CHECK (reported_card_count >= 0)
);

CREATE TABLE DisplayFilters (
  -- Contains the available display filters and their current values
  filter_id INTEGER NOT NULL PRIMARY KEY,
  filter_name TEXT NOT NULL UNIQUE,
  filter_active INTEGER NOT NULL CHECK (filter_active IN (TRUE, FALSE))
);

CREATE TABLE PrintingDisplayFilter (
  -- Stores which filter applies to which printing.
  printing_id    INTEGER NOT NULL REFERENCES Printing (printing_id) ON DELETE CASCADE,
  filter_id      INTEGER NOT NULL REFERENCES DisplayFilters (filter_id) ON DELETE CASCADE,
  PRIMARY KEY (printing_id, filter_id)
) WITHOUT ROWID;

CREATE VIEW HiddenPrintingIDs AS
SELECT printing_id
  FROM PrintingDisplayFilter
  JOIN DisplayFilters USING (filter_id)
  WHERE filter_active IS TRUE
  GROUP BY printing_id
;

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

CREATE TABLE RemovedPrintings (
  scryfall_id TEXT NOT NULL PRIMARY KEY,
  -- Required to keep the language when migrating a card to a known printing, because it is otherwise unknown.
  language TEXT NOT NULL,
  oracle_id TEXT NOT NULL
);

CREATE INDEX FaceName_for_translation ON FaceName(language_id, card_name DESC);
CREATE INDEX CardFace_for_translation ON CardFace(face_name_id, face_number, printing_id);


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
    AND FaceName.is_hidden IS FALSE
;

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

COMMIT;
