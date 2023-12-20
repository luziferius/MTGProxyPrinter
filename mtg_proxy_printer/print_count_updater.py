# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>
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


import itertools
import sqlite3

from PyQt5.QtCore import QRunnable

from mtg_proxy_printer.model.carddb import SCHEMA_NAME, with_database_write_lock
from mtg_proxy_printer.sqlite_helpers import open_database
from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger


class PrintCountUpdater(QRunnable):
    """
    This class updates the print counts stored in the database.
    """
    def __init__(self, document):
        super().__init__()
        self.document = document
        self._db = None

    @property
    def db(self) -> sqlite3.Connection:
        # Delay connection creation until first access.
        # Avoids opening connections that aren't actually used and opens the connection
        # in the thread that actually uses it.
        if self._db is None:
            logger.debug(f"{self.__class__.__name__}.db: Opening new database connection")
            source_model = self.document.card_db
            self._db = open_database(
                source_model.db_path, SCHEMA_NAME, source_model.MIN_SUPPORTED_SQLITE_VERSION)
        return self._db

    @with_database_write_lock
    def run(self):
        """
        Increments the usage count of all cards used in the document and updates the last use timestamps.
        Should be called after a successful PDF export and direct printing.
        """
        logger.info("Updating image usage for all cards in the document.")
        db = self.db
        data = self.document.get_all_card_keys_in_document()
        db.execute("BEGIN IMMEDIATE TRANSACTION")
        db.executemany(
            r"""
            INSERT INTO LastImageUseTimestamps (scryfall_id, is_front)
              VALUES (?, ?)
              ON CONFLICT (scryfall_id, is_front)
              DO UPDATE SET usage_count = usage_count + 1, last_use_date = CURRENT_TIMESTAMP;
            """,
            data
        )
        db.commit()
        db.close()
        self._db = None
