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

import typing
from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex

from mtg_proxy_printer.units_and_sizes import ConfigParser
from mtg_proxy_printer.logger import get_logger


logger = get_logger(__name__)
del get_logger

CheckState = Qt.CheckState
ItemDataRole = Qt.ItemDataRole
DisplayRole = ItemDataRole.DisplayRole
ToolTipRole = ItemDataRole.ToolTipRole
SettingsKeyRole = ItemDataRole.UserRole

ScryfallQueryRole = ItemDataRole(SettingsKeyRole.value + 1)
CheckStateRole = ItemDataRole.CheckStateRole
SectionItem = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemNeverHasChildren
CheckableItem = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemNeverHasChildren

ModelRow = dict[ItemDataRole, typing.Any]
ModelRows = list[ModelRow]

def _create_header_item(ui_text: str, tooltip: str) -> ModelRow:
    return ModelRow({DisplayRole: ui_text, ToolTipRole: tooltip, CheckStateRole: None, SettingsKeyRole: "",
                     ItemDataRole.TextAlignmentRole: Qt.AlignmentFlag.AlignCenter})

def _create_format_item(ui_text: str, tooltip: str, format_: str) -> ModelRow:
    return _create_item(ui_text, tooltip, f"hide-banned-in-{format_}", f"banned:{format_}")

def _create_item(ui_text: str, tooltip: str, settings_key: str, query_str: str) -> ModelRow:
    return ModelRow({DisplayRole: ui_text, ToolTipRole: tooltip, CheckStateRole: CheckState.Unchecked,
                     SettingsKeyRole: settings_key, ScryfallQueryRole: query_str})


class PrintingFilterModel(QAbstractListModel):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.items: ModelRows = [
            _create_header_item(self.tr("General filters"), self.tr("")),
            _create_item(self.tr("Cards depicting racism"), self.tr(""), "hide-cards-depicting-racism", "function:banned-due-to-racist-imagery"),
            _create_header_item(self.tr("Format bans: Hide bans in specific formats"), self.tr("")),
            _create_item(self.tr("Commander"), self.tr(""), "hide-banned-in-commander", "banned:commander"),
        ]

    def rowCount(self, /, parent: QModelIndex = QModelIndex()):
        return 0 if parent.isValid() else len(self.items)

    def columnCount(self, parent: QModelIndex, /):
        return 0 if parent.isValid() else 1

    def data(self, index: QModelIndex, /, role: ItemDataRole = ItemDataRole.DisplayRole):
        try:
            return self.items[index.row()][role]
        except KeyError:
            return None

    def setData(self, index: QModelIndex, value, /, role: ItemDataRole = ItemDataRole.DisplayRole):
        logger.debug(f"setData({index=}, {value=}, {role=})")
        self.items[index.row()][role] = value
        self.dataChanged.emit(index, index, [role])
        return True

    def flags(self, index: QModelIndex, /):
        return CheckableItem if index.data(SettingsKeyRole) else SectionItem

    def load_settings(self, settings: ConfigParser):
        logger.debug("Loading printing filter state from settings")
        section = settings["card-filter"]
        for row, item in enumerate(self.items):
            if item[CheckStateRole] is not None:
                item[CheckStateRole] = section.get_check_state(item[SettingsKeyRole])
        self.dataChanged.emit(
            self.index(1, 0),  # First row isn't checkable, so skip it
            self.index(self.rowCount()-1, 0),
            [CheckStateRole])
        logger.debug("Done.")

    def save_settings(self, settings: ConfigParser):
        logger.debug("Saving printing filter state to settings.")
        section = settings["card-filter"]
        for row, item in enumerate(self.items):
            if item[CheckStateRole] is not None:
                section.set_check_state(item[SettingsKeyRole],item[CheckStateRole])
        logger.debug("Done.")

    def highlight_differing_settings(self, settings: ConfigParser):
        pass

    def clear_highlight(self):
        pass