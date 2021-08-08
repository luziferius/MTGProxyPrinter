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
import http.client

import ijson
from PyQt5.QtCore import pyqtSignal, QObject, QThread

from mtg_proxy_printer.model.carddb import CardDatabase
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
# Offer accepting gzip, as that is supported by the Scryfall server and reduces network data use by 80-90%
supported_encodings = ("gzip", "identity")
JSONType = typing.Dict[str, typing.Union[str, int, list, dict, float, bool]]
BULK_DATA_API_END_POINT = "https://api.scryfall.com/bulk-data"

# Set a default socket timeout to prevent hanging indefinitely, if the network connection breaks while a download
# is in progress
socket.setdefaulttimeout(5)


class CardInfoDownloader(QObject):
    download_progress = pyqtSignal(int)  # Emits the total number of processed data after processing each item
    download_begins = pyqtSignal(int)  # Emitted when the download starts. Data represents the expected total data
    download_finished = pyqtSignal()  # Emitted when the input data is exhausted and processing finished
    working_state_changed = pyqtSignal(bool)
    network_error_occurred = pyqtSignal(str)  # Emitted when downloading failed due to network issues.

    def __init__(self, model: mtg_proxy_printer.model.carddb.CardDatabase,
                 requested_item: str = "all_cards", parent: QObject = None):
        super(CardInfoDownloader, self).__init__(parent)
        logger.info(f"Creating {self.__class__.__name__} instance.")
        logger.info(f"Using ijson backend: {ijson.backend}")
        self.model = model
        self.download_worker = CardInfoDownloadWorker(model, requested_item)
        self.worker_thread = QThread()
        self.download_worker.moveToThread(self.worker_thread)
        self.download_worker.download_begins.connect(self.download_begins)
        self.download_worker.download_progress.connect(self.download_progress)
        self.download_worker.download_finished.connect(self.download_finished)
        self.download_worker.download_finished.connect(self.worker_thread.quit)
        self.download_worker.download_finished.connect(lambda: self.working_state_changed.emit(False))
        self.download_worker.network_error_occurred.connect(self.network_error_occurred)
        self.worker_thread.started.connect(self.download_worker.download_card_data)
        logger.info(f"Created {self.__class__.__name__} instance.")

    def populate_database(self):
        self.working_state_changed.emit(True)
        logger.info("Running the background worker")
        self.worker_thread.start()

    def cancel_running_operations(self):
        if self.worker_thread.isRunning():
            logger.info("Cancelling currently running card download")
            self.download_worker.should_run = False


