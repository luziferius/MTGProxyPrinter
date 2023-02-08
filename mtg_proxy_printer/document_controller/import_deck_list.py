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

if typing.TYPE_CHECKING:
    from mtg_proxy_printer.model.carddb import CardList
    from mtg_proxy_printer.model.document import Document

from ._interface import ActionList, DocumentAction, Self, IllegalStateError
from .page_actions import ActionRemovePage
from .card_actions import ActionAddCard

__all__ = [
    "ActionImportDeckList",
]


class ActionImportDeckList(DocumentAction):

    COMPARISON_ATTRIBUTES = ["cards", "clear_document", "actions"]

    def __init__(self, cards: "CardList", clear_document: bool):
        self.cards = cards
        self.clear_document = clear_document
        self.actions: ActionList = []

    def apply(self, document: "Document") -> Self:
        if self.actions:
            raise IllegalStateError("Cannot apply action twice")
        if self.clear_document:
            self.actions.append(ActionRemovePage(0, document.rowCount()).apply(document))
        for action in map(ActionAddCard, self.cards):
            self.actions.append(action.apply(document))
        return super().apply(document)

    def undo(self, document: "Document") -> Self:
        for action in reversed(self.actions):
            action.undo(document)
        self.actions.clear()
        return self

    def card_count(self) -> int:
        """Returns the number of cards added by this action"""
        return len(self.cards)

    @functools.cached_property
    def as_str(self):
        action = "Wipe document and import" if self.clear_document else "Import"
        return f"{action} a deck list containing {len(self.cards)} cards"
