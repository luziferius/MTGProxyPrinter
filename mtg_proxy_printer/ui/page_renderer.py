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

from PyQt5.QtCore import pyqtSlot, QRectF, QPointF, QSizeF, Qt, QModelIndex, QPersistentModelIndex
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QColor, QPixmap
import pint

from mtg_proxy_printer.settings import settings
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.card_list import PageColumns
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

unit_registry = pint.UnitRegistry()
DPI: pint.Quantity = 300 / unit_registry.inch

__all__ = [
    "PageScene",
    "PageRenderer",
]


class PageScene(QGraphicsScene):
    IMAGE_WIDTH = 63
    IMAGE_HEIGHT = 88

    def __init__(self, document: Document, draw_background: bool, *args, **kwargs):
        super(PageScene, self).__init__(*args, **kwargs)
        self.document = document
        self.selected_page: QPersistentModelIndex = QPersistentModelIndex()
        self.background = None
        self.draw_background = draw_background
        logger.info(f"Created {self.__class__.__name__} instance. Drawing background: {self.draw_background}")

    def on_current_page_changed(self, selected_page: QPersistentModelIndex):
        logger.debug("Current page changed, redrawing")
        self.selected_page = selected_page
        self.redraw()

    def draw_cards(self):
        if not self.selected_page.isValid():
            logger.warning("Got invalid persistent model index. Not drawing cards.")
            return
        images_to_draw = self.selected_page.model().rowCount(self.selected_page)
        logger.info(f"Drawing {images_to_draw} cards")
        for row in range(images_to_draw):
            index = self.selected_page.child(row, PageColumns.Image)
            position = self._compute_position_for_image(index)
            image: QPixmap = index.data(Qt.DisplayRole)
            if image is not None:
                pixmap = self.addPixmap(image)
                pixmap.setTransformationMode(Qt.SmoothTransformation)
                pixmap.setPos(position)

    @pyqtSlot()
    def redraw(self):
        logger.info(f"Redraw triggered. Clearing the {self.__class__.__name__}.")
        self.clear()
        if self.draw_background:
            white = QColor("white")
            logger.debug(f"Drawing background rectangle")
            self.background = self.addRect(0, 0, self.width(), self.height(), white, white)
        if settings["documents"].getboolean("print-cut-marker"):
            self._draw_cut_markers()
        self.draw_cards()

    def _compute_position_for_image(self, index: QModelIndex):
        cards_per_row = self.document.compute_page_column_count()
        column = index.row() % cards_per_row
        row = index.row() // cards_per_row
        spacing_vertical = self.document.image_spacing_vertical
        spacing_horizontal = self.document.image_spacing_horizontal

        x_pos = self.document.margin_left + column * (PageScene.IMAGE_WIDTH + spacing_horizontal)
        y_pos = self.document.margin_top + row * (PageScene.IMAGE_HEIGHT + spacing_vertical)
        document_settings = settings["documents"]
        scaling_horizontal = self.width() / document_settings.getint("paper-width-mm")
        scaling_vertical = self.height() / document_settings.getint("paper-height-mm")
        return QPointF(
            x_pos * scaling_horizontal,
            y_pos * scaling_vertical,
        )

    def _draw_cut_markers(self):
        """Draws the optional cut markers that extend to the paper border"""
        line_color = QColor("black")
        logger.info(f"Drawing cut markers")
        self._draw_vertical_markers(line_color)
        self._draw_horizontal_markers(line_color)

    def _draw_vertical_markers(self, line_color):
        scaling_horizontal = self.width() / self.document.page_width
        column_count = self.document.compute_page_column_count()
        if not self.document.image_spacing_horizontal:
            column_count += 1
        for column in range(column_count):
            column_px = scaling_horizontal * (
                    self.document.margin_left +
                    column * (PageScene.IMAGE_WIDTH + self.document.image_spacing_horizontal)
            )
            self._draw_vertical_line(column_px, line_color)
            if self.document.image_spacing_horizontal:
                offset = 1 + PageScene.IMAGE_WIDTH * scaling_horizontal
                self._draw_vertical_line(column_px + offset, line_color)
        logger.debug(f"Vertical cut markers drawn")

    def _draw_horizontal_markers(self, line_color):
        scaling_vertical = self.height() / self.document.page_height
        row_count = self.document.compute_page_row_count()
        if not self.document.image_spacing_vertical:
            row_count += 1
        for row in range(row_count):
            row_px = scaling_vertical * (
                    self.document.margin_top +
                    row * (PageScene.IMAGE_HEIGHT + self.document.image_spacing_vertical)
            )
            self._draw_horizontal_line(row_px, line_color)
            if self.document.image_spacing_vertical:
                offset = 1 + PageScene.IMAGE_HEIGHT * scaling_vertical
                self._draw_horizontal_line(row_px + offset, line_color)
        logger.debug(f"Horizontal cut markers drawn")

    def _draw_vertical_line(self, column_px: int, line_color: QColor):
        self.addLine(column_px, 0, column_px, self.height(), line_color)

    def _draw_horizontal_line(self, row_px: int, line_color: QColor):
        self.addLine(0, row_px, self.width(), row_px, line_color)


class PageRenderer(QGraphicsView):

    def __init__(self, *args, **kwargs):
        super(PageRenderer, self).__init__(*args, **kwargs)
        self.setBackgroundBrush(QColor(200, 200, 200))
        logger.info(f"Created {self.__class__.__name__} instance.")

    def set_document(self, document: Document):
        self.setScene(PageScene(document, True, self.get_document_page_size(), self))

    @pyqtSlot(QPersistentModelIndex)
    def on_current_page_changed(self, page: QPersistentModelIndex):
        self.scene().on_current_page_changed(page)

    @staticmethod
    def get_document_page_size() -> QRectF:
        document_settings = settings["documents"]
        height: pint.Quantity = document_settings.getint("paper-height-mm") * unit_registry.millimeter
        width: pint.Quantity = document_settings.getint("paper-width-mm") * unit_registry.millimeter
        page_size = QRectF(
            QPointF(0, 0),
            QSizeF(
                (DPI*width).to_reduced_units().to_tuple()[0],
                (DPI*height).to_reduced_units().to_tuple()[0]
            )
        )
        return page_size

    @pyqtSlot()
    def on_resize_event_triggered(self):
        logger.debug("Resize event: Scaling the page view to fit.")
        self.fitInView(self.scene().sceneRect(), Qt.KeepAspectRatio)
