# Copyright (C) 2020-2024 Thomas Hess <thomas.hess@udo.edu>
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

import enum
import functools
import gzip
import math
import shutil
import textwrap
from pathlib import Path
import re
import sqlite3
import socket
import typing
import urllib.error
import urllib.parse
import urllib.request

import ijson
from PyQt5.QtCore import pyqtSignal as Signal, QObject, Qt, QThreadPool

from mtg_proxy_printer.downloader_base import DownloaderBase
from mtg_proxy_printer.model.carddb import CardDatabase, SCHEMA_NAME, with_database_write_lock
from mtg_proxy_printer.sqlite_helpers import cached_dedent
from mtg_proxy_printer.printing_filter_updater import PrintingFilterUpdater
import mtg_proxy_printer.metered_file
from mtg_proxy_printer.logger import get_logger
from mtg_proxy_printer.units_and_sizes import CardDataType, FaceDataType, BulkDataType, UUID
from mtg_proxy_printer.progress_meter import ProgressMeter
from mtg_proxy_printer.sqlite_helpers import open_database
from mtg_proxy_printer.runner import Runnable

logger = get_logger(__name__)
del get_logger

__all__ = [
    "CardInfoDownloader",
    "CardInfoDatabaseImportWorker",
    "SetWackinessScore",
]

# Just check, if the string starts with a known protocol specifier. This should only distinguish url-like strings
# from file system paths.
looks_like_url_re = re.compile(r"^(http|ftp)s?://.*")
BULK_DATA_API_END_POINT = "https://api.scryfall.com/bulk-data/all-cards"
# Set a default socket timeout to prevent hanging indefinitely, if the network connection breaks while a download
# is in progress
socket.setdefaulttimeout(5)
QueuedConnection = Qt.ConnectionType.QueuedConnection

IntTuples = typing.List[typing.Tuple[int]]
CardStream = typing.Generator[CardDataType, None, None]
CardOrFace = typing.Union[CardDataType, FaceDataType]


class CardFaceData(typing.NamedTuple):
    """Information unique to each card face."""
    printed_face_name: str
    image_uri: str
    is_front: bool
    face_number: int


class PrintingData(typing.NamedTuple):
    """Information unique to each card printing."""
    card_id: int
    set_id: int
    collector_number: str
    is_oversized: bool
    highres_image: bool
    scryfall_id: UUID


class RelatedPrintingData(typing.NamedTuple):
    printing_id: UUID
    related_id: UUID


@enum.unique
class SetWackinessScore(int, enum.Enum):
    REGULAR = 0
    PROMOTIONAL = 1
    WHITE_BORDERED = 2
    FUNNY = 3
    GOLD_BORDERED = 4
    DIGITAL = 5
    ART_SERIES = 8
    OVERSIZED = 10


class ProgressSignalContainer(QObject):
    download_progress = Signal(int)  # Emits the total number of processed data after processing each item
    download_begins = Signal(int, str)  # Emitted when the download starts. Data represents the expected total data
    download_finished = Signal()  # Emitted when the input data is exhausted and processing finished
    working_state_changed = Signal(bool)
    network_error_occurred = Signal(str)  # Emitted when downloading failed due to network issues.
    other_error_occurred = Signal(str)  # Emitted when database population failed due to non-network issues.


class CardInfoDownloader(ProgressSignalContainer):
    """
    Handles fetching the bulk card data from Scryfall and populates/updates the local card database.
    Also supports importing cards via a locally stored bulk card data file, mostly useful for debugging and testing
    purposes.

    This is the public interface. The actual implementation resides in the CardInfoDownloadWorker class, which
    is run asynchronously in another thread.
    """

    card_data_updated = Signal()

    def __init__(self, model: mtg_proxy_printer.model.carddb.CardDatabase, parent: QObject = None):
        super(CardInfoDownloader, self).__init__(parent)
        logger.info(f"Creating {self.__class__.__name__} instance.")
        logger.info(f"Using ijson backend: {ijson.backend}")
        self.model = model
        logger.info(f"Created {self.__class__.__name__} instance.")

    def download_to_file(self, download_path: Path):
        runner = CardInfoFileDownloadRunner(download_path, self)
        signals = runner.signals
        signals.download_begins.connect(self.download_begins, QueuedConnection)
        signals.download_progress.connect(self.download_progress, QueuedConnection)
        signals.download_finished.connect(self.download_finished, QueuedConnection)
        signals.network_error_occurred.connect(self.network_error_occurred, QueuedConnection)
        signals.other_error_occurred.connect(self.other_error_occurred, QueuedConnection)
        QThreadPool.globalInstance().start(runner)

    def import_from_file(self, file_path: Path):
        QThreadPool.globalInstance().start(CardInfoFileImportRunner(file_path, self))

    def import_from_api(self):
        QThreadPool.globalInstance().start(CardInfoApiImportRunner(self))


