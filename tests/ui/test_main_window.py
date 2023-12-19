# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>
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

import dataclasses
import pathlib
import unittest.mock
import socket
import urllib.error


from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import QMessageBox
from pytestqt.qtbot import QtBot
from hamcrest import *
import pytest

from mtg_proxy_printer.stop_thread import stop_thread
import mtg_proxy_printer.http_file
import mtg_proxy_printer.downloader_base
from mtg_proxy_printer.sqlite_helpers import open_database
from mtg_proxy_printer.card_info_downloader import CardInfoDownloader
from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.model.imagedb import ImageDatabase
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.document_loader import DocumentLoader, PageLayoutSettings
from mtg_proxy_printer.ui.main_window import MainWindow
from mtg_proxy_printer.ui.central_widget import Ui_CentralWidget_Columnar, Ui_CentralWidget_Grouped, \
    Ui_CentralWidget_Tabbed
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage

from tests.helpers import fill_card_database_with_json_cards
from tests.document_controller.helpers import insert_card_in_page


@pytest.fixture(params=[Ui_CentralWidget_Columnar, Ui_CentralWidget_Grouped, Ui_CentralWidget_Tabbed])
def main_window(qtbot, card_db: CardDatabase, document: Document, request) -> MainWindow:
    fill_card_database_with_json_cards(qtbot, card_db, ["regular_english_card", "oversized_card"])
    with unittest.mock.patch(
            "mtg_proxy_printer.ui.central_widget.get_configured_central_widget_layout_class",
            return_value=request.param), \
            unittest.mock.patch.object(mtg_proxy_printer.ui.main_window.MainWindow, "on_action_quit_triggered"), \
            unittest.mock.patch.object(
                mtg_proxy_printer.card_info_downloader.CardInfoDatabaseImportWorker, "get_scryfall_bulk_card_data_url",
                return_value=(unittest.mock.MagicMock(), 10)), \
            unittest.mock.patch.object(
                mtg_proxy_printer.card_info_downloader.CardInfoDatabaseImportWorker, "read_json_card_data_from_url",
                return_value=iter([10])):
        cid = CardInfoDownloader(card_db)
        main_window = MainWindow(card_db, cid, document.image_db, document, QStringListModel(["en"]))
        qtbot.add_widget(main_window)
        with qtbot.wait_exposed(main_window, timeout=1000):
            main_window.show()
        yield main_window
        main_window.hide()
        stop_thread(cid.worker_thread)
        del cid
        main_window.__dict__.clear()


def test_main_window_hides_progress_bar_after_downloading_image_during_load(
        qtbot: QtBot, main_window: MainWindow):
    with unittest.mock.patch.object(  # Mock all HTTP-specific I/O calls
                mtg_proxy_printer.downloader_base.mtg_proxy_printer.http_file.MeteredSeekableHTTPFile,
                "_read_content_length") as cl_mock, \
            unittest.mock.patch.object(
                mtg_proxy_printer.downloader_base.mtg_proxy_printer.http_file.MeteredSeekableHTTPFile,
                "getcode", return_value=200), \
            unittest.mock.patch.object(
                mtg_proxy_printer.downloader_base.mtg_proxy_printer.http_file.MeteredSeekableHTTPFile,
                "content_encoding", return_value="identity"), \
            unittest.mock.patch.object(
                mtg_proxy_printer.downloader_base.mtg_proxy_printer.http_file.MeteredSeekableHTTPFile,
                "seekable", return_value=True), \
            unittest.mock.patch("mtg_proxy_printer.ui.main_window.QMessageBox.warning") as mb1, \
            unittest.mock.patch("mtg_proxy_printer.ui.main_window.QMessageBox.critical") as mb2:
        temp_path = main_window.image_db.db_path
        mock_image_path = _create_mock_image(main_window.image_db, temp_path)
        cl_mock.return_value = mock_image_path.stat().st_size
        main_window.card_database.db.execute("UPDATE CardFace SET png_image_uri = ?", (mock_image_path.as_uri(),))
        save_file_path = _create_save_file(temp_path)

        assert_that(main_window.progress_bars.ui.inner_progress_bar.isVisible(), is_(False))
        assert_that(main_window.progress_bars.ui.outer_progress_bar.isVisible(), is_(False))
        assert_that(main_window.progress_bars.ui.inner_progress_label.isVisible(), is_(False))
        assert_that(main_window.progress_bars.ui.outer_progress_label.isVisible(), is_(False))

        with qtbot.wait_signal(main_window.document.loader.worker_thread.finished, timeout=1000):
            main_window.document.loader.load_document(save_file_path)
            
    assert_that(main_window.progress_bars.ui.inner_progress_bar.isVisible(), is_(False))
    assert_that(main_window.progress_bars.ui.outer_progress_bar.isVisible(), is_(False))
    assert_that(main_window.progress_bars.ui.inner_progress_label.isVisible(), is_(False))
    assert_that(main_window.progress_bars.ui.outer_progress_label.isVisible(), is_(False))
    mb1.assert_not_called()
    mb2.assert_not_called()


