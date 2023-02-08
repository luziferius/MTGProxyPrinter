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

import enum
import functools
import gzip
import shutil
from pathlib import Path
import re
import sqlite3
import socket
import typing
import urllib.error
import urllib.parse
import urllib.request

import ijson
from PyQt5.QtCore import pyqtSignal as Signal, QObject, QThread

from mtg_proxy_printer.downloader_base import DownloaderBase
from mtg_proxy_printer.model.carddb import CardDatabase, cached_dedent
import mtg_proxy_printer.metered_file
from mtg_proxy_printer.stop_thread import stop_thread
from mtg_proxy_printer.logger import get_logger
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

JSONType = typing.Dict[str, typing.Union[str, int, list, dict, float, bool]]
CardStream = typing.Generator[JSONType, None, None]
IntTuples = typing.List[typing.Tuple[int]]
BULK_DATA_API_END_POINT = "https://api.scryfall.com/bulk-data/all-cards"

# Set a default socket timeout to prevent hanging indefinitely, if the network connection breaks while a download
# is in progress
socket.setdefaulttimeout(5)


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
    scryfall_id: str
    is_oversized: bool
    highres_image: bool


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


class CardInfoDownloader(QObject):
    """
    Handles fetching the bulk card data from Scryfall and populates/updates the local card database.
    Also supports importing cards via a locally stored bulk card data file, mostly useful for debugging and testing
    purposes.

    This is the public interface. The actual implementation resides in the CardInfoDownloadWorker class, which
    is run asynchronously in another thread.
    """
    download_progress = Signal(int)  # Emits the total number of processed data after processing each item
    download_begins = Signal(int, str)  # Emitted when the download starts. Data represents the expected total data
    download_finished = Signal()  # Emitted when the input data is exhausted and processing finished
    working_state_changed = Signal(bool)
    network_error_occurred = Signal(str)  # Emitted when downloading failed due to network issues.
    other_error_occurred = Signal(str)  # Emitted when database population failed due to non-network issues.

    request_import_from_file = Signal(Path)
    request_import_from_url = Signal()
    request_download_to_file = Signal(Path)

    def __init__(self, model: mtg_proxy_printer.model.carddb.CardDatabase, parent: QObject = None):
        super(CardInfoDownloader, self).__init__(parent)
        logger.info(f"Creating {self.__class__.__name__} instance.")
        logger.info(f"Using ijson backend: {ijson.backend}")
        self.model = model
        self.database_import_worker = CardInfoDatabaseImportWorker(model)  # No parent assignment
        self.worker_thread = QThread()
        self.worker_thread.setObjectName(f"{self.__class__.__name__} background worker")
        self.worker_thread.finished.connect(lambda: logger.debug(f"{self.worker_thread.objectName()} stopped."))
        self.database_import_worker.moveToThread(self.worker_thread)
        self.file_download_worker = self._create_file_download_worker(self.worker_thread)
        self.request_import_from_file.connect(self.database_import_worker.import_card_data_from_local_file)
        self.request_import_from_url.connect(self.database_import_worker.import_card_data_from_online_api)
        self.database_import_worker.download_begins.connect(self.download_begins)
        self.database_import_worker.download_begins.connect(lambda: self.working_state_changed.emit(True))
        self.database_import_worker.download_progress.connect(self.download_progress)
        self.database_import_worker.download_finished.connect(self.download_finished)
        self.database_import_worker.download_finished.connect(lambda: self.working_state_changed.emit(False))
        self.database_import_worker.network_error_occurred.connect(self.network_error_occurred)
        self.database_import_worker.other_error_occurred.connect(self.other_error_occurred)
        self.worker_thread.start()
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _create_file_download_worker(self, thread: QThread) -> "CardInfoFileDownloadWorker":
        # No Qt parent assignment, because cross-thread parent relationships are unsupported
        worker = CardInfoFileDownloadWorker()
        worker.moveToThread(thread)  # Move to thread before connecting signals to create queued connections
        worker.download_begins.connect(self.download_begins)
        worker.download_progress.connect(self.download_progress)
        worker.download_finished.connect(self.download_finished)
        worker.network_error_occurred.connect(self.network_error_occurred)
        worker.other_error_occurred.connect(self.other_error_occurred)
        self.request_download_to_file.connect(worker.store_raw_card_data_in_file)
        return worker

    def cancel_running_operations(self):
        if self.worker_thread.isRunning():
            logger.info("Cancelling currently running card download")
            self.database_import_worker.should_run = False

    def quit_background_thread(self):
        if self.worker_thread.isRunning():
            logger.info(f"Quitting {self.__class__.__name__} background worker thread")
            stop_thread(self.worker_thread, logger)


