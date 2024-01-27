# Copyright (C) 2020-2024 Thomas Hess <thomas.hess@udo.edu>
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

import dataclasses
import datetime
import enum
import functools
import math
import pathlib
import typing

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, QObject, QBuffer, QIODevice, QItemSelectionModel, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QWizard, QWizardPage

from mtg_proxy_printer.natsort import NaturallySortedSortFilterProxyModel
from mtg_proxy_printer.model.carddb import CardDatabase, Card, MTGSet
from mtg_proxy_printer.model.imagedb import ImageDatabase, CacheContent as ImageCacheContent, ImageKey
from mtg_proxy_printer.ui.common import load_ui_from_file, format_size, WizardBase
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

try:
    from mtg_proxy_printer.ui.generated.cache_cleanup_wizard.card_filter_page import Ui_CardFilterPage
    from mtg_proxy_printer.ui.generated.cache_cleanup_wizard.filter_setup_page import Ui_FilterSetupPage
    from mtg_proxy_printer.ui.generated.cache_cleanup_wizard.summary_page import Ui_SummaryPage
except ModuleNotFoundError:
    Ui_CardFilterPage = load_ui_from_file("cache_cleanup_wizard/card_filter_page")
    Ui_FilterSetupPage = load_ui_from_file("cache_cleanup_wizard/filter_setup_page")
    Ui_SummaryPage = load_ui_from_file("cache_cleanup_wizard/summary_page")

__all__ = [
    "CacheCleanupWizard",
]
INVALID_INDEX = QModelIndex()


@functools.lru_cache(maxsize=256)
def get_image_for_tooltip_display(path: pathlib.Path) -> str:
    scaling_factor = 3
    source = QPixmap(str(path))
    pixmap = source.scaled(
        source.width() // scaling_factor, source.height() // scaling_factor,
        Qt.KeepAspectRatio, Qt.SmoothTransformation)
    buffer = QBuffer()
    buffer.open(QIODevice.WriteOnly)
    pixmap.save(buffer, "PNG", quality=100)
    image = bytes(buffer.data().toBase64()).decode()
    tooltip_text = f'<img src="data:image/png;base64,{image}">'
    return tooltip_text


class KnownCardColumns(enum.IntEnum):
    Name = 0
    Set = enum.auto()
    CollectorNumber = enum.auto()
    IsHidden = enum.auto()
    IsFront = enum.auto()
    HasHighResolution = enum.auto()
    Size = enum.auto()
    ScryfallId = enum.auto()
    FilesystemPath = enum.auto()


@dataclasses.dataclass()
class KnownCardRow:
    name: str
    set: MTGSet
    collector_number: str
    is_hidden: bool
    is_front: bool
    has_high_resolution: bool
    size: int
    scryfall_id: str
    path: pathlib.Path

    def data(self, column: int, role: int):
        if column == KnownCardColumns.Name and role in (Qt.DisplayRole, Qt.EditRole):
            data = self.name
        elif column == KnownCardColumns.Name and role == Qt.ToolTipRole:
            data = get_image_for_tooltip_display(self.path)
        elif column == KnownCardColumns.Set:
            data = self.set.data(role)
        elif column == KnownCardColumns.CollectorNumber and role in (Qt.DisplayRole, Qt.EditRole):
            data = self.collector_number
        elif column == KnownCardColumns.IsHidden and role == Qt.DisplayRole:
            data = "Yes" if self.is_hidden else "No"
        elif column == KnownCardColumns.IsHidden and role == Qt.ToolTipRole and self.is_hidden:
            data = "This printing is hidden by an enabled card filter\nand is thus unavailable for printing."
        elif column == KnownCardColumns.IsHidden and role == Qt.EditRole:
            data = self.is_hidden
        elif column == KnownCardColumns.IsFront and role == Qt.DisplayRole:
            data = "Front" if self.is_front else "Back"
        elif column == KnownCardColumns.IsFront and role == Qt.EditRole:
            data = self.is_front
        elif column == KnownCardColumns.HasHighResolution and role == Qt.EditRole:
            data = self.has_high_resolution
        elif column == KnownCardColumns.HasHighResolution and role == Qt.DisplayRole:
            data = "Yes" if self.has_high_resolution else "No"
        elif column == KnownCardColumns.Size and role == Qt.DisplayRole:
            data = format_size(self.size)
        elif column == KnownCardColumns.Size and role == Qt.EditRole:
            data = self.size
        elif column == KnownCardColumns.ScryfallId and role in (Qt.DisplayRole, Qt.EditRole):
            data = self.scryfall_id
        elif column == KnownCardColumns.FilesystemPath and role in {Qt.DisplayRole, Qt.ToolTipRole}:
            data = str(self.path)
        elif column == KnownCardColumns.FilesystemPath and role == Qt.EditRole:
            data = self.path
        else:
            data = None
        return data


