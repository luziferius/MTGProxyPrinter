#  Copyright © 2020-2025.  Thomas Hess <thomas.hess@udo.edu>
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

import mtg_proxy_printer.settings

from mtg_proxy_printer.ui.settings_window_pages import HidePrintingsPage

FILTER_VALUES = [
    "", " ", "\n",
    "LEA", "lea", "lEA", "LEB 2X2", "OC13", "DDU \n\nABC",
]


@pytest.fixture()
def hide_printings_page(qtbot: QtBot, document) -> HidePrintingsPage:
    page = HidePrintingsPage()
    qtbot.add_widget(page)
    return page


@pytest.mark.parametrize("filter_content", FILTER_VALUES)
def test_loads_set_code_filter(qtbot: QtBot, hide_printings_page: HidePrintingsPage, filter_content: str):
    with patch.dict(mtg_proxy_printer.settings.settings["card-filter"], {"hidden-sets": filter_content}), \
         qtbot.wait_exposed(hide_printings_page):
        hide_printings_page.load(mtg_proxy_printer.settings.settings)
        hide_printings_page.show()
    assert_that(
        hide_printings_page.ui.set_filter_settings.toPlainText(), is_(equal_to(filter_content))
    )


@pytest.mark.parametrize("filter_content", FILTER_VALUES)
@patch("mtg_proxy_printer.settings.write_settings_to_file")
def test_saves_set_code_filter(qtbot: QtBot, hide_printings_page: HidePrintingsPage, card_db, filter_content: str):
    hide_printings_page.card_db = card_db
    with qtbot.wait_exposed(hide_printings_page):
        hide_printings_page.ui.set_filter_settings.setPlainText(filter_content)
        hide_printings_page.show()
    section = mtg_proxy_printer.settings.settings["card-filter"]
    with patch.dict(section, {"hide-sets": ""}):
        hide_printings_page.save()
        assert_that(section, has_entry("hidden-sets", equal_to(filter_content)))
