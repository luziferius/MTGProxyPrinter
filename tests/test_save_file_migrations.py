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
from typing import Callable

import pint
import pytest
from hamcrest import *

import mtg_proxy_printer.async_tasks.document_loader
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
import mtg_proxy_printer.model.document
import mtg_proxy_printer.sqlite_helpers
from mtg_proxy_printer.async_tasks.document_loader import SAVE_FILE_MAGIC_NUMBER, CardType
import mtg_proxy_printer.save_file_migrations
from mtg_proxy_printer.units_and_sizes import unit_registry

from tests.helpers import quantity_close_to

mm: pint.Unit = unit_registry.mm


def validate_save_database_schema(db: sqlite3.Connection, schema_version: int):
    mtg_proxy_printer.sqlite_helpers.validate_database_schema(
        db, SAVE_FILE_MAGIC_NUMBER, f"document-v{schema_version}", "Invalid header"
    )
    user_version = db.execute("PRAGMA user_version").fetchone()[0]
    assert_that(user_version, is_(equal_to(schema_version)))


def create_save_db(schema_version: int) -> sqlite3.Connection:
    return mtg_proxy_printer.sqlite_helpers.open_database(":memory:", f"document-v{schema_version}")


@pytest.mark.parametrize("source_version", range(2, 7))
def test_single_migration_step_correctly_transforms_database_schema(page_layout: PageLayoutSettings, source_version: int):
    target_version = source_version+1
    db = create_save_db(source_version)
    migration: Callable[[sqlite3.Connection, PageLayoutSettings], None] = getattr(
        mtg_proxy_printer.save_file_migrations, f"_migrate_{source_version}_to_{target_version}")
    migration(db, page_layout)
    validate_save_database_schema(db, target_version)


def test_migration_2_to_3_transforms_data():
    db = create_save_db(2)
    db.executemany("INSERT INTO CARD VALUES (?, ?, ?)", [(1, 1, 'abc'), (2, 1, 'xyz')])
    mtg_proxy_printer.save_file_migrations._migrate_2_to_3(db)
    assert_that(
        db.execute("SELECT * FROM Card ORDER BY page ASC, slot ASC").fetchall(),
        contains_exactly((1, 1, 1, 'abc'), (2, 1, 1, 'xyz'))
    )

def test_migration_3_to_4_transforms_data(page_layout: PageLayoutSettings):
    db = create_save_db(3)
    cards = [(1, 1, 1, 'abc'), (2, 1, 1, 'xyz')]
    db.executemany("INSERT INTO CARD VALUES (?, ?, ?, ?)", cards)
    mtg_proxy_printer.save_file_migrations._migrate_3_to_4(db, page_layout)
    assert_that(
        db.execute("SELECT * FROM Card ORDER BY page ASC, slot ASC").fetchall(),
        contains_exactly(*cards)
    )
    assert_that(
        db.execute("SELECT * FROM DocumentSettings").fetchall(),
        contains_exactly(
        (1, page_layout.page_height.to("mm").magnitude, page_layout.page_width.to("mm").magnitude,
         page_layout.margin_top.to("mm").magnitude, page_layout.margin_bottom.to("mm").magnitude,
         page_layout.margin_left.to("mm").magnitude, page_layout.margin_right.to("mm").magnitude,
         page_layout.row_spacing.to("mm").magnitude, page_layout.column_spacing.to("mm").magnitude,
         int(page_layout.draw_cut_markers)
         )
    ))

