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

from collections.abc import Iterable
import dataclasses
import itertools
import math
from typing import TYPE_CHECKING, Any

from pint import Quantity
from PySide6.QtGui import QPageLayout, QPageSize, QColor, QColorConstants
from PySide6.QtCore import QMarginsF, QSizeF, Qt

import mtg_proxy_printer.settings
import mtg_proxy_printer.sqlite_helpers
from mtg_proxy_printer.logger import get_logger
from mtg_proxy_printer.settings import VALID_CUT_MARKER_STYLES
from mtg_proxy_printer.units_and_sizes import PageType, CardSize, CardSizes, unit_registry, ConfigParser, distance_to_mm
if TYPE_CHECKING:
    from mtg_proxy_printer.page_scene.page_scene import RenderMode
logger = get_logger(__name__)
del get_logger
PenStyle = Qt.PenStyle

__all__ = [
    "PageLayoutSettings",
]



def _is_quantity_setting(pair: tuple[str, Any]):
    return isinstance(pair[1], Quantity)


@dataclasses.dataclass
class PageLayoutSettings:
    """Stores all page layout attributes, like paper size, margins and spacings"""
    card_bleed: Quantity = 0 * unit_registry.mm
    cut_marker_color: QColor = dataclasses.field(default_factory=lambda: QColorConstants.Black)
    cut_marker_draw_above_cards: bool = False
    cut_marker_style: str = "None"  # TODO: Can this be Literal["None", "Solid", "Dots", "Dashes"] instead of str
    cut_marker_width: Quantity = 0 * unit_registry.mm
    document_name: str = ""
    draw_page_numbers: bool = False
    draw_sharp_corners: bool = False
    row_spacing: Quantity = 0 * unit_registry.mm
    column_spacing: Quantity = 0 * unit_registry.mm
    margin_bottom: Quantity = 0 * unit_registry.mm
    margin_left: Quantity = 0 * unit_registry.mm
    margin_right: Quantity = 0 * unit_registry.mm
    margin_top: Quantity = 0 * unit_registry.mm
    custom_page_height: Quantity = 0 * unit_registry.mm
    custom_page_width: Quantity = 0 * unit_registry.mm
    paper_orientation: str = "Portrait"  # TODO: Here, too. Literal["Portrait", "Landscape"] instead of str
    paper_size: str = "Custom"
    print_registration_marks_style: str = "None"  # TODO: Here, too.
    watermark_angle: Quantity = 0 * unit_registry.degree
    watermark_color: QColor = dataclasses.field(default_factory=lambda: QColorConstants.Transparent)
    watermark_font_size: Quantity = 0 * unit_registry.point
    watermark_pos_x: Quantity = 0 * unit_registry.mm
    watermark_pos_y: Quantity = 0 * unit_registry.mm
    watermark_text: str = ""

    @property
    def draw_cut_markers(self) -> bool:
        return self.cut_marker_style != "None"


    def cut_marker_pen_style(self) -> PenStyle:
        return VALID_CUT_MARKER_STYLES[self.cut_marker_style]

    @property
    def page_height(self) -> Quantity:
        if self.paper_size == "Custom":
            return self.custom_page_height
        page_size = mtg_proxy_printer.units_and_sizes.PageSizeManager.PageSize[self.paper_size]
        size = QPageSize.size(page_size, QPageSize.Unit.Millimeter)
        value = size.height() if self.paper_orientation == "Portrait" else size.width()
        return value*unit_registry.mm

    @page_height.setter
    def page_height(self, value: Quantity):
        assert isinstance(value, Quantity)
        self.custom_page_height = value

    @property
    def page_width(self) -> Quantity:
        if self.paper_size == "Custom":
            return self.custom_page_width
        page_size = mtg_proxy_printer.units_and_sizes.PageSizeManager.PageSize[self.paper_size]
        size = QPageSize.size(page_size, QPageSize.Unit.Millimeter)
        value = size.width() if self.paper_orientation == "Portrait" else size.height()
        return value*unit_registry.mm

    @page_width.setter
    def page_width(self, value: Quantity):
        assert isinstance(value, Quantity)
        self.custom_page_width = value

    @classmethod
    def create_from_settings(cls, settings: ConfigParser = mtg_proxy_printer.settings.settings):
        document_settings = settings["documents"]
        return cls(
            document_settings.get_quantity("card-bleed"),
            document_settings.get_color("cut-marker-color"),
            document_settings.getboolean("cut-marker-draw-above-cards"),
            document_settings["cut-marker-style"],
            document_settings.get_quantity("cut-marker-width"),
            document_settings["default-document-name"],
            document_settings.getboolean("print-page-numbers"),
            document_settings.getboolean("print-sharp-corners"),
            document_settings.get_quantity("row-spacing"),
            document_settings.get_quantity("column-spacing"),
            document_settings.get_quantity("margin-bottom"),
            document_settings.get_quantity("margin-left"),
            document_settings.get_quantity("margin-right"),
            document_settings.get_quantity("margin-top"),
            document_settings.get_quantity("custom-page-height"),
            document_settings.get_quantity("custom-page-width"),
            document_settings["paper-orientation"],
            document_settings["paper-size"],
            document_settings["print-registration-marks-style"],
            document_settings.get_quantity("watermark-angle"),
            document_settings.get_color("watermark-color"),
            document_settings.get_quantity("watermark-font-size"),
            document_settings.get_quantity("watermark-pos-x"),
            document_settings.get_quantity("watermark-pos-y"),
            document_settings["watermark-text"],
        )

    def to_page_layout(self, render_mode: "RenderMode") -> QPageLayout:
        margins = QMarginsF(
            distance_to_mm(self.margin_left), distance_to_mm(self.margin_top),
            distance_to_mm(self.margin_right), distance_to_mm(self.margin_bottom)) \
            if render_mode.IMPLICIT_MARGINS in render_mode else QMarginsF(0, 0, 0, 0)
        landscape_workaround = mtg_proxy_printer.settings.settings["printer"].getboolean(
            "landscape-compatibility-workaround")
        if self.paper_size == "Custom":
            logger.debug(
                f"Creating custom QPageLayout for a custom paper size of {self.page_width}mm×{self.page_height}mm")
            orientation = QPageLayout.Orientation.Portrait \
                if self.page_width < self.page_height or landscape_workaround \
                else QPageLayout.Orientation.Landscape
            page_size = QPageSize(
                QSizeF(*sorted([distance_to_mm(self.page_width), distance_to_mm(self.page_height)])),
                QPageSize.Unit.Millimeter,
            )
            layout = QPageLayout(
                page_size,
                orientation,
                margins,
                QPageLayout.Unit.Millimeter,
            )
        else:
            logger.debug(
                f"Creating QPageLayout for paper size {self.paper_size} and orientation {self.paper_orientation}")
            layout = QPageLayout(
                QPageSize(mtg_proxy_printer.units_and_sizes.PageSizeManager.PageSize[self.paper_size]),
                mtg_proxy_printer.units_and_sizes.PageSizeManager.PageOrientation[self.paper_orientation],
                margins,
            )
        return layout

    def to_save_file_data(self):
        values = dataclasses.asdict(self)
        settings = itertools.starmap(self._setting_to_str, itertools.filterfalse(_is_quantity_setting, values.items()))
        dimensions = filter(_is_quantity_setting, values.items())
        return settings, dimensions

    @staticmethod
    def _setting_to_str(key: str, value: Any) -> tuple[str, str]:
        if isinstance(value, str):
            pass
        elif isinstance(value, QColor):
            value = value.name(QColor.NameFormat.HexArgb)
        else:
            value = str(value)
        return key, value

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"'<' not supported between instances of '{self.__class__.__name__}' and '{other.__class__.__name__}'")
        return self.compute_page_card_capacity(PageType.REGULAR) \
            < other.compute_page_card_capacity(PageType.REGULAR) \
            or self.compute_page_card_capacity(PageType.OVERSIZED) \
            < other.compute_page_card_capacity(PageType.OVERSIZED)

    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"'>' not supported between instances of '{self.__class__.__name__}' and '{other.__class__.__name__}'")
        return self.compute_page_card_capacity(PageType.REGULAR) \
            > other.compute_page_card_capacity(PageType.REGULAR) \
            or self.compute_page_card_capacity(PageType.OVERSIZED) \
            > other.compute_page_card_capacity(PageType.OVERSIZED)

    def update(self, other: Iterable[tuple[str, Any]]):
        known_keys = set(self.__annotations__.keys())
        for key, value in other:
            if key in known_keys:
                setattr(self, key, value)

    def compute_page_column_count(self, page_type: PageType = PageType.REGULAR) -> int:
        """Returns the total number of card columns that fit on this page."""
        card_size: CardSize = CardSizes.for_page_type(page_type)
        card_width = distance_to_mm(card_size.width)
        available_width = distance_to_mm(self.page_width - (self.margin_left + self.margin_right))

        if available_width <= card_width:
            return 0
        cards = 1 + math.floor(
            (available_width - card_width) /
            (card_width + distance_to_mm(self.column_spacing)))
        return cards

    def compute_page_row_count(self, page_type: PageType = PageType.REGULAR) -> int:
        """Returns the total number of card rows that fit on this page."""
        card_size: CardSize = CardSizes.for_page_type(page_type)
        card_height = distance_to_mm(card_size.height)
        available_height = distance_to_mm(self.page_height - (self.margin_top + self.margin_bottom))

        if available_height <= card_height:
            return 0
        cards = 1 + math.floor(
            (available_height - card_height) /
            (card_height + distance_to_mm(self.row_spacing))
        )
        return cards

    def compute_page_card_capacity(self, page_type: PageType = PageType.REGULAR) -> int:
        """Returns the total number of card images that fit on a single page."""
        return self.compute_page_row_count(page_type) * self.compute_page_column_count(page_type)
