# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import typing

import pytest
from hamcrest import *
from pytestqt.qtbot import QtBot

from PySide6.QtCore import Qt, QPoint, QRect, QItemSelectionModel
from PySide6.QtWidgets import QDialogButtonBox

from mtg_proxy_printer.model.carddb import CardDatabase, CardIdentificationData
from mtg_proxy_printer.ui.add_card import HorizontalAddCardWidget, VerticalAddCardWidget

from tests.helpers import fill_card_database_with_json_card

StringList = typing.List[str]
OptString = typing.Optional[str]
LeftButton = Qt.MouseButton.LeftButton
ClearAndSelect = QItemSelectionModel.SelectionFlag.ClearAndSelect
StandardButton = QDialogButtonBox.StandardButton


@pytest.mark.parametrize("widget_class", [HorizontalAddCardWidget, VerticalAddCardWidget])
def test_add_card_works_with_art_series_card(qtbot: QtBot, card_db: CardDatabase, widget_class):
    """
    Test for bug /tktview/cca01cfe00adc56c520bcefa7cf45e1f95447267
    "Art-Series cards crash the application", found in v0.11.0
    """
    fill_card_database_with_json_card(qtbot, card_db, "english_double_faced_art_series_card")
    expected_card_identification_data = CardIdentificationData(
        "en", "Clearwater Pathway", "aznr", "25"
    )
    qtbot.add_widget(add_card_widget := widget_class())
    add_card_widget.set_card_database(card_db)
    add_card_widget.card_name_filter_updated("")  # Populate the card name list
    add_card_widget.ui.card_name_list.setSelection(QRect(1, 1, 1, 1), ClearAndSelect)
    qtbot.mouseClick(add_card_widget.ui.card_name_list, LeftButton, pos=QPoint(10, 10))
    ok_button = add_card_widget.ui.button_box.button(StandardButton.Ok)
    qtbot.mouseClick(ok_button, LeftButton, pos=QPoint(10, 10))
    assert_that(add_card_widget._read_card_data_from_ui(), is_(equal_to(expected_card_identification_data)))
