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
from typing import Optional, Sequence

import pytest
from hamcrest import *
from PySide6.QtCore import QModelIndex
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.units_and_sizes import CardSizes, IntList
from mtg_proxy_printer.model.document_page import PageType
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.document_controller import IllegalStateError
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage
from mtg_proxy_printer.document_controller.move_cards import ActionMoveCardsBetweenPages, ActionMoveCardsWithinPage

from .helpers import card_container_with, append_new_card_in_page, card_container_with_name
OptInt = Optional[int]


def validate_qt_model_move_signal_parameter(
        expected_source: int, expected_row_start: int, expected_row_end: int,
        expected_target: int, expected_target_row: int,

        source_index: QModelIndex, row_start: int, row_end: int,
        target_index: QModelIndex, target_row: int) -> bool:

    source_index_valid = source_index.isValid() \
        and source_index.row() == expected_source \
        and source_index.column() == 0 \
        and not source_index.parent().isValid()
    target_index_valid = target_index.isValid() \
        and target_index.row() == expected_target \
        and target_index.column() == 0 \
        and not target_index.parent().isValid()
    rows_match = expected_row_start == row_start \
        and expected_row_end == row_end \
        and expected_target_row == target_row
    models_match = source_index.model() is target_index.model()
    rows_valid = 0 <= row_start <= row_end and 0 <= target_row
    return source_index_valid \
        and target_index_valid \
        and rows_match \
        and models_match \
        and rows_valid


def test_apply_raises_exception_when_trying_to_create_a_mixed_size_page(document_light: Document):
    ActionNewPage().apply(document_light)
    append_new_card_in_page(document_light.pages[0], "Normal", CardSizes.REGULAR)
    append_new_card_in_page(document_light.pages[1], "Large", CardSizes.OVERSIZED)
    assert_that(document_light.pages[0].page_type(), is_(PageType.REGULAR))
    assert_that(document_light.pages[1].page_type(), is_(PageType.OVERSIZED))
    assert_that(calling(ActionMoveCardsBetweenPages(0, [0], 1).apply).with_args(document_light), raises(IllegalStateError))


def test_apply_move_all_cards_onto_empty_page(qtbot: QtBot, document_light: Document):
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    to_move = append_new_card_in_page(pages[0], "Normal")
    row_move_validator = partial(validate_qt_model_move_signal_parameter, 0, 0, 0, 1, 0)
    with qtbot.wait_signals(
            [document_light.page_type_changed] * 2 + [document_light.rowsAboutToBeMoved, document_light.rowsMoved],
            timeout=1000, check_params_cbs=[lambda index: index.row() == 0, lambda index: index.row() == 1] +
                                           [row_move_validator] * 2):
        ActionMoveCardsBetweenPages(0, [0], 1).apply(document_light)

    assert_that(
        pages,
        contains_exactly(
            empty(),
            contains_exactly(
                card_container_with(to_move, pages[1]))
        ),
        "Incorrect card move"
    )


def test_apply_move_all_cards_onto_partially_filled_page(qtbot: QtBot, document_light: Document):
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    to_move = append_new_card_in_page(pages[0], "Move")
    on_page_1 = append_new_card_in_page(pages[1], "Stay on 1")
    row_move_validator = partial(validate_qt_model_move_signal_parameter, 0, 0, 0, 1, 1)
    with qtbot.wait_signals(
            [document_light.page_type_changed, document_light.rowsAboutToBeMoved, document_light.rowsMoved],
            timeout=1000, check_params_cbs=[lambda index: index.row() == 0] +
                                           [row_move_validator] * 2):
        ActionMoveCardsBetweenPages(0, [0], 1).apply(document_light)

    assert_that(
        pages,
        contains_exactly(
            empty(),
            contains_exactly(
                card_container_with(on_page_1, pages[1]),
                card_container_with(to_move, pages[1])
            )
        ),
        "Incorrect card move"
    )


def test_apply_move_subset_of_cards_onto_empty_page(qtbot: QtBot, document_light: Document):
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    to_move = append_new_card_in_page(pages[0], "Move")
    on_page_0 = append_new_card_in_page(pages[0], "Stay on 0")

    row_move_validator = partial(validate_qt_model_move_signal_parameter, 0, 0, 0, 1, 0)
    with qtbot.wait_signals(
            [document_light.page_type_changed, document_light.rowsAboutToBeMoved, document_light.rowsMoved],
            timeout=1000, check_params_cbs=[lambda index: index.row() == 1] +
                                           [row_move_validator] * 2):
        ActionMoveCardsBetweenPages(0, [0], 1).apply(document_light)

    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(on_page_0, pages[0])),
            contains_exactly(
                card_container_with(to_move, pages[1]))
        ),
        "Incorrect card move"
    )


