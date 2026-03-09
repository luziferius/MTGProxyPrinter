#  Copyright © 2020-2026  Thomas Hess <thomas.hess@udo.edu>
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
import itertools
import typing
from collections.abc import Iterable, Generator

from PySide6.QtCore import QRect, QPoint, QPointF, QSize, QModelIndex, QPersistentModelIndex, Qt, Slot
from PySide6.QtGui import QPixmap, QPen, QColorConstants, QTransform, QPolygonF, QPalette
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsPolygonItem, QGraphicsItemGroup, QGraphicsItem, \
    QGraphicsSimpleTextItem, QGraphicsRectItem, QGraphicsLineItem, QApplication
from PySide6.QtSvgWidgets import QGraphicsSvgItem

from mtg_proxy_printer.model.card import AnyCardType, CardCorner
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.units_and_sizes import unit_registry, RESOLUTION, Quantity, CardSize, CardSizes, PageType, \
    distance_to_rounded_px
from mtg_proxy_printer.ui.common import RESOURCE_PATH_PREFIX
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

ColorGroup = QPalette.ColorGroup
ColorRole = QPalette.ColorRole
ItemDataRole = Qt.ItemDataRole
point = unit_registry.point
degree = unit_registry.degree
pixel = unit_registry.pixel
PenStyle = Qt.PenStyle


@enum.unique
class RenderMode(enum.Flag):
    ON_SCREEN = enum.auto()
    ON_PAPER = enum.auto()
    IMPLICIT_MARGINS = enum.auto()


@enum.unique
class RenderLayers(enum.IntEnum):
    BACKGROUND = -5
    CUT_LINES_BELOW = enum.auto()
    BLEEDS = enum.auto()
    CORNERS = enum.auto()
    TEXT = enum.auto()
    CARDS = enum.auto()
    CUT_LINES_ABOVE = enum.auto()
    WATERMARK = enum.auto()


@enum.unique
class BleedOrientation(enum.Enum):
    HORIZONTAL = enum.auto()
    VERTICAL = enum.auto()


class CutMarkerParameters(typing.NamedTuple):
    total_space: Quantity
    card_size: Quantity
    item_count: int
    margin: Quantity
    image_spacing: Quantity


class BullseyeMarkItem(QGraphicsSvgItem):
    """
    Draws a Bullseye print target. The used SVG uses centered 1 pixel wide lines on a 32 pixel base.
    Positions and scaling is tuned to not wander off and render on whole pixels
    """
    def __init__(self, left_aligned: bool, bottom_aligned: bool, parent: QGraphicsItem = None):
        super().__init__(f"{RESOURCE_PATH_PREFIX}/Common_Registration_Mark.svg", parentItem=parent)
        length = self.boundingRect().width()
        self.setTransformOriginPoint(length*left_aligned, length*bottom_aligned)
        self.setZValue(RenderLayers.CUT_LINES_BELOW.value)
        self.setScale(RESOLUTION.magnitude/100+285/256000)  # whole 96 pixel at 300DPI, resulting in ~8.1mm.
        self.setPos(QPoint(0, 0))

    def setPos(self, pos: QPoint | QPointF, /):
        new = QPointF(
            (pos.x()*256105/256000),
            (pos.y()*256105/256000),
        )
        super().setPos(new)

    def update_visibility(self, current_style: str):
        self.setOpacity(current_style == "Bullseye")


class CutMarkSquareItem(QGraphicsRectItem):
    def __init__(self, parent: QGraphicsItem = None):
        size = round((5.5*unit_registry.mm * RESOLUTION).to("pixel", "print").magnitude)
        super().__init__(QRect(0, 0, size, size), parent)
        self.setZValue(RenderLayers.CUT_LINES_BELOW.value)
        self.setPen(PenStyle.NoPen)
        self.setBrush(QColorConstants.Black)
        logger.debug(f"{self.__class__.__name__}: {self.boundingRect()=}")

    def update_visibility(self, current_style: str):
        self.setOpacity(current_style == "Cut marker")


class CutMarkAngleItem(QGraphicsPolygonItem):

    def __init__(self, bottom_left: bool, parent: QGraphicsItem = None):
        length_px = round((18*unit_registry.mm*RESOLUTION).to("pixel", "print").magnitude)
        thickness_px = round((1*unit_registry.mm*RESOLUTION).to("pixel", "print").magnitude)
        super().__init__([  # Forms ┓
            QPoint(0, 0), QPoint(length_px, 0),
            QPoint(length_px, length_px), QPoint(length_px-thickness_px, length_px),
            QPoint(length_px-thickness_px, thickness_px), QPoint(0, thickness_px),
            QPoint(0, 0)
        ], parent)
        self.bottom_left = bottom_left
        self.setZValue(RenderLayers.CUT_LINES_BELOW.value)
        self.setPen(PenStyle.NoPen)
        self.setBrush(QColorConstants.Black)
        self.setRotation(180 * bottom_left)
        logger.debug(f"{self.__class__.__name__}: {self.boundingRect()=}")

    def setPos(self, pos: QPoint | QPointF, /):
        bb = self.boundingRect()
        new = QPointF(
            (pos.x()+bb.width()-2*bb.width()*(not self.bottom_left)),
            (pos.y()),
        )
        super().setPos(new)

    def update_visibility(self, current_style: str):
        self.setOpacity(current_style == "Cut marker")


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

    def create_corners(self, card: AnyCardType, draw_corners: bool) -> list[QGraphicsRectItem]:
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

    @Slot(PageLayoutSettings, set)
    def on_page_layout_changed(self, new_page_layout: PageLayoutSettings, changed_values: set[str]):
        if "draw_sharp_corners" in changed_values:
            for corner in self.corners:
                corner.setOpacity(new_page_layout.draw_sharp_corners)
        if any(value.startswith("watermark") for value in changed_values):
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