class CardInfoWorkerBase(DownloaderBase):

    def get_scryfall_bulk_card_data_url(self) -> typing.Tuple[str, int]:
        """Returns the bulk data URL and item count"""
        logger.info("Obtaining the card data URL from the API bulk data end point")
        data, _ = self.read_from_url(BULK_DATA_API_END_POINT)
        with data:
            item: BulkDataType = next(ijson.items(data, "", use_float=True))
        uri = item["download_uri"]
        size = item["size"]
        logger.debug(f"Bulk data with uncompressed size {size} bytes located at: {uri}")
        return uri, size


class CardInfoFileDownloadWorker(CardInfoWorkerBase):
    """
    This class implements downloading the raw card data to a file stored in the file system.
    """
    def __init__(self, download_path: Path, parent: QObject = None):
        super().__init__(parent=parent)
        self.download_path = download_path
        self.connection = None

    def run_download(self):
        """
        Allows the user to store the raw JSON card data at the given path.
        Accessible by a button in the Debug tab in the Settings window.
        """
        logger.info(f"Store raw card data as a compressed JSON at path {self.download_path}")
        logger.debug("Request bulk data URL from the Scryfall API.")
        url, size = self.get_scryfall_bulk_card_data_url()
        file_name = urllib.parse.urlparse(url).path.split("/")[-1]
        logger.debug(f"Obtained url: '{url}'")
        monitor = self._open_url(url, "Downloading card data:")
        # Hack: As of writing this, the CDN does not offer the size of the gzip-compressed data.
        # The API also only offers the uncompressed size. So divide the API-provided size by an empirically
        # determined compression factor to estimate the download size. Only do so, if the CDN does not offer the size.
        if monitor.content_encoding() == "gzip":
            file_name += ".gz"
            size = math.floor(size / 7.09)
            logger.info(f"Content length estimated as {size} bytes")
        if monitor.content_length <= 0:
            monitor.content_length = size
        monitor.io_finished.connect(self.download_finished)  # Unlocks UI when finished
        download_file_path = self.download_path/file_name
        logger.debug(f"Opened URL '{url}' and target file at '{download_file_path}', about to download contents.")
        with download_file_path.open("wb") as download_file, monitor:
            self.connection = monitor
            try:
                shutil.copyfileobj(monitor, download_file)
            except AttributeError:
                failure = True
            else:
                failure = False
            finally:
                self.connection = None
        if failure:
            logger.error("Download failed! Deleting incomplete download.")
            download_file_path.unlink(missing_ok=True)
        else:
            logger.info("Download completed")

    def cancel(self):
        try:
            self.connection.close()
        finally:
            pass


class CardInfoFileDownloadRunner(Runnable):
    """This runner asynchronously downloads the card data and stores it in the given location"""
    def __init__(self, download_path: Path, parent: CardInfoDownloader):
        super().__init__()
        self.parent = parent
        self.signals = ProgressSignalContainer()
        self.download_path = download_path
        self.worker: typing.Optional[CardInfoFileDownloadWorker] = None

    @with_database_write_lock  # While it technically does not access the card db, it still shares the progress meter
    def run(self):
        signals = self.signals
        # Implementation note: The actual download worker uses Qt signals, and thus is encapsulated in a class
        # derived from QObject, and not this QRunnable.
        self.worker = worker = CardInfoFileDownloadWorker(self.download_path)
        worker.download_begins.connect(signals.download_begins)
        worker.download_progress.connect(signals.download_progress)
        worker.download_finished.connect(signals.download_finished)
        worker.network_error_occurred.connect(signals.network_error_occurred)
        worker.other_error_occurred.connect(signals.other_error_occurred)
        try:
            worker.run_download()
        except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout):
            pass
        finally:
            self.release_instance()

    def cancel(self):
        try:
            self.worker.connection.close()
        except AttributeError:
            pass


