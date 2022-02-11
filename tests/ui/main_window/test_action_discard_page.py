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

import pytest
from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import QApplication
from pytestqt.qtbot import QtBot
from hamcrest import *

from mtg_proxy_printer.card_info_downloader import CardInfoDownloader
from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.model.imagedb import ImageDatabase
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.ui.main_window import MainWindow

from tests.helpers import fill_card_database_with_json_card


@pytest.fixture
def main_window(card_db: CardDatabase) -> MainWindow:
    fill_card_database_with_json_card(card_db, "regular_english_card")
    card_db = CardDatabase(":memory:")
    with TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)
        image_db = ImageDatabase(temp_path)
        cid = CardInfoDownloader(card_db)
        document = Document(card_db, image_db)
        main_window = MainWindow(card_db, cid, image_db, document, QStringListModel(["en"]))
        QApplication.instance().shutdown = unittest.mock.MagicMock()
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


def test_main_window_hides_progress_bar_after_downloading_image_during_load(qtbot: QtBot, main_window: MainWindow):
    document = main_window.document
    qtbot.add_widget(main_window)
    with qtbot.wait_exposed(main_window, timeout=100):
        main_window.show()
    assert_that(main_window.document_view.selectionModel().selectedRows(0), has_length(1))
    assert_that(main_window.document_view.selectionModel().selectedRows(0)[0].row(), is_(equal_to(0)))
    assert_that(document.rowCount(), is_(equal_to(1)))
    with qtbot.wait_signal(main_window.action_new_page.triggered, timeout=100):
        main_window.action_new_page.trigger()
    assert_that(main_window.document_view.selectionModel().selectedRows(0), has_length(1))
    assert_that(main_window.document_view.selectionModel().selectedRows(0)[0].row(), is_(equal_to(0)))
    assert_that(document.rowCount(), is_(equal_to(2)))
    with qtbot.wait_signal(main_window.action_discard_page.triggered, timeout=100):
        main_window.action_discard_page.trigger()
    assert_that(main_window.document_view.selectionModel().selectedRows(0), has_length(1))
    assert_that(main_window.document_view.selectionModel().selectedRows(0)[0].row(), is_(equal_to(0)))
    assert_that(document.rowCount(), is_(equal_to(1)))
