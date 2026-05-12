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

import abc
import time
from collections.abc import Generator, Sequence
import functools
import gzip
import itertools
import math
import shutil
from gzip import GzipFile
from pathlib import Path
import re
import queue
import sqlite3
import socket
import typing
import urllib.error
import urllib.parse
import urllib.request
from typing import Literal, LiteralString, Any, Iterable

import ijson
from PySide6.QtCore import Qt, Slot

from mtg_proxy_printer import BlockingQueuedConnection
from mtg_proxy_printer.async_tasks.downloader_base import DownloaderBase
from mtg_proxy_printer.http_file import MeteredSeekableHTTPFile
from mtg_proxy_printer.model.carddb import CardDatabase, SCHEMA_NAME, with_database_write_lock, \
    DEFAULT_DATABASE_LOCATION
from mtg_proxy_printer.sqlite_helpers import cached_dedent
from mtg_proxy_printer.async_tasks.printing_filter_updater import PrintingFilterUpdater
import mtg_proxy_printer.metered_file
from mtg_proxy_printer.logger import get_logger
from mtg_proxy_printer.units_and_sizes import CardDataType, FaceDataType, BulkDataType, UUID, SetsAPIDataType
from mtg_proxy_printer.sqlite_helpers import open_database
from mtg_proxy_printer.async_tasks.base import AsyncTask

logger = get_logger(__name__)
del get_logger

__all__ = [
    "CardInfoDownloadTaskBase",
    "DatabaseImportTask",
    "ApiStreamTask",
    "FileDownloadTask",
    "FileStreamTask",
]

BULK_DATA_API_END_POINT = "https://api.scryfall.com/bulk-data/all-cards"
# Constants determined empirically. These fluctuate a bit over time, but give reasonable estimates.
AVERAGE_SIZE_PER_UNCOMPRESSED_JSON_ENTRY_IN_BYTES = 4706
GZIP_COMPRESSION_FACTOR = 7.09

# Set a default socket timeout to prevent hanging indefinitely, if the network connection breaks while a download
# is in progress
socket.setdefaulttimeout(5)

CardStream = Generator[CardDataType, None, None]
CardOrFace = CardDataType | FaceDataType
CardDataQueue = queue.Queue[tuple[CardDataType, ...] | None]


class CardFaceData(typing.NamedTuple):
    """Information unique to each card face."""
    printed_face_name: str
    image_uri: str
    is_front: bool


class RelatedPrintingData(typing.NamedTuple):
    printing_id: UUID
    related_id: UUID


class CardInfoDownloadTaskBase(DownloaderBase):
    """Base class for tasks that fetch card data from the Scryfall bulk-data API."""

    def get_scryfall_bulk_card_data_url(self) -> tuple[str, int]:
        """Returns the bulk data URL and item count"""
        logger.info("Obtaining the card data URL from the API bulk data end point")
        data, _ = self.read_from_url(BULK_DATA_API_END_POINT)
        with data:
            item: BulkDataType = next(ijson.items(data, "", use_float=True))
        uri = item["download_uri"]
        size = item["size"]
        logger.debug(f"Bulk data with uncompressed size {size} bytes located at: {uri}")
        return uri, size


class FileDownloadTask(CardInfoDownloadTaskBase):
    """Downloading the raw card data to a file stored in the file system."""
    def __init__(self, download_path: Path):
        super().__init__()
        self.download_path = download_path
        self.connection = None

    def run(self):
        try:
            self.run_download()
        except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout) as e:
            self.error_occurred.emit(e.reason)

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
        monitor = self._open_url(
            url,
            self.tr("Downloading card data:", "Progress bar label text"))
        # Hack: As of writing this, the CDN does not offer the size of the gzip-compressed data.
        # The API also only offers the uncompressed size. So divide the API-provided size by an empirically
        # determined compression factor to estimate the download size. Only do so, if the CDN does not offer the size.
        if monitor.content_encoding() == "gzip":
            file_name += ".gz"
            size = math.floor(size / GZIP_COMPRESSION_FACTOR)
            logger.info(f"Content length estimated as {size} bytes")
        if monitor.content_length <= 0:
            monitor.content_length = size
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
                self.connection.close()
                self.connection = None
                self.task_completed.emit()
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


