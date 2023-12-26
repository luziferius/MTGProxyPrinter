# Copyright (C) 2020, 2021 Thomas Hess <thomas.hess@udo.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# Import and implicitly load the settings first, before importing any modules that pull in GUI classes.
import mtg_proxy_printer.settings

import os
import platform
import sys

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication

import mtg_proxy_printer.app_dirs
from mtg_proxy_printer.argument_parser import parse_args
import mtg_proxy_printer.logger
from mtg_proxy_printer.application import Application
import mtg_proxy_printer.natsort

# Workaround that puts the Application instance into the module scope. This prevents issues with the garbage collector
# when main() is left. Without, the Python GC interferes with Qt’s memory management and may cause segmentation faults
# on application exit.
_app = None
logger = mtg_proxy_printer.logger.get_logger(__name__)


def handle_ssl_certificates():
    """
    Ensures that HTTPS connections can be established.
    On Python >= 3.10, use truststore to use the system native certificate store.
    On Python < 3.10, use certifi to set the CA certificates
    """
    if "SSL_CERT_FILE" in os.environ:
        logger.info("SSL certificate location set in the environment. Using that for HTTPS connections")
    elif not mtg_proxy_printer.natsort.str_less_than(platform.python_version(), "3.10"):
        logger.info("Use system-native SSL trust store via the truststore library for HTTPS connections")
        import truststore
        truststore.inject_into_ssl()
    else:
        import certifi
        logger.info("Use certifi library as SSL trust store for HTTPS connections")
        os.environ["SSL_CERT_FILE"] = certifi.where()


def main():
    global _app
    arguments = parse_args()
    mtg_proxy_printer.app_dirs.migrate_from_old_appdirs()
    mtg_proxy_printer.logger.configure_root_logger()
    handle_ssl_certificates()
    # According to https://doc.qt.io/qt-5/qt.html#ApplicationAttribute-enum,
    # Qt.AA_EnableHighDpiScaling has to be set prior to creating the QApplication instance
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    _app = Application(arguments, sys.argv)
    if arguments.test_exit_on_launch:
        logger.info("Skipping startup tasks, because immediate application exit was requested.")
        QTimer.singleShot(0, _app.main_window.on_action_quit_triggered)
    else:
        logger.debug("Enqueueing startup tasks.")
        _app.enqueue_startup_tasks(arguments)
    logger.debug("Initialisation done. Starting event loop.")
    _app.exec_()
    logger.debug("Left event loop.")


if __name__ == "__main__":
    main()
