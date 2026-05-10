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

from collections import defaultdict
import dataclasses
import enum

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.units_and_sizes import ConfigParser
from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger

CheckState = Qt.CheckState
ItemDataRole = Qt.ItemDataRole
EditRole = ItemDataRole.EditRole
BackgroundRole = ItemDataRole.BackgroundRole
DisplayRole = ItemDataRole.DisplayRole
ToolTipRole = ItemDataRole.ToolTipRole
UserRole = ItemDataRole.UserRole
CheckStateRole = ItemDataRole.CheckStateRole

ScryfallQueryRole = ItemDataRole(UserRole.value + 1)
ItemFlagsRole = ItemDataRole(UserRole.value + 2)
IsHeaderRole = ItemDataRole(UserRole.value + 3)

# The flag values
EmptyCellFlags: Qt.ItemFlag = Qt.ItemFlag.ItemNeverHasChildren
_DataFlags = Qt.ItemFlag.ItemNeverHasChildren | Qt.ItemFlag.ItemIsEnabled  # Common flags for cells with data
TextItemFlags: Qt.ItemFlag = _DataFlags
IsHiddenItemFlags: Qt.ItemFlag = _DataFlags | Qt.ItemFlag.ItemIsUserCheckable  # The is_hidden column is checkable
PreferenceWeightFlags: Qt.ItemFlag = _DataFlags | Qt.ItemFlag.ItemIsEditable  # the pref score column is editable

class ModelCell(defaultdict):
    def __init__(self, *args, **kwargs):
        super().__init__(lambda: None, *args, **kwargs)

MC = ModelCell


@enum.verify(enum.CONTINUOUS, enum.UNIQUE)
class ModelColumns(enum.IntEnum):
    name = 0
    is_hidden = enum.auto()
    preference_weights = enum.auto()
    scryfall_query = enum.auto()


@dataclasses.dataclass
class ModelRow:
    name: ModelCell
    is_hidden: ModelCell
    preference_weights: ModelCell
    scryfall_query: ModelCell
    _settings_key: str

    def data(self, column: ModelColumns, role: ItemDataRole):
        column = ModelColumns(column)
        attr: ModelCell = getattr(self, column._name_, ModelCell())
        return attr[role]

    def flags(self, column: ModelColumns) -> Qt.ItemFlag:
        return self.data(column, ItemFlagsRole)

    def setData(self, column: ModelColumns, value, /, role: ItemDataRole = DisplayRole) -> bool:
        column = ModelColumns(column)
        attr: ModelCell = getattr(self, column._name_, ModelCell())
        if attr[role] != value:
            attr[role] = value
            return True
        return False

    @classmethod
    def create_header(cls, header_font: QFont, ui_text: str, tooltip: str = None) -> ModelRow:
        """Create a centered, text-only header item for the PrintingFilterModel"""
        return cls(
            MC({ItemFlagsRole: TextItemFlags, DisplayRole: ui_text, ToolTipRole: tooltip, IsHeaderRole: True,
             ItemDataRole.TextAlignmentRole: Qt.AlignmentFlag.AlignCenter, ItemDataRole.FontRole: header_font}),
            MC({ItemFlagsRole: EmptyCellFlags}),
            MC({ItemFlagsRole: EmptyCellFlags}),
            MC({ItemFlagsRole: EmptyCellFlags}),
            "",
        )

    @classmethod
    def create_format_item(cls, ui_text: str, tooltip: str, internal_format_key: str) -> ModelRow:
        """
        Creates a PrintingFilterModel row item for MTG format ban filters. These have binary show/hide toggles,
        but no preference score, because the latter does not make sense here.
        """
        return cls(
            MC({ItemFlagsRole: TextItemFlags, DisplayRole: ui_text, ToolTipRole: tooltip}),
            MC({ItemFlagsRole: IsHiddenItemFlags, CheckStateRole: CheckState.Unchecked}),
            MC({ItemFlagsRole: EmptyCellFlags}),
            MC({ItemFlagsRole: EmptyCellFlags, ScryfallQueryRole: f"banned:{internal_format_key}"}),
            f"hide-banned-in-{internal_format_key}",
        )
    
    @classmethod
    def create_item(cls, ui_text: str, text_tooltip: str | None, weight_tooltip: str | None, settings_key: str, scryfall_query: str | None):
        """
        Creates a PrintingFilterModel row item for arbitrary non-format card filters.
        They have both a binary show/hide toggle, and a numerical weight.
        """
        weights_value = MC(
            {ItemFlagsRole: PreferenceWeightFlags, ToolTipRole: weight_tooltip, EditRole: 0, DisplayRole: 0}
            if weight_tooltip is not None
            else {ItemFlagsRole: EmptyCellFlags}
        )
        return cls(
            MC({ItemFlagsRole: TextItemFlags, DisplayRole: ui_text, ToolTipRole: text_tooltip}),
            MC({ItemFlagsRole: IsHiddenItemFlags, ToolTipRole: text_tooltip, CheckStateRole: CheckState.Unchecked}),
            weights_value,
            MC({ItemFlagsRole: EmptyCellFlags, ScryfallQueryRole: scryfall_query}),
            settings_key,
        )


