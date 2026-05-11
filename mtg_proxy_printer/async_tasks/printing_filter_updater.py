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

from collections.abc import Sequence
import sqlite3
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt

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
__all__ = [
    "PrintingFilterUpdater",
    "PrintingPreferenceUpdater",
]


class PrintingFilterUpdater(AsyncTask):
    """
    This class updates the printing filters stored in the database.
    Syncs the db-internal printing filters with the filters stored in the configuration file,
    and updates the is_visible column.
    """
    PROGRESS_STEP_COUNT = 4

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
        :param force_update_hidden_column: Force re-writing the is_visible column. The columns need updates,
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
        self._db = db_connection
        self.db_connection_self_opened = db_connection is None
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
                self.PROGRESS_STEP_COUNT, self.tr(
                    "Processing updated card filters:", "Progress bar label text")
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
            if self.db_connection_self_opened:
                logger.debug(f"Closing {self.__class__.__name__} connection")
                self.db.close()
                self._db = None

    def store_current_printing_filters(self) -> bool:
        db = self.db
        if self.db_connection_self_opened:
            db.execute("BEGIN IMMEDIATE TRANSACTION\n")
        section = mtg_proxy_printer.settings.settings["card-filter"]
        update_ui = self._remove_old_printing_filters(section)
        changed_or_new_filters = self._get_changed_or_new_filters(section)
        self.advance_progress.emit()
        if self.should_abort:
            return False
        if changed_or_new_filters:
            logger.info("Printing filters added or changed in the settings, update the database.")
            db.executemany(
                cached_dedent("""\
                    INSERT INTO PrintingFilters (filter_name, filter_active) -- store_current_printing_filters()
                      VALUES                    (?,           ?)
                      ON CONFLICT (filter_name) DO UPDATE
                        SET filter_active = excluded.filter_active
                    """),
                changed_or_new_filters.items()
            )
            if self.should_abort:
                return False
        self.advance_progress.emit()
        update_ui |= self._update_set_code_filters_in_db()
        if self.should_abort:
            return False
        self.advance_progress.emit()
        self._update_cached_data()
        self.advance_progress.emit()
        update_ui |= bool(changed_or_new_filters) or self.force_update_hidden_column
        if self.db_connection_self_opened:
            db.commit()
        if update_ui:
            self.ui_update_required.emit()
        return update_ui

    def _get_changed_or_new_filters(self, section: SectionProxy) -> dict[str, bool]:
        """Returns all changed or new filters with their new value."""
        old_filter_values_in_db: dict[str, bool] = dict(
            self.db.execute(
                "SELECT filter_name, filter_active FROM PrintingFilters --_get_changed_or_new_filters()\n"
             )
        )
        boolean_keys = mtg_proxy_printer.settings.get_boolean_card_filter_keys()
        filters_in_settings: dict[str, bool] = {key: section.getboolean(key) for key in boolean_keys}
        updated_filters_with_new_values = {
            key: new_filter_value
            for key, new_filter_value in filters_in_settings.items()
            if (old_filter_values_in_db.get(key, not new_filter_value) != new_filter_value)
        }
        return updated_filters_with_new_values

    def _remove_old_printing_filters(self, section) -> bool:
        stored_filters = {
            filter_name for filter_name, in self.db.execute(
                "SELECT filter_name FROM PrintingFilters -- _remove_old_printing_filters()").fetchall()
        }
        known_filters = set(section.keys())
        old_filters = stored_filters - known_filters
        if old_filters:
            logger.info(f"Removing old printing filters from the database: {old_filters}")
            self.db.executemany(
                "DELETE FROM PrintingFilters WHERE filter_name = ?",
                ((filter_name,) for filter_name in old_filters)
            )
        return bool(old_filters)

    def _update_set_code_filters_in_db(self) -> bool:
        old_set_filter_in_db = self.get_mtgset_filters_enabled_in_db()
        new_set_filter_in_config = self.get_configured_set_code_filters()
        if new_set_filter_in_config == old_set_filter_in_db:
            logger.debug("Set code filters unchanged.")
            return False
        logger.info("Set code filter changed in the settings, update the database.")
        removed_filters = old_set_filter_in_db - new_set_filter_in_config
        new_filters = new_set_filter_in_config - old_set_filter_in_db
        logger.debug(f"Hide cards in these sets: {sorted(new_filters)}")
        logger.debug(f"Show cards in these sets: {sorted(removed_filters)}")
        parameters = [(True, set_filter) for set_filter in new_filters]
        parameters += [(False, set_filter) for set_filter in removed_filters]
        self.db.executemany(
            "UPDATE MTGSet SET set_filter_active = ? WHERE set_code = ? -- _update_set_code_filters_in_db()\n",
            parameters
        )
        return True

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

    def _update_cached_data(self):
        self.db.execute(cached_dedent("""\
        UPDATE Printing -- _update_cached_data()
          SET is_visible = new_data.is_visible,
          preference_score = new_data.preference_score
        FROM (
          SELECT printing_id, is_visible, preference_score
          FROM EvaluatePrintingFilters) AS new_data
        WHERE Printing.printing_id = new_data.printing_id
        """))

    def get_mtgset_filters_enabled_in_db(self) -> set[str]:
        """Returns all MTG sets currently hidden by filters"""
        result = {item for item, in self.db.execute(
            "SELECT set_code FROM MTGSet WHERE set_filter_active IS TRUE-- get_mtgset_filters_enabled_in_db()\n"
        )}
        return result

    def _read_optional_scalar_from_db(self, query: str, parameters: Sequence[Any]):
        if result := self.db.execute(query, parameters).fetchone():
            return result[0]
        else:
            return None