def _create_mock_image(image_db: ImageDatabase, temp_path: pathlib.Path) -> pathlib.Path:
    mock_image_path = temp_path / 'temp' / "0000579f-7b35-4ed3-b44c-db2a538066fe.png"
    mock_image_path.parent.mkdir(parents=True, exist_ok=False)
    image_db.blank_image.save(str(mock_image_path), "PNG", 100)
    assert_that(mock_image_path.is_file(), is_(True))
    return mock_image_path


def _create_save_file(temp_path: pathlib.Path):
    save_file_path = temp_path/"test.mtgproxies"
    settings = dataclasses.asdict(PageLayoutSettings.create_from_settings()).items()
    with open_database(save_file_path, "document-v6", DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION) as save_file:
        save_file.execute(
            "INSERT INTO Card (page, slot, is_front, scryfall_id, type) VALUES (?, ?, ?, ?, ?)",
            (1, 1, True, "0000579f-7b35-4ed3-b44c-db2a538066fe", "r")
        )
        save_file.executemany(
            "INSERT INTO DocumentSettings (key, value) VALUES (?, ?)",
            settings
        )
    return save_file_path


def test_declining_card_data_update_offer_results_in_no_action(qtbot: QtBot, main_window: MainWindow):
    ui = main_window.ui
    ui.action_download_card_data.setEnabled(False)
    with unittest.mock.patch.object(
            mtg_proxy_printer.ui.main_window.QMessageBox, "question", return_value=QMessageBox.No) as message_box, \
            qtbot.assertNotEmitted(main_window.loading_state_changed):
        main_window.show_card_data_update_available_message_box(10000)
    message_box.assert_called_once()
    main_window.card_data_downloader.database_import_worker.get_scryfall_bulk_card_data_url.assert_not_called()
    main_window.card_data_downloader.database_import_worker.read_json_card_data_from_url.assert_not_called()
    assert_that(ui.action_download_card_data.isEnabled(), is_(True))


def test_accepting_card_data_update_offer_results_in_performed_action(qtbot: QtBot, main_window: MainWindow):
    ui = main_window.ui
    ui.action_download_card_data.setEnabled(True)
    with unittest.mock.patch.object(
            mtg_proxy_printer.ui.main_window.QMessageBox, "question", return_value=QMessageBox.Yes) as message_box, \
            qtbot.waitSignal(main_window.card_data_downloader.working_state_changed, check_params_cb=lambda value: not value), \
            qtbot.waitSignal(main_window.card_data_downloader.request_import_from_url, timeout=1000):
        main_window.show_card_data_update_available_message_box(10000)
    message_box.assert_called_once()
    main_window.card_data_downloader.database_import_worker.get_scryfall_bulk_card_data_url.assert_called_once()
    assert_that(
        main_window.card_data_downloader.database_import_worker.read_json_card_data_from_url,
        has_property("call_count", equal_to(2))
    )
    assert_that(ui.action_download_card_data.isEnabled(), is_(False))


