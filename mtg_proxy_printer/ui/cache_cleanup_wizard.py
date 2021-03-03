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
import pathlib
import typing

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, QObject, QBuffer, QIODevice
from PyQt5.QtGui import QIcon, QPixmapCache, QPixmap
from PyQt5.QtWidgets import QWidget, QWizard, QWizardPage

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
    pixmap_cache: QPixmapCache = None

    def data(self, column: int, role: int):
        if column == 0 and role in (Qt.DisplayRole, Qt.EditRole):
            data = self.name
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
            key = f"{self.scryfall_id}-{self.is_front}"
            if (pixmap := self.pixmap_cache.find(key)) is None:
                pixmap = QPixmap(str(self.path))
                scaling_factor = 3
                pixmap = pixmap.scaled(
                    pixmap.width()//scaling_factor, pixmap.height()//scaling_factor,
                    Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.pixmap_cache.insert(key, pixmap)
            buffer = QBuffer()
            buffer.open(QIODevice.WriteOnly)
            pixmap.save(buffer, "PNG", quality=100)
            image = bytes(buffer.data().toBase64()).decode()
            data = '<img src="data:image/png;base64,{}">'.format(image)
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
        self.pixmap_cache = QPixmapCache()
        self.pixmap_cache.setCacheLimit(100)

    def rowCount(self, parent: QModelIndex = None) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = None) -> int:
        return len(self.header_data)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = None) -> str:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_data[section]
        return super(KnownCardImageModel, self).headerData(section, orientation, role)

    def data(self, index: QModelIndex, role: int = None) -> typing.Any:
        if index.row() in range(0, self.rowCount()):
            row = self._data[index.row()]
            return row.data(index.column(), role)
        return None

    def add_row(self, card: Card, file_path: pathlib.Path, size_bytes: int):
        position = self.rowCount()
        self.rowsAboutToBeInserted.emit(QModelIndex(), position, position)
        row = KnownCardRow(
            card.name, MTGSet(card.set_name, card.set_abbr), card.collector_number,
            card.is_front, size_bytes, card.scryfall_id, file_path, self.pixmap_cache
        )
        self.beginInsertRows(QModelIndex(), position, position)
        self._data.append(row)
        self.endInsertRows()

    def clear(self):
        self.modelAboutToBeReset.emit()
        self.beginResetModel()
        self._data.clear()
        self.endResetModel()


class UnknownCardImageModel(QAbstractTableModel):

    header_data = [
        "Scryfall ID",
        "Front/Back",
        "Size",
        "Path",
    ]

    def columnCount(self, parent: QModelIndex = None) -> int:
        return len(self.header_data)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = None) -> str:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_data[section]
        return super(UnknownCardImageModel, self).headerData(section, orientation, role)


class FilterSetupPage(*inherits_from_ui_file_with_name("cache_cleanup_wizard/filter_setup_page")):

    def __init__(self, parent: QWidget = None):
        super(FilterSetupPage, self).__init__(parent)
        self.setupUi(self)
        self.registerField("time-filter-enabled", self.time_filter_enabled_checkbox)
        self.registerField("time-filter-value", self.time_filter_value_spinbox)
        self.registerField("filter-combination-choice", self.combination_choice_combobox)
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
        self.card_images_model = KnownCardImageModel(parent=self)
        self.unknown_images_model = UnknownCardImageModel(parent=self)
        self.card_image_view.setModel(self.card_images_model)
        self.unknown_image_view.setModel(self.unknown_images_model)

        logger.info(f"Created {self.__class__.__name__} instance.")

    def initializePage(self) -> None:
        super(CardFilterPage, self).initializePage()
        images_in_cache = self.image_db.get_cache_content()
        for scryfall_id, is_front, file_path in images_in_cache:
            if self.card_db.is_scryfall_id_known(scryfall_id, is_front):
                card = self.card_db.get_card_with_scryfall_id(scryfall_id, is_front)
                self.card_images_model.add_row(card, file_path, file_path.stat().st_size)
            else:
                model = self.unknown_images_model
                if model.insertRow(model.rowCount()):
                    model.setData(model.index(model.rowCount()-1, 0), f"{scryfall_id}, {is_front=}")
        pass

    def cleanupPage(self) -> None:
        super(CardFilterPage, self).cleanupPage()
        self.card_images_model.clear()
        self.unknown_images_model.removeRows(0, self.unknown_images_model.rowCount())


class CacheCleanupWizard(QWizard):

    def __init__(self, card_db: CardDatabase, image_db: ImageDatabase, *args, **kwargs):
        super(CacheCleanupWizard, self).__init__(*args, **kwargs)
        self.addPage(FilterSetupPage(self))
        self.addPage(CardFilterPage(card_db, image_db, self))
        self.setWindowTitle("Cleanup the local image cache")
        icon_name = "edit-clear-history"
        icon = QIcon.fromTheme(icon_name)
        self.setWindowIcon(icon if not icon.isNull() else load_icon(icon_name))
        logger.info(f"Created {self.__class__.__name__} instance.")
