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


import unittest.mock

import pytest
from hamcrest import *

from mtg_proxy_printer.async_tasks.printing_filter_updater import PrintingFilterUpdater
import mtg_proxy_printer.settings
from mtg_proxy_printer.model.carddb import CardDatabase


def test__remove_old_printing_filters_with_unchanged_boolean_settings_does_nothing(card_db: CardDatabase):
    query = "SELECT * FROM DisplayFilters ORDER BY filter_id ASC"
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
    query = "SELECT * FROM DisplayFilters ORDER BY filter_id ASC"
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
        assert_that(updater._filters_in_db_differ_from_settings(section), is_(True))
        updater.run()
        assert_that(updater._filters_in_db_differ_from_settings(section), is_(False))


@pytest.mark.parametrize("settings_key", mtg_proxy_printer.settings.get_boolean_card_filter_keys())
def test_filters_in_db_differ_from_settings_with_changed_boolean_settings_returns_true(
        card_db: CardDatabase, settings_key: str):
    updater = PrintingFilterUpdater(card_db, card_db.db)
    section = mtg_proxy_printer.settings.settings["card-filter"]
    settings_to_use = {filter_name: "False" for filter_name in section.keys()}
    settings_to_use[settings_key] = str(not section.getboolean(settings_key))
    with unittest.mock.patch.dict(section, settings_to_use):
        assert_that(
            updater._filters_in_db_differ_from_settings(section),
            is_(True)
        )


def test_filters_in_db_differ_from_settings_with_unchanged_settings_returns_false(card_db: CardDatabase):
    updater = PrintingFilterUpdater(card_db, card_db.db)
    section = mtg_proxy_printer.settings.settings["card-filter"]
    settings_to_use = {filter_name: "False" for filter_name in section.keys()}
    with unittest.mock.patch.dict(section, settings_to_use):
        assert_that(
            updater._filters_in_db_differ_from_settings(section),
            is_(False)
        )
