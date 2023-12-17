import collections
import enum
import functools
import itertools
import typing

import pint
from PyQt5.QtCore import Qt, QSizeF, QPointF, QRectF, pyqtSignal as Signal, QObject, pyqtSlot as Slot, \
    QPersistentModelIndex, QModelIndex
from PyQt5.QtGui import QPen, QColorConstants, QBrush, QColor, QPalette, QFontMetrics
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsItem, QGraphicsPixmapItem, QGraphicsRectItem, \
    QGraphicsLineItem, QGraphicsSimpleTextItem, QGraphicsScene

from mtg_proxy_printer.model.card_list import PageColumns
from mtg_proxy_printer.model.carddb import Card, CardCorner
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.document_loader import PageLayoutSettings
from mtg_proxy_printer.units_and_sizes import PageType, unit_registry, RESOLUTION, CardSizes, CardSize
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

PixelCache = typing.DefaultDict[PageType, typing.List[float]]
ItemDataRole = Qt.ItemDataRole


@enum.unique
class RenderLayers(enum.Enum):
    BACKGROUND = -3
    CUT_LINES = -2
    TEXT = -1
    CARDS = 0


@enum.unique
class RenderMode(enum.Flag):
    ON_SCREEN = enum.auto()
    ON_PAPER = enum.auto()
    IMPLICIT_MARGINS = enum.auto()


