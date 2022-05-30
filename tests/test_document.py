# Copyright (C) 2021-2022 Thomas Hess <thomas.hess@udo.edu>

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

import dataclasses
import itertools
import pathlib
from tempfile import TemporaryDirectory
import textwrap
import time

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from hamcrest import *

try:
    from hamcrest import contains_exactly
except ImportError:
    # Compatibility with PyHamcrest < 1.10
    from hamcrest import contains as contains_exactly
import pytest
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.sqlite_helpers import open_database, create_in_memory_database
from mtg_proxy_printer.model.carddb import Card, MTGSet
from mtg_proxy_printer.model.document import Document, CardContainer
from mtg_proxy_printer.model.document_loader import DocumentLoader, PageLayoutSettings
from mtg_proxy_printer.model.imagedb import ImageKey


@pytest.fixture
def document_custom_layout(document: Document) -> Document:
    document.page_layout.page_height = 300
    document.page_layout.page_width = 200
    document.page_layout.margin_top = 20
    document.page_layout.margin_bottom = 19
    document.page_layout.margin_left = 18
    document.page_layout.margin_right = 17
    document.page_layout.image_spacing_horizontal = 3
    document.page_layout.image_spacing_vertical = 2
    document.page_layout.draw_cut_markers = True
    document.on_page_layout_updated()
    yield document


def test_document_reset_clears_modified_page_layout(qtbot: QtBot, document_custom_layout: Document):
    default_layout = PageLayoutSettings()
    default_layout.update_from_settings()
    assert_that(
        document_custom_layout.total_cards_per_page,
        is_not(equal_to(default_layout.compute_page_card_capacity())),
        "Test setup failed."
    )
    with qtbot.waitSignal(document_custom_layout.total_cards_per_page_changed, timeout=1000):
        document_custom_layout.clear_all_data()

    assert_that(document_custom_layout.page_layout, is_(equal_to(default_layout)))


def test_document_two_overflow_events_only_add_one_new_page(document: Document):
    card = document.card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    document.add_card(card, document.total_cards_per_page)
    assert_that(document.rowCount(), is_(equal_to(1)))
    for _ in range(document.total_cards_per_page):
        document.add_card(card, 1)
        assert_that(document.pages, has_length(2), "Unexpected page break occurred")


def test_clear_database_not_clearing_last_image_use_timestamps(document: Document):
    card = document.card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    # Add two copies. Should only count as one usage
    document.add_card(card, 2)
    document.store_image_usage()
    usages = document.card_db.db.execute(
        "SELECT scryfall_id, is_front, usage_count, CAST(strftime('%s', last_use_date) AS INT) "
        "FROM LastImageUseTimestamps").fetchall()
    end = int(time.time())
    assert_that(
        usages,
        contains_exactly(
            contains_exactly("0000579f-7b35-4ed3-b44c-db2a538066fe", True, 1, close_to(end, 1)))
    )


def test_document_is_created_empty(document: Document):
    assert_that(document.compute_page_card_capacity(), is_(greater_than_or_equal_to(1)))
    assert_that(document.total_cards_per_page, is_(equal_to(document.compute_page_card_capacity())))
    assert_that(document.rowCount(), is_(equal_to(1)), "Expected creation of a single, empty page.")
    assert_that(document.pages, has_length(1), "Expected creation of a single, empty page.")
    assert_that(document.rowCount(document.index(0, 0)), is_(equal_to(0)), "Expected empty page, but it is not empty")
    assert_that(document.pages[0], is_(empty()), "Expected empty page, but it is not empty")


@pytest.mark.parametrize("pages_to_fill", range(1, 5))
def test_add_card_and_row_count(document: Document, pages_to_fill: int):
    card = document.card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    document.add_card(card, pages_to_fill * document.total_cards_per_page)
    assert_that(
        document.pages,
        has_length(pages_to_fill),
        "Unexpected page count"
    )
    assert_that(document.rowCount(), is_(equal_to(pages_to_fill)))
    for page_row, page in enumerate(document.pages):
        assert_that(
            page,
            has_length(document.total_cards_per_page),
            "Unexpected number of cards in page."
        )
        assert_that(document.index(page_row, 0).isValid(), is_(True))
        assert_that(
            document.index(page_row, 0).internalPointer(),
            is_(page),
            "Root element internal pointer not referring the page data list."
        )
        assert_that(
            document.rowCount(document.index(page_row, 0)),
            is_(equal_to(document.total_cards_per_page)),
            f"rowCount() of parent index at row {page_row} wrong."
        )
        for card_index in range(document.total_cards_per_page):
            assert_that(
                document.index(card_index, 0, document.index(page_row, 0)).internalPointer(),
                all_of(
                    instance_of(CardContainer),
                    has_property("parent", is_(page)),
                    has_property(
                        "card", all_of(
                            instance_of(Card),
                            has_property("scryfall_id", equal_to("0000579f-7b35-4ed3-b44c-db2a538066fe")),
                        ),
                    ),
                ),
                "Parent relationship broken"
            )


