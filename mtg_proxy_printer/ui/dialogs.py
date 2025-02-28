#  Copyright © 2020-2025  Thomas Hess <thomas.hess@udo.edu>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.


import typing
import pathlib
import sys

from PyQt5.QtCore import QFile, pyqtSlot as Slot, QThreadPool, QObject, QEvent, Qt
from PyQt5.QtWidgets import QFileDialog, QWidget, QTextBrowser, QDialogButtonBox, QDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrintDialog, QPrinter

import mtg_proxy_printer.app_dirs
from mtg_proxy_printer.model.carddb import Card, CardDatabase
import mtg_proxy_printer.model.document
import mtg_proxy_printer.model.imagedb
import mtg_proxy_printer.print
import mtg_proxy_printer.settings
import mtg_proxy_printer.ui.common
import mtg_proxy_printer.meta_data
from mtg_proxy_printer.units_and_sizes import DEFAULT_SAVE_SUFFIX, ConfigParser
from mtg_proxy_printer.document_controller.edit_document_settings import ActionEditDocumentSettings
from mtg_proxy_printer.print_count_updater import PrintCountUpdater
from mtg_proxy_printer.logger import get_logger

try:
    from mtg_proxy_printer.ui.generated.about_dialog import Ui_AboutDialog
    from mtg_proxy_printer.ui.generated.document_settings_dialog import Ui_DocumentSettingsDialog
except ModuleNotFoundError:
    from mtg_proxy_printer.ui.common import load_ui_from_file
    Ui_AboutDialog = load_ui_from_file("about_dialog")
    Ui_DocumentSettingsDialog = load_ui_from_file("document_settings_dialog")

EventType = QEvent.Type
logger = get_logger(__name__)
del get_logger

__all__ = [
    "SavePDFDialog",
    "SaveDocumentAsDialog",
    "LoadDocumentDialog",
    "AboutDialog",
    "PrintPreviewDialog",
    "PrintDialog",
    "DocumentSettingsDialog",
]


def read_path(section: str, setting: str) -> str:
    stored = mtg_proxy_printer.settings.settings[section][setting]
    if not stored:
        return ""
    resolved = str(pathlib.Path(stored).resolve())
    if not resolved:
        logger.warning(
            f"File system path stored in section {section} setting {setting} does not resolve to an existing path")
    return resolved


class SavePDFDialog(QFileDialog):

    def __init__(self, parent: QWidget, document: mtg_proxy_printer.model.document.Document):
        # Note: Cannot supply already translated strings to __init__,
        # because tr() requires to have returned from super().__init__()
        super().__init__(parent, "", self.get_preferred_file_name(document))
        self.setWindowTitle(self.tr("Export as PDF"))
        self.setNameFilter(self.tr("PDF documents (*.pdf)"))

        if default_path := read_path("pdf-export", "pdf-export-path"):
            self.setDirectory(default_path)
        self.document = document
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        self.setDefaultSuffix("pdf")
        self.setFileMode(QFileDialog.FileMode.AnyFile)
        self.accepted.connect(self.on_accept)
        self.rejected.connect(self.on_reject)
        logger.info(f"Created {self.__class__.__name__} instance.")

    @staticmethod
    def get_preferred_file_name(document: mtg_proxy_printer.model.document.Document):
        if document.save_file_path is None:
            return ""
        # Note: Qt automatically appends the preferred file extension (.pdf), if the file does not have one.
        # So ensure it ends on ".pdf", if there is a dot in the name. Otherwise, let the user enter the name without
        # pre-setting an extension for a cleaner dialog
        stem = document.save_file_path.stem
        return f"{stem}.pdf" if "." in stem else stem

    @Slot()
    def on_accept(self):
        logger.debug("User chose a file name, about to generate the PDF document")
        path = self.selectedFiles()[0]
        mtg_proxy_printer.print.export_pdf(self.document, path, self)
        QThreadPool.globalInstance().start(PrintCountUpdater(self.document))
        logger.info(f"Saved document to {path}")

    @Slot()
    def on_reject(self):
        logger.debug("User aborted saving to PDF. Doing nothing.")


class LoadSaveDialog(QFileDialog):
    def __init__(self, *args, **kwargs):
        # Note: Cannot supply already translated strings to __init__,
        # because tr() requires to have returned from super().__init__()
        super().__init__(*args, **kwargs)
        filter_text = self.tr(
            "MTGProxyPrinter document (*.{default_save_suffix})", "Human-readable file type name"
        ).format(default_save_suffix=DEFAULT_SAVE_SUFFIX)
        self.setNameFilter(filter_text)
        self.setDefaultSuffix(DEFAULT_SAVE_SUFFIX)


