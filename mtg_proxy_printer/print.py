# Copyright (C) 2020, 2021 Thomas Hess <thomas.hess@udo.edu>

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

from PyQt5.QtCore import QObject, QMarginsF
from PyQt5.QtGui import QPainter, QPdfWriter

import mtg_proxy_printer.meta_data
from mtg_proxy_printer.settings import settings
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.ui.page_renderer import PageScene, PageRenderer

__all__ = [
    "export_pdf",
]


def export_pdf(document: Document, file_path: str, parent: QObject = None):
    pages_to_print = settings["documents"].getint("pdf-page-count-limit") or document.rowCount()
    if not pages_to_print:  # No pages in document. Return now, to avoid dividing by zero
        return
    for document_index in range(math.ceil(document.rowCount()/pages_to_print)):
        printer = PDFPrinter(document, file_path, parent, document_index, pages_to_print)
        printer.print_document()


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
        self.setResolution(document.DPI.to_tuple()[0])
        # Prevent downscaling the page content
        self.setPageMargins(QMarginsF(0, 0, 0, 0))
        # PageScene reads the Page instance from the parent QObject. So store it here before starting any rendering
        self.page = None
        self.scene = PageScene(False, PageRenderer.get_document_page_size(), parent=self)

    def print_document(self):
        self.painter.begin(self)
        # Prevent quality loss by re-compressing the source images
        self.painter.setRenderHint(QPainter.LosslessImageRendering)
        self.painter.scale(
                self.logicalDpiX()/self.resolution(),
                self.logicalDpiY()/self.resolution()
            )
        first_index = self.document_index * self.pages_to_print
        last_index = (self.document_index + 1) * self.pages_to_print

        pages_to_process = self.document.pages[first_index:last_index]
        page_count = len(pages_to_process)
        for index, page in enumerate(pages_to_process, start=1):
            self.page = page
            self.scene.redraw()
            self.scene.render(self.painter)
            if index < page_count:  # Avoid including a trailing, empty page
                self.newPage()
        self.painter.end()
