# Copyright (C) 2021 Thomas Hess <thomas.hess@udo.edu>

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

import dataclasses
import datetime
import typing
import unittest.mock
from unittest.mock import MagicMock

from hamcrest import *
import pytest

from mtg_proxy_printer.model.carddb import CardDatabase, CardIdentificationData, MINIMUM_REFRESH_DELAY
import mtg_proxy_printer.card_info_downloader
from mtg_proxy_printer.model.document import Document

from .helpers import assert_model_is_empty, fill_card_database_with_json_card, \
    fill_card_database_with_json_cards, load_json

StringList = typing.List[str]
OptString = typing.Optional[str]


class DatabaseSetData(typing.NamedTuple):
    """Row data stored in the Set relation"""
    set_code: str
    set_name: str
    set_uri: str


@dataclasses.dataclass(frozen=True)
class FaceData:
    """Contains all data that is unique per card face."""
    # Implementation note: Implemented as a frozen dataclass,
    # because this is not meant to be fed directly into an _assert_* method expecting a list of tuples.
    name: str
    image_uri: str
    is_front: bool


@dataclasses.dataclass(frozen=True)
class TestCaseData:
    """
    Contains the JSON document name and all card data parsed from the JSON. This is sufficient to construct a test
    case and contains all validation data. The methods db_*() return lists of tuples suitable to test database content.
    """
    # Implementation note: Implemented as a frozen dataclass,
    # because this is not meant to be fed directly into an _assert_* method expecting a list of tuples.
    json_name: str
    highres_image: bool
    face_data: typing.Tuple[FaceData, ...]
    set: DatabaseSetData
    language: str
    collector_number: str
    scryfall_id: str
    oracle_id: str
    is_oversized: bool

    __test__ = False  # Instruct PyTest to not collect this as a Test class, even if the name starts with "Test"


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


@pytest.mark.parametrize("source_name, target_language, source_language, expected", [
    ("Forest", "en", "en", "Forest"),
    ("Wald", "de", "de", "Wald"),
    ("Bosque", "es", "es", "Bosque"),

    ("Forest", "en", None, "Forest"),
    ("Wald", "en", None, "Forest"),
    ("Bosque", "en", None, "Forest"),
    ("Bosque", "de", None, "Wald"),
    ("Forest", "de", None, "Wald"),

    ("Wald", "en", "de", "Forest"),
    ("Bosque", "en", "es", "Forest"),

    ("Wald", "en", "wrong source", None),
    ("Bosque", "en", "wrong source", None),
    ("Wald", "de", "wrong source", None),
    ("Bosque", "es", "wrong source", None),
])
def test_translate_card_name(
        qtbot, card_db: CardDatabase, source_name: str, target_language: str,
        source_language: OptString, expected: OptString):
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
        card_db.translate_card_name(source_name, target_language, source_language),
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
    document.add_card(_get_card_from_model(card_db, "e2ef9b74-481b-424b-8e33-f0b910f66370", True), 1)
    document.store_image_usage()
    document.add_card(_get_card_from_model(card_db, "ffa13d4c-6c5e-44bd-859e-38e79d47a916", True), 1)
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


