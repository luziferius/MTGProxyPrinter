# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import datetime
import textwrap
import typing
import unittest.mock
from unittest.mock import MagicMock

from hamcrest import *
import pytest

import mtg_proxy_printer.settings
from mtg_proxy_printer.model.carddb import CardDatabase, CardIdentificationData, MINIMUM_REFRESH_DELAY, CardList, Card,\
    MTGSet
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard

from .helpers import assert_model_is_empty, fill_card_database_with_json_card, \
    fill_card_database_with_json_cards, is_dataclass_equal_to, matches_type_annotation

StringList = typing.List[str]
OptString = typing.Optional[str]


def test_has_data_on_empty_database_returns_false(card_db: CardDatabase):
    assert_model_is_empty(card_db)
    assert_that(card_db.has_data(), is_(False))


def test_has_data_on_filled_database_returns_true(qtbot, card_db: CardDatabase):
    fill_card_database_with_json_card(qtbot, card_db, "regular_english_card")
    assert_that(card_db.has_data(), is_(True))


def test_get_all_languages_without_data(card_db: CardDatabase):
    assert_that(
        card_db.get_all_languages(),
        is_(empty())
    )


def test_get_all_languages_with_data(qtbot, card_db: CardDatabase):
    fill_card_database_with_json_cards(
        qtbot, card_db,
        [
            "english_Coercion",
            "english_Duress",
            "german_Coercion_with_faulty_translation",
            "spanish_basic_Forest",
            "german_Duress",
        ],
    )
    assert_that(
        card_db.get_all_languages(),
        contains_exactly("de", "en", "es")
    )


@pytest.mark.parametrize("language, prefix, expected_names", [
    ("en", None, ["Forest", "Future Sight", "Duress", "Coercion"]),
    ("en", "Fu", ["Future Sight"]),
    ("en", "%or", ["Forest"]),
    ("en", "AAAAAAAA", []),
    ("en", "F%t", ["Forest", "Future Sight"]),
    ("de", None, ["Wald", "Zwang"]),  # noqa  # A German Forest and Duress
    ("es", None, ["Bosque"]),  # noqa  # A Spanish Forest
    ("Nonexisting language", None, []),
])
def test_get_card_names(qtbot, card_db: CardDatabase, language: str, prefix: OptString, expected_names: StringList):
    fill_card_database_with_json_cards(
        qtbot, card_db,
        [
            "english_Coercion",
            "english_Duress",
            "english_basic_Forest",
            "english_basic_Forest_2",
            "english_card_Future_Sight_MH1",
            "english_card_Future_Sight_MTGO_promo",
            "german_Coercion_with_faulty_translation",
            "german_basic_Forest",
            "spanish_basic_Forest",
            "german_Duress",
        ],
    )
    assert_that(
        card_db.get_card_names(language, prefix),
        contains_inanyorder(*expected_names)
    )


@pytest.mark.parametrize("name, expected", [
    ("Forest", "en"),
    ("Future Sight", "en"),
    ("Wald", "de"),
    ("Bosque", "es"),
    ("Unknown", None),
    ("Mentor Corrosivo", "pt"),
    ("Mentor corrosivo", "es"),
])
def test_guess_language_from_name(qtbot, card_db: CardDatabase, name: str, expected: OptString):
    fill_card_database_with_json_cards(
        qtbot, card_db,
        [
            "english_Coercion",
            "english_Duress",
            "english_basic_Forest",
            "english_basic_Forest_2",
            "english_card_Future_Sight_MH1",
            "english_card_Future_Sight_MTGO_promo",
            "german_Coercion_with_faulty_translation",
            "german_basic_Forest",
            "spanish_basic_Forest",
            "german_Duress",
            "korean_Forest_with_placeholder_name",
            "portuguese_Corrosive_Mentor",
            "spanish_Corrosive_Mentor",
        ],
    )
    assert_that(
        card_db.guess_language_from_name(name),
        is_(equal_to(expected))
    )


@pytest.mark.parametrize("language, expected", [
    ("en", True),
    ("de", True),
    ("es", True),
    ("", False),
    ("Unknown", False),
])
def test_is_known_language(qtbot, card_db: CardDatabase, language: str, expected: bool):
    fill_card_database_with_json_cards(
        qtbot, card_db,
        [
            "english_Coercion",
            "english_Duress",
            "english_basic_Forest",
            "english_basic_Forest_2",
            "english_card_Future_Sight_MH1",
            "english_card_Future_Sight_MTGO_promo",
            "german_Coercion_with_faulty_translation",
            "german_basic_Forest",
            "spanish_basic_Forest",
            "german_Duress",
        ],
    )
    assert_that(
        card_db.is_known_language(language),
        is_(equal_to(expected))
    )


@pytest.fixture()
def card_db_with_cards(qtbot, card_db: CardDatabase):
    fill_card_database_with_json_cards(
        qtbot, card_db,
        [
            "english_Coercion",
            "english_Duress",
            "english_basic_Forest",
            "english_basic_Forest_2",
            "english_card_Future_Sight_MH1",
            "english_card_Future_Sight_MTGO_promo",
            "german_Coercion_with_faulty_translation",
            "german_basic_Forest",
            "spanish_basic_Forest",
            "german_Duress",
            "german_Duress_2",
            "english_Ironroot_Treefolk_1",
            "english_Ironroot_Treefolk_2",
            "english_Ironroot_Treefolk_3",
            "german_Ironroot_Treefolk_1",
            "german_Ironroot_Treefolk_2",
            "german_Ironroot_Treefolk_3",
            "oversized_card",
            "regular_english_card",
            "english_double_faced_card",
            "english_double_faced_art_series_card",
        ],
    )
    yield card_db


