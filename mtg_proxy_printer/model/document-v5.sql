-- Copyright (C) 2020-2022 Thomas Hess <thomas.hess@udo.edu>

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
PRAGMA application_id = 41325044; -- ASCII-encoded "MTGP"
PRAGMA page_size =  512;
VACUUM;  -- Required to apply setting PRAGMA page_size

CREATE TABLE Card (
  page INTEGER NOT NULL CHECK (page > 0),
  slot INTEGER NOT NULL CHECK (slot > 0),
  is_front INTEGER NOT NULL CHECK (is_front IN (TRUE, FALSE)) DEFAULT 1,
  scryfall_id TEXT NOT NULL,
  PRIMARY KEY(page, slot)
) WITHOUT ROWID;

CREATE TABLE DocumentSettings (
  rowid INTEGER NOT NULL PRIMARY KEY CHECK (rowid == 1),
  page_height INTEGER NOT NULL CHECK (page_height > 0),
  page_width INTEGER NOT NULL CHECK (page_width > 0),
  margin_top INTEGER NOT NULL CHECK (margin_top >= 0),
  margin_bottom INTEGER NOT NULL CHECK (margin_bottom >= 0),
  margin_left INTEGER NOT NULL CHECK (margin_left >= 0),
  margin_right INTEGER NOT NULL CHECK (margin_right >= 0),
  image_spacing_horizontal INTEGER NOT NULL CHECK (image_spacing_horizontal >= 0),
  image_spacing_vertical INTEGER NOT NULL CHECK (image_spacing_vertical >= 0),
  draw_cut_markers INTEGER NOT NULL CHECK (draw_cut_markers in (TRUE, FALSE)),
  draw_sharp_corners INTEGER NOT NULL CHECK (draw_sharp_corners in (TRUE, FALSE))
);
