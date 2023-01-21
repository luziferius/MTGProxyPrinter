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

from unittest.mock import patch

from hamcrest import *
import pytest
from PyQt5.QtWidgets import QGraphicsPixmapItem

from mtg_proxy_printer.ui.page_renderer import RenderMode, PageScene, PageRenderer
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard

from ..document_controller.helpers import create_card

PATH_PREFIX = "mtg_proxy_printer.ui.page_renderer.PageScene."


@pytest.fixture(params=RenderMode)
def page_scene(request, qtbot, document_light):
    """Creates a PageScene in each available rendering mode"""
    yield PageScene(document_light, request.param)


@pytest.mark.parametrize("count", [1, 2, 10])
@pytest.mark.parametrize("oversized", [True, False])
def test_adding_with_card_to_filled_page_does_not_redraw_page(qtbot, page_scene: PageScene, oversized: bool, count: int):
    card = create_card("Card", oversized)
    document = page_scene.document
    card.image_file = page_scene.document.image_db.blank_image
    with qtbot.wait_signal(document.action_applied):
        document.apply(ActionAddCard(card))
    with patch(PATH_PREFIX+"redraw") as redraw_mock, patch(PATH_PREFIX+"_draw_cut_markers") as cut_markes_mock,\
            qtbot.wait_signals([document.action_applied, document.rowsInserted]):
        document.apply(ActionAddCard(card, count))
    redraw_mock.assert_not_called()
    cut_markes_mock.assert_not_called()
    assert_that(
        page_scene.items(),
        has_items(*[instance_of(QGraphicsPixmapItem)]*len(document.currently_edited_page))
    )



