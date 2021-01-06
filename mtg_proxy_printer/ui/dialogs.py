# Copyright (C) 2020 Thomas Hess <thomas.hess@udo.edu>

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

from PyQt5.QtWidgets import QFileDialog, QWidget, QLabel

import mtg_proxy_printer.model.carddb
import mtg_proxy_printer.model.document
import mtg_proxy_printer.model.imagedb
import mtg_proxy_printer.print
import mtg_proxy_printer.ui.common
import mtg_proxy_printer.meta_data
from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger


class SavePDFDialog(QFileDialog):

    def __init__(self, parent: QWidget, document: mtg_proxy_printer.model.document.Document, **kwargs):
        super(SavePDFDialog, self).__init__(parent, "Export as PDF", filter="PDF-Documents (*.pdf)", **kwargs)
        self.document = document
        self.setAcceptMode(QFileDialog.AcceptSave)
        self.setDefaultSuffix("pdf")
        self.setFileMode(QFileDialog.AnyFile)
        logger.info(f"Created {self.__class__.__name__} instance.")

    def exec_(self) -> int:
        logger.debug(f"About to run the {self.__class__.__name__} event loop.")
        result = super(SavePDFDialog, self).exec_()
        if result == QFileDialog.Accepted:
            logger.debug("User chose a file name, about to generate the PDF document")
            path = self.selectedFiles()[0]
            mtg_proxy_printer.print.export_pdf(self.document, path, self)
            logger.info(f"Saved document to {path}")

        else:
            logger.debug("User aborted saving to PDF. Doing nothing.")
        return result


class SaveDocumentAsDialog(QFileDialog):

    def __init__(self, parent: QWidget, document: mtg_proxy_printer.model.document.Document, **kwargs):
        super(SaveDocumentAsDialog, self).__init__(
            parent, "Save document as …", filter="MTGProxyPrinter document (*.mtgproxies)", **kwargs)
        self.document = document
        self.setAcceptMode(QFileDialog.AcceptSave)
        self.setDefaultSuffix("mtgproxies")
        self.setFileMode(QFileDialog.AnyFile)
        logger.info(f"Created {self.__class__.__name__} instance.")

    def exec_(self) -> int:
        logger.debug(f"About to run the {self.__class__.__name__} event loop.")
        result = super(SaveDocumentAsDialog, self).exec_()
        if result == QFileDialog.Accepted:
            logger.debug("User chose a file name, about to save the document to disk")
            path = pathlib.Path(self.selectedFiles()[0])
            self.document.save_as(path)
            logger.info(f"Saved document to {path}")
        else:
            logger.debug("User aborted saving. Doing nothing.")
        return result


class LoadDocumentDialog(QFileDialog):

    def __init__(
            self, parent: QWidget,
            document: mtg_proxy_printer.model.document.Document,
            card_db: mtg_proxy_printer.model.carddb.CardDatabase,
            image_db: mtg_proxy_printer.model.imagedb.ImageDatabase, **kwargs):
        super(LoadDocumentDialog, self).__init__(
            parent, "Load MTGProxyPrinter document", filter="MTGProxyPrinter document (*.mtgproxies)", **kwargs)
        self.document = document
        self.card_db = card_db
        self.image_db = image_db
        self.setAcceptMode(QFileDialog.AcceptOpen)
        self.setDefaultSuffix("mtgproxies")
        self.setFileMode(QFileDialog.ExistingFile)
        logger.info(f"Created {self.__class__.__name__} instance.")

    def exec_(self) -> int:
        logger.debug(f"About to run the {self.__class__.__name__} event loop.")
        result = super(LoadDocumentDialog, self).exec_()
        if result == QFileDialog.Accepted:
            logger.debug("User chose a file name, about to load the document from disk")
            path = pathlib.Path(self.selectedFiles()[0])
            self.document.load_from_disk(path, self.card_db, self.image_db)
            logger.info(f"Loaded document from {path}")
        else:
            logger.debug("User aborted loading. Doing nothing.")
        return result

class AboutMTGProxyPrinterDialog(*mtg_proxy_printer.ui.common.inherits_from_ui_file_with_name("about_dialog")):

    def __init__(self, *args, **kwargs):
        super(AboutMTGProxyPrinterDialog, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.mtg_proxy_printer_version_label: QLabel
        self.python_version_label: QLabel
        self.mtg_proxy_printer_version_label.setText(mtg_proxy_printer.meta_data.__version__)
        self.python_version_label.setText(sys.version.replace("\n", " "))


