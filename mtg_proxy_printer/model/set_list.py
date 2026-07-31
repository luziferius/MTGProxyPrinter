#  Copyright © 2020-2026 Thomas Hess <thomas.hess@udo.edu>
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

import dataclasses
import enum
from typing import Callable
import typing

from PySide6 import __version_info__ as PySide6Version
from PySide6.QtCore import Qt, QModelIndex, QAbstractItemModel, QObject, QModelRoleDataSpan, \
    QUrl, QModelRoleData, QSortFilterProxyModel
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

from mtg_proxy_printer.model.card import MTGSet
from mtg_proxy_printer.logger import get_logger
from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.units_and_sizes import ConfigParser
from mtg_proxy_printer.settings import DEFAULT_SETTINGS

logger = get_logger(__name__)
del get_logger


Orientation = Qt.Orientation
CheckState = Qt.CheckState

# Used roles
ItemDataRole = Qt.ItemDataRole
EditRole = ItemDataRole.EditRole
DisplayRole = ItemDataRole.DisplayRole
UserRole = ItemDataRole.UserRole
CheckStateRole = ItemDataRole.CheckStateRole
BackgroundRole = ItemDataRole.BackgroundRole
ScryfallQueryRole = ItemDataRole(UserRole.value + 1)

# The flag values
ItemFlag = Qt.ItemFlag
# Only the first column can have children and be tree nodes. Everything else is a leaf without children
NodeDataFlags  = ItemFlag.ItemIsEnabled
LeafDataFlags = NodeDataFlags | ItemFlag.ItemNeverHasChildren  # noqa
IsHiddenFlags =  LeafDataFlags | ItemFlag.ItemIsUserCheckable  # noqa
PreferenceWeightsFlags = LeafDataFlags | ItemFlag.ItemIsEditable  # noqa


@enum.verify(enum.EnumCheck.CONTINUOUS, enum.EnumCheck.UNIQUE)
class ModelColumns(enum.IntEnum):
    name = 0
    is_hidden = enum.auto()
    preference_weights = enum.auto()
    release_date = enum.auto()
    scryfall_query = enum.auto()


@dataclasses.dataclass()
class SetContainer:
    """Tree item stored in the MTGSetTreeModel."""
    set: MTGSet
    scryfall_query: QUrl
    # The editable columns. MTGSet is frozen, so store the data in the mutable container
    is_hidden: bool = dataclasses.field(init=False)
    preference_weight: int = dataclasses.field(init=False)
    highlight_is_hidden: QColor | None = None
    highlight_preference_weight: QColor | None = None
    # Tree structure
    children: list["SetContainer"] = dataclasses.field(default_factory=list)
    parent: typing.Optional["SetContainer"] = None

    def __post_init__(self):
        self.is_hidden = self.set.is_hidden
        self.preference_weight = self.set.preference_weight


class SetTreeIndex(QModelIndex):
    """QModelIndex created by MTGSetTreeModel.
    Type hinting stub used to annotate the type of the internally held reference."""
    internalPointer: Callable[[], SetContainer]


INVALID_INDEX = SetTreeIndex()


