# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>

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

from PyQt5.QtCore import QStringListModel

from hamcrest import *
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.ui.settings_window import SettingsWindow


def test_first_tab_is_selected_when_shown(qtbot: QtBot, document):
    language_model = QStringListModel(["en"])
    dialog = SettingsWindow(language_model, document)
    ui = dialog.ui
    qtbot.addWidget(dialog)
    with qtbot.waitExposed(dialog):
        dialog.show()
    assert_that(
        ui.tab_widget.currentIndex(), is_(0),
        "Wrong initial tab selected. Fix the settings window UI file."
    )
