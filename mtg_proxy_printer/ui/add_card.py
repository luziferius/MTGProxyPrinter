#  Copyright © 2020-2026  Thomas Hess <thomas.hess@udo.edu>
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


from typing import Type

from PySide6.QtCore import QStringListModel, Slot, Signal, Qt, QItemSelectionModel, QItemSelection, \
    QSortFilterProxyModel, QModelIndex, QAbstractItemModel
from PySide6.QtWidgets import QWidget, QDialogButtonBox
from PySide6.QtGui import QIcon

import mtg_proxy_printer.model.card
from mtg_proxy_printer.async_tasks.image_downloader import SingleDownloadTask
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard
import mtg_proxy_printer.model.string_list
from mtg_proxy_printer.model.carddb import CardDatabase, CardIdentificationData
import mtg_proxy_printer.model.document
import mtg_proxy_printer.settings
from mtg_proxy_printer.model.card import MTGSet
from mtg_proxy_printer.model.imagedb import ImageDatabase
from mtg_proxy_printer.ui.common import load_ui_from_file

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

try:
    from mtg_proxy_printer.ui.generated.add_card_widget.vertical import Ui_VerticalAddCardWidget
    from mtg_proxy_printer.ui.generated.add_card_widget.horizontal import Ui_HorizontalAddCardWidget
except ModuleNotFoundError:
    Ui_VerticalAddCardWidget = load_ui_from_file("add_card_widget/vertical")
    Ui_HorizontalAddCardWidget = load_ui_from_file("add_card_widget/horizontal")


__all__ = [
    "AddCardWidget",
    "VerticalAddCardWidget",
    "HorizontalAddCardWidget",
]

UiTypes = Type[Ui_VerticalAddCardWidget] | Type[Ui_HorizontalAddCardWidget]
StandardButton = QDialogButtonBox.StandardButton
ItemDataRole = Qt.ItemDataRole
SelectionFlag = QItemSelectionModel.SelectionFlag


