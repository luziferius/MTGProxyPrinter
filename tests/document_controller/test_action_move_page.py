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
from functools import partial

from PySide6.QtCore import Qt, QModelIndex

import pytest
from hamcrest import *
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.document_controller import IllegalStateError
from mtg_proxy_printer.document_controller.move_page import ActionMovePage
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.document_page import PageColumns

from tests.document_controller.helpers import append_new_card_in_page


@pytest.fixture()
def document_with_pages(document: Document) -> Document:
    ActionNewPage(count=3).apply(document)
    for number in range(document.rowCount()):
        append_new_card_in_page(document.pages[number], f"{number}")
    return document


def _card_name_on_page(document: Document, page: int) -> str:
    page_index = document.index(page, 0)
    card_index = document.index(0, PageColumns.CardName, page_index)
    return document.data(card_index, Qt.ItemDataRole.EditRole)


def validate_qt_model_move_signal_parameter(
        expected_source_row: int,
        expected_target_row: int,

        source_index: QModelIndex, row_start: int, row_end: int,
        target_index: QModelIndex, target_row: int) -> bool:

    models_match = source_index.model() is target_index.model()
    both_parents_must_be_invalid = not source_index.isValid() and not target_index.isValid()
    source_rows_match = row_start == row_end == expected_source_row
    target_row_matches = target_row == expected_target_row
    rows_valid = 0 <= row_start <= row_end and 0 <= target_row

    return models_match \
        and both_parents_must_be_invalid \
        and source_rows_match \
        and target_row_matches \
        and rows_valid


@pytest.mark.parametrize("source_page, target_page, expected_order", [
    (0, 0, "0123"),
    (0, 1, "0123"),
    (0, 2, "1023"),
    (0, 3, "1203"),
    (0, 4, "1230"),

    (1, 0, "1023"),
    (1, 1, "0123"),
    (1, 2, "0123"),
    (1, 3, "0213"),
    (1, 4, "0231"),

    (2, 0, "2013"),
    (2, 1, "0213"),
    (2, 2, "0123"),
    (2, 3, "0123"),
    (2, 4, "0132"),

    (3, 0, "3012"),
    (3, 1, "0312"),
    (3, 2, "0132"),
    (3, 3, "0123"),
    (3, 4, "0123"),
])
def test_apply(qtbot: QtBot, document_with_pages: Document, source_page: int, target_page: int, expected_order: str):
    action = ActionMovePage(source_page, target_page)
    move_signal_validator = partial(validate_qt_model_move_signal_parameter, source_page, target_page)
    if source_page == target_page or source_page == target_page - 1:
        with qtbot.assert_not_emitted(document_with_pages.rowsAboutToBeMoved), qtbot.assert_not_emitted(document_with_pages.rowsMoved):
            assert_that(action.apply(document_with_pages), is_(same_instance(action)))
    else:
        with (qtbot.wait_signal(
                (document_with_pages.rowsAboutToBeMoved, "rowsAboutToBeMoved"), timeout=10,
                check_params_cb=move_signal_validator),
              qtbot.wait_signal(
                  (document_with_pages.rowsMoved, "rowsMoved"), timeout=10)):
            assert_that(action.apply(document_with_pages), is_(same_instance(action)))
    assert_that(document_with_pages.rowCount(), is_(4))
    pages_after_move = "".join(
        _card_name_on_page(document_with_pages, page) for page in range(document_with_pages.rowCount()))
    assert_that(pages_after_move, is_(equal_to(expected_order)))
    for page, expected_on_page in enumerate(expected_order):
        assert_that(_card_name_on_page(document_with_pages, page), is_(equal_to(expected_on_page)))

@pytest.mark.parametrize("source_page, target_page", [
    (-1, -1),
    (-1, 0),
    (0, -1),
    (4, -1),
    (4, 0),
    (-1, 5),
    (0, 5),
])
def test_apply_outside_range_raises_exception(document_with_pages: Document, source_page: int, target_page: int):
    action = ActionMovePage(source_page, target_page)
    assert_that(calling(action.apply).with_args(document_with_pages), raises(IllegalStateError))


@pytest.mark.parametrize("target_page, source_page, expected_order", [  # source and target intentionally swapped
    (0, 0, "0123"),
    (0, 1, "0123"),
    (0, 2, "1023"),
    (0, 3, "1203"),
    (0, 4, "1230"),

    (1, 0, "1023"),
    (1, 1, "0123"),
    (1, 2, "0123"),
    (1, 3, "0213"),
    (1, 4, "0231"),

    (2, 0, "2013"),
    (2, 1, "0213"),
    (2, 2, "0123"),
    (2, 3, "0123"),
    (2, 4, "0132"),

    (3, 0, "3012"),
    (3, 1, "0312"),
    (3, 2, "0132"),
    (3, 3, "0123"),
    (3, 4, "0123"),
])
def test_undo(document_with_pages: Document, source_page: int, target_page: int, expected_order: list):
    pytest.skip()
    action = ActionMovePage(source_page, target_page)
    assert_that(action.undo(document_with_pages), is_(same_instance(action)))
    assert_that(document_with_pages.rowCount(), is_(4))
    for page, expected_on_page in enumerate(expected_order):
        assert_that(_card_name_on_page(document_with_pages, page), is_(equal_to(expected_on_page)))

@pytest.mark.parametrize("source_page, target_page", [
    (-1, -1),
    (-1, 0),
    (0, -1),
    (4, -1),
    (4, 0),
    (-1, 5),
    (0, 5),
])
def test_undo_outside_range_raises_exception(document_with_pages: Document, source_page: int, target_page: int):
    action = ActionMovePage(source_page, target_page)
    assert_that(calling(action.undo).with_args(document_with_pages), raises(IllegalStateError))
