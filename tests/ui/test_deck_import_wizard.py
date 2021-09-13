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

import pytest
from hamcrest import *
from pytestqt.qtbot import QtBot

from PyQt5.QtCore import QStringListModel, Qt, QPoint, QObject
from PyQt5.QtWidgets import QCheckBox, QWizard, QTableView, QComboBox
from PyQt5.QtTest import QTest

from mtg_proxy_printer.model.carddb import CardDatabase, Card
from mtg_proxy_printer.ui.deck_import_wizard import DeckImportWizard
from mtg_proxy_printer.decklist_parser.re_parsers import MTGOnlineParser, MTGArenaParser
from mtg_proxy_printer.model.card_list import PageColumns

from tests.helpers import fill_card_database_with_json_card

StringList = typing.List[str]
OptString = typing.Optional[str]


def test_going_back_to_textual_deck_list_resets_parsed_cards_model(qtbot: QtBot, card_db: CardDatabase):
    fill_card_database_with_json_card(card_db, "regular_english_card")
    language_model = QStringListModel(card_db.get_all_languages(), parent=None)
    wizard = DeckImportWizard(card_db, MagicMock(), language_model)
    deck_list = "1 Fury Sliver"
    qtbot.add_widget(wizard)
    with qtbot.wait_exposed(wizard):
        wizard.show()
    _select_magic_online_parser(qtbot, wizard)
    _move_wizard_forward(qtbot, wizard)
    _input_deck_list(qtbot, wizard, deck_list)
    _move_wizard_forward(qtbot, wizard)
    list_model = wizard.summary_page.card_list
    _validate_model_content(list_model)
    _move_wizard_backward(qtbot, wizard)
    _move_wizard_forward(qtbot, wizard)
    assert_that(wizard.summary_page.card_list, is_(same_instance(list_model)))
    _validate_model_content(list_model)


def _move_wizard_forward(qtbot: QtBot, wizard: QWizard):
    with qtbot.wait_signal(wizard.currentIdChanged, timeout=100):
        wizard.next()


def _move_wizard_backward(qtbot: QtBot, wizard: QWizard):
    with qtbot.wait_signal(wizard.currentIdChanged, timeout=100):
        wizard.back()


def _select_magic_online_parser(qtbot: QtBot, wizard: DeckImportWizard):
    with qtbot.wait_signal(wizard.select_deck_parser_page.completeChanged, timeout=100):
        cb: QCheckBox = wizard.select_deck_parser_page.select_parser_mtg_online
        cb.click()
    assert_that(wizard.select_deck_parser_page.selected_parser, is_(instance_of(MTGOnlineParser)))
    assert_that(wizard.select_deck_parser_page.select_parser_mtg_online.isChecked())
    assert_that(wizard.select_deck_parser_page.complete, is_(True))
    assert_that(wizard.select_deck_parser_page.isComplete())
    assert_that(wizard.field("selected_parser"), is_(instance_of(MTGOnlineParser)))
    assert_that(wizard.validateCurrentPage(), is_(True))


def _select_magic_arena_parser(qtbot: QtBot, wizard: DeckImportWizard):
    with qtbot.wait_signal(wizard.select_deck_parser_page.completeChanged, timeout=100):
        cb: QCheckBox = wizard.select_deck_parser_page.select_parser_mtg_arena
        cb.click()
    assert_that(wizard.select_deck_parser_page.selected_parser, is_(instance_of(MTGArenaParser)))
    assert_that(wizard.select_deck_parser_page.select_parser_mtg_arena.isChecked())
    assert_that(wizard.select_deck_parser_page.complete, is_(True))
    assert_that(wizard.select_deck_parser_page.isComplete())
    assert_that(wizard.field("selected_parser"), is_(instance_of(MTGArenaParser)))
    assert_that(wizard.validateCurrentPage(), is_(True))


def _input_deck_list(qtbot: QtBot, wizard: DeckImportWizard, deck_list: str):
    with qtbot.wait_signal(wizard.load_list_page.deck_list.textChanged, timeout=100):
        wizard.load_list_page.deck_list.setPlainText(deck_list)
    assert_that(wizard.field("deck_list"), is_(equal_to(deck_list)))
    assert_that(wizard.load_list_page.isComplete())


