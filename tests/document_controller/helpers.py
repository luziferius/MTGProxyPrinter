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


"""
This module contains an assortment of small helper functions used in the tests for the document controller
"""
import itertools

import hamcrest.core.base_matcher
from hamcrest import has_properties, same_instance, all_of, instance_of, assert_that, is_, equal_to, has_property

from mtg_proxy_printer.model.card import MTGSet, Card, AnyCardType
from mtg_proxy_printer.model.document_page import CardContainer, Page
from mtg_proxy_printer.units_and_sizes import CardSizes, CardSize

__all__ = [
    "append_new_pages",
    "verify_page_index_cache_is_valid",
    "card_container_with",
    "card_container_with_name",
    "append_new_card_in_page",
    "insert_card_in_page",

]


def append_new_pages(document, count: int):
    for _ in range(count):
        document.pages.append(Page())
    document.recreate_page_index_cache()


def verify_page_index_cache_is_valid(document):
    expected_index = {id(page): index for index, page in enumerate(document.pages)}
    assert_that(
        document.page_index_cache,
        is_(equal_to(expected_index)),
        "Index of page id to page number not updated properly"
    )


def card_container_with(card: AnyCardType, parent: Page):
    """Hamcrest matcher for a CardContainer."""
    if not isinstance(card, hamcrest.core.base_matcher.BaseMatcher):
        card = same_instance(card)
    return all_of(
        instance_of(CardContainer),
        has_properties({
            "card": card,
            "parent": same_instance(parent)
        })
    )


def card_container_with_name(name: str, parent: Page):
    """Hamcrest matcher for a CardContainer, validating the card only via the given name."""
    return all_of(
        instance_of(CardContainer),
        has_properties({
            "card": has_property("name", equal_to(name)),
            "parent": equal_to(parent),
        })
    )


def append_new_card_in_page(page: Page, name: str, size: CardSize = CardSizes.REGULAR) -> Card:
    """Appends a new card with the given name and size to the given page, returning the Card"""
    card = Card(name, MTGSet("", ""), "", "", "", True, "", "", True, size, 0, False, None)
    page.append(card)
    return card


def insert_card_in_page(page: Page, card: Card, count: int = 1):
    """Inserts the given card count times into the given page."""
    page += itertools.repeat(card, count)
