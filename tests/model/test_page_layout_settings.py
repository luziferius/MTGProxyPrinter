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

import itertools
import unittest.mock

import mtg_proxy_printer.settings
import mtg_proxy_printer.model.document
import mtg_proxy_printer.async_tasks.document_loader
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.units_and_sizes import PageType, PageSizeManager, unit_registry, StrDict, Quantity
from mtg_proxy_printer.page_scene.page_scene import RenderMode

from PySide6.QtGui import QPageLayout, QPageSize, QColorConstants
from PySide6.QtCore import QMarginsF
import pytest
from hamcrest import *

from tests.hasgetter import has_getters
from tests.helpers import quantity_close_to, close_to_

mm = unit_registry.mm
HexArgb = QColorConstants.Red.NameFormat.HexArgb


@pytest.mark.parametrize("page_type, expected", [
    (PageType.OVERSIZED, 4),
    (PageType.REGULAR, 9),
    (PageType.MIXED, 9),
    (PageType.UNDETERMINED, 9),
])
def test_page_layout_compute_page_card_capacity(page_layout: PageLayoutSettings, page_type: PageType, expected: int):
    assert_that(
        page_layout.compute_page_card_capacity(page_type),
        is_(equal_to(expected))
    )


def test_page_layout_compute_page_card_capacity_default_value(page_layout: PageLayoutSettings):
    assert_that(page_layout.compute_page_card_capacity(), is_(equal_to(9)))


@pytest.mark.parametrize("row_spacing, expected, page_type", [
    (0*mm, 3, PageType.REGULAR),
    (0*mm, 3, PageType.UNDETERMINED),

    (11*mm, 3, PageType.REGULAR),
    (11*mm, 3, PageType.UNDETERMINED),
    (12*mm, 2, PageType.REGULAR),
    (12*mm, 2, PageType.UNDETERMINED),

    (110*mm, 2, PageType.REGULAR),
    (110*mm, 2, PageType.UNDETERMINED),
    (111*mm, 1, PageType.REGULAR),
    (111*mm, 1, PageType.UNDETERMINED),

    (0*mm, 2, PageType.OVERSIZED),

    (34*mm, 2, PageType.OVERSIZED),
    (35*mm, 1, PageType.OVERSIZED),

    # Spacing is between multiple rows. So any large value should result in at least 1 row,
    # because there is no spacing with one row
    (1000*mm, 1, PageType.REGULAR),
    (1000*mm, 1, PageType.UNDETERMINED),
    (1000*mm, 1, PageType.OVERSIZED),
])
def test_page_layout_compute_page_row_count(
        page_layout: PageLayoutSettings, page_type: PageType, row_spacing: Quantity, expected: int):
    assert_that(page_layout.page_height, quantity_close_to(297*mm), "Setup failed: Environment altered")
    assert_that(page_layout.margin_top, quantity_close_to(5*mm), "Setup failed: Environment altered")
    assert_that(page_layout.margin_bottom, quantity_close_to(5*mm), "Setup failed: Environment altered")
    page_layout.row_spacing = row_spacing
    assert_that(page_layout.compute_page_row_count(page_type), is_(equal_to(expected)))


def test_page_layout_compute_compute_page_row_count_default_value(page_layout: PageLayoutSettings):
    assert_that(page_layout.compute_page_row_count(), is_(equal_to(3)))


@pytest.mark.parametrize("column_spacing, expected, page_type", [
    (0*mm, 3, PageType.REGULAR),
    (0*mm, 3, PageType.UNDETERMINED),

    (5*mm, 3, PageType.REGULAR),
    (5*mm, 3, PageType.UNDETERMINED),
    (6*mm, 2, PageType.REGULAR),
    (6*mm, 2, PageType.UNDETERMINED),

    (73*mm, 2, PageType.REGULAR),
    (73*mm, 2, PageType.UNDETERMINED),
    (74*mm, 1, PageType.REGULAR),
    (74*mm, 1, PageType.UNDETERMINED),

    (0*mm, 2, PageType.OVERSIZED),

    (23*mm, 2, PageType.OVERSIZED),
    (24*mm, 1, PageType.OVERSIZED),

    # Spacing is between multiple columns. So any large value should result in at least 1 column,
    # because there is no spacing with only one column
    (1000*mm, 1, PageType.REGULAR),
    (1000*mm, 1, PageType.UNDETERMINED),
    (1000*mm, 1, PageType.OVERSIZED),
])
def test_page_layout_compute_page_column_count(
        page_layout: PageLayoutSettings, page_type: PageType, column_spacing: Quantity, expected: int):
    page_layout.column_spacing = column_spacing
    assert_that(page_layout.compute_page_column_count(page_type), is_(equal_to(expected)))


