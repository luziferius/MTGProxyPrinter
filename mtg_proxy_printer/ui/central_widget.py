# Copyright (C) 2020, 2021 Thomas Hess <thomas.hess@udo.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import functools
import math
import operator
import pathlib
from typing import Union, Type, Optional

from PyQt5.QtCore import pyqtSignal as Signal, pyqtSlot as Slot, QPersistentModelIndex, QItemSelectionModel, \
    QModelIndex, QPoint, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QAction, QMenu, QInputDialog, QFileDialog

import mtg_proxy_printer.app_dirs
import mtg_proxy_printer.settings
from mtg_proxy_printer.model.card_list import PageColumns
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.carddb import CardDatabase, Card, CardList, CheckCard, AnyCardType, AnyCardTypeForTypeCheck
from mtg_proxy_printer.model.imagedb import ImageDatabase
from mtg_proxy_printer.document_controller import DocumentAction
from mtg_proxy_printer.document_controller.card_actions import ActionRemoveCards, ActionAddCard
from mtg_proxy_printer.ui.item_delegates import ComboBoxItemDelegate

try:
    from mtg_proxy_printer.ui.generated.central_widget.columnar import Ui_CentralWidget_Columnar
    from mtg_proxy_printer.ui.generated.central_widget.grouped import Ui_CentralWidget_Grouped
    from mtg_proxy_printer.ui.generated.central_widget.tabbed_vertical import Ui_CentralWidget_Tabbed
except ModuleNotFoundError:
    from mtg_proxy_printer.ui.common import load_ui_from_file
    Ui_CentralWidget_Columnar = load_ui_from_file("central_widget/columnar")
    Ui_CentralWidget_Grouped = load_ui_from_file("central_widget/grouped")
    Ui_CentralWidget_Tabbed = load_ui_from_file("central_widget/tabbed_vertical")


from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


__all__ = [
    "CentralWidget",
]

UiType = Union[Type[Ui_CentralWidget_Grouped], Type[Ui_CentralWidget_Columnar], Type[Ui_CentralWidget_Tabbed]]


