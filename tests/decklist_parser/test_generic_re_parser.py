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


import unittest.mock

from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.model.card import Card
from mtg_proxy_printer.model.imagedb import ImageDatabase
from mtg_proxy_printer.decklist_parser.re_parsers import GenericRegularExpressionDeckParser

from tests.helpers import fill_card_database_with_json_cards

import pytest
from hamcrest import *


def _create_image_db_mock(*already_downloaded: Card) -> ImageDatabase:
    image_db: ImageDatabase = unittest.mock.MagicMock()
    image_db.filter_already_downloaded.return_value = already_downloaded
    return image_db


@pytest.mark.parametrize("prefer_already_downloaded", [True, False])
def test_generic_re_parser_with_card_name_only_list(
        qtbot, card_db: CardDatabase, prefer_already_downloaded: bool):
    fill_card_database_with_json_cards(qtbot, card_db, ["regular_english_card", "regular_english_card_reprint"])
    card = card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    image_db = _create_image_db_mock(card)
    parser = GenericRegularExpressionDeckParser(card_db, image_db, r"(?P<name>.+)")
    deck = "Fury Sliver"
    result_deck, unidentified = parser.parse_deck(deck, True, prefer_already_downloaded, "en")
    assert_that(unidentified, is_(empty()))
    assert_that(
        result_deck,
        all_of(
            has_key(
                has_properties(
                    language="en",
                    name="Fury Sliver",
                    is_front=True
                )),
            has_value(1),
            has_length(1)
        )
    )


@pytest.mark.parametrize("prefer_already_downloaded", [True, False])
def test_translating_from_hidden_name_works(
        qtbot, card_db: CardDatabase, prefer_already_downloaded: bool):
    fill_card_database_with_json_cards(
        qtbot, card_db, ["english_Back_to_Basics", "german_Back_to_Basics"], {"hide-cards-without-images": "True"}
    )
    card = card_db.get_card_with_scryfall_id("0600d6c2-0f72-4e79-a55d-1f06dffa48c2", True)
    image_db = _create_image_db_mock(card)
    parser = GenericRegularExpressionDeckParser(card_db, image_db, r"(?P<name>.+)")
    deck = "Grundlagenforschung"
    result_deck, unidentified = parser.parse_deck(deck, True, prefer_already_downloaded, "en")
    assert_that(
        unidentified,
        is_(empty())
    )
    assert_that(
        result_deck,
        all_of(
            has_key(
                has_properties(
                    language="en",
                    name="Back to Basics",
                    scryfall_id="0600d6c2-0f72-4e79-a55d-1f06dffa48c2",
                    is_front=True
                )),
            has_value(1),
            has_length(1)
        )
    )


@pytest.mark.parametrize("deck", ["Mentor Corrosivo", "Mentor corrosivo"])  # Portuguese (1st) and Spanish name (2nd)
@pytest.mark.parametrize("prefer_already_downloaded", [True, False])
def test_translating_from_name_with_ambiguous_language_works(
        qtbot, card_db: CardDatabase, prefer_already_downloaded: bool, deck: str):
    fill_card_database_with_json_cards(
        qtbot, card_db, ["english_Corrosive_Mentor", "spanish_Corrosive_Mentor", "portuguese_Corrosive_Mentor"]
    )
    card = card_db.get_card_with_scryfall_id("140457ff-ee7d-48ec-8b91-ef5c2cc1ed74", True)
    image_db = _create_image_db_mock(card)
    parser = GenericRegularExpressionDeckParser(card_db, image_db, r"(?P<name>.+)")
    result_deck, unidentified = parser.parse_deck(deck, True, prefer_already_downloaded, "en")
    assert_that(
        unidentified,
        is_(empty())
    )
    assert_that(
        result_deck,
        all_of(
            has_key(
                has_properties(
                    language="en",
                    name="Corrosive Mentor",
                    scryfall_id="140457ff-ee7d-48ec-8b91-ef5c2cc1ed74",
                    is_front=True
                )),
            has_value(1),
            has_length(1)
        )
    )


def test_print_guessing_prefers_highres_image_over_newest_printing_with_lowres_image(qtbot, card_db, image_db):
    fill_card_database_with_json_cards(
        qtbot, card_db, ["english_basic_Forest_2", "English_basic_Forest_newest_and_low_res"]
    )
    deck = "Forest"
    parser = GenericRegularExpressionDeckParser(card_db, image_db, r"(?P<name>.+)")
    result_deck, unidentified = parser.parse_deck(deck, True, False)
    assert_that(
        unidentified,
        is_(empty())
    )
    assert_that(
        result_deck,
        all_of(
            has_key(
                has_properties(
                    language="en",
                    name="Forest",
                    set=has_property("name", "Zendikar Rising"),
                    scryfall_id="e2ef9b74-481b-424b-8e33-f0b910f66370",
                    is_front=True
                )),
            has_value(1),
            has_length(1)
        )
    )
