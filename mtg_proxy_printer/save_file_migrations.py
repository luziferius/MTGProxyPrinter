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
from mtg_proxy_printer.model.document_loader import PageLayoutSettings

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
    migrate_image_spacing_settings(db)
    logger.debug("Finished running migration tasks")


def _migrate_2_to_3(db: sqlite3.Connection):
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


def migrate_image_spacing_settings(db: sqlite3.Connection):
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
        db.execute(f"{statement}\n")
