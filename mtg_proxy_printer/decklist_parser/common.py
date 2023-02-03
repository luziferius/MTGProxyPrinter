# Copyright (C) 2021, 2022 Thomas Hess <thomas.hess@udo.edu>

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

from abc import abstractmethod
import typing

from PyQt5.QtCore import QObject, pyqtSignal as Signal

from mtg_proxy_printer.model.carddb import Card, CardDatabase, CardIdentificationData
from mtg_proxy_printer.model.imagedb import ImageDatabase
import mtg_proxy_printer.settings
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

__all__ = [
    "ParsedDeck",
    "ParserBase",
]

try:
    # Profiling decorator, injected into globals by line-profiler. Because the injection does funky stuff, this
    # is the easiest way to test if the profile() function is defined.
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    profile
except NameError:
    # If not defined, use this identity decorator as a replacement
    def profile(func):
        return func

ParsedDeck = typing.Tuple[typing.Counter[Card], typing.List[str]]


class ParserBase(QObject):

    SUPPORTED_FILE_TYPES: typing.Dict[str, typing.List[str]] = {}
    incompatible_file_format = Signal()

    def __init__(self, card_db: CardDatabase, image_db: ImageDatabase, parent: QObject = None):
        super(ParserBase, self).__init__(parent)
        self.card_db = card_db
        self.image_db = image_db
        self.add_opposing_face = mtg_proxy_printer.settings.settings["images"].getboolean(
            "automatically-add-opposing-faces"
        )
        self.print_guessing_prefer_already_downloaded = \
            mtg_proxy_printer.settings.settings["decklist-import"].getboolean(
                "prefer-already-downloaded-images"
            )

    def get_file_extension_filter(self) -> str:
        everything = "All files (*)"
        if not self.SUPPORTED_FILE_TYPES:
            return everything
        return ";;".join(
            f'{name} (*.{" *.".join(extensions)})'
            for name, extensions in self.SUPPORTED_FILE_TYPES.items()
        ) + f";;{everything}"

    def parse_deck(self, deck: str,
                   print_guessing: bool,
                   print_guessing_prefer_already_downloaded: bool,
                   language_override: str = None) -> ParsedDeck:
        logger.info("About to parse deck")
        # Implementation note: If a language is given, force print_guessing_prefer_already_downloaded to False,
        # Because it would operate on the cards in the source language. The card choice gets overwritten by the
        # translation step, so performs unnecessary work that gets thrown away anyway.
        self.print_guessing_prefer_already_downloaded = print_guessing_prefer_already_downloaded \
            if language_override is None else False
        parsed_deck, unmatched_lines = self.parse_deck_internal(deck, print_guessing, language_override)
        logger.debug(f"Parsed {sum(parsed_deck.values())} cards. Not identified: {len(unmatched_lines)} lines")
        return parsed_deck, unmatched_lines

    @abstractmethod
    def parse_deck_internal(self, deck_list: str, print_guessing: bool, language_override: str = None) -> ParsedDeck:
        """
        Parse the given deck. Internal method that must be implemented by concrete parser implementations.

        :param deck_list: A multiline Python string that contains the deck list.
        :param print_guessing: Enable guessing a printing, if a line doesn’t identify a unique printing
        :param language_override: Optional two-letter language code. If given, translate all cards into the given
          language.
        :returns: A Counter that contains the parsed cards and a list of strings with unmatched lines
        """
        pass

    @property
    def requires_print_guessing(self) -> bool:
        """
        Subclasses can overwrite this and return True to indicate that the format does not work without
        print guessing enabled, most likely because the format contains insufficient information for accurate parsing.
        """
        return False

    @profile
    def guess_printing(self, card_data: CardIdentificationData) -> typing.Optional[Card]:
        logger.info(f"Guessing card printing for {card_data}")
        if card_data.name:
            card_data.name = card_data.name.strip()
            # Some sources use single forward slashes to separate faces of multi-faced cards.
            card_data.name = card_data.name.replace(" / ", " // ")
            if "//" in card_data.name:
                # If this is a split card, try to identify one half
                card_data.name = card_data.name.split("//")[0 if card_data.is_front else 1].strip()
                logger.debug(f"Card seems to be a split card. Using this part of the name: {card_data.name}")
        if self.card_db.is_valid_and_unique_card(card_data):
            logger.debug("Card is uniquely identified after post-processing the name")
            return self.card_db.get_cards_from_data(card_data)[0]
        if card_data.name and card_data.language is None:
            if (guessed_language := self.card_db.guess_language_from_name(card_data.name)) is not None:
                card_data.language = guessed_language
        if card_data.set_code and card_data.collector_number and (
                possible_matches := self.card_db.get_cards_from_data(
                    CardIdentificationData(
                        card_data.language, set_code=card_data.set_code,
                        collector_number=card_data.collector_number, is_front=card_data.is_front),
                    order_by_print_count=self.print_guessing_prefer_already_downloaded)):
            logger.debug(
                f"Matching using language, set code and collector number. Found {len(possible_matches)} matches."
            )
            return self._determine_best_match(possible_matches)
        if card_data.name and card_data.set_code and (
                possible_matches := self.card_db.get_cards_from_data(
                    CardIdentificationData(card_data.language, card_data.name, card_data.set_code),
                    order_by_print_count=self.print_guessing_prefer_already_downloaded)):
            logger.debug(
                f"Matching using language, card name and set code. Found {len(possible_matches)} matches."
            )
            return self._determine_best_match(possible_matches)
        if card_data.name and (
                possible_matches := self.card_db.get_cards_from_data(
                    CardIdentificationData(card_data.language, card_data.name),
                    order_by_print_count=self.print_guessing_prefer_already_downloaded
                )):
            logger.debug(
                f"Matching using language and card name. Found {len(possible_matches)} matches."
            )
            return self._determine_best_match(possible_matches)

    def _determine_best_match(self, possible_matches: typing.List[Card]) -> Card:
        if self.print_guessing_prefer_already_downloaded and \
                (already_downloaded := self.image_db.filter_already_downloaded(possible_matches)):
            logger.debug(
                f"Found {len(already_downloaded)} matches with already downloaded images. Choose one among those."
            )
            return already_downloaded[0]
        return possible_matches[0]

    def _add_card_to_deck(self, deck: typing.Counter[Card], card: Card, count: int):
        deck[card] += count
        if self.add_opposing_face and (opposing_face := self.card_db.get_opposing_face(card)) is not None:
            # Double-faced card
            deck[opposing_face] += count
