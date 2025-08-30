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

import itertools
from functools import partial
import typing
from unittest.mock import patch
from math import ceil

from hamcrest import *
import pytest

from pint import Quantity, Unit
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsLineItem
from PySide6.QtGui import QPalette, QColorConstants, QPixmap, QImage, QColor, QPainter
from PySide6.QtCore import QPoint

from mtg_proxy_printer.units_and_sizes import PageType, CardSizes, CardSize, unit_registry
from mtg_proxy_printer.page_scene.page_scene import RenderMode, PageScene
from mtg_proxy_printer.page_scene.items import NeighborsPresent
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard, ActionRemoveCards
from mtg_proxy_printer.document_controller.compact_document import ActionCompactDocument
from mtg_proxy_printer.model.document import Document

from tests.document_controller.helpers import create_card
from tests.hasgetter import has_getters
from tests.helpers import close_to_

PATH_PREFIX = "mtg_proxy_printer.ui.page_renderer.PageScene."
RenderHint = QPainter.RenderHint
ColorGroup = QPalette.ColorGroup
ColorRole = QPalette.ColorRole
mm: Unit = unit_registry.mm


def _fill_area(image: QImage, fill_color: QColor, pos: QPoint, width: int = 5, height: int = 5):
    for x, y in itertools.product(range(width), range(height)):  # type: int, int
        image.setPixelColor(pos+QPoint(x, y), fill_color)


def create_card_with_pixmap(name: str, size: CardSize = CardSizes.REGULAR, *, color = QColorConstants.Transparent):
    """
    Create a Card with the given size, and fill the pixmap with the given color.
    Each corner has a square transparent area, as a crude emulation of rounded corners.
    """
    card = create_card(name, size)
    image_size = size.as_qsize_px()
    image = QImage(image_size, QImage.Format.Format_ARGB32)
    image.fill(color)
    fill_transparent = partial(_fill_area, image, QColorConstants.Transparent)
    fill_transparent(QPoint(0, 0))
    fill_transparent(QPoint(0, image_size.height()-5))
    fill_transparent(QPoint(image_size.width()-5, 0))
    fill_transparent(QPoint(image_size.width()-5, image_size.height()-5))
    card.set_image_file(QPixmap.fromImage(image))
    return card

@pytest.fixture(params=itertools.product(
    [RenderMode.ON_PAPER, RenderMode.ON_SCREEN],
    [True, False]))
def page_scene(request, document_light: Document):
    """Creates a PageScene in each available rendering mode"""
    render_mode, enable_text_items = request.param  # type: RenderMode, bool
    with patch.object(document_light.page_layout, "draw_page_numbers", enable_text_items), \
         patch.object(document_light.page_layout, "document_name", "Non-empty title" if enable_text_items else ""):
        scene = PageScene(document_light, render_mode)
        yield scene

def render_scene(scene: PageScene) -> QImage:
    image = QImage(ceil(scene.width()), ceil(scene.height()), QImage.Format.Format_ARGB32)
    image.fill(QColorConstants.Transparent)
    painter = QPainter(image)
    painter.setRenderHint(RenderHint.LosslessImageRendering, True)
    scene.render(painter)
    return image


@pytest.mark.parametrize("render_mode", [RenderMode.ON_PAPER, RenderMode.ON_SCREEN])
def test___init__does_not_add_text_items_if_disabled(document_light: Document, render_mode: RenderMode):
    with patch.object(document_light.page_layout, "draw_page_numbers", False), \
         patch.object(document_light.page_layout, "document_name", ""):
        scene = PageScene(document_light, render_mode)
    assert_that(scene.text_items, is_(empty()))


@pytest.mark.parametrize("render_mode", [RenderMode.ON_PAPER, RenderMode.ON_SCREEN])
def test___init__adds_text_items_if_enabled(document_light: Document, render_mode: RenderMode):
    with patch.object(document_light.page_layout, "draw_page_numbers", True), \
         patch.object(document_light.page_layout, "document_name", "Non-empty title"):
        scene = PageScene(document_light, render_mode)
    assert_that(scene.text_items, has_length(2))


@pytest.mark.parametrize("count", [1, 2, 10])
@pytest.mark.parametrize("size", CardSizes)
def test_adding_with_card_to_filled_page_does_not_redraw_page(
        page_scene: PageScene, size: CardSize, count: int):
    document = page_scene.document
    document.apply(ActionAddCard(create_card_with_pixmap("Card", size)))
    with patch(PATH_PREFIX+"draw_cut_markers") as cut_markers_mock:
        document.apply(ActionAddCard(create_card_with_pixmap("Card", size), count))
    cut_markers_mock.assert_not_called()
    assert_that(
        page_scene.items(),
        has_items(*[instance_of(QGraphicsPixmapItem)]*len(document.currently_edited_page))
    )


def test_cut_lines_not_drawn_when_disabled_and_page_empty(page_scene: PageScene):
    document = page_scene.document
    document.page_layout.cut_marker_style = "None"
    document.page_layout_changed.emit(document.page_layout)
    assert_that(
        page_scene.items(), not_(has_items(instance_of(QGraphicsLineItem)))
    )
    assert_that(page_scene.cut_lines, is_(empty()))


@pytest.mark.parametrize("size", CardSizes)
def test_cut_lines_not_drawn_when_disabled_and_page_filled(page_scene: PageScene, size: CardSize):
    document = page_scene.document
    document.page_layout.cut_marker_style = "None"
    document.page_layout_changed.emit(document.page_layout)
    document.apply(ActionAddCard(create_card_with_pixmap("Card", size)))
    assert_that(
        page_scene.items(), not_(has_items(instance_of(QGraphicsLineItem)))
    )


@pytest.mark.parametrize("row_spacing, column_spacing", itertools.product([0*mm, 1*mm], repeat=2))
def test_cut_lines_property_only_lists_line_elements(
        page_scene: PageScene, row_spacing: Quantity, column_spacing: Quantity):
    layout = page_scene.document.page_layout
    layout.row_spacing = row_spacing
    layout.column_spacing = column_spacing
    layout.cut_marker_style = "Solid"
    page_scene.document.page_layout_changed.emit(layout)
    assert_that(
        page_scene.cut_lines, all_of(
            only_contains(instance_of(QGraphicsLineItem)),
            is_not(empty()),
        ),
        "cut_lines must only contain QGraphicsLineItem instances"
    )
    assert_that(
        page_scene.cut_lines,
        only_contains(*page_scene.items()),
        "cut_lines mut not contain lines not present in the PageScene"
    )