class MTGSetTreeModel(QAbstractItemModel):
    """
    A model used to show all MTG sets, with sub-sets as children. Sub-sets contain associated tokens,
    promo printings, and similar cards. So for parent set AFR, there's the token set TAFR, and the promo printings in PAFR.

    Also exposes the "set_filter_active" flag and "preference score" as editable columns,
    and is used by the PrintingPreferencePage settings page to configure these.
    """
    createIndex: Callable[[int, int, SetContainer], SetTreeIndex]
    ModelColumns = ModelColumns

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.header = {
            ModelColumns.name: f'  {self.tr("Set", "Set filter table header")}  ',
            ModelColumns.is_hidden: f'  {self.tr("Completely hide matching cards", "Set filter table header")}  ',
            ModelColumns.preference_weights: f'  {self.tr("Set preference", "Set filter table header")}  ',
            ModelColumns.release_date: f'  {self.tr("Release date", "Set filter table header")}  ',
            ModelColumns.scryfall_query: "",
        }
        self.set_data: list[SetContainer] = []
        self._hiding_includes_children = False

    @property
    def hiding_includes_children(self) -> bool:
        return self._hiding_includes_children

    @hiding_includes_children.setter
    def hiding_includes_children(self, value: bool):
        self._hiding_includes_children = value

    def headerData(self, section: int, orientation: Orientation, role: ItemDataRole = DisplayRole) \
            -> str | None:
        if role == ItemDataRole.DisplayRole and orientation == Orientation.Horizontal:
            # Returns None for unknown columns
            return self.header.get(ModelColumns(section))
        return super().headerData(section, orientation, role)

    def columnCount(self, parent: SetTreeIndex = INVALID_INDEX) -> int:
        return len(self.header)

    def rowCount(self, parent: SetTreeIndex = INVALID_INDEX) -> int:
        match parent.internalPointer():
            case SetContainer(children=list(children)):
                return len(children)
            case _:
                return len(self.set_data)

    def parent(self, child: SetTreeIndex) -> SetTreeIndex:  # noqa
        if not child.isValid():
            return INVALID_INDEX
        match child.internalPointer():
            case SetContainer(parent=None):
                return INVALID_INDEX
            case SetContainer(parent=SetContainer() as parent) as child_container:
                row = parent.children.index(child_container)
                return self.createIndex(row, ModelColumns.name, parent)
            case _:
                raise RuntimeError("Invalid child index!")

    def index(self, row: int, column: ModelColumns, /, parent: SetTreeIndex = INVALID_INDEX) -> SetTreeIndex:
        index_set = parent.internalPointer().children[row] if parent.isValid() else self.set_data[row]
        return self.createIndex(row, column, index_set)

    def multiData(self, index: SetTreeIndex, role_data_span: QModelRoleDataSpan | QModelRoleData, /):
        item = index.internalPointer()
        column = ModelColumns(index.column())
        if isinstance(role_data_span, QModelRoleDataSpan):
            for role_data in role_data_span:  # type: QModelRoleData  # noqa
                role = ItemDataRole(role_data.role())
                data = self._data(item, column, role)
                role_data.setData(data)
        else:
            role = ItemDataRole(role_data_span.role())
            data = self._data(item, column, role)
            role_data_span.setData(data)

    def data(self, index: SetTreeIndex, /, role: ItemDataRole = DisplayRole):
        return self._data(index.internalPointer(), ModelColumns(index.column()), role)

    def _data(self, container: SetContainer, column: ModelColumns, role: ItemDataRole):
        if column == ModelColumns.name:
            return container.set.data(role)
        elif column == ModelColumns.is_hidden:
            if role == CheckStateRole:
                return CheckState.Checked if container.is_hidden else CheckState.Unchecked
            elif role == DisplayRole:
                return self.tr("Hidden", "Set filter column display text") \
                    if container.is_hidden\
                    else self.tr("Visible", "Set filter column display text")
            elif role == BackgroundRole:
                return container.highlight_is_hidden
        elif column == ModelColumns.preference_weights and role in {DisplayRole, EditRole}:
            return container.preference_weight
        elif column == ModelColumns.preference_weights and role == BackgroundRole:
            return container.highlight_preference_weight
        elif column == ModelColumns.release_date and role == DisplayRole:
            return container.set.release_date.isoformat().split("T")[0]  # TODO: Does that need locale-aware formatting?
        elif column == ModelColumns.scryfall_query and role == ScryfallQueryRole:
            return container.scryfall_query
        return None

    def flags(self, index: SetTreeIndex) -> ItemFlag:
        item = index.internalPointer()
        has_children = bool(item.children)
        column = ModelColumns(index.column())
        if column == ModelColumns.name and has_children:
            return NodeDataFlags
        elif column == ModelColumns.is_hidden:
            return IsHiddenFlags
        elif column == ModelColumns.preference_weights:
            return PreferenceWeightsFlags
        else:
            return LeafDataFlags

    def setData(self, index: SetTreeIndex, value: CheckState | int, /, role: ItemDataRole = EditRole) -> bool:
        item = index.internalPointer()
        column = ModelColumns(index.column())
        if column == ModelColumns.is_hidden and role == CheckStateRole:
            item.is_hidden = CheckState(value) == CheckState.Checked
            self.dataChanged.emit(index, index, [DisplayRole])
            return True
        elif column == ModelColumns.preference_weights and role == EditRole:
            assert isinstance(value, int), f"{type(value)=}"
            item.preference_weight = value
            self.dataChanged.emit(index, index, [DisplayRole])
            return True
        return False

    def populate_from_card_db(self):
        set_data = CardDatabase.main_instance.get_all_sets()
        registry: dict[str, SetContainer] = {}
        for mtg_set in set_data:
            registry[mtg_set.code] = container = SetContainer(mtg_set, QUrl())
            if mtg_set.parent_set_code is not None:
                # Because of breadth-first set tree traversal, the registry lookup is guaranteed to never fail.
                container.parent = parent = registry[mtg_set.parent_set_code]
                parent.children.append(container)
        self.beginResetModel()
        self.set_data[:] = (item for item in registry.values() if item.parent is None)
        self.endResetModel()

    def get_new_preference_weights(self) -> set[tuple[str, int]]:
        """Returns all updated set preference weights"""
        result = set()
        for index in self._get_all_indices():
            set_container = index.internalPointer()
            mtg_set = set_container.set
            if set_container.preference_weight != mtg_set.preference_weight:
                result.add((mtg_set.code, set_container.preference_weight))
        return result

    def highlight_differing_settings(self, settings: ConfigParser):
        """
        Highlight any editable cell differing from the application defaults or the last saved values.
        Highlighting is implemented by setting cell backgrounds to the current palette's ColorRole.Highlight.
        """
        # Determine highlighting mode by comparing the identity of the ConfigParser
        if settings is DEFAULT_SETTINGS:
            # Default is False for is_hidden, and zero for preference weights, so any truthy value means data changed
            def is_hidden_changed(item_: SetContainer) -> bool:
                return item_.is_hidden
            def preference_weight_changed(item_: SetContainer) -> bool:
                return bool(item_.preference_weight)
        else:
            # When comparing against previously saved data, compare against the MTGSet from the CardDatabase
            def is_hidden_changed(item_: SetContainer) -> bool:
                return item_.is_hidden is not item_.set.is_hidden
            def preference_weight_changed(item_: SetContainer) -> bool:
                return item_.preference_weight != item_.set.preference_weight

        palette = QApplication.palette()
        highlight_color = palette.color(palette.currentColorGroup(), palette.ColorRole.Highlight)
        highlight_color.setAlpha(64)  # 25% opacity, same as the highlight_widget() implementation
        # Note: left/right: dataChanged() takes a rectangular region via top-left and bottom-right
        # If both is_hidden and the preference weight change, the update is grouped using this mechanism.
        for left in self._get_all_indices():
            item = left.internalPointer()
            emit = False
            if is_hidden_changed(item):
                item.highlight_is_hidden = highlight_color
                emit = True
            if preference_weight_changed(item):
                item.highlight_preference_weight = highlight_color
                right = left.siblingAtColumn(ModelColumns.preference_weights)
                emit = True
            else:
                right = left
            if emit:
                self.dataChanged.emit(left, right, [BackgroundRole])

    def clear_highlight(self):
        """Clears any cell highlighting"""
        for left in self._get_all_indices():
            item = left.internalPointer()
            emit = False
            if item.highlight_is_hidden is not None:
                item.highlight_is_hidden = None
                emit = True
            if item.highlight_preference_weight is not None:
                item.highlight_preference_weight = None
                right = left.siblingAtColumn(ModelColumns.preference_weights)
                emit = True
            else:
                right = left
            if emit:
                self.dataChanged.emit(left, right, [BackgroundRole])

    def _get_all_indices(self) -> typing.Generator[SetTreeIndex, None, None]:
        """
        Yields a SetTreeIndex for each row in the model, including children. Indices point to the
        ModelColumns.is_hidden column.

        Internally uses a queue to implement a breadth-first tree walk.
        """
        queue = [self.index(row, ModelColumns.is_hidden) for row in range(self.rowCount())]
        while queue:
            index = queue.pop(0)
            queue += (self.index(row, ModelColumns.is_hidden, index) for row in range(self.rowCount(index)))
            yield index

    def save_settings(self, settings: ConfigParser):
        logger.debug("Saving set filter state to settings.")
        active_filters: list[str] = []
        active_weights: list[str] = []
        for index in self._get_all_indices():
            item = index.internalPointer()
            if item.is_hidden:
                active_filters.append(item.set.code)
            if item.preference_weight:
                active_weights.append(f"{item.set.code}:{item.preference_weight}")
        settings["printing-filter"]["sets"] = " ".join(active_filters)
        settings["printing-weights"]["sets"] = " ".join(active_weights)
        logger.debug("Done.")


