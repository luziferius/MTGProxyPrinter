# Copyright (C) 2020, 2021 Thomas Hess <thomas.hess@udo.edu>

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

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QPersistentModelIndex, Qt
from PyQt5.QtWidgets import QTableView, QStyledItemDelegate, QWidget, QStyleOptionViewItem, QComboBox

from mtg_proxy_printer.model.card_list import PageColumns
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.ui.page_renderer import PageRenderer

from .common import inherits_from_ui_file_with_name

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger
__all__ = [
    "ComboBoxItemDelegate",
    "CurrentPageView",
]


class ComboBoxItemDelegate(QStyledItemDelegate):

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QtCore.QModelIndex) -> QComboBox:
        editor = QComboBox(parent)
        return editor

    def setEditorData(self, editor: QComboBox, index: QtCore.QModelIndex) -> None:

        model: Document = index.model()
        if index.column() == PageColumns.Set:
            matching_sets = model.card_db.find_sets_matching(
                index.siblingAtColumn(PageColumns.CardName).data(Qt.EditRole),
                index.siblingAtColumn(PageColumns.Language).data(Qt.EditRole),
            )
            current_set_code = index.data(Qt.EditRole)
            current_set_position = 0
            for position, set_data in enumerate(matching_sets):
                editor.addItem(set_data.name, set_data.code)  # Store the key (set_code) in the UserData role
                if set_data.code == current_set_code:
                    current_set_position = position
            editor.setCurrentIndex(current_set_position)

        elif index.column() == PageColumns.CollectorNumber:
            matching_collector_numbers = model.card_db.find_collector_numbers_matching(
                index.siblingAtColumn(PageColumns.CardName).data(Qt.EditRole),
                index.siblingAtColumn(PageColumns.Set).data(Qt.EditRole),
                index.siblingAtColumn(PageColumns.Language).data(Qt.EditRole),
            )
            for collector_number in matching_collector_numbers:
                editor.addItem(collector_number, collector_number)  # Store the key in the UserData role
            editor.setCurrentIndex(matching_collector_numbers.index(index.data(Qt.EditRole)))

    def setModelData(self, editor: QComboBox, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex) -> None:
        logger.debug(f"Setting data for column {index.column()} to {editor.currentData(Qt.UserRole)}")
        model.setData(index, editor.currentData(Qt.UserRole), Qt.EditRole)


class CurrentPageView(*inherits_from_ui_file_with_name("current_page_view")):

    window_size_changed = pyqtSignal()
    settings_changed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(CurrentPageView, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.page_card_table_view: QTableView
        self.combo_box_delegate = ComboBoxItemDelegate(self.page_card_table_view)
        self.page_card_table_view.setItemDelegateForColumn(PageColumns.CollectorNumber, self.combo_box_delegate)
        self.page_card_table_view.setItemDelegateForColumn(PageColumns.Set, self.combo_box_delegate)
        logger.info(f"Created {self.__class__.__name__} instance.")

    def set_document(self, document: Document):
        self._setup_page_renderer(document)
        self.page_card_table_view.setModel(document)

    def on_current_page_changed(self, new_page: QPersistentModelIndex):
        self.page_card_table_view: QTableView
        self.page_card_table_view.clearSelection()
        self.page_card_table_view.setRootIndex(new_page.sibling(new_page.row(), new_page.column()))
        self.page_card_table_view.setColumnHidden(PageColumns.Image, True)

    def _setup_page_renderer(self, document: Document):
        self.page_renderer: PageRenderer
        self.page_renderer.set_document(document)
        self.settings_changed.connect(self.page_renderer.on_settings_changed)
        self.window_size_changed.connect(self.page_renderer.on_resize_event_triggered)

    @pyqtSlot()
    def on_delete_selected_images_button_clicked(self):
        self.page_card_table_view: QTableView
        multi_selection = self.page_card_table_view.selectionModel().selectedRows()
        logger.debug(f"User removes {len(multi_selection)} items from the current page.")
        self.page_card_table_view.model().remove_card_multi_selection(multi_selection)
