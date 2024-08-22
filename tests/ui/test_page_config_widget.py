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

import functools
from unittest.mock import patch

from PySide6.QtWidgets import QDoubleSpinBox, QCheckBox

from hamcrest import *
import pytest
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.model.document_loader import PageLayoutSettings
import mtg_proxy_printer.settings
from mtg_proxy_printer.ui.page_config_widget import PageConfigWidget

from tests.hasgetter import has_getter
close_to_ = functools.partial(close_to, delta=0.01)


@pytest.fixture()
def widget(qtbot: QtBot) -> PageConfigWidget:
    widget = PageConfigWidget()
    qtbot.addWidget(widget)
    return widget

@pytest.mark.parametrize("name, min_value", [
    ("page_height", 126),
    ("page_width", 88),
])
def test_paper_size_spin_box_minimum_value(widget: PageConfigWidget, name: str, min_value: int):
    spinbox: QDoubleSpinBox = getattr(widget.ui, name)
    assert_that(spinbox, has_getter("minimum", equal_to(min_value)))


@pytest.mark.parametrize("attribute_name", [
    "page_height",
    "page_width",
    "margin_top",
    "margin_bottom",
    "margin_left",
    "margin_right",
    "row_spacing",
    "column_spacing",
    "card_bleed",
])
def test_set_numerical_spin_boxes(qtbot: QtBot, widget: PageConfigWidget, attribute_name: str):
    widget.load_from_page_layout(PageLayoutSettings.create_from_settings())
    ui = widget.ui
    assert_that(ui, has_property(attribute_name, instance_of(QDoubleSpinBox)))
    assert_that(widget.page_layout, has_property(attribute_name, instance_of(float)))
    spinbox_widget: QDoubleSpinBox = getattr(ui, attribute_name)
    with qtbot.waitSignal(spinbox_widget.valueChanged):
        previous = spinbox_widget.value()
        new_value = previous + 1
        spinbox_widget.setValue(new_value)
    assert_that(widget.page_layout, has_property(attribute_name, equal_to(new_value)))


@pytest.mark.parametrize("attribute_name", [
    "draw_cut_markers",
])
def test_boolean_check_boxes(qtbot: QtBot, widget: PageConfigWidget, attribute_name: str):
    ui = widget.ui
    assert_that(ui, has_property(attribute_name, instance_of(QCheckBox)))
    assert_that(widget.page_layout, has_property(attribute_name, instance_of(bool)))
    checkbox_widget: QCheckBox = getattr(ui, attribute_name)
    with qtbot.waitSignal(checkbox_widget.stateChanged):
        previous = checkbox_widget.isChecked()
        new_value = not previous
        checkbox_widget.setChecked(new_value)
    assert_that(checkbox_widget.isChecked(), is_(new_value))
    assert_that(widget.page_layout, has_property(attribute_name, equal_to(new_value)))
    # Test second time to ensure both ways (enable & disable) work
    with qtbot.waitSignal(checkbox_widget.stateChanged):
        previous = checkbox_widget.isChecked()
        new_value = not previous
        checkbox_widget.setChecked(new_value)
    assert_that(widget.page_layout, has_property(attribute_name, equal_to(new_value)))


ZeroMarginsSettings = {
    "paper-height-mm": "297",
    "paper-width-mm": "210",
    "margin-top-mm": "0",
    "margin-bottom-mm": "0",
    "margin-left-mm": "0",
    "margin-right-mm": "0",
    "row-spacing-mm": "0",
    "column-spacing-mm": "0",
}


