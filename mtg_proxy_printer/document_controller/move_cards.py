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
import typing

from PyQt5.QtCore import QModelIndex

from ._interface import DocumentAction, IllegalStateError, Self
from mtg_proxy_printer.logger import get_logger

if typing.TYPE_CHECKING:
    from mtg_proxy_printer.model.document_page import Page
    from mtg_proxy_printer.model.document import Document

logger = get_logger(__name__)
del get_logger
__all__ = [
    "ActionMoveCards",
]


class ActionMoveCards(DocumentAction):
    """
    Moves a sequence of cards from a source page to a target page.
    Values of consecutive card ranges are inclusive.
    """

    COMPARISON_ATTRIBUTES = ["source_page", "target_page", "card_ranges_to_move"]

    def __init__(self, source: int, cards_to_move: typing.Sequence[int], target: int):
        self.source_page = source
        self.target_page = target
        self.card_ranges_to_move = self._to_list_of_ranges(cards_to_move)

    def apply(self, document: "Document") -> Self:
        source_page = document.pages[self.source_page]
        target_page = document.pages[self.target_page]
        if not target_page.accepts_card(source_page[0].card.requested_page_type()):
            raise IllegalStateError(
                f"Can not move card requesting page type {source_page.page_type()} "
                f"onto a page with type {target_page.page_type()}"
            )
        source_index = document.index(self.source_page, 0)
        target_index = document.index(self.target_page, 0)
        source_page_type = source_page.page_type()
        target_page_type = target_page.page_type()

        destination_row = len(target_page)
        for source_row_first, source_row_last in reversed(self.card_ranges_to_move):
            self._move_cards_to_target_page(
                document, source_index, source_page, source_row_first, source_row_last, target_index,
                target_page, destination_row
            )
        if source_page.page_type() != source_page_type:
            document.page_type_changed.emit(source_index)
        if target_page.page_type() != target_page_type:
            document.page_type_changed.emit(target_index)
        return super().apply(document)

    @staticmethod
    def _move_cards_to_target_page(
            document: "Document",
            source_index: QModelIndex, source_page: "Page", source_row_first: int, source_row_last: int,
            target_index: QModelIndex, target_page: "Page", destination_row: int):
        document.beginMoveRows(source_index, source_row_first, source_row_last, target_index, destination_row)
        target_page[destination_row:destination_row] = source_page[source_row_first:source_row_last + 1]
        for item in source_page[source_row_first:source_row_last + 1]:
            item.parent = target_page
        del source_page[source_row_first:source_row_last + 1]
        document.endMoveRows()

    def undo(self, document: "Document") -> Self:
        source_page = document.pages[self.target_page]  # Swap source and target page for undo
        target_page = document.pages[self.source_page]
        source_index = document.index(self.target_page, 0)  # Same for the model index
        target_index = document.index(self.source_page, 0)
        source_page_type = source_page.page_type()
        target_page_type = target_page.page_type()

        # During apply(), all cards were appended to the target page. During undo, the ranges are extracted in order
        # from the source page. Thus, the first source row is now constant across all ranges
        source_row_first = len(source_page) - self._total_moved_cards()
        for target_row_first, target_row_last in self.card_ranges_to_move:
            source_row_last = source_row_first + target_row_last - target_row_first
            self._move_cards_to_target_page(
                document, source_index, source_page, source_row_first, source_row_last, target_index,
                target_page, target_row_first
            )

        if source_page.page_type() != source_page_type:
            document.page_type_changed.emit(source_index)
        if target_page.page_type() != target_page_type:
            document.page_type_changed.emit(target_index)
        return self

    @staticmethod
    def _to_list_of_ranges(sequence: typing.Sequence[int]) -> typing.List[typing.Tuple[int, int]]:
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

    def _total_moved_cards(self) -> int:
        return sum(last-first+1 for first, last in self.card_ranges_to_move)

    @functools.cached_property
    def as_str(self):
        return f"Move {sum(upper-lower+1 for lower, upper in self.card_ranges_to_move)} cards " \
               f"from page {self.source_page+1} to page {self.target_page+1}"
