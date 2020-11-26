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

import itertools
import typing


from PyQt5.QtCore import QAbstractListModel, QAbstractTableModel, QModelIndex, Qt, pyqtSlot, pyqtSignal


from mtg_proxy_printer.model.carddb import Card
from mtg_proxy_printer.settings import settings

CardList = typing.List[Card]


class Page(QAbstractTableModel):
    """
    This is a single page and part of a Document. It holds the proxies added to this page as a list of Card objects.
    """
    page_empty = pyqtSignal(bool)

    header = {
        0: "Card name",
        1: "Set",
        2: "Collector #",
        3: "Language",
    }

    def __init__(self, *args, **kwargs):
        super(Page, self).__init__(*args, **kwargs)
        self.cards: CardList = []
        
    def rowCount(self, parent: QModelIndex = None) -> int:
        return len(self.cards)

    def columnCount(self, parent: QModelIndex = None) -> int:
        return 4
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> typing.Any:
        card = self.cards[index.row()]
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return card.name
            elif index.column() == 1:
                return card.set_abbr
            elif index.column() == 2:
                return card.collector_number
            elif index.column() == 3:
                return card.language

    @pyqtSlot(Card)
    def add_card(self, card: Card, count: int):
        self.cards += list(itertools.repeat(card, count))
        self.layoutChanged.emit()
        if len(self.cards) == count:
            self.page_empty.emit(False)

    @pyqtSlot(list)
    def remove_cards(self, indices: typing.List[QModelIndex]):
        to_delete = set(index.row() for index in indices)
        remaining = [card for index, card in enumerate(self.cards) if index not in to_delete]
        self.cards[:] = remaining
        if indices:
            self.layoutChanged: pyqtSignal
            self.layoutChanged.emit()
        if not self.cards:
            self.page_empty.emit(True)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> str:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return Page.header[section]
        return super(Page, self).headerData(section, orientation, role)

    def get_preview(self):
        return "\n".join(card.name for card in self.cards)

    
PageList = typing.List[Page]


class Document(QAbstractListModel):
    """
    This is the root of a multi-page document that contains any number of same-size pages.
    The pages hold the individual proxy images
    """
    document_empty = pyqtSignal(bool)

    def __init__(self, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)
        self.pages: PageList = []
        document_settings = settings["documents"]
        self.page_height = document_settings.getint("paper-height-mm")
        self.page_width = document_settings.getint("paper-width-mm")
        self.margin_top = document_settings.getint("margin-top-mm")
        self.margin_bottom = document_settings.getint("margin-bottom-mm")
        self.margin_left = document_settings.getint("margin-left-mm")
        self.margin_right = document_settings.getint("margin-right-mm")
        self.image_spacing_horizontal = document_settings.getint("image-spacing-horizontal-mm")
        self.image_spacing_vertical = document_settings.getint("image-spacing-vertical-mm")
        
    @pyqtSlot()
    def apply_settings(self):
        """Applies the current, relevant application settings to this document."""
        document_settings = settings["documents"]
        self.page_height = document_settings.getint("paper-height-mm")
        self.page_width = document_settings.getint("paper-width-mm")
        self.margin_top = document_settings.getint("margin-top-mm")
        self.margin_bottom = document_settings.getint("margin-bottom-mm")
        self.margin_left = document_settings.getint("margin-left-mm")
        self.margin_right = document_settings.getint("margin-right-mm")
        self.image_spacing_horizontal = document_settings.getint("image-spacing-horizontal-mm")
        self.image_spacing_vertical = document_settings.getint("image-spacing-vertical-mm")

    @pyqtSlot()
    def add_page(self):
        self.pages.append(Page(parent=self))
        self.layoutChanged: pyqtSignal
        self.layoutChanged.emit()
        if len(self.pages) == 1:
            self.document_empty.emit(False)

    @pyqtSlot(list)
    def remove_pages(self, indices: typing.List[QModelIndex]):
        to_delete = set(index.row() for index in indices)
        remaining = [page for index, page in enumerate(self.pages) if index not in to_delete]
        self.pages[:] = remaining
        if indices:
            self.layoutChanged: pyqtSignal
            self.layoutChanged.emit()
        if not self.pages:
            self.document_empty.emit(True)
        
    def rowCount(self, parent: QModelIndex = None) -> int:
        return len(self.pages)
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> typing.Any:
        item = self.pages[index.row()]
        if role == Qt.DisplayRole:
            return item.get_preview()
        elif role == Qt.ToolTipRole:
            return f"Page {index.row()+1}/{self.rowCount()}"
        elif role == Qt.EditRole:
            return item
