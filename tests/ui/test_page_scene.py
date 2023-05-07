# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>

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
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsLineItem

from mtg_proxy_printer.settings import DuplexMode
from mtg_proxy_printer.units_and_sizes import PageType
from mtg_proxy_printer.ui.page_renderer import RenderMode, PageScene
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage
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


@pytest.fixture(params=RenderMode)
def page_scene(request, qtbot, document_light):
    """Creates a PageScene in each available rendering mode"""
    ActionNewPage().apply(document_light)
    yield PageScene(document_light, request.param)


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


class CutLineLocationTestData(typing.NamedTuple):
    page_index: int
    duplex_mode: DuplexMode
    page_type: PageType
    h_spacing: int
    v_spacing: int
    expected_verticals: typing.List[int]
    expected_horizontals: typing.List[int]


def generate_test_cases_for_test_cut_line_locations_when_enabled() \
        -> typing.Generator[CutLineLocationTestData, None, None]:
    # Default A4 Page size in pixels: width=2480, height=3508

    def arange(offset: int, size: int, count: int):
        return [offset+size*item for item in range(count+1)]

    # Odd page (0, the first page), same values regardless of duplex mode
    yield CutLineLocationTestData(0, DuplexMode.OFF, PageType.UNDETERMINED, 0, 0, arange(83, 745, 3), arange(118, 1040, 3))
    yield CutLineLocationTestData(0, DuplexMode.OFF, PageType.REGULAR, 0, 0, arange(83, 745, 3), arange(118, 1040, 3))
    yield CutLineLocationTestData(0, DuplexMode.OFF, PageType.OVERSIZED, 0, 0, arange(83, 1040, 2), arange(118, 1490, 2))
    yield CutLineLocationTestData(0, DuplexMode.OFF, PageType.UNDETERMINED, 1, 1, [83, 828, 840, 1585, 1597, 2342], [118, 1158, 1170, 2210, 2222, 3262])
    yield CutLineLocationTestData(0, DuplexMode.OFF, PageType.REGULAR, 1, 1, [83, 828, 840, 1585, 1597, 2342], [118, 1158, 1170, 2210, 2222, 3262])
    yield CutLineLocationTestData(0, DuplexMode.OFF, PageType.OVERSIZED, 1, 1, [83, 1123, 1135, 2175], [118, 1608, 1620, 3110])

    yield CutLineLocationTestData(0, DuplexMode.DFC_ONLY, PageType.UNDETERMINED, 0, 0, arange(83, 745, 3), arange(118, 1040, 3))
    yield CutLineLocationTestData(0, DuplexMode.DFC_ONLY, PageType.REGULAR, 0, 0, arange(83, 745, 3), arange(118, 1040, 3))
    yield CutLineLocationTestData(0, DuplexMode.DFC_ONLY, PageType.OVERSIZED, 0, 0, arange(83, 1040, 2), arange(118, 1490, 2))
    yield CutLineLocationTestData(0, DuplexMode.DFC_ONLY, PageType.UNDETERMINED, 1, 1, [83, 828, 840, 1585, 1597, 2342], [118, 1158, 1170, 2210, 2222, 3262])
    yield CutLineLocationTestData(0, DuplexMode.DFC_ONLY, PageType.REGULAR, 1, 1, [83, 828, 840, 1585, 1597, 2342], [118, 1158, 1170, 2210, 2222, 3262])
    yield CutLineLocationTestData(0, DuplexMode.DFC_ONLY, PageType.OVERSIZED, 1, 1, [83, 1123, 1135, 2175], [118, 1608, 1620, 3110])

    yield CutLineLocationTestData(0, DuplexMode.FULL, PageType.UNDETERMINED, 0, 0, arange(83, 745, 3), arange(118, 1040, 3))
    yield CutLineLocationTestData(0, DuplexMode.FULL, PageType.REGULAR, 0, 0, arange(83, 745, 3), arange(118, 1040, 3))
    yield CutLineLocationTestData(0, DuplexMode.FULL, PageType.OVERSIZED, 0, 0, arange(83, 1040, 2), arange(118, 1490, 2))
    yield CutLineLocationTestData(0, DuplexMode.FULL, PageType.UNDETERMINED, 1, 1, [83, 828, 840, 1585, 1597, 2342], [118, 1158, 1170, 2210, 2222, 3262])
    yield CutLineLocationTestData(0, DuplexMode.FULL, PageType.REGULAR, 1, 1, [83, 828, 840, 1585, 1597, 2342], [118, 1158, 1170, 2210, 2222, 3262])
    yield CutLineLocationTestData(0, DuplexMode.FULL, PageType.OVERSIZED, 1, 1, [83, 1123, 1135, 2175], [118, 1608, 1620, 3110])
    
    # Even page (0, second page). Duplex mode other than OFF mirrors the page layout
    yield CutLineLocationTestData(1, DuplexMode.OFF, PageType.UNDETERMINED, 0, 0, arange(83, 745, 3), arange(118, 1040, 3))
    yield CutLineLocationTestData(1, DuplexMode.OFF, PageType.REGULAR, 0, 0, arange(83, 745, 3), arange(118, 1040, 3))
    yield CutLineLocationTestData(1, DuplexMode.OFF, PageType.OVERSIZED, 0, 0, arange(83, 1040, 2), arange(118, 1490, 2))
    yield CutLineLocationTestData(1, DuplexMode.OFF, PageType.UNDETERMINED, 1, 1, [83, 828, 840, 1585, 1597, 2342], [118, 1158, 1170, 2210, 2222, 3262])
    yield CutLineLocationTestData(1, DuplexMode.OFF, PageType.REGULAR, 1, 1, [83, 828, 840, 1585, 1597, 2342], [118, 1158, 1170, 2210, 2222, 3262])
    yield CutLineLocationTestData(1, DuplexMode.OFF, PageType.OVERSIZED, 1, 1, [83, 1123, 1135, 2175], [118, 1608, 1620, 3110])

    yield CutLineLocationTestData(1, DuplexMode.DFC_ONLY, PageType.UNDETERMINED, 0, 0, [162, 907, 1652, 2397], arange(118, 1040, 3))
    yield CutLineLocationTestData(1, DuplexMode.DFC_ONLY, PageType.REGULAR, 0, 0, [162, 907, 1652, 2397], arange(118, 1040, 3))
    yield CutLineLocationTestData(1, DuplexMode.DFC_ONLY, PageType.OVERSIZED, 0, 0, [317, 1357, 2397], arange(118, 1490, 2))
    yield CutLineLocationTestData(1, DuplexMode.DFC_ONLY, PageType.UNDETERMINED, 1, 1, [138, 883, 895, 1640, 1652, 2397], [118, 1158, 1170, 2210, 2222, 3262])
    yield CutLineLocationTestData(1, DuplexMode.DFC_ONLY, PageType.REGULAR, 1, 1, [138, 883, 895, 1640, 1652, 2397], [118, 1158, 1170, 2210, 2222, 3262])
    yield CutLineLocationTestData(1, DuplexMode.DFC_ONLY, PageType.OVERSIZED, 1, 1, [305, 1345, 1357, 2397], [118, 1608, 1620, 3110])

    yield CutLineLocationTestData(1, DuplexMode.DFC_ONLY, PageType.UNDETERMINED, 0, 0, [162, 907, 1652, 2397], arange(118, 1040, 3))
    yield CutLineLocationTestData(1, DuplexMode.DFC_ONLY, PageType.REGULAR, 0, 0, [162, 907, 1652, 2397], arange(118, 1040, 3))
    yield CutLineLocationTestData(1, DuplexMode.DFC_ONLY, PageType.OVERSIZED, 0, 0, [317, 1357, 2397], arange(118, 1490, 2))
    yield CutLineLocationTestData(1, DuplexMode.DFC_ONLY, PageType.UNDETERMINED, 1, 1, [138, 883, 895, 1640, 1652, 2397], [118, 1158, 1170, 2210, 2222, 3262])
    yield CutLineLocationTestData(1, DuplexMode.DFC_ONLY, PageType.REGULAR, 1, 1, [138, 883, 895, 1640, 1652, 2397], [118, 1158, 1170, 2210, 2222, 3262])
    yield CutLineLocationTestData(1, DuplexMode.DFC_ONLY, PageType.OVERSIZED, 1, 1, [305, 1345, 1357, 2397], [118, 1608, 1620, 3110])


