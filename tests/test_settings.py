# Copyright (C) 2020-2024 Thomas Hess <thomas.hess@udo.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import configparser
from itertools import chain
from numbers import Real
import typing

import mtg_proxy_printer.settings

import pytest
from hamcrest import *


@pytest.fixture
def default_settings() -> configparser.ConfigParser:
    settings = configparser.ConfigParser()
    settings.read_dict(mtg_proxy_printer.settings.DEFAULT_SETTINGS)
    return settings


@pytest.mark.parametrize("value, multiple, expected", chain(
    # Fractional multiple
    ((x/12, 1/12, x/12) for x in range(12)),  # Fractions of 1/12
    ((x/12+1/100, 1/12, x/12) for x in range(12)),  # Larger values get rounded down
    ((x/12-1/100, 1/12, x/12) for x in range(12)),  # Smaller values get rounded up
    # Integer multiple
    ((10*x, 10, 10*x) for x in (range(10))),
    ((10*x+1, 10, 10*x) for x in (range(10))),
    ((10*x-1, 10, 10*x) for x in (range(10))),
))
def test_round_to_nearest_multiple(value: Real, multiple: Real, expected: Real):
    assert_that(
        mtg_proxy_printer.settings.round_to_nearest_multiple(value, multiple),
        is_(close_to(expected, 0.0001))
    )


@pytest.mark.parametrize("invalid", [10, 10.5, 0, -1])
def test__validate_documents_section_restore_horizontal_paper_dimensions(default_settings, invalid: float):
    documents_section = default_settings["documents"]
    documents_section["paper-width-mm"] = str(invalid)
    mtg_proxy_printer.settings.validate_settings(default_settings)
    assert_that(documents_section, has_entries({
        "paper-width-mm": equal_to(mtg_proxy_printer.settings.DEFAULT_SETTINGS["documents"]["paper-width-mm"]),
        "margin-left-mm": equal_to(mtg_proxy_printer.settings.DEFAULT_SETTINGS["documents"]["margin-left-mm"]),
        "margin-right-mm": equal_to(mtg_proxy_printer.settings.DEFAULT_SETTINGS["documents"]["margin-right-mm"]),
    }))


@pytest.mark.parametrize("invalid", [10, 10.5, 0, -1])
def test__validate_documents_section_restore_vertical_paper_dimensions(default_settings, invalid: float):
    documents_section = default_settings["documents"]
    documents_section["paper-height-mm"] = str(invalid)
    mtg_proxy_printer.settings.validate_settings(default_settings)
    assert_that(documents_section, has_entries({
        "paper-height-mm": equal_to(mtg_proxy_printer.settings.DEFAULT_SETTINGS["documents"]["paper-height-mm"]),
        "margin-top-mm": equal_to(mtg_proxy_printer.settings.DEFAULT_SETTINGS["documents"]["margin-top-mm"]),
        "margin-bottom-mm": equal_to(mtg_proxy_printer.settings.DEFAULT_SETTINGS["documents"]["margin-bottom-mm"]),
    }))


@pytest.mark.parametrize("value", [0, 1/12, 11/12, 1])
@pytest.mark.parametrize("offset", [0, -0.01, 0.01])
@pytest.mark.parametrize("settings_key", [
    "margin-top-mm", "margin-bottom-mm", "margin-left-mm", "margin-right-mm",
    "row-spacing-mm", "column-spacing-mm", "card-bleed-mm"])
def test__validate_documents_section_rounds_spacing_value_to_acceptable_value(
        default_settings, value: float, offset: float, settings_key: str):
    documents_section = default_settings["documents"]
    documents_section[settings_key] = str(value+offset)
    mtg_proxy_printer.settings.validate_settings(default_settings)
    assert_that(
        documents_section.getfloat(settings_key),
        is_(close_to(value, 0.0001))
    )


@pytest.mark.parametrize("value", [297, 297+1/12, 297+11/12, 298])
@pytest.mark.parametrize("offset", [0, -0.01, 0.01])
@pytest.mark.parametrize("settings_key", ["paper-height-mm", "paper-width-mm",])
def test__validate_documents_section_rounds_paper_size_value_to_acceptable_value(
        default_settings, value: float, offset: float, settings_key: str):
    documents_section = default_settings["documents"]
    documents_section[settings_key] = str(value+offset)
    mtg_proxy_printer.settings.validate_settings(default_settings)
    assert_that(
        documents_section.getfloat(settings_key),
        is_(close_to(value, 0.0001))
    )

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
        contains_inanyorder(*parsed_set_codes)
    )
