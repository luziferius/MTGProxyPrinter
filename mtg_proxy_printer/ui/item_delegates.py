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

import typing
from typing import Union

from PyQt5.QtCore import QModelIndex, Qt, QAbstractItemModel, QSortFilterProxyModel
from PyQt5.QtWidgets import QStyledItemDelegate, QWidget, QStyleOptionViewItem, QComboBox, QSpinBox

from mtg_proxy_printer.model.carddb import Card, MTGSet, AnyCardType
from mtg_proxy_printer.model.card_list import CardListColumns
from mtg_proxy_printer.model.document import Document, PageColumns
from mtg_proxy_printer.logger import get_logger

try:
    from mtg_proxy_printer.ui.generated.set_editor_widget import Ui_SetEditor
except ModuleNotFoundError:
    from mtg_proxy_printer.ui.common import load_ui_from_file
    Ui_SetEditor = load_ui_from_file("set_editor_widget")


logger = get_logger(__name__)
del get_logger
__all__ = [
    "ComboBoxItemDelegate",
    "DocumentComboBoxItemDelegate",
    "CardListComboBoxItemDelegate",
    "BoundedCopiesSpinboxDelegate",
    "CardSideSelectionDelegate",
    "SetEditorDelegate",
]
ItemDataRole = Qt.ItemDataRole


class BoundedCopiesSpinboxDelegate(QStyledItemDelegate):
    """A QSpinBox delegate bounded to the inclusive range (1-100). Used for card copies."""
    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QSpinBox:
        editor = QSpinBox(parent)
        editor.setMinimum(1)
        editor.setMaximum(100)
        return editor


class CardSideSelectionDelegate(QStyledItemDelegate):
    """A QComboBox delegate used to switch between Front and Back face of cards"""
    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QSpinBox:
        editor = QComboBox(parent)
        editor.addItem(self.tr("Front"), True)
        editor.addItem(self.tr("Back"), False)
        return editor

    def setModelData(self, editor: QComboBox, model: QAbstractItemModel, index: QModelIndex) -> None:
        new_value = editor.currentData(ItemDataRole.UserRole)
        previous_value = index.data(ItemDataRole.EditRole)
        if new_value != previous_value:
            logger.debug(f"Setting data for column {index.column()} to {new_value}")
            model.setData(index, new_value, ItemDataRole.EditRole)


class SetEditorDelegate(QStyledItemDelegate):

    class CustomCardSetEditor(QWidget):
        """A widget holding two line edits, allowing the user to freely edit the set name & code of custom cards."""
        def __init__(self, parent: QWidget = None, flags=Qt.WindowFlags()):
            super().__init__(parent, flags)
            self.ui = ui = Ui_SetEditor()
            ui.setupUi(self)

        def set_data(self, mtg_set: MTGSet):
            self.ui.name_editor.setText(mtg_set.name)
            self.ui.code_edit.setText(mtg_set.code)

        def to_mtg_set(self):
            return MTGSet(self.ui.code_edit.text(), self.ui.name_editor.text())

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        card: AnyCardType = index.data(ItemDataRole.UserRole)
        # Use a locked-down choice-based editor for official cards, and a free-form editor for custom cards
        return QComboBox(parent) if card.oracle_id else self.CustomCardSetEditor(parent)

    def setEditorData(self, editor: Union[QComboBox, CustomCardSetEditor], index: QModelIndex):
        card: AnyCardType = index.data(ItemDataRole.UserRole)
        if self._is_official_card(editor):
            model = index.model()
            while hasattr(model, "sourceModel"):  # Resolve the source model to gain access to the card database.
                model = model.sourceModel()
            source_model: Document = model
            matching_sets = source_model.card_db.get_available_sets_for_card(card)
            current_set_code = card.set.code
            for position, set_data in enumerate(matching_sets):
                editor.addItem(set_data.data(ItemDataRole.DisplayRole), set_data)
                if set_data.code == current_set_code:
                    editor.setCurrentIndex(position)
        else:  # Custom card
            current_data: MTGSet = index.data(ItemDataRole.EditRole)
            editor.set_data(current_data)

    def setModelData(
            self, editor: Union[QComboBox, CustomCardSetEditor], model: QAbstractItemModel, index: QModelIndex) -> None:
        data = editor.currentData(ItemDataRole.UserRole) if self._is_official_card(editor) else editor.to_mtg_set()
        model.setData(index, data, ItemDataRole.EditRole)

    @staticmethod
    def _is_official_card(editor: Union[QComboBox, CustomCardSetEditor]):
        return isinstance(editor, QComboBox)


class ComboBoxItemDelegate(QStyledItemDelegate):
    """
    Editor widget allowing the user to switch a card printing by offering a choice among valid alternatives.
    """
    COLUMNS: typing.Union[PageColumns, CardListColumns] = None

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QComboBox:
        editor = QComboBox(parent)
        return editor

    def setEditorData(self, editor: QComboBox, index: QModelIndex) -> None:
        model: typing.Union[Document, QSortFilterProxyModel] = index.model()
        column = index.column()
        while hasattr(model, "sourceModel"):  # Resolve the source model to gain access to the card database.
            model = model.sourceModel()
        source_model: Document = model
        card: Card = index.data(ItemDataRole.UserRole)
        if hasattr(self.COLUMNS, "Copies") and column == self.COLUMNS.Copies:
            pass
        elif column == self.COLUMNS.Set:  # TODO: Outdated. Remove. Replace use in Document with SetEditorDelegate
            matching_sets = source_model.card_db.get_available_sets_for_card(card)
            current_set_code = card.set.code
            current_set_position = 0
            for position, set_data in enumerate(matching_sets):
                editor.addItem(set_data.data(ItemDataRole.DisplayRole), set_data.data(ItemDataRole.EditRole))
                if set_data.code == current_set_code:
                    current_set_position = position
            editor.setCurrentIndex(current_set_position)

        elif column == self.COLUMNS.CollectorNumber:
            matching_collector_numbers = source_model.card_db.get_available_collector_numbers_for_card_in_set(card)
            for collector_number in matching_collector_numbers:
                editor.addItem(collector_number, collector_number)  # Store the key in the UserData role
            if matching_collector_numbers:
                editor.setCurrentIndex(matching_collector_numbers.index(index.data(ItemDataRole.EditRole)))

        elif column == self.COLUMNS.Language:
            card = index.data(ItemDataRole.UserRole)
            matching_languages = source_model.card_db.get_available_languages_for_card(card)
            for language in matching_languages:
                editor.addItem(language, language)
            if matching_languages:
                editor.setCurrentIndex(matching_languages.index(index.data(ItemDataRole.EditRole)))

    def setModelData(self, editor: QComboBox, model: QAbstractItemModel, index: QModelIndex) -> None:
        new_value = editor.currentData(ItemDataRole.UserRole)
        previous_value = index.data(ItemDataRole.EditRole)
        if new_value != previous_value:
            logger.debug(f"Setting data for column {index.column()} to {new_value}")
            model.setData(index, new_value, ItemDataRole.EditRole)


class DocumentComboBoxItemDelegate(ComboBoxItemDelegate):
    COLUMNS = PageColumns

class CardListComboBoxItemDelegate(ComboBoxItemDelegate):
    COLUMNS = CardListColumns
