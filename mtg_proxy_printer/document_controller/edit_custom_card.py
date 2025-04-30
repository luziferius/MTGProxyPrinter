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

from PyQt5.QtCore import QModelIndex, Qt
if typing.TYPE_CHECKING:
    from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.document_page import CardContainer, PageColumns
from ._interface import DocumentAction, Self

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger
__all__ = [
    "ActionEditCustomCard",
]
ItemDataRole = Qt.ItemDataRole


class ActionEditCustomCard(DocumentAction):
    """
    Edits a field of a custom card. Ensures that the dataChanged signal is sent for all copies of the given card
    """
    COMPARISON_ATTRIBUTES = ["old_value", "new_value", "page", "row", "column"]

    def __init__(self, index: QModelIndex, value):
        self.page = index.parent().row()
        self.row = index.row()
        self.column = PageColumns(index.column())
        self.old_value = index.data(ItemDataRole.EditRole)
        self.new_value = value
        self.new_display_value = None
        document = index.model()
        self.header_text = document.headerData(self.column, Qt.Orientation.Horizontal, ItemDataRole.DisplayRole)

    def apply(self, document: "Document") -> Self:
        self._set_data_for_custom_card(document, self.new_value)
        index = document.index(self.row, self.column, document.index(self.page, 0))
        self.new_display_value = index.data(ItemDataRole.DisplayRole)
        return super().apply(document)

    def undo(self, document: "Document") -> Self:
        self._set_data_for_custom_card(document, self.old_value)
        return super().undo(document)

    def _set_data_for_custom_card(self, document: "Document", value: typing.Any):
        row, column = self.row, self.column
        index = document.index(row, column, document.index(self.page, 0))
        container: CardContainer = index.internalPointer()
        card = container.card
        logger.debug(f"Setting page data on custom card for {column=} to {value}")
        if column == PageColumns.CardName:
            # This also affects the page overview. find_relevant_index_ranges()
            # takes care of that by also returning relevant Page indices
            card.name = value
        elif column == PageColumns.CollectorNumber:
            card.collector_number = value
        elif column == PageColumns.Language:
            card.language = value
        elif column == PageColumns.IsFront:
            card.is_front = value
            card.face_number = int(not value)
        elif column == PageColumns.Set:
            card.set = value
        for lower, upper in document.find_relevant_index_ranges(card, column):
            document.dataChanged.emit(lower, upper, [ItemDataRole.DisplayRole, ItemDataRole.EditRole])

    @functools.cached_property
    def as_str(self):
        return self.translate(
            "ActionEditCustomCard", "Edit custom card, set {column_header_text} to {new_value}",
            "Undo/redo tooltip text").format(column_header_text=self.header_text, new_value=self.new_display_value)
