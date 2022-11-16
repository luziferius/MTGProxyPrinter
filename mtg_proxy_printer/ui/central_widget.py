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
import math
import typing

from PyQt5.QtCore import pyqtSignal as Signal, pyqtSlot as Slot, QPersistentModelIndex, QItemSelectionModel, QModelIndex
from PyQt5.QtWidgets import QTableView, QWidget

import mtg_proxy_printer.settings
from mtg_proxy_printer.model.card_list import PageColumns
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.model.imagedb import ImageDatabase
from mtg_proxy_printer.ui.item_delegates import ComboBoxItemDelegate

try:
    from mtg_proxy_printer.ui.generated.central_widget.columnar import Ui_central_widget as Ui_Columnar
    from mtg_proxy_printer.ui.generated.central_widget.grouped import Ui_central_widget as Ui_Grouped
    from mtg_proxy_printer.ui.generated.central_widget.tabbed_vertical import Ui_central_widget as Ui_TabbedVertical
except ModuleNotFoundError:
    from mtg_proxy_printer.ui.common import load_ui_from_file
    Ui_Columnar = load_ui_from_file("central_widget/columnar")
    Ui_Grouped = load_ui_from_file("central_widget/grouped")
    Ui_TabbedVertical = load_ui_from_file("central_widget/tabbed_vertical")


from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


__all__ = [
    "CentralWidget",
]

UiType = typing.Union[typing.Type[Ui_Grouped], typing.Type[Ui_Columnar], typing.Type[Ui_TabbedVertical]]


class CentralWidget(QWidget):

    settings_changed = Signal()

    def __init__(self, parent: QWidget = None):
        logger.debug(f"Creating {self.__class__.__name__} instance.")
        super(CentralWidget, self).__init__(parent)
        ui_class = get_configured_central_widget_layout_class()
        logger.debug(f"Using central widget class {ui_class.__name__}")
        self.ui = ui_class()
        self.ui.setupUi(self)
        self.document = None
        self.card_db = None
        self.image_db = None
        self.combo_box_delegate = self._setup_page_card_table_view()
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _setup_page_card_table_view(self) -> ComboBoxItemDelegate:
        combo_box_delegate = ComboBoxItemDelegate(self.ui.page_card_table_view)
        self.ui.page_card_table_view.setItemDelegateForColumn(PageColumns.CollectorNumber, combo_box_delegate)
        self.ui.page_card_table_view.setItemDelegateForColumn(PageColumns.Set, combo_box_delegate)
        return combo_box_delegate

    def set_data(self, document: Document, card_db: CardDatabase, image_db: ImageDatabase):
        self.document = document
        self.card_db = card_db
        self.image_db = image_db
        document.rowsAboutToBeRemoved.connect(self.on_document_rows_about_to_be_removed)
        document.loading_state_changed.connect(self.select_first_page)
        document.current_page_changed.connect(self.on_current_page_changed)
        self.ui.page_card_table_view.setModel(document)
        # Signal has to be connected here, because setModel() implicitly creates the QItemSelectionModel
        self.ui.page_card_table_view.selectionModel().selectionChanged.connect(
            self.parsed_cards_table_selection_changed)
        self._setup_page_renderer(document)
        self._setup_add_card_widget(card_db, image_db)
        self._setup_document_view(document)

    def _setup_add_card_widget(self, card_db: CardDatabase, image_db: ImageDatabase):
        self.ui.add_card_widget.set_card_database(card_db)
        self.ui.add_card_widget.card_added.connect(image_db.get_new_card_image_asynchronous)
        self.settings_changed.connect(self.ui.add_card_widget.update_selected_language)

    def _setup_document_view(self, document: Document):
        self.ui.document_view.setModel(document)
        self.ui.document_view.selectionModel().currentChanged.connect(document.on_ui_selects_new_page)
        self.select_first_page()

    @Slot()
    def parsed_cards_table_selection_changed(self):
        """Called whenever the selection in the page_card_table_view is changed. This manages the activation state
        of the “Remove selected” button, which should only be clickable, if there are cards selected."""
        selection_model = self.ui.page_card_table_view.selectionModel()
        self.ui.delete_selected_images_button.setDisabled(selection_model.selection().isEmpty())

    def on_current_page_changed(self, new_page: QPersistentModelIndex):
        self.ui.page_card_table_view.clearSelection()
        self.ui.page_card_table_view.setRootIndex(new_page.sibling(new_page.row(), new_page.column()))
        self.ui.page_card_table_view.setColumnHidden(PageColumns.Image, True)
        # The size adjustments have to be done here,
        # because the width can only be set after the model root index to show has been set
        default_column_width = 102
        for column, scaling_factor in (
                (PageColumns.CardName, 1.7),
                (PageColumns.Set, 2),
                (PageColumns.CollectorNumber, 0.95),
                (PageColumns.Language, 0.8)):
            new_size = math.floor(default_column_width * scaling_factor)
            self.ui.page_card_table_view.setColumnWidth(column, new_size)

    def on_document_rows_about_to_be_removed(self, index: QModelIndex, first: int, last: int):
        current_row = self.ui.document_view.currentIndex().row()
        if index.parent().isValid():
            # Not interested in removed cards here, so return if cards are about to be removed.
            return
        if not index.parent().isValid() and not (last == current_row == (self.document.rowCount()-1)):
            return
        # Selecting a different page is required if the current page is the last page and is going to be deleted.
        # So re-selecting the page is required to prevent exceptions. Without this, the document view creates invalid
        # model indices.
        new_page_to_select = max(0, first-1)
        logger.debug(
            f"Currently selected last page {current_row} about to be removed. New page to select: {new_page_to_select}")
        self.ui.document_view.setCurrentIndex(self.document.index(new_page_to_select, 0))

    def _setup_page_renderer(self, document: Document):
        self.ui.page_renderer.set_document(document)
        self.settings_changed.connect(self.ui.page_renderer.scene().on_settings_changed)
        document.page_layout_changed.connect(self.ui.page_renderer.scene().on_settings_changed)

    @Slot()
    def on_delete_selected_images_button_clicked(self):
        self.page_card_table_view: QTableView
        multi_selection = self.ui.page_card_table_view.selectionModel().selectedRows()
        logger.debug(f"User removes {len(multi_selection)} items from the current page.")
        self.ui.page_card_table_view.model().remove_card_multi_selection(multi_selection)

    @Slot()
    def select_first_page(self, loading_in_progress: bool = False):
        if not loading_in_progress:
            logger.info("Loading finished. Selecting first page.")
            new_selection = self.document.index(0, 0)
            self.ui.document_view.selectionModel().select(new_selection, QItemSelectionModel.Select)
            self.document.on_ui_selects_new_page(new_selection)

    @Slot()
    def action_discard_page_triggered(self):
        if self.document.rowCount() == 1:
            logger.info(f"User selects to delete the only page, so clearing it.")
            self.document.clear_page(self.document.index(0, 0))
            return
        to_be_deleted: int = self.ui.document_view.selectedIndexes()[0].row()
        logger.info(f"User selects to delete the currently selected page {to_be_deleted}. Deleting it")
        self.document.remove_pages([self.document.index(to_be_deleted, 0)])


def get_configured_central_widget_layout_class() -> UiType:
    gui_settings = mtg_proxy_printer.settings.settings["gui"]
    configured_layout = gui_settings["central-widget-layout"]
    if configured_layout == "horizontal":
        return Ui_Grouped
    if configured_layout == "columnar":
        return Ui_Columnar
    return Ui_TabbedVertical
