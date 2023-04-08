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

import collections
import dataclasses
import enum
import itertools
import math
import pathlib
import textwrap
import typing

from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt, pyqtSlot as Slot, pyqtSignal as Signal,\
    QPersistentModelIndex

import mtg_proxy_printer.sqlite_helpers
from mtg_proxy_printer.model.document_page import CardContainer, Page, PageList
from mtg_proxy_printer.units_and_sizes import PageType
from mtg_proxy_printer.model.carddb import Card, CardDatabase, CardIdentificationData
from mtg_proxy_printer.model.card_list import PageColumns
from mtg_proxy_printer.model.document_loader import DocumentLoader, DocumentSaveFormat, PageLayoutSettings
from mtg_proxy_printer.model.imagedb import ImageDatabase
from mtg_proxy_printer.logger import get_logger

from mtg_proxy_printer.document_controller import DocumentAction
from mtg_proxy_printer.document_controller.replace_card import ActionReplaceCard

logger = get_logger(__name__)
del get_logger

__all__ = [
    "Document",
]


class DocumentColumns(enum.IntEnum):
    Page = 0


INVALID_INDEX = QModelIndex()
ActionStack = typing.Deque[DocumentAction]


class Document(QAbstractItemModel):
    """
    This holds a multi-page document that contains any number of same-size pages.
    The pages hold the individual proxy images
    """
    INVALID_INDEX = INVALID_INDEX

    loading_state_changed = Signal(bool)
    current_page_changed = Signal(QPersistentModelIndex)
    page_layout_changed = Signal(PageLayoutSettings)
    page_type_changed = Signal(QModelIndex)

    action_applied = Signal(DocumentAction)
    action_undone = Signal(DocumentAction)
    undo_available_changed = Signal(bool)
    redo_available_changed = Signal(bool)
    request_fill_image_for_action = Signal(DocumentAction)

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
        self.undo_stack: ActionStack = collections.deque()
        self.redo_stack: ActionStack = collections.deque()
        self.save_file_path: typing.Optional[pathlib.Path] = None
        self.card_db = card_db
        self.image_db = image_db
        self.loader = DocumentLoader(card_db, image_db, self)
        self.loader.loading_state_changed.connect(self.loading_state_changed)
        self.loader.load_requested.connect(self.apply)
        self.pages: PageList = [first_page := Page()]
        # Mapping from page id() to list index in the page list
        self.page_index_cache: typing.Dict[int, int] = {id(first_page): 0}
        self.currently_edited_page = first_page
        self.page_layout = PageLayoutSettings.create_from_settings()

    @Slot(DocumentAction)
    def apply(self, action: DocumentAction):
        if self.redo_stack:
            # Do not discard the rest redo stack if the top is equal to the given action
            if self.redo_stack.pop() != action:
                self.redo_stack.clear()
            if not self.redo_stack:
                self.redo_available_changed.emit(False)
        emit_undo_available_signal = not self.undo_stack
        logger.info(f"Applying {action.__class__.__name__}")
        self.undo_stack.append(action.apply(self))
        logger.debug("Action applied")
        if emit_undo_available_signal:
            self.undo_available_changed.emit(True)
        self.action_applied.emit(action)

    @Slot()
    def undo(self):
        """Undo the last action on the undo stack and push it onto the redo stack."""
        emit_redo_available_signal = not self.redo_stack
        action = self.undo_stack.pop()
        logger.info(f"Undo {action.__class__.__name__}")
        self.redo_stack.append(action.undo(self))
        logger.debug("Action undone")
        self.action_undone.emit(action)
        if not self.undo_stack:
            self.undo_available_changed.emit(False)
        if emit_redo_available_signal:
            self.redo_available_changed.emit(True)

    @Slot()
    def redo(self):
        """Apply the last action on the redo stack and push it onto the undo stack."""
        emit_undo_available_signal = not self.undo_stack
        action = self.redo_stack.pop()
        logger.info(f"Redo {action.__class__.__name__}")
        self.undo_stack.append(action.apply(self))
        logger.debug("Action redone")
        self.action_applied.emit(action)
        if not self.redo_stack:
            self.redo_available_changed.emit(False)
        if emit_undo_available_signal:
            self.undo_available_changed.emit(True)

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
        data: typing.Union[Page, CardContainer] = child.internalPointer()
        if isinstance(data, CardContainer):
            page = data.parent
            page_index = self.find_page_list_index(page)
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
            self.request_fill_image_for_action.emit(ActionReplaceCard(new_card, index.parent().row(), index.row()))
            return True
        return False

    def _data_page(self, index: QModelIndex, role: int = Qt.DisplayRole) -> typing.Any:
        """Returns the requested data for an index pointing to a page of Cards."""
        if index.row() >= self.rowCount():
            logger.error(f"Invalid index: {index.row()=}, {index.column()=}, {self.rowCount()=}, {index.isValid()=}")
            return None
        item = self.pages[index.row()]
        if role == Qt.DisplayRole:
            return self._get_page_preview(item)
        elif role == Qt.ToolTipRole:
            return f"Page {index.row()+1}/{self.rowCount()}"
        elif role == Qt.EditRole:
            return item
        elif role == Qt.UserRole:
            return item.page_type()

    def _data_card(self, index: QModelIndex, role: int = Qt.DisplayRole) -> typing.Any:
        """Returns the requested data for an index pointing to a single Card."""
        parent = index.parent()
        if index.row() >= self.rowCount(parent) or index.column() >= self.columnCount(parent):
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
    def _get_page_preview(page: Page):
        names = collections.Counter(container.card.name for container in page)
        return "\n".join(
            f"{count}× {name}" for name, count in names.items()
        )

    @Slot(QModelIndex)
    def on_missing_image_obtained(self, index: QModelIndex):
        column_index = index.siblingAtColumn(PageColumns.Image)
        self.dataChanged.emit(column_index, column_index, [Qt.DisplayRole])

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
                self.save_file_path, "document-v5", self.loader.MIN_SUPPORTED_SQLITE_VERSION) as db:
            db.execute("BEGIN TRANSACTION")
            _migrate_database(db)
            db.execute("DELETE FROM Card")
            db.executemany(
                "INSERT INTO Card (page, slot, scryfall_id, is_front) VALUES (?, ?, ?, ?)",
                flattened_data
            )
            logger.debug(f"Written {db.execute('SELECT count() FROM Card').fetchone()[0]} cards.")
            db.execute(
                textwrap.dedent("""\
                    INSERT OR REPLACE INTO DocumentSettings (rowid, page_height, page_width,
                          margin_top, margin_bottom, margin_left, margin_right,
                          image_spacing_horizontal, image_spacing_vertical, draw_cut_markers, draw_sharp_corners)
                      VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """),
                dataclasses.astuple(self.page_layout))
            logger.debug("Written document settings")
            db.commit()
            db.execute("VACUUM")
        logger.debug("Database saved and closed.")

    def compute_pages_saved_by_compacting(self) -> int:
        """
        Computes the number of pages that can be saved by compacting the document.
        """
        cards = collections.Counter()
        for page in self.pages:
            cards[page.page_type()] += len(page)
        required_pages = (
            math.ceil(cards[PageType.OVERSIZED] / self.page_layout.compute_page_card_capacity(PageType.OVERSIZED))
            + math.ceil(cards[PageType.REGULAR] / self.page_layout.compute_page_card_capacity(PageType.REGULAR))
        ) or 1
        result = self.rowCount() - required_pages
        return result

    def find_page_list_index(self, other: Page):
        """Finds the 0-indexed location of the given Page in the pages list"""
        try:
            return self.page_index_cache[id(other)]
        except KeyError as k:
            raise ValueError("List not found in the page list.") from k

    def set_currently_edited_page(self, page: Page):
        self.currently_edited_page = page
        self.current_page_changed.emit(self.get_current_page_index())

    def get_current_page_index(self) -> QPersistentModelIndex:
        position = self.find_page_list_index(self.currently_edited_page)
        return QPersistentModelIndex(self.index(position, 0))

    def get_card_indices_of_type(self, page_type: PageType):
        for page_number, page in enumerate(self.pages):
            if page.page_type() is not page_type:
                continue
            page_index = self.index(page_number, 0)
            for card_number in range(len(page)):
                yield self.index(card_number, 0, page_index)

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

    def has_missing_images(self) -> bool:
        try:
            next(self.get_missing_image_cards())
        except StopIteration:
            return False
        else:
            return True

    def missing_image_count(self) -> int:
        return sum(1 for _ in self.get_missing_image_cards())

    def get_missing_image_cards(self) -> typing.Generator[QModelIndex, None, None]:
        """Returns an iterable with indices to all cards that have missing images"""
        blank = self.image_db.blank_image
        for page_number, page in enumerate(self.pages):
            page_index = self.index(page_number, 0)
            for card_number, container in enumerate(page):
                if container.card.image_file is blank:
                    yield self.index(card_number, 0, page_index)

    @staticmethod
    def _get_page_content_as_scryfall_ids(page: Page) -> typing.Iterable[typing.Tuple[str, bool]]:
        return ((container.card.scryfall_id, container.card.is_front) for container in page)

    def recreate_page_index_cache(self):
        self.page_index_cache.clear()
        self.page_index_cache.update(
            (id(page), index) for index, page in enumerate(self.pages)
        )


