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
import errno
import functools
import io
import itertools
import pathlib
import shutil
import socket
import string
import typing
import urllib.error

from PyQt5.QtCore import QObject, pyqtSignal as Signal, pyqtSlot as Slot, QSize, QModelIndex, Qt, QThreadPool
from PyQt5.QtGui import QPixmap, QColor

from mtg_proxy_printer.document_controller.card_actions import ActionAddCard
from mtg_proxy_printer.document_controller.replace_card import ActionReplaceCard
from mtg_proxy_printer.document_controller.import_deck_list import ActionImportDeckList
from mtg_proxy_printer.document_controller import DocumentAction
import mtg_proxy_printer.app_dirs
import mtg_proxy_printer.downloader_base
import mtg_proxy_printer.http_file
from mtg_proxy_printer.model.carddb import Card, CheckCard, AnyCardType
from mtg_proxy_printer.runner import Runnable
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

ItemDataRole = Qt.ItemDataRole
DEFAULT_DATABASE_LOCATION = mtg_proxy_printer.app_dirs.data_directories.user_cache_path / "CardImages"
__all__ = [
    "ImageDatabase",
    "ImageDownloader",
    "CacheContent",
    "ImageKey",
]


@dataclasses.dataclass(frozen=True)
class ImageKey:
    scryfall_id: str
    is_front: bool
    is_high_resolution: bool

    def format_relative_path(self) -> pathlib.Path:
        """Returns the file system path of the associated image relative to the image database root path."""
        level1 = self.format_level_1_directory_name(self.is_front, self.is_high_resolution)
        return pathlib.Path(level1, self.scryfall_id[:2], f"{self.scryfall_id}.png")

    @staticmethod
    def format_level_1_directory_name(is_front: bool, is_high_resolution: bool) -> str:
        side = "front" if is_front else "back"
        res = "highres" if is_high_resolution else "lowres"
        return f"{res}_{side}"


@dataclasses.dataclass(frozen=True)
class CacheContent(ImageKey):
    absolute_path: pathlib.Path

    def as_key(self):
        return ImageKey(self.scryfall_id, self.is_front, self.is_high_resolution)


PathSizeList = typing.List[typing.Tuple[pathlib.Path, int]]
ImageKeySet = typing.Set[ImageKey]
IMAGE_SIZE = QSize(745, 1040)
BatchActions = typing.Union[ActionImportDeckList]
SingleActions = typing.Union[ActionAddCard, ActionReplaceCard]
IndexList = typing.List[QModelIndex]
OptionalPixmap = typing.Optional[QPixmap]


class InitOnDiskDataRunner(Runnable):
    """
    Iterates the image storage directory and computes the set of ImageKey instances, placing them in the image database.
    """

    def __init__(self, images_on_disk: ImageKeySet, db_path: pathlib.Path):
        super().__init__()
        self.db_path = db_path
        self.images_on_disk = images_on_disk

    def run(self):
        logger.info("Reading all image IDs of images stored on disk.")
        try:
            self.images_on_disk.update(
                image.as_key() for image in read_disk_cache_content(self.db_path)
            )
        finally:
            self.release_instance()


