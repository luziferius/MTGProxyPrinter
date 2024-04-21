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
import logging
from functools import partial
import pathlib
import typing
from abc import abstractmethod

from PyQt5.QtCore import pyqtSignal as Signal, pyqtSlot as Slot, QUrl, QStandardPaths, QStringListModel, Qt, QThreadPool
from PyQt5.QtGui import QDesktopServices, QStandardItem, QIcon
from PyQt5.QtWidgets import QWidget, QCheckBox, QFileDialog, QMessageBox, QApplication, QLineEdit

import mtg_proxy_printer.app_dirs
import mtg_proxy_printer.settings
from mtg_proxy_printer.printing_filter_updater import PrintingFilterUpdater
from mtg_proxy_printer.logger import get_logger
from mtg_proxy_printer.ui.common import highlight_widget
from mtg_proxy_printer.units_and_sizes import OptStr

if typing.TYPE_CHECKING:
    from mtg_proxy_printer.application import Application

try:
    from mtg_proxy_printer.ui.generated.settings_window.debug_settings_page import Ui_DebugSettingsPage
    from mtg_proxy_printer.ui.generated.settings_window.decklist_import_settings_page \
        import Ui_DecklistImportSettingsPage
    from mtg_proxy_printer.ui.generated.settings_window.general_settings_page import Ui_GeneralSettingsPage
    from mtg_proxy_printer.ui.generated.settings_window.hide_printings_page import Ui_HidePrintingsPage
    from mtg_proxy_printer.ui.generated.settings_window.default_document_layout_settings_page \
        import Ui_DefaultDocumentLayoutSettingsPage
    from mtg_proxy_printer.ui.generated.settings_window.printer_settings_page import Ui_PrinterSettingsPage
    from mtg_proxy_printer.ui.generated.settings_window.pdf_settings_page import Ui_PDFSettingsPage
except ModuleNotFoundError:
    from mtg_proxy_printer.ui.common import load_ui_from_file
    Ui_DebugSettingsPage = load_ui_from_file("settings_window/debug_settings_page")
    Ui_DecklistImportSettingsPage = load_ui_from_file("settings_window/decklist_import_settings_page")
    Ui_GeneralSettingsPage = load_ui_from_file("settings_window/general_settings_page")
    Ui_HidePrintingsPage = load_ui_from_file("settings_window/hide_printings_page")
    Ui_DefaultDocumentLayoutSettingsPage = load_ui_from_file("settings_window/default_document_layout_settings_page")
    Ui_PrinterSettingsPage = load_ui_from_file("settings_window/printer_settings_page")
    Ui_PDFSettingsPage = load_ui_from_file("settings_window/pdf_settings_page")

CheckState = Qt.CheckState
bool_to_check_state: typing.Dict[typing.Optional[bool], CheckState] = {
    True: CheckState.Checked,
    False: CheckState.Unchecked,
    None: CheckState.PartiallyChecked,
}
check_state_to_bool_str: typing.Dict[CheckState, str] = {v: str(k) for k, v in bool_to_check_state.items()}
QueuedConnection = Qt.ConnectionType.QueuedConnection
logger = get_logger(__name__)
del get_logger

class PageMetadata(typing.NamedTuple):
    text: str
    icon_name: OptStr
    tooltip: OptStr = None


class Page(QWidget):
    """The base class for settings page widgets. Defines the API used by the settings window"""

    def display_item(self) -> typing.Sequence[QStandardItem]:
        data = self.display_metadata
        item = QStandardItem(data.text)
        if data.icon_name:
            item.setIcon(QIcon.fromTheme(data.icon_name))
        if data.tooltip:
            item.setToolTip(data.tooltip)
        size = item.sizeHint()
        size.setHeight(32)
        item.setSizeHint(size)
        return item,

    @property
    @abstractmethod
    def display_metadata(self) -> PageMetadata:
        return PageMetadata("FIXME: FILL DATA", None, "FIXME: FILL DATA")

    @abstractmethod
    def save(self):
        """Saves the GUI state into the global application settings"""
        pass

    @abstractmethod
    def load(self, settings: configparser.ConfigParser):
        """Loads the GUI state based on the given settings. This is used to load, reset, and revert settings."""
        pass

    @abstractmethod
    def highlight_differing_settings(self, settings: configparser.ConfigParser):
        """Highlights GUI widgets with a state different from the given settings"""
        pass

    def clear_highlight(self):
        """Clears all GUI widget highlights."""
        for item in self.findChildren((QWidget,), options=Qt.FindChildOption.FindChildrenRecursively):  # type: QWidget
            item.setGraphicsEffect(None)


