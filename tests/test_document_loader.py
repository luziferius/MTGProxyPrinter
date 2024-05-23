# Copyright (C) 2020-2024 Thomas Hess <thomas.hess@udo.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import contextlib
import dataclasses
import itertools
from itertools import repeat
import pathlib
import sqlite3
import unittest.mock
import textwrap

from PyQt5.QtGui import QPageSize
from pytestqt.qtbot import QtBot
import pytest
from hamcrest import *


from mtg_proxy_printer.model.document_loader import PageLayoutSettings
import mtg_proxy_printer.model.document_loader
from mtg_proxy_printer.units_and_sizes import PageType
from mtg_proxy_printer.model.carddb import CheckCard
import mtg_proxy_printer.model.document
import mtg_proxy_printer.sqlite_helpers
import mtg_proxy_printer.settings
from mtg_proxy_printer.units_and_sizes import PageSizeManager

from tests.helpers import is_dataclass_equal_to

CardType = mtg_proxy_printer.model.document_loader.CardType


@pytest.mark.parametrize("user_version", [-1, 0, 1, 7, 8])
def test_unknown_save_version_raises_exception(empty_save_database: sqlite3.Connection, user_version: int):
    empty_save_database.execute(f"PRAGMA user_version = {user_version};")
    assert_that(empty_save_database.execute("PRAGMA user_version").fetchone()[0], is_(user_version))
    with unittest.mock.patch("mtg_proxy_printer.model.document.mtg_proxy_printer.sqlite_helpers.open_database") as mock:
        mock.return_value = empty_save_database
        assert_that(
            calling(mtg_proxy_printer.model.document_loader.Worker._read_data_from_save_path).with_args(
                "Value ignored by mock", "Value ignored by mock"),
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


def _store_page_layout_settings_in_save_file(
        db: sqlite3.Connection, data: PageLayoutSettings = None):
    """
    Stores the given PageLayoutSettings in the given database.
    If the data is None, use the default settings as given by the current default application settings.
    """
    if data is None:
        data = PageLayoutSettings.create_from_settings()
    db_data = dataclasses.asdict(data).items()
    db.executemany("INSERT INTO DocumentSettings (key, value) VALUES (?, ?)", db_data)


def _load_from_memory_database_expecting_success(
        qtbot: QtBot, document: mtg_proxy_printer.model.document.Document, db: sqlite3.Connection,
        save_path = pathlib.Path("/tmp/invalid.mtgproxies")) -> None:
    loader = document.loader
    target = "mtg_proxy_printer.model.document.mtg_proxy_printer.sqlite_helpers.open_database"
    with unittest.mock.patch(target, return_value=db) as mock, \
        qtbot.waitSignals([loader.loading_state_changed]*2,
                          check_params_cbs=[(lambda value: value), (lambda value: not value)]), \
        qtbot.assert_not_emitted(loader.loading_file_failed):
            loader.load_document(save_path)
    mock.assert_called_once()


def _load_from_memory_database_expecting_failure(
        qtbot: QtBot, document: mtg_proxy_printer.model.document.Document, db: sqlite3.Connection,
        save_path = pathlib.Path("/tmp/invalid.mtgproxies")) -> None:
    loader = document.loader
    target = "mtg_proxy_printer.model.document.mtg_proxy_printer.sqlite_helpers.open_database"
    with unittest.mock.patch(target, return_value=db) as mock, \
        qtbot.wait_signal(loader.loading_file_failed), \
        qtbot.assert_not_emitted(loader.load_requested):
            loader.load_document(save_path)
    mock.assert_called_once()


@pytest.mark.parametrize("card_bleed", [0, 1, 10])
@pytest.mark.parametrize("document_name", ["", "Test"])
# Lump all 3 boolean settings together, as they do not interact in any way. Cuts test cases by factor 4
@pytest.mark.parametrize("boolean_settings", [True, False])
@pytest.mark.parametrize("row_spacing, column_spacing", [(0, 0), (2, 3)])
@pytest.mark.parametrize("margin_bottom, margin_left, margin_right, margin_top", [(0, 0, 0, 0), (5, 5, 5, 5)])
@pytest.mark.parametrize("custom_page_height, custom_page_width", [(297, 210), (2000, 1000)])
@pytest.mark.parametrize("paper_orientation", PageSizeManager.PageOrientation.keys())
@pytest.mark.parametrize("paper_size", PageSizeManager.PageSize.keys())
def test_valid_page_layout_settings_load_correctly(
        qtbot: QtBot, empty_save_database: sqlite3.Connection,
        card_bleed: int, document_name: str, boolean_settings: bool,
        row_spacing: int, column_spacing: int,
        margin_bottom: int, margin_left: int, margin_right: int, margin_top: int,
        custom_page_height: int, custom_page_width: int,
        paper_orientation: str, paper_size: str
):
    default_settings = PageLayoutSettings.create_from_settings()
    stored_settings = PageLayoutSettings(
        card_bleed=card_bleed, document_name=document_name, draw_cut_markers=boolean_settings,
        draw_page_numbers=boolean_settings, draw_sharp_corners=boolean_settings,
        row_spacing=row_spacing, column_spacing=column_spacing,
        margin_bottom=margin_bottom, margin_left=margin_left, margin_right=margin_right, margin_top=margin_top,
        custom_page_height=custom_page_height, custom_page_width=custom_page_width,
        paper_orientation=paper_orientation, paper_size=paper_size,
    )
    if stored_settings.compute_page_card_capacity(PageType.OVERSIZED) == 0:
        pytest.skip("Invalid page size")

    _store_page_layout_settings_in_save_file(empty_save_database, stored_settings)
    settings = mtg_proxy_printer.model.document_loader.Worker._read_document_settings(
        empty_save_database, default_settings)

    assert_that(settings, is_dataclass_equal_to(stored_settings))
    if settings.paper_size == "Custom":
        assert_that(settings, has_properties({"page_height": custom_page_height, "page_width": custom_page_width}))
    else:
        size = QPageSize.size(PageSizeManager.PageSize[paper_size], QPageSize.Unit.Millimeter)
        if settings.paper_orientation == "Landscape":
            size = size.transposed()
        assert_that(
            settings,
            has_properties({
                "page_height": close_to(size.height(), 0.05),
                "page_width": close_to(size.width(), 0.05)})
        )


def test_valid_card_data_loads_correctly(
        qtbot: QtBot, document: mtg_proxy_printer.model.document.Document,
        empty_save_database: sqlite3.Connection):
    _store_page_layout_settings_in_save_file(empty_save_database)
    empty_save_database.execute(
        'INSERT INTO "Card" (page, slot, is_front, scryfall_id, type) VALUES (?, ?, ?, ?, ?)',
        (1, 1, 1, "0000579f-7b35-4ed3-b44c-db2a538066fe", "r")
    )
    _load_from_memory_database_expecting_success(qtbot, document, empty_save_database)
    assert_that(document.rowCount(), is_(equal_to(1)))
    page_index = document.index(0, 0)
    assert_that(page_index.isValid())
    assert_that(document.rowCount(page_index), is_(1))
    assert_that(
        document.index(0, mtg_proxy_printer.model.document.PageColumns.CardName, page_index).data(),
        is_("Fury Sliver")
    )


def test_loading_document_stores_save_file_path_in_document(
        qtbot: QtBot, document: mtg_proxy_printer.model.document.Document,
        empty_save_database: sqlite3.Connection):
    _store_page_layout_settings_in_save_file(empty_save_database)
    save_path = pathlib.Path("/tmp/invalid.mtgproxies")
    _load_from_memory_database_expecting_success(qtbot, document, empty_save_database, save_path)
    assert_that(document.save_file_path, is_(equal_to(save_path)))


def test_document_with_mixed_pages_distributes_cards_based_on_size(
        qtbot: QtBot, document: mtg_proxy_printer.model.document.Document,
        empty_save_database: sqlite3.Connection):
    empty_save_database.executemany(
        'INSERT INTO "Card" (page, slot, is_front, scryfall_id, type) VALUES (?, ?, ?, ?, ?)', [
            (1, 1, 1, "0000579f-7b35-4ed3-b44c-db2a538066fe", "r"),
            (1, 2, 1, "650722b4-d72b-4745-a1a5-00a34836282b", "r"),
         ]
    )
    page_layout = mtg_proxy_printer.model.document.PageLayoutSettings.create_from_settings()
    page_layout_items = dataclasses.asdict(page_layout).items()
    empty_save_database.executemany(
        "INSERT INTO DocumentSettings (key, value) VALUES (?, ?)",
        page_layout_items
    )
    _load_from_memory_database_expecting_success(qtbot, document, empty_save_database)
    assert_that(document.rowCount(), is_(2))
    total_cards = 0
    for page in document.pages:
        assert_that(page.page_type(), is_in([PageType.OVERSIZED, PageType.REGULAR]))
        total_cards += len(page)
    assert_that(total_cards, is_(2))


@pytest.mark.parametrize("data", itertools.chain(
    # Syntactically invalid
    zip([-1, 1.3, -1000.2, "", "ABC", b"binary"], repeat(1), repeat(1), repeat("0000579f-7b35-4ed3-b44c-db2a538066fe"), repeat(CardType.REGULAR.value)),
    zip(repeat(1), [-1, 1.3, -1000.2, "", "ABC", b"binary"], repeat(1), repeat("0000579f-7b35-4ed3-b44c-db2a538066fe"), repeat(CardType.REGULAR.value)),
    zip(repeat(1), repeat(1), [-1, 1.3, -1000.2, "", "ABC", b"binary"], repeat("0000579f-7b35-4ed3-b44c-db2a538066fe"), repeat(CardType.REGULAR.value)),
    zip(repeat(1), repeat(1), repeat(1), [-1, 1.3, -1000.2, "", "ABC", b"binary"], repeat(CardType.REGULAR.value)),
    zip([-1, 1.3, -1000.2, "", "ABC", b"binary"], repeat(1), repeat(1), repeat("0000579f-7b35-4ed3-b44c-db2a538066fe"), repeat(CardType.CHECK_CARD.value)),
    zip(repeat(1), [-1, 1.3, -1000.2, "", "ABC", b"binary"], repeat(1), repeat("0000579f-7b35-4ed3-b44c-db2a538066fe"), repeat(CardType.CHECK_CARD.value)),
    zip(repeat(1), repeat(1), [-1, 1.3, -1000.2, "", "ABC", b"binary"], repeat("0000579f-7b35-4ed3-b44c-db2a538066fe"), repeat(CardType.CHECK_CARD.value)),
    zip(repeat(1), repeat(1), repeat(1), [-1, 1.3, -1000.2, "", "ABC", b"binary"], repeat(CardType.CHECK_CARD.value)),
    # Semantically invalid, as type "d" means generating a DFC check card for a single sided card.
    zip(repeat(1), repeat(1), repeat(1), repeat("0000579f-7b35-4ed3-b44c-db2a538066fe"), [-1, 1.3, -1000.2, "", b"binary", CardType.CHECK_CARD.value]),
    zip(repeat(1), repeat(1), repeat(0), repeat("0000579f-7b35-4ed3-b44c-db2a538066fe"), [-1, 1.3, -1000.2, "", b"binary", CardType.CHECK_CARD.value]),
))
def test_invalid_data_in_card_columns_raises_exception(
        qtbot: QtBot, document: mtg_proxy_printer.model.document.Document,
        empty_save_database: sqlite3.Connection, data):
    # Replace the Card table with one that has no implicit type casting
    empty_save_database.execute("DROP TABLE Card")
    empty_save_database.execute("CREATE TABLE Card (page BLOB, slot BLOB, is_front BLOB, scryfall_id BLOB, type BLOB)")
    empty_save_database.execute('INSERT INTO Card (page, slot, is_front, scryfall_id, type) VALUES (?, ?, ?, ?, ?)', data)
    assert_that(
        empty_save_database.execute("SELECT page, slot, is_front, scryfall_id, type FROM Card").fetchall(),
        contains_exactly(equal_to(data)),
        "Setup failed: Data mismatch"
    )
    _load_from_memory_database_expecting_failure(qtbot, document, empty_save_database)
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
    _load_from_memory_database_expecting_failure(qtbot, document, empty_save_database)
    assert_document_is_empty(document)
    assert_that(document.save_file_path, is_(none()))


def generate_test_cases_for_test_protects_against_infinite_settings_data():
    # LIMIT clause in the definitions below are safety measures.
    yield 4, textwrap.dedent("""\
        CREATE VIEW DocumentSettings (
          rowid, page_height, page_width,
          margin_top, margin_bottom, margin_left, margin_right,
          image_spacing_horizontal, image_spacing_vertical, draw_cut_markers) AS 
        WITH RECURSIVE settings_gen (
          rowid, page_height, page_width,
          margin_top, margin_bottom, margin_left, margin_right,
          image_spacing_horizontal, image_spacing_vertical, draw_cut_markers
        ) AS (
            SELECT 1, 1, 1, 1, 2, 2, 2, 2, 2, 1
            UNION ALL 
            SELECT 1, 1, 1, 1, 2, 2, 2, 2, 2, 1
            FROM settings_gen
            LIMIT 100000
            )
        SELECT * FROM settings_gen
        """)
    yield 5, textwrap.dedent("""\
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
        """)
    yield 6, textwrap.dedent("""\
        CREATE VIEW DocumentSettings (key, value) AS 
        WITH RECURSIVE settings_gen (
          key, value
        ) AS (
            SELECT 'key', 'something'
            UNION ALL 
            SELECT 'key', 'something'
            FROM settings_gen
            LIMIT 100000
            )
        SELECT * FROM settings_gen
        """)


@pytest.mark.parametrize("user_version, script", generate_test_cases_for_test_protects_against_infinite_settings_data())
def test_protects_against_infinite_settings_data(
        qtbot: QtBot, document: mtg_proxy_printer.model.document.Document,
        empty_save_database: sqlite3.Connection, user_version: int, script: str):
    empty_save_database.execute(f"PRAGMA user_version = {user_version}")
    empty_save_database.execute("DROP TABLE DocumentSettings")
    empty_save_database.execute(script)
    _load_from_memory_database_expecting_failure(qtbot, document, empty_save_database)
    assert_document_is_empty(document)
    assert_that(document.save_file_path, is_(none()))


def test_cancelling_loading_does_not_crash(
        qtbot: QtBot, document: mtg_proxy_printer.model.document.Document,
        empty_save_database: sqlite3.Connection):
    empty_save_database.executemany(
        'INSERT INTO "Card" (page, slot, is_front, scryfall_id, type) VALUES (?, ?, ?, ?, ?)', [
            (1, 1, 1, "0000579f-7b35-4ed3-b44c-db2a538066fe", "r"),
            (1, 2, 1, "650722b4-d72b-4745-a1a5-00a34836282b", "r"),
        ]
    )
    loader = document.loader
    loader.begin_loading_loop.connect(loader.cancel)
    target = "mtg_proxy_printer.model.document.mtg_proxy_printer.sqlite_helpers.open_database"
    expected_signals = [loader.begin_loading_loop, loader.progress_loading_loop, loader.loading_state_changed, loader.finished]
    with unittest.mock.patch(target, return_value=empty_save_database), \
            qtbot.wait_signals(expected_signals, timeout=100):
        loader.load_document(pathlib.Path("/tmp/invalid.mtgproxies"))


def test_loads_check_card(
        qtbot: QtBot, document: mtg_proxy_printer.model.document.Document, empty_save_database: sqlite3.Connection):
    empty_save_database.executemany(
        'INSERT INTO "Card" (page, slot, is_front, scryfall_id, type) VALUES (?, ?, ?, ?, ?)', [
            (1, 1, 1, "b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", CardType.CHECK_CARD.value),
         ]
    )
    _load_from_memory_database_expecting_success(qtbot, document, empty_save_database)
    assert_that(
        document.pages, contains_exactly(
            contains_exactly(has_property("card", all_of(
                instance_of(CheckCard),
                has_properties({
                    "image_file": not_none(),
                    "name": "Growing Rites of Itlimoc // Itlimoc, Cradle of the Sun",
                    "is_front": True,
                    "is_dfc": False,
                })
            )))
        )
    )


@pytest.fixture(params=itertools.product([
    (4, [1, 200, 150, 4, 5, 6, 7, 2, 3, 1]),
    (5, [1, 200, 150, 4, 5, 6, 7, 2, 3, 1, 0]),
    # Only old image spacing keys present
    (6, [("document_name", ""), ("draw_cut_markers", 1), ("draw_page_numbers", 0), ("draw_sharp_corners", 0),
         ("image_spacing_horizontal", 2), ("image_spacing_vertical", 3), ("margin_top", 4), ("margin_bottom", 5),
         ("margin_left", 6), ("margin_right", 7), ("page_height", 200), ("page_width", 150)]),
    # Old and new image spacing keys present. This should never exist in the wild. Ensure that the new keys are used.
    (6, [("document_name", ""), ("draw_cut_markers", 1), ("draw_page_numbers", 0), ("draw_sharp_corners", 0),
         ("image_spacing_horizontal", 8), ("image_spacing_vertical", 9), ("margin_top", 4), ("margin_bottom", 5),
         ("margin_left", 6), ("margin_right", 7), ("page_height", 200), ("page_width", 150),
         ("row_spacing", 2), ("column_spacing", 3)]),
    # Only new spacing keys. Old paper size keys from before implementing enum-based paper sizes
    (6, [("document_name", ""), ("draw_cut_markers", 1), ("draw_page_numbers", 0), ("draw_sharp_corners", 0),
         ("margin_top", 4), ("margin_bottom", 5), ("margin_left", 6), ("margin_right", 7),
         ("page_height", 200), ("page_width", 150),
         ("row_spacing", 2), ("column_spacing", 3)]),
    # Old and new paper size keys. Should never exist in the wild.
    (6, [("document_name", ""), ("draw_cut_markers", 1), ("draw_page_numbers", 0), ("draw_sharp_corners", 0),
         ("margin_top", 4), ("margin_bottom", 5), ("margin_left", 6), ("margin_right", 7),
         ("page_height", 250), ("page_width", 180),
         ("custom_page_height", 200), ("custom_page_width", 150), ("paper_size", "Custom"),
         ("row_spacing", 2), ("column_spacing", 3)]),
    ], [True, False]))
def legacy_save_file(request):
    (save_version, settings), reverse_unordered = request.param  # type: (int, list), bool
    db = mtg_proxy_printer.sqlite_helpers.open_database(
        ":memory:", f"document-v{save_version}",
        mtg_proxy_printer.model.document_loader.DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION, False)
    if save_version < 6:
        db.execute(f"INSERT INTO DocumentSettings VALUES ({', '.join('?'*len(settings))})", settings)
    else:
        db.executemany("INSERT INTO DocumentSettings (key, value) VALUES (?, ?)", settings)
    if reverse_unordered:
        db.execute("PRAGMA reverse_unordered_selects = TRUE")
    yield db
    db.close()
    del db


def test_load_settings_from_legacy_save_file_is_successful(
        qtbot: QtBot, legacy_save_file: sqlite3.Connection, document_light):
    _load_from_memory_database_expecting_success(qtbot, document_light, legacy_save_file)
    annotations = document_light.page_layout.__annotations__
    assert_that(
        document_light.page_layout,
        has_properties({item: instance_of(value) for item, value in annotations.items()})
    )
    assert_that(document_light.page_layout, has_properties({
        "document_name": "", "draw_cut_markers": True, "draw_page_numbers": False, "draw_sharp_corners": False,
        "row_spacing": 2, "column_spacing": 3,
        "margin_top": 4, "margin_bottom": 5, "margin_left": 6, "margin_right": 7,
        "page_height": close_to(200, 0.05), "page_width": close_to(150, 0.05),
        "custom_page_height": 200, "custom_page_width": 150,
        "paper_size": "Custom", "paper_orientation": "Portrait",
    }))


@pytest.mark.parametrize("title", ["str", "", "1", "0x1", "1.0.0", "1..0", "01", "1.0"])
def test_load_correctly_sets_document_title(
        qtbot: QtBot, empty_save_database: sqlite3.Connection, document_light, title):
    if title.startswith("0") or title == "1.0":
        # TODO: Leading zeros, and trailing zero decimals aren't handled correctly
        pytest.xfail("Leading zeros and trailing zero decimals not yet supported correctly")
    empty_save_database.executemany(
        "INSERT INTO DocumentSettings (key, value) VALUES (?, ?)",
        dataclasses.asdict(document_light.page_layout).items())
    empty_save_database.execute(
        "UPDATE DocumentSettings SET value = ? WHERE key = ?",
        (title, "document_name"))
    _load_from_memory_database_expecting_success(qtbot, document_light, empty_save_database)
    assert_that(
        document_light.page_layout,
        has_properties({
            item: instance_of(value)
            for item, value
            in document_light.page_layout.__annotations__.items()})
    )
    assert_that(document_light.page_layout, has_property("document_name", equal_to(title)))
