# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>
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

import copy
import unittest.mock

import pytest
from hamcrest import *

from mtg_proxy_printer.model.carddb import Card, MTGSet, CheckCard
from mtg_proxy_printer.model.document_page import PageType
from mtg_proxy_printer.document_controller import IllegalStateError
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage

from .test_action_new_page import append_new_pages
from .helpers import insert_card_in_page, card_container_with


@pytest.fixture()
def card():
    return Card("", MTGSet("", ""), "", "", "", True, "", "", True, False, 0, False, None)


@pytest.fixture()
def oversized_card():
    return Card("", MTGSet("", ""), "", "", "", True, "", "", True, True, 0, False, None)


@pytest.fixture()
def check_card(card, image_db):
    card.image_file = image_db.blank_image
    card.is_dfc = True
    other = copy.copy(card)
    other.is_front = False
    return CheckCard(card, other)


@pytest.fixture()
def document_light_3(document_light):
    ActionNewPage(count=2).apply(document_light)
    return document_light


def test_apply_without_count_adds_single_card(qtbot, card, document_light):
    action = ActionAddCard(card)
    page = document_light.pages[0]
    assert_that(action.apply(document_light), is_(same_instance(action)))
    assert_that(
        page,
        contains_exactly(
            card_container_with(card, page)
        )
    )
    assert_that(action.added_cards_to_existing_pages, contains_exactly((0, 1)))
    assert_that(action.added_new_pages, is_(0))


@pytest.mark.parametrize("target_page", range(3))
def test_apply_without_count_and_with_target_page_adds_single_card_to_that_page(
        qtbot, card, document_light_3, target_page: int):
    action = ActionAddCard(card, target_page=target_page)
    page = document_light_3.pages[target_page]
    assert_that(action.apply(document_light_3), is_(same_instance(action)))
    assert_that(
        page,
        contains_exactly(
            card_container_with(card, page)
        )
    )
    assert_that(action.added_cards_to_existing_pages, contains_exactly((target_page, 1)))
    assert_that(action.added_new_pages, is_(0))


def test_apply_with_check_card_adds_card_to_current_page(qtbot, card, check_card, document_light):
    action1 = ActionAddCard(card)
    action2 = ActionAddCard(check_card)
    page = document_light.pages[0]
    action1.apply(document_light)
    action2.apply(document_light)
    assert_that(document_light.rowCount(), is_(1))
    assert_that(
        page,
        contains_exactly(
            card_container_with(card, page),
            card_container_with(check_card, page),
        ),
    )


@pytest.mark.parametrize("count", [1, 3])
def test_apply_with_count_adds_that_many_copies(qtbot, card, document_light, count: int):
    action = ActionAddCard(card, count)
    page = document_light.pages[0]
    assert_that(action.apply(document_light), is_(same_instance(action)))
    assert_that(
        page,
        contains_exactly(
            *[card_container_with(card, page)]*count
        )
    )
    assert_that(action.added_cards_to_existing_pages, contains_exactly((0, count)))
    assert_that(action.added_new_pages, is_(0))


@pytest.mark.parametrize("count", [1, 3])
@pytest.mark.parametrize("target_page", range(3))
def test_apply_with_count_and_with_target_page_adds_that_many_copies_to_that_page(
        qtbot, card, document_light_3, target_page: int, count: int):
    action = ActionAddCard(card, count, target_page=target_page)
    page = document_light_3.pages[target_page]
    assert_that(action.apply(document_light_3), is_(same_instance(action)))
    assert_that(
        page,
        contains_exactly(
            *[card_container_with(card, page)]*count
        )
    )
    assert_that(action.added_cards_to_existing_pages, contains_exactly((target_page, count)))
    assert_that(action.added_new_pages, is_(0))


def test_apply_with_target_page_works_while_currently_edited_page_is_full(qtbot, card, document_light_3):
    document_light_3.set_currently_edited_page(document_light_3.pages[0])
    ActionAddCard(card, 9).apply(document_light_3)
    ActionAddCard(card, 2, target_page=1).apply(document_light_3)
    assert_that(
        document_light_3.pages,
        contains_exactly(
            has_length(9),
            has_length(2),
            is_(empty()),
        )
    )


