# Copyright (C) 2020 Thomas Hess <thomas.hess@udo.edu>

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

import functools
import gzip
import json
from pathlib import Path
import re
import typing
import urllib.request
import http.client

import ijson
from PyQt5.QtCore import pyqtSignal, QObject

from mtg_proxy_printer.model.carddb import CardDatabase
import mtg_proxy_printer.settings
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

# Just check, if the string starts with a known protocol specifier. This should only distinguish url-like strings
# from file system paths.
looks_like_url_re = re.compile(r"^(http|ftp)s?://.*")
# Offer accepting gzip, as that is supported by the Scryfall server and reduces network data use by 80-90%
supported_encodings = ("gzip", "identity")
JSONType = typing.Dict[str, typing.Union[str, int, list, dict, float, bool]]
BULK_DATA_API_END_POINT = "https://api.scryfall.com/bulk-data"


class CardInfoDownloader(QObject):

    download_progress = pyqtSignal(int)  # Emits the total number of processed items after processing each item
    download_begins = pyqtSignal(int)  # Emitted when the download starts. Data represents the expected total item count
    download_finished = pyqtSignal()  # Emitted when the input data is exhausted and processing finished

    def __init__(self, model: mtg_proxy_printer.model.carddb.CardDatabase,
                 requested_item: str = "all_cards", parent: QObject = None):
        logger.info(f"Creating {self.__class__.__name__} instance.")
        super(CardInfoDownloader, self).__init__(parent)
        self.model = model
        logger.debug("Request bulk data URL from the Scryfall API.")
        self.bulk_card_data_url, self.item_count = self.get_scryfall_bulk_card_data_url(requested_item)
        logger.debug(f"Obtained url: {self.bulk_card_data_url}")
        logger.info(f"Created {self.__class__.__name__} instance.")

    def get_scryfall_bulk_card_data_url(self, requested_item: str = "all_cards") -> (str, int):
        """Returns the bulk data URL and item count"""
        with self._read_from_url(BULK_DATA_API_END_POINT) as data:
            bulk_items = json.load(data)
            for item in bulk_items["data"]:
                if item["type"] == requested_item:
                    return item["download_uri"], 300000
            raise RuntimeError(
                "URL to the Scryfall bulk data export not found. "
                "Expected a download of type 'all_cards' offered by the Scryfall bulk data end point, "
                "but it wos not found. See here: https://scryfall.com/docs/api/bulk-data/all")

    @staticmethod
    def _read_from_url(url: str):
        """
        Reads a given URL and returns a file-like object that can and should be used as a context manager.
        """
        headers = {"Accept-Encoding": ", ".join(supported_encodings)}
        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request)  # type: http.client.HTTPResponse
        if (response_code := response.getcode()) >= 300:
            raise RuntimeError(f"Error from server! Error code: {response_code}")
        encoding = response.info().get("Content-Encoding")
        if encoding == "gzip":
            data = gzip.open(response, "rb")
        elif encoding in ("identity", None):  # Implicit "identity" if the Content-Encoding header is missing.
            data = response
        else:
            raise RuntimeError(f"Server returned unsupported encoding: {encoding}")
        return data

    def read_json_card_data_from_url(self, url: str = None):
        """
        Parses the bulk card data json from https://scryfall.com/docs/api/bulk-data into individual objects.
        This function takes a URL pointing to the card data json object in the Scryfall API.

        The all cards json document is quite large (> 1GiB in 2020-11) and requires about 4GiB RAM to parse in one go.
        So use this iterative parser to generate and yield individual card objects, without having to store the whole
        document in memory.
        """
        if url is None:
            url = self.bulk_card_data_url
        with self._read_from_url(url) as data:
            yield from self._read_json_card_data_from_open_file(data)

    def read_json_card_data(self, url_or_path: typing.Union[Path, str]):
        """
        Parses the bulk card data json from https://scryfall.com/docs/api/bulk-data into individual objects.
        This function can take a file path to a locally stored json document. Mainly for testing purposes.
        Or a URL pointing to the card data json object in the Scryfall API.

        The all cards json document is quite large (> 1GiB in 2020-11) and requires about 4GiB RAM to parse in one go.
        So use this iterative parser to generate and yield individual card objects, without having to store the whole
        document in memory.
        """
        if isinstance(url_or_path, Path):
            if url_or_path.suffix.casefold() == ".gz":
                with gzip.open(url_or_path, "rb") as file:
                    yield from self._read_json_card_data_from_open_file(file)
            else:
                with url_or_path.open("rb") as file:
                    yield from self._read_json_card_data_from_open_file(file)
        elif looks_like_url_re.match(url_or_path):
            yield from self.read_json_card_data_from_url(url_or_path)
        else:
            with open(url_or_path, "rb") as file:
                yield from self._read_json_card_data_from_open_file(file)

    def _read_json_card_data_from_open_file(self, file) -> typing.Generator[JSONType, None, None]:
        self.download_begins.emit(self.item_count)
        # Using "item" as the object path returns elements from a top-level JSON array
        yield from ijson.items(file, "item")
        self.download_finished.emit()

    def populate_database(self, card_data: typing.Generator[JSONType, None, None] = None):
        """
        Takes an iterable returned by card_info_importer.read_json_card_data() and populates the database with card data.
        """
        self.model.db.execute("BEGIN TRANSACTION\n")
        ds = mtg_proxy_printer.settings.settings["downloads"]
        download_enabled = {  # Parse the boolean download settings only once per import
            key: ds.getboolean(key)
            for key in ds.keys()
        }
        for index, card in enumerate(card_data, start=1):
            if card["object"] != "card":
                logger.warning(f"Non-card found in card data during import: {card}")
                continue
            if _should_skip_card(card, download_enabled):
                logger.debug(
                    f"Skipping card '{card['name']}', because it matches a download filter.")
                continue
            language_id = _insert_language(self.model, card["lang"])
            card_id = _insert_card(self.model, card)
            set_id = _insert_set(self.model, card)
            _insert_card_faces(self.model, card, language_id, card_id, set_id)
            self.download_progress.emit(index)
            if not index % 1000:
                self.model.db.execute("PRAGMA optimize\n")
        # Store the timestamp of this import.
        self.model.db.execute("INSERT INTO LastDatabaseUpdate DEFAULT VALUES\n")
        # Populate the sqlite stat tables to give the query optimizer data to work with.
        # This greatly improves query speed.
        self.model.db.execute("ANALYZE\n")
        self.model.commit()


