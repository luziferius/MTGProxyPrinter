# Copyright (C) 2021-2022 Thomas Hess <thomas.hess@udo.edu>

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

from collections import Counter
import typing

from hamcrest import *
import pytest
from pytestqt.qtbot import QtBot
from PySide6.QtCore import QItemSelectionModel

from mtg_proxy_printer.model.carddb import CardDatabase, CardIdentificationData
from mtg_proxy_printer.model.card_list import CardListModel

from tests.helpers import fill_card_database_with_json_cards

OVERSIZED_ID = "650722b4-d72b-4745-a1a5-00a34836282b"
REGULAR_ID = "0000579f-7b35-4ed3-b44c-db2a538066fe"
FOREST_ID = "7ef83f4c-d3ff-4905-a16d-f2bae673a5b2"
WASTES_ID = "9cc070d3-4b83-4684-9caf-063e5c473a77"
SNOW_FOREST_ID = "ca17acea-f079-4e53-8176-a2f5c5c408a1"


def _populate_card_db_and_create_model(qtbot, card_db: CardDatabase) -> CardListModel:
    fill_card_database_with_json_cards(
        qtbot, card_db,
        ["oversized_card", "regular_english_card", "english_basic_Forest", "english_basic_Wastes", "english_basic_Snow_Forest"])
    model = CardListModel(card_db)
    return model


@pytest.mark.parametrize("count", [1, 2, 10])
def test_add_oversized_card_updates_oversized_count(qtbot: QtBot, card_db: CardDatabase, count: int):
    model = _populate_card_db_and_create_model(qtbot, card_db)
    oversized = card_db.get_card_with_scryfall_id(OVERSIZED_ID, True)
    with qtbot.wait_signal(model.oversized_card_count_changed, check_params_cb=(lambda value: value == count)):
        model.add_cards(Counter({oversized: count}))
    assert_that(model.oversized_card_count, is_(equal_to(count)))


def test_remove_oversized_card_updates_oversized_count(qtbot: QtBot, card_db: CardDatabase):
    model = _populate_card_db_and_create_model(qtbot, card_db)
    oversized = card_db.get_card_with_scryfall_id(OVERSIZED_ID, True)
    model.add_cards(Counter({oversized: 10}))
    assert_that(model.oversized_card_count, is_(equal_to(10)))

    with qtbot.wait_signal(model.oversized_card_count_changed, check_params_cb=(lambda value: value == 8)):
        model.remove_cards(0, 1)
    assert_that(model.oversized_card_count, is_(equal_to(8)))


def test_replace_oversized_with_regular_card_decrements_oversized_count(qtbot: QtBot, card_db: CardDatabase):
    model = _populate_card_db_and_create_model(qtbot, card_db)
    regular = card_db.get_card_with_scryfall_id(REGULAR_ID, True)
    oversized = card_db.get_card_with_scryfall_id(OVERSIZED_ID, True)
    regular_data = CardIdentificationData(
        regular.language, scryfall_id=regular.scryfall_id, is_front=regular.is_front)

    with qtbot.wait_signal(model.oversized_card_count_changed, timeout=100, check_params_cb=(lambda value: value == 1)):
        model.add_cards(Counter({oversized: 1, regular: 1}))
    oversized_index = model.index(0, 0)
    regular_index = model.index(1, 0)
    assert_that(model.cards[0].is_oversized, is_(True))
    assert_that(model.cards[oversized_index.row()].is_oversized, is_(True))
    assert_that(model.cards[1].is_oversized, is_(False))
    assert_that(model.cards[regular_index.row()].is_oversized, is_(False))
    assert_that(model.oversized_card_count, is_(1))

    with qtbot.wait_signal(model.oversized_card_count_changed, timeout=100):
        assert_that(model._request_replacement_card(oversized_index, regular_data), is_(True))
    assert_that(model.cards[0].is_oversized, is_(False))
    assert_that(model.cards[1].is_oversized, is_(False))
    assert_that(model.oversized_card_count, is_(0))


def test_replace_regular_with_oversized_card_increments_oversized_count(qtbot: QtBot, card_db: CardDatabase):
    model = _populate_card_db_and_create_model(qtbot, card_db)
    regular = card_db.get_card_with_scryfall_id(REGULAR_ID, True)
    oversized = card_db.get_card_with_scryfall_id(OVERSIZED_ID, True)
    oversized_data = CardIdentificationData(
        oversized.language, scryfall_id=oversized.scryfall_id, is_front=oversized.is_front)

    with qtbot.wait_signal(model.oversized_card_count_changed, timeout=100, check_params_cb=(lambda value: value == 1)):
        model.add_cards(Counter({oversized: 1, regular: 1}))

    oversized_index = model.index(0, 0)
    regular_index = model.index(1, 0)
    assert_that(model.cards[0].is_oversized, is_(True))
    assert_that(model.cards[oversized_index.row()].is_oversized, is_(True))
    assert_that(model.cards[1].is_oversized, is_(False))
    assert_that(model.cards[regular_index.row()].is_oversized, is_(False))
    assert_that(model.oversized_card_count, is_(1))

    with qtbot.wait_signal(model.oversized_card_count_changed, timeout=100):
        assert_that(model._request_replacement_card(regular_index, oversized_data), is_(True))
    assert_that(model.cards[0].is_oversized, is_(True))
    assert_that(model.cards[1].is_oversized, is_(True))
    assert_that(model.oversized_card_count, is_(2))


