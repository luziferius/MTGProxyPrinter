# Copyright (C) 2020 Thomas Hess <thomas.hess@udo.edu>

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

from PyQt5.QtCore import QStringListModel, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QDialogButtonBox, QComboBox, QCheckBox, QSpinBox, QFileDialog, QLineEdit, QPushButton

from mtg_proxy_printer.ui.common import inherits_from_ui_file_with_name

import mtg_proxy_printer.settings
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


class SettingsWindow(*inherits_from_ui_file_with_name("settings_window")):

    saved = pyqtSignal()

    def __init__(self, language_model: QStringListModel,  *args, **kwargs):
        super(SettingsWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.language_model = language_model
        self.preferred_language_combo_box: QComboBox
        self.preferred_language_combo_box.setModel(self.language_model)

        self.button_box: QDialogButtonBox
        self.button_box.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.restore_defaults)
        self.button_box.button(QDialogButtonBox.Reset).clicked.connect(self.reset)
        self.button_box.button(QDialogButtonBox.Save).clicked.connect(self.save)
        self.button_box.button(QDialogButtonBox.Save).clicked.connect(self.hide)
        self.button_box.button(QDialogButtonBox.Cancel).clicked.connect(self.hide)
        self._setup_icons()
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _setup_icons(self):
        action_fallback_icons: typing.List[typing.Tuple[QPushButton, str]] = [
            (self.document_save_path_browse_button, "document-open"),
            (self.pdf_save_path_browse_button, "document-open"),
        ]
        for button, icon_name in action_fallback_icons:
            if button.icon().isNull():  # Icon not available in the theme, fallback to built-in icons
                button.setIcon(mtg_proxy_printer.ui.common.load_icon(f"{icon_name}.svg"))

    def show(self):
        logger.info("Show the settings window.")
        self.load_settings(mtg_proxy_printer.settings.settings)
        super(SettingsWindow, self).show()

    def load_settings(self, settings: configparser.ConfigParser):
        self._load_images_settings(settings)
        self._load_download_settings(settings)
        self._load_document_settings(settings)
        self._load_save_path_settings(settings)

    def _load_images_settings(self, settings):
        self.preferred_language_combo_box: QComboBox
        self.avoid_low_res_images_check_box: QCheckBox
        images_section = settings["images"]
        if self.preferred_language_combo_box.model().stringList():
            self.preferred_language_combo_box.setCurrentIndex(self.get_index_for_language_code(
                images_section.get("preferred-language")
            ))
        self.avoid_low_res_images_check_box.setChecked(
            images_section.getboolean("avoid-low-resolution-images")
        )
        self.automatically_add_opposing_faces.setChecked(
            images_section.getboolean("automatically-add-opposing-faces")
        )

    def _load_document_settings(self, settings: configparser.ConfigParser):
        document_section = settings["documents"]
        widgets_with_settings = self._get_document_settings_widgets()
        for widget, setting in widgets_with_settings:
            widget.setValue(document_section.getint(setting))
        self.print_cut_marker.setChecked(document_section.getboolean("print-cut-marker"))

    def _load_download_settings(self, settings: configparser.ConfigParser):
        download_section = settings["downloads"]
        widgets_with_settings = self._get_download_settings_widgets()
        for widget, setting in widgets_with_settings:
            widget.setChecked(download_section.getboolean(setting))

    def _load_save_path_settings(self, settings: configparser.ConfigParser):
        section = settings["default-save-paths"]
        widgets_with_settings = self._get_save_path_settings_widgets()
        for widget, setting in widgets_with_settings:
            widget.setText(section[setting])

    def _get_document_settings_widgets(self):
        widgets_with_settings: typing.List[typing.Tuple[QSpinBox, str]] = [
            (self.pdf_page_count_limit, "pdf-page-count-limit"),
            (self.page_height, "paper-height-mm"),
            (self.page_width, "paper-width-mm"),
            (self.page_margin_top, "margin-top-mm"),
            (self.page_margin_bottom, "margin-bottom-mm"),
            (self.page_margin_left, "margin-left-mm"),
            (self.page_margin_right, "margin-right-mm"),
            (self.page_image_spacing_horizontal, "image-spacing-horizontal-mm"),
            (self.page_image_spacing_vertical, "image-spacing-vertical-mm"),
        ]
        return widgets_with_settings

    def _get_download_settings_widgets(self):
        widgets_with_settings: typing.List[typing.Tuple[QCheckBox, str]] = [
            (self.include_cards_depicting_racism, "download-cards-depicting-racism"),
            (self.include_white_bordered_cards, "download-white-bordered"),
            (self.include_gold_bordered_cards, "download-gold-bordered"),
            (self.include_funny_cards, "download-funny-cards"),
            (self.include_banned_in_brawl, "download-banned-in-brawl"),
            (self.include_banned_in_commander, "download-banned-in-commander"),
            (self.include_banned_in_historic, "download-banned-in-historic"),
            (self.include_banned_in_legacy, "download-banned-in-legacy"),
            (self.include_banned_in_modern, "download-banned-in-modern"),
            (self.include_banned_in_pauper, "download-banned-in-pauper"),
            (self.include_banned_in_penny, "download-banned-in-penny"),
            (self.include_banned_in_pioneer, "download-banned-in-pioneer"),
            (self.include_banned_in_standard, "download-banned-in-standard"),
            (self.include_banned_in_vintage, "download-banned-in-vintage"),
            (self.include_token, "download-token"),
        ]
        return widgets_with_settings

    def _get_save_path_settings_widgets(self):
        widgets_with_settings: typing.List[typing.Tuple[QLineEdit, str]] = [
            (self.document_save_path, "document-save-path"),
            (self.pdf_save_path, "pdf-export-path"),
        ]
        return widgets_with_settings

    def reset(self):
        logger.info("User reverts the made changes.")
        self.load_settings(mtg_proxy_printer.settings.settings)

    def hide(self):
        logger.info("User closes the settings dialog. This will reset any made changes.")
        self.reset()
        super(SettingsWindow, self).hide()

    def save(self):
        logger.info("User saves the configuration to disk.")
        self._save_images_settings()
        self._save_downloads_settings()
        self._save_documents_settings()
        self._save_save_path_settings()
        mtg_proxy_printer.settings.write_settings_to_file()
        self.saved.emit()
        logger.debug("Save finished.")

    def _save_images_settings(self):
        images_section = mtg_proxy_printer.settings.settings["images"]
        images_section["preferred-language"] = self.preferred_language_combo_box.currentText()
        images_section["avoid-low-resolution-images"] = str(self.avoid_low_res_images_check_box.isChecked())
        images_section["automatically-add-opposing-faces"] = str(self.automatically_add_opposing_faces.isChecked())

    def _save_downloads_settings(self):
        downloads_section = mtg_proxy_printer.settings.settings["downloads"]
        widgets_and_settings = self._get_download_settings_widgets()
        for widget, setting in widgets_and_settings:
            downloads_section[setting] = str(widget.isChecked())

    def _save_documents_settings(self):
        documents_section = mtg_proxy_printer.settings.settings["documents"]
        widgets_and_settings = self._get_document_settings_widgets()
        for widget, setting in widgets_and_settings:
            documents_section[setting] = str(widget.value())
        documents_section["print-cut-marker"] = str(self.print_cut_marker.isChecked())

    def _save_save_path_settings(self):
        section = mtg_proxy_printer.settings.settings["default-save-paths"]
        widgets_and_settings = self._get_save_path_settings_widgets()
        for widget, setting in widgets_and_settings:
            section[setting] = widget.text()

    def restore_defaults(self):
        logger.info("User resets the configuration to the default settings.")
        self.load_settings(mtg_proxy_printer.settings.DEFAULT_SETTINGS)
        logger.debug("Loaded DEFAULT_SETTINGS.")

    def get_index_for_language_code(self, language: str):
        languages = self.language_model.stringList()
        if language in languages:
            return languages.index(language)
        else:
            return languages.index("en")

    @pyqtSlot()
    def on_document_save_path_browse_button_clicked(self):
        logger.info("User selects a new default document save path.")
        location = QFileDialog.getExistingDirectory(self, "Select default save location")
        self.document_save_path.setText(location)

    @pyqtSlot()
    def on_pdf_save_path_browse_button_clicked(self):
        logger.info("User selects a new default PDF document export path.")
        location = QFileDialog.getExistingDirectory(self, "Select default PDF export location")
        self.pdf_save_path.setText(location)
