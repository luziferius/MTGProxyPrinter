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
import unittest.mock
from typing import Callable

import pytest
from hamcrest import *
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.model.carddb import Card, MTGSet, CheckCard
from mtg_proxy_printer.model.document_page import PageType
from mtg_proxy_printer.document_controller import IllegalStateError
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage
from mtg_proxy_printer.units_and_sizes import CardSizes

from .test_action_new_page import append_new_pages
from .helpers import insert_card_in_page, card_container_with
from tests.conftest import ImageDatabaseFixture, DocumentFixture

CheckCardFixture = Callable[[], CheckCard]

@pytest.fixture()
def card() -> Card:
    return Card("", MTGSet("", ""), "", "", "", True, "", "", True, CardSizes.REGULAR, 0, False, None)


@pytest.fixture()
def oversized_card() -> Card:
    return Card("", MTGSet("", ""), "", "", "", True, "", "", True, CardSizes.OVERSIZED, 0, False, None)


@pytest.fixture()
def check_card(card: Card, image_db: ImageDatabaseFixture) -> CheckCardFixture:
    def create():
        imdb = image_db()
        card.image_file = imdb.get_blank()
        card.is_dfc = True
        other = copy.copy(card)
        other.is_front = False
        return CheckCard(card, other)
    return create


@pytest.fixture()
def document_light_3(document_light: DocumentFixture) -> DocumentFixture:
    def create():
        doc = document_light()
        ActionNewPage(count=2).apply(doc)
        return doc
    return create


def test_apply_without_count_adds_single_card(card: Card, document_light: DocumentFixture):
    document_light = document_light()
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
        card: Card, document_light_3: DocumentFixture, target_page: int):
    document_light_3 = document_light_3()
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


def test_apply_with_check_card_adds_card_to_current_page(
        card: Card, check_card: CheckCardFixture, document_light: DocumentFixture):
    check_card, document_light = check_card(), document_light()
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


@pytest.mark.parametrize("count", [1, 3, 9])
def test_apply_with_count_adds_that_many_copies(
        card: Card, document_light: DocumentFixture, count: int):
    document_light = document_light()
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
        card: Card, document_light_3: DocumentFixture, target_page: int, count: int):
    document_light_3 = document_light_3()
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


def test_apply_with_target_page_works_while_currently_edited_page_is_full(
        card: Card, document_light_3: DocumentFixture):
    document_light_3 = document_light_3()
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


def test_apply_with_count_overflowing_page_adds_new_page(
        card: Card, document_light: DocumentFixture):
    document_light = document_light()
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


def test_apply_with_count_overflowing_page_adds_cards_to_next_page_with_empty_slots(
        card: Card, document_light_3: DocumentFixture):
    document_light_3 = document_light_3()
    capacity = document_light_3.page_layout.compute_page_card_capacity()
    count = capacity + 1
    pages = document_light_3.pages
    action = ActionAddCard(card, count)
    assert_that(action.apply(document_light_3), is_(same_instance(action)))
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(*[card_container_with(card, pages[0])]*capacity),
            contains_exactly(card_container_with(card, pages[1])),
            is_(empty()),
        )
    )
    assert_that(
        action.added_cards_to_existing_pages, contains_exactly(
            (0, capacity),
            (1, 1),
        ))
    assert_that(action.added_new_pages, is_(0))


def test_apply_emits_page_type_changed_when_page_type_changes(
        qtbot: QtBot, card: Card, document_light: DocumentFixture):
    document_light = document_light()
    with qtbot.wait_signal(document_light.page_type_changed, timeout=1000, check_params_cb=lambda x: x.row() == 0):
        ActionAddCard(card).apply(document_light)
    with qtbot.assert_not_emitted(document_light.page_type_changed):
        ActionAddCard(card).apply(document_light)


def test_undo_without_internal_saved_state_raises_exception(card: Card):
    action = ActionAddCard(card)
    assert_that(calling(action.undo).with_args(unittest.mock.MagicMock), raises(IllegalStateError))


def test_undo_deletes_pages_created_during_apply(card: Card, document_light: DocumentFixture):
    document_light = document_light()
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
            contains_exactly(card_container_with(card, pages[0])),
        )
    )
    assert_that(action.added_new_pages, is_(0))
    assert_that(action.added_cards_to_existing_pages, is_(empty()))


@pytest.mark.parametrize("oversized_first", [True, False])
def test_apply_does_not_create_pages_with_mixed_card_sizes(
        document_light: DocumentFixture, card: Card, oversized_card: Card, oversized_first: bool):
    document_light = document_light()
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


def test_apply_does_not_overfill_oversized_pages(document_light: DocumentFixture, oversized_card: Card):
    document_light = document_light()
    ActionAddCard(oversized_card, 7).apply(document_light)
    assert_that(document_light.rowCount(), is_(2))
    ActionAddCard(oversized_card, 2).apply(document_light)
    assert_that(document_light.rowCount(), is_(3))


@pytest.mark.parametrize("page_type", [PageType.REGULAR, PageType.OVERSIZED])
def test_apply_only_emits_page_type_changed_signal_if_changed(
        qtbot: QtBot, document_light: DocumentFixture, card: Card, oversized_card: Card, page_type: PageType):
    document_light = document_light()
    added_card = oversized_card if page_type == PageType.OVERSIZED else card

    with qtbot.wait_signal(document_light.page_type_changed):
        ActionAddCard(added_card).apply(document_light)
    with qtbot.assertNotEmitted(document_light.page_type_changed):
        ActionAddCard(added_card).apply(document_light)
    assert_that(document_light.pages[0].page_type(), is_(page_type))


def test_undo_works_when_apply_searched_over_multiple_full_pages_for_free_slot(
        document_light: DocumentFixture, card: Card):
    """
    A ValueError (including a SegmentationFault) occurred in undo() when
    - apply() had to search over multiple full pages,
    - then appended a new page
    - placed the card on that page
    - And then the action was undone.
    """
    document_light = document_light()
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
