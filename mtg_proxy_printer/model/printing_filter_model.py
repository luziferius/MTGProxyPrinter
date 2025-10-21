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

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from mtg_proxy_printer.units_and_sizes import ConfigParser
from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger

CheckState = Qt.CheckState
ItemDataRole = Qt.ItemDataRole
BackgroundRole = ItemDataRole.BackgroundRole
DisplayRole = ItemDataRole.DisplayRole
ToolTipRole = ItemDataRole.ToolTipRole
SettingsKeyRole = ItemDataRole.UserRole
CheckStateRole = ItemDataRole.CheckStateRole

ScryfallQueryRole = ItemDataRole(SettingsKeyRole.value + 1)
EmptyCellFlags = Qt.ItemFlag.ItemNeverHasChildren
HeaderItemFlags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemNeverHasChildren
SettingItemFlags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemNeverHasChildren

ModelRow = dict[ItemDataRole, typing.Any]
ModelRows = list[ModelRow]

def _create_header_item(header_font: QFont, ui_text: str, tooltip: str = None) -> ModelRow:
    """Create a centered, text-only header item for the PrintingFilterModel"""
    return ModelRow({DisplayRole: ui_text, ToolTipRole: tooltip, CheckStateRole: None, SettingsKeyRole: "",
                     ItemDataRole.TextAlignmentRole: Qt.AlignmentFlag.AlignCenter, ItemDataRole.FontRole: header_font})

def _create_format_item(ui_text: str, tooltip: str, internal_format_key: str) -> ModelRow:
    """Creates a PrintingFilterModel row item for MTG format ban filters"""
    return _create_item(
        ui_text, tooltip.format(format=ui_text),
        f"hide-banned-in-{internal_format_key}", f"banned:{internal_format_key}"
    )

def _create_item(ui_text: str, tooltip: str | None, settings_key: str, scryfall_query: str | None) -> ModelRow:
    """Creates a fully customizable PrintingFilterModel row item for any kind of card filters."""
    return ModelRow({DisplayRole: ui_text, ToolTipRole: tooltip, CheckStateRole: CheckState.Unchecked,
                     SettingsKeyRole: settings_key, ScryfallQueryRole: scryfall_query})


