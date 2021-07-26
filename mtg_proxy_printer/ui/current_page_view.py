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

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QPersistentModelIndex
from PyQt5.QtWidgets import QTableView

from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.ui.page_renderer import PageRenderer

from .common import inherits_from_ui_file_with_name

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger
__all__ = [
    "CurrentPageView",
]


class CurrentPageView(*inherits_from_ui_file_with_name("current_page_view")):

    window_size_changed = pyqtSignal()
    settings_changed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(CurrentPageView, self).__init__(*args, **kwargs)
        self.setupUi(self)
        logger.info(f"Created {self.__class__.__name__} instance.")

    def set_document(self, document: Document):
        self._setup_page_renderer(document)
        self.page_card_table_view.setModel(document)

    def on_current_page_changed(self, new_page: QPersistentModelIndex):
        self.page_card_table_view: QTableView
        self.page_card_table_view.clearSelection()
        self.page_card_table_view.setRootIndex(new_page.sibling(new_page.row(), new_page.column()))
        self.page_card_table_view.setColumnHidden(4, True)
        self.page_renderer.on_current_page_changed(new_page)

    def _setup_page_renderer(self, document: Document):
        self.page_renderer: PageRenderer
        self.page_renderer.set_document(document)
        self.window_size_changed.connect(self.page_renderer.on_resize_event_triggered)
        self.delete_selected_images_button.clicked.connect(self.page_renderer.scene().redraw)
        self.settings_changed.connect(self.page_renderer.scene().redraw)

    @pyqtSlot()
    def on_delete_selected_images_button_clicked(self):
        self.page_card_table_view: QTableView
        multi_selection = self.page_card_table_view.selectionModel().selectedRows()
        logger.debug(f"User removes {len(multi_selection)} items from the current page.")
        self.page_card_table_view.model().remove_card_multi_selection(multi_selection)
