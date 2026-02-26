#  Copyright © 2020-2026  Thomas Hess <thomas.hess@udo.edu>
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


import pytest
from hamcrest import *

from mtg_proxy_printer.update_checker import ApplicationUpdateCheckWorker, CardDataUpdateCheckWorker

from tests.helpers import fill_card_database_with_json_cards, fill_card_database_with_json_card


@pytest.fixture
def app_update_worker() -> ApplicationUpdateCheckWorker:
    return ApplicationUpdateCheckWorker()


@pytest.fixture
def card_update_worker(card_db) -> CardDataUpdateCheckWorker:
    worker = CardDataUpdateCheckWorker(card_db)
    worker._db = card_db.db
    return worker


def test_get_total_cards_in_last_update(qtbot, card_update_worker: CardDataUpdateCheckWorker):
    card_data = ["regular_english_card"]
    fill_card_database_with_json_cards(qtbot, card_update_worker.card_db, card_data)
    assert_that(card_update_worker.get_total_cards_in_last_update(), is_(len(card_data)))
    card_data.append("english_basic_Forest")
    fill_card_database_with_json_cards(qtbot, card_update_worker.card_db, card_data)
    assert_that(card_update_worker.get_total_cards_in_last_update(), is_(len(card_data)))


def test_card_database_has_data_on_empty_database_returns_false(card_update_worker: CardDataUpdateCheckWorker):
    assert_that(card_update_worker.card_database_has_data(), is_(False))


def test_card_database_has_data_on_filled_database_returns_true(qtbot, card_update_worker):
    fill_card_database_with_json_card(qtbot, card_update_worker.card_db, "regular_english_card")
    assert_that(card_update_worker.card_database_has_data(), is_(True))
