# Copyright (C) 2020, 2021 Thomas Hess <thomas.hess@udo.edu>

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

import datetime
import functools
import gzip
import json
import os
from pathlib import Path
import re
import sqlite3
import socket
import typing
import urllib.error
import urllib.request

import ijson
from PyQt5.QtCore import pyqtSignal, QObject, QThread

from mtg_proxy_printer.downloader_base import DownloaderBase
from mtg_proxy_printer.model.carddb import CardDatabase, cached_dedent
import mtg_proxy_printer.settings
import mtg_proxy_printer.metered_file
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

__all__ = [
    "CardInfoDownloader",
    "store_download_settings",
    "CardInfoDownloadWorker",
]

# Just check, if the string starts with a known protocol specifier. This should only distinguish url-like strings
# from file system paths.
looks_like_url_re = re.compile(r"^(http|ftp)s?://.*")

JSONType = typing.Dict[str, typing.Union[str, int, list, dict, float, bool]]
IntTuples = typing.List[typing.Tuple[int]]
BULK_DATA_API_END_POINT = "https://api.scryfall.com/bulk-data"

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


class CardInfoDownloader(QObject):
    """
    Handles fetching the bulk card data from Scryfall and populates/updates the local card database.
    Also supports importing cards via a locally stored bulk card data file, mostly useful for debugging and testing
    purposes.

    This is the public interface. The actual implementation resides in the CardInfoDownloadWorker class, which
    is run asynchronously in another thread.
    """
    download_progress = pyqtSignal(int)  # Emits the total number of processed data after processing each item
    download_begins = pyqtSignal(int)  # Emitted when the download starts. Data represents the expected total data
    download_finished = pyqtSignal()  # Emitted when the input data is exhausted and processing finished
    working_state_changed = pyqtSignal(bool)
    network_error_occurred = pyqtSignal(str)  # Emitted when downloading failed due to network issues.
    other_error_occurred = pyqtSignal(str)  # Emitted when database population failed due to non-network issues.

    request_import_from_file = pyqtSignal(Path)
    request_import_from_url = pyqtSignal()

    def __init__(self, model: mtg_proxy_printer.model.carddb.CardDatabase,
                 requested_item: str = "all_cards", parent: QObject = None):
        super(CardInfoDownloader, self).__init__(parent)
        logger.info(f"Creating {self.__class__.__name__} instance.")
        logger.info(f"Using ijson backend: {ijson.backend}")
        self.model = model
        self.download_worker = CardInfoDownloadWorker(model, requested_item)
        self.worker_thread = QThread()
        self.download_worker.moveToThread(self.worker_thread)
        self.request_import_from_file.connect(self.download_worker.download_card_data)
        self.request_import_from_url.connect(self.download_worker.download_card_data)
        self.download_worker.download_begins.connect(self.download_begins)
        self.download_worker.download_begins.connect(lambda: self.working_state_changed.emit(True))
        self.download_worker.download_progress.connect(self.download_progress)
        self.download_worker.download_finished.connect(self.download_finished)
        self.download_worker.download_finished.connect(lambda: self.working_state_changed.emit(False))
        self.download_worker.network_error_occurred.connect(self.network_error_occurred)
        self.download_worker.other_error_occurred.connect(self.other_error_occurred)
        self.worker_thread.start()
        logger.info(f"Created {self.__class__.__name__} instance.")

    def cancel_running_operations(self):
        if self.worker_thread.isRunning():
            logger.info("Cancelling currently running card download")
            self.download_worker.should_run = False

    def stop_worker_thread(self):
        self.worker_thread.quit()
        self.worker_thread.wait(100)
        logger.info(f"Background worker stopped. Result: {self.worker_thread.isRunning()=}")


