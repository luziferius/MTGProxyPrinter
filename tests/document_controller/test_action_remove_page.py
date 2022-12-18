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

from functools import partial

from hamcrest import *
from PyQt5.QtCore import QModelIndex

from mtg_proxy_printer.model.document_page import CardContainer, Page
from mtg_proxy_printer.document_controller import IllegalStateError
from mtg_proxy_printer.document_controller.page_actions import ActionRemovePage, ActionNewPage

from .test_action_new_page import insert_mock_in_page, verify_page_index_cache_is_valid, append_new_pages


def validate_qt_model_signal_parameter(
        expected_first: int, expected_last: int,
        parent: QModelIndex, first: int, last: int) -> bool:
    return not parent.isValid() and first == expected_first and last == expected_last


def test_apply_with_position_deletes_given_page_1(qtbot, document_light):
    append_new_pages(document_light, 1)
    remaining_page = document_light.pages[0]
    removed_page = document_light.pages[1]
    insert_mock_in_page(removed_page)
    action = ActionRemovePage(1)
    validator = partial(validate_qt_model_signal_parameter, 1, 1)
    with qtbot.wait_signals(
            [document_light.rowsAboutToBeRemoved, document_light.rowsRemoved],
            check_params_cbs=[validator]*2, timeout=100):
        assert_that(action.apply(document_light), is_(same_instance(action)))
    assert_that(
        document_light.pages,
        contains_exactly(
            all_of(same_instance(remaining_page), is_(empty()))
        )
    )
    verify_page_index_cache_is_valid(document_light)
    assert_that(
        action,
        has_properties({
            "position": 1,
            "count": 1,
            "removed_pages": contains_exactly(all_of(
                same_instance(removed_page),
                contains_exactly(instance_of(CardContainer)))),
            "currently_edited_page": none(),
        })
    )


def test_apply_with_position_deletes_given_page_0(qtbot, document_light):
    append_new_pages(document_light, 1)
    removed_page = document_light.pages[0]
    remaining_page = document_light.pages[1]
    insert_mock_in_page(remaining_page)
    document_light._set_currently_edited_page(remaining_page)
    action = ActionRemovePage(0)
    validator = partial(validate_qt_model_signal_parameter, 0, 0)
    with qtbot.wait_signals(
            [document_light.rowsAboutToBeRemoved, document_light.rowsRemoved],
            check_params_cbs=[validator]*2, timeout=100):
        assert_that(action.apply(document_light), is_(same_instance(action)))
    assert_that(
        document_light.pages,
        contains_exactly(
            all_of(same_instance(remaining_page), contains_exactly(instance_of(CardContainer)))
        )
    )
    verify_page_index_cache_is_valid(document_light)
    assert_that(
        action,
        has_properties({
            "position": 0,
            "count": 1,
            "removed_pages": contains_exactly(same_instance(removed_page)),
            "currently_edited_page": none(),
        })
    )


def test_apply_with_position_and_count_deletes_given_number_of_pages(qtbot, document_light):
    append_new_pages(document_light, 2)
    remaining_page = document_light.pages[0]
    removed_pages = document_light.pages[1:3]
    document_light._set_currently_edited_page(remaining_page)
    action = ActionRemovePage(1, 2)
    validator = partial(validate_qt_model_signal_parameter, 1, 2)
    with qtbot.wait_signals(
            [document_light.rowsAboutToBeRemoved, document_light.rowsRemoved],
            check_params_cbs=[validator]*2, timeout=100):
        assert_that(action.apply(document_light), is_(same_instance(action)))

    assert_that(
        document_light.pages,
        contains_exactly(
            same_instance(remaining_page)
        )
    )
    assert_that(
        action,
        has_properties({
            "position": 1,
            "count": 2,
            "removed_pages": contains_exactly(*removed_pages),
            "currently_edited_page": none(),
        })
    )
    verify_page_index_cache_is_valid(document_light)


def test_apply_with_position_and_count_includes_currently_edited_page_if_within_range(qtbot, document_light):
    append_new_pages(document_light, 2)
    remaining_page = document_light.pages[0]
    removed_pages = document_light.pages[1:3]
    document_light._set_currently_edited_page(document_light.pages[2])
    action = ActionRemovePage(1, 2)
    validator = partial(validate_qt_model_signal_parameter, 1, 2)
    with qtbot.wait_signals(
            [document_light.current_page_changed, document_light.rowsAboutToBeRemoved, document_light.rowsRemoved],
            check_params_cbs=[(lambda index: index.row() == index.column() == 0)] + [validator]*2, timeout=100):
        assert_that(action.apply(document_light), is_(same_instance(action)))
    assert_that(
        document_light.pages,
        contains_exactly(
            same_instance(remaining_page)
        )
    )
    assert_that(
        action,
        has_properties({
            "position": 1,
            "count": 2,
            "removed_pages": contains_exactly(*removed_pages),
            "currently_edited_page": removed_pages[1],
        })
    )
    verify_page_index_cache_is_valid(document_light)


