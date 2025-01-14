# Copyright (C) 2020-2024 Thomas Hess <thomas.hess@udo.edu>
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

import pytest
from hamcrest import *

from mtg_proxy_printer.units_and_sizes import PageType, CardSizes
from mtg_proxy_printer.model.carddb import CardList
from mtg_proxy_printer.model.document_page import Page
from mtg_proxy_printer.document_controller import IllegalStateError
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage
from mtg_proxy_printer.document_controller.shuffle_document import ActionShuffleDocument

from .helpers import append_new_card_in_page

REGULAR = CardSizes.REGULAR
OVERSIZED = CardSizes.OVERSIZED


def cards_on_page(page: Page) -> CardList:
    return [container.card for container in page]


def test_init_creates_nonempty_seed():
    action = ActionShuffleDocument()
    assert_that(action.random_seed, all_of(instance_of(bytes), is_not(empty())))


def test_apply(qtbot, document_light):
    action = ActionShuffleDocument()
    action.random_seed = b"1"
    page = document_light.pages[0]
    append_new_card_in_page(page, "Card 1")
    append_new_card_in_page(page, "Card 2")
    append_new_card_in_page(page, "Card 3")
    old_page_content = cards_on_page(page)
    card_count = len(old_page_content)
    assert_that(old_page_content, contains_exactly(
        has_property("name", equal_to("Card 1")),
        has_property("name", equal_to("Card 2")),
        has_property("name", equal_to("Card 3")),
    ))
    with qtbot.wait_signals([document_light.dataChanged] * card_count, timeout=1000):
        action.apply(document_light)
    new_page_content = cards_on_page(page)
    assert_that(new_page_content, contains_inanyorder(*old_page_content))
    assert_that(new_page_content, not_(contains_exactly(*old_page_content)))


@pytest.mark.parametrize("seed, order, card_names", [
    (b"a", (0, 1), ("Card 1", "Card 2")),  # This seed keeps the original order
    (b"b", (1, 0), ("Card 2", "Card 1")),  # This one swaps the cards
])
def test_apply_swaps_cards_across_pages(document_light, seed, order, card_names):
    def page_matcher(name: str):
        return contains_exactly(has_property("card", has_property("name", name)))

    ActionNewPage().apply(document_light)
    append_new_card_in_page(document_light.pages[0], "Card 1")
    append_new_card_in_page(document_light.pages[1], "Card 2")
    action = ActionShuffleDocument()
    action.random_seed = seed
    action.apply(document_light)
    assert_that(action.shuffle_order, has_entry(equal_to(PageType.REGULAR), contains_exactly(*order)))
    assert_that(
        document_light.pages,
        contains_exactly(
            *map(page_matcher, card_names)
        )
    )


def test_apply_does_not_create_mixed_pages(document_light):
    def page_matcher(names):
        return contains_inanyorder(
            *map(lambda name: has_property("card", has_property("name", name)), names))

    ActionNewPage().apply(document_light)
    append_new_card_in_page(document_light.pages[0], "Card 1", REGULAR)
    append_new_card_in_page(document_light.pages[0], "Card 2", REGULAR)
    append_new_card_in_page(document_light.pages[0], "Card 3", REGULAR)
    append_new_card_in_page(document_light.pages[1], "Oversized 1", OVERSIZED)
    append_new_card_in_page(document_light.pages[1], "Oversized 2", OVERSIZED)

    regular_card_names = ["Card 1", "Card 2", "Card 3"]
    oversized_card_names = ["Oversized 1", "Oversized 2"]
    for _ in range(1000):
        action = ActionShuffleDocument()
        action.apply(document_light)
        assert_that(
            document_light.pages,
            contains_exactly(
                page_matcher(regular_card_names),
                page_matcher(oversized_card_names)
            )
        )


def test_apply_with_existing_state_raises_exception(document_light):
    action = ActionShuffleDocument()
    action.shuffle_order[PageType.REGULAR] = [0]
    assert_that(calling(action.apply).with_args(document_light), raises(IllegalStateError))


def test_undo_reorders_cards(qtbot, document_light):
    page = document_light.pages[0]
    append_new_card_in_page(page, "Card 3")
    append_new_card_in_page(page, "Card 2")
    append_new_card_in_page(page, "Card 1")
    action = ActionShuffleDocument()
    action.shuffle_order[PageType.REGULAR] = [2, 1, 0]
    action.undo(document_light)
    assert_that(action.shuffle_order, is_(empty()))
    assert_that(
        cards_on_page(page), contains_exactly(
            has_property("name", "Card 1"),
            has_property("name", "Card 2"),
            has_property("name", "Card 3"),
        )
    )


def test_second_apply_produces_same_order(qtbot, document_light):
    action = ActionShuffleDocument()
    action.random_seed = b"1"
    page = document_light.pages[0]
    append_new_card_in_page(page, "Card 1")
    append_new_card_in_page(page, "Card 2")
    append_new_card_in_page(page, "Card 3")
    old_page_content = cards_on_page(page)
    card_count = len(old_page_content)
    with qtbot.wait_signals([document_light.dataChanged] * card_count, timeout=1000):
        action.apply(document_light)
    new_page_content = cards_on_page(page)
    with qtbot.wait_signals([document_light.dataChanged] * card_count, timeout=1000):
        action.undo(document_light)
    assert_that(cards_on_page(page), contains_exactly(*old_page_content), "Setup failed: undo() broken")
    with qtbot.wait_signals([document_light.dataChanged] * card_count, timeout=1000):
        action.apply(document_light)
    assert_that(cards_on_page(page), contains_exactly(*new_page_content), "Second apply() produced different order")
