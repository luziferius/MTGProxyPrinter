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
from itertools import combinations
from typing import Union

from PyQt5.QtCore import QModelIndex, Qt, QAbstractItemModel, QSortFilterProxyModel, QObject, QEvent
from PyQt5.QtGui import QKeyEvent, QFocusEvent
from PyQt5.QtWidgets import QStyledItemDelegate, QWidget, QStyleOptionViewItem, QComboBox, QSpinBox, QLineEdit, \
    QApplication

from mtg_proxy_printer.model.card import MTGSet, Card, AnyCardType
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.logger import get_logger

try:
    from mtg_proxy_printer.ui.generated.set_editor_widget import Ui_SetEditor
except ModuleNotFoundError:
    from mtg_proxy_printer.ui.common import load_ui_from_file
    Ui_SetEditor = load_ui_from_file("set_editor_widget")


logger = get_logger(__name__)
del get_logger
__all__ = [
    "CollectorNumberEditorDelegate",
    "BoundedCopiesSpinboxDelegate",
    "CardSideSelectionDelegate",
    "SetEditorDelegate",
    "LanguageEditorDelegate",
]
ItemDataRole = Qt.ItemDataRole


def get_document_from_index(index: QModelIndex) -> Document:
    """
    Returns the Document instance associated with the given index.
    Resolves any chain of layered sort/filter models, to grant access to non-Qt-API Document methods.
    """
    model: typing.Union[Document, QSortFilterProxyModel, None] = index.model()
    if model is None:
        raise RuntimeError("Invalid index without attached model passed")
    while hasattr(model, "sourceModel"):
        model = model.sourceModel()
    source_model: Document = model
    return source_model


class FastComboBoxDelegate(QStyledItemDelegate):
    """
    A faster QComboBox-based editor delegate.
    Immediately opens the choice popup and immediately commits when an entry is selected
    """
    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QComboBox:
        editor = QComboBox(parent)
        # Automatically commit by sending an Enter key when the user selects something in the item list
        editor.activated.connect(
            lambda: QApplication.sendEvent(
                editor,
                QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Enter, Qt.KeyboardModifier.NoModifier)
            ))
        return editor

    def eventFilter(self, editor: QComboBox, event: QFocusEvent) -> bool:
        # Subclasses may return custom editors for some cases. Only call showPopup(), if it is present.
        if editor is not None and hasattr(editor, "showPopup") and isinstance(event, QFocusEvent) \
                and event.type() == QEvent.Type.FocusIn \
                and event.reason() != Qt.FocusReason.PopupFocusReason:
            # When the editor receives focus, but not because its popup closed, show the popup to save a click.
            editor.showPopup()
        return super().eventFilter(editor, event)


class BoundedCopiesSpinboxDelegate(QStyledItemDelegate):
    """A QSpinBox delegate bounded to the inclusive range (1-100). Used for card copies."""
    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QSpinBox:
        editor = QSpinBox(parent)
        editor.setMinimum(1)
        editor.setMaximum(100)
        return editor


class CardSideSelectionDelegate(FastComboBoxDelegate):
    """A QComboBox delegate used to switch between Front and Back face of cards"""
    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QComboBox:
        editor = super().createEditor(parent, option, index)
        editor.addItem(self.tr("Front"), True)
        editor.addItem(self.tr("Back"), False)
        return editor

    def setModelData(self, editor: QComboBox, model: QAbstractItemModel, index: QModelIndex) -> None:
        new_value = editor.currentData(ItemDataRole.UserRole)
        previous_value = index.data(ItemDataRole.EditRole)
        if new_value != previous_value:
            logger.debug(f"Setting data for column {index.column()} to {new_value}")
            model.setData(index, new_value, ItemDataRole.EditRole)