class PrintingFilterModel(QAbstractTableModel):
    """
    Model holding the printing filters, used by the settings window to allow the
    user to set the hidden printings to their liking.
    The filter entries store an on/off state editable via the ItemDataRole.CheckStateRole, which makes the UI show a 
    checkbox that can be toggled via clicking it.
    Changed-item highlighting uses the BackgroundRole.
    The settings key used to persist the value is stored via the SettingsKeyRole.
    The Scryfall query showing the affected printings is stored via the ScryfallQueryRole.
    """
    def __init__(self, parent = None):
        super().__init__(parent)
        self.items = self._create_items()

    def _create_items(self) -> ModelRows:
        format_ban_tooltip = self.tr("Hide cards banned in the {format} format", "Tooltip text")
        # TODO: This hard-codes the font. A system-wide style change should update the font with the new default
        header_font = QApplication.font()
        header_font.setBold(True)
        return [
            _create_header_item(header_font,
                self.tr("General filters", "Display text. Printing filter section header"),
                self.tr("Hide printings based on general card properties", "Tooltip text")),
            _create_item(
                self.tr("Hide cards depicting racism", "Display text"),
                self.tr("Hide cards banned for depicting racism.\n\n"
                        "Background: Some cards were banned by Wizards of the Coast,\n"
                        "because they depict references to controversial real-world events,\n"
                        "religion or contain combinations of card effect, name and artwork that,\n"
                        "when viewed together, depict racism or are otherwise inappropriate.\n"
                        "These cards are banned in all sanctioned tournament formats and several\n"
                        "community formats like Commander, Oathbreaker and others.",
                        "Tooltip text"),
                "hide-cards-depicting-racism", "function:banned-due-to-racist-imagery"),
            _create_item(
                self.tr("Hide cards with placeholder images",
                        "Display text"),
                self.tr("Hide non-English cards with low-resolution,\n"
                        "English placeholder images containing an overlay text stating\n"
                        "“This card is not available in the selected language.”",
                        "Tooltip text"),
                "hide-cards-without-images", None),
            _create_item(
                self.tr("Hide “funny” cards",
                        "Display text"),
                self.tr("“Funny” cards, not legal in any constructed format.\n"
                        "This includes silver-bordered cards, full-art Contraptions from Unstable,\n"
                        "cards with acorn-shaped security stamps from Unfinity (and newer Un-Sets),\n"
                        "some black-bordered promotional cards with non-standard back faces,\nand potentially others.",
                        "Tooltip text"),
                "hide-funny-cards", "is:funny"),
            _create_item(
                self.tr("Hide digital-only cards or printings",
                        "Display text"),
                self.tr("Hide cards and printings that are only available on digital platforms. "
                        "This includes all kinds of digital printings.",
                        "Tooltip text"),
                "hide-digital-cards", "is:digital"),
            _create_item(
                self.tr("Hide reversible cards",
                        "Display text"),
                self.tr("Some single-sided cards are re-printed as two-sided, reversible cards in some "
                        "Secret Lair releases.\nThis filter hides those.",
                        "Tooltip text"),
                "hide-reversible-cards", "is:reversible"),

            _create_header_item(header_font,
                self.tr("Border style", "Display text. Printing filter section header")),
            _create_item(
                self.tr("Hide white-bordered cards",
                        "Display text"),
                None,
                "hide-white-bordered", "border:white"),
            _create_item(
                self.tr("Hide gold-bordered cards",
                        "Display text"),
                self.tr("Some “collectible” sets, like full reprints of "
                        "tournament-winning decks were printed with golden borders.\n"
                        "Many also have printed signatures of the involved players in "
                        "the text box.\n\nThese are not tournament legal",
                        "Tooltip text"),
                "hide-gold-bordered", "border:gold"),
            _create_item(
                self.tr("Hide borderless cards",
                        "Display text"),
                self.tr("Hide cards without a defined, solid-color border.\n"
                        "Those require higher cutting precision to get right.",
                        "Tooltip text"),
                "hide-borderless", "border:borderless"),
            _create_item(
                self.tr("Hide extended-art cards",
                        "Display text"),
                self.tr("Hide cards with artwork extending to the left and right card border.\n"
                        "Similar to borderless cards, these require higher precision during the cutting process.",
                        "Tooltip text"),
                "hide-extended-art", "is:extended"),

            _create_header_item(header_font,
                self.tr("Non-traditional cards", "Display text. Printing filter section header")),
            _create_item(
                self.tr("Hide oversized cards",
                        "Display text"),
                self.tr("These cards are larger than regular Magic cards and can’t be included in decks.\n"
                        "Includes Archenemy schemes, Planechase planes and\noversized commander creature or "
                        "Planeswalker cards included in some pre-constructed Commander decks.",
                        "Tooltip text"),
                "hide-oversized-cards", "is:oversized"),
            _create_item(
                self.tr("Hide Tokens",
                        "Display text"),
                self.tr("The official Tokens, used to represent permanents created by card effects.\n"
                        "Not part of deck-building. Obscure ones can be relatively rare",
                        "Tooltip text"),
                "hide-token", "is:token"),
            _create_item(
                self.tr("Hide Art Series cards",
                        "Display text"),
                self.tr("Artwork cards that can be found in Set Boosters or Play Boosters",
                        "Tooltip text"),
                "hide-art-series-cards", "layout:art-series"),

            _create_header_item(header_font,
                self.tr("Format bans: Hide cards banned in specific formats",
                        "Display text. Section header above MTG format ban filters")),
            _create_format_item(
                self.tr("Brawl", "Display text. Magic format name. Translations (if one exists) "
                                 "should probably also include the English name like {translated name}(<english name>)"),
                format_ban_tooltip, "brawl"),
            _create_format_item(
                self.tr("Commander", "Display text. Magic format name. Translations (if one exists) "
                                 "should probably also include the English name like {translated name}(<english name>)"),
                format_ban_tooltip, "commander"),
            _create_format_item(
                self.tr("Historic", "Display text. Magic format name. Translations (if one exists) "
                                 "should probably also include the English name like {translated name}(<english name>)"),
                format_ban_tooltip, "historic"),
            _create_format_item(
                self.tr("Legacy", "Display text. Magic format name. Translations (if one exists) "
                                 "should probably also include the English name like {translated name}(<english name>)"),
                format_ban_tooltip, "legacy"),
            _create_format_item(
                self.tr("Modern", "Display text. Magic format name. Translations (if one exists) "
                                 "should probably also include the English name like {translated name}(<english name>)"),
                format_ban_tooltip, "modern"),
            _create_format_item(
                self.tr("Oathbreaker", "Display text. Magic format name. Translations (if one exists) "
                                 "should probably also include the English name like {translated name}(<english name>)"),
                format_ban_tooltip, "oathbreaker"),
            _create_format_item(
                self.tr("Pauper", "Display text. Magic format name. Translations (if one exists) "
                                 "should probably also include the English name like {translated name}(<english name>)"),
                format_ban_tooltip, "pauper"),
            _create_format_item(
                self.tr("Pioneer", "Display text. Magic format name. Translations (if one exists) "
                                 "should probably also include the English name like {translated name}(<english name>)"),
                format_ban_tooltip, "pioneer"),
            _create_format_item(
                self.tr("Standard", "Display text. Magic format name. Translations (if one exists) "
                                 "should probably also include the English name like {translated name}(<english name>)"),
                format_ban_tooltip, "standard"),
            _create_format_item(
                self.tr("Vintage", "Display text. Magic format name. Translations (if one exists) "
                                 "should probably also include the English name like {translated name}(<english name>)"),
                format_ban_tooltip, "vintage"),
        ]

    def rowCount(self, /, parent: QModelIndex = QModelIndex()):
        return 0 if parent.isValid() else len(self.items)

    def columnCount(self, parent: QModelIndex = QModelIndex(), /):
        return 0 if parent.isValid() else 2

    def data(self, index: QModelIndex, /, role: ItemDataRole = DisplayRole):
        return None if index.column() else self.items[index.row()].get(role, None)

    def setData(self, index: QModelIndex, value, /, role: ItemDataRole = DisplayRole):
        if role == CheckStateRole:
            value = CheckState(value)
        item = self.items[index.row()]
        if item[role] != value:
            item[role] = value
            return True
        return False

    def flags(self, index: QModelIndex, /):
        return EmptyCellFlags if index.column() \
            else SettingItemFlags if index.data(SettingsKeyRole) \
            else HeaderItemFlags

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
        section = settings["card-filter"]
        palette = QApplication.palette()
        highlight_color = palette.color(palette.currentColorGroup(), palette.ColorRole.Highlight)
        highlight_color.setAlpha(64)  # 25% opacity, same as the highlight_widget() implementation
        for row, item in enumerate(self.items):
            current_state: CheckState = item[CheckStateRole]
            if current_state is not None and current_state != section.get_check_state(item[SettingsKeyRole]):
                index = self.index(row, 0)
                item[BackgroundRole] = highlight_color
                self.dataChanged.emit(index, index, [BackgroundRole])

    def clear_highlight(self):
        for item in self.items:
            item[BackgroundRole] = None
        self.dataChanged.emit(
            self.index(0, 0),
            self.index(self.rowCount()-1, 0),
            [BackgroundRole]
        )