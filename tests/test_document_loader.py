# Copyright (C) 2022 Thomas Hess <thomas.hess@udo.edu>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import contextlib
import dataclasses
import itertools
import pathlib
import sqlite3
import unittest.mock
import textwrap

from pytestqt.qtbot import QtBot
import pytest
from hamcrest import *

import mtg_proxy_printer.model.document_loader
from mtg_proxy_printer.units_and_sizes import PageType
import mtg_proxy_printer.model.document
import mtg_proxy_printer.sqlite_helpers


@pytest.mark.parametrize("version", [-1, 0, 1, 6, 7])
def test_unknown_save_version_raises_exception(empty_save_database: sqlite3.Connection, version: int):
    empty_save_database.execute(f"PRAGMA user_version = {version};")
    assert_that(empty_save_database.execute("PRAGMA user_version").fetchone()[0], is_(version))
    with unittest.mock.patch("mtg_proxy_printer.model.document.mtg_proxy_printer.sqlite_helpers.open_database") as mock:
        mock.return_value = empty_save_database
        assert_that(
            calling(mtg_proxy_printer.model.document_loader.DocumentLoader.Worker._read_data_from_save_path).with_args(
                "Value ignored by mock"),
            raises(AssertionError)
        )
        mock.assert_called_once()


def assert_document_is_empty(document: mtg_proxy_printer.model.document.Document):
    assert_that(document.rowCount(), is_(equal_to(1)))
    page_index = document.index(0, 0)
    assert_that(page_index.isValid())
    assert_that(document.rowCount(page_index), is_(0))


@contextlib.contextmanager
def disabled_check_constraints(db: sqlite3.Connection):
    """
    Instruct SQLite3 to ignore the SQL CHECK constraints defined in the database schema for a limited timeframe.
    """
    db.execute("PRAGMA ignore_check_constraints = TRUE;")
    yield db
    db.execute("PRAGMA ignore_check_constraints = FALSE;")


def test_valid_data_loads_correctly(
        qtbot: QtBot, document: mtg_proxy_printer.model.document.Document,
        empty_save_database: sqlite3.Connection):
    empty_save_database.execute(
        'INSERT INTO "Card" (page, slot, is_front, scryfall_id) VALUES (?, ?, ?, ?)',
        (1, 1, 1, "0000579f-7b35-4ed3-b44c-db2a538066fe")
    )
    page_layout = mtg_proxy_printer.model.document_loader.PageLayoutSettings(
        page_height=300, page_width=200,
        margin_top=20, margin_bottom=19, margin_left=18, margin_right=17,
        image_spacing_horizontal=3, image_spacing_vertical=2, draw_cut_markers=True,
    )

    assert_that(page_layout.compute_page_card_capacity(PageType.OVERSIZED), is_(greater_than_or_equal_to(1)))
    empty_save_database.execute(
        textwrap.dedent("""\
            INSERT INTO DocumentSettings (rowid, page_height, page_width,
                  margin_top, margin_bottom, margin_left, margin_right,
                  image_spacing_horizontal, image_spacing_vertical, draw_cut_markers, draw_sharp_corners)
              VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """),
        dataclasses.astuple(page_layout))
    loader = document.loader
    save_path = pathlib.Path("/tmp/invalid.mtgproxies")
    with unittest.mock.patch("mtg_proxy_printer.model.document.mtg_proxy_printer.sqlite_helpers.open_database") as mock:
        mock.return_value = empty_save_database
        with qtbot.waitSignal(loader.loading_state_changed, timeout=1000, check_params_cb=lambda value: not value), \
                qtbot.waitSignal(loader.worker.loading_file_successful, timeout=1000), \
                qtbot.waitSignal(document.page_layout_changed, timeout=1000):
            loader.load_document(save_path)
        mock.assert_called_once()
    assert_that(document.rowCount(), is_(equal_to(1)))
    page_index = document.index(0, 0)
    assert_that(page_index.isValid())
    assert_that(document.rowCount(page_index), is_(1))
    assert_that(page_index.child(0, mtg_proxy_printer.model.document.PageColumns.CardName).data(), is_("Fury Sliver"))
    assert_that(document.save_file_path, is_(equal_to(save_path)))
    assert_that(document.page_layout, is_(equal_to(page_layout)))
    assert_that(
        document.page_layout.compute_page_card_capacity(PageType.REGULAR),
        is_(equal_to(page_layout.compute_page_card_capacity(PageType.REGULAR)))
    )
    assert_that(
        document.page_layout.compute_page_card_capacity(PageType.OVERSIZED),
        is_(equal_to(page_layout.compute_page_card_capacity(PageType.OVERSIZED)))
    )


