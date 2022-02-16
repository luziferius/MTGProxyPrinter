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
import functools
import itertools
import pathlib
import textwrap
import typing

from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt, pyqtSlot, pyqtSignal, QPersistentModelIndex

import mtg_proxy_printer.sqlite_helpers
from mtg_proxy_printer.model.carddb import Card, CardDatabase, CardIdentificationData
from mtg_proxy_printer.model.card_list import PageColumns
from mtg_proxy_printer.model.document_loader import DocumentLoader, DocumentSaveFormat, PageLayoutSettings
from mtg_proxy_printer.model.imagedb import ImageDatabase
from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger

__all__ = [
    "PageList",
    "Document",
    "CardContainer",
]


class DocumentColumns(enum.IntEnum):
    Page = 0


@dataclasses.dataclass
class CardContainer:
    parent: "CardList"
    card: Card


CardList = typing.List[CardContainer]
PageList = typing.List[CardList]

INVALID_INDEX = QModelIndex()


class Document(QAbstractItemModel):
    """
    This holds a multi-page document that contains any number of same-size pages.
    The pages hold the individual proxy images
    """
    loading_state_changed = pyqtSignal(bool)
    total_cards_per_page_changed = pyqtSignal(int)
    current_page_changed = pyqtSignal(QPersistentModelIndex)
    page_layout_changed = pyqtSignal()

    page_header = {
        PageColumns.CardName: "Card name",
        PageColumns.Set: "Set",
        PageColumns.CollectorNumber: "Collector #",
        PageColumns.Language: "Language",
        PageColumns.Image: "Image",
    }
    EDITABLE_COLUMNS = {PageColumns.Set, PageColumns.CollectorNumber}

    def __init__(self, card_db: CardDatabase, image_db: ImageDatabase, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)
        self.save_file_path: typing.Optional[pathlib.Path] = None
        self.card_db = card_db
        self.image_db = image_db
        self.image_db.replacement_obtained.connect(self._on_replacement_image_received)
        self.loader = DocumentLoader(card_db, image_db, self)
        self.loader.loading_state_changed.connect(self.loading_state_changed)
        self.pages: PageList = []
        self.page_index_cache: typing.Dict[int, int] = {}  # Mapping from page id() to list index in the page list
        self.add_page()
        self.currently_edited_page = self.pages[0]
        self.page_layout = PageLayoutSettings()
        self.page_layout.update_from_settings()
        self.total_cards_per_page = self.compute_page_card_capacity()

    def on_ui_selects_new_page(self, new_page: QModelIndex):
        if new_page.parent().isValid():
            error_message = "on_ui_selects_new_page() called with model index pointing to a card instead of a page"
            logger.error(error_message)
            raise RuntimeError(error_message)
        self.currently_edited_page = self.pages[new_page.row()]
        self.current_page_changed.emit(QPersistentModelIndex(new_page))

    def headerData(
            self, section: typing.Union[int, PageColumns],
            orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> str:
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return Document.page_header.get(section)
            elif role == Qt.ToolTipRole and section in self.EDITABLE_COLUMNS:
                return "Double-click on entries to\nswitch the selected printing."
        return super(Document, self).headerData(section, orientation, role)

    @pyqtSlot()
    def apply_settings(self):
        """Applies the current, relevant application settings to this document."""
        self.page_layout.update_from_settings()
        self.on_page_layout_updated()

    def on_page_layout_updated(self):
        previous_card_count = self.total_cards_per_page
        self.compute_page_row_count.cache_clear()
        self.compute_page_column_count.cache_clear()
        self.total_cards_per_page = self.compute_page_card_capacity()
        if self.total_cards_per_page != previous_card_count:
            self.total_cards_per_page_changed.emit(self.total_cards_per_page)
        if self.total_cards_per_page < previous_card_count:
            self.move_excess_cards_to_free_pages()
        self.page_layout_changed.emit()

    @pyqtSlot()
    @pyqtSlot(int)
    def add_page(self, position: int = None) -> CardList:
        position = self.rowCount() if position is None else max(0, min(position, self.rowCount()))
        self.beginInsertRows(INVALID_INDEX, position, position)
        new_page: CardList = []
        if position == self.rowCount():
            self.pages.append(new_page)
            self.page_index_cache[id(new_page)] = len(self.pages) - 1
        else:
            self.pages.insert(position, new_page)
            self._recreate_page_index_cache()
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
        if len(self.currently_edited_page) < self.total_cards_per_page:
            copies -= (added_cards := self.add_card_to_page(current_page_position, card, copies))
            logger.debug(f"Added {added_cards} cards to page {current_page_position}. Remaining to add: {copies}")
        current_page_position += 1
        while copies > 0 and current_page_position < self.rowCount():
            copies -= (added_cards := self.add_card_to_page(current_page_position, card, copies))
            logger.debug(f"Added {added_cards} cards to page {current_page_position}. Remaining to add: {copies}")
            current_page_position += 1
        if copies > 0:
            logger.debug("No empty slots found, appending new pages to the document, until all copies are added.")
        while copies > 0:
            # Append each new page to the end. If the added amount is not divisible by the page_capacity, this causes
            # the last-added page to be non-full, instead of the first one in document page order.
            self.add_page()
            copies -= (added_cards := self.add_card_to_page(current_page_position, card, copies))
            logger.debug(f"Added {added_cards} cards to page {current_page_position}. Remaining to add: {copies}")
            current_page_position += 1

    def add_card_to_page(self, page_number: int, card: Card, count: int = 1) -> int:
        """
        Adds the given card up to count times to the given page. Returns the number of cards actually added.
        Only adds cards up to the page capacity, so may add less than count cards, if that would overflow the page.
        """
        page_index = self.index(page_number, 0)
        page_card_count = self.rowCount(page_index)
        first_index, last_index = page_card_count, page_card_count + count - 1
        if last_index >= self.total_cards_per_page:
            last_index = self.total_cards_per_page - 1
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
        logger.debug(f"Removing pages {first_index} to {last_index}. {self.rowCount()=}")
        self.beginRemoveRows(INVALID_INDEX, first_index, last_index)
        logger.debug("BeginRemoveRows() called")
        to_delete = set(index.row() for index in indices)
        logger.debug(f"Rows to delete: {sorted(to_delete)}")
        remaining = (page for index, page in enumerate(self.pages) if index not in to_delete)
        self.pages[:] = remaining
        self._recreate_page_index_cache()
        self.endRemoveRows()
        if not self.pages:
            self.currently_edited_page = self.add_page()
            self.current_page_changed.emit(QPersistentModelIndex(self.index(0, 0)))

    @pyqtSlot(list)
    def remove_card_multi_selection(self, indices: typing.List[QModelIndex]) -> int:
        """
        Remove all cards in the given multi-selection.

        :param indices: List with QModelIndex instances that represents a multi-selection.
          As returned by a QSelectionModel.
        :return: Number of cards removed
        """
        current_range: typing.List[QModelIndex] = []
        ranges: typing.List[typing.List[QModelIndex]] = []
        for index in indices:
            if not index.parent().isValid():
                raise RuntimeError("Tried to remove a page in remove_card_multi_selection()!")
            if not current_range or index.row() == current_range[-1].row() + 1:
                current_range.append(index)
            else:
                ranges.append(current_range)
                current_range = [index]
        if current_range:
            ranges.append(current_range)
        if ranges:
            ranges.reverse()
            return sum(map(self.remove_cards, ranges))

    def clear_page(self, index: QModelIndex):
        if isinstance(index.internalPointer(), list):
            cards = list(map(index.child, range(self.rowCount(index)), itertools.repeat(0)))
            self.remove_cards(cards)

    @pyqtSlot(list)
    def remove_cards(self, indices: typing.List[QModelIndex]) -> int:
        """
        Remove all cards in the given list of consecutive model indices

        :return: Number of cards removed
        """
        if not indices:
            return 0
        first_index, last_index = indices[0].row(), indices[-1].row()
        parent = indices[0].parent()
        self.beginRemoveRows(parent, first_index, last_index)
        page: CardList = parent.internalPointer()
        del page[first_index:last_index+1]
        self.endRemoveRows()
        return last_index - first_index

    def rowCount(self, parent: QModelIndex = INVALID_INDEX) -> int:
        """
        If parent is valid index, i.e. points to a page, returns the number of cards in that page.
        Otherwise, returns the number of pages.
        """
        if isinstance(parent.internalPointer(), CardContainer):
            return 0  # child rowCount of a Card instance. Always zero.
        if parent.isValid():
            return len(parent.internalPointer())  # child rowCount of a page. Number of cards in that page
        else:
            return len(self.pages)  # rowCount of an invalid index. Number of pages in the document.

    def columnCount(self, parent: QModelIndex = INVALID_INDEX) -> int:
        if isinstance(parent.internalPointer(), CardContainer):
            return 0  # child columnCount of a Card instance. Always zero.
        elif parent.isValid():
            return len(PageColumns)  # child columnCount of a page. Number of shown Card fields
        else:
            return len(DocumentColumns)  # columnCount of an invalid index.

    def parent(self, child: QModelIndex) -> QModelIndex:
        data: typing.Union[CardList, CardContainer] = child.internalPointer()
        if isinstance(data, CardContainer):
            page = data.parent
            page_id = id(page)
            page_index = self.page_index_cache[page_id]
            return self.createIndex(page_index, 0, page)
        return INVALID_INDEX  # Pages have no parent

    def index(self, row: int, column: int, parent: QModelIndex = INVALID_INDEX) -> QModelIndex:
        data = parent.internalPointer()
        if isinstance(data, list):
            card_container = data[row]
            return self.createIndex(row, column, card_container)
        else:
            page = self.pages[row]
            return self.createIndex(row, column, page)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> typing.Any:
        if not index.isValid():
            return None
        if isinstance(index.internalPointer(), CardContainer):  # Card
            return self._data_card(index, role)
        else:  # Page
            return self._data_page(index, role)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        data = index.internalPointer()
        flags = super(Document, self).flags(index)
        if isinstance(data, CardContainer) and index.column() in self.EDITABLE_COLUMNS:
            flags |= Qt.ItemIsEditable
        return flags

    def setData(self, index: QModelIndex, value: typing.Any, role: int = Qt.EditRole) -> bool:
        data = index.internalPointer()
        if isinstance(data, CardContainer) and role == Qt.EditRole and index.column() in self.EDITABLE_COLUMNS:
            logger.debug(f"Setting model data for column {index.column()} to {value}")
            card: Card = index.internalPointer().card
            if index.column() == PageColumns.CollectorNumber:
                card_data = CardIdentificationData(
                    card.language, card.name, card.set.code, value, is_front=card.is_front)
            else:
                card_data = CardIdentificationData(
                    card.language, card.name, value, is_front=card.is_front
                )
            return self._request_replacement_card(index, card_data)
        return False

    def _request_replacement_card(self, index: QModelIndex, card_data: CardIdentificationData):
        if result := self.card_db.get_cards_from_data(card_data):
            logger.debug(f"Requesting replacement for card '{card_data.name}' in set {card_data.set_code}")
            # Simply choose the first match. The user can’t make a choice at this point, so just use one of
            # the results.
            new_card = result[0]
            self.image_db.get_replacement_card_image_asynchronous(new_card, QPersistentModelIndex(index))
            return True
        return False

    @pyqtSlot(Card, QPersistentModelIndex)
    def _on_replacement_image_received(self, card: Card, index: QPersistentModelIndex):
        if index.isValid():
            logger.debug(f'Received image for replaced card printing of "{card.name}".')
            top_left = index.sibling(index.row(), index.column())
            bottom_right = top_left.siblingAtColumn(PageColumns.Image)
            card_container: CardContainer = top_left.internalPointer()
            card_container.card = card
            self.dataChanged.emit(top_left, bottom_right, (Qt.DisplayRole, Qt.EditRole, Qt.ToolTipRole))

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
        if role in {Qt.DisplayRole, Qt.EditRole}:
            if index.column() == PageColumns.CardName:
                return card.name
            elif index.column() == PageColumns.Set:
                return card.set.data(role)
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

    @functools.lru_cache(maxsize=1)
    def compute_page_column_count(self) -> int:
        """Returns the total number of card columns that fit on a page."""
        return self.page_layout.compute_page_column_count()

    @functools.lru_cache(maxsize=1)
    def compute_page_row_count(self) -> int:
        """Returns the total number of card rows that fit on a page."""
        return self.page_layout.compute_page_row_count()

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
                self.save_file_path, "document-v4", self.loader.MIN_SUPPORTED_SQLITE_VERSION) as db:
            db.execute("BEGIN TRANSACTION")
            _migrate_database(db)
            db.execute("DELETE FROM Card")
            db.executemany(
                "INSERT INTO Card (page, slot, scryfall_id, is_front) VALUES (?, ?, ?, ?)",
                flattened_data
            )
            db.execute(
                textwrap.dedent("""\
                    INSERT INTO DocumentSettings (rowid, page_height, page_width,
                          margin_top, margin_bottom, margin_left, margin_right,
                          image_spacing_horizontal, image_spacing_vertical, draw_cut_markers)
                      VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """),
                dataclasses.astuple(self.page_layout))
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
        logger.info("Compacting document.")
        maximum_cards_per_page = self.total_cards_per_page
        last_index = self.rowCount() - 1
        for current_index, current_page in enumerate(self.pages[:-1]):  # Can never add images to the last page
            if cards_to_add := maximum_cards_per_page - len(current_page):
                logger.debug(f"Found {cards_to_add} empty slots on page {current_index}")
                while cards_to_add and current_index < last_index:
                    cards_to_add -= (moved_cards := self._move_cards(current_page, self.pages[last_index]))
                    logger.debug(f"Moved {moved_cards} from page {last_index} to page {current_index}. "
                                 f"Free slots in target: {maximum_cards_per_page-len(current_page)}")
                    if not self.pages[last_index]:
                        logger.debug(f"Last page {last_index} now empty.")
                        last_index -= 1
                    else:
                        logger.debug(f"Last page contains {len(self.pages[last_index])} cards.")
                if current_index == last_index:  # No more pages available to take cards from
                    logger.debug("No more pages available to take cards from. Finished.")
                    break

        empty_trailing_pages = list(map(
            self.index, range(last_index+1, self.rowCount()), itertools.repeat(0)
        ))

        logger.debug(f"Removing {len(empty_trailing_pages)} empty, trailing pages.")
        self.remove_pages(empty_trailing_pages)
        logger.info("Compacting done.")

    def compute_pages_saved_by_compacting(self) -> int:
        """
        Computes the number of pages that can be saved by compacting the document.
        """
        if self.rowCount() <= 1:  # Can not compact an empty document or a document with a single empty page.
            return 0
        maximum_document_capacity = self.total_cards_per_page * self.rowCount()
        total_cards_in_document = sum(map(len, self.pages))
        if total_cards_in_document:
            result = (maximum_document_capacity - total_cards_in_document) // self.total_cards_per_page
        else:
            # This is a special case that is not handled correctly by the formula above. If the document
            # is empty, it can not be compacted to zero pages, but one.
            result = self.rowCount() - 1
        return result

    def _move_cards(self, page_to_fill: CardList, source: CardList, maximum_card_count: int = None) -> int:
        """
        Moves min(free_slots_in_target, maximum_card_count) cards from source to page_to_fill.
        If maximum_card_count is None, move as many cards as possible.
        """
        source_card_count = len(source)
        target_card_count = len(page_to_fill)
        if maximum_card_count is None:
            maximum_card_count = source_card_count
        card_count_to_move = min(maximum_card_count, self.total_cards_per_page - target_card_count)
        if not card_count_to_move:
            return 0
        source_page_index = self.index(self.find_page_list_index(source), 0)
        target_page_index = self.index(self.find_page_list_index(page_to_fill), 0)
        self.beginMoveRows(
            source_page_index,
            source_card_count - card_count_to_move, source_card_count,
            target_page_index,
            target_card_count
        )
        cards_to_move = source[-card_count_to_move:]  # Move the last card_count_to_move cards
        source[:] = source[:source_card_count-card_count_to_move]  # Keep the remaining cards
        for container in cards_to_move:  # Re-parent containers before moving them to their new list
            container.parent = page_to_fill
        page_to_fill += cards_to_move
        self.endMoveRows()
        return card_count_to_move

    def find_page_list_index(self, other: CardList):
        """Finds the 0-indexed location of the given CardList in the pages list"""
        try:
            return self.page_index_cache[id(other)]
        except KeyError as k:
            raise ValueError("List not found in the page list.") from k

    def move_excess_cards_to_free_pages(self) -> int:
        """
        If the page capacity is reduced due to increased margins, spacing or reduced page size, images beyond the
        page capacity should be moved from overflowing pages to free slots and potentially new pages at the end.

        :return: Number of moved images
        """
        if not self.total_cards_per_page:
            raise RuntimeError("Page capacity is zero!")
        overflowing_pages, pages_with_free_slots = self.find_overflowing_and_non_full_pages()
        logger.info(
            f"Found {len(overflowing_pages)} overflowing pages and {len(pages_with_free_slots)} pages with free slots.")
        moved_cards = 0
        for page in overflowing_pages:
            # Fill free slots on other pages first
            while (current_page_length := len(page)) > self.total_cards_per_page and pages_with_free_slots:
                page_to_fill = pages_with_free_slots.pop(0)
                moved_cards += self._move_cards(page_to_fill, page, current_page_length - self.total_cards_per_page)
            # After filling all remaining free slots, it may still contain images for multiple new pages,
            # so add new pages until all excess images are moved.
            while (current_page_length := len(page)) > self.total_cards_per_page:
                page_to_fill = self.add_page()
                self._set_currently_edited_page(page_to_fill)
                moved_cards += self._move_cards(page_to_fill, page, current_page_length - self.total_cards_per_page)
                if len(page_to_fill) < self.total_cards_per_page:
                    pages_with_free_slots.append(page_to_fill)
        logger.info(f"Moved {moved_cards} cards away from overflowing pages.")
        return moved_cards

    def _set_currently_edited_page(self, page: CardList):
        self.currently_edited_page = page
        page_position = self.find_page_list_index(page)
        self.current_page_changed.emit(QPersistentModelIndex(self.index(page_position, 0)))

    def find_overflowing_and_non_full_pages(self, total_cards_per_page: int = None):
        """
        Returns two lists of pages: The first contains all pages that are currently overflowing,
        and the second contains that currently have free slots and therefore can fit additional cards.
        """
        total_cards_per_page = total_cards_per_page or self.total_cards_per_page
        overflowing_pages = []
        pages_with_free_slots: PageList = []
        for page_number, page in enumerate(self.pages):
            if len(page) > total_cards_per_page:
                overflowing_pages.append(page)
            elif len(page) < total_cards_per_page:
                pages_with_free_slots.append(page)
        return overflowing_pages, pages_with_free_slots

    @pyqtSlot()
    def clear(self):
        logger.info("Clearing current document")
        self.remove_pages(list(map(
            self.index,
            range(self.rowCount()),
            itertools.repeat(0)
        )))

    @pyqtSlot()  # Avoid connecting both triggered() and triggered(bool)
    def clear_all_data(self):
        self.clear()
        self.page_layout.update_from_settings()
        self.on_page_layout_updated()
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

    def _recreate_page_index_cache(self):
        self.page_index_cache.clear()
        self.page_index_cache.update(
            (id(page), index) for index, page in enumerate(self.pages)
        )


