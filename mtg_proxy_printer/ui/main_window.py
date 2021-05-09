# Copyright (C) 2018, 2019 Thomas Hess <thomas.hess@udo.edu>

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

import pathlib
import typing

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QStringListModel, QModelIndex, Qt, QItemSelectionModel, QTimer
from PyQt5.QtGui import QCloseEvent, QResizeEvent, QShowEvent, QKeySequence
from PyQt5.QtWidgets import QApplication, QMessageBox, QProgressBar, QAction, QWidget, QToolBar

from mtg_proxy_printer.argument_parser import Namespace
import mtg_proxy_printer.card_info_downloader
import mtg_proxy_printer.model.carddb
import mtg_proxy_printer.model.imagedb
import mtg_proxy_printer.model.document
import mtg_proxy_printer.settings
import mtg_proxy_printer.print
from mtg_proxy_printer.ui.common import inherits_from_ui_file_with_name
from mtg_proxy_printer.ui.current_page_view import CurrentPageView
from mtg_proxy_printer.ui.document_view import DocumentView
from mtg_proxy_printer.ui.add_card import AddCardWidget
from mtg_proxy_printer.ui.dialogs import SavePDFDialog, SaveDocumentAsDialog, LoadDocumentDialog, \
    AboutMTGProxyPrinterDialog, PrintPreviewDialog, PrintDialog
from mtg_proxy_printer.ui.cache_cleanup_wizard import CacheCleanupWizard
from mtg_proxy_printer.ui.deck_import_wizard import DeckImportWizard

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger
layout = mtg_proxy_printer.settings.settings["gui"]["search-widget-layout"]
__all__ = [
    "MainWindow",
]


