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

from PyQt5.QtCore import pyqtSlot as Slot, pyqtSignal as Signal, QStringListModel, QUrl
from PyQt5.QtGui import QCloseEvent, QKeySequence, QDesktopServices
from PyQt5.QtWidgets import QApplication, QMessageBox, QProgressBar, QAction, QWidget, QLabel, QMainWindow, QDialog


from mtg_proxy_printer.missing_images_manager import MissingImagesManager
from mtg_proxy_printer.card_info_downloader import CardInfoDownloader
from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.model.imagedb import ImageDatabase
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.document_controller.compact_document import ActionCompactDocument
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage, ActionRemovePage
from mtg_proxy_printer.document_controller.shuffle_document import ActionShuffleDocument
from mtg_proxy_printer.document_controller.new_document import ActionNewDocument
import mtg_proxy_printer.settings
import mtg_proxy_printer.print
from mtg_proxy_printer.ui.dialogs import SavePDFDialog, SaveDocumentAsDialog, LoadDocumentDialog, \
    AboutMTGProxyPrinterDialog, PrintPreviewDialog, PrintDialog, DocumentSettingsDialog
from mtg_proxy_printer.ui.cache_cleanup_wizard import CacheCleanupWizard
from mtg_proxy_printer.ui.deck_import_wizard import DeckImportWizard

try:
    from mtg_proxy_printer.ui.generated.main_window import Ui_main_window as Ui_MainWindow
except ModuleNotFoundError:
    from mtg_proxy_printer.ui.common import load_ui_from_file
    Ui_MainWindow = load_ui_from_file("main_window")

from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger
__all__ = [
    "MainWindow",
]


