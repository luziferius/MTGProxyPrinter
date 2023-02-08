# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>

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

import collections
import enum
import itertools
import functools
import typing

from PyQt5.QtCore import pyqtSlot as Slot, QRectF, QPointF, QSizeF, Qt, QModelIndex, QPersistentModelIndex, QObject,\
    pyqtSignal as Signal, QEvent
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QWidget, QAction, \
    QGraphicsLineItem, QGraphicsItemGroup, QGraphicsItem, QGraphicsRectItem, QGraphicsPixmapItem
from PyQt5.QtGui import QColor, QWheelEvent, QKeySequence, QPalette, QBrush, QResizeEvent, QPen, QColorConstants
import pint

from mtg_proxy_printer.units_and_sizes import PageType, CardSizes, CardSize, unit_registry, RESOLUTION
from mtg_proxy_printer.model.document_loader import PageLayoutSettings
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
PixelCache = typing.DefaultDict[PageType, typing.List[float]]


@enum.unique
class RenderLayers(enum.Enum):
    BACKGROUND = -3
    CUT_LINES = -2
    CARDS = 0


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


class CutMarkerParameters(typing.NamedTuple):
    card_size: pint.Quantity
    item_count: int
    margin: int
    image_spacing: int


class CardItem(QGraphicsItemGroup):

    def __init__(self, card: Card, document: Document, parent: QGraphicsItem = None):
        super().__init__(parent)
        document.page_layout_changed.connect(self.on_page_layout_changed)
        self.corner_area = QSizeF(50, 50)
        self.card = card
        self.card_pixmap_item = QGraphicsPixmapItem(card.image_file)
        self.card_pixmap_item.setTransformationMode(Qt.SmoothTransformation)
        # A transparent pen reduces the corner size by 0.5 pixels around, lining it up with the pixmap outline
        self.corner_pen = QPen(QColorConstants.Transparent)
        self.corners: typing.List[QGraphicsRectItem] = list(
            self.create_corners(document.page_layout.draw_sharp_corners))
        self._draw_content()
        self.setZValue(RenderLayers.CARDS.value)

    def create_corners(self, draw_corners: bool):
        image = self.card.image_file
        card_height, card_width = image.height(), image.width()
        corner_height, corner_width = self.corner_area.height(), self.corner_area.width()
        card_width = image.width()
        opacity = 255 if draw_corners else 0
        return itertools.starmap(
            self._create_corner, (
                (CardCorner.TOP_LEFT, QPointF(0, 0), opacity),
                (CardCorner.TOP_RIGHT, QPointF(card_width-corner_width, 0), opacity),
                (CardCorner.BOTTOM_LEFT, QPointF(0, card_height-corner_height), opacity),
                (CardCorner.BOTTOM_RIGHT, QPointF(card_width-corner_width, card_height-corner_height), opacity),
            )
        )

    def _create_corner(self, corner: CardCorner, position: QPointF, opacity: float) -> QGraphicsRectItem:
        rect = QGraphicsRectItem(QRectF(QPointF(0, 0), self.corner_area))
        color = self.card.corner_color(corner)
        rect.setPos(position)
        rect.setPen(self.corner_pen)
        rect.setBrush(color)
        rect.setOpacity(opacity)
        return rect

    def on_page_layout_changed(self, new_page_layout: PageLayoutSettings):
        value = 255 if new_page_layout.draw_sharp_corners else 0
        for corner in self.corners:
            corner.setOpacity(value)

    def _draw_content(self):
        for item in self.corners:
            self.addToGroup(item)
        self.addToGroup(self.card_pixmap_item)


def is_card_item(item: QGraphicsItem) -> bool:
    return isinstance(item, CardItem)


def is_cut_line_item(item: QGraphicsItem) -> bool:
    return isinstance(item, QGraphicsLineItem)


