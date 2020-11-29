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


class PageScene(QGraphicsScene):
    IMAGE_WIDTH: pint.Quantity = unit_registry("63 millimeter")
    IMAGE_HEIGHT: pint.Quantity = unit_registry("88 millimeter")

    def __init__(self, *args, **kwargs):
        super(PageScene, self).__init__(*args, **kwargs)
        self.background = None

    @pyqtSlot(QModelIndex)
    def draw_card(self, index: QModelIndex):
        position = self._compute_position_for_image(index)
        image: QPixmap = index.sibling(index.row(), 4).data(Qt.DisplayRole)
        pixmap = self.addPixmap(image)
        pixmap.setPos(position)

    @pyqtSlot()
    def redraw(self):
        self.clear()
        white = QColor("white")
        self.background = self.addRect(0, 0, self.width(), self.height(), white, white)
        page: Page = self.parent().page
        for index in (page.createIndex(row, 0) for row in range(page.rowCount())):
            self.draw_card(index)

    def _compute_position_for_image(self, index: QModelIndex):
        document = self.get_document()
        cards_per_row = document.compute_cards_per_row()
        column = index.row() % cards_per_row
        row = index.row() // cards_per_row
        spacing_vertical = document.image_spacing_vertical * unit_registry.millimeter
        spacing_horizontal = document.image_spacing_horizontal * unit_registry.millimeter

        x_pos = document.margin_left * unit_registry.millimeter + column * (PageScene.IMAGE_WIDTH + spacing_horizontal)
        y_pos = document.margin_top * unit_registry.millimeter + row * (PageScene.IMAGE_HEIGHT + spacing_vertical)
        return QPointF(
            (x_pos * DPI).to_reduced_units().to_tuple()[0],
            (y_pos * DPI).to_reduced_units().to_tuple()[0],
        )

    def get_document(self) -> Document:
        page: Page = self.parent().page
        document: Document = page.parent()
        return document


class PageRenderer(QGraphicsView):

    def __init__(self, *args, **kwargs):
        super(PageRenderer, self).__init__(*args, **kwargs)
        self.page = None
        self.setBackgroundBrush(QColor(200, 200, 200))
        self.setScene(PageScene(self._get_document_size(), self))

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
    def _get_document_size() -> QRectF:
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