def generate_test_cases_for_test_translate_card_name():
    """Yields tuples with card data, target language and expected result."""
    # Same-language identity translation
    yield CardIdentificationData("en", "Forest"), "en", "Forest"
    yield CardIdentificationData("de", "Wald"), "de", "Wald"
    yield CardIdentificationData("es", "Bosque"), "es", "Bosque"
    # Guess source language
    yield CardIdentificationData(None, "Forest"), "en", "Forest"
    yield CardIdentificationData(None, "Wald"), "en", "Forest"
    yield CardIdentificationData(None, "Bosque"), "en", "Forest"
    yield CardIdentificationData(None, "Bosque"), "de", "Wald"
    yield CardIdentificationData(None, "Forest"), "de", "Wald"
    # translation with source language
    yield CardIdentificationData("de", "Wald"), "en", "Forest"
    yield CardIdentificationData("es", "Bosque"), "en", "Forest"
    # wrong source language. Returns no result
    yield CardIdentificationData("wrong_source", "Wald"), "en", None
    yield CardIdentificationData("wrong_source", "Forest"), "de", None
    yield CardIdentificationData("wrong_source", "Bosque"), "en", None
    yield CardIdentificationData("wrong_source", "Bosque"), "es", None
    # Card with name clash. Tests majority voting
    yield CardIdentificationData("de", "Zwang"), "en", "Duress"
    yield CardIdentificationData(None, "Zwang"), "en", "Duress"
    # Card with name clash. Tests using context information yields the expected name
    yield CardIdentificationData("de", "Zwang", scryfall_id="51c6ec30-afb2-41e6-895b-92e070aa86f3"), "en", "Duress"
    yield CardIdentificationData(None, "Zwang", scryfall_id="51c6ec30-afb2-41e6-895b-92e070aa86f3"), "en", "Duress"
    yield CardIdentificationData("de", "Zwang", scryfall_id="93054b80-fd1f-4200-8d33-2e826a181db0"), "en", "Coercion"
    yield CardIdentificationData(None, "Zwang", scryfall_id="93054b80-fd1f-4200-8d33-2e826a181db0"), "en", "Coercion"
    yield CardIdentificationData("de", "Zwang", "7ed"), "en", "Duress"
    yield CardIdentificationData(None, "Zwang", "7ed"), "en", "Duress"
    yield CardIdentificationData("de", "Zwang", "6ed"), "en", "Coercion"
    yield CardIdentificationData(None, "Zwang", "6ed"), "en", "Coercion"
    # Card with updated, localized name. Tests that all names can be a source name.
    yield CardIdentificationData("de", "Baumvolk der Eisenwurzler"), "en", "Ironroot Treefolk"
    yield CardIdentificationData(None, "Baumvolk der Eisenwurzler"), "en", "Ironroot Treefolk"
    yield CardIdentificationData("de", "Ehernen-Wald Baumvolk"), "en", "Ironroot Treefolk"
    yield CardIdentificationData(None, "Ehernen-Wald Baumvolk"), "en", "Ironroot Treefolk"
    yield CardIdentificationData("de", "Baumvolk des Ehernen-Waldes"), "en", "Ironroot Treefolk"
    yield CardIdentificationData(None, "Baumvolk des Ehernen-Waldes"), "en", "Ironroot Treefolk"
    # Card with updated, localized name. Tests returning the newest name without context information
    yield CardIdentificationData("en", "Ironroot Treefolk"), "de", "Baumvolk der Eisenwurzler"
    yield CardIdentificationData(None, "Ironroot Treefolk"), "de", "Baumvolk der Eisenwurzler"
    # Card with updated, localized name. Tests returning the correct name for the source set with context information
    yield CardIdentificationData("en", "Ironroot Treefolk", "5ed"), "de", "Baumvolk der Eisenwurzler"
    yield CardIdentificationData(None, "Ironroot Treefolk", "5ed"), "de", "Baumvolk der Eisenwurzler"
    yield CardIdentificationData("en", "Ironroot Treefolk", "4ed"), "de", "Ehernen-Wald Baumvolk"
    yield CardIdentificationData(None, "Ironroot Treefolk", "4ed"), "de", "Ehernen-Wald Baumvolk"
    yield CardIdentificationData("en", "Ironroot Treefolk", "3ed"), "de", "Baumvolk des Ehernen-Waldes"
    yield CardIdentificationData(None, "Ironroot Treefolk", "3ed"), "de", "Baumvolk des Ehernen-Waldes"
    yield CardIdentificationData("en", "Ironroot Treefolk", scryfall_id="6bdbba38-b4c9-4c14-b869-669b39390e4e"), "de", "Baumvolk der Eisenwurzler"
    yield CardIdentificationData(None, "Ironroot Treefolk", scryfall_id="6bdbba38-b4c9-4c14-b869-669b39390e4e"), "de", "Baumvolk der Eisenwurzler"
    yield CardIdentificationData("en", "Ironroot Treefolk", scryfall_id="c6c93c85-5263-4770-b937-704e57912478"), "de", "Ehernen-Wald Baumvolk"
    yield CardIdentificationData(None, "Ironroot Treefolk", scryfall_id="c6c93c85-5263-4770-b937-704e57912478"), "de", "Ehernen-Wald Baumvolk"
    yield CardIdentificationData("en", "Ironroot Treefolk", scryfall_id="6e6cfaae-ea9e-4c54-858e-381f8bf441a9"), "de", "Baumvolk des Ehernen-Waldes"
    yield CardIdentificationData(None, "Ironroot Treefolk", scryfall_id="6e6cfaae-ea9e-4c54-858e-381f8bf441a9"), "de", "Baumvolk des Ehernen-Waldes"
    # double-faced art series card. Same name on both sides
    yield CardIdentificationData("en", "Clearwater Pathway"), "en", "Clearwater Pathway"

    
@pytest.mark.parametrize("card_data, target_language, expected", generate_test_cases_for_test_translate_card_name())
def test_translate_card_name(
        card_db_with_cards: CardDatabase, card_data: CardIdentificationData, target_language: str, expected: OptString):
    assert_that(
        card_db_with_cards.translate_card_name(card_data, target_language),
        is_(equal_to(expected))
    )


@pytest.mark.parametrize("usage_count, expected", [
    (-1, []),
    (0, []),
    (1, [2]),
    (2, [1, 2]),
    (3, [0, 1, 2]),
    (100, [0, 1, 2]),
])
def test_cards_used_less_often_then(qtbot, card_db: CardDatabase, usage_count: int, expected: typing.List[int]):
    # Setup
    fill_card_database_with_json_cards(
        qtbot, card_db,
        [
            "english_Coercion",
            "english_Duress",
            "english_basic_Forest",
            "english_basic_Forest_2",
            "english_card_Future_Sight_MH1",
            "english_card_Future_Sight_MTGO_promo",
            "german_Coercion_with_faulty_translation",
            "german_basic_Forest",
            "spanish_basic_Forest",
            "german_Duress",
        ],
    )
    document = Document(card_db, MagicMock())
    document.apply(ActionAddCard(_get_card_from_model(card_db, "e2ef9b74-481b-424b-8e33-f0b910f66370", True), 1))
    document.store_image_usage()
    document.apply(ActionAddCard(_get_card_from_model(card_db, "ffa13d4c-6c5e-44bd-859e-38e79d47a916", True), 1))
    document.store_image_usage()
    # Test
    assert_that(
        result := card_db.cards_used_less_often_then([
            ("e2ef9b74-481b-424b-8e33-f0b910f66370", True),
            ("ffa13d4c-6c5e-44bd-859e-38e79d47a916", True),
            ("cd4cf73d-a408-48f1-9931-54707553c5d5", True),
        ], usage_count),
        contains_exactly(*expected),
        f"Result: {result}"
    )