@pytest.mark.parametrize("handled_error", [socket.timeout, urllib.error.URLError("Test reason")])
def test_action_download_card_data_enabled_if_error_occurs_after_accepting_card_data_update_offer(
        qtbot: QtBot, main_window: MainWindow, handled_error):
    ui = main_window.ui
    main_window.card_data_downloader.database_import_worker.get_scryfall_bulk_card_data_url.side_effect = handled_error
    ui.action_download_card_data.setEnabled(True)
    with unittest.mock.patch.object(
            mtg_proxy_printer.ui.main_window.QMessageBox, "question", return_value=QMessageBox.Yes) as message_box, \
        unittest.mock.patch.object(
            mtg_proxy_printer.ui.main_window.QMessageBox, "warning", return_value=QMessageBox.Yes) as warning_box, \
            qtbot.waitSignal(main_window.card_data_downloader.working_state_changed, check_params_cb=lambda value: not value), \
            qtbot.waitSignal(main_window.card_data_downloader.network_error_occurred):
        main_window.show_card_data_update_available_message_box(10000)
    message_box.assert_called_once()
    warning_box.assert_called_once()
    main_window.card_data_downloader.database_import_worker.get_scryfall_bulk_card_data_url.assert_called_once()
    main_window.card_data_downloader.database_import_worker.read_json_card_data_from_url.assert_not_called()
    assert_that(
        ui.action_download_card_data.isEnabled(), is_(True), "Action not re-enabled after error condition"
    )


@pytest.mark.parametrize("handled_error", [socket.timeout, urllib.error.URLError("Test reason")])
def test_action_download_card_data_enabled_if_error_occurs_after_triggering_it(
        qtbot: QtBot, main_window: MainWindow, handled_error):
    ui = main_window.ui
    main_window.card_data_downloader.database_import_worker.get_scryfall_bulk_card_data_url.side_effect = handled_error
    ui.action_download_card_data.setEnabled(True)
    with unittest.mock.patch.object(
            mtg_proxy_printer.ui.main_window.QMessageBox, "warning", return_value=QMessageBox.Yes) as warning_box, \
            qtbot.waitSignal(main_window.card_data_downloader.working_state_changed, check_params_cb=lambda value: not value), \
            qtbot.waitSignal(main_window.card_data_downloader.network_error_occurred):
        ui.action_download_card_data.trigger()
    warning_box.assert_called_once()
    main_window.card_data_downloader.database_import_worker.get_scryfall_bulk_card_data_url.assert_called_once()
    main_window.card_data_downloader.database_import_worker.read_json_card_data_from_url.assert_not_called()
    assert_that(
        ui.action_download_card_data.isEnabled(), is_(True), "Action not re-enabled after error condition"
    )


def test_declining_ask_user_about_empty_database_results_in_no_action(qtbot: QtBot, main_window: MainWindow):
    ui = main_window.ui
    ui.action_download_card_data.setEnabled(True)
    with unittest.mock.patch.object(
            mtg_proxy_printer.ui.main_window.QMessageBox, "question", return_value=QMessageBox.No) as message_box, \
            qtbot.assertNotEmitted(main_window.loading_state_changed):
        main_window.ask_user_about_empty_database()
    message_box.assert_called_once()
    main_window.card_data_downloader.database_import_worker.get_scryfall_bulk_card_data_url.assert_not_called()
    main_window.card_data_downloader.database_import_worker.read_json_card_data_from_url.assert_not_called()
    assert_that(ui.action_download_card_data.isEnabled(), is_(True))


