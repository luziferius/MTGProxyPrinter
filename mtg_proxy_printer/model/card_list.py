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

from collections import Counter
import enum
import itertools
import typing

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, pyqtSlot, pyqtSignal
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

    oversized_card_count_changed = pyqtSignal(int)

    def __init__(self, card_db: CardDatabase, *args, **kwargs):
        super(CardListModel, self).__init__(*args, **kwargs)
        self.card_db = card_db
        self.cards: CardList = []
        self.oversized_card_count = 0
        self._oversized_icon = QIcon.fromTheme("data-warning")

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.cards)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
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
            logger.debug(f"Requesting replacement for card '{card_data.name}' in set {card_data.set_code}")
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
        logger.debug("No replacement card found.")
        return False

    def add_cards(self, cards: typing.Counter[Card]):
        for card, count in cards.items():
            first_index, last_index = self.rowCount(), self.rowCount() + count - 1
            self.beginInsertRows(QModelIndex(), first_index, last_index)
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

    @pyqtSlot(list)
    def remove_multi_selection(self, indices: typing.List[QModelIndex]) -> int:
        """
        Remove all cards in the given multi-selection.

        :param indices: List with QModelIndex instances that represents a multi-selection.
          As returned by a QSelectionModel
        :return: Number of cards removed
        """
        current_range: typing.List[QModelIndex] = []
        ranges: typing.List[typing.List[QModelIndex]] = []
        for index in indices:
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

    def remove_cards(self, indices: typing.List[QModelIndex]) -> int:
        """
        Remove all cards in the given list of consecutive model indices
        Only accesses the first and last index in the list to query the first and last row to delete.
        The intermediate rows are implicit.

        :return: Number of cards removed
        """
        if not indices:
            return 0
        first_index, last_index = indices[0].row(), indices[-1].row()
        self.beginRemoveRows(QModelIndex(), first_index, last_index)
        removed_cards = self.cards[first_index:last_index+1]
        del self.cards[first_index:last_index+1]
        self.endRemoveRows()
        for card in removed_cards:
            self._remove_card_handle_oversized_flag(card)
        return last_index - first_index

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
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount()-1)
        self.cards.clear()
        self.endRemoveRows()
        if self.oversized_card_count:
            self.oversized_card_count = 0
            self.oversized_card_count_changed.emit(self.oversized_card_count)

    def as_deck(self):
        return Counter(self.cards)
