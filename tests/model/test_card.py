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
import copy

import pytest
from PySide6.QtCore import QBuffer, QIODevice
from PySide6.QtGui import QPixmap, QColorConstants, QColor
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.model.card import Card, MTGSet, CardCorner, CustomCard, CheckCard
from mtg_proxy_printer.units_and_sizes import CardSize, CardSizes, PageType, UUID

from hamcrest import *


# noinspection PyUnusedLocal
@pytest.fixture()
def card(qtbot: QtBot) -> Card:  # QPixmap() requires a QApplication to function
    size = CardSizes.REGULAR
    pixmap = QPixmap(size.as_qsize_px())
    pixmap.fill(QColorConstants.Red)
    return Card(
        "Name", MTGSet("CODE", "Set name"), "collector number", "en",
        "11112222-3333-4444-5555-666677778888", True,
        "aaaabbbb-cccc-dddd-eeee-ffff00001111", "/nonexistent", True,
        size, 1, False, pixmap
    )


# noinspection PyUnusedLocal
@pytest.fixture()
def oversized(qtbot: QtBot) -> Card:  # QPixmap() requires a QApplication to function
    size = CardSizes.OVERSIZED
    pixmap = QPixmap(size.as_qsize_px())
    pixmap.fill(QColorConstants.Red)
    return Card(
        "Name", MTGSet("CODE", "Set name"), "collector number", "en",
        "11112222-3333-4444-5555-666677778888", True,
        "aaaabbbb-cccc-dddd-eeee-ffff00001111", "/nonexistent", True,
        size, 1, False, pixmap
    )


def test_card_corner_color_is_cached(card: Card):
    assert_that(card.corner_color(CardCorner.TOP_LEFT), is_(equal_to(QColorConstants.Red)))
    new_pixmap = card.image_file.copy()
    new_pixmap.fill(QColorConstants.Blue)
    card.image_file = new_pixmap  # Direct assignment does not clear the cache
    assert_that(card.corner_color(CardCorner.TOP_LEFT), is_(equal_to(QColorConstants.Red)))


def test_card_set_image_file_resets_corner_color(card: Card):
    assert_that(card.corner_color(CardCorner.TOP_LEFT), is_(equal_to(QColorConstants.Red)))
    new_pixmap = card.image_file.copy()
    new_pixmap.fill(QColorConstants.Blue)
    card.set_image_file(new_pixmap)
    assert_that(card.corner_color(CardCorner.TOP_LEFT), is_(equal_to(QColorConstants.Blue)))


def test_card_set_code(card: Card):
    assert_that(card.set_code, is_("CODE"))


def test_card_is_custom_card(card: Card):
    assert_that(card.is_custom_card, is_(False))


def test_card_is_oversized(card: Card, oversized: Card):
    assert_that(card.is_oversized, is_(False))
    assert_that(oversized.is_oversized, is_(True))


def test_card_requested_page_type(card: Card, oversized: Card):
    assert_that(card.requested_page_type(), is_(PageType.REGULAR))
    assert_that(oversized.requested_page_type(), is_(PageType.OVERSIZED))


def test_card_display_string(card: Card):
    assert_that(card.display_string(), is_('"Name" [CODE:collector number]'))


def image_as_bytes(color: QColor, size: CardSize) -> bytes:
    pixmap = QPixmap(size.as_qsize_px())
    pixmap.fill(color)
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    pixmap.save(buffer, "PNG", quality=100)
    return buffer.data().data()


# noinspection PyUnusedLocal
@pytest.fixture()
def custom_card(qtbot: QtBot) -> CustomCard:  # QPixmap() requires a QApplication to function
    size = CardSizes.REGULAR
    image = image_as_bytes(QColorConstants.Red, size)
    return CustomCard(
        "Name", MTGSet("CODE", "Set name"), "collector number", "en",
        True, "/nonexistent", True,
        size, 1, False, image
    )


# noinspection PyUnusedLocal
@pytest.fixture()
def custom_oversized(qtbot: QtBot) -> CustomCard:  # QPixmap() requires a QApplication to function
    size = CardSizes.OVERSIZED
    image = image_as_bytes(QColorConstants.Red, size)
    return CustomCard(
        "Name", MTGSet("CODE", "Set name"), "collector number", "en",
        True, "/nonexistent", True,
        size, 1, False, image
    )


def test_custom_card_corner_color(custom_card: CustomCard):
    assert_that(custom_card.corner_color(CardCorner.TOP_LEFT), is_(equal_to(QColorConstants.Red)))


