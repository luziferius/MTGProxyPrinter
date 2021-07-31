# Copyright (C) 2021 Thomas Hess <thomas.hess@udo.edu>

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


__all__ = [
    "PrettySetListModel",
]


class SetData(typing.NamedTuple):
    set_code: str
    set_name: str

    def __str__(self):
        return f"{self.set_name} ({self.set_code.upper()})"


class PrettySetListModel(QAbstractListModel):

    header = {
        0: "Set",
    }

    def __init__(self, data: typing.List[typing.Tuple[str, str]], parent: QObject = None):
        super(PrettySetListModel, self).__init__(parent)
        # Store both the set abbreviations and set names in dicts for fast index-based lookup via the data() method
        self.set_data: typing.List[SetData] = []
        self.set_set_data(data)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = None) -> typing.Optional[str]:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            # Returns None for unknown columns
            return PrettySetListModel.header.get(section)
        return super(PrettySetListModel, self).headerData(section, orientation, role)

    def columnCount(self, parent: QModelIndex = None) -> int:
        return 1

    def rowCount(self, parent: QModelIndex = None) -> int:
        return len(self.set_data)

    def set_set_data(self, data: typing.List[typing.Tuple[str, str]]) -> None:
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount())
        self.set_data.clear()
        self.endRemoveRows()
        self.beginInsertRows(QModelIndex(), 0, len(data))
        self.set_data[:] = (SetData(set_code, set_name) for set_code, set_name in data)
        self.endInsertRows()

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> typing.Optional[str]:
        if index.isValid():
            row = index.row()
            if role == Qt.DisplayRole:
                return str(self.set_data[row])
            if role == Qt.EditRole:
                return self.set_data[row].set_code
            if role == Qt.ToolTipRole:
                return self.set_data[row].set_name