class CardInfoFileImportRunner(Runnable):

    def __init__(self, path: Path, parent: CardInfoDownloader):
        super().__init__()
        self.path = path
        self.parent = parent
        self.worker = None

    def run(self):
        parent = self.parent
        self.worker = worker = CardInfoDatabaseImportWorker(parent.model)
        worker.card_data_updated.connect(parent.card_data_updated, QueuedConnection)
        worker.download_begins.connect(parent.download_begins, QueuedConnection)
        worker.download_begins.connect(lambda: parent.working_state_changed.emit(True), QueuedConnection)
        worker.download_progress.connect(parent.download_progress, QueuedConnection)
        worker.download_finished.connect(parent.download_finished, QueuedConnection)
        worker.download_finished.connect(lambda: parent.working_state_changed.emit(False), QueuedConnection)
        worker.network_error_occurred.connect(parent.network_error_occurred, QueuedConnection)
        worker.other_error_occurred.connect(parent.other_error_occurred, QueuedConnection)
        try:
            worker.import_card_data_from_local_file(self.path)
        finally:
            self.release_instance()

    def cancel(self):
        self.worker.should_run = False


class CardInfoApiImportRunner(Runnable):

    def __init__(self, parent: CardInfoDownloader):
        super().__init__()
        self.parent = parent
        self.worker = None

    def run(self):
        parent = self.parent
        self.worker = worker = CardInfoDatabaseImportWorker(parent.model)
        worker.card_data_updated.connect(parent.card_data_updated, QueuedConnection)
        worker.download_begins.connect(parent.download_begins, QueuedConnection)
        worker.download_begins.connect(lambda: parent.working_state_changed.emit(True), QueuedConnection)
        worker.download_progress.connect(parent.download_progress, QueuedConnection)
        worker.download_finished.connect(parent.download_finished, QueuedConnection)
        worker.download_finished.connect(lambda: parent.working_state_changed.emit(False), QueuedConnection)
        worker.network_error_occurred.connect(parent.network_error_occurred, QueuedConnection)
        worker.other_error_occurred.connect(parent.other_error_occurred, QueuedConnection)
        try:
            worker.import_card_data_from_online_api()
        finally:
            self.release_instance()

    def cancel(self):
        self.worker.should_run = False


