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

from hamcrest import *

import mtg_proxy_printer.model.carddb
import mtg_proxy_printer.model.document

from .helpers import create_new_card_database_with_json_card


def test_document_two_overflow_events_only_add_one_new_page():
    card_db = create_new_card_database_with_json_card("regular_english_card")
    card = card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    document = mtg_proxy_printer.model.document.Document()
    document.add_card(card, document.total_cards_per_page)
    assert_that(document.rowCount(), is_(equal_to(1)))
    for _ in range(document.total_cards_per_page):
        document.add_card(card, 1)
        assert_that(document.pages, has_length(2), "Unexpected page break occurred")
