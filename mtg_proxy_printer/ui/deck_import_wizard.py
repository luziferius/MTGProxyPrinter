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

from collections.abc import Callable
import itertools
import pathlib
import re
import urllib.error
import urllib.parse

from PySide6.QtCore import Slot, Signal, Property, QStringListModel, Qt, SIGNAL, \
    QSize, QUrl
from PySide6.QtGui import QValidator, QIcon, QDesktopServices
from PySide6.QtWidgets import QWizard, QFileDialog, QMessageBox, QWizardPage, QWidget, QRadioButton

from mtg_proxy_printer.async_tasks.image_downloader import BatchDownloadTask
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.units_and_sizes import SectionProxy
import mtg_proxy_printer.settings
from mtg_proxy_printer.decklist_parser import re_parsers, common, csv_parsers
from mtg_proxy_printer.async_tasks.decklist_downloader import IsIdentifyingDeckUrlValidator, AVAILABLE_DOWNLOADERS, \
    get_downloader_class, ParserBase
from mtg_proxy_printer.model.card_list import CardListModel
from mtg_proxy_printer.natsort import NaturallySortedSortFilterProxyModel
from mtg_proxy_printer.ui.common import load_ui_from_file, format_size, WizardBase, markdown_to_html
from mtg_proxy_printer.document_controller.import_deck_list import ActionImportDeckList

try:
    from mtg_proxy_printer.ui.generated.deck_import_wizard.load_list_page import Ui_LoadListPage
    from mtg_proxy_printer.ui.generated.deck_import_wizard.parser_result_page import Ui_SummaryPage
    from mtg_proxy_printer.ui.generated.deck_import_wizard.select_deck_parser_page import Ui_SelectDeckParserPage
except ModuleNotFoundError:
    Ui_LoadListPage = load_ui_from_file("deck_import_wizard/load_list_page")
    Ui_SummaryPage = load_ui_from_file("deck_import_wizard/parser_result_page")
    Ui_SelectDeckParserPage = load_ui_from_file("deck_import_wizard/select_deck_parser_page")

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger
__all__ = [
    "DeckImportWizard",
]
WizardButton = QWizard.WizardButton
WizardOption = QWizard.WizardOption
State = QValidator.State
StandardButton = QMessageBox.StandardButton


class IsDecklistParserRegularExpressionValidator(QValidator):
    """
    Validator used to check if the custom RE used for the "Custom RE parser" option is a valid RE.
    Also checks, if the supplied groups are specific enough to actually identify cards.
    It does NOT check, if the RE actually matches useful data.
    """

    has_named_groups_re = re.compile(
        rf"\(\?P<({'|'.join(re_parsers.GenericRegularExpressionDeckParser.SUPPORTED_GROUP_NAMES)})>.+?\)")

    def validate(self, input_string: str, pos: int) -> tuple[State, str, int]:
        try:
            re.compile(input_string)
        except re.error:
            return State.Intermediate, input_string, pos
        except RecursionError:
            # An input like the evaluated result of the expression '('*10000+'z'+')'*10000  will throw a RecursionError.
            # (Depending on the recursion limit)
            # Deem this invalid, as it cannot be parsed at all and allowing the user to append more will not help
            return State.Invalid, input_string, pos
        else:
            return self._validate_content(input_string), input_string, pos

    def _validate_content(self, input_string: str):
        """
        Validates the user supplied RE. The RE is acceptable if it contains group matchers for a superset of
        any identifying group.
        """
        found_groups = self.has_named_groups_re.findall(input_string)
        for identifying_groups in re_parsers.GenericRegularExpressionDeckParser.IDENTIFYING_GROUP_COMBINATIONS:
            if identifying_groups.issubset(found_groups):
                return State.Acceptable
        return State.Intermediate