def test_document_with_mixed_pages_distributes_cards_based_on_size(
        qtbot: QtBot, document: mtg_proxy_printer.model.document.Document,
        empty_save_database: sqlite3.Connection):
    empty_save_database.executemany(
        'INSERT INTO "Card" (page, slot, is_front, scryfall_id) VALUES (?, ?, ?, ?)', [
            (1, 1, 1, "0000579f-7b35-4ed3-b44c-db2a538066fe"),
            (1, 2, 1, "650722b4-d72b-4745-a1a5-00a34836282b"),
         ]
    )
    empty_save_database.execute(
        textwrap.dedent("""\
            INSERT INTO DocumentSettings (rowid, page_height, page_width,
                  margin_top, margin_bottom, margin_left, margin_right,
                  image_spacing_horizontal, image_spacing_vertical, draw_cut_markers, draw_sharp_corners)
              VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """),
        dataclasses.astuple(mtg_proxy_printer.model.document.PageLayoutSettings.create_from_settings()))
    loader = document.loader
    save_path = pathlib.Path("/tmp/invalid.mtgproxies")
    with unittest.mock.patch("mtg_proxy_printer.model.document.mtg_proxy_printer.sqlite_helpers.open_database") as mock:
        mock.return_value = empty_save_database
        with qtbot.waitSignal(loader.loading_state_changed, timeout=1000, check_params_cb=lambda value: not value), \
                qtbot.waitSignal(loader.worker.loading_file_successful, timeout=1000):
            loader.load_document(save_path)
        mock.assert_called_once()
    assert_that(document.rowCount(), is_(2))
    total_cards = 0
    for page in document.pages:
        assert_that(page.page_type(), is_in([PageType.OVERSIZED, PageType.REGULAR]))
        total_cards += len(page)
    assert_that(total_cards, is_(2))


@pytest.mark.parametrize("data", itertools.chain(
    zip([-1, 1.3, -1000.2, "", "ABC", b"binary"], itertools.repeat(1), itertools.repeat(1), itertools.repeat("0000579f-7b35-4ed3-b44c-db2a538066fe")),
    zip(itertools.repeat(1), [-1, 1.3, -1000.2, "", "ABC", b"binary"], itertools.repeat(1), itertools.repeat("0000579f-7b35-4ed3-b44c-db2a538066fe")),
    zip(itertools.repeat(1), itertools.repeat(1), [-1, 1.3, -1000.2, "", "ABC", b"binary"], itertools.repeat("0000579f-7b35-4ed3-b44c-db2a538066fe")),
    zip(itertools.repeat(1), itertools.repeat(1), itertools.repeat(1), [-1, 1.3, -1000.2, "", "ABC", b"binary"]),
))
def test_invalid_data_in_card_columns_raises_exception(
        qtbot: QtBot, document: mtg_proxy_printer.model.document.Document,
        empty_save_database: sqlite3.Connection, data):
    # Replace the Card table with one that has no implicit type casting
    empty_save_database.execute("DROP TABLE Card")
    empty_save_database.execute("CREATE TABLE Card (page BLOB, slot BLOB, is_front BLOB, scryfall_id BLOB)")
    empty_save_database.execute('INSERT INTO "Card" (page, slot, is_front, scryfall_id) VALUES (?, ?, ?, ?)', data)
    assert_that(
        empty_save_database.execute("SELECT page, slot, is_front, scryfall_id FROM Card").fetchall(),
        contains_exactly(equal_to(data)),
        "Setup failed: Data mismatch"
    )
    loader = document.loader
    with unittest.mock.patch("mtg_proxy_printer.model.document.mtg_proxy_printer.sqlite_helpers.open_database") as mock:
        mock.return_value = empty_save_database
        with qtbot.waitSignal(loader.loading_file_failed, timeout=1000, raising=True), \
                qtbot.assertNotEmitted(loader.load_requested):
            loader.load_document(pathlib.Path("/tmp/invalid.mtgproxies"))
        mock.assert_called_once()
    assert_document_is_empty(document)
    assert_that(document.save_file_path, is_(none()))