def test_apply_move_subset_of_cards_onto_partially_filled_page(qtbot: QtBot, document_light: Document):
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    to_move = append_new_card_in_page(pages[0], "Move")
    on_page_0 = append_new_card_in_page(pages[0], "Stay on 0")
    on_page_1 = append_new_card_in_page(pages[1], "Stay on 1")
    row_move_validator = partial(validate_qt_model_move_signal_parameter, 0, 0, 0, 1, 1)
    with qtbot.assert_not_emitted(document_light.page_type_changed), \
            qtbot.wait_signals(
                [document_light.rowsAboutToBeMoved, document_light.rowsMoved],
                timeout=1000, check_params_cbs=[row_move_validator] * 2):
        ActionMoveCardsBetweenPages(0, [0], 1).apply(document_light)

    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(on_page_0, pages[0])),
            contains_exactly(
                card_container_with(on_page_1, pages[1]),
                card_container_with(to_move, pages[1]))
        ),
        "Incorrect card move"
    )


def test_apply_move_center_block(qtbot: QtBot, document_light: Document):
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    on_page_0_0 = append_new_card_in_page(pages[0], "Stay on 0")
    to_move_1 = append_new_card_in_page(pages[0], "Move")
    to_move_2 = append_new_card_in_page(pages[0], "Move")
    on_page_0_1 = append_new_card_in_page(pages[0], "Stay on 0")
    on_page_1_0 = append_new_card_in_page(pages[1], "Stay on 1")
    on_page_1_1 = append_new_card_in_page(pages[1], "Stay on 1")

    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(on_page_0_0, pages[0]),
                card_container_with(to_move_1, pages[0]),
                card_container_with(to_move_2, pages[0]),
                card_container_with(on_page_0_1, pages[0])),
            contains_exactly(
                card_container_with(on_page_1_0, pages[1]),
                card_container_with(on_page_1_1, pages[1])),
        ),
        "Test setup failed"
    )
    row_move_validator = partial(validate_qt_model_move_signal_parameter, 0, 1, 2, 1, 2)
    with qtbot.assert_not_emitted(document_light.page_type_changed), \
            qtbot.wait_signals(
                [document_light.rowsAboutToBeMoved, document_light.rowsMoved],
                timeout=1000, check_params_cbs=[row_move_validator] * 2):
        ActionMoveCardsBetweenPages(0, [1, 2], 1).apply(document_light)

    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(on_page_0_0, pages[0]),
                card_container_with(on_page_0_1, pages[0])),
            contains_exactly(
                card_container_with(on_page_1_0, pages[1]),
                card_container_with(on_page_1_1, pages[1]),
                card_container_with(to_move_1, pages[1]),
                card_container_with(to_move_2, pages[1])),
        ),
        "Incorrect card move"
    )


def test_apply_move_two_separate_cards(qtbot: QtBot, document_light: Document):
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    to_move_1 = append_new_card_in_page(pages[0], "Move")
    on_page_0_0 = append_new_card_in_page(pages[0], "Stay on 0")
    to_move_2 = append_new_card_in_page(pages[0], "Move")
    on_page_1_0 = append_new_card_in_page(pages[1], "Stay on 1")
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(to_move_1, pages[0]),
                card_container_with(on_page_0_0, pages[0]),
                card_container_with(to_move_2, pages[0])),
            contains_exactly(
                card_container_with(on_page_1_0, pages[1])),
        ),
        "Test setup failed"
    )
    row_move_validator_1 = partial(validate_qt_model_move_signal_parameter, 0, 2, 2, 1, 1)
    row_move_validator_2 = partial(validate_qt_model_move_signal_parameter, 0, 0, 0, 1, 1)
    with qtbot.assert_not_emitted(document_light.page_type_changed), \
            qtbot.wait_signals(
                [document_light.rowsAboutToBeMoved, document_light.rowsMoved]*2,
                timeout=1000, check_params_cbs=[row_move_validator_1] * 2 + [row_move_validator_2] * 2):
        ActionMoveCardsBetweenPages(0, [0, 2], 1).apply(document_light)
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(on_page_0_0, pages[0])),
            contains_exactly(
                card_container_with(on_page_1_0, pages[1]),
                card_container_with(to_move_1, pages[1]),
                card_container_with(to_move_2, pages[1])),
        ),
        "Incorrect card move"
    )