@pytest.mark.parametrize("data", generate_test_cases_for_test_cut_line_locations_when_enabled())
def test_cut_line_locations_when_enabled(qtbot, page_scene: PageScene, data: CutLineLocationTestData):

    document = page_scene.document
    document.set_currently_edited_page(document.pages[data.page_index])
    document.page_layout.duplex_mode = data.duplex_mode
    document.page_layout_changed.emit(document.page_layout)
    document.page_layout.image_spacing_horizontal = data.h_spacing
    document.page_layout.image_spacing_vertical = data.v_spacing
    document.page_layout.draw_cut_markers = True
    document.page_layout_changed.emit(document.page_layout)
    if data.page_type is not PageType.UNDETERMINED:
        with qtbot.wait_signals([document.action_applied, document.page_type_changed]):
            document.apply(ActionAddCard(create_card_with_pixmap("Card", data.page_type is PageType.OVERSIZED, document)))

    assert_that(
        page_scene.cut_lines,
        has_length(len(data.expected_horizontals)+len(data.expected_verticals)),
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
        page_scene.vertical_cut_line_locations[page_scene.duplex_type][data.page_type],
        contains_inanyorder(
            *map(close_to_, data.expected_verticals))
    )
    assert_that(
        page_scene.horizontal_cut_line_locations[data.page_type],
        contains_inanyorder(*map(close_to_, data.expected_horizontals))
    )
    assert_that(
        page_scene.cut_lines,
        contains_inanyorder(
            *[has_getters(
                x=close_to_(x), y=0,
                boundingRect=has_getters(
                    width=1, height=close_to_(page_height+1))
            ) for x in data.expected_verticals],
            *[has_getters(
                x=0, y=close_to_(y),
                boundingRect=has_getters(
                    width=close_to_(page_width+1), height=1)
            ) for y in data.expected_horizontals]
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
