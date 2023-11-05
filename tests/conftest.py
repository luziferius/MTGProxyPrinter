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

"""
This module is automatically discovered by pytest and all pytest
fixtures defined here are available in all test modules.
"""
import itertools
import sqlite3
import unittest.mock
from pathlib import Path
from tempfile import TemporaryDirectory

from PySide6.QtGui import QColor, QPixmap
import pytest
from hamcrest import assert_that, is_

from mtg_proxy_printer.stop_thread import stop_thread
import mtg_proxy_printer.sqlite_helpers
import mtg_proxy_printer.settings
from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.imagedb import ImageDatabase, ImageKey, IMAGE_SIZE
from tests.helpers import fill_card_database_with_json_cards


@pytest.fixture(params=[False, True])
def card_db(request) -> CardDatabase:
    section = mtg_proxy_printer.settings.settings["card-filter"]
    settings_to_use = {filter_name: "False" for filter_name in section.keys()}
    with unittest.mock.patch.dict(section, settings_to_use):
        card_db = CardDatabase(":memory:", check_same_thread=False)
    if request.param:
        card_db.db.execute("PRAGMA reverse_unordered_selects = TRUE")
    return card_db


@pytest.fixture(params=[False, True])
def empty_save_database(request) -> sqlite3.Connection:
    db = mtg_proxy_printer.sqlite_helpers.open_database(
            ":memory:", "document-v6", CardDatabase.MIN_SUPPORTED_SQLITE_VERSION, check_same_thread=False)
    if request.param:
        db.execute("PRAGMA reverse_unordered_selects = TRUE")
    return db


@pytest.fixture()
def image_db():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        image_db = ImageDatabase(temp_path)
        regular_width, regular_height = image_db.blank_image.width(), image_db.blank_image.height()
        for scryfall_id, is_front in itertools.product(
                ["0000579f-7b35-4ed3-b44c-db2a538066fe", "b3b87bfc-f97f-4734-94f6-e3e2f335fc4d"], [True, False]):
            # Regular card images
            key = ImageKey(scryfall_id, is_front, True)
            image_db.loaded_images[key] = image_db.blank_image.copy(0, 0, regular_width, regular_height)
            image_db.images_on_disk.add(key)
        for scryfall_id in ["650722b4-d72b-4745-a1a5-00a34836282b"]:
            # Oversized card images
            key = ImageKey(scryfall_id, True, True)
            image_db.loaded_images[key] = image_db.blank_image.scaled(regular_height, regular_width*2)
            image_db.images_on_disk.add(key)

        yield image_db
        if image_db.download_thread.isRunning():
            image_db.quit_background_thread()
            try:
                assert_that(image_db.download_thread.isRunning(), is_(False))
            finally:
                stop_thread(image_db.download_thread)
    assert_that(temp_path.exists(), is_(False))


@pytest.fixture
def document(qtbot, card_db: CardDatabase, image_db: ImageDatabase) -> Document:
    fill_card_database_with_json_cards(qtbot, card_db, [
        "regular_english_card", "oversized_card", "english_double_faced_card"])
    document = Document(card_db, image_db)
    document.loader.worker._db = card_db.db  # Explicitly share the in-memory database
    yield document
    stop_thread(document.loader.worker_thread)


@pytest.fixture
def document_light(qtbot) -> Document:
    mock_card_db = unittest.mock.NonCallableMagicMock()
    mock_image_db = unittest.mock.NonCallableMagicMock(spec=ImageDatabase)
    mock_image_db.blank_image = QPixmap(IMAGE_SIZE)
    mock_image_db.blank_image.fill(QColor("white"))
    document = Document(mock_card_db, mock_image_db)
    document.loader.worker._db = mtg_proxy_printer.sqlite_helpers.create_in_memory_database(
        "carddb", CardDatabase.MIN_SUPPORTED_SQLITE_VERSION, check_same_thread=False)
    yield document
    stop_thread(document.loader.worker_thread)
