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

import collections
import itertools
import pathlib
import sqlite3
import typing

import delegateto
import pint
from PyQt5.QtCore import QAbstractListModel, QAbstractTableModel, QModelIndex, Qt, pyqtSlot, pyqtSignal, QObject, \
    QThread

import mtg_proxy_printer.sqlite_helpers
from mtg_proxy_printer.model.carddb import Card, CardDatabase
from mtg_proxy_printer.model.imagedb import ImageDatabase, ImageDownloader
from mtg_proxy_printer.settings import settings
from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger

CardList = typing.List[Card]
DocumentSaveFormat = typing.Iterable[typing.Tuple[int, int, str, bool]]
unit_registry = pint.UnitRegistry()

__all__ = [
    "Page",
    "PageList",
    "Document",
]


@delegateto.delegate("cards", "__len__")
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
        return len(Page.header)
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> typing.Any:
        card = self.cards[index.row()]
        if role in (Qt.DisplayRole, Qt.EditRole):
            if index.column() == 0:
                return card.name
            elif index.column() == 1:
                if role == Qt.EditRole:
                    return card.set_abbr
                else:
                    return f"{card.set_name} ({card.set_abbr.upper()})"
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
        self.dataChanged.emit(
            self.createIndex(first_index, 0),
            self.createIndex(last_index, self.columnCount()-1)
        )

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
            return sum(map(self.remove_cards, ranges))

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

    def clear(self):
        self.remove_cards(list(map(
            self.createIndex,
            range(self.rowCount()),
            itertools.repeat(0)
        )))

    def get_content_as_scryfall_ids(self) -> typing.Iterable[typing.Tuple[str, bool]]:
        return ((card.scryfall_id, card.is_front) for card in self.cards)

    
PageList = typing.List[Page]


