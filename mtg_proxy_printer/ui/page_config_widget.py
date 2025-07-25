#  Copyright © 2020-2025  Thomas Hess <thomas.hess@udo.edu>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.


import functools
from functools import partial
import math
from typing import List, Tuple, Union, Any

import pint
from PyQt5.QtCore import pyqtSlot as Slot, Qt, pyqtSignal as Signal
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtGui import QPageSize, QPageLayout, QColor
from PyQt5.QtWidgets import QGroupBox, QWidget, QDoubleSpinBox, QCheckBox, QLineEdit, QComboBox, QColorDialog

from mtg_proxy_printer.settings import settings
from mtg_proxy_printer.ui.common import load_ui_from_file, BlockedSignals, highlight_widget
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.units_and_sizes import CardSizes, \
    PageType, unit_registry, ConfigParser, PageSizeManager, Unit

try:
    from mtg_proxy_printer.ui.generated.page_config_widget import Ui_PageConfigWidget
except ModuleNotFoundError:
    Ui_PageConfigWidget = load_ui_from_file("page_config_widget")

from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger
CheckState = Qt.CheckState
DISTANCE_UNIT = unit_registry.UnitsContainer({"[length]": 1})
mm = unit_registry.mm
degree = unit_registry.degree
point = unit_registry.point


def is_pint_distance(value: Any) -> bool:
    return isinstance(value, pint.Quantity) and value.dimensionality == DISTANCE_UNIT

def is_pint_angle(value: Any) -> bool:
    return isinstance(value, pint.Quantity) and value.units == degree

def is_pint_point(value: Any) -> bool:
    return isinstance(value, pint.Quantity) and value.units == point


