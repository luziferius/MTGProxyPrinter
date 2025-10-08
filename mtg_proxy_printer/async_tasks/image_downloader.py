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

import pathlib
import shutil
import socket
import threading
from typing import TYPE_CHECKING
import urllib.error

from PySide6.QtCore import Qt, QModelIndex, Signal
from PySide6.QtGui import QPixmap

import mtg_proxy_printer.async_tasks.downloader_base
from mtg_proxy_printer.async_tasks.base import AsyncTask
from mtg_proxy_printer.document_controller import DocumentAction

from mtg_proxy_printer.document_controller.card_actions import ActionAddCard
from mtg_proxy_printer.document_controller.import_deck_list import ActionImportDeckList
from mtg_proxy_printer.document_controller.replace_card import ActionReplaceCard
from mtg_proxy_printer.model.card import AnyCardType, CheckCard, Card
from mtg_proxy_printer.model.carddb import with_database_write_lock
if TYPE_CHECKING:
    from mtg_proxy_printer.model.document import Document
    from mtg_proxy_printer.model.imagedb import ImageDatabase
from mtg_proxy_printer.model.imagedb_files import ImageKey
from mtg_proxy_printer.units_and_sizes import CardSizes

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

ItemDataRole = Qt.ItemDataRole
QueuedConnection = Qt.ConnectionType.QueuedConnection
BatchActions = ActionImportDeckList
SingleActions = ActionAddCard | ActionReplaceCard
IndexList = list[QModelIndex]
OptionalPixmap = QPixmap | None
download_semaphore = threading.BoundedSemaphore()

__all__ = [
    "ImageDownloadTask",
    "SingleDownloadTask",
    "BatchDownloadTask",
    "ObtainMissingImagesTask",
]


class ImageDownloadTask(mtg_proxy_printer.async_tasks.downloader_base.DownloaderBase):
    image_obtained = Signal(ImageKey, QPixmap)
    request_action = Signal(DocumentAction)

    def __init__(self, image_db: "ImageDatabase"):
        super().__init__()
        self.image_obtained.connect(image_db.on_image_obtained, QueuedConnection)
        self.should_run = True
        self.image_database = image_db
        # Populated with the currently open file in run(). Accessed by cancel().
        self.currently_opened_file = self.currently_opened_file_monitor = None

    def fetch_and_set_image(self, card: AnyCardType, progress_container: AsyncTask):
        """
        Fetch the image for the given card. Fetches both sides for DFCs. Implicitly populates the memory and disk cache.
        :param card: Card to download the image for. When completed successfully, the image is loaded into the card
        :param progress_container: AsyncTask via which download progress is reported. Can be self,
          or a subtask for batch downloads
        """
        try:
            if isinstance(card, CheckCard):
                self._fetch_and_set_image(card.front, progress_container)
                self._fetch_and_set_image(card.back, progress_container)
            else:
                self._fetch_and_set_image(card, progress_container)
        except urllib.error.URLError as e:
            self._handle_network_error_during_download(card, str(e.reason))
        except socket.timeout as e:
            self._handle_network_error_during_download(card, f"Reading from socket failed: {e}")

    def _fetch_and_set_image(self, card: Card, progress_container: AsyncTask):
        key = ImageKey(card.scryfall_id, card.is_front, card.highres_image)
        image_path = self.image_database.db_path / key.format_relative_path()
        blank = self.image_database.get_blank(card.size)
        pixmap = self._load_from_memory(key) \
            or self._load_from_disk(image_path, card.name) \
            or self._download_from_scryfall(card, image_path, progress_container) \
            or blank
        if pixmap is not blank:
            self._remove_outdated_low_resolution_image(card)
            self.image_obtained.emit(key, pixmap)
        card.set_image_file(pixmap)

    def _load_from_memory(self, key: ImageKey) -> OptionalPixmap:
        return self.image_database.loaded_images.get(key)

    def _load_from_disk(self, image_path: pathlib.Path, card_name: str) -> OptionalPixmap:
        if not self.should_run:
            return None
        logger.debug(f'Image of "{card_name}" not in memory, requesting from disk')
        if image_path.exists():
            pixmap = QPixmap(str(image_path))
            if pixmap.isNull():
                logger.warning(f'Failed to load image from "{image_path}", deleting corrupted file.')
                image_path.unlink()
            else:
                logger.debug("Image loaded from disk")
                return pixmap
        return None

    def _download_from_scryfall(
            self, card: Card, image_path: pathlib.Path, progress_container: AsyncTask) -> OptionalPixmap:
        if not self.should_run:
            return None
        logger.debug(f'Image of "{card.name}" not on disk, downloading from Scryfall')
        image_path.parent.mkdir(parents=True, exist_ok=True)
        download_uri = card.image_uri
        # Download to the root of the image database directory, not into the target directory. If something goes wrong,
        # the incomplete image can be deleted. Once loading the image succeeds, it can be moved to the final location.
        # Append the side, so that concurrent downloads of both sides of a DFC do not collide.
        side = 'Front' if card.is_front else 'Back'
        download_path = self.image_database.db_path / f"{image_path.stem}-{side}{image_path.suffix}"
        self.currently_opened_file, self.currently_opened_file_monitor = self.read_from_url(
            download_uri,
            self.tr("Downloading '{card_name}':", "Progress bar label text").format(
                card_name=card.name))
        if not self.should_run:
            # The code may have hung on a broken network socket. In that case, return here if cancel() was run while it
            # was unable to close the file which wasn't yet opened.
            return None
        # Disconnect the implicitly connected signals. TODO: Rework that?
        self.currently_opened_file_monitor.io_begin.disconnect(self.task_begins)
        self.currently_opened_file_monitor.total_bytes_processed.disconnect(self.set_progress)
        self.currently_opened_file_monitor.io_begin.connect(progress_container.task_begins)
        self.currently_opened_file_monitor.total_bytes_processed.connect(progress_container.set_progress)
        try:
            with self.currently_opened_file, download_path.open("wb") as file_in_cache:
                shutil.copyfileobj(self.currently_opened_file, file_in_cache)
            pixmap = QPixmap(str(download_path))
            if pixmap.isNull():
                raise ValueError("Invalid image fetched from Scryfall")
        except Exception as e:
            logger.exception(e)
            logger.info("Download aborted, not moving potentially incomplete download into the cache.")
            download_path.unlink(missing_ok=True)
        else:
            logger.debug(f"Moving downloaded image into the image cache at {image_path}")
            shutil.move(download_path, image_path)
        finally:
            self.currently_opened_file = None
            download_path.unlink(missing_ok=True)
            progress_container.task_completed.emit()
        return pixmap

    def _remove_outdated_low_resolution_image(self, card: Card):
        if not card.highres_image:
            return
        low_resolution_image_path = self.image_database.db_path / ImageKey(
            card.scryfall_id, card.is_front, False).format_relative_path()
        if low_resolution_image_path.exists():
            logger.info(f"Removing outdated low-resolution image of {card.name}")
            low_resolution_image_path.unlink()
        try:  # Clean-up the parent directory used to bucket the images
            low_resolution_image_path.parent.rmdir()
        except (OSError, FileNotFoundError):  # It may not exist, or contain other images, so ignore those errors
            pass

    def _handle_network_error_during_download(self, card: Card, reason_str: str):
        card.set_image_file(self.image_database.get_blank(card.size))
        logger.warning(
            f"Image download failed for card {card}, reason is \"{reason_str}\". Using blank replacement image.")
        self.network_error_occurred.emit(reason_str)


