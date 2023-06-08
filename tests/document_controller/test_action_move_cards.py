# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>

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


from functools import partial

import pytest
from hamcrest import *
from PyQt5.QtCore import QModelIndex

from mtg_proxy_printer.model.document_page import PageType
from mtg_proxy_printer.document_controller import IllegalStateError
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage
from mtg_proxy_printer.document_controller.move_cards import ActionMoveCards

from .helpers import card_container_with, append_new_card_in_page


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


def test_apply_raises_exception_when_trying_to_create_a_mixed_size_page(document_light):
    ActionNewPage().apply(document_light)
    append_new_card_in_page(document_light.pages[0], "Normal")
    append_new_card_in_page(document_light.pages[1], "Large", True)
    assert_that(document_light.pages[0].page_type(), is_(PageType.REGULAR))
    assert_that(document_light.pages[1].page_type(), is_(PageType.OVERSIZED))
    assert_that(calling(ActionMoveCards(0, [0], 1).apply).with_args(document_light), raises(IllegalStateError))


def test_apply_move_all_cards_onto_empty_page(qtbot, document_light):
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    to_move = append_new_card_in_page(pages[0], "Normal")
    row_move_validator = partial(validate_qt_model_move_signal_parameter, 0, 0, 0, 1, 0)
    with qtbot.wait_signals(
            [document_light.page_type_changed] * 2 + [document_light.rowsAboutToBeMoved, document_light.rowsMoved],
            timeout=1000, check_params_cbs=[lambda index: index.row() == 0, lambda index: index.row() == 1] +
                                          [row_move_validator] * 2):
        ActionMoveCards(0, [0], 1).apply(document_light)

    assert_that(
        pages,
        contains_exactly(
            empty(),
            contains_exactly(
                card_container_with(to_move, pages[1]))
        ),
        "Incorrect card move"
    )


def test_apply_move_all_cards_onto_partially_filled_page(qtbot, document_light):
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    to_move = append_new_card_in_page(pages[0], "Move")
    on_page_1 = append_new_card_in_page(pages[1], "Stay on 1")
    row_move_validator = partial(validate_qt_model_move_signal_parameter, 0, 0, 0, 1, 1)
    with qtbot.wait_signals(
            [document_light.page_type_changed, document_light.rowsAboutToBeMoved, document_light.rowsMoved],
            timeout=1000, check_params_cbs=[lambda index: index.row() == 0] +
                                          [row_move_validator] * 2):
        ActionMoveCards(0, [0], 1).apply(document_light)

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


def test_apply_move_subset_of_cards_onto_empty_page(qtbot, document_light):
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    to_move = append_new_card_in_page(pages[0], "Move")
    on_page_0 = append_new_card_in_page(pages[0], "Stay on 0")

    row_move_validator = partial(validate_qt_model_move_signal_parameter, 0, 0, 0, 1, 0)
    with qtbot.wait_signals(
            [document_light.page_type_changed, document_light.rowsAboutToBeMoved, document_light.rowsMoved],
            timeout=1000, check_params_cbs=[lambda index: index.row() == 1] +
                                          [row_move_validator] * 2):
        ActionMoveCards(0, [0], 1).apply(document_light)

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


def test_apply_move_subset_of_cards_onto_partially_filled_page(qtbot, document_light):
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
        ActionMoveCards(0, [0], 1).apply(document_light)

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


def test_apply_move_center_block(qtbot, document_light):
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
        ActionMoveCards(0, [1, 2], 1).apply(document_light)

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


def test_apply_move_two_separate_cards(qtbot, document_light):
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
        ActionMoveCards(0, [0, 2], 1).apply(document_light)
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


@pytest.mark.parametrize("indices", [[], [0], [1], [0, 1], [0, 2], [0, 1, 2], [0, 1, 3, 4]])
def test___total_moved_cards(indices):
    action = ActionMoveCards(0, indices, 0)
    expected_result = len(indices)
    assert_that(action._total_moved_cards(), is_(equal_to(expected_result)))


def test_undo_move_all_cards_onto_empty_page(qtbot, document_light):
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    to_move = append_new_card_in_page(pages[1], "Move")
    row_move_validator = partial(validate_qt_model_move_signal_parameter, 1, 0, 0, 0, 0)
    with qtbot.wait_signals(
            [document_light.page_type_changed] * 2 + [document_light.rowsAboutToBeMoved, document_light.rowsMoved],
            timeout=1000, check_params_cbs=[lambda index: index.row() == 0, lambda index: index.row() == 1] +
                                          [row_move_validator] * 2):
        ActionMoveCards(0, [0], 1).undo(document_light)

    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(to_move, pages[0])),
            empty()
        ),
        "Incorrect card move"
    )


def test_undo_move_all_cards_onto_partially_filled_page(qtbot, document_light):
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    on_page_1 = append_new_card_in_page(pages[1], "Stay on 1")
    to_move = append_new_card_in_page(pages[1], "Move")
    row_move_validator = partial(validate_qt_model_move_signal_parameter, 1, 1, 1, 0, 0)
    with qtbot.wait_signals(
            [document_light.page_type_changed, document_light.rowsAboutToBeMoved, document_light.rowsMoved],
            timeout=1000, check_params_cbs=[lambda index: index.row() == 0] +
                                          [row_move_validator] * 2):
        ActionMoveCards(0, [0], 1).undo(document_light)

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


def test_undo_separates_two_source_ranges(qtbot, document_light):
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
    with qtbot.assert_not_emitted(document_light.page_type_changed), \
            qtbot.wait_signals(
                [document_light.rowsAboutToBeMoved, document_light.rowsMoved]*2,
                timeout=1000, check_params_cbs=[row_move_validator_1] * 2 + [row_move_validator_2] * 2):
        ActionMoveCards(0, [0, 2], 1).undo(document_light)

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

