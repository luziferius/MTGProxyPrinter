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

import typing

from mtg_proxy_printer.model.document import Document, INVALID_INDEX
from mtg_proxy_printer.model.document_page import Page
from ._interface import DocumentAction, IllegalStateError
from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger
__all__ = [
    "ActionNewPage",
    "ActionRemovePage",
]


class ActionNewPage(DocumentAction):

    def __init__(self, position: int = None, *, count: int = 1):
        """
        Insert count new, empty pages at the given index. Positions are clamped into the range [0, page_count].
        If given None for the position, append the page to the document end instead. Page count defaults to 1.
        """
        super().__init__()
        self.position = position
        self.count = count

    def apply(self, document: Document):
        self.position = document.rowCount() if self.position is None \
            else max(0, min(self.position, document.rowCount()))
        document.beginInsertRows(INVALID_INDEX, self.position, self.position+self.count-1)
        if self.position == document.rowCount():
            for _ in range(self.count):
                new_page = Page()
                document.pages.append(new_page)
                document.page_index_cache[id(new_page)] = len(document.pages) - 1
        else:
            for _ in range(self.count):
                document.pages.insert(self.position, Page())
            document.recreate_page_index_cache()
        document.endInsertRows()
        return self

    def undo(self, document: Document):
        if self.position is None:
            raise IllegalStateError("Page position not set")
        ActionRemovePage(self.position, self.count).apply(document)
        return self


class ActionRemovePage(DocumentAction):

    def __init__(self, position: int = None, count: int = 1):
        """Delete count pages at the given index. If given None for the position, delete the current page instead."""
        super().__init__()
        self.position = position
        self.count = count
        self.removed_pages: typing.List[Page] = []
        self.currently_edited_page = None  # Set, if the currently edited page is removed

    def apply(self, document: Document):
        self.position = first_index = self.position if self.position is not None \
            else document.find_page_list_index(document.currently_edited_page)
        last_index = first_index + self.count - 1
        logger.debug(f"Removing pages {first_index} to {last_index}. {document.rowCount()=}")
        self.removed_pages[:] = document.pages[first_index:last_index+1]
        # Note: Can not use "currently_edited_page in removed_pages", because the in operator does not check for
        # object identity, which is required here.
        currently_edited_page_removed = \
            first_index <= document.find_page_list_index(document.currently_edited_page) <= last_index
        if currently_edited_page_removed:
            self.currently_edited_page = document.currently_edited_page
        document.beginRemoveRows(INVALID_INDEX, first_index, last_index)
        del document.pages[first_index:last_index+1]
        document.recreate_page_index_cache()
        document.endRemoveRows()
        if not document.pages:
            document._set_currently_edited_page(document.add_page())
        elif currently_edited_page_removed:
            newly_selected_page = min(first_index, document.rowCount()-1)
            logger.debug(f"Currently edited page is removed, switching to page {newly_selected_page}")
            # Since the page list is non-empty, there is always a page to select.
            # Choose the first after the removed range or the last, whichever comes first.
            document._set_currently_edited_page(document.pages[newly_selected_page])
        return self

    def undo(self, document: Document):
        if self.position is None:
            raise IllegalStateError("Cannot undo page removal without location to restore")
        start = self.position
        end = start + len(self.removed_pages) - 1
        document.beginInsertRows(INVALID_INDEX, start, end)
        if self.position == document.rowCount():
            self._append_pages(document, start)
        else:
            self._insert_pages(document, start)
        document.endInsertRows()
        if self.currently_edited_page is not None:
            document._set_currently_edited_page(self.currently_edited_page)
        return self

    def _append_pages(self, document: Document, start: int):
        document.pages += self.removed_pages
        document.page_index_cache.update(
            (id(page), index) for index, page in enumerate(self.removed_pages, start=start)
        )

    def _insert_pages(self, document: Document, start: int):
        for index, page in enumerate(self.removed_pages, start=start):
            document.pages.insert(index, page)
        document.recreate_page_index_cache()