def _migrate_database(db):
    if db.execute("PRAGMA user_version").fetchone()[0] == 2:
        db.executescript(textwrap.dedent("""\
        ALTER TABLE Card RENAME TO Card_old;
        CREATE TABLE Card (
          page INTEGER NOT NULL CHECK (page > 0),
          slot INTEGER NOT NULL CHECK (slot > 0),
          is_front INTEGER NOT NULL CHECK (is_front IN (0, 1)) DEFAULT 1,
          scryfall_id TEXT NOT NULL,
          PRIMARY KEY(page, slot)
        ) WITHOUT ROWID;
        INSERT INTO Card (page, slot, scryfall_id, is_front)
            SELECT page, slot, scryfall_id, 1 AS is_front
            FROM Card_old;
        DROP TABLE Card_old;
        VACUUM;
        """))
        db.execute(f"PRAGMA user_version = 3")
    if db.execute("PRAGMA user_version").fetchone()[0] == 3:
        db.execute(textwrap.dedent("""\
        CREATE TABLE DocumentSettings (
          rowid INTEGER NOT NULL PRIMARY KEY CHECK (rowid == 1),
          page_height INTEGER NOT NULL CHECK (page_height > 0),
          page_width INTEGER NOT NULL CHECK (page_width > 0),
          margin_top INTEGER NOT NULL CHECK (margin_top >= 0),
          margin_bottom INTEGER NOT NULL CHECK (margin_bottom >= 0),
          margin_left INTEGER NOT NULL CHECK (margin_left >= 0),
          margin_right INTEGER NOT NULL CHECK (margin_right >= 0),
          image_spacing_horizontal INTEGER NOT NULL CHECK (image_spacing_horizontal >= 0),
          image_spacing_vertical INTEGER NOT NULL CHECK (image_spacing_vertical >= 0),
          draw_cut_markers INTEGER NOT NULL CHECK (draw_cut_markers in (0, 1))
        );"""))
        db.execute(f"PRAGMA user_version = 4")
