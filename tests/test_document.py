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

import copy
import dataclasses
import itertools
import pathlib
import typing
import unittest.mock
from tempfile import TemporaryDirectory
import textwrap
import time

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
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
from mtg_proxy_printer.model.document import Document, PageType
from mtg_proxy_printer.model.document_page import CardContainer
from mtg_proxy_printer.model.document_loader import DocumentLoader, PageLayoutSettings
from mtg_proxy_printer.model.imagedb import ImageKey

from mtg_proxy_printer.document_controller import DocumentAction
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard


class DummyAction(DocumentAction):
    """A dummy DocumentAction that does nothing. apply() and undo() are replaced with MagicMock instances."""
    apply: unittest.mock.MagicMock
    undo: unittest.mock.MagicMock

    def __init__(self, value: int = 0):
        super().__init__()
        self.value = value
        self.apply = unittest.mock.MagicMock(return_value=self)
        self.undo = unittest.mock.MagicMock(return_value=self)

    def __eq__(self, other):
        return isinstance(other, DummyAction) and other.value == self.value


@pytest.mark.parametrize("first, second, matcher", [
    (1, 1, is_),
    (0, 1, is_not),
])
def test_dummy_action_eq(first: int, second: int, matcher):
    a_1 = DummyAction(first)
    a_2 = DummyAction(second)
    assert_that(a_1, is_(equal_to(a_1)))
    assert_that(a_2, is_(equal_to(a_2)))
    assert_that(a_1, matcher(equal_to(a_2)))


def assert_unused(action: DummyAction):
    action.apply.assert_not_called()
    action.undo.assert_not_called()


def assert_applied(action: DummyAction, document: Document):
    action.apply.assert_called_once_with(document)
    action.undo.assert_not_called()


def assert_undone(action: DummyAction, document: Document):
    action.apply.assert_not_called()
    action.undo.assert_called_once_with(document)


def test_apply_on_empty_undo_stack_empty_redo_stack(qtbot: QtBot, document_light: Document):
    action = DummyAction()
    with qtbot.wait_signals([document_light.undo_available_changed, document_light.action_applied], timeout=100), \
            qtbot.assert_not_emitted(document_light.redo_available_changed), \
            qtbot.assert_not_emitted(document_light.action_undone):
        document_light.apply(action)

    assert_that(document_light.redo_stack, is_(empty()))
    assert_that(document_light.undo_stack, contains_exactly(action))

    assert_applied(action, document_light)


def test_apply_on_empty_undo_stack_filled_redo_stack(qtbot: QtBot, document_light: Document):
    document_light.redo_stack.append(redo_dummy := DummyAction(1))
    action = DummyAction(0)
    with qtbot.wait_signals([
                document_light.undo_available_changed,
                document_light.redo_available_changed,
                document_light.action_applied], timeout=100), \
            qtbot.assert_not_emitted(document_light.action_undone):
        document_light.apply(action)

    assert_that(document_light.redo_stack, is_(empty()))
    assert_that(document_light.undo_stack, contains_exactly(action))

    assert_unused(redo_dummy)
    assert_applied(action, document_light)


def test_apply_on_filled_undo_stack_empty_redo_stack(qtbot: QtBot, document_light: Document):
    document_light.undo_stack.append(previous_action := DummyAction())
    action = DummyAction()
    with qtbot.assert_not_emitted(document_light.undo_available_changed), \
            qtbot.assert_not_emitted(document_light.redo_available_changed), \
            qtbot.assert_not_emitted(document_light.action_undone), \
            qtbot.wait_signal(document_light.action_applied, timeout=100):
        document_light.apply(action)

    assert_that(document_light.redo_stack, is_(empty()))
    assert_that(document_light.undo_stack, contains_exactly(previous_action, action))

    assert_unused(previous_action)
    assert_applied(action, document_light)


