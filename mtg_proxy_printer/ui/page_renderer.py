# Copyright (C) 2020-2022 Thomas Hess <thomas.hess@udo.edu>

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

import enum
import typing

from PyQt5.QtCore import pyqtSlot as Slot, QRectF, QPointF, QSizeF, Qt, QModelIndex, QPersistentModelIndex, QObject,\
    pyqtSignal as Signal, QEvent
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QWidget, QAction
from PyQt5.QtGui import QColor, QPixmap, QWheelEvent, QKeySequence, QPalette, QBrush, QResizeEvent
import pint

from mtg_proxy_printer.units_and_sizes import PageType, CardSizes, CardSize, unit_registry, DPI
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.carddb import Card, CardCorner
from mtg_proxy_printer.model.card_list import PageColumns
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


__all__ = [
    "RenderMode",
    "PageScene",
    "PageRenderer",
]


@enum.unique
class ZoomDirection(enum.Enum):
    IN = enum.auto()
    OUT = enum.auto()

    @classmethod
    def from_bool(cls, value: bool, /):
        return cls.IN if value else cls.OUT


@enum.unique
class RenderMode(enum.Enum):
    ON_SCREEN = enum.auto()
    ON_PAPER = enum.auto()


class PageScene(QGraphicsScene):
    """This class implements the low-level rendering of the currently selected page on a blank canvas."""

    scene_size_changed = Signal()

    def __init__(self, document: Document, render_mode: RenderMode, parent: QObject = None):
        """
        :param document: The document instance
        :param render_mode: Specifies the render mode.
          On paper, no background is drawn and cut markers use black.
          On Screen, a background is drawn using the theme’s background color and a high-contrast color for cut markers.
        :param parent: Optional Qt parent object
        """
        super(PageScene, self).__init__(self.get_document_page_size(document), parent)
        self.document = document
        self.document.rowsInserted.connect(self.on_rows_inserted)
        self.document.rowsRemoved.connect(self.on_rows_removed)
        self.document.rowsAboutToBeRemoved.connect(self.on_rows_about_to_be_removed)
        self.document.rowsMoved.connect(self.on_rows_moved)
        self.document.current_page_changed.connect(self.on_current_page_changed)
        self.document.dataChanged.connect(self.on_data_changed)
        self.document.page_type_changed.connect(self.on_page_type_changed)
        self.selected_page: QPersistentModelIndex = QPersistentModelIndex()
        self.background = None
        self.render_mode = render_mode
        logger.info(f"Created {self.__class__.__name__} instance. Render mode: {self.render_mode}")

    @Slot(QPersistentModelIndex)
    def on_current_page_changed(self, selected_page: QPersistentModelIndex):
        """Draws the canvas, when the currently selected page changes."""
        logger.debug(f"Current page changed to page {selected_page.row()}, redrawing")
        self.selected_page = selected_page
        if selected_page.isValid():
            self.redraw()
        else:
            self.clear()

    @Slot()
    def on_settings_changed(self):
        new_page_size = self.get_document_page_size(self.document)
        old_size = self.sceneRect()
        size_changed = old_size != new_page_size
        if size_changed:
            logger.debug("Page size changed. Adjusting PageScene dimensions")
            self.setSceneRect(new_page_size)
        self.redraw()
        if size_changed:
            # Changed paper dimensions very likely caused the page aspect ratio to change. It may no longer fit
            # in the available space or is now too small, so emit a notification to allow the display widget to adjust.
            self.scene_size_changed.emit()

    @staticmethod
    def get_document_page_size(document: Document) -> QRectF:
        height: pint.Quantity = document.page_layout.page_height * unit_registry.millimeter
        width: pint.Quantity = document.page_layout.page_width * unit_registry.millimeter
        page_size = QRectF(
            QPointF(0, 0),
            QSizeF(
                (DPI*width).to_reduced_units().magnitude,
                (DPI*height).to_reduced_units().magnitude
            )
        )
        return page_size

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
            if self.document.page_layout.draw_sharp_corners:
                self._draw_corners(index, position)
            pixmap = self.addPixmap(image)
            pixmap.setTransformationMode(Qt.SmoothTransformation)
            pixmap.setPos(position)

    def _draw_corners(self, index: QModelIndex, position: QPointF):
        card: Card = index.internalPointer().card
        image = card.image_file
        corner_size = QSizeF(50, 50)
        # Needs to offset the corner position by some half pixels to not overlap
        self.addRect(
            QRectF(position + QPointF(0.5, 0.5), corner_size),
            card.corner_color(CardCorner.TOP_LEFT), card.corner_color(CardCorner.TOP_LEFT))
        self.addRect(
            QRectF(position + image.rect().topRight() - QPointF(49.5, -0.5), corner_size),
            card.corner_color(CardCorner.TOP_RIGHT), card.corner_color(CardCorner.TOP_RIGHT))
        self.addRect(
            QRectF(position + image.rect().bottomLeft() - QPointF(-0.5, 49.5), corner_size),
            card.corner_color(CardCorner.BOTTOM_LEFT), card.corner_color(CardCorner.BOTTOM_LEFT))
        self.addRect(
            QRectF(position + image.rect().bottomRight() - QPointF(49.5, 49.5), corner_size),
            card.corner_color(CardCorner.BOTTOM_RIGHT), card.corner_color(CardCorner.BOTTOM_RIGHT))

    @Slot(QModelIndex)
    def on_page_type_changed(self, page: QModelIndex):
        if page.row() == self.selected_page.row():
            self.redraw()

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

    @Slot()
    def redraw(self):
        """Wipes the scene and re-draws everything"""
        if not self.selected_page.isValid():
            logger.warning("Redraw requested, but current page is invalid!")
        logger.info(f"Redraw triggered. Clearing the {self.__class__.__name__}.")
        self.clear()
        if self.render_mode == RenderMode.ON_SCREEN:
            color = self.palette().color(QPalette.Active, QPalette.Base)
            logger.debug(f"Drawing background rectangle")
            self.background = self.addRect(0, 0, self.width(), self.height(), color, color)
        self.setBackgroundBrush(QBrush(QColor("white"), Qt.SolidPattern))
        if self.document.page_layout.draw_cut_markers:
            self._draw_cut_markers()
        self._draw_cards()

    def _compute_position_for_image(self, index: QModelIndex) -> QPointF:
        """Returns the page-absolute position of the top-left pixel of the given image."""
        page_type: PageType = self.selected_page.data(Qt.EditRole).page_type()
        card_size: CardSize = CardSizes.for_page_type(page_type).value
        page_layout = self.document.page_layout
        cards_per_row = page_layout.compute_page_column_count(page_type)
        column = index.row() % cards_per_row
        row = index.row() // cards_per_row
        spacing_vertical = page_layout.image_spacing_vertical
        spacing_horizontal = page_layout.image_spacing_horizontal

        x_pos = page_layout.margin_left + column * (card_size.width + spacing_horizontal)
        y_pos = page_layout.margin_top + row * (card_size.height + spacing_vertical)
        scaling_horizontal = self.width() / page_layout.page_width
        scaling_vertical = self.height() / page_layout.page_height
        return QPointF(
            x_pos * scaling_horizontal + 0.5*column,
            y_pos * scaling_vertical + 0.5*row,
        )

    def _draw_cut_markers(self):
        """Draws the optional cut markers that extend to the paper border"""
        page_type: PageType = self.selected_page.data(Qt.EditRole).page_type()
        if page_type == PageType.MIXED:
            logger.warning("Not drawing cut markers for page with mixed image sizes")
            return
        card_size: CardSize = CardSizes.for_page_type(page_type).value
        line_color = QColor("black") if self.render_mode == RenderMode.ON_PAPER \
            else self.palette().color(QPalette.Active, QPalette.WindowText)
        logger.info(f"Drawing cut markers")
        self._draw_vertical_markers(line_color, card_size)
        self._draw_horizontal_markers(line_color, card_size)

    def _draw_vertical_markers(self, line_color: QColor, card_size: CardSize):
        page_layout = self.document.page_layout
        scaling_horizontal = self.width() / page_layout.page_width
        column_count = page_layout.compute_page_column_count(page_layout)
        if not page_layout.image_spacing_horizontal:
            column_count += 1
        for column in range(column_count):
            column_px = 0.5 * column + scaling_horizontal * (
                    page_layout.margin_left +
                    column * (card_size.width + page_layout.image_spacing_horizontal)
            )
            self._draw_vertical_line(column_px, line_color)
            if page_layout.image_spacing_horizontal:
                offset = 1 + card_size.width * scaling_horizontal
                self._draw_vertical_line(column_px + offset, line_color)
        logger.debug(f"Vertical cut markers drawn")

    def _draw_horizontal_markers(self, line_color: QColor, card_size: CardSize):
        page_layout = self.document.page_layout
        scaling_vertical = self.height() / page_layout.page_height
        row_count = page_layout.compute_page_row_count(page_layout)
        if not page_layout.image_spacing_vertical:
            row_count += 1
        for row in range(row_count):
            row_px = 0.5 * row + scaling_vertical * (
                    page_layout.margin_top +
                    row * (card_size.height + page_layout.image_spacing_vertical)
            )
            self._draw_horizontal_line(row_px, line_color)
            if page_layout.image_spacing_vertical:
                offset = 0.5 + card_size.height * scaling_vertical
                self._draw_horizontal_line(row_px + offset, line_color)
        logger.debug(f"Horizontal cut markers drawn")

    def _draw_vertical_line(self, column_px: int, line_color: QColor):
        self.addLine(column_px, 0, column_px, self.height(), line_color)

    def _draw_horizontal_line(self, row_px: int, line_color: QColor):
        self.addLine(0, row_px, self.width(), row_px, line_color)


