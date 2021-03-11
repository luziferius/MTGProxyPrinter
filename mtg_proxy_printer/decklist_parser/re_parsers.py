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

from mtg_proxy_printer.decklist_parser.common import ParsedDeck, ParserBase
from mtg_proxy_printer.model.carddb import Card, CardDatabase, CardIdentificationData

MatchType = typing.Dict[str, str]


class GenericRegularExpressionDeckParser(ParserBase):
    """
    A generic regular expression based parser for deck lists. Takes a regular expression as a Python string and
    uses that to parse each input line.
    """

    def __init__(self, card_db: CardDatabase, regular_expression: typing.Union[re.Pattern, str]):
        super(GenericRegularExpressionDeckParser, self).__init__(card_db)
        self.parser = regular_expression \
            if isinstance(regular_expression, re.Pattern) \
            else re.compile(regular_expression)

    def parse_deck(self, deck: typing.Union[pathlib.Path, str]) -> ParsedDeck:
        """
        Parse the given deck using the stored regular expression.
        :param deck: A Path instance to a deck file or a multiline Python string that contains the deck list.
        :returns: A Counter that contains the parsed cards and a list of strings with unmatched lines
        """
        deck_list = deck.read_text() if isinstance(deck, pathlib.Path) else deck
        cards: typing.Counter[Card] = Counter()
        unmatched_lines = []
        for line in self.line_splitter(deck_list):
            # Convert the Match instance to a dict, in order to have get() with a default. The default is used,
            # if the used RE doesn’t contain named groups for some of the attributes.
            if match := self.parser.match(line):
                match_dict = match.groupdict()
                copies = int(match_dict.get("copies", 1))
                # If the matcher doesn’t include language information, all cards are implicitly English printings
                matched_card = self._match_card(match_dict)
                if self.card_db.is_valid_and_unique_card(matched_card):
                    self._add_matched_card(cards, matched_card, copies)
                elif self.card_db.is_valid_and_unique_card(self._remove_collector_number(matched_card)):
                    self._add_matched_card(cards, matched_card, copies)
                else:
                    unmatched_lines.append(line)
            elif line:
                # Non-empty, non-matching lines
                unmatched_lines.append(line)
        return cards, unmatched_lines

    def _add_matched_card(self, cards: typing.Counter[Card], matched_card: CardIdentificationData, copies: int):
        card = self.card_db.get_card_from_data(matched_card)
        cards[card] += copies
        if self.add_opposing_face and (
                opposing_face := self.card_db.get_opposing_face(matched_card)) is not None:
            cards[opposing_face] += copies

    @staticmethod
    def _remove_collector_number(card: CardIdentificationData) -> CardIdentificationData:
        card.collector_number = None
        return card

    def _match_card(self, match_dict: MatchType) -> CardIdentificationData:
        matched_name = self._match_name(match_dict)
        language = self._match_language(match_dict, matched_name)
        matched_card = CardIdentificationData(
            language, matched_name, match_dict.get("set_code"),
            match_dict.get("collector_number"),
            scryfall_id=match_dict.get("scryfall_id"),
        )
        # Some sources have upper case set codes, but this program uses the Scryfall convention of using lower-case
        # codes. So lower the code, if set.
        if matched_card.set_abbr is not None:
            matched_card.set_abbr = matched_card.set_abbr.lower()
        return matched_card

    def _match_language(self, match_dict: MatchType, name: typing.Optional[str]) -> str:
        """
        If the used RE doesn’t provide a language, try to guess the language based on the card name.
        If neither language nor card name are given, default to English printings.
        """
        language = match_dict.get("language")
        if language:
            language = language.lower()
        language_unknown = not language or not self.card_db.is_known_language(language)
        if language_unknown and name:
            language = self.card_db.guess_language_from_name(name)
            language_unknown = not language
        # language might be set to something not in the database, so use this boolean, instead of "not language"
        if language_unknown:
            language = "en"
        return language

    @staticmethod
    def _match_name(match_dict: MatchType) -> typing.Optional[str]:
        name = match_dict.get("name")
        if name and "//" in name:
            # Many sources combine both names of split- or flip-cards as "Front // Back". If so, simply remove the
            # second name, as the back, if any, will be added later.
            name = name.split("//")[0].rstrip()
        return name

    @staticmethod
    def line_splitter(deck_list: str) -> typing.Generator[str, None, None]:
        """
        Split the input deck list into individual lines, omitting empty lines.
        Subclasses can overwrite this method to provide custom filtering for unrelated meta-data.
        """
        for line in deck_list.splitlines():
            if line:
                yield line


class MTGArenaParser(GenericRegularExpressionDeckParser):
    """
    A parser for MTG Arena deck lists (file extension .mtga). moxfield.com uses this format to export deck lists.
    """
    def __init__(self, card_db: CardDatabase):
        super(MTGArenaParser, self).__init__(
            card_db,
            re.compile(r"(?P<copies>\d+) (?P<name>.+) \((?P<set_code>\w+)\)( (?P<collector_number>\d+))?")
        )

    def line_splitter(self, deck_list: str) -> typing.Generator[str, None, None]:
        # Skip emtpy lines and the Sideboard marker
        for line in super(MTGArenaParser, self).line_splitter(deck_list):
            if line != "SIDEBOARD:":
                yield line


class MTGOnlineParser(GenericRegularExpressionDeckParser):
    """
    A parser for Magic Online (MTGO, file extension ".dek") deck lists.
    These do not contain much information, only the English card name and count,
    so sets and individual printings have to be guessed.
    """
    def __init__(self, card_db: CardDatabase):
        super(MTGOnlineParser, self).__init__(
            card_db,
            re.compile(r"(?P<copies>\d+) (?P<name>.+)")
        )


class XMageParser(GenericRegularExpressionDeckParser):
    """
    A parser for XMage deck files (file extension ".dck").
    """
    def __init__(self, card_db: CardDatabase):
        super(XMageParser, self).__init__(
            card_db,
            re.compile(r"(SB: )?(?P<copies>\d+) \[(?P<set_code>\w+):(?P<collector_number>[^]]+)] (?P<name>.+)")
        )

    def line_splitter(self, deck_list: str) -> typing.Generator[str, None, None]:
        # Skip emtpy lines, the deck name, if set, and the deck/sideboard layout
        for line in super(XMageParser, self).line_splitter(deck_list):
            if not line.startswith("NAME") and not line.startswith("LAYOUT"):
                yield line
