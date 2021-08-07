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
import typing

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QPersistentModelIndex, Qt, QItemSelectionModel, QObject, QModelIndex, \
    QAbstractItemModel
from PyQt5.QtWidgets import QTableView, QStyledItemDelegate, QWidget, QStyleOptionViewItem, QComboBox, QListView

from mtg_proxy_printer.model.card_list import PageColumns
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.model.imagedb import ImageDatabase
from mtg_proxy_printer.ui.page_renderer import PageRenderer
from mtg_proxy_printer.ui.add_card import AddCardWidget

from .common import inherits_from_ui_file_with_name

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger
__all__ = [
    "ComboBoxItemDelegate",
    "CentralWidget",
]


class ComboBoxItemDelegate(QStyledItemDelegate):

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QComboBox:
        editor = QComboBox(parent)
        return editor

    def setEditorData(self, editor: QComboBox, index: QModelIndex) -> None:

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

    def setModelData(self, editor: QComboBox, model: QAbstractItemModel, index: QModelIndex) -> None:
        logger.debug(f"Setting data for column {index.column()} to {editor.currentData(Qt.UserRole)}")
        model.setData(index, editor.currentData(Qt.UserRole), Qt.EditRole)


class CentralWidget(QWidget):

    window_size_changed = pyqtSignal()
    settings_changed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(CentralWidget, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.document = None
        self.card_db = None
        self.image_db = None
        self.combo_box_delegate = self._setup_page_card_table_view()
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _setup_page_card_table_view(self) -> ComboBoxItemDelegate:
        self.page_card_table_view: QTableView
        combo_box_delegate = ComboBoxItemDelegate(self.page_card_table_view)
        self.page_card_table_view.setItemDelegateForColumn(PageColumns.CollectorNumber, combo_box_delegate)
        self.page_card_table_view.setItemDelegateForColumn(PageColumns.Set, combo_box_delegate)
        return combo_box_delegate

    def set_data(self, document: Document, card_db: CardDatabase, image_db: ImageDatabase):
        self.document = document
        self.card_db = card_db
        self.image_db = image_db
        document.loading_state_changed.connect(self.select_first_page)
        document.current_page_changed.connect(self.on_current_page_changed)

        self.page_card_table_view.setModel(document)
        self._setup_page_renderer(document)
        self._setup_add_card_widget(card_db, image_db)
        self._setup_document_view(document)

    def _setup_add_card_widget(self, card_db: CardDatabase, image_db: ImageDatabase):
        self.add_card_widget: AddCardWidget
        self.add_card_widget.set_card_database(card_db)
        self.add_card_widget.card_added.connect(image_db.get_new_card_image_asynchronous)
        self.settings_changed.connect(self.add_card_widget.update_selected_language)

    def _setup_document_view(self, document: Document):
        self.document_view: QListView
        self.document_view.setModel(document)
        self.document_view.selectionModel().currentChanged.connect(document.on_ui_selects_new_page)
        self.select_first_page()

    def on_current_page_changed(self, new_page: QPersistentModelIndex):
        self.page_card_table_view: QTableView
        self.page_card_table_view.clearSelection()
        self.page_card_table_view.setRootIndex(new_page.sibling(new_page.row(), new_page.column()))
        self.page_card_table_view.setColumnHidden(PageColumns.Image, True)

    def _setup_page_renderer(self, document: Document):
        self.page_renderer: PageRenderer
        self.page_renderer.set_document(document)
        self.window_size_changed.connect(self.page_renderer.on_resize_event_triggered)
        self.settings_changed.connect(self.page_renderer.scene().redraw)

    @pyqtSlot()
    def on_delete_selected_images_button_clicked(self):
        self.page_card_table_view: QTableView
        multi_selection = self.page_card_table_view.selectionModel().selectedRows()
        logger.debug(f"User removes {len(multi_selection)} items from the current page.")
        self.page_card_table_view.model().remove_card_multi_selection(multi_selection)

    @pyqtSlot()
    def select_first_page(self, loading_in_progress: bool = False):
        if not loading_in_progress:
            logger.info("Loading finished. Selecting first page.")
            new_selection = self.document.index(0, 0)
            self.document_view.selectionModel().select(new_selection, QItemSelectionModel.Select)
            self.document.on_ui_selects_new_page(new_selection)

    @pyqtSlot()
    def on_action_discard_page_triggered(self):
        self.document_view: QListView
        if self.document.rowCount() == 1:
            logger.info(f"User selects to delete the only page, so clearing it.")
            self.document.clear_page(self.document.index(0, 0))
            return
        to_be_deleted: int = self.document_view.selectedIndexes()[0].row()
        logger.info(f"User selects to delete the currently selected page. Will be removing page {to_be_deleted}")
        logger.debug("Deleting the requested page.")
        # TODO: Investigate, why unsetting the model is needed.
        #  The document_view’s selection model somehow asks for data using invalid
        #  indices, when the last page is selected and gets deleted. The only way around seems to be to
        #  completely disconnect the model, remove the row, then set it again.
        self.document_view.setModel(None)
        self.document.remove_pages([self.document.index(to_be_deleted, 0)])
        # Now reset the model (and reconnect the currentChanged signal, which seems to be disconnected implicitly
        self.document_view.setModel(self.document)
        self.document_view.selectionModel().currentChanged.connect(self.document.on_ui_selects_new_page)

        new_row_index = min(to_be_deleted, self.document.rowCount() - 1)
        logger.debug(f"Selecting page {new_row_index}.")
        new_row_selection = self.document.index(new_row_index, 0)
        self.document_view.selectionModel().select(new_row_selection, QItemSelectionModel.Select)
        self.document.on_ui_selects_new_page(new_row_selection)


class FlatVerticalCentralWidget(CentralWidget, *inherits_from_ui_file_with_name("central_widget/flat_vertical")):
    pass


class TabbedVerticalCentralWidget(CentralWidget, *inherits_from_ui_file_with_name("central_widget/tabbed_vertical")):
    pass


CentralWidgetTypes = typing.Union[FlatVerticalCentralWidget, TabbedVerticalCentralWidget]
