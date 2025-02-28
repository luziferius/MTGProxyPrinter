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


"""
Tests the KnownCardImageModel used internally by the CacheCleanupWizard.
"""

import pathlib
import typing

from PySide6.QtCore import Qt
import pytest
from hamcrest import *

from mtg_proxy_printer.ui.cache_cleanup_wizard import KnownCardImageModel, KnownCardColumns
from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.model.imagedb import ImageDatabase

from tests.helpers import fill_card_database_with_json_card
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


class Environment(typing.NamedTuple):
    card_db: CardDatabase
    image_db: ImageDatabase
    front_image: pathlib.Path
    back_image: pathlib.Path


@pytest.fixture
def environment(tmp_path: pathlib.Path, qtbot, card_db: CardDatabase):
    fill_card_database_with_json_card(qtbot, card_db, "english_double_faced_card")
    image_db = ImageDatabase(tmp_path)
    front_image = image_db.db_path/"lowres_front"/"b3"/"b3b87bfc-f97f-4734-94f6-e3e2f335fc4d.png"
    back_image = image_db.db_path/"lowres_back"/"b3"/"b3b87bfc-f97f-4734-94f6-e3e2f335fc4d.png"
    front_image.parent.mkdir(parents=True)
    back_image.parent.mkdir(parents=True)
    image_db.get_blank().save(str(front_image), "PNG")
    image_db.get_blank().save(str(back_image), "PNG")
    yield Environment(card_db, image_db, front_image, back_image)


@pytest.mark.parametrize("is_hidden", [True, False])
@pytest.mark.parametrize("is_front", [True, False])
def test_add_row_identifies_low_resolution_images(environment: Environment, is_front: bool, is_hidden: bool):
    model = KnownCardImageModel(environment.card_db)
    card = environment.card_db.get_card_with_scryfall_id("b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", is_front)
    disk_cache = environment.image_db.read_disk_cache_content()
    assert_that(disk_cache, has_length(2))
    image_under_test = disk_cache[0] if disk_cache[0].is_front == is_front else disk_cache[1]
    model.add_row(card, image_under_test, is_hidden)
    assert_that(
        model.index(0, KnownCardColumns.HasHighResolution).data(Qt.ItemDataRole.EditRole),
        is_(False)
    )
