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

import abc
from collections.abc import Generator
import enum
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
from typing import Literal

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
from mtg_proxy_printer.units_and_sizes import CardDataType, FaceDataType, BulkDataType, UUID
from mtg_proxy_printer.sqlite_helpers import open_database
from mtg_proxy_printer.async_tasks.base import AsyncTask

logger = get_logger(__name__)
del get_logger

__all__ = [
    "CardInfoDownloadTaskBase",
    "DatabaseImportTask",
    "ApiStreamTask",
    "SetWackinessScore",
    "FileDownloadTask",
]

# Just check, if the string starts with a known protocol specifier. This should only distinguish url-like strings
# from file system paths.
looks_like_url_re = re.compile(r"^(http|ftp)s?://.*")
BULK_DATA_API_END_POINT = "https://api.scryfall.com/bulk-data/all-cards"

# Constants determined empirically. These fluctuate a bit over time, but give reasonable estimates.
AVERAGE_SIZE_PER_UNCOMPRESSED_JSON_ENTRY_IN_BYTES = 4706
GZIP_COMPRESSION_FACTOR = 7.09

# Set a default socket timeout to prevent hanging indefinitely, if the network connection breaks while a download
# is in progress
socket.setdefaulttimeout(5)
QueuedConnection = Qt.ConnectionType.QueuedConnection

