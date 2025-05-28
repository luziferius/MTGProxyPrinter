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


from abc import abstractmethod
from functools import partial
import itertools
import operator
import typing

from PyQt5.QtCore import QCoreApplication

from mtg_proxy_printer.units_and_sizes import StringList

if typing.TYPE_CHECKING:
    from mtg_proxy_printer.model.document import Document

try:
    from typing import Self
except ImportError:  # Compatibility with Python < 3.11
    from typing_extensions import Self

__all__ = [
    "DocumentAction",
    "IllegalStateError",
    "Self",
    "ActionList",
    "split_iterable",
]
T = typing.TypeVar("T")


def split_iterable(iterable: typing.Iterable[T], chunk_size: int, /) -> typing.List[typing.Tuple[T, ...]]:
    """Split the given iterable into chunks of size chunk_size. Does not add padding values to the last item."""
    iterable = iter(iterable)
    return list(iter(lambda: tuple(itertools.islice(iterable, chunk_size)), ()))


class IllegalStateError(RuntimeError):
    pass


class DocumentAction:
    """Base class for modifying Document instances via the Command pattern."""

    COMPARISON_ATTRIBUTES: StringList = []  # Defines which attributes have to be compared in __eq__()
    translate = QCoreApplication.translate

    @abstractmethod
    def apply(self, document: "Document") -> Self:
        """Apply the action to the given document"""
        str(self)  # Populate the as_str cache
        return self

    @abstractmethod
    def undo(self, document: "Document") -> Self:
        """
        Reverses the application of the action to the given document, undoing its effects.
        For this to work properly, this action must have been the most recent action applied to the document.
        """
        return self

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

    def _format_number_range(self, first: int, last: int) -> str:
        """
        Formats an inclusive range. If first == last, returns that number as a string.
        Otherwise, returns a translation-enabled range first-last
        """
        if first == last:
            return str(first)
        return self.translate(
            "DocumentAction", "{first}-{last}", "Inclusive, formatted number range, from first to last")


ActionList = typing.List[DocumentAction]
