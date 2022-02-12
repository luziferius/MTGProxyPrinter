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

import sqlite3
import unittest.mock

import pytest
from hamcrest import *

import mtg_proxy_printer.model.document


@pytest.mark.parametrize("version", [-1, 0, 1, 4, 5])
def test_unknown_save_version_raises_exception(empty_save_database: sqlite3.Connection, version: int):
    empty_save_database.execute(f"PRAGMA user_version = {version};")
    assert_that(empty_save_database.execute("PRAGMA user_version").fetchone()[0], is_(version))
    with unittest.mock.patch("mtg_proxy_printer.model.document.mtg_proxy_printer.sqlite_helpers.open_database") as mock:
        mock.return_value = empty_save_database
        assert_that(
            calling(mtg_proxy_printer.model.document.DocumentLoader.Worker._read_data_from_save_path).with_args(
                "Value ignored by mock"),
            raises(mtg_proxy_printer.model.document.UnknownDocumentFormatException)
        )
        mock.assert_called_once()