class CardInfoDownloadWorker(DownloaderBase):
    """
    This class implements the actual data download and import
    """
    def __init__(self, model: mtg_proxy_printer.model.carddb.CardDatabase,
                 requested_item: str = "all_cards", parent: QObject = None):
        logger.info(f"Creating {self.__class__.__name__} instance.")
        super(CardInfoDownloadWorker, self).__init__(parent)
        self.model = model
        self.requested_item = requested_item
        self.should_run = True
        logger.info(f"Created {self.__class__.__name__} instance.")

    def download_card_data(self, url_or_path: typing.Union[Path, str] = None):
        try:
            url = url_or_path or self.get_scryfall_bulk_card_data_url(self.requested_item)
            data = self.read_json_card_data(url)
            self.populate_database(data)
        except urllib.error.URLError as e:
            logger.exception("Handling URLError during card data download.")
            self.network_error_occurred.emit(str(e.reason))
            self.model.db.rollback()
        except socket.timeout as e:
            logger.exception("Handling socket timeout error during card data download.")
            self.network_error_occurred.emit(f"Reading from socket failed: {e}")
            self.model.db.rollback()
        else:
            self.download_finished.emit()

    def get_scryfall_bulk_card_data_url(self, requested_item: str = "all_cards") -> str:
        """Returns the bulk data URL and item count"""
        logger.info("Obtaining the card data URL from the API bulk data end point")
        data, _ = self.read_from_url(BULK_DATA_API_END_POINT)
        with data:
            bulk_items = json.load(data)
            for item in bulk_items["data"]:
                if item["type"] == requested_item:
                    result = item["download_uri"]
                    logger.debug(f"Bulk data located at: {result}")
                    return result
            raise RuntimeError(
                "URL to the Scryfall bulk data export not found. "
                "Expected a download of type 'all_cards' offered by the Scryfall bulk data end point, "
                "but it wos not found. See here: https://scryfall.com/docs/api/bulk-data/all")

    def read_json_card_data_from_url(self, url: str = None, json_path: str = "item"):
        """
        Parses the bulk card data json from https://scryfall.com/docs/api/bulk-data into individual objects.
        This function takes a URL pointing to the card data json object in the Scryfall API.

        The all cards json document is quite large (> 1GiB in 2020-11) and requires about 4GiB RAM to parse in one go.
        So use an iterative parser to generate and yield individual card objects, without having to store the whole
        document in memory.
        """
        if url is None:
            logger.debug("Request bulk data URL from the Scryfall API.")
            url = self.get_scryfall_bulk_card_data_url(self.requested_item)
            logger.debug(f"Obtained url: {url}")
        else:
            logger.debug(f"Reading from given URL {url}")
        source, monitor = self.read_from_url(url)
        # Entering and exiting the context manager with the monitor emits the IO begin/end signals.
        with source, monitor:
            yield from self._read_json_card_data_from_open_file(source, json_path)

    def read_json_card_data(self, url_or_path: typing.Union[Path, str], json_path: str = "item"):
        """
        Parses the bulk card data json from https://scryfall.com/docs/api/bulk-data into individual objects.
        This function can take a file path to a locally stored json document. Mainly for testing purposes.
        Or a URL pointing to the card data json object in the Scryfall API.

        The all cards json document is quite large (> 1GiB in 2020-11) and requires about 4GiB RAM to parse in one go.
        So use this iterative parser to generate and yield individual card objects, without having to store the whole
        document in memory.
        """
        if isinstance(url_or_path, Path):
            file_size = url_or_path.stat().st_size
            raw_file = url_or_path.open("rb")
            with self._wrap_in_metered_file(raw_file, file_size) as file:
                if url_or_path.suffix.casefold() == ".gz":
                    file = gzip.open(file, "rb")
                yield from self._read_json_card_data_from_open_file(file, json_path)
        elif looks_like_url_re.match(url_or_path):
            yield from self.read_json_card_data_from_url(url_or_path, json_path)
        else:
            file_size = os.stat(url_or_path).st_size
            raw_file = open(url_or_path, "rb")
            with self._wrap_in_metered_file(raw_file, file_size) as file:
                yield from self._read_json_card_data_from_open_file(file, json_path)

    @staticmethod
    def _read_json_card_data_from_open_file(file, json_path: str) -> typing.Generator[JSONType, None, None]:
        # Using "item" as the object path returns elements from a top-level JSON array
        yield from ijson.items(file, json_path)

    def populate_database(self, card_data: typing.Generator[JSONType, None, None]):
        """
        Takes an iterable returned by card_info_importer.read_json_card_data()
        and populates the database with card data.
        """
        card_count = 0
        try:
            card_count = self._populate_database(card_data)
        except sqlite3.Error as e:
            logger.exception(f"Database error occurred: {e}")
            self.other_error_occurred.emit(str(e))
        except Exception as e:
            logger.exception(f"Error in parsing step")
            self.other_error_occurred.emit(f"Failed to parse data from Scryfall. Reported error: {e}")
        finally:
            _clear_lru_caches()
            logger.info(f"Finished import with {card_count} imported cards.")

    def _populate_database(self, card_data: typing.Generator[JSONType, None, None]) -> int:
        logger.info("About to populate the database with card data")
        self.model.begin_transaction()
        store_download_settings(self.model.db)
        ds = mtg_proxy_printer.settings.settings["downloads"]
        # Parse the boolean download settings only once per import to save multiple seconds during the import
        download_enabled: typing.Dict[str, bool] = {
            key: ds.getboolean(key)
            for key in ds.keys()
        }
        # The settings keys are formatted like “banned-in-FORMAT”, where FORMAT is a format name as listed on Scryfall,
        # like “standard” or “modern”. So the last element of the split("-") output gets the plain format name.
        skip_cards_banned_in_formats = frozenset(
            key.split("-")[-1]
            for key, enabled in download_enabled.items()
            if not enabled)
        skipped_cards = 0
        index = 0
        face_ids: IntTuples = []
        db: sqlite3.Connection = self.model.db
        for index, card in enumerate(card_data, start=1):
            if not self.should_run:
                logger.info(f"Aborting card import after {index} cards due to user request.")
                self.download_finished.emit()
                return index
            if card["object"] != "card":
                logger.warning(f"Non-card found in card data during import: {card}")
                continue
            if _should_skip_card(card, download_enabled, skip_cards_banned_in_formats):
                skipped_cards += 1
                db.execute(cached_dedent("""\
                    INSERT INTO RemovedPrintings (scryfall_id, oracle_id)
                      VALUES (?, ?)
                      ON CONFLICT (scryfall_id) DO UPDATE
                        SET oracle_id = excluded.oracle_id
                        WHERE oracle_id <> excluded.oracle_id
                    ;"""), (card["id"], _get_oracle_id(card)))
                continue
            try:
                face_ids = self._parse_single_printing(card, face_ids)
            except Exception as e:
                logger.exception(f"Error while parsing card at position {index}. {card=}")
                raise RuntimeError(f"Error while parsing card at position {index}: {e}")
            if not index % 10000:
                logger.debug(f"Imported {index} cards.")
        _clean_unused_data(self.model.db, face_ids)
        logger.info(f"Skipped {skipped_cards} cards during the import, that matched any enabled download filter")
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

    def _parse_single_printing(self, card: JSONType, face_ids: IntTuples):
        language_id = _insert_language(self.model, card["lang"])
        oracle_id = _get_oracle_id(card)
        card_id = _insert_card(self.model, oracle_id)
        set_id = _insert_set(self.model, card)
        printing_id = insert_printing(self.model, card, card_id, set_id)
        face_ids += _insert_card_faces(self.model, card, language_id, printing_id)
        return face_ids


