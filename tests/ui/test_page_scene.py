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

from mtg_proxy_printer.units_and_sizes import PageType, CardSizes
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
    (False, 0, 0, [82.68, 827.27, 1571.87, 2316.46], [118.11, 1157.98, 2197.85, 3237.72]),
    (True, 0, 0, [82.68, 1122.55, 2162.42], [118.11, 1606.8, 3095.49]),
    (False, 1, 1, [82.68, 827.77, 839.08, 1584.18, 1595.49, 2340.58], [118.11, 1157.98, 1169.79, 2209.66, 2221.47, 3261.34]),
    (True, 1, 1, [82.68, 1123.05, 1134.36, 2174.73], [118.11, 1606.8, 1618.61, 3107.3]),
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

    assert_that(
        page_scene.cut_lines,
        has_length(len(expected_horizontals)+len(expected_verticals)),
        "Unexpected line count"
    )
    assert_that(
        page_scene.cut_lines,
        only_contains(instance_of(QGraphicsLineItem)),
        "cut_lines must only contain QGraphicsLineItem instances"
    )
    assert_that(
        page_scene.cut_lines,
        only_contains(*page_scene.items()),
        "cut_lines mut not contain lines not present in the PageScene"
    )

    page_width, page_height = page_scene.width(), page_scene.height()
    d = 0.005
    assert_that(
        page_scene.cut_lines,
        contains_inanyorder(
            *[has_getters(
                x=close_to(x, d), y=0,
                boundingRect=has_getters(
                    width=1, height=close_to(page_height+1, d))
            ) for x in expected_verticals],
            *[has_getters(
                x=0, y=close_to(y, d),
                boundingRect=has_getters(
                    width=close_to(page_width+1, d), height=1)
            ) for y in expected_horizontals]
        )
    )
