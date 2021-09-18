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

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QStringListModel, QItemSelectionModel
from PyQt5.QtGui import QCloseEvent, QResizeEvent, QShowEvent, QKeySequence
from PyQt5.QtWidgets import QApplication, QMessageBox, QProgressBar, QAction, QWidget, QToolBar

from mtg_proxy_printer.card_info_downloader import CardInfoDownloader
from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.model.imagedb import ImageDatabase
from mtg_proxy_printer.model.document import Document
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
    window_size_changed = pyqtSignal()
    settings_changed = pyqtSignal()
    loading_state_changed = pyqtSignal(bool)

    def __init__(self,
                 card_db: CardDatabase,
                 card_info_downloader: CardInfoDownloader,
                 image_db: ImageDatabase,
                 document: Document,
                 language_model: QStringListModel,
                 *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        logger.info(f"Creating {self.__class__.__name__} instance using the {layout} layout.")
        self.setupUi(self)
        self.about_dialog = self._create_about_dialog()
        self.progress_bar = self._create_progress_bar()
        self.card_database = card_db
        self.image_db = image_db
        self._connect_image_database_signals(image_db)
        self.document = document
        self._connect_document_signals(document)
        self.language_model = language_model
        self.card_data_downloader = card_info_downloader
        self._connect_card_info_downloader_signals(card_info_downloader)
        self.page_view: CurrentPageView
        self._setup_page_view(document)
        self._setup_loading_state_connections()
        self._setup_add_card_widget(card_db, image_db)
        self._setup_document_view(document)
        self.action_new_page.triggered.connect(document.add_page)
        self.should_update_languages.connect(
            lambda: self.language_model.setStringList(self.card_database.get_all_languages())
        )
        self.should_update_languages.connect(self.add_card_widget.update_selected_language)
        self.settings_changed.connect(self.add_card_widget.update_selected_language)
        self.settings_changed.connect(document.apply_settings)
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

    def _setup_page_view(self, document: Document):
        self.page_view: CurrentPageView
        self.page_view.set_document(document)
        self.window_size_changed.connect(self.page_view.window_size_changed)
        self.document.current_page_changed.connect(self.page_view.on_current_page_changed)

    def _setup_loading_state_connections(self):
        for widget_or_action in self._get_widgets_and_actions_disabled_in_loading_state():
            self.loading_state_changed.connect(widget_or_action.setDisabled)

    def _connect_document_signals(self, document: Document):
        document.loading_state_changed.connect(self.loading_state_changed)
        document.loader.loading_file_failed.connect(self.on_document_loading_failed)
        document.loader.unknown_scryfall_ids_found.connect(self.on_document_loading_found_unknown_scryfall_ids)
        document.loader.network_error_occurred.connect(self.on_network_error_occurred)
        document.loading_state_changed.connect(self._select_first_page)
        self.action_new_document.triggered.connect(document.clear_all_data)

    def _connect_card_info_downloader_signals(self, downloader: CardInfoDownloader):
        downloader.download_finished.connect(self.should_update_languages)
        downloader.download_begins.connect(self.show_progress_bar)
        downloader.download_progress.connect(self.progress_bar.setValue)
        downloader.download_finished.connect(self.progress_bar.hide)
        downloader.working_state_changed.connect(self.loading_state_changed)
        downloader.network_error_occurred.connect(self.on_network_error_occurred)
        downloader.other_error_occurred.connect(self.on_error_occurred)

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

    def _connect_image_database_signals(self, image_db: ImageDatabase):
        image_db.card_download_starting.connect(self.show_progress_bar)
        image_db.card_download_finished.connect(self.progress_bar.hide)
        image_db.card_download_progress.connect(self.progress_bar.setValue)
        image_db.batch_processing_state_changed.connect(self.loading_state_changed)
        image_db.network_error_occurred.connect(self.on_network_error_occurred)

    def _create_progress_bar(self):
        progress_bar = QProgressBar(self)
        progress_bar.hide()
        self.statusBar().addPermanentWidget(progress_bar)
        return progress_bar

    def _setup_add_card_widget(self, card_db: CardDatabase, image_db: ImageDatabase):
        self.add_card_widget: AddCardWidget
        self.add_card_widget.set_card_database(card_db)
        self.add_card_widget.card_added.connect(image_db.get_new_card_image_asynchronous)

    def _setup_document_view(self, document: Document):
        self.document_view: DocumentView
        self.document_view.setModel(document)
        self.document_view.selectionModel().currentChanged.connect(document.on_ui_selects_new_page)
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
            self.action_download_card_data.trigger()

    @pyqtSlot()
    def _select_first_page(self, loading_in_progress: bool = False):
        if not loading_in_progress:
            logger.info("Loading finished. Selecting first page.")
            new_selection = self.document.index(0, 0)
            self.document_view.selectionModel().select(new_selection, QItemSelectionModel.Select)
            self.document.on_ui_selects_new_page(new_selection)

    def resizeEvent(self, event: QResizeEvent):
        super(MainWindow, self).resizeEvent(event)
        self.window_size_changed.emit()

    def showEvent(self, event: QShowEvent):
        super(MainWindow, self).showEvent(event)
        self.window_size_changed.emit()

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
        self.action_quit.trigger()

    @pyqtSlot()
    def on_action_quit_triggered(self):
        logger.info(f"User wants to quit.")
        # Prevent a loop, because shutdown() closes this window, causing closeEvent to fire, in turn causing this to be
        # called again. So just disconnect the signal. The connection won’t be needed during application shutdown.
        self.action_quit.triggered.disconnect(self.on_action_quit_triggered)
        self.card_data_downloader.cancel_running_operations()
        self.document.loader.cancel_running_operations()
        self.toolBar: QToolBar
        if self.toolBar.isVisible() != mtg_proxy_printer.settings.settings["gui"].getboolean("show-toolbar"):
            logger.debug("Toolbar visibility setting changed. Updating config and writing new state to disk.")
            mtg_proxy_printer.settings.settings["gui"]["show-toolbar"] = str(self.toolBar.isVisible())
            mtg_proxy_printer.settings.write_settings_to_file()

        QApplication.instance().shutdown()

    @pyqtSlot()
    def on_action_compact_document_triggered(self):
        # TODO: Investigate, why unsetting the model is needed.
        #  The document_view’s selection model somehow asks for data using invalid
        #  indices, when the last page is selected and gets deleted. The only way around seems to be to
        #  completely disconnect the model, remove the row, then set it again.
        self.document_view.setModel(None)
        self.document.compact_pages()
        # Now reset the model (and reconnect the currentChanged signal, which seems to be disconnected implicitly
        self.document_view.setModel(self.document)
        self.document_view.selectionModel().currentChanged.connect(self.document.on_ui_selects_new_page)

    @pyqtSlot()
    def on_action_cleanup_local_image_cache_triggered(self):
        logger.info("User wants to clean up the local image cache")
        wizard = CacheCleanupWizard(self.card_database, self.image_db, self)
        wizard.show()

    @pyqtSlot()
    def on_action_import_deck_list_triggered(self):
        logger.info(f"User imports a deck list.")
        wizard = DeckImportWizard(self.card_database, self.image_db, self.language_model, parent=self)
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

    def on_error_occurred(self, message: str):
        QMessageBox.critical(
            self, "Error",
            f"Operation failed, because an internal error occurred.\n"
            f"Reported error message:\n{message}",
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
                self.on_action_compact_document_triggered()
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

    @pyqtSlot(int)
    def show_progress_bar(self, expected_total_item_count: int):
        self.progress_bar.reset()
        self.progress_bar.setMaximum(expected_total_item_count)
        self.progress_bar.show()

    @pyqtSlot()
    def on_action_discard_page_triggered(self):
        self.document_view: DocumentView
        if self.document.rowCount() == 1:
            logger.info(f"User selects to delete the only page, so clearing it.")
            self.document.clear_page(self.document.index(0, 0))
            return
        to_be_deleted: int = self.document_view.selectedIndexes()[0].row()
        logger.info(f"User selects to delete the currently selected page. Will be removing page {to_be_deleted}")
        logger.debug("Deleting the requested page.")
        # TODO: Investigate, why unsetting the model is needed.
        #  The document_view’s selection model somehow asks for data using invalid
        #  indices, when the last page is selected and gets deleted. The only way around seems to be to
        #  completely disconnect the model, remove the row, then set it again.
        self.document_view.setModel(None)
        self.document.remove_pages([self.document.index(to_be_deleted, 0)])
        # Now reset the model (and reconnect the currentChanged signal, which seems to be disconnected implicitly
        self.document_view.setModel(self.document)
        self.document_view.selectionModel().currentChanged.connect(self.document.on_ui_selects_new_page)

        new_row_index = min(to_be_deleted, self.document.rowCount() - 1)
        logger.debug(f"Selecting page {new_row_index}.")
        new_row_selection = self.document.index(new_row_index, 0)
        self.document_view.selectionModel().select(new_row_selection, QItemSelectionModel.Select)
        self.document.on_ui_selects_new_page(new_row_selection)

    @pyqtSlot()
    def on_action_save_document_triggered(self):
        logger.debug("User clicked on Save")
        if self.document.save_file_path is None:
            logger.debug("No save file path set. Call 'Save as' instead.")
            self.action_save_as.trigger()
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

    def show_application_update_available_message_box(self, newer_version: str):
        QMessageBox.information(
            self, "Update available",
            f"An application update is available: Version {newer_version}\n\n"
            f"You are currently using version {mtg_proxy_printer.meta_data.__version__}.",
            QMessageBox.Ok, QMessageBox.Ok
        )

    def show_card_data_update_available_message_box(self, estimated_card_count: int):
        if QMessageBox.question(
                    self, "New card data available",
                    f"There are {estimated_card_count} new cards available on Scryfall. Update the local data now?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
                ) == QMessageBox.Yes:
            self.action_download_card_data.trigger()
        else:
            # If the user declines to perform the update now, allow them to perform it later by enabling the action.
            self.action_download_card_data.setEnabled(True)

    def ask_user_about_application_update_policy(self) -> bool:
        """Executed on start when the application update policy setting is set to None, the default value."""
        name = mtg_proxy_printer.meta_data.PROGRAMNAME
        return self._ask_user_about_update_policy(
            title="Check for application updates?",
            question=f"Automatically check for application updates whenever you start {name}?",
            logger_message="Application update policy set.",
            settings_key="check-for-application-updates"
        )

    def ask_user_about_card_data_update_policy(self) -> bool:
        """Executed on start when the card data update policy setting is set to None, the default value."""
        name = mtg_proxy_printer.meta_data.PROGRAMNAME
        return self._ask_user_about_update_policy(
            title="Check for card data updates?",
            question=f"Automatically check for card data updates on Scryfall whenever you start {name}?",
            logger_message="Card data update policy set.",
            settings_key="check-for-card-data-updates"
        )

    def _ask_user_about_update_policy(self, title: str, question: str, logger_message: str, settings_key: str) -> bool:
        if (result := QMessageBox.question(
                self, title,
                f"{question}\nYou can change this later in the settings.",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                )) in {QMessageBox.Yes, QMessageBox.No}:
            logger.info(f"{logger_message} User choice: {'Yes' if result == QMessageBox.Yes else 'No'}")
            mtg_proxy_printer.settings.settings["application"][settings_key] = str(
                result == QMessageBox.Yes)
            mtg_proxy_printer.settings.write_settings_to_file()
            logger.debug("Written settings to disk.")
            return True
        return False
