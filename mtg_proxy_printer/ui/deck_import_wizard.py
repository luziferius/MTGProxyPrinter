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

import collections
import pathlib
import re
import typing

from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtGui import QValidator, QIcon
from PyQt5.QtWidgets import QWizard, QFileDialog, QPlainTextEdit, QMessageBox, QLineEdit, QTableView, QPushButton
import mtg_proxy_printer.settings
from mtg_proxy_printer.decklist_parser import re_parsers, common, csv_parsers
from mtg_proxy_printer.model.carddb import CardDatabase, Card
from mtg_proxy_printer.model.imagedb import ImageDatabase
from mtg_proxy_printer.model.document import Page
from mtg_proxy_printer.ui.common import inherits_from_ui_file_with_name
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


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
        except RecursionError:
            # An input like the evaluated result of the expression '('*10000+'z'+')'*10000  will throw a RecursionError.
            # (Depending on the recursion limit)
            # Deem this invalid, as it cannot be parsed at all and allowing the user to append more will not help
            return QValidator.Invalid, input_string, pos
        else:
            return QValidator.Acceptable, input_string, pos


class LoadListPage(*inherits_from_ui_file_with_name("deck_import_wizard/load_list_page")):
    def __init__(self, *args, **kwargs):
        super(LoadListPage, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.registerField("deck_list*", self.deck_list, "plainText", self.deck_list.textChanged)
        self.registerField("print-guessing-enable", self.print_guessing_enable)
        self.registerField("print-guessing-prefer-already-downloaded", self.print_guessing_prefer_already_downloaded)
        logger.info(f"Created {self.__class__.__name__} instance.")

    def initializePage(self) -> None:
        super(LoadListPage, self).initializePage()
        options = mtg_proxy_printer.settings.settings["print-guessing"]
        self.print_guessing_enable.setChecked(options.getboolean("enable-guessing"))
        self.print_guessing_prefer_already_downloaded.setChecked(options.getboolean("prefer-already-downloaded"))
        parser: common.ParserBase = self.field("selected_parser")
        if parser.requires_print_guessing:
            logger.debug("Force-enabling print guessing, because the chosen parser requires it.")
            self.print_guessing_enable.setChecked(True)
            self.print_guessing_enable.setEnabled(False)

    def cleanupPage(self):
        super(LoadListPage, self).cleanupPage()
        self.print_guessing_enable.setEnabled(True)
        self.print_guessing_enable.setChecked(False)
        self.print_guessing_prefer_already_downloaded.setChecked(False)

    @pyqtSlot()
    def on_deck_list_browse_button_clicked(self):
        logger.info("User selects a deck list from disk")
        self.deck_list: QPlainTextEdit
        if not self.deck_list.toPlainText() \
                or QMessageBox.question(
                        self, "Overwrite existing deck list?",
                        "Selecting a file will overwrite the existing deck list. Continue?",
                        QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            logger.debug("User opted to replace the current, non-empty deck list with the file content")
            # Ignore the used file type filter (second return value)
            selected_file, _ = QFileDialog.getOpenFileName(self, "Select deck file")
            if selected_file and (file_path := pathlib.Path(selected_file)).is_file():
                logger.debug("Selected file is valid, loading it from disk, replacing the current deck list")
                self.deck_list.clear()
                self.deck_list.setPlainText(file_path.read_text())


class SelectDeckParserPage(*inherits_from_ui_file_with_name("deck_import_wizard/select_deck_parser_page")):
    """
    This page allows the user to chose which format their deck list uses.
    The result will be used to chose an appropriate parser implementation.
    """
    # Implementation note: Each QRadioButton has a signal/slot connection to the isComplete() slot method defined
    # in the loaded UI file. This is required to properly update the "complete" attribute on user input
    # and emit the completeChanged() Qt Signal whenever that attribute changes.
    # When adding new radio buttons, also add the appropriate connection. Otherwise the “Next” button will stay
    # disabled when the user selects it.

    def __init__(self, card_db: CardDatabase, image_db: ImageDatabase, *args, **kwargs):
        super(SelectDeckParserPage, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.card_db = card_db
        self.image_db = image_db
        self.custom_re_input: QLineEdit
        self.custom_re_input.setValidator(IsRegularExpressionValidator(self))
        self.complete = False
        self.registerField("custom_re", self.custom_re_input)
        self.registerField("selected_parser", self)
        logger.info(f"Created {self.__class__.__name__} instance.")

    @pyqtSlot()
    def isComplete(self) -> bool:
        acceptable = any((
            self.select_parser_mtg_arena.isChecked(),
            self.select_parser_mtg_online.isChecked(),
            self.select_parser_xmage.isChecked(),
            # self.select_parser_scryfall_csv.isChecked(),  # TODO
            # self.select_parser_tappedout_csv.isChecked(),  # TODO
        )) or all((
                self.select_parser_custom_re.isChecked(),
                self.custom_re_input.hasAcceptableInput()
        ))
        if acceptable != self.complete:
            self.complete = acceptable
            self.completeChanged.emit()
        return acceptable

    def get_parser(self):
        if self.select_parser_mtg_arena.isChecked():
            return re_parsers.MTGArenaParser(self.card_db, self.image_db)
        elif self.select_parser_mtg_online.isChecked():
            return re_parsers.MTGOnlineParser(self.card_db, self.image_db)
        elif self.select_parser_xmage.isChecked():
            return re_parsers.XMageParser(self.card_db, self.image_db)
        elif self.select_parser_scryfall_csv.isChecked():
            return csv_parsers.ScryfallCSVParser(self.card_db, self.image_db)
        elif self.select_parser_custom_re.isChecked():
            return re_parsers.GenericRegularExpressionDeckParser(
                self.card_db, self.image_db, self.field("custom_re")
            )
        raise RuntimeError("Requested parser on invalid page state")

    def validatePage(self) -> bool:
        # TODO: Despite working, this emits a warning “QWizard::setField: Couldn't write to property ''”.
        #  Research the cause and try to fix this.
        self.setField("selected_parser", self.get_parser())
        logger.info(f"User selected parser: {self.field('selected_parser').__class__.__name__}")
        return super(SelectDeckParserPage, self).validatePage()


class SummaryPage(*inherits_from_ui_file_with_name("deck_import_wizard/parser_result_page")):
    def __init__(self, *args, **kwargs):
        super(SummaryPage, self).__init__(*args, **kwargs)
        self.parsed_cards_table: QTableView
        self.setupUi(self)
        self.setCommitPage(True)
        self.page = Page(self)
        self.parsed_cards_table.setModel(self.page)
        self.parsed_cards_table.setColumnHidden(4, True)
        self.registerField("parsed_deck", self)
        self.registerField("should_replace_document", self.should_replace_document)
        logger.info(f"Created {self.__class__.__name__} instance.")

    def initializePage(self) -> None:
        super(SummaryPage, self).initializePage()
        self.parsed_cards_table: QTableView
        parser: common.ParserBase = self.field("selected_parser")
        parsed_deck, unparsed_lines = parser.parse_deck(
            self.field("deck_list"),
            self.field("print-guessing-enable"),
            self.field("print-guessing-prefer-already-downloaded")
        )
        self.setField("parsed_deck", parsed_deck)
        self.unparsed_lines_text: QPlainTextEdit
        for card, count in parsed_deck.items():
            self.page.add_card(card, count)
        self.unparsed_lines_text.setPlainText("\n".join(unparsed_lines))

    def cleanupPage(self):
        self.page.clear()


class DeckImportWizard(QWizard):
    deck_added = pyqtSignal(collections.Counter)
    clear_document = pyqtSignal()

    def __init__(self, card_db: CardDatabase, image_db: ImageDatabase, *args, **kwargs):
        super(DeckImportWizard, self).__init__(*args, **kwargs)
        self.card_db = card_db
        self.addPage(SelectDeckParserPage(card_db, image_db, self))
        self.addPage(LoadListPage(self))
        self.addPage(SummaryPage(self))
        self.setWindowIcon(QIcon.fromTheme("document-import"))
        self.setBaseSize(800, 600)
        self.setWindowTitle("Import a deck list")
        logger.info(f"Created {self.__class__.__name__} instance.")

    def accept(self):
        logger.info("User finished the import wizard, performing the requested actions")
        super(DeckImportWizard, self).accept()
        if self.field("should_replace_document"):
            logger.info("User chose to replace the current document content, clearing it")
            self.clear_document.emit()
        deck: typing.Counter[Card] = self.field("parsed_deck")
        # len(deck) only counts keys, so use sum(deck.values()) to count duplicates
        logger.info(f"User loaded a deck list with {sum(deck.values())} cards, adding these to the document")
        self.deck_added.emit(deck)
