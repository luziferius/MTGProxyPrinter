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

import math
from pathlib import Path

from PyQt5.QtCore import QObject, QMarginsF, QSizeF, pyqtSlot as Slot, QPersistentModelIndex
from PyQt5.QtGui import QPainter, QPdfWriter, QPageLayout
from PyQt5.QtPrintSupport import QPrinter

import mtg_proxy_printer.meta_data
from mtg_proxy_printer.settings import settings
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.ui.page_renderer import PageScene, RenderMode
from mtg_proxy_printer.logger import get_logger
import mtg_proxy_printer.units_and_sizes
logger = get_logger(__name__)
del get_logger

__all__ = [
    "export_pdf",
    "create_qprinter",
    "Renderer",
]


def export_pdf(document: Document, file_path: str, parent: QObject = None):
    pages_to_print = settings["documents"].getint("pdf-page-count-limit") or document.rowCount()
    if not pages_to_print:  # No pages in document. Return now, to avoid dividing by zero
        logger.error("Tried to export a document with zero pages as a PDF. Aborting.")
        return
    logger.info(f'Exporting document with {document.rowCount()} pages as PDF to "{file_path}"')
    total_documents = math.ceil(document.rowCount()/pages_to_print)
    for document_index in range(total_documents):
        logger.info(f"Creating PDF ({document_index+1}/{total_documents}) with up to {pages_to_print} pages.")
        printer = PDFPrinter(document, file_path, parent, document_index, pages_to_print)
        printer.print_document()
    document.store_image_usage()


def create_qprinter(document: Document) -> QPrinter:
    printer = QPrinter(QPrinter.HighResolution)
    page_width = document.page_layout.page_width
    page_height = document.page_layout.page_height
    if page_width > page_height:
        logger.debug(f"Document width ({page_width}mm) > height ({page_height}mm): Printing in landscape mode.")
        printer.setPageOrientation(QPageLayout.Landscape)
        # Swap width and height. Setting Landscape mode causes Qt to swap these values internally again,
        # resulting in correct values.
        page_size = QSizeF(page_height, page_width)
    else:
        page_size = QSizeF(page_width, page_height)
    printer.setPageSizeMM(page_size)
    # magnitude returns a float by default, so round to int to avoid a TypeError
    printer.setResolution(round(mtg_proxy_printer.units_and_sizes.RESOLUTION.magnitude))
    # Disable duplex printing by default
    printer.setDoubleSidedPrinting(False)
    printer.setDuplex(QPrinter.DuplexNone)
    printer.setOutputFormat(QPrinter.NativeFormat)
    # Setting both the margins to zero and FullPage to True is important for full page printing without downscaling
    printer.setFullPage(True)
    printer.setPageMargins(0, 0, 0, 0, QPrinter.Millimeter)
    return printer


class PDFPrinter(QPdfWriter):

    def __init__(self, document: Document, file_path: str, parent: QObject = None,
                 document_index: int = 0, pages_to_print: int = None):
        self.document = document
        self.document_index = document_index
        self.pages_to_print: int = pages_to_print or document.rowCount()
        if pages_to_print < document.rowCount():
            path = Path(file_path)
            # Add one to the document_index for human-readable counting starting at 1. suffix includes the separator
            file_path = str(path.parent / f"{path.stem}-{document_index+1}{path.suffix}")
        super(PDFPrinter, self).__init__(file_path)
        self.setParent(parent)
        self.setCreator(f"{mtg_proxy_printer.meta_data.PROGRAMNAME}, v{mtg_proxy_printer.meta_data.__version__}")
        self.painter = QPainter()
        # magnitude returns a float by default, so round to int to avoid a TypeError
        self.setResolution(round(mtg_proxy_printer.units_and_sizes.RESOLUTION.magnitude))
        self.setPageSizeMM(QSizeF(document.page_layout.page_width, document.page_layout.page_height))
        # Prevent downscaling the page content
        self.setPageMargins(QMarginsF(0, 0, 0, 0))
        self.scene = PageScene(document, RenderMode.ON_PAPER, self)
        logger.info(f"Created {self.__class__.__name__} instance.")

    def print_document(self):
        logger.info("Begin rendering PDF document.")
        self.painter.begin(self)
        # Prevent quality loss by re-compressing the source images
        self.painter.setRenderHint(QPainter.LosslessImageRendering)
        self.painter.scale(
                self.logicalDpiX()/self.resolution(),
                self.logicalDpiY()/self.resolution()
            )
        first_index = self.document_index * self.pages_to_print
        last_index = min((self.document_index + 1) * self.pages_to_print, self.document.rowCount())

        for index in range(first_index, last_index):
            logger.debug(f"Rendering page {index+1}/{self.document.rowCount()}")
            self.scene.on_current_page_changed(QPersistentModelIndex(self.document.index(index, 0)))
            self.scene.render(self.painter)
            if index + 1 < last_index:  # Avoid including a trailing, empty page
                self.newPage()
        self.painter.end()
        logger.info("Writing document finished.")


class Renderer(QObject):

    def __init__(self, document: Document, parent: QObject = None):
        super(Renderer, self).__init__(parent)
        self.document = document
        self.scene = PageScene(document, RenderMode.ON_PAPER, self)

    @Slot(QPrinter)
    def print_document(self, printer: QPrinter):
        logger.info("Begin printing document.")
        painter = QPainter(printer)
        painter.setRenderHint(QPainter.LosslessImageRendering)
        page_count = self.document.rowCount()
        for index in range(page_count):
            logger.debug(f"Printing page {index+1}/{page_count}")
            self.scene.on_current_page_changed(QPersistentModelIndex(self.document.index(index, 0)))
            self.scene.render(painter)
            if index+1 < page_count:
                printer.newPage()
        painter.end()
        logger.info("Printing document finished.")
