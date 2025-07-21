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

import collections
import enum
import functools
import itertools
import typing

from PyQt5.QtCore import Qt, QSizeF, QPointF, QRectF, pyqtSignal as Signal, QObject, pyqtSlot as Slot, \
    QPersistentModelIndex, QModelIndex, QRect, QPoint, QSize
from PyQt5.QtGui import QPen, QColorConstants, QColor, QPalette, QFontMetrics, QPixmap, QTransform, QPolygonF
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsItem, QGraphicsPixmapItem, QGraphicsRectItem, \
    QGraphicsLineItem, QGraphicsSimpleTextItem, QGraphicsScene, QGraphicsPolygonItem

from mtg_proxy_printer.model.card import CardCorner, AnyCardType
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.document_page import PageColumns
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.settings import settings
from mtg_proxy_printer.units_and_sizes import PageType, unit_registry, distance_to_rounded_px, CardSizes, CardSize, \
    QuantityT
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

PixelCache = typing.DefaultDict[PageType, typing.List[float]]
ItemDataRole = Qt.ItemDataRole
ColorGroup = QPalette.ColorGroup
ColorRole = QPalette.ColorRole
SortOrder = Qt.SortOrder

ZERO_WIDTH = 0 * unit_registry.mm
point = unit_registry.point
degree = unit_registry.degree
pixel = unit_registry.pixel


@enum.unique
class RenderLayers(enum.IntEnum):
    BACKGROUND = -5
    CUT_LINES = enum.auto()
    BLEEDS = enum.auto()
    CORNERS = enum.auto()
    TEXT = enum.auto()
    CARDS = enum.auto()
    WATERMARK = enum.auto()


@enum.unique
class RenderMode(enum.Flag):
    ON_SCREEN = enum.auto()
    ON_PAPER = enum.auto()
    IMPLICIT_MARGINS = enum.auto()


@enum.unique
class BleedOrientation(enum.Enum):
    HORIZONTAL = enum.auto()
    VERTICAL = enum.auto()


class CutMarkerParameters(typing.NamedTuple):
    total_space: QuantityT
    card_size: QuantityT
    item_count: int
    margin: QuantityT
    image_spacing: QuantityT


class CardBleedItem(QGraphicsPixmapItem):

    def __init__(self, image: QPixmap, rect: QRect, pos: QPoint = QPoint(0, 0), parent=None):
        self._image = pixmap = image.copy(rect)
        super().__init__(pixmap, parent)
        self.orientation = BleedOrientation.HORIZONTAL \
            if rect.height() < rect.width() \
            else BleedOrientation.VERTICAL
        self.sign = 1 - 2 * (
            # Grow up, if a horizontal bleed is at the top
            (self.orientation == BleedOrientation.HORIZONTAL and rect.top() < image.height() / 2)
            or  # Grow left, if a vertical bleed is at the left image side
            (self.orientation == BleedOrientation.VERTICAL and rect.left() < image.width() / 2)
        )
        self.setPos(pos)
        self.setZValue(RenderLayers.BLEEDS.value)

    def update_bleed_size(self, size_px: int):
        transformation = self.transform()
        transformation.reset()
        sx, sy = (self.sign*size_px, 1.0) \
            if self.orientation == BleedOrientation.VERTICAL \
            else (1.0, self.sign*size_px)
        transformation.scale(sx, sy)
        self.setTransform(transformation, False)
        # Some renderers do draw zero-width elements as faint lines, so set zero-width bleeds to be transparent
        self.setOpacity(size_px > 0)


class CardBleedCornerItem(QGraphicsPolygonItem):
    PEN = QPen(QColorConstants.Transparent)

    def __init__(self, card: AnyCardType, corner: CardCorner):
        super().__init__()
        self.corner_length = 50 if card.is_oversized else 32
        transform = QTransform()
        width = card.image_file.width()
        height = card.image_file.height()
        if corner == CardCorner.TOP_RIGHT:
            transform.scale(-1, 1)
            self.setPos(width, 0)
        elif corner == CardCorner.BOTTOM_LEFT:
            transform.scale(1, -1)
            self.setPos(0, height)
        elif corner == CardCorner.BOTTOM_RIGHT:
            transform.scale(-1, -1)
            self.setPos(width, height)
        self.setTransform(transform, False)
        self.setPen(self.PEN)
        self.setBrush(card.corner_color(corner))
        self.setZValue(RenderLayers.BLEEDS.value+0.1)

    def update_bleed_size(self, h_px: int, v_px: int):
        left = -v_px
        top = -h_px
        bottom = self.corner_length
        right = self.corner_length
        self.setPolygon(QPolygonF((
            QPointF(left, top), QPointF(right, top), QPointF(right, top+h_px),
            QPointF(left+v_px, top+h_px),
            QPointF(left+v_px, bottom),
            QPointF(left, bottom), QPointF(left, top)
        )))
        # Some renderers do draw zero-width elements as faint lines,
        # so set zero-width bleeds to be transparent
        self.setOpacity(h_px > 0 or v_px > 0)


