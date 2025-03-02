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
from mtg_proxy_printer.decklist_parser.csv_parsers import ScryfallCSVParser
from mtg_proxy_printer.decklist_downloader import DecklistDownloader

from tests.helpers import fill_card_database_with_json_cards, SHOULD_SKIP_NETWORK_TESTS

StringList = typing.List[str]
DECK_LIST_CSV_HEADER = "section,count,name,mana_cost,type,set,set_code,collector_number,lang,rarity," \
    "artist,finish,usd_price,eur_price,tix_price,scryfall_uri,scryfall_id"
SEARCH_CSV_HEADER = "multiverse_id,mtgo_id,set,collector_number,lang,rarity,name,mana_cost,cmc,type_line,artist," \
    "usd_price,usd_foil_price,eur_price,tix_price,image_uri,scryfall_uri,scryfall_id"

def append_to_header(header: str, plain_deck_list: str) -> str:
    return f"{header}\n{plain_deck_list}"

@pytest.mark.skipif(SHOULD_SKIP_NETWORK_TESTS, reason="Skipping network-hitting tests")
@pytest.mark.parametrize("url, header", [
    ("https://api.scryfall.com/decks/e1a9af19-cfff-48c4-ae74-ed2dd78cb736/export/csv", DECK_LIST_CSV_HEADER),
    ("https://api.scryfall.com/cards/search?q=scryfallid%3Ad99a9a7d-d9ca-4c11-80ab-e39d5943a315&format=csv", SEARCH_CSV_HEADER)
])
def test_local_header_conforms_to_current_scryfall_return_data(url: str, header: str):
    """Verifies that the hard-coded CSV headers above match what the API returns"""
    downloader = DecklistDownloader()
    result = downloader.download(url)
    expected = result.splitlines()[0]
    assert_that(
        header, is_(equal_to(expected)), "CSV header format changed on Scryfall"
    )



@pytest.mark.parametrize(
    "cards_to_import, deck_list, expected_card", [
        (["german_Back_to_Basics", "english_Back_to_Basics"],
        append_to_header(
            DECK_LIST_CSV_HEADER,
            "nonlands,1,Back to Basics,{2}{U},Enchantment,Urza's Saga,usg,62,de,rare,Andrew Robinson,,13.27,7.9,"
            "2.92,https://scryfall.com/card/usg/62/de/grundlagenforschung,97b84e7d-258f-46dc-baef-4b1eb6f28d4d"),
        CardIdentificationData("en", "Back to Basics", is_front=True,)),
        (["german_Back_to_Basics", "english_Back_to_Basics"],
        append_to_header(
            SEARCH_CSV_HEADER,
            ",,USG,62,de,R,Back to Basics,{2}{U},3.0,Enchantment,Andrew Robinson,,,,,"
            "https://cards.scryfall.io/large/front/9/7/97b84e7d-258f-46dc-baef-4b1eb6f28d4d.jpg?1562927127,"
            "https://scryfall.com/card/usg/62/de/grundlagenforschung,97b84e7d-258f-46dc-baef-4b1eb6f28d4d"),
        CardIdentificationData("en", "Back to Basics", is_front=True,)),
    ])
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

