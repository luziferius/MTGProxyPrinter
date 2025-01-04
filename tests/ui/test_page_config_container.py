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

from PyQt5.QtWidgets import QCheckBox, QDoubleSpinBox, QLineEdit

import pytest
from pytestqt.qtbot import QtBot
from hamcrest import *

from mtg_proxy_printer.model.document_loader import PageLayoutSettings
from mtg_proxy_printer.units_and_sizes import QuantityT, unit_registry
from mtg_proxy_printer.ui.page_config_container import PageConfigContainer

from tests.helpers import quantity_close_to


@pytest.fixture
def container(qtbot: QtBot):
    container = PageConfigContainer()
    container.ui.page_config_widget.load_from_page_layout(PageLayoutSettings.create_from_settings())
    qtbot.add_widget(container)
    return container


@pytest.mark.parametrize(
    "widget_name",
    ["draw_cut_markers", "draw_sharp_corners", "draw_page_numbers"])
def test_boolean_settings_change_signal_connection_from_config_widget_to_preview_area(
        qtbot: QtBot, container: PageConfigContainer, widget_name: str):
    page_config_widget = container.ui.page_config_widget
    document = container.ui.page_config_preview_area.document
    widget: QCheckBox = getattr(page_config_widget.ui, widget_name)
    original_state: bool = getattr(document.page_layout, widget_name)

    with qtbot.wait_signal(page_config_widget.page_layout_changed, timeout=100):
        widget.toggle()
    assert_that(getattr(document.page_layout, widget_name), is_(not original_state))

    with qtbot.wait_signal(page_config_widget.page_layout_changed, timeout=100):
        widget.toggle()
    assert_that(getattr(document.page_layout, widget_name), is_(original_state))


@pytest.mark.parametrize(
    "widget_name",[
         "card_bleed",
         "custom_page_height", "custom_page_width",
         "margin_top", "margin_bottom", "margin_left", "margin_right",
         "row_spacing", "column_spacing",
     ])
def test_decimal_settings_change_signal_connection_from_config_widget_to_preview_area(
        qtbot: QtBot, container: PageConfigContainer, widget_name: str):
    page_config_widget = container.ui.page_config_widget
    document = container.ui.page_config_preview_area.document
    widget: QDoubleSpinBox = getattr(page_config_widget.ui, widget_name)
    original_value: QuantityT = getattr(document.page_layout, widget_name)
    diff: QuantityT = 1*unit_registry.mm

    with qtbot.wait_signal(page_config_widget.page_layout_changed, timeout=100):
        widget.setValue((original_value+diff).magnitude)
    assert_that(
        getattr(document.page_layout, widget_name),
        is_(quantity_close_to(original_value + diff)),
        f"Failing widget: {widget_name}")

    with qtbot.wait_signal(page_config_widget.page_layout_changed, timeout=100):
        widget.setValue(original_value.magnitude)
    assert_that(
        getattr(document.page_layout, widget_name),
        is_(quantity_close_to(original_value)),
        f"Failing widget: {widget_name}")


@pytest.mark.parametrize(
    "widget_name",[
         "document_name",
     ])
def test_textual_settings_change_signal_connection_from_config_widget_to_preview_area(
        qtbot: QtBot, container: PageConfigContainer, widget_name: str):
    page_config_widget = container.ui.page_config_widget
    document = container.ui.page_config_preview_area.document
    widget: QLineEdit = getattr(page_config_widget.ui, widget_name)
    original_value: str = getattr(document.page_layout, widget_name)
    new_value = "Test"

    with qtbot.wait_signal(page_config_widget.page_layout_changed, timeout=100):
        widget.setText(new_value)
    assert_that(
        getattr(document.page_layout, widget_name),
        is_(new_value),
        f"Failing widget: {widget_name}")

    with qtbot.wait_signal(page_config_widget.page_layout_changed, timeout=100):
        widget.setText(original_value)
    assert_that(
        getattr(document.page_layout, widget_name),
        is_(original_value),
        f"Failing widget: {widget_name}")
