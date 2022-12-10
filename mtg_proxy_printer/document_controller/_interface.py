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

import typing
from abc import abstractmethod

from PyQt5.QtCore import QObject

from mtg_proxy_printer.model.document import Document

try:
    from typing import Self
except ImportError:  # Compatibility with Python < 3.11
    Self = typing.TypeVar("Self", bound="DocumentAction")

__all__ = [
    "DocumentAction",
    "IllegalStateError",
]


class IllegalStateError(RuntimeError):
    pass


class DocumentAction(QObject):

    @abstractmethod
    def apply(self, document: Document) -> Self:
        pass

    @abstractmethod
    def undo(self, document: Document) -> Self:
        pass
