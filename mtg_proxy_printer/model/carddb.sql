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


PRAGMA user_version = 35;
PRAGMA foreign_keys = on;
PRAGMA journal_mode = 'wal';
BEGIN TRANSACTION;


CREATE TABLE LastDatabaseUpdate (
  -- Contains the history of all performed card data updates
  update_id           INTEGER NOT NULL PRIMARY KEY,
  update_timestamp    TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  reported_card_count INTEGER NOT NULL CHECK (reported_card_count >= 0)
);

CREATE TABLE MigratedPrinting (
  migration_id TEXT NOT NULL PRIMARY KEY,
  old_scryfall_id TEXT NOT NULL,
  new_scryfall_id TEXT,
  performed_at INTEGER NOT NULL
);
CREATE INDEX MigratedPrintingLookup ON MigratedPrinting(old_scryfall_id, new_scryfall_id);

CREATE TABLE DisplayFilters (
  -- Contains the available display filters and their current values
  filter_id INTEGER NOT NULL PRIMARY KEY,
  filter_name TEXT NOT NULL UNIQUE,
  filter_active INTEGER NOT NULL CHECK (filter_active IN (TRUE, FALSE)),
  choice_score INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE PrintingDisplayFilter (
  -- Stores which filter applies to which printing.
  printing_id    INTEGER NOT NULL REFERENCES Printing (printing_id) ON DELETE CASCADE,
  filter_id      INTEGER NOT NULL REFERENCES DisplayFilters (filter_id) ON DELETE CASCADE,
  PRIMARY KEY (printing_id, filter_id)
) WITHOUT ROWID;

CREATE TABLE MTGSet (
  set_id   INTEGER PRIMARY KEY NOT NULL,
  set_code TEXT NOT NULL UNIQUE CHECK (set_code <> ''),
  set_name TEXT NOT NULL,
  release_date TEXT NOT NULL,
  icon_svg TEXT CHECK (icon_svg <> ''),
  set_scryfall_id TEXT NOT NULL UNIQUE
);

CREATE TABLE PrintingFace (
  printing_id INTEGER NOT NULL,
  is_front INTEGER NOT NULL CHECK (is_front IN (TRUE, FALSE)),
  face_name TEXT NOT NULL CHECK (face_name <> ''),
  png_image_uri TEXT NOT NULL,
  usage_count INTEGER NOT NULL CHECK (usage_count >= 0) DEFAULT 0,
  last_use_timestamp INTEGER,
  PRIMARY KEY(printing_id, is_front)
);

CREATE TABLE Card (
  card_id INTEGER NOT NULL PRIMARY KEY,
  oracle_id TEXT NOT NULL UNIQUE,
  -- There are now tokens sharing names with cards, so state if this is a card that can go into a deck.
  -- Used by the print selection in the deck list parser to always chose cards over same-name tokens
  is_card INTEGER NOT NULL CHECK (is_card IN (TRUE, FALSE))
);

CREATE TABLE RelatedCards (
  -- The related cards of a card are those it references or creates, and those creating or referencing it.
  -- The relationship is modelled bi-directional for better discoverability, especially for effects
  -- that search the library for a specific card. Given the target card, this modelling also finds the tutors.
  card_id    INTEGER NOT NULL REFERENCES Card(card_id) ON UPDATE CASCADE ON DELETE CASCADE,
  related_id INTEGER NOT NULL REFERENCES Card(card_id) ON UPDATE CASCADE ON DELETE CASCADE,
  PRIMARY KEY (card_id, related_id) ON CONFLICT IGNORE,
  CONSTRAINT 'No self-reference' CHECK (card_id <> related_id)
) WITHOUT ROWID;

CREATE TABLE Printing (
  printing_id INTEGER NOT NULL PRIMARY KEY,
  set_id INTEGER NOT NULL REFERENCES MTGSet(set_id),
  "language" TEXT NOT NULL CHECK ("language" <> ''),
  scryfall_id TEXT NOT NULL UNIQUE,
  card_id INTEGER NOT NULL REFERENCES Card(card_id),
  -- Over-sized card indicator. Over-sized cards (value TRUE) are mostly useless for play,
  -- so store this to be able to warn the user
  is_oversized INTEGER NOT NULL CHECK (is_oversized IN (TRUE, FALSE)),
  -- Indicates if the card has high resolution images.
  highres_image INTEGER NOT NULL CHECK (highres_image IN (TRUE, FALSE)),
  -- Result cache for the printing filter evaluation
  is_hidden INTEGER NOT NULL CHECK (is_hidden IN (TRUE, FALSE)) DEFAULT FALSE,
  preference_score INTEGER NOT NULL DEFAULT 0
);

COMMIT;