def test_apply_move_card_with_target_inserts_at_front(qtbot: QtBot, document_light: Document):
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    card_1 = append_new_card_in_page(pages[0], "Move1")
    not_moved = append_new_card_in_page(pages[0], "Stay on 0")
    card_2 = append_new_card_in_page(pages[1], "After")
    action = ActionMoveCardsBetweenPages(0, [0], 1, 0)
    row_move_validator = partial(validate_qt_model_move_signal_parameter, 0, 0, 0, 1, 0)
    with qtbot.assert_not_emitted(document_light.page_type_changed), \
            qtbot.wait_signals(
                [document_light.rowsAboutToBeMoved, document_light.rowsMoved],
                timeout=1000, check_params_cbs=[row_move_validator] * 2):
        action.apply(document_light)
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(not_moved, pages[0]),
            ),
            contains_exactly(
                card_container_with(card_1, pages[1]),
                card_container_with(card_2, pages[1]),
            )
        ),
        "Incorrect card move"
    )


def test_apply_move_card_with_target_inserts_between_cards(qtbot: QtBot, document_light: Document):
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    card_1 = append_new_card_in_page(pages[0], "Move1")
    not_moved = append_new_card_in_page(pages[0], "Stay on 0")
    card_2 = append_new_card_in_page(pages[1], "Before")
    card_3 = append_new_card_in_page(pages[1], "After")
    action = ActionMoveCardsBetweenPages(0, [0], 1, 1)
    row_move_validator = partial(validate_qt_model_move_signal_parameter, 0, 0, 0, 1, 1)
    with qtbot.assert_not_emitted(document_light.page_type_changed), \
            qtbot.wait_signals(
                [document_light.rowsAboutToBeMoved, document_light.rowsMoved],
                timeout=1000, check_params_cbs=[row_move_validator] * 2):
        action.apply(document_light)
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(not_moved, pages[0]),
            ),
            contains_exactly(
                card_container_with(card_2, pages[1]),
                card_container_with(card_1, pages[1]),
                card_container_with(card_3, pages[1]),
            )
        ),
        "Incorrect card move"
    )


@pytest.mark.parametrize("target_row", [None, 1])  # Because the target has 1 card, both should give the same result
def test_apply_move_card_with_target_appends_to_page(qtbot: QtBot, document_light: Document, target_row: OptInt):
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    card_1 = append_new_card_in_page(pages[0], "Move1")
    not_moved = append_new_card_in_page(pages[0], "Stay on 0")
    card_2 = append_new_card_in_page(pages[1], "Before")
    action = ActionMoveCardsBetweenPages(0, [0], 1, target_row)
    row_move_validator = partial(validate_qt_model_move_signal_parameter, 0, 0, 0, 1, 1)
    with qtbot.assert_not_emitted(document_light.page_type_changed), \
            qtbot.wait_signals(
                [document_light.rowsAboutToBeMoved, document_light.rowsMoved],
                timeout=1000, check_params_cbs=[row_move_validator] * 2):
        action.apply(document_light)
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(not_moved, pages[0]),
            ),
            contains_exactly(
                card_container_with(card_2, pages[1]),
                card_container_with(card_1, pages[1]),
            )
        ),
        "Incorrect card move"
    )


@pytest.mark.parametrize("target_row", [0, 1, None])
def test_apply_without_indices_does_nothing(qtbot: QtBot, document_light: Document, target_row: OptInt):
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    card_1 = append_new_card_in_page(pages[0], "Move1")
    card_2 = append_new_card_in_page(pages[1], "After")
    action = ActionMoveCardsBetweenPages(0, [], 1, target_row)
    with qtbot.assert_not_emitted(document_light.page_type_changed), \
            qtbot.assert_not_emitted(document_light.rowsAboutToBeMoved), \
            qtbot.assert_not_emitted(document_light.rowsMoved):
        action.apply(document_light)
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(card_1, pages[0])
            ),
            contains_exactly(
                card_container_with(card_2, pages[1]),
            )
        ),
        "Unexpected card move"
    )