def test_page_layout_compute_page_column_count_default_value(page_layout: PageLayoutSettings):
    assert_that(page_layout.compute_page_column_count(), is_(equal_to(3)))


def test_page_layout_gt_raises_type_error_on_incompatible_types(page_layout: PageLayoutSettings):
    assert_that(calling(page_layout.__gt__).with_args(1), raises(TypeError))


def test_page_layout_lt_raises_type_error_on_incompatible_types(page_layout: PageLayoutSettings):
    assert_that(calling(page_layout.__lt__).with_args(1), raises(TypeError))


def test_page_layout_gt(page_layout: PageLayoutSettings):
    page_layout.paper_size = "Custom"
    page_layout.paper_orientation = "Portrait"
    page_layout.custom_page_width = 10 * mm
    assert_that(page_layout.compute_page_card_capacity(PageType.REGULAR), is_(0))
    assert_that(page_layout, is_not(greater_than(page_layout)))


def test_page_layout_lt(page_layout: PageLayoutSettings):
    assert_that(page_layout.compute_page_card_capacity(PageType.REGULAR), is_(9))
    assert_that(page_layout, is_not(less_than(page_layout)))


@pytest.mark.parametrize("values", [
    {
        "custom-page-height": "200 mm",
        "custom-page-width": "100 mm",
        "cut-marker-color": QColorConstants.Black.name(HexArgb),
        "cut-marker-draw-above-cards": "True",
        "cut-marker-style": "Solid",
        "cut-marker-width": "0.5 mm",
        "margin-top": "9 mm",
        "margin-bottom": "8 mm",
        "margin-left": "7 mm",
        "margin-right": "6 mm",
        "row-spacing": "2 mm",
        "column-spacing": "1 mm",
        "print-cut-marker": "True",
        "print-sharp-corners": "True",
        "print-page-numbers": "True",
        "default-document-name": "Test",
        "paper-orientation": "Portrait",
        "paper-size": "Custom",
        "watermark-text": "Watermark",
        "watermark-font-size": "20 point",
        "watermark-pos-x": "50 mm",
        "watermark-pos-y": "49 mm",
        "watermark-angle": "42°",
        "watermark-color": QColorConstants.Red.name(HexArgb),
    },
    {
        "custom-page-height": "200 millimeter",
        "custom-page-width": "100 millimeter",
        "cut-marker-color": QColorConstants.Black.name(HexArgb),
        "cut-marker-draw-above-cards": "True",
        "cut-marker-style": "Solid",
        "cut-marker-width": "0.5 millimeter",
        "margin-top": "9 millimeter",
        "margin-bottom": "8 millimeter",
        "margin-left": "7 millimeter",
        "margin-right": "6 millimeter",
        "row-spacing": "2 millimeter",
        "column-spacing": "1 millimeter",
        "print-cut-marker": "True",
        "print-sharp-corners": "True",
        "print-page-numbers": "True",
        "default-document-name": "Test",
        "paper-orientation": "Portrait",
        "paper-size": "Custom",
        "watermark-text": "Watermark",
        "watermark-font-size": "20 points",
        "watermark-pos-x": "50 millimeter",
        "watermark-pos-y": "49 millimeter",
        "watermark-angle": "42 degree",
        "watermark-color": QColorConstants.Red.name(HexArgb),
    },
])
def test_create_from_settings(values: StrDict):
    with unittest.mock.patch.dict(mtg_proxy_printer.settings.settings["documents"], values):
        layout = PageLayoutSettings.create_from_settings()
    assert_that(
        layout, has_properties(
            cut_marker_color=equal_to(QColorConstants.Black),
            cut_marker_draw_above_cards=is_(True),
            cut_marker_style=equal_to("Solid"),
            cut_marker_width=quantity_close_to(0.5*mm),
            document_name=equal_to("Test"),
            draw_page_numbers=is_(True),
            draw_sharp_corners=is_(True),
            row_spacing=quantity_close_to(2*mm),
            column_spacing=quantity_close_to(1*mm),
            margin_bottom=quantity_close_to(8*mm),
            margin_left=quantity_close_to(7*mm),
            margin_right=quantity_close_to(6*mm),
            margin_top=quantity_close_to(9*mm),
            custom_page_height=quantity_close_to(200*mm),
            custom_page_width=quantity_close_to(100*mm),
            paper_orientation=equal_to("Portrait"),
            paper_size=equal_to("Custom"),
            watermark_text=equal_to("Watermark"),
            watermark_font_size=quantity_close_to(20*unit_registry.point),
            watermark_pos_x=quantity_close_to(50*mm),
            watermark_pos_y=quantity_close_to(49*mm),
            watermark_angle=quantity_close_to(42*unit_registry.degree),
            watermark_color=equal_to(QColorConstants.Red),
        )
    )