class ImageDatabase(QObject):
    """
    This class manages the on-disk PNG image cache. It can asynchronously fetch images from disk or from the Scryfall
    servers, as needed, provides an in-memory cache, and allows deletion of images on disk.
    """

    card_download_starting = Signal(int, str)
    card_download_finished = Signal()
    card_download_progress = Signal(int)

    batch_process_starting = Signal(int, str)
    batch_process_progress = Signal(int)
    batch_process_finished = Signal()

    request_action = Signal(DocumentAction)
    missing_images_obtained = Signal()
    """
    Messages if the internal ImageDownloader instance performs a batch operation when it processes image requests for
    a deck list. It signals if such a long-running process starts or finishes.
    """
    batch_processing_state_changed = Signal(bool)

    network_error_occurred = Signal(str)  # Emitted when downloading failed due to network issues.

    def __init__(self, db_path: pathlib.Path = DEFAULT_DATABASE_LOCATION, parent: QObject = None):
        super(ImageDatabase, self).__init__(parent)
        self.read_disk_cache_content = functools.partial(read_disk_cache_content, db_path)
        self.db_path = db_path
        _migrate_database(db_path)
        # Caches loaded images in a map from scryfall_id to image. If a file is already loaded, use the loaded instance
        # instead of loading it from disk again. This prevents duplicated file loads in distinct QPixmap instances
        # to save memory.
        self.loaded_images: typing.Dict[ImageKey, QPixmap] = {}
        self.images_on_disk: typing.Set[ImageKey] = set()
        QThreadPool.globalInstance().start(InitOnDiskDataRunner(self.images_on_disk, db_path))
        self.download_worker = ImageDownloader(self)
        logger.info(f"Created {self.__class__.__name__} instance.")

    @property
    @functools.lru_cache(maxsize=1)
    def blank_image(self):
        """Returns a static, empty QPixmap in the size of a regular magic card."""
        pixmap = QPixmap(IMAGE_SIZE)
        pixmap.fill(QColor("white"))
        return pixmap

    def filter_already_downloaded(self, possible_matches: typing.List[Card]) -> typing.List[Card]:
        """
        Takes a list of cards and returns a new list containing all cards from the source list that have
        already downloaded images. The order of cards is preserved.
        """
        return [
            card for card in possible_matches
            if ImageKey(card.scryfall_id, card.is_front, card.highres_image) in self.images_on_disk
        ]

    def delete_disk_cache_entries(self, images: typing.Iterable[ImageKey]) -> PathSizeList:
        """
        Remove the given images from the hard disk cache.

        :returns: List with removed paths.
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
        QThreadPool.globalInstance().start(ObtainMissingImagesRunner(self, card_indices))

    @Slot(ActionReplaceCard)
    @Slot(ActionAddCard)
    def fill_document_action_image(self, action: SingleActions):
        logger.debug(f"About to obtain image for card in action")
        QThreadPool.globalInstance().start(SingleDownloadRunner(self, action))

    @Slot(ActionImportDeckList)
    def fill_batch_document_action_images(self, action: BatchActions):
        logger.debug(f"About to obtain images for cards in batch action")
        QThreadPool.globalInstance().start(BatchDownloadRunner(self, action))


class ImageDbRunnable(Runnable):

    def __init__(self, parent: ImageDatabase):
        super().__init__()
        self.parent = parent
        self.downloader: typing.Optional[ImageDownloader] = None

    def cancel(self):
        if self.downloader is None:
            return
        self.downloader.should_run = False
        try:
            self.downloader.currently_opened_file.close()
        except AttributeError:
            pass
        try:
            self.downloader.currently_opened_file_monitor.close()
        except AttributeError:
            pass


class ObtainMissingImagesRunner(ImageDbRunnable):

    def __init__(self, parent: ImageDatabase, indices: IndexList):
        super().__init__(parent)
        self.indices = indices

    def run(self):
        try:
            self.downloader = downloader = ImageDownloader(self.parent)
            downloader.connect_image_db_signals(self.parent)
            downloader.obtain_missing_images(self.indices)
        finally:
            self.release_instance()


class SingleDownloadRunner(ImageDbRunnable):
    def __init__(self, parent: ImageDatabase, action: SingleActions):
        super().__init__(parent)
        self.action = action

    def run(self):
        try:
            self.downloader = downloader = ImageDownloader(self.parent)
            downloader.connect_image_db_signals(self.parent)
            downloader.fill_document_action_image(self.action)
        finally:
            self.release_instance()


class BatchDownloadRunner(ImageDbRunnable):
    def __init__(self, parent: ImageDatabase, action: BatchActions):
        super().__init__(parent)
        self.action = action

    def run(self):
        try:
            self.downloader = downloader = ImageDownloader(self.parent)
            downloader.connect_image_db_signals(self.parent)
            downloader.fill_batch_document_action_images(self.action)
        finally:
            self.release_instance()


class ImageDownloader(mtg_proxy_printer.downloader_base.DownloaderBase):
    """
    This class performs image downloads from Scryfall. It is designed to be used as an asynchronous worker inside
    a QThread. To perform its tasks, it offers multiple Qt Signals that broadcast its state changes
    over thread-safe signal connections.

    It can be used synchronously, if precise, synchronous sequencing of small operations is required.
    """
    request_action = Signal(DocumentAction)
    missing_images_obtained = Signal()
    missing_image_obtained = Signal(QModelIndex)

    batch_processing_state_changed = Signal(bool)

    batch_process_starting = Signal(int, str)
    batch_process_progress = Signal(int)
    batch_process_finished = Signal()

    def __init__(self, image_db: ImageDatabase, parent: QObject = None):
        super(ImageDownloader, self).__init__(parent)
        self.image_database = image_db
        self.should_run = True
        self.batch_processing_state: bool = False
        self.last_error_message = ""
        # Reference to the currently opened file. Used here to be able to force close it in case the user wants to quit
        # or cancel the download process.
        self.currently_opened_file: typing.Optional[io.BytesIO] = None
        self.currently_opened_file_monitor: typing.Optional[mtg_proxy_printer.http_file.MeteredSeekableHTTPFile] = None
        logger.info(f"Created {self.__class__.__name__} instance.")
        
    def connect_image_db_signals(self, image_db: ImageDatabase):
        self.download_begins.connect(image_db.card_download_starting)
        self.download_finished.connect(image_db.card_download_finished)
        self.download_progress.connect(image_db.card_download_progress)

        self.batch_process_starting.connect(image_db.batch_process_starting)
        self.batch_process_progress.connect(image_db.batch_process_progress)
        self.batch_process_finished.connect(image_db.batch_process_finished)
        self.batch_processing_state_changed.connect(image_db.batch_processing_state_changed)

        self.request_action.connect(image_db.request_action)
        self.missing_images_obtained.connect(image_db.missing_images_obtained)
        self.network_error_occurred.connect(image_db.network_error_occurred)

    def fill_document_action_image(self, action: SingleActions):
        logger.info("Got DocumentAction, filling card")
        self.get_image_synchronous(action.card)
        logger.info("Obtained image, requesting apply()")
        self.request_action.emit(action)

    def fill_batch_document_action_images(self, action: BatchActions):
        cards = action.cards
        total_cards = len(cards)
        logger.info(f"Got batch DocumentAction, filling {total_cards} cards")
        self.update_batch_processing_state(True)
        self.batch_process_starting.emit(total_cards, "Importing deck list")
        for index, card in enumerate(cards, start=1):
            self.get_image_synchronous(card)
            self.batch_process_progress.emit(index)
        self.request_action.emit(action)
        self.batch_process_finished.emit()
        self.update_batch_processing_state(False)
        logger.info(f"Obtained images for {total_cards} cards.")

    def obtain_missing_images(self, card_indices: typing.List[QModelIndex]):
        total_cards = len(card_indices)
        logger.debug(f"Requesting {total_cards} missing images")
        blank = self.image_database.blank_image
        self.update_batch_processing_state(True)
        self.batch_process_starting.emit(total_cards, "Fetching missing images")
        for index, card_index in enumerate(card_indices, start=1):
            card = card_index.data(ItemDataRole.UserRole)
            self.get_image_synchronous(card)
            if card.image_file is not blank:
                self.missing_image_obtained.emit(card_index)
            self.batch_process_progress.emit(index)
        self.batch_process_finished.emit()
        self.update_batch_processing_state(False)
        logger.debug(f"Done fetching {total_cards} missing images.")
        self.missing_images_obtained.emit()

    def update_batch_processing_state(self, value: bool):
        self.batch_processing_state = value
        if not self.batch_processing_state and self.last_error_message:
            self.network_error_occurred.emit(self.last_error_message)
        self.batch_processing_state_changed.emit(value)

    def _handle_network_error_during_download(self, card: Card, reason_str: str):
        card.set_image_file(self.image_database.blank_image)
        logger.warning(
            f"Image download failed for card {card}, reason is \"{reason_str}\". Using blank replacement image.")
        # Only return the error message for storage, if the queue currently processes a batch job.
        # Otherwise, it’ll be re-raised if a batch job starts right after a singular request failed.
        if not self.batch_processing_state:
            self.network_error_occurred.emit(reason_str)
        return reason_str

    def get_image_synchronous(self, card: AnyCardType):
        try:
            if isinstance(card, CheckCard):
                self._fetch_and_set_image(card.front)
                self._fetch_and_set_image(card.back)
            else:
                self._fetch_and_set_image(card)
        except urllib.error.URLError as e:
            self.last_error_message = self._handle_network_error_during_download(
                card, str(e.reason))
        except socket.timeout as e:
            self.last_error_message = self._handle_network_error_during_download(
                card, f"Reading from socket failed: {e}")

    def _fetch_and_set_image(self, card: Card):
        key = ImageKey(card.scryfall_id, card.is_front, card.highres_image)
        image_path = self.image_database.db_path / key.format_relative_path()
        pixmap = self._load_from_memory(key) \
            or self._load_from_disk(key, image_path) \
            or self._download_from_scryfall(card, image_path) \
            or self.image_database.blank_image
        if pixmap is not self.image_database.blank_image:
            self._remove_outdated_low_resolution_image(card)
        card.set_image_file(pixmap)

    def _load_from_memory(self, key: ImageKey) -> OptionalPixmap:
        return self.image_database.loaded_images.get(key)

    def _load_from_disk(self, key: ImageKey, image_path: pathlib.Path) -> OptionalPixmap:
        if not self.should_run:
            return None
        logger.debug("Image not in memory, requesting from disk")
        if image_path.exists():
            pixmap = QPixmap(str(image_path))
            if pixmap.isNull():
                logger.warning(f'Failed to load image from "{image_path}", deleting corrupted file.')
                image_path.unlink()
            else:
                logger.debug("Image loaded from disk")
                self.image_database.loaded_images[key] = pixmap
                return pixmap
        return None

    def _remove_outdated_low_resolution_image(self, card):
        if not card.highres_image:
            return
        low_resolution_image_path = self.image_database.db_path / ImageKey(
            card.scryfall_id, card.is_front, False).format_relative_path()
        if low_resolution_image_path.exists():
            logger.info("Removing outdated low-resolution image")
            low_resolution_image_path.unlink()

    def _download_from_scryfall(self, card: Card, image_path: pathlib.Path) -> OptionalPixmap:
        if not self.should_run:
            return None
        logger.debug("Image not on disk, downloading from Scryfall")
        image_path.parent.mkdir(parents=True, exist_ok=True)
        download_uri = card.image_uri
        # Download to the root of the image database directory, not into the target directory. If something goes wrong,
        # the incomplete image can be deleted. Once loading the image succeeds, it can be moved to the final location.
        download_path = self.image_database.db_path / image_path.name
        self.currently_opened_file, self.currently_opened_file_monitor = self.read_from_url(
            download_uri, f"Downloading '{card.name}'")
        self.currently_opened_file_monitor.total_bytes_processed.connect(self.download_progress)
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
            self.download_finished.emit()
        return pixmap


def read_disk_cache_content(db_path: pathlib.Path) -> typing.List[CacheContent]:
    """
    Returns all entries currently in the given hard disk image cache.

    :returns: List with tuples (scryfall_id: str, is_front: bool, absolute_image_file_path: pathlib.Path)
    """
    result: typing.List[CacheContent] = []
    data: typing.Iterable[typing.Tuple[pathlib.Path, bool, bool]] = (
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
