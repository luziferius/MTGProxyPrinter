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
import math
import pathlib
import re
import typing

from PyQt5.QtCore import pyqtSlot, pyqtSignal, pyqtProperty, QStringListModel, Qt
from PyQt5.QtGui import QValidator, QIcon
from PyQt5.QtWidgets import QWizard, QFileDialog, QPlainTextEdit, QMessageBox, QLineEdit, QTableView, QComboBox, \
    QPushButton

import mtg_proxy_printer.settings
from mtg_proxy_printer.decklist_parser import re_parsers, common, csv_parsers
from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.model.imagedb import ImageDatabase
from mtg_proxy_printer.model.card_list import CardListModel, PageColumns
from mtg_proxy_printer.natsort import NaturallySortedSortFilterProxyModel
from mtg_proxy_printer.ui.common import inherits_from_ui_file_with_name, format_size
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

    LARGE_FILE_THRESHOLD_BYTES = 200*2**10

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
            self._load_from_file(selected_file)

    def _load_from_file(self, selected_file: typing.Optional[str]):
        if selected_file and (file_path := pathlib.Path(selected_file)).is_file() and \
                self._ask_about_large_file(file_path):
            try:
                logger.debug("Selected path is valid file, trying to load the content")
                content = file_path.read_text()
            except UnicodeDecodeError:
                logger.warning(f"Unable to parse file {file_path}. Not a text file?")
                QMessageBox.critical(
                    self, "Unable to read file content",
                    f"Unable to read the content of file {file_path} as plain text.\nFailed to load the content.")
            else:
                logger.debug("Successfully read the file as plain text, replacing the current deck list")
                self.deck_list.setPlainText(content)

    def _ask_about_large_file(self, file_path: pathlib.Path) -> bool:
        size = file_path.stat().st_size
        too_large = size > LoadListPage.LARGE_FILE_THRESHOLD_BYTES
        should_load = not too_large or QMessageBox.question(
            self, "Load large file?",
            f"The selected file {file_path} is unexpectedly large ({format_size(size)}). Load anyways?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        ) == QMessageBox.Yes
        logger.debug(f"File size: {size}, {too_large=}, {should_load=}")
        return should_load


class SelectDeckParserPage(*inherits_from_ui_file_with_name("deck_import_wizard/select_deck_parser_page")):
    """
    This page allows the user to choose which format their deck list uses.
    The result will be used to choose an appropriate parser implementation.
    """
    # Implementation note: Each QRadioButton has a signal/slot connection to the isComplete() slot method defined
    # in the loaded UI file. This is required to properly update the "complete" attribute on user input
    # and emit the completeChanged() Qt Signal whenever that attribute changes.
    # When adding new radio buttons, also add the appropriate connection. Otherwise, the “Next” button will stay
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
        self.parser_creator: typing.Callable[[], None] = (lambda: None)
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
            lambda: setattr(self, "parser_creator", self._create_mtg_arena_parser)
        )
        self.select_parser_mtg_online.pressed.connect(
            lambda: setattr(self, "parser_creator", self._create_mtg_online_parser)
        )
        self.select_parser_xmage.pressed.connect(
            lambda: setattr(self, "parser_creator", self._create_xmage_parser)
        )
        self.select_parser_scryfall_csv.pressed.connect(
            lambda: setattr(self, "parser_creator", self._create_scryfall_csv_parser)
        )
        self.select_parser_tappedout_csv.pressed.connect(
            lambda: setattr(self, "parser_creator", self._create_tappedout_csv_parser)
        )
        self.select_parser_custom_re.pressed.connect(
            lambda: setattr(self, "parser_creator", self._create_generic_re_parser)
        )
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _create_mtg_arena_parser(self):
        self.selected_parser = re_parsers.MTGArenaParser(self.card_db, self.image_db, self)

    def _create_mtg_online_parser(self):
        self.selected_parser = re_parsers.MTGOnlineParser(self.card_db, self.image_db, self)

    def _create_xmage_parser(self):
        self.selected_parser = re_parsers.XMageParser(self.card_db, self.image_db, self)

    def _create_scryfall_csv_parser(self):
        self.selected_parser = csv_parsers.ScryfallCSVParser(self.card_db, self.image_db, self)

    def _create_tappedout_csv_parser(self):
        self.selected_parser = csv_parsers.TappedOutCSVParser(
            self.card_db, self.image_db,
            self.tappedout_include_maybe_board.isChecked(), self.tappedout_include_acquire_board.isChecked(), self
        )

    def _create_generic_re_parser(self):
        self.selected_parser = re_parsers.GenericRegularExpressionDeckParser(
            self.card_db, self.image_db, self.field("custom_re"), self
        )

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

    def validatePage(self) -> bool:
        self.parser_creator()
        logger.info(f"Created parser: {self.selected_parser.__class__.__name__}")
        return super().validatePage()