@pytest.mark.parametrize("cut_marker_style", ["Solid", "Dots", "Dashes"])
@pytest.mark.parametrize("row_spacing", [0*mm, 1*mm])
@pytest.mark.parametrize("column_spacing", [0*mm, 1*mm])
# TODO: Parameter for cut helper width
def test_cut_lines_bounding_rects_cross_entire_page(
        page_scene: PageScene, row_spacing: Quantity, column_spacing: Quantity, cut_marker_style: str):
    layout = page_scene.document.page_layout
    layout.row_spacing = row_spacing
    layout.column_spacing = column_spacing
    layout.cut_marker_style = cut_marker_style
    page_scene.document.page_layout_changed.emit(layout)
    page_width, page_height = page_scene.width(), page_scene.height()
    for index, line in enumerate(page_scene.cut_lines):
        rect = line.boundingRect()
        assert_that(rect, any_of(
            has_getters(width=0, height=close_to_(page_height)),
            has_getters(width=close_to_(page_width), height=0),
        ), f"Unexpected cut line bounding box at {index=}, {line.boundingRect()=}")
    '''
    assert_that(
        page_scene.cut_lines,
        only_contains(
            has_getter("boundingRect", has_getters(width=1, height=close_to_(page_height+1))),
            has_getter("boundingRect", has_getters(width=close_to_(page_width+1), height=1)),
        ),
        "Unexpected cut line bounding boxes"
    )
    '''


@pytest.mark.parametrize("page_type, spacing, margins, flags, expected_y", [
    (PageType.UNDETERMINED, 0, 0, RenderMode(0), [194, 1234, 2274, 3314]),
    (PageType.UNDETERMINED, 0, 5, RenderMode(0), [194, 1234, 2274, 3314]),
    (PageType.REGULAR, 0, 0, RenderMode(0), [194, 1234, 2274, 3314]),
    (PageType.REGULAR, 0, 5, RenderMode(0), [194, 1234, 2274, 3314]),
    (PageType.OVERSIZED, 0, 0, RenderMode(0), [264, 1754, 3244]),
    (PageType.OVERSIZED, 0, 5, RenderMode(0), [264, 1754, 3244]),

    (PageType.UNDETERMINED, 0, 0, RenderMode.IMPLICIT_MARGINS, [194, 1234, 2274, 3314]),
    (PageType.UNDETERMINED, 0, 5, RenderMode.IMPLICIT_MARGINS, [135, 1175, 2215, 3255]),
    (PageType.REGULAR, 0, 0, RenderMode.IMPLICIT_MARGINS, [194, 1234, 2274, 3314]),
    (PageType.REGULAR, 0, 5, RenderMode.IMPLICIT_MARGINS, [135, 1175, 2215, 3255]),
    (PageType.OVERSIZED, 0, 0, RenderMode.IMPLICIT_MARGINS, [264, 1754, 3244]),
    (PageType.OVERSIZED, 0, 5, RenderMode.IMPLICIT_MARGINS, [205, 1695, 3185]),

    (PageType.UNDETERMINED, 1, 0, RenderMode(0), [182, 1222, 1234, 2274, 2286, 3326]),
    (PageType.UNDETERMINED, 1, 5, RenderMode(0), [182, 1222, 1234, 2274, 2286, 3326]),
    (PageType.REGULAR, 1, 0, RenderMode(0), [182, 1222, 1234, 2274, 2286, 3326]),
    (PageType.REGULAR, 1, 5, RenderMode(0), [182, 1222, 1234, 2274, 2286, 3326]),
    (PageType.OVERSIZED, 1, 0, RenderMode(0), [258, 1748, 1760, 3250]),
    (PageType.OVERSIZED, 1, 5, RenderMode(0), [258, 1748, 1760, 3250]),
    
    (PageType.UNDETERMINED, 1, 0, RenderMode.IMPLICIT_MARGINS, [182, 1222, 1234, 2274, 2286, 3326]),
    (PageType.UNDETERMINED, 1, 5, RenderMode.IMPLICIT_MARGINS, [123, 1163, 1175, 2215, 2227, 3267]),
    (PageType.REGULAR, 1, 0, RenderMode.IMPLICIT_MARGINS, [182, 1222, 1234, 2274, 2286, 3326]),
    (PageType.REGULAR, 1, 5, RenderMode.IMPLICIT_MARGINS, [123, 1163, 1175, 2215, 2227, 3267]),
    (PageType.OVERSIZED, 1, 0, RenderMode.IMPLICIT_MARGINS, [258, 1748, 1760, 3250]),
    (PageType.OVERSIZED, 1, 5, RenderMode.IMPLICIT_MARGINS, [199, 1689, 1701, 3191]),

    # Large top margin, pushing the images down.
    # With implicit margins, the first element would otherwise have negative coordinates and gets truncated
    (PageType.UNDETERMINED, 0, 17, RenderMode(0), [201, 1241, 2281, 3321]),
    (PageType.UNDETERMINED, 1, 17, RenderMode(0), [201, 1241, 1253, 2293, 2305, 3345]),
    (PageType.REGULAR, 0, 17, RenderMode(0), [201, 1241, 2281, 3321]),
    (PageType.REGULAR, 1, 17, RenderMode(0), [201, 1241, 1253, 2293, 2305, 3345]),
    (PageType.OVERSIZED, 0, 23, RenderMode(0), [272, 1762, 3252]),
    (PageType.OVERSIZED, 1, 23, RenderMode(0), [272, 1762, 1774, 3264]),
    (PageType.UNDETERMINED, 0, 17, RenderMode.IMPLICIT_MARGINS, [0, 1040, 2080, 3120]),
    (PageType.UNDETERMINED, 1, 17, RenderMode.IMPLICIT_MARGINS, [0, 1040, 1052, 2092, 2104, 3144]),
    (PageType.REGULAR, 0, 17, RenderMode.IMPLICIT_MARGINS, [0, 1040, 2080, 3120]),
    (PageType.REGULAR, 1, 17, RenderMode.IMPLICIT_MARGINS, [0, 1040, 1052, 2092, 2104, 3144]),
    (PageType.OVERSIZED, 0, 23, RenderMode.IMPLICIT_MARGINS, [0, 1490, 2980]),
    (PageType.OVERSIZED, 1, 23, RenderMode.IMPLICIT_MARGINS, [0, 1490, 1502, 2992]),
    # TODO: Add cases for large bottom margin, pushing images up
])
def test_horizontal_cut_line_locations_when_enabled(
        page_scene: PageScene,
        page_type: PageType, spacing: int, margins: int, flags: RenderMode, expected_y: list):
    page_scene.render_mode |= flags
    document = page_scene.document
    document.page_layout.margin_top = margins*mm
    document.page_layout.margin_bottom = 0*mm
    document.page_layout.row_spacing = spacing*mm
    document.page_layout.cut_marker_style = "Solid"
    document.page_layout_changed.emit(document.page_layout)
    assert_that(
        document.page_layout.compute_page_card_capacity(page_type), is_in((4, 9)),
        "Test setup failed! Margins caused unexpected capacity decrease"
    )
    if page_type is not PageType.UNDETERMINED:
        card_size = CardSizes.for_page_type(page_type)
        document.apply(ActionAddCard(create_card_with_pixmap("Card", card_size)))

    assert_that(
        page_scene.horizontal_cut_line_locations[page_type],
        contains_inanyorder(*map(close_to_, expected_y)),
        f"Wrong values in {page_scene.horizontal_cut_line_locations[page_type]=}, "
        f"{RenderMode.IMPLICIT_MARGINS in page_scene.render_mode=}"
    )
    assert_that(
        page_scene.cut_lines,
        only_contains(
            has_getters(x=greater_than_or_equal_to(0), y=0),
            *[has_getters(x=0, y=close_to_(y)) for y in expected_y]
        )
    )


