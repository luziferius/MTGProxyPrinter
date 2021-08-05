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

import typing
from unittest.mock import MagicMock

from hamcrest import *
import pytest

from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.model.document import Document

from .helpers import assert_model_is_empty, create_new_card_database_with_multiple_cards

StringList = typing.List[str]
OptString = typing.Optional[str]


@pytest.fixture(params=[False, True])
def model(request) -> CardDatabase:
    model = create_new_card_database_with_multiple_cards("multiple_cards_for_test_card_db")
    if request.param:
        model.db.execute("PRAGMA reverse_unordered_selects = TRUE")
    return create_new_card_database_with_multiple_cards("multiple_cards_for_test_card_db")


@pytest.fixture()
def empty_model() -> CardDatabase:
    return CardDatabase(":memory:")


def test_has_data_on_empty_database_returns_false(empty_model: CardDatabase):
    assert_model_is_empty(empty_model)
    assert_that(empty_model.has_data(), is_(False))


def test_has_data_on_filled_database_returns_true(model: CardDatabase):
    assert_that(model.has_data(), is_(True))


def test_get_all_languages_without_data(empty_model: CardDatabase):
    assert_that(
        empty_model.get_all_languages(),
        is_(empty())
    )


def test_get_all_languages_with_data(model: CardDatabase):
    assert_that(
        model.get_all_languages(),
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
def test_get_card_names(model: CardDatabase, language: str, prefix: OptString, expected_names: StringList):
    assert_that(
        model.get_card_names(language, prefix),
        contains_inanyorder(*expected_names)
    )


@pytest.mark.parametrize("name, expected", [
    ("Forest", "en"),
    ("Future Sight", "en"),
    ("Wald", "de"),
    ("Bosque", "es"),
    ("Unknown", None),
])
def test_guess_language_from_name(model: CardDatabase, name: str, expected: OptString):
    assert_that(
        model.guess_language_from_name(name),
        is_(equal_to(expected))
    )


@pytest.mark.parametrize("language, expected", [
    ("en", True),
    ("de", True),
    ("es", True),
    ("", False),
    ("Unknown", False),
])
def test_is_known_language(model: CardDatabase, language: str, expected: bool):
    assert_that(
        model.is_known_language(language),
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
def test_translate_card_name(model: CardDatabase, source_name: str, target_language: str, source_language: OptString, expected: OptString):
    assert_that(
        model.translate_card_name(source_name, target_language, source_language),
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
def test_cards_used_less_often_then(model: CardDatabase, usage_count: int, expected: typing.List[int]):
    # Setup
    document = Document(model, MagicMock())
    document.add_card(_get_card_from_model(model, "e2ef9b74-481b-424b-8e33-f0b910f66370", True), 1)
    document.store_image_usage()
    document.add_card(_get_card_from_model(model, "ffa13d4c-6c5e-44bd-859e-38e79d47a916", True), 1)
    document.store_image_usage()
    # Test
    assert_that(
        result := model.cards_used_less_often_then([
            ("e2ef9b74-481b-424b-8e33-f0b910f66370", True),
            ("ffa13d4c-6c5e-44bd-859e-38e79d47a916", True),
            ("cd4cf73d-a408-48f1-9931-54707553c5d5", True),
        ], usage_count),
        contains_exactly(*expected),
        f"Result: {result}"
    )


def _get_card_from_model(model: CardDatabase, scryfall_id: str, is_front: bool):
    card = model.get_card_with_scryfall_id(scryfall_id, is_front)
    assert_that(card, has_properties({
        "scryfall_id": equal_to(scryfall_id),
        "is_front": equal_to(is_front),
    }), "Wrong card returned")
    return card

