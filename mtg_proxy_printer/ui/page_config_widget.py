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
from typing import Any, NamedTuple

from PySide6.QtCore import Slot, Qt, Signal
from PySide6.QtGui import QPageSize, QPageLayout, QColor
from PySide6.QtWidgets import QGroupBox, QWidget, QDoubleSpinBox, QCheckBox, QLineEdit, QColorDialog, \
    QLabel, QSlider, QPushButton, QComboBox
from pint.registry import Unit, Quantity
from mtg_proxy_printer.settings import settings
from mtg_proxy_printer.ui.common import load_ui_from_file, BlockedSignals, highlight_widget
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.units_and_sizes import CardSizes, \
    PageType, unit_registry, ConfigParser, PageSizeManager

try:
    from mtg_proxy_printer.ui.generated.page_config_widget import Ui_PageConfigWidget
except ModuleNotFoundError:
    Ui_PageConfigWidget = load_ui_from_file("page_config_widget")

from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger
CheckState = Qt.CheckState
UserRole = Qt.ItemDataRole.UserRole
NameFormat = QColor.NameFormat
DISTANCE_UNIT = unit_registry.UnitsContainer({"[length]": 1})
mm = unit_registry.mm
degree = unit_registry.degree
point = unit_registry.point
ShowAlphaChannel = QColorDialog.ColorDialogOption.ShowAlphaChannel


class ColorEditorWidgets(NamedTuple):
    display: QLabel
    select_button: QPushButton
    opacity_slider: QSlider
    ui_text_label: QLabel


def is_pint_distance(value: Any) -> bool:
    return isinstance(value, Quantity) and value.dimensionality == DISTANCE_UNIT



def is_pint_angle(value: Any) -> bool:
    return isinstance(value, Quantity) and value.units == degree


