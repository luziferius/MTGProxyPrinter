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

from PyQt5.QtCore import pyqtSlot, QRectF, QPointF, QSizeF, Qt, QModelIndex
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QColor, QPixmap
import pint

from mtg_proxy_printer.settings import settings
from mtg_proxy_printer.model.document import Page, Document

unit_registry = pint.UnitRegistry()
DPI: pint.Quantity = 300 / unit_registry.inch

__all__ = [
    "PageScene",
    "PageRenderer",
]


class PageScene(QGraphicsScene):
    IMAGE_WIDTH = 63
    IMAGE_HEIGHT = 88

    def __init__(self, draw_background: bool, *args, **kwargs):
        super(PageScene, self).__init__(*args, **kwargs)
        self.background = None
        self.draw_background = draw_background

    @pyqtSlot(QModelIndex)
    def draw_card(self, index: QModelIndex):
        position = self._compute_position_for_image(index)
        image: QPixmap = index.sibling(index.row(), 4).data(Qt.DisplayRole)
        if image is not None:
            pixmap = self.addPixmap(image)
            pixmap.setPos(position)

    @pyqtSlot()
    def redraw(self):
        self.clear()
        if self.draw_background:
            white = QColor("white")
            self.background = self.addRect(0, 0, self.width(), self.height(), white, white)
        if settings["documents"].getboolean("print-cut-marker"):
            self._draw_cut_markers()
        page: Page = self.parent().page
        for index in (page.createIndex(row, 0) for row in range(page.rowCount())):
            self.draw_card(index)

    def _compute_position_for_image(self, index: QModelIndex):
        document = self.get_document()
        cards_per_row = document.compute_cards_per_row()
        column = index.row() % cards_per_row
        row = index.row() // cards_per_row
        spacing_vertical = document.image_spacing_vertical
        spacing_horizontal = document.image_spacing_horizontal

        x_pos = document.margin_left + column * (PageScene.IMAGE_WIDTH + spacing_horizontal)
        y_pos = document.margin_top + row * (PageScene.IMAGE_HEIGHT + spacing_vertical)
        document_settings = settings["documents"]
        scaling_horizontal = self.width() / document_settings.getint("paper-width-mm")
        scaling_vertical = self.height() / document_settings.getint("paper-height-mm")
        return QPointF(
            x_pos * scaling_horizontal,
            y_pos * scaling_vertical,
        )

    def get_document(self) -> Document:
        page: Page = self.parent().page
        document: Document = page.parent()
        return document

    def _draw_cut_markers(self):
        """Draws the optional cut markers that extend to the paper border"""
        line_color = QColor("black")
        document = self.get_document()

        column_count = document.compute_cards_per_row()
        row_count = document.compute_row_count()

        scaling_horizontal = self.width() / document.page_width
        scaling_vertical = self.height() / document.page_height
        for column in range(column_count + 1):
            column_px = scaling_vertical * (
                    document.margin_left +
                    column * (PageScene.IMAGE_WIDTH + document.image_spacing_vertical)
            )
            self.addLine(column_px, 0, column_px, self.height(), line_color)
            if document.image_spacing_vertical and column:
                column_px = 1 + scaling_vertical * (
                        document.margin_left - document.image_spacing_vertical +
                        column * (PageScene.IMAGE_WIDTH + document.image_spacing_vertical)
                )
                self.addLine(column_px, 0, column_px, self.height(), line_color)
        for row in range(row_count + 1):
            row_px = scaling_horizontal * (
                    document.margin_top +
                    row * (PageScene.IMAGE_HEIGHT + document.image_spacing_horizontal)
            )
            self.addLine(0, row_px, self.width(), row_px, line_color)
            if document.image_spacing_horizontal and row:
                row_px = 1 + scaling_horizontal * (
                        document.margin_top - document.image_spacing_horizontal +
                        row * (PageScene.IMAGE_HEIGHT + document.image_spacing_horizontal)
                )
                self.addLine(0, row_px, self.width(), row_px, line_color)


class PageRenderer(QGraphicsView):

    def __init__(self, *args, **kwargs):
        super(PageRenderer, self).__init__(*args, **kwargs)
        self.page = None
        self.setBackgroundBrush(QColor(200, 200, 200))
        self.setScene(PageScene(True, self.get_document_page_size(), self))

    @pyqtSlot(Page)
    def set_page(self, page: Page):
        if page is None:
            self.scene().clear()
        else:
            if self.page is not None:
                self.page.dataChanged.disconnect(self.scene().draw_card)
            self.page = page
            self.page.dataChanged.connect(self.scene().draw_card)
            self.scene().redraw()

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
        self.fitInView(self.scene().sceneRect(), Qt.KeepAspectRatio)
