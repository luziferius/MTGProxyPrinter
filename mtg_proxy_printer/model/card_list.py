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

from collections import Counter
import dataclasses
import enum
import itertools
import typing

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, pyqtSignal as Signal, QItemSelection
from PyQt5.QtGui import QIcon

from mtg_proxy_printer.document_controller import DocumentAction
from mtg_proxy_printer.document_controller.edit_custom_card import ActionEditCustomCard
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.document_page import PageColumns
from mtg_proxy_printer.ui.common import get_card_image_tooltip
from mtg_proxy_printer.decklist_parser.common import CardCounter
from mtg_proxy_printer.model.carddb import CardIdentificationData
from mtg_proxy_printer.model.card import AnyCardType
from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger
ItemDataRole = Qt.ItemDataRole
ItemFlag = Qt.ItemFlag

__all__ = [
    "CardListColumns",
    "CardListModel",
]
INVALID_INDEX = QModelIndex()


@dataclasses.dataclass
class CardListModelRow:
    card: AnyCardType
    copies: int


class CardListColumns(enum.IntEnum):
    Copies = 0
    CardName = enum.auto()
    Set = enum.auto()
    CollectorNumber = enum.auto()
    Language = enum.auto()
    IsFront = enum.auto()

    def to_page_column(self):
        return CardListToPageColumnMapping[self]


CardList = typing.List[CardListModelRow]
CardListToPageColumnMapping = {
    CardListColumns.CardName: PageColumns.CardName,
    CardListColumns.Set: PageColumns.Set,
    CardListColumns.CollectorNumber: PageColumns.CollectorNumber,
    CardListColumns.Language: PageColumns.Language,
    CardListColumns.IsFront: PageColumns.IsFront,
}


