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

"""Contains some constants, like the card size"""
import enum
from typing import NamedTuple

import pint

unit_registry = pint.UnitRegistry()
RESOLUTION: pint.Quantity = unit_registry("300dots/inch")


class CardSize(NamedTuple):
    width: pint.Quantity
    height: pint.Quantity

    @staticmethod
    def as_mm(value: pint.Quantity) -> int:
        size:pint.Quantity = (value/RESOLUTION).to("mm")
        return round(size.magnitude)


@enum.unique
class CardSizes(CardSize, enum.Enum):
    REGULAR = CardSize(unit_registry("745 pixel"), unit_registry("1040 pixel"))
    OVERSIZED = CardSize(unit_registry("1040 pixel"), unit_registry("1490 pixel"))

    @classmethod
    def for_page_type(cls, page_type: "PageType") -> CardSize:
        return cls.OVERSIZED if page_type == PageType.OVERSIZED else cls.REGULAR


@enum.unique
class PageType(enum.Enum):
    """
    This enum can be used to indicate what kind of images are placed on a Page.
    A page that only contains regular-sized images is REGULAR, a page only containing oversized images is OVERSIZED.
    An empty page has an UNDETERMINED image size and can be used for both oversized or regular sized cards
    A page containing both is MIXED. This should never happen. A page being MIXED indicates a bug in the code.
    """
    UNDETERMINED = enum.auto()
    REGULAR = enum.auto()
    OVERSIZED = enum.auto()
    MIXED = enum.auto()