class CardInfoDownloadWorker(QObject):

    download_progress = pyqtSignal(int)  # Emits the total number of processed data after processing each item
    download_begins = pyqtSignal(int)  # Emitted when the download starts. Data represents the expected total data
    download_finished = pyqtSignal()  # Emitted when the input data is exhausted and processing finished
    network_error_occurred = pyqtSignal(str)  # Emitted when downloading failed due to network issues.

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
            self.network_error_occurred.emit(str(e.reason))
            self.model.db.rollback()
        except socket.timeout as e:
            self.network_error_occurred.emit(f"Reading from socket failed: {e}")
            self.model.db.rollback()
        else:
            self.download_finished.emit()

    def _wrap_in_metered_file(self, raw_file, file_size):
        monitor = mtg_proxy_printer.metered_file.MeteredFile(raw_file, file_size, self)
        monitor.total_bytes_processed.connect(self.download_progress)
        monitor.io_begin.connect(self.download_begins)
        return monitor

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
        logger.info("About to populate the database with card data")
        self.model.begin_transaction()
        store_download_settings(self.model.db)
        ds = mtg_proxy_printer.settings.settings["downloads"]
        download_enabled: typing.Dict[str, bool] = {  # Parse the boolean download settings only once per import
            key: ds.getboolean(key)
            for key in ds.keys()
        }
        skip_cards_banned_in_formats = frozenset(
            key.split("-")[-1]
            for key, enabled in download_enabled.items()
            if not enabled)
        skipped_cards = 0
        index = 0
        newest_card_date = datetime.date.today()
        for index, card in enumerate(card_data, start=1):
            if card["object"] != "card":
                logger.warning(f"Non-card found in card data during import: {card}")
                continue
            newest_card_date = _read_card_preview_date(card, newest_card_date)
            if _should_skip_card(card, download_enabled, skip_cards_banned_in_formats):
                skipped_cards += 1
                _remove_card(self.model, card)
                continue
            if not self.should_run:
                logger.info(f"Aborting card import after {index} cards due to user request.")
                self.download_finished.emit()
                return
            language_id = _insert_language(self.model, card["lang"])  # Ok
            card_id = _insert_card(self.model, card["oracle_id"])  # Ok
            set_id = _insert_set(self.model, card)  # Ok
            _insert_card_faces(self.model, card, language_id, card_id, set_id)
            if not index % 10000:
                logger.debug(f"Imported {index} cards.")
                self.model.db.execute("PRAGMA optimize\n")
        # Populate the sqlite stat tables to give the query optimizer data to work with.
        # This greatly improves query speed.
        self.model.db.execute("ANALYZE\n")
        _clean_unused_data(self.model.db)
        logger.info(f"Skipped {skipped_cards} cards during the import, that matched any enabled download filter")
        # Store the timestamp of this import.
        self.model.db.execute(
            "INSERT INTO LastDatabaseUpdate (update_timestamp, newest_card_timestamp) VALUES (?, ?)\n",
            (datetime.datetime.now(), newest_card_date)
        )
        self.model.db.execute("ANALYZE\n")
        self.model.commit()
        # Clear the lru_cache instances. If the user re-downloads data, the old, cached keys become invalid and break
        # the import. This will lead to assignment of wrong data via invalid foreign key relations.
        _insert_language.cache_clear()
        _insert_set_data.cache_clear()
        _insert_card.cache_clear()
        _insert_face_name.cache_clear()
        logger.info(f"Finished import with {index} imported cards.")

    def read_from_url(self, url: str):
        """
        Reads a given URL and returns a file-like object that can and should be used as a context manager.
        """
        headers = {"Accept-Encoding": ", ".join(supported_encodings)}
        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request)  # type: http.client.HTTPResponse
        if (response_code := response.getcode()) >= 300:
            raise RuntimeError(f"Error from server! Error code: {response_code}")
        encoding = response.info().get("Content-Encoding")
        size_bytes = int(response.info().get("Content-Length", "0"))
        metered_reader = self._wrap_in_metered_file(response, size_bytes)
        if encoding == "gzip":
            data = gzip.open(metered_reader, "rb")
        elif encoding in ("identity", None):  # Implicit "identity" if the Content-Encoding header is missing.
            data = metered_reader
        else:
            raise RuntimeError(f"Server returned unsupported encoding: {encoding}")
        return data, metered_reader


def store_download_settings(db):
    """Store the current download settings in the database"""
    section = mtg_proxy_printer.settings.settings["downloads"]
    db.executemany(
        'INSERT INTO UsedDownloadSettings (setting, "value") VALUES (?, ?) '
        'ON CONFLICT(setting) DO UPDATE '
        'SET value = excluded.value '
        'WHERE value <> excluded.value\n',
        ((setting, section.getboolean(setting)) for setting in section.keys())
    )


def _read_card_preview_date(card: JSONType, known_newest_card_date: datetime.date) -> datetime.date:
    """
    Newer cards have their previewed date set. Return that, if it is newer than the given date.

    This will be used to determine if newer card data is available online.
    """
    try:
        if date_str := card["preview"]["previewed_at"]:
            card_date = datetime.date.fromisoformat(date_str)
            if card_date > known_newest_card_date:
                # Found card from a future set
                return card_date
    except KeyError:
        pass
    return known_newest_card_date


def _clean_unused_data(db: sqlite3.Connection):
    # Remove all OracleID entries in Card, for which no CardFace is present. These are cards for which all
    # printings got removed (maybe due to a format ban filter in place).
    db.execute("DELETE FROM Card WHERE card_id NOT IN (SELECT card_id FROM CardFace)\n")
    db.execute("DELETE FROM PrintLanguage WHERE language_id NOT IN (SELECT language_id FROM CardFace)\n")
    db.execute('DELETE FROM "Set" WHERE set_id NOT IN (SELECT set_id FROM CardFace)\n')
    db.execute("DELETE FROM FaceName WHERE face_name_id NOT IN (SELECT face_name_id FROM CardFace)\n")


