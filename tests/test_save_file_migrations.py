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


import contextlib
import itertools
import functools
import pathlib
import sqlite3
import typing
import unittest.mock
import textwrap
from typing import Callable

import pint
from pint.facets import QuantityT
from pytestqt.qtbot import QtBot
import pytest
from hamcrest import *

import mtg_proxy_printer.model.document_loader
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from tests.helpers import quantity_close_to
from mtg_proxy_printer.units_and_sizes import PageType, unit_registry, UnitT
from mtg_proxy_printer.model.carddb import CheckCard
import mtg_proxy_printer.model.document

import mtg_proxy_printer.sqlite_helpers
from mtg_proxy_printer.model.document_loader import SAVE_FILE_MAGIC_NUMBER, DocumentLoader

from mtg_proxy_printer.save_file_migrations import migrate_database, _migrate_2_to_3, _migrate_3_to_4, _migrate_4_to_5,\
    _migrate_5_to_6, _migrate_image_spacing_settings
import mtg_proxy_printer.save_file_migrations


def validate_save_database_schema(db: sqlite3.Connection, schema_version: int):
    mtg_proxy_printer.sqlite_helpers.validate_database_schema(
        db, SAVE_FILE_MAGIC_NUMBER, f"document-v{schema_version}",
        DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION, "Invalid header"
    )

def create_save_db(schema_version: int) -> sqlite3.Connection:
    return mtg_proxy_printer.sqlite_helpers.open_database(
        ":memory:", f"document-v{schema_version}", DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION)


@pytest.mark.parametrize("source_version", range(2, 6))
def test_single_migration_step_correctly_transforms_database_schema(source_version: int):
    settings = PageLayoutSettings.create_from_settings()
    target_version = source_version+1
    db = create_save_db(source_version)
    migration: Callable[[sqlite3.Connection, PageLayoutSettings], None] = getattr(
        mtg_proxy_printer.save_file_migrations, f"_migrate_{source_version}_to_{target_version}")
    migration(db, settings)
    validate_save_database_schema(db, target_version)


def test_migration_2_to_3_transforms_data():
    db = create_save_db(2)
    db.executemany("INSERT INTO CARD VALUES (?, ?, ?)", [(1, 1, 'abc'), (2, 1, 'xyz')])
    mtg_proxy_printer.save_file_migrations._migrate_2_to_3(db)
    assert_that(
        db.execute("SELECT * FROM Card ORDER BY page ASC, slot ASC").fetchall(),
        contains_exactly((1, 1, 1, 'abc'), (2, 1, 1, 'xyz'))
    )

def test_migration_3_to_4_transforms_data():
    db = create_save_db(3)
    settings = PageLayoutSettings.create_from_settings()
    cards = [(1, 1, 1, 'abc'), (2, 1, 1, 'xyz')]
    db.executemany("INSERT INTO CARD VALUES (?, ?, ?, ?)", cards)
    mtg_proxy_printer.save_file_migrations._migrate_3_to_4(db, settings)
    assert_that(
        db.execute("SELECT * FROM Card ORDER BY page ASC, slot ASC").fetchall(),
        contains_exactly(*cards)
    )
    assert_that(
        db.execute("SELECT * FROM DocumentSettings").fetchall(),
        contains_exactly(
        (1, settings.page_height.to("mm").magnitude, settings.page_width.to("mm").magnitude,
         settings.margin_top.to("mm").magnitude, settings.margin_bottom.to("mm").magnitude,
         settings.margin_left.to("mm").magnitude, settings.margin_right.to("mm").magnitude,
         settings.row_spacing.to("mm").magnitude, settings.column_spacing.to("mm").magnitude,
         int(settings.draw_cut_markers)
         )
    ))

def test_migration_4_to_5_transforms_data():
    db = create_save_db(4)
    settings = PageLayoutSettings.create_from_settings()
    settings.draw_sharp_corners = True
    cards = [(1, 1, 1, 'abc'), (2, 1, 1, 'xyz')]
    db.executemany("INSERT INTO CARD VALUES (?, ?, ?, ?)", cards)
    db.execute("INSERT INTO DocumentSettings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (1, settings.page_height.to("mm").magnitude, settings.page_width.to("mm").magnitude,
         settings.margin_top.to("mm").magnitude, settings.margin_bottom.to("mm").magnitude,
         settings.margin_left.to("mm").magnitude, settings.margin_right.to("mm").magnitude,
         settings.row_spacing.to("mm").magnitude, settings.column_spacing.to("mm").magnitude,
         int(settings.draw_cut_markers))
               )
    mtg_proxy_printer.save_file_migrations._migrate_4_to_5(db, settings)
    assert_that(
        db.execute("SELECT * FROM Card ORDER BY page ASC, slot ASC").fetchall(),
        contains_exactly(*cards)
    )
    assert_that(
        db.execute("SELECT * FROM DocumentSettings").fetchall(),
        contains_exactly(
        (1, settings.page_height.to("mm").magnitude, settings.page_width.to("mm").magnitude,
         settings.margin_top.to("mm").magnitude, settings.margin_bottom.to("mm").magnitude,
         settings.margin_left.to("mm").magnitude, settings.margin_right.to("mm").magnitude,
         settings.row_spacing.to("mm").magnitude, settings.column_spacing.to("mm").magnitude,
         int(settings.draw_cut_markers), int(settings.draw_sharp_corners)
         )
    ))