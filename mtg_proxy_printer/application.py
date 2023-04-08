# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>

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

import atexit
import functools
import os
import pathlib
import platform
import shutil
import sys
from tempfile import mkdtemp
import typing

from PyQt5.QtCore import pyqtSlot as Slot, Qt, QTimer, QStringListModel
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from mtg_proxy_printer.argument_parser import Namespace
from mtg_proxy_printer import meta_data
import mtg_proxy_printer.model.carddb
import mtg_proxy_printer.model.carddb_migrations
import mtg_proxy_printer.model.document
import mtg_proxy_printer.model.imagedb
from mtg_proxy_printer import settings
from mtg_proxy_printer.update_checker import UpdateChecker
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
        if not os.getenv("QT_QPA_PLUGIN") and "-platform" not in argv and platform.system() == "Windows":
            logger.info("Running on Windows without explicit platform override. Enabling dark mode rendering.")
            # The explicit set platform and parameters overwrite the environment, so set these options iff neither
            # present as parameters nor environment variables.
            argv.append("-platform")
            argv.append("windows:darkmode=1")
        super(Application, self).__init__(argv)
        self._setup_icons()
        self.args: Namespace = args
        self.card_db, self.image_db = self._open_databases(args)
        self.card_info_downloader = mtg_proxy_printer.card_info_downloader.CardInfoDownloader(self.card_db)
        self.document = self._create_document_instance(self.card_db, self.image_db)
        self.language_model = self._create_language_model()
        logger.debug("Creating GUI")
        self.main_window = mtg_proxy_printer.ui.main_window.MainWindow(
            self.card_db, self.card_info_downloader, self.image_db, self.document, self.language_model
        )
        self.main_window.ui.action_download_card_data.setEnabled(self.card_db.allow_updating_card_data())
        self.settings_window = self._create_settings_window(
            self.language_model, self.document, self.main_window, self.card_info_downloader)
        self.main_window.show()
        self.update_checker = self._create_update_checker(args)
        self.main_window.should_update_languages.emit()

    def run_startup_tasks(self, args: Namespace):
        """
        Enqueues all tasks that should run in the Qt event loop at application start.
        Includes
        - checking for updates or undecided update policy settings
        - notifying on empty card database
        - running the card data import, if a JSON card data document is given as a command line argument
        - opening a document given via command line arguments
        - etc…
        """
        if settings.was_application_updated():
            logger.info(
                f'Updated application from {settings.settings["application"]["last-used-version"]} '
                f'to {meta_data.__version__}')
            settings.update_stored_version_string()
            settings.write_settings_to_file()
            QTimer.singleShot(0, self.main_window.about_dialog.show_changelog)
        logger.debug("Enqueueing update check")
        QTimer.singleShot(100, self._check_for_undecided_update_settings)
        QTimer.singleShot(100, self.update_checker.check_for_updates)
        if args.card_data and args.card_data.is_file():
            logger.info(f"User imports card data from file {args.card_data}")
            self.card_info_downloader.request_import_from_file.emit(args.card_data)
        elif not self.card_db.has_data():
            logger.info("Card database is empty. Will ask the user, if they choose to download the data now.")
            self.main_window.ask_user_about_empty_database()
        if args.file is not None:
            if args.file.is_file():
                QTimer.singleShot(0, functools.partial(self.document.loader.load_document, args.file))
                logger.info(f'Enqueued loading of document "{args.file}"')
            elif args.file.exists():
                logger.warning(f'Command line argument "{args.file}" exists, but is not a file. Not loading it.')
            else:
                logger.warning(f'Command line argument "{args.file}" does not exist. Ignoring it.')

    def _open_databases(self, args: Namespace):
        if args.test_exit_on_launch:
            temp_directory = pathlib.Path(mkdtemp())
            logger.info(f"Opening databases in temporary directory {temp_directory}")
            atexit.register(functools.partial(shutil.rmtree, temp_directory))
            card_db = mtg_proxy_printer.model.carddb.CardDatabase(temp_directory / "card_db" / "CardDatabase.sqlite3")
            image_db = mtg_proxy_printer.model.imagedb.ImageDatabase(
                temp_directory/"image_db", parent=self)
            return card_db, image_db
        logger.debug("Opening Databases")
        mtg_proxy_printer.model.carddb_migrations.migrate_card_database_location()
        card_db = mtg_proxy_printer.model.carddb.CardDatabase()
        image_db = mtg_proxy_printer.model.imagedb.ImageDatabase(parent=self)
        return card_db, image_db

    @staticmethod
    def _create_settings_window(
            language_model: QStringListModel, document: mtg_proxy_printer.model.document.Document,
            main_window: mtg_proxy_printer.ui.main_window.MainWindow,
            card_info_downloader: mtg_proxy_printer.card_info_downloader.CardInfoDownloader):
        settings_window = mtg_proxy_printer.ui.settings_window.SettingsWindow(
            language_model, document, main_window)
        settings_window.document_settings_updated.connect(document.apply)
        settings_window.preferred_language_changed.connect(
            main_window.ui.central_widget.ui.add_card_widget.on_settings_preferred_language_changed)
        settings_window.requested_card_download.connect(card_info_downloader.request_download_to_file)
        settings_window.long_running_process_begins.connect(main_window.show_progress_bar)
        settings_window.process_updated.connect(main_window.progress_bar.setValue)
        settings_window.process_finished.connect(main_window.hide_progress_bar)
        settings_window.error_occurred.connect(main_window.on_error_occurred)
        main_window.ui.action_show_settings.triggered.connect(settings_window.show)
        return settings_window

    def _create_document_instance(
            self,
            card_db: mtg_proxy_printer.model.carddb.CardDatabase,
            image_db: mtg_proxy_printer.model.imagedb.ImageDatabase) -> mtg_proxy_printer.model.document.Document:
        document = mtg_proxy_printer.model.document.Document(card_db, image_db, self)
        document.request_fill_image_for_action.connect(image_db.download_worker.fill_document_action_image)
        image_db.request_action.connect(document.apply)
        image_db.download_worker.missing_image_obtained.connect(document.on_missing_image_obtained)
        return document

    def _create_language_model(self):
        preferred_language = mtg_proxy_printer.settings.settings["images"]["preferred-language"]
        return QStringListModel([preferred_language], self)

    def _create_update_checker(self, args: Namespace) -> UpdateChecker:
        # Don’t do the card data update check, if the user imports card data via command line arguments
        update_checker = UpdateChecker(self.card_db, args, self)
        update_checker.network_error_occurred.connect(self.main_window.on_network_error_occurred)
        update_checker.card_data_update_found.connect(self.main_window.show_card_data_update_available_message_box)
        update_checker.application_update_found.connect(self.main_window.show_application_update_available_message_box)
        return update_checker

    def _check_for_undecided_update_settings(self):
        section = settings.settings["application"]
        if section.getboolean("check-for-application-updates") is None:
            logger.info("No user setting for application updates set. About to ask.")
            self.main_window.ask_user_about_application_update_policy()
        if section.getboolean("check-for-card-data-updates") is None:
            logger.info("No user setting for card data updates set. About to ask.")
            self.main_window.ask_user_about_card_data_update_policy()

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

    @Slot()
    def quit(self):
        logger.info("About to exit.")
        self.update_checker.stop_background_worker()
        self.closeAllWindows()
        logger.debug("All windows closed. Calling quit()")
        super().quit()
