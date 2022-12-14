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

import unittest.mock

import pytest
from hamcrest import *

from mtg_proxy_printer.model.carddb import Card, MTGSet
from mtg_proxy_printer.model.document_page import CardContainer, Page
from mtg_proxy_printer.document_controller import IllegalStateError
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard

from .test_action_new_page import append_new_pages


def insert_card_in_page(page: Page, card, count: int = 1):
    """
    Inserts the given amount of mock cards into the given page to make it distinguishable from other pages.
    """
    for _ in range(count):
        page.append(CardContainer(page, card))


@pytest.fixture()
def card():
    return Card("", MTGSet("", ""), "", "", "", True, "", "", True, False, 0, None)


def test_apply_without_count_adds_single_card(qtbot, card, document_light):
    action = ActionAddCard(card)
    page = document_light.pages[0]
    assert_that(action.apply(document_light), is_(same_instance(action)))
    assert_that(
        page,
        contains_exactly(
            all_of(
                instance_of(CardContainer),
                has_properties({
                    "parent": same_instance(page),
                    "card": same_instance(card)
                })
            )
        )
    )
    assert_that(action.added_cards_to_existing_pages, contains_exactly((0, 1)))
    assert_that(action.added_new_pages, is_(0))


@pytest.mark.parametrize("count", [1, 3])
def test_apply_with_count_adds_single_card(qtbot, card, document_light, count: int):
    action = ActionAddCard(card, count)
    page = document_light.pages[0]
    assert_that(action.apply(document_light), is_(same_instance(action)))
    assert_that(
        page,
        contains_exactly(
            *[all_of(
                instance_of(CardContainer),
                has_properties({
                    "parent": same_instance(page),
                    "card": same_instance(card)
                })
            )]*count
        )
    )
    assert_that(action.added_cards_to_existing_pages, contains_exactly((0, count)))
    assert_that(action.added_new_pages, is_(0))


def test_apply_with_count_overflowing_page_adds_new_page(qtbot, card, document_light):
    capacity = document_light.page_layout.compute_page_card_capacity()
    count = capacity * 3
    action = ActionAddCard(card, count)
    assert_that(action.apply(document_light), is_(same_instance(action)))
    for page in document_light.pages:
        assert_that(
            page,
            contains_exactly(
                *[all_of(
                    instance_of(CardContainer),
                    has_properties({
                        "parent": same_instance(page),
                        "card": same_instance(card)
                    })
                )]*capacity
            )
        )
    assert_that(action.added_cards_to_existing_pages, contains_exactly((0, capacity)))
    assert_that(action.added_new_pages, is_(2))


def test_apply_emits_page_type_changed_when_page_type_changes(qtbot, card, document_light):
    with qtbot.wait_signal(document_light.page_type_changed, timeout=100, check_params_cb=lambda x: x.row() == 0):
        ActionAddCard(card).apply(document_light)
    with qtbot.assert_not_emitted(document_light.page_type_changed):
        ActionAddCard(card).apply(document_light)


def test_undo_without_internal_saved_state_raises_exception(card):
    action = ActionAddCard(card)
    assert_that(calling(action.undo).with_args(unittest.mock.MagicMock), raises(IllegalStateError))


def test_undo_deletes_pages_created_during_apply(qtbot, card, document_light):
    capacity = document_light.page_layout.compute_page_card_capacity()
    append_new_pages(document_light, 2)
    for page in range(3):
        insert_card_in_page(document_light.pages[page], card, capacity)
    count = capacity * 3 - 1
    action = ActionAddCard(card, count)
    action.added_new_pages = 2
    action.added_cards_to_existing_pages.append((0, capacity-1))

    assert_that(action.undo(document_light), is_(same_instance(action)))
    assert_that(
        document_light.pages,
        contains_exactly(
            contains_exactly(all_of(
                instance_of(CardContainer),
                has_properties({
                    "parent": same_instance(document_light.pages[0]),
                    "card": same_instance(card)
                }))
            )
        )
    )