def test_apply_on_filled_undo_stack_filled_redo_stack(qtbot: QtBot, document_light: Document):
    document_light.undo_stack.append(previous_action := DummyAction())
    document_light.redo_stack.append(redo_dummy := DummyAction(1))
    action = DummyAction(0)
    expected_signals = [document_light.redo_available_changed, document_light.action_applied]
    with qtbot.wait_signals(expected_signals, timeout=100), \
            qtbot.assert_not_emitted(document_light.undo_available_changed), \
            qtbot.assert_not_emitted(document_light.action_undone):
        document_light.apply(action)

    assert_that(document_light.redo_stack, is_(empty()))
    assert_that(document_light.undo_stack, contains_exactly(previous_action, action))

    assert_unused(redo_dummy)
    assert_unused(previous_action)
    assert_applied(action, document_light)


def test_apply_same_action_as_on_redo_stack_does_keep_remaining_redo_stack(qtbot: QtBot, document_light: Document):
    document_light.redo_stack.append(should_stay := DummyAction(2))
    document_light.redo_stack.append(DummyAction(1))
    action = DummyAction(1)
    expected_signals = [document_light.undo_available_changed, document_light.action_applied]
    with qtbot.wait_signals(expected_signals, timeout=100), \
            qtbot.assert_not_emitted(document_light.redo_available_changed), \
            qtbot.assert_not_emitted(document_light.action_undone):
        document_light.apply(action)
    assert_that(document_light.redo_stack, contains_exactly(should_stay))
    assert_that(document_light.undo_stack, contains_exactly(action))


def test_undo_on_empty_redo_stack_2_elements_on_undo_stack(qtbot: QtBot, document_light: Document):
    document_light.undo_stack.append(first := DummyAction())
    document_light.undo_stack.append(second := DummyAction())
    expected_signals = [document_light.redo_available_changed, document_light.action_undone,]
    with qtbot.wait_signals(expected_signals, timeout=100),\
            qtbot.assert_not_emitted(document_light.undo_available_changed), \
            qtbot.assert_not_emitted(document_light.action_applied):
        document_light.undo()

    assert_that(document_light.undo_stack, contains_exactly(first))
    assert_that(document_light.redo_stack, contains_exactly(second))

    assert_unused(first)
    assert_undone(second, document_light)


def test_undo_on_empty_redo_stack_1_element_on_undo_stack(qtbot: QtBot, document_light: Document):
    document_light.undo_stack.append(first := DummyAction())
    expected_signals = [
        document_light.redo_available_changed, document_light.undo_available_changed, document_light.action_undone,
    ]
    with qtbot.wait_signals(expected_signals, timeout=100), \
            qtbot.assert_not_emitted(document_light.action_applied):
        document_light.undo()

    assert_that(document_light.undo_stack, is_(empty()))
    assert_that(document_light.redo_stack, contains_exactly(first))

    assert_undone(first, document_light)


def test_undo_on_filled_redo_stack_1_element_on_undo_stack(qtbot: QtBot, document_light: Document):
    document_light.redo_stack.append(redo_dummy := DummyAction())
    document_light.undo_stack.append(first := DummyAction())
    expected_signals = [document_light.undo_available_changed, document_light.action_undone,]
    with qtbot.wait_signals(expected_signals, timeout=100), \
            qtbot.assert_not_emitted(document_light.redo_available_changed), \
            qtbot.assert_not_emitted(document_light.action_applied):
        document_light.undo()

    assert_that(document_light.undo_stack, is_(empty()))
    assert_that(document_light.redo_stack, contains_exactly(redo_dummy, first))

    assert_unused(redo_dummy)
    assert_undone(first, document_light)


def test_undo_on_filled_redo_stack_2_elements_on_undo_stack(qtbot: QtBot, document_light: Document):
    document_light.redo_stack.append(redo_dummy := DummyAction())
    document_light.undo_stack.append(first := DummyAction())
    document_light.undo_stack.append(second := DummyAction())

    with qtbot.assert_not_emitted(document_light.undo_available_changed), \
            qtbot.assert_not_emitted(document_light.redo_available_changed), \
            qtbot.assert_not_emitted(document_light.action_applied), \
            qtbot.wait_signal(document_light.action_undone, timeout=100):
        document_light.undo()

    assert_that(document_light.undo_stack, contains_exactly(first))
    assert_that(document_light.redo_stack, contains_exactly(redo_dummy, second))

    assert_unused(redo_dummy)
    assert_unused(first)
    assert_undone(second, document_light)