class NeighborsPresent(typing.NamedTuple):
    top: bool
    bottom: bool
    left: bool
    right: bool


class CardBleeds(typing.NamedTuple):
    top: CardBleedItem
    bottom: CardBleedItem
    left: CardBleedItem
    right: CardBleedItem

    top_left: CardBleedCornerItem
    top_right: CardBleedCornerItem
    bottom_left: CardBleedCornerItem
    bottom_right: CardBleedCornerItem

    @classmethod
    def from_card(cls, card: AnyCardType) -> "CardBleeds":
        pixmap = card.image_file
        width = pixmap.width()
        height = pixmap.height()
        h_size = QSize(width, 1)
        v_size = QSize(1, height)
        bleeds = cls(
            CardBleedItem(pixmap, QRect(QPoint(0, 1), h_size)),
            CardBleedItem(pixmap, QRect(QPoint(0, height - 1), h_size), QPoint(0, height)),
            CardBleedItem(pixmap, QRect(QPoint(1, 0), v_size)),
            CardBleedItem(pixmap, QRect(QPoint(width - 1, 0), v_size), QPoint(width, 0)),

            CardBleedCornerItem(card, CardCorner.TOP_LEFT),
            CardBleedCornerItem(card, CardCorner.TOP_RIGHT),
            CardBleedCornerItem(card, CardCorner.BOTTOM_LEFT),
            CardBleedCornerItem(card, CardCorner.BOTTOM_RIGHT),
        )
        bleeds.update_bleeds(0, 0, 0, 0)
        return bleeds

    def update_bleeds(self, top: int, bottom: int, left: int, right: int):
        self.top.update_bleed_size(top)
        self.bottom.update_bleed_size(bottom)
        self.left.update_bleed_size(left)
        self.right.update_bleed_size(right)

        self.top_left.update_bleed_size(top, left)
        self.top_right.update_bleed_size(top, right)
        self.bottom_left.update_bleed_size(bottom, left)
        self.bottom_right.update_bleed_size(bottom, right)