@pytest.mark.parametrize("value", [-1, 0, 1, 200, 1000])
@pytest.mark.parametrize("settings_name, attribute_name, min_value, max_value", [
    ("paper-height-mm", "page_height", 126, 10000),
    ("paper-width-mm", "page_width", 88, 10000),
    ("margin-top-mm", "margin_top", 0, 171),
    ("margin-bottom-mm", "margin_bottom", 0, 171),
    ("margin-left-mm", "margin_left", 0, 122),
    ("margin-right-mm", "margin_right", 0, 122),
    ("row-spacing-mm", "row_spacing", 0, 10000),
    ("column-spacing-mm", "column_spacing", 0, 10000),
])
def test_load_numerical_document_settings_from_config(
        widget: PageConfigWidget, settings_name: str, attribute_name: str, min_value: int, max_value: int, value: int):
    """
    Tests loading integer settings from config. Some values, like page size, have a minimum value greater than 0,
    to ensure that at least one image fits on a page.
    """
    document_settings = mtg_proxy_printer.settings.settings["documents"]
    page_layout = widget.page_layout
    spinbox_widget: QDoubleSpinBox = getattr(widget.ui, attribute_name)
    with patch.dict(document_settings, ZeroMarginsSettings), \
            patch.dict(document_settings, {settings_name: str(value)}):
        widget.load_document_settings_from_config(mtg_proxy_printer.settings.settings)

    if value < min_value:
        assert_that(spinbox_widget, has_getter("value", equal_to(min_value)))
        assert_that(page_layout, has_property(attribute_name, equal_to(min_value)))
    elif value > max_value:
        assert_that(spinbox_widget, has_getter("value", equal_to(max_value)))
        assert_that(page_layout, has_property(attribute_name, equal_to(max_value)))
    else:
        assert_that(spinbox_widget, has_getter("value", equal_to(value)))
        assert_that(page_layout, has_property(attribute_name, equal_to(value)))


@pytest.mark.parametrize("value", [True, False])
@pytest.mark.parametrize("settings_name, attribute_name", [
    ("print-cut-marker", "draw_cut_markers"),
])
def test_load_boolean_checkboxes_from_config(
        widget: PageConfigWidget, settings_name: str, attribute_name: str, value: bool):
    document_settings = mtg_proxy_printer.settings.settings["documents"]
    with patch.dict(document_settings, {settings_name: str(value)}):
        widget.load_document_settings_from_config(mtg_proxy_printer.settings.settings)
        assert_that(widget.page_layout, has_property(attribute_name, equal_to(value)))
    checkbox_widget: QCheckBox = getattr(widget.ui, attribute_name)
    assert_that(checkbox_widget.isChecked(), is_(equal_to(value)))


@pytest.mark.parametrize("value", [-1, 0, 1, 200, 1000])
@pytest.mark.parametrize("settings_name, attribute_name, min_value, max_value", [
    ("paper-height-mm", "page_height", 126, 10000),
    ("paper-width-mm", "page_width", 88, 10000),
    ("margin-top-mm", "margin_top", 0, 171),
    ("margin-bottom-mm", "margin_bottom", 0, 171),
    ("margin-left-mm", "margin_left", 0, 122),
    ("margin-right-mm", "margin_right", 0, 122),
    ("row-spacing-mm", "row_spacing", 0, 10000),
    ("column-spacing-mm", "column_spacing", 0, 10000),
])
def test_save_numerical_document_settings_to_config(
        qtbot: QtBot,
        widget: PageConfigWidget, settings_name: str, attribute_name: str, min_value: int, max_value: int, value: int):
    """
    Tests loading integer settings from config. Some values, like page size, have a minimum value greater than 0,
    to ensure that at least one image fits on a page.
    """
    document_settings = mtg_proxy_printer.settings.settings["documents"]
    original_value = document_settings[settings_name]
    with patch.dict( document_settings, ZeroMarginsSettings), \
            patch.dict(document_settings, {settings_name: original_value}):
        widget.load_document_settings_from_config(mtg_proxy_printer.settings.settings)
        expected = str(min(max(min_value, value), max_value))
        spinbox_widget: QDoubleSpinBox = getattr(widget.ui, attribute_name)
        spinbox_widget.setValue(value)
        widget.save_document_settings_to_config()
        assert_that(document_settings, has_entry(settings_name, starts_with(expected)))
    assert_that(document_settings, has_entry(settings_name, starts_with(original_value)))


@pytest.mark.parametrize("value", [True, False])
@pytest.mark.parametrize("settings_name, attribute_name", [
    ("print-cut-marker", "draw_cut_markers"),
])
def test_save_boolean_document_settings_to_config(
        widget: PageConfigWidget, settings_name: str, attribute_name: str, value: bool):
    """
    Tests loading integer settings from config. Some values, like page size, have a minimum value greater than 0,
    to ensure that at least one image fits on a page.
    """
    document_settings = mtg_proxy_printer.settings.settings["documents"]
    widget.load_document_settings_from_config(mtg_proxy_printer.settings.settings)
    original_value = document_settings[settings_name]
    with patch.dict(document_settings, {settings_name: original_value}):
        checkbox_widget: QCheckBox = getattr(widget.ui, attribute_name)
        checkbox_widget.setChecked(value)
        widget.save_document_settings_to_config()
        assert_that(document_settings, has_entry(settings_name, equal_to(str(value))))
    assert_that(document_settings, has_entry(settings_name, equal_to(original_value)))


