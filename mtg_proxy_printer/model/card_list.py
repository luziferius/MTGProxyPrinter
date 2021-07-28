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

import enum
import itertools
import typing

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, pyqtSlot


from mtg_proxy_printer.model.carddb import Card

CardList = typing.List[Card]


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
        PageColumns.Image: "Image",
    }

    def __init__(self, *args, **kwargs):
        super(CardListModel, self).__init__(*args, **kwargs)
        self.cards: CardList = []

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
            elif index.column() == PageColumns.Image:
                return card.image_file

    def add_cards(self, cards: typing.Counter[Card]):
        for card, count in cards.items():
            first_index, last_index = self.rowCount(), self.rowCount() + count - 1
            self.beginInsertRows(QModelIndex(), first_index, last_index)
            self.cards += list(itertools.repeat(card, count))
            self.endInsertRows()

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
        del self.cards[first_index:last_index+1]
        self.endRemoveRows()
        return last_index - first_index

    def headerData(
            self, section: typing.Union[int, PageColumns],
            orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> str:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return CardListModel.header[section]
        return super(CardListModel, self).headerData(section, orientation, role)

    def clear(self):
        self.remove_cards([self.index(0, 0), self.index(self.rowCount(), 0)])
