# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>
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

from hamcrest import *
import pytest
from PySide6.QtCore import QSize
from PySide6.QtGui import QColorConstants, QPixmap, QImage, QPainter, QColor
from PySide6.QtWidgets import QGraphicsItem, QGraphicsScene

from mtg_proxy_printer.ui.page_scene import CardItem

from tests.document_controller.helpers import append_new_card_in_page
from tests.hasgetter import has_getter


def test_pixmap_set_in_init(qtbot, document_light):
    card = append_new_card_in_page(document_light.pages[0], "Card")
    card.set_image_file(document_light.image_db.blank_image)
    card_item = CardItem(card, document_light)

    # Cannot compare QPixmap, have to convert both to QImage, which has operator eq (==) defined
    assert_that(
        card_item.card_pixmap_item,
        has_getter(
            "pixmap", has_getter(
                "toImage", equal_to(
                    card.image_file.toImage())))
    )


def create_pixmap_with_transparent_corners(size: QSize) -> QPixmap:
    image = QImage(size, QImage.Format_RGBA8888)
    image.fill(QColorConstants.Red)
    for x, y in ((0, 0), (size.width()-1, 0), (0, size.height()-1), (size.width()-1, size.height()-1)):
        image.setPixelColor(x, y, QColorConstants.Transparent)
    return QPixmap.fromImage(image)


def paint_to_new_image(item: QGraphicsItem, size: QSize) -> QImage:
    painted_image = QImage(size, QImage.Format_RGBA8888)
    painted_image.fill(QColorConstants.White)
    painter = QPainter(painted_image)
    painter.setRenderHint(QPainter.LosslessImageRendering)
    scene = QGraphicsScene(0, 0, size.width(), size.height())
    scene.addItem(item)
    scene.render(painter)
    return painted_image


@pytest.mark.parametrize("new_state, expected_color", [
    (True, QColorConstants.Red),
    (False, QColorConstants.White),
])
def test_corners_render_correctly_after_creation(qtbot, document_light, new_state: bool, expected_color: QColor):
    document_light.page_layout.draw_sharp_corners = new_state
    card = append_new_card_in_page(document_light.pages[0], "Card")
    card.set_image_file(create_pixmap_with_transparent_corners(
        document_light.image_db.blank_image.size()))
    item = CardItem(card, document_light)
    painted_item = paint_to_new_image(item, card.image_file.size())
    expected = f"{expected_color.red(), expected_color.green(), expected_color.blue()}"
    assert_that(
        color := painted_item.pixelColor(0, 0),
        is_(equal_to(expected_color)),
        f"Got RGB {color.red(), color.green(), color.blue()}, {expected=}"
    )


@pytest.mark.parametrize("old_state, new_state, expected_color", [
    (False, True, QColorConstants.Red),
    (True, False, QColorConstants.White),
])
def test_corner_renders_correctly_after_changing_draw_sharp_corners_option(
        qtbot, document_light, old_state: bool, new_state: bool, expected_color: QColor):
    document_light.page_layout.draw_sharp_corners = old_state
    card = append_new_card_in_page(document_light.pages[0], "Card")
    card_size = document_light.image_db.blank_image.size()
    card.set_image_file(create_pixmap_with_transparent_corners(card_size))
    item = CardItem(card, document_light)

    document_light.page_layout.draw_sharp_corners = new_state
    document_light.page_layout_changed.emit(document_light.page_layout)

    painted_item = paint_to_new_image(item, card.image_file.size())
    expected = f"{expected_color.red(), expected_color.green(), expected_color.blue()}"
    assert_that(
        color := painted_item.pixelColor(0, 0),
        is_(equal_to(expected_color)),
        f"Got RGB {color.red(), color.green(), color.blue()}, {expected=}"
    )
    assert_that(
        color := painted_item.pixelColor(card_size.width()-1, 0),
        is_(equal_to(expected_color)),
        f"Got RGB {color.red(), color.green(), color.blue()}, {expected=}"
    )
    assert_that(
        color := painted_item.pixelColor(0, card_size.height()-1),
        is_(equal_to(expected_color)),
        f"Got RGB {color.red(), color.green(), color.blue()}, {expected=}"
    )
    assert_that(
        color := painted_item.pixelColor(card_size.width()-1, card_size.height()-1),
        is_(equal_to(expected_color)),
        f"Got RGB {color.red(), color.green(), color.blue()}, {expected=}"
    )