def _validate_model_content(list_model):
    assert_that(list_model.rowCount(), is_(equal_to(1)))
    assert_that(list_model.cards, has_length(1))
    assert_that(list_model.cards[0], has_properties({
        "name": equal_to("Fury Sliver"),
        "set": has_properties({
            "name": equal_to("Time Spiral"),
            "code": equal_to("tsp"),
        }),
        "scryfall_id": equal_to("0000579f-7b35-4ed3-b44c-db2a538066fe"),
        "collector_number": equal_to("157"),
        "language": equal_to("en"),
        "is_front": is_(True),
        "image_uri": equal_to(
            "https://c1.scryfall.com/file/scryfall-cards/png/front/"
            "0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979"),
        "image_file": is_(none()),
    }))


class DeckReceiver(QObject):
    def __init__(self, parent: QObject = None):
        super(DeckReceiver, self).__init__(parent)
        self.deck: typing.Counter[Card] = None

    def on_deck_received(self, deck: typing.Counter[Card]):
        self.deck = deck


def test_selecting_different_printing_works(qtbot: QtBot, card_db: CardDatabase):
    fill_card_database_with_json_card(card_db, "regular_english_card")
    fill_card_database_with_json_card(card_db, "regular_english_card_reprint")
    language_model = QStringListModel(card_db.get_all_languages(), parent=None)
    wizard = DeckImportWizard(card_db, MagicMock(), language_model)
    deck_list = "2 Fury Sliver (TSP) 157"
    qtbot.add_widget(wizard)
    with qtbot.wait_exposed(wizard):
        wizard.show()
    _select_magic_arena_parser(qtbot, wizard)
    _move_wizard_forward(qtbot, wizard)
    _input_deck_list(qtbot, wizard, deck_list)
    _move_wizard_forward(qtbot, wizard)
    table_view: QTableView = wizard.summary_page.parsed_cards_table
    cell_position = QPoint(
        table_view.columnViewportPosition(PageColumns.Set) + 5,
        table_view.rowViewportPosition(0) + 5
    )
    # Select cell
    QTest.mouseClick(table_view.viewport(), Qt.LeftButton, pos=cell_position)
    # Enter edit mode
    QTest.mouseDClick(table_view.viewport(), Qt.LeftButton, pos=cell_position)
    # Now get the editor and select a different set to get another printing
    editor: QComboBox = table_view.viewport().childAt(cell_position)
    assert_that(editor, is_(instance_of(QComboBox)))
    # Select the second entry in the editor’s item list
    QTest.keyClick(editor, Qt.Key_Down)
    with qtbot.wait_signal(table_view.model().dataChanged):
        # Wait until the editor saved the data in the model
        QTest.keyClick(editor, Qt.Key_Enter)
    # Now accept the dialog and capture the emitted deck
    deck_receiver = DeckReceiver()
    wizard.deck_added.connect(deck_receiver.on_deck_received)
    with qtbot.wait_signal(wizard.deck_added, timeout=100):
        QTest.keyClick(wizard, Qt.Key_Enter)
    assert_that(deck_receiver.deck, all_of(
        is_(not_none()),
        has_length(2),
    ))
    assert_that(deck_receiver.deck.keys(), contains_inanyorder(
        has_properties({
            "name": equal_to("Fury Sliver"),
            "set": has_properties({
                "name": equal_to("Time Spiral"),
                "code": equal_to("tsp"),
            }),
            "scryfall_id": equal_to("0000579f-7b35-4ed3-b44c-db2a538066fe"),
            "collector_number": equal_to("157"),
            "language": equal_to("en"),
            "is_front": is_(True),
            "image_uri": equal_to(
                "https://c1.scryfall.com/file/scryfall-cards/png/front/"
                "0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979"),
            "image_file": is_(none()),
        }),
        has_properties({
            "name": equal_to("Fury Sliver"),
            "set": has_properties({
                "name": equal_to("Time Spiral Remastered"),
                "code": equal_to("tsr"),
            }),
            "scryfall_id": equal_to("a8a64329-09fc-4e0d-b7d1-378635f2801a"),
            "collector_number": equal_to("164"),
            "language": equal_to("en"),
            "is_front": is_(True),
            "image_uri": equal_to(
                "https://c1.scryfall.com/file/scryfall-cards/png/front/"
                "a/8/a8a64329-09fc-4e0d-b7d1-378635f2801a.png?1619396979"),
            "image_file": is_(none()),
        }),
    ))
