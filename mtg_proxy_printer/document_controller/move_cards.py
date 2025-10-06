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
import enum
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
    "ActionMoveCardsBetweenPages",
    "ActionMoveCardsWithinPage",
]


class ActionMoveCardsBetweenPages(DocumentAction):
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


class CardMove(typing.NamedTuple):
    first: int
    last: int
    target_row: int
    moved_cards_count: int


class ActionMoveCardsWithinPage(DocumentAction):
    """Move a subset of cards on a page to another position within the same page."""

    def __init__(
            self, page: int, cards_to_move: Sequence[int],
            target_row: int | None, parent: QObject = None):
        """
        :param page: The page with cards, as integer page number (0-indexed)
        :param cards_to_move: The cards to move, as indices into the source Page. May be in any order. (0-indexed)
        :param target_row: The cards_to_move are inserted before that array index (0-indexed).
        """
        super().__init__(parent)
        self.page = page
        self.card_ranges_to_move = to_list_of_ranges(cards_to_move)
        self.target_row = target_row
        self.card_moves: list[CardMove] = []

    def _total_moved_cards(self) -> int:
        return sum(last-first+1 for first, last in self.card_ranges_to_move)

    def _get_card_move_ranges_without_zero_moves_at_ends(self, target_row: int, cards_on_page: int):
        card_ranges = self.card_ranges_to_move.copy()
        # Shortcut two special cases:
        # If the first row is selected and the target is before the first row, skip that move and move the target back
        # so that further moves put cards after the first block
        if target_row == (card_range := card_ranges[0])[0] == 0:
            target_row += card_range[1] - card_range[0] + 1
            del card_ranges[0]
        if not card_ranges:
            return [], target_row
        # If the last row is selected and the target is after the last row, skip that move and move the target forward
        # so that further moves put cards before the last block
        if target_row == (card_range := card_ranges[-1])[1] + 1 == cards_on_page:
            target_row -= card_range[1] - card_range[0] + 1
            del card_ranges[-1]
        return card_ranges, target_row

    def _compute_card_moves(self, document: "Document", page_index: QModelIndex):
        result: list[CardMove] = []
        card_ranges, target_row = self._get_card_move_ranges_without_zero_moves_at_ends(
            self._get_target_row(document, page_index), document.rowCount(page_index))
        if not card_ranges:
            return result

        source_offset = 0
        for first, last in card_ranges:
            moved_cards = last-first+1
            if first <= target_row <= last+1:
                # This batch of cards is currently at the correct location already.
                # The next range has to be inserted after this range, so move the target_row,
                # but no need to do anything further.
                target_row = last+1
                continue
            if last < target_row:
                # While processing batches before the target_row, moving cards to the back will move the next ranges
                # by that many cards to the front
                first -= source_offset
                last -= source_offset
                source_offset += moved_cards
            result.append(CardMove(first, last, target_row, moved_cards))
            if first > target_row:
                # When moving cards to the front, the target row moves back that many cards to keep the order stable
                target_row += moved_cards
        return result

    def apply(self, document: "Document") -> Self:
        super().apply(document)
        page_index = document.index(self.page, 0)
        page: Page = page_index.internalPointer()
        self.card_moves = self._compute_card_moves(document, page_index)
        for first, last, target_row, moved_cards_count in self.card_moves:  # type: int, int, int, int
            document.beginMoveRows(page_index, first, last, page_index, target_row)
            moving_cards = page[first:last+1]
            del page[first:last+1]
            # If cards were removed before the target row, the target shifts moved_cards_count slots to the front.
            target_row -= (last < target_row) * moved_cards_count
            page[target_row:target_row] = moving_cards
            document.endMoveRows()
        return self

    def _get_target_row(self, document: "Document", page_index: QModelIndex):
        return self.target_row if isinstance(self.target_row, int) else document.rowCount(page_index)

    def undo(self, document: "Document") -> Self:
        super().undo(document)
        page_index = document.index(self.page, 0)
        page: Page = page_index.internalPointer()
        card_moves = list(reversed(self.card_moves))
        for target_row, _, first, moved_cards_count in card_moves:  # type: int, int, int, int
            first -= (first > target_row) * moved_cards_count
            last = first + moved_cards_count
            document.beginMoveRows(page_index, first, last-1, page_index, target_row + (first < target_row) * moved_cards_count)
            moving_cards = page[first:last]
            del page[first:last]
            # If cards were removed before the target row, the target shifts moved_cards_count slots to the front.
            page[target_row:target_row] = moving_cards
            document.endMoveRows()
        return self

    @functools.cached_property
    def as_str(self):
        page = self.page+1
        count = self._total_moved_cards()
        return self.tr(
            "Reorder %n card(s) on page {page}",
            "Undo/redo tooltip text", count
        ).format(page=page)