class PageRenderer(QGraphicsView):
    """
    This class displays an internally held PageScene instance on screen.
    """
    MAX_UI_ZOOM = 16.0

    def __init__(self, parent: QWidget = None):
        super(PageRenderer, self).__init__(parent=parent)
        self.document: Document = None
        self.automatic_scaling = True
        self.setCursor(Qt.SizeAllCursor)
        self.zoom_in_action = QAction(self)
        self.zoom_in_action.setShortcuts(QKeySequence.keyBindings(QKeySequence.ZoomIn))
        self.zoom_in_action.triggered.connect(lambda: self._perform_zoom_step(ZoomDirection.IN))
        self.zoom_out_action = QAction(self)
        self.zoom_out_action.setShortcuts(QKeySequence.keyBindings(QKeySequence.ZoomOut))
        self.zoom_out_action.triggered.connect(lambda: self._perform_zoom_step(ZoomDirection.OUT))
        self.addActions((self.zoom_in_action, self.zoom_out_action))
        self.setToolTip(
            # TODO Find a better way to handle translation of the Ctrl key in the first line
            f"Use {QKeySequence('Ctrl+A').toString(QKeySequence.NativeText).split('+')[0]}+Mouse wheel to zoom.\n"
            f"Usable keyboard shortcuts are:\n"
            f"Zoom in: {', '.join(shortcut.toString(QKeySequence.NativeText) for shortcut in self.zoom_in_action.shortcuts())}\n"
            f"Zoom out: {', '.join(shortcut.toString(QKeySequence.NativeText) for shortcut in self.zoom_out_action.shortcuts())}"
        )
        self._update_background_brush()
        logger.info(f"Created {self.__class__.__name__} instance.")

    def scene(self) -> PageScene:
        return super().scene()

    def changeEvent(self, event: QEvent) -> None:
        if event.type() in {QEvent.ApplicationPaletteChange, QEvent.PaletteChange}:
            self._update_background_brush()
            self.scene().setPalette(self.palette())
            self.scene().redraw()
            event.accept()
        else:
            super().changeEvent(event)

    def _update_background_brush(self):
        self.setBackgroundBrush(self.palette().color(QPalette.Active, QPalette.Window))

    def set_document(self, document: Document):
        logger.info("Document instance received, creating PageScene.")
        self.document = document
        self.setScene(PageScene(document, RenderMode.ON_SCREEN, self))
        self.scene().scene_size_changed.connect(self.resizeEvent)

    def _perform_zoom_step(self, direction: ZoomDirection):
        scaling_factor = 1.1 if direction is ZoomDirection.IN else 0.9
        if scaling_factor * self.transform().m11() > self.MAX_UI_ZOOM:
            return
        self.automatic_scaling = self.scene_fully_visible(scaling_factor)
        self.setDragMode(QGraphicsView.NoDrag if self.automatic_scaling else QGraphicsView.ScrollHandDrag)
        if self.automatic_scaling:
            self.fitInView(self.scene().sceneRect(), Qt.KeepAspectRatio)
        else:
            # The initial tooltip text showing the zoom options is rather large, so clear it once the user triggered a
            # zoom action for the first time. This is done to un-clutter the area around the mouse cursor.
            self.setToolTip("")
            old_anchor = self.transformationAnchor()
            self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
            self.scale(scaling_factor, scaling_factor)
            self.setTransformationAnchor(old_anchor)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.modifiers() & Qt.ControlModifier:
            direction = ZoomDirection.from_bool(event.angleDelta().y() > 0)
            self._perform_zoom_step(direction)
            event.accept()
            return
        super().wheelEvent(event)

    def resizeEvent(self, event: QResizeEvent = None) -> None:
        if self.automatic_scaling or self.scene_fully_visible():
            self.automatic_scaling = True
            self.setDragMode(QGraphicsView.NoDrag)
            self.fitInView(self.scene().sceneRect(), Qt.KeepAspectRatio)
        if event is not None:
            super().resizeEvent(event)

    def scene_fully_visible(self, additional_scaling_factor: float = 1.0, /) -> bool:
        scale = self.transform().m11() * additional_scaling_factor
        scene_rect = self.sceneRect()
        content_rect = self.contentsRect()
        return round(scene_rect.width()*scale) <= content_rect.width() \
            and round(scene_rect.height()*scale) <= content_rect.height()
