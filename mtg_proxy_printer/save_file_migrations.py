#  Copyright © 2020-2025  Thomas Hess <thomas.hess@udo.edu>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.


import sqlite3
import textwrap

try:
    from hamcrest import contains_exactly
except ImportError:
    # Compatibility with PyHamcrest < 1.10
    from hamcrest import contains as contains_exactly

from mtg_proxy_printer.logger import get_logger
from mtg_proxy_printer.model.page_layout import PageLayoutSettings

logger = get_logger(__name__)
del get_logger

__all__ = [
    "migrate_database",
]


def migrate_database(db: sqlite3.Connection, settings: PageLayoutSettings):
    logger.debug("Running save file migration tasks")
    _migrate_2_to_3(db)
    _migrate_3_to_4(db, settings)
    _migrate_4_to_5(db, settings)
    _migrate_5_to_6(db, settings)
    _migrate_image_spacing_settings(db)
    _migrate_6_to_7(db)
    logger.debug("Finished running migration tasks")


def _migrate_2_to_3(db: sqlite3.Connection, _: PageLayoutSettings = None):
    if db.execute("PRAGMA user_version\n").fetchone()[0] != 2:
        return
    logger.debug("Migrating save file from version 2 to 3")
    for statement in [
        "ALTER TABLE Card RENAME TO Card_old",
        textwrap.dedent("""\
        CREATE TABLE Card (
          page INTEGER NOT NULL CHECK (page > 0),
          slot INTEGER NOT NULL CHECK (slot > 0),
          is_front INTEGER NOT NULL CHECK (is_front IN (0, 1)) DEFAULT 1,
          scryfall_id TEXT NOT NULL,
          PRIMARY KEY(page, slot)
        ) WITHOUT ROWID
        """),
        textwrap.dedent("""\
        INSERT INTO Card (page, slot, scryfall_id, is_front)
            SELECT page, slot, scryfall_id, 1 AS is_front
            FROM Card_old"""),
        "DROP TABLE Card_old",
        "PRAGMA user_version = 3",
    ]:
        db.execute(f"{statement};\n")


def _migrate_3_to_4(db: sqlite3.Connection, settings: PageLayoutSettings):
    if db.execute("PRAGMA user_version\n").fetchone()[0] != 3:
        return
    logger.debug("Migrating save file from version 3 to 4")
    db.execute(textwrap.dedent("""\
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
      draw_cut_markers INTEGER NOT NULL CHECK (draw_cut_markers in (0, 1))
    );
    """))
    db.execute(
        "INSERT INTO DocumentSettings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (1, settings.page_height.to("mm").magnitude, settings.page_width.to("mm").magnitude,
         settings.margin_top.to("mm").magnitude, settings.margin_bottom.to("mm").magnitude,
         settings.margin_left.to("mm").magnitude, settings.margin_right.to("mm").magnitude,
         settings.row_spacing.to("mm").magnitude, settings.column_spacing.to("mm").magnitude,
         settings.draw_cut_markers
         )
    )
    db.execute(f"PRAGMA user_version = 4;\n")


def _migrate_4_to_5(db: sqlite3.Connection, settings: PageLayoutSettings):
    if db.execute("PRAGMA user_version").fetchone()[0] != 4:
        return
    logger.debug("Migrating save file from version 4 to 5")
    db.execute("ALTER TABLE DocumentSettings RENAME TO DocumentSettings_Old;\n")
    db.execute(textwrap.dedent("""\
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
        """))
    db.execute(
        "INSERT INTO DocumentSettings SELECT *, ? FROM DocumentSettings_Old;\n",
        (settings.draw_sharp_corners,))
    db.execute("DROP TABLE DocumentSettings_Old;\n")
    db.execute("PRAGMA user_version = 5;\n")