class CardItem(QGraphicsItemGroup):

    CORNER_SIZE_PX = 50

    def __init__(self, index: QModelIndex, document: Document, parent: QGraphicsItem = None):
        super().__init__(parent)
        document.page_layout_changed.connect(self.on_page_layout_changed)
        card: AnyCardType = index.data(ItemDataRole.UserRole)
        self.index = QPersistentModelIndex(index)
        self.card_pixmap_item = self._create_pixmap_item(card)
        self.watermark_item = self._create_watermark(document)
        self.bleeds = CardBleeds.from_card(card)
        # A transparent pen reduces the corner size by 0.5 pixels around, lining it up with the pixmap outline
        self.corner_pen = QPen(QColorConstants.Transparent)
        self.corners = self.create_corners(card, document.page_layout.draw_sharp_corners)
        self._draw_content()
        self.setZValue(RenderLayers.CARDS.value)

    @staticmethod
    def _create_pixmap_item(card: AnyCardType):
        item = QGraphicsPixmapItem(card.image_file)
        item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        return item

    def _create_watermark(self, document: Document) -> QGraphicsSimpleTextItem:
        page_layout = document.page_layout
        item = QGraphicsSimpleTextItem("")
        item.setZValue(RenderLayers.WATERMARK.value)
        self._update_watermark(item, page_layout)
        return item

    def create_corners(self, card: AnyCardType, draw_corners: bool) -> typing.List[QGraphicsRectItem]:
        image = card.image_file
        card_height, card_width = image.height(), image.width()
        card_width = image.width()
        left, right = 0, card_width-self.CORNER_SIZE_PX
        top, bottom = 0, card_height-self.CORNER_SIZE_PX
        return [
            self._create_corner(card, CardCorner.TOP_LEFT, QPointF(left, top), draw_corners),
            self._create_corner(card, CardCorner.TOP_RIGHT, QPointF(right, top), draw_corners),
            self._create_corner(card, CardCorner.BOTTOM_LEFT, QPointF(left, bottom), draw_corners),
            self._create_corner(card, CardCorner.BOTTOM_RIGHT, QPointF(right, bottom), draw_corners),
        ]

    def _create_corner(self, card: AnyCardType, corner: CardCorner, position: QPointF, opaque: bool) -> QGraphicsRectItem:
        rect = QGraphicsRectItem(0, 0, self.CORNER_SIZE_PX, self.CORNER_SIZE_PX)
        color = card.corner_color(corner)
        rect.setPos(position)
        rect.setPen(self.corner_pen)
        rect.setBrush(color)
        rect.setOpacity(opaque)
        rect.setZValue(RenderLayers.CORNERS.value)
        return rect

    def on_page_layout_changed(self, new_page_layout: PageLayoutSettings):
        for corner in self.corners:
            corner.setOpacity(new_page_layout.draw_sharp_corners)
        self._update_watermark(self.watermark_item, new_page_layout)

    @staticmethod
    def _update_watermark(item: QGraphicsSimpleTextItem, page_layout: PageLayoutSettings):
        # TODO: This runs the unit conversions and font editing for each item on the page.
        #  Check if this is a performance issue. If so, move this into the PageScene
        item.setText(page_layout.watermark_text)
        item.setBrush(page_layout.watermark_color)
        font = item.font()
        font.setPointSizeF(page_layout.watermark_font_size.to(point).magnitude)
        item.setFont(font)
        item.setX(page_layout.watermark_pos_x.to(pixel, "print").magnitude)
        item.setY(page_layout.watermark_pos_y.to(pixel, "print").magnitude)
        item.setRotation(page_layout.watermark_angle.to(degree).magnitude)

    def _draw_content(self):
        items = itertools.chain(self.corners, self.bleeds, [self.card_pixmap_item, self.watermark_item])
        for item in items:
            self.addToGroup(item)


def is_card_item(item: QGraphicsItem) -> bool:
    return isinstance(item, CardItem)


def is_cut_line_item(item: QGraphicsItem) -> bool:
    return isinstance(item, QGraphicsLineItem)