class SaveDocumentAsDialog(LoadSaveDialog):

    def __init__(self, document: mtg_proxy_printer.model.document.Document, parent: QWidget = None, **kwargs):
        # Note: Cannot supply already translated strings to __init__,
        # because tr() requires to have returned from super().__init__()
        super().__init__(parent, **kwargs)
        self.setWindowTitle(self.tr("Save document as …"))
        if default_path := read_path("default-filesystem-paths", "document-save-path"):
            self.setDirectory(default_path)
        self.document = document
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        self.setFileMode(QFileDialog.FileMode.AnyFile)
        self.accepted.connect(self.on_accept)
        self.rejected.connect(self.on_reject)
        logger.info(f"Created {self.__class__.__name__} instance.")

    @Slot()
    def on_accept(self):
        logger.debug("User chose a file name, about to save the document to disk")
        path = pathlib.Path(self.selectedFiles()[0])
        self.document.save_as(path)
        logger.info(f"Saved document to {path}")

    @Slot()
    def on_reject(self):
        logger.debug("User aborted saving. Doing nothing.")


class LoadDocumentDialog(LoadSaveDialog):

    def __init__(
            self, parent: QWidget,
            document: mtg_proxy_printer.model.document.Document, **kwargs):
        # Note: Cannot supply already translated strings to __init__,
        # because tr() requires to have returned from super().__init__()
        super().__init__(parent, **kwargs)
        self.setWindowTitle(self.tr("Load MTGProxyPrinter document"))
        if default_path := read_path("default-filesystem-paths", "document-save-path"):
            self.setDirectory(default_path)
        self.document = document
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        self.setFileMode(QFileDialog.FileMode.ExistingFile)
        self.accepted.connect(self.on_accept)
        self.rejected.connect(self.on_reject)
        logger.info(f"Created {self.__class__.__name__} instance.")

    @Slot()
    def on_accept(self):
        logger.debug("User chose a file name, about to load the document from disk")
        path = pathlib.Path(self.selectedFiles()[0])
        self.document.loader.load_document(path)
        logger.info(f"Requested loading document from {path}")

    @Slot()
    def on_reject(self):
        logger.debug("User aborted loading. Doing nothing.")


class AboutDialog(QDialog):

    def __init__(self, card_database: CardDatabase, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)
        self.ui.mtg_proxy_printer_icon.setPixmap(
            mtg_proxy_printer.ui.common.load_icon("MTGPP.png").pixmap(self.ui.mtg_proxy_printer_icon.size()))
        self._setup_about_text()
        self._setup_changelog_text()
        self._setup_license_text()
        self._setup_third_party_license_text()
        self.card_database = card_database
        self.populate_card_database_update_timestamp_label()
        self.ui.mtg_proxy_printer_version_label.setText(mtg_proxy_printer.meta_data.__version__)
        self.ui.python_version_label.setText(sys.version.replace("\n", " "))
        logger.info(f"Created {self.__class__.__name__} instance.")

    def populate_card_database_update_timestamp_label(self):
        self.card_database.card_data_updated.connect(self.on_card_database_updated)
        self.on_card_database_updated()

    @Slot()
    def on_card_database_updated(self):
        last_update = self.card_database.get_last_card_data_update_timestamp()
        label_text = str(last_update) if last_update else ""
        self.ui.last_database_update_label.setText(label_text)

    @Slot()
    def show_about(self):
        self.ui.tab_widget.setCurrentWidget(self.ui.tab_widget.findChild(QWidget, "tab_about"))
        self.show()

    @Slot()
    def show_changelog(self):
        self.ui.tab_widget.setCurrentWidget(self.ui.tab_widget.findChild(QTextBrowser, "changelog_text_browser"))
        self.show()

    @staticmethod
    def _get_file_path(resource_path: str, fallback_filesystem_path: str) -> str:
        if mtg_proxy_printer.ui.common.HAS_COMPILED_RESOURCES:
            return resource_path
        else:
            return mtg_proxy_printer.ui.common.RESOURCE_PATH_PREFIX + fallback_filesystem_path

    def _setup_about_text(self):
        formatted_about_text = self.ui.about_text.toMarkdown().format(
            application_name=mtg_proxy_printer.meta_data.PROGRAMNAME,
            application_home_page=mtg_proxy_printer.meta_data.HOME_PAGE,
        )
        self.ui.about_text.setMarkdown(formatted_about_text)

    def _setup_license_text(self):
        file_path = self._get_file_path(":/License.md", "/../../LICENSE.md")
        self._set_text_browser_with_markdown_file_content(file_path, self.ui.license_text_browser)

    def _setup_third_party_license_text(self):
        file_path = self._get_file_path(":/ThirdPartyLicenses.md", "/../../doc/ThirdPartyLicenses.md")
        self._set_text_browser_with_markdown_file_content(file_path, self.ui.third_party_license_text_browser)

    def _setup_changelog_text(self):
        file_path = self._get_file_path(":/changelog.md", "/../../doc/changelog.md")
        self._set_text_browser_with_markdown_file_content(file_path, self.ui.changelog_text_browser)

    def _set_text_browser_with_markdown_file_content(self, file_path: str, text_browser: QTextBrowser):
        file = QFile(file_path, self)
        file.open(QFile.OpenModeFlag.ReadOnly)
        try:
            content = file.readAll().data().decode("utf-8")
        finally:
            file.close()
        text_browser.setMarkdown(content)


