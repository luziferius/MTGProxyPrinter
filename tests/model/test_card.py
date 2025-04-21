#  Copyright © 2020-2025  Thomas Hess <thomas.hess@udo.edu>
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

import pytest
from PyQt5.QtCore import QBuffer, QIODevice, QPoint
from PyQt5.QtGui import QPixmap, QColorConstants, QColor
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.model.card import Card, MTGSet, CardCorner, CustomCard
from mtg_proxy_printer.units_and_sizes import CardSize, CardSizes, PageType, UUID

from hamcrest import *

@pytest.fixture()
def card(qtbot: QtBot) -> Card:
    size = CardSizes.REGULAR
    pixmap = QPixmap(size.as_qsize_px())
    pixmap.fill(QColorConstants.Red)
    return Card(
        "Name", MTGSet("CODE", "Set name"), "collector number", "en",
        "11112222-3333-4444-5555-666677778888", True,
        "aaaabbbb-cccc-dddd-eeee-ffff00001111", "/nonexistent", True,
        size, 1, False, pixmap
    )

@pytest.fixture()
def oversized(qtbot: QtBot) -> Card:
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


@pytest.fixture()
def custom_card(qtbot: QtBot) -> CustomCard:
    size = CardSizes.REGULAR
    image = image_as_bytes(QColorConstants.Red, size)
    return CustomCard(
        "Name", MTGSet("CODE", "Set name"), "collector number", "en",
        True, "/nonexistent", True,
        size, 1, False, image
    )

@pytest.fixture()
def custom_oversized(qtbot: QtBot) -> CustomCard:
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
    assert_that(custom_card.scryfall_id, is_(instance_of(UUID)))


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
