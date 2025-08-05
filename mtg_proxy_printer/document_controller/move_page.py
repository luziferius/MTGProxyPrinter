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
import itertools
import typing

from PySide6.QtCore import QModelIndex

from ._interface import DocumentAction, IllegalStateError, Self
from mtg_proxy_printer.logger import get_logger

if typing.TYPE_CHECKING:
    from mtg_proxy_printer.model.document_page import Page
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

    def __init__(self, source_page: int, target_page: int):
        super().__init__()
        self.source_page = source_page
        self.target_page = target_page

    def apply(self, document: "Document") -> Self:
        super().apply(document)
        self._validate_parameters(document)
        document.moveRow(document.INVALID_INDEX, self.source_page, document.INVALID_INDEX, self.target_page)
        return self

    def undo(self, document: "Document") -> Self:
        super().undo(document)
        self._validate_parameters(document)
        return self

    def _validate_parameters(self, document: "Document"):
        if not (
                self.source_page >= 0 <= self.target_page < document.rowCount() > self.source_page):
            raise IllegalStateError()

    @functools.cached_property
    def as_str(self):
        return self.translate(
            "ActionMovePage",
            "Move page {source_page} to position {target_page}",
            "Both parameters are page numbers, like in 'Move page 3 to position 7'"
        ).format(source_page=self.source_page+1, target_page=self.target_page+1)