@pytest.mark.parametrize("ranges, merged", [
    ([], []),
    ([(2, 3)], [(2, 3)]),
    ([(0, 0), (0, 0)], [(0, 0)]),
    ([(0, 0), (0, 1)], [(0, 1)]),
    ([(0, 1), (2, 3)], [(0, 3)]),
    ([(0, 1), (3, 4)], [(0, 1), (3, 4)]),
])
def test__merge_ranges(ranges: typing.List[typing.Tuple[int, int]], merged: typing.List[typing.Tuple[int, int]]):
    assert_that(
        CardListModel._merge_ranges(ranges),
        contains_exactly(*merged),
        "Wrong merge result"
    )


def test_remove_multi_selection(qtbot: QtBot, card_db: CardDatabase):
    model = _populate_card_db_and_create_model(qtbot, card_db)
    regular = card_db.get_card_with_scryfall_id(REGULAR_ID, True)
    oversized = card_db.get_card_with_scryfall_id(OVERSIZED_ID, True)
    model.add_cards(Counter({
        oversized: 1,
        regular: 1,
    }))
    model.add_cards(Counter({
        oversized: 1,
    }))
    selection_model = QItemSelectionModel(model)
    selection_model.select(model.index(0, 0), QItemSelectionModel.Select)
    selection_model.select(model.index(2, 0), QItemSelectionModel.Select)
    assert_that(
        model.remove_multi_selection(selection_model.selection()),
        is_(equal_to(2))
    )
    assert_that(model.cards, contains_exactly(regular))
    assert_that(model.rowCount(), is_(equal_to(1)))


@pytest.mark.parametrize("include_wastes, include_snow_basics, present_cards, expected", [
    (False, False, [], False),
    (False, True, [], False),
    (True, False, [], False),
    (True, True, [], False),

    (False, False, [REGULAR_ID], False),
    (False, True, [REGULAR_ID], False),
    (True, False, [REGULAR_ID], False),
    (True, True, [REGULAR_ID], False),

    (False, False, [REGULAR_ID, OVERSIZED_ID], False),
    (False, True, [REGULAR_ID, OVERSIZED_ID], False),
    (True, False, [REGULAR_ID, OVERSIZED_ID], False),
    (True, True, [REGULAR_ID, OVERSIZED_ID], False),

    (False, False, [FOREST_ID], True),
    (False, True, [FOREST_ID], True),
    (True, False, [FOREST_ID], True),
    (True, True, [FOREST_ID], True),

    (False, False, [WASTES_ID], False),
    (False, True, [WASTES_ID], False),
    (True, False, [WASTES_ID], True),
    (True, True, [WASTES_ID], True),

    (False, False, [SNOW_FOREST_ID], False),
    (False, True, [SNOW_FOREST_ID], True),
    (True, False, [SNOW_FOREST_ID], False),
    (True, True, [SNOW_FOREST_ID], True),

    (False, False, [SNOW_FOREST_ID, WASTES_ID], False),
    (False, True, [SNOW_FOREST_ID, WASTES_ID], True),
    (True, False, [SNOW_FOREST_ID, WASTES_ID], True),
    (True, True, [SNOW_FOREST_ID, WASTES_ID], True),
])
def test_has_basic_lands(
        qtbot: QtBot, card_db: CardDatabase,
        include_wastes: bool, include_snow_basics: bool,
        present_cards: typing.List[str], expected: bool):
    model = _populate_card_db_and_create_model(qtbot, card_db)
    model.add_cards(Counter(
        {card_db.get_card_with_scryfall_id(scryfall_id, True): 1 for scryfall_id in present_cards}
    ))
    assert_that(
        model.has_basic_lands(include_wastes, include_snow_basics),
        is_(expected)
    )


@pytest.mark.parametrize("remove_wastes, remove_snow_basics, present_cards, expected_remaining", [
    (False, False, [], []),
    (False, True, [], []),
    (True, False, [], []),
    (True, True, [], []),
    
    (False, False, [REGULAR_ID, OVERSIZED_ID], [REGULAR_ID, OVERSIZED_ID]),
    (False, True, [REGULAR_ID, OVERSIZED_ID], [REGULAR_ID, OVERSIZED_ID]),
    (True, False, [REGULAR_ID, OVERSIZED_ID], [REGULAR_ID, OVERSIZED_ID]),
    (True, True, [REGULAR_ID, OVERSIZED_ID], [REGULAR_ID, OVERSIZED_ID]),

    (False, False, [WASTES_ID, SNOW_FOREST_ID], [WASTES_ID, SNOW_FOREST_ID]),
    (False, True, [WASTES_ID, SNOW_FOREST_ID], [WASTES_ID]),
    (True, False, [WASTES_ID, SNOW_FOREST_ID], [SNOW_FOREST_ID]),
    (True, True, [WASTES_ID, SNOW_FOREST_ID], []),

    (False, False, [FOREST_ID], []),
    (False, True, [FOREST_ID], []),
    (True, False, [FOREST_ID], []),
    (True, True, [FOREST_ID], []),
])
def test_remove_all_basic_lands(
        qtbot: QtBot, card_db: CardDatabase,
        remove_wastes: bool, remove_snow_basics: bool,
        present_cards: typing.List[str], expected_remaining: typing.List[str]):
    model = _populate_card_db_and_create_model(qtbot, card_db)
    model.add_cards(Counter(
        {card_db.get_card_with_scryfall_id(scryfall_id, True): 1 for scryfall_id in present_cards}
    ))
    model.remove_all_basic_lands(remove_wastes, remove_snow_basics)
    remaining = [card.scryfall_id for card in model.cards]
    assert_that(
        remaining,
        contains_exactly(*expected_remaining)
    )
