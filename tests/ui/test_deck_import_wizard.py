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

from collections import Counter
import itertools
import typing
import unittest.mock
from unittest.mock import MagicMock

from hamcrest import *
from pytestqt.qtbot import QtBot
import pytest

from PyQt5.QtCore import QStringListModel, Qt, QPoint, QObject
from PyQt5.QtWidgets import QCheckBox, QWizard, QTableView, QComboBox, QLineEdit
from PyQt5.QtTest import QTest

import mtg_proxy_printer.settings
from mtg_proxy_printer.model.carddb import CardDatabase, CardIdentificationData
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.ui.deck_import_wizard import DeckImportWizard
from mtg_proxy_printer.decklist_parser.re_parsers import MTGOnlineParser, MTGArenaParser, \
    GenericRegularExpressionDeckParser
from mtg_proxy_printer.model.card_list import CardListColumns, CardListModel, CardCounter
from mtg_proxy_printer.document_controller.import_deck_list import ActionImportDeckList

from tests.helpers import fill_card_database_with_json_cards

Key = Qt.Key
MouseButton = Qt.MouseButton
WizardButton = QWizard.WizardButton


def create_and_show_wizard(qtbot: QtBot, document: Document, cards: list[str]) -> DeckImportWizard:
    card_db = document.card_db
    fill_card_database_with_json_cards(qtbot, card_db, cards)
    language_model = QStringListModel(card_db.get_all_languages(), parent=None)
    wizard = DeckImportWizard(document, language_model)
    qtbot.add_widget(wizard)
    with qtbot.wait_exposed(wizard):
        wizard.show()
    return wizard


def test_going_back_to_textual_deck_list_resets_parsed_cards_model(qtbot: QtBot, document: Document):
    wizard = create_and_show_wizard(qtbot, document, ["regular_english_card"])
    deck_list = "1 Fury Sliver"
    _input_deck_list(qtbot, wizard, deck_list)
    _move_wizard_forward(qtbot, wizard)
    _select_magic_online_parser(qtbot, wizard)
    _move_wizard_forward(qtbot, wizard)
    list_model = wizard.summary_page.card_list
    _validate_model_content(list_model)
    list_model.clear()
    _move_wizard_backward(qtbot, wizard)
    _move_wizard_forward(qtbot, wizard)
    assert_that(wizard.summary_page.card_list, is_(same_instance(list_model)))
    _validate_model_content(list_model)


@pytest.mark.parametrize("removal_settings, expected_cards", [
    ({"remove-snow-basics": "False", "remove-basic-wastes": "False"}, ["Snow-Covered Forest", "Wastes"]),
    ({"remove-snow-basics": "True", "remove-basic-wastes": "False"}, ["Wastes"]),
    ({"remove-snow-basics": "False", "remove-basic-wastes": "True"}, ["Snow-Covered Forest"]),
    ({"remove-snow-basics": "True", "remove-basic-wastes": "True"}, []),

])
def test_remove_basic_lands_button_works(
        qtbot: QtBot, document: Document,
        removal_settings: dict[str, str], expected_cards: list[str]):
    deck_list = "\n".join(("1 Forest", "1 Snow-Covered Forest", "1 Wastes"))
    wizard = create_and_show_wizard(
        qtbot, document, ["english_basic_Forest", "english_basic_Snow_Forest", "english_basic_Wastes"]
    )
    _input_deck_list(qtbot, wizard, deck_list)
    _move_wizard_forward(qtbot, wizard)
    _select_magic_arena_parser(qtbot, wizard)
    _move_wizard_forward(qtbot, wizard)
    list_model = wizard.summary_page.card_list
    assert_that(list_model.rowCount(), is_(3))
    with unittest.mock.patch.dict(mtg_proxy_printer.settings.settings["decklist-import"], removal_settings):
        wizard.button(WizardButton.CustomButton1).click()
    assert_that(
        wizard.button(WizardButton.CustomButton1).isEnabled(),
        is_(False)
    )
    card_names_in_model: list[str] = [
        list_model.data(list_model.index(row, CardListColumns.CardName))
        for row in range(list_model.rowCount())
    ]
    assert_that(card_names_in_model, contains_exactly(*expected_cards))