def test_redo_on_empty_undo_stack_1_element_on_redo_stack(qtbot: QtBot, document_light: Document):
    document_light.redo_stack.append(first := DummyAction())
    expected_signals = [
        document_light.undo_available_changed, document_light.redo_available_changed, document_light.action_applied
    ]
    with qtbot.wait_signals(
            expected_signals, timeout=100), \
            qtbot.assert_not_emitted(document_light.action_undone):
        document_light.redo()

    assert_that(document_light.redo_stack, is_(empty()))
    assert_that(document_light.undo_stack, contains_exactly(first))

    assert_applied(first, document_light)


def test_redo_on_empty_undo_stack_2_elements_on_redo_stack(qtbot: QtBot, document_light: Document):
    document_light.redo_stack.append(first := DummyAction())
    document_light.redo_stack.append(second := DummyAction())

    expected_signals = [document_light.undo_available_changed, document_light.action_applied]
    with qtbot.wait_signals(expected_signals, timeout=100), \
            qtbot.assert_not_emitted(document_light.redo_available_changed), \
            qtbot.assert_not_emitted(document_light.action_undone):
        document_light.redo()

    assert_that(document_light.redo_stack, contains_exactly(first))
    assert_that(document_light.undo_stack, contains_exactly(second))

    assert_unused(first)
    assert_applied(second, document_light)


def test_redo_on_filled_undo_stack_1_element_on_redo_stack(qtbot: QtBot, document_light: Document):
    document_light.redo_stack.append(first := DummyAction())
    document_light.undo_stack.append(undo_dummy := DummyAction())
    expected_signals = [document_light.redo_available_changed, document_light.action_applied]
    with qtbot.wait_signals(expected_signals, timeout=100),\
            qtbot.assert_not_emitted(document_light.undo_available_changed), \
            qtbot.assert_not_emitted(document_light.action_undone):
        document_light.redo()

    assert_that(document_light.undo_stack, contains_exactly(undo_dummy, first))
    assert_that(document_light.redo_stack, is_(empty()))

    assert_unused(undo_dummy)
    assert_applied(first, document_light)


def test_redo_on_filled_undo_stack_2_elements_on_redo_stack(qtbot: QtBot, document_light: Document):
    document_light.redo_stack.append(first := DummyAction())
    document_light.redo_stack.append(second := DummyAction())
    document_light.undo_stack.append(undo_dummy := DummyAction())

    with qtbot.assert_not_emitted(document_light.undo_available_changed), \
            qtbot.assert_not_emitted(document_light.redo_available_changed), \
            qtbot.assert_not_emitted(document_light.action_undone), \
            qtbot.wait_signal(document_light.action_applied, timeout=100):
        document_light.redo()

    assert_that(document_light.undo_stack, contains_exactly(undo_dummy, second))
    assert_that(document_light.redo_stack, contains_exactly(first))

    assert_unused(undo_dummy)
    assert_unused(first)
    assert_applied(second, document_light)


@pytest.mark.parametrize("additional_pages", range(3))
def test_rowCount_without_index_parameter_return_page_count(document_light, additional_pages: int):
    if additional_pages:
        document_light.apply(ActionNewPage(count=additional_pages))
    assert_that(document_light.pages, has_length(1+additional_pages), "Test setup failed")
    assert_that(document_light.rowCount(), is_(1+additional_pages), "Wrong rowCount() returned")


def test_rowCount_with_valid_index_returns_card_count_on_page_given_by_index(document_light):
    document_light.apply(ActionNewPage(count=3))
    for count in range(1, 4):
        document_light._set_currently_edited_page(document_light.pages[count])
        document_light.apply(
            ActionAddCard(Card("", MTGSet("", ""), "", "", "", True, "", "", True, False, 0, None), count=count)
        )
        assert_that(document_light.currently_edited_page, has_length(count), "Test setup failed")
    for page in range(4):
        assert_that(
            document_light.rowCount(document_light.index(page, 0)),
            is_(equal_to(page)),
            f"Wrong rowCount() returned for page {page}"
        )


@pytest.fixture
def document_custom_layout(document: Document) -> Document:
    custom_layout = PageLayoutSettings(300, 200, 20, 19, 18, 17, 3, 2, True)
    document.update_page_layout(custom_layout)
    yield document


