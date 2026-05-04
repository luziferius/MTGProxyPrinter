-- Copyright (C) 2020-2026 Thomas Hess <thomas.hess@udo.edu>

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


CREATE TABLE Card (
  card_id      INTEGER         NOT NULL PRIMARY KEY,
  oracle_id    TEXT            NOT NULL UNIQUE,
  english_name TEXT            NOT NULL, -- Not UNIQUE. There are some distinct tokens and  Un-set cards sharing names
  -- There are now tokens sharing names with cards, so state if this is a card that can go into a deck.
  -- Used by the print selection in the deck list parser to always chose cards over same-name tokens
  is_card      BOOLEAN_INTEGER NOT NULL CHECK (is_card IN (TRUE, FALSE))
);

CREATE TABLE Printing (
  printing_id      INTEGER         NOT NULL PRIMARY KEY,
  set_id           INTEGER         NOT NULL REFERENCES MTGSet(set_id),
  collector_number TEXT            NOT NULL,
  "language"       TEXT            NOT NULL CHECK ("language" <> ''),
  scryfall_id      TEXT            NOT NULL UNIQUE,
  card_id          INTEGER         NOT NULL REFERENCES Card(card_id),
  -- Over-sized card indicator. Over-sized cards (value TRUE) are mostly useless for play,
  -- so store this to be able to warn the user
  is_oversized     BOOLEAN_INTEGER NOT NULL CHECK (is_oversized IN (TRUE, FALSE)),
  -- Indicates if the card has high resolution images.
  is_highres_image BOOLEAN_INTEGER NOT NULL CHECK (is_highres_image IN (TRUE, FALSE)),
  -- Result cache for the printing filter evaluation
  is_visible       BOOLEAN_INTEGER NOT NULL CHECK (is_visible IN (TRUE, FALSE)) DEFAULT TRUE,
  preference_score INTEGER         NOT NULL DEFAULT 0,
  is_dfc           BOOLEAN_INTEGER NOT NULL CHECK (is_dfc IN (TRUE, FALSE)) DEFAULT FALSE
);
CREATE INDEX Printing_find_printing_by_language ON Printing(language);

CREATE TABLE RelatedCards (
  -- The related cards of a card are those it references or creates, and those creating or referencing it.
  -- The relationship is modelled bi-directional for better discoverability, especially for effects
  -- that search the library for a specific card. Given the target card, this modelling also finds the tutors.
  card_id    INTEGER NOT NULL REFERENCES Card(card_id) ON UPDATE CASCADE ON DELETE CASCADE,
  related_id INTEGER NOT NULL REFERENCES Card(card_id) ON UPDATE CASCADE ON DELETE CASCADE,
  PRIMARY KEY (card_id, related_id) ON CONFLICT IGNORE,
  CONSTRAINT 'No self-reference' CHECK (card_id <> related_id)
) WITHOUT ROWID;

CREATE TABLE PrintingFace (
  printing_id        INTEGER            NOT NULL,
  is_front           BOOLEAN_INTEGER    NOT NULL CHECK (is_front IN (TRUE, FALSE)),
  face_name          TEXT               NOT NULL CHECK (face_name <> ''),
  png_image_uri      TEXT               NOT NULL,
  usage_count        INTEGER            NOT NULL CHECK (usage_count >= 0) DEFAULT 0,
  last_use_timestamp INTEGER_TIMESTAMP,
  download_status    INTEGER            NOT NULL CHECK (download_status >=0) DEFAULT 0,
  PRIMARY KEY(printing_id, is_front)
);
CREATE INDEX PrintingFace_find_printing_by_name ON PrintingFace(face_name, printing_id);

CREATE TABLE MTGSet (
  set_id            INTEGER           NOT NULL PRIMARY KEY,
  set_code          TEXT              NOT NULL UNIQUE CHECK (set_code <> ''),
  set_name          TEXT              NOT NULL,
  release_date      INTEGER_TIMESTAMP NOT NULL,
  set_filter_active BOOLEAN_INTEGER   NOT NULL CHECK (set_filter_active IN (TRUE, FALSE)) DEFAULT FALSE,
  icon_svg          TEXT                       CHECK (icon_svg <> ''),
  set_scryfall_id   TEXT              NOT NULL UNIQUE
);

CREATE TABLE LastDatabaseUpdate (
  -- Contains the history of all performed card data updates
  update_id           INTEGER           NOT NULL PRIMARY KEY,
  update_timestamp    INTEGER_TIMESTAMP NOT NULL DEFAULT (unixepoch(CURRENT_TIMESTAMP)),
  reported_card_count INTEGER           NOT NULL CHECK (reported_card_count >= 0)
);

CREATE TABLE PrintingFilters (
  -- Contains the available display filters and their current values
  filter_id                  INTEGER         NOT NULL PRIMARY KEY,
  filter_name                TEXT            NOT NULL UNIQUE,
  filter_active              BOOLEAN_INTEGER NOT NULL CHECK (filter_active IN (TRUE, FALSE)),
  printing_preference_weight INTEGER         NOT NULL DEFAULT 0
);

CREATE TABLE FilterAppliesTo (
  -- Stores which filter applies to which printing.
  printing_id    INTEGER NOT NULL REFERENCES Printing (printing_id) ON DELETE CASCADE,
  filter_id      INTEGER NOT NULL REFERENCES PrintingFilters (filter_id) ON DELETE CASCADE,
  PRIMARY KEY (printing_id, filter_id)
) WITHOUT ROWID;

CREATE TABLE RemovedPrintings (
  scryfall_id TEXT NOT NULL PRIMARY KEY,
  -- Required to keep the language when migrating a card to a known printing, because it is otherwise unknown.
  language    TEXT NOT NULL,
  oracle_id   TEXT NOT NULL
);

CREATE TABLE MigratedPrintings (
  migration_id    TEXT              NOT NULL PRIMARY KEY,
  old_scryfall_id TEXT              NOT NULL,
  new_scryfall_id TEXT,
  performed_at    INTEGER_TIMESTAMP NOT NULL
);
CREATE INDEX MigratedPrintingsLookup ON MigratedPrintings(old_scryfall_id, new_scryfall_id);

CREATE VIEW EvaluatePrintingFilters AS SELECT
  printing_id,
	coalesce(TRUE-(max(filter_active) OR set_filter_active), TRUE) AS is_visible,
	coalesce(sum(printing_preference_weight), 0) AS preference_score
FROM Printing
  INNER JOIN MTGSet USING (set_id)
  LEFT OUTER JOIN FilterAppliesTo USING (printing_id)
	LEFT OUTER JOIN PrintingFilters USING (filter_id)
	GROUP BY printing_id
;

CREATE VIEW AllPrintings AS SELECT
    face_name, set_code, set_name, icon_svg, collector_number, release_date,
    scryfall_id, png_image_uri, oracle_id, card_id, "language",
    is_front, is_card, is_oversized, is_highres_image, is_visible, is_dfc, usage_count,
    english_name, preference_score
  FROM Printing
  INNER JOIN Card USING(card_id)
  INNER JOIN PrintingFace USING (printing_id)
  INNER JOIN MTGSet USING (set_id)
;

CREATE VIEW VisiblePrintings AS SELECT
    face_name, set_code, set_name, icon_svg, collector_number, release_date,
    scryfall_id, png_image_uri, oracle_id, card_id, "language",
    is_front, is_card, is_oversized, is_highres_image, is_dfc, usage_count,
    english_name, preference_score
  FROM AllPrintings
  WHERE is_visible IS TRUE
;

COMMIT;