def test_remove_selected_cards_works(qtbot: QtBot, document: Document):
    deck_list = "\n".join(("1 Forest", "1 Snow-Covered Forest", "1 Wastes"))
    wizard = create_and_show_wizard(
        qtbot, document, ["english_basic_Forest", "english_basic_Snow_Forest", "english_basic_Wastes"]
    )
    _input_deck_list(qtbot, wizard, deck_list)
    _move_wizard_forward(qtbot, wizard)
    _select_magic_arena_parser(qtbot, wizard)
    _move_wizard_forward(qtbot, wizard)
    list_model = wizard.summary_page.card_list
    assert_that(list_model.rowCount(), is_(3))
    assert_that(wizard.button(wizard.WizardButton.CustomButton2).isEnabled(), is_(False))
    # Select the Forest for removal
    wizard.summary_page.ui.parsed_cards_table.selectRow(0)
    assert_that(wizard.button(wizard.WizardButton.CustomButton2).isEnabled(), is_(True))
    # Remove it
    wizard.button(wizard.WizardButton.CustomButton2).click()
    # Verify effects: Button is disabled and the Forest is no longer present in the parsed cards
    assert_that(wizard.button(wizard.WizardButton.CustomButton2).isEnabled(), is_(False))
    card_names_in_model: list[str] = [
        list_model.data(list_model.index(row, CardListColumns.CardName))
        for row in range(list_model.rowCount())
    ]
    assert_that(card_names_in_model, contains_exactly("Snow-Covered Forest", "Wastes"))


def _move_wizard_forward(qtbot: QtBot, wizard: QWizard):
    with qtbot.wait_signal(wizard.currentIdChanged, timeout=1000):
        wizard.next()


def _move_wizard_backward(qtbot: QtBot, wizard: QWizard):
    with qtbot.wait_signal(wizard.currentIdChanged, timeout=1000):
        wizard.back()


def _select_magic_online_parser(qtbot: QtBot, wizard: DeckImportWizard):
    page = wizard.select_deck_parser_page
    with qtbot.wait_signal(page.completeChanged, timeout=1000):
        cb: QCheckBox = page.ui.select_parser_mtg_online
        cb.click()
    assert_that(page.ui.select_parser_mtg_online.isChecked())
    assert_that(page.complete, is_(True))
    assert_that(page.isComplete())
    assert_that(page.parser_creator, is_(page._create_mtg_online_parser))
    assert_that(wizard.validateCurrentPage(), is_(True))
    assert_that(page.selected_parser, is_(instance_of(MTGOnlineParser)))


def _select_magic_arena_parser(qtbot: QtBot, wizard: DeckImportWizard):
    page = wizard.select_deck_parser_page
    cb: QCheckBox = page.ui.select_parser_mtg_arena
    with qtbot.wait_signal(cb.clicked, timeout=1000):
        cb.click()
    assert_that(page.ui.select_parser_mtg_arena.isChecked())
    assert_that(page.complete, is_(True))
    assert_that(page.isComplete())
    assert_that(page.parser_creator, is_(page._create_mtg_arena_parser))
    assert_that(wizard.validateCurrentPage(), is_(True))
    assert_that(page.selected_parser, is_(instance_of(MTGArenaParser)))


def _select_generic_re_parser(qtbot: QtBot, wizard: DeckImportWizard, re: str, is_identifying_re: bool):
    page = wizard.select_deck_parser_page
    cb: QCheckBox = page.ui.select_parser_custom_re
    le: QLineEdit = page.ui.custom_re_input
    with qtbot.wait_signal(le.textChanged, timeout=5000):
        cb.click()
        le.setText(re)
    assert_that(page.ui.select_parser_custom_re.isChecked())
    assert_that(le.text(), is_(equal_to(re)))
    assert_that(page.complete, is_(is_identifying_re))
    assert_that(page.isComplete(), is_(is_identifying_re))
    assert_that(page.parser_creator, is_(page._create_generic_re_parser))
    assert_that(wizard.validateCurrentPage(), is_(is_identifying_re))
    assert_that(page.selected_parser, is_(instance_of(GenericRegularExpressionDeckParser)))
    assert_that(wizard.field("custom_re"), is_(equal_to(re)))
    assert_that(page.selected_parser.parser.pattern, is_(equal_to(re)))
    assert_that(wizard.button(WizardButton.NextButton).isEnabled(), is_(is_identifying_re))


def _input_deck_list(qtbot: QtBot, wizard: DeckImportWizard, deck_list: str, *, enable_print_guessing: bool = False):
    page = wizard.load_list_page
    with qtbot.wait_signal(page.ui.deck_list.textChanged, timeout=1000):
        page.ui.deck_list.setPlainText(deck_list)
    assert_that(wizard.field("deck_list"), is_(equal_to(deck_list)))
    assert_that(page.isComplete())
    cb: QCheckBox = page.ui.print_guessing_enable
    if enable_print_guessing and not cb.isChecked():
        with qtbot.wait_signal(cb.stateChanged, timeout=1000):
            cb.click()
        assert_that(cb.isChecked())


def _validate_model_content(list_model: CardListModel):
    assert_that(list_model.rowCount(), is_(equal_to(1)))
    assert_that(list_model.rows, has_length(1))
    assert_that(list_model.rows[0], has_properties(copies=1, card=has_properties({
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
            "https://cards.scryfall.io/png/front/0/0/"
            "0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979"),
        "image_file": is_(none()),
    })))


