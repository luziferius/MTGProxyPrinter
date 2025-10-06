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


from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, Signal, Slot

from mtg_proxy_printer.async_tasks.image_downloader import ObtainMissingImagesTask
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
    request_run_async_task = Signal(ObtainMissingImagesTask)

    def __init__(self, document: Document, parent: QObject = None):
        super().__init__(parent)
        self.document = document
        self.image_db = document.image_db
        self.callback = None
        logger.info(f"Created {self.__class__.__name__} instance")

    def obtain_missing_images(self, callback: Callable[[], Any] = None):
        self.callback = callback
        images_to_fetch = list(self.document.get_missing_image_cards())
        logger.debug(f"About to fetch {len(images_to_fetch)} missing images")
        task = ObtainMissingImagesTask(self.image_db, images_to_fetch)
        task.task_completed.connect(self.on_missing_images_obtained)
        self.request_run_async_task.emit(task)

    @Slot()
    def on_missing_images_obtained(self):
        logger.info("Obtained missing images")
        if n := self.document.missing_image_count():
            logger.warning(f"Failed to download all missing images. Still missing: {n}.")
            self.obtaining_missing_images_failed.emit(self.tr(
                "Unable to obtain %n missing card image(s).\n"
                "These will be missing in exported or printed documents.",
                "Warning message. A last attempt at trying to download images of cards with missing images failed.",
                n))
        if self.callback is not None:
            self.callback()
            self.callback = None
