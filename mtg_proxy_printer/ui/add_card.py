# Copyright (C) 2020-2022 Thomas Hess <thomas.hess@udo.edu>

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

from PyQt5.QtCore import QStringListModel, pyqtSlot as Slot, pyqtSignal as Signal, Qt, QItemSelectionModel, QItemSelection
from PyQt5.QtWidgets import QWidget, QDialogButtonBox, QLineEdit, QSpinBox, QComboBox, QListView, QPushButton
from PyQt5.QtGui import QIcon

import mtg_proxy_printer.model.string_list
import mtg_proxy_printer.model.carddb
import mtg_proxy_printer.model.document
import mtg_proxy_printer.settings
from mtg_proxy_printer.ui.common import inherits_from_ui_file_with_name

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

__all__ = [
    "AddCardWidget",
    "VerticalAddCardWidget",
    "HorizontalAddCardWidget",
]


class AddCardWidget(QWidget):

    card_added = Signal(mtg_proxy_printer.model.carddb.Card, int)

    def __init__(self, parent: QWidget = None):
        super(AddCardWidget, self).__init__(parent)
        logger.debug(f"Creating {self.__class__.__name__} instance")
        self.setupUi(self)
        self.card_database: mtg_proxy_printer.model.carddb.CardDatabase = None
        self.language_model = self._setup_language_combo_box()
        self.card_name_model = self._setup_card_name_box()
        self.set_name_model = self._setup_set_name_box()
        self.collector_number_model = self._setup_collector_number_box()
        self._setup_button_box()
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _setup_button_box(self):
        box: QDialogButtonBox = self.button_box
        ok_button: QPushButton = box.button(QDialogButtonBox.Ok)
        reset_button: QPushButton = box.button(QDialogButtonBox.Reset)
        ok_button.setEnabled(False)
        ok_button.clicked.connect(self.ok_button_triggered)
        reset_button.clicked.connect(self.reset)
        buttons_with_icons = [
            (QDialogButtonBox.Reset, "edit-undo"),
            (QDialogButtonBox.Ok, "dialog-ok"),
        ]
        for role, icon in buttons_with_icons:
            button = box.button(role)
            if button.icon().isNull():
                button.setIcon(QIcon.fromTheme(icon))

    def _setup_language_combo_box(self) -> QStringListModel:
        self.language_combo_box: QComboBox
        self.language_combo_box.currentTextChanged.connect(self.language_combo_box_changed)
        preferred_language = mtg_proxy_printer.settings.settings["images"]["preferred-language"]
        model = QStringListModel([preferred_language], self.language_combo_box)
        with mtg_proxy_printer.ui.common.BlockedSignals(self.language_combo_box):
            self.language_combo_box.setModel(model)
        return model

    def _setup_card_name_box(self) -> QStringListModel:
        self.card_name_filter: QLineEdit
        self.card_name_list: QListView
        model = QStringListModel([], self.card_name_list)
        self.card_name_list.setModel(model)
        self.card_name_list.selectionModel().selectionChanged.connect(self.card_name_list_selection_changed)
        self.card_name_filter.textChanged.connect(self.card_name_filter_updated)
        return model

    def _setup_set_name_box(self) -> mtg_proxy_printer.model.string_list.PrettySetListModel:
        self.set_name_filter: QLineEdit
        self.set_name_list: QListView
        model = mtg_proxy_printer.model.string_list.PrettySetListModel(self.set_name_list)
        self.card_name_model.rowsRemoved.connect(lambda: self.set_name_box.setEnabled(False))
        self.card_name_model.rowsRemoved.connect(lambda: model.set_set_data([]))

        self.set_name_list.setModel(model)
        self.set_name_list.selectionModel().selectionChanged.connect(self.set_name_list_selection_changed)
        self.set_name_filter.textChanged.connect(self.set_name_filter_updated)
        return model

    def _setup_collector_number_box(self) -> QStringListModel:
        self.collector_number_list: QListView
        model = QStringListModel([], self.collector_number_list)
        self.set_name_model.rowsRemoved.connect(lambda: self.collector_number_box.setEnabled(False))
        self.set_name_model.rowsRemoved.connect(lambda: model.setStringList([]))

        self.collector_number_list.setModel(model)
        self.collector_number_list.selectionModel().selectionChanged.connect(
            self.collector_number_list_selection_changed
        )
        return model

    @Slot(QItemSelection)
    def card_name_list_selection_changed(self, current: QItemSelection):
        logger.info("Currently selected card changed.")
        self.set_name_list: QListView
        if not current.indexes():
            self.set_name_list.selectionModel().clearSelection()
            return
        current_model_index = current.indexes()[0]
        valid = current_model_index.isValid()
        self.set_name_box.setEnabled(valid)
        if valid:
            card_name = current_model_index.data(Qt.DisplayRole)
            sets = self.card_database.find_sets_matching(card_name, self.current_language)
            logger.debug(f'Selected: "{card_name}", language: {self.current_language}, matching {len(sets)} sets')
            self.set_name_model.set_set_data(sets)
            self.set_name_filter.clear()
            self.set_name_list.selectionModel().select(
                self.set_name_model.createIndex(0, 0), QItemSelectionModel.ClearAndSelect)

    @Slot(QItemSelection)
    def set_name_list_selection_changed(self, current: QItemSelection):
        self.collector_number_list: QListView
        if not current.indexes():
            self.collector_number_list.selectionModel().clearSelection()
            return
        logger.debug("Currently selected set changed.")
        current_model_index = current.indexes()[0]
        valid = current_model_index.isValid()
        self.collector_number_box.setEnabled(valid)
        if valid:
            set_abbr = current_model_index.data(Qt.EditRole)
            collector_numbers = self.card_database.find_collector_numbers_matching(
                self.current_card_name, set_abbr, self.current_language
            )
            logger.debug(
                f'Selected: "{set_abbr}", language: {self.current_language}, matching {len(collector_numbers)} prints')
            self.collector_number_model.setStringList(collector_numbers)
            self.collector_number_list.selectionModel().select(
                self.collector_number_model.createIndex(0, 0), QItemSelectionModel.ClearAndSelect)

    @Slot(QItemSelection)
    def collector_number_list_selection_changed(self, current: QItemSelection):
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(bool(current.indexes()))

    @Slot(str)
    def card_name_filter_updated(self, card_name_filter: str):
        logger.debug(f'Card name filter changed to: "{card_name_filter}"')
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

    @Slot(str)
    def set_name_filter_updated(self, set_name_filter: str):
        logger.debug(f'Set name/abbreviation filter changed to: "{set_name_filter}"')
        set_names = self.card_database.find_sets_matching(
            self.current_card_name, self.current_language, set_name_filter
        )
        self.set_name_model.set_set_data(set_names)

    @Slot(str)
    def language_combo_box_changed(self, new_language: str):
        logger.info(f'Selected language changed to: "{new_language}"')
        card_names = self.card_database.get_card_names(new_language)
        self.card_name_model.setStringList(card_names)
        self.set_name_model.set_set_data([])
        self.set_name_box.setEnabled(False)

    def set_card_database(self, card_db: mtg_proxy_printer.model.carddb.CardDatabase):
        logger.info("Card database set.")
        self.card_database = card_db
        languages = self.card_database.get_all_languages()
        if not languages:
            languages = [mtg_proxy_printer.settings.settings["images"]["preferred-language"]]
        self.language_model.setStringList(languages)

    def _read_card_data_from_ui(self) -> mtg_proxy_printer.model.carddb.CardIdentificationData:
        card = mtg_proxy_printer.model.carddb.CardIdentificationData(
            self.current_language, self.current_card_name, self.current_set_name, self.current_collector_number
        )
        return card

    @Slot()
    def update_selected_language(self):
        self.language_combo_box: QComboBox
        if self.language_model.stringList():
            self.language_combo_box.setCurrentIndex(
                self.language_model.stringList().index(
                    mtg_proxy_printer.settings.settings["images"]["preferred-language"])
            )
        self.language_combo_box_changed(self.language_combo_box.currentText())

    def ok_button_triggered(self):
        logger.info("User clicked OK and adds a new card to the current page.")
        card_data = self._read_card_data_from_ui()
        card = self.card_database.get_cards_from_data(card_data)[0]
        self.copies_input: QSpinBox
        copies = self.copies_input.value()
        self._log_added_card(card, copies)
        self.card_added.emit(card, copies)
        add_opposing_faces_enabled = mtg_proxy_printer.settings.settings["images"].getboolean(
            "automatically-add-opposing-faces"
        )
        if add_opposing_faces_enabled and (opposing_face := self.card_database.get_opposing_face(card)) is not None:
            logger.info(
                "Card is double faced and adding opposing faces is enabled, automatically adding the other face.")
            self._log_added_card(opposing_face, copies)
            self.card_added.emit(opposing_face, copies)

    @staticmethod
    def _log_added_card(card: mtg_proxy_printer.model.carddb.Card, copies: int):
        logger.debug(f"Adding {copies}× [{card.set.code.upper()}:{card.collector_number}] {card.name}")

    @Slot()
    def reset(self):
        logger.info("User hit the Reset button, resetting…")
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


class VerticalAddCardWidget(AddCardWidget, *inherits_from_ui_file_with_name(f"add_card_widget/vertical")):
    pass


class HorizontalAddCardWidget(AddCardWidget, *inherits_from_ui_file_with_name(f"add_card_widget/horizontal")):
    pass
