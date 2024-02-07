# Copyright (C) 2020-2024 Thomas Hess <thomas.hess@udo.edu>
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

import typing
import unittest.mock

import pytest
from hamcrest import *

from mtg_proxy_printer.model.carddb import CardDatabase, Card, CardIdentificationData
from mtg_proxy_printer.decklist_parser.csv_parsers import ScryfallCSVParser

from tests.helpers import fill_card_database_with_json_cards

StringList = typing.List[str]
CSV_HEADER = "section,count,name,mana_cost,type,set,set_code,collector_number,lang,rarity," \
             "artist,foil,usd_price,eur_price,tix_price,scryfall_uri,scryfall_id"


def append_to_header(plain_deck_list: str) -> str:
    return f"{CSV_HEADER}\n{plain_deck_list}"


def generate_test_cases_for_translation_and_replacement():
    yield (
        ["german_Back_to_Basics", "english_Back_to_Basics"],
        append_to_header(
            "nonlands,1,Back to Basics,{2}{U},Enchantment,Urza's Saga,usg,62,de,rare,Andrew Robinson,false,13.27,7.9,"
            "2.92,https://scryfall.com/card/usg/62/de/grundlagenforschung,97b84e7d-258f-46dc-baef-4b1eb6f28d4d"),
        CardIdentificationData("en", "Back to Basics", is_front=True,)
    )


@pytest.mark.parametrize(
    "cards_to_import, deck_list, expected_card", generate_test_cases_for_translation_and_replacement())
def test_excluded_printing_is_replaced_with_an_available_printing(
        qtbot, card_db, image_db, cards_to_import: StringList,  deck_list: str, expected_card: CardIdentificationData):
    fill_card_database_with_json_cards(qtbot, card_db, cards_to_import, {"hide-cards-without-images": "True"})
    card = _get_expected_card_from_database(card_db, expected_card)
    parser = ScryfallCSVParser(card_db, image_db)
    assert_that(
        parser.parse_deck(deck_list, False, False, None),
        contains_exactly(
            all_of(
                has_key(card),
                has_value(1),
                has_length(1)
            ),
            is_(empty())
        )
    )


@pytest.mark.parametrize(
    "cards_to_import, deck_list, expected_card", generate_test_cases_for_translation_and_replacement())
def test_deck_list_translation_works(
        qtbot, card_db, image_db, cards_to_import: StringList,  deck_list: str, expected_card: CardIdentificationData):
    fill_card_database_with_json_cards(qtbot, card_db, cards_to_import)
    card = _get_expected_card_from_database(card_db, expected_card)
    parser = ScryfallCSVParser(card_db, image_db)
    assert_that(
        parser.parse_deck(deck_list, False, False, "en"),
        contains_exactly(
            all_of(
                has_key(card),
                has_value(1),
                has_length(1)
            ),
            is_(empty())
        )
    )


def _get_expected_card_from_database(card_db: CardDatabase, expected_card: CardIdentificationData) -> Card:
    assert_that(
        (card_list := card_db.get_cards_from_data(expected_card)),
        has_length(1)
    )
    return card_list[0]


def generate_test_cases_for_test_card_identification_works_in_simple_cases():
    yield (
        ["english_basic_Forest", "english_basic_Forest_2"],
        append_to_header(
            "columna,1,Forest,"",Basic Land — Forest,Arena Beginner Set,anb,112,en,common,Jonas De Ro,false,0.06,0.01,"
            "0.01,https://scryfall.com/card/anb/112/forest,7ef83f4c-d3ff-4905-a16d-f2bae673a5b2"),
        CardIdentificationData("en", "Forest", scryfall_id="7ef83f4c-d3ff-4905-a16d-f2bae673a5b2", is_front=True,)
    )


@pytest.mark.parametrize(
    "cards_to_import, deck_list, expected_card",
    generate_test_cases_for_test_card_identification_works_in_simple_cases())
def test_card_identification_works_in_simple_cases(
        qtbot, card_db, image_db, cards_to_import: StringList,  deck_list: str, expected_card: CardIdentificationData):
    fill_card_database_with_json_cards(qtbot, card_db, cards_to_import, {"hide-digital-cards": "False"})
    card = _get_expected_card_from_database(card_db, expected_card)
    parser = ScryfallCSVParser(card_db, image_db)
    with unittest.mock.patch.object(CardDatabase, "translate_card") as translate_card:
        result = parser.parse_deck(deck_list, False, False, None)
        translate_card.assert_not_called()
        assert_that(
            result,
            contains_exactly(
                all_of(
                    has_key(card),
                    has_value(1),
                    has_length(1)
                ),
                is_(empty())
            )
        )


@pytest.mark.parametrize(
    "cards_to_import, deck_list", [
    (
        ["english_basic_Forest"],
        append_to_header(
        "columna,invalid_count,Forest,"",Basic Land — Forest,Arena Beginner Set,anb,112,en,common,Jonas De Ro,false,0.06,0.01,"
        "0.01,https://scryfall.com/card/anb/112/forest,7ef83f4c-d3ff-4905-a16d-f2bae673a5b2"),
    ),
    ]
)
def test_line_with_invalid_count_is_added_to_invalid_lines(
        qtbot, card_db, image_db, cards_to_import: StringList,  deck_list: str,):
    fill_card_database_with_json_cards(qtbot, card_db, cards_to_import)
    parser = ScryfallCSVParser(card_db, image_db)
    assert_that(
        parser.parse_deck(deck_list, False, False, None),
        contains_exactly(
            is_(empty()),
            contains_exactly(
                deck_list.splitlines()[-1]
            )
        )
    )
