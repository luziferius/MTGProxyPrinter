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
import typing

from PyQt5.QtCore import QModelIndex, Qt, QAbstractItemModel, QSortFilterProxyModel
from PyQt5.QtWidgets import QStyledItemDelegate, QWidget, QStyleOptionViewItem, QComboBox

from mtg_proxy_printer.model.card_list import PageColumns
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger
__all__ = [
    "ComboBoxItemDelegate",
]


class ComboBoxItemDelegate(QStyledItemDelegate):
    """
    Editor widget allowing the user to switch a card printing by offering a choice among valid alternatives.
    """

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QComboBox:
        editor = QComboBox(parent)
        return editor

    def setEditorData(self, editor: QComboBox, index: QModelIndex) -> None:
        model: typing.Union[Document, QSortFilterProxyModel] = index.model()
        source_model: Document = model
        while hasattr(source_model, "sourceModel"):  # Resolve the source model to gain access to the card database.
            source_model = source_model.sourceModel()
        if index.column() == PageColumns.Set:
            matching_sets = source_model.card_db.find_sets_matching(
                index.siblingAtColumn(PageColumns.CardName).data(Qt.EditRole),
                index.siblingAtColumn(PageColumns.Language).data(Qt.EditRole),
            )
            current_set_code = index.data(Qt.EditRole)
            current_set_position = 0
            for position, set_data in enumerate(matching_sets):
                editor.addItem(set_data.data(Qt.DisplayRole), set_data.data(Qt.EditRole))
                if set_data.code == current_set_code:
                    current_set_position = position
            editor.setCurrentIndex(current_set_position)

        elif index.column() == PageColumns.CollectorNumber:
            matching_collector_numbers = source_model.card_db.find_collector_numbers_matching(
                index.siblingAtColumn(PageColumns.CardName).data(Qt.EditRole),
                index.siblingAtColumn(PageColumns.Set).data(Qt.EditRole),
                index.siblingAtColumn(PageColumns.Language).data(Qt.EditRole),
            )
            for collector_number in matching_collector_numbers:
                editor.addItem(collector_number, collector_number)  # Store the key in the UserData role
            editor.setCurrentIndex(matching_collector_numbers.index(index.data(Qt.EditRole)))

    def setModelData(self, editor: QComboBox, model: QAbstractItemModel, index: QModelIndex) -> None:
        new_value = editor.currentData(Qt.UserRole)
        previous_value = index.data(Qt.EditRole)
        if new_value != previous_value:
            logger.debug(f"Setting data for column {index.column()} to {new_value}")
            model.setData(index, new_value, Qt.EditRole)
