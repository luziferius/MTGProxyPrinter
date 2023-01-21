# Copyright (C) 2023 Thomas Hess <thomas.hess@udo.edu>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import typing
from unittest.mock import patch

from hamcrest import *
import pytest
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsLineItem

from mtg_proxy_printer.ui.page_renderer import RenderMode, PageScene
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard

from ..document_controller.helpers import create_card
from tests.hasgetter import has_getter, has_getters

PATH_PREFIX = "mtg_proxy_printer.ui.page_renderer.PageScene."


def create_card_with_pixmap(name: str, oversized: bool, document):
    card = create_card(name, oversized)
    card.image_file = document.image_db.blank_image
    if oversized:
        card.image_file = card.image_file.scaled(1040, 1490)
    return card


@pytest.fixture(params=RenderMode)
def page_scene(request, qtbot, document_light):
    """Creates a PageScene in each available rendering mode"""
    yield PageScene(document_light, request.param)


@pytest.mark.parametrize("count", [1, 2, 10])
@pytest.mark.parametrize("oversized", [True, False])
def test_adding_with_card_to_filled_page_does_not_redraw_page(
        qtbot, page_scene: PageScene, oversized: bool, count: int):
    document = page_scene.document
    with qtbot.wait_signal(document.action_applied):
        document.apply(ActionAddCard(create_card_with_pixmap("Card", oversized, document)))
    with patch(PATH_PREFIX+"redraw") as redraw_mock, patch(PATH_PREFIX+"_draw_cut_markers") as cut_markes_mock,\
            qtbot.wait_signals([document.action_applied, document.rowsInserted]):
        document.apply(ActionAddCard(create_card_with_pixmap("Card", oversized, document), count))
    redraw_mock.assert_not_called()
    cut_markes_mock.assert_not_called()
    assert_that(
        page_scene.items(),
        has_items(*[instance_of(QGraphicsPixmapItem)]*len(document.currently_edited_page))
    )


def test_cut_lines_not_drawn_when_disabled_and_page_empty(qtbot, page_scene: PageScene):
    document = page_scene.document
    document.page_layout.draw_cut_markers = False
    document.page_layout_changed.emit(document.page_layout)
    assert_that(
        page_scene.items(), not_(has_items(instance_of(QGraphicsLineItem)))
    )


@pytest.mark.parametrize("oversized", [True, False])
def test_cut_lines_not_drawn_when_disabled_and_page_filled(qtbot, page_scene: PageScene, oversized: bool):
    document = page_scene.document
    document.page_layout.draw_cut_markers = False
    document.page_layout_changed.emit(document.page_layout)
    with qtbot.wait_signal(document.action_applied):
        document.apply(ActionAddCard(create_card_with_pixmap("Card", oversized, document)))
    assert_that(
        page_scene.items(), not_(has_items(instance_of(QGraphicsLineItem)))
    )


@pytest.mark.parametrize("oversized, horizontal_spacing, vertical_spacing, expected_verticals, expected_horizontals", [
    (False, 0, 0, [82.18, 826.77, 1571.37, 2315.96], [117.61, 1157.48, 2197.35, 3237.22]),
    (True, 0, 0, [82.18, 1122.05, 2161.92], [117.61, 1606.3, 3094.99]),
])
def test_cut_line_locations_when_enabled(
        qtbot, page_scene: PageScene,
        oversized: bool, horizontal_spacing: int, vertical_spacing: int,
        expected_verticals: typing.List[float], expected_horizontals: typing.List[float]):
    document = page_scene.document
    document.page_layout.image_spacing_horizontal = horizontal_spacing
    document.page_layout.image_spacing_vertical = vertical_spacing
    document.page_layout.draw_cut_markers = True
    document.page_layout_changed.emit(document.page_layout)
    with qtbot.wait_signals([document.action_applied, document.page_type_changed]):
        document.apply(ActionAddCard(create_card_with_pixmap("Card", oversized, document)))

    assert_that(page_scene.cut_lines, only_contains(instance_of(QGraphicsLineItem)))
    line_items = [item for item in page_scene.items() if isinstance(item, QGraphicsLineItem)]
    assert_that(page_scene.cut_lines, contains_inanyorder(*line_items))
    assert_that(line_items, has_length(len(expected_horizontals)+len(expected_verticals)))
    page_width, page_height = page_scene.width(), page_scene.height()

    d = 0.005
    bounding_boxes = [item.boundingRect() for item in line_items]
    matcher = [
        has_getters(
            # Horizontal lines, have meaningful Y coordinates (top) and width equal to page width + 1
            left=close_to(-0.5, d), top=close_to(x, d),
            width=close_to(page_width+1, d), height=close_to(1, d)
        ) for x in expected_horizontals
    ] + [
        has_getters(
            # Vertical lines, have meaningful X coordinates (left) and height equal to page height + 1
            left=close_to(y, d), top=close_to(-0.5, d),
            width=close_to(1, d), height=close_to(page_height+1, d)
        ) for y in expected_verticals]
    assert_that(
        bounding_boxes,
        contains_inanyorder(*matcher)
    )



