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


import functools
import typing

from PySide6.QtCore import QObject

from ._interface import DocumentAction, IllegalStateError, Self
from mtg_proxy_printer.logger import get_logger

if typing.TYPE_CHECKING:
    from mtg_proxy_printer.model.document import Document

logger = get_logger(__name__)
del get_logger
__all__ = [
    "ActionMovePage",
]


class ActionMovePage(DocumentAction):
    """
    Moves a page within the document from source_page to target_page
    """

    COMPARISON_ATTRIBUTES = ["source_page", "target_page"]

    def __init__(self, source_page: int, target_page: int, parent: QObject = None):
        super().__init__(parent)
        self.source_page = source_page
        self.target_page = target_page

    def apply(self, document: "Document") -> Self:
        super().apply(document)
        self._validate_parameters(document)
        source, target = self.source_page, self.target_page
        self.move_page(document, source, target)
        return self

    @staticmethod
    def move_page(
            document: "Document", source_page: int, insert_at: int, /) -> None:
        logger.info(f"Moving Page {source_page} to position {insert_at}")
        index = document.INVALID_INDEX
        if not document.beginMoveRows(index, source_page, source_page, index, insert_at):
            logger.warning("Invalid page move attempted")
            return
        if source_page+1 <= insert_at:
            # If the source is before the destination index, deleting the source shifts the destination count items down
            insert_at -= 1
        pages = document.pages[source_page:source_page + 1]
        del document.pages[source_page:source_page + 1]
        document.pages[insert_at:insert_at] = pages
        document.recreate_page_index_cache()
        document.endMoveRows()
        return

    def undo(self, document: "Document") -> Self:
        super().undo(document)
        self._validate_parameters(document)
        source = self.target_page + (self.source_page > self.target_page) - 1
        target = self.source_page + (self.source_page > self.target_page)
        self.move_page(document, source, target)
        return self

    def _validate_parameters(self, document: "Document"):
        if not (self.source_page >= 0 <= self.target_page <= document.rowCount() > self.source_page):
            raise IllegalStateError()

    @functools.cached_property
    def as_str(self):
        return self.tr(
            "Move page {source_page} to position {target_page}",
            "Both parameters are page numbers, like in 'Move page 3 to position 7'"
        ).format(source_page=self.source_page+1, target_page=self.target_page+1)