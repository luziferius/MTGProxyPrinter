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


from collections import Counter
from collections.abc import Generator
import pathlib
from unittest.mock import patch, MagicMock

from PySide6.QtCore import QStringListModel
from PySide6.QtWidgets import QMessageBox
from pytestqt.qtbot import QtBot
from hamcrest import *
import pytest

import mtg_proxy_printer.http_file
import mtg_proxy_printer.async_tasks.downloader_base
import mtg_proxy_printer.async_tasks.card_info_downloader
from mtg_proxy_printer.async_tasks.card_info_downloader import ApiStreamTask, DatabaseImportTask
from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.ui.main_window import MainWindow
from mtg_proxy_printer.ui.central_widget import Ui_ColumnarCentralWidget, Ui_GroupedCentralWidget, \
    Ui_TabbedCentralWidget
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage
from mtg_proxy_printer.async_tasks.base import AsyncTask

from tests.helpers import fill_card_database_with_json_cards, AsyncTaskReceiver
from tests.document_controller.helpers import insert_card_in_page
StandardButton = QMessageBox.StandardButton


def _create_task_receiver(main_window: MainWindow) -> AsyncTaskReceiver:
    receiver = AsyncTaskReceiver(main_window)
    main_window.request_run_async_task.connect(receiver.receive_task)
    return receiver


@pytest.fixture(params=[Ui_ColumnarCentralWidget, Ui_GroupedCentralWidget, Ui_TabbedCentralWidget])
def main_window(qtbot, card_db: CardDatabase, document: Document, request) -> Generator[MainWindow, None, None]:
    fill_card_database_with_json_cards(qtbot, card_db, ["regular_english_card", "oversized_card"])
    with patch(
            "mtg_proxy_printer.ui.central_widget.get_configured_central_widget_layout_class",
            return_value=request.param), \
            patch.object(mtg_proxy_printer.ui.main_window.MainWindow, "on_action_quit_triggered"), \
            patch.object(
                mtg_proxy_printer.async_tasks.card_info_downloader.ApiStreamTask, "get_scryfall_bulk_card_data_url",
                return_value=(MagicMock(), 10)), \
            patch.object(
                mtg_proxy_printer.async_tasks.card_info_downloader.ApiStreamTask, "read_json_card_data_from",
                return_value=iter([10])):
        main_window = MainWindow(card_db, document.image_db, document, QStringListModel(["en"]))
        qtbot.add_widget(main_window)
        with qtbot.wait_exposed(main_window, timeout=1000):
            main_window.show()
        yield main_window
        main_window.hide()

        main_window.__dict__.clear()


def test_declining_card_data_update_offer_results_in_no_action(qtbot: QtBot, main_window: MainWindow):
    ui = main_window.ui
    ui.action_download_card_data.setEnabled(False)
    with patch.object(
            mtg_proxy_printer.ui.main_window.QMessageBox, "question", return_value=StandardButton.No), \
            qtbot.assert_not_emitted(main_window.request_run_async_task):
        main_window.show_card_data_update_available_message_box(10000)


def test_accepting_card_data_update_offer_results_in_performed_action(main_window: MainWindow):
    ui = main_window.ui
    ui.action_download_card_data.setEnabled(True)
    received = _create_task_receiver(main_window)
    with patch.object(
        mtg_proxy_printer.ui.main_window.QMessageBox,
            "question", return_value=StandardButton.Yes) as message_box:
        main_window.show_card_data_update_available_message_box(10000)
    message_box.assert_called_once()
    assert_that(
        received.tasks, contains_inanyorder(instance_of(ApiStreamTask), instance_of(DatabaseImportTask))
    )


def test_action_download_card_data_disables_itself(main_window: MainWindow):
    ui = main_window.ui
    ui.action_download_card_data.trigger()
    assert_that(ui.action_download_card_data.isEnabled(), is_(False))


