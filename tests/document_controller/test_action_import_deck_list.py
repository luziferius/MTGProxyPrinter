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

import itertools
import math
import typing

from mtg_proxy_printer.units_and_sizes import PageType
from mtg_proxy_printer.document_controller import IllegalStateError
from mtg_proxy_printer.document_controller.page_actions import ActionRemovePage
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard
from mtg_proxy_printer.document_controller.import_deck_list import ActionImportDeckList

import pytest
from hamcrest import *

from .helpers import append_new_card_in_page, create_card, card_container_with

T = typing.TypeVar("T")


def split_iterable(iterable: typing.Iterable[T], chunk_size: int, /) -> typing.Iterable[typing.Tuple[T, ...]]:
    """Split the given iterable into chunks of size chunk_size. Does not add padding values to the last item."""
    iterable = iter(iterable)
    return iter(lambda: tuple(itertools.islice(iterable, chunk_size)), ())


@pytest.mark.parametrize("card_count", [1, 9, 10, 11, 100])
def test_apply_appends_cards(document_light, card_count: int):
    page_capacity = document_light.page_layout.compute_page_card_capacity(PageType.REGULAR)
    expected_pages = math.ceil(card_count/page_capacity)
    pages = document_light.pages
    cards = [create_card(f"Card {number}") for number in range(1, card_count+1)]
    action = ActionImportDeckList(cards, False)
    action.apply(document_light)
    assert_that(pages, has_length(expected_pages))
    cards_per_page = split_iterable(cards, page_capacity)
    for cards_on_page, page in zip(cards_per_page, pages):
        assert_that(
            page,
            contains_exactly(
                *[card_container_with(card, page) for card in cards_on_page]
            )
        )


def test_apply_does_not_create_mixed_size_page(document_light):
    pages = document_light.pages
    existing_card = append_new_card_in_page(pages[0], "Card")
    new_card = create_card("New", True)
    action = ActionImportDeckList([new_card], False)
    action.apply(document_light)
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(existing_card, pages[0])
            ),
            contains_exactly(
                card_container_with(new_card, pages[1])
            ),
        )
    )


def test_apply_raises_exception_if_action_list_is_not_empty(document_light):
    action = ActionImportDeckList([], False)
    action.actions.append(ActionAddCard(create_card("Card")))
    assert_that(calling(action.apply).with_args(document_light), raises(IllegalStateError))


@pytest.mark.parametrize("new_card_is_oversized", [False, True])
def test_apply_clears_document_if_enabled(qtbot, document_light, new_card_is_oversized: bool):
    """
    The new card should be placed on the first page, regardless of size compared to the existing card
    """
    pages = document_light.pages
    append_new_card_in_page(pages[0], "Card")
    new_card = create_card("New", new_card_is_oversized)
    action = ActionImportDeckList([new_card], True)
    action.apply(document_light)
    assert_that(pages, contains_exactly(has_length(1)))
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(new_card, pages[0])  # apply() implicitly creates a new page in the pages list
            )
        )
    )
    assert_that(
        action.actions,
        contains_exactly(
            instance_of(ActionRemovePage),
            instance_of(ActionAddCard),
        )

    )


@pytest.mark.parametrize("card_count", [1, 9, 10, 11, 100])
def test_undo_removes_created_pages(document_light, card_count):
    pages = document_light.pages
    cards = [create_card(f"Card {number}") for number in range(1, card_count+1)]
    action = ActionImportDeckList(cards, False)
    action.actions += [ActionAddCard(card).apply(document_light) for card in cards]
    page_capacity = document_light.page_layout.compute_page_card_capacity(PageType.REGULAR)
    expected_pages = math.ceil(card_count/page_capacity)
    assert_that(pages, has_length(expected_pages))
    assert_that(pages, contains_exactly(*[is_not(empty())]*expected_pages))
    action.undo(document_light)
    assert_that(
        pages,
        contains_exactly(
            is_(empty())
        )
    )