class CardListReceiver(QObject):
    def __init__(self, parent: QObject = None):
        super(CardListReceiver, self).__init__(parent)
        self.deck: CardCounter = Counter()

    def on_import_action_received(self, action: ActionImportDeckList):
        self.deck = action.cards


def test_selecting_different_printing_works(qtbot: QtBot, document: Document):
    wizard = create_and_show_wizard(qtbot, document, ["regular_english_card", "regular_english_card_reprint"])
    deck_list = "2 Fury Sliver (TSP) 157"
    _input_deck_list(qtbot, wizard, deck_list)
    _move_wizard_forward(qtbot, wizard)
    _select_magic_arena_parser(qtbot, wizard)
    _move_wizard_forward(qtbot, wizard)
    table_view: QTableView = wizard.summary_page.ui.parsed_cards_table
    cell_position = QPoint(
        table_view.columnViewportPosition(CardListColumns.Set) + 5,
        table_view.rowViewportPosition(0) + 5
    )
    # Select cell
    QTest.mouseClick(table_view.viewport(), MouseButton.LeftButton, pos=cell_position)
    # Enter edit mode
    QTest.mouseDClick(table_view.viewport(), MouseButton.LeftButton, pos=cell_position)
    # Now get the editor and select a different set to get another printing
    editor: QComboBox = table_view.viewport().childAt(cell_position)
    assert_that(editor, is_(instance_of(QComboBox)))
    # Select the second entry in the editor’s item list
    QTest.keyClick(editor, Key.Key_Down)
    with qtbot.wait_signal(table_view.model().dataChanged):
        # Wait until the editor saved the data in the model
        QTest.keyClick(editor, Key.Key_Enter)
    # Now accept the dialog and capture the emitted deck
    deck_receiver = CardListReceiver()
    wizard.request_action.connect(deck_receiver.on_import_action_received)
    with qtbot.wait_signal(wizard.request_action, timeout=1000):
        QTest.keyClick(wizard, Key.Key_Enter)
    assert_that(deck_receiver.deck, has_length(1))
    assert_that(
        deck_receiver.deck, has_entry(has_properties({
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
                "https://cards.scryfall.io/png/front/a/8/"
                "a8a64329-09fc-4e0d-b7d1-378635f2801a.png?1619396979"),
            "image_file": is_(none()),
        }), 2)
    )


def test_complete_button_disabled_if_zero_cards_identified(qtbot: QtBot, document: Document):
    """
    If there are zero identified cards, the Finish button must be disabled, so that the wizard can’t be completed.
    """
    wizard = create_and_show_wizard(qtbot, document, ["regular_english_card"])
    deck_list = "Invalid deck list"
    _input_deck_list(qtbot, wizard, deck_list)
    _move_wizard_forward(qtbot, wizard)
    _select_magic_arena_parser(qtbot, wizard)
    _move_wizard_forward(qtbot, wizard)
    table_view: QTableView = wizard.summary_page.ui.parsed_cards_table
    assert_that(table_view.model().rowCount(), is_(0), "Setup failed: Parsed deck model must be empty!")
    assert_that(wizard.summary_page.isComplete(), is_(False))
    assert_that(wizard.button(WizardButton.FinishButton).isEnabled(), is_(False))


def test_complete_button_enabled_if_one_card_identified(qtbot: QtBot, document: Document):
    """
    If there is at least one identified card, the Finish button must be enabled.
    """
    wizard = create_and_show_wizard(qtbot, document, ["regular_english_card"])
    deck_list = "1 Fury Sliver (TSP) 157"
    _input_deck_list(qtbot, wizard, deck_list)
    _move_wizard_forward(qtbot, wizard)
    _select_magic_arena_parser(qtbot, wizard)
    _move_wizard_forward(qtbot, wizard)
    table_view: QTableView = wizard.summary_page.ui.parsed_cards_table
    assert_that(table_view.model().rowCount(), is_(1), "Setup failed: Parsed deck model must not be empty!")
    assert_that(wizard.summary_page.isComplete(), is_(True))
    assert_that(wizard.button(WizardButton.FinishButton).isEnabled(), is_(True))


