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

from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.units_and_sizes import PageType
from ._interface import DocumentAction, IllegalStateError, ActionList, Self
from .page_actions import ActionRemovePage
from .move_cards import ActionMoveCards

from mtg_proxy_printer.logger import get_logger


logger = get_logger(__name__)
del get_logger
__all__ = [
    "ActionCompactDocument",
]


class ActionCompactDocument(DocumentAction):
    """
    Compacts a document by filling as many empty slots as possible on pages that are not at the end of the document.

    Scans the document for pages that are not completely filled and for each such page,
    moves cards from the last page with items to it.
    This fills all (but the last) pages up to the capacity limit to help reduce possible waste during printing.
    """
    COMPARISON_ATTRIBUTES = ["actions"]

    def __init__(self):
        self.actions: ActionList = []

    def apply(self, document: Document) -> Self:
        if self.actions:
            raise IllegalStateError("Cannot apply action twice")
        if document.rowCount() <= 1:  # Can not compact an empty document or a document with a single empty page.
            return self
        logger.info("Compacting document.")
        self._compact_pages_of_type(document, PageType.REGULAR)
        self._compact_pages_of_type(document, PageType.OVERSIZED)
        if not document.pages[-1]:
            logger.debug("Determining empty pages")
            first = last = document.rowCount() - 1
            for page in reversed(document.pages[1:-1]):
                if not page:
                    first -= 1
            logger.debug(f"Removing empty pages {first} - {last}")
            if count := last-first+1:
                self.actions.append(ActionRemovePage(first, count).apply(document))
        logger.info("Compacting done.")
        return super().apply(document)

    def _compact_pages_of_type(self, document, page_type: PageType):
        maximum_cards_per_page = document.page_layout.compute_page_card_capacity(page_type)
        # The algorithm is allowed to place cards on empty pages, so explicitly state the type to skip
        to_skip_type = PageType.OVERSIZED if page_type is PageType.REGULAR else PageType.REGULAR
        last_index = document.rowCount() - 1
        for current_index, current_page in enumerate(document.pages[:-1]):  # Can never add images to the last page
            if current_page.page_type() is to_skip_type:
                continue
            if cards_to_add := maximum_cards_per_page - len(current_page):
                logger.debug(f"Found {cards_to_add} empty slots on page {current_index}")
                while cards_to_add and current_index < last_index:
                    page_to_draw_from = document.pages[last_index]
                    if page_to_draw_from.page_type() is not page_type:
                        last_index -= 1
                        continue
                    cards_to_take = min(len(page_to_draw_from), cards_to_add)
                    action = ActionMoveCards(last_index, range(cards_to_take), current_index)
                    self.actions.append(action.apply(document))
                    cards_to_add -= cards_to_take
                    logger.debug(f"Moved {cards_to_take} from page {last_index} to page {current_index}. "
                                 f"Free slots in target: {maximum_cards_per_page-len(current_page)}")
                    if not page_to_draw_from:
                        logger.debug(f"Page {last_index} now empty.")
                        last_index -= 1
                    else:
                        logger.debug(f"Last page with cards now contains {len(document.pages[last_index])} cards.")
                if current_index == last_index:
                    logger.debug("No more pages available to take cards from. Finished.")
                    break

    def undo(self, document: Document) -> Self:
        logger.info("Undo compacting document.")
        for action in reversed(self.actions):
            action.undo(document)
        self.actions.clear()
        return self

    @functools.cached_property
    def as_str(self):
        last_action = self.actions[-1] if self.actions else None
        saved_pages = last_action.count if isinstance(last_action, ActionRemovePage) else 0
        return f"Compact document, removing {saved_pages} pages"
