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


import unittest.mock

import pytest
from hamcrest import *
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.async_tasks.printing_filter_updater import PrintingFilterUpdater
import mtg_proxy_printer.settings
from mtg_proxy_printer.model.carddb import CardDatabase
from tests.helpers import fill_card_database_with_json_card
from tests.test_card_info_downloader import TestCaseData


def test__remove_old_printing_filters_with_unchanged_boolean_settings_does_nothing(card_db: CardDatabase):
    query = "SELECT * FROM PrintingFilters ORDER BY filter_id ASC"
    section = mtg_proxy_printer.settings.settings["card-filter"]
    old_settings = card_db.db.execute(query).fetchall()
    updater = PrintingFilterUpdater(card_db, card_db.db)
    assert_that(
        updater._remove_old_printing_filters(section),
        is_(False)
    )
    new_settings = card_db.db.execute(query).fetchall()
    assert_that(
        new_settings,
        contains_exactly(*old_settings)
    )


def test__remove_old_printing_filters_with_removed_settings_removes_database_rows(card_db: CardDatabase):
    query = "SELECT * FROM PrintingFilters ORDER BY filter_id ASC"
    section = mtg_proxy_printer.settings.settings["card-filter"]
    updater = PrintingFilterUpdater(card_db, card_db.db)
    with unittest.mock.patch.dict(section, {}, clear=True):
        assert_that(
            updater._remove_old_printing_filters(section),
            is_(True)
        )
    new_settings = card_db.db.execute(query).fetchall()
    assert_that(
        new_settings,
        is_(empty())
    )


@pytest.mark.parametrize("settings_key", mtg_proxy_printer.settings.get_boolean_card_filter_keys())
def test_store_current_printing_filters_updates_value_in_database(card_db: CardDatabase, settings_key: str):
    section = mtg_proxy_printer.settings.settings["card-filter"]
    settings_to_use = {filter_name: "False" for filter_name in section.keys()}
    settings_to_use[settings_key] = str(not section.getboolean(settings_key))
    updater = PrintingFilterUpdater(card_db, card_db.db)
    with unittest.mock.patch.dict(section, settings_to_use):
        assert_that(updater._changed_or_new_filters(section), is_({settings_key: True}))
        updater.run()
        assert_that(updater._changed_or_new_filters(section), is_(empty()))


@pytest.mark.parametrize("settings_key", mtg_proxy_printer.settings.get_boolean_card_filter_keys())
def test_filters_in_db_differ_from_settings_with_changed_boolean_settings_returns_changed_value(
        card_db: CardDatabase, settings_key: str):
    updater = PrintingFilterUpdater(card_db, card_db.db)
    section = mtg_proxy_printer.settings.settings["card-filter"]
    settings_to_use = {filter_name: "False" for filter_name in section.keys()}
    settings_to_use[settings_key] = str(not section.getboolean(settings_key))
    with unittest.mock.patch.dict(section, settings_to_use):
        assert_that(
            updater._changed_or_new_filters(section),
            is_({settings_key: True})
        )


def test_filters_in_db_differ_from_settings_with_unchanged_settings_returns_empty_dict(card_db: CardDatabase):
    updater = PrintingFilterUpdater(card_db, card_db.db)
    section = mtg_proxy_printer.settings.settings["card-filter"]
    settings_to_use = {filter_name: "False" for filter_name in section.keys()}
    with unittest.mock.patch.dict(section, settings_to_use):
        assert_that(
            updater._changed_or_new_filters(section),
            is_(empty())
        )


def generate_test_cases_for_test_set_code_filters_updates_value_in_database():
    sliver = TestCaseData("regular_english_card")  # English "Fury Sliver" from Time Spiral
    yield sliver, "TSP", True
    yield sliver, "tsp", True
    yield sliver, "embedded tsp in other words still works", True
    yield sliver, "ABC", False
    yield sliver, "", False


@pytest.mark.parametrize(
    "test_case, filter_value, expected_set_is_hidden",
    generate_test_cases_for_test_set_code_filters_updates_value_in_database())
def test_set_code_filters_updates_value_in_database(
        qtbot: QtBot, card_db: CardDatabase, test_case: TestCaseData, filter_value: str, expected_set_is_hidden: bool):
    fill_card_database_with_json_card(qtbot, card_db, test_case.json_dict)
    expected_card_is_visible = not expected_set_is_hidden
    section = mtg_proxy_printer.settings.settings["card-filter"]
    settings_to_use = {"hidden-sets": filter_value}
    updater = PrintingFilterUpdater(card_db, card_db.db)
    with unittest.mock.patch.dict(section, settings_to_use):
        updater.run()

    assert_that(
        card_db.db.execute(
            "SELECT set_filter_active FROM MTGSet WHERE set_code = ?", ("tsp",)
        ).fetchone(),
        contains_exactly(expected_set_is_hidden),
        "MTGSet.set_filter_active not properly updated"
    )
    assert_that(
        card_db.db.execute("SELECT is_visible FROM Printing").fetchone(),
        contains_exactly(expected_card_is_visible),
        "Printing.is_visible not properly updated"
    )



