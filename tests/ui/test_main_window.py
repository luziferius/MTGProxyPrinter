# Copyright (C) 2021 Thomas Hess <thomas.hess@udo.edu>

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

import pathlib
from tempfile import TemporaryDirectory
import unittest.mock
import socket
import urllib.error

from PySide6.QtCore import QStringListModel
from PySide6.QtWidgets import QMessageBox
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
from mtg_proxy_printer.model.document_loader import DocumentLoader
from mtg_proxy_printer.ui.main_window import MainWindow
from mtg_proxy_printer.ui.central_widget import ColumnarCentralWidget, GroupedCentralWidget, TabbedVerticalCentralWidget
from tests.helpers import fill_card_database_with_json_card


@pytest.fixture(params=[ColumnarCentralWidget, GroupedCentralWidget, TabbedVerticalCentralWidget])
def main_window(qtbot, card_db: CardDatabase, request) -> MainWindow:
    fill_card_database_with_json_card(qtbot, card_db, "regular_english_card")
    with TemporaryDirectory() as temp_dir, unittest.mock.patch(
            "mtg_proxy_printer.ui.main_window.get_configured_central_widget_layout_class",
            return_value=request.param), \
            unittest.mock.patch.object(mtg_proxy_printer.ui.main_window.MainWindow, "on_action_quit_triggered"), \
            unittest.mock.patch.object(
                mtg_proxy_printer.card_info_downloader.CardInfoDownloadWorker, "get_scryfall_bulk_card_data_url"), \
            unittest.mock.patch.object(
                mtg_proxy_printer.card_info_downloader.CardInfoDownloadWorker, "read_json_card_data",
                return_value=tuple()):
        temp_path = pathlib.Path(temp_dir)
        image_db = ImageDatabase(temp_path)
        cid = CardInfoDownloader(card_db)
        document = Document(card_db, image_db)
        main_window = MainWindow(card_db, cid, image_db, document, QStringListModel(["en"]))
        qtbot.add_widget(main_window)
        with qtbot.wait_exposed(main_window, timeout=100):
            main_window.show()
        yield main_window
        stop_thread(document.loader.worker_thread)
        stop_thread(image_db.download_thread)
        stop_thread(cid.worker_thread)


def test_main_window_hides_progress_bar_after_downloading_image_during_load(
        qtbot: QtBot, card_db: CardDatabase, main_window: MainWindow):
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
            unittest.mock.patch("mtg_proxy_printer.ui.main_window.QMessageBox.warning"):
        temp_path = main_window.image_db.db_path
        mock_image_path = _create_mock_image(main_window.image_db, temp_path)
        cl_mock.return_value = mock_image_path.stat().st_size
        card_db.db.execute("UPDATE CardFace SET png_image_uri = ?", (mock_image_path.as_uri(),))
        save_file_path = _create_save_file(temp_path)
        assert_that(main_window.progress_bar.isVisible(), is_(False))
        with qtbot.wait_signal(main_window.document.loader.worker_thread.finished, timeout=1000):
            main_window.document.loader.load_document(save_file_path)
        assert_that(main_window.progress_bar.isVisible(), is_(False))


def _create_mock_image(image_db: ImageDatabase, temp_path: pathlib.Path) -> pathlib.Path:
    mock_image_path = temp_path / 'temp' / "0000579f-7b35-4ed3-b44c-db2a538066fe.png"
    mock_image_path.parent.mkdir(parents=True, exist_ok=False)
    image_db.blank_image.save(str(mock_image_path), "PNG", 100)
    assert_that(mock_image_path.is_file(), is_(True))
    return mock_image_path


def _create_save_file(temp_path: pathlib.Path):
    save_file_path = temp_path/"test.mtgproxies"
    with open_database(save_file_path, "document-v3", DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION) as save_file:
        save_file.execute(
            "INSERT INTO Card (page, slot, is_front, scryfall_id) VALUES (?, ?, ?, ?)",
            (1, 1, True, "0000579f-7b35-4ed3-b44c-db2a538066fe")
        )
    return save_file_path


def test_declining_card_data_update_offer_results_in_no_action(qtbot: QtBot, main_window: MainWindow):
    main_window.action_download_card_data.setEnabled(False)
    with unittest.mock.patch.object(
            mtg_proxy_printer.ui.main_window.QMessageBox, "question", return_value=QMessageBox.No) as message_box, \
            qtbot.assertNotEmitted(main_window.loading_state_changed):
        main_window.show_card_data_update_available_message_box(10000)
    message_box.assert_called_once()
    main_window.card_data_downloader.download_worker.get_scryfall_bulk_card_data_url.assert_not_called()
    main_window.card_data_downloader.download_worker.read_json_card_data.assert_not_called()
    assert_that(main_window.action_download_card_data.isEnabled(), is_(True))


def test_accepting_card_data_update_offer_results_in_performed_action(qtbot: QtBot, main_window: MainWindow):
    main_window.action_download_card_data.setEnabled(True)
    with unittest.mock.patch.object(
            mtg_proxy_printer.ui.main_window.QMessageBox, "question", return_value=QMessageBox.Yes) as message_box, \
            qtbot.waitSignal(main_window.loading_state_changed, check_params_cb=lambda value: not value):
        main_window.show_card_data_update_available_message_box(10000)
    message_box.assert_called_once()
    main_window.card_data_downloader.download_worker.get_scryfall_bulk_card_data_url.assert_called_once()
    main_window.card_data_downloader.download_worker.read_json_card_data.assert_called_once()
    assert_that(main_window.action_download_card_data.isEnabled(), is_(False))


