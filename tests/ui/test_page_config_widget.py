# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>
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

import unittest.mock

from PyQt5.QtWidgets import QSpinBox, QCheckBox

from hamcrest import *
import pytest
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.model.document_loader import PageLayoutSettings
import mtg_proxy_printer.settings
import mtg_proxy_printer.ui.page_config_widget


@pytest.mark.parametrize("attribute_name", [
    "page_height",
    "page_width",
    "margin_top",
    "margin_bottom",
    "margin_left",
    "margin_right",
    "row_spacing",
    "column_spacing",
])
def test_set_integer_spin_boxes(qtbot: QtBot, attribute_name: str):
    widget = mtg_proxy_printer.ui.page_config_widget.PageConfigWidget()
    ui = widget.ui
    qtbot.addWidget(widget)
    assert_that(ui, has_property(attribute_name, instance_of(QSpinBox)))
    assert_that(widget.page_layout, has_property(attribute_name, instance_of(int)))
    spinbox_widget: QSpinBox = getattr(ui, attribute_name)
    with qtbot.waitSignal(spinbox_widget.valueChanged):
        previous = spinbox_widget.value()
        new_value = previous + 1
        spinbox_widget.setValue(new_value)
    assert_that(widget.page_layout, has_property(attribute_name, equal_to(new_value)))


@pytest.mark.parametrize("attribute_name", [
    "draw_cut_markers",
])
def test_boolean_check_boxes(qtbot: QtBot, attribute_name: str):
    widget = mtg_proxy_printer.ui.page_config_widget.PageConfigWidget()
    ui = widget.ui
    qtbot.addWidget(widget)
    assert_that(ui, has_property(attribute_name, instance_of(QCheckBox)))
    assert_that(widget.page_layout, has_property(attribute_name, instance_of(bool)))
    checkbox_widget: QCheckBox = getattr(ui, attribute_name)
    with qtbot.waitSignal(checkbox_widget.stateChanged):
        previous = checkbox_widget.isChecked()
        new_value = not previous
        checkbox_widget.setChecked(new_value)
    assert_that(widget.page_layout, has_property(attribute_name, equal_to(new_value)))
    # Test second time to ensure both ways (enable & disable) work
    with qtbot.waitSignal(checkbox_widget.stateChanged):
        previous = checkbox_widget.isChecked()
        new_value = not previous
        checkbox_widget.setChecked(new_value)
    assert_that(widget.page_layout, has_property(attribute_name, equal_to(new_value)))


@pytest.mark.parametrize("value", [-1, 0, 1, 200, 1000])
@pytest.mark.parametrize("settings_name, attribute_name, min_value", [
    ("paper-height-mm", "page_height", 136),
    ("paper-width-mm", "page_width", 93),
    ("margin-top-mm", "margin_top", 0),
    ("margin-bottom-mm", "margin_bottom", 0),
    ("margin-left-mm", "margin_left", 0),
    ("margin-right-mm", "margin_right", 0),
    ("row-spacing-mm", "row_spacing", 0),
    ("column-spacing-mm", "column_spacing", 0),
])
def test_load_integer_document_settings_from_config(
        qtbot: QtBot, settings_name: str, attribute_name: str, min_value: int, value: int):
    """
    Tests loading integer settings from config. Some values, like page size, have a minimum value greater than 0,
    to ensure that at least one image fits on a page.
    """
    widget = mtg_proxy_printer.ui.page_config_widget.PageConfigWidget()
    qtbot.addWidget(widget)
    document_settings = mtg_proxy_printer.settings.settings["documents"]
    with unittest.mock.patch.dict(document_settings, {settings_name: str(value)}):
        expected = max(min_value, value)
        widget.load_document_settings_from_config(mtg_proxy_printer.settings.settings)
        assert_that(widget.page_layout, has_property(attribute_name, equal_to(expected)))
        spinbox_widget: QSpinBox = getattr(widget.ui, attribute_name)
        assert_that(spinbox_widget.value(), is_(equal_to(expected)))


@pytest.mark.parametrize("value", [True, False])
@pytest.mark.parametrize("settings_name, attribute_name", [
    ("print-cut-marker", "draw_cut_markers"),
])
def test_load_boolean_checkboxes_from_config(qtbot: QtBot, settings_name: str, attribute_name: str, value: bool):
    widget = mtg_proxy_printer.ui.page_config_widget.PageConfigWidget()
    qtbot.addWidget(widget)
    document_settings = mtg_proxy_printer.settings.settings["documents"]
    with unittest.mock.patch.dict(document_settings, {settings_name: str(value)}):
        widget.load_document_settings_from_config(mtg_proxy_printer.settings.settings)
        assert_that(widget.page_layout, has_property(attribute_name, equal_to(value)))
    checkbox_widget: QCheckBox = getattr(widget.ui, attribute_name)
    assert_that(checkbox_widget.isChecked(), is_(equal_to(value)))


