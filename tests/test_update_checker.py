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

import pytest
from hamcrest import *

from mtg_proxy_printer.update_checker import BackgroundWorker

from tests.helpers import fill_card_database_with_json_cards, fill_card_database_with_json_card


@pytest.fixture
def worker(card_db) -> BackgroundWorker:
    instance = BackgroundWorker(card_db)
    instance._db = card_db.db
    return instance


def test_get_total_cards_in_last_update(qtbot, worker: BackgroundWorker):
    card_data = ["regular_english_card"]
    fill_card_database_with_json_cards(qtbot, worker.card_db, card_data)
    assert_that(worker.get_total_cards_in_last_update(), is_(len(card_data)))
    card_data.append("english_basic_Forest")
    fill_card_database_with_json_cards(qtbot, worker.card_db, card_data)
    assert_that(worker.get_total_cards_in_last_update(), is_(len(card_data)))


def test_card_database_has_data_on_empty_database_returns_false(worker: BackgroundWorker):
    assert_that(worker.card_database_has_data(), is_(False))


def test_card_database_has_data_on_filled_database_returns_true(qtbot, worker: BackgroundWorker):
    fill_card_database_with_json_card(qtbot, worker.card_db, "regular_english_card")
    assert_that(worker.card_database_has_data(), is_(True))
