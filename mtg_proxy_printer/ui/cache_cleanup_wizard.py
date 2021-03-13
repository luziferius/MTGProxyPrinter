# Copyright (C) 2021 Thomas Hess <thomas.hess@udo.edu>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import dataclasses
import datetime
import functools
import pathlib
import typing

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, QObject, QBuffer, QIODevice, QItemSelectionModel,\
    QSortFilterProxyModel
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QWizard, QTableView, QLabel

from mtg_proxy_printer.model.carddb import CardDatabase, Card
from mtg_proxy_printer.model.imagedb import ImageDatabase
from mtg_proxy_printer.ui.common import inherits_from_ui_file_with_name, load_icon
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


def format_size(size: float) -> str:
    for unit in ('', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB'):
        if -1024 < size < 1024:
            return f"{size:3.2f} {unit}"
        size /= 1024
    return f"{size:.2f} YiB"


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
    tooltip_text = '<img src="data:image/png;base64,{}">'.format(image)
    return tooltip_text


class MTGSet:

    def __init__(self, name: str, abbr: str):
        self.name = name
        self.abbr = abbr

    def data(self, role: int):
        if role == Qt.EditRole:
            return self.abbr
        elif role == Qt.DisplayRole:
            return f"{self.name} ({self.abbr.upper()})"
        elif role == Qt.ToolTipRole:
            return self.name
        else:
            return None


@dataclasses.dataclass()
class KnownCardRow:
    name: str
    set: MTGSet
    collector_number: str
    is_front: bool
    size: int
    scryfall_id: str
    path: pathlib.Path

    def data(self, column: int, role: int):
        if column == 0 and role in (Qt.DisplayRole, Qt.EditRole):
            data = self.name
        elif column == 0 and role == Qt.ToolTipRole:
            data = get_image_for_tooltip_display(self.path)
        elif column == 1:
            data = self.set.data(role)
        elif column == 2 and role in (Qt.DisplayRole, Qt.EditRole):
            data = self.collector_number
        elif column == 3 and role == Qt.DisplayRole:
            data = "Front" if self.is_front else "Back"
        elif column == 3 and role == Qt.EditRole:
            data = self.is_front
        elif column == 4 and role == Qt.DisplayRole:
            data = format_size(self.size)
        elif column == 4 and role == Qt.EditRole:
            data = self.size
        elif column == 5 and role in (Qt.DisplayRole, Qt.EditRole):
            data = self.scryfall_id
        elif column == 6 and role == Qt.DisplayRole:
            data = str(self.path)
        elif column == 6 and role == Qt.EditRole:
            data = self.path
        elif column == 6 and role == Qt.ToolTipRole:
            data = get_image_for_tooltip_display(self.path)
        else:
            data = None
        return data


class KnownCardImageModel(QAbstractTableModel):

    header_data = [
        "Name",
        "Set",
        "Collector #",
        "Front/Back",
        "Size",
        "Scryfall ID",
        "Path",
    ]

    def __init__(self, parent: QObject):
        super(KnownCardImageModel, self).__init__(parent)
        self._data: typing.List[KnownCardRow] = []

    def rowCount(self, parent: QModelIndex = None) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = None) -> int:
        return len(self.header_data)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = None) -> str:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_data[section]
        return super(KnownCardImageModel, self).headerData(section, orientation, role)

    def data(self, index: QModelIndex, role: int = None) -> typing.Any:
        if index.row() in range(0, self.rowCount()) and index.column() in range(0, self.columnCount()):
            row = self._data[index.row()]
            return row.data(index.column(), role)
        return None

    def add_row(self, card: Card, file_path: pathlib.Path):
        position = self.rowCount()
        self.rowsAboutToBeInserted.emit(QModelIndex(), position, position)
        size_bytes = file_path.stat().st_size
        row = KnownCardRow(
            card.name, MTGSet(card.set_name, card.set_abbr), card.collector_number,
            card.is_front, size_bytes, card.scryfall_id, file_path
        )
        self.beginInsertRows(QModelIndex(), position, position)
        self._data.append(row)
        self.endInsertRows()

    def clear(self):
        self.modelAboutToBeReset.emit()
        self.beginResetModel()
        self._data.clear()
        self.endResetModel()

    def all_keys(self):
        return [
            (row.scryfall_id, row.is_front)
            for row in self._data
        ]