class CardInfoDatabaseImportWorker(CardInfoWorkerBase):
    """
    This class implements the actual data download and import
    """
    card_data_updated = Signal()

    def __init__(self, model: mtg_proxy_printer.model.carddb.CardDatabase,
                 db: sqlite3.Connection = None, parent: QObject = None):
        logger.info(f"Creating {self.__class__.__name__} instance.")
        super().__init__(parent)
        self.model = model
        self.card_data_updated.connect(model.card_data_updated, QueuedConnection)
        self._db = db
        self.should_run = True
        self.set_code_cache: typing.Dict[str, int] = {}
        logger.info(f"Created {self.__class__.__name__} instance.")

    @property
    def db(self) -> sqlite3.Connection:
        # Delay connection creation until first access.
        # Avoids opening connections that aren't actually used and opens the connection
        # in the thread that actually uses it.
        if self._db is None:
            logger.debug(f"{self.__class__.__name__}.db: Opening new database connection")
            self._db = open_database(self.model.db_path, SCHEMA_NAME, self.model.MIN_SUPPORTED_SQLITE_VERSION)
        return self._db

    @functools.lru_cache(maxsize=1)
    def get_available_card_count(self) -> int:
        url_parameters = urllib.parse.urlencode({
            "include_multilingual": "true",
            "include_variations": "true",
            "include_extras": "true",
            "unique": "prints",
            "q": "date>1970-01-01"
        })
        url = f"https://api.scryfall.com/cards/search?{url_parameters}"
        logger.debug(f"Card data update query URL: {url}")
        try:
            total_cards_available = next(self.read_json_card_data_from_url(url, "total_cards"))
        except (urllib.error.URLError, socket.timeout, StopIteration):
            logger.warning("Reading total cards failed with a network error. Report zero available cards.")
            # TODO: Perform better notification in any error case
            total_cards_available = 0
        logger.debug(f"Total cards currently available: {total_cards_available}")
        return total_cards_available

    @with_database_write_lock
    def import_card_data_from_local_file(self, path: Path):
        try:
            data = self.read_json_card_data_from_file(path)
            self.populate_database(data)
        except Exception:
            self.db.rollback()
            logger.exception(f"Error during import from file: {path}")
            self.other_error_occurred.emit(f"Error during import from file:\n{path}")
        finally:
            self.download_finished.emit()

    @with_database_write_lock
    def import_card_data_from_online_api(self):
        logger.info("About to import card data from Scryfall")
        try:
            url, _ = self.get_scryfall_bulk_card_data_url()
            data = self.read_json_card_data_from_url(url)
            estimated_total_card_count = self.get_available_card_count()
            self.download_begins.emit(estimated_total_card_count, "Updating card data from Scryfall:")
            self.populate_database(data, total_count=estimated_total_card_count)
        except urllib.error.URLError as e:
            logger.exception("Handling URLError during card data download.")
            self.network_error_occurred.emit(str(e.reason))
            self.db.rollback()
        except socket.timeout as e:
            logger.exception("Handling socket timeout error during card data download.")
            self.network_error_occurred.emit(f"Reading from socket failed: {e}")
            self.db.rollback()
        finally:
            self.download_finished.emit()

    def read_json_card_data_from_url(self, url: str = None, json_path: str = "item") -> CardStream:
        """
        Parses the bulk card data json from https://scryfall.com/docs/api/bulk-data into individual objects.
        This function takes a URL pointing to the card data json object in the Scryfall API.

        The all cards json document is quite large (> 1GiB in 2020-11) and requires about 4GiB RAM to parse in one go.
        So use an iterative parser to generate and yield individual card objects, without having to store the whole
        document in memory.
        """
        if url is None:
            logger.debug("Request bulk data URL from the Scryfall API.")
            url, _ = self.get_scryfall_bulk_card_data_url()
            logger.debug(f"Obtained url: {url}")
        else:
            logger.debug(f"Reading from given URL {url}")
        # Ignore the monitor, because progress reporting is done in the main import loop.
        source, _ = self.read_from_url(url)
        with source:
            yield from ijson.items(source, json_path)

    def read_json_card_data_from_file(self, file_path: Path, json_path: str = "item") -> CardStream:
        file_size = file_path.stat().st_size
        raw_file = file_path.open("rb")
        with self._wrap_in_metered_file(raw_file, file_size) as file:
            if file_path.suffix.casefold() == ".gz":
                file = gzip.open(file, "rb")
            yield from ijson.items(file, json_path)

    def _wrap_in_metered_file(self, raw_file, file_size):
        monitor = mtg_proxy_printer.metered_file.MeteredFile(raw_file, file_size, self)
        monitor.total_bytes_processed.connect(self.download_progress)
        monitor.io_begin.connect(lambda size: self.download_begins.emit(size, "Importing card data from disk:"))
        return monitor

    def populate_database(self, card_data: CardStream, *, total_count: int = 0):
        """
        Takes an iterable returned by card_info_importer.read_json_card_data()
        and populates the database with card data.
        """
        card_count = 0
        try:
            card_count = self._populate_database(card_data, total_count=total_count)
        except sqlite3.Error as e:
            self.db.rollback()
            logger.exception(f"Database error occurred: {e}")
            self.other_error_occurred.emit(str(e))
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Error in parsing step")
            self.other_error_occurred.emit(f"Failed to parse data from Scryfall. Reported error: {e}")
        finally:
            self._clear_lru_caches()
            logger.info(f"Finished import with {card_count} imported cards.")

    def _populate_database(self, card_data: CardStream, *, total_count: int) -> int:
        logger.info(f"About to populate the database with card data. Expected cards: {total_count or 'unknown'}")
        self.db.execute("BEGIN IMMEDIATE TRANSACTION")  # Acquire the write lock immediately
        progress_report_step = total_count // 1000
        skipped_cards = 0
        index = 0
        face_ids: IntTuples = []
        related_printings: typing.List[RelatedPrintingData] = []
        db = self.db
        for index, card in enumerate(card_data, start=1):
            if not self.should_run:
                logger.info(f"Aborting card import after {index} cards due to user request.")
                self.download_finished.emit()
                return index
            if _should_skip_card(card):
                skipped_cards += 1
                db.execute(cached_dedent("""\
                    INSERT INTO RemovedPrintings (scryfall_id, language, oracle_id)
                      VALUES (?, ?, ?)
                      ON CONFLICT (scryfall_id) DO UPDATE
                        SET oracle_id = excluded.oracle_id,
                            language = excluded.language
                        WHERE oracle_id <> excluded.oracle_id
                           OR language <> excluded.language
                    ;"""), (card["id"], card["lang"], _get_oracle_id(card)))
                continue
            try:
                face_ids += self._parse_single_printing(card)
                related_printings += _get_related_cards(card)
            except Exception as e:
                logger.exception(f"Error while parsing card at position {index}. {card=}")
                raise RuntimeError(f"Error while parsing card at position {index}: {e}")
            if not index % 10000:
                logger.debug(f"Imported {index} cards.")
            if progress_report_step and not index % progress_report_step:
                self.download_progress.emit(index)
        logger.info(f"Skipped {skipped_cards} cards during the import")
        logger.info("Post-processing card data")
        progress_meter = ProgressMeter(
            9, "Post-processing card data:",
            self.download_begins.emit, self.download_progress.emit, self.download_finished.emit)
        self._insert_related_printings(related_printings)
        progress_meter.advance()
        self._clean_unused_data(face_ids)
        progress_meter.advance()
        updater = PrintingFilterUpdater(
            self.model, self.db, force_update_hidden_column=True)
        updater.signals.advance_progress.connect(progress_meter.advance)
        updater.store_current_printing_filters()
        # Store the timestamp of this import.
        db.execute("INSERT INTO LastDatabaseUpdate (reported_card_count) VALUES (?)\n", (index,))
        progress_meter.advance()
        # Populate the sqlite stat tables to give the query optimizer data to work with.
        db.execute("ANALYZE\n")
        db.commit()
        progress_meter.advance()
        progress_meter.finish()
        self.card_data_updated.emit()
        return index

    @functools.lru_cache(maxsize=1)
    def _read_printing_filters_from_db(self) -> typing.Dict[str, int]:
        return dict(self.db.execute("SELECT filter_name, filter_id FROM DisplayFilters"))

    def _parse_single_printing(self, card: CardDataType):
        language_id = self._insert_language(card["lang"])
        oracle_id = _get_oracle_id(card)
        card_id = self._insert_card(oracle_id)
        set_id = self.set_code_cache.get(card["set"])
        if set_id is None:
            self.set_code_cache[card["set"]] = set_id = self._insert_set(card)
        printing_id = self._handle_printing(card, card_id, set_id)
        filter_data = _get_card_filter_data(card)
        self._update_card_filters(printing_id, filter_data)
        new_face_ids = self._insert_card_faces(card, language_id, printing_id)
        return new_face_ids

    def _clear_lru_caches(self):
        """
        Clears the lru_cache instances. If the user re-downloads data, the old, cached keys become invalid and break
        the import. This will lead to assignment of wrong data via invalid foreign key relations.
        To prevent these issues, clear the LRU caches. Also frees RAM by purging data that isn’t used anymore.
        """
        lru_caches = filter(lambda item: hasattr(item, "cache_clear"), self.__dict__)
        for cache in lru_caches:
            logger.debug(str(cache.cache_info()))
            cache.cache_clear()
        self.set_code_cache.clear()
        self._db = None

    def _clean_unused_data(self, new_face_ids: IntTuples):
        """Purges all excess data, like printings that are no longer in the import data."""
        # Note: No cleanup for RelatedPrintings needed, as that is cleaned automatically by the database engine
        db = self.db
        db_face_ids = frozenset(db.execute("SELECT card_face_id FROM CardFace\n"))
        excess_face_ids = db_face_ids.difference(new_face_ids)
        logger.info(f"Removing {len(excess_face_ids)} no longer existing card faces")
        db.executemany("DELETE FROM CardFace WHERE card_face_id = ?\n", excess_face_ids)
        db.execute("DELETE FROM FaceName WHERE face_name_id NOT IN (SELECT CardFace.face_name_id FROM CardFace)\n")
        db.execute("DELETE FROM Printing WHERE printing_id NOT IN (SELECT CardFace.printing_id FROM CardFace)\n")
        db.execute('DELETE FROM MTGSet WHERE set_id NOT IN (SELECT Printing.set_id FROM Printing)\n')
        db.execute("DELETE FROM Card WHERE card_id NOT IN (SELECT Printing.card_id FROM Printing)\n")
        db.execute(cached_dedent("""\
        DELETE FROM PrintLanguage
            WHERE language_id NOT IN (
              SELECT FaceName.language_id
              FROM FaceName
            )
        """))

    def _insert_related_printings(self, related_printings: typing.List[RelatedPrintingData]):
        db = self.db
        logger.debug(f"Inserting related printings data. {len(related_printings)} entries")
        db.executemany(cached_dedent("""\
        INSERT OR IGNORE INTO RelatedPrintings (card_id, related_id)
          SELECT card_id, related_id
          FROM (SELECT card_id FROM Printing WHERE scryfall_id = ?),
               (SELECT card_id AS related_id FROM Printing WHERE scryfall_id = ?)
        """), related_printings)

    @functools.lru_cache(None)
    def _insert_language(self, language: str) -> int:
        """
        Inserts the given language into the database and returns the generated ID.
        If the language is already present, just return the ID.
        """
        db = self.db
        parameters = language,
        if result := db.execute(
                'SELECT language_id FROM PrintLanguage WHERE "language" = ?\n',
                parameters).fetchone():
            language_id, = result
        else:
            language_id = db.execute(
                'INSERT INTO PrintLanguage("language") VALUES (?)\n',
                parameters).lastrowid
        return language_id

    @functools.lru_cache(None)
    def _insert_card(self, oracle_id: UUID) -> int:
        db = self.db
        parameters = oracle_id,
        if result := db.execute("SELECT card_id FROM Card WHERE oracle_id = ?\n", parameters).fetchone():
            card_id, = result
        else:
            card_id = db.execute("INSERT INTO Card (oracle_id) VALUES (?)\n", parameters).lastrowid
        return card_id

    def _insert_set(self, card: CardDataType) -> int:
        db = self.db
        set_abbr = card["set"]
        wackiness_score = _get_set_wackiness_score(card)
        db.execute(cached_dedent(
            """\
            INSERT INTO MTGSet (set_code, set_name, set_uri, release_date, wackiness_score)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (set_code) DO
                UPDATE SET
                  set_name = excluded.set_name,
                  set_uri = excluded.set_uri,
                  release_date = excluded.release_date,
                  wackiness_score  = excluded.wackiness_score
                WHERE set_name <> excluded.set_name
                  OR set_uri <> excluded.set_uri
                  -- Wizards started to add “The List” cards to older sets, i.e. reusing the original set code for newer
                  -- reprints of cards in that set. This greater than searches for the oldest release date for a given set
                  OR release_date > excluded.release_date
                  OR wackiness_score <> excluded.wackiness_score
            """),
            (set_abbr, card["set_name"], card["scryfall_set_uri"], card["released_at"], wackiness_score)
        )
        set_id, = db.execute('SELECT set_id FROM MTGSet WHERE set_code = ?\n', (set_abbr,)).fetchone()
        return set_id

    @functools.lru_cache(None)
    def _insert_face_name(self, printed_name: str, language_id: int) -> int:
        """
        Insert the given, printed face name into the database, if it not already stored. Returns the integer
        PRIMARY KEY face_name_id, used to reference the inserted face name.
        """
        db = self.db
        parameters = (printed_name, language_id)
        if result := db.execute(
                "SELECT face_name_id FROM FaceName WHERE card_name = ? AND language_id = ?\n", parameters).fetchone():
            face_name_id, = result
        else:
            face_name_id = db.execute(
                "INSERT INTO FaceName (card_name, language_id) VALUES (?, ?)\n", parameters).lastrowid
        return face_name_id

    def _handle_printing(self, card: CardDataType, card_id: int, set_id: int) -> int:
        db = self.db
        data = PrintingData(
            card_id, set_id, card["collector_number"], card["oversized"], card["highres_image"], UUID(card["id"]),
        )
        printing_id, needs_update = self._is_printing_present(data)
        if printing_id is None:
            printing_id = db.execute(cached_dedent("""\
                INSERT INTO Printing (card_id, set_id, collector_number, is_oversized, highres_image, scryfall_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """), data).lastrowid
        if needs_update:
            db.execute(
                cached_dedent("""\
                UPDATE Printing
                  SET card_id = ?, set_id = ?, collector_number = ?, is_oversized = ?, highres_image = ?
                  WHERE printing_id = ?
                """),
                (*data[:5], printing_id),
            )
        return printing_id

    def _is_printing_present(self, new_data: PrintingData) -> typing.Tuple[typing.Optional[int], bool]:
        """
        Returns tuple printing_id, needs_update for the given printing data.
        The printing_id returns the id for the given printing, if in database, or None, if not present.
        needs_update is True, if the printing is present and needs a database update, False otherwise.
        """
        db = self.db
        printing_id, = db.execute(cached_dedent("""\
            SELECT printing_id
              FROM Printing
              WHERE scryfall_id = ?
            """), (new_data.scryfall_id,)
        ).fetchone() or (None,)
        needs_update = False
        if printing_id is not None:
            card_id, set_id, collector_number, is_oversized, highres_image = db.execute(cached_dedent("""\
            SELECT card_id, set_id, collector_number, is_oversized, highres_image
                FROM Printing
                WHERE printing_id = ?
            """), (printing_id,)).fetchone()
            # Note: No db round-trip for the scryfall_id, since it is unique and was used to look up the printing_id.
            db_data = PrintingData(
                card_id, set_id, collector_number, bool(is_oversized), bool(highres_image), new_data.scryfall_id)
            needs_update = new_data != db_data
        return printing_id, needs_update

    def _insert_card_faces(self, card: CardDataType, language_id: int, printing_id: int) -> IntTuples:
        """Inserts all faces of the given card together with their names."""
        db = self.db
        face_ids: IntTuples = []
        for face in _get_card_faces(card):
            face_name_id = self._insert_face_name(face.printed_face_name, language_id)
            card_face_id: typing.Optional[typing.Tuple[int]] = db.execute(
                "SELECT card_face_id FROM CardFace WHERE face_name_id = ? AND printing_id = ? AND is_front = ?\n",
                (face_name_id, printing_id, face.is_front)).fetchone()
            if card_face_id is None:
                card_face_id = db.execute(cached_dedent("""\
                    INSERT INTO CardFace(printing_id, face_name_id, is_front, png_image_uri, face_number)
                        VALUES (?, ?, ?, ?, ?)
                    """),
                    (printing_id, face_name_id, face.is_front, face.image_uri, face.face_number),
                ).lastrowid,
            elif db.execute(
                    "SELECT png_image_uri <> ? OR face_number <> ? FROM CardFace WHERE card_face_id = ?\n",
                    (face.image_uri, face.face_number, card_face_id[0])).fetchone()[0]:
                db.execute(
                    "UPDATE CardFace SET png_image_uri = ?, face_number = ? WHERE card_face_id = ?\n",
                    (face.image_uri, face.face_number, card_face_id[0]),
                )
            if card_face_id is not None:
                face_ids.append(card_face_id)
        return face_ids

    def _update_card_filters(
            self, printing_id: int, filter_data: typing.Dict[str, bool]):
        printing_filter_ids = self._read_printing_filters_from_db()
        db = self.db
        active_printing_filters = set(
            (printing_id, printing_filter_ids[filter_name])
            for filter_name, filter_applies in filter_data.items() if filter_applies
        )
        stored_printing_filters: typing.Set[typing.Tuple[int, int]] = set(db.execute(
            "SELECT printing_id, filter_id FROM PrintingDisplayFilter WHERE printing_id = ?",
            (printing_id,)
        ))
        if new := (active_printing_filters - stored_printing_filters):
            db.executemany(
                "INSERT INTO PrintingDisplayFilter (printing_id, filter_id) VALUES (?, ?)",
                new
            )
        if removed := (stored_printing_filters - active_printing_filters):
            db.executemany(
                "DELETE FROM PrintingDisplayFilter WHERE printing_id = ? AND filter_id = ?",
                removed
            )


