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


import errno
import functools
import io
import itertools
import pathlib
import shutil
import socket
import string
import threading
from typing import Iterable, TYPE_CHECKING, Callable
import urllib.error

from PySide6.QtCore import QObject, Signal, Slot, QModelIndex, Qt
from PySide6.QtGui import QPixmap, QColorConstants

if TYPE_CHECKING:
    from mtg_proxy_printer.model.document import Document

from mtg_proxy_printer.model.carddb import with_database_write_lock
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard
from mtg_proxy_printer.document_controller.replace_card import ActionReplaceCard
from mtg_proxy_printer.document_controller.import_deck_list import ActionImportDeckList
from mtg_proxy_printer.document_controller import DocumentAction
from .imagedb_files import ImageKey, CacheContent
import mtg_proxy_printer.app_dirs
import mtg_proxy_printer.downloader_base
import mtg_proxy_printer.http_file
from mtg_proxy_printer.units_and_sizes import CardSizes, CardSize
from .card import Card, CheckCard, AnyCardType
from mtg_proxy_printer.runner import AsyncTask
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

ItemDataRole = Qt.ItemDataRole
QueuedConnection = Qt.ConnectionType.QueuedConnection
BlockingQueuedConnection = Qt.ConnectionType.BlockingQueuedConnection
DEFAULT_DATABASE_LOCATION = mtg_proxy_printer.app_dirs.data_directories.user_cache_path / "CardImages"
__all__ = [
    "ImageDatabase",
]

PathSizeList = list[tuple[pathlib.Path, int]]
ImageKeySet = set[ImageKey]
BatchActions = ActionImportDeckList
SingleActions = ActionAddCard | ActionReplaceCard
IndexList = list[QModelIndex]
OptionalPixmap = QPixmap | None
download_semaphore = threading.BoundedSemaphore()


class InitOnDiskDataTask(AsyncTask):
    """
    Iterates the image storage directory and computes the set of ImageKey instances, placing them in the image database.
    """

    def __init__(self, images_on_disk: ImageKeySet, db_path: pathlib.Path):
        super().__init__()
        self.db_path = db_path
        self.images_on_disk = images_on_disk

    def run(self):
        logger.info("Reading all image IDs of images stored on disk.")
        self.images_on_disk.update(
            image.as_key() for image in read_disk_cache_content(self.db_path)
        )


