# Copyright (C) 2021 Thomas Hess <thomas.hess@udo.edu>

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

import random
import re
import socket
import typing
import urllib.parse
import urllib.error

import ijson

import mtg_proxy_printer.meta_data
from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.card_info_downloader import read_from_url, CardInfoDownloadWorker
from mtg_proxy_printer.natsort import natural_sorted, str_less_than
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

__all__ = [
    "newer_application_version_available",
    "newer_card_data_available",
]

StringList = typing.List[str]
OptStr = typing.Optional[str]
VERSION_TAG_MATCHER = re.compile(r"v(?P<version>\d+\.\d+\.\d+)")
KNOWN_APPLICATION_MIRRORS: StringList = [
    "http://chiselapp.com/user/luziferius/repository/MTGProxyPrinter",
    "http://1337net.duckdns.org:8080/MTGProxyPrinter",
]


def get_application_mirrors() -> StringList:
    mirrors = KNOWN_APPLICATION_MIRRORS.copy()
    random.shuffle(mirrors)
    return mirrors


def read_available_application_versions() -> StringList:
    """
    Reads the available versions from any known mirror
    :returns: List of all released versions, sorted descending.
    """
    tags = []
    for mirror in get_application_mirrors():
        try:
            if tags := _read_available_application_versions_from_mirror(mirror):
                break
        except (urllib.error.URLError, socket.timeout) as e:
            logger.warning(f"Failed to read update from mirror {mirror}. Reason: {e}")
            continue
    return tags


def _read_available_application_versions_from_mirror(mirror):
    data, _ = read_from_url(f"{mirror}/json/tag/list/")
    items = ijson.items(data, "payload.tags.item")
    matches = filter(
        None,
        map(VERSION_TAG_MATCHER.fullmatch, items)
    )
    return natural_sorted((match["version"] for match in matches), reverse=True)


def newer_application_version_available() -> OptStr:
    available_versions = read_available_application_versions()
    if available_versions and str_less_than(mtg_proxy_printer.meta_data.__version__, available_versions[0]):
        return available_versions[0]
    return None


def newer_card_data_available(card_db: CardDatabase) -> int:
    newest_card_in_database = card_db.get_newest_card_date_in_database()
    dw = CardInfoDownloadWorker(card_db)
    query = urllib.parse.quote(f"date>={newest_card_in_database.isoformat()}")
    url = f"https://api.scryfall.com/cards/search?order=date&dir=asc&q={query}"
    try:
        items = next(dw.read_json_card_data(url, "total_cards"))
    except (urllib.error.URLError, socket.timeout, StopIteration):
        # TODO: Perform better notification in any error case
        items = 0
    return items