class StreamTask(CardInfoDownloadTaskBase):
    """Base class for tasks that stream data via a queue."""
    _queue_depth = 5
    _batch_size = 5000

    def __init__(self, source: str | Path = None, json_path: str = "item"):
        super().__init__()
        self.open_file: GzipFile | MeteredSeekableHTTPFile | None = None
        self.source = source
        self.json_path = json_path
        self.queue: CardDataQueue = queue.Queue(self._queue_depth)
        self._stream = None

    def _enqueue_stream(self, data: CardStream):
        """Put the CardStream into the queue for downstream consumption"""
        try:
            for batch in itertools.batched(data, self._batch_size):  # type: tuple[CardDataType, ...]
                self.queue.put(batch)
        except AttributeError:  # Cancelling closes and deletes the underlying file, causing an AttributeError in run()
            logger.info(f"{self.__class__.__name__}: Read operation cancelled")
        except Exception as e:
            # Cancelling also exhausts the queue to prevent deadlocks.
            # That exhaustion deliberately causes a "read from closed file".
            # So suppress any error, if the stream no longer exists, as it only disappears through cancel()
            if self._stream is not None:
                signal = self.error_occurred if isinstance(self.source, Path) else self.network_error_occurred
                logger.warning(f"{self.__class__.__name__}: Unexpected end of stream")
                signal.emit(str(e))
        else:
            logger.info(f"{self.__class__.__name__}: Card data exhausted.")
        finally:
            self.queue.put(None)

    @property
    def report_progress(self):
        return False

    @property
    @abc.abstractmethod
    def item_count(self) -> int:
        return 0

    @property
    def can_cancel(self) -> bool:
        return True

    def cancel(self):
        logger.debug(f"{self.__class__.__name__}: entering cancel()")
        if self.open_file is not None:
            self.open_file.close()
        self.open_file = self._stream = None
        while not self.queue.empty():
            # Flush the queue to unblock a potentially blocked writer thread:
            # The consumer thread stops immediately within it's currently processed batch,
            # so may leave the producer in a deadlock waiting for a free queue slot that will never arrive.
            try:
                self.queue.get(block=False)
            except queue.Empty:
                time.sleep(0.1)

        logger.debug(f"{self.__class__.__name__}: Cancel completed")


class FileStreamTask(StreamTask):
    """Reads card data from a local file and streams the content"""

    def run(self):
        data = self.read_json_card_data_from(self.source, self.json_path)
        self._enqueue_stream(data)

    def read_json_card_data_from(self, file_path: Path, json_path: str = "item") -> CardStream:
        file_size = file_path.stat().st_size
        raw_file = file_path.open("rb")
        with self._wrap_in_metered_file(raw_file, file_size) as file:
            if file_path.suffix.casefold() == ".gz":
                self.open_file = file = gzip.open(file, "rb")
            self._stream = ijson.items(file, json_path, use_float=True)
            yield from self._stream

    def _wrap_in_metered_file(self, raw_file, file_size: int):
        monitor = mtg_proxy_printer.metered_file.MeteredFile(raw_file, file_size)
        monitor.total_bytes_processed.connect(self.set_progress)
        monitor.io_begin.connect(lambda size: self.task_begins.emit(
            size,
            self.tr("Importing card data from disk:", "Progress bar label text")))
        return monitor

    @property
    def item_count(self):
        estimated_total_card_count = round(
            (GZIP_COMPRESSION_FACTOR if self.source.suffix.casefold() == ".gz" else 1)
            * self.source.stat().st_size
            / AVERAGE_SIZE_PER_UNCOMPRESSED_JSON_ENTRY_IN_BYTES
        )
        return estimated_total_card_count


