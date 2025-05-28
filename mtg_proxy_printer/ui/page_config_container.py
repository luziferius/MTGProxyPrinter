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


from functools import partial

from PyQt5.QtWidgets import QWidget

from mtg_proxy_printer.ui.common import load_ui_from_file
from mtg_proxy_printer.logger import get_logger

try:
    from mtg_proxy_printer.ui.generated.page_config_container import Ui_PageConfigContainer
except ModuleNotFoundError:
    Ui_PageConfigContainer = load_ui_from_file("page_config_container")

logger = get_logger(__name__)
del get_logger


class PageConfigContainer(QWidget):
    """
    Contains a PageConfigWidget and a PageConfigPreviewArea in a side-by-side configuration.
    """
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = ui = Ui_PageConfigContainer()
        ui.setupUi(self)

        preview_area = ui.page_config_preview_area
        config_widget = ui.page_config_widget

        page_layout_changed = config_widget.page_layout_changed
        page_layout_changed.connect(partial(setattr, preview_area.document, "page_layout"))
        page_layout_changed.connect(preview_area.document.page_layout_changed)
        page_layout_changed.connect(preview_area.on_page_layout_changed)

        config_widget.ui.show_preview_button.toggled.connect(preview_area.setVisible)
        logger.info(f"Created {self.__class__.__name__} instance")
