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
import typing

from PySide6.QtCore import Slot, QPersistentModelIndex, Qt
from PySide6.QtWidgets import QGraphicsObject, QGraphicsItem, QGraphicsLineItem, QApplication, QGraphicsItemGroup
from PySide6.QtGui import QPen, QPalette, QColorConstants

if typing.TYPE_CHECKING:
    from mtg_proxy_printer.page_scene.page_scene import RenderMode

from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.page_scene.items import RenderLayers
from mtg_proxy_printer.units_and_sizes import PageType, CardSizes, distance_to_rounded_px
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

ItemDataRole = Qt.ItemDataRole
ColorGroup = QPalette.ColorGroup
ColorRole = QPalette.ColorRole
__all__ = [
    "CutLineGridItem",
]


class CutLineGridItem(QGraphicsItemGroup, QGraphicsObject):
    """
    The cut helper line grid.
    Origin (0,0) is the top left corner of the top left slot.
    Line lengths are larger than the scene dimensions and stretch to negative positions to allow moving the grid
    on the scene as a whole without exposing line ends.
    """

    def __init__(self, /, document: Document, page_type: PageType, render_mode: "RenderMode",
                 parent: QGraphicsItem | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.page_type = page_type
        self.document = document
        self.render_mode = render_mode
        document.page_layout_changed.connect(self.on_page_layout_changed)
        document.current_page_changed.connect(self.on_current_page_changed)
        self._line_items: list[QGraphicsLineItem] = []
        self.grid_width = self.grid_height = 0  # type: int
        logger.debug(f"Created {self.__class__.__name__} instance with grid for {page_type}")

    @Slot(PageLayoutSettings)
    def on_page_layout_changed(self, new_layout: PageLayoutSettings):
        """Updates the line grid when the page layout changes."""
        # A full re-creation isn't expensive, and much easier than trying to compute a minimal diff,
        # and updating positions.
        for item in self._line_items:
            item.setParentItem(None)
        self._line_items.clear()
        layer = RenderLayers.CUT_LINES_ABOVE if new_layout.cut_marker_draw_above_cards else RenderLayers.CUT_LINES_BELOW
        self.setZValue(layer.value)
        # Use opacity == 0 to fully hide the grid if cut markers are disabled
        self.setOpacity(new_layout.draw_cut_markers)
        card_size = CardSizes.for_page_type(self.page_type).as_qsize_px()
        row_spacing = distance_to_rounded_px(new_layout.row_spacing)
        column_spacing = distance_to_rounded_px(new_layout.column_spacing)
        pen = self.get_cut_marker_pen(new_layout)
        column_count = new_layout.compute_page_column_count(self.page_type)
        row_count = new_layout.compute_page_row_count(self.page_type)
        horizontal_length, vertical_length = self._get_line_lengths()
        x_positions = self._compute_positions(card_size.height(), row_spacing, row_count)
        y_positions = self._compute_positions(card_size.width(), column_spacing, column_count)
        for pos_x in x_positions:
            self._draw_horizontal_line(pos_x, horizontal_length, pen)
        for pos_y in y_positions:
            self._draw_vertical_line(pos_y, vertical_length, pen)
        self.grid_width = y_positions[-1]
        self.grid_height = x_positions[-1]

    def update_line_pen(self) -> None:
        """Update the line pen for all contained line items"""
        pen = self.get_cut_marker_pen(self.document.page_layout)
        for item in self._line_items:
            item.setPen(pen)

    @Slot(QPersistentModelIndex)
    def on_current_page_changed(self, selected_page: QPersistentModelIndex):
        """Updates the cut line visibility, when the currently selected page changes."""
        current_page_type: PageType = selected_page.data(ItemDataRole.UserRole)
        this_grid_applies_to_new_page = (
            (current_page_type == self.page_type) or
            (current_page_type == PageType.UNDETERMINED and self.page_type == PageType.REGULAR)
        )
        self.setVisible(this_grid_applies_to_new_page)

    def _get_line_lengths(self) -> tuple[float, float]:
        scene = self.scene()
        return scene.width()*2.1, scene.height()*2.1

    def _draw_vertical_line(self, column_px: float | int, length: float | int, pen: QPen) -> None:
        line = QGraphicsLineItem(0, -length/2, 0, length, self)
        line.setPen(pen)
        line.setX(column_px)
        self._line_items.append(line)

    def _draw_horizontal_line(self, row_px: float | int, length: float | int, pen: QPen) -> None:
        line = QGraphicsLineItem(-length/2, 0, length, 0, self)
        line.setPen(pen)
        line.setY(row_px)
        self._line_items.append(line)

    @staticmethod
    def _compute_positions(card_size: int, spacing_size: int, count: int) -> list[int]:
        """
        Compute the line positions in one dimension in local coordinates.
        Takes one of (card width, horizontal spacing, column count) or (card height, vertical spacing, row count)
        Returns the list of pixel values in ascending order
        """
        lower = set(range(0, (card_size+spacing_size)*count, card_size+spacing_size))
        upper = set(item+card_size for item in lower)
        combined = lower.union(upper)
        result = sorted(combined)
        return result

    def get_cut_marker_pen(self, layout: PageLayoutSettings) -> QPen:
        # TODO: Move helper constructs into a separate module, obsoleting this circular import workaround
        from mtg_proxy_printer.page_scene.page_scene import RenderMode
        scene = self.scene()
        palette = QApplication.palette() if scene is None else scene.palette()
        if (RenderMode.ON_PAPER not in self.render_mode
                and layout.cut_marker_color == QColorConstants.Black):
            # Rendering on screen with the default black supports using a color scheme override for dark mode rendering
            color = palette.color(ColorGroup.Active, ColorRole.WindowText)
        else:
            color = layout.cut_marker_color
        return QPen(
            color, layout.cut_marker_width.to("point", "print").magnitude, layout.cut_marker_pen_style()
        )
