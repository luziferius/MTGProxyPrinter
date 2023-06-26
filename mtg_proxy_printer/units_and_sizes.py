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
import typing
try:
    from typing import NotRequired
except ImportError:  # Compatibility with Python < 3.11
    from typing import Optional as NotRequired

import pint

unit_registry = pint.UnitRegistry()
RESOLUTION: pint.Quantity = unit_registry("300dots/inch")
UUID = str
DEFAULT_SAVE_SUFFIX = "mtgproxies"


class CardSize(typing.NamedTuple):
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


class ImageUriType(typing.TypedDict):
    small: str
    normal: str
    large: str
    png: str
    art_crop: str
    border_crop: str


class FaceDataType(typing.TypedDict):
    image_uris: NotRequired[ImageUriType]
    layout: NotRequired[str]
    name: str
    oracle_id: NotRequired[UUID]
    printed_name: NotRequired[str]


class RelatedCardType(typing.TypedDict):
    object: str
    id: UUID
    component: str
    name: str
    type_line: str
    uri: str


class CardDataType(typing.TypedDict):
    """Card data type modelled according to https://scryfall.com/docs/api/cards"""
    all_parts: NotRequired[typing.List[RelatedCardType]]
    border_color: str
    card_back_id: UUID
    card_faces: NotRequired[typing.List[FaceDataType]]
    collector_number: str
    content_warning: NotRequired[bool]
    digital: bool
    highres_image: bool
    id: UUID
    image_status: str
    image_uris: NotRequired[ImageUriType]
    lang: str
    layout: str
    legalities: typing.Dict[str, str]
    name: str
    object: str
    oracle_id: NotRequired[UUID]  # Reversible cards hold the oracle_id in the card_faces elements instead.
    oversized: bool
    printed_name: NotRequired[str]
    promo: bool
    released_at: str
    scryfall_set_uri: str
    set: str
    set_name: str
    set_type: str


class BulkDataType(typing.TypedDict):
    """
    The data returned by the bulk data API end point.
    See https://scryfall.com/docs/api/bulk-data
    """
    id: UUID
    uri: str
    type: str
    name: str
    description: str
    download_uri: str
    updated_at: str
    size: int
    content_type: str
    content_encoding: str