@pytest.mark.parametrize("page_type, spacing, margins, flags, expected_x", [
    (PageType.UNDETERMINED, 0, 0, RenderMode(0), [122.5, 867.5, 1612.5, 2357.5]),
    (PageType.UNDETERMINED, 0, 5, RenderMode(0), [122.5, 867.5, 1612.5, 2357.5]),
    (PageType.REGULAR, 0, 0, RenderMode(0), [122.5, 867.5, 1612.5, 2357.5]),
    (PageType.REGULAR, 0, 5, RenderMode(0), [122.5, 867.5, 1612.5, 2357.5]),
    (PageType.OVERSIZED, 0, 0, RenderMode(0), [200, 1240, 2280]),
    (PageType.OVERSIZED, 0, 5, RenderMode(0), [200, 1240, 2280]),
    
    (PageType.UNDETERMINED, 0, 0, RenderMode.IMPLICIT_MARGINS, [122.5, 867.5, 1612.5, 2357.5]),
    (PageType.UNDETERMINED, 0, 5, RenderMode.IMPLICIT_MARGINS, [63.5, 808.5, 1553.5, 2298.5]),
    (PageType.REGULAR, 0, 0, RenderMode.IMPLICIT_MARGINS, [122.5, 867.5, 1612.5, 2357.5]),
    (PageType.REGULAR, 0, 5, RenderMode.IMPLICIT_MARGINS, [63.5, 808.5, 1553.5, 2298.5]),
    (PageType.OVERSIZED, 0, 0, RenderMode.IMPLICIT_MARGINS, [200, 1240, 2280]),
    (PageType.OVERSIZED, 0, 5, RenderMode.IMPLICIT_MARGINS, [141, 1181, 2221]),

    (PageType.UNDETERMINED, 1, 0, RenderMode(0), [110.5, 855.5, 867.5, 1612.5, 1624.5, 2369.5]),
    (PageType.UNDETERMINED, 1, 5, RenderMode(0), [110.5, 855.5, 867.5, 1612.5, 1624.5, 2369.5]),
    (PageType.REGULAR, 1, 0, RenderMode(0), [110.5, 855.5, 867.5, 1612.5, 1624.5, 2369.5]),
    (PageType.REGULAR, 1, 5, RenderMode(0), [110.5, 855.5, 867.5, 1612.5, 1624.5, 2369.5]),
    (PageType.OVERSIZED, 1, 0, RenderMode(0), [194, 1234, 1246, 2286]),
    (PageType.OVERSIZED, 1, 5, RenderMode(0), [194, 1234, 1246, 2286]),

    (PageType.UNDETERMINED, 1, 0, RenderMode.IMPLICIT_MARGINS, [110.5, 855.5, 867.5, 1612.5, 1624.5, 2369.5]),
    (PageType.UNDETERMINED, 1, 5, RenderMode.IMPLICIT_MARGINS, [51.5, 796.5, 808.5, 1553.5, 1565.5, 2310.5]),
    (PageType.REGULAR, 1, 0, RenderMode.IMPLICIT_MARGINS, [110.5, 855.5, 867.5, 1612.5, 1624.5, 2369.5]),
    (PageType.REGULAR, 1, 5, RenderMode.IMPLICIT_MARGINS, [51.5, 796.5, 808.5, 1553.5, 1565.5, 2310.5]),
    (PageType.OVERSIZED, 1, 0, RenderMode.IMPLICIT_MARGINS, [194, 1234, 1246, 2286]),
    (PageType.OVERSIZED, 1, 5, RenderMode.IMPLICIT_MARGINS, [135, 1175, 1187, 2227]),
    # Large left margin, pushing the images to the right.
    # With implicit margins, the first element would otherwise have negative coordinates and gets truncated
    (PageType.UNDETERMINED, 0, 17, RenderMode(0), [201, 946, 1691, 2436]),
    (PageType.UNDETERMINED, 1, 17, RenderMode(0), [201, 946, 958, 1703, 1715, 2460]),
    (PageType.REGULAR, 0, 17, RenderMode(0), [201, 946, 1691, 2436]),
    (PageType.REGULAR, 1, 17, RenderMode(0), [201, 946, 958, 1703, 1715, 2460]),
    (PageType.OVERSIZED, 0, 23, RenderMode(0), [272, 1312, 2352]),
    (PageType.OVERSIZED, 1, 23, RenderMode(0), [272, 1312, 1324, 2364]),
    (PageType.UNDETERMINED, 0, 17, RenderMode.IMPLICIT_MARGINS, [0, 745, 1490, 2235]),
    (PageType.UNDETERMINED, 1, 17, RenderMode.IMPLICIT_MARGINS, [0, 745, 757, 1502, 1514, 2259]),
    (PageType.REGULAR, 0, 17, RenderMode.IMPLICIT_MARGINS, [0, 745, 1490, 2235]),
    (PageType.REGULAR, 1, 17, RenderMode.IMPLICIT_MARGINS, [0, 745, 757, 1502, 1514, 2259]),
    (PageType.OVERSIZED, 0, 23, RenderMode.IMPLICIT_MARGINS, [0, 1040, 2080]),
    (PageType.OVERSIZED, 1, 23, RenderMode.IMPLICIT_MARGINS, [0, 1040, 1052, 2092]),
    # TODO: Add cases for large right margins pushing images to the left
])
def test_vertical_cut_line_locations_when_enabled(
        page_scene: PageScene,
        page_type: PageType, spacing: int, margins: int, flags: RenderMode, expected_x: list[float]):
    page_scene.render_mode |= flags
    document = page_scene.document
    document.page_layout.margin_left = margins*mm
    document.page_layout.margin_right = 0*mm
    document.page_layout.column_spacing = spacing*mm
    document.page_layout.cut_marker_style = "Solid"
    document.page_layout_changed.emit(document.page_layout)
    assert_that(
        document.page_layout.compute_page_card_capacity(page_type), is_in((4, 9)),
        "Test setup failed! Margins caused unexpected capacity decrease"
    )
    if page_type is not PageType.UNDETERMINED:
        card_size = CardSizes.for_page_type(page_type)
        document.apply(ActionAddCard(create_card_with_pixmap("Card", card_size)))

    assert_that(
        page_scene.vertical_cut_line_locations[page_type],
        contains_inanyorder(*map(close_to_, expected_x)),
        f"Wrong values in {page_scene.vertical_cut_line_locations[page_type]=}, "
        f"{RenderMode.IMPLICIT_MARGINS in page_scene.render_mode=}"
    )
    assert_that(
        page_scene.cut_lines,
        only_contains(
            has_getters(x=0, y=greater_than_or_equal_to(0)),
            *[has_getters(x=close_to_(x), y=0) for x in expected_x]
        )
    )


