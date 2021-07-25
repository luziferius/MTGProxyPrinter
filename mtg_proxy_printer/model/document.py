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
import dataclasses
import enum
import itertools
import pathlib
import socket
import sqlite3
import typing
import urllib.error

import pint
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt, pyqtSlot, pyqtSignal, QObject, QThread

import mtg_proxy_printer.sqlite_helpers
from mtg_proxy_printer.model.carddb import Card, CardDatabase
from mtg_proxy_printer.model.card_list import PageColumns
from mtg_proxy_printer.model.imagedb import ImageDatabase, ImageDownloader
from mtg_proxy_printer.settings import settings
from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger


DocumentSaveFormat = typing.Iterable[typing.Tuple[int, int, str, bool]]
unit_registry = pint.UnitRegistry()

__all__ = [
    "PageList",
    "Document",
]


class DocumentColumns(enum.IntEnum):
    Page = 0


@dataclasses.dataclass
class CardContainer:
    parent: list
    card: Card


CardList = typing.List[CardContainer]
PageList = typing.List[CardList]


class Document(QAbstractItemModel):
    """
    This holds a multi-page document that contains any number of same-size pages.
    The pages hold the individual proxy images
    """

    MIN_SUPPORTED_SQLITE_VERSION = (3, 31, 0)
    DPI: pint.Quantity = 300 / unit_registry.inch
    IMAGE_WIDTH: pint.Quantity = unit_registry("63 millimeter")
    IMAGE_HEIGHT: pint.Quantity = unit_registry("88 millimeter")

    loading_state_changed = pyqtSignal(bool)
    total_cards_per_page_changed = pyqtSignal(int)
    document_cleared = pyqtSignal()

    page_header = {
        PageColumns.CardName: "Card name",
        PageColumns.Set: "Set",
        PageColumns.CollectorNumber: "Collector #",
        PageColumns.Language: "Language",
        PageColumns.Image: "Image",
    }

    def __init__(self, card_db: CardDatabase, image_db: ImageDatabase, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)
        self.save_file_path: typing.Optional[pathlib.Path] = None
        self.card_db = card_db
        self.loader = DocumentLoader(card_db, image_db, self)
        self.loader.loading_state_changed.connect(self.loading_state_changed)
        self.pages: PageList = []
        self.add_page()
        self.currently_edited_page = self.pages[0]  # TODO: Attribute deprecated
        document_settings = settings["documents"]
        self.page_height = document_settings.getint("paper-height-mm")
        self.page_width = document_settings.getint("paper-width-mm")
        self.margin_top = document_settings.getint("margin-top-mm")
        self.margin_bottom = document_settings.getint("margin-bottom-mm")
        self.margin_left = document_settings.getint("margin-left-mm")
        self.margin_right = document_settings.getint("margin-right-mm")
        self.image_spacing_horizontal = document_settings.getint("image-spacing-horizontal-mm")
        self.image_spacing_vertical = document_settings.getint("image-spacing-vertical-mm")
        self.total_cards_per_page = self.compute_page_card_capacity()

    def headerData(
            self, section: typing.Union[int, PageColumns],
            orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> str:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return Document.page_header[section]
        return super(Document, self).headerData(section, orientation, role)

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
        self.total_cards_per_page = self.compute_page_card_capacity()
        if self.total_cards_per_page != previous_card_count:
            self.total_cards_per_page_changed.emit(self.total_cards_per_page)
        if self.total_cards_per_page < previous_card_count:
            self.move_excess_images_to_free_pages()

    @pyqtSlot()
    @pyqtSlot(int)
    def add_page(self, position: int = None) -> CardList:
        position = self.rowCount() if position is None else max(0, min(position, self.rowCount()))
        self.beginInsertRows(QModelIndex(), position, position)
        new_page: CardList = []
        if position == self.rowCount():
            self.pages.append(new_page)
        else:
            self.pages.insert(position, new_page)
        self.endInsertRows()
        return new_page

    @pyqtSlot(Card, int)
    def add_card(self, card: Card, copies: int):
        """
        Adds the given card copies times to the currently edited page. If copies is greater than the number of
        free slots on that page, add the remaining card copies to free slots in subsequent pages.
        If that is insufficient, add and fill new pages at the document end to fulfil the required copies.
        """
        current_page_position = self.find_page_list_index(self.currently_edited_page)
        copies -= (added_cards := self._add_card(current_page_position, card, copies))
        logger.debug(f"Added {added_cards} cards to page {current_page_position}. Remaining to add: {copies}")
        current_page_position += 1
        while copies > 0 and current_page_position < self.rowCount():
            copies -= (added_cards := self._add_card(current_page_position, card, copies))
            logger.debug(f"Added {added_cards} cards to page {current_page_position}. Remaining to add: {copies}")
            current_page_position += 1
        if copies > 0:
            logger.debug("No empty slots found, appending new pages to the document, until all copies are added.")
        while copies > 0:
            # Append each new page to the end. If the added amount is not divisible by the page_capacity, this causes
            # the last-added page to be non-full, instead of the first one in document page order.
            self.add_page()
            copies -= (added_cards := self._add_card(current_page_position, card, copies))
            logger.debug(f"Added {added_cards} cards to page {current_page_position}. Remaining to add: {copies}")
            current_page_position += 1

    def _add_card(self, page_number: int, card: Card, count: int = 1) -> int:
        """
        Adds the given card up to count times to the given page. Returns the number of cards actually added.
        Only adds cards up to the page capacity, so may add less than count cards, if that would overflow the page.
        """
        page_capacity = self.compute_page_card_capacity()
        page_index = self.index(page_number, 0)
        page_card_count = self.rowCount(page_index)
        first_index, last_index = page_card_count, page_card_count + count - 1
        if last_index >= page_capacity:
            last_index = page_capacity - 1
        cards_inserted = last_index - first_index + 1
        if not cards_inserted:
            logger.debug(f"Trying to add {count} cards into full page {page_number}. Doing nothing")
            return 0
        self.beginInsertRows(page_index, first_index, last_index)
        page = self.pages[page_number]
        page += (CardContainer(page, card) for _ in range(cards_inserted))
        logger.debug(f"After insert, page contains {len(page)} images.")
        self.endInsertRows()
        logger.debug(f'Added {cards_inserted} × "{card.name}" to page {page_number}')
        return cards_inserted

    @pyqtSlot(list)
    def remove_pages(self, indices: typing.List[QModelIndex]):
        if not indices:
            return
        if any(index.parent().isValid() for index in indices):
            raise RuntimeError("Tried to remove a Card in remove_pages()!")
        first_index, last_index = indices[0].row(), indices[-1].row()
        self.beginRemoveRows(QModelIndex(), first_index, last_index)
        to_delete = set(index.row() for index in indices)
        remaining = (page for index, page in enumerate(self.pages) if index not in to_delete)
        self.pages[:] = remaining
        self.endRemoveRows()
        if not self.pages:
            self.add_page()
            self.currently_edited_page = self.pages[0]
            self.document_cleared.emit()

    @pyqtSlot(list)
    def remove_card_multi_selection(self, indices: typing.List[QModelIndex]) -> int:
        """
        Remove all cards in the given multi-selection.

        :param indices: List with QModelIndex instances that represents a multi-selection.
          As returned by a QSelectionModel
        :return: Number of cards removed
        """
        current_range: typing.List[QModelIndex] = []
        ranges = []
        for index in indices:
            if not index.parent().isValid():
                raise RuntimeError("Tried to remove a page in remove_card_multi_selection()!")
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
        self.beginRemoveRows(indices[0].parent(), first_index, last_index)
        page: CardList = indices[0].parent().internalPointer()
        del page[first_index:last_index+1]
        self.endRemoveRows()
        return last_index - first_index
        
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        If parent is valid index, i.e. points to a page, returns the number of cards in that page.
        Otherwise returns the number of pages.
        """
        if parent.isValid() and parent.parent().isValid():
            return 0  # child rowCount of a Card instance. Always zero.
        elif parent.isValid():
            return len(parent.data(Qt.EditRole))  # child rowCount of a page. Number of cards in that page
        else:
            return len(self.pages)  # rowCount of an invalid index. Number of pages in the document.

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid() and parent.parent().isValid():
            return 0  # child columnCount of a Card instance. Always zero.
        elif parent.isValid():
            return len(PageColumns)  # child columnCount of a page. Number of shown Card fields
        else:
            return len(DocumentColumns)  # columnCount of an invalid index.

    def parent(self, child: QModelIndex) -> QModelIndex:
        data: typing.Union[CardList, CardContainer] = child.internalPointer()
        if isinstance(data, CardContainer):
            page = data.parent
            return self.createIndex(self.find_page_list_index(page), 0, page)
        return QModelIndex()  # Pages have no parent

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if self.rowCount(parent) <= row < 0 or self.columnCount(parent) <= column < 0:
            return QModelIndex()
        if parent.isValid():
            card_container = parent.data(Qt.EditRole)[row]
            index = self.createIndex(row, column, card_container)
            return index
        else:
            page = self.pages[row]
            return self.createIndex(row, column, page)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> typing.Any:
        if not index.isValid():
            return None
        if index.parent().isValid():  # Card
            return self._data_card(index, role)
        else:  # Page
            return self._data_page(index, role)

    def _data_page(self, index: QModelIndex, role: int = Qt.DisplayRole) -> typing.Any:
        """Returns the requested data for an index pointing to a page of Cards."""
        if 0 > index.row() >= self.rowCount() or not index.isValid():
            logger.error(f"Invalid index: {index.row()=}, {index.column()=}, {self.rowCount()=}, {index.isValid()=}")
            return None
        item: CardList = self.pages[index.row()]
        if role == Qt.DisplayRole:
            return self._get_page_preview(item)
        elif role == Qt.ToolTipRole:
            return f"Page {index.row()+1}/{self.rowCount()}"
        elif role == Qt.EditRole:
            return item

    def _data_card(self, index: QModelIndex, role: int = Qt.DisplayRole) -> typing.Any:
        """Returns the requested data for an index pointing to a single Card."""
        if 0 > index.row() >= self.rowCount(index) \
                or 0 > index.column() >= self.columnCount(index) \
                or not index.isValid():
            logger.error(
                f"Invalid index: {index.row()=}, {index.column()=}, "
                f"{self.rowCount(index.parent())=}, {index.isValid()=}")
            return None
        card: Card = index.internalPointer().card
        if role in (Qt.DisplayRole, Qt.EditRole):
            if index.column() == PageColumns.CardName:
                return card.name
            elif index.column() == PageColumns.Set:
                if role == Qt.EditRole:
                    return card.set.code
                else:
                    return f"{card.set.name} ({card.set.code.upper()})"
            elif index.column() == PageColumns.CollectorNumber:
                return card.collector_number
            elif index.column() == PageColumns.Language:
                return card.language
            elif index.column() == PageColumns.Image:
                return card.image_file

    @staticmethod
    def _get_page_preview(page: CardList):
        names = collections.Counter(container.card.name for container in page)
        return "\n".join(
            f"{count}× {name}" for name, count in names.items()
        )

    def compute_page_column_count(self) -> int:
        """Returns the total number of card columns that fit on a page."""
        total_width: pint.Quantity = self.page_width * unit_registry.millimeter
        margins: pint.Quantity = (self.margin_left + self.margin_right) * unit_registry.millimeter
        spacing: pint.Quantity = self.image_spacing_horizontal * unit_registry.millimeter

        total_width -= margins
        if total_width < Document.IMAGE_WIDTH:
            return 0
        total_width -= Document.IMAGE_WIDTH
        cards = total_width / (Document.IMAGE_WIDTH+spacing) + 1
        return int(cards.to_tuple()[0])

    def compute_page_row_count(self) -> int:
        """Returns the total number of card rows that fit on a page."""
        total_height: pint.Quantity = self.page_height * unit_registry.millimeter
        margins: pint.Quantity = (self.margin_top + self.margin_bottom) * unit_registry.millimeter
        spacing: pint.Quantity = self.image_spacing_vertical * unit_registry.millimeter
        total_height -= margins
        if total_height < Document.IMAGE_HEIGHT:
            return 0
        total_height -= Document.IMAGE_HEIGHT
        cards = total_height / (Document.IMAGE_HEIGHT+spacing) + 1
        return int(cards.to_tuple()[0])

    def compute_page_card_capacity(self) -> int:
        """Returns the total number of card images that fit on a single page."""
        return self.compute_page_row_count() * self.compute_page_column_count()

    def save_as(self, path: pathlib.Path):
        """Save the document at the given path, overwriting any previously stored save path."""
        self.save_file_path = path
        self.save_to_disk()

    def save_to_disk(self):
        """Save the document at the internally remembered save path. Raises a RuntimeError, if no such path is set."""
        if self.save_file_path is None:
            raise RuntimeError("Cannot save without a file path!")
        cards = (
            zip(itertools.repeat(page_index), enumerate((
                (container.card.scryfall_id, container.card.is_front) for container in page), start=1))
            for page_index, page in enumerate(self.pages, start=1)
        )
        flattened_data: DocumentSaveFormat = (
            (page, slot, scryfall_id, is_front)
            for (page, (slot, (scryfall_id, is_front)))
            in itertools.chain.from_iterable(cards)
        )
        with mtg_proxy_printer.sqlite_helpers.open_database(
                self.save_file_path, "document", self.MIN_SUPPORTED_SQLITE_VERSION) as db:
            db.execute("BEGIN TRANSACTION")
            _migrate_database(db)
            db.execute("DELETE FROM Card")
            db.executemany(
                "INSERT INTO Card (page, slot, scryfall_id, is_front) VALUES (?, ?, ?, ?)",
                flattened_data
            )
            db.commit()
            db.execute("VACUUM")

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
        maximum_cards_per_page = self.compute_page_card_capacity()
        last_index = self.rowCount() - 1
        for current_index, current_page in enumerate(self.pages[:-1]):  # Can never add images to the last page
            if cards_to_add := maximum_cards_per_page - len(current_page):
                while cards_to_add and current_index < last_index:
                    cards_to_add -= self._move_images(current_page, self.pages[last_index])
                    if not len(self.pages[last_index]):
                        last_index -= 1
                if current_index == last_index:  # No more pages available to take cards from
                    break
        empty_trailing_pages = [
            self.createIndex(row, 0) for row in range(1, self.rowCount()) if not len(self.pages[row])
        ]
        self.remove_pages(empty_trailing_pages)

    def compute_pages_saved_by_compacting(self) -> int:
        """
        Computes the number of pages that can be saved by compacting the document.
        """
        if self.rowCount() <= 1:  # Can not compact an empty document or a document with a single empty page.
            return 0
        single_page_capacity = self.compute_page_card_capacity()
        maximum_document_capacity = single_page_capacity * self.rowCount()
        total_cards_in_document = sum(map(len, self.pages))
        if total_cards_in_document != 0:
            result = (maximum_document_capacity - total_cards_in_document) // single_page_capacity
        else:
            # This is a special case that is not handled correctly by the formula above. If the document
            # is empty, it can not be compacted to zero pages, but one.
            result = self.rowCount() - 1
        return result

    def _move_images(self, page_to_fill: CardList, source: CardList, maximum_card_count: int = None) -> int:
        """
        Moves min(free_slots_in_target, maximum_card_count) cards from source to page_to_fill.
        If maximum_card_count is None, move as many cards as possible.
        """
        total_page_capacity = self.compute_page_card_capacity()
        source_card_count = len(source)
        target_card_count = len(page_to_fill)
        if maximum_card_count is None:
            maximum_card_count = source_card_count
        card_count_to_move = min(maximum_card_count, total_page_capacity - source_card_count)
        if not card_count_to_move:
            return 0

        source_page_index = self.createIndex(self.find_page_list_index(source), 0)
        target_page_index = self.createIndex(self.find_page_list_index(page_to_fill), 0)
        self.beginMoveRows(
            source_page_index,
            source_card_count - card_count_to_move, source_card_count,
            target_page_index,
            target_card_count
        )
        cards_to_move = source[:card_count_to_move]
        source[:] = source[:card_count_to_move]
        page_to_fill += cards_to_move
        self.endMoveRows()
        # TODO: Evaluate if it is necessary to emit dataChanged() for the top level source and target pages.
        #  It may be required, so that the GUI updates the page overview texts. If so, the {source,target}_page_index
        #  can be reused for that purpose.
        return card_count_to_move

    def find_page_list_index(self, other: CardList):
        for index, page in enumerate(self.pages):
            if page is other:
                return index
        raise ValueError("List not found in the page list.")

    def move_excess_images_to_free_pages(self) -> int:
        """
        If the page capacity is reduced due to increased margins, spacing or reduced page size, images beyond the
        page capacity should be moved from overflowing pages to free slots and potentially new pages at the end.

        :return: Number of moved images
        """
        total_page_capacity = self.compute_page_card_capacity()
        if not total_page_capacity:
            raise RuntimeError("Page capacity is zero!")
        overflowing_pages, pages_with_free_slots = self._find_overflowing_and_underflowing_pages(total_page_capacity)
        moved_images = 0
        for page in overflowing_pages:
            # Fill free slots on other pages first
            while (current_page_length := len(page)) > total_page_capacity and pages_with_free_slots:
                page_to_fill = pages_with_free_slots.pop(0)
                moved_images += self._move_images(page_to_fill, page, current_page_length-total_page_capacity)
            # After filling all remaining free slots, it may still contain images for multiple new pages,
            # so add new pages until all excess images are moved.
            while (current_page_length := len(page)) > total_page_capacity:
                page_to_fill = self.add_page(self.find_page_list_index(page)+1)
                moved_images += self._move_images(page_to_fill, page, current_page_length-total_page_capacity)
        return moved_images

    def _find_overflowing_and_underflowing_pages(self, total_page_capacity):
        """
        Returns two lists of pages: The first contains all pages that are currently overflowing,
        and the second contains that currently have free slots and therefore can fit additional cards.
        """
        overflowing_pages = []
        pages_with_free_slots: PageList = []
        for page_number, page in enumerate(self.pages):
            if len(page) > total_page_capacity:
                overflowing_pages.append(page)
            elif len(page) < total_page_capacity:
                pages_with_free_slots.append(page)
        return overflowing_pages, pages_with_free_slots

    @pyqtSlot()
    def clear(self):
        logger.info("Clearing current document")
        self.remove_pages(list(map(
            self.createIndex,
            range(self.rowCount()),
            itertools.repeat(0)
        )))

    @pyqtSlot()  # Avoid connecting both triggered() and triggered(bool)
    def clear_all_data(self):
        self.clear()
        self.save_file_path = None

    def store_image_usage(self):
        """
        Increments the usage count of all cards used in the document and updates the last use timestamps.
        Should be called after a successful PDF export and direct printing.
        """
        logger.info("Updating image usage for all cards in the document.")
        data = set(itertools.chain.from_iterable(
            map(self._get_page_content_as_scryfall_ids, self.pages)
        ))
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

    @staticmethod
    def _get_page_content_as_scryfall_ids(page: CardList) -> typing.Iterable[typing.Tuple[str, bool]]:
        return ((container.card.scryfall_id, container.card.is_front) for container in page)


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
    loading_file_failed = pyqtSignal(pathlib.Path)
    # Emitted when downloading required images during the loading process failed due to network issues.
    network_error_occurred = pyqtSignal(str)

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
        loading_file_failed = pyqtSignal(pathlib.Path)
        document_clear_requested = pyqtSignal()
        unknown_scryfall_ids_found = pyqtSignal(int)
        loading_file_successful = pyqtSignal(pathlib.Path)
        network_error_occurred = pyqtSignal(str)
        request_blank_pixmap = pyqtSignal(Card)

        def __init__(self, card_db: CardDatabase, image_db: ImageDatabase, document: Document):
            super(DocumentLoader.Worker, self).__init__(None)
            self.card_db = card_db
            self.image_db = image_db
            # Create our own ImageDownloader, instead of using the ImageDownloader embedded in the ImageDatabase.
            # That one lives in it’s own thread and runs asynchronously and is connected in a way that it adds loaded
            # images to the document on it’s own, interfering with the loading process, in particular with emitting page
            # breaks. Thus create a separate instance and use it synchronously inside this worker thread.
            self.image_loader = ImageDownloader(image_db, self)
            self.image_loader.card_download_starting.connect(image_db.card_download_starting)
            self.image_loader.card_download_finished.connect(image_db.card_download_finished)
            self.image_loader.card_download_progress.connect(image_db.card_download_progress)
            self.image_loader.network_error_occurred.connect(self.on_network_error_occurred)
            self.network_errors_during_load: typing.Counter[str] = collections.Counter()
            self.finished.connect(self.propagate_errors_during_load)
            self.document = document
            self.save_path = pathlib.Path()
            self.data: typing.List[typing.Tuple[int, int, str, bool]] = []
            self.should_run: bool = True

        def propagate_errors_during_load(self):
            if error_count := sum(self.network_errors_during_load.values()):
                self.network_error_occurred.emit(
                    f"Error count: {error_count}. Most common error message:\n"
                    f"{self.network_errors_during_load.most_common(1)[0][0]}"
                )
                self.network_errors_during_load.clear()

        def on_network_error_occurred(self, card: Card, error: str):
            card.image_file = self.image_db.blank_image
            self.network_errors_during_load[error] += 1

        def load_document(self):
            unknown_ids = 0
            self.should_run = True
            try:
                unknown_ids = self._load_document()
            except sqlite3.DatabaseError:
                logger.warning(f"Selected file is not an MTGProxyPrinter document. Not loading it.")
                self.loading_file_failed.emit(self.save_path)
            finally:
                if unknown_ids:
                    self.unknown_scryfall_ids_found.emit(unknown_ids)
                self.loading_file_successful.emit(self.save_path)
                self.finished.emit()

        def _load_document(self) -> int:
            data = self._read_data_from_save_path(self.save_path)
            self.document_clear_requested.emit()
            logger.info("Start filling pages with cards from loaded data")
            current_page = 1
            unknown_ids = 0
            for page_number, slot, scryfall_id, is_front in data:
                if not self.should_run:
                    logger.info("Cancel request received, stop processing the card list.")
                    return unknown_ids
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
                try:
                    self.image_loader.get_image_synchronous(card)
                except urllib.error.URLError as e:
                    self.on_network_error_occurred(card, str(e.reason))
                except socket.timeout as e:
                    self.on_network_error_occurred(card, f"Reading from socket failed: {e}")
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

        def cancel_running_operations(self):
            self.should_run = False
            if self.image_loader.currently_opened_file is not None:
                # Force aborting the download by closing the input stream
                self.image_loader.currently_opened_file.close()

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
        self.worker.loading_file_failed.connect(self.loading_file_failed)
        self.worker.unknown_scryfall_ids_found.connect(self.unknown_scryfall_ids_found)
        self.worker.loading_file_successful.connect(self.on_loading_file_successful)
        self.worker.network_error_occurred.connect(self.network_error_occurred)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(lambda: self.loading_state_changed.emit(False))
        self.worker_thread.started.connect(self.worker.load_document)

    def is_running(self) -> bool:
        return self.worker_thread.isRunning()

    @pyqtSlot(Card)
    def _on_add_card(self, card: Card):
        self.document._add_card(len(self.document.pages), card)

    def load_document(self, save_file_path: pathlib.Path):
        logger.info(f"Loading document from {save_file_path}")
        self.loading_state_changed.emit(True)
        self.worker.save_path = save_file_path
        self.worker_thread.start()

    def on_loading_file_successful(self, file_path: pathlib.Path):
        self.document.save_file_path = file_path

    def cancel_running_operations(self):
        """Can be called to cancel loading a document. This forces the """
        if not self.worker_thread.isRunning():
            return
        self.worker.cancel_running_operations()


def _migrate_database(db):
    if db.execute("PRAGMA user_version").fetchone()[0] == 2:
        db.execute("ALTER TABLE Card ADD COLUMN is_front INTEGER NOT NULL CHECK (is_front IN (0, 1)) DEFAULT 1")
        db.execute(f"PRAGMA user_version = 3")
