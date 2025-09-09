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

from typing import Type

from PySide6.QtCore import Signal, Slot, QItemSelectionModel, QModelIndex, QPersistentModelIndex
from PySide6.QtWidgets import QWidget

import mtg_proxy_printer.app_dirs
import mtg_proxy_printer.settings
from mtg_proxy_printer.async_tasks.base import AsyncTask
from mtg_proxy_printer.document_controller.move_page import ActionMovePage
from mtg_proxy_printer.model.document import Document, DocumentColumns
from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.model.imagedb import ImageDatabase

try:
    from mtg_proxy_printer.ui.generated.central_widget.columnar import Ui_ColumnarCentralWidget
    from mtg_proxy_printer.ui.generated.central_widget.grouped import Ui_GroupedCentralWidget
    from mtg_proxy_printer.ui.generated.central_widget.tabbed_vertical import Ui_TabbedCentralWidget
except ModuleNotFoundError:
    from mtg_proxy_printer.ui.common import load_ui_from_file
    Ui_ColumnarCentralWidget = load_ui_from_file("central_widget/columnar")
    Ui_GroupedCentralWidget = load_ui_from_file("central_widget/grouped")
    Ui_TabbedCentralWidget = load_ui_from_file("central_widget/tabbed_vertical")

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


__all__ = [
    "CentralWidget",
]

UiType = Type[Ui_GroupedCentralWidget] | Type[Ui_ColumnarCentralWidget] | Type[Ui_TabbedCentralWidget]
UiInstance = Ui_GroupedCentralWidget | Ui_ColumnarCentralWidget | Ui_TabbedCentralWidget