@pytest.mark.parametrize("page_type, spacing, margin, flags, expected_x", [
    (PageType.REGULAR, 0, 0, RenderMode(0), [122.5, 867.5, 1612.5]),
    (PageType.REGULAR, 0, 5, RenderMode(0), [122.5, 867.5, 1612.5]),
    (PageType.OVERSIZED, 0, 0, RenderMode(0), [200, 1240]),
    (PageType.OVERSIZED, 0, 5, RenderMode(0), [200, 1240]),
    
    (PageType.REGULAR, 1, 0, RenderMode(0), [110.5, 867.5, 1624.5]),
    (PageType.REGULAR, 1, 5, RenderMode(0), [110.5, 867.5, 1624.5]),
    (PageType.OVERSIZED, 1, 0, RenderMode(0), [194, 1246]),
    (PageType.OVERSIZED, 1, 5, RenderMode(0), [194, 1246]),

    (PageType.REGULAR, 0, 0, RenderMode.IMPLICIT_MARGINS, [122.5, 867.5, 1612.5]),
    (PageType.REGULAR, 0, 5, RenderMode.IMPLICIT_MARGINS, [63.5, 808.5, 1553.5]),
    (PageType.OVERSIZED, 0, 0, RenderMode.IMPLICIT_MARGINS, [200, 1240]),
    (PageType.OVERSIZED, 0, 5, RenderMode.IMPLICIT_MARGINS, [141, 1181]),

    (PageType.REGULAR, 1, 0, RenderMode.IMPLICIT_MARGINS, [110.5, 867.5, 1624.5]),
    (PageType.REGULAR, 1, 5, RenderMode.IMPLICIT_MARGINS, [51.5, 808.5, 1565.5]),
    (PageType.OVERSIZED, 1, 0, RenderMode.IMPLICIT_MARGINS, [194, 1246]),
    (PageType.OVERSIZED, 1, 5, RenderMode.IMPLICIT_MARGINS, [135, 1187]),

    # Large left margin, pushing the images to the right.
    # With implicit margins, the first element would otherwise have negative coordinates and gets truncated
    (PageType.UNDETERMINED, 0, 17, RenderMode(0), [201, 946, 1691]),
    (PageType.UNDETERMINED, 1, 17, RenderMode(0), [201, 958, 1715]),
    (PageType.REGULAR, 0, 17, RenderMode(0), [201, 946, 1691]),
    (PageType.REGULAR, 1, 17, RenderMode(0), [201, 958, 1715]),
    (PageType.OVERSIZED, 0, 23, RenderMode(0), [272, 1312]),
    (PageType.OVERSIZED, 1, 23, RenderMode(0), [272, 1324]),
    (PageType.UNDETERMINED, 0, 17, RenderMode.IMPLICIT_MARGINS, [0, 745, 1490]),
    (PageType.UNDETERMINED, 1, 17, RenderMode.IMPLICIT_MARGINS, [0, 757, 1514]),
    (PageType.REGULAR, 0, 17, RenderMode.IMPLICIT_MARGINS, [0, 745, 1490]),
    (PageType.REGULAR, 1, 17, RenderMode.IMPLICIT_MARGINS, [0, 757, 1514]),
    (PageType.OVERSIZED, 0, 23, RenderMode.IMPLICIT_MARGINS, [0, 1040]),
    (PageType.OVERSIZED, 1, 23, RenderMode.IMPLICIT_MARGINS, [0, 1052]),
    # TODO: Add cases for large right margins pushing images to the left
])
def test__compute_position_for_image_x(
        page_scene: PageScene,
        page_type: PageType, spacing: int, margin: int, flags: RenderMode, expected_x: list[int]):
    page_scene.render_mode |= flags
    document = page_scene.document
    document.page_layout.column_spacing = spacing*mm
    document.page_layout.margin_left = margin*mm
    document.page_layout.margin_right = 0*mm
    document.page_layout_changed.emit(document.page_layout)
    page_capacity = document.page_layout.compute_page_card_capacity(page_type)
    row_count = document.page_layout.compute_page_row_count(page_type)
    card = create_card_with_pixmap("Something", CardSizes.for_page_type(page_type))
    document.apply(ActionAddCard(card, 1))
    x_coordinates = [page_scene._compute_position_for_image(index, page_type).x() for index in range(page_capacity)]
    assert_that(
        x_coordinates, contains_exactly(*[close_to_(x) for x in expected_x]*row_count),
        f"Unexpected values: {x_coordinates}"
    )