class KnownCardImageModel(QAbstractTableModel):

    header_data = {
        KnownCardColumns.Name: "Name",
        KnownCardColumns.Set: "Set",
        KnownCardColumns.CollectorNumber: "Collector #",
        KnownCardColumns.IsHidden: "Is Hidden",
        KnownCardColumns.IsFront: "Front/Back",
        KnownCardColumns.HasHighResolution: "High resolution?",
        KnownCardColumns.Size: "Size",
        KnownCardColumns.ScryfallId: "Scryfall ID",
        KnownCardColumns.FilesystemPath: "Path",
    }

    def __init__(self, parent: QObject = None):
        super(KnownCardImageModel, self).__init__(parent)
        self._data: typing.List[KnownCardRow] = []

    def rowCount(self, parent: QModelIndex = INVALID_INDEX) -> int:
        return 0 if parent.isValid() else len(self._data)

    def columnCount(self, parent: QModelIndex = INVALID_INDEX) -> int:
        return 0 if parent.isValid() else len(self.header_data)

    def headerData(self, section: KnownCardColumns, orientation: Qt.Orientation, role: int = None) -> str:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal and 0 <= section < self.columnCount():
            return self.header_data[section]
        return super(KnownCardImageModel, self).headerData(section, orientation, role)

    def data(self, index: QModelIndex, role: int = None) -> typing.Any:
        if 0 <= index.row() <= self.rowCount() and 0 <= index.column() < self.columnCount():
            row = self._data[index.row()]
            return row.data(index.column(), role)
        return None

    def add_row(self, card: Card, image: ImageCacheContent, is_hidden: bool):
        position = self.rowCount()
        self.beginInsertRows(INVALID_INDEX, position, position)
        size_bytes = image.absolute_path.stat().st_size
        row = KnownCardRow(
            card.name, card.set, card.collector_number, is_hidden,
            image.is_front, image.is_high_resolution, size_bytes, card.scryfall_id, image.absolute_path,
        )
        self._data.append(row)
        self.endInsertRows()

    def clear(self):
        self.beginResetModel()
        self._data.clear()
        self.endResetModel()

    def all_keys(self):
        return [
            (row.scryfall_id, row.is_front)
            for row in self._data
        ]


class UnknownCardColumns(enum.IntEnum):
    ScryfallId = 0
    IsFront = 1
    HasHighResolution = 2
    Size = 3
    FilesystemPath = 4