class CutMarkerParameters(typing.NamedTuple):
    total_space: int
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
        self.selected_page = self.document.get_current_page_index()
        self.setBackgroundBrush(QBrush(QColorConstants.White, Qt.SolidPattern))
        background_color = self.get_background_color(render_mode)
        logger.debug(f"Drawing background rectangle")
        self.background = self.addRect(0, 0, self.width(), self.height(), background_color, background_color)
        self.background.setZValue(RenderLayers.BACKGROUND.value)
        self.horizontal_cut_line_locations: PixelCache = collections.defaultdict(list)
        self.vertical_cut_line_locations: PixelCache = collections.defaultdict(list)
        self._update_cut_marker_positions()
        self.document_title_text = self._create_text_item()
        self.page_number_text = self._create_text_item()
        self._update_text_items(document.page_layout)
        if document.page_layout.draw_cut_markers:
            self.draw_cut_markers()
        logger.info(f"Created {self.__class__.__name__} instance. Render mode: {render_mode}")

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
        return self.palette().color(QPalette.Active, QPalette.Base)

    def get_cut_marker_color(self, render_mode: RenderMode) -> QColor:
        if RenderMode.ON_PAPER in render_mode:
            return QColorConstants.Black
        return self.palette().color(QPalette.Active, QPalette.WindowText)

    def get_text_color(self, render_mode: RenderMode) -> QColor:
        if RenderMode.ON_PAPER in render_mode:
            return QColorConstants.Black
        return self.palette().color(QPalette.Active, QPalette.WindowText)

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
    def card_items(self) -> typing.List[CardItem]:
        return list(filter(is_card_item, self.items(Qt.AscendingOrder)))

    @property
    def cut_lines(self) -> typing.List[QGraphicsLineItem]:
        return list(filter(is_cut_line_item, self.items(Qt.AscendingOrder)))

    @property
    def text_items(self) -> typing.List[QGraphicsSimpleTextItem]:
        return list(filter(is_text_item, self.items(Qt.AscendingOrder)))

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
            self.remove_cut_markers()
            self.draw_cut_markers()
        for item in self.card_items:
            self.removeItem(item)
        if self._is_valid_page_index(selected_page):
            self._update_page_number_text()
            self._update_page_text_x()
            self._update_page_text_y()
            self._draw_cards()

    def _update_page_text_y(self):
        # Put the text labels below the
        y = 2 + round(max(
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
        self.page_number_text.setX(page_number_x)

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
        margins_px = self._mm_to_rounded_px(page_layout.margin_left+page_layout.margin_right)
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
        vertical_margins = without_margins * (page_layout.margin_top + page_layout.margin_bottom)
        horizontal_margins = without_margins * (page_layout.margin_left + page_layout.margin_right)

        height: pint.Quantity = (page_layout.page_height - vertical_margins) * unit_registry.millimeter
        width: pint.Quantity = (page_layout.page_width - horizontal_margins) * unit_registry.millimeter
        page_size = QRectF(
            QPointF(0, 0),
            QSizeF(
                (RESOLUTION * width).to("pixel").magnitude,
                (RESOLUTION * height).to("pixel").magnitude,
            )
        )
        return page_size

    def _draw_cards(self):
        index = self.selected_page.sibling(self.selected_page.row(), 0)
        page_type: PageType = self.selected_page.data(ItemDataRole.UserRole)
        images_to_draw = self.selected_page.model().rowCount(index)
        logger.info(f"Drawing {images_to_draw} cards")
        for row in range(images_to_draw):
            self.draw_card(row, page_type)

    def draw_card(self, row: int, page_type: PageType, next_item: CardItem = None):
        index = self.selected_page.child(row, PageColumns.Image)
        position = self._compute_position_for_image(row, page_type)
        if index.data(ItemDataRole.DisplayRole) is not None:  # Card has a QPixmap set
            card: Card = index.data(ItemDataRole.UserRole)
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
        page_type: PageType = self.selected_page.data(ItemDataRole.UserRole)
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

    def on_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex, roles: typing.List[ItemDataRole]):
        if top_left.parent().row() == self.selected_page.row() and ItemDataRole.DisplayRole in roles:
            page_type: PageType = top_left.parent().data(ItemDataRole.UserRole)
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
            page_type: PageType = self.selected_page.data(ItemDataRole.EditRole).page_type()
            logger.debug(f"Added {inserted_cards} cards to the currently shown page, drawing them.")
            for new in range(first, last+1):
                self.draw_card(new, page_type, next_item)
            if needs_reorder:
                logger.debug("Cards added in the middle of the page, re-order existing cards.")
                self.update_card_positions()
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

    @functools.lru_cache
    def _compute_position_for_image(self, index_row: int, page_type: PageType) -> QPointF:
        """Returns the page-absolute position of the top-left pixel of the given image."""
        page_layout: PageLayoutSettings = self.document.page_layout

        page_width = self._mm_to_rounded_px(page_layout.page_width)
        page_height = self._mm_to_rounded_px(page_layout.page_height)

        left_margin = self._mm_to_rounded_px(page_layout.margin_left)
        top_margin = self._mm_to_rounded_px(page_layout.margin_top)

        card_size = CardSizes.for_page_type(page_type)
        image_height: int = card_size.height.magnitude
        image_width: int = card_size.width.magnitude

        column_spacing = self._mm_to_rounded_px(page_layout.column_spacing)
        row_spacing = self._mm_to_rounded_px(page_layout.row_spacing)

        column_count = page_layout.compute_page_column_count(page_type)
        row_count = page_layout.compute_page_row_count(page_type)
        row, column = divmod(index_row, column_count)

        # Excessively large margins may shift the page content off-center. Clamp the borders to the non-negative range
        # to avoid clipping images off
        left_border = max(
            page_width
            - image_width * column_count
            - column_spacing * (column_count - 1),
            0
        ) / 2
        top_border = max(
            page_height
            - image_height * row_count
            - row_spacing * (row_count - 1),
            0
        ) / 2

        left_border = max(left_border, left_margin)
        top_border = max(top_border, top_margin)
        if RenderMode.IMPLICIT_MARGINS in self.render_mode:
            left_border -= left_margin
            top_border -= top_margin

        x = left_border + (image_width + column_spacing) * column
        y = top_border + (image_height + row_spacing) * row
        return QPointF(
            x,
            y,
        )

    @staticmethod
    def _mm_to_rounded_px(value: int) -> int:
        return round((value*unit_registry.mm*RESOLUTION).to("pixel").magnitude)

    def remove_cut_markers(self):
        for line in self.cut_lines:
            self.removeItem(line)

    def draw_cut_markers(self):
        """Draws the optional cut markers that extend to the paper border"""
        page_type: PageType = self.selected_page.data(ItemDataRole.EditRole).page_type()
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
        spacing = self._mm_to_rounded_px(parameters.image_spacing)
        card_size: int = parameters.card_size.magnitude

        # Excessively large margins may shift the page content off-center. Clamp the border to the non-negative range
        # to avoid placing marker lines out of the drawing range
        border = (
            self._mm_to_rounded_px(parameters.total_space)
            - card_size * parameters.item_count
            - spacing * (parameters.item_count - 1)
        ) / 2
        margin = self._mm_to_rounded_px(parameters.margin)
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