def elementwise_repeat(items: typing.Iterable, times: int) -> list:
    duplicates = (itertools.repeat(item, times) for item in items)
    return list(itertools.chain.from_iterable(duplicates))


@pytest.mark.parametrize("page_type, spacing, margin, flags, expected_y", [
    (PageType.REGULAR, 0, 0, RenderMode(0), [194, 1234, 2274]),
    (PageType.REGULAR, 0, 5, RenderMode(0), [194, 1234, 2274]),
    (PageType.OVERSIZED, 0, 0, RenderMode(0), [264, 1754]),
    (PageType.OVERSIZED, 0, 5, RenderMode(0), [264, 1754]),

    (PageType.REGULAR, 1, 0, RenderMode(0), [182, 1234, 2286]),
    (PageType.REGULAR, 1, 5, RenderMode(0), [182, 1234, 2286]),
    (PageType.OVERSIZED, 1, 0, RenderMode(0), [258, 1760]),
    (PageType.OVERSIZED, 1, 5, RenderMode(0), [258, 1760]),

    (PageType.REGULAR, 0, 0, RenderMode.IMPLICIT_MARGINS, [194, 1234, 2274]),
    (PageType.REGULAR, 0, 5, RenderMode.IMPLICIT_MARGINS, [135, 1175, 2215]),
    (PageType.OVERSIZED, 0, 0, RenderMode.IMPLICIT_MARGINS, [264, 1754]),
    (PageType.OVERSIZED, 0, 5, RenderMode.IMPLICIT_MARGINS, [205, 1695]),

    (PageType.REGULAR, 1, 0, RenderMode.IMPLICIT_MARGINS, [182, 1234, 2286]),
    (PageType.REGULAR, 1, 5, RenderMode.IMPLICIT_MARGINS, [123, 1175, 2227]),
    (PageType.OVERSIZED, 1, 0, RenderMode.IMPLICIT_MARGINS, [258, 1760]),
    (PageType.OVERSIZED, 1, 5, RenderMode.IMPLICIT_MARGINS, [199, 1701]),

    # Large top margin, pushing the images down.
    # With implicit margins, the first element would otherwise have negative coordinates and gets truncated
    (PageType.UNDETERMINED, 0, 17, RenderMode(0), [201, 1241, 2281]),
    (PageType.UNDETERMINED, 1, 17, RenderMode(0), [201, 1253, 2305]),
    (PageType.REGULAR, 0, 17, RenderMode(0), [201, 1241, 2281]),
    (PageType.REGULAR, 1, 17, RenderMode(0), [201, 1253, 2305]),
    (PageType.OVERSIZED, 0, 23, RenderMode(0), [272, 1762]),
    (PageType.OVERSIZED, 1, 23, RenderMode(0), [272, 1774]),
    (PageType.UNDETERMINED, 0, 17, RenderMode.IMPLICIT_MARGINS, [0, 1040, 2080]),
    (PageType.UNDETERMINED, 1, 17, RenderMode.IMPLICIT_MARGINS, [0, 1052, 2104]),
    (PageType.REGULAR, 0, 17, RenderMode.IMPLICIT_MARGINS, [0, 1040, 2080]),
    (PageType.REGULAR, 1, 17, RenderMode.IMPLICIT_MARGINS, [0, 1052, 2104]),
    (PageType.OVERSIZED, 0, 23, RenderMode.IMPLICIT_MARGINS, [0, 1490]),
    (PageType.OVERSIZED, 1, 23, RenderMode.IMPLICIT_MARGINS, [0, 1502]),
])
def test__compute_position_for_image_y(
        page_scene: PageScene,
        page_type: PageType, spacing: int, margin: int, flags: RenderMode, expected_y: list[int]):
    page_scene.render_mode |= flags
    document = page_scene.document
    document.page_layout.row_spacing = spacing*mm
    document.page_layout.margin_top = margin*mm
    document.page_layout.margin_bottom = 0*mm
    document.page_layout_changed.emit(document.page_layout)
    page_capacity = document.page_layout.compute_page_card_capacity(page_type)
    column_count = document.page_layout.compute_page_column_count(page_type)
    card = create_card_with_pixmap("Something", CardSizes.for_page_type(page_type))
    document.apply(ActionAddCard(card, 1))
    y_coordinates = [page_scene._compute_position_for_image(index, page_type).y() for index in range(page_capacity)]
    assert_that(
        y_coordinates, contains_exactly(*elementwise_repeat([close_to_(y) for y in expected_y], column_count)),
        f"Unexpected values: {y_coordinates}"
    )


@pytest.mark.parametrize("removed_range", [range(1), range(2), range(1, 3), range(9)])
def test_compacting_document_moves_cards_onto_currently_shown_page(page_scene: PageScene, removed_range: range):
    # Test for issue [b33546aa1cbd62f3e1e7852bfc89a206fed89501]. PageScene crashes when compacting a document
    # moves cards onto the currently shown page.

    # Setup
    document = page_scene.document
    page_capacity = document.page_layout.compute_page_card_capacity(PageType.REGULAR)
    card = create_card_with_pixmap("Something")
    document.apply(ActionAddCard(card, page_capacity*2))
    document.apply(ActionRemoveCards(removed_range, 0))
    # Verify no IndexError is raised when handling signals during:
    document.apply(ActionCompactDocument())

    assert_that(
        page_scene.card_items,
        has_length(page_capacity)
    )


def test_setPalette_runs_without_exception(page_scene: PageScene):
    palette = QPalette()
    page_scene.setPalette(palette)


