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

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QGraphicsObject, QGraphicsItem, QGraphicsLineItem

from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.units_and_sizes import PageType
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


class CutLineGridItem(QGraphicsObject):
    """The cut helper line grid"""

    def __init__(self, /, document: Document, page_type: PageType, parent: QGraphicsItem | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.page_type = page_type
        document.page_layout_changed.connect(self.on_page_layout_changed)
        self._line_items: list[QGraphicsLineItem] = []
        logger.debug(f"Created {self.__class__.__name__} instance with grid for {page_type}")

    @Slot
    def on_page_layout_changed(self, new_layout: PageLayoutSettings):
        column_count = new_layout.compute_page_column_count(self.page_type)
        row_count = new_layout.compute_page_row_count(self.page_type)
        width = 1000
        height = 1000

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
