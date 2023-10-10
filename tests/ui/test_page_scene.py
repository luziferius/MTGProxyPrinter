# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>
import itertools
import unittest.mock
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

from functools import partial
import typing
from unittest.mock import patch

from hamcrest import *
import pytest
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsLineItem

from mtg_proxy_printer.units_and_sizes import PageType
from mtg_proxy_printer.ui.page_renderer import RenderMode, PageScene
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard, ActionRemoveCards
from mtg_proxy_printer.document_controller.compact_document import ActionCompactDocument

from ..document_controller.helpers import create_card
from tests.hasgetter import has_getters

PATH_PREFIX = "mtg_proxy_printer.ui.page_renderer.PageScene."


def create_card_with_pixmap(name: str, oversized: bool, document):
    card = create_card(name, oversized)
    card.image_file = document.image_db.blank_image
    if oversized:
        card.image_file = card.image_file.scaled(1040, 1490)
    return card


@pytest.fixture(params=itertools.product(RenderMode, [True, False]))
def page_scene(request, qtbot, document_light):
    """Creates a PageScene in each available rendering mode"""
    render_mode, enable_text_items = request.param
    with patch.object(document_light.page_layout, "draw_page_numbers", enable_text_items), \
         patch.object(document_light.page_layout, "document_name", "Non-empty title" if enable_text_items else ""):
        scene = PageScene(document_light, render_mode)
        yield scene


@pytest.mark.parametrize("render_mode", RenderMode)
def test___init__does_not_add_text_items_if_disabled(document_light, render_mode: RenderMode):
    with patch.object(document_light.page_layout, "draw_page_numbers", False), \
         patch.object(document_light.page_layout, "document_name", ""):
        scene = PageScene(document_light, render_mode)
    assert_that(scene.text_items, is_(empty()))


@pytest.mark.parametrize("render_mode", RenderMode)
def test___init__adds_text_items_if_enabled(document_light, render_mode: RenderMode):
    with patch.object(document_light.page_layout, "draw_page_numbers", True), \
         patch.object(document_light.page_layout, "document_name", "Non-empty title"):
        scene = PageScene(document_light, render_mode)
    assert_that(scene.text_items, has_length(2))


@pytest.mark.parametrize("count", [1, 2, 10])
@pytest.mark.parametrize("oversized", [True, False])
def test_adding_with_card_to_filled_page_does_not_redraw_page(
        qtbot, page_scene: PageScene, oversized: bool, count: int):
    document = page_scene.document
    with qtbot.wait_signal(document.action_applied):
        document.apply(ActionAddCard(create_card_with_pixmap("Card", oversized, document)))
    with patch(PATH_PREFIX+"draw_cut_markers") as cut_markes_mock,\
            qtbot.wait_signals([document.action_applied, document.rowsInserted]):
        document.apply(ActionAddCard(create_card_with_pixmap("Card", oversized, document), count))
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


@pytest.mark.parametrize("page_type, horizontal_spacing, vertical_spacing, expected_verticals, expected_horizontals", [
    (PageType.UNDETERMINED, 0, 0, [83, 828, 1573, 2318], [118, 1158, 2198, 3238]),
    (PageType.REGULAR, 0, 0, [83, 828, 1573, 2318], [118, 1158, 2198, 3238]),
    (PageType.OVERSIZED, 0, 0, [83, 1123, 2163], [118, 1608, 3098]),

    (PageType.UNDETERMINED, 1, 1, [83, 828, 840, 1585, 1597, 2342], [118, 1158, 1170, 2210, 2222, 3262]),
    (PageType.REGULAR, 1, 1, [83, 828, 840, 1585, 1597, 2342], [118, 1158, 1170, 2210, 2222, 3262]),
    (PageType.OVERSIZED, 1, 1, [83, 1123, 1135, 2175], [118, 1608, 1620, 3110]),
])
def test_cut_line_locations_when_enabled(
        qtbot, page_scene: PageScene,
        page_type: PageType, horizontal_spacing: int, vertical_spacing: int,
        expected_verticals: typing.List[float], expected_horizontals: typing.List[float]):
    document = page_scene.document
    document.page_layout.image_spacing_horizontal = horizontal_spacing
    document.page_layout.image_spacing_vertical = vertical_spacing
    document.page_layout.draw_cut_markers = True
    document.page_layout_changed.emit(document.page_layout)
    if page_type is not PageType.UNDETERMINED:
        with qtbot.wait_signals([document.action_applied, document.page_type_changed]):
            document.apply(ActionAddCard(create_card_with_pixmap("Card", page_type is PageType.OVERSIZED, document)))

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

    close_to_ = partial(close_to, delta=0.005)
    assert_that(
        page_scene.vertical_cut_line_locations[page_type],
        contains_inanyorder(
            *map(close_to_, expected_verticals))
    )
    assert_that(
        page_scene.horizontal_cut_line_locations[page_type],
        contains_inanyorder(*map(close_to_, expected_horizontals))
    )
    assert_that(
        page_scene.cut_lines,
        contains_inanyorder(
            *[has_getters(
                x=close_to_(x), y=0,
                boundingRect=has_getters(
                    width=1, height=close_to_(page_height+1))
            ) for x in expected_verticals],
            *[has_getters(
                x=0, y=close_to_(y),
                boundingRect=has_getters(
                    width=close_to_(page_width+1), height=1)
            ) for y in expected_horizontals]
        )
    )


@pytest.mark.parametrize("removed_range", [range(1), range(2), range(1, 3), range(9)])
def test_compacting_document_moves_cards_onto_currently_shown_page(qtbot, page_scene, removed_range: range):
    # Test for issue [b33546aa1cbd62f3e1e7852bfc89a206fed89501]. PageScene crashes when compacting a document
    # moves cards onto the currently shown page.

    # Setup
    document = page_scene.document
    page_capacity = document.page_layout.compute_page_card_capacity(PageType.REGULAR)
    card = create_card_with_pixmap("Something", False, document)
    ActionAddCard(card, page_capacity*2).apply(document)
    ActionRemoveCards(removed_range, 0).apply(document)
    # Verify no IndexError is raised when handling signals during:
    ActionCompactDocument().apply(document)

    assert_that(
        page_scene.card_items,
        has_length(page_capacity)
    )


def test_setPalette_runs_without_exception(qtbot, page_scene):
    palette = QPalette()
    page_scene.setPalette(palette)

