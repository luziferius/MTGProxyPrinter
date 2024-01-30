# Copyright (C) 2020-2024 Thomas Hess <thomas.hess@udo.edu>
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

from unittest.mock import patch
import pytest
from hamcrest import *

from PySide6.QtCore import QStringListModel
from pytestqt.qtbot import QtBot

import mtg_proxy_printer.settings

from mtg_proxy_printer.ui.settings_window import SettingsWindow

FILTER_VALUES = [
    "", " ", "\n",
    "LEA", "lea", "lEA", "LEB 2X2", "OC13", "DDU \n\nABC",
]


@pytest.fixture()
def settings_window(qtbot: QtBot, document):
    language_model = QStringListModel(["en"])
    window = SettingsWindow(language_model, document)
    qtbot.add_widget(window)
    yield window


@pytest.mark.parametrize("filter_content", FILTER_VALUES)
def test_loads_set_code_filter(qtbot: QtBot, settings_window: SettingsWindow, filter_content: str):
    with patch.dict(mtg_proxy_printer.settings.settings["card-filter"], {"hidden-sets": filter_content}), \
         qtbot.wait_exposed(settings_window):
        settings_window.show()
    assert_that(
        settings_window.ui.set_filter_settings.toPlainText(), is_(equal_to(filter_content))
    )


@pytest.mark.parametrize("filter_content", FILTER_VALUES)
@patch("mtg_proxy_printer.settings.write_settings_to_file")
def test_saves_set_code_filter(qtbot: QtBot, settings_window: SettingsWindow, filter_content: str):
    with qtbot.wait_exposed(settings_window):
        settings_window.show()
    settings_window.ui.set_filter_settings.setPlainText(filter_content)
    section = mtg_proxy_printer.settings.settings["card-filter"]
    with patch.dict(section, {"hide-sets": ""}):
        settings_window.save()
        assert_that(section, has_entry("hidden-sets", equal_to(filter_content)))
