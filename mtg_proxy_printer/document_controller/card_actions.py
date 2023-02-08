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

import functools
import itertools
import math
import typing

from mtg_proxy_printer.model.carddb import Card
if typing.TYPE_CHECKING:
    from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.document_page import CardContainer
from ._interface import DocumentAction, IllegalStateError, Self
from .page_actions import ActionNewPage, ActionRemovePage
from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger
__all__ = [
    "ActionAddCard",
    "ActionRemoveCards",
]


class ActionAddCard(DocumentAction):
    """
    Add an amount of copies of a card to a document page. If the count exceeds the available space on that page,
    distribute the remainder across free spots on later pages or append new pages to the document end.
    """

    COMPARISON_ATTRIBUTES = ["card", "count", "added_new_pages", "added_cards_to_existing_pages"]

    def __init__(self, card: Card, count: int = 1):
        self.card = card
        self.count = count
        self.added_new_pages: int = 0
        self.first_added_page: int = 0
        self.added_cards_to_existing_pages: typing.List[typing.Tuple[int, int]] = []

    def apply(self, document: "Document") -> Self:
        """
        Adds the given card count times to the currently edited page. If count is greater than the number of
        free slots on that page, add the remaining card copies to free slots in subsequent pages.
        If that is insufficient, add and fill new pages at the document end to fulfil the required copies.
        """
        copies = self.count  # Copy the count, because the value is mutated
        page_capacity_for_card = document.page_layout.compute_page_card_capacity(self.card.requested_page_type())
        current_page_position = document.find_page_list_index(document.currently_edited_page)
        if len(document.currently_edited_page) < page_capacity_for_card \
                and document.currently_edited_page.accepts_card(self.card):
            copies -= (added_cards := self.add_card_to_page(document, current_page_position, self.card, copies))
            if added_cards:
                self.added_cards_to_existing_pages.append((current_page_position, added_cards))
            logger.debug(f"Added {added_cards} cards to page {current_page_position}. Remaining to add: {copies}")
        current_page_position += 1
        while copies > 0 and current_page_position < document.rowCount():
            if document.pages[current_page_position].accepts_card(self.card):
                copies -= (added_cards := self.add_card_to_page(document, current_page_position, self.card, copies))
                if added_cards:
                    self.added_cards_to_existing_pages.append((current_page_position, added_cards))
                logger.debug(f"Added {added_cards} cards to page {current_page_position}. Remaining to add: {copies}")
            current_page_position += 1
        if copies > 0:
            self.added_new_pages = math.ceil(copies/page_capacity_for_card)
            logger.debug(
                f"No further empty slots found. Appending {self.added_new_pages} new pages to the document, "
                f"to fit the remaining {copies} copies.")
            ActionNewPage(count=self.added_new_pages).apply(document)
        if copies > 0:
            self.first_added_page = current_page_position
        while copies > 0:
            # Here, the individual cards don’t need to be tracked, as the whole pages get deleted on undo.
            copies -= (added_cards := self.add_card_to_page(document, current_page_position, self.card, copies))
            logger.debug(f"Added {added_cards} cards to page {current_page_position}. Remaining to add: {copies}")
            current_page_position += 1
        return super().apply(document)

    @staticmethod
    def add_card_to_page(document: "Document", page_number: int, card: Card, count: int = 1) -> int:
        """
        Adds the given card up to count times to the given page. Returns the number of cards actually added.
        Only adds cards up to the page capacity, so may add less than count cards, if that would overflow the page.
        """
        page_index = document.index(page_number, 0)
        page = document.pages[page_number]
        page_card_count = len(page)
        # Not using the current page’s page type, because UNDETERMINED pages overestimate the capacity when adding
        # oversized pages. Using the requested page type from the Card object is fine, because this method is only
        # called, if the given card fits on the given page.
        page_capacity = document.page_layout.compute_page_card_capacity(card.requested_page_type())
        first_index, last_index = page_card_count, page_card_count + count - 1
        if last_index >= page_capacity:
            last_index = page_capacity - 1
        cards_inserted = last_index - first_index + 1
        if not cards_inserted:
            logger.debug(f"Trying to add {count} cards into full page {page_number}. Doing nothing")
            return 0
        document.beginInsertRows(page_index, first_index, last_index)
        old_page_type = page.page_type()
        page += (CardContainer(page, card) for _ in range(cards_inserted))
        logger.debug(f"After insert, page contains {len(page)} images.")
        document.endInsertRows()
        if old_page_type != (new_page_type := page.page_type()):
            logger.debug(f"Page type of page {page_number} changed from {old_page_type} to {new_page_type}")
            document.page_type_changed.emit(page_index)
        logger.debug(f'Added {cards_inserted} × "{card.name}" to page {page_number}')
        return cards_inserted

    def undo(self, document: "Document") -> Self:
        if not self.added_new_pages and not self.added_cards_to_existing_pages:
            raise IllegalStateError("No cards added to undo")
        if self.added_new_pages:  # Drop all appended pages, implicitly removing all cards on them
            ActionRemovePage(document.rowCount() - self.added_new_pages, count=self.added_new_pages).apply(document)
        for page_number, count in self.added_cards_to_existing_pages:
            cards_on_page = len(document.pages[page_number])
            # Cards are always appended when filling a page via this action. So remove the last count cards will remove
            # the cards added during apply().
            ActionRemoveCards(
                range(cards_on_page-count, cards_on_page),
                page_number
            ).apply(document)

        self.added_new_pages = self.first_added_page = 0
        self.added_cards_to_existing_pages.clear()
        return self

    @functools.cached_property
    def as_str(self):
        if len(self.added_cards_to_existing_pages) == 1:
            # Cards added to a single existing page
            target = f"to page {self.added_cards_to_existing_pages[0][0]+1}"
        elif self.first_added_page:
            # Cards added to a single new page
            target = f"to page {self.first_added_page+1}"
        else:
            # Cards added to multiple existing and/or new pages
            pages = itertools.chain(
                ((page + 1) for page, _ in self.added_cards_to_existing_pages),  # Existing pages, can be empty
                range(self.first_added_page, self.first_added_page+self.added_new_pages)  # New pages, can be empty
            )
            page_ranges = ActionRemoveCards.to_list_of_ranges(pages)
            # Human-readable representation: pages are comma-separated,
            # with consecutive values collapsed into hyphen-separated ranges like lower-upper
            formatted_pages = ", ".join(
                (f"{lower}-{upper}" if lower < upper else f"{lower}") for lower, upper in page_ranges)
            target = f"across pages {formatted_pages}"
        return f'Add {self.count} × {self.card.display_string()} {target}'