@pytest.mark.parametrize("indices", [[], [0], [1], [0, 1], [0, 2], [0, 1, 2], [0, 1, 3, 4]])
def test___total_moved_cards(indices: IntList):
    action = ActionMoveCardsBetweenPages(0, indices, 0)
    expected_result = len(indices)
    assert_that(action._total_moved_cards(), is_(equal_to(expected_result)))


def _create_applied_action(
        source: int, cards_to_move: list[int], target_page: int, target_row: int = None) -> ActionMoveCardsBetweenPages:
    action = ActionMoveCardsBetweenPages(source, cards_to_move, target_page, target_row)
    action._already_applied = True
    return action


def test_undo_resets_already_applied(document_light: Document):
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    append_new_card_in_page(pages[1], "Move")
    action = _create_applied_action(0, [0], 1)
    action.undo(document_light)
    assert_that(action._already_applied, is_(False))


def test_undo_move_all_cards_onto_empty_page(qtbot: QtBot, document_light: Document):
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    to_move = append_new_card_in_page(pages[1], "Move")
    row_move_validator = partial(validate_qt_model_move_signal_parameter, 1, 0, 0, 0, 0)
    action = _create_applied_action(0, [0], 1)
    with qtbot.wait_signals(
            [document_light.page_type_changed] * 2 + [document_light.rowsAboutToBeMoved, document_light.rowsMoved],
            timeout=1000, check_params_cbs=[lambda index: index.row() == 0, lambda index: index.row() == 1] +
                                           [row_move_validator] * 2):
        action.undo(document_light)

    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(to_move, pages[0])),
            empty()
        ),
        "Incorrect card move"
    )


def test_undo_move_all_cards_onto_partially_filled_page(qtbot: QtBot, document_light: Document):
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    on_page_1 = append_new_card_in_page(pages[1], "Stay on 1")
    to_move = append_new_card_in_page(pages[1], "Move")
    row_move_validator = partial(validate_qt_model_move_signal_parameter, 1, 1, 1, 0, 0)
    action = _create_applied_action(0, [0], 1)
    with qtbot.wait_signals(
            [document_light.page_type_changed, document_light.rowsAboutToBeMoved, document_light.rowsMoved],
            timeout=1000, check_params_cbs=[lambda index: index.row() == 0] +
                                           [row_move_validator] * 2):
        action.undo(document_light)

    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(to_move, pages[0])),
            contains_exactly(
                card_container_with(on_page_1, pages[1]))
        ),
        "Incorrect card move"
    )


def test_undo_separates_two_source_ranges(qtbot: QtBot, document_light: Document):
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    on_page_0_0 = append_new_card_in_page(pages[0], "Stay on 0")
    on_page_1_0 = append_new_card_in_page(pages[1], "Stay on 1")
    to_move_1 = append_new_card_in_page(pages[1], "Move")
    to_move_2 = append_new_card_in_page(pages[1], "Move")
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(on_page_0_0, pages[0])),
            contains_exactly(
                card_container_with(on_page_1_0, pages[1]),
                card_container_with(to_move_1, pages[1]),
                card_container_with(to_move_2, pages[1])),
        ),
        "Test setup failed"
    )
    row_move_validator_1 = partial(validate_qt_model_move_signal_parameter, 1, 1, 1, 0, 0)
    row_move_validator_2 = partial(validate_qt_model_move_signal_parameter, 1, 1, 1, 0, 2)
    action = _create_applied_action(0, [0, 2], 1)
    with qtbot.assert_not_emitted(document_light.page_type_changed), \
            qtbot.wait_signals(
                [document_light.rowsAboutToBeMoved, document_light.rowsMoved]*2,
                timeout=1000, check_params_cbs=[row_move_validator_1] * 2 + [row_move_validator_2] * 2):
        action.undo(document_light)

    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(to_move_1, pages[0]),
                card_container_with(on_page_0_0, pages[0]),
                card_container_with(to_move_2, pages[0])),
            contains_exactly(
                card_container_with(on_page_1_0, pages[1])),
        ),
        "Incorrect card move" +
        f": {[c.card.name for c in pages[0]]} + {[c.card.name for c in pages[1]]}"
    )