def _migrate_5_to_6(db: sqlite3.Connection, settings: PageLayoutSettings):
    if db.execute("PRAGMA user_version").fetchone()[0] != 5:
        return
    logger.debug("Migrating save file from version 5 to 6")
    for statement in [
            "ALTER TABLE Card RENAME TO Card_old",
            textwrap.dedent("""\
            CREATE TABLE Card (
              page INTEGER NOT NULL CHECK (page > 0),
              slot INTEGER NOT NULL CHECK (slot > 0),
              is_front INTEGER NOT NULL CHECK (is_front IN (TRUE, FALSE)),
              scryfall_id TEXT NOT NULL,
              type TEXT NOT NULL CHECK (type <> ''),
              PRIMARY KEY(page, slot)
            ) WITHOUT ROWID;"""),
            textwrap.dedent("""\
            INSERT INTO Card (page, slot, scryfall_id, is_front, type)
                SELECT page, slot, scryfall_id, 1 AS is_front, 'r' AS type
                FROM Card_old"""),
            "DROP TABLE Card_old",
            "ALTER TABLE DocumentSettings RENAME TO DocumentSettings_Old",
            textwrap.dedent("""\
            CREATE TABLE DocumentSettings (
              key TEXT NOT NULL UNIQUE CHECK (key <> ''),
              value INTEGER NOT NULL CHECK (value >= 0)
            )"""),
            textwrap.dedent("""INSERT INTO DocumentSettings (key, value) 
              SELECT 'page_height', "page_height" FROM DocumentSettings_Old UNION ALL
              SELECT 'page_width', "page_width" FROM DocumentSettings_Old UNION ALL
              SELECT 'margin_top', "margin_top" FROM DocumentSettings_Old UNION ALL
              SELECT 'margin_bottom', "margin_bottom" FROM DocumentSettings_Old UNION ALL
              SELECT 'margin_left', "margin_left" FROM DocumentSettings_Old UNION ALL
              SELECT 'margin_right', "margin_right" FROM DocumentSettings_Old UNION ALL
              SELECT 'row_spacing', "image_spacing_horizontal" FROM DocumentSettings_Old UNION ALL
              SELECT 'column_spacing', "image_spacing_vertical" FROM DocumentSettings_Old UNION ALL
              SELECT 'draw_cut_markers', "draw_cut_markers" FROM DocumentSettings_Old UNION ALL
              SELECT 'draw_sharp_corners', "draw_sharp_corners" FROM DocumentSettings_Old
              """),
            "DROP TABLE DocumentSettings_Old",
            "PRAGMA user_version = 6",
    ]:
        db.execute(f"{statement}\n")
    db.executemany(
        "INSERT INTO DocumentSettings (key, value) VALUES (?, ?)", [
            ("document_name", settings.document_name),
            ("card_bleed", settings.card_bleed.to("mm").magnitude),
            ("draw_page_numbers", settings.draw_page_numbers),
        ])


def _migrate_image_spacing_settings(db: sqlite3.Connection):
    if db.execute("PRAGMA user_version").fetchone()[0] != 6:
        return
    logger.debug("Migrating save file version 6 image spacing settings")
    for statement in [
        textwrap.dedent("""\
        UPDATE DocumentSettings SET key = 'row_spacing'
          WHERE key == 'image_spacing_horizontal' 
          AND NOT EXISTS (
            SELECT key FROM DocumentSettings
            WHERE key == 'row_spacing')
        """),
        textwrap.dedent("""\
        UPDATE DocumentSettings SET key = 'column_spacing'
          WHERE key == 'image_spacing_vertical' 
          AND NOT EXISTS (
            SELECT key FROM DocumentSettings
            WHERE key == 'column_spacing')
        """),
        "DELETE FROM DocumentSettings WHERE key = 'image_spacing_vertical'",
        "DELETE FROM DocumentSettings WHERE key = 'image_spacing_horizontal'",
        # Not updating the user_version
    ]:
        db.execute(f"{statement};\n")