class CardInfoWorkerBase(DownloaderBase):

    def get_scryfall_bulk_card_data_url(self) -> str:
        """Returns the bulk data URL and item count"""
        logger.info("Obtaining the card data URL from the API bulk data end point")
        data, _ = self.read_from_url(BULK_DATA_API_END_POINT)
        with data:
            item = next(ijson.items(data, "", use_float=True))
        result = item["download_uri"]
        logger.debug(f"Bulk data located at: {result}")
        return result


class CardInfoFileDownloadWorker(CardInfoWorkerBase):
    """
    This class implements downloading the raw card data to a file stored in the file system
    """

    def store_raw_card_data_in_file(self, download_path: Path):
        """
        Allows the user to store the raw JSON card data at the given path.
        Accessible by a button in the Debug tab in the Settings window.
        """
        logger.info(f"Store raw card data as a compressed JSON at path {download_path}")
        logger.debug("Request bulk data URL from the Scryfall API.")
        url = self.get_scryfall_bulk_card_data_url()
        file_name = urllib.parse.urlparse(url).path.split("/")[-1]
        logger.debug(f"Obtained url: '{url}'")
        monitor = self._open_url(url, "Downloading card data:")
        monitor.io_finished.connect(self.download_finished)  # Unlocks UI when finished
        if monitor.content_encoding() == "gzip":
            file_name += ".gz"
        download_file_path = download_path/file_name
        logger.debug(f"Opened URL '{url}' and target file at '{download_file_path}', about to download contents.")
        with download_file_path.open("wb") as download_file, monitor:
            shutil.copyfileobj(monitor, download_file)
        logger.info("Download completed")


