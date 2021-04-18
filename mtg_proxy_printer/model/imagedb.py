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

import queue
import itertools
import pathlib
import shutil
import string
import typing

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from PyQt5.QtGui import QPixmap

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
]

ImageKey = typing.Tuple[str, bool]
CacheContent = typing.Tuple[str, bool, pathlib.Path]
PathSizeList = typing.List[typing.Tuple[pathlib.Path, int]]


class ImageDatabase(QObject):

    card_download_starting = pyqtSignal(int)
    card_download_finished = pyqtSignal()
    card_download_progress = pyqtSignal(int)
    add_card = pyqtSignal(Card, int)
    batch_processing_state_changed = pyqtSignal(bool)

    def __init__(self, *args, db_path: pathlib.Path = DEFAULT_DATABASE_LOCATION, **kwargs):
        super(ImageDatabase, self).__init__(*args, **kwargs)
        self.db_path = db_path
        _migrate_database(db_path)
        # Caches loaded images in a map from scryfall_id to image. If a file is already loaded, use the loaded instance
        # instead of loading it from disk again. This prevents duplicated file loads in distinct QPixmap instances
        # to save memory.
        self.loaded_images: typing.Dict[ImageKey, QPixmap] = {}
        self.images_on_disk: typing.Set[typing.Tuple[str, bool]] = set()
        self.queue: queue.SimpleQueue[
            typing.Union[typing.Tuple[Card, int], typing.Tuple[None, bool]]] = queue.SimpleQueue()
        self.download_thread = QThread()
        self.download_worker = ImageDownloader(self)
        self.download_worker.moveToThread(self.download_thread)
        self.download_worker.card_download_starting.connect(self.card_download_starting)
        self.download_worker.card_download_finished.connect(self.card_download_finished)
        self.download_worker.card_download_progress.connect(self.card_download_progress)
        self.download_worker.batch_processing_state_changed.connect(self.batch_processing_state_changed)
        self.download_worker.add_card.connect(self.add_card)
        self.download_thread.started.connect(self.download_worker.scan_disk_image_cache_then_process_queue)
        self.download_thread.start()
        logger.info(f"Created {self.__class__.__name__} instance.")

    @pyqtSlot(Card)
    @pyqtSlot(Card, int)
    def get_image_asynchronous(self, card: Card, count: int = 1):
        self.queue.put((card, count))

    def get_deck_asynchronous(self, deck: typing.Counter[Card]):
        self.queue.put((None, True))
        for card, count in deck.items():
            self.queue.put((card, count))
        self.queue.put((None, False))

    def get_disk_cache_content(self) -> typing.List[CacheContent]:
        """
        Returns all entries currently in the hard disk image cache.

        :returns: List with tuples (scryfall_id: str, is_front: bool, absolute_image_file_path: pathlib.Path)
        """
        result: typing.List[CacheContent] = []
        for directory, is_front in ((self.db_path/"front", True), (self.db_path/"back", False)):
            result += (
                (path.stem, is_front, path)
                for path in directory.glob("[0-9a-z][0-9a-z]/*.png"))
        return result

    def delete_disk_cache_entries(self, images: typing.Iterable[ImageKey]) -> PathSizeList:
        """
        Remove the given images from the hard disk cache.

        :returns: List with removed paths.
        """
        removed: PathSizeList = []
        for scryfall_id, is_front in images:
            path = self.db_path/("front" if is_front else "back")/scryfall_id[:2]/f"{scryfall_id}.png"
            if path.is_file():
                logger.debug(f"Removing image: {path}")
                size_bytes = path.stat().st_size
                path.unlink()
                removed.append((path, size_bytes))
                self.images_on_disk.remove((scryfall_id, is_front))
            else:
                logger.warning(f"Trying to remove image not in the cache. Not present: {scryfall_id=}, {is_front=}")
        logger.info(f"Removed {len(removed)} images from the card cache")
        return removed


class ImageDownloader(QObject):

    card_download_starting = pyqtSignal(int)
    card_download_finished = pyqtSignal()
    card_download_progress = pyqtSignal(int)
    add_card = pyqtSignal(Card, int)
    batch_processing_state_changed = pyqtSignal(bool)

    def __init__(self, image_db: ImageDatabase, parent: QObject = None):
        super(ImageDownloader, self).__init__(parent)
        self.image_database = image_db
        self.queue = image_db.queue
        self.should_run = True
        logger.info(f"Created {self.__class__.__name__} instance.")

    def scan_disk_image_cache_then_process_queue(self):
        logger.info("Reading all image IDs of images stored on disk.")
        self.image_database.images_on_disk.update(
            (scryfall_id, is_front)
            for scryfall_id, is_front, _ in self.image_database.get_disk_cache_content()
        )
        self.process_queue()

    def process_queue(self):
        logger.info("Start processing download queue")
        while self.should_run:
            card, count = self.queue.get()
            if card is None:
                self.batch_processing_state_changed.emit(count)
                continue
            logger.debug("Received image request, processing it…")
            self.get_image_synchronous(card, count)

    def _connect_file_monitor(self, monitor: mtg_proxy_printer.metered_file.MeteredFile):
        monitor.io_begin.connect(self.card_download_starting)
        monitor.total_bytes_processed.connect(self.card_download_progress)

    def get_image_synchronous(self, card: Card, count: int = 1):
        key = card.scryfall_id, card.is_front
        try:
            pixmap = self.image_database.loaded_images[key]
        except KeyError:
            logger.debug("Image not in memory, requesting from disk")
            pixmap = self._fetch_image(card)
            self.image_database.loaded_images[key] = pixmap
            self.image_database.images_on_disk.add(key)
            logger.debug("Image loaded")
        card.image_file = pixmap
        self.card_download_finished.emit()
        self.add_card.emit(card, count)

    def _fetch_image(self, card: Card) -> QPixmap:
        cache_file_path = pathlib.Path(
            self.image_database.db_path,
            "front" if card.is_front else "back",
            card.scryfall_id[:2],
            f"{card.scryfall_id}.png"
        )
        if not cache_file_path.parent.exists():
            cache_file_path.parent.mkdir(parents=True)
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
        source, monitor = mtg_proxy_printer.card_info_downloader.read_from_url(download_uri, self)
        self._connect_file_monitor(monitor)
        download_path = self.image_database.db_path / target_path.name
        # Download to the root of the cache first. Move to the target only after downloading finished.
        # This prevents inserting damaged files into the cache, if the download aborts due to an application crash,
        # getting terminated by the user, a mid-transfer network outage, a full disk or any other failure condition.
        try:
            with source, download_path.open("wb") as file_in_cache:
                shutil.copyfileobj(source, file_in_cache)
            shutil.move(download_path, target_path)
        finally:
            if download_path.is_file():
                download_path.unlink()


def _migrate_database(db_path: pathlib.Path):
    if not db_path.exists():
        db_path.mkdir(parents=True)
    if not (db_path/"version.txt").exists():
        for possible_dir in map("".join, itertools.product(string.hexdigits, string.hexdigits)):
            if (path := db_path/possible_dir).exists():
                shutil.rmtree(path)

        (db_path/"version.txt").write_text("2")
