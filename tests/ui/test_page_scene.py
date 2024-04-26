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


import itertools
from functools import partial
import typing
from unittest.mock import patch

from hamcrest import *
import pytest
from pytestqt.qtbot import QtBot
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsLineItem
from PyQt5.QtGui import QPalette, QColorConstants, QPixmap

from mtg_proxy_printer.units_and_sizes import PageType, CardSizes
from mtg_proxy_printer.ui.page_scene import RenderMode, PageScene
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard, ActionRemoveCards
from mtg_proxy_printer.document_controller.compact_document import ActionCompactDocument
from mtg_proxy_printer.model.document import Document

from ..document_controller.helpers import create_card
from tests.hasgetter import has_getters, has_getter

PATH_PREFIX = "mtg_proxy_printer.ui.page_renderer.PageScene."
close_to_ = partial(close_to, delta=0.005)


def create_card_with_pixmap(name: str, oversized: bool, *, color = QColorConstants.Transparent):
    card = create_card(name, oversized)
    size = (CardSizes.OVERSIZED if oversized else CardSizes.REGULAR).as_qsize_px()
    card.image_file = image = QPixmap(size)
    image.fill(color)
    return card

@pytest.fixture(params=itertools.product(
    [RenderMode.ON_PAPER, RenderMode.ON_SCREEN],
    [True, False]))
def page_scene(request, qtbot: QtBot, document_light: Document):
    """Creates a PageScene in each available rendering mode"""
    render_mode, enable_text_items = request.param  # type: RenderMode, bool
    with patch.object(document_light.page_layout, "draw_page_numbers", enable_text_items), \
         patch.object(document_light.page_layout, "document_name", "Non-empty title" if enable_text_items else ""):
        scene = PageScene(document_light, render_mode)
        yield scene


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
@pytest.mark.parametrize("oversized", [True, False])
def test_adding_with_card_to_filled_page_does_not_redraw_page(
        qtbot: QtBot, page_scene: PageScene, oversized: bool, count: int):
    document = page_scene.document
    with qtbot.wait_signal(document.action_applied):
        document.apply(ActionAddCard(create_card_with_pixmap("Card", oversized)))
    with patch(PATH_PREFIX+"draw_cut_markers") as cut_markes_mock, \
            qtbot.wait_signals([document.action_applied, document.rowsInserted]):
        document.apply(ActionAddCard(create_card_with_pixmap("Card", oversized), count))
    cut_markes_mock.assert_not_called()
    assert_that(
        page_scene.items(),
        has_items(*[instance_of(QGraphicsPixmapItem)]*len(document.currently_edited_page))
    )


def test_cut_lines_not_drawn_when_disabled_and_page_empty(qtbot: QtBot, page_scene: PageScene):
    document = page_scene.document
    document.page_layout.draw_cut_markers = False
    document.page_layout_changed.emit(document.page_layout)
    assert_that(
        page_scene.items(), not_(has_items(instance_of(QGraphicsLineItem)))
    )
    assert_that(page_scene.cut_lines, is_(empty()))


@pytest.mark.parametrize("oversized", [True, False])
def test_cut_lines_not_drawn_when_disabled_and_page_filled(qtbot: QtBot, page_scene: PageScene, oversized: bool):
    document = page_scene.document
    document.page_layout.draw_cut_markers = False
    document.page_layout_changed.emit(document.page_layout)
    with qtbot.wait_signal(document.action_applied):
        document.apply(ActionAddCard(create_card_with_pixmap("Card", oversized)))
    assert_that(
        page_scene.items(), not_(has_items(instance_of(QGraphicsLineItem)))
    )


@pytest.mark.parametrize("row_spacing, column_spacing", itertools.product([0, 1], repeat=2))
def test_cut_lines_property_only_lists_line_elements(
        qtbot: QtBot, page_scene: PageScene, row_spacing: int, column_spacing: int):
    layout = page_scene.document.page_layout
    layout.row_spacing = row_spacing
    layout.column_spacing = column_spacing
    layout.draw_cut_markers = True
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


