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
import typing

from PyQt5.QtCore import pyqtSlot, QRectF, QPointF, QSizeF, Qt, QModelIndex, QPersistentModelIndex, QObject
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

    def __init__(self, document: Document, draw_background: bool, scene_rect: QRectF, parent: QObject = None):
        super(PageScene, self).__init__(scene_rect, parent)
        self.document = document
        self.document.rowsInserted.connect(self.on_rows_inserted)
        self.document.rowsRemoved.connect(self.on_rows_removed)
        self.document.rowsAboutToBeRemoved.connect(self.on_rows_about_to_be_removed)
        self.document.rowsMoved.connect(self.on_rows_moved)
        self.document.current_page_changed.connect(self.on_current_page_changed)
        self.document.dataChanged.connect(self.on_data_changed)
        self.selected_page: QPersistentModelIndex = QPersistentModelIndex()
        self.background = None
        self.draw_background = draw_background
        logger.info(f"Created {self.__class__.__name__} instance. Drawing background: {self.draw_background}")

    @pyqtSlot(QPersistentModelIndex)
    def on_current_page_changed(self, selected_page: QPersistentModelIndex):
        logger.debug(f"Current page changed to page {selected_page.row()}, redrawing")
        self.selected_page = selected_page
        self.redraw()

    def _draw_cards(self):
        if not self.selected_page.isValid():
            logger.warning("Got invalid persistent model index. Not drawing cards.")
            return
        index = self.selected_page.sibling(self.selected_page.row(), 0)
        images_to_draw = self.selected_page.model().rowCount(index)
        logger.info(f"Drawing {images_to_draw} cards")
        for row in range(images_to_draw):
            self.draw_card(row)

    def draw_card(self, row: int):
        index = self.selected_page.child(row, PageColumns.Image)
        position = self._compute_position_for_image(index)
        image: QPixmap = index.data(Qt.DisplayRole)
        if image is not None:
            pixmap = self.addPixmap(image)
            pixmap.setTransformationMode(Qt.SmoothTransformation)
            pixmap.setPos(position)

    def on_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex, roles: typing.List[Qt.ItemDataRole]):
        if top_left.parent().row() == self.selected_page.row() and Qt.DisplayRole in roles:
            logger.info("A card on the current page was replaced, redrawing.")
            self.redraw()

    def on_rows_inserted(self, parent: QModelIndex, first: int, last: int):
        if parent.isValid() and self.selected_page.isValid() and parent.row() == self.selected_page.row():
            logger.debug(f"{last-first+1} cards inserted to the currently shown page, drawing them.")
            for new in range(first, last+1):
                self.draw_card(new)

    def on_rows_about_to_be_removed(self, parent: QModelIndex, first: int, last: int):
        if not parent.isValid() and self.selected_page.isValid() and first <= self.selected_page.row() <= last:
            logger.debug("About to delete the currently shown page. Removing the held index and clearing the view.")
            self.selected_page = QPersistentModelIndex()
            self.clear()

    def on_rows_removed(self, parent: QModelIndex, first: int, last: int):
        if parent.isValid() and self.selected_page.isValid() and parent.row() == self.selected_page.row():
            logger.debug(f"Cards {first} to {last} removed from the currently shown page, re-drawing the page.")
            self.redraw()

    def on_rows_moved(self, parent: QModelIndex, start: int, end: int, destination: QModelIndex, row: int):
        if parent.isValid() and self.selected_page.isValid() and parent.row() == self.selected_page.row():
            # Cards moved away are treated as if they were deleted
            logger.debug("Cards moved away from the currently shown page, calling card removal handler.")
            self.on_rows_removed(parent, start, end)
        if destination.isValid() and destination.row() == self.selected_page.row():
            # Moved in cards are treated as if they were added
            logger.debug("Cards moved onto the currently shown page, calling card insertion handler.")
            self.on_rows_inserted(destination, row, row+end-start-1)

    @pyqtSlot()
    def redraw(self):
        if not self.selected_page.isValid():
            logger.warning("Redraw requested, but current page is invalid!")
        logger.info(f"Redraw triggered. Clearing the {self.__class__.__name__}.")
        self.clear()
        if self.draw_background:
            white = QColor("white")
            logger.debug(f"Drawing background rectangle")
            self.background = self.addRect(0, 0, self.width(), self.height(), white, white)
        if settings["documents"].getboolean("print-cut-marker"):
            self._draw_cut_markers()
        self._draw_cards()

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
        logger.info("Document instance received, creating PageScene.")
        self.setScene(PageScene(document, True, self.get_document_page_size(), self))

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
