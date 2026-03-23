BEGIN IMMEDIATE TRANSACTION;
DROP VIEW CurrentlyEnabledSetCodeFilters;
DROP VIEW AllPrintings;
DROP VIEW VisiblePrintings;
DROP VIEW HiddenPrintingIDs;


CREATE TABLE RelatedCards (
  -- The related cards of a card are those it references or creates, and those creating or referencing it.
  -- The relationship is modelled bi-directional for better discoverability, especially for effects
  -- that search the library for a specific card. Given the target card, this modelling also finds the tutors.
  card_id    INTEGER NOT NULL REFERENCES Card(card_id) ON UPDATE CASCADE ON DELETE CASCADE,
  related_id INTEGER NOT NULL REFERENCES Card(card_id) ON UPDATE CASCADE ON DELETE CASCADE,
  PRIMARY KEY (card_id, related_id) ON CONFLICT IGNORE,
  CONSTRAINT "No self-reference" CHECK (card_id <> related_id)
) WITHOUT ROWID;
INSERT INTO RelatedCards SELECT card_id, related_id FROM RelatedPrintings;
DROP TABLE RelatedPrintings;

ALTER TABLE PrintingDisplayFilter RENAME TO FilterAppliesTo;
ALTER TABLE DisplayFilters RENAME TO PrintingFilters;
ALTER TABLE PrintingFilters ADD COLUMN printing_preference_weight INTEGER NOT NULL DEFAULT 0;

CREATE TABLE MTGSet_new (
  set_id   INTEGER PRIMARY KEY NOT NULL,
  set_code TEXT NOT NULL UNIQUE CHECK (set_code <> ''),
  set_name TEXT NOT NULL,
  release_date INTEGER NOT NULL,
  set_filter_active INTEGER NOT NULL CHECK (set_filter_active IN (TRUE, FALSE)) DEFAULT FALSE,
  icon_svg TEXT CHECK (icon_svg <> ''),
  set_scryfall_id TEXT NOT NULL UNIQUE
);
INSERT INTO MTGSet_new (set_id, set_code, set_name, release_date,            set_scryfall_id)
  SELECT                set_id, set_code, set_name, unixepoch(release_date, 'utc'), set_code
  FROM MTGSet;
DROP TABLE MTGSet;
ALTER TABLE MTGSet_new RENAME TO MTGSet;


CREATE TABLE MigratedPrintings (
  migration_id TEXT NOT NULL PRIMARY KEY,
  old_scryfall_id TEXT NOT NULL,
  new_scryfall_id TEXT,
  performed_at INTEGER NOT NULL
);
CREATE INDEX MigratedPrintingsLookup ON MigratedPrintings(old_scryfall_id, new_scryfall_id);


CREATE TABLE Card_new (
  card_id INTEGER NOT NULL PRIMARY KEY,
  oracle_id TEXT NOT NULL UNIQUE,
  -- There are now tokens sharing names with cards, so state if this is a card that can go into a deck.
  -- Used by the print selection in the deck list parser to always chose cards over same-name tokens
  is_card INTEGER NOT NULL CHECK(is_card IN (TRUE, FALSE))
);
WITH tokens(card_id, is_card) AS (
  SELECT distinct card_id, FALSE
    FROM Printing
    LEFT OUTER JOIN FilterAppliesTo USING (printing_id)
    LEFT OUTER JOIN PrintingFilters USING (filter_id)
    WHERE filter_name = 'hide-token')
INSERT INTO Card_new (card_id, oracle_id, is_card)
  SELECT              card_id, oracle_id, coalesce(is_card, TRUE) AS is_card
    FROM Card
    LEFT OUTER JOIN tokens USING (card_id);
DROP TABLE Card;
ALTER TABLE Card_new RENAME TO Card;



