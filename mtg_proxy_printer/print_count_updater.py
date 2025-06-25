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



import sqlite3
import typing

from mtg_proxy_printer.model.carddb import SCHEMA_NAME, with_database_write_lock
from mtg_proxy_printer.sqlite_helpers import open_database
from mtg_proxy_printer.runner import Runnable
from mtg_proxy_printer.logger import get_logger
if typing.TYPE_CHECKING:
    from mtg_proxy_printer.model.document import Document

logger = get_logger(__name__)
del get_logger


class PrintCountUpdater(Runnable):
    """
    This class updates the print counts stored in the database.

    Implementation note: Why is this an async task, even though it only takes a few milliseconds to complete?
    Answer: This encapsulates the database writing work associated with printing, allowing the application to delay
    the execution of the database write transaction arbitrarily without stalling the main thread.
    This allows the app to offer printing while a card data update writes to the card database,
    which can take multiple minutes if the network connection is sufficiently slow.
    If it were synchronous, printing would block the UI thread until the update completes,
    or the app would miss writing the data at all, or printing/PDF export had to be prohibited.
    """
    def __init__(self, document: "Document", db: sqlite3.Connection = None):
        super().__init__()
        self.db_path = document.card_db.db_path
        # Collect the data now, so that the delayed run() does not operate on a potentially modified document,
        # but can use the data from the time the document was printed/exported.
        self.data = [(item.scryfall_id, item.is_front) for item in document.get_all_image_keys_in_document()]
        self.db_passed_in = bool(db)
        self._db = db

    @property
    def db(self) -> sqlite3.Connection:
        # Delay connection creation until first access.
        # Avoids opening connections that aren't actually used and opens the connection
        # in the thread that actually uses it.
        if self._db is None:
            logger.debug(f"{self.__class__.__name__}.db: Opening new database connection")
            self._db = open_database(self.db_path, SCHEMA_NAME)
        return self._db

    def run(self):
        """
        Increments the usage count of all cards used in the document and updates the last use timestamps.
        Should be called after a successful PDF/PNG export and direct printing.
        """
        try:
            self._update_image_usage()
        finally:
            self.release_instance()

    @with_database_write_lock()
    def _update_image_usage(self):
        logger.info("Updating image usage for all cards in the document.")
        db = self.db
        db.execute("BEGIN IMMEDIATE TRANSACTION -- _update_image_usage()")
        db.executemany(
            r"""
            INSERT INTO LastImageUseTimestamps (scryfall_id, is_front) -- _update_image_usage()
              VALUES (?, ?)
              ON CONFLICT (scryfall_id, is_front)
              DO UPDATE SET usage_count = usage_count + 1, last_use_date = CURRENT_TIMESTAMP;
            """,
            self.data
        )
        db.commit()
        logger.info("Usage data written.")
        if not self.db_passed_in:
            db.close()
        self._db = None
