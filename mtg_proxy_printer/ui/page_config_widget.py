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

import configparser
import functools
from functools import partial
from typing import List, Tuple

from PyQt5.QtCore import pyqtSlot as Slot, Qt
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtGui import QPageSize, QPageLayout
from PyQt5.QtWidgets import QGroupBox, QWidget, QSpinBox, QCheckBox, QLineEdit, QComboBox


from mtg_proxy_printer.settings import settings, PageSize, PageSizeReverse, PageOrientation, PageOrientationReverse
from mtg_proxy_printer.ui.common import load_ui_from_file, BlockedSignals, highlight_widget
from mtg_proxy_printer.model.document_loader import PageLayoutSettings
from mtg_proxy_printer.units_and_sizes import CardSizes, PageType

try:
    from mtg_proxy_printer.ui.generated.page_config_widget import Ui_PageConfigWidget
except ModuleNotFoundError:
    Ui_PageConfigWidget = load_ui_from_file("page_config_widget")

from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger
CheckState = Qt.CheckState


class PageConfigWidget(QGroupBox):

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = ui = Ui_PageConfigWidget()
        ui.setupUi(self)
        self.page_layout = self._setup_page_layout(ui)
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _setup_page_layout(self, ui: Ui_PageConfigWidget) -> PageLayoutSettings:
        # Implementation note: The signal connections below will also trigger
        # when programmatically populating the widget values.
        # Therefore, it is not necessary to ever explicitly set the page_layout
        # attributes to the current values.
        page_layout = PageLayoutSettings()
        for item, value in PageSize.items():
            ui.paper_size.addItem(item, value)
        for item, value in PageOrientation.items():
            ui.paper_orientation.addItem(item, value)

        ui.paper_size.currentIndexChanged.connect(self._on_paper_size_changed)
        ui.paper_size.currentIndexChanged.connect(self.validate_paper_size_settings)
        ui.paper_size.currentIndexChanged.connect(self.page_layout_setting_changed)

        ui.paper_orientation.currentIndexChanged.connect(self._on_paper_orientation_changed)
        ui.paper_orientation.currentIndexChanged.connect(self.validate_paper_size_settings)
        ui.paper_orientation.currentIndexChanged.connect(self.page_layout_setting_changed)

        ui.card_bleed.valueChanged[int].connect(partial(setattr, page_layout, "card_bleed"))
        ui.custom_page_height.valueChanged[int].connect(partial(setattr, page_layout, "custom_page_height"))
        ui.custom_page_width.valueChanged[int].connect(partial(setattr, page_layout, "custom_page_width"))
        ui.margin_top.valueChanged[int].connect(partial(setattr, page_layout, "margin_top"))
        ui.margin_bottom.valueChanged[int].connect(partial(setattr, page_layout, "margin_bottom"))
        ui.margin_left.valueChanged[int].connect(partial(setattr, page_layout, "margin_left"))
        ui.margin_right.valueChanged[int].connect(partial(setattr, page_layout, "margin_right"))
        ui.row_spacing.valueChanged[int].connect(partial(setattr, page_layout, "row_spacing"))
        ui.column_spacing.valueChanged[int].connect(partial(setattr, page_layout, "column_spacing"))

        for spinbox in (
                ui.custom_page_height, ui.custom_page_width,
                ui.margin_top, ui.margin_left, ui.margin_bottom, ui.margin_right,
                ui.row_spacing, ui.column_spacing):
            spinbox.valueChanged[int].connect(self.validate_paper_size_settings)
            spinbox.valueChanged[int].connect(self.page_layout_setting_changed)
        ui.draw_cut_markers.stateChanged.connect(
            lambda new: setattr(page_layout, "draw_cut_markers", new == CheckState.Checked))
        ui.draw_sharp_corners.stateChanged.connect(
            lambda new: setattr(page_layout, "draw_sharp_corners", new == CheckState.Checked))
        ui.draw_page_numbers.stateChanged.connect(
            lambda new: setattr(page_layout, "draw_page_numbers", new == CheckState.Checked))
        ui.document_name.textChanged.connect(partial(setattr, page_layout, "document_name"))
        return page_layout

    @Slot(int)
    def _on_paper_size_changed(self, index: int):
        ui = self.ui
        ui.paper_orientation.setEnabled(index)
        ui.custom_page_width.setDisabled(index)
        ui.custom_page_height.setDisabled(index)
        ui.flip_page_dimensions.setDisabled(index)
        selected_paper_size_item: QPageSize.PageSizeId = ui.paper_size.currentData(Qt.ItemDataRole.UserRole)
        self.page_layout.paper_size = PageSizeReverse[selected_paper_size_item]

    @Slot()
    def _on_paper_orientation_changed(self):
        ui = self.ui
        orientation: QPageLayout.Orientation = ui.paper_orientation.currentData(Qt.ItemDataRole.UserRole)
        self.page_layout.paper_orientation = PageOrientationReverse[orientation]

    @Slot()
    def page_layout_setting_changed(self):
        """
        Recomputes and updates the page capacity display, whenever any page layout widget changes.
        """
        regular_capacity = self.page_layout.compute_page_card_capacity(PageType.REGULAR)
        oversized_capacity = self.page_layout.compute_page_card_capacity(PageType.OVERSIZED)
        capacity_text = f"{regular_capacity} regular cards, {oversized_capacity} oversized cards"
        self.ui.page_capacity.setText(capacity_text)

    @Slot()
    def on_flip_page_dimensions_clicked(self):
        """Toggles between landscape/portrait mode by flipping the page height and page width values."""
        logger.debug("User flips paper dimensions")
        ui = self.ui
        width = ui.custom_page_width.value()
        ui.custom_page_width.setValue(ui.custom_page_height.value())
        ui.custom_page_height.setValue(width)

    @Slot()
    def validate_paper_size_settings(self):
        """
        Recomputes and updates the minimum page size, whenever any page layout widget changes.
        """
        ui = self.ui
        oversized = CardSizes.OVERSIZED
        available_width = ui.custom_page_width.value() - oversized.as_mm(oversized.width)
        available_height = ui.custom_page_height.value() - oversized.as_mm(oversized.height)
        ui.margin_left.setMaximum(
            max(0, available_width - ui.margin_right.value())
        )
        ui.margin_right.setMaximum(
            max(0, available_width - ui.margin_left.value())
        )
        ui.margin_top.setMaximum(
            max(0, available_height - ui.margin_bottom.value())
        )
        ui.margin_bottom.setMaximum(
            max(0, available_height - ui.margin_top.value())
        )

    def load_document_settings_from_config(self, settings: configparser.ConfigParser):
        logger.debug(f"About to load document settings from the global settings")
        documents_section = settings["documents"]
        for spinbox, setting in self._get_integer_settings_widgets():
            value = documents_section.getint(setting)
            spinbox.setValue(value)
            setattr(self.page_layout, spinbox.objectName(), spinbox.value())
        for checkbox, setting in self._get_boolean_settings_widgets():
            checkbox.setChecked(documents_section.getboolean(setting))
        for line_edit, setting in self._get_string_settings_widgets():
            line_edit.setText(documents_section[setting])
        self._load_paper_size(documents_section["paper-size"])
        self._load_paper_orientation(documents_section["paper-orientation"])
        self.validate_paper_size_settings()
        self.page_layout_setting_changed()
        logger.debug(f"Loading from settings finished")

    def load_from_page_layout(self, other: PageLayoutSettings):
        """Loads the page layout from another PageLayoutSettings instance"""
        logger.debug(f"About to load document settings from a document instance")
        ui = self.ui
        layout = self.page_layout
        for key in layout.__annotations__.keys():
            value = getattr(other, key)
            widget = getattr(ui, key)
            with BlockedSignals(widget):  # Don’t call the validation methods in each iteration
                if isinstance(widget, QSpinBox):
                    widget.setValue(value)
                    setattr(self.page_layout, key, widget.value())
                elif isinstance(widget, QLineEdit):
                    widget.setText(value)
                    setattr(self.page_layout, key, widget.text())
                elif isinstance(widget, QComboBox):
                    pass
                else:
                    widget.setChecked(value)
                    setattr(self.page_layout, key, widget.isChecked())
        self._load_paper_size(other.paper_size)
        self._load_paper_orientation(other.paper_orientation)
        self.validate_paper_size_settings()
        self.page_layout_setting_changed()
        logger.debug(f"Loading from document settings finished")

    def _load_paper_size(self, size: str):
        page_size = PageSize[size]
        combo_box = self.ui.paper_size
        model = combo_box.model()
        for row in range(model.rowCount()):
            if model.data(model.index(row, 0), Qt.ItemDataRole.UserRole) == page_size:
                combo_box.setCurrentIndex(row)
                break

    def _load_paper_orientation(self, orientation_str: str):
        orientation = PageOrientation[orientation_str]
        combo_box = self.ui.paper_orientation
        model = combo_box.model()
        for row in range(model.rowCount()):
            if model.data(model.index(row, 0), Qt.ItemDataRole.UserRole) == orientation:
                combo_box.setCurrentIndex(row)
                break

    def save_document_settings_to_config(self):
        logger.info("About to save document settings to the global settings")
        documents_section = settings["documents"]
        for spinbox, setting in self._get_integer_settings_widgets():
            documents_section[setting] = str(spinbox.value())
        for checkbox, setting in self._get_boolean_settings_widgets():
            documents_section[setting] = str(checkbox.isChecked())
        for line_edit, setting in self._get_string_settings_widgets():
            documents_section[setting] = line_edit.text()
        documents_section["paper-size"] = PageSizeReverse[self._current_page_size()]
        documents_section["paper-orientation"] = PageOrientationReverse[self._current_page_orientation()]
        logger.debug("Saving done.")

    def _get_integer_settings_widgets(self):
        ui = self.ui
        widgets_with_settings: List[Tuple[QSpinBox, str]] = [
            (ui.card_bleed, "card-bleed-mm"),
            (ui.custom_page_height, "paper-height-mm"),
            (ui.custom_page_width, "paper-width-mm"),
            (ui.margin_top, "margin-top-mm"),
            (ui.margin_bottom, "margin-bottom-mm"),
            (ui.margin_left, "margin-left-mm"),
            (ui.margin_right, "margin-right-mm"),
            (ui.row_spacing, "row-spacing-mm"),
            (ui.column_spacing, "column-spacing-mm"),
        ]
        return widgets_with_settings

    def _get_boolean_settings_widgets(self):
        ui = self.ui
        widgets_with_settings: List[Tuple[QCheckBox, str]] = [
            (ui.draw_cut_markers, "print-cut-marker"),
            (ui.draw_sharp_corners, "print-sharp-corners"),
            (ui.draw_page_numbers, "print-page-numbers"),
        ]
        return widgets_with_settings

    def _get_string_settings_widgets(self):
        ui = self.ui
        widgets_with_settings: List[Tuple[QLineEdit, str]] = [
            (ui.document_name, "default-document-name"),
        ]
        return widgets_with_settings

    def _current_page_size(self) -> QPrinter.PageSize:
        return self.ui.paper_size.currentData(Qt.ItemDataRole.UserRole)

    def _current_page_orientation(self) -> QPageLayout.Orientation:
        return self.ui.paper_orientation.currentData(Qt.ItemDataRole.UserRole)

    @functools.singledispatchmethod
    def highlight_differing_settings(self, settings):
        pass

    @highlight_differing_settings.register
    def _(self, settings: configparser.ConfigParser):
        section = settings["documents"]
        for widget, setting in self._get_string_settings_widgets():
            if widget.text() != section[setting]:
                highlight_widget(widget)
        for widget, setting in self._get_boolean_settings_widgets():
            if widget.isChecked() is not section.getboolean(setting):
                highlight_widget(widget)
        for widget, setting in self._get_integer_settings_widgets():
            if widget.value() != section.getint(setting):
                highlight_widget(widget)
        if self._current_page_size() != PageSize[section["paper-size"]]:
            highlight_widget(self.ui.paper_size)
        if self._current_page_orientation() != PageOrientation[section["paper-orientation"]]:
            highlight_widget(self.ui.paper_orientation)

    @highlight_differing_settings.register
    def _(self, settings: PageLayoutSettings):
        for widget, _ in self._get_string_settings_widgets():
            if widget.text() != getattr(settings, widget.objectName()):
                highlight_widget(widget)
        for widget, _ in self._get_boolean_settings_widgets():
            if widget.isChecked() is not getattr(settings, widget.objectName()):
                highlight_widget(widget)
        for widget, _ in self._get_integer_settings_widgets():
            if widget.value() != getattr(settings, widget.objectName()):
                highlight_widget(widget)
        if self._current_page_size() != PageSize[settings.paper_size]:
            highlight_widget(self.ui.paper_size)
        if self._current_page_orientation() != PageOrientation[settings.paper_orientation]:
            highlight_widget(self.ui.paper_orientation)
