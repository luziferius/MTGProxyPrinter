# Copyright (C) 2018-2020 Thomas Hess <thomas.hess@udo.edu>

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

import sys
import typing

from PyQt5.QtCore import pyqtSlot, Qt, QTimer
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from mtg_proxy_printer.argument_parser import Namespace
from mtg_proxy_printer import meta_data
import mtg_proxy_printer.model.carddb
from mtg_proxy_printer import settings
from mtg_proxy_printer.natsort import str_less_than
from mtg_proxy_printer.update_checker import newer_application_version_available, newer_card_data_available
import mtg_proxy_printer.card_info_downloader
import mtg_proxy_printer.ui.common
import mtg_proxy_printer.ui.main_window
import mtg_proxy_printer.ui.settings_window
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

__all__ = [
    "Application",
]


class Application(QApplication):

    def __init__(self, args: Namespace, argv: typing.List[str] = None):
        if argv is None:
            argv = sys.argv
        logger.info("Starting MTGProxyPrinter")
        super(Application, self).__init__(argv)
        self._setup_icons()
        self.args: Namespace = args
        logger.debug("Opening Database")
        self.card_db = mtg_proxy_printer.model.carddb.CardDatabase()
        logger.debug("Creating GUI")
        self.main_window = mtg_proxy_printer.ui.main_window.MainWindow(self.args, self.card_db)
        self.settings_window = mtg_proxy_printer.ui.settings_window.SettingsWindow(
            self.main_window.language_model, self.main_window)
        self.settings_window.saved.connect(self.main_window.settings_changed)
        self.main_window.action_show_settings.triggered.connect(self.settings_window.show)
        self.main_window.action_download_card_data.setEnabled(self.card_db.allow_updating_card_data())
        self.main_window.show()
        QTimer.singleShot(0, self._check_for_updates)
        self._show_changelog_after_update()
        if not self.card_db.has_data():
            logger.info("Card database is empty. Will ask the user, if they choose to download the data now.")
            self.main_window.ask_user_about_empty_database()
        self.main_window.should_update_languages.emit()
        logger.debug("Initialisation done. Starting event loop.")
        self.exec_()
        logger.debug("Left event loop.")

    def _check_for_updates(self):
        self._check_for_application_update_if_enabled()
        self._check_for_card_data_update_if_enabled()

    def _check_for_application_update_if_enabled(self):
        if setting := settings.settings["application"].getboolean("check-for-application-updates"):
            logger.info("Checking for application updates.")
            if (newer_version := newer_application_version_available()) is not None:
                logger.info(f"A new update is available: {newer_version}. Notifying the user.")
                self.main_window.show_application_update_available_message_box(newer_version)
            else:
                logger.debug("No application update found.")
        elif setting is None:
            logger.info("No user setting for update set. About to ask.")
            if self.main_window.ask_user_about_application_update_policy():
                self._check_for_application_update_if_enabled()
        else:
            logger.info("Checking for application updates disabled. Not checking for updates.")

    def _check_for_card_data_update_if_enabled(self):
        if setting := settings.settings["application"].getboolean("check-for-card-data-updates"):
            logger.info("Checking for card data updates.")
            if estimated_new_card_count := newer_card_data_available(self.card_db):
                logger.info(f"New card data is available. Notifying the user.")
                self.main_window.show_card_data_update_available_message_box(estimated_new_card_count)
            else:
                logger.debug("No new card data found.")
        elif setting is None:
            logger.info("No user setting for card data updates set. About to ask.")
            if self.main_window.ask_user_about_card_data_update_policy():
                self._check_for_card_data_update_if_enabled()
        else:
            logger.info("Checking for card data updates disabled. Not checking for updates.")

    def _show_changelog_after_update(self):
        if str_less_than(settings.settings["application"]["last-used-version"], meta_data.__version__):
            logger.info(
                f'Updated application from {settings.settings["application"]["last-used-version"]} '
                f'to {meta_data.__version__}')
            settings.update_version_string()
            settings.write_settings_to_file()
            QTimer.singleShot(0, self.main_window.about_dialog.show_changelog)

    def _setup_icons(self):
        # The current icon theme name is empty by default, which causes the system-default theme, returned by
        # QIcon.fallbackThemeName() to be used.
        # On platforms without native icon theme support, both QIcon.themeName() and QIcon.fallbackThemeName()
        # return an empty string and no icons will load. These platforms require an explicit theme name set.

        # To test if the current platform has native icon theme support, check, if QIcon.fallbackThemeName() returns
        # a non-empty string. If it is empty, explicitly set the name of the internal icon theme. This will load the
        # internal icons.
        if not QIcon.fallbackThemeName():
            logger.info(
                "No native icon theme support or no system theme set, defaulting to internal icons."
            )
            if not mtg_proxy_printer.ui.common.HAS_COMPILED_RESOURCES:
                # If the compiled resources are available, the default search path ":/icons" is sufficient. Only append
                # the resources directory file system path, if directly running from the source distribution.
                theme_search_paths = QIcon.themeSearchPaths()
                theme_search_paths.append(mtg_proxy_printer.ui.common.ICON_PATH_PREFIX)
                QIcon.setThemeSearchPaths(theme_search_paths)
            QIcon.setThemeName("breeze")

        self.setAttribute(Qt.AA_UseHighDpiPixmaps)

    @pyqtSlot()
    def shutdown(self):
        logger.info("About to exit.")
        self.closeAllWindows()
        logger.debug("All windows closed. Calling quit()")
        self.quit()