def _remove_card(model: CardDatabase, card: JSONType):
    """
    Removes the given printing from the database, if it is currently stored in the database.
    Called on each skipped card, to ensure cards that start to fall under any download filter are removed from
    the database and do not remain stored locally.
    """
    lang = card["lang"]
    set_code = card["set"]
    oracle_id = card["oracle_id"]
    collector_number = card["collector_number"]
    try:
        faces = list(_get_card_faces(card))
    except KeyError:
        # Card has no image URIs, so skip it
        return
    for _, name, _, is_front in faces:
        parameters = (name, lang, set_code, oracle_id, is_front, collector_number)
        model.db.execute(
            'DELETE FROM CardFace '
            'WHERE (face_name_id, set_id, card_id, is_front, collector_number) IN '
            '( SELECT'
            '  (SELECT face_name_id FROM FaceName JOIN PrintLanguage USING (language_id)'
            '     WHERE card_name = ? AND language = ?) AS face_name_id,'
            '  (SELECT set_id FROM "Set" where "set" = ?) AS set_id,'
            '  (SELECT card_id FROM Card where oracle_id = ?) AS card_id,'
            '  ? AS is_front,'
            '  ? AS collector_number)\n',
            parameters
        )


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
    set_abbr, set_name, set_uri = card["set"], card["set_name"], card["scryfall_set_uri"]
    return _insert_set_data(model, set_abbr, set_name, set_uri)


@functools.lru_cache(None)
def _insert_set_data(model: CardDatabase, set_abbr: str, set_name: str, set_uri: str) -> int:
    model.db.execute(
        'INSERT INTO "Set" ("set", set_name, set_uri) VALUES (?, ?, ?) '
        'ON CONFLICT ("set") DO '
        'UPDATE SET set_name = excluded.set_name, set_uri = excluded.set_uri '
        'WHERE set_name <> excluded.set_name OR set_uri <> excluded.set_uri\n',
        (set_abbr, set_name, set_uri)
    )
    set_id, = model.db.execute('SELECT set_id FROM "Set" WHERE "set" = ?\n', (set_abbr,)).fetchone()
    return set_id


@functools.lru_cache(None)
def _insert_face_name(model: CardDatabase, printed_name: str, language_id: int) -> int:
    parameters = (printed_name, language_id)
    if result := model.db.execute(
            'SELECT face_name_id FROM FaceName WHERE card_name = ? AND language_id = ?\n', parameters).fetchone():
        face_name_id, = result
    else:
        face_name_id = model.db.execute(
            'INSERT INTO FaceName (card_name, language_id) VALUES (?, ?)\n', parameters).lastrowid
    return face_name_id


def _insert_card_faces(model: CardDatabase, card: JSONType, language_id: int, card_id: int, set_id: int):
    collector_number = card["collector_number"]
    highres_image = card["highres_image"]
    for scryfall_id, printed_name, png_image_uri, is_front in _get_card_faces(card):
        face_name_id = _insert_face_name(model, printed_name, language_id)
        model.db.execute(
            "INSERT INTO CardFace (\n"
            "card_id, set_id, face_name_id, collector_number, scryfall_id, highres_image, png_image_uri, is_front) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?) \n"
            "  ON CONFLICT (face_name_id, set_id, card_id, is_front, collector_number) DO UPDATE "
            "SET scryfall_id = excluded.scryfall_id, highres_image = excluded.highres_image, "
            "png_image_uri = excluded.png_image_uri\n"
            "  WHERE scryfall_id <> excluded.scryfall_id OR highres_image <> excluded.highres_image "
            "OR png_image_uri <> excluded.png_image_uri\n",
            (card_id, set_id, face_name_id, collector_number, scryfall_id, highres_image, png_image_uri, is_front)
        )


def _should_skip_card(
        card: JSONType, download_enabled: typing.Dict[str, bool],
        skip_cards_banned_in_formats: typing.FrozenSet[str]) -> bool:
    """Determine, if the given card should be included based on the application settings"""
    legalities = card["legalities"]
    banned_in_formats = frozenset(format_ for format_, status in legalities.items() if status == "banned")

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
        # Specific format legality.
        banned_in_formats.intersection(skip_cards_banned_in_formats),
    ))


def _get_card_faces(card: JSONType) -> typing.Generator[typing.Tuple[str, str, str, bool], None, None]:
    """
    Yields a tuple (Scryfall_id, printed_name, PNG_image_URI, is_front) for each face found in the card object.
    The printed name falls back to the English name, if the card has no printed_name key.

    Yields a single face, if the card has no "card_faces" key with a faces array. In this case,
    this function builds a "card_face" object providing only the required information from the card object itself.
    """
    try:
        faces = card["card_faces"]
    except KeyError:
        faces = [
            {
                "printed_name": _get_card_name(card),
                "image_uris": card["image_uris"],
            }
        ]
    for face in faces:  # type: JSONType
        yield card["id"], _get_card_name(face), (image_uri := _get_png_image_uri(card, face)), _is_front_face(image_uri)


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
    # English cards only have name, so use that as a fallback.
    try:
        return card_or_face["printed_name"]
    except KeyError:
        return card_or_face["name"]
