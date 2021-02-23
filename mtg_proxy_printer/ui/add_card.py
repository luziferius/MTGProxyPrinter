# Copyright (C) 2020, 2021 Thomas Hess <thomas.hess@udo.edu>

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

from PyQt5.QtCore import QStringListModel, pyqtSlot, pyqtSignal, Qt, QItemSelectionModel, QTimer, QItemSelection
from PyQt5.QtWidgets import QWidget, QDialogButtonBox, QLineEdit, QSpinBox, QComboBox, QListView, QPushButton

import mtg_proxy_printer.model.string_list
import mtg_proxy_printer.model.carddb
import mtg_proxy_printer.model.document
import mtg_proxy_printer.settings
from mtg_proxy_printer.ui.common import inherits_from_ui_file_with_name, BlockedSignals

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


class AddCardWidget(*inherits_from_ui_file_with_name("horizontal_search_layout/add_card_widget")):

    card_added = pyqtSignal(mtg_proxy_printer.model.carddb.Card, int)

    def __init__(self, parent: QWidget = None):
        super(AddCardWidget, self).__init__(parent)
        self.setupUi(self)
        self.card_database: mtg_proxy_printer.model.carddb.CardDatabase = None
        self.language_model = self._setup_language_combo_box()
        self.card_name_model = self._setup_card_name_box()
        self.set_name_model = self._setup_set_name_box()
        self.collector_number_model = self._setup_collector_number_box()
        self._setup_button_box()
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _setup_button_box(self):
        ok_button: QPushButton = self.button_box.button(QDialogButtonBox.Ok)
        reset_button: QPushButton = self.button_box.button(QDialogButtonBox.Reset)
        ok_button.setEnabled(False)
        reset_button.clicked.connect(ok_button.setEnabled)
        self.button_box.button(QDialogButtonBox.Ok).clicked.connect(self.on_ok_button_triggered)
        self.button_box.button(QDialogButtonBox.Reset).clicked.connect(self.reset)

    def _setup_language_combo_box(self) -> QStringListModel:
        self.language_combo_box: QComboBox
        self.language_combo_box.currentTextChanged.connect(self.on_language_combo_box_changed)
        model = QStringListModel([], self.language_combo_box)
        self.language_combo_box.setModel(model)
        return model

    def _setup_card_name_box(self) -> QStringListModel:
        self.card_name_filter: QLineEdit
        self.card_name_list: QListView
        model = QStringListModel([], self.card_name_list)
        self.card_name_list.setModel(model)
        self.card_name_list.selectionModel().selectionChanged.connect(self.on_card_name_list_selection_changed)
        self.card_name_filter.textChanged.connect(self.on_card_name_filter_updated)
        return model

    def _setup_set_name_box(self) -> mtg_proxy_printer.model.string_list.PrettySetListModel:
        self.set_name_filter: QLineEdit
        self.set_name_list: QListView
        model = mtg_proxy_printer.model.string_list.PrettySetListModel([], self.set_name_list)
        self.card_name_model.rowsRemoved.connect(lambda: self.set_name_box.setEnabled(False))
        self.card_name_model.rowsRemoved.connect(lambda: model.set_set_data([]))

        self.set_name_list.setModel(model)
        self.set_name_list.selectionModel().selectionChanged.connect(self.on_set_name_list_selection_changed)
        self.set_name_filter.textChanged.connect(self.on_set_name_filter_updated)
        return model

    def _setup_collector_number_box(self) -> QStringListModel:
        self.collector_number_list: QListView
        model = QStringListModel([], self.collector_number_list)
        self.set_name_model.rowsRemoved.connect(lambda: self.collector_number_box.setEnabled(False))
        self.set_name_model.rowsRemoved.connect(lambda: model.setStringList([]))

        self.collector_number_list.setModel(model)
        self.collector_number_list.selectionModel().selectionChanged.connect(
            self.on_collector_number_list_selection_changed
        )
        return model

    @pyqtSlot(QItemSelection)
    def on_card_name_list_selection_changed(self, current: QItemSelection):
        self.set_name_list: QListView
        if not current.indexes():
            self.set_name_list.selectionModel().clearSelection()
            return
        current_model_index = current.indexes()[0]
        valid = current_model_index.isValid()
        self.set_name_box.setEnabled(valid)
        if valid:
            sets = self.card_database.find_sets_matching(
                current_model_index.data(Qt.DisplayRole),
                self.current_language
            )
            self.set_name_model.set_set_data(sets)
            # Converts a recursive call structure into a sequential call structure, which is required here
            QTimer.singleShot(
                0, lambda: self.set_name_list.selectionModel().select(
                        self.set_name_model.createIndex(0, 0), QItemSelectionModel.ClearAndSelect
                ))

    @pyqtSlot(QItemSelection)
    def on_set_name_list_selection_changed(self, current: QItemSelection):
        self.collector_number_list: QListView
        if not current.indexes():
            self.collector_number_list.selectionModel().clearSelection()
            return
        current_model_index = current.indexes()[0]
        valid = current_model_index.isValid()
        self.collector_number_box.setEnabled(valid)
        if valid:
            collector_numbers = self.card_database.find_collector_numbers_matching(
                self.current_card_name, current_model_index.data(Qt.EditRole), self.current_language
            )
            self.collector_number_model.setStringList(collector_numbers)
            # Converts a recursive call structure into a sequential call structure, which is required here
            QTimer.singleShot(
                0, lambda: self.collector_number_list.selectionModel().select(
                    self.collector_number_model.createIndex(0, 0), QItemSelectionModel.ClearAndSelect
                ))

    @pyqtSlot(QItemSelection)
    def on_collector_number_list_selection_changed(self, current: QItemSelection):
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(bool(current.indexes()))

    def _create_card_from_user_input(self):
        card = mtg_proxy_printer.model.carddb.Card(
            card_name if (card_name := self.card_name_search.currentText()) else None,
            set_abbreviation if (set_abbreviation := self.set_name_search.currentText()) else None,
            collector_number if (collector_number := self.collectors_number_search.currentText()) else None,
            self.language_combo_box.currentText()
        )
        return card

    @pyqtSlot(str)
    def on_card_name_filter_updated(self, card_name_filter: str):
        selected_card_name = self.current_card_name
        card_names = self.card_database.get_card_names(self.current_language, card_name_filter)
        self.card_name_model.setStringList(card_names)

        if selected_card_name in card_names:
            self.card_name_list.selectionModel().select(
                self.card_name_model.createIndex(card_names.index(selected_card_name), 0),
                QItemSelectionModel.ClearAndSelect
            )
        else:
            self.set_name_model.set_set_data([])
            self.set_name_box.setDisabled(True)

    @pyqtSlot(str)
    def on_set_name_filter_updated(self, set_name_filter: str):
        set_names = self.card_database.find_sets_matching(
            self.current_card_name, self.current_language, set_name_filter
        )
        self.set_name_model.set_set_data(set_names)

    @pyqtSlot(str)
    def on_language_combo_box_changed(self, new_language: str):
        card_names = self.card_database.get_card_names(new_language)
        self.card_name_model.setStringList(card_names)
        self.set_name_model.set_set_data([])
        self.set_name_box.setEnabled(False)

    def set_card_database(self, card_db: mtg_proxy_printer.model.carddb.CardDatabase):
        self.card_database = card_db
        languages = self.card_database.get_all_languages()
        if not languages:
            languages = [mtg_proxy_printer.settings.settings["images"]["preferred-language"]]
        self.language_model.setStringList(languages)

    def _create_new_card(self) -> mtg_proxy_printer.model.carddb.Card:
        card = mtg_proxy_printer.model.carddb.Card(
            self.current_card_name, self.current_set_name, self.current_collector_number, self.current_language
        )
        return card

    @pyqtSlot()
    def update_selected_language(self):
        self.language_combo_box: QComboBox
        if self.language_model.stringList():
            self.language_combo_box.setCurrentIndex(
                self.language_model.stringList().index(
                    mtg_proxy_printer.settings.settings["images"]["preferred-language"])
            )

    def on_ok_button_triggered(self):
        logger.debug("User clicked OK and adds a new card to the current page.")
        card = self._create_new_card()
        self.card_database.add_missing_information(card)
        self.copies_input: QSpinBox
        copies = self.copies_input.value()
        self.card_added.emit(card, copies)
        add_opposing_faces_enabled = mtg_proxy_printer.settings.settings["images"].getboolean(
            "automatically-add-opposing-faces"
        )
        if add_opposing_faces_enabled and (
                opposing_face := self.card_database.get_opposing_face(card)) is not None:
            self.card_added.emit(opposing_face, copies)

    @pyqtSlot()
    def reset(self):
        self.card_name_list: QListView
        self.collector_number_list.clearSelection()
        self.collector_number_model.setStringList([])
        self.set_name_list.clearSelection()
        self.set_name_model.set_set_data([])
        self.card_name_list.clearSelection()
        self.card_name_filter.clear()
        self.set_name_filter.clear()
        self.copies_input.setValue(1)

    @property
    def current_language(self) -> str:
        return self.language_combo_box.currentText()

    @property
    def current_card_name(self) -> typing.Optional[str]:
        self.card_name_list: QListView
        selected = self.card_name_list.selectedIndexes()
        if selected:
            return selected[0].data(Qt.DisplayRole)
        else:
            return None

    @property
    def current_set_name(self) -> typing.Optional[str]:
        self.set_name_list: QListView
        selected = self.set_name_list.selectedIndexes()
        if selected:
            return selected[0].data(Qt.EditRole)
        else:
            return None

    @property
    def current_collector_number(self) -> typing.Optional[str]:
        self.collector_number_list: QListView
        selected = self.collector_number_list.selectedIndexes()
        if selected:
            return selected[0].data(Qt.DisplayRole)
        else:
            return None