class ImageDatabase(QObject):
    """
    This class manages the on-disk PNG image cache. It can asynchronously fetch images from disk or from the Scryfall
    servers, as needed, provides an in-memory cache, and allows deletion of images on disk.
    """
    request_run_async_task = Signal(AsyncTask)

    request_action = Signal(DocumentAction)
    missing_images_obtained = Signal()
    missing_image_obtained = Signal(QModelIndex)

    network_error_occurred = Signal(str)  # Emitted when downloading failed due to network issues.

    def __init__(self, db_path: pathlib.Path = DEFAULT_DATABASE_LOCATION, parent: QObject = None):
        super().__init__(parent)
        self.read_disk_cache_content: Callable[[], list[CacheContent]] = functools.partial(
            read_disk_cache_content, db_path)
        self.db_path = db_path
        _migrate_database(db_path)
        # Caches loaded images in a map from scryfall_id to image. If a file is already loaded, use the loaded instance
        # instead of loading it from disk again. This prevents duplicated file loads in distinct QPixmap instances
        # to save memory.
        self.loaded_images: dict[ImageKey, QPixmap] = {}
        self.images_on_disk: set[ImageKey] = set()
        InitOnDiskDataTask(self.images_on_disk, db_path).run()
        logger.info(f"Created {self.__class__.__name__} instance.")

    @functools.lru_cache()
    def get_blank(self, size: CardSize = CardSizes.REGULAR):
        """Returns a static, transparent QPixmap in the given size."""
        pixmap = QPixmap(size.as_qsize_px())
        pixmap.fill(QColorConstants.Transparent)
        return pixmap

    def filter_already_downloaded(self, possible_matches: list[Card]) -> list[Card]:
        """
        Takes a list of cards and returns a new list containing all cards from the source list that have
        already downloaded images. The order of cards is preserved.
        """
        return [
            card for card in possible_matches
            if ImageKey(card.scryfall_id, card.is_front, card.highres_image) in self.images_on_disk
        ]

    def delete_disk_cache_entries(self, images: Iterable[ImageKey]) -> PathSizeList:
        """
        Remove the given images from the hard disk cache.

        :returns: list with removed paths.
        """
        removed: PathSizeList = []
        for image in images:
            path = self.db_path/image.format_relative_path()
            if path.is_file():
                logger.debug(f"Removing image: {path}")
                size_bytes = path.stat().st_size
                path.unlink()
                removed.append((path, size_bytes))
                self.images_on_disk.remove(image)
                self._delete_image_parent_directory_if_empty(path)
            else:
                logger.warning(f"Trying to remove image not in the cache. Not present: {image}")
        logger.info(f"Removed {len(removed)} images from the card cache")
        return removed

    @staticmethod
    def _delete_image_parent_directory_if_empty(image_path: pathlib.Path):
        try:
            image_path.parent.rmdir()
        except OSError as e:
            if e.errno != errno.ENOTEMPTY:
                raise e

    @Slot(list)
    def obtain_missing_images(self, card_indices: IndexList):
        logger.info(f"Trying to obtain {len(card_indices)} missing images.")
        task = ObtainMissingImagesTask(self, card_indices)
        # Ensure the task lives until the Document processed it to prevent the garbage collector
        # from collecting it mid-flight through C++ code
        task.request_action.connect(self.request_action, BlockingQueuedConnection)
        self.request_run_async_task.emit(ObtainMissingImagesTask(self, card_indices))

    @Slot(ActionReplaceCard)
    @Slot(ActionAddCard)
    def fill_document_action_image(self, action: SingleActions):
        logger.debug(f"About to obtain image for card in action")
        task = SingleDownloadTask(self, action)
        # Ensure the task lives until the Document processed it to prevent the garbage collector
        # from collecting it mid-flight through C++ code
        task.request_action.connect(self.request_action, BlockingQueuedConnection)
        self.request_run_async_task.emit(task)

    @Slot(ActionImportDeckList)
    def fill_batch_document_action_images(self, action: BatchActions):
        logger.debug(f"About to obtain images for cards in batch action")
        task = BatchDownloadTask(self, action)
        # Ensure the task lives until the Document processed it to prevent the garbage collector
        # from collecting it mid-flight through C++ code
        task.request_action.connect(self.request_action, BlockingQueuedConnection)
        self.request_run_async_task.emit(task)

    @Slot(ImageKey, QPixmap)
    def on_image_obtained(self, key: ImageKey, pixmap: QPixmap):
        """Registers downloaded images for direct use in other card instances"""
        self.loaded_images[key] = pixmap
        self.images_on_disk.add(key)


class ImageDownloadTask(mtg_proxy_printer.downloader_base.DownloaderBase):
    image_obtained = Signal(ImageKey, QPixmap)
    request_action = Signal(DocumentAction)

    def __init__(self, image_db: ImageDatabase):
        super().__init__()
        self.should_run = True
        self.image_database = image_db

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
            self.tr("Downloading '{card_name}'", "Progress bar label text").format(
                card_name=card.name))
        # Disconnect the implicitly connected signals. TODO: Rework that?
        self.currently_opened_file_monitor.io_begin.disconnect(self.task_begins)
        self.currently_opened_file_monitor.total_bytes_processed.disconnect(self.set_progress)
        self.currently_opened_file_monitor.io_begin.connect(progress_container.task_begins)
        self.currently_opened_file_monitor.total_bytes_processed.connect(progress_container.set_progress)
        # Download to the root of the cache first. Move to the target only after downloading finished.
        # This prevents inserting damaged files into the cache, if the download aborts due to an application crash,
        # getting terminated by the user, a mid-transfer network outage, a full disk or any other failure condition.
        pixmap = None
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
    def __init__(self, image_db: ImageDatabase, action: SingleActions):
        super().__init__(image_db)
        self.action = action

    @with_database_write_lock(download_semaphore)
    def run(self):
        logger.info("Got DocumentAction, filling card")
        self.fetch_and_set_image(self.action.card, self)
        logger.info("Obtained image, requesting apply()")
        self.request_action.emit(self.action)