def _clear_lru_caches():
    """
    Clears the lru_cache instances. If the user re-downloads data, the old, cached keys become invalid and break
    the import. This will lead to assignment of wrong data via invalid foreign key relations.
    To prevent these issues, clear the LRU caches. Also frees RAM by purging data that isn’t used any more.
    """
    _insert_language.cache_clear()
    _insert_set_data.cache_clear()
    _insert_card.cache_clear()
    _insert_face_name.cache_clear()
    _insert_printing.cache_clear()


def store_download_settings(db):
    """Store the current download settings in the database"""
    section = mtg_proxy_printer.settings.settings["downloads"]
    db.executemany(cached_dedent(
        '''\
        INSERT INTO UsedDownloadSettings (setting, "value") VALUES (?, ?)
            ON CONFLICT(setting) DO UPDATE
                SET value = excluded.value
                WHERE value <> excluded.value
        '''),
        ((setting, section.getboolean(setting)) for setting in section.keys())
    )


def _read_card_date(card: JSONType, known_newest_card_date: datetime.date) -> datetime.date:
    """
    If the card’s set release is older than the given date and is in the past, return the release date.

    Newer cards have their previewed date set. Return that, if it is newer than the given date,
    even if it is in the future.

    This will be used to determine if newer card data is available online.
    """
    release_date = datetime.date.fromisoformat(card.get("released_at", "1970-01-01"))
    if known_newest_card_date < release_date < datetime.date.today():
        return release_date
    return known_newest_card_date