def test_document_reset_clears_modified_page_layout(qtbot: QtBot, document_custom_layout: Document):
    default_layout = PageLayoutSettings.create_from_settings()
    assert_that(
        document_custom_layout,
        has_property("page_layout", not_(equal_to(default_layout)))
    )
    assert_that(
        document_custom_layout.page_layout.compute_page_row_count(),
        is_not(equal_to(default_layout.compute_page_card_capacity())),
        "Test setup failed."
    )
    with qtbot.waitSignal(document_custom_layout.page_layout_changed, timeout=1000):
        document_custom_layout.clear_all_data()

    assert_that(
        document_custom_layout,
        has_property("page_layout", equal_to(default_layout))
    )


def test_clear_database_not_clearing_last_image_use_timestamps(document: Document):
    card = document.card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    # Add two copies. Should only count as one usage
    document.apply(ActionAddCard(card, 2))
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
    capacity = document.page_layout.compute_page_card_capacity()
    assert_that(capacity, is_(greater_than_or_equal_to(1)))
    assert_that(document.total_cards_per_page, is_(equal_to(capacity)))
    assert_that(document.rowCount(), is_(equal_to(1)), "Expected creation of a single, empty page.")
    assert_that(document.pages, has_length(1), "Expected creation of a single, empty page.")
    assert_that(document.rowCount(document.index(0, 0)), is_(equal_to(0)), "Expected empty page, but it is not empty")
    assert_that(document.pages[0], is_(empty()), "Expected empty page, but it is not empty")
    assert_that(
        document.pages[0].page_type(), is_(PageType.UNDETERMINED), "Empty page should have an undetermined page type"
    )


@pytest.mark.parametrize("pages_to_fill", range(1, 5))
def test_add_card_and_row_count(document: Document, pages_to_fill: int):
    card = document.card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    document.apply(ActionAddCard(card, pages_to_fill * document.total_cards_per_page))
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
                document.index(page_row, 0).child(card_index, 0).internalPointer(),
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