@delegateto.delegate("pages", "__len__")
class Document(QAbstractListModel):
    """
    This is the root of a multi-page document that contains any number of same-size pages.
    The pages hold the individual proxy images
    """

    MIN_SUPPORTED_SQLITE_VERSION = (3, 31, 0)
    DPI: pint.Quantity = 300 / unit_registry.inch
    IMAGE_WIDTH: pint.Quantity = unit_registry("63 millimeter")
    IMAGE_HEIGHT: pint.Quantity = unit_registry("88 millimeter")

    loading_state_changed = pyqtSignal(bool)
    total_cards_per_page_changed = pyqtSignal(int)
    document_cleared = pyqtSignal()

    def __init__(self, card_db: CardDatabase, image_db: ImageDatabase, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)
        self.file_path: typing.Optional[pathlib.Path] = None
        self.pages: PageList = []
        self.card_db = card_db
        self.loader = DocumentLoader(card_db, image_db, self)
        self.loader.loading_state_changed.connect(self.loading_state_changed)
        self.add_page()
        self.currently_edited_page = self.pages[0]
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

    @pyqtSlot(Page)
    def on_currently_edited_page_changed(self, new_page: Page):
        self.currently_edited_page = new_page

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
            self.move_excess_images_to_free_pages()

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

    @pyqtSlot(Card, int)
    def add_card(self, card: Card, copies: int):
        page_capacity = self.compute_total_cards_per_page()
        if current_page_capacity := page_capacity - self.currently_edited_page.rowCount():
            self.currently_edited_page.add_card(card, min(copies, current_page_capacity))
            copies -= current_page_capacity
        current_page_position = self.pages.index(self.currently_edited_page) + 1
        while copies > 0 and current_page_position < self.rowCount():
            page = self.pages[current_page_position]
            if current_page_capacity := page_capacity - page.rowCount():
                page.add_card(card, min(copies, current_page_capacity))
                copies -= current_page_capacity
            current_page_position += 1
        while copies > 0:
            self.add_page(current_page_position).add_card(card, min(copies, page_capacity))
            # Increment the index for each page. If the added amount is not divisible by the page_capacity, this causes
            # the last-added page to be non-full, instead of the first one in document page order.
            current_page_position += 1
            copies -= page_capacity

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
            self.currently_edited_page = self.pages[0]
            self.document_cleared.emit()
        
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

    def save_as(self, path: pathlib.Path):
        self.file_path = path
        self.save_to_disk()

    def save_to_disk(self):
        if self.file_path is None:
            raise RuntimeError("Cannot save without a file path!")
        cards = (
            zip(itertools.repeat(page_index), enumerate((
                (card.scryfall_id, card.is_front) for card in page.cards), start=1))
            for page_index, page in enumerate(self.pages, start=1)
        )
        flattened_data: DocumentSaveFormat = (
            (page, slot, scryfall_id, is_front)
            for (page, (slot, (scryfall_id, is_front)))
            in itertools.chain.from_iterable(cards)
        )
        with mtg_proxy_printer.sqlite_helpers.open_database(
                self.file_path, "document", self.MIN_SUPPORTED_SQLITE_VERSION) as db:
            db.execute("BEGIN TRANSACTION")
            _migrate_database(db)
            db.execute("DELETE FROM Card")
            db.executemany(
                "INSERT INTO Card (page, slot, scryfall_id, is_front) VALUES (?, ?, ?, ?)",
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
        if self.rowCount() <= 1:  # Can not compact an empty document or a document with a single empty page.
            return
        maximum_cards_per_page = self.compute_total_cards_per_page()
        last_index = self.rowCount() - 1
        for current_index, current_page in enumerate(self.pages[:-1]):  # Can never add images to the last page
            if cards_to_add := maximum_cards_per_page - current_page.rowCount():
                while cards_to_add and current_index < last_index:
                    cards_to_add -= self._move_images_to_fill_page(current_page, self.pages[last_index])
                    if not self.pages[last_index].rowCount():
                        last_index -= 1
                if current_index == last_index:  # No more pages available to take cards from
                    break

        empty_trailing_pages = [
            self.createIndex(row, 0) for row in range(1, self.rowCount()) if not self.pages[row].rowCount()
        ]
        self.remove_pages(empty_trailing_pages)

    def compute_pages_saved_by_compacting(self) -> int:
        """
        Computes the number of pages that can be saved by compacting the document.
        """
        if self.rowCount() <= 1:  # Can not compact an empty document or a document with a single empty page.
            return 0
        single_page_capacity = self.compute_total_cards_per_page()
        maximum_document_capacity = single_page_capacity * self.rowCount()
        total_cards_in_document = sum(map(len, self.pages))
        if total_cards_in_document != 0:
            result = (maximum_document_capacity - total_cards_in_document) // single_page_capacity
        else:
            # This is a special case that is not handled correctly by the formula above. If the document
            # is empty, it can not be compacted to zero pages, but one.
            result = self.rowCount() - 1
        return result

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

    def move_excess_images_to_free_pages(self) -> int:
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
                # Qt includes the last value in a range and Python excludes it, so add one to the range 'stop'
                to_remove = list(map(
                    page.createIndex,
                    range(current_capacity, images_on_page+1),
                    itertools.repeat(0)
                ))
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

    @pyqtSlot()
    def clear(self):
        logger.info("Clearing current document")
        self.remove_pages(list(map(
            self.createIndex,
            range(self.rowCount()),
            itertools.repeat(0)
        )))

    def store_image_usage(self):
        """
        Increments the usage count of all cards used in the document and updates the last use timestamps.
        Should be called after a successful PDF export and direct printing.
        """
        logger.info("Updating image usage for all cards in the document.")
        data = set(itertools.chain.from_iterable(page.get_content_as_scryfall_ids() for page in self.pages))
        self.card_db.begin_transaction()
        self.card_db.db.executemany(
            r"""
            INSERT INTO LastImageUseTimestamps (scryfall_id, is_front)
              VALUES (?, ?)
              ON CONFLICT (scryfall_id, is_front)
              DO UPDATE SET usage_count = usage_count + 1, last_use_date = CURRENT_TIMESTAMP;
            """,
            data
        )
        self.card_db.commit()


class DocumentLoader(QObject):
    """
    Implements asynchronous background document loading.
    Loading a document can take a long time, if it includes downloading all card images and still takes a noticeable
    time when the card images have to be loaded from disk.

    This class uses a QThread with a background worker to push that work off the GUI thread to keep the application
    responsive during a loading process.
    """

    loading_state_changed = pyqtSignal(bool)
    unknown_scryfall_ids_found = pyqtSignal(int)
    error_loading_file_occured = pyqtSignal(pathlib.Path)

    class Worker(QObject):
        """
        This is the worker object that runs inside the DocumentLoader’s internal QThread.

        It iterates over the loaded data and creates a stream of events that, when executed sequentially,
        load the document. It does not directly edit the Document instance.
        Events are created by simply emitting the defined Qt Signals. The DocumentLoader living in the GUI thread will
        receive these and update the document living in the same thread accordingly.
        This prevents issues with QObject instances getting parents assigned across threads.

        Because the thread emits the signals after each long-running I/O process (image loading or downloading)
        finished, processing the generated events in the GUI thread is fast.
        """

        # These signals are used to enqueue a stream of commands across thread boundaries.
        new_page = pyqtSignal()
        add_card = pyqtSignal(Card)
        finished = pyqtSignal()
        error_loading_file_occured = pyqtSignal(pathlib.Path)
        document_clear_requested = pyqtSignal()
        unknown_scryfall_ids_found = pyqtSignal(int)

        def __init__(self, card_db: CardDatabase, image_db: ImageDatabase, document: Document):
            super(DocumentLoader.Worker, self).__init__(None)
            self.card_db = card_db
            # Create our own ImageDownloader, instead of using the ImageDownloader embedded in the ImageDatabase.
            # That one lives in it’s own thread and runs asynchronously and is connected in a way that it adds loaded
            # images to the document on it’s own, interfering with the loading process, in particular with emitting page
            # breaks. Thus create a separate instance and use it synchronously inside this worker thread.
            self.image_loader = ImageDownloader(image_db, self)
            self.image_loader.card_download_starting.connect(image_db.card_download_starting)
            self.image_loader.card_download_finished.connect(image_db.card_download_finished)
            self.image_loader.card_download_progress.connect(image_db.card_download_progress)
            self.document = document
            self.save_path = pathlib.Path()
            self.data: typing.List[typing.Tuple[int, int, str, bool]] = []

        def load_document(self):
            unknown_ids = 0
            try:
                unknown_ids = self._load_document()
            except sqlite3.DatabaseError:
                logger.warning(f"Selected file is not an MTGProxyPrinter document. Not loading it.")
                self.error_loading_file_occured.emit(self.save_path)
            finally:
                if unknown_ids:
                    self.unknown_scryfall_ids_found.emit(unknown_ids)
                self.finished.emit()

        def _load_document(self) -> int:
            data = self._read_data_from_save_path(self.save_path)
            self.document_clear_requested.emit()
            logger.info("Start filling pages with cards from loaded data")
            current_page = 1
            unknown_ids = 0
            for page_number, slot, scryfall_id, is_front in data:
                if current_page != page_number:
                    current_page = page_number
                    self.new_page.emit()
                card = self.card_db.get_card_with_scryfall_id(scryfall_id, is_front)
                if card is None:
                    # If the save file was tampered with or the database used to save contained more cards than the
                    # currently used one, the save may contain unknown Scryfall IDs. So skip all unknown data.
                    unknown_ids += 1
                    logger.info(f"Unknown ID found in document: {scryfall_id=}, {is_front=}")
                    continue
                self.image_loader.get_image_synchronous(card)
                self.add_card.emit(card)
            self.data.clear()
            return unknown_ids

        @staticmethod
        def _read_data_from_save_path(save_file_path: pathlib.Path) -> DocumentSaveFormat:
            logger.info("Reading data from save file")
            with mtg_proxy_printer.sqlite_helpers.open_database(
                    save_file_path, "document", Document.MIN_SUPPORTED_SQLITE_VERSION) as db:
                if db.execute("PRAGMA application_id").fetchone()[0] != 41325044:
                    raise sqlite3.DatabaseError("Not an MTGProxyPrinter save file!")

                if db.execute("PRAGMA user_version").fetchone()[0] == 2:
                    query = r"""SELECT page, slot, scryfall_id, 1 AS is_front
                    FROM Card
                    ORDER BY page, slot ASC"""
                else:
                    query = r"""SELECT page, slot, scryfall_id, is_front
                    FROM Card
                    ORDER BY page, slot ASC"""
                data = [
                    (page, slot, scryfall_id, bool(is_front))
                    for page, slot, scryfall_id, is_front in db.execute(query)
                ]
            return data

    def __init__(self, card_db: CardDatabase, image_db: ImageDatabase, document: Document):
        super(DocumentLoader, self).__init__(None)
        self.document = document
        self.worker_thread = QThread()
        self.worker = self.Worker(card_db, image_db, document)
        self.worker.moveToThread(self.worker_thread)
        self.worker.document_clear_requested.connect(self.document.clear)
        self.worker.new_page.connect(self.document.add_page)
        self.worker.add_card.connect(self._on_add_card)
        # Relay two errors/warnings. Can be used to notify the user by displaying some message box with relevant info
        self.worker.error_loading_file_occured.connect(self.error_loading_file_occured)
        self.worker.unknown_scryfall_ids_found.connect(self.unknown_scryfall_ids_found)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(lambda: self.loading_state_changed.emit(False))
        self.worker_thread.started.connect(self.worker.load_document)

    @pyqtSlot(Card)
    def _on_add_card(self, card: Card):
        self.document.pages[-1].add_card(card)

    def load_document(self, save_file_path: pathlib.Path):
        logger.info(f"Loading document from {save_file_path}")
        self.loading_state_changed.emit(True)
        self.worker.save_path = save_file_path
        self.worker_thread.start()


def _migrate_database(db):
    if (schema_version := db.execute("PRAGMA user_version").fetchone()[0]) == 2:
        db.execute("ALTER TABLE Card ADD COLUMN is_front INTEGER NOT NULL CHECK (is_front IN (0, 1)) DEFAULT 1")
        db.execute(f"PRAGMA user_version = 3")
