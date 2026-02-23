#  Copyright © 2020-2026  Thomas Hess <thomas.hess@udo.edu>
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
from mtg_proxy_printer.decklist_parser.re_parsers import MTGArenaParser


import pytest
from hamcrest import *


@pytest.mark.parametrize("deck, count, card_data", [
    # Single word name
    ("7 Counterspell", 7, CardIdentificationData(name="Counterspell")),
    ("6 Counterspell (PHED)", 6, CardIdentificationData(name="Counterspell", set_code="PHED")),
    ("5 Counterspell (phed)", 5, CardIdentificationData(name="Counterspell", set_code="phed")),
    ("4 Counterspell (PHED) 33", 4, CardIdentificationData(name="Counterspell", set_code="PHED", collector_number="33")),
    ("3 Counterspell (phed) 33", 3, CardIdentificationData(name="Counterspell", set_code="phed", collector_number="33")),
    # Card with spaces in name
    ("7 Fury Sliver", 7, CardIdentificationData(name="Fury Sliver")),
    ("6 Fury Sliver (TSP)", 6, CardIdentificationData(name="Fury Sliver", set_code="TSP")),
    ("5 Fury Sliver (tsp)", 5, CardIdentificationData(name="Fury Sliver", set_code="tsp")),
    ("4 Fury Sliver (TSP) 157", 4, CardIdentificationData(name="Fury Sliver", set_code="TSP", collector_number="157")),
    ("3 Fury Sliver (tsp) 157", 3, CardIdentificationData(name="Fury Sliver", set_code="tsp", collector_number="157")),
    # Silver-bordered card with a term in parentheses in the card name. This is quite a hard case to match correctly
    ("7 Erase (Not the Urza's Legacy One)", 7, CardIdentificationData(name="Erase (Not the Urza's Legacy One)")),
    ("6 Erase (Not the Urza's Legacy One) (UNH)", 6, CardIdentificationData(name="Erase (Not the Urza's Legacy One)", set_code="UNH")),
    ("5 Erase (Not the Urza's Legacy One) (unh)", 5, CardIdentificationData(name="Erase (Not the Urza's Legacy One)", set_code="unh")),
    ("4 Erase (Not the Urza's Legacy One) (UNH) 10", 4, CardIdentificationData(name="Erase (Not the Urza's Legacy One)", set_code="UNH", collector_number="10")),
    ("3 Erase (Not the Urza's Legacy One) (unh) 10", 3, CardIdentificationData(name="Erase (Not the Urza's Legacy One)", set_code="unh", collector_number="10")),
])
def test_mtg_arena_parser_all_format_variants_work(
        card_db: CardDatabase, deck: str, count: int, card_data: CardIdentificationData):
    image_db = unittest.mock.MagicMock()
    image_db.filter_already_downloaded.return_value = []
    parser = MTGArenaParser(card_db, image_db)
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
            "collector_number": equal_to(card_data.collector_number),
        })
    )