def is_pint_point(value: Any) -> bool:
    return isinstance(value, Quantity) and value.units == point


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

        ui.cut_marker_style.addItem(self.tr("Disabled", "A cut marker style"), "None")
        ui.cut_marker_style.addItem(self.tr("Solid lines", "A cut marker style"), "Solid")
        ui.cut_marker_style.addItem(self.tr("Dashed lines", "A cut marker style"), "Dashes")
        ui.cut_marker_style.addItem(self.tr("Dotted lines", "A cut marker style"), "Dots")
        ui.cut_marker_style.currentIndexChanged.connect(self._on_cut_marker_style_changed)
        ui.cut_marker_style.currentIndexChanged.connect(lambda: self.page_layout_changed.emit(page_layout))

        ui.print_registration_marks_style.addItem(self.tr("Disabled", "A print/cut registration marker style"), "None")
        ui.print_registration_marks_style.addItem(self.tr("Bullseye", "A print/cut registration marker style"), "Bullseye")
        ui.print_registration_marks_style.addItem(
            self.tr("Silhouette cutter (Cameo-compatible)",
                    "A print/cut registration marker style"), "Cut marker")
        ui.print_registration_marks_style.currentIndexChanged.connect(self._on_print_registration_marks_style_changed)
        ui.print_registration_marks_style.currentIndexChanged.connect(lambda: self.page_layout_changed.emit(page_layout))

        for page_size_id in PageSizeManager.PageSize.values():
            ui.paper_size.addItem(QPageSize.name(page_size_id), page_size_id)
        for item, value in PageSizeManager.PageOrientation.items():
            ui.paper_orientation.addItem(item, value)

        ui.paper_size.currentIndexChanged.connect(self._on_paper_size_changed)
        ui.paper_size.currentIndexChanged.connect(self.validate_paper_size_settings)
        ui.paper_size.currentIndexChanged.connect(self.on_page_layout_changed)
        ui.paper_size.currentIndexChanged.connect(lambda: self.page_layout_changed.emit(page_layout))

        ui.paper_orientation.currentIndexChanged.connect(self._on_paper_orientation_changed)
        ui.paper_orientation.currentIndexChanged.connect(self.validate_paper_size_settings)
        ui.paper_orientation.currentIndexChanged.connect(self.on_page_layout_changed)
        ui.paper_orientation.currentIndexChanged.connect(lambda: self.page_layout_changed.emit(page_layout))

        ui.watermark_color_button.clicked.connect(self._on_watermark_color_button_clicked)
        ui.watermark_opacity.valueChanged.connect(self._on_watermark_color_opacity_changed)
        ui.watermark_opacity.valueChanged.connect(lambda: self.page_layout_changed.emit(page_layout))

        ui.cut_marker_color_button.clicked.connect(self._on_cut_marker_color_button_clicked)
        ui.cut_marker_opacity.valueChanged.connect(self._on_cut_marker_color_opacity_changed)
        ui.cut_marker_opacity.valueChanged.connect(lambda: self.page_layout_changed.emit(page_layout))

        for spinbox, _, unit in self._get_numerical_settings_widgets():
            layout_key = spinbox.objectName()
            spinbox.valueChanged[float].connect(
                partial(self.set_numerical_page_layout_item, page_layout, layout_key, unit))
            spinbox.valueChanged[float].connect(self.validate_paper_size_settings)
            spinbox.valueChanged[float].connect(self.on_page_layout_changed)
            spinbox.valueChanged[float].connect(lambda: self.page_layout_changed.emit(page_layout))

        for checkbox, _ in self._get_boolean_settings_widgets():
            layout_key = checkbox.objectName()
            checkbox.stateChanged.connect(partial(self.set_boolean_page_layout_item, page_layout, layout_key))
            checkbox.stateChanged.connect(lambda: self.page_layout_changed.emit(page_layout))

        for line_edit, _ in self._get_string_settings_widgets():
            layout_key = line_edit.objectName()
            line_edit.textChanged.connect(partial(setattr, page_layout, layout_key))
            line_edit.textChanged.connect(lambda: self.page_layout_changed.emit(page_layout))
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
        #
        # PySide6 maps the QCheckBox check states to proper Python enums, but the stateChanged Qt signal carries raw
        # integers. To get the integers for comparison, the lambdas below require accessing the CheckState enum values.
        setattr(page_layout, layout_key, value == CheckState.Checked.value)

    @Slot(int)
    def _on_cut_marker_style_changed(self, _: int):
        self.page_layout.cut_marker_style = self.ui.cut_marker_style.currentData(Qt.ItemDataRole.UserRole)

    @Slot(int)
    def _on_print_registration_marks_style_changed(self, _: int):
        self.page_layout.print_registration_marks_style = (
            self.ui.print_registration_marks_style.currentData(Qt.ItemDataRole.UserRole)
        )

    @Slot(int)
    def _on_paper_size_changed(self, index: int):
        ui = self.ui
        custom_paper_size_selected = not index
        ui.paper_orientation.setDisabled(custom_paper_size_selected)  # Only valid for predefined paper sizes
        ui.custom_page_width.setEnabled(custom_paper_size_selected)  # 3 UI elements for custom paper sizes
        ui.custom_page_height.setEnabled(custom_paper_size_selected)
        ui.flip_page_dimensions.setEnabled(custom_paper_size_selected)
        selected_paper_size_item: QPageSize.PageSizeId = ui.paper_size.currentData(UserRole)
        self.page_layout.paper_size = PageSizeManager.PageSizeReverse[selected_paper_size_item]

    @Slot()
    def _on_paper_orientation_changed(self):
        ui = self.ui
        orientation: QPageLayout.Orientation = ui.paper_orientation.currentData(UserRole)
        self.page_layout.paper_orientation = PageSizeManager.PageOrientationReverse[orientation]

    @Slot(int)
    def _on_watermark_color_opacity_changed(self, value: int):
        ui = self.ui
        self.page_layout.watermark_color.setAlpha(value)
        self._show_color(ui.watermark_color, ui.watermark_opacity, self.page_layout.watermark_color)

    @Slot()
    def _on_watermark_color_button_clicked(self):
        ui = self.ui
        if not (selected := QColorDialog.getColor(
                self.page_layout.cut_marker_color, self,
                self.tr("Select watermark text color"), options=ShowAlphaChannel)).isValid():
            return
        selected.setAlpha(ui.watermark_opacity.value())
        self.page_layout.watermark_color = selected
        self._show_color(ui.watermark_color, ui.watermark_opacity, self.page_layout.watermark_color)
        self.page_layout_changed.emit(self.page_layout)

    @Slot(int)
    def _on_cut_marker_color_opacity_changed(self, value: int):
        ui = self.ui
        self.page_layout.cut_marker_color.setAlpha(value)
        self._show_color(ui.cut_marker_color, ui.cut_marker_opacity, self.page_layout.cut_marker_color)

    @Slot()
    def _on_cut_marker_color_button_clicked(self):
        ui = self.ui
        if not (selected := QColorDialog.getColor(
                self.page_layout.cut_marker_color, self,
                self.tr("Select cut marker color"), options=ShowAlphaChannel)).isValid():
            return
        selected.setAlpha(ui.cut_marker_opacity.value())
        self.page_layout.cut_marker_color = selected
        self._show_color(ui.cut_marker_color, ui.cut_marker_opacity, selected)
        self.page_layout_changed.emit(self.page_layout)

    @Slot()
    def on_page_layout_changed(self):
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
        layout = self.page_layout
        width, height = ui.custom_page_width.value(), ui.custom_page_height.value()
        with BlockedSignals(ui.custom_page_width), BlockedSignals(ui.custom_page_height):
            ui.custom_page_width.setValue(height)
            ui.custom_page_height.setValue(width)
        layout.page_width, layout.page_height = layout.page_height, layout.page_width
        self.on_page_layout_changed()
        self.page_layout_changed.emit(self.page_layout)

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
        page_size: QPageSize.PageSizeId = ui.paper_size.currentData(UserRole)
        size = QPageSize.size(page_size, QPageSize.Unit.Millimeter)
        orientation = PageSizeManager.PageOrientationReverse[ui.paper_orientation.currentData(UserRole)]
        return size.height() if orientation == "Portrait" else size.width()

    def _current_page_width(self) -> float:
        """Returns the current page width in mm as set via GUI elements. Used for validations"""
        ui = self.ui
        if not ui.paper_size.currentIndex():
            return ui.custom_page_width.value()
        page_size: QPageSize.PageSizeId = ui.paper_size.currentData(UserRole)
        size = QPageSize.size(page_size, QPageSize.Unit.Millimeter)
        orientation = PageSizeManager.PageOrientationReverse[ui.paper_orientation.currentData(UserRole)]
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
        for label, slider, setting, _ in self._get_color_settings_widgets():  # Ignore the text display label
            color = documents_section.get_color(setting)
            self._show_color(label, slider, color)
            setattr(self.page_layout, label.objectName(), color)

        self._load_paper_size(documents_section["paper-size"])
        self._load_paper_orientation(documents_section["paper-orientation"])
        self._load_cut_marker_style(documents_section["cut-marker-style"])
        self._load_print_registration_marks_style(documents_section["print-registration-marks-style"])
        self.validate_paper_size_settings()
        self.on_page_layout_changed()
        self.page_layout_changed.emit(self.page_layout)
        logger.debug(f"Loading from settings finished")

    def load_from_page_layout(self, other: PageLayoutSettings):
        """Loads the page layout from another PageLayoutSettings instance"""
        logger.debug(f"About to load document settings from a document instance")
        layout = self.page_layout
        # Block change signals to not trigger the validation logic on each iteration.
        # Especially the dimensions loop may pass invalid states:
        #  When loading valid margins left|right (160|5) over previous, valid (5|160),
        #  it may pass invalid state (160|160) in between, which would trigger a reset
        #  or unwanted value clamping.
        for spinbox, setting, unit in self._get_numerical_settings_widgets():
            value: Quantity | bool | str | QColor = getattr(other, name := spinbox.objectName())
            with BlockedSignals(spinbox):
                spinbox.setValue(value.magnitude)
            value = spinbox.value()*value.units
            setattr(layout, name, value)
        for checkbox, setting in self._get_boolean_settings_widgets():
            with BlockedSignals(checkbox):
                checkbox.setChecked(value := getattr(other, name := checkbox.objectName()))
            setattr(layout, name, value)
        for line_edit, setting in self._get_string_settings_widgets():
            with BlockedSignals(line_edit):
                line_edit.setText(value := getattr(other, name := line_edit.objectName()))
            setattr(layout, name, value)
        for label, slider, setting, _ in self._get_color_settings_widgets():  # Ignore the other widgets
            with BlockedSignals(slider):
                self._show_color(label, slider, value := getattr(other, name := label.objectName()))
            setattr(layout, name, value)
        self._load_paper_size(other.paper_size)
        self._load_paper_orientation(other.paper_orientation)
        self._load_cut_marker_style(other.cut_marker_style)
        self._load_print_registration_marks_style(other.print_registration_marks_style)
        self.validate_paper_size_settings()
        self.on_page_layout_changed()
        self.page_layout_changed.emit(self.page_layout)
        logger.debug(f"Loading from document settings finished")

    @staticmethod
    def _show_color(label: QLabel, opacity_slider: QSlider, color: QColor):
        sheet = "QLabel {" + f"background-color: {color.name(NameFormat.HexArgb)}" + "}"
        label.setStyleSheet(sheet)
        if opacity_slider.value() != color.alpha():
            opacity_slider.setValue(color.alpha())

    def _load_paper_size(self, size: str):
        self.page_layout.paper_size = size
        page_size = PageSizeManager.PageSize[size]
        self._set_combo_box_current_item_to_given_item(self.ui.paper_size, page_size)

    def _load_paper_orientation(self, orientation_str: str):
        self.page_layout.paper_orientation = orientation_str
        orientation = PageSizeManager.PageOrientation[orientation_str]
        self._set_combo_box_current_item_to_given_item(self.ui.paper_orientation, orientation)

    def _load_cut_marker_style(self, style_str: str):
        self.page_layout.cut_marker_style = style_str
        self._set_combo_box_current_item_to_given_item(self.ui.cut_marker_style, style_str)

    def _load_print_registration_marks_style(self, style_str: str):
        self.page_layout.print_registration_marks_style = style_str
        self._set_combo_box_current_item_to_given_item(self.ui.print_registration_marks_style, style_str)

    @staticmethod
    def _set_combo_box_current_item_to_given_item(combo_box: QComboBox, user_data_item: Any):
        model = combo_box.model()
        for row in range(model.rowCount()):
            if model.data(model.index(row, 0), UserRole) == user_data_item:
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
        documents_section["cut-marker-style"] = self.page_layout.cut_marker_style
        documents_section["print-registration-marks-style"] = self.page_layout.print_registration_marks_style
        documents_section["watermark-color"] = self.page_layout.watermark_color.name(QColor.NameFormat.HexArgb)
        documents_section["cut-marker-color"] = self.page_layout.cut_marker_color.name(NameFormat.HexArgb)
        documents_section["paper-size"] = PageSizeManager.PageSizeReverse[self._current_page_size()]
        documents_section["paper-orientation"] = PageSizeManager.PageOrientationReverse[self._current_page_orientation()]
        logger.debug("Saving done.")

    def _get_numerical_settings_widgets(self) -> list[tuple[QDoubleSpinBox, str, Unit]]:
        ui = self.ui
        widgets_with_settings: list[tuple[QDoubleSpinBox, str, Unit]] = [
            (ui.card_bleed, "card-bleed", mm),
            (ui.custom_page_height, "custom-page-height", mm),
            (ui.custom_page_width, "custom-page-width", mm),
            (ui.cut_marker_width, "cut-marker-width", mm),
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
        widgets_with_settings: list[tuple[QCheckBox, str]] = [
            (ui.draw_sharp_corners, "print-sharp-corners"),
            (ui.draw_page_numbers, "print-page-numbers"),
            (ui.cut_marker_draw_above_cards, "cut-marker-draw-above-cards"),
        ]
        return widgets_with_settings

    def _get_string_settings_widgets(self):
        ui = self.ui
        widgets_with_settings: list[tuple[QLineEdit, str]] = [
            (ui.document_name, "default-document-name"),
            (ui.watermark_text, "watermark-text"),
        ]
        return widgets_with_settings

    def _get_color_settings_widgets(self):
        """
        Returns the display label with current color, the opacity slider, the settings key carrying the configured
        value, and the list of UI elements for highlighting purposes.
        """
        ui = self.ui
        widgets_with_settings: list[tuple[QLabel, QSlider, str, ColorEditorWidgets]] = [
            (ui.watermark_color, ui.watermark_opacity, "watermark-color", ColorEditorWidgets(
                ui.watermark_color, ui.watermark_color_button, ui.watermark_opacity, ui.watermark_color_label)),
            (ui.cut_marker_color, ui.cut_marker_opacity, "cut-marker-color", ColorEditorWidgets(
                ui.cut_marker_color, ui.cut_marker_color_button, ui.cut_marker_opacity, ui.cut_marker_color_label)),
        ]
        return widgets_with_settings

    def _current_page_size(self) -> QPageSize.PageSizeId:
        return self.ui.paper_size.currentData(UserRole)

    def _current_page_orientation(self) -> QPageLayout.Orientation:
        return self.ui.paper_orientation.currentData(Qt.ItemDataRole.UserRole)

    def _current_cut_marker_style(self) -> str:
        return self.ui.cut_marker_style.currentData(Qt.ItemDataRole.UserRole)

    def _current_print_registration_marks_style(self) -> str:
        return self.ui.print_registration_marks_style.currentData(UserRole)

    @functools.singledispatchmethod
    def highlight_differing_settings(self, to_compare: ConfigParser | PageLayoutSettings):
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
        for label, slider, setting, to_highlight in self._get_color_settings_widgets():
            attribute_name = setting.replace("-", "_")
            if getattr(self.page_layout, attribute_name) != section.get_color(setting):
                highlight_widget(to_highlight)
        if self._current_page_size() != PageSizeManager.PageSize[section["paper-size"]]:
            highlight_widget(self.ui.paper_size)
        if self._current_page_orientation() != PageSizeManager.PageOrientation[section["paper-orientation"]]:
            highlight_widget(self.ui.paper_orientation)
        if self._current_cut_marker_style() != section["cut-marker-style"]:
            highlight_widget(self.ui.cut_marker_style)
        if self._current_print_registration_marks_style() != section["print-registration-marks-style"]:
            highlight_widget(self.ui.print_registration_marks_style)

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
        for label, slider, setting, to_highlight in self._get_color_settings_widgets():
            attribute_name = setting.replace("-", "_")
            if getattr(self.page_layout, attribute_name) != getattr(to_compare, attribute_name):
                highlight_widget(to_highlight)
        if self._current_page_size() != PageSizeManager.PageSize[to_compare.paper_size]:
            highlight_widget(self.ui.paper_size)
        if self._current_page_orientation() != PageSizeManager.PageOrientation[to_compare.paper_orientation]:
            highlight_widget(self.ui.paper_orientation)
        if self._current_cut_marker_style() != to_compare.cut_marker_style:
            highlight_widget(self.ui.cut_marker_style)
        if self._current_print_registration_marks_style() != to_compare.print_registration_marks_style:
            highlight_widget(self.ui.print_registration_marks_style)
