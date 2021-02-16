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

line_parser = re.compile(r"(?P<copies>\d+) (?P<name>.+) \((?P<set_abbr>\w+)\) (?P<collector_number>\d+)")

ParsedDeck = typing.Tuple[typing.Counter[Card], typing.List[str]]


def parse_deck(card_db: CardDatabase, deck: typing.Union[pathlib.Path, str]) -> ParsedDeck:
    """Parse an MTG Arena deck list. Compatible with Moxfield exports."""
    deck_list = deck.read_text() if isinstance(deck, pathlib.Path) else deck
    add_opposing_faces = mtg_proxy_printer.settings.settings["images"].getboolean("automatically-add-opposing-faces")
    cards = Counter()
    unmatched_lines = []
    for line in deck_list.splitlines():
        if match := line_parser.match(line):
            copies = int(match["copies"])
            # Doesn’t include language information, all cards are implicitly English printings
            matched_card = Card(match["name"], match["set_abbr"].lower(), match["collector_number"], "en")
            if card_db.is_valid_and_unique_card(matched_card):
                card_db.add_missing_information(matched_card)
                cards[matched_card] += copies
                if add_opposing_faces and (opposing_face := card_db.get_opposing_face(matched_card)) is not None:
                    cards[opposing_face] += copies
        elif line:
            # Non-empty, non-matching lines
            unmatched_lines.append(line)
    return cards, unmatched_lines
