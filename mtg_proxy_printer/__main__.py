# Copyright (C) 2020, 2021 Thomas Hess <thomas.hess@udo.edu>

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

# Import and implicitly load the settings first, before importing any modules that pull in GUI classes.
import mtg_proxy_printer.settings

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication

import mtg_proxy_printer.argument_parser
import mtg_proxy_printer.logger
import mtg_proxy_printer.application

# Workaround that puts the Application instance into the module scope. This prevents issues with the garbage collector
# when main() is left. Without, the Python GC interferes with Qt’s memory management and may cause segmentation faults
# on application exit.
_app = None
logger = mtg_proxy_printer.logger.get_logger(__name__)


def main():
    global _app
    arguments = mtg_proxy_printer.argument_parser.parse_args()
    mtg_proxy_printer.logger.configure_root_logger()
    # According to https://doc.qt.io/qt-5/qt.html#ApplicationAttribute-enum,
    # Qt.AA_EnableHighDpiScaling has to be set prior to creating the QApplication instance
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    _app = mtg_proxy_printer.application.Application(arguments)
    if arguments.test_exit_on_launch:
        logger.info("Skipping startup tasks, because immediate application exit was requested.")
        QTimer.singleShot(0, _app.main_window.on_action_quit_triggered)
    else:
        logger.debug("Enqueueing startup tasks.")
        _app.run_startup_tasks(arguments)
    logger.debug("Initialisation done. Starting event loop.")
    _app.exec_()
    logger.debug("Left event loop.")


if __name__ == "__main__":
    main()