class ActionRemoveCards(DocumentAction):
    """Deletes one or more cards from a page. The cards are given as an ascendingly sorted sequence of array indices."""

    COMPARISON_ATTRIBUTES = ["card_ranges_to_remove", "page_number", "removed_cards"]

    def __init__(self, cards_to_remove: typing.Sequence[int], page_number: int = None):
        if not cards_to_remove:
            raise ValueError("Parameter cards_to_remove must not be empty")
        self.card_ranges_to_remove = self.to_list_of_ranges(cards_to_remove)
        self.page_number = page_number
        self.removed_cards: typing.List[typing.List[CardContainer]] = []

    def apply(self, document: "Document") -> Self:
        if self.page_number is None:
            self.page_number = document.find_page_list_index(document.currently_edited_page)
        page_index = document.index(self.page_number, 0)
        page = document.pages[self.page_number]
        old_page_type = page.page_type()
        for lower, upper in reversed(self.card_ranges_to_remove):
            document.beginRemoveRows(page_index, lower, upper)
            self.removed_cards.append(page[lower:upper+1])
            del page[lower:upper+1]
            document.endRemoveRows()
        self.removed_cards.reverse()
        if page.page_type() != old_page_type:
            document.page_type_changed.emit(document.index(self.page_number, 0))
        return super().apply(document)

    def undo(self, document: "Document") -> Self:
        if self.page_number is None:
            raise IllegalStateError("page_number is None")
        page = document.pages[self.page_number]
        page_index = document.index(self.page_number, 0)
        for (begin, end), cards in zip(self.card_ranges_to_remove, self.removed_cards):
            document.beginInsertRows(page_index, begin, end)
            for card in reversed(cards):
                page.insert(begin, card)
            document.endInsertRows()
        self.removed_cards.clear()
        return self

    @staticmethod
    def to_list_of_ranges(sequence: typing.Iterable[int]) -> typing.List[typing.Tuple[int, int]]:
        ranges: typing.List[typing.Tuple[int, int]] = []
        sequence = itertools.chain(sequence, (sentinel := object(),))
        lower = upper = next(sequence)
        for item in sequence:
            if item is sentinel or upper != item-1:
                ranges.append((lower, upper))
                lower = upper = item
            else:
                upper = item
        return ranges

    @functools.cached_property
    def as_str(self):
        return f"Remove {sum(upper-lower+1 for lower, upper in self.card_ranges_to_remove)} " \
               f"from page {self.page_number+1}"