def _migrate_database(db):
    if db.execute("PRAGMA user_version\n").fetchone()[0] == 2:
        for statement in [
            "ALTER TABLE Card RENAME TO Card_old",
            textwrap.dedent("""\
            CREATE TABLE Card (
              page INTEGER NOT NULL CHECK (page > 0),
              slot INTEGER NOT NULL CHECK (slot > 0),
              is_front INTEGER NOT NULL CHECK (is_front IN (0, 1)) DEFAULT 1,
              scryfall_id TEXT NOT NULL,
              PRIMARY KEY(page, slot)
            ) WITHOUT ROWID"""),
            textwrap.dedent("""\
            INSERT INTO Card (page, slot, scryfall_id, is_front)
                SELECT page, slot, scryfall_id, 1 AS is_front
                FROM Card_old"""),
            "DROP TABLE Card_old",
            "PRAGMA user_version = 3",
        ]:
            db.execute(f"{statement};\n")
    if db.execute("PRAGMA user_version\n").fetchone()[0] == 3:
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
    if db.execute("PRAGMA user_version").fetchone()[0] == 4:
        for statement in [
            "ALTER TABLE DocumentSettings RENAME TO DocumentSettings_Old",
            textwrap.dedent("""\
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
              draw_cut_markers INTEGER NOT NULL CHECK (draw_cut_markers in (TRUE, FALSE)),
              draw_sharp_corners INTEGER NOT NULL CHECK (draw_sharp_corners in (TRUE, FALSE))
            )"""),
            "INSERT INTO DocumentSettings SELECT *, FALSE FROM DocumentSettings_Old",
            "DROP TABLE DocumentSettings_Old",
            "PRAGMA user_version = 5",
        ]:
            db.execute(f"{statement}\n")