def test_remove_pages_removes_middle_page(document: Document):
    pages_to_create = 10
    for _ in range(pages_to_create-1):  # Create one less, because the document has one page by default
        document.add_page()
    assert_that(document.rowCount(), is_(equal_to(pages_to_create)), "Unexpected page count before deletion.")
    assert_that(document.pages, has_length(pages_to_create), "Unexpected page count before deletion.")
    page_to_delete = document.pages[5]
    document.remove_pages([document.index(5, 0)])
    assert_that(document.rowCount(), is_(equal_to(pages_to_create - 1)), "Unexpected page count after deletion.")
    assert_that(document.pages, has_length(pages_to_create - 1), "Unexpected page count after deletion.")
    assert_that(
        calling(document.find_page_list_index).with_args(page_to_delete),
        raises(ValueError), "Wrong page deleted."
    )


@pytest.mark.timeout(0.5)
def test_compacting_document(document: Document):
    pages_to_fill = 5
    card = document.card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    document.add_card(card, pages_to_fill * document.total_cards_per_page)
    cards_to_remove = 6
    for page_index in range(1, 4):
        document.remove_cards(
            list(map(
                document.index,
                range(cards_to_remove), itertools.repeat(0), itertools.repeat(document.index(page_index, 0))
            ))
        )
        assert_that(document.pages[page_index], has_length(document.total_cards_per_page - cards_to_remove))
    for page_index in (0, 4):
        assert_that(document.pages[page_index], has_length(document.total_cards_per_page))
    document.compact_pages()
    assert_that(document.pages, has_length(3), "Unexpected page count after compacting")
    for index, page in enumerate(document.pages):
        assert_that(page, has_length(document.total_cards_per_page), "Unexpected card count found on a page")
        for card_container in page:
            assert_that(
                card_container.parent,
                same_instance(page),
                f"Parent relationship incorrect on page {index}"
            )


@pytest.mark.parametrize("source_version", [2, 3])
def test_save_migration(document: Document, source_version: int):
    """Tests migration of existing saves to the newest schema revision on save."""
    card = document.card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    document.add_card(card, document.total_cards_per_page)
    with TemporaryDirectory() as temp_dir:
        document.save_file_path = _create_save_file(pathlib.Path(temp_dir), source_version)
        document.save_to_disk()
        _validate_database_schema(document.save_file_path)
        _validate_saved_document_settings(document)


def test_create_save(document_custom_layout: Document):
    """Tests that saving a new document uses the newest database schema version"""
    assert_that(
        set(dataclasses.astuple(document_custom_layout.page_layout)),
        contains_inanyorder(*dataclasses.astuple(document_custom_layout.page_layout)),
        "Setup failed. Duplicate values in page layout settings"
    )
    card = document_custom_layout.card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    document_custom_layout.add_card(card, document_custom_layout.total_cards_per_page)
    with TemporaryDirectory() as temp_dir:
        save_dir = pathlib.Path(temp_dir)/"test.mtgproxies"
        document_custom_layout.save_as(save_dir)
        _validate_database_schema(save_dir)
        _validate_saved_document_settings(document_custom_layout)


def test_subsequent_save_updates_settings(qtbot: QtBot, document_custom_layout: Document):
    """Tests that saving a new document uses the newest database schema version"""
    assert_that(
        set(dataclasses.astuple(document_custom_layout.page_layout)),
        contains_inanyorder(*dataclasses.astuple(document_custom_layout.page_layout)),
        "Setup failed. Duplicate values in page layout settings"
    )
    card = document_custom_layout.card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    # Prevent network access when re-loading the document
    document_custom_layout.image_db.loaded_images[
        ImageKey(card.scryfall_id, card.is_front, card.highres_image)] = document_custom_layout.image_db.blank_image
    document_custom_layout.add_card(card, document_custom_layout.total_cards_per_page)
    with TemporaryDirectory() as temp_dir:
        save_dir = pathlib.Path(temp_dir)/"test.mtgproxies"
        document_custom_layout.save_as(save_dir)
        _validate_database_schema(save_dir)
        _validate_saved_document_settings(document_custom_layout)
        document_custom_layout.page_layout.page_height = 1000
        with qtbot.waitSignal(document_custom_layout.page_layout_changed):
            document_custom_layout.on_page_layout_updated()
        document_custom_layout.save_to_disk()
        with qtbot.waitSignal(document_custom_layout.loading_state_changed, check_params_cb=lambda value: not value):
            document_custom_layout.loader.load_document(save_dir)
        assert_that(document_custom_layout.page_layout.page_height, is_(equal_to(1000)))


