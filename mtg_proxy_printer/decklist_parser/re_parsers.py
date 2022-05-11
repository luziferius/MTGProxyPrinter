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
import re
import typing

from PyQt5.QtCore import QObject

from mtg_proxy_printer.decklist_parser.common import ParsedDeck, ParserBase
from mtg_proxy_printer.model.carddb import Card, CardDatabase, CardIdentificationData
from mtg_proxy_printer.model.imagedb import ImageDatabase
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

MatchType = typing.Dict[str, str]

__all__ = [
    "GenericRegularExpressionDeckParser",
    "MTGArenaParser",
    "MTGOnlineParser",
    "XMageParser",
]


class GenericRegularExpressionDeckParser(ParserBase):
    """
    A generic regular expression based parser for deck lists. Takes a regular expression as a Python string and
    uses that to parse each input line.
    """

    SUPPORTED_GROUP_NAMES = frozenset((
        "copies", "language", "set_code", "collector_number", "scryfall_id", "name"
    ))

    LINES_TO_SKIP = frozenset()

    def __init__(
            self, card_db: CardDatabase, image_db: ImageDatabase, regular_expression: typing.Union[re.Pattern, str],
            parent: QObject = None):
        super().__init__(card_db, image_db, parent)
        self.parser = regular_expression \
            if isinstance(regular_expression, re.Pattern) \
            else re.compile(regular_expression)
        logger.info(f"Created {self.__class__.__name__} instance using RE '{regular_expression}'")

    def parse_deck_internal(self, deck_list: str, print_guessing: bool, language_override: str = None) -> ParsedDeck:
        cards: typing.Counter[Card] = Counter()
        unmatched_lines = []
        for line in self.line_splitter(deck_list):
            # Convert the Match instance to a dict, in order to have the get() method with a default.
            # The default is used, if the used RE doesn’t contain named groups for some of the defined attributes.
            if match := self.parser.match(line):
                match_dict = match.groupdict()
                copies = int(match_dict.get("copies", 1))
                # If the matcher doesn’t include language information, all cards are implicitly English printings
                matched_card = self._match_card(match_dict)
                if language_override and (translated := self.card_db.translate_card_name(
                        matched_card, language_override)):
                    matched_card.name = translated
                    matched_card.language = language_override
                if self.card_db.is_valid_and_unique_card(matched_card):
                    self._add_matched_card(cards, matched_card, copies)
                elif self.card_db.is_valid_and_unique_card(self._remove_collector_number(matched_card)):
                    # Some sources have invalid collector numbers. So try again without that.
                    self._add_matched_card(cards, matched_card, copies)
                elif print_guessing and (guessed_card := self.guess_printing(matched_card)) is not None:
                    self._add_card_to_deck(cards, guessed_card, copies)
                else:
                    unmatched_lines.append(line)
            elif line:
                # Non-empty, non-matching lines
                unmatched_lines.append(line)
        return cards, unmatched_lines

    def _add_matched_card(self, cards: typing.Counter[Card], matched_card: CardIdentificationData, copies: int):
        card = self.card_db.get_cards_from_data(matched_card)[0]
        self._add_card_to_deck(cards, card, copies)

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
        if matched_card.set_code is not None:
            matched_card.set_code = matched_card.set_code.lower()
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

    def line_splitter(self, deck_list: str) -> typing.Generator[str, None, None]:
        """
        Split the input deck list into individual lines, omitting empty lines.
        Subclasses can overwrite this method to provide custom filtering for unrelated meta-data.
        """
        for line in deck_list.splitlines():
            if line and line not in self.LINES_TO_SKIP:
                yield line


class MTGArenaParser(GenericRegularExpressionDeckParser):
    """
    A parser for MTG Arena deck lists (file extension .mtga). moxfield.com uses this format to export deck lists.
    """
    SUPPORTED_FILE_TYPES = {
        # Magic Arena typically uses the clipboard. Some sites offer downloads with the .txt ending.
        # XMage also lists the .mtga suffix, so add that too.
        "Magic Arena deck file": ["txt", "mtga"]
    }
    
    # The deck segment headers seem inconsistent across different sites
    LINES_TO_SKIP = frozenset((
        # Moxfield uses only the capital SIDEBOARD: with colon, nothing else
        "SIDEBOARD:",
        # MTGGoldfish, mtgazone.com and others indicate that these headers are valid
        "Deck", "Commander", "Sideboard", "Companion",
    ))

    def __init__(self, card_db: CardDatabase, image_db: ImageDatabase, parent: QObject = None):
        super().__init__(
            card_db, image_db,
            # Matcher for the “name” group must be lazy (.+?) to prevent it from swallowing
            # the optional set code and collector number up, if present in the line.
            # Although the format is specified as only allowing two variants, "<copies> <Card name>" and
            # "<copies> <Card name> (<set>) <collector number>", there are broken implementations that also emit
            # “<copies> <Card name> (<set>)”. This RE is designed to also parse this invalid variant.
            re.compile(r"(?P<copies>\d+) (?P<name>.+?)( \((?P<set_code>\w+)\)( (?P<collector_number>.+))?)?$"), parent
        )


class MTGOnlineParser(GenericRegularExpressionDeckParser):
    """
    A parser for Magic Online (MTGO, file extension ".dek") deck lists.
    These do not contain much information, only the English card name and count,
    so sets and individual printings have to be guessed.
    """

    SUPPORTED_FILE_TYPES = {
        # Tappedout and Scryfall exports them with .dek suffix, Moxfield uses .txt
        "Magic Online (MTGO) deck file": ["dek", "txt"],
    }

    def __init__(self, card_db: CardDatabase, image_db: ImageDatabase, parent: QObject = None):
        super().__init__(
            card_db, image_db,
            re.compile(r"(?P<copies>\d+) (?P<name>.+)"), parent
        )

    @property
    def requires_print_guessing(self) -> bool:
        return True


class XMageParser(GenericRegularExpressionDeckParser):
    """
    A parser for XMage deck files (file extension ".dck").
    """

    SUPPORTED_FILE_TYPES = {
        "XMage Deck file": ["dck"],
    }

    def __init__(self, card_db: CardDatabase, image_db: ImageDatabase, parent: QObject = None):
        super().__init__(
            card_db, image_db,
            re.compile(r"(SB: )?(?P<copies>\d+) \[(?P<set_code>\w+):(?P<collector_number>[^]]+)] (?P<name>.+)"), parent
        )

    def line_splitter(self, deck_list: str) -> typing.Generator[str, None, None]:
        # Skip the deck name, if set, and the deck/sideboard layout
        for line in super().line_splitter(deck_list):
            if not line.startswith("NAME") and not line.startswith("LAYOUT"):
                yield line
