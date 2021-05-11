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
import typing

import ijson

import mtg_proxy_printer.meta_data
from mtg_proxy_printer.card_info_downloader import read_from_url
from mtg_proxy_printer.natsort import natural_sorted, str_less_than

__all__ = [
    "newer_application_version_available",
]

StringList = typing.List[str]
OptStr = typing.Optional[str]
VERSION_TAG_MATCHER = re.compile(r"v(?P<version>\d+\.\d+\.\d+)")
KNOWN_APPLICATION_MIRRORS: StringList = [
    "https://chiselapp.com/user/luziferius/repository/MTGProxyPrinter",
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
        if tags := _read_available_application_versions_from_mirror(mirror):
            break
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


def newer_card_data_available() -> bool:

    return False