class SummaryPage(*inherits_from_ui_file_with_name("deck_import_wizard/parser_result_page")):
    def __init__(self, card_db: CardDatabase, *args, **kwargs):
        super(SummaryPage, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setCommitPage(True)
        self.card_list = CardListModel(card_db, self)
        self.card_list_sort_model = self._create_sort_model(self.card_list)
        self.card_list.oversized_card_count_changed.connect(self._update_accept_button_on_oversized_card_count_changed)
        self.combo_box_delegate = self._setup_parsed_cards_table(self.card_list_sort_model)
        self.registerField("should_replace_document", self.should_replace_document)
        self.should_replace_document.toggled[bool].connect(
            self._update_accept_button_on_replace_document_option_toggled)
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _create_sort_model(self, source_model: CardListModel) -> NaturallySortedSortFilterProxyModel:
        proxy_model = NaturallySortedSortFilterProxyModel(self)
        proxy_model.setSourceModel(source_model)
        proxy_model.setSortRole(Qt.EditRole)
        return proxy_model

    @pyqtSlot(int)
    def _update_accept_button_on_oversized_card_count_changed(self, oversized_cards: int):
        accept_button = self.wizard().button(QWizard.FinishButton)
        if oversized_cards:
            accept_button.setIcon(QIcon.fromTheme("data-warning"))
            accept_button.setToolTip(
                f"Beware: The card list currently contains {oversized_cards} potentially oversized cards.\n"
                f"Printings may overlap"
            )
        elif self.field("should_replace_document"):
            accept_button.setIcon(QIcon.fromTheme("document-replace"))
            accept_button.setToolTip("Replace document content with the identified cards")
        else:
            accept_button.setIcon(QIcon())
            accept_button.setToolTip("Append identified cards to the document")

    @pyqtSlot(bool)
    def _update_accept_button_on_replace_document_option_toggled(self, enabled: bool):
        accept_button: QPushButton = self.wizard().button(QWizard.FinishButton)
        if accept_button.icon().name() == "data-warning":
            return
        if enabled:
            accept_button.setIcon(QIcon.fromTheme("document-replace"))
            accept_button.setToolTip("Replace document content with the identified cards")
        else:
            accept_button.setIcon(QIcon.fromTheme("dialog-ok"))
            accept_button.setToolTip("Append identified cards to the document")

    def _setup_parsed_cards_table(self, model) -> ComboBoxItemDelegate:
        self.parsed_cards_table: QTableView
        self.parsed_cards_table.setModel(model)
        delegate = ComboBoxItemDelegate(self.parsed_cards_table)
        self.parsed_cards_table.setItemDelegateForColumn(PageColumns.Set, delegate)
        self.parsed_cards_table.setItemDelegateForColumn(PageColumns.CollectorNumber, delegate)
        for column, scaling_factor in (
                (PageColumns.CardName, 2),
                (PageColumns.Set, 2.75),
                (PageColumns.CollectorNumber, 0.95),
                (PageColumns.Language, 0.9)):
            new_size = math.floor(self.parsed_cards_table.columnWidth(column) * scaling_factor)
            self.parsed_cards_table.setColumnWidth(column, new_size)
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
        self.unparsed_lines_text: QPlainTextEdit
        self.card_list.add_cards(parsed_deck)
        self.unparsed_lines_text.setPlainText("\n".join(unidentified_lines))
        logger.debug(f"Initialized {self.__class__.__name__}")

    def cleanupPage(self):
        self.card_list.clear()
        super(SummaryPage, self).cleanupPage()
        logger.debug(f"Cleaned up {self.__class__.__name__}")

    @pyqtSlot()
    def isComplete(self) -> bool:
        return self.card_list.rowCount() > 0


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
        self._set_default_size()
        self.setWindowTitle("Import a deck list")
        self._setup_dialog_button_icons()
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _set_default_size(self):
        new_width, new_height = 800, 600
        if (parent := self.parent()) is not None:
            parent_pos = parent.mapToGlobal(parent.pos())
            self.setGeometry(
                parent_pos.x() + parent.width()//2 - new_width//2,
                parent_pos.y() + parent.height()//2 - new_height//2,
                new_width, new_height
            )
        else:
            self.resize(new_width, new_height)

    def _setup_dialog_button_icons(self):
        buttons_with_icons = [
            (QWizard.FinishButton, "dialog-ok"),
            (QWizard.CancelButton, "dialog-cancel"),
        ]
        for role, icon in buttons_with_icons:
            button = self.button(role)
            if button.icon().isNull():
                button.setIcon(QIcon.fromTheme(icon))

    def accept(self):
        if not self._ask_about_oversized_cards():
            logger.info("Aborting accept(), because oversized cards are present "
                        "in the deck list and the user chose to go back.")
            return
        super(DeckImportWizard, self).accept()
        logger.info("User finished the import wizard, performing the requested actions")
        if self.field("should_replace_document"):
            logger.info("User chose to replace the current document content, clearing it")
            self.clear_document.emit()
        deck = self.summary_page.card_list.as_deck(self.summary_page.card_list_sort_model.row_sort_order())
        # len(deck) only counts keys, so use sum(deck.values()) to count duplicates
        logger.info(f"User loaded a deck list with {sum(deck.values())} cards, adding these to the document")
        self.deck_added.emit(deck)

    def _ask_about_oversized_cards(self) -> bool:
        oversized_count = self.summary_page.card_list.oversized_card_count
        if oversized_count and QMessageBox.question(
                self, "Oversized cards present",
                f"There are {oversized_count} possibly oversized cards in the deck list that "
                f"may not fit into a deck, when printed out.\n\nContinue and use these cards as-is?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.No:
            return False
        return True
