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


import enum
from unittest.mock import MagicMock

from PyQt5.QtCore import pyqtSlot as Slot, QPersistentModelIndex
from PyQt5.QtGui import QColorConstants, QPainter, QPixmap
from PyQt5.QtWidgets import QWidget

from mtg_proxy_printer.document_controller.page_actions import ActionNewPage
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard, ActionRemoveCards
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.units_and_sizes import CardSizes, CardSize
from mtg_proxy_printer.model.document_page import PageType
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.card import MTGSet, Card
from mtg_proxy_printer.ui.common import load_ui_from_file
from mtg_proxy_printer.logger import get_logger

try:
    from mtg_proxy_printer.ui.generated.page_config_preview_area import Ui_PageConfigPreviewArea
except ModuleNotFoundError:
    Ui_PageConfigPreviewArea = load_ui_from_file("page_config_preview_area")

logger = get_logger(__name__)
del get_logger


class PagesData(enum.Enum):
    def __init__(self, page: int, corner_radius: int, border_width: int):
        self.page = page
        self.corner_radius = corner_radius
        self.border_width = border_width

    REGULAR = 0, 27, 27  # Pixel values empirically determined
    OVERSIZED = 1, 50, 28

    @classmethod
    def from_card_size(cls, size: CardSize):
        return cls.REGULAR if size is CardSizes.REGULAR else cls.OVERSIZED


class PageConfigPreviewArea(QWidget):
    """
    Contains a PageRenderer and widgets to select a number of either regular or oversized cards.
    """
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = ui = Ui_PageConfigPreviewArea()
        ui.setupUi(self)
        self.document = Document(MagicMock(), MagicMock())
        self.regular_card = self._create_card(CardSizes.REGULAR, "Regular-size placeholder")
        self.oversized_card = self._create_card(CardSizes.OVERSIZED, "Oversized placeholder")
        ActionNewPage().apply(self.document)
        ui.preview_area.set_document(self.document)
        self.on_page_layout_changed(self.document.page_layout)
        initial_regular_cards = ui.regular_card_count.maximum()//2
        initial_oversized_cards = ui.oversized_card_count.maximum()//2
        logger.debug(
            f"Initializing document with {initial_regular_cards} regular, "
            f"and {initial_oversized_cards} oversized cards")
        ui.oversized_card_count.setValue(initial_oversized_cards)
        ui.regular_card_count.setValue(initial_regular_cards)
        logger.info(f"Created {self.__class__.__name__} instance")

    @staticmethod
    def _create_card(size: CardSize, name: str):
        data = PagesData.from_card_size(size)
        card_width = round(size.width.magnitude)
        card_height = round(size.height.magnitude)
        image = QPixmap(card_width, card_height)
        image.fill(QColorConstants.Transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColorConstants.Transparent)
        painter.setBrush(QColorConstants.Black)  # The border, as a black, rounded rectangle
        painter.drawRoundedRect(0, 0, card_width, card_height, data.border_width, data.corner_radius)
        painter.setBrush(QColorConstants.Gray)  # The card content, as a simple, gray rectangle
        painter.drawRect(
            data.border_width, data.border_width,
            card_width - 2 * data.border_width, card_height - 2 * data.border_width)
        painter.end()
        return Card(name , MTGSet("", ""), "", "", "", True, "", "", True, size, 0, False, image)


    @Slot(PageLayoutSettings)
    def on_page_layout_changed(self, layout: PageLayoutSettings):
        ui = self.ui
        ui.oversized_card_count.setMaximum(layout.compute_page_card_capacity(PageType.OVERSIZED))
        ui.regular_card_count.setMaximum(layout.compute_page_card_capacity(PageType.REGULAR))

    @Slot(int)
    def on_regular_card_count_valueChanged(self, value: int):
        logger.debug(f"Setting regular card count to {value}")
        self._adjust_card_count_on_page(PagesData.REGULAR.page, value, self.regular_card)

    @Slot(int)
    def on_oversized_card_count_valueChanged(self, value: int):
        logger.debug(f"Setting oversized card count to {value}")
        self._adjust_card_count_on_page(PagesData.OVERSIZED.page, value, self.oversized_card)


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
        self._switch_to_document_page(PagesData.REGULAR.page)

    @Slot()
    def on_oversized_selected_clicked(self):
        logger.debug(f"Use oversized cards for the preview")
        self._switch_to_document_page(PagesData.OVERSIZED.page)

    def _switch_to_document_page(self, page: int):
        document = self.document
        document.currently_edited_page = document.pages[page]
        index = document.index(page,0)
        document.current_page_changed.emit(QPersistentModelIndex(index))
