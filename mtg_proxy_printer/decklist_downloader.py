# Copyright (C) 2022 Thomas Hess <thomas.hess@udo.edu>

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

"""
This module is responsible for downloading deck lists from a known list of deckbuilder websites.
"""
import abc
import csv
from io import StringIO
import re
import typing

import ijson
from PyQt5.QtGui import QValidator

from mtg_proxy_printer.downloader_base import DownloaderBase
from mtg_proxy_printer.decklist_parser.common import ParserBase
from mtg_proxy_printer.decklist_parser.csv_parsers import ScryfallCSVParser, TappedOutCSVParser
from mtg_proxy_printer.decklist_parser.re_parsers import MTGArenaParser, MTGOnlineParser
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


class IsIdentifyingDeckUrlValidator(QValidator):
    """
    Validator that checks, if the given string is a valid URL prefix pointing to a deck on a known deck
    building website.
    If this validator passes, at least one downloader class is able to fetch a deck list from the given input string.
    """

    def validate(self, input_string: str, pos: int = 0) -> typing.Tuple[QValidator.State, str, int]:
        logger.debug(f"Validating input: {input_string}")
        for downloader_class in AVAILABLE_DOWNLOADERS:
            if downloader_class.DECKLIST_PATH_RE.match(input_string) is not None:
                logger.debug(f"Input is valid URL for {downloader_class.APPLICABLE_WEBSITES}")
                return QValidator.Acceptable, input_string, pos
        return QValidator.Intermediate, input_string, pos


class DecklistDownloader(DownloaderBase):
    DECKLIST_PATH_RE = re.compile(r"")
    PARSER_CLASS: ParserBase = None
    APPLICABLE_WEBSITES: str = ""

    def download(self, decklist_url: str) -> str:
        logger.info(f"About to fetch deck list from {decklist_url}")
        download_url = self.map_to_download_url(decklist_url)
        logger.debug(f"Obtained download URL: {download_url}")
        data, monitor = self.read_from_url(download_url, "Downloading deck list:")
        with data, monitor:
            raw_data = data.read()
        deck_list = self.post_process(raw_data)
        line_count = deck_list.count('\n')
        logger.debug(f"Obtained deck list containing {line_count} lines.")
        return deck_list

    @staticmethod
    def post_process(data: bytes) -> str:
        """Takes the raw, downloaded data and post-processes them into a user-presentable string."""
        deck_list = data.replace(b"\r\n", b"\n")
        deck_list = deck_list.decode("utf-8")
        return deck_list

    @abc.abstractmethod
    def map_to_download_url(self, decklist_url: str) -> str:
        """Takes a URL to a deck list and returns a download URL"""
        pass
    pass


class ScryfallDownloader(DecklistDownloader):
    DECKLIST_PATH_RE = re.compile(
        r"https://scryfall\.com/@\w+/decks/(?P<uuid>[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12})/?"
    )
    PARSER_CLASS = ScryfallCSVParser
    APPLICABLE_WEBSITES = "Scryfall (scryfall.com)"

    def map_to_download_url(self, decklist_url: str) -> str:
        match = self.DECKLIST_PATH_RE.match(decklist_url)
        uuid = match.group("uuid")
        return f"https://api.scryfall.com/decks/{uuid}/export/csv"


class MTGGoldfishDownloader(DecklistDownloader):
    DECKLIST_PATH_RE = re.compile(
        r"https://(www\.)?mtggoldfish\.com/deck(/download)?/(?P<deck_id>\d+)([#?].*)?$"
    )
    PARSER_CLASS = MTGArenaParser
    APPLICABLE_WEBSITES = "MTGGoldfish (mtggoldfish.com)"

    def map_to_download_url(self, decklist_url: str) -> str:
        match = self.DECKLIST_PATH_RE.match(decklist_url)
        deck_id = match.group("deck_id")
        url = f"https://www.mtggoldfish.com/deck/download/{deck_id}?type=arena"
        return url


class MTGWTFDownloader(DecklistDownloader):
    """
    Downloader for https://mtg.wtf. They offer a list of all official pre-constructed decks in existence.
    """
    DECKLIST_PATH_RE = re.compile(
        r"https://mtg\.wtf/deck/\w+/(?P<name>\w+)/?"
    )
    PARSER_CLASS = None  # TODO
    APPLICABLE_WEBSITES = "mtg.wtf"

    def map_to_download_url(self, decklist_url: str) -> str:
        return f"{decklist_url}/download"


class TappedOutDownloader(DecklistDownloader):
    DECKLIST_PATH_RE = re.compile(
        r"https://tappedout.net/mtg-decks/(?P<name>[-\w_%]+)/?"
    )
    PARSER_CLASS = TappedOutCSVParser
    APPLICABLE_WEBSITES = "TappedOut (tappedout.net)"

    def map_to_download_url(self, decklist_url: str) -> str:
        match = self.DECKLIST_PATH_RE.match(decklist_url)
        name = match.group("name")
        return f"https://tappedout.net/mtg-decks/{name}/?fmt=csv"


class MoxfieldDownloader(DecklistDownloader):
    DECKLIST_PATH_RE = re.compile(
        r"https://www.moxfield.com/decks/(?P<moxfield_id>[-\w_]+)/?"
    )
    PARSER_CLASS = ScryfallCSVParser
    APPLICABLE_WEBSITES = "Moxfield (moxfield.com)"

    @staticmethod
    def post_process(data: bytes) -> str:
        cards = MoxfieldDownloader._read_board(data, "mainboard")
        cards += MoxfieldDownloader._read_board(data, "sideboard")
        buffer = StringIO(newline="")
        writer = csv.writer(buffer, MoxfieldDownloader.PARSER_CLASS.Dialect)
        writer.writerow(("count", "scryfall_id", "lang", "name", "set_code", "collector_number"))
        writer.writerows(cards)
        return buffer.getvalue()

    @staticmethod
    def _read_board(data: bytes, board: str) -> typing.List[typing.Tuple[str, str, str, str, str, str]]:
        result = []
        for entry in next(ijson.items(data, board)).values():
            card = entry["card"]
            result.append(
                (str(entry["quantity"]), card["scryfall_id"], card["lang"], card["name"], card["set"], card["cn"]))
        return result

    def map_to_download_url(self, decklist_url: str) -> str:
        match = self.DECKLIST_PATH_RE.match(decklist_url)
        moxfield_id = match.group("moxfield_id")
        return f"https://api.moxfield.com/v2/decks/all/{moxfield_id}"


AVAILABLE_DOWNLOADERS = [
    ScryfallDownloader,
    MTGGoldfishDownloader,
    MTGWTFDownloader,
    TappedOutDownloader,
    MoxfieldDownloader,
]


def get_downloader_class(url: str):
    for downloader in AVAILABLE_DOWNLOADERS:
        if downloader.DECKLIST_PATH_RE.match(url) is not None:
            return downloader
    return None
