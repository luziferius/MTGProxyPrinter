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
from collections.abc import Generator
import enum
import functools
import itertools
import typing

from PySide6.QtCore import Qt, QSizeF, QPointF, QRectF, QPoint, Signal, QObject, Slot, \
    QPersistentModelIndex, QModelIndex
from PySide6.QtGui import QPen, QColorConstants, QColor, QPalette, QFontMetrics
from PySide6.QtWidgets import QGraphicsItem, QGraphicsLineItem, QGraphicsSimpleTextItem, QGraphicsScene

from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.document_page import PageColumns
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.page_scene.items import RenderLayers, CutMarkerParameters, NeighborsPresent, CardItem, \
    BullseyeMarkItem, CutMarkSquareItem, CutMarkAngleItem
from mtg_proxy_printer.settings import settings
from mtg_proxy_printer.units_and_sizes import PageType, unit_registry, distance_to_rounded_px, CardSizes, CardSize, \
    Quantity
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

PixelCache = collections.defaultdict[PageType, list[float]]
ItemDataRole = Qt.ItemDataRole
ColorGroup = QPalette.ColorGroup
ColorRole = QPalette.ColorRole
SortOrder = Qt.SortOrder

ZERO_WIDTH: Quantity = 0 * unit_registry.mm

@enum.unique
class RenderMode(enum.Flag):
    ON_SCREEN = enum.auto()
    ON_PAPER = enum.auto()
    IMPLICIT_MARGINS = enum.auto()


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
        self.print_markers = self._create_print_marker_items()
        self._update_print_markers()
        self._update_text_items(page_layout)
        if page_layout.draw_cut_markers:
            self.draw_cut_markers()
        logger.info(f"Created {self.__class__.__name__} instance. Render mode: {render_mode}")

    def _connect_document_signals(self, document: Document):
        document.rowsInserted.connect(self.on_rows_inserted)
        document.rowsRemoved.connect(self.on_rows_removed)
        document.rowsAboutToBeRemoved.connect(self.on_rows_about_to_be_removed)
        document.rowsAboutToBeMoved.connect(self.on_rows_about_to_be_moved)
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

    def _create_print_marker_items(self) -> list[BullseyeMarkItem]:
        items = [
            BullseyeMarkItem(False, False), BullseyeMarkItem(True, False), BullseyeMarkItem(False, True),
            CutMarkSquareItem(), CutMarkAngleItem(False), CutMarkAngleItem(True)
        ]
        for item in items:
            self.addItem(item)
        return items

    def get_background_color(self, render_mode: RenderMode) -> QColor:
        if RenderMode.ON_PAPER in render_mode:
            return QColorConstants.Transparent
        return self.palette().color(ColorGroup.Active, ColorRole.Base)

    def get_cut_marker_pen(self, render_mode: RenderMode) -> QPen:
        layout = self.document.page_layout
        if (RenderMode.ON_PAPER not in render_mode
                and layout.cut_marker_color == QColorConstants.Black):
            # Rendering on screen with the default black supports using a color scheme override for dark mode rendering
            color = self.palette().color(ColorGroup.Active, ColorRole.WindowText)
        else:
            color = layout.cut_marker_color
        return QPen(
            color, layout.cut_marker_width.to("point", "print").magnitude, layout.cut_marker_pen_style()
        )

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
        cut_line_color = self.get_cut_marker_pen(self.render_mode)
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
    def card_items(self) -> list[CardItem]:
        return list(filter(is_card_item, self.items(SortOrder.AscendingOrder)))

    @property
    def cut_lines(self) -> list[QGraphicsLineItem]:
        return list(filter(is_cut_line_item, self.items(SortOrder.AscendingOrder)))

    @property
    def text_items(self) -> list[QGraphicsSimpleTextItem]:
        return list(filter(is_text_item, self.items(SortOrder.AscendingOrder)))

    @Slot(QPersistentModelIndex)
    def on_current_page_changed(self, selected_page: QPersistentModelIndex):
        """Draws the canvas, when the currently selected page changes."""
        logger.debug(f"Current page changed to page {selected_page.row()}")
        page_types: set[PageType] = {
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

    def _update_print_markers(self):
        layout = self.document.page_layout
        current_style = layout.print_registration_marks_style

        top = distance_to_rounded_px(layout.margin_top)
        bottom = distance_to_rounded_px(layout.page_height)-distance_to_rounded_px(layout.margin_bottom)

        left = distance_to_rounded_px(layout.margin_left) + self.x_offset
        right = distance_to_rounded_px(layout.page_width) - distance_to_rounded_px(layout.margin_right) + self.x_offset

        positions = [QPoint(left, top), QPoint(right, top), QPoint(left, bottom)]
        for item, position in zip(self.print_markers, itertools.cycle(positions)):
            item.update_visibility(current_style)
            item.setPos(position)

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
        self._update_print_markers()

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
        lines: list[str] = []
        current_line_words: list[str] = []
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

        height: Quantity = page_layout.page_height - vertical_margins
        width: Quantity = page_layout.page_width - horizontal_margins
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

    def update_card_positions(self):
        page_type: PageType = self.selected_page.data(ItemDataRole.UserRole)
        for card in self.card_items:
            card.setPos(self._compute_position_for_image(card.index.row(), page_type))

    def _is_valid_page_index(self, index: QModelIndex | QPersistentModelIndex):
        return index.isValid() and not index.parent().isValid() and index.row() < self.document.rowCount()

    @Slot(QModelIndex)
    def on_page_type_changed(self, page: QModelIndex):
        if page.row() == self.selected_page.row():
            self._update_row_and_column_counts(self.document)
            self.update_card_positions()
            if self.document.page_layout.draw_cut_markers:
                self.remove_cut_markers()
                self.draw_cut_markers()

    @Slot(QModelIndex, QModelIndex, list)
    def on_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex, roles: list[ItemDataRole]):
        parent = top_left.parent()
        if not parent.isValid() or parent.row() != self.selected_page.row() or ItemDataRole.DisplayRole not in roles:
            # Ignore all events not regarding the currently shown page
            return
        card_items = self.card_items

        # Editing custom cards only changes single columns other than the Image column.
        # So multiple columns edited means the card was replaced and all affected rows needs to be replaced
        if top_left.column() < bottom_right.column():
            page_type: PageType = parent.data(ItemDataRole.UserRole)
            for row in range(top_left.row(), bottom_right.row()+1):
                logger.debug(f"Card {row} on the current page was replaced, replacing image.")
                current_item = card_items[row]
                self.draw_card(top_left.siblingAtRow(row), page_type, current_item)
                self.removeItem(current_item)
        # Editing the Image column only happens when the custom card corner style was toggled.
        elif top_left.column() == PageColumns.Image:
            for row in range(top_left.row(), bottom_right.row()+1):
                index = top_left.siblingAtRow(row)
                logger.debug(f"Update pixmap for custom card on {row=} on the current page")
                current_item = card_items[row]
                current_item.card_pixmap_item.setPixmap(index.data(ItemDataRole.DisplayRole))

    @Slot(QModelIndex, int, int)
    def on_rows_inserted(self, parent: QModelIndex, first: int, last: int):
        if self._is_valid_page_index(parent) and parent.row() == self.selected_page.row():
            inserted_cards = last-first+1
            needs_reorder = first + inserted_cards < self.document.rowCount(parent)
            next_item = self.card_items[first] if needs_reorder else None
            page_type: PageType = self.selected_page.data(ItemDataRole.UserRole)
            logger.debug(f"Added {inserted_cards} cards to the currently shown page, drawing them.")
            model = parent.model()
            for new in range(first, last+1):
                self.draw_card(model.index(new, PageColumns.Image, parent), page_type, next_item)
            if needs_reorder:
                logger.debug("Cards added in the middle of the page, re-order existing cards.")
                self.update_card_positions()
            self.update_card_bleeds()
        elif not parent.isValid():
            # Page inserted. Update the page number text, as it contains the total number of pages
            self._update_page_number_text()

    @Slot(QModelIndex, int, int)
    def on_rows_about_to_be_removed(self, parent: QModelIndex, first: int, last: int):
        if not parent.isValid() and first <= self.selected_page.row() <= last:
            logger.debug("About to delete the currently shown page. Removing the held index.")
            self.selected_page = QPersistentModelIndex()
        elif parent.isValid() and parent.row() == self.selected_page.row():
            # Remove the cards now, as the model indices are still valid and point to the correct cards
            logger.debug(f"Removing cards {first} to {last} from the current page.")
            for item in self.card_items:
                # Identify the cards by their internal index. The list position is arbitrary.
                # Update the positions of the remaining cards later, when their new position is known
                if first <= item.index.row() <= last:
                    self.removeItem(item)


    @Slot(QModelIndex, int, int)
    def on_rows_removed(self, parent: QModelIndex, first: int, last: int):
        if not parent.isValid():
            # Page removed. Update the page number text, as it contains the total number of pages
            self._update_page_number_text()
        if parent.isValid() and parent.row() == self.selected_page.row():
            self.update_card_positions()
            self.update_card_bleeds()

    @Slot(QModelIndex, int, int, QModelIndex)
    def on_rows_about_to_be_moved(self, parent: QModelIndex, start: int, end: int, destination: QModelIndex):
        source_page_row = parent.row()
        current_page_row = self.selected_page.row()
        destination_page_row = destination.row()
        if source_page_row == current_page_row != destination_page_row:
            # Cards moved away are treated as if they were deleted
            logger.debug("Cards moved away from the currently shown page, calling card removal handler.")
            self.on_rows_about_to_be_removed(parent, start, end)


    @Slot(QModelIndex, int, int, QModelIndex, int)
    def on_rows_moved(self, parent: QModelIndex, start: int, end: int, destination: QModelIndex, row: int):
        source_page_row = parent.row()
        current_page_row = self.selected_page.row()
        destination_page_row = destination.row()
        if not parent.isValid():
            # Moved pages around. Needs to update the current page text
            self._update_page_number_text()
            return
        # Parent is valid, thus [start, end] point to cards on it
        if source_page_row != current_page_row == destination_page_row:
            # Cards moved onto the current page are treated as if they were added
            logger.debug("Cards moved onto the currently shown page, calling card insertion handler.")
            self.on_rows_inserted(destination, row, row + end - start)
        elif source_page_row == current_page_row:
            logger.debug("Card move affects the current page, updating positions.")
            self.update_card_positions()
        # Remaining cases are card moves happening "off-screen", so nothing has to be done on them.


    @functools.cache
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
            # There is a card above, iff the card's row > 1, i.e. there are at least column_count cards before it
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
        pen = self.get_cut_marker_pen(self.render_mode)
        logger.info(f"Drawing cut markers")
        layer = RenderLayers.CUT_LINES_ABOVE \
            if self.document.page_layout.cut_marker_draw_above_cards else RenderLayers.CUT_LINES_BELOW
        self._draw_vertical_markers(pen, page_type, layer)
        self._draw_horizontal_markers(pen, page_type, layer)

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

    def _draw_vertical_markers(self, pen: QPen, page_type: PageType, layer: RenderLayers):
        offset = self.x_offset
        for column_px in self.vertical_cut_line_locations[page_type]:
            self._draw_vertical_line(column_px + offset, pen, layer)
        logger.debug(f"Vertical cut markers drawn")

    def _draw_horizontal_markers(self, pen: QPen, page_type: PageType, layer: RenderLayers):
        for row_px in self.horizontal_cut_line_locations[page_type]:
            self._draw_horizontal_line(row_px, pen, layer)
        logger.debug(f"Horizontal cut markers drawn")

    def _draw_vertical_line(self, column_px: float, pen: QPen, layer: RenderLayers):
        line = self.addLine(0, 0, 0, self.height(), pen)
        line.setX(column_px)
        line.setZValue(layer.value)

    def _draw_horizontal_line(self, row_px: float, pen: QPen, layer: RenderLayers):
        line = self.addLine(0, 0, self.width(), 0, pen)
        line.setY(row_px)
        line.setZValue(layer.value)