@dataclasses.dataclass()
class UnknownCardRow:
    scryfall_id: str
    is_front: bool
    size: int
    path: pathlib.Path

    def data(self, column: int, role: int):
        if column == 0 and role in (Qt.DisplayRole, Qt.EditRole):
            data = self.scryfall_id
        elif column == 1 and role == Qt.DisplayRole:
            data = "Front" if self.is_front else "Back"
        elif column == 1 and role == Qt.EditRole:
            data = self.is_front
        elif column == 2 and role == Qt.DisplayRole:
            data = format_size(self.size)
        elif column == 2 and role == Qt.EditRole:
            data = self.size
        elif column == 3 and role == Qt.DisplayRole:
            data = str(self.path)
        elif column == 3 and role == Qt.EditRole:
            data = self.path
        elif column == 3 and role == Qt.ToolTipRole:
            data = get_image_for_tooltip_display(self.path)
        else:
            data = None
        return data


class UnknownCardImageModel(QAbstractTableModel):

    header_data = [
        "Scryfall ID",
        "Front/Back",
        "Size",
        "Path",
    ]

    def __init__(self, parent: QObject):
        super(UnknownCardImageModel, self).__init__(parent)
        self._data: typing.List[UnknownCardRow] = []

    def rowCount(self, parent: QModelIndex = None) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = None) -> int:
        return len(self.header_data)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = None) -> str:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_data[section]
        return super(UnknownCardImageModel, self).headerData(section, orientation, role)

    def data(self, index: QModelIndex, role: int = None) -> typing.Any:
        if index.row() in range(0, self.rowCount()):
            row = self._data[index.row()]
            return row.data(index.column(), role)
        return None

    def add_row(self, scryfall_id: str, is_front: bool, file_path: pathlib.Path):
        position = self.rowCount()
        self.rowsAboutToBeInserted.emit(QModelIndex(), position, position)
        row = UnknownCardRow(scryfall_id, is_front, file_path.stat().st_size, file_path)
        self.beginInsertRows(QModelIndex(), position, position)
        self._data.append(row)
        self.endInsertRows()

    def clear(self):
        self.modelAboutToBeReset.emit()
        self.beginResetModel()
        self._data.clear()
        self.endResetModel()


class FilterSetupPage(*inherits_from_ui_file_with_name("cache_cleanup_wizard/filter_setup_page")):

    def __init__(self, parent: QWidget = None):
        super(FilterSetupPage, self).__init__(parent)
        self.setupUi(self)
        self.registerField("remove-everything-enabled", self.delete_everything_checkbox)
        self.registerField("time-filter-enabled", self.time_filter_enabled_checkbox)
        self.registerField("time-filter-value", self.time_filter_value_spinbox)
        self.registerField("count-filter-enabled", self.count_filter_enabled_checkbox)
        self.registerField("count-filter-value", self.count_filter_value_spinbox)
        self.registerField("remove-unknown-cards-enabled", self.remove_unknown_cards_checkbox)
        logger.info(f"Created {self.__class__.__name__} instance.")


