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

import pathlib
import sys

from PyQt5.QtCore import QFile, pyqtSlot as Slot
from PyQt5.QtWidgets import QFileDialog, QWidget, QTextBrowser, QDialogButtonBox, QDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrintDialog, QPrinter

import mtg_proxy_printer.model.carddb
import mtg_proxy_printer.model.document
import mtg_proxy_printer.model.imagedb
import mtg_proxy_printer.print
import mtg_proxy_printer.settings
import mtg_proxy_printer.ui.common
import mtg_proxy_printer.meta_data
from mtg_proxy_printer.document_controller.edit_document_settings import ActionEditDocumentSettings
from mtg_proxy_printer.logger import get_logger

try:
    from mtg_proxy_printer.ui.generated.about_dialog import Ui_Dialog as Ui_AboutDialog
    from mtg_proxy_printer.ui.generated.page_config_dialog import Ui_Dialog as Ui_PageConfigDialog
except ModuleNotFoundError:
    from mtg_proxy_printer.ui.common import load_ui_from_file
    Ui_AboutDialog = load_ui_from_file("about_dialog")
    Ui_PageConfigDialog = load_ui_from_file("page_config_dialog")

logger = get_logger(__name__)
del get_logger

__all__ = [
    "SavePDFDialog",
    "SaveDocumentAsDialog",
    "LoadDocumentDialog",
    "AboutMTGProxyPrinterDialog",
    "PrintPreviewDialog",
    "PrintDialog",
    "DocumentSettingsDialog",
]


def read_path(setting: str) -> str:
    return mtg_proxy_printer.settings.settings["default-filesystem-paths"][setting]


class SavePDFDialog(QFileDialog):

    def __init__(self, parent: QWidget, document: mtg_proxy_printer.model.document.Document):
        preferred_file_name = document.save_file_path.name if document.save_file_path is not None else ""
        super(SavePDFDialog, self).__init__(parent, "Export as PDF", preferred_file_name, "PDF-Documents (*.pdf)")
        if default_path := read_path("pdf-export-path"):
            self.setDirectory(default_path)
        self.document = document
        self.setAcceptMode(QFileDialog.AcceptSave)
        self.setDefaultSuffix("pdf")
        self.setFileMode(QFileDialog.AnyFile)
        self.accepted.connect(self.on_accept)
        self.rejected.connect(self.on_reject)
        logger.info(f"Created {self.__class__.__name__} instance.")

    @Slot()
    def on_accept(self):
        logger.debug("User chose a file name, about to generate the PDF document")
        path = self.selectedFiles()[0]
        mtg_proxy_printer.print.export_pdf(self.document, path, self)
        logger.info(f"Saved document to {path}")

    @Slot()
    def on_reject(self):
        logger.debug("User aborted saving to PDF. Doing nothing.")


class SaveDocumentAsDialog(QFileDialog):

    def __init__(self, document: mtg_proxy_printer.model.document.Document, parent: QWidget = None, **kwargs):
        super(SaveDocumentAsDialog, self).__init__(
            parent, "Save document as …", filter="MTGProxyPrinter document (*.mtgproxies)", **kwargs)
        if default_path := read_path("document-save-path"):
            self.setDirectory(default_path)
        self.document = document
        self.setAcceptMode(QFileDialog.AcceptSave)
        self.setDefaultSuffix("mtgproxies")
        self.setFileMode(QFileDialog.AnyFile)
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


class LoadDocumentDialog(QFileDialog):

    def __init__(
            self, parent: QWidget,
            document: mtg_proxy_printer.model.document.Document, **kwargs):
        super(LoadDocumentDialog, self).__init__(
            parent, "Load MTGProxyPrinter document", filter="MTGProxyPrinter document (*.mtgproxies)", **kwargs)
        if default_path := read_path("document-save-path"):
            self.setDirectory(default_path)
        self.document = document
        self.setAcceptMode(QFileDialog.AcceptOpen)
        self.setDefaultSuffix("mtgproxies")
        self.setFileMode(QFileDialog.ExistingFile)
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


class AboutMTGProxyPrinterDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super(AboutMTGProxyPrinterDialog, self).__init__(*args, **kwargs)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)
        self._setup_about_text()
        self._setup_changelog_text()
        self._setup_license_text()
        self._setup_third_party_license_text()
        self.ui.mtg_proxy_printer_version_label.setText(mtg_proxy_printer.meta_data.__version__)
        self.ui.python_version_label.setText(sys.version.replace("\n", " "))
        logger.info(f"Created {self.__class__.__name__} instance.")

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
        file_path = self._get_file_path(":/ThirdPartyLicenses.md", "/../../ThirdPartyLicenses.md")
        self._set_text_browser_with_markdown_file_content(file_path, self.ui.third_party_license_text_browser)

    def _setup_changelog_text(self):
        file_path = self._get_file_path(":/changelog.md", "/../../doc/changelog.md")
        self._set_text_browser_with_markdown_file_content(file_path, self.ui.changelog_text_browser)

    def _set_text_browser_with_markdown_file_content(self, file_path: str, text_browser: QTextBrowser):
        file = QFile(file_path, self)
        file.open(QFile.ReadOnly)
        try:
            content = bytes(file.readAll()).decode("utf-8")
        finally:
            file.close()
        text_browser.setMarkdown(content)


class PrintPreviewDialog(QPrintPreviewDialog):

    def __init__(self, document: mtg_proxy_printer.model.document.Document, parent: QWidget = None):
        self.qprinter = mtg_proxy_printer.print.create_qprinter(document)
        super(PrintPreviewDialog, self).__init__(self.qprinter, parent)
        self.renderer = mtg_proxy_printer.print.Renderer(document, self)
        self.paintRequested.connect(self.renderer.print_document)
        logger.info(f"Created {self.__class__.__name__} instance.")


class PrintDialog(QPrintDialog):

    def __init__(self, document: mtg_proxy_printer.model.document.Document, parent: QWidget = None):
        self.qprinter = mtg_proxy_printer.print.create_qprinter(document)
        super(PrintDialog, self).__init__(self.qprinter, parent)
        self.renderer = mtg_proxy_printer.print.Renderer(document, self)
        # When the user accepts the dialog, print the document and increase the usage counts
        self.accepted[QPrinter].connect(self.renderer.print_document)
        self.accepted.connect(document.store_image_usage)
        logger.info(f"Created {self.__class__.__name__} instance.")


class DocumentSettingsDialog(QDialog):

    def __init__(self, document: mtg_proxy_printer.model.document.Document, parent: QWidget = None):
        super(DocumentSettingsDialog, self).__init__(parent)
        self.ui = Ui_PageConfigDialog()
        self.ui.setupUi(self)
        self.setModal(True)
        self.document = document
        self.ui.page_config_groupbox.load_from_page_layout(document.page_layout)
        self.ui.page_config_groupbox.setTitle("These settings only affect the current document")
        self._setup_button_box()
        self.accepted.connect(self.on_accept)
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _setup_button_box(self):
        button_box = self.ui.button_box
        button_box.button(QDialogButtonBox.RestoreDefaults).clicked.connect(
            lambda: logger.info("User reverts the document settings to the values from the global configuration")
        )
        button_box.button(QDialogButtonBox.RestoreDefaults).clicked.connect(
            lambda: self.ui.page_config_groupbox.load_document_settings_from_config(mtg_proxy_printer.settings.settings)
        )
        button_box.button(QDialogButtonBox.Reset).clicked.connect(
            lambda: logger.info("User resets made changes")
        )
        button_box.button(QDialogButtonBox.Reset).clicked.connect(
            lambda: self.ui.page_config_groupbox.load_from_page_layout(self.document.page_layout)
        )
        buttons_with_icons = [
            (QDialogButtonBox.Reset, "edit-undo"),
            (QDialogButtonBox.Save, "document-save"),
            (QDialogButtonBox.Cancel, "dialog-cancel"),
            (QDialogButtonBox.RestoreDefaults, "document-revert"),
        ]
        for role, icon in buttons_with_icons:
            button = button_box.button(role)
            if button.icon().isNull():
                button.setIcon(QIcon.fromTheme(icon))

    @Slot()
    def on_accept(self):
        logger.info(f"User accepted the {self.__class__.__name__}")
        action = ActionEditDocumentSettings(self.ui.page_config_groupbox.page_layout)
        self.document.apply(action)
        logger.debug("Saving settings in the document done.")
