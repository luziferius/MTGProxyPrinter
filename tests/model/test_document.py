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

import copy
import typing
import unittest.mock

from pint import Unit
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from hamcrest import *

from hamcrest import contains_exactly
import pytest
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.units_and_sizes import PageType, unit_registry, Unit, CardSizes, CardSize
from mtg_proxy_printer.model.card import MTGSet, Card
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.document_page import PageColumns
from mtg_proxy_printer.model.page_layout import PageLayoutSettings

from mtg_proxy_printer.document_controller import DocumentAction
from mtg_proxy_printer.document_controller.new_document import ActionNewDocument
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard
from mtg_proxy_printer.document_controller.edit_document_settings import ActionEditDocumentSettings

from tests.document_controller.helpers import append_new_card_in_page
from ..document_controller.helpers import insert_card_in_page, create_card

ItemDataRole = Qt.ItemDataRole
mm: Unit = unit_registry.mm
REGULAR = CardSizes.REGULAR
OVERSIZED = CardSizes.OVERSIZED


class DummyAction(DocumentAction):
    """A dummy DocumentAction that does nothing. apply() and undo() are replaced with MagicMock instances."""
    apply: unittest.mock.MagicMock
    undo: unittest.mock.MagicMock
    COMPARISON_ATTRIBUTES = ["value"]

    def __init__(self, value: int = 0):
        super().__init__()
        self.value = value
        self.apply = unittest.mock.MagicMock(return_value=self)
        self.undo = unittest.mock.MagicMock(return_value=self)

    @property
    def as_str(self):
        return f"Value: {self.value}"


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
    with qtbot.wait_signals([document_light.undo_available_changed, document_light.action_applied], timeout=1000), \
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
                document_light.action_applied], timeout=1000), \
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
            qtbot.wait_signal(document_light.action_applied, timeout=1000):
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
    with qtbot.wait_signals(expected_signals, timeout=1000), \
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
    with qtbot.wait_signals(expected_signals, timeout=1000), \
            qtbot.assert_not_emitted(document_light.redo_available_changed), \
            qtbot.assert_not_emitted(document_light.action_undone):
        document_light.apply(action)
    assert_that(document_light.redo_stack, contains_exactly(should_stay))
    assert_that(document_light.undo_stack, contains_exactly(action))


def test_undo_on_empty_redo_stack_2_elements_on_undo_stack(qtbot: QtBot, document_light: Document):
    document_light.undo_stack.append(first := DummyAction())
    document_light.undo_stack.append(second := DummyAction())
    expected_signals = [document_light.redo_available_changed, document_light.action_undone,]
    with qtbot.wait_signals(expected_signals, timeout=1000), \
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
    with qtbot.wait_signals(expected_signals, timeout=1000), \
            qtbot.assert_not_emitted(document_light.action_applied):
        document_light.undo()

    assert_that(document_light.undo_stack, is_(empty()))
    assert_that(document_light.redo_stack, contains_exactly(first))

    assert_undone(first, document_light)


def test_undo_on_filled_redo_stack_1_element_on_undo_stack(qtbot: QtBot, document_light: Document):
    document_light.redo_stack.append(redo_dummy := DummyAction())
    document_light.undo_stack.append(first := DummyAction())
    expected_signals = [document_light.undo_available_changed, document_light.action_undone,]
    with qtbot.wait_signals(expected_signals, timeout=1000), \
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
            qtbot.wait_signal(document_light.action_undone, timeout=1000):
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
            expected_signals, timeout=1000), \
            qtbot.assert_not_emitted(document_light.action_undone):
        document_light.redo()

    assert_that(document_light.redo_stack, is_(empty()))
    assert_that(document_light.undo_stack, contains_exactly(first))

    assert_applied(first, document_light)


