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

import dataclasses
import hashlib
import enum
import functools
import typing

from PyQt5.QtCore import QRect, QPoint, QSize, Qt, QPointF
from PyQt5.QtGui import QPixmap, QColor, QColorConstants, QPainter, QTransform

from mtg_proxy_printer.units_and_sizes import CardSize, PageType, CardSizes, UUID

ItemDataRole = Qt.ItemDataRole
RenderHint = QPainter.RenderHint
SmoothTransformation = Qt.TransformationMode.SmoothTransformation
IgnoreAspectRatio = Qt.AspectRatioMode.IgnoreAspectRatio

@dataclasses.dataclass(frozen=True)
class MTGSet:
    code: str
    name: str

    def data(self, role: ItemDataRole):
        """data getter used for Qt Model API based access"""
        if role == ItemDataRole.EditRole:
            return self
        elif role == ItemDataRole.DisplayRole:
            return f"{self.name} ({self.code.upper()})"
        elif role == ItemDataRole.ToolTipRole:
            return self.name
        else:
            return None


@enum.unique
class CardCorner(enum.Enum):
    """
    The four corners of a card. Values are relative image positions in X and Y.
    These are fractions so that they work properly for both regular and oversized cards

    Values are tuned to return the top-left corner of a 10x10 area
    centered around (20,20) away from the respective corner.
    """
    TOP_LEFT = (15/745, 15/1040)
    TOP_RIGHT = (1-25/745, 15/1040)
    BOTTOM_LEFT = (15/745, 1-25/1040)
    BOTTOM_RIGHT = (1-25/745, 1-25/1040)


@dataclasses.dataclass(unsafe_hash=True)
class Card:
    name: str = dataclasses.field(compare=True)
    set: MTGSet = dataclasses.field(compare=True)
    collector_number: str = dataclasses.field(compare=True)
    language: str = dataclasses.field(compare=True)
    scryfall_id: str = dataclasses.field(compare=True)
    is_front: bool = dataclasses.field(compare=True)
    oracle_id: str = dataclasses.field(compare=True)
    image_uri: str = dataclasses.field(compare=True)
    highres_image: bool = dataclasses.field(compare=False)
    size: CardSize = dataclasses.field(compare=False)
    face_number: int = dataclasses.field(compare=True)
    is_dfc: bool = dataclasses.field(compare=True)
    image_file: typing.Optional[QPixmap] = dataclasses.field(default=None, compare=False)

    def set_image_file(self, image: QPixmap):
        self.image_file = image
        self.corner_color.cache_clear()

    def requested_page_type(self) -> PageType:
        if self.image_file is None:
            return PageType.OVERSIZED if self.is_oversized else PageType.REGULAR
        return PageType.OVERSIZED if self.image_file.size() == CardSizes.OVERSIZED.as_qsize_px() else PageType.REGULAR

    @functools.lru_cache(maxsize=len(CardCorner))
    def corner_color(self, corner: CardCorner) -> QColor:
        """Returns the color of the card at the given corner. """
        if self.image_file is None:
            return QColorConstants.Transparent
        sample_area = self.image_file.copy(QRect(
            QPoint(
                round(self.image_file.width() * corner.value[0]),
                round(self.image_file.height() * corner.value[1])),
            QSize(10, 10)
        ))
        average_color = sample_area.scaledToWidth(1, SmoothTransformation).toImage().pixelColor(0, 0)
        return average_color

    def display_string(self):
        return f'"{self.name}" [{self.set.code.upper()}:{self.collector_number}]'

    @property
    def set_code(self):  # Compatibility with CardIdentificationData
        return self.set.code

    @property
    def is_custom_card(self) -> bool:
        return not self.oracle_id

    @property
    def is_oversized(self) -> bool:
        return self.size == CardSizes.OVERSIZED


