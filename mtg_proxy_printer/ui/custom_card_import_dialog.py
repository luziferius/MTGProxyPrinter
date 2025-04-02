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

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from PyQt5.QtWidgets import QDialog, QWidget

from mtg_proxy_printer.model.carddb import CardDatabase, Card, MTGSet
from mtg_proxy_printer.units_and_sizes import CardSizes

try:
    from mtg_proxy_printer.ui.generated.custom_card_import_dialog import Ui_CustomCardImportDialog
except ModuleNotFoundError:
    from mtg_proxy_printer.ui.common import load_ui_from_file
    Ui_CustomCardImportDialog = load_ui_from_file("custom_card_import_dialog")

from mtg_proxy_printer.model.card_list import CardListModel  # TODO: This doesn't fit. Doesn't (yet) support editing custom cards
import mtg_proxy_printer.units_and_sizes
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger
TransformationMode = Qt.TransformationMode
EventTypes = typing.Union[QDragEnterEvent, QDropEvent]


class CustomCardImportDialog(QDialog):

    def __init__(self, card_db: CardDatabase, parent: QWidget = None, flags=Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.ui = ui = Ui_CustomCardImportDialog()
        ui.setupUi(self)
        self.model = CardListModel(card_db)
        ui.image_table.setModel(self.model)  # TODO: The table needs validators for the copies column

    @staticmethod
    def dragdrop_acceptable(event: EventTypes) -> bool:
        urls = event.mimeData().urls()
        local_paths = [Path(url.toLocalFile()) for url in urls]
        return local_paths and all((path.is_file() for path in local_paths))

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
                # TODO: The object hash has to take the URI or pixmap into account
                card = Card("Custom card", MTGSet("", ""), "", "en", "", True, "", str(path), True, regular, 1, False, pixmap)
                result[card] += 1
        return result