@pytest.mark.parametrize("height, width, landscape_workaround, expected_orientation", [
    (297*mm, 210*mm, True, QPageLayout.Orientation.Portrait),
    (297*mm, 210*mm, False, QPageLayout.Orientation.Portrait),
    (210*mm, 297*mm, True, QPageLayout.Orientation.Portrait),
    (210*mm, 297*mm, False, QPageLayout.Orientation.Landscape),
])
@pytest.mark.parametrize("render_mode, margins", [
    (RenderMode(0), QMarginsF(0, 0, 0, 0)),
    (RenderMode.IMPLICIT_MARGINS, QMarginsF(1, 2, 3, 4)),
])
def test_to_page_layout(
        page_layout: PageLayoutSettings,
        render_mode: RenderMode, margins: QMarginsF,
        height: Quantity, width: Quantity, landscape_workaround: bool, expected_orientation: QPageLayout.Orientation
):
    page_layout.custom_page_height = height
    page_layout.custom_page_width = width
    page_layout.paper_size = "Custom"
    page_layout.paper_orientation = PageSizeManager.PageOrientationReverse[expected_orientation]
    page_layout.margin_left = 1*mm
    page_layout.margin_top = 2*mm
    page_layout.margin_right = 3*mm
    page_layout.margin_bottom = 4*mm
    section = mtg_proxy_printer.settings.settings["printer"]
    with unittest.mock.patch.dict(section, {"landscape-compatibility-workaround": str(landscape_workaround)}):
        q_page_layout = page_layout.to_page_layout(render_mode)
    assert_that(q_page_layout, has_getters(
        margins=has_getters(
            left=close_to_(margins.left()),
            top=close_to_(margins.top()),
            right=close_to_(margins.right()),
            bottom=close_to_(margins.bottom()),
        ),
        isValid=True,
        orientation=equal_to(expected_orientation),
    ))
    assert_that(q_page_layout.pageSize().size(QPageSize.Unit.Millimeter), has_getters(
        height=close_to(max(height.to(mm).magnitude, width.to(mm).magnitude), 0.01),
        width=close_to(min(height.to(mm).magnitude, width.to(mm).magnitude), 0.01),
    ))


def test_to_save_file_data_contains_all_keys(page_layout: PageLayoutSettings):
    data = [key for key, value in itertools.chain.from_iterable(page_layout.to_save_file_data())]
    assert_that(
        data,
        contains_inanyorder(*PageLayoutSettings.__annotations__.keys()),
    )


def test_to_save_file_data_returns_only_acceptable_types(page_layout: PageLayoutSettings):
    settings, dimensions = page_layout.to_save_file_data()
    assert_that(
        [value for key, value in settings],
        only_contains(instance_of(str)),
    )
    assert_that(
        [value for key, value in dimensions],
        only_contains(instance_of(Quantity)),
    )
