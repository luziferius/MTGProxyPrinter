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

import io
from unittest.mock import MagicMock

from PyQt5.QtCore import QBuffer, QIODevice
from PyQt5.QtGui import QPixmap
from hamcrest import *
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.model.carddb import Card, MTGSet
from mtg_proxy_printer.model.imagedb import ImageDatabase, ImageKey


def test_quit_background_thread(image_db: ImageDatabase):
    image_db.quit_background_thread()
    assert_that(image_db.download_thread.isRunning(), is_(False))


def qpixmap_to_bytes_io(pixmap: QPixmap) -> io.BytesIO:
    buffer = QBuffer()
    buffer.open(QIODevice.WriteOnly)
    pixmap.save(buffer, "PNG", quality=100)
    image = bytes(buffer.data())
    return io.BytesIO(image)


def test_delete_disk_cache_entries_removes_empty_parent_directories(qtbot: QtBot, image_db: ImageDatabase):
    # Setup
    keys = [
        ImageKey("7ef83f4c-d3ff-4905-a16d-f2bae673a5b2", True, True),
        ImageKey("7ef83f4c-abcd-abcd-9876-1234567890ab", True, True),  # Same prefix
    ]
    for key in keys:
        with qtbot.waitSignal(image_db.download_worker.download_finished, timeout=100):
            blank_image_file = qpixmap_to_bytes_io(image_db.blank_image)
            image_db.download_worker.read_from_url = mock_downloader = MagicMock()
            mock_downloader.return_value = blank_image_file, MagicMock()
            image_db.download_worker.get_image_synchronous(
                Card(  # Only care about the relevant key attributes, as the rest isn’t accessed.
                    "", MTGSet("", ""), "", "", key.scryfall_id, key.is_front,
                    "", "", key.is_high_resolution, False, 1, False))
        mock_downloader.assert_called()
    for key in keys:
        assert_that((image_db.db_path / key.format_relative_path()).is_file(), is_(True))

    # Test
    image_db.delete_disk_cache_entries([keys[0]])
    assert_that((image_db.db_path / keys[0].format_relative_path()).is_file(), is_(False))
    assert_that((image_db.db_path / keys[1].format_relative_path()).is_file(), is_(True))
    assert_that((image_db.db_path / keys[0].format_relative_path()).parent.is_dir(), is_(True))
    image_db.delete_disk_cache_entries([keys[1]])
    assert_that((image_db.db_path / keys[1].format_relative_path()).is_file(), is_(False))
    assert_that((image_db.db_path / keys[0].format_relative_path()).parent.is_dir(), is_(False))