class BatchDownloadTask(ImageDownloadTask):
    def __init__(self, image_db: ImageDatabase, action: BatchActions):
        super().__init__(image_db)
        self.action = action
        self.image_download_task = AsyncTask()
        self.inner_tasks.append(self.image_download_task)

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
            self.tr("Importing deck list", "Progress bar label text"))
        for card in cards:
            self.fetch_and_set_image(card, self.image_download_task)
            self.advance_progress.emit()
        self.request_action.emit(action)
        self.task_completed.emit()
        logger.info(f"Obtained images for {total_cards} cards.")


class ObtainMissingImagesTask(ImageDownloadTask):
    missing_image_obtained = Signal(QModelIndex)

    def __init__(self, image_db: ImageDatabase, indices: IndexList):
        super().__init__(image_db)
        self.indices = indices
        if indices:
            document: "Document" = indices[0].model()
            self.missing_image_obtained.connect(document.on_missing_image_obtained, QueuedConnection)
        self.image_download_task = AsyncTask()
        self.inner_tasks.append(self.image_download_task)

    @with_database_write_lock(download_semaphore)
    def run(self):
        self.request_register_subtask.emit(self.image_download_task)
        self.obtain_missing_images(self.indices)

    def obtain_missing_images(self, card_indices: list[QModelIndex]):
        if not card_indices:
            return
        total_cards = len(card_indices)
        logger.debug(f"Requesting {total_cards} missing images")
        blanks = {self.image_database.get_blank(CardSizes.REGULAR),
                  self.image_database.get_blank(CardSizes.OVERSIZED)}
        self.task_begins.emit(
            total_cards,
            self.tr("Fetching missing images", "Progress bar label text"))
        for card_index in card_indices:
            card = card_index.data(ItemDataRole.UserRole)
            self.fetch_and_set_image(card, self.image_download_task)
            if card.image_file not in blanks:
                self.missing_image_obtained.emit(card_index)
            self.advance_progress.emit()
        self.task_completed.emit()
        logger.debug(f"Done fetching {total_cards} missing images.")


def read_disk_cache_content(db_path: pathlib.Path) -> list[CacheContent]:
    """
    Returns all entries currently in the given hard disk image cache.

    :returns: list with tuples (scryfall_id: str, is_front: bool, absolute_image_file_path: pathlib.Path)
    """
    result: list[CacheContent] = []
    data: Iterable[tuple[pathlib.Path, bool, bool]] = (
        (db_path/CacheContent.format_level_1_directory_name(is_front, is_high_resolution),
         is_front, is_high_resolution)
        for is_front, is_high_resolution in itertools.product([True, False], repeat=2)
    )
    for directory, is_front, is_high_resolution in data:
        result += (
            CacheContent(path.stem, is_front, is_high_resolution, path)
            for path in directory.glob("[0-9a-z][0-9a-z]/*.png"))
    return result


def _migrate_database(db_path: pathlib.Path):
    if not db_path.exists():
        db_path.mkdir(parents=True)
    version_file = db_path/"version.txt"
    if not version_file.exists():
        for possible_dir in map("".join, itertools.product(string.hexdigits, string.hexdigits)):
            if (path := db_path/possible_dir).exists():
                shutil.rmtree(path)
        version_file.write_text("2")
    if version_file.read_text() == "2":
        old_front = db_path/"front"
        old_back = db_path/"back"
        high_res_front = db_path/ImageKey.format_level_1_directory_name(True, True)
        low_res_front = db_path/ImageKey.format_level_1_directory_name(True, False)
        high_res_back = db_path/ImageKey.format_level_1_directory_name(False, True)
        low_res_back = db_path/ImageKey.format_level_1_directory_name(False, False)
        if old_front.exists():
            old_front.rename(low_res_front)
        else:
            low_res_front.mkdir(exist_ok=True)
        if old_back.exists():
            old_back.rename(low_res_back)
        else:
            low_res_back.mkdir(exist_ok=True)
        high_res_front.mkdir(exist_ok=True)
        high_res_back.mkdir(exist_ok=True)
        version_file.write_text("3")