class AddCardWidget(QWidget):

    request_run_async_task = Signal(SingleDownloadTask)

    def __init__(self, ui_class: UiTypes, parent: QWidget | None = None):
        super().__init__(parent)
        logger.debug(f"Creating {self.__class__.__name__} instance")
        self.ui = ui = ui_class()
        ui.setupUi(self)
        self.card_db: CardDatabase = CardDatabase.main_instance
        self.card_db.card_data_updated.connect(lambda: self.card_name_filter_updated(ui.card_name_filter.text()))
        self.image_db: ImageDatabase = None
        self.language_model = self._setup_language_combo_box()
        self.card_name_model, self.card_name_filter_model = self._setup_card_name_box()
        self.set_name_model, self.set_name_filter_model = self._setup_set_name_box()
        self.collector_number_model = self._setup_collector_number_box()
        self._setup_button_box()
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _setup_button_box(self):
        box = self.ui.button_box
        ok_button = box.button(StandardButton.Ok)
        reset_button = box.button(StandardButton.Reset)
        ok_button.setEnabled(False)
        ok_button.clicked.connect(self.ok_button_triggered)
        reset_button.clicked.connect(self.reset)
        buttons_with_icons = [
            (StandardButton.Reset, "edit-undo"),
            (StandardButton.Ok, "dialog-ok"),
        ]
        for role, icon in buttons_with_icons:
            button = box.button(role)
            if button.icon().isNull():
                button.setIcon(QIcon.fromTheme(icon))

    def _setup_language_combo_box(self) -> QStringListModel:
        preferred_language = mtg_proxy_printer.settings.settings["cards"]["preferred-language"]
        model = QStringListModel([preferred_language], self)
        self.ui.language_combo_box.setModel(model)
        self.ui.language_combo_box.currentTextChanged.connect(self.language_combo_box_changed)
        return model

    def _setup_card_name_box(self) -> tuple[QStringListModel, QSortFilterProxyModel]:
        card_name_list = self.ui.card_name_list
        model = QStringListModel([], self)
        filter_model = self._create_filter_model(model)
        card_name_list.setModel(filter_model)
        card_name_list.selectionModel().selectionChanged.connect(self.card_name_list_selection_changed)
        self.ui.card_name_filter.textChanged.connect(filter_model.setFilterWildcard)
        self.ui.card_name_filter.textChanged.connect(self.card_name_filter_updated)
        return model, filter_model

    def _setup_set_name_box(self) -> tuple[mtg_proxy_printer.model.string_list.PrettySetListModel, QSortFilterProxyModel]:
        set_name_list = self.ui.set_name_list
        model = mtg_proxy_printer.model.string_list.PrettySetListModel(self)
        filter_model = self._create_filter_model(model)
        set_name_list.setModel(filter_model)
        set_name_list.selectionModel().selectionChanged.connect(self.set_name_list_selection_changed)
        self.ui.set_name_filter.textChanged.connect(filter_model.setFilterWildcard)
        self.ui.set_name_filter.textChanged.connect(self.set_name_filter_updated)
        return model, filter_model

    def _create_filter_model(self, source_model: QAbstractItemModel) -> QSortFilterProxyModel:
        filter_model = QSortFilterProxyModel(
            self, filterCaseSensitivity=Qt.CaseSensitivity.CaseInsensitive,
            filterKeyColumn=0, filterRole=ItemDataRole.DisplayRole,
            dynamicSortFilter=True,
        )
        filter_model.setSourceModel(source_model)
        return filter_model

    def _setup_collector_number_box(self) -> QStringListModel:
        model = QStringListModel([], self.ui.collector_number_list)
        self.set_name_model.modelReset.connect(lambda: self.ui.collector_number_box.setEnabled(False))
        self.set_name_model.modelReset.connect(lambda: model.setStringList([]))

        self.ui.collector_number_list.setModel(model)
        self.ui.collector_number_list.selectionModel().selectionChanged.connect(
            self.collector_number_list_selection_changed
        )
        return model

    @Slot(QItemSelection)
    def card_name_list_selection_changed(self, current: QItemSelection):
        logger.info("Currently selected card changed.")
        if not current.indexes():
            self.ui.set_name_list.selectionModel().clearSelection()
            return
        current_model_index = current.indexes()[0]
        valid = current_model_index.isValid()
        self.ui.set_name_box.setEnabled(valid)
        if valid:
            card_name = current_model_index.data(ItemDataRole.DisplayRole)
            sets = self.card_db.find_sets_matching(card_name, self.current_language)
            logger.debug(f'Selected: "{card_name}", language: {self.current_language}, matching {len(sets)} sets')
            self.set_name_model.set_set_data(sets)
            self.ui.set_name_filter.clear()
            self.ui.set_name_list.selectionModel().select(
                self.set_name_model.createIndex(0, 0), SelectionFlag.ClearAndSelect)

    @Slot(QItemSelection)
    def set_name_list_selection_changed(self, current: QItemSelection):
        if not current.indexes():
            self.ui.collector_number_list.selectionModel().clearSelection()
            return
        logger.debug("Currently selected set changed.")
        current_model_index = current.indexes()[0]
        valid = current_model_index.isValid()
        self.ui.collector_number_box.setEnabled(valid)
        if valid:
            mtg_set: MTGSet = current_model_index.data(ItemDataRole.EditRole)
            collector_numbers = self.card_db.find_collector_numbers_matching(
                self.current_card_name, mtg_set.code, self.current_language
            )
            logger.debug(
                f'Selected: "{mtg_set.code}", language: {self.current_language}, matching {len(collector_numbers)} prints')
            self.collector_number_model.setStringList(collector_numbers)
            self.ui.collector_number_list.selectionModel().select(
                self.collector_number_model.createIndex(0, 0), SelectionFlag.ClearAndSelect)

    @Slot(QItemSelection)
    def collector_number_list_selection_changed(self, current: QItemSelection):
        something_is_selected = bool(current.indexes())
        self.ui.button_box.button(StandardButton.Ok).setEnabled(something_is_selected)

    @Slot(str)
    def card_name_filter_updated(self, card_name_filter: str):
        logger.debug(f'Card name filter changed to: "{card_name_filter}"')
        if self.current_card_name is None:
            self.set_name_model.set_set_data([])
            self.ui.set_name_box.setDisabled(True)

    @Slot(str)
    def set_name_filter_updated(self, set_name_filter: str):
        logger.debug(f'Set name/abbreviation filter changed to: "{set_name_filter}"')
        if self.current_set_name is None:
            self.collector_number_model.setStringList([])
            self.ui.collector_number_box.setDisabled(True)

    @Slot(str)
    def language_combo_box_changed(self, new_language: str):
        logger.info(f'Selected language changed to: "{new_language}"')
        card_names = self.card_db.get_card_names(new_language)
        self.card_name_model.setStringList(card_names)
        self.set_name_model.set_set_data([])
        self.ui.set_name_box.setEnabled(False)

    def set_databases(self, image_db: ImageDatabase):
        logger.debug("About to set the image database")
        self.image_db = image_db
        preferred_language = mtg_proxy_printer.settings.settings["cards"]["preferred-language"]
        languages = self.card_db.get_all_languages()
        if not languages:
            languages = [preferred_language]
        self.language_model.setStringList(languages)
        self.ui.language_combo_box.setCurrentText(preferred_language)
        logger.info("Card database set.")

    def _read_card_data_from_ui(self) -> CardIdentificationData:
        card = CardIdentificationData(
            self.current_language, self.current_card_name, self.current_set_name, self.current_collector_number
        )
        return card

    @Slot(str)
    def on_settings_preferred_language_changed(self, new_preferred_language: str):
        if self.language_model.stringList():
            self.ui.language_combo_box.setCurrentIndex(
                self.language_model.stringList().index(new_preferred_language)
            )
        self.language_combo_box_changed(new_preferred_language)

    @Slot()
    def ok_button_triggered(self):
        logger.info("User clicked OK and adds a new card to the current page.")
        card_data = self._read_card_data_from_ui()
        card = self.card_db.get_cards_from_data(card_data)[0]
        copies = self.ui.copies_input.value()
        self._log_added_card(card, copies)
        action = ActionAddCard(card, copies)
        self.request_run_async_task.emit(SingleDownloadTask(self.image_db, action))
        add_opposing_faces_enabled = mtg_proxy_printer.settings.settings["cards"].getboolean(
            "automatically-add-opposing-faces"
        )
        if add_opposing_faces_enabled and (opposing_face := self.card_db.get_opposing_face(card)) is not None:
            logger.info(
                "Card is double faced and adding opposing faces is enabled, automatically adding the other face.")
            self._log_added_card(opposing_face, copies)
            self.request_run_async_task.emit(SingleDownloadTask(self.image_db, ActionAddCard(opposing_face, copies)))

    @staticmethod
    def _log_added_card(card: mtg_proxy_printer.model.card.Card, copies: int):
        logger.debug(f"Adding {copies}× [{card.set.code.upper()}:{card.collector_number}] {card.name}")

    @Slot()
    def reset(self):
        logger.info("User hit the Reset button, resetting…")
        self.ui.collector_number_list.clearSelection()
        self.collector_number_model.setStringList([])
        self.ui.set_name_list.clearSelection()
        self.set_name_model.set_set_data([])
        self.ui.card_name_list.clearSelection()
        self.ui.card_name_filter.clear()
        self.ui.set_name_filter.clear()
        self.ui.copies_input.setValue(1)

    @property
    def current_language(self) -> str:
        return self.ui.language_combo_box.currentText()

    @property
    def current_card_name(self) -> str | None:
        match self.ui.card_name_list.selectedIndexes():
            case [QModelIndex() as index]:
                return index.data(ItemDataRole.DisplayRole)
            case _:
                return None

    @property
    def current_set_name(self) -> str | None:
        match self.ui.set_name_list.selectedIndexes():
            case [QModelIndex() as index]:
                return index.data(ItemDataRole.EditRole).code
            case _:
                return None

    @property
    def current_collector_number(self) -> str | None:
        match self.ui.collector_number_list.selectedIndexes():
            case [QModelIndex() as index]:
                return index.data(ItemDataRole.DisplayRole)
            case _:
                return None


class VerticalAddCardWidget(AddCardWidget):

    def __init__(self, parent: QWidget | None = None):
        super().__init__(Ui_VerticalAddCardWidget, parent)


class HorizontalAddCardWidget(AddCardWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(Ui_HorizontalAddCardWidget, parent)
