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

import configparser
import typing

import mtg_proxy_printer.settings

import pytest
from hamcrest import *


@pytest.fixture()
def default_settings() -> configparser.ConfigParser:
    settings = configparser.ConfigParser()
    settings.read_dict(mtg_proxy_printer.settings.DEFAULT_SETTINGS)
    return settings


def test__validate_documents_section_restore_horizontal_paper_dimensions(default_settings):
    documents_section = default_settings["documents"]
    documents_section["paper-width-mm"] = "10"
    mtg_proxy_printer.settings.validate_settings(default_settings)
    assert_that(documents_section, has_entries({
        "paper-width-mm": equal_to(mtg_proxy_printer.settings.DEFAULT_SETTINGS["documents"]["paper-width-mm"]),
        "margin-left-mm": equal_to(mtg_proxy_printer.settings.DEFAULT_SETTINGS["documents"]["margin-left-mm"]),
        "margin-right-mm": equal_to(mtg_proxy_printer.settings.DEFAULT_SETTINGS["documents"]["margin-right-mm"]),
    }))


def test__validate_documents_section_restore_vertical_paper_dimensions(default_settings):
    documents_section = default_settings["documents"]
    documents_section["paper-height-mm"] = "10"
    mtg_proxy_printer.settings.validate_settings(default_settings)
    assert_that(documents_section, has_entries({
        "paper-height-mm": equal_to(mtg_proxy_printer.settings.DEFAULT_SETTINGS["documents"]["paper-height-mm"]),
        "margin-top-mm": equal_to(mtg_proxy_printer.settings.DEFAULT_SETTINGS["documents"]["margin-top-mm"]),
        "margin-bottom-mm": equal_to(mtg_proxy_printer.settings.DEFAULT_SETTINGS["documents"]["margin-bottom-mm"]),
    }))


def test__validate_documents_section_document_name(default_settings):
    key, value = "default-document-name", "Test"
    documents_section = default_settings["documents"]
    documents_section[key] = value
    mtg_proxy_printer.settings.validate_settings(default_settings)
    assert_that(documents_section, has_entry(key, equal_to(value)))


@pytest.mark.parametrize("set_filter, parsed_set_codes", [
    ("", []),
    ("LEA", ["lea"]),
    ("2xM", ["2xm"]),
    ("LEB 2xM", ["2xm", "leb"]),
    ("leb 2xM leb LEB", ["2xm", "leb"]),
    ("   LEB\n\n\t2xM ", ["2xm", "leb"]),
])
def test_parse_card_set_filters(default_settings, set_filter: str, parsed_set_codes: typing.List[str]):
    default_settings["card-filter"]["hidden-sets"] = set_filter
    assert_that(
        mtg_proxy_printer.settings.parse_card_set_filters(default_settings),
        contains_exactly(*parsed_set_codes)
    )
