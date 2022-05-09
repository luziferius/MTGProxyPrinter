# Copyright (C) 2017-2019, 2021-2022 Thomas Hess <thomas.hess@udo.edu>

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

"""
Natural sorting for lists or other iterables of strings.
"""

import re
import typing

from PyQt5.QtCore import QSortFilterProxyModel, QModelIndex

__all__ = [
    "natural_sorted",
    "str_less_than",
    "NaturallySortedSortFilterProxyModel",
]

_NUMBER_GROUP_REG_EXP = re.compile(r"(\d+)")


def try_convert_int(s: str):
    try:
        return int(s)
    except ValueError:
        return s


def alphanum_key(s: str):
    """
    Turn a string into a list of string and number chunks.
    "z23a" -> ["z", 23, "a"]
    """
    return [try_convert_int(c) for c in _NUMBER_GROUP_REG_EXP.split(s)]


def natural_sorted(unsorted: typing.Iterable[str], reverse: bool = False):
    """
    Sort the given iterable in the way that humans expect.
    """
    return sorted(unsorted, key=alphanum_key, reverse=reverse)


def str_less_than(first: str, other: str, /):
    """
    Compare two strings using natural sorting
    :return: True, if the first string is less than the second, False otherwise
    """
    if first == other:
        return False
    s1, s2 = natural_sorted((first, other))
    return s1 == first


class NaturallySortedSortFilterProxyModel(QSortFilterProxyModel):

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        left_data = left.data(self.sortRole())
        right_data = right.data(self.sortRole())
        if isinstance(left_data, str) and isinstance(right_data, str):
            return str_less_than(left_data, right_data)
        return super().lessThan(left, right)

    def row_sort_order(self) -> typing.List[int]:
        """Returns the row numbers of the source model in the current sort order."""
        return [
            self.mapToSource(self.index(row, 0)).row() for row in range(self.rowCount())
        ]