def test_undo_with_target_at_front_from_front(qtbot: QtBot, document_light: Document):
    """
    test Undo [[C1, C2], [C3]] → [[C2], [C1, C3]]
    """
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    c2 = append_new_card_in_page(pages[0], "C2")
    c1 = append_new_card_in_page(pages[1], "C1")
    c3 = append_new_card_in_page(pages[1], "C3")
    row_move_validator = partial(validate_qt_model_move_signal_parameter, 1, 0, 0, 0, 0)
    action = _create_applied_action(0, [0], 1, 0)
    with qtbot.assert_not_emitted(document_light.page_type_changed), \
            qtbot.wait_signals(
                [document_light.rowsAboutToBeMoved, document_light.rowsMoved],
                timeout=1000, check_params_cbs=[row_move_validator] * 2):
        action.undo(document_light)
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with_name(c1.name, pages[0]),
                card_container_with_name(c2.name, pages[0]),
            ),
            contains_exactly(
                card_container_with_name(c3.name, pages[1]),
            )
        ),
        "Incorrect card move"
    )


def test_undo_with_target_within_page(qtbot: QtBot, document_light: Document):
    """
    test Undo [[C1, C2], [C3, C4]] → [[C2], [C3, C1, C4]]
    """
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    c2 = append_new_card_in_page(pages[0], "C2")
    c3 = append_new_card_in_page(pages[1], "C3")
    c1 = append_new_card_in_page(pages[1], "C1")
    c4 = append_new_card_in_page(pages[1], "C4")
    row_move_validator = partial(validate_qt_model_move_signal_parameter, 1, 1, 1, 0, 0)
    action = _create_applied_action(0, [0], 1, 1)
    with qtbot.assert_not_emitted(document_light.page_type_changed), \
            qtbot.wait_signals(
                [document_light.rowsAboutToBeMoved, document_light.rowsMoved],
                timeout=1000, check_params_cbs=[row_move_validator] * 2):
        action.undo(document_light)
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(c1, pages[0]),
                card_container_with(c2, pages[0]),
            ),
            contains_exactly(
                card_container_with(c3, pages[1]),
                card_container_with(c4, pages[1]),
            )
        ),
        "Incorrect card move"
    )


@pytest.mark.parametrize("target_row", [None, 1])
def test_undo_with_target_at_end_from_begin(qtbot: QtBot, document_light: Document, target_row: OptInt):
    """
    test Undo [[C1, C2], [C3]] → [[C2], [C3, C1]]
    """
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    c2 = append_new_card_in_page(pages[0], "C2")
    c3 = append_new_card_in_page(pages[1], "C3")
    c1 = append_new_card_in_page(pages[1], "C1")
    row_move_validator = partial(validate_qt_model_move_signal_parameter, 1, 1, 1, 0, 0)
    action = _create_applied_action(0, [0], 1, target_row)
    with qtbot.assert_not_emitted(document_light.page_type_changed), \
            qtbot.wait_signals(
                [document_light.rowsAboutToBeMoved, document_light.rowsMoved],
                timeout=1000, check_params_cbs=[row_move_validator] * 2):
        action.undo(document_light)
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(c1, pages[0]),
                card_container_with(c2, pages[0]),
            ),
            contains_exactly(
                card_container_with(c3, pages[1]),
            )
        ),
        "Incorrect card move"
    )


@pytest.mark.parametrize("target_row", [None, 1])
def test_undo_with_target_at_end_from_end(qtbot: QtBot, document_light: Document, target_row: OptInt):
    """
    test Undo [[C1, C2], [C3]] → [[C1], [C3, C2]]
    """
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    c1 = append_new_card_in_page(pages[0], "C1")
    c3 = append_new_card_in_page(pages[1], "C3")
    c2 = append_new_card_in_page(pages[1], "C2")
    row_move_validator = partial(validate_qt_model_move_signal_parameter, 1, 1, 1, 0, 1)
    action = _create_applied_action(0, [1], 1, target_row)
    with qtbot.assert_not_emitted(document_light.page_type_changed), \
            qtbot.wait_signals(
                [document_light.rowsAboutToBeMoved, document_light.rowsMoved],
                timeout=1000, check_params_cbs=[row_move_validator] * 2):
        action.undo(document_light)
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(c1, pages[0]),
                card_container_with(c2, pages[0]),
            ),
            contains_exactly(
                card_container_with(c3, pages[1]),
            )
        ),
        "Incorrect card move"
    )