@pytest.mark.parametrize("row_spacing", [0, 1])
@pytest.mark.parametrize("column_spacing", [0, 1])
def test_cut_lines_bounding_rects_cross_entire_page(
        qtbot: QtBot, page_scene: PageScene, row_spacing: int, column_spacing: int):
    layout = page_scene.document.page_layout
    layout.row_spacing = row_spacing
    layout.column_spacing = column_spacing
    layout.draw_cut_markers = True
    page_scene.document.page_layout_changed.emit(layout)
    page_width, page_height = page_scene.width(), page_scene.height()
    assert_that(
        page_scene.cut_lines,
        only_contains(
            has_getter("boundingRect", has_getters(width=1, height=close_to_(page_height+1))),
            has_getter("boundingRect", has_getters(width=close_to_(page_width+1), height=1)),
        ),
        "Unexpected cut line bounding boxes"
    )


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
        qtbot: QtBot, page_scene: PageScene,
        page_type: PageType, spacing: int, margins: int, flags: RenderMode, expected_y: typing.List):
    page_scene.render_mode |= flags
    document = page_scene.document
    document.page_layout.margin_top = margins
    document.page_layout.margin_bottom = 0
    document.page_layout.row_spacing = spacing
    document.page_layout.draw_cut_markers = True
    document.page_layout_changed.emit(document.page_layout)
    assert_that(
        document.page_layout.compute_page_card_capacity(page_type), is_in((4, 9)),
        "Test setup failed! Margins caused unexpected capacity decrease"
    )
    if page_type is not PageType.UNDETERMINED:
        with qtbot.wait_signals([document.action_applied, document.page_type_changed]):
            document.apply(
                ActionAddCard(create_card_with_pixmap("Card", page_type is PageType.OVERSIZED)))

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
        qtbot: QtBot, page_scene: PageScene,
        page_type: PageType, spacing: int, margins: int, flags: RenderMode, expected_x: typing.List[float]):
    page_scene.render_mode |= flags
    document = page_scene.document
    document.page_layout.margin_left = margins
    document.page_layout.margin_right = 0
    document.page_layout.column_spacing = spacing
    document.page_layout.draw_cut_markers = True
    document.page_layout_changed.emit(document.page_layout)
    assert_that(
        document.page_layout.compute_page_card_capacity(page_type), is_in((4, 9)),
        "Test setup failed! Margins caused unexpected capacity decrease"
    )
    if page_type is not PageType.UNDETERMINED:
        with qtbot.wait_signals([document.action_applied, document.page_type_changed]):
            document.apply(
                ActionAddCard(create_card_with_pixmap("Card", page_type is PageType.OVERSIZED)))

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
        qtbot: QtBot, page_scene: PageScene,
        page_type: PageType, spacing: int, margin: int, flags: RenderMode, expected_x: typing.List[int]):
    page_scene.render_mode |= flags
    document = page_scene.document
    document.page_layout.column_spacing = spacing
    document.page_layout.margin_left = margin
    document.page_layout.margin_right = 0
    document.page_layout_changed.emit(document.page_layout)
    page_capacity = document.page_layout.compute_page_card_capacity(page_type)
    row_count = document.page_layout.compute_page_row_count(page_type)
    card = create_card_with_pixmap("Something", page_type == PageType.OVERSIZED)
    ActionAddCard(card, 1).apply(document)
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
        qtbot: QtBot, page_scene: PageScene,
        page_type: PageType, spacing: int, margin: int, flags: RenderMode, expected_y: typing.List[int]):
    page_scene.render_mode |= flags
    document = page_scene.document
    document.page_layout.row_spacing = spacing
    document.page_layout.margin_top = margin
    document.page_layout.margin_bottom = 0
    document.page_layout_changed.emit(document.page_layout)
    page_capacity = document.page_layout.compute_page_card_capacity(page_type)
    column_count = document.page_layout.compute_page_column_count(page_type)
    card = create_card_with_pixmap("Something", page_type == PageType.OVERSIZED)
    ActionAddCard(card, 1).apply(document)
    y_coordinates = [page_scene._compute_position_for_image(index, page_type).y() for index in range(page_capacity)]
    assert_that(
        y_coordinates, contains_exactly(*elementwise_repeat([close_to_(y) for y in expected_y], column_count)),
        f"Unexpected values: {y_coordinates}"
    )


@pytest.mark.parametrize("removed_range", [range(1), range(2), range(1, 3), range(9)])
def test_compacting_document_moves_cards_onto_currently_shown_page(
        qtbot: QtBot, page_scene: PageScene, removed_range: range):
    # Test for issue [b33546aa1cbd62f3e1e7852bfc89a206fed89501]. PageScene crashes when compacting a document
    # moves cards onto the currently shown page.

    # Setup
    document = page_scene.document
    page_capacity = document.page_layout.compute_page_card_capacity(PageType.REGULAR)
    card = create_card_with_pixmap("Something", False)
    ActionAddCard(card, page_capacity*2).apply(document)
    ActionRemoveCards(removed_range, 0).apply(document)
    # Verify no IndexError is raised when handling signals during:
    ActionCompactDocument().apply(document)

    assert_that(
        page_scene.card_items,
        has_length(page_capacity)
    )


def test_setPalette_runs_without_exception(qtbot: QtBot, page_scene: PageScene):
    palette = QPalette()
    page_scene.setPalette(palette)