@dataclasses.dataclass(unsafe_hash=True)
class CustomCard:
    name: str = dataclasses.field(compare=True)
    set: MTGSet = dataclasses.field(compare=True)
    collector_number: str = dataclasses.field(compare=True)
    language: str = dataclasses.field(compare=True)
    is_front: bool = dataclasses.field(compare=True)
    image_uri: str = dataclasses.field(compare=True)
    highres_image: bool = dataclasses.field(compare=False)
    size: CardSize = dataclasses.field(compare=False)
    face_number: int = dataclasses.field(compare=True)
    is_dfc: bool = dataclasses.field(compare=True)
    source_image_file: bytes = dataclasses.field(default=None, compare=False)

    def requested_page_type(self) -> PageType:
        if self.image_file is None:
            return PageType.OVERSIZED if self.is_oversized else PageType.REGULAR
        return PageType.OVERSIZED if self.image_file.size() == CardSizes.OVERSIZED.as_qsize_px() else PageType.REGULAR

    @functools.lru_cache(maxsize=len(CardCorner))
    def corner_color(self, corner: CardCorner) -> QColor:
        """Returns the color of the card at the given corner. """
        if self.image_file is None:
            return QColorConstants.Transparent
        sample_area = self.image_file.copy(QRect(
            QPoint(
                round(self.image_file.width() * corner.value[0]),
                round(self.image_file.height() * corner.value[1])),
            QSize(10, 10)
        ))
        average_color = sample_area.scaledToWidth(1, SmoothTransformation).toImage().pixelColor(0, 0)
        return average_color

    def display_string(self):
        return f'"{self.name}" [{self.set.code.upper()}:{self.collector_number}]'

    @property
    def oracle_id(self):
        return ""

    @property
    def set_code(self):  # Compatibility with CardIdentificationData
        return self.set.code

    @property
    def is_oversized(self) -> bool:
        return self.size == CardSizes.OVERSIZED

    @property
    def is_custom_card(self) -> bool:
        return True

    @functools.cached_property
    def image_file(self) -> QPixmap:
        source = QPixmap()
        source.loadFromData(self.source_image_file)
        target_size = self.size.as_qsize_px()
        return source if source.size() == target_size else source.scaled(
            target_size, IgnoreAspectRatio, SmoothTransformation)

    @functools.cached_property
    def scryfall_id(self) -> UUID:
        hd = hashlib.md5(self.source_image_file).hexdigest()  # TODO: Maybe use something else instead of md5?
        return UUID(f"{hd[:8]}-{hd[8:12]}-{hd[12:16]}-{hd[16:20]}-{hd[20:]}")


@dataclasses.dataclass(unsafe_hash=True)
class CheckCard:
    front: Card
    back: Card

    @property
    def name(self) -> str:
        return f"{self.front.name} // {self.back.name}"

    @property
    def set(self) -> MTGSet:
        return self.front.set

    @set.setter
    def set(self, value: MTGSet):
        self.front.set = value
        self.back.set = value

    @property
    def collector_number(self) -> str:
        return self.front.collector_number

    @property
    def language(self) -> str:
        return self.front.language

    @property
    def scryfall_id(self) -> str:
        return self.front.scryfall_id

    @property
    def is_front(self) -> bool:
        return True

    @property
    def oracle_id(self) -> str:
        return self.front.oracle_id

    @property
    def size(self):
        return self.front.size

    @property
    def image_uri(self) -> str:
        return ""

    @property
    def set_code(self):
        return self.front.set_code

    @property
    def highres_image(self) -> bool:
        return self.front.highres_image and self.back.highres_image

    @property
    def is_oversized(self):
        return self.front.is_oversized

    @property
    def face_number(self) -> int:
        return 1

    @property
    def is_dfc(self) -> bool:
        return False

    @property
    def is_custom_card(self):
        return self.front.is_custom_card

    @property
    def image_file(self) -> typing.Optional[QPixmap]:
        if self.front.image_file is None or self.back.image_file is None:
            return None
        card_size = self.front.image_file.size()
        # Unlike metric paper sizes, the MTG card aspect ratio does not follow the golden ratio.
        # Cards thus can’t be scaled using a singular factor of sqrt(2) on both axis.
        # The scaled cards get a bit compressed horizontally.
        vertical_scaling_factor = card_size.width() / card_size.height()
        horizontal_scaling_factor = card_size.height() / (2 * card_size.width())
        combined_image = QPixmap(card_size)
        combined_image.fill(QColorConstants.Transparent)
        painter = QPainter(combined_image)
        painter.setRenderHints(RenderHint.SmoothPixmapTransform | RenderHint.HighQualityAntialiasing)
        transformation = QTransform()
        transformation.rotate(90)
        transformation.scale(horizontal_scaling_factor, vertical_scaling_factor)
        painter.setTransform(transformation)
        painter.drawPixmap(QPointF(card_size.width(), -card_size.height()), self.back.image_file)
        painter.drawPixmap(QPointF(0, -card_size.height()), self.front.image_file)

        return combined_image

    def requested_page_type(self) -> PageType:
        return self.front.requested_page_type()

    @functools.lru_cache(maxsize=len(CardCorner))
    def corner_color(self, corner: CardCorner) -> QColor:
        """Returns the color of the card at the given corner. """
        if corner == CardCorner.TOP_LEFT:
            return self.front.corner_color(CardCorner.BOTTOM_LEFT)
        elif corner == CardCorner.TOP_RIGHT:
            return self.front.corner_color(CardCorner.TOP_LEFT)
        elif corner == CardCorner.BOTTOM_LEFT:
            return self.back.corner_color(CardCorner.BOTTOM_RIGHT)
        elif corner == CardCorner.BOTTOM_RIGHT:
            return self.back.corner_color(CardCorner.TOP_RIGHT)
        return QColorConstants.Transparent

    def display_string(self):
        return f'"{self.name}" [{self.set.code.upper()}:{self.collector_number}]'


AnyCardType = typing.Union[Card, CheckCard, CustomCard]
CardList = typing.List[AnyCardType]
OptionalCard = typing.Optional[AnyCardType]
# Py3.8 compatibility hack, because isinstance(a, AnyCardType) fails on 3.8
AnyCardTypeForTypeCheck = typing.get_args(AnyCardType)