@functools.lru_cache()
def _insert_language(model: CardDatabase, language: str) -> int:
    """
    Inserts the given language into the database and returns the generated ID.
    If the language is already present, just return the ID.
    """
    if result := model.db.execute(
            'SELECT language_id FROM PrintLanguage WHERE "language" = ?\n',
            (language,)).fetchone():
        language_id, = result
    else:
        language_id = model.db.execute(
            'INSERT INTO PrintLanguage("language") VALUES (?)\n',
            (language,)
        ).lastrowid
    return language_id


def _insert_card(model: CardDatabase, card: JSONType) -> int:
    oracle_id: typing.Tuple[str] = card["oracle_id"],
    if result := model.db.execute('SELECT card_id FROM Card WHERE oracle_id = ?\n', oracle_id).fetchone():
        card_id, = result
    else:
        card_id = model.db.execute(
            'INSERT INTO Card (oracle_id) VALUES (?)\n',
            oracle_id
        ).lastrowid
    return card_id


def _insert_set(model: CardDatabase, card: JSONType) -> int:
    set_abbr, set_name, set_uri = card["set"], card["set_name"], card["scryfall_set_uri"]
    if result := model.db.execute('SELECT set_id FROM "Set" WHERE "set" = ?\n', (set_abbr,)).fetchone():
        set_id, = result
    else:
        set_id = model.db.execute(
            'INSERT INTO "Set" ("set", set_name, set_uri) VALUES (?, ?, ?)\n',
            (set_abbr, set_name, set_uri)
        ).lastrowid
    return set_id


