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

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, pyqtSlot as Slot, pyqtSignal as Signal, QItemSelection
from PyQt5.QtGui import QIcon

from mtg_proxy_printer.decklist_parser.common import CardCounter
from mtg_proxy_printer.model.carddb import Card, CardIdentificationData, CardDatabase, AnyCardType
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
    card: Card
    copies: int


class CardListColumns(enum.IntEnum):
    Copies = 0
    CardName = enum.auto()
    Set = enum.auto()
    CollectorNumber = enum.auto()
    Language = enum.auto()
    IsFront = enum.auto()


CardList = typing.List[CardListModelRow]

class CardListModel(QAbstractTableModel):
    """
    This is a model for holding a list of cards.
    """
    EDITABLE_COLUMNS = {
        CardListColumns.Copies, CardListColumns.Set, CardListColumns.CollectorNumber, CardListColumns.Language,
    }
    oversized_card_count_changed = Signal(int)

    def __init__(self, card_db: CardDatabase, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.header = {
            CardListColumns.Copies: self.tr("Copies"),
            CardListColumns.CardName: self.tr("Card name"),
            CardListColumns.Set: self.tr("Set"),
            CardListColumns.CollectorNumber: self.tr("Collector #"),
            CardListColumns.Language: self.tr("Language"),
            CardListColumns.IsFront: self.tr("Side"),
        }
        self.card_db = card_db
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
                    return card.set.code
                else:
                    return f"{card.set.name} ({card.set.code.upper()})"
            elif column == CardListColumns.CollectorNumber:
                return card.collector_number
            elif column == CardListColumns.Language:
                return card.language
            elif column == CardListColumns.IsFront:
                if role == ItemDataRole.EditRole:
                    return card.is_front
                return self.tr("Front") if card.is_front else self.tr("Back")
        if card.is_oversized:
            if role == ItemDataRole.ToolTipRole:
                return self.tr("Beware: Potentially oversized card!\nThis card may not fit in your deck.")
            elif role == ItemDataRole.DecorationRole:
                return self._oversized_icon

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        flags = super().flags(index)
        if index.column() in self.EDITABLE_COLUMNS:
            flags |= ItemFlag.ItemIsEditable
        return flags

    def setData(self, index: QModelIndex, value: typing.Any, role: ItemDataRole = ItemDataRole.EditRole) -> bool:
        row, column = index.row(), index.column()
        if role == ItemDataRole.EditRole and column in self.EDITABLE_COLUMNS:
            logger.debug(f"Setting card list model data for column {column} to {value}")
            container = self.rows[row]
            card = container.card
            if column == CardListColumns.Copies:
                old_value, container.copies = container.copies, value
                if card.is_oversized and (difference := value-old_value):
                    self.oversized_card_count += difference
                    self.oversized_card_count_changed.emit(self.oversized_card_count)
                return True
            elif column == CardListColumns.CollectorNumber:
                card_data = CardIdentificationData(
                    card.language, card.name, card.set.code, value, is_front=card.is_front)
            elif column == CardListColumns.Set:
                card_data = CardIdentificationData(
                    card.language, card.name, value, is_front=card.is_front
                )
            else:
                card_data = self.card_db.translate_card(card, value)
                if card_data == card:
                    return False
            return self._request_replacement_card(index, card_data)
        return False

    def _request_replacement_card(
            self, index: QModelIndex, card_data: typing.Union[CardIdentificationData, AnyCardType]):
        row, column = index.row(), index.column()
        if isinstance(card_data, CardIdentificationData):
            logger.debug(f"Requesting replacement for {card_data}")
            result = self.card_db.get_cards_from_data(card_data)
        else:
            result = [card_data]
        if result:
            # Simply choose the first match. The user can’t make a choice at this point, so just use one of
            # the results.
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

    @Slot(list)
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