def test_action_download_card_data_is_enabled_after_network_error(main_window: MainWindow):
    ui = main_window.ui
    receiver = _create_task_receiver(main_window)
    ui.action_download_card_data.trigger()
    # This connection is created by Application
    receiver.api_stream_task.network_error_occurred.connect(main_window.on_network_error_occurred)
    if ui.action_download_card_data.isEnabled():
        pytest.skip("Test setup failed")
    with patch.object(
        mtg_proxy_printer.ui.main_window.QMessageBox, "warning", return_value=StandardButton.Ok
    ) as warning_box:
        receiver.api_stream_task.network_error_occurred.emit("Test reason")
    warning_box.assert_called_once()
    assert_that(ui.action_download_card_data.isEnabled(), is_(True))


@pytest.mark.parametrize("task_raising_error", [ApiStreamTask, DatabaseImportTask])
def test_action_download_card_data_is_enabled_after_other_error(
        main_window: MainWindow, task_raising_error: type[AsyncTask]):
    ui = main_window.ui
    receiver = _create_task_receiver(main_window)
    ui.action_download_card_data.trigger()
    # This connection is created by Application
    receiver.api_stream_task.error_occurred.connect(main_window.on_error_occurred)
    receiver.database_import_task.error_occurred.connect(main_window.on_error_occurred)
    if ui.action_download_card_data.isEnabled():
        pytest.skip("Test setup failed")
    failing_task = receiver.find_task(task_raising_error)
    MB = mtg_proxy_printer.ui.main_window.QMessageBox
    Ok = StandardButton.Ok
    with (patch.object(MB, "warning", return_value=Ok) as warning_box,  # Network error
          patch.object(MB, "critical", return_value=Ok) as error_box,  # Other error
          ):
        failing_task.error_occurred.emit("Test reason")
    assert_that(ui.action_download_card_data.isEnabled(), is_(True))
    assert_that(warning_box.call_count+error_box.call_count, is_(1))


def test_declining_ask_user_about_empty_database_results_in_no_action(qtbot: QtBot, main_window: MainWindow):
    ui = main_window.ui
    ui.action_download_card_data.setEnabled(True)
    with patch.object(
            mtg_proxy_printer.ui.main_window.QMessageBox, "question", return_value=StandardButton.No) as message_box, \
        patch("mtg_proxy_printer.async_tasks.card_info_downloader.ApiStreamTask.run") as stream_run, \
        patch("mtg_proxy_printer.async_tasks.card_info_downloader.DatabaseImportTask.run") as import_run, \
            qtbot.assert_not_emitted(main_window.request_run_async_task):
        main_window.ask_user_about_empty_database()
    message_box.assert_called_once()
    stream_run.assert_not_called()
    import_run.assert_not_called()
    assert_that(ui.action_download_card_data.isEnabled(), is_(True))


def test_accepting_ask_user_about_empty_database_results_in_performed_action(qtbot: QtBot, main_window: MainWindow):
    ui = main_window.ui
    ui.action_download_card_data.setEnabled(True)
    with patch.object(
            mtg_proxy_printer.ui.main_window.QMessageBox, "question", return_value=StandardButton.Yes
            ) as message_box, \
            qtbot.wait_signal(
                main_window.request_run_async_task, check_params_cb=lambda task: isinstance(task, ApiStreamTask)), \
            qtbot.wait_signal(
                main_window.request_run_async_task, check_params_cb=lambda task: isinstance(task, DatabaseImportTask)):
        main_window.ask_user_about_empty_database()
    message_box.assert_called_once()


def test_accepting_application_update_offer_opens_website_in_default_browser(main_window: MainWindow):
    with patch.object(
        mtg_proxy_printer.ui.main_window.QMessageBox, "question", return_value=StandardButton.Yes) as message_box, \
        patch.object(
            mtg_proxy_printer.ui.main_window.QDesktopServices, "openUrl") as open_url_service:
        main_window.show_application_update_available_message_box("1.0.0-test")
        message_box.assert_called_once()
        open_url_service.assert_called_once()


