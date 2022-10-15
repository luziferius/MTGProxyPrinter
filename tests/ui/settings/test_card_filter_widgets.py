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

from PySide6.QtWidgets import QCheckBox
import pytest
from hamcrest import *

import mtg_proxy_printer.settings
from mtg_proxy_printer.ui.printing_filter_widgets import AbstractPrintingFilterWidget, GeneralPrintingFilterWidget, \
    FormatPrintingFilterWidget

T = typing.TypeVar("T")


@pytest.fixture(params=[False, True])
def download_section(request) -> SectionProxy:
    section = mtg_proxy_printer.settings.settings["card-filter"]
    mock_values = {key: str(request.param) for key in section.keys()}
    with patch.dict(section, mock_values):
        yield section
        

general_printing_widget_mapping = {
    "hide-cards-depicting-racism": "hide_cards_depicting_racism",
    "hide-cards-without-images": "hide_cards_without_images",
    "hide-digital-cards": "hide_digital_cards",
    "hide-funny-cards": "hide_funny_cards",
    "hide-gold-bordered": "hide_gold_bordered_cards",
    "hide-oversized-cards": "hide_oversized_cards",
    "hide-token": "hide_token",
    "hide-white-bordered": "hide_white_bordered_cards"
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
    with qtbot.waitExposed(widget, timeout=1000):
        widget.show()
    widget.load_settings(download_section)
    return widget


format_printing_widget_mapping = {
    "hide-banned-in-brawl": "hide_banned_in_brawl",
    "hide-banned-in-commander": "hide_banned_in_commander",
    "hide-banned-in-historic": "hide_banned_in_historic",
    "hide-banned-in-legacy": "hide_banned_in_legacy",
    "hide-banned-in-modern": "hide_banned_in_modern",
    "hide-banned-in-pauper": "hide_banned_in_pauper",
    "hide-banned-in-penny": "hide_banned_in_penny",
    "hide-banned-in-pioneer": "hide_banned_in_pioneer",
    "hide-banned-in-standard": "hide_banned_in_standard",
    "hide-banned-in-vintage": "hide_banned_in_vintage",
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