class CardListModel(QAbstractTableModel):
    """
    This is a model for holding a list of cards.
    """
    EDITABLE_COLUMNS = {
        CardListColumns.Copies, CardListColumns.Set, CardListColumns.CollectorNumber, CardListColumns.Language,
    }
    oversized_card_count_changed = Signal(int)
    request_action = Signal(DocumentAction)

    def __init__(self, document: Document, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.header = {
            CardListColumns.Copies: self.tr("Copies"),
            CardListColumns.CardName: self.tr("Card name"),
            CardListColumns.Set: self.tr("Set"),
            CardListColumns.CollectorNumber: self.tr("Collector #"),
            CardListColumns.Language: self.tr("Language"),
            CardListColumns.IsFront: self.tr("Side"),
        }
        self.document = document
        self.card_db = document.card_db
        self.rows: CardList = []
        self.oversized_card_count = 0
        self._oversized_icon = QIcon.fromTheme("data-warning")

    def rowCount(self, parent: QModelIndex = INVALID_INDEX) -> int:
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent: QModelIndex = INVALID_INDEX) -> int:
        return 0 if parent.isValid() else len(self.header)

    def data(self, index: QModelIndex, role: ItemDataRole = ItemDataRole.DisplayRole) -> typing.Any:
        row, column = index.row(), index.column()
        card = self.rows[row].card
        if role == ItemDataRole.UserRole:
            return card
        if role in (ItemDataRole.DisplayRole, ItemDataRole.EditRole):
            if column == CardListColumns.Copies:
                return self.rows[row].copies
            elif column == CardListColumns.CardName:
                return card.name
            elif column == CardListColumns.Set:
                if role == ItemDataRole.EditRole:
                    return card.set
                else:
                    set_ = card.set
                    return f"{set_.name} ({set_.code.upper()})"
            elif column == CardListColumns.CollectorNumber:
                return card.collector_number
            elif column == CardListColumns.Language:
                return card.language
            elif column == CardListColumns.IsFront:
                if role == ItemDataRole.EditRole:
                    return card.is_front
                return self.tr("Front") if card.is_front else self.tr("Back")
        if card.is_custom_card and column == CardListColumns.CardName and role == ItemDataRole.ToolTipRole:
            return get_card_image_tooltip(card.source_image_file)
        elif card.is_oversized and role == ItemDataRole.ToolTipRole:
            return self.tr("Beware: Potentially oversized card!\nThis card may not fit in your deck.")
        if card.is_oversized and role == ItemDataRole.DecorationRole:
            return self._oversized_icon
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        flags = super().flags(index)
        if index.column() in self.EDITABLE_COLUMNS or self.rows[index.row()].card.is_custom_card:
            flags |= ItemFlag.ItemIsEditable
        return flags

    def setData(self, index: QModelIndex, value: typing.Any, role: ItemDataRole = ItemDataRole.EditRole) -> bool:
        row, column = index.row(), index.column()
        container = self.rows[row]
        card = container.card
        if not card.is_custom_card and role == ItemDataRole.EditRole and column in self.EDITABLE_COLUMNS:
            return self._set_data_for_official_card(index, value)
        elif card.is_custom_card and role == ItemDataRole.EditRole:
            return self._set_data_for_custom_card(index, value)
        return False

    def _set_data_for_official_card(self, index: QModelIndex, value: typing.Any) -> bool:
        row, column = index.row(), index.column()
        container = self.rows[row]
        card = container.card
        logger.debug(f"Setting card list model data on official card for column {column} to {value}")
        if column == CardListColumns.Copies:
            return self._set_copies_value(container, card, value)
        elif column == CardListColumns.CollectorNumber:
            card_data = CardIdentificationData(
                card.language, card.name, card.set_code, value, is_front=card.is_front)
        elif column == CardListColumns.Set:
            card_data = CardIdentificationData(
                card.language, card.name, value.code, is_front=card.is_front
            )
        else:
            card_data = self.card_db.translate_card(card, value)
            if card_data == card:
                return False
        return self._request_replacement_card(index, card_data)

    def _set_data_for_custom_card(self, index: QModelIndex, value: typing.Any) -> bool:
        row, column = index.row(), CardListColumns(index.column())
        container = self.rows[row]
        card = container.card
        logger.debug(f"Setting card list model data on custom card for column {column} to {value}")
        action = None
        if document_indices := list(self.document.find_relevant_index_ranges(card, column.to_page_column())):
            # Create the action before updating the card to gather the old data for undo purposes
            # Take the first index found as the reference
            document_card_index = i if (i := document_indices[0][0]).parent().isValid() else document_indices[1][0]
            action = ActionEditCustomCard(document_card_index, value)

        if column == CardListColumns.Copies:
            return self._set_copies_value(container, card, value)
        if column == CardListColumns.CardName:
            card.name = value
        elif column == CardListColumns.CollectorNumber:
            card.collector_number = value
        elif column == CardListColumns.Language:
            card.language = value
        elif column == CardListColumns.IsFront:
            card.is_front = value
            card.face_number = int(not value)
        elif column == CardListColumns.Set:
            card.set = value
        if card_indices := list(self.document.find_relevant_index_ranges(card, column.to_page_column())):
            logger.info(
                f"Edited custom card present in {len(card_indices)} locations in the document."
                f"Applying the change to the current document.")
        if action is not None:
            self.request_action.emit(action)
        return True

    def _set_copies_value(self, container: CardListModelRow, card: AnyCardType, value: int) -> bool:
        old_value, container.copies = container.copies, value
        if card.is_oversized and (difference := value - old_value):
            self.oversized_card_count += difference
            self.oversized_card_count_changed.emit(self.oversized_card_count)
        return value != old_value

    def _request_replacement_card(
            self, index: QModelIndex, card_data: typing.Union[CardIdentificationData, AnyCardType]):
        row, column = index.row(), index.column()
        if isinstance(card_data, CardIdentificationData):
            logger.debug(f"Requesting replacement for {card_data}")
            result = self.card_db.get_cards_from_data(card_data)
        else:
            result = [card_data]
        if result:
            # Simply choose the first match. The user can’t make a choice at this point, so just use one of the results.
            new_card = result[0]
            logger.debug(f"Replacing with {new_card}")
            top_left = index.sibling(row, column)
            bottom_right = top_left.siblingAtColumn(len(CardListColumns)-1)
            old_row = self.rows[row]
            self.rows[row] = new_row = CardListModelRow(new_card, old_row.copies)
            self.dataChanged.emit(
                top_left, bottom_right,
                (ItemDataRole.DisplayRole, ItemDataRole.EditRole, ItemDataRole.ToolTipRole)
            )
            # Oversized card count changes, iff the flags differ
            if old_row.card.is_oversized and not new_card.is_oversized:
                self._remove_card_handle_oversized_flag(old_row)
            elif new_card.is_oversized and not old_row.card.is_oversized:
                self._add_card_handle_oversized_flag(new_row)
            return True
        logger.debug(f"No replacement card found for {card_data}.")
        return False

    def add_cards(self, cards: CardCounter):
        for card, count in cards.items():
            count = min(100, max(1, count))
            first_index = last_index = self.rowCount()
            self.beginInsertRows(INVALID_INDEX, first_index, last_index)
            self.rows.append(row := CardListModelRow(card, count))
            self.endInsertRows()
            self._add_card_handle_oversized_flag(row)

    def _add_card_handle_oversized_flag(self, row: CardListModelRow):
        if row.card.is_oversized:
            self.oversized_card_count += row.copies
            self.oversized_card_count_changed.emit(self.oversized_card_count)

    def _remove_card_handle_oversized_flag(self, row: CardListModelRow):
        if row.card.is_oversized:
            self.oversized_card_count -= row.copies
            self.oversized_card_count_changed.emit(self.oversized_card_count)

    def remove_multi_selection(self, indices: QItemSelection) -> int:
        """
        Remove all cards in the given multi-selection.
        :return: Number of cards removed
        """
        selected_ranges = sorted(
            (selected_range.top(), selected_range.bottom()) for selected_range in indices
        )
        # This both minimizes the number of model changes needed and de-duplicates the data received from the
        # selection model. If the user selects a row, the UI returns a range for each cell selected, creating many
        # duplicates that have to be removed.
        selected_ranges = self._merge_ranges(selected_ranges)
        # Start removing from the end to avoid shifting later array indices during the removal.
        selected_ranges.reverse()
        logger.info(f"About to remove selections {selected_ranges}")
        result = sum(
            itertools.starmap(self.remove_cards, selected_ranges)
        )
        logger.info(f"Removed {result} cards")
        return result

    @staticmethod
    def _merge_ranges(ranges: typing.List[typing.Tuple[int, int]]) -> typing.List[typing.Tuple[int, int]]:
        result = []
        if len(ranges) < 2:
            return ranges
        bottom, top = ranges[0]
        next_bottom, next_top = ranges[0]
        for next_bottom, next_top in ranges[1:]:
            # Add one to top to also merge adjacent ranges. E.g. (0, 1) + (2, 3) → (0, 3)
            if next_bottom <= top + 1:
                top = next_top
            else:
                result.append((bottom, top))
                bottom, top = next_bottom, next_top
        result.append((bottom, next_top))
        return result

    def remove_cards(self, top: int, bottom: int) -> int:
        """
        Remove all cards in between top and bottom row, including.
        :return: Number of cards removed
        """
        logger.debug(f"Removing range {top, bottom}")
        self.beginRemoveRows(INVALID_INDEX, top, bottom)
        last_row = bottom + 1
        removed_rows = self.rows[top:last_row]
        total_count = sum(row.copies for row in removed_rows)
        del self.rows[top:last_row]
        self.endRemoveRows()
        for row in removed_rows:
            self._remove_card_handle_oversized_flag(row)
        return total_count

    def headerData(
            self, section: typing.Union[int, CardListColumns],
            orientation: Qt.Orientation, role: ItemDataRole = ItemDataRole.DisplayRole) -> str:
        if orientation == Qt.Orientation.Horizontal:
            if role == ItemDataRole.DisplayRole:
                return self.header.get(section)
            elif role == ItemDataRole.ToolTipRole and section in self.EDITABLE_COLUMNS:
                return self.tr("Double-click on entries to\nswitch the selected printing.")
        return super().headerData(section, orientation, role)

    def clear(self):
        count = self.rowCount()
        logger.debug(f"About to clear {self.__class__.__name__} instance. Removing {count} entries.")
        self.beginRemoveRows(INVALID_INDEX, 0, count-1)
        self.rows.clear()
        self.endRemoveRows()
        if self.oversized_card_count:
            self.oversized_card_count = 0
            self.oversized_card_count_changed.emit(self.oversized_card_count)

    def as_cards(self, row_order: typing.List[int] = None) -> CardCounter:
        """
        Returns the internal card data. If a custom row order is given, return the cards in that order.
        The row_order is used when the user sorted the table by any column. The imported cards then inherit the order
        as shown in the table.
        """
        result = Counter()
        rows = self.rows if row_order is None else (self.rows[row] for row in row_order)
        for row in rows:
            result[row.card] += row.copies
        return result

    def has_basic_lands(self, include_wastes: bool = False, include_snow_basics: bool = False) -> bool:
        basic_land_oracle_ids = self.card_db.get_basic_land_oracle_ids(include_wastes, include_snow_basics)
        return any(filter(lambda row: row.card.oracle_id in basic_land_oracle_ids, self.rows))

    def remove_all_basic_lands(self, remove_wastes: bool = False, remove_snow_basics: bool = False):
        basic_land_oracle_ids = self.card_db.get_basic_land_oracle_ids(remove_wastes, remove_snow_basics)
        to_remove_rows = list(
            (index, index)
            for index, row in enumerate(self.rows)
            if row.card.oracle_id in basic_land_oracle_ids
        )
        merged = reversed(self._merge_ranges(to_remove_rows))
        removed_cards = sum(itertools.starmap(self.remove_cards, merged))
        logger.info(f"User requested removal of basic lands, removed {removed_cards} cards")

    def set_copies_to(self, indices: QItemSelection, value: int):
        """
        Sets the number of copies for all selected cards to value.
        If no card is selected, set the count for all cards.
        """
        if indices.isEmpty():
            selected_ranges = [
                (0, self.rowCount()-1)
            ]
        else:
            selected_ranges = sorted(
                (selected_range.top(), selected_range.bottom()) for selected_range in indices
            )
            # This both minimizes the number of model changes needed and de-duplicates the data received from the
            # selection model. If the user selects a row, the UI returns a range for each cell selected, creating many
            # duplicates that have to be removed.
            selected_ranges = self._merge_ranges(selected_ranges)
        column = CardListColumns.Copies
        roles = [ItemDataRole.DisplayRole, ItemDataRole.EditRole]
        for top, bottom in selected_ranges:
            for item in self.rows[top:bottom+1]:
                item.copies = value
            self.dataChanged.emit(self.index(top, column), self.index(bottom, column), roles)