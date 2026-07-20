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

from PySide6.QtCore import Qt, QModelIndex, QAbstractItemModel, QObject, QModelRoleDataSpan, QUrl, QModelRoleData

from mtg_proxy_printer.model.card import MTGSet
from mtg_proxy_printer.logger import get_logger
from mtg_proxy_printer.model.carddb import CardDatabase

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
ScryfallQueryRole = ItemDataRole(UserRole.value + 1)

# The flag values
ItemFlag = Qt.ItemFlag
ParentStaticDataFlags = ItemFlag.ItemIsEnabled
ChildStaticDataFlags = ParentStaticDataFlags | ItemFlag.ItemNeverHasChildren  # noqa

ParentIsHiddenFlags =  ItemFlag.ItemIsEnabled | ItemFlag.ItemIsUserCheckable  # noqa
ChildIsHiddenFlags = ParentIsHiddenFlags | ItemFlag.ItemNeverHasChildren  # noqa

ParentPreferenceWeightsFlags = ItemFlag.ItemIsEnabled | ItemFlag.ItemIsEditable  # noqa
ChildPreferenceWeightsFlags = ParentPreferenceWeightsFlags | ItemFlag.ItemNeverHasChildren  # noqa


@enum.verify(enum.CONTINUOUS, enum.UNIQUE)
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
    # The editable columns. MTGSet is frozen
    is_hidden: bool = dataclasses.field(init=False)
    preference_weight: int = dataclasses.field(init=False)
    # Tree structure
    children: list["SetContainer"] = dataclasses.field(default_factory=list)
    parent: typing.Optional["SetContainer"] = None

    def __post_init__(self):
        self.editable_is_hidden = self.set.is_hidden
        self.editable_preference_weight = self.set.preference_weight


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


    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.header = {
            ModelColumns.name: self.tr("Set", "Table column header"),
            ModelColumns.is_hidden: self.tr("Hidden?", "Table column header"),
            ModelColumns.preference_weights: self.tr("", "Table column header"),
            ModelColumns.release_date: self.tr("Released", "Table column header"),
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
        match child.internalPointer():
            case SetContainer(parent=None):
                return INVALID_INDEX
            case None:
                return INVALID_INDEX
            case SetContainer(parent=SetContainer() as parent):
                row = parent.children.index(parent)
                return self.createIndex(row, ModelColumns.name, parent)
            case _:
                raise RuntimeError("Invalid child index!")

    def index(self, row: int, column: ModelColumns, /, parent: SetTreeIndex = INVALID_INDEX) -> SetTreeIndex:
        if parent.isValid():
            parent_set = parent.internalPointer()
            index_set = parent_set.children[row]
        else:
            index_set = self.set_data[row]
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
                return "Hidden" if container.is_hidden else "Visible"  # TODO: Translation support
        elif column == ModelColumns.preference_weights and role in {DisplayRole, EditRole}:
            return container.preference_weight
        elif column == ModelColumns.release_date and role == DisplayRole:
            return container.set.release_date  # TODO: Does that need locale-aware formatting?
        elif column == ModelColumns.scryfall_query and role == ScryfallQueryRole:
            return container.scryfall_query
        return None

    def flags(self, index: SetTreeIndex) -> ItemFlag:
        parent = index.internalPointer().parent
        column = ModelColumns(index.column())
        if parent is None:
            if column == ModelColumns.is_hidden:
                return ParentIsHiddenFlags
            elif column == ModelColumns.preference_weights:
                return ParentPreferenceWeightsFlags
            else:
                return ParentStaticDataFlags
        else:
            if column == ModelColumns.is_hidden:
                return ChildIsHiddenFlags
            elif column == ModelColumns.preference_weights:
                return ChildPreferenceWeightsFlags
            else:
                return ChildStaticDataFlags

    def setData(self, index: SetTreeIndex, value: CheckState | int, /, role: ItemDataRole = EditRole) -> bool:
        item = index.internalPointer()
        column = ModelColumns(index.column())
        if column == ModelColumns.is_hidden and role == CheckStateRole:
            assert isinstance(value, CheckState)
            item.is_hidden = value == CheckState.Checked
            self.dataChanged.emit(index, index, [DisplayRole])
            return True
        elif column == ModelColumns.preference_weights and role == EditRole:
            assert isinstance(value, int)
            item.preference_weight = value
            self.dataChanged.emit(index, index, [DisplayRole])
            return True
        return False

    def populate_from_card_db(self):
        set_data = CardDatabase.main_instance.get_all_sets()
        registry: dict[str, SetContainer] = {}
        for mtg_set in set_data:
            if mtg_set.parent_set_code is None:
                registry[mtg_set.code] = SetContainer(mtg_set, QUrl())
            else:
                parent = registry[mtg_set.parent_set_code]
                parent.children.append(SetContainer(mtg_set, QUrl(), parent=parent))
        self.beginResetModel()
        self.set_data[:] = registry.values()
        self.endResetModel()