def _clean_unused_data(db: sqlite3.Connection, new_face_ids: IntTuples):
    """Purges all excess data, like printings that are no longer in the import data."""
    db_face_ids = frozenset(db.execute("SELECT card_face_id FROM CardFace\n"))
    excess_face_ids = db_face_ids.difference(new_face_ids)
    logger.info(f"Removing {len(excess_face_ids)} no longer existing card faces")
    db.executemany('DELETE FROM CardFace WHERE card_face_id = ?\n', excess_face_ids)
    db.execute('DELETE FROM FaceName WHERE face_name_id NOT IN (SELECT CardFace.face_name_id FROM CardFace)\n')
    db.execute('DELETE FROM Printing WHERE printing_id NOT IN (SELECT CardFace.printing_id FROM CardFace)\n')
    db.execute('DELETE FROM "Set" WHERE set_id NOT IN (SELECT Printing.set_id FROM Printing)\n')
    db.execute('DELETE FROM Card WHERE card_id NOT IN (SELECT Printing.card_id FROM Printing)\n')
    db.execute(cached_dedent("""\
    DELETE FROM RemovedPrintings
      WHERE scryfall_id IN (
        SELECT Printing.scryfall_id
        FROM Printing
      )
    """))
    db.execute(cached_dedent("""\
    DELETE FROM PrintLanguage
        WHERE language_id NOT IN (
          SELECT FaceName.language_id
          FROM FaceName
        )
    """))


@functools.lru_cache(None)
def _insert_language(model: CardDatabase, language: str) -> int:
    """
    Inserts the given language into the database and returns the generated ID.
    If the language is already present, just return the ID.
    """
    parameters = language,
    if result := model.db.execute(
            'SELECT language_id FROM PrintLanguage WHERE "language" = ?\n',
            parameters).fetchone():
        language_id, = result
    else:
        language_id = model.db.execute(
            'INSERT INTO PrintLanguage("language") VALUES (?)\n',
            parameters).lastrowid
    return language_id


@functools.lru_cache(None)
def _insert_card(model: CardDatabase, oracle_id: str) -> int:
    parameters = oracle_id,
    if result := model.db.execute('SELECT card_id FROM Card WHERE oracle_id = ?\n', parameters).fetchone():
        card_id, = result
    else:
        card_id = model.db.execute('INSERT INTO Card (oracle_id) VALUES (?)\n', parameters).lastrowid
    return card_id


def _insert_set(model: CardDatabase, card: JSONType) -> int:
    # Can’t use lru_cache here, because each card object is unique. So extract a hashable parameter set
    # and delegate to a cacheable function.
    set_abbr, set_name, set_uri = card["set"], card["set_name"], card["scryfall_set_uri"]
    return _insert_set_data(model, set_abbr, set_name, set_uri)


@functools.lru_cache(None)
def _insert_set_data(model: CardDatabase, set_abbr: str, set_name: str, set_uri: str) -> int:
    model.db.execute(cached_dedent(
        '''\
        INSERT INTO "Set" ("set", set_name, set_uri)
            VALUES (?, ?, ?)
            ON CONFLICT ("set") DO
            UPDATE SET set_name = excluded.set_name, set_uri = excluded.set_uri
            WHERE set_name <> excluded.set_name OR set_uri <> excluded.set_uri
        '''),
        (set_abbr, set_name, set_uri)
    )
    set_id, = model.db.execute('SELECT set_id FROM "Set" WHERE "set" = ?\n', (set_abbr,)).fetchone()
    return set_id


@functools.lru_cache(None)
def _insert_face_name(model: CardDatabase, printed_name: str, language_id: int) -> int:
    """
    Insert the given, printed face name into the database, if it not already stored. Returns the integer
    PRIMARY KEY face_name_id, used to reference the inserted face name.
    """
    parameters = (printed_name, language_id)
    if result := model.db.execute(
            'SELECT face_name_id FROM FaceName WHERE card_name = ? AND language_id = ?\n', parameters).fetchone():
        face_name_id, = result
    else:
        face_name_id = model.db.execute(
            'INSERT INTO FaceName (card_name, language_id) VALUES (?, ?)\n', parameters).lastrowid
    return face_name_id


def insert_printing(model: CardDatabase, card: JSONType, card_id: int, set_id: int) -> int:
    data = PrintingData(
        card_id,
        set_id,
        card["collector_number"],
        card["id"],
        card["oversized"],
        card["highres_image"],
    )
    return _insert_printing(model, data)


@functools.lru_cache(None)
def _insert_printing(model: CardDatabase, data: PrintingData) -> int:
    model.db.execute(cached_dedent(
        '''\
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
        '''), data,
    )
    printing_id, = model.db.execute(cached_dedent(
        '''\
        SELECT printing_id
            FROM Printing
            WHERE scryfall_id = ?
        '''), (data.scryfall_id,)
    ).fetchone()
    return printing_id


