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
from PyQt5.QtWidgets import QWidget, QDialogButtonBox, QLineEdit, QSpinBox, QComboBox, QMessageBox

import mtg_proxy_printer.model.carddb
import mtg_proxy_printer.settings
from mtg_proxy_printer.ui.common import inherits_from_ui_file_with_name, BlockedSignals

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


class AddCardWidget(*inherits_from_ui_file_with_name("add_card_widget")):

    input_is_valid_and_unique_card = pyqtSignal(bool)
    card_added = pyqtSignal(mtg_proxy_printer.model.carddb.Card)

    def __init__(self, parent: QWidget = None):
        super(AddCardWidget, self).__init__(parent)
        self.setupUi(self)
        self.card_database: mtg_proxy_printer.model.carddb.CardDatabase = None
        self.card = mtg_proxy_printer.model.carddb.Card(
            None, None, None,
            mtg_proxy_printer.settings.settings["images"]["preferred-language"])
        self.language_combo_box: QComboBox
        self.language_model = None
        self.card_name_search: QComboBox
        self.card_name_search.lineEdit().setPlaceholderText("Search by card name")
        self.card_name_search.lineEdit().setClearButtonEnabled(True)
        self.card_name_model = QStringListModel([], self.card_name_search)
        self.card_name_search.setModel(self.card_name_model)
        self.card_name_search.currentTextChanged.connect(self.on_card_name_search_updated)
        self.set_name_search: QComboBox
        self.set_name_search.lineEdit().setPlaceholderText("Search by released set")
        self.set_name_search.lineEdit().setClearButtonEnabled(True)
        self.set_name_model = QStringListModel([], self.set_name_search)
        self.set_name_search.setModel(self.set_name_model)
        self.set_name_search.currentTextChanged.connect(self.on_set_name_search_updated)
        self.collectors_number_search: QComboBox
        self.collectors_number_search.lineEdit().setPlaceholderText("Number")
        self.collectors_number_search.lineEdit().setClearButtonEnabled(True)
        self.collectors_number_model = QStringListModel([], self.collectors_number_search)
        self.collectors_number_search.setModel(self.collectors_number_model)
        self.collectors_number_search.currentTextChanged.connect(self.on_collector_number_search_updated)

        self.copies_input: QSpinBox
        self.scryfall_url_input: QLineEdit
        self.scryfall_url_input.setEnabled(False)
        self._connect_reset_button()
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
        self.input_is_valid_and_unique_card.connect(self.button_box.button(QDialogButtonBox.Ok).setEnabled)
        self.button_box.button(QDialogButtonBox.Ok).clicked.connect(self.on_ok_button_triggered)

        for input_box in (
                self.card_name_search,
                self.set_name_search,
                self.collectors_number_search,
                self.language_combo_box
                ):
            input_box.currentTextChanged.connect(self.check_input_is_valid_and_unique_card)
        self.card_added.connect(self.card_added_debug_slot)
        logger.info(f"Created {self.__class__.__name__} instance.")

    @pyqtSlot()
    def check_input_is_valid_and_unique_card(self):
        if self.card_database is None:
            return False
        self.card_name_search: QComboBox
        self.set_name_search: QComboBox
        self.collectors_number_search: QComboBox
        self.language_combo_box: QComboBox
        card = self._create_card_from_user_input()
        result = self.card_database.is_valid_and_unique_card(card)
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
        if self.card_database is not None and changed != self.card.name:
            print(f"on_card_name_search_updated: new: {changed=}, old: {self.card=}")
            self.card.name = changed
            set_names = self.card_database.find_sets_matching(self.card)
            collector_numbers = self.card_database.find_collector_numbers_matching(self.card)
            with BlockedSignals(self.set_name_search):
                self.set_name_model.setStringList(set_names)
                if self.card.set_abbr:
                    self.set_name_search.setCurrentText(self.card.set_abbr)
            with BlockedSignals(self.collectors_number_search):
                self.collectors_number_model.setStringList(collector_numbers)
                if self.card.collector_number:
                    self.collectors_number_search.setCurrentText(self.card.collector_number)

    @pyqtSlot(str)
    def on_set_name_search_updated(self, changed: str):
        if self.card_database is not None and changed != self.card.set_abbr:
            print(f"on_set_name_search_updated: new: {changed=}, old: {self.card=}")
            self.card.set_abbr = changed
            card_names = self.card_database.find_card_names_matching(self.card)
            print(f"Matching cards #{len(card_names)}")
            self.card_name_search: QComboBox
            with BlockedSignals(self.card_name_search):
                self.card_name_model.setStringList(card_names)
                if self.card.name:
                    self.card_name_search.setCurrentText(self.card.name)
            with BlockedSignals(self.collectors_number_search):
                collector_numbers = self.card_database.find_collector_numbers_matching(self.card)
                self.collectors_number_model.setStringList(collector_numbers)
                if self.card.collector_number:
                    self.collectors_number_search.setCurrentText(self.card.collector_number)

    @pyqtSlot(str)
    def on_collector_number_search_updated(self, changed: str):
        if self.card_database is not None and changed != self.card.collector_number:
            print(f"on_collector_number_search_updated: new: {changed=}, old: {self.card=}")
            self.card.collector_number = changed
            card_names = self.card_database.find_card_names_matching(self.card)
            with BlockedSignals(self.card_name_search):
                self.card_name_model.setStringList(card_names)
            self.card_name_search: QComboBox
            if self.card.name:
                self.card_name_search.setCurrentText(self.card.name)
            if self.card.set_abbr:
                self.set_name_search.setCurrentText(self.card.set_abbr)

    def set_card_database(self, card_db: mtg_proxy_printer.model.carddb.CardDatabase):
        self.card_database = card_db

    def set_language_model(self, model: QStringListModel):
        self.language_model = model
        self.language_combo_box.setModel(self.language_model)
        self.update_selected_language()

    @pyqtSlot()
    def update_selected_language(self):
        self.language_combo_box: QComboBox
        self.language_combo_box.setCurrentIndex(
            self.language_model.stringList().index(
                mtg_proxy_printer.settings.settings["images"]["preferred-language"])
        )
        self.card.language = self.language_combo_box.currentText()

    def _connect_reset_button(self):
        logger.debug("User reset the add_card_widget form.")
        self.button_box: QDialogButtonBox
        reset_button_clicked_signal = self.button_box.button(QDialogButtonBox.Reset).clicked
        reset_button_clicked_signal.connect(self.card_name_search.clearEditText)
        reset_button_clicked_signal.connect(self.set_name_search.clearEditText)
        reset_button_clicked_signal.connect(self.collectors_number_search.clearEditText)
        reset_button_clicked_signal.connect(lambda: self.copies_input.setValue(1))
        reset_button_clicked_signal.connect(self.scryfall_url_input.clear)

    def on_ok_button_triggered(self):
        logger.debug("User clicked OK and adds a new card to the current page.")
        card = self._create_card_from_user_input()
        self.card_database.add_missing_information(card)
        self.card_added.emit(card)

    @pyqtSlot(mtg_proxy_printer.model.carddb.Card)
    def card_added_debug_slot(self, card):
        QMessageBox.information(
            self, "Adding cards not implemented",
            f"Selected card:\n{card.name=}\n{card.set_abbr=}\n{card.collector_number=}\n{card.language=}\n{card.image_uri=}",
            QMessageBox.Ok, QMessageBox.Ok
        )