def test_migration_4_to_5_transforms_data(page_layout: PageLayoutSettings):
    db = create_save_db(4)
    page_layout.draw_sharp_corners = True
    cards = [(1, 1, 1, 'abc'), (2, 1, 1, 'xyz')]
    db.executemany("INSERT INTO CARD VALUES (?, ?, ?, ?)", cards)
    # Insert slightly altered data, then pass the unaltered PageLayoutSettings.
    # This verifies that the stored data is used and not replaced with the current default settings.
    db.execute(
        "INSERT INTO DocumentSettings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (1, page_layout.page_height.to("mm").magnitude, page_layout.page_width.to("mm").magnitude,
         page_layout.margin_top.to("mm").magnitude+1, page_layout.margin_bottom.to("mm").magnitude-1,
         page_layout.margin_left.to("mm").magnitude, page_layout.margin_right.to("mm").magnitude,
         page_layout.row_spacing.to("mm").magnitude, page_layout.column_spacing.to("mm").magnitude,
         int(not page_layout.draw_cut_markers))
    )
    mtg_proxy_printer.save_file_migrations._migrate_4_to_5(db, page_layout)
    assert_that(
        db.execute("SELECT * FROM Card ORDER BY page ASC, slot ASC").fetchall(),
        contains_exactly(*cards)
    )
    assert_that(
        db.execute("SELECT * FROM DocumentSettings").fetchall(),
        contains_exactly(
        (1, page_layout.page_height.to("mm").magnitude, page_layout.page_width.to("mm").magnitude,
         page_layout.margin_top.to("mm").magnitude+1, page_layout.margin_bottom.to("mm").magnitude-1,
         page_layout.margin_left.to("mm").magnitude, page_layout.margin_right.to("mm").magnitude,
         page_layout.row_spacing.to("mm").magnitude, page_layout.column_spacing.to("mm").magnitude,
         int(not page_layout.draw_cut_markers), int(page_layout.draw_sharp_corners)
         )
    ))

def test_migration_5_to_6_transforms_data(page_layout: PageLayoutSettings):
    db = create_save_db(5)
    page_layout.draw_sharp_corners = True
    db.executemany("INSERT INTO Card VALUES (?, ?, ?, ?)", [(1, 1, 1, 'abc'), (2, 1, 1, 'xyz')])
    # Insert slightly altered data, then pass the unaltered PageLayoutSettings.
    # This verifies that the stored data is used and not replaced with the current default settings.
    db.execute(
        "INSERT INTO DocumentSettings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (1, page_layout.page_height.to("mm").magnitude, page_layout.page_width.to("mm").magnitude,
         page_layout.margin_top.to("mm").magnitude+1, page_layout.margin_bottom.to("mm").magnitude-1,
         page_layout.margin_left.to("mm").magnitude, page_layout.margin_right.to("mm").magnitude,
         page_layout.row_spacing.to("mm").magnitude, page_layout.column_spacing.to("mm").magnitude,
         int(not page_layout.draw_cut_markers), int(not page_layout.draw_sharp_corners))
    )
    mtg_proxy_printer.save_file_migrations._migrate_5_to_6(db, page_layout)
    assert_that(
        db.execute("SELECT * FROM Card ORDER BY page ASC, slot ASC").fetchall(),
        contains_exactly((1, 1, 1, 'abc', 'r'), (2, 1, 1, 'xyz', 'r'))
    )
    assert_that(
        db.execute("SELECT * FROM DocumentSettings").fetchall(),
        contains_inanyorder(
            # Migrated
            ("page_height", page_layout.page_height.to("mm").magnitude), ("page_width", page_layout.page_width.to("mm").magnitude),
            ("margin_top", page_layout.margin_top.to("mm").magnitude+1),("margin_bottom", page_layout.margin_bottom.to("mm").magnitude-1),
            ("margin_left", page_layout.margin_left.to("mm").magnitude),("margin_right", page_layout.margin_right.to("mm").magnitude),
            ("row_spacing", page_layout.row_spacing.to("mm").magnitude),("column_spacing", page_layout.column_spacing.to("mm").magnitude),
            ("draw_cut_markers", int(not page_layout.draw_cut_markers)),("draw_sharp_corners", int(not page_layout.draw_sharp_corners)),
            # New
            ("document_name", page_layout.document_name), ("card_bleed", page_layout.card_bleed.to("mm").magnitude),
            ("draw_page_numbers", int(page_layout.draw_page_numbers)),
    ))


