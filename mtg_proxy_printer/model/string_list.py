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


import typing

from PyQt5.QtCore import QAbstractListModel, Qt, QObject, QModelIndex

from mtg_proxy_printer.model.card import MTGSet

__all__ = [
    "PrettySetListModel",
]
INVALID_INDEX = QModelIndex()
ItemDataRole = Qt.ItemDataRole
Orientation = Qt.Orientation


class PrettySetListModel(QAbstractListModel):

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.header = {
            0: self.tr("Set", "MTG set name"),
        }
        self.set_data: typing.List[MTGSet] = []

    def headerData(self, section: int, orientation: Orientation, role: ItemDataRole = ItemDataRole.DisplayRole) \
            -> typing.Optional[str]:
        if role == ItemDataRole.DisplayRole and orientation == Orientation.Horizontal:
            # Returns None for unknown columns
            return self.header.get(section)
        return super().headerData(section, orientation, role)

    def columnCount(self, parent: QModelIndex = INVALID_INDEX) -> int:
        return 0 if parent.isValid() else len(self.header)

    def rowCount(self, parent: QModelIndex = INVALID_INDEX) -> int:
        return 0 if parent.isValid() else len(self.set_data)

    def set_set_data(self, data: typing.List[MTGSet]) -> None:
        self.beginResetModel()
        self.set_data[:] = data
        self.endResetModel()

    def data(self, index: QModelIndex, role: ItemDataRole = ItemDataRole.DisplayRole) -> typing.Optional[str]:
        if index.isValid():
            return self.set_data[index.row()].data(role)
        return None