class MainWindow(QMainWindow):

    should_update_languages = Signal()
    loading_state_changed = Signal(bool)

    def __init__(self,
                 card_db: CardDatabase,
                 card_info_downloader: CardInfoDownloader,
                 image_db: ImageDatabase,
                 document: Document,
                 language_model: QStringListModel,
                 *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        logger.info(f"Creating {self.__class__.__name__} instance.")
        self.is_running = True
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.default_undo_tooltip = self.ui.action_undo.toolTip()
        self.default_redo_tooltip = self.ui.action_redo.toolTip()
        self.missing_images_manager = MissingImagesManager(document, self)
        self.missing_images_manager.request_obtaining_images.connect(image_db.download_worker.obtain_missing_images)
        self.missing_images_manager.obtaining_missing_images_failed.connect(self.on_network_error_occurred)
        self.about_dialog = self._create_about_dialog()
        self.progress_label = self._create_progress_label()
        self.progress_bar = self._create_progress_bar()
        self.card_database = card_db
        self.image_db = image_db
        self._connect_image_database_signals(image_db)
        self.document = document
        self._connect_document_signals(document)
        self.language_model = language_model
        self.card_data_downloader = card_info_downloader
        self._connect_card_info_downloader_signals(card_info_downloader)
        self._setup_central_widget()
        self._setup_loading_state_connections()
        self._setup_undo_redo_actions(document)
        self.should_update_languages.connect(
            lambda: self.language_model.setStringList(self.card_database.get_all_languages())
        )
        self.ui.action_show_toolbar.setChecked(mtg_proxy_printer.settings.settings["gui"].getboolean("show-toolbar"))
        self._setup_platform_dependent_default_shortcuts()
        self.current_dialog: typing.Optional[QDialog] = None
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _create_about_dialog(self) -> AboutMTGProxyPrinterDialog:
        about_dialog = AboutMTGProxyPrinterDialog(self)
        self.ui.action_show_about_dialog.triggered.connect(about_dialog.show_about)
        self.ui.action_show_changelog.triggered.connect(about_dialog.show_changelog)
        return about_dialog

    def _setup_platform_dependent_default_shortcuts(self):
        actions_with_shortcuts: typing.List[typing.Tuple[QAction, QKeySequence.StandardKey]] = [
            (self.ui.action_new_document, QKeySequence.New),
            (self.ui.action_load_document, QKeySequence.Open),
            (self.ui.action_save_document, QKeySequence.Save),
            (self.ui.action_save_as, QKeySequence.SaveAs),
            (self.ui.action_show_settings, QKeySequence.Preferences),
            (self.ui.action_print, QKeySequence.Print),
            (self.ui.action_quit, QKeySequence.Quit),
        ]
        for action, shortcut in actions_with_shortcuts:
            action.setShortcut(shortcut)

    def _setup_central_widget(self):
        self.setCentralWidget(self.ui.central_widget)
        self.ui.central_widget.set_data(self.document, self.card_database, self.image_db)

    def _setup_loading_state_connections(self):
        for widget_or_action in self._get_widgets_and_actions_disabled_in_loading_state():
            self.loading_state_changed.connect(widget_or_action.setDisabled)

    def _setup_undo_redo_actions(self, document: Document):
        self.ui.action_undo.triggered.connect(document.undo)
        self.ui.action_redo.triggered.connect(document.redo)
        document.action_applied.connect(self.on_document_action_applied_or_undone)
        document.action_undone.connect(self.on_document_action_applied_or_undone)
        document.undo_available_changed.connect(self.ui.action_undo.setEnabled)
        document.redo_available_changed.connect(self.ui.action_redo.setEnabled)

    def _connect_document_signals(self, document: Document):
        document.loading_state_changed.connect(self.loading_state_changed)
        document.loader.loading_file_failed.connect(self.on_document_loading_failed)
        document.loader.unknown_scryfall_ids_found.connect(self.on_document_loading_found_unknown_scryfall_ids)
        document.loader.network_error_occurred.connect(self.on_network_error_occurred)
        self.ui.action_new_page.triggered.connect(lambda: document.apply(ActionNewPage()))
        self.ui.action_discard_page.triggered.connect(lambda: document.apply(ActionRemovePage()))
        self.ui.action_new_document.triggered.connect(lambda: document.apply(ActionNewDocument()))
        self.ui.action_compact_document.triggered.connect(lambda: document.apply(ActionCompactDocument()))
        self.ui.action_shuffle_document.triggered.connect(lambda: document.apply(ActionShuffleDocument()))

    def _connect_card_info_downloader_signals(self, downloader: CardInfoDownloader):
        # Do not connect the card_info_downloader.working_state_changed
        # signal to not re-enable the action when completed. This action in particular should remain disabled.
        downloader.download_begins.connect(
            lambda: self.ui.action_download_card_data.setDisabled(True)
        )
        self.ui.action_download_card_data.triggered.connect(downloader.request_import_from_url)
        downloader.download_finished.connect(self.should_update_languages)
        downloader.download_begins.connect(self.show_progress_bar)
        downloader.download_progress.connect(self.progress_bar.setValue)
        downloader.download_finished.connect(self.hide_progress_bar)
        downloader.working_state_changed.connect(self.loading_state_changed)
        downloader.network_error_occurred.connect(self.on_network_error_occurred)
        downloader.network_error_occurred.connect(lambda _: self.ui.action_download_card_data.setEnabled(True))
        downloader.other_error_occurred.connect(self.on_error_occurred)
        downloader.other_error_occurred.connect(lambda _: self.ui.action_download_card_data.setEnabled(True))

    def _get_widgets_and_actions_disabled_in_loading_state(self) -> typing.List[typing.Union[QWidget, QAction]]:
        ui = self.ui
        return [
            ui.action_new_document,
            ui.action_save_as,
            ui.action_save_document,
            ui.action_edit_document_settings,
            ui.action_compact_document,
            ui.action_shuffle_document,
            ui.action_load_document,
            ui.action_print,
            ui.action_print_preview,
            ui.action_print_pdf,
            ui.action_import_deck_list,
            ui.action_new_page,
            ui.action_discard_page,
            ui.action_show_settings,
            ui.action_cleanup_local_image_cache,
            ui.central_widget,
        ]

    def _connect_image_database_signals(self, image_db: ImageDatabase):
        image_db.card_download_starting.connect(self.show_progress_bar)
        image_db.card_download_finished.connect(self.hide_progress_bar)
        image_db.card_download_progress.connect(self.progress_bar.setValue)
        image_db.batch_processing_state_changed.connect(self.loading_state_changed)
        image_db.network_error_occurred.connect(self.on_network_error_occurred)

    def _create_progress_label(self):
        progress_label = QLabel(self)
        self.statusBar().addPermanentWidget(progress_label)
        return progress_label

    def _create_progress_bar(self):
        progress_bar = QProgressBar(self)
        progress_bar.hide()
        self.statusBar().addPermanentWidget(progress_bar)
        return progress_bar

    @Slot()
    def on_dialog_finished(self):
        self.current_dialog = None

    @Slot()
    def on_document_action_applied_or_undone(self):
        undo_tooltip = f"Undo:\n{self.document.undo_stack[-1]}" \
            if self.document.undo_stack else self.default_undo_tooltip
        redo_tooltip = f"Redo:\n{self.document.redo_stack[-1]}" \
            if self.document.redo_stack else self.default_redo_tooltip
        self.ui.action_undo.setToolTip(undo_tooltip)
        self.ui.action_redo.setToolTip(redo_tooltip)

    def closeEvent(self, event: QCloseEvent):
        """
        This function is automatically called when the window is closed using the close [X] button in the window
        decorations or by right-clicking in the system window list and using the close action, or similar ways to close
        the window.
        """
        logger.debug("User closed the main window, closing application…")
        event.ignore()
        # Triggering the quit action implicitly closes all windows, thus causes this event to fire during application
        # quit. This check prevents the quit logic from running twice.
        if self.is_running:
            event.ignore()
            self.on_action_quit_triggered()

    @Slot()
    def on_action_quit_triggered(self):
        logger.info(f"User wants to quit.")
        self.is_running = False
        self.card_data_downloader.cancel_running_operations()
        self.card_data_downloader.quit_background_thread()
        self.document.loader.cancel_running_operations()
        self.document.loader.quit_background_thread()
        self.image_db.quit_background_thread()
        if self.ui.toolBar.isVisible() != mtg_proxy_printer.settings.settings["gui"].getboolean("show-toolbar"):
            logger.debug("Toolbar visibility setting changed. Updating config and writing new state to disk.")
            mtg_proxy_printer.settings.settings["gui"]["show-toolbar"] = str(self.ui.toolBar.isVisible())
            mtg_proxy_printer.settings.write_settings_to_file()
        QApplication.instance().quit()

    @Slot()
    def on_action_cleanup_local_image_cache_triggered(self):
        logger.info("User wants to clean up the local image cache")
        wizard = CacheCleanupWizard(self.card_database, self.image_db, self)
        wizard.show()

    @Slot()
    def on_action_import_deck_list_triggered(self):
        logger.info(f"User imports a deck list.")
        wizard = DeckImportWizard(self.card_database, self.image_db, self.language_model, parent=self)
        wizard.request_action.connect(self.image_db.download_worker.fill_batch_document_action_images)
        wizard.show()

    @Slot()
    def on_action_print_triggered(self):
        logger.info(f"User prints the current document.")
        if self._ask_user_about_compacting_document("printing") == QMessageBox.Cancel:
            return
        self.current_dialog = PrintDialog(self.document, self)
        self.current_dialog.finished.connect(self.on_dialog_finished)
        self.missing_images_manager.obtain_missing_images(self.current_dialog.open)

    @Slot()
    def on_action_print_preview_triggered(self):
        logger.info(f"User views the print preview.")
        if self._ask_user_about_compacting_document("printing") == QMessageBox.Cancel:
            return
        self.current_dialog = PrintPreviewDialog(self.document, self)
        self.current_dialog.finished.connect(self.on_dialog_finished)
        self.missing_images_manager.obtain_missing_images(self.current_dialog.open)

    @Slot()
    def on_action_print_pdf_triggered(self):
        logger.info(f"User prints the current document to PDF.")
        if self._ask_user_about_compacting_document("exporting as a PDF") == QMessageBox.Cancel:
            return
        self.current_dialog = SavePDFDialog(self, self.document)
        self.current_dialog.finished.connect(self.on_dialog_finished)
        self.missing_images_manager.obtain_missing_images(self.current_dialog.open)

    def on_network_error_occurred(self, message: str):
        QMessageBox.warning(
            self, "Network error",
            f"Operation failed, because a network error occurred.\n"
            f"Check your internet connection. Reported error message:\n\n{message}",
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
            if (result := QMessageBox.question(
                self, "Saving pages possible",
                f"It is possible to save {savable_pages} pages when printing this document.\n"
                f"Do you want to compact the document now to minimize the page count prior to {action}?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )) == QMessageBox.Yes:
                self.document.apply(ActionCompactDocument())
            return result
        return QMessageBox.No  # No pages can be saved, assume "No" for this case

    def ask_user_about_empty_database(self):
        """
        This is called when the application starts with an empty or no card database. Ask the user if they wish
        to download the card data now. If so, trigger the appropriate action, just as if the user clicked the menu item.
        """
        if QMessageBox.question(
                self, "Download required Card data from Scryfall?",
                "This program requires downloading additional card data from Scryfall to operate the card search.\n"
                "Download the required data from Scryfall now?\n"
                "If you decline now, you can exclude some card types or individual cards based on ban lists "
                "in the settings and then manually start the download later.\n"
                "Or accept and use the current settings.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.Yes:
            self.ui.action_download_card_data.trigger()

    @Slot(int)
    @Slot(int, str)
    def show_progress_bar(self, expected_total_item_count: int, message: str = ""):
        self.progress_label.setText(message)
        self.progress_bar.reset()
        self.progress_bar.setMaximum(expected_total_item_count)
        self.progress_bar.show()

    @Slot()
    def hide_progress_bar(self):
        self.progress_label.clear()
        self.progress_bar.reset()
        self.progress_bar.hide()

    @Slot()
    def on_action_save_document_triggered(self):
        logger.debug("User clicked on Save")
        if self.document.save_file_path is None:
            logger.debug("No save file path set. Call 'Save as' instead.")
            self.ui.action_save_as.trigger()
        else:
            logger.debug("About to save the document")
            self.document.save_to_disk()
            logger.debug("Saved.")

    @Slot()
    def on_action_edit_document_settings_triggered(self):
        logger.info("User wants to edit the document settings. Showing the editor dialog")
        self.current_dialog = DocumentSettingsDialog(self.document, self)
        self.current_dialog.finished.connect(self.on_dialog_finished)
        self.current_dialog.open()

    @Slot()
    def on_action_download_missing_card_images_triggered(self):
        logger.info("User wants to download missing card images")
        self.missing_images_manager.obtain_missing_images()

    @Slot()
    def on_action_save_as_triggered(self):
        self.current_dialog = SaveDocumentAsDialog(self.document, self)
        self.current_dialog.finished.connect(self.on_dialog_finished)
        self.current_dialog.open()

    @Slot()
    def on_action_load_document_triggered(self):
        self.current_dialog = LoadDocumentDialog(self, self.document)
        self.current_dialog.accepted.connect(self.ui.central_widget.select_first_page)
        self.current_dialog.finished.connect(self.on_dialog_finished)
        self.current_dialog.open()

    def on_document_loading_failed(self, failed_path: pathlib.Path, reason: str):
        QMessageBox.critical(
            self, "Document loading failed",
            f"Loading file \"{failed_path}\" failed. The file was not recognized as an "
            f"{mtg_proxy_printer.meta_data.PROGRAMNAME} document. If you want to load a deck list, use the "
            f"\"{self.ui.action_import_deck_list.text()}\" function instead.\n"
            f"Reported failure reason: {reason}",
            QMessageBox.Ok, QMessageBox.Ok
        )

    def on_document_loading_found_unknown_scryfall_ids(self, unknown: int, replaced: int):
        if replaced:
            QMessageBox.warning(
                self, "Unavailable printings replaced",
                f"The document contained {replaced} unavailable printings of cards that were automatically replaced "
                f"with other printings. The replaced printings are unavailable, "
                f"because they match a configured download filter."
            )
        if unknown:
            QMessageBox.warning(
                self, "Unrecognized cards in loaded document found",
                f"Skipped {unknown} unrecognized cards in the loaded document. "
                f"Saving the document will remove these entries permanently.\n\nThe locally stored card "
                f"data may be outdated or the document was tampered with.",
                QMessageBox.Ok, QMessageBox.Ok
            )

    def show_application_update_available_message_box(self, newer_version: str):
        if QMessageBox.question(
                self, "Application update available. Visit website?",
                f"An application update is available: Version {newer_version}\n"
                f"You are currently using version {mtg_proxy_printer.meta_data.__version__}.\n\n"
                f"Open the {mtg_proxy_printer.meta_data.PROGRAMNAME} website in your webbrowser "
                f"to download the new version?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                ) == QMessageBox.Yes:
            url = QUrl(mtg_proxy_printer.meta_data.DOWNLOAD_WEB_PAGE, QUrl.StrictMode)
            QDesktopServices.openUrl(url)

    def show_card_data_update_available_message_box(self, estimated_card_count: int):
        if QMessageBox.question(
                    self, "New card data available",
                    f"There are {estimated_card_count} new printings available on Scryfall. Update the local data now?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
                ) == QMessageBox.Yes:
            logger.info("User agreed to update the card data from Scryfall. Performing update")
            self.ui.action_download_card_data.trigger()
        else:
            # If the user declines to perform the update now, allow them to perform it later by enabling the action.
            self.ui.action_download_card_data.setEnabled(True)

    def ask_user_about_application_update_policy(self):
        """Executed on start when the application update policy setting is set to None, the default value."""
        name = mtg_proxy_printer.meta_data.PROGRAMNAME
        self._ask_user_about_update_policy(
            title="Check for application updates?",
            question=f"Automatically check for application updates whenever you start {name}?",
            logger_message="Application update policy set.",
            settings_key="check-for-application-updates"
        )

    def ask_user_about_card_data_update_policy(self):
        """Executed on start when the card data update policy setting is set to None, the default value."""
        name = mtg_proxy_printer.meta_data.PROGRAMNAME
        self._ask_user_about_update_policy(
            title="Check for card data updates?",
            question=f"Automatically check for card data updates on Scryfall whenever you start {name}?",
            logger_message="Card data update policy set.",
            settings_key="check-for-card-data-updates"
        )

    def _ask_user_about_update_policy(self, title: str, question: str, logger_message: str, settings_key: str):
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
