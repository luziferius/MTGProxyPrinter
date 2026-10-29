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

import collections
import enum
import itertools

from PySide6.QtCore import Qt, QSizeF, QPointF, QRectF, Signal, QObject, Slot, \
    QPersistentModelIndex, QModelIndex
from PySide6.QtGui import QPen, QColorConstants, QColor, QPalette, QFontMetrics
from PySide6.QtWidgets import QGraphicsItem, QGraphicsLineItem, QGraphicsSimpleTextItem, QGraphicsScene

from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.document_page import PageColumns
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.model.page_geometry import PageGeometry, build_page_geometry
from mtg_proxy_printer.page_scene.items import RenderLayers, NeighborsPresent, CardItem
from mtg_proxy_printer.page_scene.registration_profiles import RegistrationProfile, get_registration_profile
from mtg_proxy_printer.registration_profile_ids import RegistrationProfileId
from mtg_proxy_printer.settings import settings
from mtg_proxy_printer.units_and_sizes import PageType, unit_registry, distance_to_rounded_px, \
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
    FILE_EXPORT = enum.auto()
    NATIVE_PRINT = enum.auto()


def is_card_item(item: QGraphicsItem) -> bool:
    return isinstance(item, CardItem)


def is_cut_line_item(item: QGraphicsItem) -> bool:
    return isinstance(item, QGraphicsLineItem)


def is_text_item(item: QGraphicsItem) -> bool:
    return isinstance(item, QGraphicsSimpleTextItem)


