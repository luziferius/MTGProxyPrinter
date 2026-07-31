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
from unittest.mock import patch

import pytest
from hamcrest import *

from pytestqt.qtbot import QtBot

import mtg_proxy_printer
from mtg_proxy_printer.async_tasks.printing_filter_updater import PrintingFilterUpdater, PrintingPreferenceUpdater
from tests.hasgetter import has_getter
from mtg_proxy_printer.model.printing_filter_model import PrintingFilterModel
from mtg_proxy_printer.model.set_list import MTGSetTreeModel, MTGSetTreeFilterModel

from mtg_proxy_printer.ui.settings_window_pages import PrintingPreferencesPage
import mtg_proxy_printer.settings
from mtg_proxy_printer.units_and_sizes import ConfigParser


@pytest.fixture()
def printing_preferences_page(qtbot: QtBot, document) -> PrintingPreferencesPage:
    page = PrintingPreferencesPage()
    page.card_db = document.card_db
    qtbot.add_widget(page)
    return page


def test_page_has_printing_filter_model(printing_preferences_page: PrintingPreferencesPage):
    assert_that(printing_preferences_page.printing_filter_model, instance_of(PrintingFilterModel))
    assert_that(printing_preferences_page.ui.printing_filter_view, has_getter("model", equal_to(printing_preferences_page.printing_filter_model)))


def test_page_has_set_filter_model(printing_preferences_page: PrintingPreferencesPage):
    assert_that(printing_preferences_page.set_filter_model, instance_of(MTGSetTreeModel))
    assert_that(printing_preferences_page.set_filter_proxy_model, instance_of(MTGSetTreeFilterModel))
    assert_that(printing_preferences_page.set_filter_proxy_model, has_getter("sourceModel", equal_to(printing_preferences_page.set_filter_model)))
    assert_that(printing_preferences_page.ui.set_filter_view, has_getter("model", equal_to(printing_preferences_page.set_filter_proxy_model)))


def test_highlight_differing_settings_delegates_to_models(printing_preferences_page: PrintingPreferencesPage):
    settings = ConfigParser()
    with (patch.object(printing_preferences_page, "printing_filter_model") as printing_filter_model,
            patch.object(printing_preferences_page, "set_filter_proxy_model") as set_filter_proxy_model):
        printing_preferences_page.highlight_differing_settings(settings)
    printing_filter_model.highlight_differing_settings.assert_called_once_with(settings)
    set_filter_proxy_model.highlight_differing_settings.assert_called_once_with(settings)


def test_clear_highlight_delegates_to_models(printing_preferences_page: PrintingPreferencesPage):
    with (patch.object(printing_preferences_page, "printing_filter_model") as printing_filter_model,
            patch.object(printing_preferences_page, "set_filter_proxy_model") as set_filter_proxy_model):
        printing_preferences_page.clear_highlight()
    printing_filter_model.clear_highlight.assert_called_once_with()
    set_filter_proxy_model.clear_highlight.assert_called_once_with()


def test_save(qtbot: QtBot, printing_preferences_page: PrintingPreferencesPage):
    expected_signals = [printing_preferences_page.request_run_async_task]*2
    expected_signal_params = [
        lambda param: isinstance(param, PrintingFilterUpdater),
        lambda param: isinstance(param, PrintingPreferenceUpdater),
    ]
    with (patch.object(printing_preferences_page, "printing_filter_model") as printing_filter_model,
            patch.object(printing_preferences_page, "set_filter_model") as set_filter_model,
            qtbot.wait_signals(expected_signals, check_params_cbs=expected_signal_params)):
        printing_preferences_page.save()
    printing_filter_model.save_settings.assert_called_once_with(mtg_proxy_printer.settings.settings)
    set_filter_model.save_settings.assert_called_once_with(mtg_proxy_printer.settings.settings)
