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

from PyQt5.QtCore import QStringListModel, pyqtSlot
from PyQt5.QtWidgets import QWidget, QDialogButtonBox, QLineEdit, QSpinBox, QComboBox

import mtg_proxy_printer.model.carddb
import mtg_proxy_printer.settings
from mtg_proxy_printer.ui.common import inherits_from_ui_file_with_name

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


class AddCardWidget(*inherits_from_ui_file_with_name("add_card_widget")):

    def __init__(self, parent: QWidget = None):
        super(AddCardWidget, self).__init__(parent)
        self.setupUi(self)
        self.card_database: mtg_proxy_printer.model.carddb.CardDatabase = None
        self.language_combo_box: QComboBox
        self.language_combo_box.currentTextChanged.connect(self.update_card_name_model)
        self.language_model = None
        self.card_name_search: QComboBox
        self.card_name_search.lineEdit().setPlaceholderText("Search by card name")
        self.card_name_search.lineEdit().setClearButtonEnabled(True)
        self.card_name_model = QStringListModel([], self.card_name_search)
        self.card_name_search.setModel(self.card_name_model)
        self.set_name_search: QComboBox
        self.set_name_search.lineEdit().setPlaceholderText("Search by released set")
        self.set_name_search.lineEdit().setClearButtonEnabled(True)
        self.set_name_model = QStringListModel([], self.set_name_search)
        self.set_name_search.setModel(self.set_name_model)
        self.collectors_number_search: QComboBox
        self.collectors_number_search.lineEdit().setPlaceholderText("Number")
        self.collectors_number_search.lineEdit().setClearButtonEnabled(True)
        self.copies_input: QSpinBox
        self.scryfall_url_input: QLineEdit
        self._connect_reset_button()
        self.button_box.button(QDialogButtonBox.Ok).clicked.connect(self.on_ok_button_triggered)
        logger.info(f"Created {self.__class__.__name__} instance.")

    @pyqtSlot(str)
    def update_card_name_model(self, language: str):
        if self.card_database is not None:
            card_names = self.card_database.get_card_names(language)
            self.card_name_model.setStringList(card_names)
            self.card_name_search.lineEdit().clear()

    def update_set_name_model(self):
        if self.card_database is not None:
            set_names = self.card_database.get_sets()
            self.set_name_model.setStringList(set_names)
            self.set_name_search.lineEdit().clear()

    def set_card_database(self, card_db: mtg_proxy_printer.model.carddb.CardDatabase):
        self.card_database = card_db
        preferred_language = mtg_proxy_printer.settings.settings["images"]["preferred-language"]
        self.update_card_name_model(preferred_language)
        self.update_set_name_model()

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
        self.parent().parent().nothing_happens_box.show()
        pass
