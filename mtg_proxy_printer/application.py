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
import mtg_proxy_printer.card_info_importer
import mtg_proxy_printer.ui.main_window
import mtg_proxy_printer.ui.settings_window
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


class Application(QApplication):

    def __init__(self, argv: typing.List[str] = None):
        if argv is None:
            argv = sys.argv
        super(Application, self).__init__(argv)
        logger.info("Starting MTGProxyPrinter")
        self.card_db = mtg_proxy_printer.model.carddb.CardDatabase()

        self.main_window = mtg_proxy_printer.ui.main_window.MainWindow()
        self.settings_window = mtg_proxy_printer.ui.settings_window.SettingsWindow(self.main_window)
        self.settings_window.hide()
        self.main_window.action_show_settings.triggered.connect(self.settings_window.show)
        self.main_window.show()
        card_db_has_data = self.card_db.has_data()
        self.main_window.action_download_card_data.setDisabled(card_db_has_data)
        if not card_db_has_data:
            self.main_window.action_download_card_data.trigger()
        logger.debug("Initialisation done. Starting event loop.")
        self.exec_()
        logger.debug("Left event loop.")

    @pyqtSlot()
    def shutdown(self):
        logger.info("About to exit.")
        self.closeAllWindows()
        self.quit()