@pytest.mark.parametrize("color", [QColorConstants.Black, QColorConstants.Cyan])
@pytest.mark.parametrize("draw_sharp_corners", [True, False])
@pytest.mark.parametrize("card_bleed", [0*mm, 1*mm])
def test_sharp_corners(page_scene: PageScene, draw_sharp_corners: bool, color: QColor, card_bleed: Quantity):
    document = page_scene.document
    document.page_layout.draw_sharp_corners = draw_sharp_corners
    document.page_layout.card_bleed = card_bleed
    document.page_layout_changed.emit(document.page_layout)
    card = create_card_with_pixmap("Something", color=color)
    document.apply(ActionAddCard(card))

    pixmap_item = page_scene.card_items[0].card_pixmap_item
    top_left = pixmap_item.scenePos().toPoint()
    right, down = QPoint(card.image_file.width()-1, 0), QPoint(0, card.image_file.height()-1)

    rendered = render_scene(page_scene)
    expected_color =  color if draw_sharp_corners \
        else QColorConstants.Transparent if page_scene.render_mode == RenderMode.ON_PAPER \
        else page_scene.palette().color(ColorGroup.Active, ColorRole.Base)
    has_expected_color = is_(equal_to(expected_color))
    assert_that(rendered.pixelColor(top_left), has_expected_color, "Top left corner wrong")
    assert_that(rendered.pixelColor(top_left+right), has_expected_color, "Top right corner wrong")
    assert_that(rendered.pixelColor(top_left+down), has_expected_color, "Bottom left corner wrong")
    assert_that(rendered.pixelColor(top_left+right+down), has_expected_color, "Bottom right corner wrong")


@pytest.mark.parametrize("card_bleed", [0*mm, 1*mm])
def test_card_item_origin_equals_pixmap_origin(page_scene: PageScene, card_bleed: Quantity):
    document = page_scene.document
    document.page_layout.card_bleed = card_bleed
    document.page_layout_changed.emit(document.page_layout)
    card = create_card_with_pixmap("Something", color=QColorConstants.Black)
    document.apply(ActionAddCard(card))
    item = page_scene.card_items[0]
    assert_that(
        item.scenePos(), is_(equal_to(item.card_pixmap_item.scenePos()))
    )


@pytest.mark.parametrize("cards, neighbors", [
    (1, [NeighborsPresent(False, False, False, False)]),
    (2, [NeighborsPresent(False, False, False, True), NeighborsPresent(False, False, True, False)]),
    (3, [NeighborsPresent(False, False, False, True), NeighborsPresent(False, False, True, True), NeighborsPresent(False, False, True, False)]),

    (4, [NeighborsPresent(False, True, False, True), NeighborsPresent(False, False, True, True), NeighborsPresent(False, False, True, False),
         NeighborsPresent(True, False, False, False)]),

    (5, [NeighborsPresent(False, True, False, True), NeighborsPresent(False, True, True, True), NeighborsPresent(False, False, True, False),
         NeighborsPresent(True, False, False, True), NeighborsPresent(True, False, True, False)]),

    (6, [NeighborsPresent(False, True, False, True), NeighborsPresent(False, True, True, True), NeighborsPresent(False, True, True, False),
         NeighborsPresent(True, False, False, True), NeighborsPresent(True, False, True, True), NeighborsPresent(True, False, True, False)]),

    (7, [NeighborsPresent(False, True, False, True), NeighborsPresent(False, True, True, True), NeighborsPresent(False, True, True, False),
         NeighborsPresent(True, True, False, True), NeighborsPresent(True, False, True, True), NeighborsPresent(True, False, True, False),
         NeighborsPresent(True, False, False, False)]),

    (8, [NeighborsPresent(False, True, False, True), NeighborsPresent(False, True, True, True), NeighborsPresent(False, True, True, False),
         NeighborsPresent(True, True, False, True), NeighborsPresent(True, True, True, True), NeighborsPresent(True, False, True, False),
         NeighborsPresent(True, False, False, True), NeighborsPresent(True, False, True, False)]),

    (9, [NeighborsPresent(False, True, False, True), NeighborsPresent(False, True, True, True), NeighborsPresent(False, True, True, False),
         NeighborsPresent(True, True, False, True), NeighborsPresent(True, True, True, True), NeighborsPresent(True, True, True, False),
         NeighborsPresent(True, False, False, True), NeighborsPresent(True, False, True, True), NeighborsPresent(True, False, True, False)]),
])
def test__has_neighbors(page_scene: PageScene, cards: int, neighbors: list[NeighborsPresent]):
    page_scene.document.apply(ActionAddCard(create_card_with_pixmap("Something", color=QColorConstants.Black), cards))
    for index, item, expected in zip(range(cards), page_scene.card_items, neighbors):
        assert_that(page_scene._has_neighbors(item), is_(equal_to(expected)), f"Broken {index=}")