def _get_related_cards(card: CardDataType):
    if card["layout"] == "token":
        # A token is never a source, as that would pull all cards creating that token
        return
    card_id = UUID(card["id"])
    for related_card in card.get("all_parts", []):
        if card_id != (related_id := UUID(related_card["id"])):
            yield RelatedPrintingData(card_id, related_id)


def _get_card_filter_data(card: CardDataType) -> typing.Dict[str, bool]:
    legalities = card["legalities"]
    return {
        # Racism filter
        "hide-cards-depicting-racism": card.get("content_warning", False),
        # Cards with placeholder images (low-res image with "not available in your language" overlay)
        "hide-cards-without-images": card["image_status"] == "placeholder",
        "hide-oversized-cards": card["oversized"],
        # Border filter
        "hide-white-bordered": card["border_color"] == "white",
        "hide-gold-bordered": card["border_color"] == "gold",
        "hide-borderless": card["border_color"] == "borderless",
        "hide-extended-art": "extendedart" in card.get("frame_effects", tuple()),
        # Some special SLD reprints of single-sided cards as double-sided cards with unique artwork per side
        "hide-reversible-cards": card["layout"] == "reversible_card",
        # “Funny” cards, not legal in any constructed format. This includes full-art Contraptions from Unstable and some
        # black-bordered promotional cards, in addition to silver-bordered cards.
        "hide-funny-cards": card["set_type"] == "funny" and "legal" not in legalities.values(),
        # Token cards
        "hide-token": card["layout"] == "token",
        "hide-digital-cards": card["digital"],
        # Specific format legality. Use .get() with a default instead of [] to not fail
        # if Scryfall removes one of the listed formats in the future.
        "hide-banned-in-brawl": legalities.get("brawl", "") == "banned",
        "hide-banned-in-commander": legalities.get("commander", "") == "banned",
        "hide-banned-in-historic": legalities.get("historic", "") == "banned",
        "hide-banned-in-legacy": legalities.get("legacy", "") == "banned",
        "hide-banned-in-modern": legalities.get("modern", "") == "banned",
        "hide-banned-in-oathbreaker": legalities.get("oathbreaker", "") == "banned",
        "hide-banned-in-pauper": legalities.get("pauper", "") == "banned",
        "hide-banned-in-penny": legalities.get("penny", "") == "banned",
        "hide-banned-in-pioneer": legalities.get("pioneer", "") == "banned",
        "hide-banned-in-standard": legalities.get("standard", "") == "banned",
        "hide-banned-in-vintage": legalities.get("vintage", "") == "banned",
    }


