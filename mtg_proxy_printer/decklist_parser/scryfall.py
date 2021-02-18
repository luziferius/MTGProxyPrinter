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
import csv
import pathlib
import typing

from mtg_proxy_printer.model.carddb import Card, CardDatabase
import mtg_proxy_printer.settings

ParsedDeck = typing.Tuple[typing.Counter[Card], typing.List[str]]


class ScryfallDialect(csv.Dialect):
    '''
    Specifies the CSV dialect used by Scryfall’s CSV deck export function
    The parameters were determined by inspecting exports. As a test case, a deck containing "Ach! Hans, Run!" was used.
    (Note that the actual card name contains both a comma and the quotation marks.)
    It is exported as """Ach! Hans, Run!""", therefore Scryfall uses the doublequote option.
    '''
    delimiter = ","
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = "\n"
    quoting = csv.QUOTE_MINIMAL


_CSV_DIALECT_NAME = "scryfall_com"
csv.register_dialect(_CSV_DIALECT_NAME, ScryfallDialect)


def parse_deck(card_db: CardDatabase, deck_list: typing.Union[pathlib.Path, str]) -> ParsedDeck:
    deck = collections.Counter()
    unmatched_lines = []
    add_opposing_faces = mtg_proxy_printer.settings.settings["images"].getboolean("automatically-add-opposing-faces")
    for line in _read_lines_from_csv(deck_list):
        cards = _parse_card_from_line(card_db, line, add_opposing_faces)
        if cards:
            deck.update(cards)
        else:
            unmatched_lines.append(str(line))
    return deck, unmatched_lines


def _read_lines_from_csv(
        deck_list: typing.Union[pathlib.Path, str]) -> typing.Generator[typing.Dict[str, str], None, None]:
    if isinstance(deck_list, pathlib.Path):
        with deck_list.open("r", encoding="utf-8", newline="") as csv_file:
            yield from csv.DictReader(csv_file, dialect=_CSV_DIALECT_NAME)
    else:
        yield from csv.DictReader(deck_list.splitlines(), dialect=_CSV_DIALECT_NAME)


def _parse_card_from_line(
        card_db: CardDatabase, line: typing.Dict[str, str], add_opposing_faces: bool) -> typing.Counter[Card]:
    # Only interested in the srcyfall_id and language
    cards = collections.Counter()
    if card_db.is_scryfall_id_known(line["scryfall_id"], True):
        count = int(line["count"])
        card = card_db.get_card_with_scryfall_id(line["scryfall_id"], True)
        print(card)
        cards[card] += count
        if add_opposing_faces and "//" in line["name"] and "//" in line["type"]:
            # Double-faced card
            card = card_db.get_card_with_scryfall_id(line["scryfall_id"], False)
            cards[card] += count
    return cards
