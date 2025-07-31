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
from itertools import chain, repeat
from pathlib import Path
import sqlite3
import unittest.mock
import textwrap

from PySide6.QtGui import QColorConstants
from pytestqt.qtbot import QtBot
import pytest
from hamcrest import *

from mtg_proxy_printer.model.document_loader import DocumentLoader, CardType
from tests.helpers import quantity_close_to
from mtg_proxy_printer.units_and_sizes import PageType, unit_registry, Unit, CardSizes
from mtg_proxy_printer.model.card import CheckCard
import mtg_proxy_printer.sqlite_helpers
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.document_page import PageColumns
from mtg_proxy_printer.model.page_layout import PageLayoutSettings

from tests.helpers import create_save_database_with

OPEN_DATABASE = "mtg_proxy_printer.model.document_loader.open_database"
MOCK_SAVE_PATH = Path("/tmp/invalid.mtgproxies")

mm: Unit = unit_registry.mm
degree = unit_registry.degree


@pytest.fixture()
def loader(document: Document):
    loader = DocumentLoader(document, MOCK_SAVE_PATH)
    return loader


@pytest.fixture()
def page_layout() -> PageLayoutSettings:
    page_layout = PageLayoutSettings(
        custom_page_height=300 * mm, custom_page_width=200 * mm,
        margin_top=20*mm, margin_bottom=19*mm, margin_left=18*mm, margin_right=17*mm,
        row_spacing=3*mm, column_spacing=2*mm, card_bleed=1*mm,
        draw_cut_markers=True, draw_sharp_corners=False, draw_page_numbers=True,
        paper_size="Custom", paper_orientation="Portrait",
        watermark_angle=1*degree, watermark_color=QColorConstants.Cyan, watermark_font_size=60*unit_registry.point,
        watermark_pos_x=23*mm, watermark_pos_y=24*mm, watermark_text="Watermark",
    )
    assert_that(
        page_layout.compute_page_card_capacity(PageType.OVERSIZED), is_(greater_than_or_equal_to(1)), "Setup failed"
    )
    return page_layout


@pytest.mark.parametrize("user_version", [-1, 0, 1, 8, 9])
def test_unknown_save_version_raises_exception(empty_save_database: sqlite3.Connection, user_version: int):
    empty_save_database.execute(f"PRAGMA user_version = {user_version};")
    assert_that(empty_save_database.execute("PRAGMA user_version").fetchone()[0], is_(user_version))
    with unittest.mock.patch(OPEN_DATABASE, return_value=empty_save_database) as open_database:
        assert_that(
            calling(DocumentLoader._open_validate_and_migrate_save_file).with_args(Path()),
            raises(AssertionError)
        )
    open_database.assert_called_once()


def assert_document_is_empty(document: Document):
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


def test_document_with_card_loads_correctly(
        qtbot: QtBot, loader: DocumentLoader, empty_save_database: sqlite3.Connection, page_layout: PageLayoutSettings):
    document = loader.document
    create_save_database_with(
        empty_save_database,
        [(1, CardSizes.REGULAR)],
        [(1, 1, True, "0000579f-7b35-4ed3-b44c-db2a538066fe", CardType.REGULAR)],
        page_layout
    )
    with unittest.mock.patch(OPEN_DATABASE, return_value=empty_save_database) as open_database, \
            qtbot.wait_signals([loader.load_requested, document.action_applied]), \
            qtbot.assert_not_emitted(loader.loading_file_failed):
        loader.run()
    open_database.assert_called_once()
    assert_that(document.rowCount(), is_(equal_to(1)))
    page_index = document.index(0, 0)
    assert_that(page_index.isValid())
    assert_that(document.rowCount(page_index), is_(1))
    assert_that(
        document.index(0, PageColumns.CardName, page_index).data(),
        is_("Fury Sliver")
    )
    assert_that(document.save_file_path, is_(equal_to(MOCK_SAVE_PATH)))
    assert_that(document.page_layout, is_(equal_to(page_layout)))


def test_empty_document_loads_correctly(
        qtbot: QtBot, loader: DocumentLoader,
        empty_save_database: sqlite3.Connection, page_layout: PageLayoutSettings):
    document = loader.document
    create_save_database_with(empty_save_database, [], [], page_layout)
    with unittest.mock.patch(OPEN_DATABASE, return_value=empty_save_database) as mock, \
        qtbot.wait_signals([loader.load_requested, document.action_applied]), \
        qtbot.assert_not_emitted(loader.loading_file_failed):
            loader.run()
    mock.assert_called_once()
    assert_that(document.rowCount(), is_(equal_to(1)))
    page_index = document.index(0, 0)
    assert_that(page_index.isValid())
    assert_that(document.rowCount(page_index), is_(0))
    assert_that(document.save_file_path, is_(equal_to(MOCK_SAVE_PATH)))
    assert_that(document.page_layout, is_(equal_to(page_layout)))


