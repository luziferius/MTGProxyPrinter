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

from collections.abc import Iterable
import errno
import functools
import itertools
import pathlib
import shutil
import string
from typing import Callable

from PySide6.QtCore import QObject, Signal, Slot, QModelIndex, Qt
from PySide6.QtGui import QPixmap, QColorConstants

from mtg_proxy_printer import BlockingQueuedConnection
from .imagedb_files import ImageKey, CacheContent
import mtg_proxy_printer.app_dirs
import mtg_proxy_printer.http_file
from mtg_proxy_printer.units_and_sizes import CardSizes, CardSize
from .card import Card
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


__all__ = [
    "ImageDatabase",
]

DEFAULT_DATABASE_LOCATION = mtg_proxy_printer.app_dirs.data_directories.user_cache_path / "CardImages"
PathSizeList = list[tuple[pathlib.Path, int]]
ImageKeySet = set[ImageKey]
IndexList = list[QModelIndex]
OptionalPixmap = QPixmap | None

class InitOnDiskDataTask:
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

    missing_image_obtained = Signal(QModelIndex)

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

    @Slot(ImageKey, QPixmap)
    def on_image_obtained(self, key: ImageKey, pixmap: QPixmap):
        self.loaded_images[key] = pixmap
        self.images_on_disk.add(key)


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