class PageScene(QGraphicsScene):
    """This class implements the low-level rendering of the currently selected page on a blank canvas."""

    scene_size_changed = Signal()

    def __init__(self, document: Document, render_mode: RenderMode, parent: QObject = None):
        """
        :param document: The document instance
        :param render_mode: Specifies the render mode.
          On paper, no background is drawn and cut markers use black.
          On Screen, the background uses the theme’s background color and cut markers use a high-contrast color.
        :param parent: Optional Qt parent object
        """
        super(PageScene, self).__init__(self.get_document_page_size(document.page_layout), parent)
        self.document = document
        self.document.rowsInserted.connect(self.on_rows_inserted)
        self.document.rowsRemoved.connect(self.on_rows_removed)
        self.document.rowsAboutToBeRemoved.connect(self.on_rows_about_to_be_removed)
        self.document.rowsMoved.connect(self.on_rows_moved)
        self.document.current_page_changed.connect(self.on_current_page_changed)
        self.document.dataChanged.connect(self.on_data_changed)
        self.document.page_type_changed.connect(self.on_page_type_changed)
        self.document.page_layout_changed.connect(self.on_page_layout_changed)
        self.selected_page: QPersistentModelIndex = self.document.get_current_page_index()
        self.setBackgroundBrush(QBrush(QColorConstants.White, Qt.SolidPattern))
        self.render_mode = render_mode
        background_color = self.get_background_color(render_mode)
        logger.debug(f"Drawing background rectangle")
        self.background = self.addRect(0, 0, self.width(), self.height(), background_color, background_color)
        self.background.setZValue(RenderLayers.BACKGROUND.value)
        self.horizontal_cut_line_locations: PixelCache = collections.defaultdict(list)
        self.vertical_cut_line_locations: PixelCache = collections.defaultdict(list)
        self._update_cut_marker_positions()
        if document.page_layout.draw_cut_markers:
            self.draw_cut_markers()
        logger.info(f"Created {self.__class__.__name__} instance. Render mode: {self.render_mode}")

    def get_background_color(self, render_mode: RenderMode) -> QColor:
        if render_mode is RenderMode.ON_PAPER:
            return QColorConstants.Transparent
        return self.palette().color(QPalette.Active, QPalette.Base)

    def get_cut_marker_color(self, render_mode: RenderMode) -> QColor:
        if render_mode is RenderMode.ON_PAPER:
            return QColorConstants.Black
        return self.palette().color(QPalette.Active, QPalette.WindowText)

    def setPalette(self, palette: QPalette) -> None:
        logger.info("Color palette changed, updating PageScene background and cut line colors.")
        super().setPalette(palette)
        background_color = self.get_background_color(self.render_mode)
        self.background.setPen(background_color)
        self.background.setBrush(background_color)
        cut_line_color = self.get_cut_marker_color(self.render_mode)
        logger.info(f"Number of cut lines: {len(self.cut_lines)}")
        for line in self.cut_lines:
            line.setPen(cut_line_color)

    @property
    def card_items(self) -> typing.List[CardItem]:
        return list(filter(is_card_item, self.items(Qt.AscendingOrder)))

    @property
    def cut_lines(self) -> typing.List[QGraphicsLineItem]:
        return list(filter(is_cut_line_item, self.items(Qt.AscendingOrder)))

    @Slot(QPersistentModelIndex)
    def on_current_page_changed(self, selected_page: QPersistentModelIndex):
        """Draws the canvas, when the currently selected page changes."""
        logger.debug(f"Current page changed to page {selected_page.row()}")
        page_types: typing.Set[PageType] = {
            self.selected_page.data(Qt.UserRole),
            selected_page.data(Qt.UserRole)
        }
        self.selected_page = selected_page

        if PageType.OVERSIZED in page_types and len(page_types) > 1:  # Switching to or from an oversized page
            logger.debug("New page contains cards of different size, re-drawing cut markers")
            self.remove_cut_markers()
            self.draw_cut_markers()

        for item in self.card_items:
            self.removeItem(item)
        if self._is_valid_page_index(selected_page):
            self._draw_cards()

    @Slot(PageLayoutSettings)
    def on_page_layout_changed(self, new_page_layout: PageLayoutSettings):
        new_page_size = self.get_document_page_size(new_page_layout)
        old_size = self.sceneRect()
        size_changed = old_size != new_page_size
        if size_changed:
            logger.debug("Page size changed. Adjusting PageScene dimensions")
            self.setSceneRect(new_page_size)
            self.background.setRect(new_page_size)
        self._update_cut_marker_positions()
        self.remove_cut_markers()
        if new_page_layout.draw_cut_markers:
            self.draw_cut_markers()
        self._compute_position_for_image.cache_clear()
        self.update_card_positions()
        if size_changed:
            # Changed paper dimensions very likely caused the page aspect ratio to change. It may no longer fit
            # in the available space or is now too small, so emit a notification to allow the display widget to adjust.
            self.scene_size_changed.emit()

    @staticmethod
    def get_document_page_size(page_layout: PageLayoutSettings) -> QRectF:
        height: pint.Quantity = page_layout.page_height * unit_registry.millimeter
        width: pint.Quantity = page_layout.page_width * unit_registry.millimeter
        page_size = QRectF(
            QPointF(0, 0),
            QSizeF(
                (RESOLUTION * width).to("pixel").magnitude,
                (RESOLUTION * height).to("pixel").magnitude
            )
        )
        return page_size

    def _draw_cards(self):
        index = self.selected_page.sibling(self.selected_page.row(), 0)
        page_type: PageType = self.selected_page.data(Qt.UserRole)
        images_to_draw = self.selected_page.model().rowCount(index)
        logger.info(f"Drawing {images_to_draw} cards")
        for row in range(images_to_draw):
            self.draw_card(row, page_type)

    def draw_card(self, row: int, page_type: PageType, next_item: CardItem = None):
        index = self.selected_page.child(row, PageColumns.Image)
        position = self._compute_position_for_image(row, page_type)
        if index.data(Qt.DisplayRole) is not None:  # Card has a QPixmap set
            card: Card = index.internalPointer().card
            self.addItem(card_item := CardItem(card, self.document))
            card_item.setPos(position)
            if next_item is not None:
                # See https://doc.qt.io/qt-6/qgraphicsitem.html#sorting
                # "You can call stackBefore() to reorder the list of children.
                # This will directly modify the insertion order."
                # This is required to keep the card order consistent with the model when inserting cards in the
                # middle of the page. This can happen when undoing a card removal. The caller has to supply the
                # item which’s position the new item takes.
                card_item.stackBefore(next_item)

    def update_card_positions(self):
        page_type: PageType = self.selected_page.data(Qt.UserRole)
        for index, card in enumerate(self.card_items):
            card.setPos(self._compute_position_for_image(index, page_type))

    def _is_valid_page_index(self, index: QModelIndex):
        return index.isValid() and not index.parent().isValid() and index.row() < self.document.rowCount()

    @Slot(QModelIndex)
    def on_page_type_changed(self, page: QModelIndex):
        if page.row() == self.selected_page.row():
            self.update_card_positions()
            if self.document.page_layout.draw_cut_markers:
                self.remove_cut_markers()
                self.draw_cut_markers()

    def on_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex, roles: typing.List[Qt.ItemDataRole]):
        if top_left.parent().row() == self.selected_page.row() and Qt.DisplayRole in roles:
            page_type: PageType = top_left.parent().data(Qt.UserRole)
            card_items = self.card_items
            for row in range(top_left.row(), bottom_right.row()+1):
                logger.debug(f"Card {row} on the current page was replaced, replacing image.")
                current_item = card_items[row]
                self.draw_card(row, page_type, current_item)
                self.removeItem(current_item)

    def on_rows_inserted(self, parent: QModelIndex, first: int, last: int):
        if self._is_valid_page_index(parent) and parent.row() == self.selected_page.row():
            inserted_cards = last-first+1
            needs_reorder = first + inserted_cards < self.document.rowCount(parent)
            next_item = self.card_items[first] if needs_reorder else None
            page_type: PageType = self.selected_page.data(Qt.EditRole).page_type()
            logger.debug(f"Added {inserted_cards} cards to the currently shown page, drawing them.")
            for new in range(first, last+1):
                self.draw_card(new, page_type, next_item)
            if needs_reorder:
                logger.debug("Cards added in the middle of the page, re-order existing cards.")
                self.update_card_positions()

    def on_rows_about_to_be_removed(self, parent: QModelIndex, first: int, last: int):
        if not parent.isValid() and first <= self.selected_page.row() <= last:
            logger.debug("About to delete the currently shown page. Removing the held index.")
            self.selected_page = QPersistentModelIndex()

    def on_rows_removed(self, parent: QModelIndex, first: int, last: int):
        if parent.isValid() and parent.row() == self.selected_page.row():
            logger.debug(f"Removing cards {first} to {last} from the current page.")
            for item in self.card_items[first:last+1]:
                self.removeItem(item)
            self.update_card_positions()

    def on_rows_moved(self, parent: QModelIndex, start: int, end: int, destination: QModelIndex, row: int):
        if parent.isValid() and parent.row() == self.selected_page.row():
            # Cards moved away are treated as if they were deleted
            logger.debug("Cards moved away from the currently shown page, calling card removal handler.")
            self.on_rows_removed(parent, start, end)
        if destination.isValid() and destination.row() == self.selected_page.row():
            # Moved in cards are treated as if they were added
            logger.debug("Cards moved onto the currently shown page, calling card insertion handler.")
            self.on_rows_inserted(destination, row, row+end-start-1)

    @functools.lru_cache
    def _compute_position_for_image(self, index_row: int, page_type: PageType) -> QPointF:
        """Returns the page-absolute position of the top-left pixel of the given image."""
        card_size = CardSizes.for_page_type(page_type)
        card_height: int = card_size.height.magnitude
        card_width: int = card_size.width.magnitude
        page_layout = self.document.page_layout

        margin_left = self._mm_to_rounded_px(page_layout.margin_left)
        margin_top = self._mm_to_rounded_px(page_layout.margin_top)

        cards_per_row = page_layout.compute_page_column_count(page_type)
        row, column = divmod(index_row, cards_per_row)

        spacing_vertical = self._mm_to_rounded_px(page_layout.image_spacing_vertical)
        spacing_horizontal = self._mm_to_rounded_px(page_layout.image_spacing_horizontal)

        x_pos = margin_left + column * (card_width + spacing_horizontal)
        y_pos = margin_top + row * (card_height + spacing_vertical)
        return QPointF(
            x_pos,
            y_pos,
        )

    @staticmethod
    def _mm_to_rounded_px(value: int) -> int:
        return round((value*unit_registry.mm*RESOLUTION).to("pixel").magnitude)

    def remove_cut_markers(self):
        for line in self.cut_lines:
            self.removeItem(line)

    def draw_cut_markers(self):
        """Draws the optional cut markers that extend to the paper border"""
        page_type: PageType = self.selected_page.data(Qt.EditRole).page_type()
        if page_type == PageType.MIXED:
            logger.warning("Not drawing cut markers for page with mixed image sizes")
            return
        line_color = self.get_cut_marker_color(self.render_mode)
        logger.info(f"Drawing cut markers")
        self._draw_vertical_markers(line_color, page_type)
        self._draw_horizontal_markers(line_color, page_type)

    def _update_cut_marker_positions(self):
        logger.debug("Updating cut marker positions")
        self.vertical_cut_line_locations.clear()
        self.horizontal_cut_line_locations.clear()
        page_layout = self.document.page_layout
        for page_type in (PageType.UNDETERMINED, PageType.REGULAR, PageType.OVERSIZED):
            card_size: CardSize = CardSizes.for_page_type(page_type)
            self.horizontal_cut_line_locations[page_type] += self._compute_cut_marker_positions(CutMarkerParameters(
                card_size.height, page_layout.compute_page_row_count(page_type),
                page_layout.margin_top, page_layout.image_spacing_horizontal)
            )
            self.vertical_cut_line_locations[page_type] += self._compute_cut_marker_positions(CutMarkerParameters(
                card_size.width, page_layout.compute_page_column_count(page_type),
                page_layout.margin_left, page_layout.image_spacing_vertical
            ))

    def _compute_cut_marker_positions(self, parameters: CutMarkerParameters) \
            -> typing.Generator[float, None, None]:
        margin = self._mm_to_rounded_px(parameters.margin)
        spacing = self._mm_to_rounded_px(parameters.image_spacing)
        card_size: int = parameters.card_size.magnitude
        # Without spacing, draw a line top/left of each row/column.
        # To also draw a line below/right of the last row/column, add a virtual row/column if spacing is zero.
        # With positive spacing, draw a line left/right/above/below *each* row/column.
        for item in range(parameters.item_count + (0 if spacing else 1)):
            pixel_position: float = margin + item*(spacing+card_size)
            yield pixel_position
            if parameters.image_spacing:
                yield pixel_position + card_size

    def _draw_vertical_markers(self, line_color: QColor, page_type: PageType):
        for column_px in self.vertical_cut_line_locations[page_type]:
            self._draw_vertical_line(column_px, line_color)
        logger.debug(f"Vertical cut markers drawn")

    def _draw_horizontal_markers(self, line_color: QColor, page_type: PageType):
        for row_px in self.horizontal_cut_line_locations[page_type]:
            self._draw_horizontal_line(row_px, line_color)
        logger.debug(f"Horizontal cut markers drawn")

    def _draw_vertical_line(self, column_px: float, line_color: QColor):
        line = self.addLine(0, 0, 0, self.height(), line_color)
        line.setX(column_px)
        line.setZValue(RenderLayers.CUT_LINES.value)

    def _draw_horizontal_line(self, row_px: float, line_color: QColor):
        line = self.addLine(0, 0, self.width(), 0, line_color)
        line.setY(row_px)
        line.setZValue(RenderLayers.CUT_LINES.value)


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
            event.accept()
        else:
            super().changeEvent(event)

    def _update_background_brush(self):
        self.setBackgroundBrush(self.palette().color(QPalette.Active, QPalette.Window))

    def set_document(self, document: Document):
        logger.info("Document instance received, creating PageScene.")
        self.document = document
        self.setScene(scene := PageScene(document, RenderMode.ON_SCREEN, self))
        scene.scene_size_changed.connect(self.resizeEvent)

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
