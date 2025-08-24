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

from collections.abc import Sequence
import sqlite3
from typing import LiteralString, TYPE_CHECKING, Any

from PySide6.QtCore import Qt, QCoreApplication

import mtg_proxy_printer.settings
if TYPE_CHECKING:
    from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.model.carddb import SCHEMA_NAME, with_database_write_lock
from mtg_proxy_printer.sqlite_helpers import cached_dedent, open_database
from mtg_proxy_printer.async_tasks.base import AsyncTask
from mtg_proxy_printer.logger import get_logger
from mtg_proxy_printer.units_and_sizes import SectionProxy
logger = get_logger(__name__)
del get_logger

QueuedConnection = Qt.ConnectionType.QueuedConnection


class PrintingFilterUpdater(AsyncTask):
    """
    This class updates the printing filters stored in the database.
    Syncs the db-internal printing filters with the filters stored in the configuration file,
    and updates the is_hidden columns.
    """
    PROGRESS_STEP_COUNT = 6

    def __init__(
            self, model: "CardDatabase", db_connection: sqlite3.Connection = None, *,
            force_update_hidden_column: bool = False):
        """
        :param model: CardDatabase instance to work on
        :param db_connection: Database connection to use. Only useful for testing. During normal operation, this class opens
          a separate connection by using the database filesystem path stored in the passed-in model.
          This doesn't work for in-memory databases used by unit tests.
          Thus, it requires an option to pass an existing connection to override the logic that opens new connections,
          and also suppresses automatic connection closure during tests.
        :param force_update_hidden_column: Force re-writing the is_hidden columns. The columns need updates,
          if the filter values change (determined internally) or the card data changes.
          This boolean can be used by the card data update to enforce refreshing
          the cached is_hidden, as the value may change for each card, even if the filters were unchanged.
        """
        super().__init__()
        self.model = model
        self.progress = 0
        self.ui_update_required.connect(model.restart_transaction, QueuedConnection)
        self.ui_update_required.connect(model.card_data_updated, QueuedConnection)
        self.force_update_hidden_column = force_update_hidden_column
        self.uses_self_opened_db_connection = not db_connection
        self._db = db_connection
        self.update_ui = False
        self.should_abort = False
        logger.debug(f"Created {self.__class__.__name__} instance.")

    def cancel(self):
        self.should_abort = True

    @property
    def db(self) -> sqlite3.Connection:
        # Delay connection creation until first access.
        # Avoids opening connections that aren't actually used and opens the connection
        # in the thread that actually uses it.
        if self._db is None:
            logger.debug(f"{self.__class__.__name__}.db: Opening new database connection")
            self._db = open_database(self.model.db_path, SCHEMA_NAME)
        return self._db

    @with_database_write_lock()
    def run(self):
        logger.debug(f"Called {self.__class__.__name__}.run()")
        try:
            self.task_begins.emit(
                self.PROGRESS_STEP_COUNT, QCoreApplication.translate(
                    "PrintingFilterUpdater.store_current_printing_filters()",
                    "Processing updated card filters:")
            )
            self.update_ui = self.store_current_printing_filters()
            if self.should_abort:
                self.db.rollback()
            else:
                self.db.commit()
            return
        except sqlite3.Error as e:
            logger.exception(e)
            self.error_occurred.emit(e.sqlite_errorname)
            self.db.rollback()
        finally:
            self.task_completed.emit()
            if self.uses_self_opened_db_connection:
                logger.debug(f"Closing {self.__class__.__name__} connection")
                self.db.close()
                self._db = None

    def store_current_printing_filters(self) -> bool:
        db = self.db
        if self.uses_self_opened_db_connection:
            db.execute("BEGIN IMMEDIATE TRANSACTION\n")
        section = mtg_proxy_printer.settings.settings["card-filter"]
        boolean_keys = mtg_proxy_printer.settings.get_boolean_card_filter_keys()
        old_filter_removed = self._remove_old_printing_filters(section)
        filters_need_update = self._filters_in_db_differ_from_settings(section)
        if self.should_abort:
            return False
        if filters_need_update:
            logger.info("Printing filters changed in the settings, update the database.")
            db.executemany(
                cached_dedent("""\
                    INSERT INTO DisplayFilters (filter_name, filter_active) -- store_current_printing_filters()
                      VALUES (?, ?)
                      ON CONFLICT (filter_name) DO UPDATE
                        SET filter_active = excluded.filter_active
                        WHERE filter_active <> excluded.filter_active
                    """),
                ((key, section.getboolean(key)) for key in boolean_keys)
            )
            if self.should_abort:
                return False
            self.advance_progress.emit()
        if set_code_updated := self._set_code_filters_need_update():
            self._update_set_code_filters_in_db()
        if self.should_abort:
            return False
        self.advance_progress.emit()
        update_ui = filters_need_update or old_filter_removed or self.force_update_hidden_column or set_code_updated
        if update_ui:
            self._update_cached_data()
        if self.uses_self_opened_db_connection:
            db.commit()
        if update_ui:
            self.ui_update_required.emit()
        return update_ui

    def _set_code_filters_need_update(self) -> bool:
        return self.get_currently_enabled_set_code_filters() != self.get_configured_set_code_filters()

    def _filters_in_db_differ_from_settings(self, section: SectionProxy) -> bool:
        filters_in_db: dict[str, bool] = {
            key: bool(value) for key, value
            in self.db.execute(cached_dedent("""\
            SELECT filter_name, filter_active --_filters_in_db_differ_from_settings()
              FROM DisplayFilters
              WHERE filter_name LIKE 'hide-%'
            """), ()).fetchall()
        }
        boolean_keys = mtg_proxy_printer.settings.get_boolean_card_filter_keys()
        filters_in_settings: dict[str, bool] = {key: section.getboolean(key) for key in boolean_keys}
        return filters_in_settings != filters_in_db

    def _remove_old_printing_filters(self, section) -> bool:
        stored_filters = {
            filter_name for filter_name, in self.db.execute("SELECT filter_name FROM DisplayFilters").fetchall()
        }
        known_filters = set(section.keys())
        old_filters = stored_filters - known_filters
        if old_filters:
            logger.info(f"Removing old printing filters from the database: {old_filters}")
            self.db.executemany(
                "DELETE FROM DisplayFilters WHERE filter_name = ?",
                ((filter_name,) for filter_name in old_filters)
            )
        return bool(old_filters)

    def _update_set_code_filters_in_db(self):
        # Because this is called at application start if the user changed the settings file,
        # and whenever the filter settings are changed in the settings window,
        # the internal state of the display filter table is always consistent with the application settings.
        # Thus, potentially added cards during a card data update do not cause
        # the database to enter an inconsistent state.
        # Invariant: Before the update starts, all filters are consistent with the settings.
        # During the update, new cards are added with filters consistent with the settings.
        # Thus, after the update completes, the data is consistent.
        logger.info("Set code filter changed in the settings, update the database.")
        settings_set_code_filters = self.get_configured_set_code_filters()
        database_set_code_filters = self.get_currently_enabled_set_code_filters()
        new_filters = settings_set_code_filters - database_set_code_filters
        removed_filters = database_set_code_filters - settings_set_code_filters
        logger.debug(f"Hide cards in these sets: {sorted(new_filters)}")
        logger.debug(f"Show cards in these sets: {sorted(removed_filters)}")
        self.db.execute(
            cached_dedent("""\
                    INSERT INTO DisplayFilters (filter_name, filter_active) -- store_current_printing_filters()
                      VALUES (?, ?)
                      ON CONFLICT (filter_name) DO UPDATE
                        SET filter_active = excluded.filter_active
                        WHERE filter_active <> excluded.filter_active
                    """),
            ("hidden-sets", bool(settings_set_code_filters))
        )
        filter_id: int = self._read_optional_scalar_from_db(
            "SELECT filter_id FROM DisplayFilters WHERE filter_name = ?", ("hidden-sets",))
        self.db.execute(
            "CREATE TEMP TABLE RemovedSetFilters(set_code TEXT NOT NULL UNIQUE); -- store_current_printing_filters()\n")
        self.db.executemany(
            "INSERT INTO RemovedSetFilters(set_code) VALUES (?)\n",
            ((code,) for code in removed_filters))
        self.db.execute(
            "CREATE TEMP TABLE AddedSetFilters(set_code TEXT NOT NULL UNIQUE); -- store_current_printing_filters()\n")
        self.db.executemany(
            "INSERT INTO AddedSetFilters(set_code) VALUES (?)\n",
            ((code,) for code in new_filters))
        self.db.execute(cached_dedent("""\
                DELETE FROM PrintingDisplayFilter -- store_current_printing_filters()
                  WHERE filter_id = ?
                  AND printing_id IN (
                    SELECT printing_id
                      FROM Printing
                      JOIN MTGSet USING (set_id)
                      JOIN RemovedSetFilters USING (set_code)
                  )
                """), (filter_id,))
        self.db.execute(cached_dedent("""\
                INSERT OR IGNORE INTO PrintingDisplayFilter (printing_id, filter_id) -- store_current_printing_filters()
                  SELECT printing_id, ?
                  FROM Printing
                  JOIN MTGSet USING (set_id)
                  JOIN AddedSetFilters USING (set_code)
                """), (filter_id,))
        self.db.execute("DROP TABLE RemovedSetFilters -- store_current_printing_filters()\n")
        self.db.execute("DROP TABLE AddedSetFilters -- store_current_printing_filters()\n")

    def get_configured_set_code_filters(self) -> set[str]:
        # The intersection removes all words that are not known set codes
        return mtg_proxy_printer.settings.parse_card_set_filters().intersection(
            self.get_all_set_codes()
        )

    def get_all_set_codes(self) -> list[str]:
        """Returns all known set codes."""
        logger.debug("Reading all known set codes")
        result = [
            code for code, in self.db.execute(
                "SELECT set_code FROM MTGSet -- get_all_set_codes()\n")
        ]
        return result

    UPDATE_CACHED_DATA_STEPS: list[tuple[str, LiteralString]] = [
        ("Update the Printing.is_hidden column", cached_dedent("""\
        UPDATE Printing    -- _update_cached_data()
            SET is_hidden = Printing.printing_id IN (
              SELECT HiddenPrintingIDs.printing_id FROM HiddenPrintingIDs
            )
            WHERE is_hidden <> (Printing.printing_id IN (
              SELECT HiddenPrintingIDs.printing_id FROM HiddenPrintingIDs
            ))
        ;
        """)),
        ("Update the FaceName.is_hidden column", cached_dedent("""\
        WITH FaceNameShouldBeHidden (face_name_id, should_be_hidden) AS (    -- _update_cached_data()
          -- A FaceName should be hidden, iff all uses by printings are hidden,
          -- i.e. the total use count is equal to the hidden use count
          SELECT face_name_id, COUNT() = sum(Printing.is_hidden) AS should_be_hidden
          FROM Printing
          JOIN CardFace USING (printing_id)
          JOIN FaceName USING (face_name_id)
          -- Also group by language_id, because there are actual name conflicts across languages.
          -- Additionally, some non-English cards are listed using their English name, because the information is
          -- unavailable. So these cases are caught by including the language_id.
          GROUP BY card_name, language_id
        )
        UPDATE FaceName
          SET is_hidden = FaceNameShouldBeHidden.should_be_hidden
          FROM FaceNameShouldBeHidden
          WHERE FaceName.face_name_id = FaceNameShouldBeHidden.face_name_id
          AND FaceName.is_hidden <> FaceNameShouldBeHidden.should_be_hidden
        ;
        """)),
        ("Remove outdated entries in the RemovedPrintings table", cached_dedent("""\
        DELETE FROM RemovedPrintings    -- _update_cached_data()
          WHERE scryfall_id IN (
            SELECT Printing.scryfall_id
            FROM Printing
            WHERE Printing.is_hidden IS FALSE
          );
        """)),
        # Performance note: Using INSERT OR IGNORE and removing the inner scryfall_id NOT IN (subquery) simplifies the
        # query plan, but takes about 40% longer to evaluate (on the card data of late April 2022)
        # than the current method that only inserts missing rows.
        ("Add new items to the RemovedPrintings table", cached_dedent("""\
        INSERT INTO RemovedPrintings (scryfall_id, language, oracle_id)    -- _update_cached_data()
          SELECT DISTINCT scryfall_id, language, oracle_id
            FROM Printing
            JOIN Card USING (card_id)
            JOIN CardFace USING (printing_id)
            JOIN FaceName USING (face_name_id)
            JOIN PrintLanguage USING (language_id)
            WHERE Printing.is_hidden IS TRUE
              AND scryfall_id NOT IN (
                SELECT rp.scryfall_id
                FROM RemovedPrintings AS rp
            );
        """)),
    ]

    def _update_cached_data(self):
        db = self.db
        for step, statement in self.UPDATE_CACHED_DATA_STEPS:  # type: str, LiteralString
            logger.debug(step)
            db.execute(statement)
            self.advance_progress.emit()
            if self.should_abort:
                return
        logger.debug("Finished maintenance tasks.")

    def get_currently_enabled_set_code_filters(self) -> set[str]:
        values = self.db.execute(
            "SELECT set_code FROM CurrentlyEnabledSetCodeFilters -- get_currently_enabled_set_code_filters()\n")
        result = {value for (value,) in values}
        return result

    def _read_optional_scalar_from_db(self, query: str, parameters: Sequence[Any]):
        if result := self.db.execute(query, parameters).fetchone():
            return result[0]
        else:
            return None