def _insert_face_name(model: CardDatabase, printed_name: str, language_id: int) -> int:
    if result := model.db.execute(
            'SELECT face_name_id FROM FaceName WHERE card_name = ? AND language_id = ?\n',
            (printed_name, language_id)).fetchone():
        face_name_id, = result
    else:
        face_name_id = model.db.execute(
            'INSERT INTO FaceName (card_name, language_id) VALUES (?, ?)\n',
            (printed_name, language_id)
        ).lastrowid
    return face_name_id


def _insert_card_faces(model: CardDatabase, card: JSONType, language_id: int, card_id: int, set_id: int):
    collector_number = card["collector_number"]
    highres_image = card["highres_image"]
    for scryfall_id, printed_name, png_image_uri in _get_card_faces(card):
        face_name_id = _insert_face_name(model, printed_name, language_id)
        model.db.execute(
            "INSERT INTO CardFace (\n"
            "  card_id, set_id, face_name_id, collector_number, scryfall_id, highres_image, png_image_uri)\n"
            "VALUES (?, ?, ?, ?, ?, ?, ?)\n",
            (card_id, set_id, face_name_id, collector_number, scryfall_id, highres_image, png_image_uri)
        )


def _should_skip_card(card: JSONType, download_enabled: typing.Dict[str, bool]) -> bool:
    """Determine, if the given card should be included based on the application settings"""
    legalities = card["legalities"]
    return any((
        # Racism filter
        card.get("content_warning", False) and not download_enabled["download-cards-depicting-racism"],
        # Border filter
        card["border_color"] == "white" and not download_enabled["download-white-bordered"],
        card["border_color"] == "gold" and not download_enabled["download-gold-bordered"],
        # 'Funny' cards, not legal in any constructed format. This includes full-art Contraptions from Unstable and some
        # black-bordered promotional cards, in addition to silver-bordered cards.
        card["set_type"] == "funny" and not download_enabled["download-funny-cards"],
        # Format legality. Compare with "legal" to catch both "not_legal" and "banned"
        not (legalities["brawl"] == "legal" or download_enabled["download-illegal-in-brawl"]),
        not (legalities["commander"] == "legal" or download_enabled["download-illegal-in-commander"]),
        not (legalities["historic"] == "legal" or download_enabled["download-illegal-in-historic"]),
        not (legalities["legacy"] == "legal" or download_enabled["download-illegal-in-legacy"]),
        not (legalities["modern"] == "legal" or download_enabled["download-illegal-in-modern"]),
        not (legalities["pauper"] == "legal" or download_enabled["download-illegal-in-pauper"]),
        not (legalities["penny"] == "legal" or download_enabled["download-illegal-in-penny"]),
        not (legalities["pioneer"] == "legal" or download_enabled["download-illegal-in-pioneer"]),
        not (legalities["standard"] == "legal" or download_enabled["download-illegal-in-standard"]),
        not (legalities["vintage"] == "legal" or download_enabled["download-illegal-in-vintage"]),
    ))


def _get_card_faces(card: JSONType) -> typing.Generator[typing.Tuple[str, str, str], None, None]:
    """
    Yields a tuple (Scryfall_id, printed_name, PNG_image_URI) for each face found in the card object.
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
        yield card["id"], _get_card_name(face), _get_png_image_uri(card, face)


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


def _get_card_name(card_or_face: JSONType) -> str:
    # Reads the card name. Non-English cards have both "printed_name" and "name", so prefer "printed_name".
    # English cards only have name, so use that as a fallback.
    try:
        return card_or_face["printed_name"]
    except KeyError:
        return card_or_face["name"]