def test_complete_state_updates_when_deck_list_updated_to_contain_cards(qtbot: QtBot, document: Document):
    """
    Test that going back and changing the deck list updates the isComplete()
    value of the SummaryPage and the Finish button enabled state.
    """
    wizard = create_and_show_wizard(qtbot, document, ["regular_english_card"])
    invalid_deck_list = "Invalid deck list"
    valid_deck_list = "1 Fury Sliver (TSP) 157"
    _input_deck_list(qtbot, wizard, invalid_deck_list)
    _move_wizard_forward(qtbot, wizard)
    _select_magic_arena_parser(qtbot, wizard)
    _move_wizard_forward(qtbot, wizard)
    table_view: QTableView = wizard.summary_page.ui.parsed_cards_table
    assert_that(table_view.model().rowCount(), is_(0), "Setup failed: Parsed deck model must be empty!")
    assert_that(wizard.summary_page.isComplete(), is_(False))
    assert_that(wizard.button(WizardButton.FinishButton).isEnabled(), is_(False))

    # Transition from invalid to valid state
    _move_wizard_backward(qtbot, wizard)
    _move_wizard_backward(qtbot, wizard)
    _input_deck_list(qtbot, wizard, valid_deck_list)
    _move_wizard_forward(qtbot, wizard)
    _select_magic_arena_parser(qtbot, wizard)
    _move_wizard_forward(qtbot, wizard)
    assert_that(table_view.model().rowCount(), is_(1), "Setup failed: Parsed deck model must not be empty!")
    assert_that(wizard.summary_page.isComplete(), is_(True))
    assert_that(wizard.button(WizardButton.FinishButton).isEnabled(), is_(True))

    # Transition from valid to invalid state
    _move_wizard_backward(qtbot, wizard)
    _move_wizard_backward(qtbot, wizard)
    _input_deck_list(qtbot, wizard, invalid_deck_list)
    _move_wizard_forward(qtbot, wizard)
    _select_magic_arena_parser(qtbot, wizard)
    _move_wizard_forward(qtbot, wizard)
    assert_that(table_view.model().rowCount(), is_(0), "Setup failed: Parsed deck model must be empty!")
    assert_that(wizard.summary_page.isComplete(), is_(False))
    assert_that(wizard.button(WizardButton.FinishButton).isEnabled(), is_(False))


def test_custom_re_parser_works(qtbot: QtBot, document: Document):
    valid_re = r"(?P<name>.+)"
    deck_list = "Fury Sliver"
    wizard = create_and_show_wizard(qtbot, document, ["regular_english_card", "regular_english_card_reprint"])
    _input_deck_list(qtbot, wizard, deck_list, enable_print_guessing=True)
    _move_wizard_forward(qtbot, wizard)
    _select_generic_re_parser(qtbot, wizard, valid_re, True)
    _move_wizard_forward(qtbot, wizard)
    table_view: QTableView = wizard.summary_page.ui.parsed_cards_table
    assert_that(table_view.model().rowCount(), is_(1), "Setup failed: Parsed deck model must not be empty!")
    assert_that(wizard.summary_page.isComplete(), is_(True))
    assert_that(wizard.button(WizardButton.FinishButton).isEnabled(), is_(True))


def generate_test_cases_for_test_custom_re_parser_accepts_valid_re():
    def flattened_powerset_without_empty(iterable: typing.FrozenSet[typing.FrozenSet[str]]):
        """Based on the powerset recipe in the itertools documentation"""
        powerset_without_empty = itertools.chain.from_iterable(
            itertools.combinations(iterable, r)
            for r in range(1, len(iterable) + 1))
        return (frozenset.union(*groups) for groups in powerset_without_empty)

    def generate_re(groups: typing.FrozenSet[str]):
        return " ".join(fr"(?P<{group_name}>.+)" for group_name in groups)

    for groups in flattened_powerset_without_empty(GenericRegularExpressionDeckParser.IDENTIFYING_GROUP_COMBINATIONS):
        yield generate_re(groups)


@pytest.mark.parametrize("valid_re", generate_test_cases_for_test_custom_re_parser_accepts_valid_re())
def test_custom_re_parser_accepts_valid_re(qtbot: QtBot, document: Document, valid_re: str):
    wizard = create_and_show_wizard(qtbot, document, ["regular_english_card", "regular_english_card_reprint"])
    deck_list = "Fury Sliver"
    _input_deck_list(qtbot, wizard, deck_list, enable_print_guessing=True)
    _move_wizard_forward(qtbot, wizard)
    _select_generic_re_parser(qtbot, wizard, valid_re, True)


@pytest.mark.parametrize("invalid_re", [
    "No group",
    r"(?P<count>.+)",
    r"(?P<collector_number>.+)",
    r"(?P<set_code>.+)",
    r"(?P<count>.+) (?P<collector_number>.+)",
    r"(?P<count>.+) (?P<set_code>.+)",
])
def test_custom_re_parser_declines_non_identifying_re(qtbot: QtBot, document: Document, invalid_re: str):
    wizard = create_and_show_wizard(qtbot, document, ["regular_english_card", "regular_english_card_reprint"])
    deck_list = "Fury Sliver"
    _input_deck_list(qtbot, wizard, deck_list, enable_print_guessing=True)
    _move_wizard_forward(qtbot, wizard)
    _select_generic_re_parser(qtbot, wizard, invalid_re, False)