class PageConfigWidget(QGroupBox):
    page_layout_changed = Signal(PageLayoutSettings)

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
        page_layout = PageLayoutSettings.create_from_settings()

        for page_size_id in PageSizeManager.PageSize.values():
            ui.paper_size.addItem(QPageSize.name(page_size_id), page_size_id)
        for item, value in PageSizeManager.PageOrientation.items():
            ui.paper_orientation.addItem(item, value)

        ui.paper_size.currentIndexChanged.connect(self._on_paper_size_changed)
        ui.paper_size.currentIndexChanged.connect(self.validate_paper_size_settings)
        ui.paper_size.currentIndexChanged.connect(self.on_page_layout_setting_changed)
        ui.paper_size.currentIndexChanged.connect(partial(self.page_layout_changed.emit, page_layout))

        ui.paper_orientation.currentIndexChanged.connect(self._on_paper_orientation_changed)
        ui.paper_orientation.currentIndexChanged.connect(self.validate_paper_size_settings)
        ui.paper_orientation.currentIndexChanged.connect(self.on_page_layout_setting_changed)
        ui.paper_orientation.currentIndexChanged.connect(partial(self.page_layout_changed.emit, page_layout))

        ui.watermark_opacity.valueChanged.connect(self._on_watermark_color_opacity_changed)
        ui.watermark_opacity.valueChanged.connect(partial(self.page_layout_changed.emit, page_layout))

        ui.watermark_color_button.clicked.connect(self._on_watermark_color_button_clicked)

        for spinbox, _, unit in self._get_numerical_settings_widgets():
            layout_key = spinbox.objectName()
            spinbox.valueChanged[float].connect(
                partial(self.set_numerical_page_layout_item, page_layout, layout_key, unit))
            spinbox.valueChanged[float].connect(self.validate_paper_size_settings)
            spinbox.valueChanged[float].connect(self.on_page_layout_setting_changed)
            spinbox.valueChanged[float].connect(partial(self.page_layout_changed.emit, page_layout))

        for checkbox, _ in self._get_boolean_settings_widgets():
            layout_key = checkbox.objectName()
            checkbox.stateChanged.connect(partial(self.set_boolean_page_layout_item, page_layout, layout_key))
            checkbox.stateChanged.connect(partial(self.page_layout_changed.emit, page_layout))

        for line_edit, _ in self._get_string_settings_widgets():
            layout_key = line_edit.objectName()
            line_edit.textChanged.connect(partial(setattr, page_layout, layout_key))
            line_edit.textChanged.connect(partial(self.page_layout_changed.emit, page_layout))
        return page_layout

    @staticmethod
    def set_numerical_page_layout_item(page_layout: PageLayoutSettings, layout_key: str, unit: Unit, value: float):
        # Implementation note: This call is placed here, because stuffing it into a lambda defined within a while loop
        # somehow uses the wrong references and will set the attribute that was processed last in the loop.
        # This method can be used via functools.partial to reduce the signature to (float) -> None,
        # which can be connected to the valueChanged[float] signal just fine.
        # Also, functools.partial does not exhibit the same issue as the lambda expression shows.
        setattr(page_layout, layout_key, value*unit)

    @staticmethod
    def set_boolean_page_layout_item(page_layout: PageLayoutSettings, layout_key: str, value: CheckState):
        # Implementation note: This call is placed here, because stuffing it into a lambda defined within a while loop
        # somehow uses the wrong references and will set the attribute that was processed last in the loop.
        # This method can be used via functools.partial to reduce the signature to (CheckState) -> None,
        # which can be connected to the stateChanged signal just fine.
        # Also, functools.partial does not exhibit the same issue as the lambda expression shows.
        setattr(page_layout, layout_key, value == CheckState.Checked)

    @Slot(int)
    def _on_paper_size_changed(self, index: int):
        ui = self.ui
        custom_paper_size_selected = not index
        ui.paper_orientation.setDisabled(custom_paper_size_selected)  # Only valid for predefined paper sizes
        ui.custom_page_width.setEnabled(custom_paper_size_selected)  # 3 UI elements for custom paper sizes
        ui.custom_page_height.setEnabled(custom_paper_size_selected)
        ui.flip_page_dimensions.setEnabled(custom_paper_size_selected)
        selected_paper_size_item: QPageSize.PageSizeId = ui.paper_size.currentData(Qt.ItemDataRole.UserRole)
        self.page_layout.paper_size = PageSizeManager.PageSizeReverse[selected_paper_size_item]

    @Slot()
    def _on_paper_orientation_changed(self):
        ui = self.ui
        orientation: QPageLayout.Orientation = ui.paper_orientation.currentData(Qt.ItemDataRole.UserRole)
        self.page_layout.paper_orientation = PageSizeManager.PageOrientationReverse[orientation]

    @Slot(int)
    def _on_watermark_color_opacity_changed(self, value: int):
        self.page_layout.watermark_color.setAlpha(value)
        self._show_watermark_color(self.page_layout.watermark_color)

    @Slot()
    def _on_watermark_color_button_clicked(self):
        selected = QColorDialog.getColor(self.page_layout.watermark_color)
        selected.setAlpha(self.ui.watermark_opacity.value())
        self.page_layout.watermark_color = selected
        self._show_watermark_color(self.page_layout.watermark_color)
        self.page_layout_changed.emit(self.page_layout)

    @Slot()
    def on_page_layout_setting_changed(self):
        """
        Recomputes and updates the page capacity display, whenever any page layout widget changes.
        """
        regular_capacity = self.page_layout.compute_page_card_capacity(PageType.REGULAR)
        oversized_capacity = self.page_layout.compute_page_card_capacity(PageType.OVERSIZED)
        regular_text = self.tr(
            "%n regular card(s)",
            "Display of the resulting page capacity for regular-sized cards",
            regular_capacity)
        oversized_text = self.tr(
            "%n oversized card(s)",
            "Display of the resulting page capacity for oversized cards",
            oversized_capacity
        )
        capacity_text = self.tr(
            "{regular_text}, {oversized_text}",
            "Combination of the page capacities for regular, and oversized cards"
        ).format(regular_text=regular_text, oversized_text=oversized_text)
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
        available_width = self._current_page_width() - oversized.width.to(mm, "print").magnitude
        available_height = self._current_page_height() - oversized.height.to(mm, "print").magnitude
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

    def _current_page_height(self) -> float:
        """Returns the current page height in mm as set via GUI elements. Used for validations"""
        ui = self.ui
        if not ui.paper_size.currentIndex():
            return ui.custom_page_height.value()
        page_size: QPageSize.PageSizeId = ui.paper_size.currentData(Qt.ItemDataRole.UserRole)
        size = QPageSize.size(page_size, QPageSize.Unit.Millimeter)
        orientation = PageSizeManager.PageOrientationReverse[ui.paper_orientation.currentData(Qt.ItemDataRole.UserRole)]
        return size.height() if orientation == "Portrait" else size.width()

    def _current_page_width(self) -> float:
        """Returns the current page width in mm as set via GUI elements. Used for validations"""
        ui = self.ui
        if not ui.paper_size.currentIndex():
            return ui.custom_page_width.value()
        page_size: QPageSize.PageSizeId = ui.paper_size.currentData(Qt.ItemDataRole.UserRole)
        size = QPageSize.size(page_size, QPageSize.Unit.Millimeter)
        orientation = PageSizeManager.PageOrientationReverse[ui.paper_orientation.currentData(Qt.ItemDataRole.UserRole)]
        return size.width() if orientation == "Portrait" else size.height()

    def load_document_settings_from_config(self, new_config: ConfigParser):
        logger.debug(f"About to load document settings from the global settings")
        documents_section = new_config["documents"]
        for spinbox, setting, unit in self._get_numerical_settings_widgets():
            value = documents_section.get_quantity(setting).to(unit)
            spinbox.setValue(value.magnitude)
            setattr(self.page_layout, spinbox.objectName(), spinbox.value()*value.units)
        for checkbox, setting in self._get_boolean_settings_widgets():
            checkbox.setChecked(documents_section.getboolean(setting))
        for line_edit, setting in self._get_string_settings_widgets():
            line_edit.setText(documents_section[setting])
        self._show_watermark_color(documents_section.get_color("watermark-color"))

        self._load_paper_size(documents_section["paper-size"])
        self._load_paper_orientation(documents_section["paper-orientation"])
        self.validate_paper_size_settings()
        self.on_page_layout_setting_changed()
        self.page_layout_changed.emit(self.page_layout)
        logger.debug(f"Loading from settings finished")

    def load_from_page_layout(self, other: PageLayoutSettings):
        """Loads the page layout from another PageLayoutSettings instance"""
        logger.debug(f"About to load document settings from a document instance")
        ui = self.ui
        layout = self.page_layout
        # TODO: Maybe reverse the iteration direction and use the _get_*_settings_widgets() helpers?
        for key in layout.__annotations__.keys():
            value: Union[pint.Quantity, bool, str, QColor] = getattr(other, key)
            widget: QWidget = getattr(ui, key)
            with (BlockedSignals(widget)):  # Don’t call the validation methods in each iteration
                if is_pint_point(value):  # Points are a kind of distance, so catch that first
                    value = value.to(point).magnitude
                    widget.setValue(value)
                    value = value*point
                elif is_pint_distance(value):
                    value = value.to(mm).magnitude
                    widget.setValue(value)
                    value = widget.value()*mm
                elif is_pint_angle(value):
                    value = value.to(degree).magnitude
                    widget.setValue(value)
                    value = widget.value()*degree
                elif isinstance(widget, QComboBox):  # Ignore paper size attributes
                    pass
                elif isinstance(value, str):  # Load document title and watermark text
                    widget.setText(value)
                elif isinstance(value, QColor):
                    self._show_watermark_color(value)
                else:
                    widget.setChecked(value)
            setattr(self.page_layout, key, value)
        self._load_paper_size(other.paper_size)
        self._load_paper_orientation(other.paper_orientation)
        self.validate_paper_size_settings()
        self.on_page_layout_setting_changed()
        self.page_layout_changed.emit(self.page_layout)
        logger.debug(f"Loading from document settings finished")

    def _show_watermark_color(self, color: QColor):
        sheet = "QLabel {" + f"background-color: {color.name(QColor.NameFormat.HexArgb)}" + "}"
        self.ui.watermark_color.setStyleSheet(sheet)
        if self.ui.watermark_opacity.value() != color.alpha():
            self.ui.watermark_opacity.setValue(color.alpha())


    def _load_paper_size(self, size: str):
        page_size = PageSizeManager.PageSize[size]
        combo_box = self.ui.paper_size
        model = combo_box.model()
        for row in range(model.rowCount()):
            if model.data(model.index(row, 0), Qt.ItemDataRole.UserRole) == page_size:
                # Blocks premature execution of validation logic triggered via change signals
                # that should not run *right now*.
                with BlockedSignals(combo_box):
                    combo_box.setCurrentIndex(row)
                break

    def _load_paper_orientation(self, orientation_str: str):
        orientation = PageSizeManager.PageOrientation[orientation_str]
        combo_box = self.ui.paper_orientation
        model = combo_box.model()
        for row in range(model.rowCount()):
            if model.data(model.index(row, 0), Qt.ItemDataRole.UserRole) == orientation:
                # Blocks premature execution of validation logic triggered via change signals
                # that should not run *right now*.
                with BlockedSignals(combo_box):
                    combo_box.setCurrentIndex(row)
                break

    def save_document_settings_to_config(self):
        logger.info("About to save document settings to the global settings")
        documents_section = settings["documents"]
        for spinbox, setting, unit in self._get_numerical_settings_widgets():
            documents_section[setting] = str(spinbox.value()*unit)
        for checkbox, setting in self._get_boolean_settings_widgets():
            documents_section[setting] = str(checkbox.isChecked())
        for line_edit, setting in self._get_string_settings_widgets():
            documents_section[setting] = line_edit.text()
        documents_section["watermark-color"] = self.page_layout.watermark_color.name(QColor.NameFormat.HexArgb)
        documents_section["paper-size"] = PageSizeManager.PageSizeReverse[self._current_page_size()]
        documents_section["paper-orientation"] = PageSizeManager.PageOrientationReverse[self._current_page_orientation()]
        logger.debug("Saving done.")

    def _get_numerical_settings_widgets(self) -> List[Tuple[QDoubleSpinBox, str, Unit]]:
        ui = self.ui
        widgets_with_settings: List[Tuple[QDoubleSpinBox, str, Unit]] = [
            (ui.card_bleed, "card-bleed", mm),
            (ui.custom_page_height, "custom-page-height", mm),
            (ui.custom_page_width, "custom-page-width", mm),
            (ui.margin_top, "margin-top", mm),
            (ui.margin_bottom, "margin-bottom", mm),
            (ui.margin_left, "margin-left", mm),
            (ui.margin_right, "margin-right", mm),
            (ui.row_spacing, "row-spacing", mm),
            (ui.column_spacing, "column-spacing", mm),
            (ui.watermark_pos_x, "watermark-pos-x", mm),
            (ui.watermark_pos_y, "watermark-pos-y", mm),
            (ui.watermark_angle, "watermark-angle", degree),
            (ui.watermark_font_size, "watermark-font-size", point),
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
            (ui.watermark_text, "watermark-text"),
        ]
        return widgets_with_settings

    def _current_page_size(self) -> QPrinter.PageSize:
        return self.ui.paper_size.currentData(Qt.ItemDataRole.UserRole)

    def _current_page_orientation(self) -> QPageLayout.Orientation:
        return self.ui.paper_orientation.currentData(Qt.ItemDataRole.UserRole)

    @functools.singledispatchmethod
    def highlight_differing_settings(self, to_compare: Union[ConfigParser, PageLayoutSettings]):
        pass

    @highlight_differing_settings.register
    def _(self, to_compare: ConfigParser):
        section = to_compare["documents"]
        for widget, setting in self._get_string_settings_widgets():
            if widget.text() != section[setting]:
                highlight_widget(widget)
        for widget, setting in self._get_boolean_settings_widgets():
            if widget.isChecked() is not section.getboolean(setting):
                highlight_widget(widget)
        for widget, setting, unit in self._get_numerical_settings_widgets():
            if not math.isclose(widget.value(), section.get_quantity(setting).to(unit).magnitude):
                highlight_widget(widget)
        self._highlight_watermark_color_widgets(section.get_color("watermark-color"))
        if self._current_page_size() != PageSizeManager.PageSize[section["paper-size"]]:
            highlight_widget(self.ui.paper_size)
        if self._current_page_orientation() != PageSizeManager.PageOrientation[section["paper-orientation"]]:
            highlight_widget(self.ui.paper_orientation)

    @highlight_differing_settings.register
    def _(self, to_compare: PageLayoutSettings):
        for line_edit, _ in self._get_string_settings_widgets():
            name = line_edit.objectName()
            if line_edit.text() != getattr(to_compare, name):
                highlight_widget(line_edit)
        for checkbox, _ in self._get_boolean_settings_widgets():
            name = checkbox.objectName()
            if checkbox.isChecked() is not getattr(to_compare, name):
                highlight_widget(checkbox)
        for spinbox, _, unit in self._get_numerical_settings_widgets():
            name = spinbox.objectName()
            if not math.isclose(spinbox.value(), getattr(to_compare, name).to(unit).magnitude):
                highlight_widget(spinbox)
        self._highlight_watermark_color_widgets(to_compare.watermark_color)
        if self._current_page_size() != PageSizeManager.PageSize[to_compare.paper_size]:
            highlight_widget(self.ui.paper_size)
        if self._current_page_orientation() != PageSizeManager.PageOrientation[to_compare.paper_orientation]:
            highlight_widget(self.ui.paper_orientation)

    def _highlight_watermark_color_widgets(self, color_to_compare: QColor):
        ui = self.ui
        if self.page_layout.watermark_color != color_to_compare:
            for widget in (
                    ui.watermark_color, ui.watermark_color_label,
                    ui.watermark_color_button, ui.watermark_opacity):
                highlight_widget(widget)
