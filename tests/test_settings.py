#  Copyright © 2020-2025  Thomas Hess <thomas.hess@udo.edu>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.

from collections.abc import Iterable
from itertools import chain
from numbers import Real
from pathlib import Path
from unittest.mock import patch

import pint
import pytest
from hamcrest import *

import mtg_proxy_printer.settings
from mtg_proxy_printer.units_and_sizes import unit_registry, ConfigParser
from tests.helpers import quantity_between


def between_including(lower: Real, upper: Real):
    return all_of(greater_than_or_equal_to(lower), less_than_or_equal_to(upper))


def to_mm_str(value: Real) -> str:
    return str(value*unit_registry.mm)


@pytest.fixture
def default_settings() -> ConfigParser:
    settings = ConfigParser()
    settings.read_dict(mtg_proxy_printer.settings.DEFAULT_SETTINGS)
    return settings


def length_document_settings_keys() -> Iterable[str]:
    return (
        key for key, value in mtg_proxy_printer.settings.DEFAULT_SETTINGS["documents"].items()
        if value.endswith(" mm")
    )


def test_configparser_has_get_quantity(default_settings: ConfigParser):
    assert_that(default_settings, has_property("get_quantity"))


def test_section_has_get_quantity(default_settings: ConfigParser):
    assert_that(default_settings["DEFAULT"], has_property("get_quantity"))


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


@pytest.mark.parametrize("unit", ["mm", "in"])
@pytest.mark.parametrize("invalid", [2, 2.5, 0, -1])
def test__validate_documents_section_restore_horizontal_paper_dimensions(
        default_settings: ConfigParser, invalid: float, unit: str):
    documents_section = default_settings["documents"]
    documents_section["custom-page-width"] = str(invalid*unit_registry(unit))
    mtg_proxy_printer.settings.validate_settings(default_settings)
    assert_that(documents_section, has_entries({
        "custom-page-width": equal_to(mtg_proxy_printer.settings.DEFAULT_SETTINGS["documents"]["custom-page-width"]),
        "margin-left": equal_to(mtg_proxy_printer.settings.DEFAULT_SETTINGS["documents"]["margin-left"]),
        "margin-right": equal_to(mtg_proxy_printer.settings.DEFAULT_SETTINGS["documents"]["margin-right"]),
    }))


@pytest.mark.parametrize("unit", ["mm", "in"])
@pytest.mark.parametrize("invalid", [2, 2.5, 0, -1])
def test__validate_documents_section_restore_vertical_paper_dimensions(
        default_settings: ConfigParser, invalid: float, unit: str):
    defaults = mtg_proxy_printer.settings.DEFAULT_SETTINGS["documents"]
    documents_section = default_settings["documents"]
    documents_section["custom-page-height"] = str(invalid*unit_registry(unit))
    mtg_proxy_printer.settings.validate_settings(default_settings)
    assert_that(documents_section, has_entries({
        "custom-page-height": equal_to(defaults["custom-page-height"]),
        "margin-top": equal_to(defaults["margin-top"]),
        "margin-bottom": equal_to(defaults["margin-bottom"]),
    }))


@pytest.mark.parametrize("setting", length_document_settings_keys())
@pytest.mark.parametrize("unit", ["s", "", "kg", ' " '])
def test__validate_document_section_restore_paper_dimensions_with_invalid_units(
        default_settings: ConfigParser, setting: str, unit: str):
    defaults = mtg_proxy_printer.settings.DEFAULT_SETTINGS["documents"]
    documents_section = default_settings["documents"]
    invalid_value = f'{documents_section[setting].split(" ")[0]} {unit}'.rstrip(" ")
    documents_section[setting] = invalid_value
    mtg_proxy_printer.settings.validate_settings(default_settings)
    assert_that(documents_section, has_entry(setting, equal_to(defaults[setting])))