class PrintPreviewDialog(QPrintPreviewDialog):

    def __init__(self, document: mtg_proxy_printer.model.document.Document, parent: QWidget = None):
        self.renderer = mtg_proxy_printer.print.Renderer(document)
        self.q_printer = mtg_proxy_printer.print.create_printer(self.renderer)
        super().__init__(self.q_printer, parent)
        self.renderer.setParent(self)
        # The only way found to reliably set the window size is by forcing it larger via the minimum size.
        self.setMinimumSize(1000, 800)
        self.paintRequested.connect(self.renderer.print_document)
        logger.info(f"Created {self.__class__.__name__} instance.")

    def showEvent(self, a0):
        # Resetting the minimum size to allow shrinking it again requires some delay.
        # So reset it once the window shows up.
        self.setMinimumSize(0, 0)
        super().showEvent(a0)


class PrintDialog(QPrintDialog):

    def __init__(self, document: mtg_proxy_printer.model.document.Document, parent: QWidget = None):
        self.renderer = mtg_proxy_printer.print.Renderer(document)
        self.q_printer = mtg_proxy_printer.print.create_printer(self.renderer)
        super().__init__(self.q_printer, parent)
        self.renderer.setParent(self)
        # When the user accepts the dialog, print the document and increase the usage counts
        self.accepted[QPrinter].connect(self.renderer.print_document)
        self.accepted.connect(lambda: QThreadPool.globalInstance().start(PrintCountUpdater(document)))
        logger.info(f"Created {self.__class__.__name__} instance.")


class ChangedSettingsHoverEventFilter(QObject):
    parent: typing.Callable[[], "DocumentSettingsDialog"]

    def __init__(self, settings: ConfigParser, parent: "DocumentSettingsDialog"):
        super().__init__(parent)
        self.settings = settings

    def eventFilter(self, object_, event: QEvent):
        event_type = event.type()
        # This check avoids a crash during application shutdown
        if event_type not in {EventType.HoverEnter, EventType.HoverLeave}:
            return False
        parent = self.parent()
        if event_type == EventType.HoverEnter:
            parent.ui.page_config_container.ui.page_config_widget.highlight_differing_settings(self.settings)
        elif event_type == EventType.HoverLeave:
            parent.clear_highlight()
        return False


class DocumentSettingsDialog(QDialog):

    def __init__(self, document: mtg_proxy_printer.model.document.Document, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_DocumentSettingsDialog()
        self.ui.setupUi(self)
        self.setModal(True)
        self.document = document
        page_config_widget = self.ui.page_config_container.ui.page_config_widget
        page_config_widget.ui.show_preview_button.hide()
        page_config_widget.load_from_page_layout(document.page_layout)
        page_config_widget.setTitle(
            self.tr("These settings only affect the current document"))
        self._setup_button_box()
        self.accepted.connect(self.on_accept)
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _setup_button_box(self):
        button_roles = QDialogButtonBox.StandardButton
        button_box = self.ui.button_box

        restore_defaults = button_box.button(button_roles.RestoreDefaults)
        restore_defaults.installEventFilter(ChangedSettingsHoverEventFilter(mtg_proxy_printer.settings.settings, self))
        restore_defaults.clicked.connect(self.restore_defaults_button_clicked)

        reset = button_box.button(button_roles.Reset)
        reset.installEventFilter(ChangedSettingsHoverEventFilter(self.document.page_layout, self))
        reset.clicked.connect(self.reset_button_clicked)

        buttons_with_icons = [
            (button_roles.Reset, "edit-undo"),
            (button_roles.Save, "document-save"),
            (button_roles.Cancel, "dialog-cancel"),
            (button_roles.RestoreDefaults, "document-revert"),
        ]
        for role, icon in buttons_with_icons:
            button = button_box.button(role)
            if button.icon().isNull():
                button.setIcon(QIcon.fromTheme(icon))

    @Slot()
    def restore_defaults_button_clicked(self):
        logger.info("User reverts the document settings to the values from the global configuration")
        self.ui.page_config_container.ui.page_config_widget.load_document_settings_from_config(
            mtg_proxy_printer.settings.settings)
        self.clear_highlight()

    @Slot()
    def reset_button_clicked(self):
        logger.info("User resets made changes")
        self.ui.page_config_container.ui.page_config_widget.load_from_page_layout(self.document.page_layout)
        self.clear_highlight()

    @Slot()
    def on_accept(self):
        logger.info(f"User accepted the {self.__class__.__name__}")
        action = ActionEditDocumentSettings(self.ui.page_config_container.ui.page_config_widget.page_layout)
        self.document.apply(action)
        logger.debug("Saving settings in the document done.")

    def clear_highlight(self):
        """Clears all GUI widget highlights."""
        for item in self.findChildren((QWidget,), options=Qt.FindChildOption.FindChildrenRecursively):  # type: QWidget
            item.setGraphicsEffect(None)
