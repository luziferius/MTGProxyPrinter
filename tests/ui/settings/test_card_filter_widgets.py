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

from configparser import SectionProxy
import typing
from unittest.mock import patch

from PyQt5.QtWidgets import QCheckBox
import pytest
from hamcrest import *

import mtg_proxy_printer.settings
from mtg_proxy_printer.ui.settings_window import GeneralPrintingFilterWidget, FormatPrintingFilterWidget, AbstractPrintingFilterWidget

T = typing.TypeVar("T")


@pytest.fixture(params=[False, True])
def download_section(request) -> SectionProxy:
    section = mtg_proxy_printer.settings.settings["downloads"]
    mock_values = {key: str(request.param) for key in section.keys()}
    with patch.dict(section, mock_values):
        yield section
        

general_printing_widget_mapping = {
    "download-cards-depicting-racism": "include_cards_depicting_racism",
    "download-cards-without-images": "include_cards_without_images",
    "download-digital-cards": "include_digital_cards",
    "download-funny-cards": "include_funny_cards",
    "download-gold-bordered": "include_gold_bordered_cards",
    "download-oversized-cards": "include_oversized_cards",
    "download-token": "include_token",
    "download-white-bordered": "include_white_bordered_cards"
}


@pytest.mark.parametrize("value", [True, False])
@pytest.mark.parametrize("setting", general_printing_widget_mapping.keys())
def test_general_printing_filter_loads_correctly(qtbot, download_section, setting: str, value: bool):
    download_section[setting] = str(value)
    widget = _create_widget_with_loaded_settings(qtbot, GeneralPrintingFilterWidget, download_section)
    for key, widget_name in general_printing_widget_mapping.items():
        checkbox = getattr(widget, widget_name)
        assert_that(
            checkbox.isChecked(),
            is_(equal_to(download_section.getboolean(key))),
            f"Failing key: {key}"
        )


def _create_widget_with_loaded_settings(qtbot, widget_class: typing.Type[T], download_section: SectionProxy) -> T:
    widget: AbstractPrintingFilterWidget = widget_class()
    qtbot.addWidget(widget)
    with qtbot.waitExposed(widget, timeout=100):
        widget.show()
    widget.load_settings(download_section)
    return widget


format_printing_widget_mapping = {
    "download-banned-in-brawl": "include_banned_in_brawl",
    "download-banned-in-commander": "include_banned_in_commander",
    "download-banned-in-historic": "include_banned_in_historic",
    "download-banned-in-legacy": "include_banned_in_legacy",
    "download-banned-in-modern": "include_banned_in_modern",
    "download-banned-in-pauper": "include_banned_in_pauper",
    "download-banned-in-penny": "include_banned_in_penny",
    "download-banned-in-pioneer": "include_banned_in_pioneer",
    "download-banned-in-standard": "include_banned_in_standard",
    "download-banned-in-vintage": "include_banned_in_vintage",
}


@pytest.mark.parametrize("value", [True, False])
@pytest.mark.parametrize("setting", format_printing_widget_mapping.keys())
def test_format_printing_filter_loads_correctly(qtbot, download_section, setting: str, value: bool):
    download_section[setting] = str(value)
    widget = _create_widget_with_loaded_settings(qtbot, FormatPrintingFilterWidget, download_section)
    checkbox: QCheckBox = getattr(widget, format_printing_widget_mapping[setting])
    assert_that(
        checkbox.isChecked(),
        is_(equal_to(value))
    )
    for key, widget_name in format_printing_widget_mapping.items():
        checkbox: QCheckBox = getattr(widget, widget_name)
        assert_that(checkbox, is_(instance_of(QCheckBox)))
        assert_that(
            checkbox.isChecked(),
            is_(equal_to(download_section.getboolean(key))),
            f"Failing key: {key}"
        )


@pytest.mark.parametrize("value", [True, False])
@pytest.mark.parametrize("setting", format_printing_widget_mapping.keys())
def test_format_printing_filter_saves_correctly(qtbot, download_section, setting: str, value: bool):
    widget = _create_widget_with_loaded_settings(qtbot, FormatPrintingFilterWidget, download_section)
    checkbox: QCheckBox = getattr(widget, format_printing_widget_mapping[setting])
    assert_that(checkbox, is_(instance_of(QCheckBox)))
    checkbox.setChecked(value)
    widget.save_settings(download_section)
    assert_that(
        download_section,
        has_entry(setting, equal_to(str(value))),
        f"Key not saved correctly: {setting}"
    )