class DebugSettingsPage(Page):

    requested_card_download = Signal(pathlib.Path)
    display_metadata = PageMetadata("Debug settings", None, "Things useful for investigating bugs in the application")

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = ui = Ui_DebugSettingsPage()
        ui.setupUi(self)
        self.requested_card_download.connect(lambda _: ui.debug_download_card_data_as_file.setEnabled(False))
        ui.log_level_combo_box.addItems(map(logging.getLevelName, range(10, 60, 10)))
        url = QUrl("https://github.com/busimus/cutelog", QUrl.ParsingMode.StrictMode)
        ui.open_cutelog_website_button.clicked.connect(partial(QDesktopServices.openUrl, url))

    def load(self, settings: configparser.ConfigParser):
        section = settings["debug"]
        for widget, setting in self._get_debug_settings_checkbox_widgets():
            widget.setChecked(section.getboolean(setting))
        log_level_combo_box = self.ui.log_level_combo_box
        configured_level_index = log_level_combo_box.findText(section["log-level"])
        log_level_combo_box.setCurrentIndex(configured_level_index)

    def save(self):
        debug_section = mtg_proxy_printer.settings.settings["debug"]
        for widget, setting in self._get_debug_settings_checkbox_widgets():
            debug_section[setting] = str(widget.isChecked())
        debug_section["log-level"] = self.ui.log_level_combo_box.currentText()

    def highlight_differing_settings(self, settings: configparser.ConfigParser):
        section = settings["debug"]
        for widget, setting in self._get_debug_settings_checkbox_widgets():
            if widget.isChecked() != section.getboolean(setting):
                highlight_widget(widget)
        debug_combo_box = self.ui.log_level_combo_box
        if debug_combo_box.currentText() != section["log-level"]:
            highlight_widget(debug_combo_box)

    def _get_debug_settings_checkbox_widgets(self):
        ui = self.ui
        widgets_with_settings: typing.List[typing.Tuple[QCheckBox, str]] = [
            (ui.enable_cutelog_integration, "cutelog-integration"),
            (ui.enable_write_log_file, "write-log-file")
        ]
        return widgets_with_settings

    @Slot()
    def on_open_debug_log_location_clicked(self):
        logger.debug("About to open the log directory using the default file manager.")
        log_dir = mtg_proxy_printer.app_dirs.data_directories.user_log_dir
        log_url = QUrl.fromLocalFile(log_dir)
        QDesktopServices.openUrl(log_url)

    @Slot()
    def on_debug_download_card_data_as_file_clicked(self):
        logger.debug("User about to download the card data from Scryfall to a file.")
        location = QFileDialog.getExistingDirectory(
            self, "Select download location",
            QStandardPaths.locate(QStandardPaths.DownloadLocation, "", QStandardPaths.LocateDirectory))
        if not location:
            logger.debug("User cancelled location selection. Not downloading.")
            return
        if not (path := pathlib.Path(location)).is_dir():
            logger.warning("User selected something that is not a directory. Aborting.")
            QMessageBox.critical(
                self, "Selected location is not a directory",
                f"Cannot write the card data at the given location, because it is not a directory:\n{location}",
                QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
            return
        logger.info(f"Download card data to file {path}")
        self.requested_card_download.emit(path)

    @Slot()
    def on_debug_import_card_data_from_file_clicked(self):
        logger.debug("User about to import card tata from a previously downloaded file.")
        location, _ = QFileDialog.getOpenFileName(
            self, "Import previously downloaded card data obtained from Scryfall",
            QStandardPaths.locate(QStandardPaths.DownloadLocation, "", QStandardPaths.LocateDirectory),
            "Scryfall card data (*.json, *.json.gz)")
        logger.info(f"{location=}")
        if not location:
            logger.debug("User cancelled file selection. Not importing.")
            return
        if not (path := pathlib.Path(location)).is_file():
            logger.warning("User selected something that is not a file. Aborting.")
            QMessageBox.critical(
                self, "Selected location is not a file",
                f"Cannot find the selected file:\n{location}",
                QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
            return
        logger.info(f"Import card data from {path}")
        app: "Application" = QApplication.instance()
        app.card_info_downloader.import_from_file(path)


class DecklistImportSettingsPage(Page):
    display_metadata = PageMetadata("Deck list import", "edit-download", "Configure the deck list importer")

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = ui = Ui_DecklistImportSettingsPage()
        ui.setupUi(self)

    @Slot()
    def on_deck_list_search_path_browse_button_clicked(self):
        logger.debug("User about to select a new default deck list search path.")
        if location := QFileDialog.getExistingDirectory(self, "Select default deck list search path"):
            logger.info("User selected a new default deck list search path.")
            self.ui.deck_list_search_path.setText(location)

    def load(self, settings: configparser.ConfigParser):
        section = settings["decklist-import"]
        for widget, setting in self._get_checkbox_widgets():
            widget.setChecked(section.getboolean(setting))

        section = settings["default-filesystem-paths"]
        widgets_with_settings = self._get_save_path_settings_widgets()
        for widget, setting in widgets_with_settings:
            widget.setText(section[setting])

    def save(self):
        section = mtg_proxy_printer.settings.settings["decklist-import"]
        for widget, setting in self._get_checkbox_widgets():
            section[setting] = str(widget.isChecked())

        section = mtg_proxy_printer.settings.settings["default-filesystem-paths"]
        for widget, setting in self._get_save_path_settings_widgets():
            section[setting] = widget.text()

    def _get_checkbox_widgets(self):
        ui = self.ui
        widgets_with_settings: typing.List[typing.Tuple[QCheckBox, str]] = [
            (ui.print_guessing_enable, "enable-print-guessing-by-default"),
            (ui.print_guessing_prefer_already_downloaded, "prefer-already-downloaded-images"),
            (ui.automatic_deck_list_translation_enable, "always-translate-deck-lists"),
            (ui.remove_basic_wastes_enable, "remove-basic-wastes"),
            (ui.remove_snow_basics_enable, "remove-snow-basics"),
        ]
        return widgets_with_settings

    def _get_save_path_settings_widgets(self):
        ui = self.ui
        widgets_with_settings: typing.List[typing.Tuple[QLineEdit, str]] = [
            (ui.deck_list_search_path, "deck-list-search-path"),
        ]
        return widgets_with_settings

    def highlight_differing_settings(self, settings: configparser.ConfigParser):
        section = mtg_proxy_printer.settings.settings["decklist-import"]
        for widget, setting in self._get_checkbox_widgets():
            if widget.isChecked() != section.getboolean(setting):
                highlight_widget(widget)

        section = mtg_proxy_printer.settings.settings["default-filesystem-paths"]
        for widget, setting in self._get_save_path_settings_widgets():
            if widget.text() != section[setting]:
                highlight_widget(widget)


class GeneralSettingsPage(Page):
    display_metadata = PageMetadata("General settings", "configure")

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = ui = Ui_GeneralSettingsPage()
        self.language_model = QStringListModel([], self)
        ui.setupUi(self)
        ui.add_card_widget_style_combo_box.addItem("Horizontal layout", "horizontal")
        ui.add_card_widget_style_combo_box.addItem("Columnar layout", "columnar")
        ui.add_card_widget_style_combo_box.addItem("Tabbed layout", "tabbed")

    def set_language_model(self, model: QStringListModel):
        self.language_model = model
        self.ui.preferred_language_combo_box.setModel(model)

    @Slot()
    def on_document_save_path_browse_button_clicked(self):
        logger.debug("User about to select a new default document save path.")
        if location := QFileDialog.getExistingDirectory(self, "Select default save location"):
            logger.info("User selected a new default document save path.")
            self.ui.document_save_path.setText(location)

    def load(self, settings: configparser.ConfigParser):
        self._load_layout_settings(settings)
        self._load_update_settings(settings)
        self._load_images_settings(settings)
        self._load_path_settings(settings)

    def _load_layout_settings(self, settings: configparser.ConfigParser):
        ui = self.ui
        gui_section = settings["gui"]
        search_layout_index = ui.add_card_widget_style_combo_box.findData(gui_section["central-widget-layout"])
        ui.add_card_widget_style_combo_box.setCurrentIndex(search_layout_index)

    def _load_update_settings(self, settings: configparser.ConfigParser):
        application_section = settings["application"]
        for widget, setting in self._get_update_check_settings_widgets():
            widget.setCheckState(bool_to_check_state[application_section.getboolean(setting)])

    def _load_images_settings(self, settings: configparser.ConfigParser):
        images_section = settings["images"]
        preferred_language_combo_box = self.ui.preferred_language_combo_box
        preferred_language = images_section.get("preferred-language")
        if not (known := preferred_language_combo_box.model().stringList()) or preferred_language not in known:
            preferred_language_combo_box.addItem(preferred_language)
        preferred_language_combo_box.setCurrentIndex(self.get_index_for_language_code(preferred_language))
        self.ui.automatically_add_opposing_faces.setChecked(
            images_section.getboolean("automatically-add-opposing-faces")
        )

    def _load_path_settings(self, settings: configparser.ConfigParser):
        section = settings["default-filesystem-paths"]
        widgets_with_settings = self._get_save_path_settings_widgets()
        for widget, setting in widgets_with_settings:
            widget.setText(section[setting])

    def _get_update_check_settings_widgets(self):
        ui = self.ui
        widgets_with_settings: typing.List[typing.Tuple[QCheckBox, str]] = [
            (ui.check_application_updates_enabled, "check-for-application-updates"),
            (ui.check_card_data_updates_enabled, "check-for-card-data-updates"),
        ]
        return widgets_with_settings

    def get_index_for_language_code(self, language: str) -> int:
        languages = self.language_model.stringList()
        if language in languages:
            return languages.index(language)
        else:
            return languages.index("en")

    def save(self):
        self._save_update_check_settings()
        self._save_look_and_feel_settings()
        self._save_images_settings()
        self._save_path_settings()

    def _save_update_check_settings(self):
        section = mtg_proxy_printer.settings.settings["application"]
        for widget, setting in self._get_update_check_settings_widgets():
            section[setting] = check_state_to_bool_str[widget.checkState()]

    def _save_look_and_feel_settings(self):
        section = mtg_proxy_printer.settings.settings["gui"]
        section["central-widget-layout"] = self.ui.add_card_widget_style_combo_box.currentData(
            Qt.ItemDataRole.UserRole)

    def _save_images_settings(self):
        section = mtg_proxy_printer.settings.settings["images"]
        section["preferred-language"] = self.ui.preferred_language_combo_box.currentText()
        section["automatically-add-opposing-faces"] = str(self.ui.automatically_add_opposing_faces.isChecked())

    def _save_path_settings(self):
        section = mtg_proxy_printer.settings.settings["default-filesystem-paths"]
        widgets_and_settings = self._get_save_path_settings_widgets()
        for widget, setting in widgets_and_settings:
            section[setting] = widget.text()

    def highlight_differing_settings(self, settings: configparser.ConfigParser):
        ui = self.ui

        section = settings["application"]
        for widget, setting in self._get_update_check_settings_widgets():
            if section[setting] != check_state_to_bool_str[widget.checkState()]:
                highlight_widget(widget)

        section = settings["gui"]
        if section["central-widget-layout"] != ui.add_card_widget_style_combo_box.currentData(
                Qt.ItemDataRole.UserRole):
            highlight_widget(ui.add_card_widget_style_combo_box)

        section = settings["images"]
        if section["preferred-language"] != ui.preferred_language_combo_box.currentText():
            highlight_widget(ui.preferred_language_combo_box)
        if section.getboolean("automatically-add-opposing-faces") is not ui.automatically_add_opposing_faces.isChecked():
            highlight_widget(ui.automatically_add_opposing_faces)

        section = settings["default-filesystem-paths"]
        widgets_and_settings = self._get_save_path_settings_widgets()
        for widget, setting in widgets_and_settings:
            if section[setting] != widget.text():
                highlight_widget(widget)

    def _get_save_path_settings_widgets(self):
        ui = self.ui
        widgets_with_settings: typing.List[typing.Tuple[QLineEdit, str]] = [
            (ui.document_save_path, "document-save-path"),
        ]
        return widgets_with_settings


class HidePrintingsPage(Page):
    display_metadata = PageMetadata("Hide printings", "view-hidden", "Hide unwanted printings")

    error_occurred = Signal(str)
    long_running_process_begins = Signal(int, str)
    process_updated = Signal(int)
    process_finished = Signal()

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = ui = Ui_HidePrintingsPage()
        ui.setupUi(self)
        self.card_db = None

    def load(self, settings: configparser.ConfigParser):
        ui = self.ui
        section = settings["card-filter"]
        ui.set_filter_settings.setPlainText(section["hidden-sets"])
        ui.card_filter_general_settings.load_settings(section)
        ui.card_filter_format_settings.load_settings(section)

    def save(self):
        section = mtg_proxy_printer.settings.settings["card-filter"]
        ui = self.ui
        ui.card_filter_general_settings.save_settings(section)
        ui.card_filter_format_settings.save_settings(section)
        section["hidden-sets"] = ui.set_filter_settings.toPlainText()
        updater = PrintingFilterUpdater(self.card_db)
        updater.connect_progress_signals(self.long_running_process_begins, self.process_updated, self.process_finished)
        updater.signals.error_occurred.connect(self.error_occurred, QueuedConnection)
        QThreadPool.globalInstance().start(updater)

    def highlight_differing_settings(self, settings: configparser.ConfigParser):
        section = settings["card-filter"]
        ui = self.ui
        ui.card_filter_general_settings.highlight_differing_settings(settings)
        ui.card_filter_general_settings.highlight_differing_settings(settings)
        if section["hidden-sets"] != ui.set_filter_settings.toPlainText():
            highlight_widget(ui.set_filter_settings)


class DefaultDocumentLayoutSettingsPage(Page):
    display_metadata = PageMetadata(
        "Default document settings", "document-properties",
        "Set the default document settings used for new documents,\nlike page size, margins, spacings, etc."
    )

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = ui = Ui_DefaultDocumentLayoutSettingsPage()
        ui.setupUi(self)
        ui.page_configuration_group_box.setTitle("Default settings for new documents")

    def load(self, settings: configparser.ConfigParser):
        self.ui.page_configuration_group_box.load_document_settings_from_config(settings)

    def save(self):
        self.ui.page_configuration_group_box.save_document_settings_to_config()

    def highlight_differing_settings(self, settings: configparser.ConfigParser):
        self.ui.page_configuration_group_box.highlight_differing_settings(settings)


class PrinterSettingsPage(Page):
    display_metadata = PageMetadata("Printer settings", "document-print", "Configure the printer")

    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.ui = ui = Ui_PrinterSettingsPage()
        ui.setupUi(self)

    def _get_printer_settings_widgets(self):
        ui = self.ui
        widgets_with_settings: typing.List[typing.Tuple[QCheckBox, str]] = [
            (ui.printer_use_borderless_printing, "borderless-printing"),
            (ui.landscape_workaround, "landscape-compatibility-workaround"),
        ]
        return widgets_with_settings

    def load(self, settings: configparser.ConfigParser):
        section = settings["printer"]
        for widget, setting in self._get_printer_settings_widgets():
            widget.setChecked(section.getboolean(setting))

    def save(self):
        section = mtg_proxy_printer.settings.settings["printer"]
        for widget, setting in self._get_printer_settings_widgets():
            section[setting] = str(widget.isChecked())

    def highlight_differing_settings(self, settings: configparser.ConfigParser):
        section = settings["printer"]
        for widget, setting in self._get_printer_settings_widgets():
            if section.getboolean(setting) != widget.isChecked():
                highlight_widget(widget)


class PDFSettingsPage(Page):
    display_metadata = PageMetadata("PDF export settings", "viewpdf", "Configure the PDF export")

    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.ui = ui = Ui_PDFSettingsPage()
        ui.setupUi(self)

    def load(self, settings: configparser.ConfigParser):
        ui = self.ui
        section = settings["pdf-export"]
        ui.pdf_page_count_limit.setValue(section.getint("pdf-page-count-limit"))
        ui.pdf_save_path.setText(section["pdf-export-path"])
        ui.landscape_workaround.setChecked(section.getboolean("landscape-compatibility-workaround"))

    def save(self):
        ui = self.ui
        section = mtg_proxy_printer.settings.settings["pdf-export"]
        section["pdf-page-count-limit"] = str(ui.pdf_page_count_limit.value())
        section["pdf-export-path"] = ui.pdf_save_path.text()
        section["landscape-compatibility-workaround"] = str(ui.landscape_workaround.isChecked())

    def highlight_differing_settings(self, settings: configparser.ConfigParser):
        ui = self.ui
        section = settings["pdf-export"]
        if section.getint("pdf-page-count-limit") != ui.pdf_page_count_limit.value():
            highlight_widget(ui.pdf_page_count_limit)
        if ui.pdf_save_path.text() != section["pdf-export-path"]:
            highlight_widget(ui.pdf_save_path)
        if ui.landscape_workaround.isChecked() != section.getboolean("landscape-compatibility-workaround"):
            highlight_widget(ui.landscape_workaround)

    @Slot()
    def on_pdf_save_path_browse_button_clicked(self):
        logger.debug("User about to select a new default PDF document export path.")
        if location := QFileDialog.getExistingDirectory(self, "Select default PDF export location"):
            logger.info("User selected a new default PDF document export path.")
            self.ui.pdf_save_path.setText(location)
        else:
            logger.debug("User cancelled path selection")