def _get_card_from_model(card_db: CardDatabase, scryfall_id: str, is_front: bool):
    card = card_db.get_card_with_scryfall_id(scryfall_id, is_front)
    assert_that(card, has_properties({
        "scryfall_id": equal_to(scryfall_id),
        "is_front": equal_to(is_front),
    }), "Wrong card returned")
    return card


@pytest.mark.parametrize("json_name, scryfall_id, expected", [
    ("regular_english_card", "0000579f-7b35-4ed3-b44c-db2a538066fe", False),
    ("oversized_card", "650722b4-d72b-4745-a1a5-00a34836282b", True)
])
def test_card_is_oversized(qtbot, card_db: CardDatabase, json_name: str, scryfall_id: str, expected: bool):
    """
    Tests that all methods creating Card instances correctly set is_oversized attribute.
    """
    fill_card_database_with_json_card(qtbot, card_db, json_name)
    assert_that(
        card_db.get_card_with_scryfall_id(scryfall_id, True),
        has_property("is_oversized", is_(expected))
    )


def generate_test_cases_for_test_get_cards_from_data():
    yield CardIdentificationData("en", scryfall_id="0000579f-7b35-4ed3-b44c-db2a538066fe"), [
        Card('Fury Sliver', MTGSet('tsp', 'Time Spiral'), '157', 'en', '0000579f-7b35-4ed3-b44c-db2a538066fe', True, '44623693-51d6-49ad-8cd7-140505caf02f', 'https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979', True, False, 0, None),
    ]
    yield CardIdentificationData("en", scryfall_id="650722b4-d72b-4745-a1a5-00a34836282b"), [
        Card("Atraxa, Praetors' Voice", MTGSet('oc16', 'Commander 2016 Oversized'), '28', 'en', '650722b4-d72b-4745-a1a5-00a34836282b', True, '7e6b9b59-cd68-4e3c-827b-38833c92d6eb', 'https://c1.scryfall.com/file/scryfall-cards/png/front/6/5/650722b4-d72b-4745-a1a5-00a34836282b.png?1561757296', True, True, 0, None),
    ]
    yield CardIdentificationData(scryfall_id="0000579f-7b35-4ed3-b44c-db2a538066fe"), [
        Card('Fury Sliver', MTGSet('tsp', 'Time Spiral'), '157', 'en', '0000579f-7b35-4ed3-b44c-db2a538066fe', True, '44623693-51d6-49ad-8cd7-140505caf02f', 'https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979', True, False, 0, None),
    ]
    yield CardIdentificationData(scryfall_id="650722b4-d72b-4745-a1a5-00a34836282b"), [
        Card("Atraxa, Praetors' Voice", MTGSet('oc16', 'Commander 2016 Oversized'), '28', 'en', '650722b4-d72b-4745-a1a5-00a34836282b', True, '7e6b9b59-cd68-4e3c-827b-38833c92d6eb', 'https://c1.scryfall.com/file/scryfall-cards/png/front/6/5/650722b4-d72b-4745-a1a5-00a34836282b.png?1561757296', True, True, 0, None),
    ]
    # Tests effect of is_front on double-faced cards
    yield CardIdentificationData(scryfall_id="b3b87bfc-f97f-4734-94f6-e3e2f335fc4d"), [
        Card('Growing Rites of Itlimoc', MTGSet('xln', 'Ixalan'), '191', 'en', 'b3b87bfc-f97f-4734-94f6-e3e2f335fc4d', True, 'ea9c459a-6047-43aa-968f-a582be4000e8', 'https://c1.scryfall.com/file/scryfall-cards/png/front/b/3/b3b87bfc-f97f-4734-94f6-e3e2f335fc4d.png?1562562539', True, False, 0, None),
        Card('Itlimoc, Cradle of the Sun', MTGSet('xln', 'Ixalan'), '191', 'en', 'b3b87bfc-f97f-4734-94f6-e3e2f335fc4d', False, 'ea9c459a-6047-43aa-968f-a582be4000e8', 'https://c1.scryfall.com/file/scryfall-cards/png/back/b/3/b3b87bfc-f97f-4734-94f6-e3e2f335fc4d.png?1562562539', True, False, 1, None),
    ]
    yield CardIdentificationData(scryfall_id="b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", is_front=True), [
        Card('Growing Rites of Itlimoc', MTGSet('xln', 'Ixalan'), '191', 'en', 'b3b87bfc-f97f-4734-94f6-e3e2f335fc4d', True, 'ea9c459a-6047-43aa-968f-a582be4000e8', 'https://c1.scryfall.com/file/scryfall-cards/png/front/b/3/b3b87bfc-f97f-4734-94f6-e3e2f335fc4d.png?1562562539', True, False, 0, None),
    ]
    yield CardIdentificationData(scryfall_id="b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", is_front=False), [
        Card('Itlimoc, Cradle of the Sun', MTGSet('xln', 'Ixalan'), '191', 'en', 'b3b87bfc-f97f-4734-94f6-e3e2f335fc4d', False, 'ea9c459a-6047-43aa-968f-a582be4000e8', 'https://c1.scryfall.com/file/scryfall-cards/png/back/b/3/b3b87bfc-f97f-4734-94f6-e3e2f335fc4d.png?1562562539', True, False, 1, None),
    ]
    # Tests identification based on oracle_id alone. Also tests highres_image boolean
    yield CardIdentificationData(oracle_id="b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6"), [
        Card('Forest', MTGSet('anb', 'Arena Beginner Set'), '112', 'en', '7ef83f4c-d3ff-4905-a16d-f2bae673a5b2', True, 'b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6', 'https://c1.scryfall.com/file/scryfall-cards/png/front/7/e/7ef83f4c-d3ff-4905-a16d-f2bae673a5b2.png?1597375433', True, False, 0, None),
        Card('Forest', MTGSet('znr', 'Zendikar Rising'), '280', 'en', 'e2ef9b74-481b-424b-8e33-f0b910f66370', True, 'b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6', 'https://c1.scryfall.com/file/scryfall-cards/png/front/e/2/e2ef9b74-481b-424b-8e33-f0b910f66370.png?1604202251', True, False, 0, None),
        Card('Wald', MTGSet('znr', 'Zendikar Rising'), '384', 'de', 'cd4cf73d-a408-48f1-9931-54707553c5d5', True, 'b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6', 'https://c1.scryfall.com/file/scryfall-cards/png/front/c/d/cd4cf73d-a408-48f1-9931-54707553c5d5.png?1602136077', False, False, 0, None),
        Card('Bosque', MTGSet('znr', 'Zendikar Rising'), '280', 'es', 'ffa13d4c-6c5e-44bd-859e-38e79d47a916', True, 'b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6', 'https://c1.scryfall.com/file/scryfall-cards/png/front/f/f/ffa13d4c-6c5e-44bd-859e-38e79d47a916.png?1615068408', False, False, 0, None),
    ]
    # Tests other attribute combinations
    yield CardIdentificationData(name="Bosque"), [
        Card('Bosque', MTGSet('znr', 'Zendikar Rising'), '280', 'es', 'ffa13d4c-6c5e-44bd-859e-38e79d47a916', True, 'b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6', 'https://c1.scryfall.com/file/scryfall-cards/png/front/f/f/ffa13d4c-6c5e-44bd-859e-38e79d47a916.png?1615068408', False, False, 0, None),
    ]
    yield CardIdentificationData(set_code="anb"), [
        Card('Forest', MTGSet('anb', 'Arena Beginner Set'), '112', 'en', '7ef83f4c-d3ff-4905-a16d-f2bae673a5b2', True, 'b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6', 'https://c1.scryfall.com/file/scryfall-cards/png/front/7/e/7ef83f4c-d3ff-4905-a16d-f2bae673a5b2.png?1597375433', True, False, 0, None),
    ]
    yield CardIdentificationData("de", set_code="znr"), [
        Card('Wald', MTGSet('znr', 'Zendikar Rising'), '384', 'de', 'cd4cf73d-a408-48f1-9931-54707553c5d5', True, 'b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6', 'https://c1.scryfall.com/file/scryfall-cards/png/front/c/d/cd4cf73d-a408-48f1-9931-54707553c5d5.png?1602136077', False, False, 0, None),
    ]
    yield CardIdentificationData(set_code="znr", collector_number="280"), [
        Card('Forest', MTGSet('znr', 'Zendikar Rising'), '280', 'en', 'e2ef9b74-481b-424b-8e33-f0b910f66370', True, 'b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6', 'https://c1.scryfall.com/file/scryfall-cards/png/front/e/2/e2ef9b74-481b-424b-8e33-f0b910f66370.png?1604202251', True, False, 0, None),
        Card('Bosque', MTGSet('znr', 'Zendikar Rising'), '280', 'es', 'ffa13d4c-6c5e-44bd-859e-38e79d47a916', True, 'b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6', 'https://c1.scryfall.com/file/scryfall-cards/png/front/f/f/ffa13d4c-6c5e-44bd-859e-38e79d47a916.png?1615068408', False, False, 0, None),
    ]
    # Empty result set
    yield CardIdentificationData(scryfall_id="invalid"), []


