#  Copyright © 2020-2025  Thomas Hess <thomas.hess@udo.edu>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.


import unittest.mock

from mtg_proxy_printer.model.carddb import CardDatabase, CardIdentificationData
from mtg_proxy_printer.decklist_parser.re_parsers import MagicWorkstationDeckDataFormatParser


import pytest
from hamcrest import *


@pytest.mark.parametrize("deck, count, card_data", [
    # Card with spaces in name
    ("7 [] Fury Sliver", 7, CardIdentificationData(name="Fury Sliver")),
    ("6 [TSP] Fury Sliver", 6, CardIdentificationData(name="Fury Sliver", set_code="TSP")),
    ("SB:  5 [] Fury Sliver", 5, CardIdentificationData(name="Fury Sliver")),
    ("SB:  4 [TSP] Fury Sliver", 4, CardIdentificationData(name="Fury Sliver", set_code="TSP")),
])
def test_magic_workstation_deck_list_all_variants_work(
        card_db: CardDatabase, deck: str, count: int, card_data: CardIdentificationData):
    image_db = unittest.mock.MagicMock()
    image_db.filter_already_downloaded.return_value = []
    parser = MagicWorkstationDeckDataFormatParser(card_db, image_db)
    assert_that(
        match := parser.parser.match(deck),
        is_(not_none())
    )
    group_dict = match.groupdict()
    assert_that(
        group_dict,
        has_entries({
            "copies": (str(count)),
            "name": equal_to(card_data.name),
            "set_code": equal_to(card_data.set_code),
        })
    )