def _get_set_wackiness_score(card: CardDataType) -> SetWackinessScore:
    if card["oversized"]:
        result = SetWackinessScore.OVERSIZED
    elif card["layout"] == "art_series":
        result = SetWackinessScore.ART_SERIES
    elif card["digital"]:
        result = SetWackinessScore.DIGITAL
    elif card["border_color"] == "white":
        result = SetWackinessScore.WHITE_BORDERED
    elif card["set_type"] == "funny":
        result = SetWackinessScore.FUNNY
    elif card["border_color"] == "gold":
        result = SetWackinessScore.GOLD_BORDERED
    elif card["set_type"] == "promo":
        result = SetWackinessScore.PROMOTIONAL
    else:
        result = SetWackinessScore.REGULAR
    return result


def _should_skip_card(card: CardDataType) -> bool:
    # Cards without images. These have no "image_uris" item can’t be printed at all. Unconditionally skip these
    # Also skip double faced cards that have at least one face without images
    return card["image_status"] == "missing" or (
            "card_faces" in card
            and "image_uris" not in card
            and any("image_uris" not in face for face in card["card_faces"])
    )


def _get_card_faces(card: CardDataType) -> typing.Generator[CardFaceData, None, None]:
    """
    Yields a CardFaceData object for each face found in the card object.
    The printed name falls back to the English name, if the card has no printed_name key.

    Yields a single face, if the card has no "card_faces" key with a faces array. In this case,
    this function builds a "card_face" object providing only the required information from the card object itself.
    """
    faces = card.get("card_faces") or [
        FaceDataType(
            printed_name=_get_card_name(card),
            image_uris=card["image_uris"],
            name=card["name"],
            object=card["object"],
            mana_cost=card["mana_cost"],
        )
    ]
    return (
        CardFaceData(
            _get_card_name(face),
            image_uri := (face.get("image_uris") or card["image_uris"])["png"],
            # (image_uri := self._get_png_image_uri(card, face)),
            # The API does not expose which side a face is, so get that
            # detail using the directory structure in the URI. This is kind of a hack, though.
            "/front/" in image_uri,
            face_number
        )
        for face_number, face in enumerate(faces)
    )


def _get_oracle_id(card: CardDataType) -> UUID:
    """
    Reads the oracle_id property of the given card.

    This assumes that both sides of a double-faced card have the same oracle_id, in the case that the parent
    card object does not contain the oracle_id.
    """
    try:
        return UUID(card["oracle_id"])
    except KeyError:
        first_face = card["card_faces"][0]
        return UUID(first_face["oracle_id"])


def _get_card_name(card_or_face: CardOrFace) -> str:
    """
    Reads the card name. Non-English cards have both "printed_name" and "name", so prefer "printed_name".
    English cards only have the “name” attribute, so use that as a fallback.
    """
    return card_or_face.get("printed_name") or card_or_face["name"]