@pytest.mark.parametrize("color", [QColorConstants.Black, QColorConstants.Cyan])
@pytest.mark.parametrize("draw_sharp_corners", [False, True])
@pytest.mark.parametrize("card_bleed", [0*mm, 1*mm])
def test_card_bleed_with_single_card(
        page_scene: PageScene, draw_sharp_corners: bool, color: QColor, card_bleed: Quantity):
    document = page_scene.document
    document.page_layout.draw_sharp_corners = draw_sharp_corners
    document.page_layout.card_bleed = card_bleed
    document.page_layout_changed.emit(document.page_layout)
    document.apply(ActionAddCard(create_card_with_pixmap("Something", color=color)))

    size = CardSizes.REGULAR.as_qsize_px()
    right = QPoint(size.width() - 1, 0)
    down = QPoint(0, size.height() - 1)
    half_right, half_down = right/2, down/2
    h_1 = QPoint(1, 0)
    h_12 = QPoint(12, 0)
    h_13 = QPoint(13, 0)
    v_1 = QPoint(0, 1)
    v_12 = QPoint(0, 12)
    v_13 = QPoint(0, 13)

    top_left = page_scene.card_items[0].scenePos().toPoint()
    top_right = top_left + right
    bottom_left = top_left + down
    bottom_right = top_left + right+down

    top_center = top_left + half_right
    left_center = top_left + half_down
    right_center = top_right + half_down
    bottom_center = bottom_left + half_right
    
    rendered = render_scene(page_scene)
    background_color = QColorConstants.Transparent if page_scene.render_mode == RenderMode.ON_PAPER \
        else page_scene.palette().color(ColorGroup.Active, ColorRole.Base)
    expected_color = color if card_bleed > 0*mm else background_color

    has_expected_color = is_(equal_to(expected_color))
    has_background_color = is_(equal_to(background_color))

    # Top border
    # Inner bleed edge
    assert_that(rendered.pixelColor(top_left - v_1), has_expected_color)
    assert_that(rendered.pixelColor(top_center - v_1), has_expected_color)
    assert_that(rendered.pixelColor(top_right - v_1), has_expected_color)
    # Outer bleed edge
    assert_that(rendered.pixelColor(top_left - v_12), has_expected_color)
    assert_that(rendered.pixelColor(top_center - v_12), has_expected_color)
    assert_that(rendered.pixelColor(top_right - v_12), has_expected_color)
    # Outside bleed
    assert_that(rendered.pixelColor(top_left - v_13), has_background_color)
    assert_that(rendered.pixelColor(top_center - v_13), has_background_color)
    assert_that(rendered.pixelColor(top_right - v_13), has_background_color)

    # Bottom border
    # Inner bleed edge
    assert_that(rendered.pixelColor(bottom_left + v_1), has_expected_color)
    assert_that(rendered.pixelColor(bottom_center + v_1), has_expected_color)
    assert_that(rendered.pixelColor(bottom_right + v_1), has_expected_color)
    # Outer bleed edge
    assert_that(rendered.pixelColor(bottom_left + v_12), has_expected_color)
    assert_that(rendered.pixelColor(bottom_center + v_12), has_expected_color)
    assert_that(rendered.pixelColor(bottom_right + v_12), has_expected_color)
    # Outside bleed
    assert_that(rendered.pixelColor(bottom_left + v_13), has_background_color)
    assert_that(rendered.pixelColor(bottom_center + v_13), has_background_color)
    assert_that(rendered.pixelColor(bottom_right + v_13), has_background_color)
    
    # Left border
    # Inner bleed edge
    assert_that(rendered.pixelColor(top_left - h_1), has_expected_color)
    assert_that(rendered.pixelColor(left_center - h_1), has_expected_color)
    assert_that(rendered.pixelColor(bottom_left - h_1), has_expected_color)
    # Outer bleed edge
    assert_that(rendered.pixelColor(top_left - h_12), has_expected_color)
    assert_that(rendered.pixelColor(left_center - h_12), has_expected_color)
    assert_that(rendered.pixelColor(bottom_left - h_12), has_expected_color)
    # Outside bleed
    assert_that(rendered.pixelColor(top_left - h_13), has_background_color)
    assert_that(rendered.pixelColor(left_center - h_13), has_background_color)
    assert_that(rendered.pixelColor(bottom_left - h_13), has_background_color)
    
    # Right border
    # Inner bleed edge
    assert_that(rendered.pixelColor(top_right + h_1), has_expected_color)
    assert_that(rendered.pixelColor(right_center + h_1), has_expected_color)
    assert_that(rendered.pixelColor(bottom_right + h_1), has_expected_color)
    # Outer bleed edge
    assert_that(rendered.pixelColor(top_right + h_12), has_expected_color)
    assert_that(rendered.pixelColor(right_center + h_12), has_expected_color)
    assert_that(rendered.pixelColor(bottom_right + h_12), has_expected_color)
    # Outside bleed
    assert_that(rendered.pixelColor(top_right + h_13), has_background_color)
    assert_that(rendered.pixelColor(right_center + h_13), has_background_color)
    assert_that(rendered.pixelColor(bottom_right + h_13), has_background_color)


