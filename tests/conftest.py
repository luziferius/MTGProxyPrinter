#  Copyright © 2020-2026  Thomas Hess <thomas.hess@udo.edu>
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


"""
This module is automatically discovered by pytest and all pytest
fixtures defined here are available in all test modules.
"""
import itertools
import sqlite3
import unittest.mock
from pathlib import Path

from PySide6.QtGui import QColorConstants, QPixmap
import pytest
from hamcrest import assert_that

import mtg_proxy_printer.sqlite_helpers
import mtg_proxy_printer.settings
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.async_tasks.printing_filter_updater import PrintingFilterUpdater
from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.units_and_sizes import CardSizes
from mtg_proxy_printer.model.imagedb import ImageDatabase
from mtg_proxy_printer.model.imagedb_files import ImageKey
from tests.helpers import fill_card_database_with_json_cards, is_dataclass_equal_to


@pytest.fixture(params=[False, True])
def card_db(request) -> CardDatabase:
    section = mtg_proxy_printer.settings.settings["card-filter"]
    settings_to_use = {filter_name: "False" for filter_name in section.keys()}
    with unittest.mock.patch.dict(section, settings_to_use):
        CardDatabase.main_instance = card_db = CardDatabase(":memory:", check_same_thread=False)
    db = card_db.db
    if request.param:
        db.execute("PRAGMA reverse_unordered_selects = TRUE")
    PrintingFilterUpdater(card_db, card_db.db).run()
    yield card_db
    del card_db.db
    CardDatabase.main_instance = None
    db.close()


@pytest.fixture(params=[False, True])
def empty_save_database(request) -> sqlite3.Connection:
    db = mtg_proxy_printer.sqlite_helpers.open_database(":memory:", "document-v7", check_same_thread=False)
    if request.param:
        db.execute("PRAGMA reverse_unordered_selects = TRUE")
    yield db
    db.close()


@pytest.fixture
def image_db(qtbot, tmp_path: Path) -> ImageDatabase:
    image_db = ImageDatabase(tmp_path)
    regular = image_db.get_blank(CardSizes.REGULAR)
    large = image_db.get_blank(CardSizes.OVERSIZED)
    for scryfall_id, is_front in itertools.product(
            ["0000579f-7b35-4ed3-b44c-db2a538066fe", "b3b87bfc-f97f-4734-94f6-e3e2f335fc4d"], [True, False]):
        # Regular card images
        key = ImageKey(scryfall_id, is_front, True)
        image_db.loaded_images[key] = regular.copy()
        image_db.images_on_disk.add(key)
    for scryfall_id in ["650722b4-d72b-4745-a1a5-00a34836282b"]:
        # Oversized card images
        key = ImageKey(scryfall_id, True, True)
        image_db.loaded_images[key] = large.copy()
        image_db.images_on_disk.add(key)

    return image_db


@pytest.fixture
def document(qtbot, card_db: CardDatabase, image_db: ImageDatabase) -> Document:
    fill_card_database_with_json_cards(qtbot, card_db, [
        "regular_english_card", "oversized_card", "english_double_faced_card"])
    return Document(card_db, image_db)


@pytest.fixture
def mock_imagedb():
    mock_image_db = unittest.mock.NonCallableMagicMock(spec=ImageDatabase)
    blanks = {
        CardSizes.REGULAR: QPixmap(CardSizes.REGULAR.as_qsize_px()),
        CardSizes.OVERSIZED: QPixmap(CardSizes.OVERSIZED.as_qsize_px()),
    }
    blanks[CardSizes.REGULAR].fill(QColorConstants.Transparent)
    blanks[CardSizes.OVERSIZED].fill(QColorConstants.Transparent)
    mock_image_db.get_blank = blanks.get
    return mock_image_db


@pytest.fixture
def document_light(qtbot, mock_imagedb) -> Document:
    mock_card_db = unittest.mock.NonCallableMagicMock()
    mock_card_db.db = db = mtg_proxy_printer.sqlite_helpers.create_in_memory_database(
        "carddb", check_same_thread=False)
    yield Document(mock_card_db, mock_imagedb)
    db.close()
    del mock_card_db.db


@pytest.fixture
def page_layout() -> PageLayoutSettings:
    layout = PageLayoutSettings.create_from_settings()
    defaults = PageLayoutSettings.create_from_settings(mtg_proxy_printer.settings.DEFAULT_SETTINGS)
    assert_that(layout, is_dataclass_equal_to(defaults))
    return layout
