#  Copyright © 2020-2025.  Thomas Hess <thomas.hess@udo.edu>
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


from unittest.mock import patch

import pytest
from hamcrest import *
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QAction

from mtg_proxy_printer.ui.page_renderer import PageRenderer, ZoomDirection

PATH_PREFIX = "mtg_proxy_printer.ui.page_renderer."


@pytest.fixture
def renderer(qtbot, document_light):
    """
    Creates a PageRenderer.
    Note: qtbot fixture parameter is required for the implicitly provided event loop. Qt segfaults without it present
    """
    with patch(PATH_PREFIX+"PageRenderer._perform_zoom_step"):
        page_renderer = PageRenderer()
        page_renderer.set_document(document_light)
        yield page_renderer


@pytest.fixture(params=[QEvent.ApplicationPaletteChange, QEvent.PaletteChange])
def palette_change_event(request):
    yield QEvent(request.param)


def test_renderer_redraws_scene_on_palette_change(renderer: PageRenderer, palette_change_event: QEvent):
    with patch(PATH_PREFIX+"PageScene.setPalette") as set_palette_mock:
        renderer.changeEvent(palette_change_event)
    set_palette_mock.assert_called_once_with(renderer.palette())
    assert_that(palette_change_event.isAccepted())


@pytest.mark.parametrize("zoom_action, direction", [
    ("zoom_in_action", ZoomDirection.IN), ("zoom_out_action", ZoomDirection.OUT)])
def test_renderer_zoom_action_triggers_zoom(renderer: PageRenderer, zoom_action: str, direction: ZoomDirection):
    action: QAction = getattr(renderer, zoom_action)
    action.trigger()
    renderer._perform_zoom_step.assert_called_once_with(direction, False)