def test_apply_with_count_overflowing_page_adds_new_page(qtbot, card, document_light):
    capacity = document_light.page_layout.compute_page_card_capacity()
    count = capacity * 3
    action = ActionAddCard(card, count)
    assert_that(action.apply(document_light), is_(same_instance(action)))
    for page in document_light.pages:
        assert_that(
            page,
            contains_exactly(
                *[card_container_with(card, page)]*capacity
            )
        )
    assert_that(action.added_cards_to_existing_pages, contains_exactly((0, capacity)))
    assert_that(action.added_new_pages, is_(2))


def test_apply_emits_page_type_changed_when_page_type_changes(qtbot, card, document_light):
    with qtbot.wait_signal(document_light.page_type_changed, timeout=1000, check_params_cb=lambda x: x.row() == 0):
        ActionAddCard(card).apply(document_light)
    with qtbot.assert_not_emitted(document_light.page_type_changed):
        ActionAddCard(card).apply(document_light)


def test_undo_without_internal_saved_state_raises_exception(card):
    action = ActionAddCard(card)
    assert_that(calling(action.undo).with_args(unittest.mock.MagicMock), raises(IllegalStateError))


def test_undo_deletes_pages_created_during_apply(qtbot, card, document_light):
    pages = document_light.pages
    capacity = document_light.page_layout.compute_page_card_capacity()
    append_new_pages(document_light, 2)
    for page in range(3):
        insert_card_in_page(pages[page], card, capacity)
    count = capacity * 3 - 1
    action = ActionAddCard(card, count)
    action.added_new_pages = 2
    action.added_cards_to_existing_pages.append((0, capacity-1))

    assert_that(action.undo(document_light), is_(same_instance(action)))
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(card_container_with(card, pages[0])
            )
        )
    )
    assert_that(action.added_new_pages, is_(0))
    assert_that(action.added_cards_to_existing_pages, is_(empty()))


@pytest.mark.parametrize("oversized_first", [True, False])
def test_apply_does_not_create_pages_with_mixed_card_sizes(
        document_light, card: Card, oversized_card: Card, oversized_first: bool):
    if oversized_first:
        ActionAddCard(oversized_card).apply(document_light)
        ActionAddCard(card).apply(document_light)
    else:
        ActionAddCard(card).apply(document_light)
        ActionAddCard(oversized_card).apply(document_light)

    assert_that(document_light.rowCount(), is_(2))
    for page in document_light.pages:
        assert_that(page.page_type(), is_in((PageType.REGULAR, PageType.OVERSIZED)))
        assert_that(page, has_length(1))


def test_apply_does_not_overfill_oversized_pages(document_light, oversized_card: Card):
    ActionAddCard(oversized_card, 7).apply(document_light)
    assert_that(document_light.rowCount(), is_(2))
    ActionAddCard(oversized_card, 2).apply(document_light)
    assert_that(document_light.rowCount(), is_(3))


@pytest.mark.parametrize("page_type", [PageType.REGULAR, PageType.OVERSIZED])
def test_apply_only_emits_page_type_changed_signal_if_changed(
        qtbot, document_light, card, oversized_card, page_type: PageType):
    added_card = oversized_card if page_type == PageType.OVERSIZED else card

    with qtbot.wait_signal(document_light.page_type_changed):
        ActionAddCard(added_card).apply(document_light)
    with qtbot.assertNotEmitted(document_light.page_type_changed):
        ActionAddCard(added_card).apply(document_light)
    assert_that(document_light.pages[0].page_type(), is_(page_type))


def test_undo_works_when_apply_searched_over_multiple_full_pages_for_free_slot(document_light, card):
    """
    A ValueError (including a SegmentationFault) occurred in undo() when
    - apply() had to search over multiple full pages,
    - then appended a new page
    - placed the card on that page
    - And then the action was undone.
    """
    pages = document_light.pages
    page_capactiy = document_light.page_layout.compute_page_card_capacity(card.requested_page_type())
    ActionAddCard(card, 2*page_capactiy).apply(document_light)
    assert_that(document_light.currently_edited_page, is_(same_instance(pages[0])))
    failing_action = ActionAddCard(card, 1).apply(document_light)
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                *[card_container_with(card, pages[0])]*page_capactiy
            ),
            contains_exactly(
                *[card_container_with(card, pages[1])]*page_capactiy
            ),
            contains_exactly(
                card_container_with(card, pages[2])
            )
        )
    )
    # Crash occurs in undo()
    failing_action.undo(document_light)
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                *[card_container_with(card, pages[0])]*page_capactiy
            ),
            contains_exactly(
                *[card_container_with(card, pages[1])]*page_capactiy
            )
        )
    )
