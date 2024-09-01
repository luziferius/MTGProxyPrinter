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

from PyQt5.QtCore import pyqtSlot as Slot, QPersistentModelIndex
from PyQt5.QtGui import QColorConstants, QPainter, QPixmap

from mtg_proxy_printer.document_controller.page_actions import ActionNewPage
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard, ActionRemoveCards
from mtg_proxy_printer.model.document_loader import PageLayoutSettings
from mtg_proxy_printer.units_and_sizes import CardSizes, CardSize
from mtg_proxy_printer.model.document_page import PageType
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.carddb import Card, MTGSet
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
        self.regular_card = self._create_card(CardSizes.REGULAR)
        self.oversized_card = self._create_card(CardSizes.OVERSIZED)
        ActionNewPage().apply(self.document)
        ui.preview_area.set_document(self.document)
        logger.info(f"Created {self.__class__.__name__} instance")

    @staticmethod
    def _create_card(size: CardSize):
        is_oversized = size is CardSizes.OVERSIZED
        corner_radius = 50 if is_oversized else 27  # Pixel values empirically determined
        border_width = 38 if is_oversized else 27
        width = round(size.width.magnitude)
        height = round(size.height.magnitude)
        image = QPixmap(width, height)
        image.fill(QColorConstants.Transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColorConstants.Transparent)
        painter.setBrush(QColorConstants.Black)  # The border, as a black, rounded rectangle
        painter.drawRoundedRect(0, 0, width, height, corner_radius, corner_radius)
        painter.setBrush(QColorConstants.Gray)  # The card content, as a simple, gray rectangle
        painter.drawRect(border_width, border_width, width-2*border_width, height-2*border_width)
        painter.end()
        return Card("" , MTGSet("", ""), "", "", "", True, "", "", True, size is CardSizes.OVERSIZED, 0, False, image)


    @Slot(PageLayoutSettings)
    def on_page_layout_changed(self, layout: PageLayoutSettings):
        ui = self.ui
        ui.oversized_card_count.setMaximum(layout.compute_page_card_capacity(PageType.OVERSIZED))
        ui.regular_card_count.setMaximum(layout.compute_page_card_capacity(PageType.REGULAR))

    @Slot(int)
    def on_regular_card_count_valueChanged(self, value: int):
        logger.debug(f"Setting regular card count to {value}")
        self._adjust_card_count_on_page(0, value, self.regular_card)

    @Slot(int)
    def on_oversized_card_count_valueChanged(self, value: int):
        logger.debug(f"Setting oversized card count to {value}")
        self._adjust_card_count_on_page(1, value, self.oversized_card)


    def _adjust_card_count_on_page(self, page: int, new_count: int, card: Card):
        document = self.document
        previous_value = document.rowCount(document.index(page, 0))
        if previous_value > new_count:
            count = previous_value - new_count
            logger.debug(f"Removing {count} preview card(s) from page {page}.")
            ActionRemoveCards(range(new_count, previous_value), page).apply(document)
        else:
            count = new_count - previous_value
            logger.debug(f"Adding {count} preview card(s) to page {page}")
            ActionAddCard(card, count, target_page=page).apply(document)

    @Slot()
    def on_regular_size_selected_clicked(self):
        logger.debug(f"Use regular cards for the preview")
        self._switch_to_document_page(0)

    @Slot()
    def on_oversized_selected_clicked(self):
        logger.debug(f"Use oversized cards for the preview")
        self._switch_to_document_page(1)

    def _switch_to_document_page(self, page: int):
        document = self.document
        document.currently_edited_page = document.pages[page]
        index = document.index(page,0)
        document.current_page_changed.emit(QPersistentModelIndex(index))