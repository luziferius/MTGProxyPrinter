# Copyright (C) 2021 Thomas Hess <thomas.hess@udo.edu>

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

import collections
import copy
import itertools
import typing
from abc import abstractmethod

from PyQt5.QtCore import QObject

from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.carddb import CardDatabase, Card, CardIdentificationData
from mtg_proxy_printer.model.imagedb import ImageDatabase
import mtg_proxy_printer.decklist_parser.common


class FormatterBase(QObject):

    def __init__(self, card_db: CardDatabase, image_db: ImageDatabase, parent: QObject = None):
        super(FormatterBase, self).__init__(parent)
        self.card_db = card_db
        self.parser = mtg_proxy_printer.decklist_parser.common.ParserBase(self.card_db, image_db)

    def format(self, document: Document) -> str:
        """Format the given document as a deck list."""
        # FIXME: Handle some corner cases:
        #  What about a document that contains back faces without any fronts?
        #  What about mismatched front and back faces? Which printing should be chosen for formats that allow
        #  specifying the exact print?

        # Work on a copy of the card objects. This prevents side effects when formatting card names of double-faced
        # cards
        cards: typing.Iterable[Card] = map(copy.copy, itertools.chain.from_iterable(document))
        counted_cards = collections.Counter()
        for card in cards:
            if not card.is_front:
                continue
            if card.language != "en":
                card = self._translate_card(card)
            self._format_name_of_double_faced_cards(card)
            counted_cards[card] += 1

        result = "\n".join(itertools.starmap(self.format_card, counted_cards.items()))
        return result

    def _translate_card(self, non_english_card: Card) -> Card:
        translated_name = self.card_db.translate_card_name(non_english_card.name, "en", non_english_card.language)
        card_data = CardIdentificationData(
            "en", translated_name, non_english_card.set.code, is_front=non_english_card.is_front
        )
        possible_cards = self.card_db.get_cards_from_data(card_data)
        if possible_cards:
            translated_card = possible_cards[0]
            self._format_name_of_double_faced_cards(translated_card)
            return translated_card
        elif translated_card := self.parser.guess_printing(card_data):
            self._format_name_of_double_faced_cards(translated_card)
            return translated_card
        else:
            # TODO: Translation failed?
            pass

        return translated_card

    def _format_name_of_double_faced_cards(self, card: Card):
        if opposing_face := self.card_db.get_opposing_face(card):
            card.name = f"{card.name} // {opposing_face.name}"

    @abstractmethod
    def format_card(self, card: Card, count: int) -> str:
        pass


class XMageFormatter(FormatterBase):
    def format_card(self, card: Card, count: int) -> str:
        # Sample: "1 [AER:154] Hope of Ghirapur"
        return f"{count} [{card.set.code.upper()}:{card.collector_number}] {card.name}"


class MTGOnlineFormatter(FormatterBase):
    def format_card(self, card: Card, count: int) -> str:
        # Sample: "1 Mental Misstep"
        return f"{count} {card.name}"


class MTGArenaFormatter(FormatterBase):
    def format_card(self, card: Card, count: int) -> str:
        # Sample: "1 Dispel (BFZ) 76"
        return f"{count} {card.name} ({card.set.code.upper()}) {card.collector_number}"
