# Copyright (C) 2022 Thomas Hess <thomas.hess@udo.edu>

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

import typing

from PyQt5.QtCore import QObject, pyqtSignal as Signal, pyqtSlot as Slot, Qt

from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

__all__ = [
    "MissingImagesManager",
]


class MissingImagesManager(QObject):
    """
    This class is responsible for obtaining missing images when printing or exporting a document as a PDF.
    Cards with missing images may occur in a document, if cards were added, while the PC was offline.
    If such cards are in a document, the images should be obtained before handing the document over to the PDF renderer
    or printer.
    """
    obtaining_missing_images_failed = Signal(str)

    def __init__(self, document: Document, parent: QObject = None):
        super().__init__(parent)
        self.document = document
        self.document.image_db.batch_processing_state_changed.connect(self.on_batch_processing_runs)
        self.document.image_db.network_error_occurred.connect(lambda: setattr(self, "network_error_occurred", True))
        self.callback = None
        logger.info(f"Created {self.__class__.__name__} instance")

    def obtain_missing_images(self, callback: typing.Callable[[], typing.Any] = None):
        self.callback = callback
        images_to_fetch = [
            (index.parent().data(Qt.EditRole)[index.row()].card, index)
            for index in self.document.get_missing_image_cards()
        ]
        logger.debug(f"About to fetch {len(images_to_fetch)} missing images")
        self.document.image_db.get_card_list_asynchronous(images_to_fetch)

    @Slot(bool)
    def on_batch_processing_runs(self, state: bool):
        if not state:
            missing_count = self.document.missing_image_count()
            if missing_count:
                logger.warning(f"Failed to download all missing images. Still missing: {missing_count}.")
                plural = 's' if missing_count > 1 else ''
                self.obtaining_missing_images_failed.emit(
                    f"Unable to obtain missing image{plural} for {missing_count} card{plural}.\n"
                    f"These will be missing in exported or printed documents.")
            if self.callback is not None:
                self.callback()
                self.callback = None