class MainWindow(*inherits_from_ui_file_with_name(f"{layout}_search_layout/main_window")):

    should_update_languages = pyqtSignal()
    current_page_changed = pyqtSignal(mtg_proxy_printer.model.document.Page)
    window_size_changed = pyqtSignal()
    settings_changed = pyqtSignal()
    loading_state_changed = pyqtSignal(bool)

    def __init__(self, arguments: Namespace, card_db: mtg_proxy_printer.model.carddb.CardDatabase, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        logger.info(f"Creating {self.__class__.__name__} instance using the {layout} layout.")
        self.setupUi(self)
        self.about_dialog = self._create_about_dialog()
        self.progress_bar = self._create_progress_bar()
        self.card_database: mtg_proxy_printer.model.carddb.CardDatabase = card_db
        self.image_db = self._create_image_database()
        self.document = self._create_document_instance(arguments)
        preferred_language = mtg_proxy_printer.settings.settings["images"]["preferred-language"]
        self.language_model = QStringListModel([preferred_language], self)
        self.card_data_downloader = self._create_card_data_downloader()
        self.action_compact_document.triggered.connect(self.document.compact_pages)
        self.page_view: CurrentPageView
        self.window_size_changed.connect(self.page_view.window_size_changed)
        self.current_page_changed.connect(self.page_view.current_page_changed)
        self._setup_loading_state_connections()
        self._setup_add_card_widget()
        self._setup_document_view()
        self.action_new_page.triggered.connect(self.document.add_page)
        self.should_update_languages.connect(self.update_language_model)
        self.should_update_languages.connect(self.add_card_widget.update_selected_language)
        self.settings_changed.connect(self.add_card_widget.update_selected_language)
        self.settings_changed.connect(self.document.apply_settings)
        self.settings_changed.connect(self.page_view.settings_changed)
        self.settings_changed.connect(self.offer_re_downloading_card_database)
        self.action_show_toolbar: QAction
        self.action_show_toolbar.setChecked(mtg_proxy_printer.settings.settings["gui"].getboolean("show-toolbar"))
        self._setup_platform_dependent_default_shortcuts()
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _create_about_dialog(self) -> AboutMTGProxyPrinterDialog:
        about_dialog = AboutMTGProxyPrinterDialog(self)
        self.action_show_about_dialog.triggered.connect(about_dialog.show_about)
        self.action_show_changelog.triggered.connect(about_dialog.show_changelog)
        return about_dialog

    def _setup_platform_dependent_default_shortcuts(self):
        actions_with_shortcuts: typing.List[typing.Tuple[QAction, QKeySequence.StandardKey]] = [
            (self.action_new_document, QKeySequence.New),
            (self.action_load_document, QKeySequence.Open),
            (self.action_save_document, QKeySequence.Save),
            (self.action_save_as, QKeySequence.SaveAs),
            (self.action_show_settings, QKeySequence.Preferences),
            (self.action_print, QKeySequence.Print),
            (self.action_quit, QKeySequence.Quit),
        ]
        for action, shortcut in actions_with_shortcuts:
            action.setShortcut(shortcut)

    def _setup_loading_state_connections(self):
        for widget_or_action in self._get_widgets_and_actions_disabled_in_loading_state():
            self.loading_state_changed.connect(widget_or_action.setDisabled)

    def _create_document_instance(self, args: Namespace):
        document = mtg_proxy_printer.model.document.Document(self.card_database, self.image_db, self)
        document.document_cleared.connect(self._select_first_page)
        document.loading_state_changed.connect(self.loading_state_changed)
        document.loader.loading_file_failed.connect(self.on_document_loading_failed)
        document.loader.unknown_scryfall_ids_found.connect(self.on_document_loading_found_unknown_scryfall_ids)
        document.loader.network_error_occurred.connect(self.on_network_error_occurred)
        self.current_page_changed.connect(document.on_currently_edited_page_changed)
        self.action_new_document.triggered.connect(document.clear_all_data)
        self.image_db.add_card.connect(document.add_card)
        if args.file is not None:
            if args.file.is_file():
                # Wait until after __init__ finished and the main loop starts
                QTimer.singleShot(0, lambda: document.loader.load_document(args.file))
                logger.info(f'Enqueued loading of document "{args.file}"')
            elif args.file.exists():
                logger.warning(f'Command line argument "{args.file}" exists, but is not a file. Not loading it.')
            else:
                logger.warning(f'Command line argument "{args.file}" does not exist. Ignoring it.')
        return document

    def _create_card_data_downloader(self) -> mtg_proxy_printer.card_info_downloader.CardInfoDownloader:
        downloader = mtg_proxy_printer.card_info_downloader.CardInfoDownloader(self.card_database)
        downloader.download_finished.connect(self.should_update_languages)
        downloader.download_finished.connect(self.update_language_model)
        downloader.download_begins.connect(self.show_progress_bar)
        downloader.download_progress.connect(self.progress_bar.setValue)
        downloader.download_finished.connect(self.progress_bar.hide)
        downloader.working_state_changed.connect(self.loading_state_changed)
        downloader.network_error_occurred.connect(self.on_network_error_occurred)
        return downloader

    def _get_widgets_and_actions_disabled_in_loading_state(self) -> typing.List[typing.Union[QWidget, QAction]]:
        return [
            self.action_new_document,
            self.action_save_as,
            self.action_save_document,
            self.action_compact_document,
            self.action_load_document,
            self.action_print,
            self.action_print_preview,
            self.action_print_pdf,
            self.action_import_deck_list,
            self.action_new_page,
            self.action_discard_page,
            self.add_card_widget,
            self.action_show_settings,
            self.action_cleanup_local_image_cache,
            self.page_view.delete_selected_images_button,
        ]

    def _create_image_database(self):
        image_db = mtg_proxy_printer.model.imagedb.ImageDatabase(parent=self)
        image_db.card_download_starting.connect(self.show_progress_bar)
        image_db.card_download_finished.connect(self.progress_bar.hide)
        image_db.card_download_progress.connect(self.progress_bar.setValue)
        image_db.batch_processing_state_changed.connect(self.loading_state_changed)
        image_db.network_error_occurred.connect(self.on_network_error_occurred)
        return image_db

    def _create_progress_bar(self):
        progress_bar = QProgressBar(self)
        progress_bar.hide()
        self.statusBar().addPermanentWidget(progress_bar)
        return progress_bar

    def _setup_add_card_widget(self):
        self.add_card_widget: AddCardWidget
        self.add_card_widget.set_card_database(self.card_database)
        self.add_card_widget.card_added.connect(self.image_db.get_image_asynchronous)

    def _setup_document_view(self):
        self.document_view: DocumentView
        self.document_view.setModel(self.document)
        self.document_view.selectionModel().currentChanged.connect(self.on_selected_page_changed)
        self._select_first_page()

    def offer_re_downloading_card_database(self):
        settings_changed = self.card_database.check_if_download_settings_changed()
        self.action_download_card_data.setEnabled(self.card_database.allow_updating_card_data())
        if settings_changed and QMessageBox.question(
                self, "Card download filter changed",
                "The card download filter settings changed.\n"
                "Do you want to re-download the card data now to apply the new settings?\n"
                "If you decline, you can do this later using the Settings menu.",
                QMessageBox.Yes | QMessageBox.No
                ) == QMessageBox.Yes:
            self.on_action_download_card_data_triggered()

    @pyqtSlot()
    def _select_first_page(self):
        old_selection = self.document_view.selectionModel().currentIndex()
        self.document_view.selectionModel().select(self.document.createIndex(0, 0), QItemSelectionModel.Select)
        # Programmatically selecting the first page in the document seems to not emit this signal, like it happens
        # when the user clicks on one. So manually emit this signal to properly initialize the page_view state.
        self.document_view.selectionModel().currentChanged.emit(self.document.createIndex(0, 0), old_selection)

    def resizeEvent(self, event: QResizeEvent):
        super(MainWindow, self).resizeEvent(event)
        self.window_size_changed.emit()

    def showEvent(self, event: QShowEvent):
        super(MainWindow, self).showEvent(event)
        self.window_size_changed.emit()

    @pyqtSlot()
    def update_language_model(self):
        self.language_model.setStringList(self.card_database.get_all_languages())

    def closeEvent(self, event: QCloseEvent):
        """
        This function is automatically called when the window is closed using the close [X] button in the window
        decorations or by right clicking in the system window list and using the close action, or similar ways to close
        the window.
        Just ignore this event and simulate that the user used action_quit instead.

        To quote the Qt5 QCloseEvent documentation: If you do not want your widget to be hidden, or want some special
        handling, you should reimplement the event handler and ignore() the event.
        """
        logger.debug("User tried to close the window. Ignore the event and trigger the quit action")
        event.ignore()
        # Be safe and emit this signal, because it might be connected to multiple slots.
        self.action_quit.triggered.emit()

    @pyqtSlot()
    def on_action_quit_triggered(self):
        logger.info(f"User wants to quit.")
        # Prevent a loop, because shutdown() closes this window, causing closeEvent to fire, in turn causing this to be
        # called again. So just disconnect the signal. The connection won’t be needed during application shutdown.
        logger.debug("Quit action confirmed. Exiting…")
        self.card_data_downloader.cancel_running_operations()
        self.toolBar: QToolBar
        if self.toolBar.isVisible() != mtg_proxy_printer.settings.settings["gui"].getboolean("show-toolbar"):
            logger.debug("Toolbar visibility setting changed. Updating config and writing new state to disk.")
            mtg_proxy_printer.settings.settings["gui"]["show-toolbar"] = str(self.toolBar.isVisible())
            mtg_proxy_printer.settings.write_settings_to_file()
        self.action_quit.triggered.disconnect(self.on_action_quit_triggered)
        QApplication.instance().shutdown()

    @pyqtSlot()
    def on_action_cleanup_local_image_cache_triggered(self):
        logger.info("User wants to clean up the local image cache")
        wizard = CacheCleanupWizard(self.card_database, self.image_db, self)
        wizard.show()

    @pyqtSlot()
    def on_action_import_deck_list_triggered(self):
        logger.info(f"User imports a deck list.")
        wizard = DeckImportWizard(self.card_database, self.image_db, parent=self)
        wizard.clear_document.connect(self.document.clear_all_data)
        wizard.deck_added.connect(self.image_db.get_deck_asynchronous)
        wizard.show()

    @pyqtSlot()
    def on_action_print_triggered(self):
        logger.info(f"User prints the current document.")
        if self._ask_user_about_compacting_document("printing") == QMessageBox.Cancel:
            return
        print_dialog = PrintDialog(self.document, self)
        print_dialog.exec_()

    @pyqtSlot()
    def on_action_print_preview_triggered(self):
        logger.info(f"User views the print preview.")
        if self._ask_user_about_compacting_document("printing") == QMessageBox.Cancel:
            return
        print_preview_dialog = PrintPreviewDialog(self.document, self)
        print_preview_dialog.exec_()

    @pyqtSlot()
    def on_action_print_pdf_triggered(self):
        logger.info(f"User prints the current document to PDF.")
        if self._ask_user_about_compacting_document("exporting as a PDF") == QMessageBox.Cancel:
            return
        dialog = SavePDFDialog(self, self.document)
        dialog.exec_()

    def on_network_error_occurred(self, message: str):
        QMessageBox.warning(
            self, "Network error",
            f"Operation failed, because a network error occurred.\n"
            f"Check your internet connection. Reported error message:\n{message}",
            QMessageBox.Ok, QMessageBox.Ok)
        self.loading_state_changed.emit(False)

    def _ask_user_about_compacting_document(self, action: str) -> QMessageBox.ButtonRole:
        if savable_pages := self.document.compute_pages_saved_by_compacting():
            result = QMessageBox.question(
                self, "Saving pages possible",
                f"It is possible to save {savable_pages} pages when printing this document.\n"
                f"Do you want to compact the document now to minimize the page count prior to {action}?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if result == QMessageBox.Yes:
                self.document.compact_pages()
            return result
        return QMessageBox.No  # No pages can be saved, assume "No" for this case

    def ask_user_about_empty_database(self):
        """
        This is called when the application starts with an empty or no card database. Ask the user if they wish
        to download the card data now. If so, trigger the appropriate action, just as if the user clicked the menu item.
        """
        should_download = QMessageBox.question(
            self, "Download required Card data from Scryfall?",
            "This program requires downloading additional card data from Scryfall to operate the card search.\n"
            "Download the required data from Scryfall now?\n"
            "If you decline now, you can exclude some card types or individual cards based on ban lists "
            "in the settings and then manually start the download later.\n"
            "Or accept and use the current settings.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.Yes
        if should_download:
            self.action_download_card_data.trigger()

    @pyqtSlot()
    def on_action_download_card_data_triggered(self):
        logger.info(f"User downloads the card data from Scryfall.")
        self.action_download_card_data.setDisabled(True)
        self.card_data_downloader.populate_database()

    @pyqtSlot(int)
    def show_progress_bar(self, expected_total_item_count: int):
        self.progress_bar.reset()
        self.progress_bar.setMaximum(expected_total_item_count)
        self.progress_bar.show()

    @pyqtSlot(QModelIndex)
    def on_selected_page_changed(self, selected: QModelIndex):
        if selected.isValid():
            new_page: mtg_proxy_printer.model.document.Page = selected.data(Qt.EditRole)
            self.current_page_changed.emit(new_page)

    @pyqtSlot()
    def on_action_discard_page_triggered(self):
        self.document_view: DocumentView
        to_be_deleted = self.document_view.selectedIndexes()
        self.document.remove_pages(to_be_deleted)
        new_row_selection = self.document.createIndex(
            min(to_be_deleted[0].row(), self.document.rowCount()-1),
            0
        )
        old_selection = self.document_view.selectionModel().currentIndex()
        self.document_view.selectionModel().select(
            new_row_selection, QItemSelectionModel.ClearAndSelect)
        # Programmatically selecting the first page in the document seems to not emit this signal, like it happens
        # when the user clicks on one. So manually emit this signal to properly initialize the page_view state.
        self.document_view.selectionModel().currentChanged.emit(new_row_selection, old_selection)

    @pyqtSlot()
    def on_action_save_document_triggered(self):
        logger.debug("User clicked on Save")
        if self.document.file_path is None:
            logger.debug("No save file path set. Call 'Save as' instead.")
            self.action_save_as.triggered.emit()
        else:
            logger.debug("About to save the document")
            self.document.save_to_disk()
            logger.debug("Saved.")

    @pyqtSlot()
    def on_action_save_as_triggered(self):
        dialog = SaveDocumentAsDialog(self, self.document)
        dialog.exec_()

    @pyqtSlot()
    def on_action_load_document_triggered(self):
        dialog = LoadDocumentDialog(self, self.document)
        if dialog.exec_() == LoadDocumentDialog.Accepted:
            self._select_first_page()

    def on_document_loading_failed(self, failed_path: pathlib.Path):
        QMessageBox.critical(
            self, "Document loading failed",
            f"Loading file \"{failed_path}\" failed. The file was not recognized as an "
            f"{mtg_proxy_printer.meta_data.PROGRAMNAME} document. If you want to load a deck list, use the "
            f"\"{self.action_import_deck_list.text()}\" function instead.",
            QMessageBox.Ok, QMessageBox.Ok
        )

    def on_document_loading_found_unknown_scryfall_ids(self, count: int):
        QMessageBox.warning(
            self, "Unrecognized cards in loaded document found",
            f"Skipped {count} unrecognized cards in the loaded document. Saving the document will remove these entries "
            f"from the document.\n\nThe locally stored card "
            f"data may be outdated or the document was created using a less restrictive download filter.",
            QMessageBox.Ok, QMessageBox.Ok
        )

    def show_update_available_message_box(self, newer_version: str):
        QMessageBox.information(
            self, "Update available",
            f"An application update is available: Version {newer_version}\n\n"
            f"You are currently using version {mtg_proxy_printer.meta_data.__version__}.",
            QMessageBox.Ok, QMessageBox.Ok
        )