@pytest.mark.parametrize("card_data, expected", generate_test_cases_for_test_get_cards_from_data())
def test_get_cards_from_data(
        card_db_with_cards: CardDatabase,
        card_data: CardIdentificationData, expected: CardList):
    cards = card_db_with_cards.get_cards_from_data(card_data)
    for card in cards:
        assert_that(card, matches_type_annotation())
    assert_that(
        cards,
        contains_inanyorder(
            *map(is_dataclass_equal_to, expected)
        )
    )


def generate_test_cases_for_test_get_card_with_scryfall_id() -> \
        typing.Generator[typing.Tuple[CardIdentificationData, typing.Optional[Card]], None, None]:
    # Regular card
    yield CardIdentificationData(scryfall_id="0000579f-7b35-4ed3-b44c-db2a538066fe", is_front=True), \
        Card('Fury Sliver', MTGSet('tsp', 'Time Spiral'), '157', 'en', '0000579f-7b35-4ed3-b44c-db2a538066fe', True, '44623693-51d6-49ad-8cd7-140505caf02f', 'https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979', True, False, 0, None)
    # Back side of regular card returns None
    yield CardIdentificationData(scryfall_id="0000579f-7b35-4ed3-b44c-db2a538066fe", is_front=False), \
        None
    # Unknown scryfall_id returns None
    yield CardIdentificationData(scryfall_id="ueueueue-abcd-1234-5678-abcdefabcdef", is_front=True), \
        None
    # Oversized card
    yield CardIdentificationData(scryfall_id="650722b4-d72b-4745-a1a5-00a34836282b", is_front=True), \
        Card("Atraxa, Praetors' Voice", MTGSet('oc16', 'Commander 2016 Oversized'), '28', 'en', '650722b4-d72b-4745-a1a5-00a34836282b', True, '7e6b9b59-cd68-4e3c-827b-38833c92d6eb', 'https://c1.scryfall.com/file/scryfall-cards/png/front/6/5/650722b4-d72b-4745-a1a5-00a34836282b.png?1561757296', True, True, 0, None)
    # German Forest
    yield CardIdentificationData(scryfall_id="cd4cf73d-a408-48f1-9931-54707553c5d5", is_front=True), \
        Card('Wald', MTGSet('znr', 'Zendikar Rising'), '384', 'de', 'cd4cf73d-a408-48f1-9931-54707553c5d5', True, 'b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6', 'https://c1.scryfall.com/file/scryfall-cards/png/front/c/d/cd4cf73d-a408-48f1-9931-54707553c5d5.png?1602136077', False, False, 0, None),
    # Spanish Forest
    yield CardIdentificationData(scryfall_id="ffa13d4c-6c5e-44bd-859e-38e79d47a916", is_front=True), \
        Card('Bosque', MTGSet('znr', 'Zendikar Rising'), '280', 'es', 'ffa13d4c-6c5e-44bd-859e-38e79d47a916', True, 'b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6', 'https://c1.scryfall.com/file/scryfall-cards/png/front/f/f/ffa13d4c-6c5e-44bd-859e-38e79d47a916.png?1615068408', False, False, 0, None),
    # Double-faced with high-res image
    yield CardIdentificationData(scryfall_id="b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", is_front=True), \
        Card('Growing Rites of Itlimoc', MTGSet('xln', 'Ixalan'), '191', 'en', 'b3b87bfc-f97f-4734-94f6-e3e2f335fc4d', True, 'ea9c459a-6047-43aa-968f-a582be4000e8', 'https://c1.scryfall.com/file/scryfall-cards/png/front/b/3/b3b87bfc-f97f-4734-94f6-e3e2f335fc4d.png?1562562539', True, False, 0, None),
    yield CardIdentificationData(scryfall_id="b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", is_front=False), \
        Card('Itlimoc, Cradle of the Sun', MTGSet('xln', 'Ixalan'), '191', 'en', 'b3b87bfc-f97f-4734-94f6-e3e2f335fc4d', False, 'ea9c459a-6047-43aa-968f-a582be4000e8', 'https://c1.scryfall.com/file/scryfall-cards/png/back/b/3/b3b87bfc-f97f-4734-94f6-e3e2f335fc4d.png?1562562539', True, False, 1, None),
    # Art series card
    yield CardIdentificationData(scryfall_id="002ad179-ddf4-4f48-9504-cfa02e11a52e", is_front=True), \
        Card('Clearwater Pathway', MTGSet('aznr', 'Zendikar Rising Art Series'), '25', 'en', '002ad179-ddf4-4f48-9504-cfa02e11a52e', True, 'a755add5-04ec-4e37-9eb6-152d52cfa46d', 'https://cards.scryfall.io/png/front/0/0/002ad179-ddf4-4f48-9504-cfa02e11a52e.png?1678735457', True, False, 0, None),
    yield CardIdentificationData(scryfall_id="002ad179-ddf4-4f48-9504-cfa02e11a52e", is_front=False), \
        Card('Clearwater Pathway', MTGSet('aznr', 'Zendikar Rising Art Series'), '25', 'en', '002ad179-ddf4-4f48-9504-cfa02e11a52e', False, 'a755add5-04ec-4e37-9eb6-152d52cfa46d', 'https://cards.scryfall.io/png/back/0/0/002ad179-ddf4-4f48-9504-cfa02e11a52e.png?1678735457', True, False, 1, None),
    # Digital card
    yield CardIdentificationData(scryfall_id="7ef83f4c-d3ff-4905-a16d-f2bae673a5b2", is_front=True), \
        Card('Forest', MTGSet('anb', 'Arena Beginner Set'), '112', 'en', '7ef83f4c-d3ff-4905-a16d-f2bae673a5b2', True, 'b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6', 'https://c1.scryfall.com/file/scryfall-cards/png/front/7/e/7ef83f4c-d3ff-4905-a16d-f2bae673a5b2.png?1597375433', True, False, 0, None),


