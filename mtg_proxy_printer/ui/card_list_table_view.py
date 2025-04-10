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

import math

from PyQt5.QtCore import Qt, pyqtSignal as Signal, pyqtSlot as Slot
from PyQt5.QtWidgets import QTableView, QWidget

from mtg_proxy_printer.model.card_list import CardListColumns, CardListModel
from mtg_proxy_printer.natsort import NaturallySortedSortFilterProxyModel
from mtg_proxy_printer.ui.item_delegates import CollectorNumberEditorDelegate, BoundedCopiesSpinboxDelegate, \
    CardSideSelectionDelegate, SetEditorDelegate, LanguageEditorDelegate

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger
ItemDataRole = Qt.ItemDataRole


class CardListTableView(QTableView):
    """
    This table view shows a CardListModel, and sets up all item delegates used for proper display and validation.

    """
    changed_selection_is_empty = Signal(bool)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._column_delegates = (
            self._setup_combo_box_item_delegate(),
            self._setup_language_delegate(),
            self._setup_copies_delegate(),
            self._setup_side_delegate(),
            self._setup_set_delegate(),
        )
        self.sort_model = NaturallySortedSortFilterProxyModel(self)

    def setModel(self, model: CardListModel):
        self.sort_model.setSourceModel(model)
        super().setModel(self.sort_model)
        # Has to be set up here, because setModel() implicitly creates the QItemSelectionModel
        self.selectionModel().selectionChanged.connect(self._on_selection_changed)
        # Now that the model is set and columns are discovered, set the column widths to reasonable values.
        self._setup_default_column_widths()

    @Slot()
    def _on_selection_changed(self):
        selection = self.selectionModel().selection()
        is_empty = selection.isEmpty()
        logger.debug(f"Selection changed: Currently selected cells: {selection.count()}")
        self.changed_selection_is_empty.emit(is_empty)

    def _setup_language_delegate(self):
        delegate = LanguageEditorDelegate(self)
        self.setItemDelegateForColumn(CardListColumns.Language, delegate)
        return delegate

    def _setup_combo_box_item_delegate(self) -> CollectorNumberEditorDelegate:
        delegate = CollectorNumberEditorDelegate(self)
        self.setItemDelegateForColumn(CardListColumns.CollectorNumber, delegate)
        return delegate

    def _setup_copies_delegate(self) -> BoundedCopiesSpinboxDelegate:
        delegate = BoundedCopiesSpinboxDelegate(self)
        self.setItemDelegateForColumn(CardListColumns.Copies, delegate)
        return delegate

    def _setup_side_delegate(self) -> CardSideSelectionDelegate:
        delegate = CardSideSelectionDelegate(self)
        self.setItemDelegateForColumn(CardListColumns.IsFront, delegate)
        return delegate

    def _setup_set_delegate(self) -> SetEditorDelegate:
        delegate = SetEditorDelegate(self)
        self.setItemDelegateForColumn(CardListColumns.Set, delegate)
        return delegate

    def _setup_default_column_widths(self):
        # These factors are empirically determined to give reasonable column sizes
        for column, scaling_factor in (
                (CardListColumns.Copies, 0.9),
                (CardListColumns.CardName, 2),
                (CardListColumns.Set, 2.75),
                (CardListColumns.CollectorNumber, 0.95),
                (CardListColumns.Language, 0.9)):
            new_size = math.floor(self.columnWidth(column) * scaling_factor)
            self.setColumnWidth(column, new_size)
