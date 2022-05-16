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

from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import QApplication
from pytestqt.qtbot import QtBot
from hamcrest import *
import pytest

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


@pytest.mark.parametrize("central_widget_class", [
    ColumnarCentralWidget, GroupedCentralWidget, TabbedVerticalCentralWidget
])
def test_main_window_hides_progress_bar_after_downloading_image_during_load(
        qtbot: QtBot, card_db: CardDatabase, central_widget_class):
    fill_card_database_with_json_card(qtbot, card_db, "regular_english_card")
    with TemporaryDirectory() as temp_dir, \
            unittest.mock.patch(
                "mtg_proxy_printer.ui.main_window.get_configured_central_widget_layout_class",
                return_value=central_widget_class), \
            unittest.mock.patch.object(  # Mock all HTTP-specific I/O calls
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
                "seekable", return_value=True):
        temp_path = pathlib.Path(temp_dir)
        image_db = ImageDatabase(temp_path)
        cid = CardInfoDownloader(card_db)
        document = Document(card_db, image_db)
        try:
            mock_image_path = _create_mock_image(image_db, temp_path)
            cl_mock.return_value = mock_image_path.stat().st_size
            card_db.db.execute("UPDATE CardFace SET png_image_uri = ?", (mock_image_path.as_uri(),))
            save_file_path = _create_save_file(temp_path)
            main_window = MainWindow(card_db, cid, image_db, document, QStringListModel(["en"]))
            QApplication.instance().shutdown = unittest.mock.MagicMock()
            qtbot.add_widget(main_window)
            with qtbot.wait_exposed(main_window, timeout=100):
                main_window.show()
            assert_that(main_window.progress_bar.isVisible(), is_(False))
            with qtbot.wait_signal(document.loader.worker_thread.finished, timeout=1000):
                document.loader.load_document(save_file_path)
            assert_that(main_window.progress_bar.isVisible(), is_(False))
        finally:
            if document.loader.worker_thread.isRunning():
                document.loader.worker_thread.quit()
                document.loader.worker_thread.wait(100)
            image_db.quit_background_thread()
            if cid.worker_thread.isRunning():
                cid.worker_thread.quit()
                cid.worker_thread.wait(100)


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
