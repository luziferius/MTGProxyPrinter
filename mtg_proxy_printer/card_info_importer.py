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
            with url_or_path.open("rb") as file:
                yield from self._read_json_card_data_from_open_file(file)
        elif looks_like_url_re.match(url_or_path):
            yield from self.read_json_card_data_from_url(url_or_path)
        else:
            with open(url_or_path, "rb") as file:
                yield from self._read_json_card_data_from_open_file(file)

    def _read_json_card_data_from_open_file(self, file) -> typing.Generator[JSONType, None, None]:
        self.download_begins.emit(self.item_count)
        parser = ijson.basic_parse(file, use_float=True)
        # Throw away the outer json array [] that encapsulates the whole data set
        next(parser)
        # Tracks the current nesting depth. Whenever it reaches 0, an object is fully read and can be yielded.
        nesting_depth = 0
        object_builder = ijson.ObjectBuilder()
        for event, value in parser:
            if event in ("start_map", "start_array"):
                nesting_depth += 1
            elif event in ("end_map", "end_array"):
                nesting_depth -= 1
            if nesting_depth == -1:
                # End of the outer json array reached, so stop iterating
                break
            object_builder.event(event, value)
            if nesting_depth == 0:
                yield object_builder.value  # value is dynamically created whenever the parser gathered a full object
                object_builder = ijson.ObjectBuilder()
        self.download_finished.emit()

    def populate_database(self, model: CardDatabase, card_data: typing.Generator[JSONType, None, None] = None):
        """
        Takes an iterable returned by card_info_importer.read_json_card_data() and populates the database with card data.
        """
        for index, card in enumerate(card_data, start=1):
            if card["object"] != "card":
                logger.warning(f"Non-card found in card data during import: {card}")
                continue
            if _should_skip_card(card):
                logger.debug(
                    f"Skipping card '{card['name']}', because it matches a download filter.")
                continue
            set_info = _get_set_info(card)
            card_info = _get_card_info(card)
            faces = list(_get_card_faces(card))
            model.db.execute(
                r"""INSERT OR IGNORE INTO "Set" ("set", set_name, set_uri) VALUES (?, ?, ?)""",
                set_info
            )
            model.db.execute(
                r"""INSERT INTO CARD
                (scryfall_id, oracle_id, "set", collector_number, language, highres_image)
                VALUES (?, ?, ?, ?, ?, ?)""",
                card_info
            )
            model.db.executemany(
                r"""INSERT INTO CardFace (scryfall_id, card_name, png_image_uri) VALUES (?, ?, ?)""",
                faces
            )
            self.download_progress.emit(index)
        # Populate the sqlite stat tables to give the query optimizer data to work with.
        # This greatly improves query speed.
        model.db.execute("ANALYZE")


def _should_skip_card(card: JSONType) -> bool:
    """Determine, if the given card should be included based on the application settings"""
    ds = mtg_proxy_printer.settings.settings["downloads"]
    return any((
        # Racism filter
        card.get("content_warning", False) and not ds.getboolean("download-cards-depicting-racism"),
        # Border filter
        card["border_color"] == "white" and not ds.getboolean("download-white-bordered"),
        card["border_color"] == "gold" and not ds.getboolean("download-gold-bordered"),
        # 'Funny' cards, not legal in any constructed format
        card["set_type"] == "funny" and not ds.getboolean("download-funny-cards"),
        # Format legality. Compare with "legal" to catch both "not_legal" and "banned"
        not (card["legalities"]["brawl"] == "legal" or ds.getboolean("download-illegal-in-brawl")),
        not (card["legalities"]["commander"] == "legal" or ds.getboolean("download-illegal-in-commander")),
        not (card["legalities"]["historic"] == "legal" or ds.getboolean("download-illegal-in-historic")),
        not (card["legalities"]["legacy"] == "legal" or ds.getboolean("download-illegal-in-legacy")),
        not (card["legalities"]["modern"] == "legal" or ds.getboolean("download-illegal-in-modern")),
        not (card["legalities"]["pauper"] == "legal" or ds.getboolean("download-illegal-in-pauper")),
        not (card["legalities"]["penny"] == "legal" or ds.getboolean("download-illegal-in-penny")),
        not (card["legalities"]["pioneer"] == "legal" or ds.getboolean("download-illegal-in-pioneer")),
        not (card["legalities"]["standard"] == "legal" or ds.getboolean("download-illegal-in-standard")),
        not (card["legalities"]["vintage"] == "legal" or ds.getboolean("download-illegal-in-vintage")),
    ))


def _get_set_info(card: JSONType) -> typing.Tuple[str, str, str]:
    set_info = card["set"], card["set_name"], card["scryfall_set_uri"]
    return set_info


def _get_card_info(card: JSONType):
    card_info = (
        card["id"], card["oracle_id"], card["set"], card["collector_number"], card["lang"], card["highres_image"]
    )
    return card_info


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