@pytest.mark.parametrize("card_data, expected", generate_test_cases_for_test_get_card_with_scryfall_id())
def test_get_card_with_scryfall_id(
        card_db_with_cards: CardDatabase, card_data: CardIdentificationData, expected: typing.Optional[Card]):
    assert_that(
        card_db_with_cards.get_card_with_scryfall_id(card_data.scryfall_id, card_data.is_front),
        is_(any_of(
            all_of(
                none(),
                instance_of(type(expected))  # None if and only if expected is None
            ),
            all_of(
                is_(instance_of(Card)),
                matches_type_annotation(),
                has_properties({
                    # Verifies that the expected card matches the given card identification data.
                    # Not strictly required, but ensures that the test data is consistent
                    "scryfall_id": card_data.scryfall_id,
                    "is_front": card_data.is_front,
                }),
                is_dataclass_equal_to(expected),
            )))
    )


@pytest.mark.parametrize("language", ["en", None])
@pytest.mark.parametrize("card_count_data", [
    [("7ef83f4c-d3ff-4905-a16d-f2bae673a5b2", 2), ("e2ef9b74-481b-424b-8e33-f0b910f66370", 1)],
    [("7ef83f4c-d3ff-4905-a16d-f2bae673a5b2", 1), ("e2ef9b74-481b-424b-8e33-f0b910f66370", 2)],
])
def test_get_cards_from_data_order_by_print_count_enabled(
        qtbot, card_db: CardDatabase, language: OptString, card_count_data):
    fill_card_database_with_json_cards(qtbot, card_db, ["english_basic_Forest", "english_basic_Forest_2"])
    card_db.db.executemany(
        "INSERT INTO LastImageUseTimestamps (scryfall_id, is_front, usage_count) VALUES (?, 1, ?)",
        card_count_data
    )
    card_data = CardIdentificationData(language, name="Forest")
    cards = card_db.get_cards_from_data(card_data, order_by_print_count=True)
    assert_that(
        cards,
        contains_exactly(
            has_property("scryfall_id", equal_to(
                card_count_data[0 if card_count_data[0][1] > card_count_data[1][1] else 1][0]
            )),
            has_property("scryfall_id", equal_to(
                card_count_data[1 if card_count_data[0][1] > card_count_data[1][1] else 0][0]
            )),
        )
    )


def test_get_replacement_card(
        qtbot, card_db: CardDatabase):
    fill_card_database_with_json_cards(qtbot, card_db, ["english_basic_Forest", "german_basic_Forest"])
    card_db.db.executemany(
        textwrap.dedent("""\
            INSERT INTO RemovedPrintings (scryfall_id, language, oracle_id)
                VALUES (?, ?, ?)
            """), [
            ("english-id", "en", "b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6"),
            ("german-id", "de", "b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc"),
            ("non-english-id", "invalid", "b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6"),
        ])
    card_db.get_replacement_card_for_unknown_printing(CardIdentificationData(scryfall_id="english-id", language="en"))


