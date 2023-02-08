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

import abc
import collections
import csv
import typing

from PyQt5.QtCore import QObject

from mtg_proxy_printer.model.carddb import Card, CardDatabase, CardIdentificationData
from mtg_proxy_printer.model.imagedb import ImageDatabase

from .common import ParsedDeck, ParserBase
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

LineParserResult = typing.Counter[Card]
CsvLine = typing.Tuple[str, typing.Dict[str, str]]

__all__ = [
    "ScryfallCSVParser",
    "TappedOutCSVParser",
]


class BaseCSVParser(ParserBase):

    DIALECT_NAME = ""

    SUPPORTED_FILE_TYPES = {
        "CSV-Document": ["csv"]
    }
    USED_COLUMNS: typing.Set[str] = {

    }

    def parse_deck_internal(self, deck_list: str, print_guessing: bool, language_override: str = None) -> ParsedDeck:
        deck = collections.Counter()
        unmatched_lines = []
        reader, parsed_lines = self._read_lines_from_csv(deck_list)
        if self.USED_COLUMNS-set(reader.fieldnames):
            self.incompatible_file_format.emit()
            return deck, deck_list.splitlines()
        for source, line in parsed_lines:
            if self.should_skip_entry(line):
                continue
            try:
                cards = self.parse_cards_from_line(line, print_guessing, language_override)
            except ValueError:
                unmatched_lines.append(source)
                continue
            if cards:
                deck.update(cards)
            else:
                unmatched_lines.append(source)
        return deck, unmatched_lines

    def _read_lines_from_csv(self, deck_list: str):
        lines = deck_list.splitlines()
        # Skip the header line when zipping the original lines and the parsed result.
        reader = csv.DictReader(lines, dialect=self.DIALECT_NAME)
        return reader,  zip(lines[1:], reader)

    @abc.abstractmethod
    def parse_cards_from_line(self, line: typing.Dict[str, str], guess_printing: bool, language_override: str = None) \
            -> LineParserResult:
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
    USED_COLUMNS = {
        "scryfall_id", "count", "lang", "name", "set_code", "collector_number",
    }

    def parse_cards_from_line(self, line: typing.Dict[str, str], guess_printing: bool, language_override: str = None) \
            -> LineParserResult:
        cards = collections.Counter()
        scryfall_id = line["scryfall_id"]
        count = int(line["count"])
        language = line["lang"]
        target_language = language_override or language

        if card := self.card_db.get_card_with_scryfall_id(scryfall_id, True):
            if language_override:
                card = self.card_db.translate_card(card, target_language)
            self._add_card_to_deck(cards, card, count)
        elif card := self._handle_removed_printing(scryfall_id, language, guess_printing):
            if language_override:
                card = self.card_db.translate_card(card, target_language)
            self._add_card_to_deck(cards, card, count)
        elif guess_printing:
            logger.debug(f"Card not identified. Try guessing a printing")
            english_name = line["name"]
            card_name = english_name if target_language == "en" else self.card_db.translate_card_name(
                CardIdentificationData("en", english_name, scryfall_id=scryfall_id), target_language)
            card_data = CardIdentificationData(
                target_language, card_name, line["set_code"], line["collector_number"]
            )
            if (card := self.guess_printing(card_data)) is not None:
                self._add_card_to_deck(cards, card, count)
        return cards

    def _handle_removed_printing(self, scryfall_id: str, language: str, guess_printing: bool) -> typing.Optional[Card]:
        if self.card_db.is_removed_printing(scryfall_id):
            choices = self.card_db.get_replacement_card_for_unknown_printing(
                CardIdentificationData(language, scryfall_id=scryfall_id, is_front=True),
                order_by_print_count=guess_printing)
            if choices:
                result = choices[0]
                logger.debug(f"Found {len(choices)} matching printings for removed printing with {scryfall_id=}, "
                             f"using the best match: {result}")
                return result
        return None


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

    DIALECT_NAME = "tappedout_net"
    USED_COLUMNS = {
        # Does not include the Language column,
        # because there is the fallback to the old "Languange" column.
        "Qty", "Name", "Board", "Printing",
    }

    def __init__(self, card_db: CardDatabase, image_db: ImageDatabase,
                 include_maybe_board: bool = False, include_acquire_board: bool = False, parent: QObject = None):
        super(TappedOutCSVParser, self).__init__(card_db, image_db, parent)
        self.allowed_boards = {"main", "side"}
        if include_maybe_board:
            self.allowed_boards.add("maybe")
        if include_acquire_board:
            self.allowed_boards.add("acquire")

    def parse_cards_from_line(self, line: typing.Dict[str, str], guess_printing: bool, language_override: str = None) \
            -> LineParserResult:
        cards = collections.Counter()
        target_language = language_override or self._read_language(line)
        set_code = self._read_set_code(line)
        english_name = line["Name"]
        card_name = self.card_db.translate_card_name(
            CardIdentificationData("en", english_name, set_code), target_language)\
            if target_language != "en" else english_name
        if english_name and not card_name:
            # Unable to translate card. Missing localized card data? Defaulting to English
            card_name = english_name
            target_language = "en"
        count = int(line["Qty"])  # Quantity (Qty) contains the number of copies
        # The current CSV format (2021-02) does not include the collector number, so no way to identify special
        # printings inside larger sets
        for card_data in [
                CardIdentificationData(target_language, card_name, set_code),
                # Try again without the set code, because there may be no card in the original set,
                # so use an arbitrary set in that case.
                CardIdentificationData(target_language, card_name)]:
            if guess_printing and (card := self.guess_printing(card_data)) is not None:
                self._add_card_to_deck(cards, card, count)
                break
            elif not guess_printing and len(result := self.card_db.get_cards_from_data(card_data)) == 1:
                self._add_card_to_deck(cards, result[0], count)
                break
        return cards

    @staticmethod
    def _read_set_code(line: typing.Dict[str, str]) -> typing.Optional[str]:
        set_code = line.get("Printing")
        if set_code:
            # TappedOut uses upper case set codes, so convert to lower case
            set_code = set_code.lower()
        return set_code

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
        return board not in self.allowed_boards


for parser_class in [
    ScryfallCSVParser,
    TappedOutCSVParser,
]:
    csv.register_dialect(parser_class.DIALECT_NAME, parser_class.Dialect)
