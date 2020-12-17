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

from PyQt5.QtWidgets import QFileDialog, QWidget

import mtg_proxy_printer.model.document
import mtg_proxy_printer.print
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
            printer = mtg_proxy_printer.print.PDFPrinter(self.document, path)
            printer.print_document()
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
        self.setDefaultSuffix("pdf")
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