@pytest.mark.parametrize("handled_error", [socket.timeout, urllib.error.URLError("Test reason")])
def test_action_download_card_data_enabled_if_error_occurs_after_accepting_card_data_update_offer(
        qtbot: QtBot, main_window: MainWindow, handled_error):
    main_window.card_data_downloader.download_worker.get_scryfall_bulk_card_data_url.side_effect = handled_error
    main_window.action_download_card_data.setEnabled(True)
    with unittest.mock.patch.object(
            mtg_proxy_printer.ui.main_window.QMessageBox, "question", return_value=QMessageBox.Yes) as message_box, \
        unittest.mock.patch.object(
            mtg_proxy_printer.ui.main_window.QMessageBox, "warning", return_value=QMessageBox.Yes) as warning_box, \
            qtbot.waitSignal(main_window.loading_state_changed, check_params_cb=lambda value: not value), \
            qtbot.waitSignal(main_window.card_data_downloader.network_error_occurred):
        main_window.show_card_data_update_available_message_box(10000)
    message_box.assert_called_once()
    warning_box.assert_called_once()
    main_window.card_data_downloader.download_worker.get_scryfall_bulk_card_data_url.assert_called_once()
    main_window.card_data_downloader.download_worker.read_json_card_data.assert_not_called()
    assert_that(
        main_window.action_download_card_data.isEnabled(), is_(True), "Action not re-enabled after error condition"
    )


@pytest.mark.parametrize("handled_error", [socket.timeout, urllib.error.URLError("Test reason")])
def test_action_download_card_data_enabled_if_error_occurs_after_triggering_it(
        qtbot: QtBot, main_window: MainWindow, handled_error):
    main_window.card_data_downloader.download_worker.get_scryfall_bulk_card_data_url.side_effect = handled_error
    main_window.action_download_card_data.setEnabled(True)
    with unittest.mock.patch.object(
            mtg_proxy_printer.ui.main_window.QMessageBox, "warning", return_value=QMessageBox.Yes) as warning_box, \
            qtbot.waitSignal(main_window.loading_state_changed, check_params_cb=lambda value: not value), \
            qtbot.waitSignal(main_window.card_data_downloader.network_error_occurred):
        main_window.action_download_card_data.trigger()
    warning_box.assert_called_once()
    main_window.card_data_downloader.download_worker.get_scryfall_bulk_card_data_url.assert_called_once()
    main_window.card_data_downloader.download_worker.read_json_card_data.assert_not_called()
    assert_that(
        main_window.action_download_card_data.isEnabled(), is_(True), "Action not re-enabled after error condition"
    )


def test_declining_ask_user_about_empty_database_results_in_no_action(qtbot: QtBot, main_window: MainWindow):
    main_window.action_download_card_data.setEnabled(True)
    with unittest.mock.patch.object(
            mtg_proxy_printer.ui.main_window.QMessageBox, "question", return_value=QMessageBox.No) as message_box, \
            qtbot.assertNotEmitted(main_window.loading_state_changed):
        main_window.ask_user_about_empty_database()
    message_box.assert_called_once()
    main_window.card_data_downloader.download_worker.get_scryfall_bulk_card_data_url.assert_not_called()
    main_window.card_data_downloader.download_worker.read_json_card_data.assert_not_called()
    assert_that(main_window.action_download_card_data.isEnabled(), is_(True))


def test_accepting_ask_user_about_empty_database_results_in_performed_action(qtbot: QtBot, main_window: MainWindow):
    main_window.action_download_card_data.setEnabled(True)
    with unittest.mock.patch.object(
            mtg_proxy_printer.ui.main_window.QMessageBox, "question", return_value=QMessageBox.Yes) as message_box, \
            qtbot.waitSignal(main_window.loading_state_changed, check_params_cb=lambda value: not value):
        main_window.ask_user_about_empty_database()
    message_box.assert_called_once()
    main_window.card_data_downloader.download_worker.get_scryfall_bulk_card_data_url.assert_called_once()
    main_window.card_data_downloader.download_worker.read_json_card_data.assert_called_once()
    assert_that(main_window.action_download_card_data.isEnabled(), is_(False))


@pytest.mark.parametrize("handled_error", [socket.timeout, urllib.error.URLError("Test reason")])
def test_action_download_card_data_enabled_if_error_occurs_after_accepting_ask_user_about_empty_database(
        qtbot: QtBot, main_window: MainWindow, handled_error):
    main_window.card_data_downloader.download_worker.get_scryfall_bulk_card_data_url.side_effect = handled_error
    main_window.action_download_card_data.setEnabled(True)
    with unittest.mock.patch.object(
            mtg_proxy_printer.ui.main_window.QMessageBox, "question", return_value=QMessageBox.Yes) as message_box, \
        unittest.mock.patch.object(
            mtg_proxy_printer.ui.main_window.QMessageBox, "warning", return_value=QMessageBox.Yes) as warning_box, \
            qtbot.waitSignal(main_window.loading_state_changed, check_params_cb=lambda value: not value), \
            qtbot.waitSignal(main_window.card_data_downloader.network_error_occurred):
        main_window.ask_user_about_empty_database()
    message_box.assert_called_once()
    warning_box.assert_called_once()
    main_window.card_data_downloader.download_worker.get_scryfall_bulk_card_data_url.assert_called_once()
    main_window.card_data_downloader.download_worker.read_json_card_data.assert_not_called()
    assert_that(
        main_window.action_download_card_data.isEnabled(), is_(True), "Action not re-enabled after error condition"
    )