class PrintingPreferenceUpdater(AsyncTask):
    """
    This class saves the updated printing preference scores in the database.
    This is a database-writing task, thus has to operate under a database write lock.
    It may take several hundred milliseconds per changed preference weight.
    Many weights only affect a few thousand printings,
    but some like "borderless card" or "white-bordered card" have over 20k printings that need to be updated.
    """

    def __init__(
            self, model: "CardDatabase", new_preference_weights: set[tuple[str, int]],
            db_connection: sqlite3.Connection = None, /):
        """
        :param model: CardDatabase instance to work on
        :param new_preference_weights: The new printing preference weights to use, as a set[tuple[filter_name, weight]],
          obtained from the PrintingFilterModel used by the settings window.
        :param db_connection: Database connection to use. Only useful for testing. During normal operation, this class opens
          a separate connection by using the database filesystem path stored in the passed-in model.
          This doesn't work for in-memory databases used by unit tests.
          Thus, it requires an option to pass an existing connection to override the logic that opens new connections,
          and also suppresses automatic connection closure during tests.
        """
        super().__init__()
        self.model = model
        self.new_preference_weights = new_preference_weights
        self.old_preference_weights = set(model.get_printing_filter_weights().items())
        self.progress = 0
        self.task_completed.connect(model.restart_transaction, QueuedConnection)
        self._db = db_connection
        self.db_connection_self_opened = db_connection is None
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
        needs_update_weights = self.new_preference_weights - self.old_preference_weights
        db = self.db
        try:
            self.task_begins.emit(
                len(needs_update_weights), self.tr(
                    "Processing printing preferences:", "Progress bar label text")
            )
            self.update_printing_preferences(needs_update_weights)
            if self.should_abort:
                db.rollback()
            else:
                db.commit()
            return
        except sqlite3.Error as e:
            logger.exception(e)
            self.error_occurred.emit(e.sqlite_errorname)
            db.rollback()
        finally:
            self.task_completed.emit()
            if self.db_connection_self_opened:
                logger.debug(f"Closing {self.__class__.__name__} connection")
                db.close()
                self._db = None

    def update_printing_preferences(self, needs_update_weights: set[tuple[str, int]]):
        db = self.db
        if self.db_connection_self_opened:
            db.execute("BEGIN IMMEDIATE TRANSACTION -- update_printing_preferences()\n")
        for name, weight in needs_update_weights:
            db.execute(cached_dedent("""\
                UPDATE PrintingFilters  -- update_printing_preferences()
                  SET printing_preference_weight = ?
                  WHERE filter_name = ?
                """),
                (weight, name)
            )
            self.advance_progress.emit()
            if self.should_abort: break