def test_protects_against_infinite_save_data(
        qtbot: QtBot, document: mtg_proxy_printer.model.document.Document,
        empty_save_database: sqlite3.Connection):
    empty_save_database.execute("DROP TABLE Card")
    # LIMIT clause in the definition below is a safety measure.
    empty_save_database.execute(textwrap.dedent("""\
        CREATE VIEW Card (page, slot, scryfall_id, is_front) AS 
            WITH RECURSIVE card_gen (page, slot, scryfall_id, is_front) AS (
                SELECT 1, 1, '0000579f-7b35-4ed3-b44c-db2a538066fe', 1
                UNION ALL 
                SELECT 1, 1, '0000579f-7b35-4ed3-b44c-db2a538066fe', 1
                FROM card_gen
                LIMIT 100000
            )
        SELECT * FROM card_gen
        """))
    loader = document.loader
    with unittest.mock.patch("mtg_proxy_printer.model.document.mtg_proxy_printer.sqlite_helpers.open_database") as mock:
        mock.return_value = empty_save_database
        with qtbot.waitSignal(loader.loading_file_failed, timeout=1000, raising=True), \
                qtbot.assertNotEmitted(loader.load_requested):
            loader.load_document(pathlib.Path("/tmp/invalid.mtgproxies"))
        mock.assert_called_once()
    assert_document_is_empty(document)
    assert_that(document.save_file_path, is_(none()))


def test_protects_against_infinite_settings_data(
        qtbot: QtBot, document: mtg_proxy_printer.model.document.Document,
        empty_save_database: sqlite3.Connection):
    empty_save_database.execute("DROP TABLE DocumentSettings")
    # LIMIT clause in the definition below is a safety measure.
    empty_save_database.execute(textwrap.dedent("""\
        CREATE VIEW DocumentSettings (
          rowid, page_height, page_width,
          margin_top, margin_bottom, margin_left, margin_right,
          image_spacing_horizontal, image_spacing_vertical, draw_cut_markers, draw_sharp_corners) AS 
        WITH RECURSIVE settings_gen (
          rowid, page_height, page_width,
          margin_top, margin_bottom, margin_left, margin_right,
          image_spacing_horizontal, image_spacing_vertical, draw_cut_markers, draw_sharp_corners
        ) AS (
                SELECT 1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 1
                UNION ALL 
                SELECT 1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 1
                FROM settings_gen
                LIMIT 100000
            )
        SELECT * FROM settings_gen
        """))
    loader = document.loader
    with unittest.mock.patch("mtg_proxy_printer.model.document.mtg_proxy_printer.sqlite_helpers.open_database") as mock:
        mock.return_value = empty_save_database
        with qtbot.waitSignal(loader.loading_file_failed, timeout=1000, raising=True), \
                qtbot.assertNotEmitted(loader.load_requested):
            loader.load_document(pathlib.Path("/tmp/invalid.mtgproxies"))
        mock.assert_called_once()
    assert_document_is_empty(document)
    assert_that(document.save_file_path, is_(none()))


@pytest.mark.parametrize("page_type, expected", [
    (PageType.OVERSIZED, 4),
    (PageType.REGULAR, 9),
    (PageType.MIXED, 9),
    (PageType.UNDETERMINED, 9),
])
def test_page_layout_compute_page_card_capacity(
        document: mtg_proxy_printer.model.document.Document, page_type: PageType, expected: int):
    assert_that(
        document.page_layout.compute_page_card_capacity(page_type),
        is_(equal_to(expected))
    )


def test_page_layout_compute_page_card_capacity_default_value(
        document):
    assert_that(
        document.page_layout.compute_page_card_capacity(),
        is_(equal_to(9))
    )


@pytest.mark.parametrize("page_type, expected", [
    (PageType.OVERSIZED, 2),
    (PageType.REGULAR, 3),
    (PageType.MIXED, 3),
    (PageType.UNDETERMINED, 3),
])
def test_page_layout_ccompute_page_row_count(
        document: mtg_proxy_printer.model.document.Document, page_type: PageType, expected: int):
    assert_that(
        document.page_layout.compute_page_row_count(page_type),
        is_(equal_to(expected))
    )


def test_page_layout_compute_compute_page_row_count_default_value(
        document):
    assert_that(
        document.page_layout.compute_page_row_count(),
        is_(equal_to(3))
    )


@pytest.mark.parametrize("page_type, expected", [
    (PageType.OVERSIZED, 2),
    (PageType.REGULAR, 3),
    (PageType.MIXED, 3),
    (PageType.UNDETERMINED, 3),
])
def test_page_layout_compute_page_column_count(
        document: mtg_proxy_printer.model.document.Document, page_type: PageType, expected: int):
    assert_that(
        document.page_layout.compute_page_column_count(page_type),
        is_(equal_to(expected))
    )


def test_page_layout_compute_page_column_count_default_value(
        document):
    assert_that(
        document.page_layout.compute_page_column_count(),
        is_(equal_to(3))
    )
