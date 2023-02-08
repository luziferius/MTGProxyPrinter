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

import dataclasses
import typing

from mtg_proxy_printer.model.carddb import Card
from mtg_proxy_printer.units_and_sizes import PageType


@dataclasses.dataclass
class CardContainer:
    parent: "Page"
    card: Card


class Page(typing.List[CardContainer]):

    def page_type(self) -> PageType:
        if not self:
            return PageType.UNDETERMINED
        found_types = set(container.card.requested_page_type() for container in self)
        if found_types == {PageType.REGULAR}:
            return PageType.REGULAR
        if found_types == {PageType.OVERSIZED}:
            return PageType.OVERSIZED
        return PageType.MIXED

    def accepts_card(self, card: typing.Union[Card, PageType]) -> bool:
        other_type = card.requested_page_type() if isinstance(card, Card) else card
        own_page_type = self.page_type()
        return other_type == own_page_type or own_page_type is PageType.UNDETERMINED


PageList = typing.List[Page]