@pytest.mark.parametrize("value", [0, 1, 200, 1000])
@pytest.mark.parametrize("attribute_name, min_value, max_value", [
    ("page_height", 126, 10000),
    ("page_width", 88, 10000),
    ("margin_top", 0, 171),
    ("margin_bottom", 0, 171),
    ("margin_left", 0, 122),
    ("margin_right", 0, 122),
    ("row_spacing", 0, 10000),
    ("column_spacing", 0, 10000),
])
def test_load_numerical_values_from_page_layout(
        widget: PageConfigWidget, attribute_name: str, min_value: int, max_value: int, value: int):
    """
    Tests loading integer settings from config. Some values, like page size, have a minimum value greater than 0,
    to ensure that at least one image fits on a page.
    """
    with patch.dict(mtg_proxy_printer.settings.settings["documents"], ZeroMarginsSettings):
        other = PageLayoutSettings.create_from_settings()
    setattr(other, attribute_name, value)
    expected = min(max(min_value, value), max_value)
    widget.load_from_page_layout(other)
    assert_that(widget.page_layout, has_property(attribute_name, close_to_(expected)))
    spinbox_widget: QDoubleSpinBox = getattr(widget.ui, attribute_name)
    assert_that(spinbox_widget.value(), is_(close_to_(expected)))


@pytest.mark.parametrize("value", [True, False])
@pytest.mark.parametrize("attribute_name", [
    "draw_cut_markers",
])
def test_load_booleans_from_page_layout(widget: PageConfigWidget, attribute_name: str, value: bool):
    other = PageLayoutSettings.create_from_settings()
    setattr(other, attribute_name, value)
    widget.load_from_page_layout(other)
    assert_that(widget.page_layout, has_property(attribute_name, equal_to(value)))
    checkbox_widget: QCheckBox = getattr(widget.ui, attribute_name)
    assert_that(checkbox_widget.isChecked(), is_(equal_to(value)))


def test_flip_page_dimensions_button(widget: PageConfigWidget):
    widget.load_from_page_layout(PageLayoutSettings.create_from_settings())
    assert_that(widget.page_layout, has_properties({
        "page_height": equal_to(297),
        "page_width": equal_to(210),
    }), "Setup failed")
    widget.ui.flip_page_dimensions.click()

    assert_that(widget.page_layout, has_properties({
        "page_height": equal_to(210),
        "page_width": equal_to(297),
    }), "Values not correctly flipped")


def test_flip_page_dimensions_updates_capacity(widget: PageConfigWidget):
    widget.load_from_page_layout(PageLayoutSettings.create_from_settings())
    assert_that(widget.page_layout, has_properties({
        "page_height": equal_to(297),
        "page_width": equal_to(210),
    }), "Setup failed")
    widget.ui.flip_page_dimensions.click()
    assert_that(widget.ui.page_capacity, has_getter("text", all_of(
        contains_string("8"),
        contains_string("3"),
    )))
    widget.ui.flip_page_dimensions.click()
    assert_that(widget.ui.page_capacity, has_getter("text", all_of(
        contains_string("9"),
        contains_string("4"),
    )))


def test_page_capacity_updates_correctly(widget: PageConfigWidget):
    widget.load_from_page_layout(PageLayoutSettings.create_from_settings())
    page_layout = widget.page_layout
    row_spacing = widget.ui.row_spacing
    page_capacity = widget.ui.page_capacity

    row_spacing.setValue(11)
    assert_that(page_layout.compute_page_card_capacity(), is_(9))
    assert_that(page_capacity, has_getter("text", contains_string("9")))

    row_spacing.setValue(12)
    assert_that(page_layout.compute_page_card_capacity(), is_(6))
    assert_that(page_capacity, has_getter("text", contains_string("6")))

    row_spacing.setValue(11)
    assert_that(page_layout.compute_page_card_capacity(), is_(9))
    assert_that(page_capacity, has_getter("text", contains_string("9")))
