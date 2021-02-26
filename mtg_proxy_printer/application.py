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

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication

import mtg_proxy_printer.model.carddb
import mtg_proxy_printer.card_info_downloader
import mtg_proxy_printer.ui.common
import mtg_proxy_printer.ui.main_window
import mtg_proxy_printer.ui.settings_window
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


class Application(QApplication):

    def __init__(self, argv: typing.List[str] = None):
        if argv is None:
            argv = sys.argv
            logger.info("Starting MTGProxyPrinter")
        super(Application, self).__init__(argv)
        self.card_db = mtg_proxy_printer.model.carddb.CardDatabase()

        self.main_window = mtg_proxy_printer.ui.main_window.MainWindow(self.card_db)
        self.settings_window = mtg_proxy_printer.ui.settings_window.SettingsWindow(
            self.main_window.language_model, self.main_window)
        self.main_window.action_show_settings.triggered.connect(self.settings_window.show)
        self.settings_window.saved.connect(self.main_window.settings_changed)

        self.main_window.show()
        self.main_window.action_download_card_data.setEnabled(self.card_db.allow_updating_card_data())
        if not self.card_db.has_data():
            logger.info("Card database is empty. Will ask the user, if they choose to download the data now.")
            self.main_window.ask_user_about_empty_database()
        self.main_window.should_update_languages.emit()
        logger.debug("Initialisation done. Starting event loop.")
        self.exec_()
        logger.debug("Left event loop.")

    @pyqtSlot()
    def shutdown(self):
        logger.info("About to exit.")
        self.closeAllWindows()
        self.quit()
