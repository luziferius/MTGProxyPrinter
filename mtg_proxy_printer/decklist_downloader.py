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
import re


from mtg_proxy_printer.downloader_base import DownloaderBase
from mtg_proxy_printer.decklist_parser.common import ParserBase
from mtg_proxy_printer.decklist_parser.csv_parsers import ScryfallCSVParser


class DecklistDownloader(DownloaderBase):
    DECKLIST_PATH_RE = re.compile(r"")
    PARSER_CLASS: ParserBase = None

    def download(self, decklist_url: str) -> str:
        download_url = self.map_to_download_url(decklist_url)
        data, monitor = self.read_from_url(download_url, "Downloading deck list:")
        with data, monitor:
            deck_list = data.read()
            if isinstance(deck_list, bytes):
                deck_list = deck_list.decode("utf-8")
        return deck_list

    @abc.abstractmethod
    def map_to_download_url(self, decklist_url: str) -> str:
        pass
    pass


class ScryfallDownloader(DecklistDownloader):
    DECKLIST_PATH_RE = re.compile(
        r"https://scryfall\.com/@\w+/decks/(?P<uuid>[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12})/?"
    )
    PARSER_CLASS = ScryfallCSVParser

    def map_to_download_url(self, decklist_url: str) -> str:
        """Takes a URL to a deck list and returns a download URL"""
        match = self.DECKLIST_PATH_RE.match(decklist_url)
        uuid = match.group("uuid")
        return f"https://api.scryfall.com/decks/{uuid}/export/csv"



