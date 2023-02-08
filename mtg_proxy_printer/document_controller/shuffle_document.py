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

from random import Random
try:
    from random import randbytes
except ImportError:
    # Compatibility with Py 3.8
    from secrets import token_bytes as randbytes

import typing

from PyQt5.QtCore import Qt, QModelIndex

from ._interface import DocumentAction, IllegalStateError, Self
from mtg_proxy_printer.model.carddb import Card
from mtg_proxy_printer.model.card_list import PageColumns
from mtg_proxy_printer.model.document_page import CardContainer
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.units_and_sizes import PageType

__all__ = [
    "ActionShuffleDocument",
]

IndexedCards = typing.List[typing.Tuple[int, Card]]
ModelIndexList = typing.List[QModelIndex]


class ActionShuffleDocument(DocumentAction):
    """
    Shuffle the cards in the current document.
    """
    COMPARISON_ATTRIBUTES = ["random_seed"]

    def __init__(self):
        # The seed is created at instantiation time and ensures that two runs of apply() return a deterministic
        # order. This ensures that redoing the same action always returns the same result
        self.random_seed = randbytes(64)
        self.shuffle_order: typing.Dict[PageType, typing.List[int]] = {}

    def apply(self, document: Document) -> Self:
        if self.shuffle_order:
            raise IllegalStateError("Cannot apply(). A previous shuffle order is already set")
        shuffler = Random(self.random_seed)
        for page_type in (PageType.REGULAR, PageType.OVERSIZED):
            self._shuffle_pages_of_type(document, shuffler, page_type)
        return super().apply(document)

    def _shuffle_pages_of_type(self, document: Document, shuffler: Random, page_type: PageType):
        model_indices = list(document.get_card_indices_of_type(page_type))
        cards: IndexedCards = list(
            enumerate(index.internalPointer().card for index in model_indices)  # The index holds the card container
        )
        shuffler.shuffle(cards)
        self._swap_cards(document, model_indices, cards)
        self.shuffle_order[page_type] = [old_position for old_position, _ in cards]

    def undo(self, document: Document) -> Self:
        for page_type in (PageType.REGULAR, PageType.OVERSIZED):
            if page_type in self.shuffle_order:
                self._undo_shuffle_of_type(document, page_type)
        self.shuffle_order.clear()
        return self

    def _undo_shuffle_of_type(self, document: Document, page_type: PageType):
        model_indices = list(document.get_card_indices_of_type(page_type))
        cards: IndexedCards = list(zip(
            self.shuffle_order[page_type],
            (index.internalPointer().card for index in model_indices)  # The index holds the card container
        ))
        cards.sort()
        self._swap_cards(document, model_indices, cards)

    @staticmethod
    def _swap_cards(document: Document, model_indices: ModelIndexList, cards: IndexedCards):
        rightmost_column = len(PageColumns)-1
        for (_, card), model_index in zip(cards, model_indices):
            bottom_right = model_index.siblingAtColumn(rightmost_column)
            container: CardContainer = model_index.internalPointer()
            container.card = card
            document.dataChanged.emit(model_index, bottom_right, (Qt.DisplayRole, Qt.EditRole, Qt.ToolTipRole))

    @property
    def as_str(self):
        return "Shuffle document"