class CentralWidget(QWidget):
    request_run_async_task = Signal(AsyncTask)

    def __init__(self, parent: QWidget = None):
        logger.debug(f"Creating {self.__class__.__name__} instance.")
        super().__init__(parent)
        ui_class = get_configured_central_widget_layout_class()
        logger.debug(f"Using central widget class {ui_class.__name__}")
        self.ui = ui_class()
        self.ui.setupUi(self)
        self.document: Document = None
        self._currently_edited_page: int = 0
        logger.info(f"Created {self.__class__.__name__} instance.")

    def set_data(self, document: Document, card_db: CardDatabase, image_db: ImageDatabase):
        logger.debug(f"{self.__class__.__name__} received model instances. Setting up child widgets…")
        self.document = document
        ui = self.ui
        document.current_page_changed.connect(self.on_document_current_page_changed)
        self._setup_page_card_table_view(ui, document, card_db)
        document.rowsAboutToBeRemoved.connect(self.on_document_rows_about_to_be_removed)
        document.rowsInserted.connect(self.on_document_rows_inserted)
        document.rowsRemoved.connect(self.on_document_rows_removed)
        ui.page_renderer.set_document(document)
        self._setup_add_card_widget(card_db, image_db)
        self._setup_document_view(document)
        logger.debug(f"{self.__class__.__name__} setup completed")

    def _setup_page_card_table_view(self, ui: UiInstance, document: Document, card_db: CardDatabase):
        view = ui.page_card_table_view
        view.set_data(document, card_db)
        # Have the "delete selected" button enabled iff the current selection is non-empty
        view.changed_selection_is_empty.connect(ui.delete_selected_images_button.setDisabled)
        ui.delete_selected_images_button.clicked.connect(ui.page_card_table_view.delete_selected_images)
        view.request_run_async_task.connect(self.request_run_async_task)

    def _setup_add_card_widget(self, card_db: CardDatabase, image_db: ImageDatabase):
        self.ui.add_card_widget.set_databases(card_db, image_db)
        self.ui.add_card_widget.request_run_async_task.connect(self.request_run_async_task)

    def _setup_document_view(self, document: Document):
        view = self.ui.document_view
        view.setModel(document)
        # Has to be set up here, because setModel() implicitly creates the QItemSelectionModel
        view.selectionModel().currentChanged.connect(document.on_ui_selects_new_page)
        self.select_first_page()

    @Slot(QModelIndex, int, int)
    def on_document_rows_about_to_be_removed(self, parent: QModelIndex, first: int, last: int):
        if parent.isValid():
            # Not interested in removed cards here, so return if cards are about to be removed.
            return
        document_view = self.ui.document_view
        currently_selected_page = document_view.currentIndex().row()
        removed_pages = last - first + 1
        if currently_selected_page < self.document.rowCount()-removed_pages:
            # After removal, the current page remains within the document and stays valid. Nothing to do.
            return
        # Selecting a different page is required if the current page is going to be deleted.
        # So re-selecting the page is required to prevent exceptions. Without this, the document view creates invalid
        # model indices.
        new_page_to_select = max(0, first-1)
        logger.debug(
            f"Currently selected page {currently_selected_page} about to be removed. "
            f"New page to select: {new_page_to_select}")
        document_view.setCurrentIndex(self.document.index(new_page_to_select, 0))

    @Slot(QModelIndex,int,int)
    def on_document_rows_inserted(self, parent: QModelIndex, first: int, _: int):
        if parent.isValid():  # Not interested in card additions
            return
        # When inserting after the current page, the current page can now be moved down.
        self.ui.page_move_down.setEnabled(self._currently_edited_page < first)

    @Slot(QModelIndex,int,int)
    def on_document_rows_removed(self, parent: QModelIndex, first: int, last: int):
        if parent.isValid():  # Not interested in card removals
            return
        # When the current page becomes the first, disable the move up button
        self.ui.page_move_up.setDisabled(self._currently_edited_page-last+first == 0)
        # When the current page becomes the last, disable the move down button
        self.ui.page_move_down.setEnabled(self._currently_edited_page >= self.document.rowCount()-1)

    @Slot()
    def select_first_page(self, loading_in_progress: bool = False, page_to_select: int = 0):
        if not loading_in_progress:
            logger.info("Loading finished. Selecting first page.")
            new_selection = self.document.index(page_to_select, 0)
            self.ui.document_view.selectionModel().select(new_selection, QItemSelectionModel.SelectionFlag.Select)
            self.document.on_ui_selects_new_page(new_selection)

    @Slot(QPersistentModelIndex)
    def on_document_current_page_changed(self, page: QPersistentModelIndex):
        self._currently_edited_page = page.row()
        self._update_page_move_buttons()

    def _update_page_move_buttons(self):
        row = self._currently_edited_page
        row_count = self.document.rowCount()
        ui = self.ui
        ui.page_move_up.setEnabled(row > 0)
        ui.page_move_down.setEnabled(row < row_count-1)

    @Slot()
    def on_page_move_up_clicked(self):
        self.document.apply(ActionMovePage(self._currently_edited_page, self._currently_edited_page - 1))
        self._currently_edited_page -= 1
        self.ui.document_view.setCurrentIndex(self.document.index(self._currently_edited_page, DocumentColumns.Page))
        self._update_page_move_buttons()

    @Slot()
    def on_page_move_down_clicked(self):
        # The API moves cards *before* the given row, so to move one row down,
        # move the current page before the next but one page
        self.document.apply(ActionMovePage(self._currently_edited_page, self._currently_edited_page + 2))
        self._currently_edited_page += 1
        self.ui.document_view.setCurrentIndex(self.document.index(self._currently_edited_page, DocumentColumns.Page))
        self._update_page_move_buttons()


def get_configured_central_widget_layout_class() -> UiType:
    gui_settings = mtg_proxy_printer.settings.settings["gui"]
    configured_layout = gui_settings["central-widget-layout"]
    if configured_layout == "horizontal":
        return Ui_GroupedCentralWidget
    if configured_layout == "columnar":
        return Ui_ColumnarCentralWidget
    return Ui_TabbedCentralWidget
