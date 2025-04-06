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

from collections import Counter
from pathlib import Path
import typing

from PyQt5.QtCore import Qt, QSize, pyqtSignal as Signal, pyqtSlot as Slot
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from PyQt5.QtWidgets import QDialog, QWidget, QFileDialog

from mtg_proxy_printer.document_controller import DocumentAction
from mtg_proxy_printer.document_controller.import_deck_list import ActionImportDeckList
from mtg_proxy_printer.model.carddb import CardDatabase, Card, MTGSet
from mtg_proxy_printer.units_and_sizes import CardSizes

try:
    from mtg_proxy_printer.ui.generated.custom_card_import_dialog import Ui_CustomCardImportDialog
except ModuleNotFoundError:
    from mtg_proxy_printer.ui.common import load_ui_from_file
    Ui_CustomCardImportDialog = load_ui_from_file("custom_card_import_dialog")

from mtg_proxy_printer.model.card_list import CardListModel
import mtg_proxy_printer.units_and_sizes
from mtg_proxy_printer.app_dirs import data_directories
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger
TransformationMode = Qt.TransformationMode
EventTypes = typing.Union[QDragEnterEvent, QDropEvent]


class CustomCardImportDialog(QDialog):

    request_action = Signal(DocumentAction)

    def __init__(self, card_db: CardDatabase, parent: QWidget = None, flags=Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.ui = ui = Ui_CustomCardImportDialog()
        ui.setupUi(self)
        self.model = CardListModel(card_db)
        ui.card_table.setModel(self.model)
        logger.info(f"Created {self.__class__.__name__} instance")

    @staticmethod
    def dragdrop_acceptable(event: EventTypes) -> bool:
        urls = event.mimeData().urls()
        local_paths = [Path(url.toLocalFile()) for url in urls]
        acceptable = local_paths and all((path.is_file() for path in local_paths))
        return acceptable

    @Slot()
    def on_add_cards_clicked(self):
        logger.info("User about to add additional card images")
        default_path = getattr(data_directories, "user_pictures_dir", str(Path.home()))
        files, _ = QFileDialog.getOpenFileNames(self, self.tr("Import custom cards"), default_path)
        logger.debug(f"User selected {len(files)} paths")
        file_paths = list(map(Path, files))
        cards = self.create_cards(file_paths)
        self.model.add_cards(cards)
        logger.info(f"Added {len(cards)} cards from the selected files.")

    @Slot()
    def on_remove_selected_clicked(self):
        logger.info("User about to delete all selected cards from the card table")
        self.model.clear()

    @Slot()
    def on_set_copies_to_clicked(self):
        value = 1
        self.model.set_all_copies_to(value)
        logger.info(f"All copy counts set to {value}")

    def show_from_drop_event(self, event: QDropEvent):
        urls = event.mimeData().urls()
        local_paths = [Path(url.toLocalFile()) for url in urls]
        cards = self.create_cards(local_paths)
        self.model.add_cards(cards)
        self.show()

    @staticmethod
    def create_cards(paths: typing.List[Path]) -> typing.Counter[Card]:
        result: typing.Counter[Card] = Counter()
        regular = mtg_proxy_printer.units_and_sizes.CardSizes.REGULAR
        width, height = regular.width.magnitude, regular.height.magnitude
        for path in paths:
            pixmap = QPixmap(str(path))
            if not pixmap.isNull():
                if pixmap.width() != width or pixmap.height() != height:
                    new_size = QSize(width, height)
                    pixmap = pixmap.scaled(new_size, transformMode=TransformationMode.SmoothTransformation)
                card = Card(
                    path.stem, MTGSet("", ""), "", "en", "", True, "", str(path), True, regular, 1, False, pixmap
                )
                result[card] += 1
        return result

    def accept(self):
        action = ActionImportDeckList(self.model.as_cards(), False)
        self.request_action.emit(action)
        super().accept()