# Copyright (C) 2020-2024 Thomas Hess <thomas.hess@udo.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import dataclasses
from functools import partial
import typing

from mtg_proxy_printer.model.carddb import AnyCardType, AnyCardTypeForTypeCheck
from mtg_proxy_printer.units_and_sizes import PageType


@dataclasses.dataclass
class CardContainer:
    parent: "Page"
    card: AnyCardType


class Page(typing.List[CardContainer]):

    def __init__(self, __iterable: typing.Iterable[AnyCardType] = None):
        __iterable = __iterable or []
        __iterable = map(partial(CardContainer, self), __iterable)
        super().__init__(__iterable)

    def __iadd__(self, other, /):
        if isinstance(other, Page):
            return super().__iadd__(other)
        else:
            return super().__iadd__(map(partial(CardContainer, self), other))

    def page_type(self) -> PageType:
        if not self:
            return PageType.UNDETERMINED
        found_types = set(container.card.requested_page_type() for container in self)
        if found_types == {PageType.REGULAR}:
            return PageType.REGULAR
        if found_types == {PageType.OVERSIZED}:
            return PageType.OVERSIZED
        return PageType.MIXED

    def accepts_card(self, card: typing.Union[AnyCardType, PageType]) -> bool:
        other_type = card.requested_page_type() if isinstance(card, AnyCardTypeForTypeCheck) else card
        own_page_type = self.page_type()
        return other_type == own_page_type or own_page_type is PageType.UNDETERMINED

    def insert(self, __index: int, __object: typing.Union[AnyCardType, CardContainer]) -> CardContainer:
        if isinstance(__object, CardContainer):
            container = __object
            container.parent = self
        else:
            container = CardContainer(self, __object)
        super().insert(__index, container)
        return container

    def append(self, __object: AnyCardType) -> CardContainer:
        container = CardContainer(self, __object)
        super().append(container)
        return container


PageList = typing.List[Page]
