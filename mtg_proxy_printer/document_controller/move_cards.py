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

from collections.abc import Sequence
import functools
import typing

from PySide6.QtCore import QModelIndex, QObject

from mtg_proxy_printer.natsort import to_list_of_ranges
from ._interface import DocumentAction, IllegalStateError, Self
from mtg_proxy_printer.logger import get_logger
from .page_actions import ActionNewPage

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
    Moves a sequence of cards from a source page to a target page. By default, cards are appended.
    Values of consecutive card ranges are inclusive.
    """

    COMPARISON_ATTRIBUTES = ["source_page", "target_page", "card_ranges_to_move", "target_row", "insert_page_action"]

    def __init__(
            self, source: int, cards_to_move: Sequence[int],
            target_page: int, target_row: int = None, parent: QObject = None):
        """
        :param source: The source page, as integer page number (0-indexed)
        :param cards_to_move: The cards to move, as indices into the source Page. May be in any order. (0-indexed)
        :param target_page: The target page, as integer page number. (0-indexed)
        :param target_row: If given, the cards_to_move are inserted at that array index (0-indexed).
                           Existing cards in the target page at that index are pushed back.
                           None means "append". -1 means "0, but insert new page at target_page"
        """
        super().__init__(parent)
        if target_row == -1:
            target_row = None
            self.insert_page_action = ActionNewPage(target_page, parent=self)
        else:
            self.insert_page_action = None
        # When inserting a new page before the source page, add one to compensate
        self.source_page = source + (target_page < source and self.insert_page_action is not None)
        self.target_page = target_page
        self.target_row = target_row
        self.card_ranges_to_move = to_list_of_ranges(cards_to_move)

    def apply(self, document: "Document") -> Self:
        if self.insert_page_action is not None:
            self.insert_page_action.apply(document)
        source_page = document.pages[self.source_page]
        target_page = document.pages[self.target_page]
        source_page_type = source_page.page_type()
        target_page_type = target_page.page_type()
        if not target_page.accepts_card(source_page_type):
            raise IllegalStateError(
                f"Can not move card requesting page type {source_page_type} "
                f"onto a page with type {target_page_type}"
            )
        source_index = document.index(self.source_page, 0)
        target_index = document.index(self.target_page, 0)

        destination_row = len(target_page) if self.target_row is None else self.target_row
        in_page_move = self.source_page == self.target_page

        for source_row_first, source_row_last in reversed(self.card_ranges_to_move):
            if in_page_move and source_row_first <= destination_row <= source_row_last + 1:
                # Nothing to do. Cards already at the right location.
                # Offset +1: Cards are inserted before the given row, so moving card 0 to position 1 moves it *before*
                # the second card, thus not moving it at all.
                continue
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
        source_row_first = len(source_page) - self._total_moved_cards() if self.target_row is None else self.target_row
        for target_row_first, target_row_last in self.card_ranges_to_move:
            source_row_last = source_row_first + target_row_last - target_row_first
            self._move_cards_to_target_page(
                document, source_index, source_page, source_row_first, source_row_last, target_index,
                target_page, target_row_first
            )
        if self.insert_page_action is not None:
            self.insert_page_action.undo(document)
        if source_page.page_type() != source_page_type:
            document.page_type_changed.emit(source_index)
        if target_page.page_type() != target_page_type:
            document.page_type_changed.emit(target_index)
        return super().undo(document)

    def _total_moved_cards(self) -> int:
        return sum(last-first+1 for first, last in self.card_ranges_to_move)

    @functools.cached_property
    def as_str(self):
        source_page = self.source_page+1
        target_page = self.target_page+1
        count = self._total_moved_cards()
        return self.tr(
            "Move %n card(s) from page {source_page} to {target_page}",
            "Undo/redo tooltip text", count
        ).format(source_page=source_page, target_page=target_page)
