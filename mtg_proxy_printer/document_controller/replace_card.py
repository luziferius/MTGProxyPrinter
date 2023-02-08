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
import typing

from PyQt5.QtCore import Qt

from mtg_proxy_printer.model.carddb import Card
from mtg_proxy_printer.model.card_list import PageColumns
if typing.TYPE_CHECKING:
    from mtg_proxy_printer.model.document_page import CardContainer
    from mtg_proxy_printer.model.document import Document

from ._interface import DocumentAction, Self, ActionList
from .card_actions import ActionRemoveCards, ActionAddCard

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger
__all__ = [
    "ActionReplaceCard",
]


class ActionReplaceCard(DocumentAction):
    """
    Replace a single card on a page with another one.
    """
    COMPARISON_ATTRIBUTES = ["card", "old_card", "page", "slot"]

    def __init__(self, new_card: Card, page: int, slot: int):
        self.card = new_card
        self.old_card: typing.Optional[Card] = None
        # The new card may have a different size than the old one. Most likely when the commander card of old
        # pre-constructed commander decks is swapped for the over-sized display card that was included in those decks.
        # In those cases, the swap may create a mixed-size page, which has to be mitigated. In those, and only those,
        # cases, the list below contains an ActionRemoveCard and ActionAddCard responsible for moving the size-changing
        # card onto an appropriate page.
        # It is fine to perform the size-changing swap in place, if the swapped card is the only card on the page.
        self.size_change_actions: ActionList = []
        self.page = page
        self.slot = slot

    def apply(self, document: "Document") -> Self:
        self.old_card = document.pages[self.page][self.slot].card
        self._replace_card_in_document_with(document, self.card)
        return super().apply(document)

    def undo(self, document: "Document") -> Self:
        if self.size_change_actions:
            logger.info("Undo card replacement that changed the card size")
            for action in reversed(self.size_change_actions):
                action.undo(document)
        else:
            self._replace_card_in_document_with(document, self.old_card)
        self.old_card = None
        self.size_change_actions.clear()
        return self

    def _replace_card_in_document_with(self, document: "Document", replacement: Card):
        rightmost_column = len(PageColumns)-1
        page_index = document.index(self.page, 0)
        top_left = document.index(self.slot, 0, page_index)
        bottom_right = top_left.siblingAtColumn(rightmost_column)
        container: "CardContainer" = top_left.internalPointer()
        previous_card_page_type = container.card.requested_page_type()
        new_card_page_type = replacement.requested_page_type()
        if document.rowCount(page_index) > 1 and previous_card_page_type != new_card_page_type:
            logger.info(f"New card has different size and other cards are present, moving the replacement away")
            self.size_change_actions.append(ActionRemoveCards((self.slot,), self.page).apply(document))
            self.size_change_actions.append(ActionAddCard(replacement).apply(document))
        else:
            container.card = replacement
            document.dataChanged.emit(top_left, bottom_right, (Qt.DisplayRole, Qt.EditRole, Qt.ToolTipRole))
            if previous_card_page_type != new_card_page_type:
                logger.info("New card has different size, but page is otherwise empty, changing page type…")
                document.page_type_changed.emit(page_index)

    @functools.cached_property
    def as_str(self):
        return f"Replace card {self.old_card.display_string()} on page {self.page+1} with {self.card.display_string()}"
