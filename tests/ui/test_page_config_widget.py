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

from PyQt5.QtWidgets import QSpinBox, QCheckBox

from hamcrest import *
import pytest
from pytestqt.qtbot import QtBot

import mtg_proxy_printer.ui.page_config_widget


@pytest.mark.parametrize("attribute_name", [
    "page_height",
    "page_width",
    "margin_top",
    "margin_bottom",
    "margin_left",
    "margin_right",
    "image_spacing_horizontal",
    "image_spacing_vertical",
])
def test_set_integer_spin_boxes(qtbot: QtBot, attribute_name: str):
    widget = mtg_proxy_printer.ui.page_config_widget.PageConfigWidget()
    qtbot.addWidget(widget)
    assert_that(widget, has_property(attribute_name, instance_of(QSpinBox)))
    assert_that(widget.page_layout, has_property(attribute_name, instance_of(int)))
    spinbox_widget: QSpinBox = getattr(widget, attribute_name)
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
    qtbot.addWidget(widget)
    assert_that(widget, has_property(attribute_name, instance_of(QCheckBox)))
    assert_that(widget.page_layout, has_property(attribute_name, instance_of(bool)))
    checkbox_widget: QCheckBox = getattr(widget, attribute_name)
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