IntTuples = list[tuple[int]]
CardStream = Generator[CardDataType, None, None]
CardOrFace = CardDataType | FaceDataType
CardDataQueue = queue.Queue[tuple[CardDataType, ...] | None]


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
    """
    Used to order multiple printing choices, when automatically determining a printing choice.
    Lower values have higher priority, so that the choice is steered towards normal cards.
    """
    REGULAR = 0
    PROMOTIONAL = 1  # Pre-release or planeswalker stamp. Extended/full art versions
    WHITE_BORDERED = 2  # Old core sets. Some folks dislike the white border
    FUNNY = 3  # Non-tournament legal
    GOLD_BORDERED = 4  # Tournament-memorabilia printed with golden border and signed by players
    DIGITAL = 5  # MTG Arena/Online cards. Especially Arena cards aren't pleasantly looking when printed
    ART_SERIES = 8  # Not playable
    OVERSIZED = 10  # Not playable


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

    def _enqueue_stream(self, data: CardStream):
        """Put the CardStream into the queue for downstream consumption"""
        try:
            for batch in itertools.batched(data, self._batch_size):  # type: tuple[CardDataType, ...]
                self.queue.put(batch)
        except AttributeError:  # Cancelling closes and deletes the underlying file, causing an AttributeError in run()
            logger.info(f"{self.__class__.__name__}: Read operation cancelled")
        except Exception as e:
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
        if self.open_file is not None:
            self.open_file.close()
            self.open_file = None


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
            yield from ijson.items(file, json_path, use_float=True)

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
        Parses the bulk card data json from https://scryfall.com/docs/api/bulk-data into individual objects.
        This function takes a URL pointing to the card data json array in the Scryfall API.

        The all cards json document is quite large (> 2.1GiB in 2024-10) and requires about 8GiB RAM to parse in one go.
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
            yield from ijson.items(self.open_file, json_path, use_float=True)

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
        self._db = db
        self.should_run = True
        self.set_code_cache: dict[str, int] = {}
        logger.info(f"Created {self.__class__.__name__} instance.")

    @property
    def can_cancel(self) -> bool:
        return True

    @Slot()
    def cancel(self):
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
    def _consume_from_queue(queue: CardDataQueue) -> CardStream:
        while (batch := queue.get()) is not None:
            yield from batch

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
        face_ids: IntTuples = []
        related_printings: list[RelatedPrintingData] = []
        for index, card in enumerate(card_data, start=1):
            if not self.should_run:
                logger.info(f"Aborting card import after {index} cards due to user request or data erro.")
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
                face_ids += self._parse_single_printing(card)
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
            4 + PrintingFilterUpdater.PROGRESS_STEP_COUNT,
            self.tr("Post-processing card data:", "Progress bar label text"))
        self._insert_related_printings(related_printings)
        self.advance_progress.emit()
        self._clean_unused_data(face_ids)
        self.advance_progress.emit()
        updater = PrintingFilterUpdater(
            CardDatabase(self.carddb_path, check_same_thread=True, register_exit_hooks=False),
            self.db, force_update_hidden_column=True)
        updater.advance_progress.connect(self.advance_progress)
        updater.store_current_printing_filters()  # Don't call run() to not deadlock via the db semaphore
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
    def _read_printing_filters_from_db(self) -> dict[str, int]:
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

    def _insert_related_printings(self, related_printings: list[RelatedPrintingData]):
        db = self.db
        logger.debug(f"Inserting related printings data. {len(related_printings)} entries")
        db.execute("DELETE FROM RelatedPrintings")
        # Implementation note on "OR IGNORE below":
        # On all cards with related printings, the related cards array also includes the identity/self reference.
        # For the relation, Scryfall uses the print-identifying scryfall id.
        # But on some cards, the self-reference is given by another printing.
        # So for example, the etched foil printing refers to itself in the related cards list by the regular printing.
        # And because the related card object only contains the scryfall id as the identification, the parser step
        # cannot identify these cases.
        # If it happens, the entry should be ignored during the insert.
        db.executemany(cached_dedent("""\
        INSERT OR IGNORE INTO RelatedPrintings (card_id, related_id)
          SELECT card_id, related_id
          FROM (SELECT card_id FROM Printing WHERE scryfall_id = ?),
               (SELECT card_id AS related_id FROM Printing WHERE scryfall_id = ?)
        """), related_printings)

    @functools.cache
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

    @functools.cache
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

    @functools.cache
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

    def _is_printing_present(self, new_data: PrintingData) -> tuple[int | None, bool]:
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
            card_face_id: tuple[int] | None = db.execute(
                "SELECT card_face_id FROM CardFace WHERE face_name_id = ? AND printing_id = ? AND is_front = ?\n",
                (face_name_id, printing_id, face.is_front)).fetchone()
            if card_face_id is None:
                card_face_id = db.execute(
                    cached_dedent("""\
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

    def _update_card_filters(self, printing_id: int, filter_data: dict[str, bool]):
        printing_filter_ids = self._read_printing_filters_from_db()
        db = self.db
        active_printing_filters = set(
            (printing_id, printing_filter_ids[filter_name])
            for filter_name, filter_applies in filter_data.items() if filter_applies
        )
        stored_printing_filters: set[tuple[int, int]] = set(db.execute(
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
    if card["layout"].endswith("token"):
        # Tokens are never sources, as that would pull all cards creating that token
        return
    card_id = UUID(card["id"])
    is_dungeon = card.get("type_line") == "Dungeon"
    for related_card in card.get("all_parts", []):
        related_id = UUID(related_card["id"])
        related_is_token = related_card["component"].endswith("token")
        # No self reference allowed. And the implication is_dungeon ⇒ related_is_token must be True.
        # I.e. If the source is a Dungeon, then it may link with tokens only, and nothing else.
        if card_id != related_id and (not is_dungeon or related_is_token):
            yield RelatedPrintingData(card_id, related_id)


def _get_card_filter_data(card: CardDataType) -> dict[str, bool]:
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
        "hide-token": card["layout"].endswith("token") or card.get("type_line") == "Dungeon",
        "hide-digital-cards": card["digital"],
        "hide-art-series-cards": card["layout"] == "art_series",
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
            # Has faces, but no image_uris, therefore is a DFC
            "card_faces" in card and "image_uris" not in card
            # And at least one face has no images
            and any("image_uris" not in face for face in card["card_faces"])
    )


def _get_card_faces(card: CardDataType) -> Generator[CardFaceData, None, None]:
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
