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


from pathlib import PurePath
from unittest.mock import NonCallableMagicMock, patch

import pytest
from pytestqt.qtbot import QtBot
from hamcrest import *

from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.carddb import Card, MTGSet, CheckCard, CardDatabase, AnyCardType
from mtg_proxy_printer.units_and_sizes import CardSizes
from mtg_proxy_printer.ui.page_card_table_view import PageCardTableView

# Import dynamically used by pytest. Without this, the main_window fixture won’t be found by pytest.
from .test_main_window import main_window  # noqa

@pytest.fixture()
def table_view(document_light: Document, card_db: CardDatabase) -> PageCardTableView:
    view = PageCardTableView()
    view.set_data(document_light, card_db)
    return view

@pytest.mark.parametrize("name, expected", [
    ('"Quoted"', 'Quoted'),
    ('New\nline', 'Newline'),
    ('Ends with dot and space. ', 'Ends with dot and space'),
    ('Ends with dot and space .', 'Ends with dot and space'),
    ('\tTab\t', 'Tab')
])
def test__get_default_image_save_path(table_view: PageCardTableView, name: str, expected: str):
    card = NonCallableMagicMock(spec=Card)
    card.name = name
    result = PurePath(table_view._get_default_image_save_path(card))
    assert_that(
        result,
        has_properties({
            "stem": equal_to(expected),
            "suffix": equal_to(".png"),
        })
    )


@pytest.mark.parametrize("card", [
    Card("", MTGSet("", ""), "", "", "", True, "", "", True, CardSizes.REGULAR, 1, False, None),
    CheckCard(
        Card("", MTGSet("", ""), "", "", "", True, "", "", True, CardSizes.REGULAR, 1, False, None),
        Card("", MTGSet("", ""), "", "", "", True, "", "", True, CardSizes.REGULAR, 1, False, None),
    )
])
@pytest.mark.parametrize("count", [1, 3])
def test__add_copies_directly_adds_card_with_image(
        table_view: PageCardTableView, image_db, card: AnyCardType, count: int):
    if isinstance(card, Card):
        card.image_file = image_db.get_blank()
    else:
        card.front.image_file = card.back.image_file = image_db.get_blank()
    assert_that(card.image_file, is_(not_none()), "Test setup failed. Card image is None")
    with patch.object(table_view, "request_action", spec=True) as request_action, \
            patch.object(table_view, "obtain_card_image", spec=True) as obtain_card_image:
        table_view._add_copies(card, count)
    request_action.emit.assert_called_once()
    obtain_card_image.emit.assert_not_called()


@pytest.mark.parametrize("card", [
    Card("", MTGSet("", ""), "", "", "", True, "", "", True, CardSizes.REGULAR, 1, False, None)
])
@pytest.mark.parametrize("count", [1, 3])
def test__add_copies_uses_image_db_for_card_without_image(
        table_view: PageCardTableView, card: AnyCardType, count: int):
    with patch.object(table_view, "request_action", spec=True) as request_action, \
            patch.object(table_view, "obtain_card_image", spec=True) as obtain_card_image:
        table_view._add_copies(card, count)
    request_action.emit.assert_not_called()
    obtain_card_image.emit.assert_called_once()
