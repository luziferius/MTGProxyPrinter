# Copyright (C) 2020 Thomas Hess <thomas.hess@udo.edu>

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

from PyQt5.QtCore import QStringListModel, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget, QDialogButtonBox, QLineEdit, QSpinBox, QComboBox

import mtg_proxy_printer.model.carddb
import mtg_proxy_printer.model.document
import mtg_proxy_printer.settings
from mtg_proxy_printer.ui.common import inherits_from_ui_file_with_name, BlockedSignals

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


class AddCardWidget(*inherits_from_ui_file_with_name("add_card_widget")):

    input_is_valid_and_unique_card = pyqtSignal(bool)
    card_added = pyqtSignal(mtg_proxy_printer.model.carddb.Card, int)

    def __init__(self, parent: QWidget = None):
        super(AddCardWidget, self).__init__(parent)
        self.setupUi(self)
        self.card_database: mtg_proxy_printer.model.carddb.CardDatabase = None
        self.card = self._create_new_card()
        self.page_free_slots = self.page_total_slots = 9
        self.language_combo_box: QComboBox
        self.language_model = None
        self.language_combo_box.currentTextChanged.connect(self.on_language_combo_box_changed)
        self._setup_card_name_search()
        self._setup_set_name_search()
        self._setup_collector_number_search()
        self.copies_input: QSpinBox
        self.scryfall_url_input: QLineEdit
        self.scryfall_url_input.setEnabled(False)
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
        self.input_is_valid_and_unique_card.connect(self.button_box.button(QDialogButtonBox.Ok).setEnabled)
        self.button_box.button(QDialogButtonBox.Ok).clicked.connect(self.on_ok_button_triggered)
        self.button_box.button(QDialogButtonBox.Reset).clicked.connect(self.reset)
        for input_box in (
                self.card_name_search,
                self.set_name_search,
                self.collectors_number_search,
                self.language_combo_box
                ):
            input_box.currentTextChanged.connect(self.check_input_is_valid_and_unique_card)
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _setup_card_name_search(self):
        self.card_name_search: QComboBox
        self.card_name_search.lineEdit().setPlaceholderText("Search by card name")
        self.card_name_search.lineEdit().setClearButtonEnabled(True)
        self.card_name_model = QStringListModel([], self.card_name_search)
        with BlockedSignals(self.card_name_search):  # Do not emit signals without a card_database used to handle them
            self.card_name_search.setModel(self.card_name_model)
        self.card_name_search.currentTextChanged.connect(self.on_card_name_search_updated)

    def _setup_set_name_search(self):
        self.set_name_search: QComboBox
        self.set_name_search.lineEdit().setPlaceholderText("Search by released set")
        self.set_name_search.lineEdit().setClearButtonEnabled(True)
        self.set_name_model = QStringListModel([], self.set_name_search)
        with BlockedSignals(self.set_name_search):
            self.set_name_search.setModel(self.set_name_model)
        self.set_name_search.currentTextChanged.connect(self.on_set_name_search_updated)

    def _setup_collector_number_search(self):
        self.collectors_number_search: QComboBox
        self.collectors_number_search.lineEdit().setPlaceholderText("Number")
        self.collectors_number_search.lineEdit().setClearButtonEnabled(True)
        self.collectors_number_model = QStringListModel([], self.collectors_number_search)
        with BlockedSignals(self.collectors_number_search):
            self.collectors_number_search.setModel(self.collectors_number_model)
        self.collectors_number_search.currentTextChanged.connect(self.on_collector_number_search_updated)

    @pyqtSlot(int)
    def on_page_total_slots_changed(self, slots: int):
        difference = self.page_total_slots - slots
        self.page_total_slots = slots
        self.page_free_slots -= difference
        self.copies_input.setMaximum(self.page_free_slots)

    @pyqtSlot(mtg_proxy_printer.model.document.Page)
    def on_current_page_changed(self, page: mtg_proxy_printer.model.document.Page):
        self.page_free_slots = self.page_total_slots - page.rowCount()
        if self.page_free_slots and not self.copies_input.maximum():
            # If the previous maximum was 0 (because the page was full),
            # the minimum value was automatically set from 1 to 0 by Qt, so set it up to 1 again.
            self.copies_input.setMinimum(1)
        self.copies_input.setMaximum(self.page_free_slots)
        self.check_input_is_valid_and_unique_card()

    @pyqtSlot()
    def check_input_is_valid_and_unique_card(self):
        if self.card_database is None:
            return False
        self.card_name_search: QComboBox
        self.set_name_search: QComboBox
        self.collectors_number_search: QComboBox
        self.language_combo_box: QComboBox
        result = self.card_database.is_valid_and_unique_card(self.card) and bool(self.page_free_slots)
        self.input_is_valid_and_unique_card.emit(result)

    def _create_card_from_user_input(self):
        card = mtg_proxy_printer.model.carddb.Card(
            card_name if (card_name := self.card_name_search.currentText()) else None,
            set_abbreviation if (set_abbreviation := self.set_name_search.currentText()) else None,
            collector_number if (collector_number := self.collectors_number_search.currentText()) else None,
            self.language_combo_box.currentText()
        )
        return card

    @pyqtSlot(str)
    def on_card_name_search_updated(self, changed: str):
        if changed != self.card.name:
            self.card.name = changed if changed else None
            self._update_set_name_search()
            self._update_collector_number_search()

    def _update_set_name_search(self):
        with BlockedSignals(self.set_name_search):
            set_names = self.card_database.find_sets_matching(self.card)
            self.set_name_model.setStringList(set_names)
        if self.card.set_abbr and any(abbr.startswith(self.card.set_abbr) for abbr in set_names):
            self.set_name_search.setCurrentText(self.card.set_abbr)

    def _update_collector_number_search(self):
        with BlockedSignals(self.collectors_number_search):
            collector_numbers = self.card_database.find_collector_numbers_matching(self.card)
            self.collectors_number_model.setStringList(collector_numbers)
        if self.card.collector_number and any(num.startswith(self.card.collector_number) for num in collector_numbers):
            self.collectors_number_search.setCurrentText(self.card.collector_number)

    def _update_card_search(self):
        with BlockedSignals(self.card_name_search):
            card_names = self.card_database.find_card_names_matching(self.card)
            self.card_name_model.setStringList(card_names)
        if self.card.name and any(name.startswith(self.card.name) for name in card_names):
            self.card_name_search.setCurrentText(self.card.name)

    @pyqtSlot(str)
    def on_set_name_search_updated(self, changed: str):
        if changed != self.card.set_abbr:
            self.card.set_abbr = changed if changed else None
            self.card_name_search: QComboBox
            self._update_card_search()
            self._update_collector_number_search()

    @pyqtSlot(str)
    def on_collector_number_search_updated(self, changed: str):
        if changed != self.card.collector_number:
            self.card.collector_number = changed if changed else None
            self._update_card_search()
            self._update_set_name_search()

    @pyqtSlot(str)
    def on_language_combo_box_changed(self, changed: str):
        if changed != self.card.language:
            self.card.language = changed
            self._update_card_search()
            self._update_set_name_search()
            self._update_collector_number_search()

    def set_card_database(self, card_db: mtg_proxy_printer.model.carddb.CardDatabase):
        self.card_database = card_db
        self.reset()

    def set_language_model(self, model: QStringListModel):
        self.language_model = model
        self.language_combo_box.setModel(self.language_model)
        self.update_selected_language()

    @staticmethod
    def _create_new_card() -> mtg_proxy_printer.model.carddb.Card:
        card = mtg_proxy_printer.model.carddb.Card(
            None, None, None,
            mtg_proxy_printer.settings.settings["images"]["preferred-language"])
        return card

    @pyqtSlot()
    def update_selected_language(self):
        self.language_combo_box: QComboBox
        if self.language_model.stringList():
            self.language_combo_box.setCurrentIndex(
                self.language_model.stringList().index(
                    mtg_proxy_printer.settings.settings["images"]["preferred-language"])
            )
            self.card.language = self.language_combo_box.currentText()
        else:
            self.card.language = mtg_proxy_printer.settings.settings["images"]["preferred-language"]

    def on_ok_button_triggered(self):
        logger.debug("User clicked OK and adds a new card to the current page.")
        self.card_database.add_missing_information(self.card)
        self.copies_input: QSpinBox
        copies = self.copies_input.value()
        self.page_free_slots -= copies
        self.copies_input.setMaximum(self.page_free_slots)
        self.card_added.emit(self.card, copies)
        self.reset()

    @pyqtSlot()
    def reset(self):
        self.card = self._create_new_card()
        self._update_card_search()
        self._update_set_name_search()
        self._update_collector_number_search()
        self.input_is_valid_and_unique_card.emit(False)

    @pyqtSlot(int)
    def cards_removed(self, amount: int):
        self.page_free_slots += amount
        self.copies_input.setMaximum(self.page_free_slots)