ModelRows = list[ModelRow]


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
        self.card_db = CardDatabase.main_instance
        self.items = self._create_items()

    def _create_items(self) -> ModelRows:
        format_ban_tooltip = self.tr("Hide cards banned in the {format} format", "Tooltip text")
        # TODO: This hard-codes the font. A system-wide style change should update the font with the new default
        header_font = QApplication.font()
        header_font.setBold(True)
        weight_tooltip = self.tr(
            "High values encourage choosing this kind of card, negative values discourage choosing it.",
            "Is preference weight column tooltip text")
        return [
            ModelRow.create_header(header_font,
                self.tr("General card filters", "Display text. Printing filter section header"),
                None),
            ModelRow.create_item(
                self.tr("Cards depicting racism", "Display text"),
                self.tr("Cards banned for depicting racism or for being culturally inappropriate.\n\n"
                        "Background: Some cards were banned by Wizards of the Coast,\n"
                        "because they depict references to controversial real-world events,\n"
                        "religion or contain combinations of card effect, name and artwork that,\n"
                        "when viewed together, depict racism or are otherwise inappropriate.\n"
                        "These cards are banned in all sanctioned tournament formats and several\n"
                        "community formats like Commander, Oathbreaker and others.",
                        "Tooltip text"),
                None, "hide-cards-depicting-racism", "is:content_warning"),
            ModelRow.create_item(
                self.tr("Cards with placeholder images",
                        "Display text"),
                self.tr("Non-English cards with low-resolution,\n"
                        "English placeholder images containing an overlay text stating\n"
                        "“This card is not available in the selected language.”",
                        "Tooltip text"),
                weight_tooltip, "hide-cards-without-images", None),
            ModelRow.create_item(
                self.tr("“Funny” cards",
                        "Display text"),
                self.tr("“Funny” cards, not legal in any constructed format.\n"
                        "This includes silver-bordered cards, full-art Contraptions from Unstable,\n"
                        "cards with acorn-shaped security stamps from Unfinity (and newer Un-Sets),\n"
                        "some black-bordered promotional cards with non-standard back faces,\nand potentially others.",
                        "Tooltip text"),
                None, "hide-funny-cards", "is:funny"),
            ModelRow.create_item(
                self.tr("Digital-only cards or printings",
                        "Display text"),
                self.tr("Cards and printings that are only available on digital platforms. "
                        "This includes all kinds of digital printings.",
                        "Tooltip text"),
                weight_tooltip, "hide-digital-cards", "is:digital"),
            ModelRow.create_item(
                self.tr("Reversible cards",
                        "Display text"),
                self.tr("Some single-sided cards are re-printed as two-sided, reversible cards in some "
                        "Secret Lair releases.",
                        "Tooltip text"),
                weight_tooltip, "hide-reversible-cards", "is:reversible"),
            ModelRow.create_item(
                self.tr("Universes Beyond cards", "Display text"),
                self.tr('"Universes Beyond" are cards coming from other, non-Magic IPs, like Lord of the Ring, '
                        'Marvel comics, Warhammer 40k, and a lot others.',
                        "Tooltip text"),
                weight_tooltip, "hide-universes-beyond-cards", "is:universesbeyond"),

            ModelRow.create_header(header_font,
                self.tr("Border style", "Display text. Printing filter section header")),
            ModelRow.create_item(
                self.tr("White-bordered cards",
                        "Display text"),
                None,
                weight_tooltip, "hide-white-bordered", "border:white"),
            ModelRow.create_item(
                self.tr("Gold-bordered cards",
                        "Display text"),
                self.tr("Some “collectible” sets, like full reprints of "
                        "tournament-winning decks were printed with golden borders.\n"
                        "Many also have printed signatures of the involved players in "
                        "the text box.\n\nThese are not tournament legal",
                        "Tooltip text"),
                weight_tooltip, "hide-gold-bordered", "border:gold"),
            ModelRow.create_item(
                self.tr("Borderless cards",
                        "Display text"),
                self.tr("Cards without a defined, solid-color border.\n"
                        "Those require higher cutting precision to get right.",
                        "Tooltip text"),
                weight_tooltip, "hide-borderless", "border:borderless"),
            ModelRow.create_item(
                self.tr("Extended-art cards",
                        "Display text"),
                self.tr("Cards with artwork extending to the left and right card border.\n"
                        "Similar to borderless cards, these require higher precision during the cutting process.",
                        "Tooltip text"),
                weight_tooltip, "hide-extended-art", "is:extended"),

            ModelRow.create_header(header_font,
                self.tr("Non-traditional cards", "Display text. Printing filter section header")),
            ModelRow.create_item(
                self.tr("Oversized cards",
                        "Display text"),
                self.tr("These cards are larger than regular Magic cards and can’t be included in decks.\n"
                        "Includes Archenemy schemes, Planechase planes and\noversized commander creature or "
                        "Planeswalker cards included in some pre-constructed Commander decks.",
                        "Tooltip text"),
                weight_tooltip, "hide-oversized-cards", "is:oversized"),
            ModelRow.create_item(
                self.tr("Tokens",
                        "Display text"),
                self.tr("The official Tokens, used to represent permanents created by card effects.\n"
                        "Not part of deck-building. Obscure ones can be relatively rare",
                        "Tooltip text"),
                None, "hide-token", "is:token"),
            ModelRow.create_item(
                self.tr("Art Series cards",
                        "Display text"),
                self.tr("Artwork cards that can be found in Set Boosters or Play Boosters",
                        "Tooltip text"),
                None, "hide-art-series-cards", "layout:art-series"),

            ModelRow.create_header(header_font,
                self.tr("Format bans: Hide cards banned in specific formats",
                        "Display text. Section header above MTG format ban filters")),
            ModelRow.create_format_item(
                self.tr("Brawl", "Display text. Magic format name. Translations (if one exists) "
                                 "should probably also include the English name like {translated name}(<english name>)"),
                format_ban_tooltip, "brawl"),
            ModelRow.create_format_item(
                self.tr("Commander", "Display text. Magic format name. Translations (if one exists) "
                                 "should probably also include the English name like {translated name}(<english name>)"),
                format_ban_tooltip, "commander"),
            ModelRow.create_format_item(
                self.tr("Historic", "Display text. Magic format name. Translations (if one exists) "
                                 "should probably also include the English name like {translated name}(<english name>)"),
                format_ban_tooltip, "historic"),
            ModelRow.create_format_item(
                self.tr("Legacy", "Display text. Magic format name. Translations (if one exists) "
                                 "should probably also include the English name like {translated name}(<english name>)"),
                format_ban_tooltip, "legacy"),
            ModelRow.create_format_item(
                self.tr("Modern", "Display text. Magic format name. Translations (if one exists) "
                                 "should probably also include the English name like {translated name}(<english name>)"),
                format_ban_tooltip, "modern"),
            ModelRow.create_format_item(
                self.tr("Oathbreaker", "Display text. Magic format name. Translations (if one exists) "
                                 "should probably also include the English name like {translated name}(<english name>)"),
                format_ban_tooltip, "oathbreaker"),
            ModelRow.create_format_item(
                self.tr("Pauper", "Display text. Magic format name. Translations (if one exists) "
                                 "should probably also include the English name like {translated name}(<english name>)"),
                format_ban_tooltip, "pauper"),
            ModelRow.create_format_item(
                self.tr("Pioneer", "Display text. Magic format name. Translations (if one exists) "
                                 "should probably also include the English name like {translated name}(<english name>)"),
                format_ban_tooltip, "pioneer"),
            ModelRow.create_format_item(
                self.tr("Standard", "Display text. Magic format name. Translations (if one exists) "
                                 "should probably also include the English name like {translated name}(<english name>)"),
                format_ban_tooltip, "standard"),
            ModelRow.create_format_item(
                self.tr("Vintage", "Display text. Magic format name. Translations (if one exists) "
                                 "should probably also include the English name like {translated name}(<english name>)"),
                format_ban_tooltip, "vintage"),
        ]

    def rowCount(self, /, parent: QModelIndex = QModelIndex()):
        return 0 if parent.isValid() else len(self.items)

    def columnCount(self, parent: QModelIndex = QModelIndex(), /):
        return 0 if parent.isValid() else len(ModelColumns)

    def headerData(self, section: ModelColumns, orientation: Qt.Orientation, role: ItemDataRole = DisplayRole, /):
        if orientation == Qt.Orientation.Vertical or role != DisplayRole:
            return None
        match section:
            case ModelColumns.name:
                return f'  {self.tr("Filter name", "Printing filter table header")}  '
            case ModelColumns.is_hidden:
                return f'  {self.tr("Completely hide matching cards", "Printing filter table header")}  '
            case ModelColumns.preference_weights:
                return f'  {self.tr("Printing preference", "Printing filter table header")}  '
            case _:
                return None

    def data(self, index: QModelIndex, /, role: ItemDataRole = DisplayRole):
        column = ModelColumns(index.column())
        item = self.items[index.row()]
        data = item.data(column, role)
        return data

    def setData(self, index: QModelIndex, value, /, role: ItemDataRole = DisplayRole):
        column = ModelColumns(index.column())
        item = self.items[index.row()]
        if role == CheckStateRole:
            value = CheckState(value)
            text = self.tr("Hidden", "Card filter column display text") \
                if value == CheckState.Checked \
                else self.tr("Visible", "Card filter column display text")
            item.setData(column, text, DisplayRole)
            self.dataChanged.emit(index, index, [DisplayRole])
        elif role == EditRole and column == ModelColumns.preference_weights:
            item.setData(column, value, DisplayRole)
        return item.setData(column, value, role)

    def flags(self, index: QModelIndex, /) -> Qt.ItemFlag:
        return self.data(index, ItemFlagsRole) or Qt.ItemFlag.NoItemFlags

    def load_settings(self, settings: ConfigParser):
        logger.debug("Loading printing filter state from settings")
        section = settings["card-filter"]
        printing_weights_db = self.card_db.get_printing_filter_weights()
        for row, item in enumerate(self.items):
            if item.is_hidden[CheckStateRole] is not None:
                self.setData(self.index(row, ModelColumns.is_hidden), section.get_check_state(item._settings_key), CheckStateRole)
            if item.preference_weights[EditRole] is not None:
                item.preference_weights[DisplayRole] = item.preference_weights[DisplayRole] = printing_weights_db[item._settings_key]
        self.dataChanged.emit(
            self.index(1, ModelColumns.is_hidden),  # First row isn't checkable, so skip it
            self.index(self.rowCount()-1, ModelColumns.is_hidden),
            [CheckStateRole, DisplayRole])
        self.dataChanged.emit(
            self.index(1, ModelColumns.preference_weights),  # First row isn't checkable, so skip it
            self.index(self.rowCount() - 1, ModelColumns.preference_weights),
            [DisplayRole])
        logger.debug("Done.")

    def save_settings(self, settings: ConfigParser):
        logger.debug("Saving printing filter state to settings.")
        section = settings["card-filter"]
        for row, item in enumerate(self.items):
            if item.is_hidden[CheckStateRole] is not None:
                section.set_check_state(item._settings_key, item.is_hidden[CheckStateRole])
        logger.debug("Done.")

    def get_new_preference_weights(self) -> set[tuple[str, int]]:
        result = set(
            (item._settings_key, weight)
            for item in self.items
            if (weight := item.preference_weights[EditRole]) is not None
        )
        return result


    def highlight_differing_settings(self, settings: ConfigParser):
        section = settings["card-filter"]
        printing_weights_db = self.card_db.get_printing_filter_weights()
        palette = QApplication.palette()
        highlight_color = palette.color(palette.currentColorGroup(), palette.ColorRole.Highlight)
        highlight_color.setAlpha(64)  # 25% opacity, same as the highlight_widget() implementation
        for row, item in enumerate(self.items):
            if item.is_hidden[CheckStateRole] != section.get_check_state(item._settings_key):
                index = self.index(row, ModelColumns.is_hidden)
                item.is_hidden[BackgroundRole] = highlight_color
                self.dataChanged.emit(index, index, [BackgroundRole])
            if item.preference_weights[EditRole] != printing_weights_db[item._settings_key]:
                index = self.index(row, ModelColumns.preference_weights)
                item.preference_weights[BackgroundRole] = highlight_color
                self.dataChanged.emit(index, index, [BackgroundRole])
            

    def clear_highlight(self):
        for item in self.items:
            item.is_hidden[BackgroundRole] = item.preference_weights[BackgroundRole] = None
        self.dataChanged.emit(
            self.index(0, ModelColumns.is_hidden),
            self.index(self.rowCount()-1, ModelColumns.preference_weights),
            [BackgroundRole]
        )