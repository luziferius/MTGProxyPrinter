# Copyright (C) 2020 Thomas Hess <thomas.hess@udo.edu>

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

import mtg_proxy_printer.model.document
from mtg_proxy_printer.ui.page_renderer import PageRenderer

from .common import inherits_from_ui_file_with_name


class CurrentPageView(*inherits_from_ui_file_with_name("current_page_view")):

    current_page_changed = pyqtSignal(mtg_proxy_printer.model.document.Page)
    card_added = pyqtSignal()
    window_size_changed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(CurrentPageView, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.current_page: mtg_proxy_printer.model.document.Page = None
        self.page_renderer: PageRenderer
        self.window_size_changed.connect(self.page_renderer.on_resize_event_triggered)

        self.current_page_changed.connect(self._on_current_page_changed)
        self.current_page_changed.connect(self.page_card_table_view.setModel)
        self.current_page_changed.connect(self.page_renderer.set_page)

    @pyqtSlot(mtg_proxy_printer.model.document.Page)
    def _on_current_page_changed(self, page: mtg_proxy_printer.model.document.Page):
        self.current_page = page



