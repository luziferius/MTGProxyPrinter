# Copyright (C) 2022 Thomas Hess <thomas.hess@udo.edu>

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
import socket
from tempfile import TemporaryDirectory
import unittest.mock
import urllib.error

import pytest
from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import QApplication, QAction
from pytestqt.qtbot import QtBot
from hamcrest import *

from mtg_proxy_printer.card_info_downloader import CardInfoDownloader
from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.model.imagedb import ImageDatabase
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.ui.main_window import MainWindow
from mtg_proxy_printer.ui.central_widget import ColumnarCentralWidget, GroupedCentralWidget, TabbedVerticalCentralWidget

from tests.helpers import fill_card_database_with_json_card


@pytest.fixture(params=[ColumnarCentralWidget, GroupedCentralWidget, TabbedVerticalCentralWidget])
def main_window(qtbot, card_db: CardDatabase, request) -> MainWindow:
    fill_card_database_with_json_card(qtbot, card_db, "regular_english_card")
    card_db = CardDatabase(":memory:")
    with TemporaryDirectory() as temp_dir, unittest.mock.patch(
            "mtg_proxy_printer.ui.main_window.get_configured_central_widget_layout_class",
            return_value=request.param):
        temp_path = pathlib.Path(temp_dir)
        image_db = ImageDatabase(temp_path)
        cid = CardInfoDownloader(card_db)
        document = Document(card_db, image_db)
        main_window = MainWindow(card_db, cid, image_db, document, QStringListModel(["en"]))
        QApplication.instance().shutdown = unittest.mock.MagicMock()
        main_window.action_quit.triggered.disconnect(main_window.on_action_quit_triggered)
        yield main_window
        if document.loader.worker_thread.isRunning():
            document.loader.worker_thread.quit()
            document.loader.worker_thread.wait(100)
        if image_db.download_thread.isRunning():
            image_db.download_thread.quit()
            image_db.download_thread.wait(100)
        if cid.worker_thread.isRunning():
            cid.worker_thread.quit()
            cid.worker_thread.wait(100)


@pytest.mark.parametrize("handled_error", [socket.timeout, urllib.error.URLError("Test reason")])
def test_action_download_card_data(qtbot: QtBot, main_window: MainWindow, handled_error: Exception):
    qtbot.add_widget(main_window)
    with qtbot.waitExposed(main_window):
        main_window.show()
    action: QAction = main_window.action_download_card_data
    action.setEnabled(True)

    def validate_prior_to_error(_):
        """
        Validate that the action is disabled while the download is in progress.
        Also emits the download_begins signal, which is not emitted, because the function responsible is replaced with
        a mock that calls this as the side_effect.
        """
        with qtbot.waitSignal(main_window.loading_state_changed, timeout=1000, check_params_cb=lambda value: value):
            main_window.card_data_downloader.download_worker.download_begins.emit(1000)
        assert_that(main_window.action_download_card_data.isEnabled(), is_(False))
        raise handled_error

    with unittest.mock.patch.object(
            main_window.card_data_downloader.download_worker, "get_scryfall_bulk_card_data_url") as downloader_mock, \
            unittest.mock.patch("mtg_proxy_printer.ui.main_window.QMessageBox.warning") as message_box_mock:
        downloader_mock.side_effect = validate_prior_to_error
        with qtbot.waitSignal(main_window.loading_state_changed, timeout=1000,
                              check_params_cb=lambda value: not value):
            action.trigger()
        message_box_mock.assert_called_once()
        downloader_mock.assert_called_once()
    assert_that(action.isEnabled(), is_(True), "Action not properly re-enabled after error condition")
