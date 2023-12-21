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

import datetime
import itertools
from pathlib import Path
import textwrap
import typing
import unittest.mock
from unittest.mock import MagicMock

from hamcrest import *
import pytest

from mtg_proxy_printer.model.carddb import CardDatabase, CardIdentificationData, MINIMUM_REFRESH_DELAY, CardList, Card
from mtg_proxy_printer.model.imagedb import CacheContent
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.print_count_updater import PrintCountUpdater
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard

from .helpers import assert_model_is_empty, fill_card_database_with_json_card, \
    fill_card_database_with_json_cards, is_dataclass_equal_to, matches_type_annotation
from .test_card_info_downloader import TestCaseData

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


@pytest.fixture
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
    return card_db


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
    (1, [2]),
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
    document.apply(ActionAddCard(
        _get_card_from_model(card_db, "e2ef9b74-481b-424b-8e33-f0b910f66370", True), 1))
    PrintCountUpdater(document, card_db.db).run()
    document.apply(ActionAddCard(
        _get_card_from_model(card_db, "ffa13d4c-6c5e-44bd-859e-38e79d47a916", True), 1))
    PrintCountUpdater(document, card_db.db).run()
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
    case = TestCaseData("regular_english_card")
    yield CardIdentificationData(case.language, scryfall_id=case.scryfall_id), [case.as_card(),]
    yield CardIdentificationData(scryfall_id=case.scryfall_id), [case.as_card(),]

    case = TestCaseData("oversized_card")
    yield CardIdentificationData(case.language, scryfall_id=case.scryfall_id), [case.as_card(),]
    yield CardIdentificationData(scryfall_id=case.scryfall_id), [case.as_card(),]


    # Tests effect of is_front on double-faced cards
    case = TestCaseData("english_double_faced_card")
    yield CardIdentificationData(scryfall_id=case.scryfall_id), [
        case.as_card(1),
        case.as_card(2),
    ]
    yield CardIdentificationData(scryfall_id=case.scryfall_id, is_front=True), [
        case.as_card(1),
    ]
    yield CardIdentificationData(scryfall_id=case.scryfall_id, is_front=False), [
        case.as_card(2),
    ]

    # Tests identification based on oracle_id alone. Also tests highres_image boolean
    forest_en_1 = TestCaseData("english_basic_Forest")
    forest_en_2 = TestCaseData("english_basic_Forest_2")
    forest_de = TestCaseData("german_basic_Forest")
    forest_es = TestCaseData("spanish_basic_Forest")
    yield CardIdentificationData(oracle_id="b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6"), [
        forest_en_1.as_card(),
        forest_en_2.as_card(),
        forest_de.as_card(),
        forest_es.as_card(),
    ]
    # Tests other attribute combinations
    yield CardIdentificationData(name="Bosque"), [
        forest_es.as_card()
    ]
    yield CardIdentificationData(set_code="anb"), [
        forest_en_1.as_card()
    ]
    yield CardIdentificationData("de", set_code="znr"), [
       forest_de.as_card()
    ]
    yield CardIdentificationData(set_code="znr", collector_number="280"), [
        forest_en_2.as_card(),
        forest_es.as_card(),
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
    case = TestCaseData("regular_english_card")
    yield CardIdentificationData(scryfall_id=case.scryfall_id, is_front=True), case.as_card()
    # Back side of regular card returns None
    yield CardIdentificationData(scryfall_id=case.scryfall_id, is_front=False), None
    # Unknown scryfall_id returns None
    yield CardIdentificationData(scryfall_id="ueueueue-abcd-1234-5678-abcdefabcdef", is_front=True), None

    case = TestCaseData("oversized_card")
    yield CardIdentificationData(scryfall_id=case.scryfall_id, is_front=True), case.as_card()

    case = TestCaseData("german_basic_Forest")
    yield CardIdentificationData(scryfall_id=case.scryfall_id, is_front=True), case.as_card()

    case = TestCaseData("spanish_basic_Forest")
    yield CardIdentificationData(scryfall_id=case.scryfall_id, is_front=True), case.as_card()

    # Double-faced with high-res image
    case = TestCaseData("english_double_faced_card")
    yield CardIdentificationData(scryfall_id=case.scryfall_id, is_front=True), case.as_card(1)
    yield CardIdentificationData(scryfall_id=case.scryfall_id, is_front=False), case.as_card(2)

    # Art series card
    case = TestCaseData("english_double_faced_art_series_card")
    yield CardIdentificationData(scryfall_id=case.scryfall_id, is_front=True), case.as_card(1)
    yield CardIdentificationData(scryfall_id=case.scryfall_id, is_front=False), case.as_card(2)
    # Digital card
    case = TestCaseData("english_basic_Forest")
    yield CardIdentificationData(scryfall_id=case.scryfall_id, is_front=True), case.as_card()


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
    # Same-language translation
    for case in (TestCaseData("regular_english_card"), TestCaseData("regular_english_card")):
        yield CardIdentificationData(case.language, scryfall_id=case.scryfall_id, is_front=True), case.as_card()
    for case in (TestCaseData("english_double_faced_card"), TestCaseData("english_double_faced_art_series_card")):
        yield CardIdentificationData(case.language, scryfall_id=case.scryfall_id, is_front=True), case.as_card(1)
        yield CardIdentificationData(case.language, scryfall_id=case.scryfall_id, is_front=False), case.as_card(2)

    # Translate single-faced card
    forests = TestCaseData("english_basic_Forest_2"), TestCaseData("german_basic_Forest"), TestCaseData("spanish_basic_Forest")
    for source, target in itertools.product(forests, repeat=2):  # type: TestCaseData, TestCaseData
        yield CardIdentificationData(target.language, scryfall_id=source.scryfall_id, is_front=True), target.as_card()
    #
    treefolk = (
        (TestCaseData("german_Ironroot_Treefolk_1"), TestCaseData("english_Ironroot_Treefolk_1")),
        (TestCaseData("german_Ironroot_Treefolk_2"), TestCaseData("english_Ironroot_Treefolk_2")),
        (TestCaseData("german_Ironroot_Treefolk_3"), TestCaseData("english_Ironroot_Treefolk_3")),
    )
    for card_1, card_2 in treefolk:
        yield CardIdentificationData(card_2.language, scryfall_id=card_1.scryfall_id, is_front=True), card_2.as_card()
        yield CardIdentificationData(card_1.language, scryfall_id=card_2.scryfall_id, is_front=True), card_1.as_card()


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
    # Single-faced cards
    for case in (TestCaseData("regular_english_card"), TestCaseData("oversized_card")):
        # The back side of a regular card does not exist, Expect None
        yield CardIdentificationData(scryfall_id=case.scryfall_id, is_front=True), None
        # The other side of a non-existing back side of a regular card returns the existing front
        yield CardIdentificationData(scryfall_id=case.scryfall_id, is_front=False), case.as_card()
    case = TestCaseData("split_card")
    yield CardIdentificationData(scryfall_id=case.scryfall_id, is_front=True), None
    # FIXME: This returns None, but should return the first face of the front
    # yield CardIdentificationData(scryfall_id=case.scryfall_id, is_front=False), case.as_card(1)

    # Double-faced cards
    for case in (TestCaseData("english_double_faced_card"), TestCaseData("english_double_faced_art_series_card")):
        yield CardIdentificationData(scryfall_id=case.scryfall_id, is_front=True), case.as_card(2)
        yield CardIdentificationData(scryfall_id=case.scryfall_id, is_front=False), case.as_card(1)


@pytest.mark.parametrize("card_data, expected", generate_test_cases_for_test_get_opposing_face())
def test_get_opposing_face(
        card_db_with_cards: CardDatabase, card_data: CardIdentificationData, expected: typing.Optional[Card]):
    result = card_db_with_cards.get_opposing_face(card_data)
    if expected is None:
        assert_that(result, is_(none()))
    else:
        assert_that(
            result,
            is_(all_of(
                is_(instance_of(Card)),
                matches_type_annotation(),
                has_properties({
                    # Verifies that the expected card matches the given card identification data.
                    # Not strictly required, but ensures that the test data is consistent
                    "scryfall_id": card_data.scryfall_id,
                    "is_front": not card_data.is_front,  # Negation here
                }),
                is_dataclass_equal_to(expected),
            ))
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
    today = datetime.datetime.today()
    now = today + MINIMUM_REFRESH_DELAY + datetime.timedelta(delta_days)
    fromisoformat = datetime.datetime.fromisoformat
    with unittest.mock.patch("mtg_proxy_printer.model.carddb.datetime.datetime") as mock_date:
        mock_date.today.return_value = now
        mock_date.fromisoformat = fromisoformat
        assert_that(datetime.datetime.today(), is_not(today))
        assert_that(
            card_db.allow_updating_card_data(),
            is_(delta_days >= 0)
        )



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
        include_wastes: bool, include_snow_basics: bool, expected_oracle_ids: StringList):
    fill_card_database_with_json_cards(
        qtbot, card_db, ["english_basic_Forest", "english_basic_Wastes", "english_basic_Snow_Forest"])
    assert_that(
        card_db.get_basic_land_oracle_ids(include_wastes, include_snow_basics),
        contains_inanyorder(*expected_oracle_ids)
    )


@pytest.mark.parametrize("source_id, expected_cards_names", [
    ("2c6e5b25-b721-45ee-894a-697de1310b8c", ["Food"]),  # Bake into a Pie
    ("37e32ba6-108a-421f-9dad-3d03f7ebe239", []),  # Food token
    ("e4b7e3b5-2f3c-4eb7-abc9-322a049a9e1a", []),  # Food Token
    # Both printings of Asmoranomardicadaistinaculdacar
    ("d99a9a7d-d9ca-4c11-80ab-e39d5943a315", ["The Underworld Cookbook", "Food"]),
    ("2879f780-e17f-4e68-931e-6e45f9df28e1", ["The Underworld Cookbook", "Food"]),
    # The Underworld Cookbook
    ("4f24504e-b397-4b98-b8e8-8166457f7a2e", ["Asmoranomardicadaistinaculdacar", "Food"]),

])
def test_find_related_printings(qtbot, card_db: CardDatabase, source_id: str, expected_cards_names: StringList):
    fill_card_database_with_json_cards(
        qtbot, card_db, [
        "The_Underworld_Cookbook",
        "Food_Token",
        "Asmoranomardicadaistinaculdacar",
        "Bake_into_a_Pie",
        "Asmoranomardicadaistinaculdacar_2",
        "Food_Token_2",
    ])
    source_card = card_db.get_card_with_scryfall_id(source_id, True)
    assert_that(source_card, is_(not_none()))
    related = card_db.find_related_cards(source_card)
    assert_that(
        related, contains_inanyorder(
            *[has_property("name", equal_to(expected)) for expected in expected_cards_names]
        )
    )


def test_get_all_cards_from_image_cache(qtbot, card_db):
    fill_card_database_with_json_cards(
        qtbot, card_db, ["regular_english_card", "oversized_card"], {"hide-oversized-cards": str(True)})
    cache_content = [
        CacheContent("650722b4-d72b-4745-a1a5-00a34836282b", True, True, Path()),  # Atraxa
        CacheContent("0000579f-7b35-4ed3-b44c-db2a538066fe", True, True, Path()),  # Fury Sliver
        CacheContent("abcdeabc-abcd-abcd-abcd-efghijklmnop", True, True, Path()),  # Non-existing
    ]
    assert_that(
        card_db.get_all_cards_from_image_cache(cache_content),
        contains_exactly(
            contains_exactly(contains_exactly(
                has_property("name", equal_to("Fury Sliver")),
                cache_content[1])),
            contains_exactly(contains_exactly(
                has_property("name", equal_to("Atraxa, Praetors' Voice")),
                cache_content[0])),
            contains_exactly(cache_content[-1]),
        )
    )


@pytest.mark.parametrize("json_name, scryfall_id, expected", [
    ("regular_english_card", "0000579f-7b35-4ed3-b44c-db2a538066fe", False),
    ("english_double_faced_card", "b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", True),

])
def test_is_dfc(qtbot, card_db: CardDatabase, json_name: str, scryfall_id: str, expected: bool):
    fill_card_database_with_json_card(qtbot, card_db, json_name)
    assert_that(
        card_db.is_dfc(scryfall_id),
        is_(equal_to(expected))
    )


@pytest.mark.parametrize("card_data, expected", [
    # Forests. All source languages return all available languages
    (CardIdentificationData(scryfall_id="7ef83f4c-d3ff-4905-a16d-f2bae673a5b2", is_front=True), ["de", "en", "es"]),
    (CardIdentificationData(scryfall_id="ffa13d4c-6c5e-44bd-859e-38e79d47a916", is_front=True), ["de", "en", "es"]),
    (CardIdentificationData(scryfall_id="cd4cf73d-a408-48f1-9931-54707553c5d5", is_front=True), ["de", "en", "es"]),
    # The mis-translated German Coercion cannot be translated, as the English Coercion is not in the imported test data
    (CardIdentificationData(scryfall_id="93054b80-fd1f-4200-8d33-2e826a181db0", is_front=True), ["de"]),
    # English/German Duress can be translated
    (CardIdentificationData(scryfall_id="51c6ec30-afb2-41e6-895b-92e070aa86f3", is_front=True), ["de", "en"]),
    (CardIdentificationData(scryfall_id="15c8d82e-6e65-4d36-bf09-b24dde016581", is_front=True), ["de", "en"]),
])
def test_get_available_languages_for_card(qtbot, card_db, card_data: CardIdentificationData, expected: StringList):
    fill_card_database_with_json_cards(qtbot, card_db, [
        "english_basic_Forest", "german_basic_Forest", "spanish_basic_Forest",
        "german_Coercion_with_faulty_translation", "german_Duress", "english_Duress",
    ])
    card = card_db.get_card_with_scryfall_id(card_data.scryfall_id, card_data.is_front)
    assert_that(card, is_(not_none()), "Setup failed, card not found")
    assert_that(
        card_db.get_available_languages_for_card(card),
        contains_exactly(*expected)
    )


def test_get_card_from_data_prefers_highres_images_over_newer_lowres_printings(qtbot, card_db):
    fill_card_database_with_json_cards(
        qtbot, card_db, ["english_basic_Forest_2", "English_basic_Forest_newest_and_low_res"]
    )
    assert_that(
        card_db.get_cards_from_data(CardIdentificationData(name="Forest")),
        contains_exactly(
            has_properties(
                language="en",
                name="Forest",
                set=has_property("name", "Zendikar Rising"),
                scryfall_id="e2ef9b74-481b-424b-8e33-f0b910f66370",
                is_front=True,
                highres_image=True,
            ),
            has_properties(
                language="en",
                name="Forest",
                set=has_property("name", "Doctor Who"),
                scryfall_id="15b3f35e-451e-4de6-a4f7-249287566964",
                is_front=True,
                highres_image=False,
            ),
        )
    )
