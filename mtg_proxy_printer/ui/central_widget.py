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

from typing import Union, Type

from PyQt5.QtCore import  pyqtSlot as Slot, QItemSelectionModel, QModelIndex
from PyQt5.QtWidgets import QWidget

import mtg_proxy_printer.app_dirs
import mtg_proxy_printer.settings
from mtg_proxy_printer.model.document import Document
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

UiType = Union[Type[Ui_GroupedCentralWidget], Type[Ui_ColumnarCentralWidget], Type[Ui_TabbedCentralWidget]]


class CentralWidget(QWidget):

    def __init__(self, parent: QWidget = None):
        logger.debug(f"Creating {self.__class__.__name__} instance.")
        super().__init__(parent)
        ui_class = get_configured_central_widget_layout_class()
        logger.debug(f"Using central widget class {ui_class.__name__}")
        self.ui = ui_class()
        self.ui.setupUi(self)
        self.document: Document = None
        logger.info(f"Created {self.__class__.__name__} instance.")

    def set_data(self, document: Document, card_db: CardDatabase, image_db: ImageDatabase):
        logger.debug(f"{self.__class__.__name__} received model instances. Setting up child widgets…")
        self.document = document
        ui = self.ui
        ui.page_card_table_view.set_data(document, card_db)
        ui.page_card_table_view.obtain_card_image.connect(image_db.fill_document_action_image)
        # Have the "delete selected" button enabled iff the current selection is non-empty
        ui.page_card_table_view.changed_selection_is_empty.connect(ui.delete_selected_images_button.setDisabled)
        ui.delete_selected_images_button.clicked.connect(ui.page_card_table_view.delete_selected_images)
        document.rowsAboutToBeRemoved.connect(self.on_document_rows_about_to_be_removed)
        document.loading_state_changed.connect(self.select_first_page)
        ui.page_renderer.set_document(document)
        self._setup_add_card_widget(card_db, image_db)
        self._setup_document_view(document)
        logger.debug(f"{self.__class__.__name__} setup completed")

    def _setup_add_card_widget(self, card_db: CardDatabase, image_db: ImageDatabase):
        self.ui.add_card_widget.set_card_database(card_db)
        self.ui.add_card_widget.request_action.connect(image_db.fill_document_action_image)

    def _setup_document_view(self, document: Document):
        self.ui.document_view.setModel(document)
        # Has to be set up here, because setModel() implicitly creates the QItemSelectionModel
        self.ui.document_view.selectionModel().currentChanged.connect(document.on_ui_selects_new_page)
        self.select_first_page()

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

    @Slot()
    def select_first_page(self, loading_in_progress: bool = False):
        if not loading_in_progress:
            logger.info("Loading finished. Selecting first page.")
            new_selection = self.document.index(0, 0)
            self.ui.document_view.selectionModel().select(new_selection, QItemSelectionModel.SelectionFlag.Select)
            self.document.on_ui_selects_new_page(new_selection)


def get_configured_central_widget_layout_class() -> UiType:
    gui_settings = mtg_proxy_printer.settings.settings["gui"]
    configured_layout = gui_settings["central-widget-layout"]
    if configured_layout == "horizontal":
        return Ui_GroupedCentralWidget
    if configured_layout == "columnar":
        return Ui_ColumnarCentralWidget
    return Ui_TabbedCentralWidget
