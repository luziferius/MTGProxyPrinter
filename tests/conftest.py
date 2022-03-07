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

"""
This module is automatically discovered by pytest and all pytest
fixtures defined here are available in all test modules.
"""
import sqlite3

import pytest

import mtg_proxy_printer.sqlite_helpers
from mtg_proxy_printer.model.carddb import CardDatabase


@pytest.fixture(params=[False, True])
def card_db(request) -> CardDatabase:
    card_db = CardDatabase(":memory:")
    if request.param:
        card_db.db.execute("PRAGMA reverse_unordered_selects = TRUE")
    return card_db


@pytest.fixture(params=[False, True])
def empty_save_database(request) -> sqlite3.Connection:
    db = mtg_proxy_printer.sqlite_helpers.open_database(
            ":memory:", "document-v4", CardDatabase.MIN_SUPPORTED_SQLITE_VERSION, check_same_thread=False)
    if request.param:
        db.execute("PRAGMA reverse_unordered_selects = TRUE")
    return db