def test_redo_on_empty_undo_stack_2_elements_on_redo_stack(qtbot: QtBot, document_light: Document):
    document_light.redo_stack.append(first := DummyAction())
    document_light.redo_stack.append(second := DummyAction())

    expected_signals = [document_light.undo_available_changed, document_light.action_applied]
    with qtbot.wait_signals(expected_signals, timeout=1000), \
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
    with qtbot.wait_signals(expected_signals, timeout=1000), \
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
            qtbot.wait_signal(document_light.action_applied, timeout=1000):
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
        document_light.set_currently_edited_page(document_light.pages[count])
        card = Card("", MTGSet("", ""), "", "", "", True, "", "", True, REGULAR, 0, None)
        document_light.apply(ActionAddCard(card, count=count))
        assert_that(document_light.currently_edited_page, has_length(count), "Test setup failed")
    for page in range(4):
        assert_that(
            document_light.rowCount(document_light.index(page, 0)),
            is_(equal_to(page)),
            f"Wrong rowCount() returned for page {page}"
        )


@pytest.mark.parametrize("page_type, parent_row, child_rows", [
    (PageType.REGULAR, 0, [0]),
    (PageType.OVERSIZED, 2, [0, 1]),
])
def test_get_card_indices_of_type(document_light, page_type: PageType, parent_row: int, child_rows: list[int]):
    ActionNewPage(count=2).apply(document_light)
    append_new_card_in_page(document_light.pages[0], "Normal", REGULAR)
    append_new_card_in_page(document_light.pages[2], "Oversized", OVERSIZED)
    append_new_card_in_page(document_light.pages[2], "Oversized", OVERSIZED)
    indices = list(document_light.get_card_indices_of_type(page_type))
    assert_that(indices, has_length(len(child_rows)))
    for index, expected_row in zip(indices, child_rows):
        assert_that(index.row(), is_(expected_row))
        assert_that(index.parent().row(), is_(parent_row))
        card: Card = index.data(ItemDataRole.UserRole)
        assert_that(card.requested_page_type(), is_(page_type))


@pytest.fixture
def document_custom_layout(document: Document) -> Document:
    custom_layout = PageLayoutSettings(
        custom_page_height=300 * mm, custom_page_width=200 * mm,
        margin_top=20*mm, margin_bottom=19*mm, margin_left=18*mm, margin_right=17*mm,
        row_spacing=3*mm, column_spacing=2*mm, card_bleed=1*mm,
        draw_cut_markers=True,
        paper_size="Custom", paper_orientation="Portrait",
    )
    document.apply(ActionEditDocumentSettings(custom_layout))
    return document


def test_document_reset_clears_modified_page_layout(qtbot: QtBot, page_layout: PageLayoutSettings, document_custom_layout: Document):
    assert_that(
        document_custom_layout,
        has_property("page_layout", not_(equal_to(page_layout)))
    )
    assert_that(
        document_custom_layout.page_layout.compute_page_row_count(),
        is_not(equal_to(page_layout.compute_page_card_capacity())),
        "Test setup failed."
    )
    with qtbot.waitSignal(document_custom_layout.page_layout_changed, timeout=1000):
        document_custom_layout.apply(ActionNewDocument())

    assert_that(
        document_custom_layout,
        has_property("page_layout", equal_to(page_layout))
    )


def test_document_is_created_empty(document_light: Document):
    capacity = document_light.page_layout.compute_page_card_capacity()
    assert_that(capacity, is_(greater_than_or_equal_to(1)))
    assert_that(document_light.rowCount(), is_(equal_to(1)), "Expected creation of a single, empty page.")
    assert_that(
        document_light.pages,
        contains_exactly(empty()),
        "Expected creation of a single, empty page."
    )
    assert_that(
        document_light.rowCount(document_light.index(0, 0)), is_(equal_to(0)),
        "Expected empty page, but it is not empty")
    assert_that(
        document_light.pages[0].page_type(), is_(PageType.UNDETERMINED),
        "Empty page should have an undetermined page type"
    )


