#  Copyright © 2020-2025  Thomas Hess <thomas.hess@udo.edu>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.


from collections import deque, Counter
from collections.abc import Generator, Iterable
import json
import typing
import enum
import itertools
import math
from pathlib import Path
from typing import Any, Literal

from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt, Slot, Signal, \
    QPersistentModelIndex, QMimeData

from mtg_proxy_printer import BlockingQueuedConnection
from mtg_proxy_printer.async_tasks.base import AsyncTask
from mtg_proxy_printer.async_tasks.image_downloader import SingleDownloadTask, SingleActions
from mtg_proxy_printer.document_controller import DocumentAction
from mtg_proxy_printer.document_controller.replace_card import ActionReplaceCard
from mtg_proxy_printer.document_controller.save_document import ActionSaveDocument
from mtg_proxy_printer.document_controller.move_cards import ActionMoveCardsBetweenPages, ActionMoveCardsWithinPage
from mtg_proxy_printer.document_controller.move_page import ActionMovePage
from mtg_proxy_printer.model.imagedb_files import ImageKey
from mtg_proxy_printer.natsort import to_list_of_ranges
from mtg_proxy_printer.document_controller.edit_custom_card import ActionEditCustomCard
from mtg_proxy_printer.model.document_page import CardContainer, Page, PageColumns
from mtg_proxy_printer.units_and_sizes import PageType, CardSizes, CardSize
from mtg_proxy_printer.model.carddb import CardDatabase, CardIdentificationData
from mtg_proxy_printer.model.card import MTGSet, Card, AnyCardType, CustomCard
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.model.imagedb import ImageDatabase
from mtg_proxy_printer.logger import get_logger


logger = get_logger(__name__)
del get_logger

__all__ = [
    "Document",
]


class DocumentColumns(enum.IntEnum):
    Page = 0


INVALID_INDEX = QModelIndex()
ActionStack = deque[DocumentAction]
AnyIndex = QModelIndex | QPersistentModelIndex
ItemDataRole = Qt.ItemDataRole
Orientation = Qt.Orientation
ItemFlag = Qt.ItemFlag
PAGE_MOVE_MIME_TYPE = "application/x-MTGProxyPrinter-PageMove"
CARD_MOVE_MIME_TYPE = "application/x-MTGProxyPrinter-CardMove"
DRAG_OPERATION_TYPE = Literal["application/x-MTGProxyPrinter-PageMove"] | Literal["application/x-MTGProxyPrinter-CardMove"] | None


class DragOperationType(typing.TypedDict):
    type: Literal["application/x-MTGProxyPrinter-PageMove"] | Literal["application/x-MTGProxyPrinter-CardMove"]
    source_size: typing.NotRequired[PageType]  # Size of moved cards. Prevents creation of mixed pages
    source_count: typing.NotRequired[int]  # Number of cards moved. Prevents overflowing pages
    source_page: typing.NotRequired[int]  # The origin page of card moves. Disables count checks for in-page moves


class CardMoveMimeData(typing.TypedDict):
    page: int
    cards: list[int]