@dataclasses.dataclass()
class UnknownCardRow:
    scryfall_id: str
    is_front: bool
    has_high_resolution: bool
    size: int
    path: pathlib.Path

    @classmethod
    def from_cache_content(cls, image: ImageCacheContent):
        return cls(
            image.scryfall_id, image.is_front, image.is_high_resolution,
            image.absolute_path.stat().st_size, image.absolute_path
        )

    def data(self, column: int, role: int):
        if column == UnknownCardColumns.ScryfallId and role in (Qt.DisplayRole, Qt.EditRole):
            data = self.scryfall_id
        elif column == UnknownCardColumns.ScryfallId and role == Qt.ToolTipRole:
            data = get_image_for_tooltip_display(self.path)
        elif column == UnknownCardColumns.IsFront and role == Qt.DisplayRole:
            data = "Front" if self.is_front else "Back"
        elif column == UnknownCardColumns.IsFront and role == Qt.EditRole:
            data = self.is_front
        elif column == UnknownCardColumns.HasHighResolution and role == Qt.EditRole:
            data = self.has_high_resolution
        elif column == UnknownCardColumns.HasHighResolution and role == Qt.DisplayRole:
            data = "Yes" if self.has_high_resolution else "No"
        elif column == UnknownCardColumns.Size and role == Qt.DisplayRole:
            data = format_size(self.size)
        elif column == UnknownCardColumns.Size and role == Qt.EditRole:
            data = self.size
        elif column == UnknownCardColumns.FilesystemPath and role in {Qt.DisplayRole, Qt.ToolTipRole}:
            data = str(self.path)
        elif column == UnknownCardColumns.FilesystemPath and role == Qt.EditRole:
            data = self.path
        else:
            data = None
        return data


class UnknownCardImageModel(QAbstractTableModel):

    header_data = {
        UnknownCardColumns.ScryfallId: "Scryfall ID",
        UnknownCardColumns.IsFront: "Front/Back",
        UnknownCardColumns.HasHighResolution: "High resolution?",
        UnknownCardColumns.Size: "Size",
        UnknownCardColumns.FilesystemPath: "Path",
    }

    def __init__(self, parent: QObject = None):
        super(UnknownCardImageModel, self).__init__(parent)
        self._data: typing.List[UnknownCardRow] = []

    def rowCount(self, parent: QModelIndex = INVALID_INDEX) -> int:
        return 0 if parent.isValid() else len(self._data)

    def columnCount(self, parent: QModelIndex = INVALID_INDEX) -> int:
        return 0 if parent.isValid() else len(self.header_data)

    def headerData(self, section: UnknownCardColumns, orientation: Qt.Orientation, role: int = None) -> str:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal and 0 <= section < self.columnCount():
            return self.header_data[section]
        return super(UnknownCardImageModel, self).headerData(section, orientation, role)

    def data(self, index: QModelIndex, role: int = None) -> typing.Any:
        if 0 <= index.row() < self.rowCount():
            row = self._data[index.row()]
            return row.data(index.column(), role)
        return None

    def add_row(self, image: ImageCacheContent):
        position = self.rowCount()
        self.beginInsertRows(INVALID_INDEX, position, position)
        row = UnknownCardRow.from_cache_content(image)
        self._data.append(row)
        self.endInsertRows()

    def clear(self):
        self.beginResetModel()
        self._data.clear()
        self.endResetModel()


class FilterSetupPage(QWizardPage):

    def __init__(self, parent: QWidget = None):
        super(FilterSetupPage, self).__init__(parent)
        self.ui = Ui_FilterSetupPage()
        self.ui.setupUi(self)
        self.registerField("remove-everything-enabled", self.ui.delete_everything_checkbox)
        self.registerField("time-filter-enabled", self.ui.time_filter_enabled_checkbox)
        self.registerField("time-filter-value", self.ui.time_filter_value_spinbox)
        self.registerField("count-filter-enabled", self.ui.count_filter_enabled_checkbox)
        self.registerField("count-filter-value", self.ui.count_filter_value_spinbox)
        self.registerField("remove-unknown-cards-enabled", self.ui.remove_unknown_cards_checkbox)
        logger.info(f"Created {self.__class__.__name__} instance.")


