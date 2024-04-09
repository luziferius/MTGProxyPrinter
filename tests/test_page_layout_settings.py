# Copyright (C) 2020-2024 Thomas Hess <thomas.hess@udo.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import unittest.mock

import mtg_proxy_printer.settings
import mtg_proxy_printer.model.document
import mtg_proxy_printer.model.document_loader
from mtg_proxy_printer.units_and_sizes import PageType
from mtg_proxy_printer.ui.page_scene import RenderMode

from PySide6.QtGui import QPageLayout, QPageSize
from PySide6.QtCore import QMarginsF
import pytest
from hamcrest import *
PageLayoutSettings = mtg_proxy_printer.model.document_loader.PageLayoutSettings

from tests.hasgetter import has_getters


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
    (0, 3, PageType.REGULAR),
    (0, 3, PageType.UNDETERMINED),

    (11, 3, PageType.REGULAR),
    (11, 3, PageType.UNDETERMINED),
    (12, 2, PageType.REGULAR),
    (12, 2, PageType.UNDETERMINED),

    (111, 2, PageType.REGULAR),
    (111, 2, PageType.UNDETERMINED),
    (112, 1, PageType.REGULAR),
    (112, 1, PageType.UNDETERMINED),

    (0, 2, PageType.OVERSIZED),

    (35, 2, PageType.OVERSIZED),
    (36, 1, PageType.OVERSIZED),

    # Spacing is between multiple rows. So any large value should result in at least 1 row,
    # because there is no spacing with one row
    (1000, 1, PageType.REGULAR),
    (1000, 1, PageType.UNDETERMINED),
    (1000, 1, PageType.OVERSIZED),
])
def test_page_layout_compute_page_row_count(
        page_layout: PageLayoutSettings, page_type: PageType, row_spacing: int, expected: int):
    page_layout.row_spacing = row_spacing
    assert_that(page_layout.compute_page_row_count(page_type), is_(equal_to(expected)))


def test_page_layout_compute_compute_page_row_count_default_value(page_layout: PageLayoutSettings):
    assert_that(page_layout.compute_page_row_count(), is_(equal_to(3)))


@pytest.mark.parametrize("column_spacing, expected, page_type", [
    (0, 3, PageType.REGULAR),
    (0, 3, PageType.UNDETERMINED),

    (5, 3, PageType.REGULAR),
    (5, 3, PageType.UNDETERMINED),
    (6, 2, PageType.REGULAR),
    (6, 2, PageType.UNDETERMINED),

    (74, 2, PageType.REGULAR),
    (74, 2, PageType.UNDETERMINED),
    (75, 1, PageType.REGULAR),
    (75, 1, PageType.UNDETERMINED),

    (0, 2, PageType.OVERSIZED),

    (24, 2, PageType.OVERSIZED),
    (25, 1, PageType.OVERSIZED),

    # Spacing is between multiple columns. So any large value should result in at least 1 column,
    # because there is no spacing with only one column
    (1000, 1, PageType.REGULAR),
    (1000, 1, PageType.UNDETERMINED),
    (1000, 1, PageType.OVERSIZED),
])
def test_page_layout_compute_page_column_count(
        page_layout: PageLayoutSettings, page_type: PageType, column_spacing: int, expected: int):
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
    layout.page_height = 300
    assert_that(layout.compute_page_card_capacity(PageType.REGULAR), is_(0))
    assert_that(layout, is_not(greater_than(layout)))


def test_page_layout_lt():
    layout = mtg_proxy_printer.model.document_loader.PageLayoutSettings.create_from_settings()
    assert_that(layout.compute_page_card_capacity(PageType.REGULAR), is_(9))
    assert_that(layout, is_not(less_than(layout)))


def test_create_from_settings():
    values = {
        "paper-height-mm": "200",
        "paper-width-mm": "100",
        "margin-top-mm": "9",
        "margin-bottom-mm": "8",
        "margin-left-mm": "7",
        "margin-right-mm": "6",
        "row-spacing-mm": "2",
        "column-spacing-mm": "1",
        "print-cut-marker": "True",
        "print-sharp-corners": "True",
        "print-page-numbers": "True",
        "default-document-name": "Test",
    }
    with unittest.mock.patch.dict(mtg_proxy_printer.settings.settings["documents"], values):
        layout = PageLayoutSettings.create_from_settings()
    assert_that(
        layout, has_properties(
            document_name="Test",
            draw_cut_markers=True,
            draw_page_numbers=True,
            draw_sharp_corners=True,
            row_spacing=2,
            column_spacing=1,
            margin_bottom=8,
            margin_left=7,
            margin_right=6,
            margin_top=9,
            page_height=200,
            page_width=100,
        )
    )


@pytest.mark.parametrize("height, width, landscape_workaround, orientation", [
    (297, 210, True, QPageLayout.Orientation.Portrait),
    (297, 210, False, QPageLayout.Orientation.Portrait),
    (210, 297, True, QPageLayout.Orientation.Portrait),
    (210, 297, False, QPageLayout.Orientation.Landscape),
])
@pytest.mark.parametrize("render_mode, margins", [
    (RenderMode(0), QMarginsF(0, 0, 0, 0)),
    (RenderMode.IMPLICIT_MARGINS, QMarginsF(1, 2, 3, 4)),
])
def test_to_page_layout(
        page_layout: PageLayoutSettings,
        render_mode: RenderMode, margins: QMarginsF,
        height: int, width: int, landscape_workaround: bool, orientation: QPageLayout.Orientation
):
    page_layout.page_height = height
    page_layout.page_width = width
    page_layout.margin_left = 1
    page_layout.margin_top = 2
    page_layout.margin_right = 3
    page_layout.margin_bottom = 4
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
