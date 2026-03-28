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


from itertools import repeat

from hamcrest import *

from mtg_proxy_printer.units_and_sizes import PageType, CardSizes
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.document_controller import IllegalStateError
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage, ActionRemovePage
from mtg_proxy_printer.document_controller.compact_document import ActionCompactDocument
from mtg_proxy_printer.document_controller.move_cards import ActionMoveCardsBetweenPages

from tests.helpers import create_card
from .helpers import append_new_card_in_page, card_container_with

OVERSIZED = CardSizes.OVERSIZED
REGULAR = CardSizes.REGULAR


def test_apply_does_nothing_on_single_page_empty_document(document_light: Document):
    action = ActionCompactDocument().apply(document_light)
    assert_that(action.actions, is_(empty()))


def test_apply_raises_exception_if_called_twice(document_light: Document):
    ActionNewPage().apply(document_light)
    action = ActionCompactDocument().apply(document_light)
    assert_that(calling(action.apply).with_args(document_light), raises(IllegalStateError))


def test_apply_does_not_create_mixed_size_pages(document_light: Document):
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    normal = append_new_card_in_page(pages[0], "Normal", REGULAR)
    oversized = append_new_card_in_page(pages[1], "Oversized", OVERSIZED)
    action = ActionCompactDocument().apply(document_light)
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(normal, pages[0])
            ),
            contains_exactly(
                card_container_with(oversized, pages[1])
            )
        )
    )
    assert_that(action.actions, is_(empty()))


def test_apply_removes_trailing_empty_pages(document_light: Document):
    pages = document_light.pages
    ActionNewPage().apply(document_light)
    action = ActionCompactDocument().apply(document_light)
    assert_that(
        pages,
        contains_exactly(
            empty()
        )
    )
    assert_that(
        action.actions,
        contains_exactly(instance_of(ActionRemovePage))
    )


def test_compacting_document(document_light: Document):
    pages = document_light.pages
    card = create_card("Card", REGULAR)
    # Can be compacted to 4 pages, with the last having one free slot
    target_cards_per_page = document_light.page_layout.compute_page_card_capacity(PageType.REGULAR)
    pages_to_fill = 5
    cards_per_page = 7
    ActionNewPage(count=pages_to_fill-1).apply(document_light)
    for page in pages:
        document_light.set_currently_edited_page(page)
        ActionAddCard(card, count=cards_per_page).apply(document_light)
    assert_that(
        pages,
        contains_exactly(
            *(contains_exactly(
                *repeat(card_container_with(card, page), cards_per_page))
              for page in pages)
        ),
        "Setup failed"
    )

    action = ActionCompactDocument()
    action.apply(document_light)
    assert_that(
        action.actions,
        contains_exactly(
            *[instance_of(ActionMoveCardsBetweenPages)] * 4,
            instance_of(ActionRemovePage)
        )
    )
    assert_that(pages, has_length(4))
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(*repeat(card_container_with(card, pages[0]), target_cards_per_page)),
            contains_exactly(*repeat(card_container_with(card, pages[1]), target_cards_per_page)),
            contains_exactly(*repeat(card_container_with(card, pages[2]), target_cards_per_page)),
            contains_exactly(*repeat(card_container_with(card, pages[3]), target_cards_per_page-1)),
        )
    )


def test_compacting_document_with_regular_and_oversized_pages(document_light: Document):
    pages = document_light.pages
    ActionNewPage(count=3).apply(document_light)
    regular1 = append_new_card_in_page(pages[0], "Regular", REGULAR)
    oversized1 = append_new_card_in_page(pages[1], "Oversized", OVERSIZED)
    regular2 = append_new_card_in_page(pages[2], "Regular", REGULAR)
    oversized2 = append_new_card_in_page(pages[3], "Oversized", OVERSIZED)

    assert_that(document_light.rowCount(), is_(4))
    action = ActionCompactDocument().apply(document_light)
    assert_that(document_light.rowCount(), is_(2))

    assert_that(
        [page.page_type() for page in pages],
        contains_exactly(PageType.REGULAR, PageType.OVERSIZED),
        "Unexpectedly created a mixed-sizes page or left an empty page"
    )
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(regular1, pages[0]),
                card_container_with(regular2, pages[0])),
            contains_exactly(
                card_container_with(oversized1, pages[1]),
                card_container_with(oversized2, pages[1])),
        )
    )
    assert_that(
        action.actions,
        contains_exactly(
            *[instance_of(ActionMoveCardsBetweenPages)] * 2,
            instance_of(ActionRemovePage))
    )
