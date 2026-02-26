#  Copyright © 2020-2026  Thomas Hess <thomas.hess@udo.edu>
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

import unittest.mock
from typing import List

import pytest
from hamcrest import *
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.model.document_page import CardContainer, PageType
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.document_controller import IllegalStateError, DocumentAction
from mtg_proxy_printer.document_controller.card_actions import ActionRemoveCards, to_list_of_ranges

from .helpers import append_new_card_in_page, card_container_with, create_card


def test___init___raises_exception_with_epty_cards_to_remove_parameter():
    assert_that(calling(ActionRemoveCards).with_args([]), raises(ValueError))


@pytest.mark.parametrize("sequence, expected", [
    ([1], [(1, 1)]),
    ([0], [(0, 0)]),
    ([-10], [(-10, -10)]),
    ([1, -1, 0], [(-1, 1)]),
    ([1, 2], [(1, 2)]),
    ([2, 1], [(1, 2)]),
    ([1, 2, 3], [(1, 3)]),
    ([1, 3, 2], [(1, 3)]),
    ([3, 1, 2], [(1, 3)]),
    ([3, 2, 1], [(1, 3)]),
    ([1, 3], [(1, 1), (3, 3)]),
    ([3, 1], [(1, 1), (3, 3)]),
    ([1, 3, 4], [(1, 1), (3, 4)]),
])
def test_to_list_of_ranges(sequence, expected):
    assert_that(to_list_of_ranges(sequence), is_(equal_to(expected)))


@unittest.mock.patch("mtg_proxy_printer.document_controller.card_actions.to_list_of_ranges")
def test___init___converts_index_list_to_ranges_list(mock_to_list_of_ranges: unittest.mock.MagicMock):
    sequence = [0]
    action = ActionRemoveCards(sequence)
    mock_to_list_of_ranges.assert_called_once_with(sequence)
    assert_that(action.card_ranges_to_remove, is_(same_instance(mock_to_list_of_ranges.return_value)))


def test_apply_removes_two_1_card_ranges(qtbot: QtBot, document_light: Document):
    page = document_light.pages[0]
    removed_1 = append_new_card_in_page(page, "Removed 1")
    remaining = append_new_card_in_page(page, "Remaining")
    removed_2 = append_new_card_in_page(page, "Removed 2")
    action = ActionRemoveCards([0, 2])
    with qtbot.wait_signals([document_light.rowsAboutToBeRemoved, document_light.rowsRemoved], timeout=1000):
        assert_that(action.apply(document_light), is_(instance_of(DocumentAction)))
    assert_that(
        page,
        contains_exactly(
            card_container_with(remaining, page)
        )
    )
    assert_that(
        action.removed_cards,
        contains_exactly(
            contains_exactly(
                card_container_with(removed_1, page)
            ),
            contains_exactly(
                card_container_with(removed_2, page)
            ),
        )
    )


@pytest.mark.parametrize("row_selection", [[0, 1], [1, 0]])
def test_apply_removes_one_2_card_range(qtbot: QtBot, document_light: Document, row_selection: List[int]):
    page = document_light.pages[0]
    removed_1 = append_new_card_in_page(page, "Removed 1")
    removed_2 = append_new_card_in_page(page, "Removed 2")
    remaining = append_new_card_in_page(page, "Remaining")
    action = ActionRemoveCards(row_selection)
    with qtbot.wait_signals([document_light.rowsAboutToBeRemoved, document_light.rowsRemoved], timeout=1000):
        assert_that(action.apply(document_light), is_(instance_of(DocumentAction)))
    assert_that(
        page,
        contains_exactly(
            card_container_with(remaining, page)
        )
    )
    assert_that(
        action.removed_cards,
        contains_exactly(
            contains_exactly(
                card_container_with(removed_1, page),
                card_container_with(removed_2, page),
            ),
        )
    )


def test_apply_emits_page_type_changed_signal_if_changed(qtbot: QtBot, document_light: Document):
    """Removes the first card on the page. The second one (if present) determines the new page type."""
    page = document_light.currently_edited_page
    removed_1 = append_new_card_in_page(page, "Removed 1")
    removed_2 = append_new_card_in_page(page, "Removed 2")
    assert_that(
        page,
        contains_exactly(
            card_container_with(removed_1, page),
            card_container_with(removed_2, page),
        ), "Test setup failed"
    )
    assert_that(page.page_type(), is_(PageType.REGULAR), "Test setup failed")

    with qtbot.assert_not_emitted(document_light.page_type_changed):
        ActionRemoveCards([0]).apply(document_light)
    assert_that(page.page_type(), is_(PageType.REGULAR))
    with qtbot.wait_signal(document_light.page_type_changed, timeout=1000):
        ActionRemoveCards([0]).apply(document_light)
    assert_that(page.page_type(), is_(PageType.UNDETERMINED))


def test_undo_restores_two_1_card_ranges(qtbot: QtBot, document_light: Document):
    page = document_light.pages[0]
    remaining = append_new_card_in_page(page, "Remaining")
    action = ActionRemoveCards([0, 2], page_number=0)
    removed_1 = create_card("Removed 1")
    removed_2 = create_card("Removed 2")
    action.removed_cards.append([CardContainer(page, removed_1)])  # Range [0, 0]
    action.removed_cards.append([CardContainer(page, removed_2)])  # Range [2, 2]

    with qtbot.wait_signals([document_light.rowsAboutToBeInserted, document_light.rowsInserted], timeout=1000):
        assert_that(action.undo(document_light), is_(instance_of(DocumentAction)))
    assert_that(
        page,
        contains_exactly(
            card_container_with(removed_1, page),
            card_container_with(remaining, page),
            card_container_with(removed_2, page),
        )
    )
    assert_that(action.removed_cards, is_(empty()))


def test_undo_restores_one_2_card_range(qtbot: QtBot, document_light: Document):
    page = document_light.pages[0]
    remaining = append_new_card_in_page(page, "Remaining")
    removed_1 = create_card("Removed 1")
    removed_2 = create_card("Removed 2")
    action = ActionRemoveCards([0, 1], page_number=0)
    action.removed_cards.append(
        [CardContainer(page, removed_1), CardContainer(page, removed_2)]
    )
    with qtbot.wait_signals([document_light.rowsAboutToBeInserted, document_light.rowsInserted], timeout=1000):
        assert_that(action.undo(document_light), is_(instance_of(DocumentAction)))
    assert_that(
        page,
        contains_exactly(
            card_container_with(removed_1, page),
            card_container_with(removed_2, page),
            card_container_with(remaining, page),
        )
    )
    assert_that(action.removed_cards, is_(empty()))


def test_undo_without_page_index_raises_exception(document_light: Document):
    action = ActionRemoveCards([1])
    assert_that(calling(action.undo).with_args(document_light), raises(IllegalStateError))
