
import itertools
import random
import typing

from PyQt5.QtCore import Qt

from ._interface import DocumentAction, IllegalStateError, Self
from mtg_proxy_printer.model.carddb import Card
from mtg_proxy_printer.model.document import Document, Page, PageColumns
from mtg_proxy_printer.units_and_sizes import PageType

__all__ = [
    "ActionShuffleDocument",
]


class ActionShuffleDocument(DocumentAction):
    """
    Shuffle the cards in the current document.
    """
    COMPARISON_ATTRIBUTES = ["random_seed"]

    def __init__(self):
        super().__init__()
        self.random_seed = random.randbytes(64)
        self.shuffle_order: typing.Dict[PageType, typing.List[int]] = {}

    def apply(self, document: Document) -> Self:
        if self.shuffle_order:
            raise IllegalStateError("Cannot apply(). A previous shuffle order is already set")
        shuffler = random.Random(self.random_seed)
        for page_type in (PageType.REGULAR, PageType.OVERSIZED):
            self._shuffle_pages_of_type(document, shuffler, page_type)
        return self

    def _shuffle_pages_of_type(self, document: Document, shuffler: random.Random, page_type: PageType):
        model_indices = list(document.get_card_indices_of_type(page_type))
        cards: typing.List[typing.Tuple[int, Card]] = list(
            enumerate(index.internalPointer().card for index in model_indices)  # The index holds the card container
        )
        shuffler.shuffle(cards)
        for (_, card), model_index in zip(cards, model_indices):
            bottom_right = model_index.siblingAtColumn(PageColumns.Image)
            page: Page = model_index.parent().internalPointer()
            page[model_index.row()].card = card
            document.dataChanged.emit(model_index, bottom_right, (Qt.DisplayRole, Qt.EditRole, Qt.ToolTipRole))
        self.shuffle_order[page_type] = [old_position for old_position, _ in cards]

    def undo(self, document: Document) -> Self:
        for page_type in (PageType.REGULAR, PageType.OVERSIZED):
            self._undo_shuffle_of_type(document, page_type)
        self.shuffle_order.clear()
        return self

    def _undo_shuffle_of_type(self, document: Document, page_type: PageType):
        model_indices = list(zip(self.shuffle_order[page_type], document.get_card_indices_of_type(page_type)))
