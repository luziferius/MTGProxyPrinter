# Copyright (C) 2020-2024 Thomas Hess <thomas.hess@udo.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from unittest.mock import MagicMock

from mtg_proxy_printer.model.document_loader import PageLayoutSettings
from mtg_proxy_printer.units_and_sizes import CardSizes
from mtg_proxy_printer.model.document_page import PageType
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.ui.common import load_ui_from_file
from mtg_proxy_printer.logger import get_logger

from PyQt5.QtWidgets import QWidget

try:
    from mtg_proxy_printer.ui.generated.page_config_preview_area import Ui_PageConfigPreviewArea
except ModuleNotFoundError:
    Ui_PageConfigPreviewArea = load_ui_from_file("page_config_preview_area")

logger = get_logger(__name__)
del get_logger


class PageConfigPreviewArea(QWidget):
    """
    Contains a PageRenderer and widgets to select a number of either regular or oversized cards.
    """
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = ui = Ui_PageConfigPreviewArea()
        ui.setupUi(self)
        self.document = Document(MagicMock(), MagicMock())
        ui.preview_area.set_document(self.document)
        logger.info(f"Created {self.__class__.__name__} instance")

    def on_page_layout_changed(self, layout: PageLayoutSettings):
        ui = self.ui
        ui.oversized_card_count.setMaximum(layout.compute_page_card_capacity(PageType.OVERSIZED))
        ui.regular_card_count.setMaximum(layout.compute_page_card_capacity(PageType.REGULAR))