class CardFilterPage(QWizardPage):

    def __init__(self, card_db: CardDatabase, image_db: ImageDatabase, parent: QWidget = None):
        super(CardFilterPage, self).__init__(parent)
        self.ui = Ui_CardFilterPage()
        self.ui.setupUi(self)
        self.card_db = card_db
        self.image_db = image_db
        self.card_image_model = KnownCardImageModel(parent=self)
        self.card_image_sort_model = self._setup_card_image_sort_model(self.card_image_model)
        self._setup_card_image_view(self.card_image_sort_model)
        self.unknown_image_model = UnknownCardImageModel(parent=self)
        self.ui.unknown_image_view.setModel(self.unknown_image_model)
        self.registerField("selected-images", self)
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _setup_card_image_sort_model(self, card_image_model: KnownCardImageModel):
        sort_model = NaturallySortedSortFilterProxyModel(self)
        sort_model.setSourceModel(card_image_model)
        # Use the EditRole for sorting, as this returns the raw data.
        # Makes it possible to sort the file sizes correctly.
        sort_model.setSortRole(Qt.EditRole)
        return sort_model

    def _setup_card_image_view(self, model: NaturallySortedSortFilterProxyModel):
        view = self.ui.card_image_view
        view.setModel(model)
        view.setSortingEnabled(True)
        view.sortByColumn(KnownCardColumns.Name, Qt.AscendingOrder)
        view.setColumnHidden(KnownCardColumns.ScryfallId, True)
        for column, scaling_factor in (
                (KnownCardColumns.Name, 2),
                (KnownCardColumns.Set, 2.5),
                (KnownCardColumns.CollectorNumber, 0.95),
                (KnownCardColumns.IsFront, 0.9),
                (KnownCardColumns.Size, 0.7)):
            new_size = math.floor(view.columnWidth(column)*scaling_factor)
            view.setColumnWidth(column, new_size)

    def initializePage(self) -> None:
        super(CardFilterPage, self).initializePage()
        images = self.image_db.read_disk_cache_content()
        visible, hidden, unknown = self.card_db.get_all_cards_from_image_cache(images)
        for card, key in visible:
            self.card_image_model.add_row(card, key, False)
        for card, key in hidden:
            self.card_image_model.add_row(card, key, True)
        for key in unknown:
            self.unknown_image_model.add_row(key)
        self._apply_filter()

    def _apply_filter(self):
        self._select_unknown_cards_if_enabled()
        if self.field("remove-everything-enabled"):
            self._select_rows(range(self.card_image_model.rowCount()))
        else:
            keys = self.card_image_model.all_keys()
            if self.field("time-filter-enabled"):
                date = datetime.date.today() - datetime.timedelta(days=self.field("time-filter-value"))
                logger.debug(f"Select for deletion all images not used since {date.isoformat()}")
                indices = self.card_db.cards_not_used_since(keys, date)
                self._select_rows(indices)
            if self.field("count-filter-enabled"):
                logger.debug(f"Select for deletion all images used less that {self.field('count-filter-value')} times")
                indices = self.card_db.cards_used_less_often_then(keys, self.field("count-filter-value"))
                self._select_rows(indices)
            if self.field("remove-unknown-cards-enabled"):
                selection_model = self.ui.card_image_view.selectionModel()
                for row in range(self.card_image_sort_model.rowCount()):
                    index = self.card_image_sort_model.index(row, KnownCardColumns.IsHidden)
                    if index.data(Qt.ItemDataRole.EditRole):
                        selection_model.select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)

    def _select_unknown_cards_if_enabled(self):
        if self.field("remove-unknown-cards-enabled") or self.field("remove-everything-enabled"):
            selection_model = self.ui.unknown_image_view.selectionModel()
            for row in range(self.unknown_image_model.rowCount()):
                index = self.unknown_image_model.index(row, UnknownCardColumns.ScryfallId)
                selection_model.select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)

    def _select_rows(self, indices: typing.Iterable[int]):
        selection_model = self.ui.card_image_view.selectionModel()
        for index in indices:
            selection_model.select(
                self.card_image_model.index(index, KnownCardColumns.Name),
                QItemSelectionModel.Select | QItemSelectionModel.Rows
            )

    def cleanupPage(self) -> None:
        super(CardFilterPage, self).cleanupPage()
        self.card_image_model.clear()
        self.unknown_image_model.clear()

    def validatePage(self) -> bool:
        logger.info(f"{self.__class__.__name__}: User clicks on Next, storing the selected indices")
        selected_images: typing.List[typing.Tuple[str, bool, bool, int]] = [
            (index.siblingAtColumn(UnknownCardColumns.ScryfallId).data(Qt.EditRole),
             index.siblingAtColumn(UnknownCardColumns.IsFront).data(Qt.EditRole),
             index.siblingAtColumn(UnknownCardColumns.HasHighResolution).data(Qt.EditRole),
             index.siblingAtColumn(UnknownCardColumns.Size).data(Qt.EditRole))
            for index in self.ui.unknown_image_view.selectedIndexes() if not index.column()
        ] + [
            (index.siblingAtColumn(KnownCardColumns.ScryfallId).data(Qt.EditRole),
             index.siblingAtColumn(KnownCardColumns.IsFront).data(Qt.EditRole),
             index.siblingAtColumn(KnownCardColumns.HasHighResolution).data(Qt.EditRole),
             index.siblingAtColumn(KnownCardColumns.Size).data(Qt.EditRole))
            for index in self.ui.card_image_view.selectedIndexes() if not index.column()
        ]
        self.setField("selected-images", selected_images)
        return super(CardFilterPage, self).validatePage()


