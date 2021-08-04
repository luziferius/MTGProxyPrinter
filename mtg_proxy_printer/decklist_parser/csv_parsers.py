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
import typing

from PyQt5.QtCore import QObject

from mtg_proxy_printer.model.carddb import Card, CardDatabase, CardIdentificationData
from mtg_proxy_printer.model.imagedb import ImageDatabase

from .common import ParsedDeck, ParserBase

LineParserResult = typing.Counter[Card]
CsvLine = typing.Tuple[str, typing.Dict[str, str]]

__all__ = [
    "ScryfallCSVParser",
    "TappedOutCSVParser",
]


class BaseCSVParser(ParserBase):

    DIALECT_NAME = ""

    def parse_deck(self, deck_list: str,
                   print_guessing: bool,
                   print_guessing_prefer_already_downloaded: bool) -> ParsedDeck:
        self.print_guessing_prefer_already_downloaded = print_guessing_prefer_already_downloaded
        deck = collections.Counter()
        unmatched_lines = []
        for source, line in self._read_lines_from_csv(deck_list):
            if self.should_skip_entry(line):
                continue
            cards = self.parse_cards_from_line(line, print_guessing)
            if cards:
                deck.update(cards)
            else:
                unmatched_lines.append(source)
        return deck, unmatched_lines

    def _read_lines_from_csv(
            self, deck_list: str) -> typing.Generator[CsvLine, None, None]:
        lines = deck_list.splitlines()
        # Skip the header line when zipping the original lines and the parsed result.
        yield from zip(lines[1:], csv.DictReader(lines, dialect=self.DIALECT_NAME))

    @abc.abstractmethod
    def parse_cards_from_line(self, line: typing.Dict[str, str], guess_printing: bool) -> LineParserResult:
        pass

    def should_skip_entry(self, line: typing.Dict[str, str]) -> bool:
        return False


class ScryfallCSVParser(BaseCSVParser):

    class Dialect(csv.Dialect):
        '''
        Specifies the CSV dialect used by Scryfall’s CSV deck export function
        The parameters were determined by inspecting exports.
        As a test case, a deck containing "Ach! Hans, Run!" was used.
        (Note that the actual card name contains both a comma and the quotation marks.)
        It is exported as """Ach! Hans, Run!""", therefore Scryfall uses the doublequote option.
        '''
        delimiter = ","
        quotechar = '"'
        doublequote = True
        skipinitialspace = False
        lineterminator = "\n"
        quoting = csv.QUOTE_MINIMAL

    DIALECT_NAME = "scryfall_com"

    def parse_cards_from_line(self, line: typing.Dict[str, str], guess_printing: bool) -> LineParserResult:
        # Only interested in the scryfall_id and language
        cards = collections.Counter()
        scryfall_id = line["scryfall_id"]
        count = int(line["count"])
        if (card := self.card_db.get_card_with_scryfall_id(scryfall_id, True)) is not None:
            self._add_card_to_deck(cards, card, count)
        else:
            language = line["lang"]
            english_name = line["name"]
            card_name = self.card_db.translate_card_name(english_name, language) if language != "en" else english_name
            card_data = CardIdentificationData(
                language, card_name, line["set_code"], line["collector_number"]
            )
            if (card := self.guess_printing(card_data)) is not None:
                self._add_card_to_deck(cards, card, count)
        return cards


class TappedOutCSVParser(BaseCSVParser):

    class Dialect(csv.Dialect):
        '''
        Specifies the CSV dialect used by TappedOut (http://tappedout.net/).
        The parameters were determined by inspecting exports.
        As a test case, a deck containing "Ach! Hans, Run!" was used.
        (Note that the actual card name contains both a comma and the quotation marks.)
        It is exported as """Ach! Hans, Run!""", therefore TappedOut uses the doublequote option.
        '''
        delimiter = ","
        quotechar = '"'
        doublequote = True
        skipinitialspace = False
        lineterminator = "\r\n"
        quoting = csv.QUOTE_MINIMAL

    DIALECT_NAME = "tappedout_com"

    def __init__(self, card_db: CardDatabase, image_db: ImageDatabase,
                 include_maybe_board: bool = False, include_acquire_board: bool = False, parent: QObject = None):
        super(TappedOutCSVParser, self).__init__(card_db, image_db, parent)
        self.include_acquire_board = include_acquire_board
        self.include_maybe_board = include_maybe_board

    def parse_cards_from_line(self, line: typing.Dict[str, str], guess_printing: bool) -> LineParserResult:
        cards = collections.Counter()
        language = self._read_language(line)
        english_name = line["Name"]
        card_name = self.card_db.translate_card_name(english_name, language) if language != "en" else english_name
        if english_name and not card_name:
            # Unable to translate card. Missing localized card data? Defaulting to English
            card_name = english_name
            language = "en"
        set_code = line["Printing"].lower()  # TappedOut uses upper case set codes, so convert to lower case
        count = int(line["Qty"])  # Quantity (Qty) contains the number of copies
        # The current CSV format (2021-02) does not include the collector number, so no way to identify special
        # printings inside larger sets
        card_data = CardIdentificationData(
            language, card_name, set_code
        )
        if guess_printing and (card := self.guess_printing(card_data)) is not None:
            self._add_card_to_deck(cards, card, count)
        elif not guess_printing and len(result := self.card_db.get_cards_from_data(card_data)) == 1:
            self._add_card_to_deck(cards, result[0], count)
        return cards

    def _read_language(self, line: typing.Dict[str, str]):
        try:
            language = line["Language"]
        except KeyError:
            # TappedOut fixed the typo in the CSV header in December 2019.
            # Older (or previously compatible) exports may still have the typo in the header line.
            language = line["Languange"]  # noqa
        if language:
            language = language.lower()
        if not language or not self.card_db.is_known_language(language):
            language = "en"
        return language

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
    csv.register_dialect(parser_class.DIALECT_NAME, parser_class.Dialect)