@pytest.mark.parametrize("value", [-1, 0, 1, 200, 1000])
@pytest.mark.parametrize("settings_name, attribute_name, min_value", [
    ("paper-height-mm", "page_height", 136),
    ("paper-width-mm", "page_width", 98),
    ("margin-top-mm", "margin_top", 0),
    ("margin-bottom-mm", "margin_bottom", 0),
    ("margin-left-mm", "margin_left", 0),
    ("margin-right-mm", "margin_right", 0),
    ("row-spacing-mm", "row_spacing", 0),
    ("column-spacing-mm", "column_spacing", 0),
])
def test_save_integer_document_settings_to_config(
        qtbot: QtBot, settings_name: str, attribute_name: str, min_value: int, value: int):
    """
    Tests loading integer settings from config. Some values, like page size, have a minimum value greater than 0,
    to ensure that at least one image fits on a page.
    """
    widget = mtg_proxy_printer.ui.page_config_widget.PageConfigWidget()
    qtbot.addWidget(widget)
    document_settings = mtg_proxy_printer.settings.settings["documents"]
    widget.load_document_settings_from_config(mtg_proxy_printer.settings.settings)
    original_value = document_settings[settings_name]
    with unittest.mock.patch.dict(document_settings, {settings_name: original_value}):
        expected = str(max(min_value, value))
        spinbox_widget: QSpinBox = getattr(widget.ui, attribute_name)
        spinbox_widget.setValue(spinbox_widget.value()+10000)
        with qtbot.waitSignal(spinbox_widget.valueChanged, timeout=1000):
            spinbox_widget.setValue(value)
        widget.save_document_settings_to_config()
        assert_that(document_settings, has_entry(settings_name, equal_to(expected)))
    assert_that(document_settings, has_entry(settings_name, equal_to(original_value)))


@pytest.mark.parametrize("value", [True, False])
@pytest.mark.parametrize("settings_name, attribute_name", [
    ("print-cut-marker", "draw_cut_markers"),
])
def test_save_boolean_document_settings_to_config(
        qtbot: QtBot, settings_name: str, attribute_name: str, value: bool):
    """
    Tests loading integer settings from config. Some values, like page size, have a minimum value greater than 0,
    to ensure that at least one image fits on a page.
    """
    widget = mtg_proxy_printer.ui.page_config_widget.PageConfigWidget()
    qtbot.addWidget(widget)
    document_settings = mtg_proxy_printer.settings.settings["documents"]
    widget.load_document_settings_from_config(mtg_proxy_printer.settings.settings)
    original_value = document_settings[settings_name]
    with unittest.mock.patch.dict(document_settings, {settings_name: original_value}):
        checkbox_widget: QCheckBox = getattr(widget.ui, attribute_name)
        checkbox_widget.setChecked(value)
        widget.save_document_settings_to_config()
        assert_that(document_settings, has_entry(settings_name, equal_to(str(value))))
    assert_that(document_settings, has_entry(settings_name, equal_to(original_value)))


@pytest.mark.parametrize("value", [0, 1, 200, 1000])
@pytest.mark.parametrize("attribute_name, min_value", [
    ("page_height", 136),
    ("page_width", 98),
    ("margin_top", 0),
    ("margin_bottom", 0),
    ("margin_left", 0),
    ("margin_right", 0),
    ("row_spacing", 0),
    ("column_spacing", 0),
])
def test_load_integers_from_page_layout(qtbot: QtBot, attribute_name: str, min_value: int, value: int):
    """
    Tests loading integer settings from config. Some values, like page size, have a minimum value greater than 0,
    to ensure that at least one image fits on a page.
    """
    widget = mtg_proxy_printer.ui.page_config_widget.PageConfigWidget()
    qtbot.addWidget(widget)
    other = PageLayoutSettings.create_from_settings()
    setattr(other, attribute_name, value)
    expected = max(min_value, value)
    widget.load_from_page_layout(other)
    assert_that(widget.page_layout, has_property(attribute_name, equal_to(expected)))
    spinbox_widget: QSpinBox = getattr(widget.ui, attribute_name)
    assert_that(spinbox_widget.value(), is_(equal_to(expected)))


@pytest.mark.parametrize("value", [True, False])
@pytest.mark.parametrize("attribute_name", [
    "draw_cut_markers",
])
def test_load_booleans_from_page_layout(qtbot: QtBot, attribute_name: str, value: bool):
    widget = mtg_proxy_printer.ui.page_config_widget.PageConfigWidget()
    qtbot.addWidget(widget)
    other = PageLayoutSettings.create_from_settings()
    setattr(other, attribute_name, value)
    widget.load_from_page_layout(other)
    assert_that(widget.page_layout, has_property(attribute_name, equal_to(value)))
    checkbox_widget: QCheckBox = getattr(widget.ui, attribute_name)
    assert_that(checkbox_widget.isChecked(), is_(equal_to(value)))