def test_accepting_ask_user_about_empty_database_results_in_performed_action(qtbot: QtBot, main_window: MainWindow):
    ui = main_window.ui
    ui.action_download_card_data.setEnabled(True)
    with unittest.mock.patch.object(
            mtg_proxy_printer.ui.main_window.QMessageBox, "question", return_value=QMessageBox.Yes) as message_box, \
            qtbot.waitSignal(main_window.card_data_downloader.working_state_changed, check_params_cb=lambda value: not value), \
            qtbot.waitSignal(main_window.card_data_downloader.request_import_from_url, timeout=1000):
        main_window.ask_user_about_empty_database()
    message_box.assert_called_once()
    main_window.card_data_downloader.database_import_worker.get_scryfall_bulk_card_data_url.assert_called_once()
    assert_that(
        main_window.card_data_downloader.database_import_worker.read_json_card_data_from_url,
        has_property("call_count", equal_to(2))
    )
    assert_that(ui.action_download_card_data.isEnabled(), is_(False))


@pytest.mark.parametrize("handled_error", [socket.timeout, urllib.error.URLError("Test reason")])
def test_action_download_card_data_enabled_if_error_occurs_after_accepting_ask_user_about_empty_database(
        qtbot: QtBot, main_window: MainWindow, handled_error):
    ui = main_window.ui
    main_window.card_data_downloader.database_import_worker.get_scryfall_bulk_card_data_url.side_effect = handled_error
    ui.action_download_card_data.setEnabled(True)
    with unittest.mock.patch.object(
            mtg_proxy_printer.ui.main_window.QMessageBox, "question", return_value=QMessageBox.Yes) as message_box, \
        unittest.mock.patch.object(
            mtg_proxy_printer.ui.main_window.QMessageBox, "warning", return_value=QMessageBox.Yes) as warning_box, \
            qtbot.waitSignal(main_window.card_data_downloader.working_state_changed, check_params_cb=lambda value: not value), \
            qtbot.waitSignal(main_window.card_data_downloader.network_error_occurred):
        main_window.ask_user_about_empty_database()
    message_box.assert_called_once()
    warning_box.assert_called_once()
    main_window.card_data_downloader.database_import_worker.get_scryfall_bulk_card_data_url.assert_called_once()
    main_window.card_data_downloader.database_import_worker.read_json_card_data_from_url.assert_not_called()
    assert_that(
        ui.action_download_card_data.isEnabled(), is_(True), "Action not re-enabled after error condition"
    )


def test_accepting_application_update_offer_opens_website_in_default_browser(main_window: MainWindow):
    with unittest.mock.patch.object(
        mtg_proxy_printer.ui.main_window.QMessageBox, "question", return_value=QMessageBox.Yes) as message_box, \
        unittest.mock.patch.object(
            mtg_proxy_printer.ui.main_window.QDesktopServices, "openUrl") as open_url_service:
        main_window.show_application_update_available_message_box("1.0.0-test")
        message_box.assert_called_once()
        open_url_service.assert_called_once()


def test_declining_application_update_offer_does_nothing(main_window: MainWindow):
    with unittest.mock.patch.object(
        mtg_proxy_printer.ui.main_window.QMessageBox, "question", return_value=QMessageBox.No) as message_box, \
        unittest.mock.patch.object(
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
    document.page_layout.draw_cut_markers = True
    document.page_layout_changed.emit(document.page_layout)
    ui.action_new_page.trigger()  # Condition 2
    assert_that(document.pages, has_length(2))
    with qtbot.waitSignal(document.current_page_changed):
        ui.central_widget.ui.document_view.setCurrentIndex(document.index(1, 0))  # Condition 3
    with unittest.mock.patch.object(
            mtg_proxy_printer.ui.main_window.QMessageBox, "question", return_value=QMessageBox.Yes), \
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
    card.image_file = main_window.image_db.blank_image
    action = ActionImportDeckList(
        [card]*page_capacity*2,
        False
    )
    document.apply(action)
    document_view = main_window.ui.central_widget.ui.document_view
    document_view.setCurrentIndex(document.index(1, 0))
    main_window.ui.action_undo.trigger()
    assert_that(main_window.document.rowCount(), is_(1))