def test_document_with_mixed_pages_distributes_cards_based_on_size(
        qtbot: QtBot, loader: DocumentLoader, page_layout: PageLayoutSettings,
        empty_save_database: sqlite3.Connection):
    document = loader.document
    create_save_database_with(
        empty_save_database,
        [(1, CardSizes.REGULAR)],
        [
            (1, 1, True, "0000579f-7b35-4ed3-b44c-db2a538066fe", CardType.REGULAR),
            (1, 2, True, "650722b4-d72b-4745-a1a5-00a34836282b", CardType.REGULAR),
        ],
        page_layout
    )
    with unittest.mock.patch(OPEN_DATABASE, return_value=empty_save_database) as open_database, \
        qtbot.wait_signals([loader.load_requested, document.action_applied]):
            loader.run()
    open_database.assert_called_once()
    assert_that(document.rowCount(), is_(2))
    total_cards = 0
    for page in document.pages:
        assert_that(page.page_type(), is_in([PageType.OVERSIZED, PageType.REGULAR]))
        total_cards += len(page)
    assert_that(total_cards, is_(2))


@pytest.mark.parametrize("data", chain(
    # Syntactically invalid
    zip([-1, 1.3, -1000.2, "", "ABC", b"binary"], repeat(1), repeat(1), repeat("0000579f-7b35-4ed3-b44c-db2a538066fe"), repeat(CardType.REGULAR)),
    zip(repeat(1), [-1, 1.3, -1000.2, "", "ABC", b"binary"], repeat(1), repeat("0000579f-7b35-4ed3-b44c-db2a538066fe"), repeat(CardType.REGULAR)),
    zip(repeat(1), repeat(1), [-1, 1.3, -1000.2, "", "ABC", b"binary"], repeat("0000579f-7b35-4ed3-b44c-db2a538066fe"), repeat(CardType.REGULAR)),
    zip(repeat(1), repeat(1), repeat(1), [-1, 1.3, -1000.2, "", "ABC", b"binary"], repeat(CardType.REGULAR)),
    zip([-1, 1.3, -1000.2, "", "ABC", b"binary"], repeat(1), repeat(1), repeat("0000579f-7b35-4ed3-b44c-db2a538066fe"), repeat(CardType.CHECK_CARD)),
    zip(repeat(1), [-1, 1.3, -1000.2, "", "ABC", b"binary"], repeat(1), repeat("0000579f-7b35-4ed3-b44c-db2a538066fe"), repeat(CardType.CHECK_CARD)),
    zip(repeat(1), repeat(1), [-1, 1.3, -1000.2, "", "ABC", b"binary"], repeat("0000579f-7b35-4ed3-b44c-db2a538066fe"), repeat(CardType.CHECK_CARD)),
    zip(repeat(1), repeat(1), repeat(1), [-1, 1.3, -1000.2, "", "ABC", b"binary"], repeat(CardType.CHECK_CARD)),
    # Semantically invalid, as type "d" it means generating a DFC check card for a single sided card.
    zip(repeat(1), repeat(1), repeat(1), repeat("0000579f-7b35-4ed3-b44c-db2a538066fe"), [-1, 1.3, -1000.2, "", b"binary", CardType.CHECK_CARD]),
    zip(repeat(1), repeat(1), repeat(0), repeat("0000579f-7b35-4ed3-b44c-db2a538066fe"), [-1, 1.3, -1000.2, "", b"binary", CardType.CHECK_CARD]),
))
def test_invalid_data_in_card_columns_raises_exception(
        qtbot: QtBot, loader: DocumentLoader,
        empty_save_database: sqlite3.Connection, data):
    document = loader.document
    # Replace the Card table with one that has no implicit type casting
    empty_save_database.execute("DROP TABLE Card")
    empty_save_database.execute("CREATE TABLE Card (page BLOB, slot BLOB, is_front BLOB, scryfall_id BLOB, type BLOB)")
    empty_save_database.execute('INSERT INTO Card (page, slot, is_front, scryfall_id, type) VALUES (?, ?, ?, ?, ?)', data)
    assert_that(
        empty_save_database.execute("SELECT page, slot, is_front, scryfall_id, type FROM Card").fetchall(),
        contains_exactly(equal_to(data)),
        "Setup failed: Data mismatch"
    )
    with unittest.mock.patch(OPEN_DATABASE, return_value=empty_save_database) as open_database, \
        qtbot.wait_signal(loader.loading_file_failed, raising=True), \
        qtbot.assert_not_emitted(loader.load_requested):
            loader.run()
    open_database.assert_called_once()
    assert_document_is_empty(document)
    assert_that(document.save_file_path, is_(none()))


