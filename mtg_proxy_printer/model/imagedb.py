# Copyright (C) 2020, 2021 Thomas Hess <thomas.hess@udo.edu>

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
import io
import queue
import itertools
import pathlib
import shutil
import socket
import string
import typing
import urllib.error

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QSize, QPersistentModelIndex
from PyQt5.QtGui import QPixmap, QColor

import mtg_proxy_printer.meta_data
import mtg_proxy_printer.metered_file
from mtg_proxy_printer.model.carddb import Card
from mtg_proxy_printer.logger import get_logger
import mtg_proxy_printer.card_info_downloader
logger = get_logger(__name__)
del get_logger

DEFAULT_DATABASE_LOCATION = pathlib.Path(
    mtg_proxy_printer.meta_data.data_directories.user_cache_dir,
    "CardImages"
)
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
IMAGE_SIZE = QSize(745, 1040)

QueueContentTypes = typing.Union[
    typing.Tuple[Card, QPersistentModelIndex],
    typing.Tuple[Card, int],
    typing.Tuple[None, bool],
]


class ImageDatabase(QObject):
    """
    This class manages the on-disk PNG image cache. It can asynchronously fetch images from disk or from the Scryfall
    servers, as needed, provides an in-memory cache, and allows deletion of images on disk.
    """

    card_download_starting = pyqtSignal(int)
    card_download_finished = pyqtSignal()
    card_download_progress = pyqtSignal(int)
    # Emitted when image retrieval for a to-be-added card completes
    add_card = pyqtSignal(Card, int)
    # Emitted when an image retrieval for a to-be-replaced card completes
    replacement_obtained = pyqtSignal(Card, QPersistentModelIndex)
    """
    Messages if the internal ImageDownloader instance performs a batch operation when it processes image requests for
    a deck list. It signals if such a long-running process starts or finishes.
    """
    batch_processing_state_changed = pyqtSignal(bool)
    network_error_occurred = pyqtSignal(str)  # Emitted when downloading failed due to network issues.

    def __init__(self, db_path: pathlib.Path = DEFAULT_DATABASE_LOCATION, parent: QObject = None):
        super(ImageDatabase, self).__init__(parent)
        self.db_path = db_path
        _migrate_database(db_path)
        self._blank_image = QPixmap()
        # Caches loaded images in a map from scryfall_id to image. If a file is already loaded, use the loaded instance
        # instead of loading it from disk again. This prevents duplicated file loads in distinct QPixmap instances
        # to save memory.
        self.loaded_images: typing.Dict[ImageKey, QPixmap] = {}
        self.images_on_disk: typing.Set[ImageKey] = set()
        self.queue: queue.SimpleQueue[QueueContentTypes] = queue.SimpleQueue()
        self.download_thread = QThread()
        self.download_worker = ImageDownloader(self)
        self.download_worker.moveToThread(self.download_thread)
        self.download_worker.card_download_starting.connect(self.card_download_starting)
        self.download_worker.card_download_finished.connect(self.card_download_finished)
        self.download_worker.card_download_progress.connect(self.card_download_progress)
        self.download_worker.batch_processing_state_changed.connect(self.batch_processing_state_changed)
        self.download_worker.network_error_occurred.connect(self.network_error_occurred)
        self.download_worker.add_card.connect(self.add_card)
        self.download_worker.replacement_obtained.connect(self.replacement_obtained)
        self.download_thread.started.connect(self.download_worker.scan_disk_image_cache_then_process_queue)
        self.download_thread.start()
        logger.info(f"Created {self.__class__.__name__} instance.")

    @property
    def blank_image(self):
        if self._blank_image.isNull():
            self._blank_image = QPixmap(IMAGE_SIZE)
            self._blank_image.fill(QColor("white"))
        return self._blank_image

    def filter_already_downloaded(self, possible_matches: typing.List[Card]):
        return [card for card in possible_matches if ImageKey(card.scryfall_id, card.is_front, card.highres_image) in self.images_on_disk]

    @pyqtSlot(Card)
    @pyqtSlot(Card, int)
    def get_new_card_image_asynchronous(self, card: Card, count: int = 1):
        """
        Asynchronously fetches the image for the given card and stores it in the card instance.
        Emits add_card(card, count) signal when completed.
        """
        self.queue.put((card, count))

    def get_replacement_card_image_asynchronous(self, card: Card, index: QPersistentModelIndex):
        """
        Asynchronously fetches the image for the given card and stores it in the card instance.
        Emits replacement_obtained(card, index) signal when completed.
        """
        self.queue.put((card, index))

    def get_deck_asynchronous(self, deck: typing.Counter[Card]):
        self.queue.put((None, True))
        for card, count in deck.items():
            self.queue.put((card, count))
        self.queue.put((None, False))

    def read_disk_cache_content(self) -> typing.List[CacheContent]:
        """
        Returns all entries currently in the hard disk image cache.

        :returns: List with tuples (scryfall_id: str, is_front: bool, absolute_image_file_path: pathlib.Path)
        """
        result: typing.List[CacheContent] = []
        data: typing.Iterable[typing.Tuple[pathlib.Path, bool, bool]] = (
            (self.db_path/CacheContent.format_level_1_directory_name(is_front, is_high_resolution),
             is_front, is_high_resolution)
            for is_front, is_high_resolution in itertools.product([True, False], repeat=2)
        )
        for directory, is_front, is_high_resolution in data:
            result += (
                CacheContent(path.stem, is_front, is_high_resolution, path)
                for path in directory.glob("[0-9a-z][0-9a-z]/*.png"))
        return result

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
            else:
                logger.warning(f"Trying to remove image not in the cache. Not present: {image}")
        logger.info(f"Removed {len(removed)} images from the card cache")
        return removed


