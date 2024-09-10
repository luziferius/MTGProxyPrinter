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

from unittest.mock import patch

import pint
from PyQt5.QtWidgets import QDoubleSpinBox, QCheckBox

from hamcrest import *
import pytest
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.model.document_loader import PageLayoutSettings
import mtg_proxy_printer.settings
from mtg_proxy_printer.ui.page_config_widget import PageConfigWidget
from mtg_proxy_printer.units_and_sizes import unit_registry, UnitT, QuantityT

from tests.hasgetter import has_getter
from tests.helpers import quantity_close_to, quantity_between, number_between, close_to_
mm: UnitT = unit_registry.mm

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
    assert_that(widget.page_layout, has_property(attribute_name, instance_of(pint.Quantity)))
    spinbox_widget: QDoubleSpinBox = getattr(ui, attribute_name)
    with qtbot.waitSignal(spinbox_widget.valueChanged):
        previous = spinbox_widget.value()
        new_value = previous + 1
        spinbox_widget.setValue(new_value)
    assert_that(widget.page_layout, has_property(attribute_name, quantity_close_to(new_value*mm)))


@pytest.mark.parametrize("attribute_name", [
    "draw_cut_markers",
    "draw_sharp_corners",
    "draw_page_numbers",
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
    "paper-height": "297 mm",
    "paper-width": "210 mm",
    "margin-top": "0 mm",
    "margin-bottom": "0 mm",
    "margin-left": "0 mm",
    "margin-right": "0 mm",
    "row-spacing": "0 mm",
    "column-spacing": "0 mm",
}


@pytest.mark.parametrize("value", [-1*mm, 0*mm, 1*mm, 200*mm, 1000*mm])
@pytest.mark.parametrize("settings_name, attribute_name, min_value, max_value", [
    ("paper-height", "page_height", 126*mm, 10000*mm),
    ("paper-width", "page_width", 88*mm, 10000*mm),
    ("margin-top", "margin_top", 0*mm, 170.85*mm),
    ("margin-bottom", "margin_bottom", 0*mm, 170.85*mm),
    ("margin-left", "margin_left", 0*mm, 121.95*mm),
    ("margin-right", "margin_right", 0*mm, 121.95*mm),
    ("row-spacing", "row_spacing", 0*mm, 10000*mm),
    ("column-spacing", "column_spacing", 0*mm, 10000*mm),
])
def test_load_numerical_document_settings_from_config(
        widget: PageConfigWidget, settings_name: str, attribute_name: str,
        min_value: QuantityT, max_value: QuantityT, value: QuantityT):
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
        assert_that(spinbox_widget, has_getter("value", close_to_(min_value.magnitude)))
        assert_that(page_layout, has_property(attribute_name, quantity_close_to(min_value)))
    elif value > max_value:
        assert_that(spinbox_widget, has_getter("value", close_to_(max_value.magnitude)))
        assert_that(page_layout, has_property(attribute_name, quantity_close_to(max_value)))
    else:
        assert_that(spinbox_widget, has_getter("value", close_to_(value.magnitude)))
        assert_that(page_layout, has_property(attribute_name, quantity_close_to(value)))


@pytest.mark.parametrize("value", [True, False])
@pytest.mark.parametrize("settings_name, attribute_name", [
    ("print-cut-marker", "draw_cut_markers",),
    ("print-sharp-corners", "draw_sharp_corners"),
    ("print-page-numbers", "draw_page_numbers"),
])
def test_load_boolean_checkboxes_from_config(
        widget: PageConfigWidget, settings_name: str, attribute_name: str, value: bool):
    document_settings = mtg_proxy_printer.settings.settings["documents"]
    with patch.dict(document_settings, {settings_name: str(value)}):
        widget.load_document_settings_from_config(mtg_proxy_printer.settings.settings)
        assert_that(widget.page_layout, has_property(attribute_name, equal_to(value)))
    checkbox_widget: QCheckBox = getattr(widget.ui, attribute_name)
    assert_that(checkbox_widget.isChecked(), is_(equal_to(value)))


@pytest.mark.parametrize("value", [-1*mm, 0*mm, 1*mm, 200*mm, 1000*mm])
@pytest.mark.parametrize("settings_name, attribute_name, min_value, max_value", [
    ("paper-height", "page_height", 126*mm, 10000*mm),
    ("paper-width", "page_width", 88*mm, 10000*mm),
    ("margin-top", "margin_top", 0*mm, 170.85*mm),
    ("margin-bottom", "margin_bottom", 0*mm, 170.85*mm),
    ("margin-left", "margin_left", 0*mm, 121.95*mm),
    ("margin-right", "margin_right", 0*mm, 121.95*mm),
    ("row-spacing", "row_spacing", 0*mm, 10000*mm),
    ("column-spacing", "column_spacing", 0*mm, 10000*mm),
])
def test_save_numerical_document_settings_to_config(
        qtbot: QtBot,
        widget: PageConfigWidget, settings_name: str, attribute_name: str,
        min_value: QuantityT, max_value: QuantityT, value: QuantityT):
    """
    Tests loading integer settings from config. Some values, like page size, have a minimum value greater than 0,
    to ensure that at least one image fits on a page.
    """
    document_settings = mtg_proxy_printer.settings.settings["documents"]
    original_value = document_settings[settings_name]
    with patch.dict( document_settings, ZeroMarginsSettings), \
            patch.dict(document_settings, {settings_name: original_value}):
        widget.load_document_settings_from_config(mtg_proxy_printer.settings.settings)
        expected = min(max(min_value, value), max_value)
        spinbox_widget: QDoubleSpinBox = getattr(widget.ui, attribute_name)
        spinbox_widget.setValue(value.magnitude)
        widget.save_document_settings_to_config()
        assert_that(document_settings.get_quantity(settings_name), quantity_close_to(expected))

    assert_that(document_settings, has_entry(settings_name, starts_with(original_value)))


@pytest.mark.parametrize("value", [True, False])
@pytest.mark.parametrize("settings_name, attribute_name", [
    ("print-cut-marker", "draw_cut_markers",),
    ("print-sharp-corners", "draw_sharp_corners"),
    ("print-page-numbers", "draw_page_numbers"),
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


@pytest.mark.parametrize("value", [0*mm, 1*mm, 200*mm, 1000*mm])
@pytest.mark.parametrize("attribute_name, min_value, max_value", [
    ("page_height", 126*mm, 10000*mm),
    ("page_width", 88*mm, 10000*mm),
    ("margin_top", 0*mm, 170.85*mm),
    ("margin_bottom", 0*mm, 170.85*mm),
    ("margin_left", 0*mm, 121.95*mm),
    ("margin_right", 0*mm, 121.95*mm),
    ("row_spacing", 0*mm, 10000*mm),
    ("column_spacing", 0*mm, 10000*mm),
])
def test_load_numerical_values_from_page_layout(
        widget: PageConfigWidget, attribute_name: str, min_value: QuantityT, max_value: QuantityT, value: QuantityT):
    """
    Tests loading integer settings from config. Some values, like page size, have a minimum value greater than 0,
    to ensure that at least one image fits on a page.
    """
    with patch.dict(mtg_proxy_printer.settings.settings["documents"], ZeroMarginsSettings):
        other = PageLayoutSettings.create_from_settings()
    setattr(other, attribute_name, value)
    widget.load_from_page_layout(other)
    assert_that(widget.page_layout, has_property(attribute_name, quantity_between(min_value, max_value)))
    spinbox_widget: QDoubleSpinBox = getattr(widget.ui, attribute_name)
    assert_that(spinbox_widget.value(), is_(number_between(min_value.magnitude, max_value.magnitude)))
    assert_that(spinbox_widget.value(), close_to_(getattr(widget.page_layout, attribute_name).magnitude))


@pytest.mark.parametrize("value", [True, False])
@pytest.mark.parametrize("attribute_name", [
    "draw_cut_markers",
    "draw_sharp_corners",
    "draw_page_numbers",
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
        "page_height": equal_to(297*mm),
        "page_width": equal_to(210*mm),
    }), "Setup failed")
    widget.ui.flip_page_dimensions.click()

    assert_that(widget.page_layout, has_properties({
        "page_height": equal_to(210*mm),
        "page_width": equal_to(297*mm),
    }), "Values not correctly flipped")


def test_flip_page_dimensions_updates_capacity(widget: PageConfigWidget):
    widget.load_from_page_layout(PageLayoutSettings.create_from_settings())
    assert_that(widget.page_layout, has_properties({
        "page_height": equal_to(297*mm),
        "page_width": equal_to(210*mm),
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
