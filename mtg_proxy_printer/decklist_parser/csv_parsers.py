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

import abc
import collections
import csv
import pathlib
import typing

from mtg_proxy_printer.model.carddb import Card, CardDatabase

from .common import ParsedDeck, ParserBase


class BaseCSVParser(ParserBase):

    DIALECT = ""

    def __init__(self, card_db: CardDatabase, ):
        super(BaseCSVParser, self).__init__(card_db)

    def parse_deck(self, deck_list: typing.Union[pathlib.Path, str]) -> ParsedDeck:
        deck = collections.Counter()
        unmatched_lines = []
        for line in self._read_lines_from_csv(deck_list):
            cards = self.parse_card_from_line(line)
            if cards:
                deck.update(cards)
            else:
                unmatched_lines.append(str(line))
        return deck, unmatched_lines

    def _read_lines_from_csv(
            self, deck_list: typing.Union[pathlib.Path, str]) -> typing.Generator[typing.Dict[str, str], None, None]:
        if isinstance(deck_list, pathlib.Path):
            with deck_list.open("r", encoding="utf-8", newline="") as csv_file:
                yield from csv.DictReader(csv_file, dialect=self.DIALECT)
        else:
            yield from csv.DictReader(deck_list.splitlines(), dialect=self.DIALECT)

    @abc.abstractmethod
    def parse_card_from_line(self, line: typing.Dict[str, str]) -> typing.Counter[Card]:
        pass


class ScryfallCSVParser(BaseCSVParser):

    class Dialect(csv.Dialect):
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

    DIALECT = "scryfall_com"

    def parse_card_from_line(self, line: typing.Dict[str, str]) -> typing.Counter[Card]:
        # Only interested in the srcyfall_id and language
        cards = collections.Counter()
        if self.card_db.is_scryfall_id_known(line["scryfall_id"], True):
            count = int(line["count"])
            card = self.card_db.get_card_with_scryfall_id(line["scryfall_id"], True)
            print(card)
            cards[card] += count
            # TODO: This is wrong for split cards
            if self.add_opposing_face and "//" in line["name"] and "//" in line["type"]:
                # Double-faced card
                card = self.card_db.get_card_with_scryfall_id(line["scryfall_id"], False)
                cards[card] += count
        return cards


class TappedOutCSVParser(BaseCSVParser):

    class Dialect(csv.Dialect):
        '''
        Specifies the CSV dialect used by TappedOut (http://tappedout.net/).
        The parameters were determined by inspecting exports. As a test case, a deck containing "Ach! Hans, Run!" was used.
        (Note that the actual card name contains both a comma and the quotation marks.)
        It is exported as """Ach! Hans, Run!""", therefore TappedOut uses the doublequote option.
        '''
        delimiter = ","
        quotechar = '"'
        doublequote = True
        skipinitialspace = False
        lineterminator = "\r\n"
        quoting = csv.QUOTE_MINIMAL

    DIALECT = "tappedout_com"

    def __init__(self, card_db: CardDatabase, include_maybe_board: bool = False, include_acquire_board: bool = False):
        super(TappedOutCSVParser, self).__init__(card_db)
        self.include_acquire_board = include_acquire_board
        self.include_maybe_board = include_maybe_board

    def parse_card_from_line(self, line: typing.Dict[str, str]) -> typing.Counter[Card]:
        cards = collections.Counter()
        if self.should_skip_entry(line):
            return cards
        try:
            language = line["Language"]
        except KeyError:
            # TappedOut fixed the typo in the CSV header in December 2019.
            # Older (or previously compatible) exports may still have the typo in the header line.
            language = line["Languange"]
        if not language or not self.card_db.is_known_language(language):
            language = "en"
        english_name = line["Name"]
        card_name = self.card_db.translate_card_name(english_name, language) if language != "en" else english_name
        set_abbr = line["Printing"].lower()
        count = int(line["Qty"])
        # THe current CSV format (2021-02) does not include the collector number, so no way to identify special
        # printings inside larger sets
        card = Card(
            card_name, set_abbr, None, language
        )
        # TODO: Guess printings.
        return cards

    def should_skip_entry(self, line: typing.Dict[str, str]) -> bool:
        board = line["Board"]
        return any((
            board == "maybe" and not self.include_maybe_board,
            board == "acquire" and not self.include_acquire_board
        ))


for parser_class in [
    ScryfallCSVParser,
    TappedOutCSVParser,
]:
    csv.register_dialect(parser_class.DIALECT, parser_class.Dialect)