CREATE TABLE PrintingFace (
  printing_id INTEGER NOT NULL,
  is_front INTEGER NOT NULL CHECK (is_front IN (TRUE, FALSE)),
  face_name TEXT NOT NULL CHECK (face_name <> ''),
  png_image_uri TEXT NOT NULL,
  usage_count INTEGER NOT NULL CHECK (usage_count >= 0) DEFAULT 0,
  last_use_timestamp INTEGER,
  currently_downloaded INTEGER NOT NULL CHECK (currently_downloaded IN (TRUE, FALSE)) DEFAULT FALSE,
  PRIMARY KEY(printing_id, is_front)
);

INSERT INTO PrintingFace
        (printing_id,    is_front,    png_image_uri,
         usage_count,                 last_use_timestamp,
         face_name)
  SELECT cf.printing_id, cf.is_front, cf.png_image_uri,
         coalesce(lu.usage_count, 0), unixepoch(lu.last_use_date, 'utc') AS last_use_timestamp,
         group_concat(card_name, ' // ' ORDER BY face_number asc) AS face_name
  FROM CardFace AS cf
  JOIN Printing USING (printing_id)
  LEFT OUTER JOIN LastImageUseTimestamps AS lu USING (scryfall_id, is_front)
  JOIN FaceName AS fn USING (face_name_id)
  GROUP BY scryfall_id, is_front
;

CREATE TABLE Printing_new (
  printing_id INTEGER NOT NULL PRIMARY KEY,
  set_id INTEGER NOT NULL REFERENCES MTGSet(set_id),
  collector_number TEXT NOT NULL,
  "language" TEXT NOT NULL CHECK ("language" <> ''),
  scryfall_id TEXT NOT NULL UNIQUE,
  card_id INTEGER NOT NULL REFERENCES Card(card_id),
  -- Over-sized card indicator. Over-sized cards (value TRUE) are mostly useless for play,
  -- so store this to be able to warn the user
  is_oversized INTEGER NOT NULL CHECK (is_oversized IN (TRUE, FALSE)),
  -- Indicates if the card has high resolution images.
  is_highres_image INTEGER NOT NULL CHECK (is_highres_image IN (TRUE, FALSE)),
  -- Result cache for the printing filter evaluation
  is_visible INTEGER NOT NULL CHECK(is_visible IN (TRUE, FALSE)) DEFAULT TRUE,
  preference_score INTEGER NOT NULL DEFAULT 0,
  is_dfc INTEGER NOT NULL CHECK (is_dfc IN (TRUE, FALSE)) DEFAULT FALSE
);
INSERT INTO Printing_new
        (printing_id, set_id, collector_number, scryfall_id, card_id, is_oversized,
         is_highres_image, is_visible,              "language")
  SELECT printing_id, set_id, collector_number, scryfall_id, card_id, is_oversized,
         highres_image,    TRUE-Printing.is_hidden, "language"
    FROM Printing
    INNER JOIN CardFace USING(printing_id)
    INNER JOIN FaceName USING(face_name_id)
    INNER JOIN PrintLanguage USING(language_id)
    GROUP BY printing_id
;
DROP TABLE Printing;
ALTER TABLE Printing_new RENAME TO Printing;

DROP TABLE CardFace;
DROP TABLE FaceName;
DROP TABLE PrintLanguage;
DROP INDEX PrintingDisplayFilter_Printing_from_filter_lookup;

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
    scryfall_id, png_image_uri, oracle_id, "language",
    is_front, is_card, is_oversized, is_highres_image, is_visible, is_dfc, usage_count
  FROM Printing
  INNER JOIN Card USING(card_id)
  INNER JOIN PrintingFace USING (printing_id)
  INNER JOIN MTGSet USING (set_id)
;

CREATE VIEW VisiblePrintings AS SELECT 
    face_name, set_code, set_name, icon_svg, collector_number, release_date,
    scryfall_id, png_image_uri, oracle_id, "language",
    is_front, is_card, is_oversized, is_highres_image, is_dfc, usage_count
  FROM AllPrintings
  WHERE is_visible IS TRUE
;

PRAGMA user_version = 35;
PRAGMA foreign_keys = 1;
PRAGMA integrity_check;
ANALYZE;
COMMIT;
VACUUM;
