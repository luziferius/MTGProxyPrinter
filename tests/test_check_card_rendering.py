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
from hamcrest import *
from PySide6.QtGui import QPixmap, QColorConstants

from mtg_proxy_printer.model.card import MTGSet, Card, CheckCard
from mtg_proxy_printer.units_and_sizes import CardSizes


@pytest.fixture
def blank_image(qtbot) -> QPixmap:
    pixmap = QPixmap(CardSizes.REGULAR.as_qsize_px())
    pixmap.fill(QColorConstants.White)
    return pixmap


def test_render_check_card_image_is_not_none_if_both_faces_have_an_image(blank_image: QPixmap):
    front = Card(name='Search for Azcanta', set=MTGSet(code='xln', name='Ixalan'), collector_number='74', language='en', scryfall_id='1a7e242e-bb48-4134-a1c2-6033713d658f', is_front=True, oracle_id='f74c4d96-bc4a-4d32-9519-a753d192144e', image_uri='https://cards.scryfall.io/png/front/1/a/1a7e242e-bb48-4134-a1c2-6033713d658f.png?1562551479', highres_image=True, size=CardSizes.REGULAR, face_number=0, is_dfc=True,
                 image_file=blank_image)
    back = Card(name='Azcanta, the Sunken Ruin', set=MTGSet(code='xln', name='Ixalan'), collector_number='74', language='en', scryfall_id='1a7e242e-bb48-4134-a1c2-6033713d658f', is_front=False, oracle_id='f74c4d96-bc4a-4d32-9519-a753d192144e', image_uri='https://cards.scryfall.io/png/back/1/a/1a7e242e-bb48-4134-a1c2-6033713d658f.png?1562551479', highres_image=True, size=CardSizes.REGULAR, face_number=1, is_dfc=True,
                image_file=blank_image)
    check_card = CheckCard(front, back)
    assert_that(check_card.image_file, is_(not_none()))


def test_render_check_card_image_is_none_if_front_image_is_None(blank_image: QPixmap):
    front = Card(name='Search for Azcanta', set=MTGSet(code='xln', name='Ixalan'), collector_number='74', language='en', scryfall_id='1a7e242e-bb48-4134-a1c2-6033713d658f', is_front=True, oracle_id='f74c4d96-bc4a-4d32-9519-a753d192144e', image_uri='https://cards.scryfall.io/png/front/1/a/1a7e242e-bb48-4134-a1c2-6033713d658f.png?1562551479', highres_image=True, size=CardSizes.REGULAR, face_number=0, is_dfc=True,
                 image_file=None)
    back = Card(name='Azcanta, the Sunken Ruin', set=MTGSet(code='xln', name='Ixalan'), collector_number='74', language='en', scryfall_id='1a7e242e-bb48-4134-a1c2-6033713d658f', is_front=False, oracle_id='f74c4d96-bc4a-4d32-9519-a753d192144e', image_uri='https://cards.scryfall.io/png/back/1/a/1a7e242e-bb48-4134-a1c2-6033713d658f.png?1562551479', highres_image=True, size=CardSizes.REGULAR, face_number=1, is_dfc=True,
                image_file=blank_image)
    check_card = CheckCard(front, back)
    assert_that(check_card.image_file, is_(none()))


def test_render_check_card_image_is_none_if_back_image_is_None(blank_image: QPixmap):
    front = Card(name='Search for Azcanta', set=MTGSet(code='xln', name='Ixalan'), collector_number='74', language='en', scryfall_id='1a7e242e-bb48-4134-a1c2-6033713d658f', is_front=True, oracle_id='f74c4d96-bc4a-4d32-9519-a753d192144e', image_uri='https://cards.scryfall.io/png/front/1/a/1a7e242e-bb48-4134-a1c2-6033713d658f.png?1562551479', highres_image=True, size=CardSizes.REGULAR, face_number=0, is_dfc=True,
                 image_file=blank_image)
    back = Card(name='Azcanta, the Sunken Ruin', set=MTGSet(code='xln', name='Ixalan'), collector_number='74', language='en', scryfall_id='1a7e242e-bb48-4134-a1c2-6033713d658f', is_front=False, oracle_id='f74c4d96-bc4a-4d32-9519-a753d192144e', image_uri='https://cards.scryfall.io/png/back/1/a/1a7e242e-bb48-4134-a1c2-6033713d658f.png?1562551479', highres_image=True, size=CardSizes.REGULAR, face_number=1, is_dfc=True,
                image_file=None)
    check_card = CheckCard(front, back)
    assert_that(check_card.image_file, is_(none()))


def test_render_check_card_image_is_none_if_both_images_are_None():
    front = Card(name='Search for Azcanta', set=MTGSet(code='xln', name='Ixalan'), collector_number='74', language='en', scryfall_id='1a7e242e-bb48-4134-a1c2-6033713d658f', is_front=True, oracle_id='f74c4d96-bc4a-4d32-9519-a753d192144e', image_uri='https://cards.scryfall.io/png/front/1/a/1a7e242e-bb48-4134-a1c2-6033713d658f.png?1562551479', highres_image=True, size=CardSizes.REGULAR, face_number=0, is_dfc=True,
                 image_file=None)
    back = Card(name='Azcanta, the Sunken Ruin', set=MTGSet(code='xln', name='Ixalan'), collector_number='74', language='en', scryfall_id='1a7e242e-bb48-4134-a1c2-6033713d658f', is_front=False, oracle_id='f74c4d96-bc4a-4d32-9519-a753d192144e', image_uri='https://cards.scryfall.io/png/back/1/a/1a7e242e-bb48-4134-a1c2-6033713d658f.png?1562551479', highres_image=True, size=CardSizes.REGULAR, face_number=1, is_dfc=True,
                image_file=None)
    check_card = CheckCard(front, back)
    assert_that(check_card.image_file, is_(none()))
