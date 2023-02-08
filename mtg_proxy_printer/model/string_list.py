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

import typing

from PyQt5.QtCore import QAbstractListModel, Qt, QObject, QModelIndex

from mtg_proxy_printer.model.carddb import MTGSet


__all__ = [
    "PrettySetListModel",
]
INVALID_INDEX = QModelIndex()


class PrettySetListModel(QAbstractListModel):

    header = {
        0: "Set",
    }

    def __init__(self, parent: QObject = None):
        super(PrettySetListModel, self).__init__(parent)
        # Store both the set abbreviations and set names in dicts for fast index-based lookup via the data() method
        self.set_data: typing.List[MTGSet] = []

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> typing.Optional[str]:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            # Returns None for unknown columns
            return PrettySetListModel.header.get(section)
        return super(PrettySetListModel, self).headerData(section, orientation, role)

    def columnCount(self, parent: QModelIndex = INVALID_INDEX) -> int:
        return 0 if parent.isValid() else len(self.header)

    def rowCount(self, parent: QModelIndex = INVALID_INDEX) -> int:
        return 0 if parent.isValid() else len(self.set_data)

    def set_set_data(self, data: typing.List[MTGSet]) -> None:
        if self.set_data:
            self.beginRemoveRows(INVALID_INDEX, 0, self.rowCount())
            self.set_data.clear()
            self.endRemoveRows()
        if data:
            self.beginInsertRows(INVALID_INDEX, 0, len(data))
            self.set_data[:] = data
            self.endInsertRows()

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> typing.Optional[str]:
        if index.isValid():
            return self.set_data[index.row()].data(role)