def generate_test_cases_for_test__translate_card():
    # Regular card
    yield CardIdentificationData(scryfall_id="0000579f-7b35-4ed3-b44c-db2a538066fe", is_front=True), \
        Card('Fury Sliver', MTGSet('tsp', 'Time Spiral'), '157', 'en', '0000579f-7b35-4ed3-b44c-db2a538066fe', True, '44623693-51d6-49ad-8cd7-140505caf02f', 'https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979', True, False, 0, None)
    # Oversized card
    yield CardIdentificationData(scryfall_id="650722b4-d72b-4745-a1a5-00a34836282b", is_front=True), \
        Card("Atraxa, Praetors' Voice", MTGSet('oc16', 'Commander 2016 Oversized'), '28', 'en', '650722b4-d72b-4745-a1a5-00a34836282b', True, '7e6b9b59-cd68-4e3c-827b-38833c92d6eb', 'https://c1.scryfall.com/file/scryfall-cards/png/front/6/5/650722b4-d72b-4745-a1a5-00a34836282b.png?1561757296', True, True, 0, None)
    # Translate Forest to German. Also tests is_highres==False
    yield CardIdentificationData(scryfall_id="7ef83f4c-d3ff-4905-a16d-f2bae673a5b2", is_front=True), \
        Card('Wald', MTGSet('znr', 'Zendikar Rising'), '384', 'de', 'cd4cf73d-a408-48f1-9931-54707553c5d5', True, 'b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6', 'https://c1.scryfall.com/file/scryfall-cards/png/front/c/d/cd4cf73d-a408-48f1-9931-54707553c5d5.png?1602136077', False, False, 0, None),
    # Translate Forest to Spanish. Also tests is_highres==False
    yield CardIdentificationData(scryfall_id="7ef83f4c-d3ff-4905-a16d-f2bae673a5b2", is_front=True), \
        Card('Bosque', MTGSet('znr', 'Zendikar Rising'), '280', 'es', 'ffa13d4c-6c5e-44bd-859e-38e79d47a916', True, 'b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6', 'https://c1.scryfall.com/file/scryfall-cards/png/front/f/f/ffa13d4c-6c5e-44bd-859e-38e79d47a916.png?1615068408', False, False, 0, None),
    # Translate German Forest to Spanish
    yield CardIdentificationData(scryfall_id="cd4cf73d-a408-48f1-9931-54707553c5d5", is_front=True), \
        Card('Bosque', MTGSet('znr', 'Zendikar Rising'), '280', 'es', 'ffa13d4c-6c5e-44bd-859e-38e79d47a916', True, 'b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6', 'https://c1.scryfall.com/file/scryfall-cards/png/front/f/f/ffa13d4c-6c5e-44bd-859e-38e79d47a916.png?1615068408', False, False, 0, None),
    # Double-faced with high-res image
    yield CardIdentificationData(scryfall_id="b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", is_front=True), \
        Card('Growing Rites of Itlimoc', MTGSet('xln', 'Ixalan'), '191', 'en', 'b3b87bfc-f97f-4734-94f6-e3e2f335fc4d', True, 'ea9c459a-6047-43aa-968f-a582be4000e8', 'https://c1.scryfall.com/file/scryfall-cards/png/front/b/3/b3b87bfc-f97f-4734-94f6-e3e2f335fc4d.png?1562562539', True, False, 0, None),
    yield CardIdentificationData(scryfall_id="b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", is_front=False), \
        Card('Itlimoc, Cradle of the Sun', MTGSet('xln', 'Ixalan'), '191', 'en', 'b3b87bfc-f97f-4734-94f6-e3e2f335fc4d', False, 'ea9c459a-6047-43aa-968f-a582be4000e8', 'https://c1.scryfall.com/file/scryfall-cards/png/back/b/3/b3b87bfc-f97f-4734-94f6-e3e2f335fc4d.png?1562562539', True, False, 1, None),
    # Art series card
    yield CardIdentificationData(scryfall_id="002ad179-ddf4-4f48-9504-cfa02e11a52e", is_front=True), \
        Card('Clearwater Pathway', MTGSet('aznr', 'Zendikar Rising Art Series'), '25', 'en', '002ad179-ddf4-4f48-9504-cfa02e11a52e', True, 'a755add5-04ec-4e37-9eb6-152d52cfa46d', 'https://cards.scryfall.io/png/front/0/0/002ad179-ddf4-4f48-9504-cfa02e11a52e.png?1678735457', True, False, 0, None),
    yield CardIdentificationData(scryfall_id="002ad179-ddf4-4f48-9504-cfa02e11a52e", is_front=False), \
        Card('Clearwater Pathway', MTGSet('aznr', 'Zendikar Rising Art Series'), '25', 'en', '002ad179-ddf4-4f48-9504-cfa02e11a52e', False, 'a755add5-04ec-4e37-9eb6-152d52cfa46d', 'https://cards.scryfall.io/png/back/0/0/002ad179-ddf4-4f48-9504-cfa02e11a52e.png?1678735457', True, False, 1, None),


# Re-use the test cases for test_find_all_translated_printings. Both should return the same data
@pytest.mark.parametrize("card_data, expected", generate_test_cases_for_test__translate_card())
def test__translate_card(card_db_with_cards: CardDatabase, card_data: CardIdentificationData, expected: Card):
    is_front = card_data.is_front is None or card_data.is_front
    to_translate = card_db_with_cards.get_card_with_scryfall_id(card_data.scryfall_id, is_front)
    # Use the private method to skip the internal shortcut in translate_card()
    # that skips requested same-language translations.
    assert_that(
        card_db_with_cards._translate_card(to_translate, expected.language), all_of(
            is_(Card),
            is_not(same_instance(to_translate)),  # No shortcut taken, is actually a new instance
            matches_type_annotation(),
            is_dataclass_equal_to(expected),
        )
    )