def test_migration_6_to_7_transforms_data(page_layout: PageLayoutSettings):
    db = create_save_db(6)
    page_layout.draw_sharp_corners = True
    uuid1 = "aaaabbbb-1111-2222-3333-55556666ffff"
    uuid2 = "ffffeeee-9999-8888-7777-ddddccccbbbb"
    db.executemany("INSERT INTO Card VALUES (?, ?, ?, ?, ?)", [(1, 1, 1, uuid1, CardType.REGULAR), (2, 1, 1, uuid2, CardType.REGULAR)])
    # Insert slightly altered data, then pass the unaltered PageLayoutSettings.
    # This verifies that the stored data is used and not replaced with the current default settings.
    db.executemany(
        'INSERT INTO DocumentSettings ("key", value) VALUES (?, ?)',(
            ("page_height", page_layout.page_height.to("mm").magnitude), ("page_width", page_layout.page_width.to("mm").magnitude),
            ("margin_top", page_layout.margin_top.to("mm").magnitude+1),("margin_bottom", page_layout.margin_bottom.to("mm").magnitude-1),
            ("margin_left", page_layout.margin_left.to("mm").magnitude),("margin_right", page_layout.margin_right.to("mm").magnitude),
            ("row_spacing", page_layout.row_spacing.to("mm").magnitude),("column_spacing", page_layout.column_spacing.to("mm").magnitude),
            ("card_bleed", page_layout.card_bleed.to("mm").magnitude),
            ("document_name", page_layout.document_name),
            ("draw_cut_markers", int(not page_layout.draw_cut_markers)),("draw_sharp_corners", int(not page_layout.draw_sharp_corners)),
            ("draw_page_numbers", int(page_layout.draw_page_numbers)),
        )
    )
    mtg_proxy_printer.save_file_migrations._migrate_6_to_7(db, page_layout)
    assert_that(
        data := db.execute("SELECT * FROM Card ORDER BY page ASC, slot ASC").fetchall(),
        contains_exactly((1, 1, True, 'r', uuid1, None), (2, 1, True, 'r', uuid2, None)),
        f"Bad card data: {data}"
    )
    assert_that(
        data := db.execute("SELECT * FROM DocumentSettings").fetchall(),
        contains_inanyorder(
            contains_exactly("draw_cut_markers", str(not page_layout.draw_cut_markers)),
            contains_exactly("draw_sharp_corners", str(not page_layout.draw_sharp_corners)),
            contains_exactly("document_name", page_layout.document_name),
            contains_exactly("draw_page_numbers", str(page_layout.draw_page_numbers)),),
        f"Bad settings: {data}"
    )
    assert_that(
        data := db.execute("SELECT * FROM DocumentDimensions").fetchall(),
        contains_inanyorder(
            contains_exactly("page_height", quantity_close_to(page_layout.page_height)), contains_exactly("page_width", quantity_close_to(page_layout.page_width)),
            contains_exactly("margin_top", quantity_close_to(page_layout.margin_top+1*mm)), contains_exactly("margin_bottom", quantity_close_to(page_layout.margin_bottom-1*mm)),
            contains_exactly("margin_left", quantity_close_to(page_layout.margin_left)), contains_exactly("margin_right", quantity_close_to(page_layout.margin_right)),
            contains_exactly("row_spacing", quantity_close_to(page_layout.row_spacing)), contains_exactly("column_spacing", quantity_close_to(page_layout.column_spacing)),
            contains_exactly("card_bleed", quantity_close_to(page_layout.card_bleed)),
        ),
        f"Bad settings: {data}"
    )
    assert_that(db.execute("SELECT * FROM CustomCardData").fetchall(), is_(empty()))


def test__migrate_paper_size_settings_passes_on_empty_settings_table(empty_save_database):
    mtg_proxy_printer.save_file_migrations._migrate_paper_size_settings(empty_save_database)
