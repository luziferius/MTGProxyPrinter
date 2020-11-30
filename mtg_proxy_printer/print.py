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

from PyQt5.QtCore import QObject, QMarginsF
from PyQt5.QtGui import QPainter, QPdfWriter

import mtg_proxy_printer.meta_data
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.ui.page_renderer import PageScene, PageRenderer


class PDFPrinter(QPdfWriter):

    def __init__(self, document: Document, file_path: str, parent: QObject = None):
        super(PDFPrinter, self).__init__(file_path)
        self.setParent(parent)
        self.setCreator(f"{mtg_proxy_printer.meta_data.PROGRAMNAME}, v{mtg_proxy_printer.meta_data.__version__}")
        self.painter = QPainter()
        self.document = document
        self.setResolution(document.DPI.to_tuple()[0])
        self.setPageMargins(QMarginsF(0, 0, 0, 0))
        self.page = None
        self.scene = PageScene(False, PageRenderer.get_document_page_size(), parent=self)

    def print_document(self):
        page_count = self.document.rowCount()
        self.painter.begin(self)
        self.painter.setRenderHint(QPainter.LosslessImageRendering)
        self.painter.scale(
                self.logicalDpiX()/self.resolution(),
                self.logicalDpiY()/self.resolution()
            )
        for index, page in enumerate(self.document.pages, start=1):
            self.page = page
            self.scene.redraw()
            self.scene.render(self.painter)
            if index < page_count:
                self.newPage()
        self.painter.end()