@pytest.fixture()
def document_with_cards(document_light: Document) -> Document:
    ActionNewPage(count=3, content=[[], [], []]).apply(document_light)
    pages = document_light.pages
    content: list[tuple[int, str]] = [
        (0, "A1"),
        (0, "A2"),
        (0, "A3"),
        (1, "B1"),
        (1, "B2"),
        (1, "B3"),
        (3, "D1"),
        (3, "D2"),
        (3, "D3"),
        (3, "D4"),
        (3, "D5"),
        (3, "D6"),
    ]
    for page, name in content:
        append_new_card_in_page(pages[page], name)
    return document_light


def gather_card_names(document: Document) -> Sequence[str]:
    return [
        ",".join(container.card.name for container in page)
        for page in document.pages
    ]

def generate_test_cases_for_card_moves_between_pages():
    # Tuples source, cards_to_move, target_page, target_row, expected
    # Origin card order: ["A1,A2,A3", "B1,B2,B3", "", "D1,D2,D3,D4,D5,D6"]

    # Move onto another existing page
    yield 0, [0], 1, None, ["A2,A3", "B1,B2,B3,A1", "", "D1,D2,D3,D4,D5,D6"]
    yield 0, [0], 1, 3, ["A2,A3", "B1,B2,B3,A1", "", "D1,D2,D3,D4,D5,D6"]
    yield 0, [0], 1, 0, ["A2,A3", "A1,B1,B2,B3", "", "D1,D2,D3,D4,D5,D6"]
    yield 0, [0, 2], 1, None, ["A2", "B1,B2,B3,A1,A3", "", "D1,D2,D3,D4,D5,D6"]
    yield 0, [1], 1, None, ["A1,A3", "B1,B2,B3,A2", "", "D1,D2,D3,D4,D5,D6"]
    yield 0, [0, 1, 2], 1, None, ["", "B1,B2,B3,A1,A2,A3", "", "D1,D2,D3,D4,D5,D6"]
    yield 0, [0, 1, 2], 1, 1, ["", "B1,A1,A2,A3,B2,B3", "", "D1,D2,D3,D4,D5,D6"]
    yield 1, [0], 2, None, ["A1,A2,A3", "B2,B3", "B1", "D1,D2,D3,D4,D5,D6"]
    yield 1, [0], 3, None, ["A1,A2,A3", "B2,B3", "", "D1,D2,D3,D4,D5,D6,B1"]
    yield 3, [0, 2], 0, None, ["A1,A2,A3,D1,D3", "B1,B2,B3", "", "D2,D4,D5,D6"]
    # Move to new page before target_page
    yield 3, [0, 2, 3, 5], 0, -1, ["D1,D3,D4,D6", "A1,A2,A3", "B1,B2,B3", "", "D2,D5"]
    yield 3, [0, 2, 3, 5], 1, -1, ["A1,A2,A3", "D1,D3,D4,D6", "B1,B2,B3", "", "D2,D5"]
    # Move to new page at document end
    yield 3, [0, 2, 3, 5], 4, -1, ["A1,A2,A3", "B1,B2,B3", "", "D2,D5", "D1,D3,D4,D6"]


@pytest.mark.parametrize(
    "source, cards_to_move, target_page, target_row, expected",
    generate_test_cases_for_card_moves_between_pages())
def test_ActionMoveCardsBetweenPages_apply(
        document_with_cards: Document,
        source: int, cards_to_move: list[int], target_page: int, target_row: int|None,
        expected: list[str]):
    action = ActionMoveCardsBetweenPages(source, cards_to_move, target_page, target_row)
    action.apply(document_with_cards)
    result = gather_card_names(document_with_cards)
    assert_that(result, contains_exactly(*expected), f"Got: {result}")


@pytest.mark.parametrize(
    "source, cards_to_move, target_page, target_row, expected",
    generate_test_cases_for_card_moves_between_pages())
def test_ActionMoveCardsBetweenPages_undo(
        document_with_cards: Document,
        source: int, cards_to_move: list[int], target_page: int, target_row: int|None,
        expected: list[str]):
    action = ActionMoveCardsBetweenPages(source, cards_to_move, target_page, target_row)
    action.apply(document_with_cards)
    try:
        assert_that(gather_card_names(document_with_cards), contains_exactly(*expected))
    except AssertionError:
        pytest.skip("Test setup failed")
    action.undo(document_with_cards)
    result = gather_card_names(document_with_cards)
    assert_that(result, contains_exactly("A1,A2,A3", "B1,B2,B3", "", "D1,D2,D3,D4,D5,D6"), f"Got: {result}")

