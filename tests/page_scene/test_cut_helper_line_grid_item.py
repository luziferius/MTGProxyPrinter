#  Copyright © 2020-2026  Thomas Hess <thomas.hess@udo.edu>
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

from hamcrest import *
import pytest

from mtg_proxy_printer.document_controller.page_actions import ActionNewPage
from mtg_proxy_printer.units_and_sizes import CardSizes
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.page_scene.items import CutHelperLineGridItem

from tests.helpers import close_to_, create_card_with_pixmap


@pytest.fixture()
def document_with_pages(document_light: Document) -> Document:
    document_light.apply(
        ActionNewPage(content=[[create_card_with_pixmap("Oversized", CardSizes.OVERSIZED)]])
    )
    document_light.page_layout.cut_marker_style = "Solid"
    return document_light


@pytest.mark.parametrize("cut_marker_style, grid_size, new_page, expected_opacity", [
    ("None", CardSizes.OVERSIZED, 0, 0.0),
    ("None", CardSizes.OVERSIZED, 1, 0.0),
    ("None", CardSizes.REGULAR, 0, 0.0),
    ("None", CardSizes.REGULAR, 1, 0.0),
    ("Solid", CardSizes.OVERSIZED, 0, 0.0),
    ("Solid", CardSizes.OVERSIZED, 1, 1.0),
    ("Solid", CardSizes.REGULAR, 0, 1.0),
    ("Solid", CardSizes.REGULAR, 1, 0.0),
])
def test_on_current_page_changed(
        document_with_pages: Document,
        cut_marker_style: str, grid_size: CardSizes, new_page: int, expected_opacity: float):
    grid = CutHelperLineGridItem(document_with_pages, grid_size)
    document_with_pages.page_layout.cut_marker_style = cut_marker_style
    document_with_pages.page_layout_changed.emit(document_with_pages.page_layout, {"cut_marker_style"})
    document_with_pages.set_currently_edited_page(document_with_pages.pages[new_page])
    assert_that(grid.opacity(), is_(close_to_(expected_opacity)))
