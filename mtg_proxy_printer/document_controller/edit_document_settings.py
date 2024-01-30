# Copyright (C) 2020-2024 Thomas Hess <thomas.hess@udo.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import copy
import itertools
import typing

from ._interface import DocumentAction, ActionList, Self, split_iterable
from .card_actions import ActionRemoveCards
from .move_cards import ActionMoveCards
from .page_actions import ActionNewPage
from mtg_proxy_printer.logger import get_logger

from mtg_proxy_printer.units_and_sizes import PageType
from mtg_proxy_printer.model.document_loader import PageLayoutSettings

if typing.TYPE_CHECKING:
    from mtg_proxy_printer.model.document_page import Page
    from mtg_proxy_printer.model.document import Document

logger = get_logger(__name__)
del get_logger
__all__ = [
    "ActionEditDocumentSettings",
]


class PagePartition(typing.NamedTuple):
    page_type: PageType
    pages: typing.List["Page"]

    def size(self):
        return len(self.pages)


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
        page_partitions = self._partition_pages_by_accepting_card_size(document)
        for partition in page_partitions:  # type: int, PageType, typing.List[Page]
            self._reflow_partition(document, partition)

    @staticmethod
    def _partition_pages_by_accepting_card_size(document: "Document") -> typing.List[PagePartition]:
        """
        Partitions the document pages into consecutive lists of pages.
        Each partition only contains pages with exactly one page type (REGULAR or OVERSIZED) plus empty pages.
        Leading empty pages are ignored.
        """
        pages = document.pages
        first_populated_page = sum(1 for _ in itertools.takewhile(lambda page: not page, pages))
        if first_populated_page == len(pages):
            return []

        current_page_type = pages[first_populated_page].page_type()
        result: typing.List[PagePartition] = [PagePartition(current_page_type, [])]

        for page_index, page in enumerate(pages[first_populated_page:], start=first_populated_page):
            if page.accepts_card(current_page_type):
                # Empty pages accept any type of card, thus will be included in any partition
                result[-1].pages.append(page)
            else:
                # Here, the page type must have flipped between REGULAR and OVERSIZED, thus page_type() is safe to use
                current_page_type = page.page_type()
                result.append(PagePartition(current_page_type, [page]))
        return result

    def _reflow_partition(self, document: "Document", partition: PagePartition):
        start_index = document.find_page_list_index(partition.pages[0])
        end_index = start_index + partition.size()
        page_capacity = document.page_layout.compute_page_card_capacity(partition.page_type)
        # TODO: The algorithm currently isn't very optimized. This loop should insert new pages,
        #  if the excess exceeds some threshold.
        for page_index, page in enumerate(partition.pages[:-1], start=start_index):
            if (page_length := len(page)) > page_capacity:
                action = ActionMoveCards(page_index, range(page_capacity, page_length), page_index+1, 0)
                self.reflow_actions.append(action.apply(document))
        last_page = partition.pages[-1]
        if (page_length := len(last_page)) > page_capacity:
            excess = split_iterable((c.card for c in last_page[page_capacity:]), page_capacity)
            self.reflow_actions.append(ActionRemoveCards(range(page_capacity, page_length), end_index-1).apply(document))
            self.reflow_actions.append(ActionNewPage(end_index, count=len(excess), content=excess).apply(document))

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
