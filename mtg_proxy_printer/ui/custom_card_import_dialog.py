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

from pathlib import Path
import typing

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from PyQt5.QtWidgets import QDialog, QWidget

try:
    from mtg_proxy_printer.ui.generated.custom_card_import_dialog import Ui_CustomCardImportDialog
except ModuleNotFoundError:
    from mtg_proxy_printer.ui.common import load_ui_from_file
    Ui_CustomCardImportDialog = load_ui_from_file("custom_card_import_dialog")

import mtg_proxy_printer.units_and_sizes
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger
TransformationMode = Qt.TransformationMode
EventTypes = typing.Union[QDragEnterEvent, QDropEvent]


class CustomCardImportDialog(QDialog):

    def __init__(self, parent: QWidget = None, flags=Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.ui = ui = Ui_CustomCardImportDialog()
        ui.setupUi(self)

    @staticmethod
    def dragdrop_acceptable(event: EventTypes) -> bool:
        urls = event.mimeData().urls()
        local_paths = [Path(url.toLocalFile()) for url in urls]
        return local_paths and all((path.is_file() for path in local_paths))

    @staticmethod
    def populate_model(event: QDropEvent):
        result: typing.List[QPixmap] = []
        mime_data = event.mimeData()
        regular = mtg_proxy_printer.units_and_sizes.CardSizes.REGULAR
        width, height = regular.width.magnitude, regular.height.magnitude
        for url in mime_data.urls():
            pixmap = QPixmap(url.toLocalFile())
            if not pixmap.isNull():
                if pixmap.width() != width or pixmap.height() != height:
                    new_size = QSize(width, height)
                    pixmap = pixmap.scaled(new_size, transformMode=TransformationMode.SmoothTransformation)
                result.append(pixmap)