class Document(QAbstractItemModel):
    """
    This holds a multi-page document that contains any number of same-size pages.
    The pages hold the individual proxy images
    """
    INVALID_INDEX = INVALID_INDEX

    current_page_changed = Signal(QPersistentModelIndex)
    page_layout_changed = Signal(PageLayoutSettings)
    page_type_changed = Signal(QModelIndex)

    action_applied = Signal(DocumentAction)
    action_undone = Signal(DocumentAction)
    undo_available_changed = Signal(bool)
    redo_available_changed = Signal(bool)
    request_run_async_task = Signal(AsyncTask)

    EDITABLE_COLUMNS = {PageColumns.Set, PageColumns.CollectorNumber, PageColumns.Language}

    def __init__(self, card_db: CardDatabase, image_db: ImageDatabase, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.header = {
            PageColumns.CardName: self.tr("Card name", "Table header"),
            PageColumns.Set: self.tr("Set", "Table header"),
            PageColumns.CollectorNumber: self.tr("Collector #", "Table header"),
            PageColumns.Language: self.tr("Language", "Table header"),
            PageColumns.Image: self.tr("Image", "Table header"),
            PageColumns.IsFront: self.tr("Side", "Table header"),
        }

        self.undo_stack: ActionStack = deque()
        self.redo_stack: ActionStack = deque()
        self.save_file_path: Path | None = None
        self.card_db = card_db
        self.image_db = image_db
        self.pages: list[Page] = [first_page := Page()]
        # Mapping from page id() to list index in the page list
        self.page_index_cache: dict[int, int] = {id(first_page): 0}
        self.currently_edited_page = first_page
        self.page_layout = PageLayoutSettings.create_from_settings()
        # The last started drag operation affects the index flags() related to drag&drop.
        self.current_drag_operation: DragOperationType = {"type": PAGE_MOVE_MIME_TYPE}
        logger.debug(f"Loaded document settings from configuration file: {self.page_layout}")
        logger.info(f"Created {self.__class__.__name__} instance")

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

    @Slot()
    def on_custom_card_corner_style_changed(self):
        logger.info("Custom card corner style toggled. Resetting custom card pixmaps.")
        column = PageColumns.Image
        roles = [ItemDataRole.DisplayRole]
        for page_row, page in enumerate(self.pages):
            page_index = self.index(page_row, DocumentColumns.Page)
            for card_row, container in enumerate(page):
                card = container.card
                if card.is_custom_card:
                    del card.image_file  # Rebuild the pixmap the next time it is accessed.
                    card_index = self.index(card_row, column, page_index)
                    self.dataChanged.emit(card_index, card_index, roles)

    def headerData(
            self, section: int | PageColumns,
            orientation: Orientation, role: ItemDataRole = ItemDataRole.DisplayRole) -> str:
        if orientation == Orientation.Horizontal:
            if role == ItemDataRole.DisplayRole:
                return self.header.get(section)
            elif role == ItemDataRole.ToolTipRole and section in self.EDITABLE_COLUMNS:
                return self.tr("Double-click on entries to\nswitch the selected printing.")
        return super().headerData(section, orientation, role)

    def rowCount(self, parent: AnyIndex = INVALID_INDEX) -> int:
        """
        If parent is valid index, i.e. points to a page, returns the number of cards in that page.
        Otherwise, returns the number of pages.
        """
        parent = self._to_index(parent)
        if isinstance(parent.internalPointer(), CardContainer):
            return 0  # child rowCount of a Card instance. Always zero.
        if parent.isValid():
            return len(parent.internalPointer())  # child rowCount of a page. Number of cards in that page
        else:
            return len(self.pages)  # rowCount of an invalid index. Number of pages in the document.

    def columnCount(self, parent: AnyIndex = INVALID_INDEX) -> int:
        parent = self._to_index(parent)
        if isinstance(parent.internalPointer(), CardContainer):
            return 0  # child columnCount of a Card instance. Always zero.
        elif parent.isValid():
            return len(PageColumns)  # child columnCount of a page. Number of shown Card fields
        else:
            return len(DocumentColumns)  # columnCount of an invalid index.

    def parent(self, child: AnyIndex) -> QModelIndex:
        data: Page | CardContainer = self._to_index(child).internalPointer()
        if isinstance(data, CardContainer):
            page = data.parent
            page_index = self.find_page_list_index(page)
            return self.createIndex(page_index, 0, page)
        return INVALID_INDEX  # Pages have no parent

    def index(self, row: int, column: int, parent: AnyIndex = INVALID_INDEX) -> QModelIndex:
        data: Page | None = self._to_index(parent).internalPointer()
        if isinstance(data, Page):
            card_container = data[row]
            return self.createIndex(row, column, card_container)
        else:
            if row == len(self.pages):
                # Dropping data onto the last
                return INVALID_INDEX
            page = self.pages[row]
            return self.createIndex(row, column, page)

    def data(self, index: AnyIndex, role: ItemDataRole = ItemDataRole.DisplayRole) -> Any:
        index = self._to_index(index)
        if not index.isValid():
            return None
        if isinstance(index.internalPointer(), CardContainer):  # Card
            return self._data_card(index, role)
        else:  # Page
            return self._data_page(index, role)

    def flags(self, index: AnyIndex) -> Qt.ItemFlag:
        index = self._to_index(index)
        data = index.internalPointer()
        flags = super().flags(index)
        if isinstance(data, CardContainer) and (index.column() in self.EDITABLE_COLUMNS or data.card.is_custom_card):
            flags |= ItemFlag.ItemIsEditable
        if isinstance(data, Page|CardContainer):
            flags |= ItemFlag.ItemIsDragEnabled  # Pages and cards can be moved
        if (not index.isValid()  # Top level can accept any drop, both pages and cards, where the latter gets a new page
            or (
                isinstance(data, Page)  # Dropped onto a page.
                and self.current_drag_operation["type"] == CARD_MOVE_MIME_TYPE  # Pages only accept cards …
                and data.accepts_card(self.current_drag_operation["source_size"])  # that have an acceptable size, …
                and (len(data) + self.current_drag_operation["source_count"] # and if they can fit the dropped cards
                    <= self.page_layout.compute_page_card_capacity(self.current_drag_operation["source_size"])
                    or self.current_drag_operation["source_page"] == index.row()
                )
                )):
            flags |= ItemFlag.ItemIsDropEnabled
        return flags

    def setData(self, index: AnyIndex, value: Any, role: ItemDataRole = ItemDataRole.EditRole) -> bool:
        index = self._to_index(index)
        data: CardContainer = index.internalPointer()
        if not isinstance(data, CardContainer) or role != ItemDataRole.EditRole:
            return False
        column = index.column()
        card = data.card
        if card.is_custom_card:
            self.apply(ActionEditCustomCard(index, value))
            return True
        elif column in self.EDITABLE_COLUMNS:
            logger.debug(f"Setting page data on official card for {column=} to {value}")
            if column == PageColumns.CollectorNumber:
                card_data = CardIdentificationData(
                    card.language, card.name, card.set.code, value, is_front=card.is_front)
            elif column == PageColumns.Set:
                card_data = CardIdentificationData(
                    card.language, card.name, value.code, is_front=card.is_front
                )
            else:
                replacement = self.card_db.translate_card(card, value)
                if replacement != card:
                    action = ActionReplaceCard(replacement, index.parent().row(), index.row())
                    self._fetch_image_and_apply_action(action)
                    return True
                return False
            return self._request_replacement_card(index, card_data)
        return False

    def _fetch_image_and_apply_action(self, action: SingleActions):
        self.request_run_async_task.emit(SingleDownloadTask(self.image_db, action))

    def mimeData(self, indexes: list[QModelIndex], /) -> QMimeData:
        """
        Reads model data and converts them into QMimeData used for Drag&Drop.
        Dragging a page encodes its initial position
        Dragging cards encodes their shared page index, and a list of card indices.
        """
        mime_data = QMimeData()
        if not indexes:
            return mime_data

        if not (first := indexes[0]).parent().isValid():
            row = first.row()
            logger.debug(f"Initiating drag for page {row}")
            mime_data.setData(PAGE_MOVE_MIME_TYPE, row.to_bytes(8))
            self.current_drag_operation = DragOperationType(type=PAGE_MOVE_MIME_TYPE)
            return mime_data
        page = first.parent().row()
        cards = sorted(set(index.row() for index in indexes))
        logger.debug(f"Initiating drag for {len(cards)} cards on page {page}")
        data: CardMoveMimeData = {"page": page, "cards": cards}
        encoded_data = json.dumps(data).encode("utf-8")
        mime_data.setData(CARD_MOVE_MIME_TYPE, encoded_data)
        self.current_drag_operation = DragOperationType(
            type=CARD_MOVE_MIME_TYPE, source_count=len(cards), source_size=self.pages[page].page_type(),
            source_page=page)
        return mime_data

    def dropMimeData(
            self, data: QMimeData, action: Qt.DropAction,
            row: int, column: PageColumns | DocumentColumns, parent: QModelIndex, /):
        """Supports dropping cards or pages moved via drag&drop."""

        # https://doc.qt.io/qt-6/qabstractitemmodel.html#dropMimeData:
        # "When row and column are -1 it means that the dropped data should be considered as
        # dropped directly on parent. Usually this will mean appending the data as child items of parent.
        # If row and column are greater than or equal zero, it means that the drop occurred just
        # before the specified row and column in the specified parent."
        if data.hasFormat(PAGE_MOVE_MIME_TYPE):
            # Here, parent is always invalid. row == column == -1 means the drop ended on empty space within the view.
            # The only location with empty space is below the last page, so treat it as if the user dropped directly
            # below the last page, and move the page to the end.
            # If row != -1, row states the drop location, so use that.
            logger.debug(f"Received page drop onto {row=}")
            if row == -1:
                row = self.rowCount()
            source_row = int.from_bytes(data.data(PAGE_MOVE_MIME_TYPE).data())
            self.apply(ActionMovePage(source_row, row))
        elif data.hasFormat(CARD_MOVE_MIME_TYPE):
            # Here, parent may be valid, and there are two main cases, one of which has 2 subcases:
            card_data: CardMoveMimeData = json.loads(data.data(CARD_MOVE_MIME_TYPE).data())
            logger.debug(f"Received card drop onto {row=}: {card_data}")
            # Case 1:  Cards are dropped onto an existing page, given by parent.row().
            if parent.isValid():
                if row == column == -1:
                    # The drop ended on empty space within the page card table view.
                    # Append the cards at the end of the given page
                    row = self.rowCount(parent)
                if parent.row() == card_data["page"]:
                    action = ActionMoveCardsWithinPage(parent.row(), card_data["cards"], row)
                else:
                    action = ActionMoveCardsBetweenPages(card_data["page"], card_data["cards"], parent.row(), None)
            else:
                # Case 2: Cards are dropped between pages, and a new page must be inserted for the dropped cards
                if row == column == -1:
                    # Subcase 1: The drop ended on empty space within the view. Append a new page.
                    row = self.rowCount()
                # Subcase 2: Cards are moved to row on the page given by parent
                action = ActionMoveCardsBetweenPages(card_data["page"], card_data["cards"], row, -1)
            self.apply(action)

        return False  # Move complete, so signal via False that the caller does not have to remove the source rows

    def supportedDropActions(self, /) -> Qt.DropAction:
        return Qt.DropAction.MoveAction

    def mimeTypes(self, /) -> list[str]:
        """Supported mime types."""
        return [PAGE_MOVE_MIME_TYPE, CARD_MOVE_MIME_TYPE]

    @staticmethod
    def _to_index(other: QPersistentModelIndex | QModelIndex) -> QModelIndex:
        return QModelIndex(other) if isinstance(other, QPersistentModelIndex) else other

    def _request_replacement_card(self, index: QModelIndex, card_data: CardIdentificationData):
        if result := self.card_db.get_cards_from_data(card_data):
            logger.debug(f"Requesting replacement for card '{card_data.name}' in set {card_data.set_code}")
            # Simply choose the first match. The user can’t make a choice at this point, so just use one of
            # the results.
            new_card = result[0]
            action = ActionReplaceCard(new_card, index.parent().row(), index.row())
            self._fetch_image_and_apply_action(action)
            return True
        return False

    def _data_page(self, index: QModelIndex, role: ItemDataRole = ItemDataRole.DisplayRole) -> Any:
        """Returns the requested data for an index pointing to a page of Cards."""
        row = index.row()
        if row >= self.rowCount():
            logger.error(f"Invalid index: {row=}, {index.column()=}, {self.rowCount()=}, {index.isValid()=}")
            return None
        item = self.pages[row]
        if role == ItemDataRole.DisplayRole:
            return self._get_page_preview(item)
        elif role == ItemDataRole.ToolTipRole:
            return self.tr(
                "Page {current}/{total}", "Tooltip. Shown when hovering over a page in the page list"
            ).format(current=row + 1, total=self.rowCount())
        elif role == ItemDataRole.EditRole:
            return item
        elif role == ItemDataRole.UserRole:
            return item.page_type()
        return None

    def _data_card(self, index: QModelIndex, role: ItemDataRole = ItemDataRole.DisplayRole) -> Any:
        """Returns the requested data for an index pointing to a single Card."""
        parent = index.parent()
        column = index.column()
        if index.row() >= self.rowCount(parent) or column >= self.columnCount(parent):
            logger.error(
                f"Invalid index: {index.row()=}, { column=}, "
                f"{self.rowCount(parent)=}, {index.isValid()=}")
            return None
        card: AnyCardType = index.internalPointer().card
        if role == ItemDataRole.UserRole:
            return card
        if role in {ItemDataRole.DisplayRole, ItemDataRole.EditRole}:
            if column == PageColumns.CardName:
                return card.name
            elif column == PageColumns.Set:
                return card.set.data(role)
            elif column == PageColumns.CollectorNumber:
                return card.collector_number
            elif column == PageColumns.Language:
                return card.language
            elif column == PageColumns.Image:
                return card.image_file
            elif column == PageColumns.IsFront:
                return card.is_front if role == ItemDataRole.EditRole else (
                    self.tr("Front", "Magic card side") if card.is_front else self.tr("Back", "Magic card side"))
        return None

    def _get_page_preview(self, page: Page):
        names = Counter(container.card.name for container in page)
        return "\n".join(self.tr(
            "%n× {name}",
            "Used to display a card name and amount of copies in the page overview. "
            "Only needs translation for RTL language support", count).format(name=name) for name, count in names.items()
        )

    @Slot(QModelIndex)
    def on_missing_image_obtained(self, index: QModelIndex):
        column_index = index.siblingAtColumn(PageColumns.Image)
        self.dataChanged.emit(column_index, column_index, [ItemDataRole.DisplayRole])

    def save_as(self, path: Path):
        """Save the document at the given path, overwriting any previously stored save path."""
        self.save_file_path = path
        ActionSaveDocument(path).apply(self)  # Note: Not using the action stack. Saving cannot be undone

    def save_to_disk(self):
        """Save the document at the internally remembered save path. Raises a RuntimeError, if no such path is set."""
        if self.save_file_path is None:
            raise RuntimeError("Cannot save without a file path!")
        ActionSaveDocument(self.save_file_path).apply(self)  # Note: Not using the action stack. Saving cannot be undone

    def compute_pages_saved_by_compacting(self) -> int:
        """
        Computes the number of pages that can be saved by compacting the document.
        """
        cards: Counter[PageType] = Counter()
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

    def get_empty_card_for_current_page(self) -> Card:
        size = CardSizes.for_page_type(self.currently_edited_page.page_type())
        return self.get_empty_card_for_size(size)

    def get_empty_card_for_size(self, size: CardSize) -> Card:
        pixmap = self.image_db.get_blank(size)
        name = self.tr(
            "Empty Placeholder",
            "Card name of the blank placeholder that can be added to keep slots on a page free.")
        card = Card(name, MTGSet("", ""), "", "", "", True, "", "", True, size, 0, False, pixmap)
        return card

    def get_card_indices_of_type(self, page_type: PageType):
        for page_number, page in enumerate(self.pages):
            if page.page_type() is not page_type:
                continue
            page_index = self.index(page_number, 0)
            for card_number in range(len(page)):
                yield self.index(card_number, 0, page_index)

    def has_missing_images(self) -> bool:
        try:
            next(self.get_missing_image_cards())
        except StopIteration:
            return False
        else:
            return True

    def missing_image_count(self) -> int:
        return sum(1 for _ in self.get_missing_image_cards())

    def get_missing_image_cards(self) -> Generator[QModelIndex, None, None]:
        """Returns an iterable with indices to all cards that have missing images"""
        blanks = {self.image_db.get_blank(CardSizes.REGULAR), self.image_db.get_blank(CardSizes.OVERSIZED)}
        for page_number, page in enumerate(self.pages):
            page_index = self.index(page_number, 0)
            for card_number, container in enumerate(page):
                card = container.card
                # Skip explicitly added empty placeholders, which have an empty image_uri
                if card.image_file in blanks and card.image_uri:
                    yield self.index(card_number, 0, page_index)

    def _get_page_content_as_image_keys(self, page: Page) -> Iterable[ImageKey]:
        image_db = self.image_db
        return (
            ImageKey(card.scryfall_id, card.is_front, card.highres_image)
            for container in page
            if not (card := container.card).is_custom_card
               and card.image_file is not image_db.get_blank(card.size))

    def get_all_image_keys_in_document(self) -> set[ImageKey]:
        return set(itertools.chain.from_iterable(
            map(self._get_page_content_as_image_keys, self.pages)
        ))

    def get_all_custom_cards(self) -> set[CustomCard]:
        result = set()
        for page in self.pages:
            for container in page:
                if isinstance(container.card, CustomCard):
                    result.add(container.card)
        return result

    def recreate_page_index_cache(self):
        self.page_index_cache.clear()
        self.page_index_cache.update(
            (id(page), index) for index, page in enumerate(self.pages)
        )

    def find_relevant_index_ranges(self, to_find: AnyCardType, column: PageColumns):
        """Finds all indices relevant for the given card."""
        # TODO: This runs in O(n)
        for page_row, page in enumerate(self.pages):
            instance_rows = to_list_of_ranges(
                # Use is to find exact same instances
                (row for row, container in enumerate(page) if container.card is to_find)
            )
            if instance_rows:
                parent = self.index(page_row, 0)
                if column == PageColumns.CardName:
                    yield parent, parent
                for lower, upper in instance_rows:
                    yield self.index(lower, column, parent), self.index(upper, column, parent)
