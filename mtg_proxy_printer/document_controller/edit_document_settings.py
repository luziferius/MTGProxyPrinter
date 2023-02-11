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

import copy
import typing

from ._interface import DocumentAction, ActionList, Self
from .move_cards import ActionMoveCards
from .page_actions import ActionNewPage
from mtg_proxy_printer.logger import get_logger

from mtg_proxy_printer.units_and_sizes import PageType
from mtg_proxy_printer.model.document_loader import PageLayoutSettings

if typing.TYPE_CHECKING:
    from mtg_proxy_printer.model.document import Document

logger = get_logger(__name__)
del get_logger
__all__ = [
    "ActionEditDocumentSettings",
]


class ActionEditDocumentSettings(DocumentAction):
    """Modify the document settings."""

    COMPARISON_ATTRIBUTES = ["new_settings", "old_settings", "reflow_actions"]

    def __init__(self, new_settings: PageLayoutSettings):
        if new_settings.compute_page_card_capacity(PageType.OVERSIZED) < 1:
            raise ValueError("New document settings must allow at least one card per page")
        self.new_settings = copy.copy(new_settings)
        self.old_settings: typing.Optional[PageLayoutSettings] = None
        self.reflow_actions: ActionList = []

    def apply(self, document: "Document") -> Self:
        self.old_settings = document.page_layout
        document.page_layout = self.new_settings
        if self.old_settings != self.new_settings:
            document.page_layout_changed.emit(self.new_settings)
        old_capacities = self.old_settings.compute_page_card_capacity(PageType.REGULAR), \
            self.old_settings.compute_page_card_capacity(PageType.OVERSIZED)
        new_capacities = self.new_settings.compute_page_card_capacity(PageType.REGULAR), \
            self.new_settings.compute_page_card_capacity(PageType.OVERSIZED)
        if new_capacities < old_capacities:
            self._reflow_document(document)
        return super().apply(document)

    def _reflow_document(self, document: "Document"):
        self._reflow_pages_of_type(document, PageType.REGULAR)
        self._reflow_pages_of_type(document, PageType.OVERSIZED)

    def _reflow_pages_of_type(self, document: "Document", page_type: PageType):
        pages = document.pages
        layout = document.page_layout
        page_capacity = layout.compute_page_card_capacity(page_type)

        current_index = -1
        while current_index < document.rowCount()-1:
            current_index += 1
            current_page = pages[current_index]
            if not current_page.accepts_card(page_type):
                continue
            cards_on_page = len(current_page)
            if (excess_cards := cards_on_page - page_capacity) > 0:
                target_index = self._find_next_page_accepting(document, page_type, current_index)
                if target_index is None or excess_cards >= page_capacity:
                    # There is no fitting page or there are enough cards to fill at least an entire page.
                    # In both cases, insert a blank page to take these cards
                    target_index = current_index + 1
                    self.reflow_actions.append(ActionNewPage(target_index).apply(document))

                action = ActionMoveCards(current_index, range(page_capacity, cards_on_page), target_index)
                self.reflow_actions.append(action.apply(document))

    @staticmethod
    def _find_next_page_accepting(document: "Document", page_type: PageType, index: int) -> typing.Optional[int]:
        index += 1
        for found_index, page in enumerate(document.pages[index:], start=index):
            if page.accepts_card(page_type):
                return found_index
        return None

    def undo(self, document: "Document") -> Self:
        document.page_layout = self.old_settings
        if self.old_settings != self.new_settings:
            document.page_layout_changed.emit(self.old_settings)
        for action in reversed(self.reflow_actions):
            action.undo(document)
        self.old_settings = None
        self.reflow_actions.clear()
        return self

    @property
    def as_str(self):
        return "Update document settings"
