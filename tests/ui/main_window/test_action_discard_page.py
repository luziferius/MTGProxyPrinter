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

from pytestqt.qtbot import QtBot
from hamcrest import *

from mtg_proxy_printer.ui.main_window import MainWindow
# This import is used dynamically by pytest to resolve the main_window fixture and cannot be removed.
from ..test_main_window import main_window  # noqa


def test_main_window_action_discard_page(qtbot: QtBot, main_window: MainWindow):
    ui = main_window.ui
    document = main_window.document
    selection_model = ui.central_widget.ui.document_view.selectionModel()
    assert_that(selection_model.selectedRows(0), has_length(1))
    assert_that(selection_model.selectedRows(0)[0].row(), is_(equal_to(0)))
    assert_that(document.rowCount(), is_(equal_to(1)))
    with qtbot.wait_signal(ui.action_new_page.triggered, timeout=100):
        ui.action_new_page.trigger()
    assert_that(selection_model.selectedRows(0), has_length(1))
    assert_that(selection_model.selectedRows(0)[0].row(), is_(equal_to(0)))
    assert_that(document.rowCount(), is_(equal_to(2)))
    with qtbot.wait_signal(ui.action_discard_page.triggered, timeout=100), \
            qtbot.wait_signal(selection_model.selectionChanged, timeout=100):
        ui.action_discard_page.trigger()
    assert_that(document.rowCount(), is_(equal_to(1)))
