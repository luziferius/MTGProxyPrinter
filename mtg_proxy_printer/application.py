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

import mtg_proxy_printer.ui.main_window
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


class Application(QApplication):

    def __init__(self, argv: typing.List[str] = None):
        if argv is None:
            argv = sys.argv
        super(Application, self).__init__(argv)
        logger.info("Starting visual_image_splitter")

        self.main_window = mtg_proxy_printer.ui.main_window.MainWindow()
        self.main_window.show()
        logger.debug("Initialisation done. Starting event loop.")
        self.exec_()
        logger.debug("Left event loop.")

    @pyqtSlot()
    def shutdown(self):
        logger.info("About to exit.")
        self.closeAllWindows()
        self.quit()
