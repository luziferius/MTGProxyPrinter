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

from PyQt5.QtCore import pyqtSlot, pyqtSignal, pyqtProperty, QStringListModel
from PyQt5.QtGui import QValidator, QIcon
from PyQt5.QtWidgets import QWizard, QFileDialog, QPlainTextEdit, QMessageBox, QLineEdit, QTableView, QComboBox
import mtg_proxy_printer.settings
from mtg_proxy_printer.decklist_parser import re_parsers, common, csv_parsers
from mtg_proxy_printer.model.carddb import CardDatabase, Card
from mtg_proxy_printer.model.imagedb import ImageDatabase
from mtg_proxy_printer.model.card_list import CardListModel, PageColumns
from mtg_proxy_printer.ui.common import inherits_from_ui_file_with_name
from mtg_proxy_printer.ui.item_delegates import ComboBoxItemDelegate
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger
__all__ = [
    "DeckImportWizard",
]


class IsRegularExpressionValidator(QValidator):
    """
    Validator used to check if the custom RE used for the "Custom RE parser" option is a valid RE.
    """

    has_named_groups_re = re.compile(
        rf"\(\?P<({'|'.join(re_parsers.GenericRegularExpressionDeckParser.SUPPORTED_GROUP_NAMES)})>.+?\)")

    def validate(self, input_string: str, pos: int) -> typing.Tuple[QValidator.State, str, int]:
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
            return self._validate_content(input_string), input_string, pos

    def _validate_content(self, input_string: str):
        """
        Validates the user supplied RE. Currently, this method only checks, if the user content contains a valid
        named group matching any supported group name.
        """
        if self.has_named_groups_re.search(input_string):
            return QValidator.Acceptable
        else:
            return QValidator.Intermediate


