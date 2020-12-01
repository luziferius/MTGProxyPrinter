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


PRAGMA user_version = 0000004;
PRAGMA foreign_keys = on;
BEGIN TRANSACTION;

CREATE TABLE "Set" (
  "set" TEXT NOT NULL PRIMARY KEY,
  set_name TEXT NOT NULL,
  set_uri TEXT NOT NULL
);

CREATE TABLE Card (
  scryfall_id TEXT NOT NULL PRIMARY KEY, -- Unique ID for this exact print
  oracle_id   TEXT NOT NULL,  -- Unique ID for this card. All reprints have the same oracle_id
  "set" NOT NULL REFERENCES "Set"("set"),  -- Set abbreviation
  collector_number TEXT NOT NULL, -- Most have simple integers, but some cards have non-integer collector numbers.
  "language" TEXT NOT NULL,
  highres_image INTEGER NOT NULL  -- Boolean indicating that the card has high resolution images.
);

CREATE INDEX CardLanguageIndex ON Card (
  "language",
  scryfall_id,
  "set"
);

CREATE TABLE CardFace (
  scryfall_id TEXT NOT NULL REFERENCES Card(scryfall_id),  -- The card to which this face belongs
  card_name TEXT NOT NULL,  -- Card name as printed
  png_image_uri TEXT NOT NULL  -- URI pointing to the high resolution PNG image
);

CREATE INDEX CardNameIndex ON CardFace(
  card_name,
  scryfall_id
);

CREATE TABLE LastDatabaseUpdate (
  update_id        INTEGER NOT NULL PRIMARY KEY,
  update_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

COMMIT;
