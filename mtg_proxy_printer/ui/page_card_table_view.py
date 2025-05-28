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

import functools
import math
import operator
from pathlib import Path
from typing import Union, Optional

from PyQt5.QtCore import QPoint, Qt, pyqtSignal as Signal, pyqtSlot as Slot, QPersistentModelIndex
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableView, QWidget, QMenu, QAction, QInputDialog, QFileDialog

from mtg_proxy_printer.app_dirs import data_directories
from mtg_proxy_printer.document_controller import DocumentAction
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard, ActionRemoveCards
from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.model.card import Card, CheckCard, CardList, AnyCardType, AnyCardTypeForTypeCheck
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.document_page import PageColumns
from mtg_proxy_printer.ui.item_delegates import CollectorNumberEditorDelegate, SetEditorDelegate, LanguageEditorDelegate

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger
ItemDataRole = Qt.ItemDataRole


class PageCardTableView(QTableView):

    request_action = Signal(DocumentAction)
    obtain_card_image = Signal(ActionAddCard)
    changed_selection_is_empty = Signal(bool)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.customContextMenuRequested.connect(self.page_table_context_menu_requested)
        self._column_delegates = (
            self._setup_combo_box_item_delegate(),
            self._setup_language_delegate(),
            self._setup_set_delegate(),
        )
        self.card_db: CardDatabase = None

    def set_data(self, document: Document, card_db: CardDatabase):
        self.card_db = card_db
        self.setModel(document)
        self.request_action.connect(document.apply)
        document.current_page_changed.connect(self.on_current_page_changed)
        # Has to be set up here, because setModel() implicitly creates the QItemSelectionModel
        self.selectionModel().selectionChanged.connect(self._on_selection_changed)

    @Slot()
    def _on_selection_changed(self):
        is_empty = self.selectionModel().selection().isEmpty()
        self.changed_selection_is_empty.emit(is_empty)

    def _setup_combo_box_item_delegate(self):
        combo_box_delegate = CollectorNumberEditorDelegate(self)
        self.setItemDelegateForColumn(PageColumns.CollectorNumber, combo_box_delegate)
        return combo_box_delegate

    def _setup_language_delegate(self):
        delegate = LanguageEditorDelegate(self)
        self.setItemDelegateForColumn(PageColumns.Language, delegate)
        return delegate

    def _setup_set_delegate(self):
        delegate = SetEditorDelegate(self)
        self.setItemDelegateForColumn(PageColumns.Set, delegate)
        return delegate

    @Slot(QPoint)
    def page_table_context_menu_requested(self, pos: QPoint):
        if not (index := self.indexAt(pos)).isValid():
            logger.debug("Right clicked empty space in the page card table view, ignoring event")
            return
        logger.info(f"Page card table requests context menu at x={pos.x()}, y={pos.y()}, row={index.row()}")
        menu = QMenu(self)
        card: Card = index.data(ItemDataRole.UserRole)
        menu.addActions(self._create_add_copies_actions(card))
        if card.is_dfc:
            menu.addSeparator()
            self._create_add_check_card_actions(menu, card)
        if related_cards := self.card_db.find_related_cards(card):
            menu.addSeparator()
            self._create_add_related_actions(menu, related_cards)
        self._add_save_image_action(menu, card)
        menu.popup(self.viewport().mapToGlobal(pos))

    def _create_add_check_card_actions(self, parent: QMenu, card: Card):
        other_face = self.card_db.get_opposing_face(card)
        front, back = sorted([card, other_face], key=operator.attrgetter("is_front"), reverse=True)
        check_card = CheckCard(front, back)
        actions = [
            self._create_add_copies_action(
                self.tr("Add %n copies",
                        "Context menu action: Add additional card copies to the document", copy_count),
                copy_count, check_card)
            for copy_count in range(1, 5)
        ]
        actions.append(
            self._create_add_copies_action(
                self.tr("Add copies …",
                        "Context menu action: Add additional card copies to the document. "
                        "User will be asked for a number"),
                None, check_card))

        parent.addMenu(self.tr("Generate DFC check card")).addActions(actions)

    def _create_add_copies_actions(self, card: Union[AnyCardType, CardList], add_4th: bool = False):
        """
        Returns a list of QActions to add 1, 2, 3, optionally 4, and a user-defined number of copies of the given card.
        """
        actions = [
            self._create_add_copies_action(
                self.tr("Add %n copies","Context menu action: "
                        "Add additional card copies to the document", copy_count),
                copy_count, card)
            for copy_count in range(1, 4+add_4th)
        ]
        actions.append(self._create_add_copies_action(
            self.tr("Add copies …", "Context menu action: "
                    "Add additional card copies to the document. User will be asked for a number"),
            None, card))
        return actions

    def _create_add_copies_action(self, label: str, count: Optional[int],
                                  card: Union[AnyCardType, CardList]):
        action = QAction(QIcon.fromTheme("list-add"), label, self)
        action.triggered.connect(functools.partial(self._add_copies, card, count))
        return action

    def _create_add_related_actions(self, parent: QMenu, related_cards: CardList) -> None:
        logger.debug(f"Found {len(related_cards)} related cards. Adding them to the context menu")
        parent.addMenu(self.tr("All related cards")).addActions(self._create_add_copies_actions(related_cards, True))
        for card in related_cards:
            parent.addMenu(card.name).addActions(self._create_add_copies_actions(card, True))

    def _add_copies(self, card: Union[AnyCardType, CardList], count: Optional[int]):
        nl = '\n'
        card_name = card.name if isinstance(card, AnyCardTypeForTypeCheck) else nl + nl.join(item.name for item in card)
        if count is None:
            count, success = QInputDialog.getInt(
                self, self.tr("Add copies"), self.tr(
                    "Add copies of {card_name}",
                    "Asks the user for a number. Does not need plural forms").format(card_name=card_name),
                1, 1, 100)
            if not success:
                logger.info("User cancelled adding card copies")
                return
        logger.info(f"Add {count} × {card_name.replace(nl, ',')} via the context menu action")
        if isinstance(card, AnyCardTypeForTypeCheck):
            self._request_action_add_card(card, count)
        else:
            for item in card:
                self._request_action_add_card(item, count)

    def _request_action_add_card(self, card: AnyCardType, count: int):
        # If cards have images, request the action directly. This happens when adding copies of already added cards
        # and is required for custom cards. Otherwise, request the image from the image database. Cards without images
        # at this point are CheckCards or related cards.
        action = ActionAddCard(card, count)
        if card.image_file is None:
            self.obtain_card_image.emit(action)
        else:
            self.request_action.emit(action)

    def _add_save_image_action(self, parent: QMenu, card: AnyCardType):
        action = QAction(QIcon.fromTheme("document-save"), self.tr("Export image"), parent)
        action.setData(card)
        action.triggered.connect(self._on_save_image_action_triggered)
        parent.addSeparator()
        parent.addAction(action)

    @Slot()
    def _on_save_image_action_triggered(self):
        logger.info("User requests exporting card image.")
        action: QAction = self.sender()
        if action is None:
            logger.error("Action triggering _on_save_image_action_triggered not obtained!")
            return
        card: Card = action.data()
        default_save_file = self._get_default_image_save_path(card)
        result, _ = QFileDialog.getSaveFileName(
            self, self.tr("Save card image"), default_save_file, self.tr("Images (*.png *.bmp *.jpg)"))  # type: str, str
        if result:
            card.image_file.save(result)
            logger.info(f"Exported image of card {card.name} to {result}")
        else:
            logger.debug("User cancelled file name selection. Cancelling image export.")

    @staticmethod
    def _get_default_image_save_path(card: Card) -> str:
        try:
            parent = data_directories.user_pictures_path
        except AttributeError:
            parent = Path.home()
        disallowed = str.maketrans('', '', '\\\n/:*?"<>|')  # Exclude newlines and characters restricted on Windows
        file_name = card.name.replace(" // ", " ").translate(disallowed).lstrip().rstrip(" \t.")
        logger.debug(f"Cleaned card name: '{file_name}'")
        return str(parent/f"{file_name}.png")

    def on_current_page_changed(self, new_page: QPersistentModelIndex):
        self.clearSelection()
        self.setRootIndex(new_page.sibling(new_page.row(), new_page.column()))
        self.setColumnHidden(PageColumns.Image, True)
        # The size adjustments have to be done here,
        # because the width can only be set after the model root index to show has been set
        default_column_width = 102
        for column, scaling_factor in (
            (PageColumns.CardName, 1.7),
            (PageColumns.Set, 2),
            (PageColumns.CollectorNumber, 0.95),
            (PageColumns.Language, 0.8),
            (PageColumns.IsFront, 0.8),
        ):
            new_size = math.floor(default_column_width * scaling_factor)
            self.setColumnWidth(column, new_size)

    @Slot()
    def delete_selected_images(self):
        multi_selection = self.selectionModel().selectedRows()
        if multi_selection:
            rows = [index.row() for index in multi_selection]
            logger.debug(f"User removes {len(multi_selection)} items from the current page.")
            action = ActionRemoveCards(rows)
            self.request_action.emit(action)
