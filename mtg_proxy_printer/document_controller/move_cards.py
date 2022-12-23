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

import itertools
import typing

from ._interface import DocumentAction, IllegalStateError
from mtg_proxy_printer.logger import get_logger

if typing.TYPE_CHECKING:
    from mtg_proxy_printer.model.document import Document

logger = get_logger(__name__)
del get_logger
__all__ = [
    "ActionMoveCards",
]


class ActionMoveCards(DocumentAction):
    """
    Moves a sequence of cards from a source page to a target page.
    """

    def __init__(self, source: int, cards_to_move: typing.Sequence[int], target: int):
        super().__init__()
        self.source_page = source
        self.target_page = target
        self.card_ranges_to_move = self._to_list_of_ranges(cards_to_move)

    def apply(self, document: "Document"):
        source_page = document.pages[self.source_page]
        target_page = document.pages[self.target_page]
        if not target_page.accepts_card(source_page[0].card.requested_page_type()):
            raise IllegalStateError(
                f"Can not move card requesting page type {source_page.page_type()} "
                f"onto a page with type {target_page.page_type()}"
            )
        source_index = document.index(self.source_page, 0)
        target_index = document.index(self.target_page, 0)

        destination_row = len(target_page)
        source_page_type = source_page.page_type()
        target_page_type = target_page.page_type()
        for source_row_first, source_row_last in reversed(self.card_ranges_to_move):
            document.beginMoveRows(source_index, source_row_first, source_row_last, target_index, destination_row)
            target_page[destination_row:destination_row] = source_page[source_row_first:source_row_last+1]
            del source_page[source_row_first:source_row_last+1]
            document.endMoveRows()
        if source_page.page_type() != source_page_type:
            document.page_type_changed.emit(source_index)
        if target_page.page_type() != target_page_type:
            document.page_type_changed.emit(target_index)
        return self

    def undo(self, document: "Document"):
        raise NotImplementedError("undo() not yet implemented")
        # return self

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

    def __eq__(self, other):
        return isinstance(other, ActionMoveCards) \
            and other.source_page == self.source_page \
            and other.target_page == self.target_page \
            and other.card_ranges_to_move == self.card_ranges_to_move