class PageScene(QGraphicsScene):
    """This class implements the low-level rendering of the currently selected page on a blank canvas."""

    scene_size_changed = Signal()

    def __init__(self, document: Document, render_mode: RenderMode, parent: QObject | None = None):
        """
        :param document: The document instance
        :param render_mode: Specifies the render mode.
          On paper, no background is drawn and cut markers use black.
          On Screen, the background uses the theme’s background color and cut markers use a high-contrast color.
        :param parent: Optional Qt parent object
        """
        self.render_mode = render_mode
        self.print_markers: list[QGraphicsItem] = []
        self._registration_profile: RegistrationProfile | None = None
        page_layout = document.page_layout
        super().__init__(self.get_document_page_size(page_layout), parent)
        self.document = document
        self._connect_document_signals(document)
        self.selected_page = self.document.get_current_page_index()
        self.row_count = self.column_count = 1
        self.geometry: PageGeometry | None = None
        self.full_grid_geometry: dict[PageType, PageGeometry] = {}
        self.geometry_pending = False
        self.geometry_unavailable_reason: str | None = None
        self.registration_unavailable_reason: str | None = None
        self._rebuild_full_grid_geometry()
        background_color = self.get_background_color(render_mode)
        logger.debug(f"Drawing background rectangle")
        self.background = self.addRect(0, 0, self.width(), self.height(), background_color, background_color)
        self.background.setZValue(RenderLayers.BACKGROUND.value)
        self.horizontal_cut_line_locations: PixelCache = collections.defaultdict(list)
        self.vertical_cut_line_locations: PixelCache = collections.defaultdict(list)
        self._update_cut_marker_positions()
        self.document_title_text = self._create_text_item()
        self.page_number_text = self._create_text_item()
        self._refresh_actual_geometry()
        self._update_text_items(page_layout)
        if self.geometry is not None:
            self._draw_cards()
            self.update_card_bleeds()
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
        document.action_applied.connect(self._retry_pending_geometry)
        document.action_undone.connect(self._retry_pending_geometry)

    def _rebuild_full_grid_geometry(self):
        layout = self.document.page_layout
        self.full_grid_geometry = {
            page_type: build_page_geometry(layout, page_type, layout.compute_page_card_capacity(page_type))
            for page_type in (PageType.REGULAR, PageType.OVERSIZED)
        }

    def _clear_card_items(self):
        for item in self.card_items:
            self.removeItem(item)

    def _geometry_unavailable(self, reason: str):
        self.geometry = None
        self.geometry_pending = True
        self.geometry_unavailable_reason = reason
        self.row_count = self.column_count = 0
        self._clear_card_items()
        self.remove_cut_markers()
        self._clear_registration_items()
        self.document_title_text.setVisible(False)
        self.page_number_text.setVisible(False)

    def _refresh_actual_geometry(self) -> bool:
        previous = self.geometry
        if not self._is_valid_page_index(self.selected_page):
            self._geometry_unavailable("No valid selected page")
            return False
        try:
            geometry = build_page_geometry(
                self.document.page_layout, self.selected_page.data(ItemDataRole.UserRole),
                self.document.rowCount(self.selected_page),
            )
        except ValueError as error:
            self._geometry_unavailable(str(error))
            return False
        recovering = self.geometry_pending
        self.geometry = geometry
        self.row_count, self.column_count = geometry.rows, geometry.columns
        self.geometry_pending = False
        self.geometry_unavailable_reason = None
        grid_changed = previous is None or (
            previous.grid_x_edges_px, previous.grid_y_edges_px
        ) != (geometry.grid_x_edges_px, geometry.grid_y_edges_px)
        if grid_changed:
            self.remove_cut_markers()
            if self.document.page_layout.draw_cut_markers:
                self.draw_cut_markers()
        if recovering:
            # Deferred model notifications may have skipped insertion/replacement.
            self._clear_card_items()
            self._draw_cards()
            self.update_card_bleeds()
            self._update_text_items(self.document.page_layout)
        self._update_print_markers()
        return True

    def _retry_pending_geometry(self, *_):
        if self.geometry_pending:
            if not self._is_valid_page_index(self.selected_page):
                try:
                    self.selected_page = self.document.get_current_page_index()
                except ValueError:
                    return
            self._refresh_actual_geometry()

    def require_geometry_ready(self):
        """Fail explicit output rather than rendering stale or unavailable geometry."""
        self._retry_pending_geometry()
        if self.geometry is None:
            raise RuntimeError(f"Page geometry unavailable: {self.geometry_unavailable_reason}")

    def require_output_ready(self):
        self.require_geometry_ready()
        if self.registration_unavailable_reason:
            raise RuntimeError(f'Registration unavailable: {self.registration_unavailable_reason}')

    def render(self, *args, **kwargs):
        self.require_output_ready()
        return super().render(*args, **kwargs)

    def _presentation_position(self, x: float, y: float) -> QPointF:
        if RenderMode.IMPLICIT_MARGINS in self.render_mode:
            frame = self.full_grid_geometry[PageType.REGULAR].margin_frame_px
            x -= frame.x
            y -= frame.y
        return QPointF(x + self.x_offset, y)

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
        if self.document.page_layout.print_registration_marks_style == RegistrationProfileId.SISER.value:
            return QColorConstants.White
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
        return 0 if self.render_mode & (RenderMode.ON_SCREEN | RenderMode.FILE_EXPORT | RenderMode.NATIVE_PRINT) \
            else distance_to_rounded_px(settings["printer"].get_quantity("horizontal-offset"))

    @property
    def card_items(self) -> list[CardItem]:
        # Presentation order only. Model-slot identity comes from each persistent index.
        card_items = filter(is_card_item, self.items())
        return sorted(card_items, key=lambda item: tuple(reversed(item.scenePos().toTuple())))

    @property
    def cut_lines(self) -> list[QGraphicsLineItem]:
        return [item for item in self.items(SortOrder.AscendingOrder)
                if is_cut_line_item(item) and not self._is_registration_item(item)]

    @property
    def text_items(self) -> list[QGraphicsSimpleTextItem]:
        return [item for item in self.items(SortOrder.AscendingOrder)
                if is_text_item(item) and not self._is_registration_item(item)]

    def _is_registration_item(self, item: QGraphicsItem) -> bool:
        # PySide6 6.11.2 parentItem() gives a parentless item Python ownership,
        # even when its scene owns it. Avoid traversing unrelated card trees.
        if not any(root == item or root.isAncestorOf(item) for root in self.print_markers):
            return False
        ancestor = item
        while ancestor is not None:
            if ancestor in self.print_markers:
                return True
            ancestor = ancestor.parentItem()
        return False

    @Slot(QPersistentModelIndex)
    def on_current_page_changed(self, selected_page: QPersistentModelIndex):
        """Draws the canvas, when the currently selected page changes."""
        logger.debug(f"Current page changed to page {selected_page.row()}")
        self.selected_page = QPersistentModelIndex(selected_page)
        self._clear_card_items()
        if self._refresh_actual_geometry():
            self._update_text_items(self.document.page_layout)
            self._draw_cards()
            self.update_card_bleeds()

    def _update_page_text_y(self):
        # Guide caches derive from snapshots and retain the legacy implicit-margin translation.
        y_edges = [edge for page_type in (PageType.REGULAR, PageType.OVERSIZED)
                   for edge in self.horizontal_cut_line_locations[page_type][-1:]]
        if not y_edges:
            self.document_title_text.setVisible(False)
            self.page_number_text.setVisible(False)
            return
        y = 2 + distance_to_rounded_px(self.document.page_layout.card_bleed) + round(max(y_edges))
        for item in self.text_items:
            item.setY(y)

    def _update_page_text_x(self):
        edges = self.vertical_cut_line_locations[PageType.REGULAR]
        if not edges:
            self.document_title_text.setVisible(False)
            self.page_number_text.setVisible(False)
            return
        self.document_title_text.setX(round(edges[0]))
        font_metrics = QFontMetrics(self.page_number_text.font())
        text_width = font_metrics.horizontalAdvance(self.page_number_text.text())
        self.page_number_text.setX(round(edges[-1]) - text_width - 2 + self.x_offset)

    def _update_page_number_text(self):
        if self.page_number_text not in self.text_items:
            return  # Rendering page numbers disabled, so skipping the update
        logger.debug("Updating page number text")
        page = self.selected_page.row() + 1
        total_pages = self.document.rowCount()
        self.page_number_text.setText(f"{page}/{total_pages}")

    def _update_print_markers(self):
        background_color = self.get_background_color(self.render_mode)
        self.background.setPen(background_color)
        self.background.setBrush(background_color)
        if self.geometry is None:
            self._clear_registration_items()
            return
        profile = get_registration_profile(self.document.page_layout.print_registration_marks_style)
        try:
            if profile is not self._registration_profile:
                self._clear_registration_items()
                self._registration_profile = profile
                self.print_markers = profile.create_items()
                for item in self.print_markers:
                    self.addItem(item)
            profile.place_items(self.print_markers, self.geometry, legacy_x_offset_px=self.x_offset)
        except (ValueError, RuntimeError) as error:
            if profile.profile_id != RegistrationProfileId.SISER:
                raise
            self._clear_registration_items()
            self.registration_unavailable_reason = str(error)
            return
        self.registration_unavailable_reason = None
        self._restore_registration_stacking()

    def _clear_registration_items(self):
        for item in self.print_markers:
            self.removeItem(item)
        self.print_markers.clear()
        self._registration_profile = None
        self.registration_unavailable_reason = None

    def _restore_registration_stacking(self):
        guides = self.cut_lines
        for root in self.print_markers:
            parent = root.parentItem()
            if parent is None:
                root.scene()  # Restore PySide scene ownership without another C++ insertion.
            for guide in guides:
                guide_parent = guide.parentItem()
                if guide_parent is None:
                    guide.scene()
                if parent == guide_parent and root.zValue() == guide.zValue():
                    root.stackBefore(guide)
                    break

    @Slot(PageLayoutSettings)
    def on_page_layout_changed(self, new_page_layout: PageLayoutSettings):
        logger.info("Applying new document settings …")
        new_page_size = self.get_document_page_size(new_page_layout)
        self._rebuild_full_grid_geometry()
        old_size = self.sceneRect()
        size_changed = old_size != new_page_size
        if size_changed:
            logger.debug("Page size changed. Adjusting PageScene dimensions")
            self.setSceneRect(new_page_size)
            self.background.setRect(new_page_size)
        self._update_cut_marker_positions()
        self._refresh_actual_geometry()
        self.remove_cut_markers()
        if new_page_layout.draw_cut_markers and self.geometry is not None:
            self.draw_cut_markers()
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
        visible = self.geometry is not None and bool(self.full_grid_geometry[PageType.REGULAR].grid_x_edges_px)
        self.document_title_text.setVisible(visible)
        self.page_number_text.setVisible(visible)

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
        if not without_margins:
            nominal = build_page_geometry(page_layout, PageType.UNDETERMINED, 0)
            return QRectF(0, 0, nominal.scene_width_px, nominal.scene_height_px)
        vertical_margins = (page_layout.margin_top + page_layout.margin_bottom) if without_margins else ZERO_WIDTH
        horizontal_margins = (page_layout.margin_left + page_layout.margin_right) if without_margins else ZERO_WIDTH

        height: Quantity = page_layout.page_height - vertical_margins
        width: Quantity = page_layout.page_width - horizontal_margins
        page_size = QRectF(
            QPointF(0, 0),
            QSizeF(
                distance_to_rounded_px(width),
                distance_to_rounded_px(height),
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

    def draw_card(self, index: QModelIndex, page_type: PageType):
        if self.geometry is None or not index.isValid():
            return
        if any(item.index == index for item in self.card_items):
            return
        if index.data(ItemDataRole.DisplayRole) is not None:
            placement = self.geometry.placements[index.row()]
            card_item = CardItem(index, self.document)
            self.addItem(card_item)
            card_item.setPos(self._presentation_position(placement.trim_px.x, placement.trim_px.y))

    def update_card_positions(self):
        if self.geometry is None:
            return
        for card in self.card_items:
            if card.index.isValid():
                trim = self.geometry.placements[card.index.row()].trim_px
                card.setPos(self._presentation_position(trim.x, trim.y))

    def _is_valid_page_index(self, index: QModelIndex | QPersistentModelIndex):
        return (index.isValid() and index.model() == self.document
                and not index.parent().isValid() and index.row() < self.document.rowCount())

    @Slot(QModelIndex)
    def on_page_type_changed(self, page: QModelIndex):
        if page == self.selected_page and self._refresh_actual_geometry():
            self.update_card_positions()
            self.update_card_bleeds()
            self._update_text_items(self.document.page_layout)

    @Slot(QModelIndex, QModelIndex, list)
    def on_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex, roles: list[ItemDataRole]):
        parent = top_left.parent()
        if parent != self.selected_page or (roles and ItemDataRole.DisplayRole not in roles):
            return
        if not (top_left.column() <= PageColumns.Image <= bottom_right.column()):
            return
        if not self._refresh_actual_geometry():
            return
        # Resolve by persistent model slot, including holes left by missing pixmaps.
        for row in range(top_left.row(), bottom_right.row() + 1):
            index = self.document.index(row, PageColumns.Image, parent)
            for item in self.card_items:
                if item.index == index:
                    self.removeItem(item)
            self.draw_card(index, self.geometry.page_type)
        self.update_card_positions()
        self.update_card_bleeds()

    @Slot(QModelIndex, int, int)
    def on_rows_inserted(self, parent: QModelIndex, first: int, last: int):
        if self._is_valid_page_index(parent) and parent == self.selected_page:
            if not self._refresh_actual_geometry():
                return
            inserted_cards = last-first+1
            needs_reorder = first + inserted_cards < self.document.rowCount(parent)
            page_type: PageType = self.selected_page.data(ItemDataRole.UserRole)
            logger.debug(f"Added {inserted_cards} cards to the currently shown page, drawing them.")
            model = parent.model()
            for new in range(first, last+1):
                self.draw_card(model.index(new, PageColumns.Image, parent), page_type)
            if needs_reorder:
                logger.debug("Cards added in the middle of the page, re-order existing cards.")
                self.update_card_positions()
            self.update_card_bleeds()
        elif not parent.isValid():
            # Page inserted. Update the page number text, as it contains the total number of pages
            self._update_page_number_text()
            self._retry_pending_geometry()

    @Slot(QModelIndex, int, int)
    def on_rows_about_to_be_removed(self, parent: QModelIndex, first: int, last: int):
        if not parent.isValid() and first <= self.selected_page.row() <= last:
            logger.debug("About to delete the currently shown page. Removing the held index.")
            self.selected_page = QPersistentModelIndex()
            self._geometry_unavailable("Selected page is being removed")
        elif parent.isValid() and parent.row() == self.selected_page.row():
            # Remove the cards now, as the model indices are still valid and point to the correct cards
            logger.debug(f"Removing cards {first} to {last} from the current page.")
            for item in self.card_items:
                # Identify the cards by their internal index. The list position is arbitrary.
                # Update the positions of the remaining cards later, when their new position is known
                if first <= item.index.row() <= last:
                    self.removeItem(item)

    @Slot(QModelIndex)
    def on_rows_removed(self, parent: QModelIndex):
        if not parent.isValid():
            # Page removed. Update the page number text, as it contains the total number of pages
            self._update_page_number_text()
            self._retry_pending_geometry()
        if parent.isValid() and parent == self.selected_page:
            if not self._refresh_actual_geometry():
                return
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
            if self._refresh_actual_geometry():
                self.update_card_positions()
                self.update_card_bleeds()
        # Remaining cases are card moves happening "off-screen", so nothing has to be done on them.

    def _compute_position_for_image(self, index_row: int, page_type: PageType) -> QPointF:
        """Compatibility query for any full-capacity slot, not actual occupancy."""
        if page_type == PageType.UNDETERMINED:
            page_type = PageType.REGULAR
        trim = self.full_grid_geometry[page_type].placements[index_row].trim_px
        return self._presentation_position(trim.x, trim.y)

    def update_card_bleeds(self):
        if self.geometry is None:
            return
        for item in self.card_items:
            if item.index.isValid():
                bleed = self.geometry.placements[item.index.row()].bleed_px
                item.bleeds.update_bleeds(top=bleed.top, bottom=bleed.bottom, left=bleed.left, right=bleed.right)

    def _has_neighbors(self, item: CardItem) -> NeighborsPresent:
        """Compatibility only: adjacency cannot be inferred from bleed size."""
        placement = self.geometry.placements[item.index.row()]
        occupied = {(p.row, p.column) for p in self.geometry.placements}
        row, column = placement.row, placement.column
        return NeighborsPresent((row - 1, column) in occupied, (row + 1, column) in occupied,
                                (row, column - 1) in occupied, (row, column + 1) in occupied)

    def remove_cut_markers(self):
        for line in self.cut_lines:
            self.removeItem(line)

    def draw_cut_markers(self):
        """Draws the optional cut markers that extend to the paper border"""
        if self.geometry is None:
            return
        page_type = self.geometry.page_type
        pen = self.get_cut_marker_pen(self.render_mode)
        logger.info(f"Drawing cut markers")
        layer = RenderLayers.CUT_LINES_ABOVE \
            if self.document.page_layout.cut_marker_draw_above_cards else RenderLayers.CUT_LINES_BELOW
        self._draw_vertical_markers(pen, page_type, layer)
        self._draw_horizontal_markers(pen, page_type, layer)
        self._restore_registration_stacking()

    def _update_cut_marker_positions(self):
        self.vertical_cut_line_locations.clear()
        self.horizontal_cut_line_locations.clear()
        frame = self.full_grid_geometry[PageType.REGULAR].margin_frame_px
        left = frame.x if RenderMode.IMPLICIT_MARGINS in self.render_mode else 0
        top = frame.y if RenderMode.IMPLICIT_MARGINS in self.render_mode else 0
        for page_type in (PageType.UNDETERMINED, PageType.REGULAR, PageType.OVERSIZED):
            geometry = self.full_grid_geometry[PageType.REGULAR if page_type == PageType.UNDETERMINED else page_type]
            self.vertical_cut_line_locations[page_type] = [edge - left for edge in geometry.grid_x_edges_px]
            self.horizontal_cut_line_locations[page_type] = [edge - top for edge in geometry.grid_y_edges_px]

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