@pytest.mark.parametrize("size", [REGULAR, OVERSIZED])
def test_get_missing_image_cards(document_light: Document, size: CardSize):
    blank_image = document_light.image_db.get_blank(size)
    expected = create_card("Placeholder Image", size, "https://someurl", blank_image)
    # Create a new, distinct image by copying the blank image
    unexpected = create_card("Other Image", size, "", QPixmap(blank_image))
    document_light.apply(ActionAddCard(expected, 2))
    document_light.apply(ActionAddCard(unexpected, 2))
    assert_that(
        result := list(document_light.get_missing_image_cards()),
        has_length(2)
    )
    cards = [i.data(ItemDataRole.UserRole) for i in result]
    assert_that(cards, only_contains(expected))


@pytest.mark.parametrize("size", [REGULAR, OVERSIZED])
@pytest.mark.parametrize("result", [True, False])
def test_has_missing_images(document_light: Document, result: bool, size: CardSize):
    blank_image = document_light.image_db.get_blank(CardSizes.REGULAR)
    blank_image_card = create_card("Placeholder Image", size, "https://someurl", blank_image)
    # Create a new, distinct image by copying the blank image
    other_card = create_card("Other Image", size, "", QPixmap(blank_image))
    if result:
        document_light.apply(ActionAddCard(blank_image_card, 2))
    document_light.apply(ActionAddCard(other_card, 2))
    assert_that(
        document_light.has_missing_images(),
        is_(result)
    )


@pytest.mark.parametrize("pages_content, expected", [
    ([], 0),
    ([None, None], 1),
    ([create_card("Regular", REGULAR)], 0),
    ([create_card("Regular", REGULAR)]*2, 1),
    ([create_card("Regular", REGULAR), create_card("Oversized", OVERSIZED)], 0),
    ([create_card("Regular", REGULAR), create_card("Oversized", OVERSIZED)]*2, 2),
    ([create_card("Regular", REGULAR), create_card("Oversized", OVERSIZED), None]*2, 4),
])
def test_compute_pages_saved_by_compacting(
        document_light: Document, pages_content: list[Card | None], expected: int):
    if len(pages_content) > 1:
        document_light.apply(ActionNewPage(count=len(pages_content)-1))
    for page, card in zip(document_light.pages, pages_content):
        if card is not None:
            insert_card_in_page(page, card)
    assert_that(
        document_light.compute_pages_saved_by_compacting(),
        is_(equal_to(expected))
    )


def test_update_page_layout_copies_the_passed_in_instance(document_light: Document):
    layout = copy.copy(document_light.page_layout)
    layout.row_spacing = 1*mm
    document_light.apply(ActionEditDocumentSettings(layout))
    layout.row_spacing = 2*mm
    assert_that(document_light.page_layout, has_property("row_spacing", equal_to(1*mm)))


@pytest.mark.parametrize("invalid_page_row", [2])
def test_document__data_page_logs_error_on_invalid_index(document_light, invalid_page_row: int):
    index = document_light.createIndex(invalid_page_row, 0, None)
    with unittest.mock.patch("mtg_proxy_printer.model.document.logger.error") as logger_mock:
        assert_that(document_light._data_page(index), is_(None))
        logger_mock.assert_called_once()


@pytest.mark.parametrize("invalid_card_row", [2])
def test_document__data_card_logs_error_on_invalid_index_row(document_light, invalid_card_row: int):
    append_new_card_in_page(document_light.pages[0], "Card")
    index = document_light.createIndex(invalid_card_row, 0, document_light.pages[0][0])
    with unittest.mock.patch("mtg_proxy_printer.model.document.logger.error") as logger_mock:
        assert_that(document_light._data_card(index), is_(None))
        logger_mock.assert_called_once()


@pytest.mark.parametrize("invalid_card_column", [len(PageColumns)])
def test_document__data_card_logs_error_on_invalid_index_column(document_light, invalid_card_column: int):
    append_new_card_in_page(document_light.pages[0], "Card")
    index = document_light.createIndex(0, invalid_card_column, document_light.pages[0][0])
    with unittest.mock.patch("mtg_proxy_printer.model.document.logger.error") as logger_mock:
        assert_that(document_light._data_card(index), is_(None))
        logger_mock.assert_called_once()
