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
    is_hidden: bool
    preference_weight: int
    scryfall_query: QUrl
    # Backup copy of the original values as stored in the database.
    # Used for resets and highlighting differing settings
    original_is_hidden: bool = dataclasses.field(init=False)
    original_preference_weight: int = dataclasses.field(init=False)
    # Tree structure
    children: list["SetContainer"] = dataclasses.field(default_factory=list)
    parent: typing.Optional["SetContainer"] = None

    def __post_init__(self):
        self.original_is_hidden = self.is_hidden
        self.original_preference_weight = self.preference_weight

    def data(self, column: ModelColumns, role: ItemDataRole):
        if column == ModelColumns.name:
            return self.set.data(role)
        elif column == ModelColumns.is_hidden:
            if role == CheckStateRole:
                return CheckState.Checked if self.is_hidden else CheckState.Unchecked
            elif role == DisplayRole:
                return "Hidden" if self.is_hidden else "Visible"  # TODO: Translation support
        elif column == ModelColumns.preference_weights and role in {DisplayRole, EditRole}:
            return self.preference_weight
        elif column == ModelColumns.release_date:
            return None  # TODO
        elif column == ModelColumns.scryfall_query and role == ScryfallQueryRole:
            return self.scryfall_query
        return None


class SetTreeIndex(QModelIndex):
    """QModelIndex created by MTGSetTreeModel.
    Type hinting stub used to annotate the type of the internally held reference."""
    internalPointer: Callable[[], SetContainer]


INVALID_INDEX = SetTreeIndex()


class MTGSetTreeModel(QAbstractItemModel):
    """
    A model used to show all MTG sets, with sub-sets as children. Sub-sets are associated token,
    promo printings, and similar sets.

    Also exposes the "set_filter_active" flag and "preference score" as editable columns,
    and is used by the PrintingPreferencePage settings page to configure these.
    """
    createIndex: Callable[[int, int, typing.Any], SetTreeIndex]


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

    def headerData(self, section: int, orientation: Orientation, role: ItemDataRole = ItemDataRole.DisplayRole) \
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
                data = item.data(column, role)
                role_data.setData(data)
        else:
            role = ItemDataRole(role_data_span.role())
            data = item.data(column, role)
            role_data_span.setData(data)

    def data(self, index: SetTreeIndex, /, role: ItemDataRole = ItemDataRole.DisplayRole):
        return index.internalPointer().data(ModelColumns(index.column()), role)

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
