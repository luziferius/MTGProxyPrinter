# Copyright (C) 2020-2024 Thomas Hess <thomas.hess@udo.edu>
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

import io

import pytest
from PySide6.QtCore import QBuffer, QIODevice
from PySide6.QtGui import QPixmap
from hamcrest import *
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.units_and_sizes import CardSizes, CardSize
from mtg_proxy_printer.model.imagedb import ImageDatabase, ImageKey

from tests.hasgetter import has_getter


def qpixmap_to_bytes_io(pixmap: QPixmap) -> io.BytesIO:
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    pixmap.save(buffer, "PNG", quality=100)
    image = buffer.data().data()
    return io.BytesIO(image)


DOWNLOADER = "mtg_proxy_printer.model.imagedb.ImageDownloader"


def test_delete_disk_cache_entries_removes_empty_parent_directories(qtbot: QtBot, image_db: ImageDatabase):
    # Setup
    keys = [
        ImageKey("7ef83f4c-d3ff-4905-a16d-f2bae673a5b2", True, True),
        ImageKey("7ef83f4c-abcd-abcd-9876-1234567890ab", True, True),  # Same prefix
    ]
    blank_image_file = qpixmap_to_bytes_io(image_db.get_blank())
    for key in keys:
        path = image_db.db_path / key.format_relative_path()
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_bytes(blank_image_file.read())
    image_db.images_on_disk.update(keys)

    # Test
    image_db.delete_disk_cache_entries([keys[0]])
    assert_that((image_db.db_path / keys[0].format_relative_path()).is_file(), is_(False))
    assert_that((image_db.db_path / keys[1].format_relative_path()).is_file(), is_(True))
    assert_that((image_db.db_path / keys[0].format_relative_path()).parent.is_dir(), is_(True))
    image_db.delete_disk_cache_entries([keys[1]])
    assert_that((image_db.db_path / keys[1].format_relative_path()).is_file(), is_(False))
    assert_that((image_db.db_path / keys[0].format_relative_path()).parent.is_dir(), is_(False))

@pytest.mark.parametrize("size", [CardSizes.REGULAR, CardSizes.OVERSIZED])
def test_get_blank(image_db: ImageDatabase, size: CardSize):
    image = image_db.get_blank(size)
    assert_that(image, is_(instance_of(QPixmap)))
    assert_that(image, has_getter("size", equal_to(size.as_qsize_px())))
