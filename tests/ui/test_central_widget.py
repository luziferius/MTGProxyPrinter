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

from pathlib import PurePath
from unittest.mock import NonCallableMagicMock, patch

import pytest
from pytestqt.qtbot import QtBot
from PySide6.QtCore import Qt

from hamcrest import *

from mtg_proxy_printer.model.document_page import Page
from mtg_proxy_printer.model.carddb import Card, MTGSet, CheckCard
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard

# Import dynamically used by pytest. Without this, the main_window fixture won’t be found by pytest.
from .test_main_window import main_window  # noqa


def test_deleting_last_card_of_current_page_does_not_raise_exception(qtbot: QtBot, main_window):
    card = main_window.card_database.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    document = main_window.document
    central_widget = main_window.ui.central_widget
    main_window.document.apply(ActionAddCard(card, 9))
    assert_that(
        document.pages,
        only_contains(instance_of(Page))
    )
    central_widget.ui.page_card_table_view.setCurrentIndex(document.index(8, 0, document.index(0, 0)))
    qtbot.mouseClick(central_widget.ui.delete_selected_images_button, Qt.MouseButton.LeftButton)


@pytest.mark.parametrize("name, expected", [
    ('"Quoted"', 'Quoted'),
    ('New\nline', 'Newline'),
    ('Ends with dot and space. ','Ends with dot and space'),
    ('Ends with dot and space .','Ends with dot and space'),
    ('\tTab\t', 'Tab')
])
def test__get_default_image_save_path(qtbot, main_window, name: str, expected: str):
    card = NonCallableMagicMock(spec=Card)
    card.name = name
    result = PurePath(main_window.ui.central_widget._get_default_image_save_path(card))
    assert_that(
        result,
        has_properties({
            "stem": equal_to(expected),
            "suffix": equal_to(".png"),
        })
    )


@pytest.mark.parametrize("card", [
    Card("", MTGSet("", ""), "", "", "", True, "", "", True, False, 1, False, None),
    CheckCard(
        Card("", MTGSet("", ""), "", "", "", True, "", "", True, False, 1, False, None),
        Card("", MTGSet("", ""), "", "", "", True, "", "", True, False, 1, False, None),
    )
])
@pytest.mark.parametrize("count", [1, 3])
def test__add_copies_directly_adds_card_with_image(qtbot, main_window, image_db, card, count):
    if isinstance(card, Card):
        card.image_file = image_db.blank_image
    else:
        card.front.image_file = card.back.image_file = image_db.blank_image
    assert_that(card.image_file, is_(not_none()), "Test setup failed. Card image is None")
    cw = main_window.ui.central_widget
    with patch.object(cw, "request_action", spec=True) as request_action, \
            patch.object(cw, "obtain_card_image", spec=True) as obtain_card_image:
        cw._add_copies(card, count)
    request_action.emit.assert_called_once()
    obtain_card_image.emit.assert_not_called()


@pytest.mark.parametrize("card", [
    Card("", MTGSet("", ""), "", "", "", True, "", "", True, False, 1, False, None)
])
@pytest.mark.parametrize("count", [1, 3])
def test__add_copies_uses_image_db_for_card_without_image(qtbot, main_window, card, count):
    cw = main_window.ui.central_widget
    with patch.object(cw, "request_action", spec=True) as request_action, \
            patch.object(cw, "obtain_card_image", spec=True) as obtain_card_image:
        cw._add_copies(card, count)
    request_action.emit.assert_not_called()
    obtain_card_image.emit.assert_called_once()