def _insert_card_faces(model: CardDatabase, card: JSONType, language_id: int, printing_id: int) -> IntTuples:
    """Inserts all faces of the given card together with their names."""
    face_ids: IntTuples = []
    for face in _get_card_faces(card):
        face_name_id = _insert_face_name(model, face.printed_face_name, language_id)
        face_id: typing.Tuple[int] = model.db.execute(cached_dedent(
            '''\
            INSERT INTO CardFace(printing_id, face_name_id, is_front, png_image_uri, face_number)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (printing_id, face_name_id, is_front) DO UPDATE
                SET png_image_uri = excluded.png_image_uri,
                    face_number = excluded.face_number
                RETURNING card_face_id
            '''),
            (printing_id, face_name_id, face.is_front, face.image_uri, face.face_number),
        ).fetchone()
        if face_id is not None:
            face_ids.append(face_id)
    return face_ids


def _should_skip_card(
        card: JSONType, download_enabled: typing.Dict[str, bool],
        skip_cards_banned_in_formats: typing.FrozenSet[str]) -> bool:
    """Determine, if the given card should be included based on the application settings"""
    legalities: typing.Dict[str, str] = card["legalities"]
    banned_in_formats = frozenset(magic_format for magic_format, legality in legalities.items() if legality == "banned")

    return any((
        # Racism filter
        card.get("content_warning", False) and not download_enabled["download-cards-depicting-racism"],
        # Cards with placeholder images (low-res image with "not available in your language" overlay)
        card["image_status"] == "placeholder" and not download_enabled["download-cards-without-images"],
        # Cards without images. These have no "image_uris" item can’t be printed at all. Unconditionally skip these
        card["image_status"] == "missing",
        card["oversized"] and not download_enabled["download-oversized-cards"],
        # Border filter
        card["border_color"] == "white" and not download_enabled["download-white-bordered"],
        card["border_color"] == "gold" and not download_enabled["download-gold-bordered"],
        # “Funny” cards, not legal in any constructed format. This includes full-art Contraptions from Unstable and some
        # black-bordered promotional cards, in addition to silver-bordered cards.
        card["set_type"] == "funny" and not download_enabled["download-funny-cards"],
        # Token cards
        card["layout"] == "token" and not download_enabled["download-token"],
        card["digital"] is True and not download_enabled["download-digital-cards"],
        # Specific format legality.
        not banned_in_formats.isdisjoint(skip_cards_banned_in_formats),
    ))


def _get_card_faces(card: JSONType) -> typing.Generator[CardFaceData, None, None]:
    """
    Yields a CardFaceData object for each face found in the card object.
    The printed name falls back to the English name, if the card has no printed_name key.

    Yields a single face, if the card has no "card_faces" key with a faces array. In this case,
    this function builds a "card_face" object providing only the required information from the card object itself.
    """
    try:
        faces: typing.List[JSONType] = card["card_faces"]
    except KeyError:
        faces: typing.List[JSONType] = [
            {
                "printed_name": _get_card_name(card),
                "image_uris": card["image_uris"],
            }
        ]
    return (
        CardFaceData(
            _get_card_name(face),
            (image_uri := _get_png_image_uri(card, face)),
            _is_front_face(image_uri),
            face_number
        )
        for face_number, face in enumerate(faces)
    )


def _get_png_image_uri(card: JSONType, face: JSONType):
    """
    Get the PNG image URI of the given card face.

    Double-faced cards have multiple faces and an image in each face.
    Split cards have multiple faces, but the singular image is located in the card itself.
    """
    try:
        return face["image_uris"]["png"]
    except KeyError:
        return card["image_uris"]["png"]


def _get_oracle_id(card: JSONType) -> str:
    """
    Reads the oracle_id property of the given card.

    This assumes that both sides of a double-faced card have the same oracle_id, in the case that the parent
    card object does not contain the oracle_id.
    """
    try:
        return card["oracle_id"]
    except KeyError:
        return card["card_faces"][0]["oracle_id"]


def _is_front_face(image_uri: str) -> bool:
    """
    Determine if the PNG image URI is a front or back face. The API does not expose which side a face is, so get that
    detail using the directory structure in the URI. This is kind of a hack, though.

    :param image_uri: URI pointing to the image on the Scryfall servers
    :return: True, if the face is a front face, False otherwise
    """
    return "/front/" in image_uri


def _get_card_name(card_or_face: JSONType) -> str:
    # Reads the card name. Non-English cards have both "printed_name" and "name", so prefer "printed_name".
    # English cards only have the “name” attribute, so use that as a fallback.
    try:
        return card_or_face["printed_name"]
    except KeyError:
        return card_or_face["name"]
