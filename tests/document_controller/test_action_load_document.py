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

from pathlib import Path

from hamcrest import *

from mtg_proxy_printer.document_controller.load_document import ActionLoadDocument
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.page_layout import PageLayoutSettings


def test_loading_two_distinct_cards_on_first_page_works(document: Document):
    cdb = document.card_db
    content = [
        [
            front := cdb.get_card_with_scryfall_id("b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", True),
            cdb.get_opposing_face(front)
        ]
    ]
    action = ActionLoadDocument(Path("/invalid.mtgproxies"), content, PageLayoutSettings.create_from_settings())
    action.apply(document)
    assert_that(document.rowCount(), is_(1))
    assert_that(document.rowCount(document.index(0, 0)), is_(2))
