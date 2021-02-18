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

from collections import Counter
import pathlib
import re
import typing

from mtg_proxy_printer.model.carddb import Card, CardDatabase
import mtg_proxy_printer.settings

ParsedDeck = typing.Tuple[typing.Counter[Card], typing.List[str]]


class GenericRegularExpressionDeckParser:
    """
    A generic regular expression based parser for deck lists. Takes a regular expression as a Python string and
    uses that to parse each input line.
    """

    def __init__(self, card_db: CardDatabase, regular_expression: str):
        self.card_db = card_db
        self.parser = re.compile(regular_expression)
        self.add_opposing_face = mtg_proxy_printer.settings.settings["images"].getboolean(
            "automatically-add-opposing-faces"
        )

    def parse_deck(self, deck: typing.Union[pathlib.Path, str]) -> ParsedDeck:
        """Parse an MTG Arena deck list. Compatible with Moxfield exports."""
        deck_list = deck.read_text() if isinstance(deck, pathlib.Path) else deck
        cards = Counter()
        unmatched_lines = []
        for line in deck_list.splitlines():
            # Convert the Match instance to a dict, in order to have get() with a default. The default is used,
            # if the user-supplied RE doesn’t contain named groups for some of the attributes.
            if match := self.parser.match(line):
                match_dict = match.groupdict()
                copies = int(match_dict.get("copies", 1))
                # If the matcher doesn’t include language information, all cards are implicitly English printings
                matched_card = Card(
                    match_dict.get("name"), match_dict.get("set_code"),
                    match_dict.get("collector_number"), match_dict.get("language", "en"),
                    scryfall_id=match_dict.get("scryfall_id"),
                )
                if matched_card.set_abbr is not None:
                    matched_card.set_abbr = matched_card.set_abbr.lower()
                if self.card_db.is_valid_and_unique_card(matched_card):
                    self.card_db.add_missing_information(matched_card)
                    cards[matched_card] += copies
                    if self.add_opposing_face and (
                            opposing_face := self.card_db.get_opposing_face(matched_card)) is not None:
                        cards[opposing_face] += copies
            elif line:
                # Non-empty, non-matching lines
                unmatched_lines.append(line)
        return cards, unmatched_lines


class MTGArenaParser(GenericRegularExpressionDeckParser):
    """
    A parser for MTG Arena deck lists. moxfield.com uses this format to export deck lists.
    """
    def __init__(self, card_db: CardDatabase):
        super(MTGArenaParser, self).__init__(
            card_db,
            r"(?P<copies>\d+) (?P<name>.+) \((?P<set_code>\w+)\) (?P<collector_number>\d+)"
        )


class MTGOnlineParser(GenericRegularExpressionDeckParser):
    """
    A parser for Magic Online (MTGO, file extension ".dek") deck lists.
    These do not contain much information, only the English card name and count,
    so sets and individual printings have to be guessed.
    """
    def __init__(self, card_db: CardDatabase):
        super(MTGOnlineParser, self).__init__(
            card_db,
            r"(?P<copies>\d+) (?P<name>.+)"
        )
