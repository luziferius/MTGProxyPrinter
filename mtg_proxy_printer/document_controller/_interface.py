# Copyright (C) 2022 Thomas Hess <thomas.hess@udo.edu>

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

from abc import abstractmethod
from functools import partial
import operator
import typing

from PyQt5.QtCore import QObject

if typing.TYPE_CHECKING:
    from mtg_proxy_printer.model.document import Document

try:
    from typing import Self
except ImportError:  # Compatibility with Python < 3.11
    Self = typing.TypeVar("Self", bound="DocumentAction")

StringList = typing.List[str]

__all__ = [
    "DocumentAction",
    "IllegalStateError",
    "Self",
]


class IllegalStateError(RuntimeError):
    pass


class DocumentAction(QObject):

    COMPARISON_ATTRIBUTES: StringList = []

    @abstractmethod
    def apply(self, document: "Document") -> Self:
        pass

    @abstractmethod
    def undo(self, document: "Document") -> Self:
        pass

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and all(
            map(
                operator.eq,
                map((partial(getattr, self)), self.COMPARISON_ATTRIBUTES),
                map((partial(getattr, other)), self.COMPARISON_ATTRIBUTES)
            )
        )