def test_custom_card_image_file(custom_card: CustomCard):
    image = custom_card.image_file.toImage()
    test_px = image.pixelColor(image.width()//2, image.height()//2)
    assert_that(test_px, is_(equal_to(QColorConstants.Red)))


def test_custom_card_scryfall_id_is_uuid(custom_card: CustomCard):
    assert_that(custom_card.scryfall_id, instance_of(UUID), "Scryfall ID not a UUID")


def test_custom_card_set_code(custom_card: CustomCard):
    assert_that(custom_card.set_code, is_("CODE"))


def test_custom_card_is_custom_card(custom_card: CustomCard):
    assert_that(custom_card.is_custom_card, is_(True))


def test_custom_card_is_oversized(custom_card: CustomCard, custom_oversized: CustomCard):
    assert_that(custom_card.is_oversized, is_(False))
    assert_that(custom_oversized.is_oversized, is_(True))


def test_custom_card_requested_page_type(custom_card: CustomCard, custom_oversized: CustomCard):
    assert_that(custom_card.requested_page_type(), is_(PageType.REGULAR))
    assert_that(custom_oversized.requested_page_type(), is_(PageType.OVERSIZED))


def test_custom_card_display_string(custom_card: CustomCard):
    assert_that(custom_card.display_string(), is_('"Name" [CODE:collector number]'))


def test_custom_card_oracle_id_is_empty(custom_card: CustomCard):
    assert_that(custom_card.oracle_id, is_(empty()))


@pytest.mark.parametrize("property_name", Card.__annotations__)
def test_custom_card_has_all_card_attributes(custom_card: CustomCard, property_name: str):
    assert_that(custom_card, has_property(property_name))


def _create_back(front: Card) -> Card:
    back = copy.copy(front)
    image = front.image_file.copy()
    image.fill(QColorConstants.Green)
    back.set_image_file(image)
    back.name = "Back"
    back.is_front = False
    back.face_number = front.face_number + 1
    return back


@pytest.fixture()
def check_card(card: Card) -> CheckCard:
    back = _create_back(card)
    return CheckCard(card, back)


@pytest.fixture()
def oversized_check_card(oversized: Card) -> CheckCard:
    back = _create_back(oversized)
    return CheckCard(oversized, back)


def test_check_card_corner_color(check_card: CheckCard):
    assert_that(check_card.corner_color(CardCorner.TOP_LEFT), is_(equal_to(QColorConstants.Red)))
    assert_that(check_card.corner_color(CardCorner.BOTTOM_LEFT), is_(equal_to(QColorConstants.Green)))


def test_check_card_image_file(check_card: CheckCard):
    image = check_card.image_file.toImage()
    test_px_top = image.pixelColor(image.width()//2, image.height()//3)
    assert_that(test_px_top, is_(equal_to(QColorConstants.Red)))
    test_px_bottom = image.pixelColor(image.width()//2, image.height()-image.height()//3)
    assert_that(test_px_bottom, is_(equal_to(QColorConstants.Green)))


def test_check_card_scryfall_id_is_uuid(check_card: CheckCard):
    assert_that(check_card.scryfall_id, is_(check_card.front.scryfall_id))


def test_check_card_set_code(check_card: CheckCard):
    assert_that(check_card.set_code, is_("CODE"))


def test_check_card_is_custom_card(check_card: CheckCard):
    assert_that(check_card.is_custom_card, is_(False))


def test_check_card_is_oversized(check_card: CheckCard, oversized_check_card: CheckCard):
    assert_that(check_card.is_oversized, is_(False))
    assert_that(oversized_check_card.is_oversized, is_(True))


def test_check_card_requested_page_type(check_card: CheckCard, oversized_check_card: CheckCard):
    assert_that(check_card.requested_page_type(), is_(PageType.REGULAR))
    assert_that(oversized_check_card.requested_page_type(), is_(PageType.OVERSIZED))


def test_check_card_display_string(check_card: CheckCard):
    assert_that(check_card.display_string(), is_('"Name // Back" [CODE:collector number]'))


def test_check_card_oracle_id_is_empty(check_card: CheckCard):
    assert_that(check_card.oracle_id, is_(check_card.front.oracle_id))


@pytest.mark.parametrize("property_name", Card.__annotations__)
def test_check_card_has_all_card_attributes(check_card: CheckCard, property_name: str):
    assert_that(check_card, has_property(property_name))
