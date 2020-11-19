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


PRAGMA journal_mode = wal;
PRAGMA user_version = 0000001;
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
  card_name TEXT NOT NULL,  -- Card name as printed
  "set" NOT NULL REFERENCES "Set"("set"),  -- Set abbreviation
  collector_number TEXT NOT NULL, -- Most have simple integers, but some cards have non-integer collector numbers.
  language TEXT NOT NULL,
  png_image_uri TEXT NOT NULL,  -- URI pointing to the high resolution PNG image
  highres_image INTEGER NOT NULL  -- Boolean indicating that the card has high resolution images.
);


COMMIT;
