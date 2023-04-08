# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>

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
from functools import partial
import typing

from PyQt5.QtCore import pyqtSlot as Slot, Qt
from PyQt5.QtWidgets import QGroupBox, QWidget, QSpinBox, QCheckBox

import mtg_proxy_printer.settings
from mtg_proxy_printer.ui.common import load_ui_from_file, BlockedSignals
from mtg_proxy_printer.model.document_loader import PageLayoutSettings
from mtg_proxy_printer.units_and_sizes import CardSizes, CardSize

try:
    from mtg_proxy_printer.ui.generated.page_config_widget import Ui_page_configuration_group_box as Ui_PageConfigWidget
except ModuleNotFoundError:
    Ui_PageConfigWidget = load_ui_from_file("page_config_widget")

from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger


class PageConfigWidget(QGroupBox):
    def __init__(self, parent: QWidget = None):
        super(PageConfigWidget, self).__init__(parent)
        self.ui = Ui_PageConfigWidget()
        self.ui.setupUi(self)
        self.page_layout = self._setup_page_layout()
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _setup_page_layout(self) -> PageLayoutSettings:
        # Implementation note: The signal connections below will also trigger
        # when programmatically populating the widget values.
        # Therefore, it is not necessary to ever explicitly set the page_layout
        # attributes to the current values.
        page_layout = PageLayoutSettings()
        self.ui.page_height.valueChanged[int].connect(partial(setattr, page_layout, "page_height"))
        self.ui.page_width.valueChanged[int].connect(partial(setattr, page_layout, "page_width"))
        self.ui.margin_top.valueChanged[int].connect(partial(setattr, page_layout, "margin_top"))
        self.ui.margin_bottom.valueChanged[int].connect(partial(setattr, page_layout, "margin_bottom"))
        self.ui.margin_left.valueChanged[int].connect(partial(setattr, page_layout, "margin_left"))
        self.ui.margin_right.valueChanged[int].connect(partial(setattr, page_layout, "margin_right"))
        self.ui.image_spacing_horizontal.valueChanged[int].connect(
            partial(setattr, page_layout, "image_spacing_horizontal"))
        self.ui.image_spacing_vertical.valueChanged[int].connect(partial(setattr, page_layout, "image_spacing_vertical"))
        self.ui.draw_cut_markers.stateChanged.connect(
            lambda new: setattr(page_layout, "draw_cut_markers", new == Qt.Checked))
        self.ui.draw_sharp_corners.stateChanged.connect(
            lambda new: setattr(page_layout, "draw_sharp_corners", new == Qt.Checked))
        return page_layout

    @Slot()
    def page_layout_setting_changed(self):
        """
        Recomputes and updates the page capacity value, whenever any page layout widget changes.
        Qt Signal/Slot connections from editor widgets valueChanged[int] signals are defined in the UI file.
        """
        new_capacity = self.page_layout.compute_page_card_capacity()
        self.ui.page_capacity.setText(str(new_capacity))

    @Slot()
    def validate_paper_size_settings(self):
        """
        Recomputes and updates the minimum page size, whenever any page layout widget changes.
        Qt Signal/Slot connections from editor widgets valueChanged[int] signals are defined in the UI file.
        """
        oversized = CardSizes.OVERSIZED
        pl = self.page_layout
        min_page_height = pl.margin_bottom + pl.margin_top + oversized.as_mm(oversized.height)
        min_page_width = pl.margin_left + pl.margin_right + oversized.as_mm(oversized.width)
        self.ui.page_height.setMinimum(min_page_height)
        self.ui.page_width.setMinimum(min_page_width)

    def load_document_settings_from_config(self, settings: configparser.ConfigParser):
        logger.debug(f"About to load document settings from the global settings")
        document_section = settings["documents"]
        for spinbox, setting in self._get_integer_settings_widgets():
            spinbox.setValue(document_section.getint(setting))
        for checkbox, setting in self._get_boolean_settings_widgets():
            checkbox.setChecked(document_section.getboolean(setting))
        logger.debug(f"Loading from settings finished")

    def load_from_page_layout(self, other: PageLayoutSettings):
        """Loads the page layout from another PageLayoutSettings instance"""
        logger.debug(f"About to load document settings from a document instance")
        ui = self.ui
        layout = self.page_layout
        for key in layout.__annotations__.keys():
            value = getattr(other, key)
            setattr(self.page_layout, key, value)
            widget = getattr(ui, key)
            with BlockedSignals(widget):  # Don’t call the validation methods in each iteration
                if isinstance(widget, QSpinBox):
                    widget.setValue(value)
                else:
                    widget.setChecked(value)
        self.validate_paper_size_settings()
        self.page_layout_setting_changed()
        logger.debug(f"Loading from document settings finished")

    def save_document_settings_to_config(self):
        logger.info("About to save document settings to the global settings")
        documents_section = mtg_proxy_printer.settings.settings["documents"]
        for spinbox, setting in self._get_integer_settings_widgets():
            documents_section[setting] = str(spinbox.value())
        for checkbox, setting in self._get_boolean_settings_widgets():
            documents_section[setting] = str(checkbox.isChecked())
        logger.debug("Saving done.")

    def _get_integer_settings_widgets(self):
        widgets_with_settings: typing.List[typing.Tuple[QSpinBox, str]] = [
            (self.ui.page_height, "paper-height-mm"),
            (self.ui.page_width, "paper-width-mm"),
            (self.ui.margin_top, "margin-top-mm"),
            (self.ui.margin_bottom, "margin-bottom-mm"),
            (self.ui.margin_left, "margin-left-mm"),
            (self.ui.margin_right, "margin-right-mm"),
            (self.ui.image_spacing_horizontal, "image-spacing-horizontal-mm"),
            (self.ui.image_spacing_vertical, "image-spacing-vertical-mm"),
        ]
        return widgets_with_settings

    def _get_boolean_settings_widgets(self):
        widgets_with_settings: typing.List[typing.Tuple[QCheckBox, str]] = [
            (self.ui.draw_cut_markers, "print-cut-marker"),
            (self.ui.draw_sharp_corners, "print-sharp-corners"),
        ]
        return widgets_with_settings
