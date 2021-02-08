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

import collections
import itertools
import pathlib
import typing

import pint
from PyQt5.QtCore import QAbstractListModel, QAbstractTableModel, QModelIndex, Qt, pyqtSlot, pyqtSignal


import mtg_proxy_printer.sqlite_helpers
from mtg_proxy_printer.model.carddb import Card, CardDatabase
from mtg_proxy_printer.model.imagedb import ImageDatabase
from mtg_proxy_printer.settings import settings

CardList = typing.List[Card]
unit_registry = pint.UnitRegistry()

__all__ = [
    "Page",
    "PageList",
    "Document",
]


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
        4: "Image",
    }

    def __init__(self, *args, **kwargs):
        super(Page, self).__init__(*args, **kwargs)
        self.cards: CardList = []
        
    def rowCount(self, parent: QModelIndex = None) -> int:
        return len(self.cards)

    def columnCount(self, parent: QModelIndex = None) -> int:
        return 5
    
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
            elif index.column() == 4:
                return card.image_file

    @pyqtSlot(Card)
    @pyqtSlot(Card, int)
    def add_card(self, card: Card, count: int = 1):
        first_index, last_index = self.rowCount(), self.rowCount() + count - 1
        self.beginInsertRows(QModelIndex(), first_index, last_index)
        self.cards += list(itertools.repeat(card, count))
        self.endInsertRows()
        if self.rowCount() == count:
            self.page_empty.emit(False)
        for row in range(first_index, last_index + 1):  # Qt includes last_index, Python excludes it, so add one here
            self.dataChanged.emit(self.createIndex(row, 0), self.createIndex(row, self.columnCount()-1))

    @pyqtSlot(list)
    def remove_multi_selection(self, indices: typing.List[QModelIndex]) -> int:
        """
        Remove all cards in the given multi-selection.
        :param indices: List with QModelIndex instances that represents a multi-selection.
          As returned by a QSelectionModel
        :return: Number of cards removed
        """
        current_range: typing.List[QModelIndex] = []
        ranges = []
        for index in indices:
            if not current_range or index.row() == current_range[-1].row() + 1:
                current_range.append(index)
            if current_range and index.row() != current_range[-1].row() + 1:
                ranges.append(current_range)
                current_range = []
        if current_range:
            ranges.append(current_range)
        if ranges:
            ranges.reverse()
            return sum(self.remove_cards(range_) for range_ in ranges)

    @pyqtSlot(list)
    def remove_cards(self, indices: typing.List[QModelIndex]) -> int:
        """
        Remove all cards in the given list of consecutive model indices

        :return: Number of cards removed
        """
        if not indices:
            return 0
        first_index, last_index = indices[0].row(), indices[-1].row()
        self.beginRemoveRows(QModelIndex(), first_index, last_index)
        to_delete = set(index.row() for index in indices)
        remaining = [card for index, card in enumerate(self.cards) if index not in to_delete]
        self.cards[:] = remaining
        self.endRemoveRows()
        if not self.cards:
            self.page_empty.emit(True)
        for row in range(first_index, last_index + 1):  # Qt includes last_index, Python excludes it, so add one here
            self.dataChanged.emit(self.createIndex(row, 0), self.createIndex(row, self.columnCount()-1))
        return len(to_delete)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> str:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return Page.header[section]
        return super(Page, self).headerData(section, orientation, role)

    def get_preview(self):
        names = collections.Counter(card.name for card in self.cards)
        return "\n".join(
            f"{count}× {name}" for name, count in names.items()
        )

    
PageList = typing.List[Page]