def is_text_item(item: QGraphicsItem) -> bool:
    return isinstance(item, QGraphicsSimpleTextItem)


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
        self.render_mode = render_mode
        page_layout = document.page_layout
        super().__init__(self.get_document_page_size(page_layout), parent)
        self.document = document
        self._connect_document_signals(document)
        self.selected_page = self.document.get_current_page_index()
        self.row_count = self.column_count = 1
        self._update_row_and_column_counts(document)
        background_color = self.get_background_color(render_mode)
        logger.debug(f"Drawing background rectangle")
        self.background = self.addRect(0, 0, self.width(), self.height(), background_color, background_color)
        self.background.setZValue(RenderLayers.BACKGROUND.value)
        self.horizontal_cut_line_locations: PixelCache = collections.defaultdict(list)
        self.vertical_cut_line_locations: PixelCache = collections.defaultdict(list)
        self._update_cut_marker_positions()
        self.document_title_text = self._create_text_item()
        self.page_number_text = self._create_text_item()
        self._update_text_items(page_layout)
        if page_layout.draw_cut_markers:
            self.draw_cut_markers()
        logger.info(f"Created {self.__class__.__name__} instance. Render mode: {render_mode}")
        
    def _connect_document_signals(self, document: Document):
        document.rowsInserted.connect(self.on_rows_inserted)
        document.rowsRemoved.connect(self.on_rows_removed)
        document.rowsAboutToBeRemoved.connect(self.on_rows_about_to_be_removed)
        document.rowsMoved.connect(self.on_rows_moved)
        document.current_page_changed.connect(self.on_current_page_changed)
        document.dataChanged.connect(self.on_data_changed)
        document.page_type_changed.connect(self.on_page_type_changed)
        document.page_layout_changed.connect(self.on_page_layout_changed)

    def _update_row_and_column_counts(self, document: Document):
        page_type = document.currently_edited_page.page_type()
        layout = document.page_layout
        self.column_count = layout.compute_page_column_count(page_type)
        self.row_count = layout.compute_page_row_count(page_type)
        self._compute_position_for_image.cache_clear()

    @staticmethod
    def _create_text_item(font_size: float = 40) -> QGraphicsSimpleTextItem:
        item = QGraphicsSimpleTextItem()
        font = item.font()
        font.setPointSizeF(font_size)
        item.setFont(font)
        return item

    def get_background_color(self, render_mode: RenderMode) -> QColor:
        if RenderMode.ON_PAPER in render_mode:
            return QColorConstants.Transparent
        return self.palette().color(ColorGroup.Active, ColorRole.Base)

    def get_cut_marker_color(self, render_mode: RenderMode) -> QColor:
        if RenderMode.ON_PAPER in render_mode:
            return QColorConstants.Black
        return self.palette().color(ColorGroup.Active, ColorRole.WindowText)

    def get_text_color(self, render_mode: RenderMode) -> QColor:
        if RenderMode.ON_PAPER in render_mode:
            return QColorConstants.Black
        return self.palette().color(ColorGroup.Active, ColorRole.WindowText)

    def setPalette(self, palette: QPalette) -> None:
        logger.info("Color palette changed, updating PageScene background and cut line colors.")
        super().setPalette(palette)
        background_color = self.get_background_color(self.render_mode)
        self.background.setPen(background_color)
        self.background.setBrush(background_color)
        cut_line_color = self.get_cut_marker_color(self.render_mode)
        text_color = self.get_text_color(self.render_mode)
        logger.info(f"Number of cut lines: {len(self.cut_lines)}")
        for line in self.cut_lines:
            line.setPen(cut_line_color)
        for item in self.text_items:
            item.setBrush(text_color)

    @property
    def x_offset(self) -> int:
        return 0 if RenderMode.ON_SCREEN in self.render_mode \
            else distance_to_rounded_px(settings["printer"].get_quantity("horizontal-offset"))

    @property
    def card_items(self) -> typing.List[CardItem]:
        return list(filter(is_card_item, self.items(SortOrder.AscendingOrder)))

    @property
    def cut_lines(self) -> typing.List[QGraphicsLineItem]:
        return list(filter(is_cut_line_item, self.items(SortOrder.AscendingOrder)))

    @property
    def text_items(self) -> typing.List[QGraphicsSimpleTextItem]:
        return list(filter(is_text_item, self.items(SortOrder.AscendingOrder)))

    @Slot(QPersistentModelIndex)
    def on_current_page_changed(self, selected_page: QPersistentModelIndex):
        """Draws the canvas, when the currently selected page changes."""
        logger.debug(f"Current page changed to page {selected_page.row()}")
        page_types: typing.Set[PageType] = {
            self.selected_page.data(ItemDataRole.UserRole),
            selected_page.data(ItemDataRole.UserRole)
        }
        self.selected_page = selected_page

        if PageType.OVERSIZED in page_types and len(page_types) > 1:  # Switching to or from an oversized page
            logger.debug("New page contains cards of different size, re-drawing cut markers")
            self._update_row_and_column_counts(self.document)
            self.remove_cut_markers()
            self.draw_cut_markers()
        for item in self.card_items:
            self.removeItem(item)
        if self._is_valid_page_index(selected_page):
            self._update_page_number_text()
            self._update_page_text_x()
            self._update_page_text_y()
            self._draw_cards()
            self.update_card_bleeds()

    def _update_page_text_y(self):
        # Put the text labels below the bleed
        y = 2 + distance_to_rounded_px(self.document.page_layout.card_bleed) + round(max(
            self.horizontal_cut_line_locations[PageType.REGULAR][-1],
            self.horizontal_cut_line_locations[PageType.OVERSIZED][-1]
        ))
        for item in self.text_items:
            item.setY(y)

    def _update_page_text_x(self):
        try:
            # This may throw a KeyError on MIXED pages
            title_x = round(self.vertical_cut_line_locations[PageType.REGULAR][0])
            page_number_x = round(self.vertical_cut_line_locations[PageType.REGULAR][-1])
        except KeyError:
            title_x = 0
            page_number_x = self.width()
        self.document_title_text.setX(title_x)
        font_metrics = QFontMetrics(self.page_number_text.font())
        text_width = font_metrics.horizontalAdvance(self.page_number_text.text())
        page_number_x -= text_width + 2
        self.page_number_text.setX(page_number_x + self.x_offset)

    def _update_page_number_text(self):
        if self.page_number_text not in self.text_items:
            return
        logger.debug("Updating page number text")
        page = self.selected_page.row() + 1
        total_pages = self.document.rowCount()
        self.page_number_text.setText(f"{page}/{total_pages}")

    @Slot(PageLayoutSettings)
    def on_page_layout_changed(self, new_page_layout: PageLayoutSettings):
        logger.info("Applying new document settings …")
        new_page_size = self.get_document_page_size(new_page_layout)
        self._update_row_and_column_counts(self.document)
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
        self.update_card_bleeds()
        self._update_text_items(new_page_layout)

        if size_changed:
            # Changed paper dimensions very likely caused the page aspect ratio to change. It may no longer fit
            # in the available space or is now too small, so emit a notification to allow the display widget to adjust.
            self.scene_size_changed.emit()
        logger.info("New document settings applied")

    def _update_text_items(self, page_layout: PageLayoutSettings):
        self._update_page_number_text()
        self.document_title_text.setText(self._format_document_title(page_layout.document_name))
        self._update_text_visibility(self.document_title_text, page_layout.document_name)
        self._update_text_visibility(self.page_number_text, page_layout.draw_page_numbers)
        self._update_page_text_x()
        self._update_page_text_y()

    def _format_document_title(self, title: str) -> str:
        page_layout = self.document.page_layout
        font_metrics = QFontMetrics(self.document_title_text.font())
        space_width_px = font_metrics.horizontalAdvance(" ")
        margins_px = distance_to_rounded_px(page_layout.margin_left + page_layout.margin_right)
        width = self.width()-margins_px-4
        available_widths_px = itertools.chain(
            [width-QFontMetrics(self.page_number_text.font()).horizontalAdvance("999/999")],
            itertools.repeat(width)
        )
        words = collections.deque(title.split(" "))
        lines: typing.List[str] = []
        current_line_words: typing.List[str] = []
        current_line_available_space = next(available_widths_px)
        current_line_used_space = 0
        logger.debug(f"Formatting line {len(lines)+1}, {current_line_available_space=}")
        while words:
            word = words.popleft()
            word_width_px = font_metrics.horizontalAdvance(word)
            if current_line_used_space + word_width_px + space_width_px <= current_line_available_space:
                current_line_words.append(word)
                current_line_used_space += space_width_px + word_width_px
            else:
                logger.debug(f"Formatting line {len(lines)+1}, {current_line_available_space=}")
                current_line_available_space = next(available_widths_px)
                lines.append(" ".join(current_line_words))
                current_line_words = [word]
                current_line_used_space = word_width_px
        if current_line_words:
            lines.append(" ".join(current_line_words))
        return "\n".join(lines)

    def _update_text_visibility(self, item: QGraphicsSimpleTextItem, new_visibility):
        text_items = self.text_items
        if item not in text_items and new_visibility:
            self.addItem(item)
        elif item in text_items and not new_visibility:
            self.removeItem(item)

    def get_document_page_size(self, page_layout: PageLayoutSettings) -> QRectF:
        without_margins = RenderMode.IMPLICIT_MARGINS in self.render_mode
        vertical_margins = (page_layout.margin_top + page_layout.margin_bottom) if without_margins else ZERO_WIDTH
        horizontal_margins = (page_layout.margin_left + page_layout.margin_right) if without_margins else ZERO_WIDTH

        height: QuantityT = page_layout.page_height - vertical_margins
        width: QuantityT = page_layout.page_width - horizontal_margins
        page_size = QRectF(
            QPointF(0, 0),
            QSizeF(
                distance_to_rounded_px(width),
               distance_to_rounded_px( height),
            )
        )
        return page_size

    def _draw_cards(self):
        parent = self.selected_page.sibling(self.selected_page.row(), 0)
        document = self.selected_page.model()
        page_type: PageType = self.selected_page.data(ItemDataRole.UserRole)
        images_to_draw = document.rowCount(parent)
        logger.info(f"Drawing {images_to_draw} cards")
        for row in range(images_to_draw):
            self.draw_card(document.index(row, PageColumns.Image, parent), page_type)

    def draw_card(self, index: QModelIndex, page_type: PageType, next_item: CardItem = None):
        position = self._compute_position_for_image(index.row(), page_type)
        if index.data(ItemDataRole.DisplayRole) is not None:  # Card has a QPixmap set
            card_item = CardItem(index, self.document)
            self.addItem(card_item)
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
        page_type: PageType = self.selected_page.data(ItemDataRole.UserRole)
        for index, card in enumerate(self.card_items):
            card.setPos(self._compute_position_for_image(index, page_type))

    def _is_valid_page_index(self, index: QModelIndex):
        return index.isValid() and not index.parent().isValid() and index.row() < self.document.rowCount()

    @Slot(QModelIndex)
    def on_page_type_changed(self, page: QModelIndex):
        if page.row() == self.selected_page.row():
            self._update_row_and_column_counts(self.document)
            self.update_card_positions()
            if self.document.page_layout.draw_cut_markers:
                self.remove_cut_markers()
                self.draw_cut_markers()

    def on_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex, roles: typing.List[ItemDataRole]):
        if (top_left.parent().row() == self.selected_page.row()
                and ItemDataRole.DisplayRole in roles
                # Multiple columns changed means card replaced.
                # Editing custom cards only changes single columns.
                # Thes cases can be ignored, as the pixmap never changes
                and top_left.column() < bottom_right.column()
        ):
            parent = top_left.parent()
            page_type: PageType = parent.data(ItemDataRole.UserRole)
            card_items = self.card_items
            for row in range(top_left.row(), bottom_right.row()+1):
                logger.debug(f"Card {row} on the current page was replaced, replacing image.")
                current_item = card_items[row]
                self.draw_card(top_left.siblingAtRow(row), page_type, current_item)
                self.removeItem(current_item)

    def on_rows_inserted(self, parent: QModelIndex, first: int, last: int):
        if self._is_valid_page_index(parent) and parent.row() == self.selected_page.row():
            inserted_cards = last-first+1
            needs_reorder = first + inserted_cards < self.document.rowCount(parent)
            next_item = self.card_items[first] if needs_reorder else None
            page_type: PageType = self.selected_page.data(ItemDataRole.UserRole)
            logger.debug(f"Added {inserted_cards} cards to the currently shown page, drawing them.")
            for new in range(first, last+1):
                self.draw_card(parent.child(new, PageColumns.Image), page_type, next_item)
            if needs_reorder:
                logger.debug("Cards added in the middle of the page, re-order existing cards.")
                self.update_card_positions()
            self.update_card_bleeds()
        elif not parent.isValid():
            # Page inserted. Update the page number text, as it contains the total number of pages
            self._update_page_number_text()

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
            self.update_card_bleeds()
        elif not parent.isValid():
            # Page removed. Update the page number text, as it contains the total number of pages
            self._update_page_number_text()

    def on_rows_moved(self, parent: QModelIndex, start: int, end: int, destination: QModelIndex, row: int):
        if parent.isValid() and parent.row() == self.selected_page.row():
            # Cards moved away are treated as if they were deleted
            logger.debug("Cards moved away from the currently shown page, calling card removal handler.")
            self.on_rows_removed(parent, start, end)
        if destination.isValid() and destination.row() == self.selected_page.row():
            # Moved in cards are treated as if they were added
            logger.debug("Cards moved onto the currently shown page, calling card insertion handler.")
            self.on_rows_inserted(destination, row, row+end-start)

    @functools.lru_cache(None)
    def _compute_position_for_image(self, index_row: int, page_type: PageType) -> QPointF:
        """Returns the page-absolute position of the top-left pixel of the given image."""
        page_layout: PageLayoutSettings = self.document.page_layout
        page_width = distance_to_rounded_px(page_layout.page_width)
        page_height = distance_to_rounded_px(page_layout.page_height)

        left_margin = distance_to_rounded_px(page_layout.margin_left)
        top_margin = distance_to_rounded_px(page_layout.margin_top)

        card_size = CardSizes.for_page_type(page_type).as_qsize_px()
        image_height: int = card_size.height()
        image_width: int = card_size.width()

        column_spacing = distance_to_rounded_px(page_layout.column_spacing)
        row_spacing = distance_to_rounded_px(page_layout.row_spacing)

        row, column = divmod(index_row, self.column_count)

        # Excessively large margins may shift the page content off-center. Clamp the borders to the non-negative range
        # to avoid clipping images off
        left_border = max(
            page_width
            - image_width * self.column_count
            - column_spacing * (self.column_count - 1),
            0
        ) / 2
        top_border = max(
            page_height
            - image_height * self.row_count
            - row_spacing * (self.row_count - 1),
            0
        ) / 2

        left_border = max(left_border, left_margin)
        top_border = max(top_border, top_margin)
        if RenderMode.IMPLICIT_MARGINS in self.render_mode:
            left_border -= left_margin
            top_border -= top_margin

        x = left_border + (image_width + column_spacing) * column + self.x_offset
        y = top_border + (image_height + row_spacing) * row
        return QPointF(
            x,
            y,
        )

    def update_card_bleeds(self):
        full_bleed = self.document.page_layout.card_bleed
        full_bleed_px = distance_to_rounded_px(full_bleed)
        inner_bleed_h_px = distance_to_rounded_px(min(self.document.page_layout.row_spacing/2, full_bleed))
        inner_bleed_v_px = distance_to_rounded_px(min(self.document.page_layout.column_spacing/2, full_bleed))
        for item in self.card_items:
            neighbors = self._has_neighbors(item)
            item.bleeds.update_bleeds(
                inner_bleed_h_px if neighbors.top else full_bleed_px,
                inner_bleed_h_px if neighbors.bottom else full_bleed_px,
                inner_bleed_v_px if neighbors.left else full_bleed_px,
                inner_bleed_v_px if neighbors.right else full_bleed_px,
            )

    def _has_neighbors(self, item: CardItem) -> NeighborsPresent:
        index_row = item.index.row()
        cards_on_page = self.document.rowCount(self.selected_page)
        return NeighborsPresent(
            # Cards in all rows except the top row have cards above them
            index_row >= self.column_count,
            # There is a card below, iff there are at least column_count more cards on the page
            index_row + self.column_count < cards_on_page,
            # There is a card on the left, iff the row modulo column_count is non-zero
            index_row % self.column_count > 0,
            # There is a card on the right, iff there is an additional card, and this is not on the right-most column.
            index_row % self.column_count + 1 != self.column_count and index_row + 1 < cards_on_page
        )

    def remove_cut_markers(self):
        for line in self.cut_lines:
            self.removeItem(line)

    def draw_cut_markers(self):
        """Draws the optional cut markers that extend to the paper border"""
        page_type: PageType = self.selected_page.data(ItemDataRole.UserRole)
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
        page_layout: PageLayoutSettings = self.document.page_layout
        for page_type in (PageType.UNDETERMINED, PageType.REGULAR, PageType.OVERSIZED):
            card_size: CardSize = CardSizes.for_page_type(page_type)
            self.horizontal_cut_line_locations[page_type] += self._compute_cut_marker_positions(CutMarkerParameters(
                page_layout.page_height,
                card_size.height, page_layout.compute_page_row_count(page_type),
                page_layout.margin_top, page_layout.row_spacing)
            )
            self.vertical_cut_line_locations[page_type] += self._compute_cut_marker_positions(CutMarkerParameters(
                page_layout.page_width,
                card_size.width, page_layout.compute_page_column_count(page_type),
                page_layout.margin_left, page_layout.column_spacing
            ))

    def _compute_cut_marker_positions(self, parameters: CutMarkerParameters) -> typing.Generator[float, None, None]:
        spacing = distance_to_rounded_px(parameters.image_spacing)
        card_size: int = round(parameters.card_size.magnitude)

        # Excessively large margins may shift the page content off-center. Clamp the border to the non-negative range
        # to avoid placing marker lines out of the drawing range
        border = (
            distance_to_rounded_px(parameters.total_space)
            - card_size * parameters.item_count
            - spacing * (parameters.item_count - 1)
        ) / 2
        margin = distance_to_rounded_px(parameters.margin)
        border = max(border, margin)
        if RenderMode.IMPLICIT_MARGINS in self.render_mode:
            border -= margin

        # Without spacing, draw a line top/left of each row/column.
        # To also draw a line below/right of the last row/column, add a virtual row/column if spacing is zero.
        # With positive spacing, draw a line left/right/above/below *each* row/column.
        for item in range(parameters.item_count + (not spacing)):
            pixel_position: float = border + item*(spacing+card_size)
            yield pixel_position
            if parameters.image_spacing:
                yield pixel_position + card_size

    def _draw_vertical_markers(self, line_color: QColor, page_type: PageType):
        offset = self.x_offset
        for column_px in self.vertical_cut_line_locations[page_type]:
            self._draw_vertical_line(column_px + offset, line_color)
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
