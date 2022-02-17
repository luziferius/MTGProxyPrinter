# Copyright (C) 2020-2022 Thomas Hess <thomas.hess@udo.edu>

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

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QGroupBox, QWidget, QSpinBox, QLabel, QCheckBox

import mtg_proxy_printer.settings
from mtg_proxy_printer.ui.common import inherits_from_ui_file_with_name
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.document_loader import PageLayoutSettings
from mtg_proxy_printer.units_and_sizes import IMAGE_WIDTH, IMAGE_HEIGHT


class PageConfigWidget(inherits_from_ui_file_with_name("page_config_widget")[0], QGroupBox):
    def __init__(self, parent: QWidget = None):
        super(PageConfigWidget, self).__init__(parent)
        self.setupUi(self)
        self.page_layout = self._setup_page_layout()

    def _setup_page_layout(self) -> PageLayoutSettings:
        # Implementation note: The signal connections below will also trigger
        # when programmatically populating the widget values.
        # Therefore, it is not necessary to ever explicitly set the page_layout
        # attributes to the current values.
        page_layout = PageLayoutSettings()
        self.page_height.valueChanged[int].connect(
            lambda new: setattr(page_layout, "page_height", new))
        self.page_width.valueChanged[int].connect(
            lambda new: setattr(page_layout, "page_width", new))
        self.margin_top.valueChanged[int].connect(
            lambda new: setattr(page_layout, "margin_top", new))
        self.margin_bottom.valueChanged[int].connect(
            lambda new: setattr(page_layout, "margin_bottom", new))
        self.margin_left.valueChanged[int].connect(
            lambda new: setattr(page_layout, "margin_left", new))
        self.margin_right.valueChanged[int].connect(
            lambda new: setattr(page_layout, "margin_right", new))
        self.image_spacing_horizontal.valueChanged[int].connect(
            lambda new: setattr(page_layout, "image_spacing_horizontal", new))
        self.image_spacing_vertical.valueChanged[int].connect(
            lambda new: setattr(page_layout, "image_spacing_vertical", new))
        self.draw_cut_markers: QCheckBox
        self.draw_cut_markers.stateChanged.connect(
            lambda new: setattr(page_layout, "draw_cut_markers", new == Qt.Checked))
        return page_layout

    @pyqtSlot()
    def on_page_layout_setting_changed(self):
        """
        Recomputes and updates the page capacity value, whenever any page layout widget changes.
        Qt Signal/Slot connections from editor widgets valueChanged[int] signals are defined in the UI file.
        """
        self.page_capacity: QLabel
        new_capacity = self.page_layout.compute_page_card_capacity()
        self.page_capacity.setText(str(new_capacity))

    @pyqtSlot()
    def validate_paper_size_settings(self):
        """
        Recomputes and updates the minimum page size, whenever any page layout widget changes.
        Qt Signal/Slot connections from editor widgets valueChanged[int] signals are defined in the UI file.
        """
        pl = self.page_layout
        min_page_height = pl.margin_bottom + pl.margin_top + IMAGE_HEIGHT.to_tuple()[0]
        min_page_width = pl.margin_left + pl.margin_right + IMAGE_WIDTH.to_tuple()[0]
        self.page_height: QSpinBox
        self.page_width: QSpinBox
        self.page_height.setMinimum(min_page_height)
        self.page_width.setMinimum(min_page_width)

    def load_document_settings_from_config(self, settings: configparser.ConfigParser):
        document_section = settings["documents"]
        widgets_with_settings = self._get_document_settings_widgets()
        for widget, setting in widgets_with_settings:
            widget.setValue(document_section.getint(setting))
        self.draw_cut_markers.setChecked(document_section.getboolean("print-cut-marker"))

    def save_document_settings_to_config(self):
        documents_section = mtg_proxy_printer.settings.settings["documents"]
        widgets_and_settings = self._get_document_settings_widgets()
        for widget, setting in widgets_and_settings:
            documents_section[setting] = str(widget.value())
        documents_section["print-cut-marker"] = str(self.draw_cut_markers.isChecked())

    def _get_document_settings_widgets(self):
        widgets_with_settings: typing.List[typing.Tuple[QSpinBox, str]] = [
            (self.page_height, "paper-height-mm"),
            (self.page_width, "paper-width-mm"),
            (self.margin_top, "margin-top-mm"),
            (self.margin_bottom, "margin-bottom-mm"),
            (self.margin_left, "margin-left-mm"),
            (self.margin_right, "margin-right-mm"),
            (self.image_spacing_horizontal, "image-spacing-horizontal-mm"),
            (self.image_spacing_vertical, "image-spacing-vertical-mm"),
        ]
        return widgets_with_settings