def generate_test_cases_for_translation_and_replacement():
    # DE to EN
    yield (["german_Back_to_Basics", "english_Back_to_Basics"],
        append_to_header(
            DECK_LIST_CSV_HEADER,
            "nonlands,1,Back to Basics,{2}{U},Enchantment,Urza's Saga,usg,62,de,rare,Andrew Robinson,,13.27,7.9,"
            "2.92,https://scryfall.com/card/usg/62/de/grundlagenforschung,97b84e7d-258f-46dc-baef-4b1eb6f28d4d"),
        CardIdentificationData("en", "Back to Basics", is_front=True,))
    yield (["german_Back_to_Basics", "english_Back_to_Basics"],
        append_to_header(
            SEARCH_CSV_HEADER,
            ",,USG,62,de,R,Back to Basics,{2}{U},3.0,Enchantment,Andrew Robinson,,,,,"
            "https://cards.scryfall.io/large/front/9/7/97b84e7d-258f-46dc-baef-4b1eb6f28d4d.jpg?1562927127,"
            "https://scryfall.com/card/usg/62/de/grundlagenforschung,97b84e7d-258f-46dc-baef-4b1eb6f28d4d"),
        CardIdentificationData("en", "Back to Basics", is_front=True,))
    # DE to DE
    yield (
        ["german_Back_to_Basics", "english_Back_to_Basics"],
        append_to_header(
            DECK_LIST_CSV_HEADER,
            "nonlands,1,Back to Basics,{2}{U},Enchantment,Urza's Saga,usg,62,de,rare,Andrew Robinson,,13.27,7.9,"
            "2.92,https://scryfall.com/card/usg/62/de/grundlagenforschung,97b84e7d-258f-46dc-baef-4b1eb6f28d4d"),
        CardIdentificationData("de", "Grundlagenforschung", is_front=True,))
    yield (["german_Back_to_Basics", "english_Back_to_Basics"],
        append_to_header(
            SEARCH_CSV_HEADER,
            ",,USG,62,de,R,Back to Basics,{2}{U},3.0,Enchantment,Andrew Robinson,,,,,"
            "https://cards.scryfall.io/large/front/9/7/97b84e7d-258f-46dc-baef-4b1eb6f28d4d.jpg?1562927127,"
            "https://scryfall.com/card/usg/62/de/grundlagenforschung,97b84e7d-258f-46dc-baef-4b1eb6f28d4d"),
        CardIdentificationData("de", "Grundlagenforschung", is_front=True,))
    # EN TO DE
    yield (
        ["german_Back_to_Basics", "english_Back_to_Basics"],
        append_to_header(
            DECK_LIST_CSV_HEADER,
            "columna,1,Back to Basics,{2}{U},Enchantment,Urza's Saga,usg,62,en,rare,Andrew Robinson,nonfoil,"
            "13.52,9.77,5.12,https://scryfall.com/card/usg/62/back-to-basics,fab4cd7e-b56f-4408-a0e9-c07e040cc38f"),
        CardIdentificationData("de", "Grundlagenforschung", is_front=True,))
    yield (["german_Back_to_Basics", "english_Back_to_Basics"],
        append_to_header(
            SEARCH_CSV_HEADER,
            "5711,12287,USG,62,en,R,Back to Basics,{2}{U},3.0,Enchantment,Andrew Robinson,13.52,,9.77,5.12,"
            "https://cards.scryfall.io/large/front/f/a/fab4cd7e-b56f-4408-a0e9-c07e040cc38f.jpg?1562948100,"
            "https://scryfall.com/card/usg/62/back-to-basics,fab4cd7e-b56f-4408-a0e9-c07e040cc38f"),
        CardIdentificationData("de", "Grundlagenforschung", is_front=True,))


@pytest.mark.parametrize(
    "cards_to_import, deck_list, target_card", generate_test_cases_for_translation_and_replacement())
def test_deck_list_translation_works(
        qtbot, card_db, image_db, cards_to_import: StringList,  deck_list: str, target_card: CardIdentificationData):
    fill_card_database_with_json_cards(qtbot, card_db, cards_to_import, {"hide-cards-without-images": "False"})
    card = _get_expected_card_from_database(card_db, target_card)
    parser = ScryfallCSVParser(card_db, image_db)
    assert_that(
        parser.parse_deck(deck_list, False, False, target_card.language),
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
    matches = card_db.get_cards_from_data(expected_card)
    assert_that(matches, has_length(1), "Setup failed.")
    card, = matches
    assert_that(
        card, has_properties(
            name=equal_to(expected_card.name),
            language=equal_to(expected_card.language),
            is_front=is_(expected_card.is_front),
        ),
        "Setup failed.")
    return card


def generate_test_cases_for_test_card_identification_works_in_simple_cases():
    yield (
        ["english_basic_Forest", "english_basic_Forest_2"],
        append_to_header(
            DECK_LIST_CSV_HEADER,
            "columna,1,Forest,"",Basic Land — Forest,Arena Beginner Set,anb,112,en,common,Jonas De Ro,,0.06,0.01,"
            "0.01,https://scryfall.com/card/anb/112/forest,7ef83f4c-d3ff-4905-a16d-f2bae673a5b2"),
        CardIdentificationData("en", "Forest", scryfall_id="7ef83f4c-d3ff-4905-a16d-f2bae673a5b2", is_front=True,)
    )
    yield (
        ["english_basic_Forest", "english_basic_Forest_2"],
        append_to_header(
            SEARCH_CSV_HEADER,
            "548224,,ANB,112,en,C,Forest,"",0.0,Basic Land — Forest,Jonas De Ro,,,,,"
            "https://cards.scryfall.io/large/front/7/e/7ef83f4c-d3ff-4905-a16d-f2bae673a5b2.jpg?1597375433,"
            "https://scryfall.com/card/anb/112/forest,7ef83f4c-d3ff-4905-a16d-f2bae673a5b2"),
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
            DECK_LIST_CSV_HEADER,
            "columna,invalid_count,Forest,"",Basic Land — Forest,Arena Beginner Set,anb,112,en,common,Jonas De Ro,,0.06,0.01,"
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
