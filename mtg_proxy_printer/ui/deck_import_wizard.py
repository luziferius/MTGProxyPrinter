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

import re
import typing

from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtGui import QValidator
from PyQt5.QtWidgets import QWizard, QFileDialog, QPlainTextEdit, QMessageBox, QLineEdit, QTableView

from mtg_proxy_printer.decklist_parser import re_parsers
from mtg_proxy_printer.model.carddb import CardDatabase, Card
from mtg_proxy_printer.model.document import Page
from mtg_proxy_printer.ui.common import inherits_from_ui_file_with_name


class IsRegularExpressionValidator(QValidator):
    """
    Validator used to check if the custom RE used for the "Custom RE parser" option is a valid RE.
    """
    def validate(self, input_string: str, pos: int) -> typing.Tuple[QValidator.State, str, int]:
        if not input_string:
            # Even though an empty RE is technically valid, it can never be used to parse groups,
            # so consider empty REs as Intermediate inputs.
            return QValidator.Intermediate, input_string, pos
        try:
            re.compile(input_string)
        except re.error:
            return QValidator.Intermediate, input_string, pos
        else:
            return QValidator.Acceptable, input_string, pos


class LoadListPage(*inherits_from_ui_file_with_name("load_list_page")):
    def __init__(self, *args, **kwargs):
        super(LoadListPage, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.registerField("deck_list*", self.deck_list, "plainText", self.deck_list.textChanged)

    @pyqtSlot()
    def on_deck_list_browse_button_clicked(self):
        self.deck_list: QPlainTextEdit
        if not self.deck_list.toPlainText() \
                or QMessageBox.question(
                        self, "Overwrite existing deck list?",
                        "Selecting a file will overwrite the existing deck list. Continue?",
                        QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            # Ignore the used file type filter (second return value)
            selected_file, _ = QFileDialog.getOpenFileName(self, "Select deck file")
            if selected_file:
                self.deck_list.clear()
                with open(selected_file, "rt") as opened_file:
                    self.deck_list.setPlainText(opened_file.read())


class SelectDeckParserPage(*inherits_from_ui_file_with_name("select_deck_parser_page")):
    """
    This page allows the user to chose which format their deck list uses.
    The result will be used to chose an appropriate parser implementation.
    """
    # Implementation note: Each QRadioButton has a signal/slot connection to the isComplete() slot method defined
    # in the loaded UI file. This is required to properly update the "complete" attribute on user input
    # and emit the completeChanged() Qt Signal whenever that attribute changes.
    # When adding new radio buttons, also add the appropriate connection. Otherwise the “Next” button will stay
    # disabled when the user selects it.

    def __init__(self, card_db: CardDatabase, *args, **kwargs):
        super(SelectDeckParserPage, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.card_db = card_db
        self.custom_re_input: QLineEdit
        self.custom_re_input.setValidator(IsRegularExpressionValidator(self))
        self.custom_re_input.textChanged.connect(self.isComplete)
        self.complete = False
        self.parser = None
        self.registerField("custom_re", self.custom_re_input)
        self.registerField("selected_parser", self, "parser")

    @pyqtSlot()
    def isComplete(self) -> bool:
        result = any((
            self.select_parser_mtg_arena.isChecked(),
            self.select_parser_mtg_online.isChecked(),
            self.select_parser_xmage.isChecked(),
            # self.select_parser_scryfall_csv.isChecked(),  # TODO
        )) or all((
                self.select_parser_custom_re.isChecked(),
                self.custom_re_input.hasAcceptableInput()
        ))
        if result != self.complete:
            self.complete = result
            self.completeChanged.emit()
        return result

    def get_parser(self):
        if self.select_parser_mtg_arena.isChecked():
            return re_parsers.MTGArenaParser(self.card_db)
        elif self.select_parser_mtg_online.isChecked():
            return re_parsers.MTGOnlineParser(self.card_db)
        elif self.select_parser_xmage.isChecked():
            return re_parsers.XMageParser(self.card_db)
        elif self.select_parser_scryfall_csv.isChecked():
            pass
        elif self.select_parser_custom_re.isChecked():
            return re_parsers.GenericRegularExpressionDeckParser(
                self.card_db, self.field("custom_re")
            )
        raise RuntimeError("Requested parser on invalid page state")

    def validatePage(self) -> bool:
        # TODO: Despite working, this emits a warning “QWizard::setField: Couldn't write to property 'parser'”.
        #  Research the cause and try to fix this.
        self.setField("selected_parser", self.get_parser())
        return super(SelectDeckParserPage, self).validatePage()


class SummaryPage(*inherits_from_ui_file_with_name("parser_result_page")):
    def __init__(self, *args, **kwargs):
        super(SummaryPage, self).__init__(*args, **kwargs)
        self.parsed_cards_table: QTableView
        self.setupUi(self)
        self.setCommitPage(True)
        self.page = Page(self)
        self.parsed_cards_table.setModel(self.page)
        self.parsed_cards_table.setColumnHidden(4, True)
        self.parsed_deck = None
        self.registerField("parsed_deck", self, "parsed_deck")
        self.registerField("should_replace_document", self.should_replace_document)

    def initializePage(self) -> None:
        super(SummaryPage, self).initializePage()
        self.parsed_cards_table: QTableView
        parser: re_parsers.GenericRegularExpressionDeckParser = self.field("selected_parser")
        self.parsed_deck, unparsed_lines = parser.parse_deck(self.field("deck_list"))
        self.setField("parsed_deck", self.parsed_deck)
        self.unparsed_lines_text: QPlainTextEdit
        for card, count in self.parsed_deck.items():
            self.page.add_card(card, count)
        self.unparsed_lines_text.setPlainText("\n".join(unparsed_lines))

    def cleanupPage(self):
        self.page.clear()
        self.parsed_deck = None


class DeckImportWizard(QWizard):
    card_added = pyqtSignal(Card, int)
    clear_document = pyqtSignal()

    def __init__(self, card_db: CardDatabase, *args, **kwargs):
        super(DeckImportWizard, self).__init__(*args, **kwargs)
        self.card_db = card_db
        self.addPage(SelectDeckParserPage(card_db))
        self.addPage(LoadListPage())
        self.addPage(SummaryPage())
        self.setWindowTitle("Import a deck list")

    def accept(self):
        super(DeckImportWizard, self).accept()
        if self.field("should_replace_document"):
            self.clear_document.emit()
        deck: typing.Counter[Card] = self.field("parsed_deck")
        for card, count in deck.items():
            self.card_added.emit(card, count)