class LoadListPage(*inherits_from_ui_file_with_name("deck_import_wizard/load_list_page")):

    def __init__(self, language_model: QStringListModel, *args, **kwargs):
        super(LoadListPage, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.translate_deck_list_target_language.setModel(language_model)
        self.registerField("deck_list*", self.deck_list, "plainText", self.deck_list.textChanged)
        self.registerField("print-guessing-enable", self.print_guessing_enable)
        self.registerField("print-guessing-prefer-already-downloaded", self.print_guessing_prefer_already_downloaded)
        self.registerField("translate-deck-list-enable", self.translate_deck_list_enable)
        self.registerField(
            "translate-deck-list-target-language", self.translate_deck_list_target_language,
            "currentText", self.translate_deck_list_target_language.currentTextChanged
        )
        logger.info(f"Created {self.__class__.__name__} instance.")

    def initializePage(self) -> None:
        super(LoadListPage, self).initializePage()
        self.translate_deck_list_target_language: QComboBox
        language_model: QStringListModel = self.translate_deck_list_target_language.model()
        preferred_language = mtg_proxy_printer.settings.settings["images"]["preferred-language"]
        preferred_language_index = language_model.stringList().index(preferred_language)
        self.translate_deck_list_target_language.setCurrentIndex(preferred_language_index)
        options = mtg_proxy_printer.settings.settings["print-guessing"]
        self.print_guessing_enable.setChecked(options.getboolean("enable-guessing"))
        self.print_guessing_prefer_already_downloaded.setChecked(options.getboolean("prefer-already-downloaded"))
        self.translate_deck_list_enable.setChecked(options.getboolean("always-translate-deck-lists"))
        parser: common.ParserBase = self.field("selected_parser")
        if parser.requires_print_guessing:
            logger.debug("Force-enabling print guessing, because the chosen parser requires it.")
            self.print_guessing_enable.setChecked(True)
            self.print_guessing_enable.setEnabled(False)
        logger.debug(f"Initialized {self.__class__.__name__}")

    def cleanupPage(self):
        super(LoadListPage, self).cleanupPage()
        self.translate_deck_list_enable.setChecked(False)
        self.print_guessing_enable.setEnabled(True)
        self.print_guessing_enable.setChecked(False)
        self.print_guessing_prefer_already_downloaded.setChecked(False)
        logger.debug(f"Cleaned up {self.__class__.__name__}")

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

    selected_parser_changed = pyqtSignal(common.ParserBase)

    @pyqtProperty(common.ParserBase, notify=selected_parser_changed)
    def selected_parser(self):
        pass

    @selected_parser.setter
    def selected_parser(self, parser: common.ParserBase):
        logger.debug(f"Parser set to {parser.__class__.__name__}")
        self._selected_parser = parser
        self.selected_parser_changed.emit(parser)
        self.setField("selected_parser", parser)

    @selected_parser.getter
    def selected_parser(self) -> common.ParserBase:
        logger.debug(f"Reading selected parser {self._selected_parser.__class__.__name__}")
        return self._selected_parser

    def __init__(self, card_db: CardDatabase, image_db: ImageDatabase, *args, **kwargs):
        super(SelectDeckParserPage, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.card_db = card_db
        self.image_db = image_db
        self._selected_parser = None
        self.custom_re_input: QLineEdit
        self.custom_re_input.setToolTip(
            f"Enter a Regular Expression containing at least one supported, named group.\n\n"
            f"Supported named groups are: "
            f"{', '.join(sorted(re_parsers.GenericRegularExpressionDeckParser.SUPPORTED_GROUP_NAMES))}\n\n"
            f"See the 'What’s this?' (?-Button) help for details."
        )
        self.custom_re_input.setValidator(IsRegularExpressionValidator(self))
        self.complete = False
        self.registerField("custom_re", self.custom_re_input)
        self.registerField("selected_parser", self)
        self.select_parser_mtg_arena.pressed.connect(
            lambda: setattr(self, "selected_parser", re_parsers.MTGArenaParser(self.card_db, self.image_db, self))
        )
        self.select_parser_mtg_online.pressed.connect(
            lambda: setattr(self, "selected_parser", re_parsers.MTGOnlineParser(self.card_db, self.image_db, self))
        )
        self.select_parser_xmage.pressed.connect(
            lambda: setattr(self, "selected_parser", re_parsers.XMageParser(self.card_db, self.image_db, self))
        )
        self.select_parser_scryfall_csv.pressed.connect(
            lambda: setattr(self, "selected_parser", csv_parsers.ScryfallCSVParser(self.card_db, self.image_db, self))
        )
        self.select_parser_tappedout_csv.pressed.connect(
            lambda: setattr(self, "selected_parser", csv_parsers.TappedOutCSVParser(
                self.card_db, self.image_db,
                self.tappedout_include_maybe_board.isChecked(), self.tappedout_include_acquire_board.isChecked(), self
            ))
        )
        self.select_parser_custom_re.pressed.connect(
            lambda: setattr(self, "selected_parser", re_parsers.GenericRegularExpressionDeckParser(
                self.card_db, self.image_db, self.field("custom_re"), self
            ))
        )
        logger.info(f"Created {self.__class__.__name__} instance.")

    @pyqtSlot()
    def isComplete(self) -> bool:
        acceptable = any((
            self.select_parser_mtg_arena.isChecked(),
            self.select_parser_mtg_online.isChecked(),
            self.select_parser_xmage.isChecked(),
            self.select_parser_scryfall_csv.isChecked(),
            self.select_parser_tappedout_csv.isChecked(),
        )) or all((
                self.select_parser_custom_re.isChecked(),
                self.custom_re_input.hasAcceptableInput()
        ))
        if acceptable != self.complete:
            self.complete = acceptable
            self.completeChanged.emit()
        return acceptable


class SummaryPage(*inherits_from_ui_file_with_name("deck_import_wizard/parser_result_page")):
    def __init__(self, card_db: CardDatabase, *args, **kwargs):
        super(SummaryPage, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setCommitPage(True)
        self.card_list = CardListModel(card_db, self)
        self.combo_box_delegate = self._setup_parsed_cards_table()
        self.registerField("parsed_deck", self)
        self.registerField("should_replace_document", self.should_replace_document)
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _setup_parsed_cards_table(self) -> ComboBoxItemDelegate:
        self.parsed_cards_table: QTableView
        self.parsed_cards_table.setModel(self.card_list)
        delegate = ComboBoxItemDelegate(self.parsed_cards_table)
        self.parsed_cards_table.setItemDelegateForColumn(PageColumns.Set, delegate)
        self.parsed_cards_table.setItemDelegateForColumn(PageColumns.CollectorNumber, delegate)
        return delegate

    def initializePage(self) -> None:
        super(SummaryPage, self).initializePage()
        self.parsed_cards_table: QTableView
        parser: common.ParserBase = self.field("selected_parser")
        logger.debug(f"About to parse the deck list using parser {parser.__class__.__name__}")
        if self.field("translate-deck-list-enable"):
            language_override = self.field("translate-deck-list-target-language")
            logger.info(f"Language override enabled. Will translate deck list to language {language_override}")
        else:
            language_override = None
        parsed_deck, unidentified_lines = parser.parse_deck(
            self.field("deck_list"),
            self.field("print-guessing-enable"),
            self.field("print-guessing-prefer-already-downloaded"),
            language_override
        )
        self.setField("parsed_deck", parsed_deck)
        self.unparsed_lines_text: QPlainTextEdit
        self.card_list.add_cards(parsed_deck)
        self.unparsed_lines_text.setPlainText("\n".join(unidentified_lines))
        logger.debug(f"Initialized {self.__class__.__name__}")

    def cleanupPage(self):
        self.card_list.clear()
        super(SummaryPage, self).cleanupPage()
        logger.debug(f"Cleaned up {self.__class__.__name__}")


class DeckImportWizard(QWizard):
    deck_added = pyqtSignal(collections.Counter)
    clear_document = pyqtSignal()

    def __init__(self, card_db: CardDatabase, image_db: ImageDatabase,
                 language_model: QStringListModel, *args, **kwargs):
        super(DeckImportWizard, self).__init__(*args, **kwargs)
        self.card_db = card_db
        self.select_deck_parser_page = SelectDeckParserPage(card_db, image_db, self)
        self.load_list_page = LoadListPage(language_model, self)
        self.summary_page = SummaryPage(card_db, self)
        self.addPage(self.select_deck_parser_page)
        self.addPage(self.load_list_page)
        self.addPage(self.summary_page)
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