def test_protects_against_infinite_save_data(
        qtbot: QtBot, loader: DocumentLoader,
        empty_save_database: sqlite3.Connection):
    document = loader.document
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
    with unittest.mock.patch(OPEN_DATABASE, return_value=empty_save_database) as open_database, \
        qtbot.wait_signal(loader.loading_file_failed, raising=True), \
        qtbot.assert_not_emitted(loader.load_requested):
            loader.run()
    open_database.assert_called_once()
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
        qtbot: QtBot, loader: DocumentLoader,
        empty_save_database: sqlite3.Connection, user_version: int, script: str):
    document = loader.document
    empty_save_database.execute(f"PRAGMA user_version = {user_version}")
    empty_save_database.execute("DROP TABLE DocumentSettings")
    empty_save_database.execute(script)
    with unittest.mock.patch(OPEN_DATABASE, return_value=empty_save_database) as open_database, \
        qtbot.wait_signal(loader.loading_file_failed, raising=True), \
        qtbot.assert_not_emitted(loader.load_requested):
            loader.run()
    open_database.assert_called_once()
    assert_document_is_empty(document)
    assert_that(document.save_file_path, is_(none()))


def test_cancelling_loading_does_not_crash(
        loader: DocumentLoader,
        empty_save_database: sqlite3.Connection):
    pytest.skip("Cancelling loading not yet supported again")
    document = loader.document
    create_save_database_with(
        empty_save_database,
        [(1, CardSizes.REGULAR)],
        [
            (1, 1, True, "0000579f-7b35-4ed3-b44c-db2a538066fe", CardType.REGULAR),
            (1, 2, True, "650722b4-d72b-4745-a1a5-00a34836282b", CardType.REGULAR),
        ],
        document.page_layout
    )
    loader.begin_loading_loop.connect(loader.cancel)
    with unittest.mock.patch(OPEN_DATABASE, return_value=empty_save_database) as open_database:
        loader.run()
    open_database.assert_called_once()


def test_loads_check_card(
        qtbot: QtBot, loader: DocumentLoader, empty_save_database: sqlite3.Connection):
    document = loader.document
    create_save_database_with(
        empty_save_database,
        [(1, CardSizes.REGULAR)],
        [(1, 1, True, "b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", CardType.CHECK_CARD)],
        document.page_layout
    )
    with unittest.mock.patch(OPEN_DATABASE, return_value=empty_save_database) as open_database, \
            qtbot.wait_signal(document.action_applied), \
            qtbot.assert_not_emitted(loader.loading_file_failed):
        loader.run()
    open_database.assert_called_once()
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


@pytest.fixture(params=[
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
    ])
def legacy_save_file(request, tmp_path: Path):
    save = tmp_path/"save.mtxproxies"
    save_version, settings = request.param  # type: int, list
    db = mtg_proxy_printer.sqlite_helpers.open_database(save, f"document-v{save_version}", False)
    db.execute("BEGIN IMMEDIATE TRANSACTION")
    if save_version < 6:
        db.execute(f"INSERT INTO DocumentSettings VALUES ({', '.join('?'*len(settings))})", settings)
    elif save_version == 6:
        db.executemany("INSERT INTO DocumentSettings (key, value) VALUES (?, ?)", settings)
    else:
        pass
    db.commit()
    db.close()
    return save


def test_load_settings_from_legacy_save_file_is_successful(
        qtbot: QtBot, legacy_save_file: Path, loader: DocumentLoader):
    document = loader.document
    loader.save_path = legacy_save_file
    with qtbot.wait_signals([loader.load_requested, document.action_applied]), \
            qtbot.assert_not_emitted(loader.loading_file_failed):
        loader.run()
    annotations = document.page_layout.__annotations__
    assert_that(
        document.page_layout,
        has_properties({
            item: instance_of(value)
            for item, value in annotations.items()
        })
    )
    assert_that(document.page_layout, has_properties({
        "document_name": "", "draw_cut_markers": True, "draw_page_numbers": False, "draw_sharp_corners": False,
        "row_spacing": quantity_close_to(2*mm), "column_spacing": quantity_close_to(3*mm),
        "margin_top": quantity_close_to(4*mm), "margin_bottom": quantity_close_to(5*mm),
        "margin_left": quantity_close_to(6*mm), "margin_right": quantity_close_to(7*mm),
        "page_height": quantity_close_to(200*mm), "page_width": quantity_close_to(150*mm)
    }))


@pytest.mark.parametrize("title", ["str", "", "1", "0x1", "1.0.0", "1..0", "01", "1.0"])
def test_load_correctly_sets_document_title(
        qtbot: QtBot, page_layout: PageLayoutSettings,
        empty_save_database: sqlite3.Connection, loader: DocumentLoader, title: str):
    document = loader.document
    page_layout.document_name = title
    create_save_database_with(empty_save_database, [], [], page_layout)
    with unittest.mock.patch(OPEN_DATABASE, return_value=empty_save_database), \
            qtbot.wait_signals([loader.load_requested, document.action_applied]), \
            qtbot.assert_not_emitted(loader.loading_file_failed):
        loader.run()
    assert_that(document.page_layout, has_property("document_name", equal_to(title)))