class CentralWidget(QWidget):

    request_action = Signal(DocumentAction)
    obtain_card_image = Signal(ActionAddCard)

    def __init__(self, parent: QWidget = None):
        logger.debug(f"Creating {self.__class__.__name__} instance.")
        super(CentralWidget, self).__init__(parent)
        ui_class = get_configured_central_widget_layout_class()
        logger.debug(f"Using central widget class {ui_class.__name__}")
        self.ui = ui_class()
        self.ui.setupUi(self)
        self.document: Document = None
        self.card_db: CardDatabase = None
        self.image_db: ImageDatabase = None
        self.combo_box_delegate = self._setup_page_card_table_view()
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _setup_page_card_table_view(self) -> ComboBoxItemDelegate:
        self.ui.page_card_table_view.customContextMenuRequested.connect(self.page_table_context_menu_requested)
        combo_box_delegate = ComboBoxItemDelegate(self.ui.page_card_table_view)
        self.ui.page_card_table_view.setItemDelegateForColumn(PageColumns.CollectorNumber, combo_box_delegate)
        self.ui.page_card_table_view.setItemDelegateForColumn(PageColumns.Set, combo_box_delegate)
        self.ui.page_card_table_view.setItemDelegateForColumn(PageColumns.Language, combo_box_delegate)
        return combo_box_delegate

    def set_data(self, document: Document, card_db: CardDatabase, image_db: ImageDatabase):
        self.document = document
        self.card_db = card_db
        self.image_db = image_db
        self.obtain_card_image.connect(image_db.fill_document_action_image)  # TODO: Why here?
        document.rowsAboutToBeRemoved.connect(self.on_document_rows_about_to_be_removed)
        document.loading_state_changed.connect(self.select_first_page)
        document.current_page_changed.connect(self.on_current_page_changed)
        self.request_action.connect(document.apply)
        self.ui.page_card_table_view.setModel(document)
        # Signal has to be connected here, because setModel() implicitly creates the QItemSelectionModel
        self.ui.page_card_table_view.selectionModel().selectionChanged.connect(
            self.parsed_cards_table_selection_changed)
        self.ui.page_renderer.set_document(document)
        self._setup_add_card_widget(card_db, image_db)
        self._setup_document_view(document)

    def _setup_add_card_widget(self, card_db: CardDatabase, image_db: ImageDatabase):
        self.ui.add_card_widget.set_card_database(card_db)
        self.ui.add_card_widget.request_action.connect(image_db.fill_document_action_image)

    def _setup_document_view(self, document: Document):
        self.ui.document_view.setModel(document)
        self.ui.document_view.selectionModel().currentChanged.connect(document.on_ui_selects_new_page)
        self.select_first_page()

    def page_table_context_menu_requested(self, pos: QPoint):
        view = self.ui.page_card_table_view
        if not (index := view.indexAt(pos)).isValid():
            logger.debug("Right clicked empty space in the page card table view, ignoring event")
            return
        logger.info(f"Page card table requests context menu at x={pos.x()}, y={pos.y()}, row={index.row()}")
        menu = QMenu(view)
        card: Card = index.data(Qt.ItemDataRole.UserRole)
        menu.addActions(self._create_add_copies_actions(card))
        if card.is_dfc:
            menu.addSeparator()
            self._create_add_check_card_actions(menu, card)
        if related_cards := self.card_db.find_related_cards(card):
            menu.addSeparator()
            self._create_add_related_actions(menu, related_cards)
        self._add_save_image_action(menu, card)
        menu.popup(view.viewport().mapToGlobal(pos))

    def _create_add_copies_actions(self, card: Union[AnyCardType, CardList], add_4th: bool = False):
        actions = [
            self._create_add_copies_action("Add 1 copy", 1, card),
            self._create_add_copies_action("Add 2 copies", 2, card),
            self._create_add_copies_action("Add 3 copies", 3, card),
            self._create_add_copies_action("Add copies …", None, card)
        ]
        if add_4th:
            actions.insert(-1, self._create_add_copies_action("Add 4 copies", 4, card),)
        return actions

    def _create_add_copies_action(self, label: str, count: Optional[int],
                                  card: Union[AnyCardType, CardList]):
        action = QAction(QIcon.fromTheme("list-add"), label, self.ui.page_card_table_view)
        action.triggered.connect(functools.partial(self._add_copies, card, count))
        return action

    def _create_add_check_card_actions(self, parent: QMenu, card: Card):
        other_face = self.card_db.get_opposing_face(card)
        front, back = sorted([card, other_face], key=operator.attrgetter("is_front"), reverse=True)
        check_card = CheckCard(front, back)
        actions = [
            self._create_add_copies_action("Add 1 copy", 1, check_card),
            self._create_add_copies_action("Add 2 copies", 2, check_card),
            self._create_add_copies_action("Add 3 copies", 3, check_card),
            self._create_add_copies_action("Add 4 copies", 4, check_card),
            self._create_add_copies_action("Add copies …", None, check_card)
        ]
        parent.addMenu("Generate DFC check card").addActions(actions)

    def _create_add_related_actions(self, parent: QMenu, related_cards: CardList) -> None:
        logger.debug(f"Found {len(related_cards)} related cards. Adding them to the context menu")
        parent.addMenu("All related cards").addActions(self._create_add_copies_actions(related_cards, True))
        for card in related_cards:
            parent.addMenu(card.name).addActions(self._create_add_copies_actions(card, True))

    def _add_copies(self, card: Union[AnyCardType, CardList], count: Optional[int]):
        nl = '\n'
        card_name = card.name if isinstance(card, AnyCardTypeForTypeCheck) else nl + nl.join(item.name for item in card)
        if count is None:
            count, success = QInputDialog.getInt(self, "Add copies", f"Add copies of {card_name}", 1, 1, 100)
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
        action = QAction(QIcon.fromTheme("document-save"), "Export image", parent)
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
            self, "Save card image", default_save_file, "Images (*.png *.bmp *.jpg)")  # type: str, str
        if result:
            card.image_file.save(result)
            logger.info(f"Exported image of card {card.name} to {result}")
        else:
            logger.debug("User cancelled file name selection. Cancelling image export.")

    @staticmethod
    def _get_default_image_save_path(card: Card) -> str:
        try:
            parent = mtg_proxy_printer.app_dirs.data_directories.user_pictures_path
        except AttributeError:
            parent = pathlib.Path.home()
        disallowed = str.maketrans('', '', '\\\n/:*?"<>|')  # Exclude newlines and characters restricted on Windows
        file_name = card.name.replace(" // ", " ").translate(disallowed).lstrip().rstrip(" \t.")
        logger.debug(f"Cleaned card name: '{file_name}'")
        return str(parent/f"{file_name}.png")

    @Slot()
    def parsed_cards_table_selection_changed(self):
        """Called whenever the selection in the page_card_table_view is changed. This manages the activation state
        of the “Remove selected” button, which should only be clickable, if there are cards selected."""
        selection_model = self.ui.page_card_table_view.selectionModel()
        self.ui.delete_selected_images_button.setDisabled(selection_model.selection().isEmpty())

    def on_current_page_changed(self, new_page: QPersistentModelIndex):
        self.ui.page_card_table_view.clearSelection()
        self.ui.page_card_table_view.setRootIndex(new_page.sibling(new_page.row(), new_page.column()))
        self.ui.page_card_table_view.setColumnHidden(PageColumns.Image, True)
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
            self.ui.page_card_table_view.setColumnWidth(column, new_size)

    def on_document_rows_about_to_be_removed(self, parent: QModelIndex, first: int, last: int):
        currently_selected_page = self.ui.document_view.currentIndex().row()
        is_page_index = not parent.isValid()
        if not is_page_index:
            # Not interested in removed cards here, so return if cards are about to be removed.
            return
        removed_pages = last - first + 1
        if currently_selected_page < self.document.rowCount()-removed_pages:
            # After removal, the current page remains within the document and stays valid. Nothing to do.
            return
        # Selecting a different page is required if the current page is going to be deleted.
        # So re-selecting the page is required to prevent exceptions. Without this, the document view creates invalid
        # model indices.
        new_page_to_select = max(0, first-1)
        logger.debug(
            f"Currently selected last page {currently_selected_page} about to be removed. New page to select: {new_page_to_select}")
        self.ui.document_view.setCurrentIndex(self.document.index(new_page_to_select, 0))

    @Slot()
    def on_delete_selected_images_button_clicked(self):
        multi_selection = self.ui.page_card_table_view.selectionModel().selectedRows()
        if multi_selection:
            rows = [index.row() for index in multi_selection]
            logger.debug(f"User removes {len(multi_selection)} items from the current page.")
            action = ActionRemoveCards(rows)
            self.request_action.emit(action)

    @Slot()
    def select_first_page(self, loading_in_progress: bool = False):
        if not loading_in_progress:
            logger.info("Loading finished. Selecting first page.")
            new_selection = self.document.index(0, 0)
            self.ui.document_view.selectionModel().select(new_selection, QItemSelectionModel.Select)
            self.document.on_ui_selects_new_page(new_selection)


def get_configured_central_widget_layout_class() -> UiType:
    gui_settings = mtg_proxy_printer.settings.settings["gui"]
    configured_layout = gui_settings["central-widget-layout"]
    if configured_layout == "horizontal":
        return Ui_CentralWidget_Grouped
    if configured_layout == "columnar":
        return Ui_CentralWidget_Columnar
    return Ui_CentralWidget_Tabbed