class LoadListPage(QWizardPage):

    LARGE_FILE_THRESHOLD_BYTES = 200*2**10
    deck_list_downloader_changed = Signal(str)

    def __init__(self, language_model: QStringListModel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = ui = Ui_LoadListPage()
        ui.setupUi(self)
        self.deck_list_url_validator = IsIdentifyingDeckUrlValidator(self)
        self._deck_list_downloader: str | None = None
        ui.scryfall_search.textChanged.connect(
            lambda text: ui.scryfall_search_view_button.setEnabled(bool(text))
        )
        ui.scryfall_search.textChanged.connect(
            lambda text: ui.scryfall_search_download_button.setEnabled(bool(text))
        )
        ui.deck_list_download_url_line_edit.textChanged.connect(
            lambda text: ui.deck_list_download_button.setEnabled(
                self.deck_list_url_validator.validate(text)[0] == State.Acceptable))
        supported_sites = "\n".join((downloader.APPLICABLE_WEBSITES for downloader in AVAILABLE_DOWNLOADERS.values()))
        ui.deck_list_download_url_line_edit.setToolTip(
            self.tr("Supported websites:\n{supported_sites}", "Tooltip text"
                    ).format(supported_sites=supported_sites))
        ui.translate_deck_list_target_language.setModel(language_model)
        self.registerField("deck_list*", ui.deck_list)
        self.registerField("print-guessing-enable", ui.print_guessing_enable)
        self.registerField("print-guessing-prefer-already-downloaded", ui.print_guessing_prefer_already_downloaded)
        self.registerField("translate-deck-list-enable", ui.translate_deck_list_enable)
        self.registerField("deck-list-downloaded", self, "deck_list_downloader", "deck_list_downloader_changed(str)")
        self.registerField(
            "translate-deck-list-target-language", ui.translate_deck_list_target_language,
            "currentText", "currentTextChanged(str)"
        )
        logger.info(f"Created {self.__class__.__name__} instance.")


    @Property(str, notify=deck_list_downloader_changed)
    def deck_list_downloader(self):
        return self._deck_list_downloader

    @deck_list_downloader.setter
    def deck_list_downloader(self, value: str):
        if value is not self._deck_list_downloader:
            self.deck_list_downloader_changed.emit(value)
        self._deck_list_downloader = value

    def initializePage(self) -> None:
        super().initializePage()
        language_model: QStringListModel = self.ui.translate_deck_list_target_language.model()
        preferred_language = mtg_proxy_printer.settings.settings["cards"]["preferred-language"]
        preferred_language_index = language_model.stringList().index(preferred_language)
        self.ui.translate_deck_list_target_language.setCurrentIndex(preferred_language_index)
        options = mtg_proxy_printer.settings.settings["decklist-import"]
        self.ui.print_guessing_enable.setChecked(options.getboolean("enable-print-guessing-by-default"))
        self.ui.print_guessing_prefer_already_downloaded.setChecked(options.getboolean("prefer-already-downloaded-images"))
        self.ui.translate_deck_list_enable.setChecked(options.getboolean("always-translate-deck-lists"))
        logger.debug(f"Initialized {self.__class__.__name__}")

    def cleanupPage(self):
        super().cleanupPage()
        self.ui.translate_deck_list_enable.setChecked(False)
        self.ui.print_guessing_enable.setEnabled(True)
        self.ui.print_guessing_enable.setChecked(False)
        self.ui.print_guessing_prefer_already_downloaded.setChecked(False)
        logger.debug(f"Cleaned up {self.__class__.__name__}")

    @Slot()
    def on_deck_list_browse_button_clicked(self):
        logger.info("User selects a deck list from disk")
        default_path: str = mtg_proxy_printer.settings.settings["default-filesystem-paths"]["deck-list-search-path"]
        current_deck_list = self.ui.deck_list.toPlainText()
        if not current_deck_list or QMessageBox.question(
                self, self.tr("Overwrite existing deck list?", "Message box title"),
                self.tr("Selecting a file will overwrite the existing deck list. Continue?", "Message box body text"),
                StandardButton.Yes | StandardButton.No
        ) == StandardButton.Yes:
            if current_deck_list:
                logger.debug("User opted to replace the current, non-empty deck list with the file content")
            file_extension_filter = self.get_file_extension_filter()
            title = self.tr("Select deck file", "File selection dialog window title")
            selected_file, _ = QFileDialog.getOpenFileName(self, title, default_path, file_extension_filter)
            self._load_from_file(selected_file)

    def get_file_extension_filter(self) -> str:
        parsers = [
            re_parsers.MTGOnlineParser, re_parsers.MTGArenaParser, re_parsers.XMageParser,
            re_parsers.MagicWorkstationDeckDataFormatParser,
            csv_parsers.ScryfallCSVParser, csv_parsers.TappedOutCSVParser,
        ]
        everything = self.tr("All files (*)", "File type filter value")
        individual_file_types = list(
            itertools.chain.from_iterable(parser.supported_file_types().items() for parser in parsers)
        )
        # At this point, the data required (file extension list) is in a list of dict values containing
        # lists of strings. Thus, it requires two levels of iterable unpacking. Because of duplicates in file,
        # extensions across all parsers, de-duplicate and then sort the result.
        all_supported = sorted(set(
            itertools.chain.from_iterable(itertools.chain.from_iterable(
                parser.supported_file_types().values() for parser in parsers))
        ))
        # FIXME: This needs to be refactored for proper language-specific template substitution
        result = self.tr('All Supported ', 'File type filter value') + f'(*.{" *.".join(all_supported)});;' \
                 + ";;".join(
                     f'{name} (*.{" *.".join(extensions)})'
                     for name, extensions in individual_file_types) \
                 + f";;{everything}"
        return result

    @Slot()
    def on_deck_list_download_button_clicked(self):
        url = self.ui.deck_list_download_url_line_edit.text()
        bad_request_msg=self.tr(
            "Verify that the URL is valid, reachable, and that the deck list is set to public.\n"
            "This program cannot download private deck lists. Please note, that setting deck lists to\n"
            "public may take a minute or two to apply.",
            "Error message shown when trying to download a deck list from a seemingly valid URL fails")
        self._populate_deck_list_from_url(url, bad_request_msg)

    def _populate_deck_list_from_url(self, url: str, bad_request_msg: str):
        if not self.ui.deck_list.toPlainText() \
                or QMessageBox.question(
            self, self.tr(
                "Overwrite existing deck list?",
                "Message box title. Shown when loading a deck list would overwrite existing text"),
            self.tr(
                "Downloading a deck list will overwrite the existing deck list. Continue?",
                "Message box body text. Shown when loading a deck list would overwrite existing text"),
            StandardButton.Yes | StandardButton.No) == StandardButton.Yes:
            logger.info(f"User requests to download a deck list from the internet: {url}")
            downloader_class = get_downloader_class(url)
            if downloader_class is not None:
                self.setField("deck-list-downloaded", downloader_class.__name__)
                downloader = downloader_class(self)
                try:
                    deck_list = downloader.download(url)
                except urllib.error.HTTPError as e:
                    btn = StandardButton.Ok
                    title = self.tr("Deck list download failed", "Message box title. Shown when downloading failed")
                    msg = self.tr(
                        "Download failed with HTTP error {http_error_code}.\n\n{bad_request_msg}",
                        "Message box body text. Shown when the server returns an error code"
                    ).format(http_error_code=e.code, bad_request_msg=bad_request_msg)
                    QMessageBox.critical(self, title, msg, btn, btn)
                except Exception:
                    btn = StandardButton.Ok
                    title = self.tr("Deck list download failed", "Message box title. Shown when downloading failed")
                    msg = self.tr("Download failed.\n\n"
                                  "Check your internet connection, verify that the URL is valid, reachable, "
                                  "and that the deck list is set to public. "
                                  "This program cannot download private deck lists. If this persists, "
                                  "please report a bug in the issue tracker on the homepage.",
                                  "Message box body text. Shown when an unknown error occurred.")
                    QMessageBox.critical(self, title, msg, btn, btn)
                else:
                    self.ui.deck_list.setPlainText(deck_list)

    @Slot()
    def on_scryfall_search_view_button_clicked(self):
        logger.debug("User views the currently entered Scryfall query on the Scryfall website")
        query = urllib.parse.quote(self.ui.scryfall_search.text())
        QDesktopServices.openUrl(QUrl(f"https://scryfall.com/search?q={query}"))

    @Slot()
    def on_scryfall_search_download_button_clicked(self):
        logger.debug("User downloads the currently entered Scryfall query results")
        query = urllib.parse.quote(self.ui.scryfall_search.text())
        self._populate_deck_list_from_url(
            f"https://api.scryfall.com/cards/search?q={query}",
            self.tr("Invalid Scryfall query entered, no result obtained", "Message box body text"))

    def _load_from_file(self, selected_file: str | None):
        if selected_file and (file_path := pathlib.Path(selected_file)).is_file() and \
                self._ask_about_large_file(file_path):
            try:
                logger.debug("Selected path is valid file, trying to load the content")
                content = file_path.read_text()
            except UnicodeDecodeError:
                logger.warning(f"Unable to parse file {file_path}. Not a text file?")
                title = self.tr(
                    "Unable to read file content",
                    "Message box title. Shown when the user-selected file is unreadable.")
                msg = self.tr(
                    "Unable to read the content of file {file_path} as plain text.\nFailed to load the content.",
                    "Message box body text. Shown when the user-selected file is unreadable."
                ).format(file_path=file_path)
                QMessageBox.critical(self, title, msg)
            else:
                logger.debug("Successfully read the file as plain text, replacing the current deck list")
                self.ui.deck_list.setPlainText(content)

    def _ask_about_large_file(self, file_path: pathlib.Path) -> bool:
        size = file_path.stat().st_size
        too_large = size > LoadListPage.LARGE_FILE_THRESHOLD_BYTES
        should_load = not too_large or QMessageBox.question(
            self, self.tr(
                "Load large file?",
                "Message box title. Shown when the user-selected file is unreasonably large."),
            self.tr(
                "The selected file {file_path} is unexpectedly large ({formatted_size}). Load anyways?",
                "Message box body text. Shown when the user-selected file is unreasonably large."
            ).format(
                file_path=file_path, formatted_size=format_size(size)),
            StandardButton.Yes | StandardButton.No, StandardButton.No
        ) == StandardButton.Yes
        logger.debug(f"File size: {size}, {too_large=}, {should_load=}")
        return should_load


class SelectDeckParserPage(QWizardPage):
    """
    This page allows the user to choose which format their deck list uses.
    The result will be used to choose an appropriate parser implementation.
    """
    # Implementation note: Each QRadioButton has a signal/slot connection to the isComplete() slot method defined
    # in the loaded UI file. This is required to properly update the "complete" attribute on user input
    # and emit the completeChanged() Qt Signal whenever that attribute changes.
    # When adding new radio buttons, also add the appropriate connection. Otherwise, the “Next” button will stay
    # disabled when the user selects it.

    selected_parser_changed = Signal(common.ParserBase)

    @Property(common.ParserBase, notify=selected_parser_changed)
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

    def __init__(self, document: Document, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = ui = Ui_SelectDeckParserPage()
        ui.setupUi(self)
        self.card_db = document.card_db
        self.image_db = document.image_db
        self._selected_parser = None
        self.parser_creator: Callable[[], None] = (lambda: None)
        group_names = ', '.join(sorted(re_parsers.GenericRegularExpressionDeckParser.SUPPORTED_GROUP_NAMES))
        custom_re_input = ui.custom_re_input
        custom_re_input.setToolTip(custom_re_input.toolTip().format(group_names=group_names))
        custom_re_input.setWhatsThis(markdown_to_html(custom_re_input.whatsThis()))
        custom_re_input.setValidator(IsDecklistParserRegularExpressionValidator(self))
        ui.insert_copies_matcher_sample_button.clicked.connect(
            lambda: self.append_group_to_custom_re_input(r"(?P<copies>\d+)"))
        ui.insert_name_matcher_sample_button.clicked.connect(
            lambda: self.append_group_to_custom_re_input(r"(?P<name>.+)"))
        ui.insert_set_code_matcher_sample_button.clicked.connect(
            lambda: self.append_group_to_custom_re_input(r"(?P<set_code>\w+)"))
        ui.insert_collector_number_matcher_sample_button.clicked.connect(
            lambda: self.append_group_to_custom_re_input(r"(?P<collector_number>.+)"))
        ui.insert_language_matcher_sample_button.clicked.connect(
            lambda: self.append_group_to_custom_re_input(r"(?P<language>[a-zA-Z]{2})"))
        ui.insert_scryfall_id_matcher_sample_button.clicked.connect(
            lambda: self.append_group_to_custom_re_input(r"(?P<scryfall_id>[a-f\d]{8}(-[a-f\d]{4}){3}-[a-f\d]{12})"))
        self.complete = False
        self.registerField("custom_re", custom_re_input)
        self.registerField("selected_parser", self)
        ui.select_parser_magic_workstation.clicked.connect(
            lambda: setattr(self, "parser_creator", self._create_magic_workstation_parser)
        )
        ui.select_parser_mtg_arena.clicked.connect(
            lambda: setattr(self, "parser_creator", self._create_mtg_arena_parser)
        )
        ui.select_parser_mtg_online.clicked.connect(
            lambda: setattr(self, "parser_creator", self._create_mtg_online_parser)
        )
        ui.select_parser_xmage.clicked.connect(
            lambda: setattr(self, "parser_creator", self._create_xmage_parser)
        )
        ui.select_parser_scryfall_csv.clicked.connect(
            lambda: setattr(self, "parser_creator", self._create_scryfall_csv_parser)
        )
        ui.select_parser_tappedout_csv.clicked.connect(
            lambda: setattr(self, "parser_creator", self._create_tappedout_csv_parser)
        )
        ui.select_parser_custom_re.clicked.connect(
            lambda: setattr(self, "parser_creator", self._create_generic_re_parser)
        )
        ui.select_parser_card_name_list.clicked.connect(
            lambda: setattr(self, "parser_creator", self._create_card_name_list_parser)
        )
        logger.info(f"Created {self.__class__.__name__} instance.")

    def initializePage(self) -> None:
        super().initializePage()
        ui = self.ui
        used_downloader: str = self.field("deck-list-downloaded")
        if used_downloader:
            parser_to_use = AVAILABLE_DOWNLOADERS[used_downloader].PARSER_CLASS
            parser_table: dict[type[ParserBase], QRadioButton] = {
                re_parsers.MagicWorkstationDeckDataFormatParser: ui.select_parser_magic_workstation,
                re_parsers.MTGArenaParser: ui.select_parser_mtg_arena,
                re_parsers.MTGOnlineParser: ui.select_parser_mtg_online,
                re_parsers.CardNameListParser: ui.select_parser_card_name_list,
                re_parsers.XMageParser: ui.select_parser_xmage,
                csv_parsers.ScryfallCSVParser: ui.select_parser_scryfall_csv,
                csv_parsers.TappedOutCSVParser: ui.select_parser_tappedout_csv,
            }
            parser_table[parser_to_use].click()

    def append_group_to_custom_re_input(self, value: str):
        self.ui.custom_re_input.setText(self.ui.custom_re_input.text()+value)

    def _create_magic_workstation_parser(self):
        self.selected_parser = re_parsers.MagicWorkstationDeckDataFormatParser(self.card_db, self.image_db, self)

    def _create_mtg_arena_parser(self):
        self.selected_parser = re_parsers.MTGArenaParser(self.card_db, self.image_db, self)

    def _create_mtg_online_parser(self):
        self.selected_parser = re_parsers.MTGOnlineParser(self.card_db, self.image_db, self)

    def _create_xmage_parser(self):
        self.selected_parser = re_parsers.XMageParser(self.card_db, self.image_db, self)

    def _create_scryfall_csv_parser(self):
        self.selected_parser = csv_parsers.ScryfallCSVParser(self.card_db, self.image_db, self)

    def _create_card_name_list_parser(self):
        self.selected_parser = re_parsers.CardNameListParser(self.card_db, self.image_db, self)

    def _create_tappedout_csv_parser(self):
        self.selected_parser = csv_parsers.TappedOutCSVParser(
            self.card_db, self.image_db,
            self.ui.tappedout_include_maybe_board.isChecked(), self.ui.tappedout_include_acquire_board.isChecked(), self
        )

    def _create_generic_re_parser(self):
        self.selected_parser = re_parsers.GenericRegularExpressionDeckParser(
            self.card_db, self.image_db, self.field("custom_re"), self
        )

    @Slot()
    def isComplete(self) -> bool:
        acceptable = any((
            self.ui.select_parser_magic_workstation.isChecked(),
            self.ui.select_parser_mtg_arena.isChecked(),
            self.ui.select_parser_mtg_online.isChecked(),
            self.ui.select_parser_xmage.isChecked(),
            self.ui.select_parser_scryfall_csv.isChecked(),
            self.ui.select_parser_tappedout_csv.isChecked(),
            self.ui.select_parser_card_name_list.isChecked(),
        )) or all((
                self.ui.select_parser_custom_re.isChecked(),
                self.ui.custom_re_input.hasAcceptableInput()
        ))
        if acceptable != self.complete:
            self.complete = acceptable
            self.completeChanged.emit()
        return acceptable

    def validatePage(self) -> bool:
        self.parser_creator()
        # The call to connect() is here, because the  parser_creator callback created the selected parser.
        # If that later determines an incompatibility, it has to signal that to the user, so connect the error signal
        # here.
        self.selected_parser.incompatible_file_format.connect(self.wizard().on_incompatible_deck_file_selected)
        logger.info(f"Created parser: {self.selected_parser.__class__.__name__}")
        return self.isComplete()


class SummaryPage(QWizardPage):

    # Give the generic enum constants a semantic name
    BasicLandRemovalOption = WizardOption.HaveCustomButton1
    BasicLandRemovalButton = WizardButton.CustomButton1

    SelectedRemovalOption = WizardOption.HaveCustomButton2
    SelectedRemovalButton = WizardButton.CustomButton2

    def __init__(self, document: Document, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.ui = ui = Ui_SummaryPage()
        ui.setupUi(self)
        self.setCommitPage(True)
        self.card_list = CardListModel(document, self)
        self.card_list.oversized_card_count_changed.connect(self._update_accept_button_on_oversized_card_count_changed)
        ui.parsed_cards_table.setModel(self.card_list)
        self.registerField("should_replace_document", self.ui.should_replace_document)
        ui.should_replace_document.toggled[bool].connect(
            self._update_accept_button_on_replace_document_option_toggled)
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _create_sort_model(self, source_model: CardListModel) -> NaturallySortedSortFilterProxyModel:
        proxy_model = NaturallySortedSortFilterProxyModel(self)
        proxy_model.setSourceModel(source_model)
        proxy_model.setSortRole(Qt.ItemDataRole.EditRole)
        return proxy_model

    @Slot(int)
    def _update_accept_button_on_oversized_card_count_changed(self, oversized_cards: int):
        accept_button = self.wizard().button(WizardButton.FinishButton)
        if oversized_cards:
            accept_button.setIcon(QIcon.fromTheme("data-warning"))
            accept_button.setToolTip(self.tr(
                "Beware: The card list currently contains %n potentially oversized card(s).",
                "Warning emitted, if at least 1 card has the oversized flag set. "
                "The Scryfall server *may* still return a regular-sized image, so not *all* printings marked "
                "as oversized are actually so when fetched.", oversized_cards
            ))
        elif self.field("should_replace_document"):
            accept_button.setIcon(QIcon.fromTheme("document-replace"))
            accept_button.setToolTip(self.tr(
                "Replace document content with the identified cards",
                "Wizard Accept button tooltip, if replacing the document with the loaded list is enabled."
            ))
        else:
            accept_button.setIcon(QIcon.fromTheme("dialog-ok"))
            accept_button.setToolTip(self.tr(
                "Append identified cards to the document",
                "Wizard Accept button tooltip, if replacing the document with the loaded list is disabled."
            ))

    @Slot(bool)
    def _update_accept_button_on_replace_document_option_toggled(self, enabled: bool):
        accept_button = self.wizard().button(WizardButton.FinishButton)
        if accept_button.icon().name() == "data-warning":
            return
        if enabled:
            accept_button.setIcon(QIcon.fromTheme("document-replace"))
            accept_button.setToolTip(self.tr(
                "Replace document content with the identified cards",
                "Wizard Accept button tooltip, if replacing the document with the loaded list is enabled."
            ))
        else:
            accept_button.setIcon(QIcon.fromTheme("dialog-ok"))
            accept_button.setToolTip(self.tr(
                "Append identified cards to the document",
                "Wizard Accept button tooltip, if replacing the document with the loaded list is disabled."
            ))

    def initializePage(self) -> None:
        super().initializePage()
        parser: common.ParserBase = self.field("selected_parser")
        decklist_import_section = mtg_proxy_printer.settings.settings["decklist-import"]
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
        self.card_list.add_cards(parsed_deck)
        self.ui.unparsed_lines_text.setPlainText("\n".join(unidentified_lines))
        self._initialize_custom_buttons(decklist_import_section)
        if decklist_import_section.getboolean("automatically-remove-basic-lands"):
            logger.info("Automatically remove basic lands")
            self._remove_basic_lands()
        logger.debug(f"Initialized {self.__class__.__name__}")

    def _initialize_custom_buttons(self, decklist_import_section: SectionProxy):
        wizard = self.wizard()
        wizard.customButtonClicked.connect(self.custom_button_clicked)
        # When basic lands are stripped fully automatically, there is no need to have a non-functional button.
        should_offer_basic_land_removal = not decklist_import_section.getboolean("automatically-remove-basic-lands")
        wizard.setOption(self.BasicLandRemovalOption, should_offer_basic_land_removal)
        remove_basic_lands_button = wizard.button(self.BasicLandRemovalButton)
        remove_basic_lands_button.setEnabled(self.card_list.has_basic_lands(
            decklist_import_section.getboolean("remove-basic-wastes"),
            decklist_import_section.getboolean("remove-snow-basics")))
        remove_basic_lands_button.setText(self.tr("Remove basic lands", "Button text"))
        remove_basic_lands_button.setToolTip(self.tr(
            "Remove all basic lands in the deck list above", "Button tooltip"))
        remove_basic_lands_button.setIcon(QIcon.fromTheme("edit-delete"))
        wizard.setOption(self.SelectedRemovalOption, True)
        remove_selected_cards_button = wizard.button(self.SelectedRemovalButton)
        remove_selected_cards_button.setEnabled(False)
        remove_selected_cards_button.setText(self.tr(
            "Remove selected", "Button text. Clicking removes all selected cards in the table"))
        remove_selected_cards_button.setToolTip(self.tr(
            "Remove all selected cards in the deck list above", "Button tooltip"))
        remove_selected_cards_button.setIcon(QIcon.fromTheme("edit-delete"))
        self.ui.parsed_cards_table.changed_selection_is_empty.connect(
            remove_selected_cards_button.setDisabled
        )

    def cleanupPage(self):
        self.card_list.clear()
        super().cleanupPage()
        wizard = self.wizard()
        wizard.customButtonClicked.disconnect(self.custom_button_clicked)
        wizard.setOption(self.BasicLandRemovalOption, False)
        wizard.setOption(self.SelectedRemovalOption, False)
        self.ui.parsed_cards_table.changed_selection_is_empty.disconnect(
            wizard.button(self.SelectedRemovalButton).setDisabled
        )
        logger.debug(f"Cleaned up {self.__class__.__name__}")

    @Slot()
    def isComplete(self) -> bool:
        return self.card_list.rowCount() > 0

    @Slot(int)
    def custom_button_clicked(self, button_id: int):
        button = WizardButton(button_id)
        self.wizard().button(button).setEnabled(False)
        if button == self.BasicLandRemovalButton:
            logger.info("User requests to remove all basic lands")
            self._remove_basic_lands()
        elif button == self.SelectedRemovalButton:
            self._remove_selected_cards()

    def _remove_basic_lands(self):
        decklist_import_section = mtg_proxy_printer.settings.settings["decklist-import"]
        self.card_list.remove_all_basic_lands(
            decklist_import_section.getboolean("remove-basic-wastes"),
            decklist_import_section.getboolean("remove-snow-basics"))

    def _remove_selected_cards(self):
        logger.info("User removes the selected cards")
        sort_model = self.ui.parsed_cards_table.sort_model
        selection_mapped_to_source = sort_model.mapSelectionToSource(
            self.ui.parsed_cards_table.selectionModel().selection())
        self.card_list.remove_multi_selection(selection_mapped_to_source)
        if not self.card_list.rowCount():
            # User deleted everything, so nothing left to complete the wizard. This’ll disable the Finish button.
            self.completeChanged.emit()


class DeckImportWizard(WizardBase):
    request_run_async_task = Signal(BatchDownloadTask)
    BUTTON_ICONS = {
        QWizard.WizardButton.FinishButton: "dialog-ok",
        QWizard.WizardButton.CancelButton: "dialog-cancel",
    }

    def __init__(self, document: Document, language_model: QStringListModel,
                 parent: QWidget = None, flags=Qt.WindowType.Window):
        super().__init__(QSize(1000, 600), parent, flags)
        self.setDefaultProperty("QPlainTextEdit", "plainText", SIGNAL("textChanged()"))
        self.select_deck_parser_page = SelectDeckParserPage(document, self)
        self.load_list_page = LoadListPage(language_model, self)
        self.summary_page = SummaryPage(document, self)
        self.addPage(self.load_list_page)
        self.addPage(self.select_deck_parser_page)
        self.addPage(self.summary_page)
        self.setWindowIcon(QIcon.fromTheme("document-import"))
        self.setWindowTitle(self.tr("Import a deck list", "Window title"))
        self.image_db = document.image_db
        logger.info(f"Created {self.__class__.__name__} instance.")

    def accept(self):
        if not self._ask_about_oversized_cards():
            logger.info("Aborting accept(), because oversized cards are present "
                        "in the deck list and the user chose to go back.")
            return
        super().accept()
        logger.info("User finished the import wizard, performing the requested actions")
        if replace_document := self.field("should_replace_document"):
            logger.info("User chose to replace the current document content, clearing it")
        sort_order = self.summary_page.ui.parsed_cards_table.sort_model.row_sort_order()
        action = ActionImportDeckList(
            self.summary_page.card_list.as_cards(sort_order),
            replace_document
        )
        logger.info(f"User loaded a deck list with {action.card_count()} cards, adding these to the document")

        self.request_run_async_task.emit(BatchDownloadTask(self.image_db, action))

    def _ask_about_oversized_cards(self) -> bool:
        oversized_count = self.summary_page.card_list.oversized_card_count
        if oversized_count and QMessageBox.question(
                self, self.tr(
                    "Oversized cards present",
                    "Message box title. Shown when the deck list contains likely unwanted oversized cards."),
                self.tr(
                    "There are %n possibly oversized cards in the deck list that "
                    "may not fit into a deck, when printed out.\n\nContinue and use these cards as-is?",
                    "Message box body text. "
                    "Shown when the deck list contains likely unwanted oversized cards.",
                    oversized_count),
                StandardButton.Yes | StandardButton.No, StandardButton.No) == StandardButton.No:
            return False
        return True

    def on_incompatible_deck_file_selected(self):
        QMessageBox.warning(
            self, self.tr(
                "Incompatible file selected",
                "Message box title. Shown when trying to parse a deck list returns no results."),
            self.tr(
                "Unable to parse the given deck list, no results were obtained.\n"
                "Maybe you selected the wrong deck list type?",
                "Message box body text. Shown when trying to parse a deck list returns no results."),
            StandardButton.Ok, StandardButton.Ok
        )
