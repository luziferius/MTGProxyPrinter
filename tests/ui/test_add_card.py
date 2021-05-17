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

import typing
from unittest.mock import MagicMock

from hamcrest import *
import pytest

from PyQt5.QtCore import Qt, QPoint, QRect, QItemSelectionModel
from PyQt5.QtWidgets import QDialogButtonBox

from mtg_proxy_printer.model.carddb import CardDatabase, CardIdentificationData
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.ui.add_card import AddCardWidget

from tests.helpers import create_new_card_database_with_json_card

StringList = typing.List[str]
OptString = typing.Optional[str]


@pytest.fixture()
def model_with_art_series_card() -> CardDatabase:
    return create_new_card_database_with_json_card("english_double_faced_art_series_card")


def test_add_card_works_with_art_series_card(qtbot, model_with_art_series_card: CardDatabase):
    """
    Test for bug /tktview/cca01cfe00adc56c520bcefa7cf45e1f95447267
    "Art-Series cards crash the application", found in v0.11.0
    """
    expected_card_identification_data = CardIdentificationData(
        "en", "Clearwater Pathway", "aznr", "25"
    )
    qtbot.add_widget(add_card_widget := AddCardWidget())
    add_card_widget.set_card_database(model_with_art_series_card)
    add_card_widget.copies_input.setValue(1)
    add_card_widget.card_name_list.setSelection(QRect(1, 1, 1, 1), QItemSelectionModel.ClearAndSelect)
    qtbot.mouseClick(add_card_widget.card_name_list, Qt.LeftButton, pos=QPoint(10, 10))
    qtbot.wait(10)
    qtbot.mouseClick(
        add_card_widget.button_box.button(QDialogButtonBox.Ok), Qt.LeftButton
    )
    assert_that(add_card_widget._read_card_data_from_ui(), is_(equal_to(expected_card_identification_data)))