def _create_save_file(temp_path: pathlib.Path, source_version: int):
    """Creates an empty document save file at the given path and using the given schema version."""
    save_file_path = temp_path/"test.mtgproxies"
    open_database(save_file_path, f"document-v{source_version}", DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION).close()
    return save_file_path


def _validate_database_schema(db_path: pathlib.Path):
    """
    Validates the database schema of the user-provided file against a known-good schema.

    :raises AssertionError: If the provided file contains an invalid schema
    :returns: Database schema version
    """
    target_schema_version = 4
    db_unsafe = open_database(
        db_path, f"document-v{target_schema_version}", DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION)
    if db_unsafe.execute("PRAGMA application_id").fetchone()[0] != 41325044:
        raise AssertionError("Not an MTGProxyPrinter save file!")
    user_schema_version = db_unsafe.execute("PRAGMA user_version").fetchone()[0]
    assert_that(user_schema_version, is_(equal_to(target_schema_version)))
    db_known_good = create_in_memory_database(
        f"document-v{target_schema_version}", DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION)
    tables_and_views_query = textwrap.dedent("""\
        SELECT   s.type, s.name,
                 p.cid AS column_id, p.name AS column_name, p.type AS column_type,
                 p."notnull" AS column_not_null_constraint_enabled, p.dflt_value AS column_default_value,
                 p.pk AS column_primary_key_component
          FROM   sqlite_schema AS s
          JOIN   pragma_table_info(s.name) AS p
         WHERE   s.type IN ('table', 'view')
           AND   s.name NOT LIKE 'sqlite_%'
        ORDER BY s.name, column_id
        ;""")
    indices_query = textwrap.dedent("""\
        -- Note: Also include the “sqlite_autoindex*” indices that are
        -- automatically created for UNIQUE and PRIMARY KEY constraints.
        SELECT   s.name AS index_name,
                 p.seqno AS index_column_sequence_number,
                 p.cid AS column_id,
                 p.name AS column_name
          FROM   sqlite_schema AS s
          JOIN   pragma_index_info(s.name) AS p
         WHERE   s.type = 'index'
        ORDER BY index_name ASC, index_column_sequence_number ASC
        ;""")
    with db_known_good:
        assert_that(
            db_unsafe.execute(tables_and_views_query).fetchall(),
            contains_exactly(*db_known_good.execute(tables_and_views_query).fetchall()),
            "Given save file inconsistent: Unexpected tables or views")
        assert_that(
            db_unsafe.execute(indices_query).fetchall(),
            contains_exactly(*db_known_good.execute(indices_query).fetchall()),
            "Given save file inconsistent: Unexpected indices")


def _validate_saved_document_settings(document: Document):
    with open_database(document.save_file_path, "document-v4", DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION) as save:
        assert_that(save.execute("SELECT COUNT(*) FROM DocumentSettings").fetchone(), contains_exactly(1))
        assert_that(save.execute(
            textwrap.dedent("""\
                SELECT page_height, page_width,
                       margin_top, margin_bottom, margin_left, margin_right,
                       image_spacing_horizontal, image_spacing_vertical, draw_cut_markers
                FROM DocumentSettings
                WHERE rowid == 1""")).fetchone(),
            contains_exactly(
                document.page_layout.page_height,
                document.page_layout.page_width,
                document.page_layout.margin_top,
                document.page_layout.margin_bottom,
                document.page_layout.margin_left,
                document.page_layout.margin_right,
                document.page_layout.image_spacing_horizontal,
                document.page_layout.image_spacing_vertical,
                document.page_layout.draw_cut_markers,
        ))


def test_get_missing_image_cards(qtbot: QtBot, document: Document):
    blank_image = document.image_db.blank_image
    expected = Card(
        "Placeholder Image", MTGSet("A", "a"), "1","en", "0", True, "1", "", True, False, 0,
        blank_image)
    unexpected = Card(
        "Other Image", MTGSet("A", "a"), "1","en", "0", True, "1", "", True, False, 0,
        QPixmap(blank_image)
    )
    document.add_card(expected, 2)
    document.add_card(unexpected, 2)
    assert_that(
        result := list(document.get_missing_image_cards()),
        has_length(2)
    )
    for item in result:
        card = item.parent().data(Qt.EditRole)[item.row()].card
        assert_that(card, is_(expected))


@pytest.mark.parametrize("result", [True, False])
def test_has_missing_images(qtbot: QtBot, document: Document, result: bool):
    blank_image = document.image_db.blank_image
    expected = Card(
        "Placeholder Image", MTGSet("A", "a"), "1","en", "0", True, "1", "", True, False, 0,
        blank_image)
    unexpected = Card(
        "Other Image", MTGSet("A", "a"), "1","en", "0", True, "1", "", True, False, 0,
        QPixmap(blank_image)
    )
    if result:
        document.add_card(expected, 2)
    document.add_card(unexpected, 2)
    assert_that(
        document.has_missing_images(),
        is_(result)
    )
