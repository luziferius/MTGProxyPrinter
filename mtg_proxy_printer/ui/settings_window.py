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

from PyQt5.QtCore import QStringListModel, pyqtSignal
from PyQt5.QtWidgets import QDialogButtonBox, QComboBox, QCheckBox, QSpinBox

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
        logger.info(f"Created {self.__class__.__name__} instance.")

    def show(self):
        logger.info("Show the settings window.")
        self.load_settings(mtg_proxy_printer.settings.settings)
        super(SettingsWindow, self).show()

    def load_settings(self, settings: configparser.ConfigParser):
        self._load_images_settings(settings)
        self._load_download_settings(settings)
        self._load_document_settings(settings)

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
            (self.include_illegal_in_brawl, "download-illegal-in-brawl"),
            (self.include_illegal_in_commander, "download-illegal-in-commander"),
            (self.include_illegal_in_historic, "download-illegal-in-historic"),
            (self.include_illegal_in_legacy, "download-illegal-in-legacy"),
            (self.include_illegal_in_modern, "download-illegal-in-modern"),
            (self.include_illegal_in_pauper, "download-illegal-in-pauper"),
            (self.include_illegal_in_penny, "download-illegal-in-penny"),
            (self.include_illegal_in_pioneer, "download-illegal-in-pioneer"),
            (self.include_illegal_in_standard, "download-illegal-in-standard"),
            (self.include_illegal_in_vintage, "download-illegal-in-vintage"),
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
        mtg_proxy_printer.settings.write_settings_to_file()
        self.saved.emit()
        logger.debug("Save finished.")

    def _save_images_settings(self):
        images_section = mtg_proxy_printer.settings.settings["images"]
        images_section["preferred-language"] = self.preferred_language_combo_box.currentText()
        images_section["avoid-low-resolution-images"] = str(self.avoid_low_res_images_check_box.isChecked())

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
