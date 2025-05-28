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


import dataclasses
import pathlib

from PyQt5.QtCore import Qt
import mtg_proxy_printer.app_dirs
import mtg_proxy_printer.http_file
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

ItemDataRole = Qt.ItemDataRole
DEFAULT_DATABASE_LOCATION = mtg_proxy_printer.app_dirs.data_directories.user_cache_path / "CardImages"
__all__ = [
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