class ApiStreamTask(StreamTask):
    """
    This class implements reading the card data from the Scryfall API as a CardStream.

    When used as a Task, it streams the decoded card data from the API and batches the result.
    This encapsulates requesting data via HTTPS, decryption, gzip stream decompression and parsing into dicts via ijson.
    It enqueues a single None as the last value after finishing the last batch.
    """
    def run(self):
        logger.info(f"{self.__class__.__name__}: About to stream card data in batches of {self._batch_size}")
        data = self.read_json_card_data_from(self.source, self.json_path)
        self._enqueue_stream(data)

    def read_json_card_data_from(self, url: str = None, json_path: str = "item") -> CardStream:
        """
        Parses the bulk card data JSON from https://scryfall.com/docs/api/bulk-data into individual objects.
        This function takes a URL pointing to the card data JSON array in the Scryfall API.

        The all cards JSON document is quite large (> 2.1GiB in 2024-10) and requires about 8GiB RAM to parse in one go.
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
        self.open_file, _ = self.read_from_url(url)  # type: GzipFile | MeteredSeekableHTTPFile, MeteredSeekableHTTPFile
        with self.open_file:
            self._stream = ijson.items(self.open_file, json_path, use_float=True)
            yield from self._stream

    @functools.cache
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
            total_cards_available = next(self.read_json_card_data_from(url, "total_cards"))
        except (urllib.error.URLError, socket.timeout, StopIteration) as e:
            logger.warning(
                "Requesting the number of available cards on Scryfall failed with a network error. "
                "Report zero available cards.")
            self.network_error_occurred.emit(
                self.tr(
                    "Requesting the number of available cards on Scryfall failed: \n{error}",
                    "Error message shown in a message box").format(error=e))
            total_cards_available = 0
        logger.debug(f"Total cards currently available: {total_cards_available}")
        return total_cards_available

    @property
    def item_count(self):
        return self.get_available_card_count()


class SetIconImportTask(DownloaderBase):

    def __init__(self, db: sqlite3.Connection = None, carddb_path: Path | Literal[":memory:"] = DEFAULT_DATABASE_LOCATION):
        super().__init__()
        self.carddb_path = carddb_path
        self._db = db
        self.db_created = db is None
        self.should_run = True
        self.network_error_occurred.connect(self.cancel)
        self.error_occurred.connect(self.cancel)

    def run(self):
        db = self.db
        logger.info("About to fetch set symbols.")
        # icon_filename is empty for unset symbols, so they are guaranteed to be unequal to the file name in the URI.
        symbols_in_db: dict[UUID, str] =  dict(db.execute("SELECT set_scryfall_id, icon_file_name FROM MTGSet"))
        if not self.should_run: return
        progress_bar_text = self.tr("Download set symbols: ", "Progress bar label")
        self.task_begins.emit(1, progress_bar_text)
        icon_uris = self._fetch_icon_uris_to_download(symbols_in_db)
        if not icon_uris:
            logger.info("No icons to download.")
            self.task_completed.emit()
            return
        # Now that the number of items to download is known, update the progress bar
        download_count = len(icon_uris)
        self.task_begins.emit(download_count+2, progress_bar_text)
        self.advance_progress.emit()
        if not self.should_run: return
        logger.debug(f"Total of {download_count} SVG icon URIs to download, starting downloads…")
        icon_svgs = self._fetch_icon_svgs(icon_uris)
        if not self.should_run: return
        logger.debug("SVG icons downloaded, updating the database…")
        db.executemany(
            "UPDATE MTGSet SET icon_svg = ?, icon_file_name = ? WHERE set_scryfall_id = ?",
            icon_svgs
        )
        logger.debug(f"All {download_count} SVG icons updated.")
        self.advance_progress.emit()
        logger.info("All missing or outdated set symbols downloaded")
        self.task_completed.emit()

    def _fetch_icon_uris_to_download(self, filenames_in_db: dict[UUID, str]) -> dict[UUID, str]:
        """
        Fetches the SVG icon URIs from the Scryfall API.
        :param filenames_in_db: Mapping of currently downloaded set symbols. Keys are set ids, values are filenames.
        :returns: Mapping from set ids to SVG icon URIs
        """
        logger.debug(f"Requesting URIs for all {len(filenames_in_db)} in the database from the set code API end point.")
        # This bulk end point is sometimes slow to react
        socket.setdefaulttimeout(30)
        open_file, _ = self.read_from_url("https://api.scryfall.com/sets")
        with open_file:
            response = open_file.read()
        socket.setdefaulttimeout(5)
        # Data is fetched. Check against the file names in the database. Any difference will cause a re-download.
        # Missing symbols have empty file names in the database, which is a guaranteed to be different
        # from the non-empty file names supplied by the API.
        result: dict[UUID, str] = {}
        stream: Iterable[SetsAPIDataType] = ijson.items(response, "data.item", use_float=True)
        for set_item in stream:
            set_scryfall_id = set_item["id"]
            uri = set_item["icon_svg_uri"]
            file_name = uri.rsplit("/", 1)[1]
            # If a set is completely skipped during import, this get() avoids a KeyError
            if filenames_in_db.get(set_scryfall_id) != file_name:
                result[set_scryfall_id] = uri
        # All parsed and filtered
        self.advance_progress.emit()
        return result

    def _fetch_icon_svgs(self, icon_uris: dict[UUID, str]) -> list[tuple[bytes, str, UUID]]:
        """
        Fetches the given SVG icons. Note: The returned tuples have the set_scryfall_id at the end, because that's the
        item order expected by the database UPDATE query.
        :param icon_uris: Mapping from set_scryfall_id to the SVG uri
        :returns: list with tuples [SVG source code, file name, set_scryfall_id]
        """
        result : list[tuple[bytes, str, UUID]] = []
        for set_scryfall_id, uri in icon_uris.items():
            if not self.should_run: return result
            svg = self.read_from_url(uri,)[0].read()
            filename = uri.rsplit("/", 1)[1]
            result.append((svg, filename, set_scryfall_id))
            self.advance_progress.emit()
        return result


    @property
    def db(self) -> sqlite3.Connection:
        # Delay connection creation until first access.
        # Avoids opening connections that aren't actually used and opens the connection
        # in the thread that actually uses it.
        if self._db is None:
            logger.debug(f"{self.__class__.__name__}.db: Opening new database connection")
            self._db = open_database(self.carddb_path, SCHEMA_NAME)
        return self._db

    def _read_optional_scalar_from_db(self, query: LiteralString, parameters: Sequence[Any] = ()):
        """
        Runs the query with the given parameters that is expected to return either a singular value or None,
        and returns the result
        """
        match self.db.execute(query, parameters).fetchone():
            case result, :
                return result
            case _, *_:
                raise RuntimeError(f"BUG: {query} result was not a scalar")
        return None

    @property
    def can_cancel(self) -> bool:
        return True

    def cancel(self):
        logger.info(f"{self.__class__.__name__}: Cancelling…")
        self.should_run = False
        self.task_completed.emit()

class DatabaseImportTask(AsyncTask):
    """This class implements importing a CardStream into the given CardDatabase instance"""

    def __init__(self, source: StreamTask, db: sqlite3.Connection = None,
                 carddb_path: Path | Literal[":memory:"] = DEFAULT_DATABASE_LOCATION):
        logger.info(f"Creating {self.__class__.__name__} instance.")
        super().__init__()
        self.carddb_path = carddb_path
        self.source = source
        # Any error in the data source must cancel the consumer to roll back any open transaction.
        # The most efficient way is to use the signal/slot mechanism already in place and call cancel using that.
        source.error_occurred.connect(self.cancel, BlockingQueuedConnection)
        source.network_error_occurred.connect(self.cancel, BlockingQueuedConnection)
        self._subtask: AsyncTask | None = None
        self._db = db
        self.db_created = db is None
        self.should_run = True
        self.set_code_cache: dict[str, int] = {}
        self._printing_filter_dict: dict[str, bool] = {}
        logger.info(f"Created {self.__class__.__name__} instance.")

    @property
    def can_cancel(self) -> bool:
        return True

    @Slot()
    def cancel(self):
        if self._subtask is not None and self._subtask.can_cancel:
            self._subtask.cancel()
        self.source.cancel()
        self.should_run = False

    @property
    def db(self) -> sqlite3.Connection:
        # Delay connection creation until first access.
        # Avoids opening connections that aren't actually used and opens the connection
        # in the thread that actually uses it.
        if self._db is None:
            logger.debug(f"{self.__class__.__name__}.db: Opening new database connection")
            self._db = open_database(self.carddb_path, SCHEMA_NAME)
        return self._db

    @staticmethod
    def _consume_from_queue(queue_: CardDataQueue) -> CardStream:
        while (batch := queue_.get()) is not None:
            yield from batch

    def _read_optional_scalar_from_db(self, query: LiteralString, parameters: Sequence[Any] = ()):
        """
        Runs the query with the given parameters that is expected to return either a singular value or None,
        and returns the result
        """
        match self.db.execute(query, parameters).fetchone():
            case result, :
                return result
            case _, *_:
                raise RuntimeError(f"BUG: {query} result was not a scalar")
        return None

    @with_database_write_lock()
    def run(self):
        item_count = self.source.item_count
        file_task = isinstance(self.source, FileStreamTask)
        if file_task:
            logger.info("About to import card data from a local file on disk")
            self.task_begins.emit(
                item_count,
                self.tr("Import card data from File:", "Progress bar label text"))
        else:
            logger.info("About to import card data from Scryfall")
            self.task_begins.emit(
                item_count,
                self.tr("Update card data from Scryfall:", "Progress bar label text"))
        try:
            items = self._consume_from_queue(self.source.queue)
            self.populate_database(items, total_count=item_count)
        except Exception as e:
            self.db.rollback()
            if file_task:
                logger.exception(
                    f"Error during import from file: {self.source.source}")
                self.error_occurred.emit(self.tr(
                    "Error during import from file:\n{path}",
                    "Error message shown in a message box").format(path=self.source.source))
            else:
                logger.exception(
                    f"Error during import from Scryfall: {e}")
                self.error_occurred.emit(self.tr(
                    "Error during update from Scryfall", "Error message shown in a message box"))
        finally:
            if self.db_created:
                self.db.close()
                self._db = None
            self.task_completed.emit()

    def populate_database(self, card_data: CardStream, *, total_count: int = 0):
        """
        Takes an iterable returned by card_info_importer.read_json_card_data()
        and populates the database with card data.
        """
        card_count = 0
        try:
            card_count = self._populate_database(card_data, total_count=total_count)
            self.task_completed.emit()
        except sqlite3.Error as e:
            self.db.rollback()
            logger.exception(f"Database error occurred: {e}")
            self.error_occurred.emit(str(e))
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Error in parsing step")
            self.error_occurred.emit(
                self.tr(
                    "Failed to parse data from Scryfall. Reported error: {error}",
                    "Error message shown in a message box").format(error=e))
        finally:
            logger.info(f"Finished import with {card_count} imported cards.")

    def _populate_database(self, card_data: CardStream, *, total_count: int) -> int:
        logger.info(f"About to populate the database with card data. Expected cards: {total_count or 'unknown'}")
        db = self.db
        db.execute("BEGIN IMMEDIATE TRANSACTION")  # Acquire the write lock immediately
        progress_report_step = total_count // 1000
        skipped_cards = 0
        index = 0
        related_printings: list[RelatedPrintingData] = []
        for index, card in enumerate(card_data, start=1):
            if not self.should_run:
                logger.info(f"Aborting card import after {index} cards due to user request or data error.")
                db.rollback()
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
                self._parse_single_printing(card)
                related_printings += _get_related_cards(card)
            except Exception as e:
                logger.exception(f"Error while parsing card at position {index}. {card=}")
                raise RuntimeError(f"Error while parsing card at position {index}: {e}")
            if not index % 10000:
                logger.debug(f"Imported {index} cards.")
            if progress_report_step and not index % progress_report_step:
                self.set_progress.emit(index)
        logger.info(f"Skipped {skipped_cards} cards during the import")
        if not self.should_run:
            logger.info(f"Aborting card import after {index} cards due to user request or data error.")
            db.rollback()
            return index
        logger.info("Post-processing card data")
        self.task_begins.emit(
            5 + PrintingFilterUpdater.PROGRESS_STEP_COUNT,
            self.tr("Post-processing card data:", "Progress bar label text"))
        self._insert_related_cards(related_printings)
        self.advance_progress.emit()
        self._clean_unused_data()
        self.advance_progress.emit()
        db.execute("""\
        -- Remove previously unacceptable printings, if those were acceptable this import.
        DELETE FROM RemovedPrintings WHERE scryfall_id IN (
          SELECT scryfall_id FROM Printing
        )""")
        self.advance_progress.emit()
        self._subtask = updater = PrintingFilterUpdater(
            CardDatabase(self.carddb_path, check_same_thread=True, register_exit_hooks=False),
            self.db, force_update_hidden_column=True)
        updater.advance_progress.connect(self.advance_progress)
        updater.store_current_printing_filters()  # Don't call run() to not deadlock via the db semaphore
        self._subtask = updater = SetIconImportTask(db, self.carddb_path)
        updater.error_occurred.connect(updater.cancel)
        self.request_register_subtask.emit(updater)
        if self.should_run:
            updater.run()
        # Store the timestamp of this import.
        db.execute("INSERT INTO LastDatabaseUpdate (reported_card_count) VALUES (?)\n", (index,))
        self.advance_progress.emit()
        # Populate the sqlite stat tables to give the query optimizer data to work with.
        db.execute("ANALYZE\n")
        self.advance_progress.emit()
        if self.should_run:
            db.commit()
        else:
            db.rollback()
        self.task_completed.emit()
        return index

    @functools.cache
    def _read_available_printing_filters_from_db(self) -> dict[str, int]:
        """
        Returns all defined filters as a mapping from string key to internal filter_id.
        """
        return dict(self.db.execute("SELECT filter_name, filter_id FROM PrintingFilters"))

    def _parse_single_printing(self, card: CardDataType):
        oracle_id = _get_oracle_id(card)
        is_card = not (
            card["layout"] in {"art_series", "double_faced_token", "token", "vanguard"}
            or card["set_type"] == "token")
        english_name = card["name"]
        card_id = self._insert_or_update_card(oracle_id, is_card, english_name)
        set_code = card["set"]
        if (set_id := self.set_code_cache.get(set_code)) is None:
            self.set_code_cache[set_code] = set_id = self._insert_or_update_set(card)
        printing_id = self._insert_or_update_printing(card, card_id, set_id)
        _get_card_filter_data(card, self._printing_filter_dict)
        self._insert_or_update_card_filters(printing_id, self._printing_filter_dict)
        self._insert_or_update_printing_faces(card, printing_id)

    def _clean_unused_data(self):
        """Purges all excess data, like printings that are no longer in the import data."""
        db = self.db
        db.execute("DELETE FROM MTGSet WHERE MTGSet.set_id NOT IN (SELECT Printing.set_id FROM Printing)")
        db.execute("DELETE FROM Card WHERE Card.card_id NOT IN (SELECT Printing.card_id FROM Printing)")
        db.execute(cached_dedent("""\
        DELETE FROM Printing WHERE Printing.printing_id NOT IN (
          SELECT PrintingFace.printing_id FROM PrintingFace)
          """))

    def _insert_related_cards(self, related_cards: list[RelatedPrintingData]):
        db = self.db
        logger.debug(f"Inserting related cards data. {len(related_cards)} entries")
        db.execute("DELETE FROM RelatedCards")
        # Implementation note on "INSERT OR IGNORE" below:
        # On all cards with related cards, the related cards array also includes the identity/self reference.
        # For the relation, Scryfall uses the print-identifying scryfall id.
        # But on some cards, the self-reference is given by another printing.
        # So for example, the etched foil printing refers to itself in the related cards list by the regular printing.
        # And because the related card object only contains the scryfall id as the identification, the parser step
        # cannot identify these cases.
        # If it happens, the constraint attached to table is violated, and the entry should be ignored during the insert.
        db.executemany(cached_dedent("""\
        INSERT OR IGNORE INTO RelatedCards (card_id, related_id)
          SELECT card_id, related_id
          FROM (SELECT card_id FROM Printing WHERE scryfall_id = ?),
               (SELECT card_id AS related_id FROM Printing WHERE scryfall_id = ?)
        """), related_cards)

    @functools.cache
    def _insert_or_update_card(self, oracle_id: UUID, is_card: bool, english_name) -> int:
        db = self.db
        query = cached_dedent("""\
        SELECT card_id, ( -- _insert_or_update_card()
          is_card <> ?
          OR english_name <> ?
        ) AS needs_update
        FROM Card WHERE oracle_id = ?
        """)
        parameters = [is_card, english_name, oracle_id]
        match db.execute(query, parameters).fetchone():
            case card_id, 0:
                pass  # Already present and nothing changed
            case None:
                card_id = db.execute(cached_dedent("""\
                INSERT INTO Card  -- _insert_or_update_card()
                       (is_card, english_name, oracle_id)
                VALUES (?,       ?,            ?)
                """), parameters).lastrowid
            case card_id, 1:
                parameters[-1] = card_id
                db.execute(cached_dedent("""\
                UPDATE Card -- _insert_or_update_card()
                  SET is_card = ?, english_name = ?
                  WHERE card_id = ?
                """), parameters)
            case check_result:
                raise RuntimeError(f"Unexpected data: {check_result}")
        return card_id

    def _insert_or_update_set(self, card: CardDataType) -> int:
        db = self.db
        set_code = card["set"]
        query = cached_dedent("""\
        SELECT set_ID, ( -- _insert_or_update_set()
          set_name <> ?
          OR release_date > unixepoch(?, 'utc')
          OR set_scryfall_id <> ?
        ) AS needs_update
        FROM MTGSet WHERE set_code = ?
        """)
        parameters = [card["set_name"], card["released_at"], card["set_id"], set_code]
        match db.execute(query, parameters).fetchone():
            case set_id, 0:
                pass  # Already present and nothing changed
            case None:
                set_id = db.execute(cached_dedent("""\
                INSERT INTO MTGSet  -- _insert_or_update_set()
                       (set_name, release_date,        set_scryfall_id, set_code)
                VALUES (?,        unixepoch(?, 'utc'), ?,               ?)
                ON CONFLICT (set_scryfall_id) DO UPDATE 
                  SET set_code = excluded.set_code 
                  WHERE set_scryfall_id = excluded.set_scryfall_id
                """), parameters).lastrowid
            case set_id, 1:
                parameters[-1] = set_id
                db.execute(cached_dedent("""\
                UPDATE MTGSet -- _insert_or_update_set()
                  SET (set_name, release_date,        set_scryfall_id)
                    = (?,        unixepoch(?, 'utc'), ?)
                  WHERE set_id = ?
                """), parameters)
            case check_result:
                raise RuntimeError(f"Unexpected data: {check_result}")
        return set_id

    def _insert_or_update_printing(self, card: CardDataType, card_id: int, set_id: int) -> int:
        db = self.db
        is_dfc = "card_faces" in card and "image_uris" not in card
        query = cached_dedent("""\
        SELECT printing_id, ( -- _insert_or_update_printing()
              set_id <> ?
              OR collector_number <> ? 
              OR language <> ?
              OR card_id <> ?
              OR is_oversized <> ? 
              OR is_highres_image <> ?
              OR is_dfc <> ?
          ) AS needs_update
          FROM Printing
          WHERE scryfall_id = ?
        """)
        parameters = [
            set_id, card["collector_number"], card["lang"], card_id,
            card["oversized"], card["highres_image"], is_dfc, card["id"]]
        match db.execute(query, parameters).fetchone():
            case None:                
                printing_id = db.execute(cached_dedent("""\
                INSERT INTO Printing  -- _insert_or_update_printing()
                       (set_id, collector_number, language, card_id, is_oversized, is_highres_image, is_dfc, scryfall_id)
                VALUES (?,      ?,                ?,        ?,       ?,            ?,                ?,      ?)
                """), parameters).lastrowid
            case printing_id, 1:
                parameters.append(printing_id)
                db.execute(cached_dedent("""\
                UPDATE Printing -- _insert_or_update_printing()
                  SET (set_id, collector_number, language, card_id, is_oversized, is_highres_image, is_dfc, scryfall_id)
                    = (?,      ?,                ?,        ?,       ?,            ?,                ?,      ?)
                  WHERE printing_id = ?
                """), parameters)
            case printing_id, 0:
                pass  # Already present and nothing changed
            case check_result:
                raise RuntimeError(f"Unexpected data: {check_result}")
        return printing_id

    def _insert_or_update_printing_faces(self, card: CardDataType, printing_id: int):
        """Inserts all faces of the given card together with their names."""
        db = self.db
        check_query = cached_dedent("""\
        SELECT (face_name <> ? OR png_image_uri <> ?) AS needs_update -- _insert_or_update_printing_faces()
          FROM PrintingFace
          WHERE printing_id = ? 
            AND is_front = ?
        """)
        for face in _get_card_faces(card):
            parameters = face.printed_face_name, face.image_uri, printing_id, face.is_front
            match self._read_optional_scalar_from_db(check_query, parameters):
                case None:
                    db.execute(cached_dedent("""\
                    INSERT INTO PrintingFace (face_name, png_image_uri, printing_id, is_front)
                      VALUES                 (?,         ?,             ?,           ?)
                    """), parameters)
                case 1:
                    db.execute(cached_dedent("""\
                    UPDATE PrintingFace
                      SET   face_name = ?, png_image_uri = ? 
                      WHERE printing_id = ? AND is_front = ?
                    """), parameters)
                case 0:
                    continue  # Everything already present and up-to-date
                case check_result:
                    raise RuntimeError(f"Unexpected data retuned from query: {check_query} {check_result=}")

    def _insert_or_update_card_filters(self, printing_id: int, filter_data: dict[str, bool]):
        printing_filter_ids = self._read_available_printing_filters_from_db()
        db = self.db
        active_printing_filters = set(
            (printing_id, printing_filter_ids[filter_name])
            for filter_name, filter_applies in filter_data.items() if filter_applies
        )
        stored_printing_filters: set[tuple[int, int]] = set(db.execute(
            "SELECT printing_id, filter_id FROM FilterAppliesTo WHERE printing_id = ?",
            (printing_id,)
        ))
        if new := (active_printing_filters - stored_printing_filters):
            db.executemany(
                "INSERT INTO FilterAppliesTo (printing_id, filter_id) VALUES (?, ?)",
                new
            )
        if removed := (stored_printing_filters - active_printing_filters):
            db.executemany(
                "DELETE FROM FilterAppliesTo WHERE printing_id = ? AND filter_id = ?",
                removed
            )


def _get_related_cards(card: CardDataType):
    if card["layout"].endswith("token"):
        # Tokens are never sources, as that would pull all cards creating that token
        return
    card_id = card["id"]
    is_dungeon = card.get("type_line") == "Dungeon"
    for related_card in card.get("all_parts", []):
        related_id = related_card["id"]
        related_is_token = related_card["component"].endswith("token")
        # No self reference allowed. And the implication is_dungeon ⇒ related_is_token must be True.
        # I.e. If the source is a Dungeon, then it may link with tokens only, and nothing else.
        if card_id != related_id and (not is_dungeon or related_is_token):
            yield RelatedPrintingData(card_id, related_id)


def _get_card_filter_data(card: CardDataType, filter_dict: dict[str, bool]):
    legalities = card["legalities"]
    image_status = card["image_status"]
    border_color = card["border_color"]
    # The API documentation states the type_line is mandatory, but reversible cards miss it in the parent Card.
    # Performance note: Converting into sets and computing if they are not disjoint is more expensive than this.
    type_line = card.get("type_line") or " // ".join(face["type_line"] for face in card.get("card_faces", ()))
    is_token = any(("Dungeon" in type_line, "Token" in type_line, "Emblem" in type_line))
    # Racism filter
    filter_dict["hide-cards-depicting-racism"] = card.get("content_warning", False)
    # Cards with placeholder images (low-res image with "not available in your language" overlay)
    filter_dict["hide-cards-without-images"] = image_status == "placeholder"
    filter_dict["hide-low-resolution-cards"] = image_status == "lowres"
    filter_dict["hide-oversized-cards"] = card["oversized"]
    # Frame and border filter
    filter_dict["hide-full-art-cards"] = card["full_art"]
    filter_dict["hide-textless-cards"] = card["textless"]
    filter_dict["hide-white-bordered"] = border_color == "white"
    filter_dict["hide-gold-bordered"] = border_color == "gold"
    filter_dict["hide-borderless"] = border_color == "borderless"
    filter_dict["hide-extended-art"] = "extendedart" in card.get("frame_effects", ())
    # Some special SLD reprints of single-sided cards as double-sided cards with unique artwork per side
    filter_dict["hide-reversible-cards"] = card["layout"] == "reversible_card"
    # “Funny” cards, not legal in any constructed format. This includes full-art Contraptions from Unstable and some
    # black-bordered promotional cards, in addition to silver-bordered cards.
    filter_dict["hide-funny-cards"] = card["set_type"] == "funny" and "legal" not in legalities.values()
    filter_dict["hide-token"] = is_token
    filter_dict["hide-digital-cards"] = card["digital"]
    filter_dict["hide-art-series-cards"] = card["layout"] == "art_series"
    filter_dict["hide-universes-beyond-cards"] = "universesbeyond" in card.get("promo_types", ())
    # Specific format legality. Use .get() with a default instead of [] to not fail
    # if Scryfall removes one of the listed formats in the future.
    filter_dict["hide-banned-in-brawl"] = legalities.get("brawl") == "banned"
    filter_dict["hide-banned-in-commander"] = legalities.get("commander") == "banned"
    filter_dict["hide-banned-in-historic"] = legalities.get("historic") == "banned"
    filter_dict["hide-banned-in-legacy"] = legalities.get("legacy") == "banned"
    filter_dict["hide-banned-in-modern"] = legalities.get("modern") == "banned"
    filter_dict["hide-banned-in-oathbreaker"] = legalities.get("oathbreaker") == "banned"
    filter_dict["hide-banned-in-pauper"] = legalities.get("pauper") == "banned"
    filter_dict["hide-banned-in-penny"] = legalities.get("penny") == "banned"
    filter_dict["hide-banned-in-pioneer"] = legalities.get("pioneer") == "banned"
    filter_dict["hide-banned-in-standard"] = legalities.get("standard") == "banned"
    filter_dict["hide-banned-in-vintage"] = legalities.get("vintage") == "banned"


def _should_skip_card(card: CardDataType) -> bool:
    # Cards without images. These have no "image_uris" item can’t be printed at all. Unconditionally skip these
    # Also skip double faced cards that have at least one face without images
    return card["image_status"] == "missing" or (
        # Has faces, but no image_uris, therefore is a DFC
        "card_faces" in card and "image_uris" not in card
        # And at least one face has no images
        and any("image_uris" not in face for face in card["card_faces"])
    )


def _get_card_faces(card: CardDataType) -> list[CardFaceData]:
    """
    Returns a CardFaceData object for each side found in the card object.
    The printed name falls back to the English name, if the card has no printed_name key.

    Returns 2 faces for DFCs, and one for single-faced cards.
    Cards with multiple faces per side use the "Face 1 // Face 2" notation.
    """
    card_name = card.get("printed_name") or card["name"]
    # Non-English cards use "printed_name" (and have English fallbacks in "name"),
    # while English cards only use "name", and do not have "printed_name" present.
    #
    # English cards with multiple faces have a combined, top-level name "Face1 // Face2".
    # Non-English cards do not have a localized equivalent, and thus require
    # to build it manually from the individual values.
    match card:
        # DFCs have "image_uris" keys within card_faces
        case {"card_faces": [
                {"image_uris": {"png": first_image}, "printed_name": f},
                {"image_uris": {"png": second_image}, "printed_name": b}]}:
            return [
                CardFaceData(f, first_image, "/front/" in first_image),
                CardFaceData(b, second_image, "/front/" in second_image),
            ]
        case {"card_faces": [
                {"image_uris": {"png": first_image}, "name": f},
                {"image_uris": {"png": second_image}, "name": b}]}:
            return [
                CardFaceData(f, first_image, "/front/" in first_image),
                CardFaceData(b, second_image, "/front/" in second_image),
            ]
        # Single-sided cards have a top-level "image_uris" key.
        # Of those, Cards with multiple faces per side still have image_uris: Split cards, Adventure, Omen, etc…
        case {"card_faces": [{"printed_name": f}, {"printed_name": b}], "image_uris": {"png": first_image}}:
            return [CardFaceData(f"{f} // {b}", first_image, True)]
        case {"card_faces": _, "image_uris": {"png": first_image}}:
            return [CardFaceData(card_name, first_image, True)]
        # No "card_faces" means regular, single-sided card
        case {"image_uris": {"png": first_image}}:
            return [CardFaceData(card_name, first_image, True)]
        case _:
            raise RuntimeError(f"Unexpected structure in card {card}")


def _get_oracle_id(card: CardDataType) -> UUID:
    """
    Reads the oracle_id property of the given card.

    This assumes that both sides of a double-faced card have the same oracle_id, in the case that the parent
    card object does not contain the oracle_id.
    """
    try:
        return card["oracle_id"]
    except KeyError:
        first_face = card["card_faces"][0]
        return first_face["oracle_id"]


def _get_card_name(card_or_face: CardOrFace) -> str:
    """
    Reads the card name. Non-English cards have both "printed_name" and "name", so prefer "printed_name".
    English cards only have the “name” attribute, so use that as a fallback.
    """
    return card_or_face.get("printed_name") or card_or_face["name"]
