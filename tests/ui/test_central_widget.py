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


from pytestqt.qtbot import QtBot
from PySide6.QtCore import Qt
from hamcrest import *

from mtg_proxy_printer.model.document_page import Page
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard
from mtg_proxy_printer.ui.main_window import MainWindow
from tests.helpers import AsyncTaskReceiver

# Import dynamically used by pytest. Without this, the main_window fixture won’t be found by pytest.
from .test_main_window import main_window  # noqa


def test_deleting_last_card_of_current_page_does_not_raise_exception(qtbot: QtBot, main_window: MainWindow):
    card = main_window.card_database.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    document = main_window.document
    central_widget = main_window.ui.central_widget
    main_window.document.apply(ActionAddCard(card, 9))
    assert_that(
        document.pages,
        only_contains(instance_of(Page))
    )
    central_widget.ui.page_card_table_view.setCurrentIndex(document.index(8, 0, document.index(0, 0)))
    with qtbot.wait_signal(document.action_applied):
        qtbot.mouseClick(central_widget.ui.delete_selected_images_button, Qt.MouseButton.LeftButton)
    assert_that(document.pages, contains_exactly(has_length(8)))


def test_adding_new_page_enables_move_down_button(main_window: MainWindow):
    main_window.ui.action_new_page.trigger()
    assert_that(main_window.ui.central_widget.ui.page_move_down.isEnabled(), is_(True))


def test_undoing_remove_last_page_enables_move_down_button(main_window: MainWindow):
    pmd = main_window.ui.central_widget.ui.page_move_down
    ui = main_window.ui
    ui.action_new_page.trigger()
    ui.central_widget.select_first_page(True, 1)
    ui.action_discard_page.trigger()
    assert_that(pmd.isEnabled(), is_(False), "Test setup failed")
    ui.action_undo.trigger()
    assert_that(pmd.isEnabled(), is_(True))

def test_clicking_move_page_button_triggers_only_once(main_window: MainWindow):
    main_window.ui.action_new_page.trigger()
    main_window.ui.central_widget.ui.page_move_down.click()
    assert_that(
        main_window.document.get_current_page_index().row(), is_(1),
        "Current page in document not updated")
    assert_that(
        main_window.ui.central_widget.ui.document_view.selectionModel().currentIndex().row(), is_(1),
        "Currently selected page not updated")