def test_apply_without_position_deletes_currently_edited_page(qtbot, document_light):
    append_new_pages(document_light, 1)
    removed_page = document_light.pages[1]
    document_light._set_currently_edited_page(removed_page)
    insert_mock_in_page(removed_page)
    action = ActionRemovePage()
    validator = partial(validate_qt_model_signal_parameter, 1, 1)

    with qtbot.wait_signals(
            [document_light.current_page_changed, document_light.rowsAboutToBeRemoved, document_light.rowsRemoved],
            check_params_cbs=[(lambda index: index.row() == index.column() == 0)] + [validator]*2, timeout=100):
        assert_that(action.apply(document_light), is_(same_instance(action)))
    assert_that(
        document_light.pages,
        contains_exactly(
            all_of(instance_of(Page), is_(empty()))
        )
    )
    assert_that(
        action,
        has_properties({
            "position": 1,
            "count": 1,
            "removed_pages": contains_exactly(same_instance(removed_page)),
            "currently_edited_page": same_instance(removed_page),
        })
    )
    verify_page_index_cache_is_valid(document_light)


def test_undo_with_position_restores_page_at_given_middle_position(qtbot, document_light):
    append_new_pages(document_light, 1)
    action = ActionRemovePage(1)
    action.removed_pages.append(removed_page := Page())

    validator = partial(validate_qt_model_signal_parameter, 1, 1)
    with qtbot.wait_signals(
            [document_light.rowsAboutToBeInserted, document_light.rowsInserted],
            check_params_cbs=[validator]*2, timeout=100):
        assert_that(action.undo(document_light), is_(same_instance(action)))


    assert_that(
        document_light.pages,
        contains_exactly(
            all_of(instance_of(Page), is_(empty())),
            same_instance(removed_page),
            all_of(instance_of(Page), is_(empty())),
        )
    )
    verify_page_index_cache_is_valid(document_light)


def test_undo_with_position_restores_multiple_pages_at_given_middle_position(qtbot, document_light):
    append_new_pages(document_light, 1)
    action = ActionRemovePage(1, 2)
    action.removed_pages.append(removed_page_1 := Page())
    action.removed_pages.append(removed_page_2 := Page())
    validator = partial(validate_qt_model_signal_parameter, 1, 2)
    with qtbot.wait_signals(
            [document_light.rowsAboutToBeInserted, document_light.rowsInserted],
            check_params_cbs=[validator] * 2, timeout=100):
        assert_that(action.undo(document_light), is_(same_instance(action)))

    assert_that(
        document_light.pages,
        contains_exactly(
            all_of(instance_of(Page), is_(empty())),
            same_instance(removed_page_1),
            same_instance(removed_page_2),
            all_of(instance_of(Page), is_(empty())),
        )
    )
    verify_page_index_cache_is_valid(document_light)


def test_undo_restores_currently_edited_page(qtbot, document_light):
    append_new_pages(document_light, 1)
    action = ActionRemovePage(2)
    action.removed_pages.append(removed_page := Page())
    action.currently_edited_page = removed_page
    validator = partial(validate_qt_model_signal_parameter, 2, 2)
    with qtbot.wait_signals(
            [document_light.current_page_changed, document_light.rowsAboutToBeInserted, document_light.rowsInserted],
            check_params_cbs=[(lambda index: index.row() == 2 and index.column() == 0)] + [validator]*2, timeout=100):
        assert_that(action.undo(document_light), is_(same_instance(action)))
    assert_that(
        document_light.pages,
        contains_exactly(
            all_of(instance_of(Page), is_(empty())),
            all_of(instance_of(Page), is_(empty())),
            same_instance(removed_page),
        )
    )
    assert_that(document_light.currently_edited_page, is_(same_instance(removed_page)))
    verify_page_index_cache_is_valid(document_light)


def test_undo_without_initial_position_raises_exception(document_light):
    append_new_pages(document_light, 2)
    document_light._set_currently_edited_page(document_light.pages[1])
    action = ActionRemovePage()
    assert_that(calling(action.undo).with_args(document_light), raises(IllegalStateError))