def _migrate_6_to_7(db: sqlite3.Connection, _: PageLayoutSettings = None):
    if db.execute("PRAGMA user_version").fetchone()[0] != 6:
        return
    logger.debug("Migrating save file from version 6 to 7")
    for statement in [
        # The new schema enforces proper UUID formatting. So ensure no invalid data is present.
        # This should never delete rows, unless the user tampered with the file.
        textwrap.dedent("""\
        DELETE FROM Card
          WHERE NOT scryfall_id GLOB
          '[a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9]-[a-f0-9][a-f0-9][a-f0-9][a-f0-9]-[a-f0-9][a-f0-9][a-f0-9][a-f0-9]-[a-f0-9][a-f0-9][a-f0-9][a-f0-9]-[a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9]'"""),
        textwrap.dedent("""\
        CREATE TABLE CustomCardData (
          -- Holds custom cards. The original file path is not retained.
          -- The path may contain sensitive information and is not portable.
          card_id TEXT NOT NULL PRIMARY KEY CHECK (card_id GLOB '[a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9]-[a-f0-9][a-f0-9][a-f0-9][a-f0-9]-[a-f0-9][a-f0-9][a-f0-9][a-f0-9]-[a-f0-9][a-f0-9][a-f0-9][a-f0-9]-[a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9]'),
          image BLOB NOT NULL,  -- The raw image content
          name TEXT NOT NULL DEFAULT '',
          set_name TEXT NOT NULL DEFAULT '',
          set_code TEXT NOT NULL DEFAULT '',
          collector_number TEXT NOT NULL DEFAULT '',
          is_front BOOLEAN_INTEGER NOT NULL CHECK (is_front IN (TRUE, FALSE)) DEFAULT TRUE,
          other_face TEXT REFERENCES CustomCardData(card_id)  -- If this is a DFC, this references the other side
        )"""),
        "ALTER TABLE Card RENAME TO Card_old",
        textwrap.dedent("""\
        CREATE TABLE Page (
          page INTEGER NOT NULL PRIMARY KEY CHECK (page > 0),
          image_size TEXT NOT NULL CHECK(image_size <> '')
        )"""),
        "INSERT INTO Page (page, image_size) SELECT DISTINCT page, '745x1040' FROM Card_old",
        textwrap.dedent("""\
        CREATE TABLE Card (
          page INTEGER NOT NULL CHECK (page > 0) REFERENCES Page(page),
          slot INTEGER NOT NULL CHECK (slot > 0),
          is_front BOOLEAN_INTEGER NOT NULL CHECK (is_front IN (TRUE, FALSE)),
          type TEXT NOT NULL CHECK (type <> ''),
          scryfall_id TEXT CHECK (scryfall_id GLOB '[a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9]-[a-f0-9][a-f0-9][a-f0-9][a-f0-9]-[a-f0-9][a-f0-9][a-f0-9][a-f0-9]-[a-f0-9][a-f0-9][a-f0-9][a-f0-9]-[a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9]'),
          custom_card_id TEXT REFERENCES CustomCardData(card_id) DEFAULT NULL,
          PRIMARY KEY(page, slot),
          CONSTRAINT "Card slot must not refer to both an official and custom card" CHECK ((scryfall_id IS NULL) OR (custom_card_id IS NULL))
        ) WITHOUT ROWID"""),
        textwrap.dedent("""\
        INSERT INTO Card (page, slot, is_front, type, scryfall_id, custom_card_id)
            SELECT page, slot, is_front, type, scryfall_id, NULL
            FROM Card_old"""),
        "DROP TABLE Card_old",
        "ALTER TABLE DocumentSettings RENAME TO DocumentSettings_old",
        textwrap.dedent("""\
        CREATE TABLE DocumentSettings (
          -- Non-numerical document settings
          "key" TEXT NOT NULL PRIMARY KEY CHECK (typeof("key") == 'text' and "key" <> ''),
          value TEXT NOT NULL CHECK (typeof(value) == 'text')
        ) WITHOUT ROWID"""),
        textwrap.dedent("""\
        INSERT INTO DocumentSettings ("key", value)
          SELECT "key", value FROM DocumentSettings_old
          WHERE "key" = 'document_name'
        """),
        textwrap.dedent("""\
        INSERT INTO DocumentSettings ("key", value)
          SELECT "key", iif(value, 'True', 'False') FROM DocumentSettings_old
          WHERE "key" in ('draw_cut_markers', 'draw_sharp_corners', 'draw_page_numbers')
        """),
        textwrap.dedent("""\
        CREATE TABLE DocumentDimensions (
          -- Numerical document settings. Values are stored as texts including units, for example '12 mm'
          -- Type contains Quantity, which is used to register an automatic conversion method to pint.Quantity
          "key" TEXT NOT NULL PRIMARY KEY CHECK (typeof("key") == 'text' and "key" <> ''),
          value TEXT_QUANTITY NOT NULL CHECK (typeof(value) == 'text' and value <> '')
        ) WITHOUT ROWID"""),
        textwrap.dedent("""\
        INSERT INTO DocumentDimensions ("key", value)
          SELECT "key", printf('%d millimeter', value) FROM DocumentSettings_old
          WHERE "key" in (
            'page_height', 'page_width', 
            'margin_top', 'margin_bottom',
            'margin_left', 'margin_right', 
            'column_spacing', 'row_spacing',
            'card_bleed'
          )
        """),
        "DROP TABLE DocumentSettings_old",
        "PRAGMA user_version = 7"
    ]:
        db.execute(f"{statement};\n")
