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


import typing
import unittest.mock

import pytest
from hamcrest import *

from mtg_proxy_printer.model.carddb import CardDatabase, Card, CardIdentificationData
from mtg_proxy_printer.decklist_parser.csv_parsers import TappedOutCSVParser
from mtg_proxy_printer.decklist_downloader import TappedOutDownloader

from tests.helpers import fill_card_database_with_json_cards, SHOULD_SKIP_NETWORK_TESTS

StringList = typing.List[str]
CSV_HEADER = "Board,Qty,Name,Printing,Foil,Alter,Signed,Condition,Language"


def append_to_header(plain_deck_list: str) -> str:
    return f"{CSV_HEADER}\n{plain_deck_list}"


@pytest.mark.skipif(SHOULD_SKIP_NETWORK_TESTS, reason="Skipping network-hitting tests")
@pytest.mark.parametrize("url, header", [
    ("https://tappedout.net/mtg-decks/mtgproxyprinter-test-deck/", CSV_HEADER),
    # TODO: Commander decks have an additional column for Commander designation
])
def test_local_header_conforms_to_current_scryfall_return_data(url: str, header: str):
    """Verifies that the hard-coded CSV headers above match what the API returns"""
    downloader = TappedOutDownloader()
    result = downloader.download(url)
    expected = result.splitlines()[0]
    assert_that(
        header, is_(equal_to(expected)), "CSV header format changed on Tappedout"
    )

def generate_test_cases_for_translation_and_replacement():
    yield (
        ["german_Back_to_Basics", "english_Back_to_Basics"],
        append_to_header("main,1,Back to Basics,USG,,,,,de"),
        CardIdentificationData("en", "Back to Basics", is_front=True,)
    )


@pytest.mark.parametrize(
    "cards_to_import, deck_list, expected_card", generate_test_cases_for_translation_and_replacement())
def test_excluded_printing_is_replaced_with_an_available_printing(
        qtbot, card_db, image_db, cards_to_import: StringList,  deck_list: str, expected_card: CardIdentificationData):
    fill_card_database_with_json_cards(qtbot, card_db, cards_to_import, {"hide-cards-without-images": "True"})
    card = _get_expected_card_from_database(card_db, expected_card)
    parser = TappedOutCSVParser(card_db, image_db)
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


@pytest.mark.parametrize("cards_to_import, deck_list, expected_card", generate_test_cases_for_translation_and_replacement())
def test_deck_list_translation_works(
        qtbot, card_db, image_db, cards_to_import: StringList,  deck_list: str, expected_card: CardIdentificationData):
    fill_card_database_with_json_cards(qtbot, card_db, cards_to_import)
    card = _get_expected_card_from_database(card_db, expected_card)
    parser = TappedOutCSVParser(card_db, image_db)
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
        append_to_header("main,1,Forest,ANB,,,,,en"),
        CardIdentificationData("en", "Forest", scryfall_id="7ef83f4c-d3ff-4905-a16d-f2bae673a5b2", is_front=True,)
    )


@pytest.mark.parametrize(
    "cards_to_import, deck_list, expected_card",
    generate_test_cases_for_test_card_identification_works_in_simple_cases())
def test_card_identification_works_in_simple_cases(
        qtbot, card_db, image_db, cards_to_import: StringList,  deck_list: str, expected_card: CardIdentificationData):
    fill_card_database_with_json_cards(qtbot, card_db, cards_to_import, {"hide-digital-cards": "False"})
    card = _get_expected_card_from_database(card_db, expected_card)
    parser = TappedOutCSVParser(card_db, image_db)
    with unittest.mock.patch.object(CardDatabase, "translate_card") as translate_card:
        result = parser.parse_deck(deck_list, False, False, None)
        translate_card.assert_not_called()
        assert_that(
            result,
            contains_exactly(
                has_key(card),
                is_(empty())
            )
        )


@pytest.mark.parametrize(
    "cards_to_import, deck_list", [
        (
            ["english_basic_Forest"],
            append_to_header("main,invalid_count,Forest,ANB,,,,,en"),
        ),
    ]
)
def test_rows_with_invalid_data_are_added_to_invalid_lines(
        qtbot, card_db, image_db, cards_to_import: StringList,  deck_list: str):
    fill_card_database_with_json_cards(qtbot, card_db, cards_to_import)
    parser = TappedOutCSVParser(card_db, image_db)
    assert_that(
        parser.parse_deck(deck_list, False, False, None),
        contains_exactly(
            is_(empty()),
            contains_exactly(
                deck_list.splitlines()[-1]
            )
        )
    )
