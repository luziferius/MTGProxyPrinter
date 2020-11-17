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


from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import QWidget, QDialogButtonBox, QComboBox, QCheckBox

from mtg_proxy_printer.model.language import get_known_language_codes
from mtg_proxy_printer.ui.common import inherits_from_ui_file_with_name

import mtg_proxy_printer.settings
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


class SettingsWindow(*inherits_from_ui_file_with_name("settings_window")):

    def __init__(self, parent: QWidget = None):
        super(SettingsWindow, self).__init__(parent)
        self.setupUi(self)
        self.language_model = QStringListModel(get_known_language_codes(), self)
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
        defaults = mtg_proxy_printer.settings.DEFAULT_SETTINGS
        images_section = self._get_section(settings, "images")
        self.preferred_language_combo_box.setCurrentIndex(self.get_index_for_language_code(
            images_section.get(
                "preferred-language",
                defaults["images"]["preferred-language"]))
        )
        self.avoid_low_res_images_check_box.setChecked(
            images_section.getboolean(
                "avoid-low-resolution-images",
                defaults["images"].getboolean("avoid-low-resolution-images"))
        )

    def reset(self):
        logger.info("User reverts the made changes.")
        self.load_settings(mtg_proxy_printer.settings.settings)

    def hide(self):
        logger.info("User closes the settings dialog. This will reset any made changes.")
        self.reset()
        super(SettingsWindow, self).hide()

    def save(self):
        logger.info("User saves the configuration to disk.")
        settings = mtg_proxy_printer.settings.settings
        images_section = self._get_section(settings, "images")
        images_section["preferred-language"] = self.preferred_language_combo_box.currentText()
        self.avoid_low_res_images_check_box: QCheckBox
        images_section["avoid-low-resolution-images"] = str(self.avoid_low_res_images_check_box.isChecked())
        mtg_proxy_printer.settings.write_settings_to_file()
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

    @staticmethod
    def _get_section(settings, name: str):
        if not settings.has_section(name):
            settings.add_section(name)
        section = settings[name]
        return section
