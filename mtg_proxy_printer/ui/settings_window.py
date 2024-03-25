# Copyright (C) 2020-2024 Thomas Hess <thomas.hess@udo.edu>
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
import configparser
import pathlib
import typing

from PyQt5.QtCore import QStringListModel, pyqtSignal as Signal, Qt, QItemSelectionModel, QEvent, QObject
from PyQt5.QtWidgets import QDialogButtonBox, QMessageBox, QWidget, QDialog
from PyQt5.QtGui import QIcon, QStandardItemModel, QResizeEvent

import mtg_proxy_printer.app_dirs
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.document_controller import DocumentAction
from mtg_proxy_printer.document_controller.edit_document_settings import ActionEditDocumentSettings

import mtg_proxy_printer.settings
from mtg_proxy_printer.logger import get_logger
from mtg_proxy_printer.ui.settings_window_pages import Page, HidePrintingsPage

try:
    from mtg_proxy_printer.ui.generated.settings_window.settings_window import Ui_SettingsWindow
except ModuleNotFoundError:
    from mtg_proxy_printer.ui.common import load_ui_from_file
    Ui_SettingsWindow = load_ui_from_file("settings_window/settings_window")


logger = get_logger(__name__)
del get_logger
MessageBoxButton = QMessageBox.StandardButton
DialogBoxButton = QDialogButtonBox.StandardButton
ItemDataRole = Qt.ItemDataRole
ClearAndSelect = QItemSelectionModel.SelectionFlag.ClearAndSelect
TALL_LAYOUT_THRESHOLD = 750

__all__ = [
    "SettingsWindow",
]


class HoverEventFilter(QObject):
    def __init__(self, settings: configparser.ConfigParser, parent: "SettingsWindow"):
        super().__init__(parent)
        self.settings = settings

    def eventFilter(self, object_, event: QEvent):
        event_type = event.type()
        # This check avoids a crash during application shutdown
        if event_type not in {QEvent.HoverEnter, QEvent.HoverLeave}:
            return False
        parent: "SettingsWindow" = self.parent()
        if event_type == QEvent.HoverEnter:
            parent.highlight_differing_settings(self.settings)
        elif event_type == QEvent.HoverLeave:
            parent.clear_highlight()
        return False


