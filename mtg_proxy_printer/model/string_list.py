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


StringList = typing.List[str]
StringDict = typing.Dict[int, str]


class PrettySetListModel(QAbstractListModel):

    header = {
        0: "Set",
    }

    def __init__(self, data: typing.List[typing.Tuple[str, str]], parent: QObject = None):
        super(PrettySetListModel, self).__init__(parent)
        # Store both the set abbreviations and set names in dicts for fast index-based lookup via the data() method
        self.set_codes: StringDict = {}
        self.set_names: StringDict = {}
        self.set_set_data(data)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = None) -> typing.Optional[str]:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            # Returns None for unknown columns
            return PrettySetListModel.header.get(section)
        return super(PrettySetListModel, self).headerData(section, orientation, role)

    def columnCount(self, parent: QModelIndex = None) -> int:
        return 1

    def rowCount(self, parent: QModelIndex = None) -> int:
        return len(self.set_codes)

    def set_set_data(self, data: typing.List[typing.Tuple[str, str]]) -> None:
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount())
        self.set_codes.clear()
        self.set_names.clear()
        self.endRemoveRows()
        self.beginInsertRows(QModelIndex(), 0, len(data))
        for index, (code, name) in enumerate(data):
            self.set_codes[index] = code
            self.set_names[index] = name
        self.endInsertRows()

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> typing.Optional[str]:
        if index.isValid():
            row = index.row()
            if role == Qt.DisplayRole:
                return f"{self.set_names[row]} ({self.set_codes[row].upper()})"
            if role == Qt.EditRole:
                return self.set_codes[row]
            if role == Qt.ToolTipRole:
                return self.set_names[row]