class SummaryPage(QWizardPage):

    def __init__(self, parent: QWidget = None):
        super(SummaryPage, self).__init__(parent)
        self.ui = Ui_SummaryPage()
        self.ui.setupUi(self)
        logger.info(f"Created {self.__class__.__name__} instance.")

    def initializePage(self) -> None:
        indices = self.field("selected-images")
        disk_space_freed = format_size(sum(size_bytes for _, _, _, size_bytes in indices))
        self.ui.image_count_summary.setText(f"Images about to be deleted: {len(indices)}")
        self.ui.filesize_summary.setText(f"Disk space that will be freed: {disk_space_freed}")
        logger.debug(f"{self.__class__.__name__} populated.")


class CacheCleanupWizard(WizardBase):
    BUTTON_ICONS = {
        QWizard.WizardButton.FinishButton: "edit-delete",
        QWizard.WizardButton.CancelButton: "dialog-cancel",
        QWizard.WizardButton.HelpButton: "help-contents",
    }

    def __init__(self, card_db: CardDatabase, image_db: ImageDatabase,
                 parent: QWidget = None, flags=Qt.WindowFlags()):
        super().__init__(QSize(1024, 768), parent, flags)
        self.image_db = image_db
        self.addPage(FilterSetupPage(self))
        self.addPage(CardFilterPage(card_db, image_db, self))
        self.addPage(SummaryPage(self))
        self.setWindowTitle("Cleanup locally stored card images")
        self.setWindowIcon(QIcon.fromTheme("edit-clear-history"))
        logger.info(f"Created {self.__class__.__name__} instance.")

    def accept(self) -> None:
        super(CacheCleanupWizard, self).accept()
        logger.info("User accepted the wizard, deleting entries from the cache.")
        self.image_db.delete_disk_cache_entries((
            ImageKey(scryfall_id, is_front, is_high_resolution)
            for scryfall_id, is_front, is_high_resolution, _ in self.field("selected-images")
        ))
        self._clear_tooltip_cache()

    def reject(self) -> None:
        super(CacheCleanupWizard, self).reject()
        logger.info("User canceled the cache cleanup.")
        self._clear_tooltip_cache()

    @staticmethod
    def _clear_tooltip_cache():
        logger.debug(f"Tooltip cache efficiency: {get_image_for_tooltip_display.cache_info()}")
        # Free memory by clearing the cached, base64 encoded PNGs used for tooltip display
        get_image_for_tooltip_display.cache_clear()
