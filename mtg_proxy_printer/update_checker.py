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

import random
import re
import socket
import typing
import urllib.parse
import urllib.error

import ijson
from PyQt5.QtCore import QObject, QThread, pyqtSignal as Signal

from mtg_proxy_printer.argument_parser import Namespace
import mtg_proxy_printer.meta_data
from mtg_proxy_printer import settings
from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.card_info_downloader import CardInfoDatabaseImportWorker
from mtg_proxy_printer.natsort import natural_sorted, str_less_than
from mtg_proxy_printer.stop_thread import stop_thread
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

__all__ = [
    "UpdateChecker",
]

StringList = typing.List[str]
OptStr = typing.Optional[str]
VERSION_TAG_MATCHER = re.compile(r"v(?P<version>\d+\.\d+\.\d+)")
KNOWN_APPLICATION_MIRRORS: StringList = [
    "http://chiselapp.com/user/luziferius/repository/MTGProxyPrinter",
    # Don’t use the master repository for now, as it may not be able to handle load spikes
    # "http://1337net.duckdns.org:8080/MTGProxyPrinter",
]


class BackgroundWorker(QObject):

    job_completed = Signal()  # Emitted whenever a background task finishes, both successful or unsuccessful
    card_data_update_found = Signal(int)
    application_update_found = Signal(str)
    network_error_occurred = Signal(str)

    def __init__(self, card_db: CardDatabase, parent: QObject = None):
        logger.info(f"Creating {self.__class__.__name__} instance.")
        super(BackgroundWorker, self).__init__(parent)
        self.card_db = card_db
        self.dw: CardInfoDatabaseImportWorker = None
        logger.info(f"Created {self.__class__.__name__} instance.")

    def on_thread_started(self):
        logger.debug(f"{self.__class__.__name__} event loop started, creating DownloadWorker")
        self.dw = CardInfoDatabaseImportWorker(self.card_db)
        self.dw.network_error_occurred.connect(self.network_error_occurred)

    def perform_card_data_update_check(self):
        if not settings.settings["application"].getboolean("check-for-card-data-updates"):
            logger.info("Checking for card data updates disabled. Not checking for updates.")
            self.job_completed.emit()
            return
        if not self.card_db.has_data():
            logger.info("Card database has no data. Not checking for updates.")
            self.job_completed.emit()
            return
        logger.info("Checking for card data updates.")
        try:
            total_cards_available, total_cards_in_last_update = self._is_newer_card_data_available()
            if total_cards_available and total_cards_available > total_cards_in_last_update:
                new_cards = total_cards_available - total_cards_in_last_update
                logger.info(f"New card data is available: {new_cards} new cards. Notifying the user.")
                self.card_data_update_found.emit(new_cards)
            else:
                logger.debug("No new card data found.")
        finally:
            self.job_completed.emit()

    def _is_newer_card_data_available(self) -> typing.Tuple[int, int]:
        total_cards_in_last_update = self.card_db.get_total_cards_in_last_update()
        total_cards_available = self.dw.get_available_card_count()
        logger.debug(f"Total cards during last update: {total_cards_in_last_update}")
        return total_cards_available, total_cards_in_last_update

    def perform_application_update_check(self):
        if not settings.settings["application"].getboolean("check-for-application-updates"):
            logger.info("Application update check disabled, not performing update check.")
            self.job_completed.emit()
            return
        logger.info("Checking for application updates.")
        try:
            if result := self._is_newer_application_version_available():
                logger.info(f"A new update is available: {result}. Notifying the user.")
                self.application_update_found.emit(result)
            else:
                logger.debug("No application update found.")
        finally:
            self.job_completed.emit()

    def _is_newer_application_version_available(self) -> OptStr:
        available_versions = self._read_available_application_versions()
        if available_versions and str_less_than(mtg_proxy_printer.meta_data.__version__, available_versions[0]):
            return available_versions[0]
        return None

    @staticmethod
    def _get_application_mirrors() -> StringList:
        mirrors = KNOWN_APPLICATION_MIRRORS.copy()
        random.shuffle(mirrors)
        return mirrors

    def _read_available_application_versions(self) -> StringList:
        """
        Reads the available versions from any known mirror
        :returns: List of all released versions, sorted descending.
        """
        tags = []
        for mirror in BackgroundWorker._get_application_mirrors():
            try:
                if tags := self._read_available_application_versions_from_mirror(mirror):
                    break
            except (urllib.error.URLError, socket.timeout) as e:
                logger.warning(f"Failed to read update from mirror {mirror}. Reason: {e}")
                continue
        return tags

    def _read_available_application_versions_from_mirror(self, mirror):
        data, _ = self.dw.read_from_url(f"{mirror}/json/tag/list/")
        items = ijson.items(data, "payload.tags.item")
        matches = filter(
            None,
            map(VERSION_TAG_MATCHER.fullmatch, items)
        )
        return natural_sorted((match["version"] for match in matches), reverse=True)


class UpdateChecker(QObject):

    card_data_update_found = Signal(int)
    application_update_found = Signal(str)
    network_error_occurred = Signal(str)

    _card_update_check_requested = Signal()
    _application_update_check_requested = Signal()

    def __init__(self, card_db: CardDatabase, args: Namespace, parent: QObject = None):
        logger.info(f"Creating {self.__class__.__name__} instance.")
        super(UpdateChecker, self).__init__(parent)
        self.perform_card_data_update_check = not (args.card_data and args.card_data.is_file())
        self.background_thread = QThread()
        self.background_thread.setObjectName(f"{self.__class__.__name__} background worker")
        self.background_thread.finished.connect(lambda: logger.debug(f"{self.background_thread.objectName()} stopped."))
        self.worker = self._create_background_worker(card_db, self.background_thread)
        self.running_background_jobs: int = 0
        self.background_thread.start()
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _create_background_worker(self, card_db: CardDatabase, thread_to_use: QThread) -> BackgroundWorker:
        worker = BackgroundWorker(card_db)
        worker.moveToThread(thread_to_use)
        thread_to_use.started.connect(worker.on_thread_started)
        worker.card_data_update_found.connect(self.card_data_update_found)
        worker.application_update_found.connect(self.application_update_found)
        worker.job_completed.connect(self._on_job_completed)
        worker.network_error_occurred.connect(self.network_error_occurred)
        self._card_update_check_requested.connect(worker.perform_card_data_update_check)
        self._application_update_check_requested.connect(worker.perform_application_update_check)
        return worker

    def _on_job_completed(self):
        self.running_background_jobs -= 1
        if not self.running_background_jobs:
            self.background_thread.quit()

    def check_for_updates(self):
        self._check_for_application_updates()
        if self.perform_card_data_update_check:
            self._check_for_card_data_updates()

    def _check_for_card_data_updates(self):
        self._start_background_thread_if_not_running()
        self._card_update_check_requested.emit()

    def _check_for_application_updates(self):
        self._start_background_thread_if_not_running()
        self._application_update_check_requested.emit()

    def _start_background_thread_if_not_running(self):
        if not self.running_background_jobs:
            self.background_thread.start()
        self.running_background_jobs += 1

    def stop_background_worker(self):
        if self.background_thread.isRunning():
            logger.info(f"Quitting {self.__class__.__name__} background worker thread")
            stop_thread(self.background_thread, logger)
