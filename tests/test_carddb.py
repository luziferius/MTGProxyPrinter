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

from hamcrest import *
import pytest

from mtg_proxy_printer.model.carddb import CardDatabase

from .helpers import assert_model_is_empty, create_new_card_database_with_json_card, create_new_card_database_with_multiple_cards

StringList = typing.List[str]
OptString = typing.Optional[str]

def test_has_data_on_empty_database_returns_false():
    model = CardDatabase(":memory:")
    assert_model_is_empty(model)
    assert_that(model.has_data(), is_(False))


def test_has_data_on_filled_database_returns_true():
    model = create_new_card_database_with_json_card("regular_english_card")
    assert_that(model.has_data(), is_(True))


def test_get_all_languages_without_data():
    model = CardDatabase(":memory:")
    assert_that(
        model.get_all_languages(),
        is_(empty())
    )


def test_get_all_languages_with_data():
    model = create_new_card_database_with_multiple_cards("multiple_cards_for_test_card_db")
    assert_that(
        model.get_all_languages(),
        contains_exactly("de", "en", "es")
    )


@pytest.mark.parametrize("language, prefix, expected_names", [
    ("en", None, ["Forest", "Future Sight"]),
    ("en", "Fu", ["Future Sight"]),
    ("en", "%or", ["Forest"]),
    ("en", "AAAAAAAA", []),
    ("en", "F%t", ["Forest", "Future Sight"]),
    ("de", None, ["Wald"]),  # noqa  # A German Forest
    ("es", None, ["Bosque"]),  # noqa  # A Spanish Forest
    ("Nonexisting language", None, []),
])
def test_get_card_names(language: str, prefix: OptString, expected_names: StringList):
    model = create_new_card_database_with_multiple_cards("multiple_cards_for_test_card_db")
    assert_that(
        model.get_card_names(language, prefix),
        contains_exactly(*expected_names)
    )