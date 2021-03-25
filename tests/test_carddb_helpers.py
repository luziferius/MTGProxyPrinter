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

import time
from unittest.mock import MagicMock

from hamcrest import *

from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.carddb_helpers import clear_database

from .helpers import create_new_card_database_with_json_card, assert_model_is_empty


def test_clear_database_not_clearing_last_image_use_timestamps():
    model = create_new_card_database_with_json_card("regular_english_card")
    document = Document(model, MagicMock())
    # Add two copies. Should only count as one usage
    document.add_card(model.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True), 2)
    document.store_image_usage()
    end = int(time.time())
    document.clear()
    clear_database(model.db)
    assert_model_is_empty(model)
    usages = model.db.execute(
        "SELECT scryfall_id, is_front, usage_count, CAST(strftime('%s', last_use_date) AS INT) "
        "FROM LastImageUseTimestamps").fetchall()

    assert_that(
        usages,
        contains_exactly(
            contains_exactly("0000579f-7b35-4ed3-b44c-db2a538066fe", True, 1, close_to(end, 1)))
    )