class CardInfoDatabaseImportWorker(CardInfoWorkerBase):
    """
    This class implements the actual data download and import
    """
    def __init__(self, model: mtg_proxy_printer.model.carddb.CardDatabase, parent: QObject = None):
        logger.info(f"Creating {self.__class__.__name__} instance.")
        super().__init__(parent)
        self.model = model
        self.should_run = True
        self.set_code_cache: typing.Dict[str, int] = {}
        logger.info(f"Created {self.__class__.__name__} instance.")

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
            # TODO: Perform better notification in any error case
            total_cards_available = 0
        logger.debug(f"Total cards currently available: {total_cards_available}")
        return total_cards_available

    def import_card_data_from_local_file(self, path: Path):
        try:
            data = self.read_json_card_data_from_file(path)
            self.populate_database(data)
        except Exception:
            self.model.db.rollback()
            logger.exception(f"Error during import from file: {path}")
            self.other_error_occurred.emit(f"Error during import from file:\n{path}")
        finally:
            self.download_finished.emit()

    def import_card_data_from_online_api(self):
        logger.info("About to import card data from Scryfall")
        try:
            url = self.get_scryfall_bulk_card_data_url()
            data = self.read_json_card_data_from_url(url)
            estimated_total_card_count = self.get_available_card_count()
            self.download_begins.emit(estimated_total_card_count, "Updating card data from Scryfall:")
            self.populate_database(data, total_count=estimated_total_card_count)
        except urllib.error.URLError as e:
            logger.exception("Handling URLError during card data download.")
            self.network_error_occurred.emit(str(e.reason))
            self.model.db.rollback()
        except socket.timeout as e:
            logger.exception("Handling socket timeout error during card data download.")
            self.network_error_occurred.emit(f"Reading from socket failed: {e}")
            self.model.db.rollback()
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
            url = self.get_scryfall_bulk_card_data_url()
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
            logger.exception(f"Database error occurred: {e}")
            self.other_error_occurred.emit(str(e))
        except Exception as e:
            logger.exception(f"Error in parsing step")
            self.other_error_occurred.emit(f"Failed to parse data from Scryfall. Reported error: {e}")
        finally:
            self._clear_lru_caches()
            logger.info(f"Finished import with {card_count} imported cards.")

    def _populate_database(self, card_data: CardStream, *, total_count: int) -> int:
        logger.info(f"About to populate the database with card data. Expected cards: {total_count or 'unknown'}")
        self.model.begin_transaction()
        progress_report_step = total_count // 100
        # Look up the printing filter ids only once per import
        printing_filter_ids = self._read_printing_filters_from_db()
        skipped_cards = 0
        index = 0
        face_ids: IntTuples = []
        db: sqlite3.Connection = self.model.db
        # PrintingDisplayFilter will be re-populated while iterating over the card data.
        # Axing the previous data is far cheaper than trying
        # to update it in-place by removing up to number-of-available-filters entries per each individual card,
        # just to make sure that rare un-banned cards are updated properly.
        db.execute("DELETE FROM PrintingDisplayFilter\n")
        for index, card in enumerate(card_data, start=1):
            if not self.should_run:
                logger.info(f"Aborting card import after {index} cards due to user request.")
                self.download_finished.emit()
                return index
            if card["object"] != "card":
                logger.warning(f"Non-card found in card data during import: {card}")
                continue
            if self._should_skip_card(card):
                skipped_cards += 1
                db.execute(cached_dedent("""\
                    INSERT INTO RemovedPrintings (scryfall_id, language, oracle_id)
                      VALUES (?, ?, ?)
                      ON CONFLICT (scryfall_id) DO UPDATE
                        SET oracle_id = excluded.oracle_id,
                            language = excluded.language
                        WHERE oracle_id <> excluded.oracle_id
                           OR language <> excluded.language
                    ;"""), (card["id"], card["lang"], self._get_oracle_id(card)))
                continue
            try:
                face_ids += self._parse_single_printing(card, printing_filter_ids)
            except Exception as e:
                logger.exception(f"Error while parsing card at position {index}. {card=}")
                raise RuntimeError(f"Error while parsing card at position {index}: {e}")
            if not index % 10000:
                logger.debug(f"Imported {index} cards.")
            if progress_report_step and not index % progress_report_step:
                self.download_progress.emit(index)

        self._clean_unused_data(face_ids)
        logger.info(f"Skipped {skipped_cards} cards during the import")
        self.download_begins.emit(5, "Processing card filters")
        self.model.store_current_printing_filters(
            False, force_update_hidden_column=True, progress_signal=self.download_progress.emit)
        # Store the timestamp of this import.
        db.execute(cached_dedent(
            """\
            INSERT INTO LastDatabaseUpdate (reported_card_count)
                VALUES (?)
            """),
            (index,)
        )
        # Populate the sqlite stat tables to give the query optimizer data to work with.
        db.execute("ANALYZE\n")
        db.commit()
        return index

    def _read_printing_filters_from_db(self) -> typing.Dict[str, int]:
        return {
            filter_name: filter_id
            for filter_name, filter_id
            in self.model.db.execute("SELECT filter_name, filter_id FROM DisplayFilters").fetchall()
        }

    def _parse_single_printing(self, card: JSONType, printing_filter_ids):
        language_id = self._insert_language(card["lang"])
        oracle_id = self._get_oracle_id(card)
        card_id = self._insert_card(oracle_id)
        set_id = self.set_code_cache.get(card["set"])
        if not set_id:
            self.set_code_cache[card["set"]] = set_id = self._insert_set(card)
        printing_id = self._insert_printing(card, card_id, set_id)
        filter_data = self._get_card_filter_data(card)
        self._insert_card_filters(printing_id, filter_data, printing_filter_ids)
        new_face_ids = self._insert_card_faces(card, language_id, printing_id)
        return new_face_ids

    def _clear_lru_caches(self):
        """
        Clears the lru_cache instances. If the user re-downloads data, the old, cached keys become invalid and break
        the import. This will lead to assignment of wrong data via invalid foreign key relations.
        To prevent these issues, clear the LRU caches. Also frees RAM by purging data that isn’t used anymore.
        """
        for cache in (self._insert_language, self._insert_card):
            logger.debug(str(cache.cache_info()))
            cache.cache_clear()
        self.set_code_cache.clear()

    def _clean_unused_data(self, new_face_ids: IntTuples):
        """Purges all excess data, like printings that are no longer in the import data."""
        db = self.model.db
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

    @functools.lru_cache(None)
    def _insert_language(self, language: str) -> int:
        """
        Inserts the given language into the database and returns the generated ID.
        If the language is already present, just return the ID.
        """
        db = self.model.db
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
    def _insert_card(self, oracle_id: str) -> int:
        db = self.model.db
        parameters = oracle_id,
        if result := db.execute("SELECT card_id FROM Card WHERE oracle_id = ?\n", parameters).fetchone():
            card_id, = result
        else:
            card_id = db.execute("INSERT INTO Card (oracle_id) VALUES (?)\n", parameters).lastrowid
        return card_id

    def _insert_set(self, card: JSONType) -> int:
        db = self.model.db
        set_abbr = card["set"]
        wackiness_score = self._get_set_wackiness_score(card)
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

    def _insert_face_name(self, printed_name: str, language_id: int) -> int:
        """
        Insert the given, printed face name into the database, if it not already stored. Returns the integer
        PRIMARY KEY face_name_id, used to reference the inserted face name.
        """
        db = self.model.db
        parameters = (printed_name, language_id)
        if result := db.execute(
                "SELECT face_name_id FROM FaceName WHERE card_name = ? AND language_id = ?\n", parameters).fetchone():
            face_name_id, = result
        else:
            face_name_id = db.execute(
                "INSERT INTO FaceName (card_name, language_id) VALUES (?, ?)\n", parameters).lastrowid
        return face_name_id

    def _insert_printing(self, card: JSONType, card_id: int, set_id: int) -> int:
        db = self.model.db
        data = PrintingData(
            card_id,
            set_id,
            card["collector_number"],
            card["id"],
            card["oversized"],
            card["highres_image"],
        )
        db.execute(cached_dedent(
            """\
            INSERT INTO Printing (card_id, set_id, collector_number, scryfall_id, is_oversized, highres_image)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT (scryfall_id) DO UPDATE
                    SET card_id = excluded.card_id,
                        set_id = excluded.set_id,
                        collector_number = excluded.collector_number,
                        is_oversized = excluded.is_oversized,
                        highres_image = excluded.highres_image
                WHERE card_id <> excluded.card_id
                   OR set_id <> excluded.set_id
                   OR collector_number <> excluded.collector_number
                   OR is_oversized <> excluded.is_oversized
                   OR highres_image <> excluded.highres_image
            """), data,
        )
        printing_id, = db.execute(cached_dedent(
            """\
            SELECT printing_id
                FROM Printing
                WHERE scryfall_id = ?
            """), (data.scryfall_id,)
        ).fetchone()
        return printing_id

    def _insert_card_faces(self, card: JSONType, language_id: int, printing_id: int) -> IntTuples:
        """Inserts all faces of the given card together with their names."""
        db = self.model.db
        face_ids: IntTuples = []
        for face in self._get_card_faces(card):
            face_name_id = self._insert_face_name(face.printed_face_name, language_id)
            face_id: typing.Tuple[int] = db.execute(cached_dedent(
                """\
                INSERT INTO CardFace(printing_id, face_name_id, is_front, png_image_uri, face_number)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT (printing_id, face_name_id, is_front) DO UPDATE
                    SET png_image_uri = excluded.png_image_uri,
                        face_number = excluded.face_number
                    RETURNING card_face_id
                """),
                (printing_id, face_name_id, face.is_front, face.image_uri, face.face_number),
            ).fetchone()
            if face_id is not None:
                face_ids.append(face_id)
        return face_ids

    @staticmethod
    def _get_card_filter_data(card: JSONType) -> typing.Dict[str, bool]:
        legalities: typing.Dict[str, str] = card["legalities"]
        return {
            # Racism filter
            "hide-cards-depicting-racism": card.get("content_warning", False),
            # Cards with placeholder images (low-res image with "not available in your language" overlay)
            "hide-cards-without-images": card["image_status"] == "placeholder",
            "hide-oversized-cards": card["oversized"],
            # Border filter
            "hide-white-bordered": card["border_color"] == "white",
            "hide-gold-bordered": card["border_color"] == "gold",
            # “Funny” cards, not legal in any constructed format. This includes full-art Contraptions from Unstable and some
            # black-bordered promotional cards, in addition to silver-bordered cards.
            "hide-funny-cards": card["set_type"] == "funny",
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
            "hide-banned-in-pauper": legalities.get("pauper", "") == "banned",
            "hide-banned-in-penny": legalities.get("penny", "") == "banned",
            "hide-banned-in-pioneer": legalities.get("pioneer", "") == "banned",
            "hide-banned-in-standard": legalities.get("standard", "") == "banned",
            "hide-banned-in-vintage": legalities.get("vintage", "") == "banned",
        }

    @staticmethod
    def _get_set_wackiness_score(card: JSONType) -> SetWackinessScore:
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

    def _insert_card_filters(
            self, printing_id: int, filter_data: typing.Dict[str, bool],
            printing_filter_ids: typing.Dict[str, int]):
        self.model.db.executemany(
            "INSERT INTO PrintingDisplayFilter (printing_id, filter_id) VALUES (?, ?)\n",
            ((printing_id, printing_filter_ids[filter_name])
             for filter_name, filter_applies in filter_data.items() if filter_applies)
        )

    @staticmethod
    def _should_skip_card(card: JSONType) -> bool:
        # Cards without images. These have no "image_uris" item can’t be printed at all. Unconditionally skip these
        # Also skip double faced cards that have at least one face without images
        return card["image_status"] == "missing" or (
                "card_faces" in card
                and "image_uris" not in card
                and any("image_uris" not in face for face in card["card_faces"])
        )

    def _get_card_faces(self, card: JSONType) -> typing.Generator[CardFaceData, None, None]:
        """
        Yields a CardFaceData object for each face found in the card object.
        The printed name falls back to the English name, if the card has no printed_name key.

        Yields a single face, if the card has no "card_faces" key with a faces array. In this case,
        this function builds a "card_face" object providing only the required information from the card object itself.
        """
        faces: typing.List[JSONType] = card.get("card_faces") or [
            {
                "printed_name": self._get_card_name(card),
                "image_uris": card["image_uris"],
            }
        ]
        return (
            CardFaceData(
                self._get_card_name(face),
                image_uri := (face.get("image_uris") or card["image_uris"])["png"],
                # (image_uri := self._get_png_image_uri(card, face)),
                # The API does not expose which side a face is, so get that
                # detail using the directory structure in the URI. This is kind of a hack, though.
                "/front/" in image_uri,
                face_number
            )
            for face_number, face in enumerate(faces)
        )

    @staticmethod
    def _get_oracle_id(card: JSONType) -> str:
        """
        Reads the oracle_id property of the given card.

        This assumes that both sides of a double-faced card have the same oracle_id, in the case that the parent
        card object does not contain the oracle_id.
        """
        try:
            return card["oracle_id"]
        except KeyError:
            first_face: JSONType = card["card_faces"][0]
            return first_face["oracle_id"]

    @staticmethod
    def _get_card_name(card_or_face: JSONType) -> str:
        """
        Reads the card name. Non-English cards have both "printed_name" and "name", so prefer "printed_name".
        English cards only have the “name” attribute, so use that as a fallback.
        """
        return card_or_face.get("printed_name") or card_or_face["name"]