class CutHelperLineGridItem(QGraphicsItemGroup):
    POSITIONAL_PAGE_LAYOUT_SETTINGS = {
        "paper_size", "paper_orientation", "custom_page_height", "custom_page_width",
        "margin_left", "margin_right", "margin_top", "margin_bottom",
        "column_spacing", "row_spacing",
    }
    STYLE_SETTINGS = {
        "cut_marker_style", "cut_marker_color", "cut_marker_width"
    }

    def __init__(self, document: Document, render_mode: RenderMode, card_size: CardSize, parent: QGraphicsItem = None):
        super().__init__(parent)
        self.document = document
        self.render_mode = render_mode
        self.grid_size = card_size
        self.lines: list[QGraphicsLineItem] = []
        self._create_line_items(document.page_layout, self._get_cut_helper_line_pen(document.page_layout))
        document.current_page_changed.connect(self.on_current_page_changed)
        document.page_layout_changed.connect(self.on_page_layout_changed)
        self.setVisible(False)

    def _get_cut_helper_line_pen(self, layout: PageLayoutSettings) -> QPen:
        """Returns the QPen to use for line items"""
        if (RenderMode.ON_PAPER not in self.render_mode
                and layout.cut_marker_color == QColorConstants.Black):
            # Rendering on screen with the default black supports using a color scheme override for dark mode rendering
            color = QApplication.palette().color(ColorGroup.Active, ColorRole.WindowText)
        else:
            color = layout.cut_marker_color
        return QPen(
            color, layout.cut_marker_width.to("point", "print").magnitude, layout.cut_marker_pen_style()
        )

    @Slot(PageLayoutSettings, set)
    def on_page_layout_changed(self, new_page_layout: PageLayoutSettings, changed_values: set[str]):
        if not new_page_layout.draw_cut_markers:
            self.setVisible(False)
        pen = self._get_cut_helper_line_pen(new_page_layout)
        if changed_values.intersection(self.POSITIONAL_PAGE_LAYOUT_SETTINGS):
            self._delete_line_items()
            self._create_line_items(new_page_layout, pen)
        elif changed_values.intersection(self.STYLE_SETTINGS):
            self._update_line_style(pen)
        if "cut_marker_draw_above_cards" in changed_values:
            self.setZValue(
                (RenderLayers.CUT_LINES_ABOVE
                 if new_page_layout.cut_marker_draw_above_cards
                 else RenderLayers.CUT_LINES_BELOW).value
            )

    def _update_line_style(self, pen: QPen):
        for line in self.lines:
            line.setPen(pen)

    def _delete_line_items(self):
        for line in self.lines:
            self.removeFromGroup(line)
        self.lines.clear()

    def _create_line_items(self, page_layout: PageLayoutSettings, pen: QPen):
        card_size = self.grid_size
        page_type = PageType.REGULAR if card_size is CardSizes.REGULAR else PageType.OVERSIZED

        self._draw_horizontal_markers(
            pen,
            distance_to_rounded_px(page_layout.page_width),
            self._compute_cut_marker_positions(CutMarkerParameters(
                page_layout.page_height,
                card_size.height, page_layout.compute_page_row_count(page_type),
                page_layout.margin_top, page_layout.row_spacing))
        )
        self._draw_vertical_markers(
            pen,
            distance_to_rounded_px(page_layout.page_height),
            self._compute_cut_marker_positions(CutMarkerParameters(
                page_layout.page_width,
                card_size.width, page_layout.compute_page_column_count(page_type),
                page_layout.margin_left, page_layout.column_spacing))
        )

    @Slot(QPersistentModelIndex)
    def on_current_page_changed(self, selected_page: QPersistentModelIndex):
        if not self.document.page_layout.draw_cut_markers:
            return
        new_page_type: PageType = selected_page.data(ItemDataRole.UserRole)
        grid_is_visible = CardSizes.for_page_type(new_page_type) == self.grid_size
        self.setVisible(grid_is_visible)

    def _compute_cut_marker_positions(self, parameters: CutMarkerParameters) -> Generator[float, None, None]:
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

    def _draw_vertical_markers(self, pen: QPen, length: float, positions: Iterable[float]):
        for column_px in positions:
            self._draw_vertical_line(pen, length, column_px)
        logger.debug(f"Vertical cut markers drawn")

    def _draw_horizontal_markers(self, pen: QPen, length: float, positions: Iterable[float]):
        for row_px in positions:
            self._draw_horizontal_line(pen, length, row_px)
        logger.debug(f"Horizontal cut markers drawn")

    def _draw_vertical_line(self, pen: QPen, length: float, column_px: float):
        line = QGraphicsLineItem(0, 0, 0, length)
        line.setX(column_px)
        line.setPen(pen)
        self.lines.append(line)
        self.addToGroup(line)

    def _draw_horizontal_line(self, pen: QPen, length: float, row_px: float):
        line = QGraphicsLineItem(0, 0, length, 0)
        line.setY(row_px)
        line.setPen(pen)
        self.lines.append(line)
        self.addToGroup(line)