def generate_test_cases_for_test_get_opposing_face() -> \
        typing.Generator[typing.Tuple[CardIdentificationData, typing.Optional[Card]], None, None]:
    # The back side of a regular card does not exist, Expect None
    yield CardIdentificationData(scryfall_id="0000579f-7b35-4ed3-b44c-db2a538066fe", is_front=True), \
        None
    # The other side of a non-existing back side of a regular card returns the existing front
    yield CardIdentificationData(scryfall_id="0000579f-7b35-4ed3-b44c-db2a538066fe", is_front=False), \
        Card('Fury Sliver', MTGSet('tsp', 'Time Spiral'), '157', 'en', '0000579f-7b35-4ed3-b44c-db2a538066fe', True, '44623693-51d6-49ad-8cd7-140505caf02f', 'https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979', True, False, 0, None)
    # Unknown scryfall_id returns None
    yield CardIdentificationData(scryfall_id="ueueueue-abcd-1234-5678-abcdefabcdef", is_front=True), \
        None
    yield CardIdentificationData(scryfall_id="ueueueue-abcd-1234-5678-abcdefabcdef", is_front=False), \
        None
    # Double-faced with high-res image
    yield CardIdentificationData(scryfall_id="b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", is_front=True), \
        Card('Itlimoc, Cradle of the Sun', MTGSet('xln', 'Ixalan'), '191', 'en', 'b3b87bfc-f97f-4734-94f6-e3e2f335fc4d', False, 'ea9c459a-6047-43aa-968f-a582be4000e8', 'https://c1.scryfall.com/file/scryfall-cards/png/back/b/3/b3b87bfc-f97f-4734-94f6-e3e2f335fc4d.png?1562562539', True, False, 1, None),
    yield CardIdentificationData(scryfall_id="b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", is_front=False), \
        Card('Growing Rites of Itlimoc', MTGSet('xln', 'Ixalan'), '191', 'en', 'b3b87bfc-f97f-4734-94f6-e3e2f335fc4d', True, 'ea9c459a-6047-43aa-968f-a582be4000e8', 'https://c1.scryfall.com/file/scryfall-cards/png/front/b/3/b3b87bfc-f97f-4734-94f6-e3e2f335fc4d.png?1562562539', True, False, 0, None),
    # Art series card
    yield CardIdentificationData(scryfall_id="002ad179-ddf4-4f48-9504-cfa02e11a52e", is_front=True), \
        Card('Clearwater Pathway', MTGSet('aznr', 'Zendikar Rising Art Series'), '25', 'en', '002ad179-ddf4-4f48-9504-cfa02e11a52e', False, 'a755add5-04ec-4e37-9eb6-152d52cfa46d', 'https://cards.scryfall.io/png/back/0/0/002ad179-ddf4-4f48-9504-cfa02e11a52e.png?1678735457', True, False, 1, None),
    yield CardIdentificationData(scryfall_id="002ad179-ddf4-4f48-9504-cfa02e11a52e", is_front=False), \
        Card('Clearwater Pathway', MTGSet('aznr', 'Zendikar Rising Art Series'), '25', 'en', '002ad179-ddf4-4f48-9504-cfa02e11a52e', True, 'a755add5-04ec-4e37-9eb6-152d52cfa46d', 'https://cards.scryfall.io/png/front/0/0/002ad179-ddf4-4f48-9504-cfa02e11a52e.png?1678735457', True, False, 0, None),


@pytest.mark.parametrize("card_data, expected", generate_test_cases_for_test_get_opposing_face())
def test_get_opposing_face(
        card_db_with_cards: CardDatabase, card_data: CardIdentificationData, expected: typing.Optional[Card]):
    assert_that(
        card_db_with_cards.get_opposing_face(card_data),
        is_(any_of(
            all_of(
                none(),
                instance_of(type(expected))  # None if and only if expected is None
            ),
            all_of(
                is_(instance_of(Card)),
                matches_type_annotation(),
                has_properties({
                    # Verifies that the expected card matches the given card identification data.
                    # Not strictly required, but ensures that the test data is consistent
                    "scryfall_id": card_data.scryfall_id,
                    "is_front": not card_data.is_front,  # Negation here
                }),
                is_dataclass_equal_to(expected),
            )))
    )


def test_allow_updating_card_data_on_empty_database_returns_true(card_db: CardDatabase):
    assert_that(card_db.allow_updating_card_data(), is_(True))


def test_allow_updating_card_data_on_freshly_populated_database_returns_false(qtbot, card_db: CardDatabase):
    fill_card_database_with_json_card(qtbot, card_db, "regular_english_card")
    assert_that(card_db.allow_updating_card_data(), is_(False))


@pytest.mark.parametrize("delta_days", [-2, -1, 0, 1, 2])
def test_allow_updating_card_data_on_stale_populated_database_returns_true(
        qtbot, card_db: CardDatabase, delta_days: int):
    fill_card_database_with_json_card(qtbot, card_db, "regular_english_card")
    today = datetime.date.today()
    now = today + MINIMUM_REFRESH_DELAY + datetime.timedelta(delta_days)
    with unittest.mock.patch("mtg_proxy_printer.model.carddb.datetime.date") as mock_date:
        mock_date.today.return_value = now
        assert_that(datetime.date.today(), is_not(today))
        assert_that(
            card_db.allow_updating_card_data(),
            is_(delta_days >= 0)
        )


def test_get_total_cards_in_last_update(qtbot, card_db: CardDatabase):
    card_data = ["regular_english_card"]
    fill_card_database_with_json_cards(qtbot, card_db, card_data)
    assert_that(card_db.get_total_cards_in_last_update(), is_(len(card_data)))
    card_data.append("english_basic_Forest")
    fill_card_database_with_json_cards(qtbot, card_db, card_data)
    assert_that(card_db.get_total_cards_in_last_update(), is_(len(card_data)))


def test_is_removed_printing_with_removed_printing_returns_true(qtbot, card_db: CardDatabase):
    fill_card_database_with_json_card(qtbot, card_db, "missing_image_double_faced_card")
    assert_that(
        card_db.is_removed_printing("b120e3c2-21b1-43e3-b685-9cf62bd7aa07"),
        is_(True)
    )


@pytest.mark.parametrize("filter_value", [True, False])
def test_is_removed_printing_with_included_printing_returns_false(qtbot, card_db: CardDatabase, filter_value: bool):
    fill_card_database_with_json_card(qtbot, card_db, "oversized_card", {"hide-oversized-cards": str(filter_value)})
    assert_that(
        card_db.is_removed_printing("650722b4-d72b-4745-a1a5-00a34836282b"),
        is_(filter_value)
    )


@pytest.mark.parametrize("settings_key", mtg_proxy_printer.settings.settings["card-filter"].keys())
def test_filters_in_db_differ_from_settings_with_changed_settings_returns_true(
        card_db: CardDatabase, settings_key: str):
    section = mtg_proxy_printer.settings.settings["card-filter"]
    settings_to_use = {filter_name: "False" for filter_name in section.keys()}
    settings_to_use[settings_key] = str(not section.getboolean(settings_key))
    with unittest.mock.patch.dict(section, settings_to_use):
        assert_that(
            card_db._filters_in_db_differ_from_settings(section),
            is_(True)
        )