class CardFilterPage(*inherits_from_ui_file_with_name("cache_cleanup_wizard/card_filter_page")):

    def __init__(self, card_db: CardDatabase, image_db: ImageDatabase, parent: QWidget = None):
        super(CardFilterPage, self).__init__(parent)
        self.setupUi(self)
        self.card_db = card_db
        self.image_db = image_db
        self.unknown_image_view: QTableView
        self.card_image_view: QTableView
        self.card_image_model = KnownCardImageModel(parent=self)
        self.card_image_sort_model = QSortFilterProxyModel(self)
        self.card_image_sort_model.setSourceModel(self.card_image_model)
        self.unknown_image_model = UnknownCardImageModel(parent=self)
        self.card_image_view.setModel(self.card_image_sort_model)
        # Use the EditRole for sorting, as this returns the raw data.
        # Makes it possible to sort the file sizes correctly.
        self.card_image_sort_model.setSortRole(Qt.EditRole)
        self.card_image_view.setSortingEnabled(True)
        self.card_image_view.sortByColumn(0, Qt.AscendingOrder)
        self.unknown_image_view.setModel(self.unknown_image_model)
        self.registerField("selected-images", self)
        logger.info(f"Created {self.__class__.__name__} instance.")

    def initializePage(self) -> None:
        super(CardFilterPage, self).initializePage()
        images_in_cache = self.image_db.get_cache_content()
        for scryfall_id, is_front, file_path in images_in_cache:
            if (card := self.card_db.get_card_with_scryfall_id(scryfall_id, is_front)) is not None:
                self.card_image_model.add_row(card, file_path)
            else:
                self.unknown_image_model.add_row(scryfall_id, is_front, file_path)
        self._apply_filter()

    def _apply_filter(self):
        self._select_unknown_cards_if_enabled()
        self.card_image_view: QTableView
        if self.field("remove-everything-enabled"):
            self._select_indices(range(self.card_image_model.rowCount()))
        else:
            keys = self.card_image_model.all_keys()
            if self.field("time-filter-enabled"):
                date = datetime.date.today() - datetime.timedelta(days=self.field("time-filter-value"))
                logger.debug(f"Select for deletion all images not used since {date.isoformat()}")
                indices = self.card_db.cards_not_used_since(keys, date)
                self._select_indices(indices)
            if self.field("count-filter-enabled"):
                logger.debug(f"Select for deletion all images used less that {self.field('count-filter-value')} times")
                indices = self.card_db.cards_used_less_often_then(keys, self.field("count-filter-value"))
                self._select_indices(indices)

    def _select_unknown_cards_if_enabled(self):
        self.unknown_image_view: QTableView
        if self.field("remove-unknown-cards-enabled") or self.field("remove-everything-enabled"):
            for row in range(self.unknown_image_model.rowCount()):
                self.unknown_image_view.selectionModel().select(
                    self.unknown_image_model.createIndex(row, 0),
                    QItemSelectionModel.Select | QItemSelectionModel.Rows
                )

    def _select_indices(self, indices: typing.Iterable[int]):
        self.card_image_view: QTableView
        selection_model = self.card_image_view.selectionModel()
        for index in indices:
            selection_model.select(
                self.card_image_model.createIndex(index, 0),
                QItemSelectionModel.Select | QItemSelectionModel.Rows
            )

    def cleanupPage(self) -> None:
        super(CardFilterPage, self).cleanupPage()
        self.card_image_model.clear()
        self.unknown_image_model.clear()

    def validatePage(self) -> bool:
        logger.info(f"{self.__class__.__name__}: User clicks on Next, storing the selected indices")
        self.unknown_image_view: QTableView
        self.card_image_view: QTableView
        selected_images: typing.List[typing.Tuple[str, bool, int]] = [
            (index.siblingAtColumn(0).data(Qt.EditRole),
             index.siblingAtColumn(1).data(Qt.EditRole),
             index.siblingAtColumn(2).data(Qt.EditRole))
            for index in self.unknown_image_view.selectedIndexes() if not index.column()
        ] + [
            (index.siblingAtColumn(5).data(Qt.EditRole),
             index.siblingAtColumn(3).data(Qt.EditRole),
             index.siblingAtColumn(4).data(Qt.EditRole))
            for index in self.card_image_view.selectedIndexes() if not index.column()
        ]
        self.setField("selected-images", selected_images)
        return super(CardFilterPage, self).validatePage()


class SummaryPage(*inherits_from_ui_file_with_name("cache_cleanup_wizard/summary_page")):

    def __init__(self, parent: QWidget = None):
        super(SummaryPage, self).__init__(parent)
        self.setupUi(self)
        logger.info(f"Created {self.__class__.__name__} instance.")

    def initializePage(self) -> None:
        self.image_count_summary: QLabel
        self.filesize_summary: QLabel
        indices = self.field("selected-images")
        disk_space_freed = format_size(sum(size_bytes for _, _, size_bytes in indices))
        self.image_count_summary.setText(f"Images about to be deleted: {len(indices)}")
        self.filesize_summary.setText(f"Disk space that will be freed: {disk_space_freed}")
        logger.debug(f"{self.__class__.__name__} populated.")


class CacheCleanupWizard(QWizard):

    def __init__(self, card_db: CardDatabase, image_db: ImageDatabase, *args, **kwargs):
        super(CacheCleanupWizard, self).__init__(*args, **kwargs)
        self.image_db = image_db
        self.addPage(FilterSetupPage(self))
        self.addPage(CardFilterPage(card_db, image_db, self))
        self.addPage(SummaryPage(self))
        self.setWindowTitle("Cleanup the local image cache")
        self._setup_window_icon()
        self._setup_button_icons()
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _setup_window_icon(self, icon_name: str = "edit-clear-history"):
        icon = QIcon.fromTheme(icon_name)
        if icon.isNull():
            icon = load_icon(icon_name)
        self.setWindowIcon(icon)

    def _setup_button_icons(self):
        buttons_with_icons: typing.List[typing.Tuple[QWizard.WizardButton, str]] = [
            (QWizard.CancelButton, "dialog-cancel"),
            (QWizard.HelpButton, "help-contents"),
            (QWizard.FinishButton, "edit-delete"),
        ]
        for button, icon_name in buttons_with_icons:
            icon = QIcon.fromTheme(icon_name)
            if icon.isNull():
                icon = load_icon(icon_name)
            self.button(button).setIcon(icon)

    def accept(self) -> None:
        super(CacheCleanupWizard, self).accept()
        logger.info("User accepted the wizard, deleting entries from the cache.")
        self.image_db.delete_entries((
            (scryfall_id, is_front)
            for scryfall_id, is_front, _ in self.field("selected-images")
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

