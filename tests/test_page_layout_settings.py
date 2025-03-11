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


import unittest.mock

import mtg_proxy_printer.settings
import mtg_proxy_printer.model.document
import mtg_proxy_printer.model.document_loader
from mtg_proxy_printer.units_and_sizes import PageType, QuantityT, UnitT, unit_registry, StrDict
from mtg_proxy_printer.ui.page_scene import RenderMode

from PySide6.QtGui import QPageLayout, QPageSize
from PySide6.QtCore import QMarginsF
import pytest
from hamcrest import *
PageLayoutSettings = mtg_proxy_printer.model.document_loader.PageLayoutSettings

from tests.hasgetter import has_getters
from tests.helpers import quantity_close_to

mm: UnitT = unit_registry.mm


@pytest.fixture
def page_layout():
    layout = PageLayoutSettings.create_from_settings()
    return layout


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
        page_layout: PageLayoutSettings, page_type: PageType, row_spacing: QuantityT, expected: int):
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
        page_layout: PageLayoutSettings, page_type: PageType, column_spacing: QuantityT, expected: int):
    page_layout.column_spacing = column_spacing
    assert_that(page_layout.compute_page_column_count(page_type), is_(equal_to(expected)))


def test_page_layout_compute_page_column_count_default_value(page_layout: PageLayoutSettings):
    assert_that(page_layout.compute_page_column_count(), is_(equal_to(3)))


def test_page_layout_gt_raises_type_error_on_incompatible_types(page_layout: PageLayoutSettings):
    assert_that(calling(page_layout.__gt__).with_args(1), raises(TypeError))


def test_page_layout_lt_raises_type_error_on_incompatible_types(page_layout: PageLayoutSettings):
    assert_that(calling(page_layout.__lt__).with_args(1), raises(TypeError))


def test_page_layout_gt():
    layout = mtg_proxy_printer.model.document_loader.PageLayoutSettings()
    layout.page_height = 300*mm
    assert_that(layout.compute_page_card_capacity(PageType.REGULAR), is_(0))
    assert_that(layout, is_not(greater_than(layout)))


def test_page_layout_lt():
    layout = mtg_proxy_printer.model.document_loader.PageLayoutSettings.create_from_settings()
    assert_that(layout.compute_page_card_capacity(PageType.REGULAR), is_(9))
    assert_that(layout, is_not(less_than(layout)))


@pytest.mark.parametrize("values", [
    {
        "paper-height": "200 mm",
        "paper-width": "100 mm",
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
    },
    {
        "paper-height": "200 millimeter",
        "paper-width": "100 millimeter",
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
    },
])
def test_create_from_settings(values: StrDict):
    with unittest.mock.patch.dict(mtg_proxy_printer.settings.settings["documents"], values):
        layout = PageLayoutSettings.create_from_settings()
    assert_that(
        layout, has_properties(
            document_name=equal_to("Test"),
            draw_cut_markers=is_(True),
            draw_page_numbers=is_(True),
            draw_sharp_corners=is_(True),
            row_spacing=quantity_close_to(2*mm),
            column_spacing=quantity_close_to(1*mm),
            margin_bottom=quantity_close_to(8*mm),
            margin_left=quantity_close_to(7*mm),
            margin_right=quantity_close_to(6*mm),
            margin_top=quantity_close_to(9*mm),
            page_height=quantity_close_to(200*mm),
            page_width=quantity_close_to(100*mm),
        )
    )


@pytest.mark.parametrize("height, width, landscape_workaround, orientation", [
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
        height: QuantityT, width: QuantityT, landscape_workaround: bool, orientation: QPageLayout.Orientation
):
    page_layout.page_height = height
    page_layout.page_width = width
    page_layout.margin_left = 1*mm
    page_layout.margin_top = 2*mm
    page_layout.margin_right = 3*mm
    page_layout.margin_bottom = 4*mm
    section = mtg_proxy_printer.settings.settings["printer"]
    with unittest.mock.patch.dict(section, {"landscape-compatibility-workaround": str(landscape_workaround)}):
        q_page_layout = page_layout.to_page_layout(render_mode)
    assert_that(q_page_layout, has_getters(
        margins=has_getters(
            left=margins.left(),
            top=margins.top(),
            right=margins.right(),
            bottom=margins.bottom(),
        ),
        isValid=True,
        orientation=orientation,
    ))
    assert_that(q_page_layout.pageSize().size(QPageSize.Unit.Millimeter), has_getters(
        height=close_to(297, 0.01),
        width=close_to(210, 0.01),
    ))

def test_to_save_file_data_contains_all_keys(page_layout: PageLayoutSettings):
    data = [key for key, value in page_layout.to_save_file_data()]
    assert_that(
        data,
        contains_inanyorder(*PageLayoutSettings.__annotations__.keys()),
    )

def test_to_save_file_data_returns_only_acceptable_types(page_layout: PageLayoutSettings):
    data = [value for key, value in page_layout.to_save_file_data()]
    assert_that(
        data,
        only_contains(instance_of(str), instance_of(float), instance_of(bool), instance_of(int)),
    )
