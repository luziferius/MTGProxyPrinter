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

import enum
import itertools
import typing

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, pyqtSlot as Slot, pyqtSignal as Signal, QItemSelection
from PyQt5.QtGui import QIcon

from mtg_proxy_printer.model.carddb import Card, CardIdentificationData, CardDatabase
from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger
CardList = typing.List[Card]

__all__ = [
    "CardListModel",
    "PageColumns",
]
INVALID_INDEX = QModelIndex()


class PageColumns(enum.IntEnum):
    CardName = 0
    Set = 1
    CollectorNumber = 2
    Language = 3
    Image = 4


class CardListModel(QAbstractTableModel):
    """
    This is a model for holding a simple list of cards.
    """

    header = {
        PageColumns.CardName: "Card name",
        PageColumns.Set: "Set",
        PageColumns.CollectorNumber: "Collector #",
        PageColumns.Language: "Language",
    }
    EDITABLE_COLUMNS = {PageColumns.Set, PageColumns.CollectorNumber}

    oversized_card_count_changed = Signal(int)

    def __init__(self, card_db: CardDatabase, *args, **kwargs):
        super(CardListModel, self).__init__(*args, **kwargs)
        self.card_db = card_db
        self.cards: CardList = []
        self.oversized_card_count = 0
        self._oversized_icon = QIcon.fromTheme("data-warning")

    def rowCount(self, parent: QModelIndex = INVALID_INDEX) -> int:
        return 0 if parent.isValid() else len(self.cards)

    def columnCount(self, parent: QModelIndex = INVALID_INDEX) -> int:
        return 0 if parent.isValid() else len(CardListModel.header)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> typing.Any:
        card = self.cards[index.row()]
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
        if card.is_oversized:
            if role == Qt.ToolTipRole:
                return "Beware: Potentially oversized card!\nThis card may not fit in your deck."
            elif role == Qt.DecorationRole:
                return self._oversized_icon

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        flags = super(CardListModel, self).flags(index)
        if index.column() in self.EDITABLE_COLUMNS:
            flags |= Qt.ItemIsEditable
        return flags

    def setData(self, index: QModelIndex, value: typing.Any, role: int = Qt.EditRole) -> bool:
        if role == Qt.EditRole and index.column() in self.EDITABLE_COLUMNS:
            logger.debug(f"Setting card list model data for column {index.column()} to {value}")
            card = self.cards[index.row()]
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
            logger.debug(f"Requesting replacement for {card_data}")
            # Simply choose the first match. The user can’t make a choice at this point, so just use one of
            # the results.
            new_card = result[0]
            top_left = index.sibling(index.row(), index.column())
            bottom_right = top_left.siblingAtColumn(PageColumns.CollectorNumber)
            old_card = self.cards[index.row()]
            self.cards[index.row()] = new_card
            self.dataChanged.emit(top_left, bottom_right, (Qt.DisplayRole, Qt.EditRole, Qt.ToolTipRole))
            # Oversized card count changes, iff the flags differ
            if old_card.is_oversized and not new_card.is_oversized:
                self._remove_card_handle_oversized_flag(old_card)
            elif new_card.is_oversized and not old_card.is_oversized:
                self._add_card_handle_oversized_flag(new_card)
            return True
        logger.debug(f"No replacement card found for {card_data}.")
        return False

    def add_cards(self, cards: typing.Counter[Card]):
        for card, count in cards.items():
            first_index, last_index = self.rowCount(), self.rowCount() + count - 1
            self.beginInsertRows(INVALID_INDEX, first_index, last_index)
            self.cards += list(itertools.repeat(card, count))
            self.endInsertRows()
            self._add_card_handle_oversized_flag(card, count)

    def _add_card_handle_oversized_flag(self, card: Card, count: int = 1):
        if card.is_oversized:
            self.oversized_card_count += count
            self.oversized_card_count_changed.emit(self.oversized_card_count)

    def _remove_card_handle_oversized_flag(self, card: Card):
        if card.is_oversized:
            self.oversized_card_count -= 1
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
        removed_cards = self.cards[top:last_row]
        del self.cards[top:last_row]
        self.endRemoveRows()
        for card in removed_cards:
            self._remove_card_handle_oversized_flag(card)
        return last_row - top

    def headerData(
            self, section: typing.Union[int, PageColumns],
            orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> str:
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return CardListModel.header.get(section)
            elif role == Qt.ToolTipRole and section in self.EDITABLE_COLUMNS:
                return "Double-click on entries to\nswitch the selected printing."
        return super(CardListModel, self).headerData(section, orientation, role)

    def clear(self):
        logger.debug(f"About to clear {self.__class__.__name__} instance. Removing {self.rowCount()} entries.")
        self.beginRemoveRows(INVALID_INDEX, 0, self.rowCount()-1)
        self.cards.clear()
        self.endRemoveRows()
        if self.oversized_card_count:
            self.oversized_card_count = 0
            self.oversized_card_count_changed.emit(self.oversized_card_count)

    def as_cards(self, row_order: typing.List[int] = None) -> CardList:
        """
        Returns the internal card list. If a custom row order is given, return the cards in that order.
        The row_order is used when the user sorted the table by any column. The imported cards then inherit the order
        as shown in the table.
        """
        if row_order is None:
            return self.cards
        return [self.cards[row] for row in row_order]

    def has_basic_lands(self, include_wastes: bool = False, include_snow_basics: bool = False) -> bool:
        basic_land_oracle_ids = self.card_db.get_basic_land_oracle_ids(include_wastes, include_snow_basics)
        return any(filter(lambda card: card.oracle_id in basic_land_oracle_ids, self.cards))

    def remove_all_basic_lands(self, remove_wastes: bool = False, remove_snow_basics: bool = False):
        basic_land_oracle_ids = self.card_db.get_basic_land_oracle_ids(remove_wastes, remove_snow_basics)
        to_remove_rows = list(
            (index, index)
            for index, card in enumerate(self.cards)
            if card.oracle_id in basic_land_oracle_ids
        )
        merged = reversed(self._merge_ranges(to_remove_rows))
        removed_cards = sum(itertools.starmap(self.remove_cards, merged))
        logger.info(f"User requested removal of basic lands, removed {removed_cards} cards")