class SetEditorDelegate(FastComboBoxDelegate):
    """
    A set editor. For official cards, use a QComboBox with valid set choices for the given card.
    For custom cards, use the embedded editor widget to allow free-form text entry.
    """
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
        return self.CustomCardSetEditor(parent) if card.is_custom_card else super().createEditor(parent, option, index)

    def setEditorData(self, editor: Union[QComboBox, CustomCardSetEditor], index: QModelIndex):
        card: AnyCardType = index.data(ItemDataRole.UserRole)
        if card.is_custom_card:
            current_data: MTGSet = index.data(ItemDataRole.EditRole)
            editor.set_data(current_data)
        else:
            model = get_document_from_index(index)
            matching_sets = model.card_db.get_available_sets_for_card(card)
            current_set_code = card.set.code
            for position, set_data in enumerate(matching_sets):
                editor.addItem(set_data.data(ItemDataRole.DisplayRole), set_data)
                if set_data.code == current_set_code:
                    editor.setCurrentIndex(position)

    def setModelData(
            self, editor: Union[QComboBox, CustomCardSetEditor], model: QAbstractItemModel, index: QModelIndex) -> None:
        card: AnyCardType = index.data(ItemDataRole.UserRole)
        data = editor.to_mtg_set() if card.is_custom_card else editor.currentData(ItemDataRole.UserRole)
        model.setData(index, data, ItemDataRole.EditRole)

    @staticmethod
    def _is_official_card(editor: Union[QComboBox, CustomCardSetEditor]):
        return isinstance(editor, QComboBox)


class LanguageEditorDelegate(FastComboBoxDelegate):
    """
    A language editor. For official cards, use a QComboBox with valid language choices for the given card.
    For custom cards, populate the combo box with all known languages and also enable the edit functionality
    to allow free-form text entry.
    """
    MAX_LENGTH = 5

    def setEditorData(self, editor: QComboBox, index: QModelIndex):
        model = get_document_from_index(index)
        card: Card = index.data(ItemDataRole.UserRole)
        current_language = card.language
        is_custom_card = card.is_custom_card
        editor.setEditable(is_custom_card)  # Allow custom languages for custom cards only
        if is_custom_card:
            editor.lineEdit().setMaxLength(self.MAX_LENGTH)
            languages = model.card_db.get_all_languages()
        else:
            languages = model.card_db.get_available_languages_for_card(card)
        for language in languages:
            editor.addItem(language, language)
        if current_language in languages:  # This is only false for custom cards and user-entered, unknown languages
            editor.setCurrentIndex(languages.index(index.data(ItemDataRole.EditRole)))

    def setModelData(self, editor: QComboBox, model: QAbstractItemModel, index: QModelIndex) -> None:
        new_value = editor.lineEdit().text() if editor.isEditable() else editor.currentData(ItemDataRole.UserRole)
        previous_value = index.data(ItemDataRole.EditRole)
        if new_value != previous_value:
            logger.debug(f"Setting data for column {index.column()} to {new_value}")
            model.setData(index, new_value, ItemDataRole.EditRole)


class CollectorNumberEditorDelegate(FastComboBoxDelegate):
    """
    Editor for collector numbers. Allows free-form editing for custom cards,
    and uses a locked-down choice-based combo box for official cards
    """
    def createEditor(
            self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex
    ) -> typing.Union[QLineEdit, QComboBox]:
        card: AnyCardType = index.data(ItemDataRole.UserRole)
        # Use a locked-down choice-based editor for official cards, and a free-form editor for custom cards
        return QLineEdit(parent) if card.is_custom_card else super().createEditor(parent, option, index)

    def setEditorData(self, editor: typing.Union[QLineEdit, QComboBox], index: QModelIndex) -> None:
        model = get_document_from_index(index)
        card: Card = index.data(ItemDataRole.UserRole)
        if card.is_custom_card:
            editor.setText(card.collector_number)
        else:
            matching_collector_numbers = model.card_db.get_available_collector_numbers_for_card_in_set(card)
            for collector_number in matching_collector_numbers:
                editor.addItem(collector_number, collector_number)  # Store the key in the UserData role
            if matching_collector_numbers:
                editor.setCurrentIndex(matching_collector_numbers.index(index.data(ItemDataRole.EditRole)))

    def setModelData(
            self, editor: typing.Union[QLineEdit, QComboBox], model: QAbstractItemModel, index: QModelIndex) -> None:
        card: Card = index.data(ItemDataRole.UserRole)
        new_value = editor.text() if card.is_custom_card else editor.currentData(ItemDataRole.UserRole)
        previous_value = card.collector_number
        if new_value != previous_value:
            logger.debug(f"Setting collector number from {previous_value} to {new_value}")
            model.setData(index, new_value, ItemDataRole.EditRole)
