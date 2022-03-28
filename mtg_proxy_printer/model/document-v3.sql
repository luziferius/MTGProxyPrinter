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

PRAGMA user_version = 0000003;
PRAGMA application_id = 41325044; -- ASCII-encoded "MTGP"
PRAGMA page_size =  512;
VACUUM;  -- Required to apply setting PRAGMA page_size

CREATE TABLE Card (
  page INTEGER NOT NULL CHECK (page > 0),
  slot INTEGER NOT NULL CHECK (slot > 0),
  is_front INTEGER NOT NULL CHECK (is_front IN (0, 1)) DEFAULT 1,
  scryfall_id TEXT NOT NULL,
  PRIMARY KEY(page, slot)
) WITHOUT ROWID;