@pytest.mark.parametrize("setting", length_document_settings_keys())
@pytest.mark.parametrize("value", [
    "1_000_000_000 nm", "1.0570008340246154e-16 light_year", "11811.023622047245 pixel",  # 1 m
    "-1_000_000_000 nm", "-1.0570008340246154e-16 light_year", "-11811.023622047245 pixel",  # -1 m
    "100_000_000_000 nm", "1.0570008340246154e-14 light_year", "1181102.3622047245 pixel",  # 100 m
    "-100_000_000_000 nm", "-1.0570008340246154e-14 light_year", "-1181102.3622047245 pixel",  # -100 m

])
def test__validate_document_section_normalizes_unsupported_length_units_to_mm(
        default_settings: ConfigParser, setting: str, value: str):
    documents_section = default_settings["documents"]
    documents_section[setting] = value
    mtg_proxy_printer.settings.validate_settings(default_settings)
    limit = mtg_proxy_printer.settings.DOCUMENT_SETTINGS_QUANTITY_LIMITS[setting]
    assert_that(
        documents_section.get_quantity(setting),
        is_(quantity_between(limit.minimum, limit.maximum))
    )


@pytest.mark.parametrize("expected", [0, 1/12, 11/12, 1])
@pytest.mark.parametrize("offset", [0, -1/101, 1/101])
@pytest.mark.parametrize("settings_key", [
    "margin-top", "margin-bottom", "margin-left", "margin-right",
    "row-spacing", "column-spacing", "card-bleed"])
def test__validate_documents_section_rounds_spacing_value_to_acceptable_value(
        default_settings: ConfigParser, expected: float, offset: float, settings_key: str):
    documents_section = default_settings["documents"]
    documents_section[settings_key] = to_mm_str(expected+offset)
    mtg_proxy_printer.settings.validate_settings(default_settings)
    value = documents_section.get_quantity(settings_key).to("mm").magnitude
    assert_that(value, is_(close_to(expected, 0.01)))


@pytest.mark.parametrize("expected", [297, 297 + 1 / 12, 297 + 11 / 12, 298])
@pytest.mark.parametrize("offset", [0, -1/101, 1/101])
@pytest.mark.parametrize("settings_key", ["custom-page-height", "custom-page-width",])
def test__validate_documents_section_rounds_paper_size_value_to_acceptable_value(
        default_settings: ConfigParser, expected: float | int, offset: float, settings_key: str):
    documents_section = default_settings["documents"]
    documents_section[settings_key] = to_mm_str(expected + offset)
    mtg_proxy_printer.settings.validate_settings(default_settings)
    value = documents_section.get_quantity(settings_key).to("mm").magnitude
    assert_that(value, is_(close_to(expected, 0.01)))


def test__validate_documents_section_document_name(default_settings: ConfigParser):
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
def test_parse_card_set_filters(default_settings: ConfigParser, set_filter: str, parsed_set_codes: list[str]):
    default_settings["card-filter"]["hidden-sets"] = set_filter
    assert_that(
        mtg_proxy_printer.settings.parse_card_set_filters(default_settings),
        contains_inanyorder(*parsed_set_codes)
    )


@pytest.mark.parametrize("value, expected", [
    (-0.01, 0),
    (0, 0),
    (1, 1),
    (9999, 9999),
    (10000, 10000),
    (10001, 10000),
    (10000.1, 10000),
])
def test_clamp_to_supported_range(value: float, expected: float):
    value_as_distance: pint.Quantity = value*unit_registry.mm
    clamped_value = mtg_proxy_printer.settings.clamp_to_supported_range(
        value_as_distance, mtg_proxy_printer.settings.DEFAULT_LENGTH_LIMIT).magnitude
    assert_that(clamped_value, is_(close_to(expected, 0.001)))


@pytest.mark.parametrize("source_file", Path(__file__).with_name("settings_files").glob("*.ini"))
def test_migration_does_not_crash(source_file: Path, default_settings: ConfigParser):
    """
    The settings_files directory contains sample configuration files from throughout the application history.
    Any of these must migrate to the newest version without raising exceptions.
    """
    with patch("mtg_proxy_printer.settings.config_file_path", source_file), \
            patch("mtg_proxy_printer.settings.settings", default_settings):
        mtg_proxy_printer.settings.read_settings_from_file()
