# Copyright (C) 2020 Thomas Hess <thomas.hess@udo.edu>

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

import typing

StringList = typing.List[str]


class CardDatabase:

    def __init__(self):
        pass

    def get_card_names(self, language: str) -> StringList:
        """Returns a list with all card names in the given language."""
        pass

    def get_sets(self) -> StringList:
        """Returns a list with all set names."""
        pass

    def find_cards_from_set(self,language: str, set_prefix: str, collectors_number_prefix: str) -> StringList:
        """
        Finds all cards given the set name prefix and collector number prefix.

        :returns: List of card names
        """
        pass

    def find_sets_for_card(self, language: str, card_name: str) -> typing.Tuple[str, StringList]:
        """
        Finds all sets and collector numbers given the card name and language.
        May find multiple collector numbers per set, if the card has multiple printings in a set.
        (Prime example: Basic lands)

        :returns: List with tuples (set name, List[collector number strings])
        """
        pass
