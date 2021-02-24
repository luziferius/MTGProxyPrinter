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

import itertools
import pathlib
import shutil
import string
import typing

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
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
]

ImageKey = typing.Tuple[str, bool]


class ImageDatabase(QObject):

    card_download_starting = pyqtSignal(int)
    card_download_finished = pyqtSignal()
    card_download_progress = pyqtSignal(int)

    def __init__(self, *args, db_path: pathlib.Path = DEFAULT_DATABASE_LOCATION, **kwargs):
        super(ImageDatabase, self).__init__(*args, **kwargs)
        self.db_path = db_path
        _migrate_database(db_path)
        # Caches loaded images in a map from scryfall_id to image. If a file is already loaded, use the loaded instance
        # instead of loading it from disk again. This prevents duplicated file loads in distinct QPixmap instances
        # to save memory.  TODO: Maybe use the QPixmapCache class instead?
        self.loaded_images: typing.Dict[ImageKey, QPixmap] = {}

    def _connect_file_monitor(self, monitor: mtg_proxy_printer.metered_file.MeteredFile):
        monitor.io_begin.connect(self.card_download_starting)
        monitor.total_bytes_processed.connect(self.card_download_progress)
        monitor.io_end.connect(self.card_download_finished)

    @pyqtSlot(Card)
    def get_image(self, card: Card):
        try:
            pixmap = self.loaded_images[(card.scryfall_id, card.is_front)]
        except KeyError:
            cache_file_path = self._fetch_image_from_scryfall(card)
            pixmap = QPixmap(str(cache_file_path))
            self.loaded_images[(card.scryfall_id, card.is_front)] = pixmap
        card.image_file = pixmap

    def _fetch_image_from_scryfall(self, card):
        cache_file_path = pathlib.Path(
            self.db_path,
            "front" if card.is_front else "back",
            card.scryfall_id[:2],
            f"{card.scryfall_id}.png"
        )
        if not cache_file_path.parent.exists():
            cache_file_path.parent.mkdir(parents=True)
        if not cache_file_path.exists():
            self._download_image(card, cache_file_path)
        return cache_file_path

    def _download_image(self, card: Card, fs_path: pathlib.Path):
        download_uri = card.image_uri
        source, monitor = mtg_proxy_printer.card_info_downloader.read_from_url(download_uri, self)
        self._connect_file_monitor(monitor)
        with source, fs_path.open("wb") as file_in_cache:
            shutil.copyfileobj(source, file_in_cache)


def _migrate_database(db_path: pathlib.Path):
    if not (db_path/"version.txt").exists():
        for possible_dir in map("".join, itertools.product(string.hexdigits, string.hexdigits)):
            if (path := db_path/possible_dir).exists():
                shutil.rmtree(path)
        (db_path/"version.txt").write_text("2")