@pytest.mark.parametrize("column_spacing", [0*mm, 1*mm])
def test_card_bleed_with_two_cards(page_scene: PageScene, column_spacing: Quantity):
    document = page_scene.document
    document.page_layout.draw_sharp_corners = True
    document.page_layout.card_bleed = 1*mm
    document.page_layout.column_spacing = column_spacing
    document.page_layout_changed.emit(document.page_layout)
    document.apply(ActionAddCard(create_card_with_pixmap("Left", color=QColorConstants.Black)))
    document.apply(ActionAddCard(create_card_with_pixmap("Right", color=QColorConstants.Cyan)))

    size = CardSizes.REGULAR.as_qsize_px()
    right = QPoint(size.width() - 1, 0)
    down = QPoint(0, size.height() - 1)
    half_right, half_down = right / 2, down / 2
    h_1 = QPoint(1, 0)
    h_6 = QPoint(6, 0)
    h_7 = QPoint(7, 0)
    h_12 = QPoint(12, 0)
    h_13 = QPoint(13, 0)
    v_1 = QPoint(0, 1)
    v_12 = QPoint(0, 12)
    v_13 = QPoint(0, 13)

    top_left = page_scene.card_items[0].scenePos().toPoint()
    top_right = top_left + right
    bottom_left = top_left + down
    bottom_right = top_left + right + down

    top_center = top_left + half_right
    left_center = top_left + half_down
    right_center = top_right + half_down
    bottom_center = bottom_left + half_right

    rendered = render_scene(page_scene)
    has_left_color = is_(equal_to(QColorConstants.Black))
    has_right_color = is_(equal_to(QColorConstants.Cyan))
    background_color = QColorConstants.Transparent if page_scene.render_mode == RenderMode.ON_PAPER \
        else page_scene.palette().color(ColorGroup.Active, ColorRole.Base)
    has_background_color = is_(equal_to(background_color))

    # Left card
    
    # Top border
    # Inner bleed edge
    assert_that(rendered.pixelColor(top_left - v_1), has_left_color)
    assert_that(rendered.pixelColor(top_center - v_1), has_left_color)
    assert_that(rendered.pixelColor(top_right - v_1), has_left_color)
    # Outer bleed edge
    assert_that(rendered.pixelColor(top_left - v_12), has_left_color)
    assert_that(rendered.pixelColor(top_center - v_12), has_left_color)
    assert_that(rendered.pixelColor(top_right - v_12), has_left_color)
    # Outside bleed
    assert_that(rendered.pixelColor(top_left - v_13), has_background_color)
    assert_that(rendered.pixelColor(top_center - v_13), has_background_color)
    assert_that(rendered.pixelColor(top_right - v_13), has_background_color)

    # Bottom border
    # Inner bleed edge
    assert_that(rendered.pixelColor(bottom_left + v_1), has_left_color)
    assert_that(rendered.pixelColor(bottom_center + v_1), has_left_color)
    assert_that(rendered.pixelColor(bottom_right + v_1), has_left_color)
    # Outer bleed edge
    assert_that(rendered.pixelColor(bottom_left + v_12), has_left_color)
    assert_that(rendered.pixelColor(bottom_center + v_12), has_left_color)
    assert_that(rendered.pixelColor(bottom_right + v_12), has_left_color)
    # Outside bleed
    assert_that(rendered.pixelColor(bottom_left + v_13), has_background_color)
    assert_that(rendered.pixelColor(bottom_center + v_13), has_background_color)
    assert_that(rendered.pixelColor(bottom_right + v_13), has_background_color)

    # Left border
    # Inner bleed edge
    assert_that(rendered.pixelColor(top_left - h_1), has_left_color)
    assert_that(rendered.pixelColor(left_center - h_1), has_left_color)
    assert_that(rendered.pixelColor(bottom_left - h_1), has_left_color)
    # Outer bleed edge
    assert_that(rendered.pixelColor(top_left - h_12), has_left_color)
    assert_that(rendered.pixelColor(left_center - h_12), has_left_color)
    assert_that(rendered.pixelColor(bottom_left - h_12), has_left_color)
    # Outside bleed
    assert_that(rendered.pixelColor(top_left - h_13), has_background_color)
    assert_that(rendered.pixelColor(left_center - h_13), has_background_color)
    assert_that(rendered.pixelColor(bottom_left - h_13), has_background_color)

    # Right border
    if column_spacing:
        # Inner bleed edge
        assert_that(rendered.pixelColor(top_right + h_1), has_left_color)
        assert_that(rendered.pixelColor(right_center + h_1), has_left_color)
        assert_that(rendered.pixelColor(bottom_right + h_1), has_left_color)
        # Outer bleed edge
        assert_that(rendered.pixelColor(top_right + h_6), has_left_color)
        assert_that(rendered.pixelColor(right_center + h_6), has_left_color)
        assert_that(rendered.pixelColor(bottom_right + h_6), has_left_color)
        # Outside bleed
        assert_that(rendered.pixelColor(top_right + h_7), has_right_color)
        assert_that(rendered.pixelColor(right_center + h_7), has_right_color)
        assert_that(rendered.pixelColor(bottom_right + h_7), has_right_color)
    else:
        assert_that(rendered.pixelColor(top_right + h_1), has_right_color)
        assert_that(rendered.pixelColor(right_center + h_1), has_right_color)
        assert_that(rendered.pixelColor(bottom_right + h_1), has_right_color)

    # Right card
    
    top_left = page_scene.card_items[1].scenePos().toPoint()
    top_right = top_left + right
    bottom_left = top_left + down
    bottom_right = top_left + right + down

    top_center = top_left + half_right
    left_center = top_left + half_down
    right_center = top_right + half_down
    bottom_center = bottom_left + half_right

    # Top border
    # Inner bleed edge
    assert_that(rendered.pixelColor(top_left - v_1), has_right_color)
    assert_that(rendered.pixelColor(top_center - v_1), has_right_color)
    assert_that(rendered.pixelColor(top_right - v_1), has_right_color)
    # Outer bleed edge
    assert_that(rendered.pixelColor(top_left - v_12), has_right_color)
    assert_that(rendered.pixelColor(top_center - v_12), has_right_color)
    assert_that(rendered.pixelColor(top_right - v_12), has_right_color)
    # Outside bleed
    assert_that(rendered.pixelColor(top_left - v_13), has_background_color)
    assert_that(rendered.pixelColor(top_center - v_13), has_background_color)
    assert_that(rendered.pixelColor(top_right - v_13), has_background_color)

    # Bottom border
    # Inner bleed edge
    assert_that(rendered.pixelColor(bottom_left + v_1), has_right_color)
    assert_that(rendered.pixelColor(bottom_center + v_1), has_right_color)
    assert_that(rendered.pixelColor(bottom_right + v_1), has_right_color)
    # Outer bleed edge
    assert_that(rendered.pixelColor(bottom_left + v_12), has_right_color)
    assert_that(rendered.pixelColor(bottom_center + v_12), has_right_color)
    assert_that(rendered.pixelColor(bottom_right + v_12), has_right_color)
    # Outside bleed
    assert_that(rendered.pixelColor(bottom_left + v_13), has_background_color)
    assert_that(rendered.pixelColor(bottom_center + v_13), has_background_color)
    assert_that(rendered.pixelColor(bottom_right + v_13), has_background_color)

    # Left border
    if column_spacing:
        # Inner bleed edge
        assert_that(rendered.pixelColor(top_left - h_1), has_right_color)
        assert_that(rendered.pixelColor(left_center - h_1), has_right_color)
        assert_that(rendered.pixelColor(bottom_left - h_1), has_right_color)
        # Outer bleed edge
        assert_that(rendered.pixelColor(top_left - h_6), has_right_color)
        assert_that(rendered.pixelColor(left_center - h_6), has_right_color)
        assert_that(rendered.pixelColor(bottom_left - h_6), has_right_color)
        # Outside bleed
        assert_that(rendered.pixelColor(top_left - h_7-h_1), has_left_color)
        assert_that(rendered.pixelColor(left_center - h_7-h_1), has_left_color)
        assert_that(rendered.pixelColor(bottom_left - h_7-h_1), has_left_color)
    else:
        assert_that(rendered.pixelColor(top_left - h_1), has_left_color)
        assert_that(rendered.pixelColor(left_center - h_1), has_left_color)
        assert_that(rendered.pixelColor(bottom_left - h_1), has_left_color)

    # Right border
    # Inner bleed edge
    assert_that(rendered.pixelColor(top_right + h_1), has_right_color)
    assert_that(rendered.pixelColor(right_center + h_1), has_right_color)
    assert_that(rendered.pixelColor(bottom_right + h_1), has_right_color)
    # Outer bleed edge
    assert_that(rendered.pixelColor(top_right + h_12 - h_1), has_right_color)
    assert_that(rendered.pixelColor(right_center + h_12 - h_1), has_right_color)
    assert_that(rendered.pixelColor(bottom_right + h_12 - h_1), has_right_color)
    # Outside bleed
    assert_that(rendered.pixelColor(top_right + h_13), has_background_color)
    assert_that(rendered.pixelColor(right_center + h_13), has_background_color)
    assert_that(rendered.pixelColor(bottom_right + h_13), has_background_color)