class Document(QAbstractListModel):
    """
    This is the root of a multi-page document that contains any number of same-size pages.
    The pages hold the individual proxy images
    """

    MIN_SUPPORTED_SQLITE_VERSION = (3, 31, 0)
    DPI: pint.Quantity = 300 / unit_registry.inch
    IMAGE_WIDTH: pint.Quantity = unit_registry("63 millimeter")
    IMAGE_HEIGHT: pint.Quantity = unit_registry("88 millimeter")

    total_cards_per_page_changed = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)
        self.file_path: typing.Optional[pathlib.Path] = None
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
        self.total_cards_per_page = self.compute_total_cards_per_page()
        self.add_page()
        
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
        previous_card_count = self.total_cards_per_page
        self.total_cards_per_page = self.compute_total_cards_per_page()
        if self.total_cards_per_page != previous_card_count:
            self.total_cards_per_page_changed.emit(self.total_cards_per_page)
        if self.total_cards_per_page < previous_card_count:
            self._move_excess_images_to_free_pages()

    @pyqtSlot()
    @pyqtSlot(int)
    def add_page(self, position: int = None) -> Page:
        position = self.rowCount() if position is None else min(position, self.rowCount())
        if position < 0:
            raise ValueError("Attempted to add a page at a negative position.")
        self.beginInsertRows(QModelIndex(), position, position)
        page = Page(parent=self)
        if position == self.rowCount():
            self.pages.append(page)
        else:
            self.pages.insert(position, page)
        page.dataChanged.connect(self.on_page_data_changed)
        self.endInsertRows()
        return page

    @pyqtSlot(list)
    def remove_pages(self, indices: typing.List[QModelIndex]):
        if not indices:
            return
        first_index, last_index = indices[0].row(), indices[-1].row()
        self.beginRemoveRows(QModelIndex(), first_index, last_index)
        to_delete = set(index.row() for index in indices)
        remaining = []
        for index, page in enumerate(self.pages):
            if index in to_delete:
                page.dataChanged.disconnect(self.on_page_data_changed)
            else:
                remaining.append(page)
        self.pages[:] = remaining
        self.endRemoveRows()
        if not self.pages:
            self.add_page()
        
    def rowCount(self, parent: QModelIndex = None) -> int:
        return len(self.pages)
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> typing.Any:

        if 0 < index.row() >= self.rowCount():
            print(f"Warning: Invalid index: {index.row()=}, {index.column()=}, {self.rowCount()=}, {index.isValid()=}")
            item = self.pages[0]
        else:
            item = self.pages[index.row()]
        if role == Qt.DisplayRole:
            return item.get_preview()
        elif role == Qt.ToolTipRole:
            return f"Page {index.row()+1}/{self.rowCount()}"
        elif role == Qt.EditRole:
            return item

    @pyqtSlot(QModelIndex)
    def on_page_data_changed(self, page_model_index: QModelIndex):
        page: Page = page_model_index.model()
        index = self.createIndex(self.pages.index(page), 0)
        self.dataChanged.emit(index, index)

    def compute_cards_per_row(self) -> int:
        total_width: pint.Quantity = self.page_width * unit_registry.millimeter
        margins: pint.Quantity = (self.margin_left + self.margin_right) * unit_registry.millimeter
        spacing: pint.Quantity = self.image_spacing_horizontal * unit_registry.millimeter

        total_width -= margins
        if total_width < Document.IMAGE_WIDTH:
            return 0
        total_width -= Document.IMAGE_WIDTH
        cards = total_width/(Document.IMAGE_WIDTH+spacing)+1
        return int(cards.to_tuple()[0])

    def compute_row_count(self) -> int:
        total_height: pint.Quantity = self.page_height * unit_registry.millimeter
        margins: pint.Quantity = (self.margin_top + self.margin_bottom) * unit_registry.millimeter
        spacing: pint.Quantity = self.image_spacing_vertical * unit_registry.millimeter
        total_height -= margins
        if total_height < Document.IMAGE_HEIGHT:
            return 0
        total_height -= Document.IMAGE_HEIGHT
        cards = total_height/(Document.IMAGE_HEIGHT+spacing)+1
        return int(cards.to_tuple()[0])

    def compute_total_cards_per_page(self) -> int:
        return self.compute_row_count() * self.compute_cards_per_row()

    def load_from_disk(self, path: pathlib.Path, card_db: CardDatabase, image_db: ImageDatabase):
        self.file_path = path
        with mtg_proxy_printer.sqlite_helpers.open_database(
                self.file_path, "document", self.MIN_SUPPORTED_SQLITE_VERSION) as db:
            data = db.execute(
                "SELECT page, slot, scryfall_id\n"
                "FROM Card\n"
                "ORDER BY page, slot ASC").fetchall()
        if self.pages:
            self.beginRemoveRows(QModelIndex(), 0, self.rowCount())
            for page in self.pages:
                page.dataChanged.disconnect(self.on_page_data_changed)
            self.pages.clear()
            self.endRemoveRows()

        current_page = None
        for page_number, slot, scryfall_id in data:
            if current_page != page_number:
                current_page = page_number
                self.add_page()
            if not card_db.is_scryfall_id_known(scryfall_id):
                # If the save file was tampered with or the database used to save contained more cards than the
                # currently used one, the save may contain unknown Scryfall IDs. So skip all unknown data.
                continue
            page = self.pages[-1]
            card = card_db.get_card_with_scryfall_id(scryfall_id)
            image_db.get_image(card)
            page.add_card(card)

    def save_as(self, path: pathlib.Path):
        self.file_path = path
        self.save_to_disk()

    def save_to_disk(self):
        if self.file_path is None:
            raise RuntimeError("Cannot save without a file path!")
        cards = (
            zip(itertools.repeat(page_index), enumerate((card.scryfall_id for card in page.cards), start=1))
            for page_index, page in enumerate(self.pages, start=1)
        )
        flattened_data = (
            (page, slot, scryfall_id)
            for (page, (slot, scryfall_id))
            in itertools.chain.from_iterable(cards)
        )
        with mtg_proxy_printer.sqlite_helpers.open_database(
                self.file_path, "document", self.MIN_SUPPORTED_SQLITE_VERSION) as db:
            db.execute("BEGIN TRANSACTION")
            db.execute("DELETE FROM Card")
            db.executemany(
                "INSERT INTO Card (page, slot, scryfall_id) VALUES (?, ?, ?)",
                flattened_data
            )
            db.commit()

    @pyqtSlot()
    def compact_pages(self):
        """
        Compacts a document by filling as many empty slots as possible on pages that are not at the end of the document.

        Scans the document for pages that are not completely filled and for each such page,
        moves cards from the last page with items to it.
        This fills all (but the last) pages up to the capacity limit to help reducing possible waste during printing.
        """
        maximum_cards_per_page = self.compute_total_cards_per_page()
        last_index = self.rowCount() - 1
        current_index = 0
        for current_index, current_page in enumerate(self.pages[:-1]):  # Can never add images to the last page
            if cards_to_add := maximum_cards_per_page - current_page.rowCount():
                while cards_to_add and current_index < last_index:
                    cards_to_add -= self._move_images_to_fill_page(current_page, self.pages[last_index])
                    if not self.pages[last_index].rowCount():
                        last_index -= 1
                if current_index == last_index:  # No more pages available to take cards from
                    break
        # Subtract 2 (two) to skip the last page, which this algorithm must not look at. Otherwise the last page will
        # get lost when compacting an already compacted document.
        if current_index < self.rowCount() - 2:
            empty_trailing_pages = [self.createIndex(row, 0) for row in range(current_index+1, self.rowCount())]
            self.remove_pages(empty_trailing_pages)

    def _move_images_to_fill_page(self, page_to_fill: Page, source: Page) -> int:
        """
        Moves min(free_slots_in_target, cards_in_source) items from the source page to the target page.

        :return: Number of moved images

        """
        cards_per_page = self.compute_total_cards_per_page()
        card_count_to_move = min(cards_per_page - page_to_fill.rowCount(), source.rowCount())
        if not card_count_to_move:
            return 0
        cards_to_move = source.cards[:card_count_to_move]
        source_model_indices_to_remove = [source.createIndex(row, 0) for row in range(card_count_to_move)]
        source.remove_cards(source_model_indices_to_remove)
        for card in cards_to_move:
            page_to_fill.add_card(card)
        return card_count_to_move

    def _move_excess_images_to_free_pages(self) -> int:
        """
        If the page capacity is reduced due to increased margins, spacing or reduced page size, images beyond the
        page capacity should be moved from overflowing pages to free slots and potentially new pages at the end.

        :return: Number of moved images
        """
        current_capacity = self.compute_total_cards_per_page()
        if not current_capacity:
            raise RuntimeError("Page capacity is zero!")
        excess_images = []
        for page in self.pages:
            images_on_page = page.rowCount()
            if images_on_page > current_capacity:
                to_remove = [
                    page.createIndex(row, 0)
                    # Qt includes the last value in a range and Python excludes it, so add one to the range 'stop'
                    for row in range(current_capacity, images_on_page + 1)
                ]
                excess_images += page.cards[current_capacity: images_on_page]
                page.remove_cards(to_remove)
        total_moved_images = len(excess_images)
        for page in self.pages:
            images_on_page = page.rowCount()
            if free_slots := current_capacity - images_on_page:
                to_add = excess_images[:free_slots]
                excess_images = excess_images[free_slots:]
                for card in to_add:
                    page.add_card(card)
        while excess_images:
            page = self.add_page()
            to_add = excess_images[:current_capacity]
            excess_images = excess_images[current_capacity:]
            for card in to_add:
                page.add_card(card)
        return total_moved_images