@pytest.mark.parametrize("test_case", [
    TestCaseData(  # English "Fury Sliver" from Time Spiral.
        "regular_english_card", True, (
            FaceData("Fury Sliver", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979", True),
        ), DatabaseSetData("tsp", "Time Spiral", "https://scryfall.com/sets/tsp?utm_source=api"),
        "en", "157", "0000579f-7b35-4ed3-b44c-db2a538066fe", "44623693-51d6-49ad-8cd7-140505caf02f", False,
    ),
    TestCaseData(  # Oversized printing of "Atraxa, Praetors' Voice"
        "oversized_card", True, (
            FaceData("Atraxa, Praetors' Voice", "https://c1.scryfall.com/file/scryfall-cards/png/front/6/5/650722b4-d72b-4745-a1a5-00a34836282b.png?1561757296", True),
        ), DatabaseSetData("oc16", "Commander 2016 Oversized", "https://scryfall.com/sets/oc16?utm_source=api"),
        "en", "28", "650722b4-d72b-4745-a1a5-00a34836282b", "7e6b9b59-cd68-4e3c-827b-38833c92d6eb", True,
    ),
])
def test__translate_card(qtbot, card_db: CardDatabase, test_case: TestCaseData):
    fill_card_database_with_json_card(qtbot, card_db, test_case.json_name)
    card = card_db.get_card_with_scryfall_id(test_case.scryfall_id, test_case.face_data[0].is_front)
    # Use the private method to skip the internal shortcut in translate_card()
    # that skips requested same-language translations.
    assert_that(
        card_db._translate_card(card, "en"), all_of(
            is_not(same_instance(card)),  # No shortcut taken, is actually a new instance
            has_properties({
                "is_oversized": all_of(
                    is_(test_case.is_oversized),
                    instance_of(bool),
                ),
                "name": is_(equal_to(test_case.face_data[0].name)),
                "is_front": all_of(
                    is_(test_case.face_data[0].is_front),
                    instance_of(bool),
                ),
                "oracle_id": is_(equal_to(test_case.oracle_id)),
                "scryfall_id": is_(equal_to(test_case.scryfall_id)),
                "language": is_(equal_to(test_case.language)),
                "image_uri": is_(equal_to(test_case.face_data[0].image_uri)),
                "collector_number": is_(equal_to(test_case.collector_number)),
                "face_number": all_of(
                    is_(card.face_number),
                    instance_of(int),
                ),
                "highres_image": all_of(
                    is_(test_case.highres_image),
                    instance_of(bool),
                ),
                "set": has_properties({
                    "name": test_case.set.set_name,
                    "code": test_case.set.set_code,
                }),
            }),
        ))


@pytest.mark.parametrize("json_name, scryfall_id, expected", [
    ("regular_english_card", "0000579f-7b35-4ed3-b44c-db2a538066fe", False),
    ("oversized_card", "650722b4-d72b-4745-a1a5-00a34836282b", True)
])
def test_find_all_translated_printings__card_attribute_is_oversized(
        qtbot, card_db: CardDatabase, json_name: str, scryfall_id: str, expected: bool):
    fill_card_database_with_json_card(qtbot, card_db, json_name)
    card = card_db.get_card_with_scryfall_id(scryfall_id, True)
    cards = card_db.find_all_translated_printings(card, "en")
    assert_that(cards, has_length(1))
    assert_that(
        cards[0],  all_of(
            is_not(same_instance(card)),  # No shortcut taken, is actually a new instance
            has_property("is_oversized", is_(expected)),
            has_property("is_oversized", instance_of(bool)),
        ))


@pytest.mark.parametrize("json_name, scryfall_id, expected", [
    ("regular_english_card", "0000579f-7b35-4ed3-b44c-db2a538066fe", False),
    ("oversized_card", "650722b4-d72b-4745-a1a5-00a34836282b", True)
])
def test_get_cards_from_data__card_attribute_is_oversized(
        qtbot, card_db: CardDatabase, json_name: str, scryfall_id: str, expected: bool):
    fill_card_database_with_json_card(qtbot, card_db, json_name)
    card_data = CardIdentificationData("en", scryfall_id=scryfall_id, is_front=True)
    cards = card_db.get_cards_from_data(card_data)
    assert_that(cards, has_length(1))
    assert_that(cards[0], has_property("is_oversized", all_of(is_(expected), instance_of(bool))))


@pytest.mark.parametrize("front", [True, False])
def test_translate_double_faced_card(qtbot, card_db: CardDatabase, front: bool):
    fill_card_database_with_json_cards(qtbot, card_db, ["english_double_faced_card", "non_english_double_faced_card"])
    english_card = card_db.get_card_with_scryfall_id("b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", front)
    non_english_card = card_db.get_card_with_scryfall_id("000847d3-ebde-4580-a00e-61d501e99485", front)
    assert_that(
        card_db.translate_card_name(non_english_card.name, english_card.language),
        is_(equal_to(english_card.name))
    )
    assert_that(
        card_db.translate_card_name(english_card.name, non_english_card.language),
        is_(equal_to(non_english_card.name))
    )


@pytest.mark.parametrize("is_front", [True, False])
@pytest.mark.parametrize("json_name, scryfall_id", [
    ("english_double_faced_card", "b3b87bfc-f97f-4734-94f6-e3e2f335fc4d"),
    ("english_double_faced_art_series_card", "002ad179-ddf4-4f48-9504-cfa02e11a52e"),
])
def test_translate_card__card_attribute_is_front(
        qtbot, card_db: CardDatabase, json_name: str, scryfall_id: str, is_front: bool):
    fill_card_database_with_json_card(qtbot, card_db, json_name)
    card = card_db.get_card_with_scryfall_id(scryfall_id, is_front)
    # Use the private method to skip the internal shortcut in translate_card()
    # that skips requested same-language translations.
    assert_that(
        card_db._translate_card(card, "en"), all_of(
            is_not(same_instance(card)),  # No shortcut taken, is actually a new instance
            has_property("is_front", is_(is_front)),
            has_property("is_front", instance_of(bool)),
        ))


@pytest.mark.parametrize("is_front", [True, False])
@pytest.mark.parametrize("json_name, scryfall_id", [
    ("english_double_faced_card", "b3b87bfc-f97f-4734-94f6-e3e2f335fc4d"),
    ("english_double_faced_art_series_card", "002ad179-ddf4-4f48-9504-cfa02e11a52e"),
])
def test_find_all_translated_printings__card_attribute_is_front(
        qtbot, card_db: CardDatabase, json_name: str, scryfall_id: str, is_front: bool):
    fill_card_database_with_json_card(qtbot, card_db, json_name)
    card = card_db.get_card_with_scryfall_id(scryfall_id, is_front)
    cards = card_db.find_all_translated_printings(card, "en")
    assert_that(cards, has_length(1))
    assert_that(
        cards[0],  all_of(
            is_not(same_instance(card)),  # No shortcut taken, is actually a new instance
            has_property("is_front", is_(is_front)),
            has_property("is_front", instance_of(bool)),
        ))


@pytest.mark.parametrize("is_front", [True, False])
@pytest.mark.parametrize("json_name, scryfall_id", [
    ("english_double_faced_card", "b3b87bfc-f97f-4734-94f6-e3e2f335fc4d"),
    ("english_double_faced_art_series_card", "002ad179-ddf4-4f48-9504-cfa02e11a52e"),
])
def test_get_cards_from_data__card_attribute_is_front(
        qtbot, card_db: CardDatabase, json_name: str, scryfall_id: str, is_front: bool):
    fill_card_database_with_json_card(qtbot, card_db, json_name)
    card_data = CardIdentificationData("en", scryfall_id=scryfall_id, is_front=is_front)
    cards = card_db.get_cards_from_data(card_data)
    assert_that(cards, has_length(1))
    assert_that(cards[0], has_property("is_front", all_of(is_(is_front), instance_of(bool))))


@pytest.mark.parametrize("is_front", [True, False])
@pytest.mark.parametrize("json_name, scryfall_id", [
    ("english_double_faced_card", "b3b87bfc-f97f-4734-94f6-e3e2f335fc4d"),
    ("english_double_faced_art_series_card", "002ad179-ddf4-4f48-9504-cfa02e11a52e"),
])
def test_get_opposing_face__card_attribute_is_front(
        qtbot, card_db: CardDatabase, json_name: str, scryfall_id: str, is_front: bool):
    fill_card_database_with_json_card(qtbot, card_db, json_name)
    card_data = CardIdentificationData("en", scryfall_id=scryfall_id, is_front=is_front)
    card = card_db.get_opposing_face(card_db.get_cards_from_data(card_data)[0])
    assert_that(card, is_(not_none()))
    assert_that(card, has_property("is_front", all_of(is_not(is_front), instance_of(bool))))


@pytest.mark.parametrize("is_front", [True, False])
@pytest.mark.parametrize("json_name, scryfall_id, highres_image", [
    ("english_double_faced_card", "b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", True),
    ("english_double_faced_art_series_card", "002ad179-ddf4-4f48-9504-cfa02e11a52e", False),
])
def test_find_all_translated_printings__card_attribute_highres_image(
        qtbot, card_db: CardDatabase, json_name: str, scryfall_id: str, highres_image: bool, is_front: bool):
    fill_card_database_with_json_card(qtbot, card_db, json_name)
    card = card_db.get_card_with_scryfall_id(scryfall_id, is_front)
    cards = card_db.find_all_translated_printings(card, "en")
    assert_that(cards, has_length(1))
    assert_that(
        cards[0],  all_of(
            is_not(same_instance(card)),  # No shortcut taken, is actually a new instance
            has_property("highres_image", is_(highres_image)),
            has_property("highres_image", instance_of(bool)),
        ))


@pytest.mark.parametrize("is_front", [True, False])
@pytest.mark.parametrize("json_name, scryfall_id, highres_image", [
    ("english_double_faced_card", "b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", True),
    ("english_double_faced_art_series_card", "002ad179-ddf4-4f48-9504-cfa02e11a52e", False),
])
def test_get_cards_from_data__card_attribute_highres_image(
        qtbot, card_db: CardDatabase, json_name: str, scryfall_id: str, highres_image: bool, is_front: bool):
    fill_card_database_with_json_card(qtbot, card_db, json_name)
    card_data = CardIdentificationData("en", scryfall_id=scryfall_id, is_front=is_front)
    cards = card_db.get_cards_from_data(card_data)
    assert_that(cards, has_length(1))
    assert_that(cards[0], has_property("highres_image", all_of(is_(highres_image), instance_of(bool))))


@pytest.mark.parametrize("card_count_data", [
    [("7ef83f4c-d3ff-4905-a16d-f2bae673a5b2", 2), ("e2ef9b74-481b-424b-8e33-f0b910f66370", 1)],
    [("7ef83f4c-d3ff-4905-a16d-f2bae673a5b2", 1), ("e2ef9b74-481b-424b-8e33-f0b910f66370", 2)],
])
def test_get_cards_from_data_order_by_print_count_enabled(qtbot, card_db: CardDatabase, card_count_data):
    fill_card_database_with_json_cards(qtbot, card_db, ["english_basic_Forest", "english_basic_Forest_2"])
    card_db.db.executemany(
        "INSERT INTO LastImageUseTimestamps (scryfall_id, is_front, usage_count) VALUES (?, 1, ?)",
        card_count_data
    )
    card_data = CardIdentificationData("en", name="Forest")
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


@pytest.mark.parametrize("card_count_data", [
    [("7ef83f4c-d3ff-4905-a16d-f2bae673a5b2", 2), ("e2ef9b74-481b-424b-8e33-f0b910f66370", 1)],
    [("7ef83f4c-d3ff-4905-a16d-f2bae673a5b2", 1), ("e2ef9b74-481b-424b-8e33-f0b910f66370", 2)],
])
def test_find_all_translated_printings_order_by_print_count_enabled(qtbot, card_db: CardDatabase, card_count_data):
    fill_card_database_with_json_cards(qtbot, card_db, ["english_basic_Forest", "english_basic_Forest_2"])
    card_db.db.executemany(
        "INSERT INTO LastImageUseTimestamps (scryfall_id, is_front, usage_count) VALUES (?, 1, ?)",
        card_count_data
    )
    card_to_translate = card_db.get_card_with_scryfall_id(card_count_data[0][0], True)
    cards = card_db.find_all_translated_printings(card_to_translate, "en", order_by_print_count=True)
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


@pytest.mark.parametrize("is_front", [True, False])
@pytest.mark.parametrize("json_name, scryfall_id, highres_image", [
    ("english_double_faced_card", "b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", True),
    ("english_double_faced_art_series_card", "002ad179-ddf4-4f48-9504-cfa02e11a52e", False),
])
def test_get_opposing_face__card_attribute_highres_image(
        qtbot, card_db: CardDatabase, json_name: str, scryfall_id: str, highres_image: bool, is_front: bool):
    fill_card_database_with_json_card(qtbot, card_db, json_name)
    card_data = CardIdentificationData("en", scryfall_id=scryfall_id, is_front=is_front)
    card = card_db.get_opposing_face(card_db.get_cards_from_data(card_data)[0])
    assert_that(card, is_(not_none()))
    assert_that(card, has_property("highres_image", all_of(is_(highres_image), instance_of(bool))))


def test_allow_updating_card_data_on_empty_database_returns_true(card_db: CardDatabase):
    assert_that(card_db.allow_updating_card_data(), is_(True))


def test_allow_updating_card_data_on_freshly_populated_database_returns_false(card_db: CardDatabase):
    cidw = mtg_proxy_printer.card_info_downloader.CardInfoDownloadWorker(card_db)
    card_data = [load_json("regular_english_card")]
    cidw.populate_database(card_data)
    assert_that(card_db.allow_updating_card_data(), is_(False))


@pytest.mark.parametrize("delta_days", [0, 1, 2])
def test_allow_updating_card_data_on_stale_populated_database_returns_true(card_db: CardDatabase, delta_days: int):
    cidw = mtg_proxy_printer.card_info_downloader.CardInfoDownloadWorker(card_db)
    card_data = [load_json("regular_english_card")]
    cidw.populate_database(card_data)
    today = datetime.date.today()
    now = today + MINIMUM_REFRESH_DELAY + datetime.timedelta(delta_days)
    with unittest.mock.patch("mtg_proxy_printer.card_info_downloader.datetime.date") as mock_date:
        mock_date.today.return_value = now
        assert_that(datetime.date.today(), is_not(today))
        assert_that(
            card_db.allow_updating_card_data(),
            is_(True)
        )


def test_get_total_cards_in_last_update(card_db: CardDatabase):
    cidw = mtg_proxy_printer.card_info_downloader.CardInfoDownloadWorker(card_db)
    card_data = [load_json("regular_english_card")]
    cidw.populate_database(card_data)
    assert_that(card_db.get_total_cards_in_last_update(), is_(len(card_data)))
    card_data.append(load_json("english_basic_Forest"))
    cidw.populate_database(card_data)
    assert_that(card_db.get_total_cards_in_last_update(), is_(len(card_data)))