class SettingsWindow(QDialog):
    """Implements the Settings window."""
    saved = Signal()
    preferred_language_changed = Signal(str)
    document_settings_updated = Signal(DocumentAction)
    error_occurred = Signal(str)
    requested_card_download = Signal(pathlib.Path)
    long_running_process_begins = Signal(int, str)
    process_updated = Signal(int)
    process_finished = Signal()

    def __init__(self, language_model: QStringListModel, document: Document, parent: QWidget = None):
        super().__init__(parent)
        self.language_model = language_model
        self.document = document
        self.ui = ui = Ui_SettingsWindow()
        ui.setupUi(self)
        ui.debug_settings_page.requested_card_download.connect(self.requested_card_download)
        self.pages_model = self._setup_pages_model(ui)
        ui.general_settings_page.set_language_model(language_model)
        self._setup_hide_printing_page(ui.hide_printings_page, document.card_db)
        self._setup_button_box()
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _setup_pages_model(self, ui: Ui_SettingsWindow) -> QStandardItemModel:
        model = QStandardItemModel(self)
        # Create the model entries for each page, in the order they are stacked.
        pages: typing.List[Page] = [ui.stacked_pages.widget(index) for index in range(ui.stacked_pages.count())]
        for page in pages:
            model.appendRow(page.display_item())

        # Set the models
        ui.page_selection_list_view.setModel(model)
        ui.page_selection_combo_box.setModel(model)
        ui.page_selection_list_view.setSelectionMode(ui.page_selection_list_view.SelectionMode.SingleSelection)
        first_page = model.index(0, 0)
        selection_model = ui.page_selection_list_view.selectionModel()
        selection_model.select(first_page, ClearAndSelect)
        # Connect the list view selection model and the combo box with the page stack
        selection_model.currentRowChanged.connect(lambda current, _: ui.stacked_pages.setCurrentIndex(current.row()))
        ui.page_selection_combo_box.currentIndexChanged.connect(ui.stacked_pages.setCurrentIndex)

        # Sync selections of both page list views
        selection_model.currentRowChanged.connect(
            lambda current, _: ui.page_selection_combo_box.setCurrentIndex(current.row()))
        ui.page_selection_combo_box.currentIndexChanged.connect(
            lambda row: selection_model.setCurrentIndex(model.index(row, 0), ClearAndSelect))

        return model

    def _setup_hide_printing_page(self, page: HidePrintingsPage, card_db):
        page.card_db = card_db
        page.error_occurred.connect(self.error_occurred)
        page.long_running_process_begins.connect(self.long_running_process_begins)
        page.process_updated.connect(self.process_updated)
        page.process_finished.connect(self.process_finished)

    def _setup_button_box(self):
        button_box = self.ui.button_box

        restore_defaults = button_box.button(DialogBoxButton.RestoreDefaults)
        restore_defaults.clicked.connect(self.restore_defaults)
        restore_defaults.installEventFilter(HoverEventFilter(mtg_proxy_printer.settings.DEFAULT_SETTINGS, self))

        reset = button_box.button(DialogBoxButton.Reset)
        reset.clicked.connect(self.reset)
        reset.installEventFilter(HoverEventFilter(mtg_proxy_printer.settings.settings, self))

        buttons_with_icons = [
            (DialogBoxButton.Reset, "edit-undo"),
            (DialogBoxButton.Save, "document-save"),
            (DialogBoxButton.Cancel, "dialog-cancel"),
            (DialogBoxButton.RestoreDefaults, "document-revert"),
        ]
        for role, icon in buttons_with_icons:
            button = button_box.button(role)
            if button.icon().isNull():
                button.setIcon(QIcon.fromTheme(icon))

    def show(self):
        logger.info("Show the settings window.")
        self.load_settings(mtg_proxy_printer.settings.settings)
        self._adapt_layout_to_size(self.size())
        super().show()

    def resizeEvent(self, a0: QResizeEvent):
        self._adapt_layout_to_size(a0.size())
        super().resizeEvent(a0)

    def highlight_differing_settings(self, setting: configparser.ConfigParser):
        for page in self._get_pages():
            page.highlight_differing_settings(setting)

    def clear_highlight(self):
        for page in self._get_pages():
            page.clear_highlight()

    def _adapt_layout_to_size(self, size):
        is_narrow = size.width() < TALL_LAYOUT_THRESHOLD
        self.ui.page_selection_list_view.setHidden(is_narrow)
        self.ui.page_selection_combo_box.setVisible(is_narrow)

    def _get_pages(self) -> typing.Sequence[Page]:
        ui = self.ui
        return [ui.stacked_pages.widget(index) for index in range(ui.stacked_pages.count())]


    def load_settings(self, settings: configparser.ConfigParser):
        logger.debug("Loading the settings")
        for page in self._get_pages():
            page.load(settings)
        logger.debug("Finished loading settings")

    def accept(self):
        """Automatically called when the user hits the "Save" button."""
        logger.info("User wants to save the settings.")
        old_preferred_language = mtg_proxy_printer.settings.settings["images"]["preferred-language"]
        new_preferred_language = self.ui.general_settings_page.ui.preferred_language_combo_box.currentText()
        if old_preferred_language != new_preferred_language:
            self.preferred_language_changed.emit(new_preferred_language)
        current_document_layout = self.document.page_layout
        new_default_layout = self.ui.default_document_layout_page.ui.page_configuration_group_box.page_layout
        if current_document_layout != new_default_layout and QMessageBox.question(
                self, "Apply settings to the current document?",
                "The new default settings differ from the settings used by the current document.\n"
                "Apply the new settings to the current document?",
                MessageBoxButton.Yes | MessageBoxButton.No, MessageBoxButton.Yes
        ) == MessageBoxButton.Yes:
            logger.info("User applies changed document settings to the current document")
            self.document_settings_updated.emit(ActionEditDocumentSettings(new_default_layout))
        self.save()
        super().accept()

    def reset(self):
        logger.debug("User clicked the reset button.")
        scope_question = QMessageBox(
            QMessageBox.Icon.Question,
            "Reset unsaved changes?",
            "Reset unsaved changes on the current page or on all pages?",
            MessageBoxButton.YesToAll | MessageBoxButton.Yes | MessageBoxButton.Cancel,
            self)
        scope_question.button(MessageBoxButton.YesToAll).setText("Reset everything")
        scope_question.button(MessageBoxButton.Yes).setText("Reset current page")
        if (result := scope_question.exec()) == MessageBoxButton.YesToAll:
            logger.info("User resets changes made on all pages.")
            self.load_settings(mtg_proxy_printer.settings.settings)
            self.clear_highlight()
        elif result == MessageBoxButton.Yes:
            logger.info("User resets changes made on the current page.")
            self.ui.stacked_pages.currentWidget().load(mtg_proxy_printer.settings.settings)
            self.clear_highlight()

    def reject(self):
        """Automatically called when the user hits the "Cancel" button or closes the settings window."""
        logger.info("User closes the settings dialog. This will reset any made changes.")
        self.load_settings(mtg_proxy_printer.settings.settings)
        super().reject()

    def save(self):
        logger.info("User saves the configuration to disk.")
        for page in self._get_pages():
            page.save()
        logger.debug("Settings read from UI widgets, about to write the configuration to disk.")
        mtg_proxy_printer.settings.write_settings_to_file()
        self.saved.emit()
        logger.debug("Save finished.")

    def restore_defaults(self):
        logger.debug("User clicked the 'Restore Defaults' button.")
        scope_question = QMessageBox(
            QMessageBox.Icon.Question,
            "Restore defaults for the current page or everything?",
            "Restore the settings on the current page or on all pages to their default values?",
            MessageBoxButton.YesToAll | MessageBoxButton.Yes | MessageBoxButton.Cancel,
            self)
        scope_question.button(MessageBoxButton.YesToAll).setText("Restore everything")
        scope_question.button(MessageBoxButton.Yes).setText("Restore current page")
        if (result := scope_question.exec()) == MessageBoxButton.YesToAll:
            logger.info("User reverts all pages to their default values.")
            self.load_settings(mtg_proxy_printer.settings.DEFAULT_SETTINGS)
            self.clear_highlight()
        elif result == MessageBoxButton.Yes:
            logger.info("User reverts the current page to the default values.")
            self.ui.stacked_pages.currentWidget().load(mtg_proxy_printer.settings.DEFAULT_SETTINGS)
            self.clear_highlight()
        logger.debug("Loaded DEFAULT_SETTINGS.")