def test_declining_application_update_offer_does_nothing(main_window: MainWindow):
    with patch.object(
        mtg_proxy_printer.ui.main_window.QMessageBox, "question", return_value=StandardButton.No) as message_box, \
        patch.object(
            mtg_proxy_printer.ui.main_window.QDesktopServices, "openUrl") as open_url_service:
        main_window.show_application_update_available_message_box("1.0.0-test")
        message_box.assert_called_once()
        open_url_service.assert_not_called()


def test_creating_new_document_with_second_page_selected_works_without_raising_exception(
        qtbot: QtBot, main_window: MainWindow):
    """
    Tests for an exception when creating a new document. Conditions required for reproduction:
    - Cut markers enabled
    - At least two pages present
    - Any page but the first is currently selected
    - User creates a new document
    """
    ui = main_window.ui
    document = main_window.document
    # Condition 1
    document.page_layout.cut_marker_style = "Solid"
    document.page_layout_changed.emit(document.page_layout, {"cut_marker_style"})
    ui.action_new_page.trigger()  # Condition 2
    assert_that(document.pages, has_length(2))
    with qtbot.waitSignal(document.current_page_changed):
        ui.central_widget.ui.document_view.setCurrentIndex(document.index(1, 0))  # Condition 3
    with patch.object(
            mtg_proxy_printer.ui.main_window.QMessageBox, "question", return_value=StandardButton.Yes), \
            qtbot.waitSignal(document.current_page_changed):
        # Condition 4. This triggered the exception
        ui.action_new_document.trigger()
    assert_that(document.pages, has_length(1))


def test_compacting_document_while_last_page_is_selected_works_without_raising_exception(main_window: MainWindow):
    """
    Tests for an exception when compacting the document. Conditions required for reproduction:
    - 4 pages. Two with one regular card, two with one oversized card each
    - Page capacity at least 2 for each page type
    - Last page is selected
    - User compacts the document
    """
    ui = main_window.ui
    document = main_window.document
    cards = [
        main_window.card_database.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True),
        main_window.card_database.get_card_with_scryfall_id("650722b4-d72b-4745-a1a5-00a34836282b", True)
    ]*2
    pages = main_window.document.pages
    document.apply(ActionNewPage(count=len(cards)))
    for _ in map(insert_card_in_page, pages, cards):
        pass
    ui.central_widget.ui.document_view.setCurrentIndex(document.index(4, 0))
    ui.action_compact_document.trigger()
    assert_that(document.rowCount(), is_(2))


def test_removing_last_page_while_selected_works_without_raising_exception(main_window: MainWindow):
    ui = main_window.ui
    main_window.document.apply(ActionNewPage())
    ui.central_widget.ui.document_view.setCurrentIndex(main_window.document.index(1, 0))
    ui.action_discard_page.trigger()
    assert_that(main_window.document.rowCount(), is_(1))


def test_undo_load_document_with_middle_page_selected_works_without_raising_exception(main_window: MainWindow):
    from mtg_proxy_printer.document_controller.load_document import ActionLoadDocument
    document = main_window.document
    card = main_window.card_database.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    action = ActionLoadDocument(pathlib.Path(), [
        [card], [card], [card]
    ], document.page_layout)
    document.apply(action)
    document_view = main_window.ui.central_widget.ui.document_view
    document_view.setCurrentIndex(document.index(1, 0))
    main_window.ui.action_undo.trigger()
    assert_that(main_window.document.rowCount(), is_(1))


def test_undo_import_deck_list_with_last_page_selected_works_without_raising_exception(main_window):
    from mtg_proxy_printer.document_controller.import_deck_list import ActionImportDeckList
    document = main_window.document
    card = main_window.card_database.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    page_capacity = document.page_layout.compute_page_card_capacity(card.requested_page_type())
    card.image_file = main_window.image_db.get_blank()
    action = ActionImportDeckList(
        Counter({card: page_capacity*2}),
        False
    )
    document.apply(action)
    document_view = main_window.ui.central_widget.ui.document_view
    document_view.setCurrentIndex(document.index(1, 0))
    main_window.ui.action_undo.trigger()
    assert_that(main_window.document.rowCount(), is_(1))