class SingleDownloadTask(ImageDownloadTask):
    def __init__(self, image_db: "ImageDatabase", action: SingleActions):
        super().__init__(image_db)
        self.action = action

    @with_database_write_lock(download_semaphore)
    def run(self):
        logger.info("Got DocumentAction, filling card")
        # Card replacement is an asynchronous task operating on a card in the model. At the time of action application,
        # the card may have been moved, then deleted, that delete undone, or similar. It is not possible to track it
        # using a QPersistentModelIndex through all possible edits. Especially deleting the card, even if only temporary,
        # is problematic. So lock the UI while the app replaces a printing.
        requires_ui_lock = isinstance(self.action, ActionReplaceCard)
        try:
            if requires_ui_lock:
                self.ui_lock_acquire.emit()
            self.fetch_and_set_image(self.action.card, self)
            logger.info("Obtained image, requesting apply()")
            self.request_action.emit(self.action)
        finally:
            if requires_ui_lock:
                self.ui_lock_release.emit()


class BatchDownloadTask(ImageDownloadTask):
    def __init__(self, image_db: "ImageDatabase", action: BatchActions):
        super().__init__(image_db)
        self.action = action
        self.image_download_task = AsyncTask()
        self.inner_tasks.append(self.image_download_task)

    @property
    def can_cancel(self) -> bool:
        return True

    def cancel(self):
        self.should_run = False

    @with_database_write_lock(download_semaphore)
    def run(self):
        self.request_register_subtask.emit(self.image_download_task)
        self.fill_batch_document_action_images(self.action)

    def fill_batch_document_action_images(self, action: BatchActions):
        cards = action.cards
        total_cards = len(cards)
        logger.info(f"Got batch DocumentAction, filling {total_cards} cards")
        self.task_begins.emit(
            total_cards,
            self.tr("Importing deck list:", "Progress bar label text"))
        for card in cards:
            if not self.should_run:
                return
            self.fetch_and_set_image(card, self.image_download_task)
            self.advance_progress.emit()
        self.request_action.emit(action)
        self.task_completed.emit()
        logger.info(f"Obtained images for {total_cards} cards.")


class ObtainMissingImagesTask(ImageDownloadTask):
    missing_image_obtained = Signal(QModelIndex)

    def __init__(self, image_db: "ImageDatabase", indices: IndexList):
        super().__init__(image_db)
        self.indices = indices
        if indices:
            document: "Document" = indices[0].model()
            self.missing_image_obtained.connect(document.on_missing_image_obtained, QueuedConnection)
        self.image_download_task = AsyncTask()
        self.inner_tasks.append(self.image_download_task)

    @property
    def can_cancel(self) -> bool:
        return True

    def cancel(self):
        self.should_run = False

    @with_database_write_lock(download_semaphore)
    def run(self):
        self.request_register_subtask.emit(self.image_download_task)
        self.obtain_missing_images(self.indices)

    def obtain_missing_images(self, card_indices: list[QModelIndex]):
        if not card_indices:
            self.task_completed.emit()
            return
        total_cards = len(card_indices)
        logger.debug(f"Requesting {total_cards} missing images")
        blanks = {self.image_database.get_blank(CardSizes.REGULAR),
                  self.image_database.get_blank(CardSizes.OVERSIZED)}
        self.task_begins.emit(
            total_cards,
            self.tr("Fetching missing images:", "Progress bar label text"))
        for card_index in card_indices:
            if not self.should_run:
                self.task_completed.emit()
                return
            card = card_index.data(ItemDataRole.UserRole)
            self.fetch_and_set_image(card, self.image_download_task)
            if card.image_file not in blanks:
                self.missing_image_obtained.emit(card_index)
            self.advance_progress.emit()
        self.task_completed.emit()
        logger.debug(f"Done fetching {total_cards} missing images.")