@pytest.mark.timeout(0.5)
def test_compacting_document(document: Document):
    pages_to_fill = 5
    card = document.card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    document.apply(ActionAddCard(card, pages_to_fill * document.total_cards_per_page))
    cards_to_remove = 6
    for page_index in range(1, 4):
        document.remove_cards(
            list(map(document.index(page_index, 0).child, range(cards_to_remove), itertools.repeat(0)))
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


def test_compacting_document_with_regular_and_oversized_pages(document: Document):
    regular = document.card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    oversized = document.card_db.get_card_with_scryfall_id("650722b4-d72b-4745-a1a5-00a34836282b", True)
    document.apply(ActionNewPage(count=3))
    assert_that(document.rowCount(), is_(4))
    document.add_card_to_page(0, regular)
    document.add_card_to_page(1, oversized)
    document.add_card_to_page(2, regular)
    document.add_card_to_page(3, oversized)
    document.compact_pages()
    assert_that(document.rowCount(), is_(2))
    assert_that(
        [document.pages[0].page_type(), document.pages[1].page_type()],
        contains_inanyorder(PageType.REGULAR, PageType.OVERSIZED),
        "Unexpectedly created a mixed-sizes page or left an empty page"
    )


def test_page_types_correctly_returned(document: Document):
    regular = document.card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    oversized = document.card_db.get_card_with_scryfall_id("650722b4-d72b-4745-a1a5-00a34836282b", True)
    assert_that(regular, is_(not_none()), "Test setup failed")
    assert_that(oversized, is_(not_none()), "Test setup failed")
    document.apply(ActionNewPage(count=5))
    assert_that(document.rowCount(), is_(6))
    document.add_card_to_page(0, regular)
    document.add_card_to_page(1, oversized)
    document.add_card_to_page(2, regular)
    document.add_card_to_page(3, oversized)
    document.add_card_to_page(4, regular)
    document.add_card_to_page(4, oversized)
    assert_that(document.pages[0].page_type(), is_(PageType.REGULAR))
    assert_that(document.pages[1].page_type(), is_(PageType.OVERSIZED))
    assert_that(document.pages[2].page_type(), is_(PageType.REGULAR))
    assert_that(document.pages[3].page_type(), is_(PageType.OVERSIZED))
    assert_that(document.pages[4].page_type(), is_(PageType.MIXED))
    assert_that(document.pages[5].page_type(), is_(PageType.UNDETERMINED))


@pytest.mark.parametrize("source_version", [2, 3, 4])
def test_save_migration(document: Document, source_version: int):
    """Tests migration of existing saves to the newest schema revision on save."""
    card = document.card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    document.apply(ActionAddCard(card, document.total_cards_per_page))
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
    document_custom_layout.apply(ActionAddCard(card, document_custom_layout.total_cards_per_page))
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
    layout = copy.copy(document_custom_layout.page_layout)
    layout.page_height = 1000
    card = document_custom_layout.card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    # Prevent network access when re-loading the document
    document_custom_layout.image_db.loaded_images[
        ImageKey(card.scryfall_id, card.is_front, card.highres_image)] = document_custom_layout.image_db.blank_image
    document_custom_layout.apply(ActionAddCard(card, document_custom_layout.total_cards_per_page))
    with TemporaryDirectory() as temp_dir:
        save_dir = pathlib.Path(temp_dir)/"test.mtgproxies"
        document_custom_layout.save_as(save_dir)
        _validate_database_schema(save_dir)
        _validate_saved_document_settings(document_custom_layout)
        with qtbot.waitSignal(document_custom_layout.page_layout_changed):
            document_custom_layout.update_page_layout(layout)
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
    target_schema_version = 5
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
    document.apply(ActionAddCard(expected, 2))
    document.apply(ActionAddCard(unexpected, 2))
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
    blank_image_card = Card(
        "Placeholder Image", MTGSet("A", "a"), "1","en", "0", True, "1", "", True, False, 0,
        blank_image)
    other_card = Card(
        "Other Image", MTGSet("A", "a"), "1","en", "0", True, "1", "", True, False, 0,
        QPixmap(blank_image)
    )
    if result:
        document.apply(ActionAddCard(blank_image_card, 2))
    document.apply(ActionAddCard(other_card, 2))
    assert_that(
        document.has_missing_images(),
        is_(result)
    )


@pytest.mark.parametrize("pages_content, expected", [
    ([], 0),
    ([None, None], 1),
    (["0000579f-7b35-4ed3-b44c-db2a538066fe"], 0),
    (["0000579f-7b35-4ed3-b44c-db2a538066fe"]*2, 1),
    (["0000579f-7b35-4ed3-b44c-db2a538066fe", "650722b4-d72b-4745-a1a5-00a34836282b"], 0),
    (["0000579f-7b35-4ed3-b44c-db2a538066fe", "650722b4-d72b-4745-a1a5-00a34836282b"]*2, 2),
    (["0000579f-7b35-4ed3-b44c-db2a538066fe", "650722b4-d72b-4745-a1a5-00a34836282b", None]*2, 4),
])
def test_compute_pages_saved_by_compacting(
        document: Document, pages_content: typing.List[typing.Optional[str]], expected: int):
    for page_number, scryfall_id in enumerate(pages_content):
        if scryfall_id:
            card = document.card_db.get_card_with_scryfall_id(scryfall_id, True)
            document.add_card_to_page(page_number, card)
        document.apply(ActionNewPage())
    # Each iteration above keeps a trailing empty page. Remove that here.
    document.remove_pages([document.index(document.rowCount()-1, 0)]*2)
    assert_that(
        document.compute_pages_saved_by_compacting(),
        is_(equal_to(expected))
    )


@pytest.mark.parametrize("scryfall_ids, expected_page_type", [
    (["0000579f-7b35-4ed3-b44c-db2a538066fe"], PageType.UNDETERMINED),
    (["650722b4-d72b-4745-a1a5-00a34836282b"], PageType.UNDETERMINED),
    (["0000579f-7b35-4ed3-b44c-db2a538066fe", "650722b4-d72b-4745-a1a5-00a34836282b"], PageType.OVERSIZED),
    (["650722b4-d72b-4745-a1a5-00a34836282b", "0000579f-7b35-4ed3-b44c-db2a538066fe"], PageType.REGULAR),
])
def test_remove_cards_emits_page_type_changed_signal(
        qtbot: QtBot, document: Document, scryfall_ids: typing.List[str], expected_page_type: PageType):
    """Removes the first card on the page. The second one (if present) determines the new page type."""
    cards = [document.card_db.get_card_with_scryfall_id(scryfall_id, True) for scryfall_id in scryfall_ids]
    for card in cards:
        document.add_card_to_page(0, card)
    page_index = document.index(0, 0)
    with qtbot.waitSignal(document.page_type_changed):
        document.remove_cards([document.index(0, 0, page_index)]*2)
    assert_that(document.pages[0].page_type(), is_(expected_page_type))


@pytest.mark.parametrize("scryfall_ids, expected_page_type", [
    (["0000579f-7b35-4ed3-b44c-db2a538066fe"], PageType.REGULAR),
    (["650722b4-d72b-4745-a1a5-00a34836282b"], PageType.OVERSIZED),
    (["0000579f-7b35-4ed3-b44c-db2a538066fe", "650722b4-d72b-4745-a1a5-00a34836282b"], PageType.MIXED),
    (["650722b4-d72b-4745-a1a5-00a34836282b", "0000579f-7b35-4ed3-b44c-db2a538066fe"], PageType.MIXED),
])
def test_remove_cards_only_emits_page_type_changed_signal_if_changed(
        qtbot: QtBot, document: Document, scryfall_ids: typing.List[str], expected_page_type: PageType):
    """
    The first card is added two times and then the first card is removed. The parameters state what is left in the page
    when remove_cards is called. In all of these situations, the page type does not change, thus the signal should not
    be emitted.
    """
    cards = [document.card_db.get_card_with_scryfall_id(scryfall_id, True) for scryfall_id in scryfall_ids]
    document.add_card_to_page(0, cards[0])
    for card in cards:
        document.add_card_to_page(0, card)
    page_index = document.index(0, 0)
    with qtbot.assertNotEmitted(document.page_type_changed):
        document.remove_cards([document.index(0, 0, page_index)]*2)
    assert_that(document.pages[0].page_type(), is_(expected_page_type))


def test_update_page_layout_copies_the_passed_in_instance(document: Document):
    layout = copy.copy(document.page_layout)
    layout.image_spacing_horizontal = 1
    document.update_page_layout(layout)
    layout.image_spacing_horizontal = 2
    assert_that(document.page_layout, has_property("image_spacing_horizontal", equal_to(1)))


@pytest.mark.parametrize("initial_h_spacing, new_h_spacing", [
    (0, 10),  # Regular cards overflow, oversized do not
    (10, 25),  # Oversized cards overflow, regular do not
    (0, 30),  # Both sizes overflow

])
def test_creating_potential_overflow_calls_method_move_excess_cards_to_free_pages(
        qtbot: QtBot, document: Document, initial_h_spacing: int, new_h_spacing: int):
    """
    Tests if increasing the horizontal spacing from a given value to another calls the logic to move excess cards
    to new pages.
    Regular and oversized cards overflow at different thresholds, so perform multiple tests to see that each
    card type can individually trigger this
    """
    layout = copy.copy(document.page_layout)
    layout.image_spacing_horizontal = initial_h_spacing
    document.update_page_layout(layout)
    initial_capacities = document.page_layout.compute_page_card_capacity(PageType.REGULAR),\
                         document.page_layout.compute_page_card_capacity(PageType.OVERSIZED)
    for scryfall_id in ["0000579f-7b35-4ed3-b44c-db2a538066fe", "650722b4-d72b-4745-a1a5-00a34836282b"]:
        card = document.card_db.get_card_with_scryfall_id(scryfall_id, True)
        document.apply(ActionAddCard(card, document.page_layout.compute_page_card_capacity(card.requested_page_type())))
    with unittest.mock.patch.object(Document, "move_excess_cards_to_free_pages") as expected_call_mock, \
            qtbot.waitSignal(document.page_layout_changed, timeout=1000):
        layout.image_spacing_horizontal = new_h_spacing
        document.update_page_layout(layout)
        expected_call_mock.assert_called_once()
    assert_that(
        (document.page_layout.compute_page_card_capacity(PageType.REGULAR),
         document.page_layout.compute_page_card_capacity(PageType.OVERSIZED)),
        less_than(initial_capacities)
    )


@pytest.mark.parametrize("initial_h_spacing, new_h_spacing", [
    (0, 10),  # Regular cards overflow, oversized do not
    (10, 25),  # Oversized cards overflow, regular do not
    (0, 30),  # Both sizes overflow

])
def test_method_move_excess_cards_to_free_pages_does_not_create_mixed_size_pages(
        document: Document, initial_h_spacing: int, new_h_spacing: int):
    """
    Tests move_excess_cards_to_free_pages() does not create pages with mixed-size cards.
    Regular and oversized cards overflow at different thresholds, so perform multiple tests to see that each
    combination works
    """
    layout = copy.copy(document.page_layout)
    layout.image_spacing_horizontal = initial_h_spacing
    document.update_page_layout(layout)
    initial_capacities = document.page_layout.compute_page_card_capacity(PageType.REGULAR),\
                         document.page_layout.compute_page_card_capacity(PageType.OVERSIZED)
    for scryfall_id in ["0000579f-7b35-4ed3-b44c-db2a538066fe", "650722b4-d72b-4745-a1a5-00a34836282b"]:
        card = document.card_db.get_card_with_scryfall_id(scryfall_id, True)
        capacity = document.page_layout.compute_page_card_capacity(card.requested_page_type())
        document.apply(ActionAddCard(card, capacity-1))

    layout.image_spacing_horizontal = new_h_spacing
    document.update_page_layout(layout)

    assert_that(
        (document.page_layout.compute_page_card_capacity(PageType.REGULAR),
         document.page_layout.compute_page_card_capacity(PageType.OVERSIZED)),
        less_than(initial_capacities)
    )
    assert_that(
        document.rowCount(),
        is_(greater_than(2))
    )
    for page in document.pages:
        assert_that(page.page_type(), is_in([PageType.REGULAR, PageType.OVERSIZED]))


@pytest.mark.parametrize("page_type, v_spacing, h_spacing, expected", [
    (PageType.REGULAR, 0, 0, 9),
    (PageType.REGULAR, 10, 0, 6),
    (PageType.REGULAR, 0, 10, 6),
    (PageType.OVERSIZED, 0, 0, 4),
    (PageType.OVERSIZED, 0, 10, 4),
    (PageType.OVERSIZED, 0, 25, 2),
])
def test_page_layout_compute_page_card_capacity(page_type:PageType, v_spacing: int, h_spacing: int, expected: int):
    layout = PageLayoutSettings.create_from_settings()
    layout.image_spacing_horizontal = h_spacing
    layout.image_spacing_vertical = v_spacing
    assert_that(layout.compute_page_card_capacity(page_type), is_(expected))


def test_replacing_regular_with_oversized_on_otherwise_filled_card_moves_oversized_away(document: Document):
    regular = document.card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    oversized = document.card_db.get_card_with_scryfall_id("650722b4-d72b-4745-a1a5-00a34836282b", True)
    document.apply(ActionAddCard(regular, 2))
    page_index = document.index(0, 0)
    document._on_replacement_image_received(oversized, document.index(0, 0, page_index))
    assert_that(document.rowCount(), is_(2))
    assert_that(document.rowCount(page_index), is_(1))
    assert_that(document.rowCount(document.index(1, 0)), is_(1))
    assert_that(document.pages[0][0].card, is_(equal_to(regular)))
    assert_that(document.pages[1][0].card, is_(equal_to(oversized)))
    assert_that(document.pages[0].page_type(), is_(PageType.REGULAR))
    assert_that(document.pages[1].page_type(), is_(PageType.OVERSIZED))


def test_replacing_regular_with_oversized_on_otherwise_empty_page_keeps_card_on_same_page(document: Document):
    regular = document.card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    oversized = document.card_db.get_card_with_scryfall_id("650722b4-d72b-4745-a1a5-00a34836282b", True)
    document.apply(ActionAddCard(regular, 1))
    page_index = document.index(0, 0)
    document._on_replacement_image_received(oversized, document.index(0, 0, page_index))
    assert_that(document.rowCount(), is_(1))
    assert_that(document.rowCount(page_index), is_(1))
    assert_that(document.pages[0][0].card, is_(equal_to(oversized)))
    assert_that(document.pages[0].page_type(), is_(PageType.OVERSIZED))