class ImageDownloader(QObject):
    """
    This class performs image downloads from Scryfall. It is designed to be used as an asynchronous worker inside
    a QThread. To perform it’s tasks, it offers multiple Qt Signals that broadcast it’s state changes
    over thread-safe signal connections.

    It can be used synchronously, if precise, synchronous sequencing of small operations is required.
    """
    card_download_starting = pyqtSignal(int)
    card_download_finished = pyqtSignal()
    card_download_progress = pyqtSignal(int)
    add_card = pyqtSignal(Card, int)
    replacement_obtained = pyqtSignal(Card, QPersistentModelIndex)
    network_error_occurred = pyqtSignal(str)  # Emitted when downloading failed due to network issues.
    """
    Messages if the instance performs a batch operation when it processes image requests for
    a deck list. It signals if such a long-running process starts or finishes.
    """
    batch_processing_state_changed = pyqtSignal(bool)

    def __init__(self, image_db: ImageDatabase, parent: QObject = None):
        super(ImageDownloader, self).__init__(parent)
        self.image_database = image_db
        self.queue = image_db.queue
        self.should_run = True
        self.batch_processing_state: bool = False
        self.currently_opened_file: typing.Optional[io.BytesIO] = None
        self.download_worker = self._create_download_worker()
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _create_download_worker(self) -> mtg_proxy_printer.card_info_downloader.CardInfoDownloadWorker:
        download_worker = mtg_proxy_printer.card_info_downloader.CardInfoDownloadWorker(None, parent=self)
        # Not connecting download_worker.download_finished with self.card_download_finished,
        # because that signal is emitted explicitly by this class.
        download_worker.download_progress.connect(self.card_download_progress)
        download_worker.download_begins.connect(self.card_download_starting)
        return download_worker

    def scan_disk_image_cache_then_process_queue(self):
        logger.info("Reading all image IDs of images stored on disk.")
        self.image_database.images_on_disk.update(
            image.as_key() for image in self.image_database.read_disk_cache_content()
        )
        self.process_queue()

    def process_queue(self):
        logger.info("Start processing download queue")
        last_error_msg = ""
        while self.should_run:
            card, value = self.queue.get()
            if card is None:
                if not value and last_error_msg:
                    self.network_error_occurred.emit(last_error_msg)
                    last_error_msg = ""
                self.batch_processing_state = value
                self.batch_processing_state_changed.emit(value)
                continue
            logger.debug("Received image request, processing it…")
            signal_to_emit = self.add_card if isinstance(value, int) else self.replacement_obtained
            try:
                self.get_image_synchronous(card)
            except urllib.error.URLError as e:
                last_error_msg = self._handle_network_error_during_download(card, str(e.reason))
            except socket.timeout as e:
                last_error_msg = self._handle_network_error_during_download(card, f"Reading from socket failed: {e}")
            finally:
                self.card_download_finished.emit()
                signal_to_emit.emit(card, value)

        logger.info("Processing download queue stopped")

    def _handle_network_error_during_download(self, card, reason_str):
        card.image_file = self.image_database.blank_image
        logger.warning(
            f"Image download failed for card {card}, reason is \"{reason_str}\". Using blank replacement image.")
        if not self.batch_processing_state:
            self.network_error_occurred.emit(reason_str)
        return reason_str

    def get_image_synchronous(self, card: Card):
        key = ImageKey(card.scryfall_id, card.is_front, card.highres_image)
        try:
            pixmap = self.image_database.loaded_images[key]
        except KeyError:
            logger.debug("Image not in memory, requesting from disk")
            pixmap = self._fetch_image(card)
            self.image_database.loaded_images[key] = pixmap
            self.image_database.images_on_disk.add(key)
            logger.debug("Image loaded")
        card.image_file = pixmap

    def _fetch_image(self, card: Card) -> QPixmap:
        key = ImageKey(card.scryfall_id, card.is_front, card.highres_image)
        cache_file_path = self.image_database.db_path / key.format_relative_path()
        cache_file_path.parent.mkdir(parents=True, exist_ok=True)
        pixmap = None
        if cache_file_path.exists():
            pixmap = QPixmap(str(cache_file_path))
            if pixmap.isNull():
                logger.warning(f'Failed to load image from "{cache_file_path}", deleting file.')
                cache_file_path.unlink()
        if not cache_file_path.exists():
            logger.debug("Image not in disk cache, downloading from Scryfall")
            self._download_image_from_scryfall(card, cache_file_path)
            pixmap = QPixmap(str(cache_file_path))
        return pixmap

    def _download_image_from_scryfall(self, card: Card, target_path: pathlib.Path):
        download_uri = card.image_uri
        source, _ = self.download_worker.read_from_url(download_uri)
        download_path = self.image_database.db_path / target_path.name
        # Download to the root of the cache first. Move to the target only after downloading finished.
        # This prevents inserting damaged files into the cache, if the download aborts due to an application crash,
        # getting terminated by the user, a mid-transfer network outage, a full disk or any other failure condition.
        try:
            with source, download_path.open("wb") as file_in_cache:
                self.currently_opened_file = source
                shutil.copyfileobj(source, file_in_cache)
            if self.should_run:
                shutil.move(download_path, target_path)
        finally:
            self.currently_opened_file = None
            if download_path.is_file():
                download_path.unlink()


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
