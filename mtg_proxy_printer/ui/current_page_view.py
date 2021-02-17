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

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QTableView

import mtg_proxy_printer.model.document
from mtg_proxy_printer.ui.page_renderer import PageRenderer

from .common import inherits_from_ui_file_with_name

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


class CurrentPageView(*inherits_from_ui_file_with_name("current_page_view")):

    current_page_changed = pyqtSignal(mtg_proxy_printer.model.document.Page)
    window_size_changed = pyqtSignal()
    settings_changed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(CurrentPageView, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.current_page: mtg_proxy_printer.model.document.Page = None
        self.page_renderer: PageRenderer
        self.page_card_table_view: QTableView
        self.window_size_changed.connect(self.page_renderer.on_resize_event_triggered)
        self.delete_selected_images_button.clicked.connect(self.page_renderer.scene().redraw)
        self.current_page_changed.connect(self._on_current_page_changed)
        self.current_page_changed.connect(self.page_card_table_view.setModel)
        self.current_page_changed.connect(lambda: self.page_card_table_view.setColumnHidden(4, True))
        self.current_page_changed.connect(self.page_renderer.set_page)
        self.settings_changed.connect(self.page_renderer.scene().redraw)

    @pyqtSlot(mtg_proxy_printer.model.document.Page)
    def _on_current_page_changed(self, page: mtg_proxy_printer.model.document.Page):
        logger.debug("Current page changed. Loading new page.")
        self.current_page = page

    @pyqtSlot()
    def on_delete_selected_images_button_clicked(self):
        self.page_card_table_view: QTableView
        multi_selection = self.page_card_table_view.selectionModel().selectedRows()
        logger.debug(f"User removes {len(multi_selection)} items from the current page.")
        self.current_page.remove_multi_selection(multi_selection)