class MTGSetTreeFilterModel(QSortFilterProxyModel):
    sourceModel: Callable[[], MTGSetTreeModel]
    setSourceModel: Callable[[MTGSetTreeModel], None]
    mapToSource: Callable[[QModelIndex], SetTreeIndex]
    
    def __init__(self, /, parent: QObject | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.setDynamicSortFilter(False)
        self.setRecursiveFilteringEnabled(True)
        self.highlight_mode: bool = False

    # Wrappers around changed API for filter change notification
    # Note: Not a version mismatch: https://doc.qt.io/archives/qt-6.9/qsortfilterproxymodel.html#beginFilterChange
    # < 6.9 uses only a single invalidateRowsFilter() call,
    # 6.9.x uses beginFilterChange() with invalidateRowsFilter(), and
    # > 6.9 uses beginFilterChange() with endFilterChange(Direction).
    # invalidateRowsFilter() is scheduled for removal in 6.13
    def _begin_filter_change(self):
        if PySide6Version >= (6, 9):
            self.beginFilterChange()

    def _end_filter_change(self):
        if PySide6Version >= (6, 10):
            self.endFilterChange(QSortFilterProxyModel.Direction.Rows)
        else:
            self.invalidateRowsFilter()

    def highlight_differing_settings(self, settings: ConfigParser):
        self._begin_filter_change()
        self.highlight_mode = True
        self.sourceModel().highlight_differing_settings(settings)
        self._end_filter_change()

    def clear_highlight(self):
        self._begin_filter_change()
        self.highlight_mode = False
        self.sourceModel().clear_highlight()
        self._end_filter_change()

    def filterAcceptsRow(self, source_row: int, source_parent: SetTreeIndex, /) -> bool:
        if self.highlight_mode:
            return self._is_highlighted(source_row, source_parent)
        return True

    def _is_highlighted(
            self, source_row: int,
            source_parent: SetTreeIndex, /) -> bool:
        index = self.sourceModel().index(source_row, MTGSetTreeModel.ModelColumns.is_hidden, source_parent)
        item = index.internalPointer()
        return item.highlight_is_hidden is not None or item.highlight_preference_weight is not None

    def _get_all_indices(self) -> typing.Generator[QModelIndex, None, None]:
        """
        Yields a SetTreeIndex for each row in the model, including children. Indices point to the
        ModelColumns.is_hidden column.

        Internally uses a queue to implement a breadth-first tree walk.
        """
        queue = [self.index(row, ModelColumns.is_hidden) for row in range(self.rowCount())]
        while queue:
            index = queue.pop(0)
            queue += (self.index(row, ModelColumns.is_hidden, index) for row in range(self.rowCount(index)))
            yield index
