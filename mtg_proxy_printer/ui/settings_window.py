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


from PyQt5.QtCore import QStringListModel, pyqtSignal
from PyQt5.QtWidgets import QWidget, QDialogButtonBox, QComboBox, QCheckBox

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

    def load_settings(self, settings):
        self.preferred_language_combo_box: QComboBox
        self.avoid_low_res_images_check_box: QCheckBox
        self.include_cards_depicting_racism_check_box: QCheckBox
        images_section = settings["images"]
        if self.preferred_language_combo_box.model().stringList():
            self.preferred_language_combo_box.setCurrentIndex(self.get_index_for_language_code(
                images_section.get("preferred-language")
            ))
        self.avoid_low_res_images_check_box.setChecked(
            images_section.getboolean("avoid-low-resolution-images")
        )
        self.include_cards_depicting_racism_check_box.setChecked(
            settings["downloads"].getboolean("download-cards-depicting-racism")
        )
        document_section = settings["documents"]
        self.page_height.setValue(document_section.getint("paper-height-mm"))
        self.page_width.setValue(document_section.getint("paper-width-mm"))
        self.page_margin_top.setValue(document_section.getint("margin-top-mm"))
        self.page_margin_bottom.setValue(document_section.getint("margin-bottom-mm"))
        self.page_margin_left.setValue(document_section.getint("margin-left-mm"))
        self.page_margin_right.setValue(document_section.getint("margin-right-mm"))
        self.page_image_spacing_horizontal.setValue(document_section.getint("image-spacing-horizontal-mm"))
        self.page_image_spacing_vertical.setValue(document_section.getint("image-spacing-vertical-mm"))

    def reset(self):
        logger.info("User reverts the made changes.")
        self.load_settings(mtg_proxy_printer.settings.settings)

    def hide(self):
        logger.info("User closes the settings dialog. This will reset any made changes.")
        self.reset()
        super(SettingsWindow, self).hide()

    def save(self):
        logger.info("User saves the configuration to disk.")
        images_section = mtg_proxy_printer.settings.settings["images"]
        downloads_section = mtg_proxy_printer.settings.settings["downloads"]
        documents_section = mtg_proxy_printer.settings.settings["documents"]
        images_section["preferred-language"] = self.preferred_language_combo_box.currentText()
        self.avoid_low_res_images_check_box: QCheckBox
        images_section["avoid-low-resolution-images"] = str(self.avoid_low_res_images_check_box.isChecked())
        downloads_section["download-cards-depicting-racism"] = str(
            self.include_cards_depicting_racism_check_box.isChecked())
        documents_section["paper-height-mm"] = str(self.page_height.value())
        documents_section["paper-width-mm"] = str(self.page_width.value())
        documents_section["margin-top-mm"] = str(self.page_margin_top.value())
        documents_section["margin-bottom-mm"] = str(self.page_margin_bottom.value())
        documents_section["margin-left-mm"] = str(self.page_margin_left.value())
        documents_section["margin-right-mm"] = str(self.page_margin_right.value())
        documents_section["image-spacing-horizontal-mm"] = str(self.page_image_spacing_horizontal.value())
        documents_section["image-spacing-vertical-mm"] = str(self.page_image_spacing_vertical.value())
        mtg_proxy_printer.settings.write_settings_to_file()
        self.saved.emit()
        logger.debug("Save finished.")

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