def generate_test_cases_for_card_moves_within_page():
    # Tuples page, cards_to_move, target_row, expected
    # Origin card order: ["A1,A2,A3", "B1,B2,B3", "", "D1,D2,D3,D4,D5,D6"]

    yield 0, [0], None, ["A2,A3,A1", "B1,B2,B3", "", "D1,D2,D3,D4,D5,D6"]  # 0
    yield 0, [0], 0, ["A1,A2,A3", "B1,B2,B3", "", "D1,D2,D3,D4,D5,D6"]  # 1
    yield 0, [0], 1, ["A1,A2,A3", "B1,B2,B3", "", "D1,D2,D3,D4,D5,D6"]  # 2
    yield 0, [0], 2, ["A2,A1,A3", "B1,B2,B3", "", "D1,D2,D3,D4,D5,D6"]  # 3
    yield 0, [0], 3, ["A2,A3,A1", "B1,B2,B3", "", "D1,D2,D3,D4,D5,D6"]  # 4
    yield 3, [0, 1, 5], None, ["A1,A2,A3", "B1,B2,B3", "", "D3,D4,D5,D1,D2,D6"]  # 5
    yield 3, [0, 5], 0, ["A1,A2,A3", "B1,B2,B3", "", "D1,D6,D2,D3,D4,D5"]  # 6
    yield 3, [0, 5], 3, ["A1,A2,A3", "B1,B2,B3", "", "D2,D3,D1,D6,D4,D5"]  # 7
    yield 3, [0, 2], 4, ["A1,A2,A3", "B1,B2,B3", "", "D2,D4,D1,D3,D5,D6"]  # 8
    yield 3, [3, 5], 0, ["A1,A2,A3", "B1,B2,B3", "", "D4,D6,D1,D2,D3,D5"]  # 9
    yield 3, [1, 2, 4, 5], 0, ["A1,A2,A3", "B1,B2,B3", "", "D2,D3,D5,D6,D1,D4"]  # 10
    yield 0, [2], 0, ["A3,A1,A2", "B1,B2,B3", "", "D1,D2,D3,D4,D5,D6"]  # 11
    yield 0, [2], 1, ["A1,A3,A2", "B1,B2,B3", "", "D1,D2,D3,D4,D5,D6"]  # 12
    yield 0, [2], 2, ["A1,A2,A3", "B1,B2,B3", "", "D1,D2,D3,D4,D5,D6"]  # 13
    yield 0, [2], 3, ["A1,A2,A3", "B1,B2,B3", "", "D1,D2,D3,D4,D5,D6"]  # 14
    yield 3, [0,2,4], 2, ["A1,A2,A3", "B1,B2,B3", "", "D2,D1,D3,D5,D4,D6"]  # 15
    yield 3, [1,2,5], 1, ["A1,A2,A3", "B1,B2,B3", "", "D1,D2,D3,D6,D4,D5"]  # 16


@pytest.mark.parametrize(
    "page, cards_to_move, target_row, expected",
    generate_test_cases_for_card_moves_within_page())
def test_ActionMoveCardsWithinPage_apply(document_with_cards: Document, page: int, cards_to_move: list[int],
                                         target_row: int|None, expected: list[str]):
    ActionMoveCardsWithinPage(page, cards_to_move, target_row).apply(document_with_cards)
    result = gather_card_names(document_with_cards)
    assert_that(result, contains_exactly(*expected), f"Got: {result}")


@pytest.mark.parametrize(
    "page, cards_to_move, target_row, after_apply",
    generate_test_cases_for_card_moves_within_page())
def test_ActionMoveCardsWithinPage_undo(document_with_cards: Document, page: int, cards_to_move: list[int],
                                        target_row: int|None, after_apply: list[str]):
    (action := ActionMoveCardsWithinPage(page, cards_to_move, target_row)).apply(document_with_cards)
    try:
        assert_that(gather_card_names(document_with_cards), contains_exactly(*after_apply))
    except AssertionError:
        pytest.skip("Test setup failed")
    action.undo(document_with_cards)
    result = gather_card_names(document_with_cards)
    assert_that(result, contains_exactly("A1,A2,A3", "B1,B2,B3", "", "D1,D2,D3,D4,D5,D6"), f"Got: {result}")