def test_filters_in_db_differ_from_settings_with_unchanged_settings_returns_false(card_db: CardDatabase):
    section = mtg_proxy_printer.settings.settings["card-filter"]
    settings_to_use = {filter_name: "False" for filter_name in section.keys()}
    with unittest.mock.patch.dict(section, settings_to_use):
        assert_that(
            card_db._filters_in_db_differ_from_settings(section),
            is_(False)
        )


def test__remove_old_printing_filters_with_unaltered_settings_does_nothing(card_db: CardDatabase):
    query = "SELECT * FROM DisplayFilters ORDER BY filter_id ASC"
    section = mtg_proxy_printer.settings.settings["card-filter"]
    old_settings = card_db.db.execute(query).fetchall()
    assert_that(
        card_db._remove_old_printing_filters(section),
        is_(False)
    )
    new_settings = card_db.db.execute(query).fetchall()
    assert_that(
        new_settings,
        contains_exactly(*old_settings)
    )


def test__remove_old_printing_filters_with_removed_settings_removes_database_rows(card_db: CardDatabase):
    query = "SELECT * FROM DisplayFilters ORDER BY filter_id ASC"
    section = mtg_proxy_printer.settings.settings["card-filter"]
    with unittest.mock.patch.dict(section, {}, clear=True):
        assert_that(
            card_db._remove_old_printing_filters(section),
            is_(True)
        )
    new_settings = card_db.db.execute(query).fetchall()
    assert_that(
        new_settings,
        is_(empty())
    )


@pytest.mark.parametrize("settings_key", mtg_proxy_printer.settings.settings["card-filter"].keys())
def test_store_current_printing_filters_updates_value_in_database(card_db: CardDatabase, settings_key: str):
    section = mtg_proxy_printer.settings.settings["card-filter"]
    settings_to_use = {filter_name: "False" for filter_name in section.keys()}
    settings_to_use[settings_key] = str(not section.getboolean(settings_key))
    with unittest.mock.patch.dict(section, settings_to_use):
        assert_that(card_db._filters_in_db_differ_from_settings(section), is_(True))
        card_db.store_current_printing_filters(True)
        assert_that(card_db._filters_in_db_differ_from_settings(section), is_(False))


@pytest.mark.parametrize("order_printings", [True, False])
@pytest.mark.parametrize("cards_to_import, filter_name, card_data, expected_replacement", [
    (["missing_image_double_faced_card", "english_double_faced_card_2"], "any", CardIdentificationData("en", scryfall_id="b120e3c2-21b1-43e3-b685-9cf62bd7aa07", is_front=True), "d9131fc3-018a-4975-8795-47be3956160d"),
    (["missing_image_double_faced_card", "english_double_faced_card_2"], "any", CardIdentificationData(scryfall_id="b120e3c2-21b1-43e3-b685-9cf62bd7aa07", is_front=True), "d9131fc3-018a-4975-8795-47be3956160d"),
    (["german_Back_to_Basics", "english_Back_to_Basics"], "hide-cards-without-images", CardIdentificationData("de", scryfall_id="97b84e7d-258f-46dc-baef-4b1eb6f28d4d", is_front=True), "0600d6c2-0f72-4e79-a55d-1f06dffa48c2"),
    (["german_Back_to_Basics", "english_Back_to_Basics"], "hide-cards-without-images", CardIdentificationData(scryfall_id="97b84e7d-258f-46dc-baef-4b1eb6f28d4d", is_front=True), "0600d6c2-0f72-4e79-a55d-1f06dffa48c2"),
])
def test_get_replacement_card_for_unknown_printing(
        qtbot, card_db: CardDatabase, cards_to_import, filter_name: str, card_data: CardIdentificationData,
        expected_replacement: str, order_printings: bool):
    fill_card_database_with_json_cards(qtbot, card_db, cards_to_import, {filter_name: "True"})

    assert_that(
        card_db.get_replacement_card_for_unknown_printing(card_data, order_by_print_count=order_printings),
        all_of(
            not_(empty()),
            contains_exactly(
                has_property("scryfall_id", equal_to(expected_replacement)),
            )
        )
    )


@pytest.mark.parametrize("cards_to_import, filter_name, printing, expected", [
    (["missing_image_double_faced_card", "english_double_faced_card_2"], "any", "b120e3c2-21b1-43e3-b685-9cf62bd7aa07", True),
    (["missing_image_double_faced_card", "english_double_faced_card_2"], "any", "d9131fc3-018a-4975-8795-47be3956160d", False),
    (["german_Back_to_Basics", "english_Back_to_Basics"], "hide-cards-without-images", "97b84e7d-258f-46dc-baef-4b1eb6f28d4d", True),
    (["german_Back_to_Basics", "english_Back_to_Basics"], "hide-cards-without-images", "0600d6c2-0f72-4e79-a55d-1f06dffa48c2", False),
])
def test_is_removed_printing(
        qtbot, card_db: CardDatabase, cards_to_import, filter_name: str, printing: str, expected: bool):
    fill_card_database_with_json_cards(qtbot, card_db, cards_to_import, {filter_name: "True"})
    assert_that(
        card_db.is_removed_printing(printing),
        is_(expected)
    )


@pytest.mark.timeout(1)
@pytest.mark.parametrize("include_wastes, include_snow_basics, expected_oracle_ids", [
    (False, False, ["b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6"]),
    (True, False, ["b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6", "05d24b0c-904a-46b6-b42a-96a4d91a0dd4"]),
    (False, True, ["b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6", "5f0d3be8-e63e-4ade-ae58-6b0c14f2ce6d"]),
    (True, True, ["b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6", "05d24b0c-904a-46b6-b42a-96a4d91a0dd4", "5f0d3be8-e63e-4ade-ae58-6b0c14f2ce6d"]),
])
def test_get_basic_land_oracle_ids(
        qtbot, card_db: CardDatabase,
        include_wastes: bool, include_snow_basics: bool, expected_oracle_ids: typing.List[str]):
    fill_card_database_with_json_cards(
        qtbot, card_db, ["english_basic_Forest", "english_basic_Wastes", "english_basic_Snow_Forest"])
    assert_that(
        card_db.get_basic_land_oracle_ids(include_wastes, include_snow_basics),
        contains_inanyorder(*expected_oracle_ids)
    )
