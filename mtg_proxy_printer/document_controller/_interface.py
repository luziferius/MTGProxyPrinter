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

from abc import abstractmethod
from functools import partial
import operator
import typing

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
    "ActionList"
]


class IllegalStateError(RuntimeError):
    pass


class DocumentAction:

    COMPARISON_ATTRIBUTES: StringList = []

    @abstractmethod
    def apply(self, document: "Document") -> Self:
        str(self)  # Populate the as_str cache
        return self

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

    @property
    @abstractmethod
    def as_str(self):
        # Note: Why this abstract property?
        # Some string representations require data that is deleted in undo(), so in order
        # to keep the representation, the value has to be saved. But @functools.lru_cache() can’t be used on
        # DocumentAction methods, like __str__(), because instances aren’t hashable.
        # Other caches, like @functools.cache() aren’t available in Py 3.8, require third-party dependencies or
        # require some boilerplate code. Using @functools.cached_property is a reasonably elegant workaround.
        pass

    def __str__(self):
        return self.as_str


ActionList = typing.List[DocumentAction]
