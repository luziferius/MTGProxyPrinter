# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>

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


from typing import Iterable, List, Optional, BinaryIO, Union
from io import BufferedIOBase

from PyQt5.QtCore import QObject, pyqtSignal as Signal
from delegateto import delegate

from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger
__all__ = [
    "MeteredFile",
]

WrappedIoType = Union[BufferedIOBase, BinaryIO]


@delegate(
    "file",
    # IOBase and BufferedIOBase methods
    "seekable", "readable", "writable", "close", "fileno", "flush", "isatty", "tell", "truncate", "detach",  # noqa
)
class MeteredFile(QObject):
    """
    Takes a file-like object and monitors read and write progress.
    """

    io_begin = Signal(int)
    total_bytes_processed = Signal(int)
    io_end = Signal()

    def __init__(self, file: WrappedIoType, expected_size_bytes: int = 0, parent: QObject = None):
        logger.debug(f"Creating {self.__class__.__name__} instance.")
        super(MeteredFile, self).__init__(parent)
        self.file = file
        self._total_bytes_processed = 0
        self.expected_size_bytes = expected_size_bytes
        logger.debug(f"Created {self.__class__.__name__} instance.")

    def __enter__(self):
        self.io_begin.emit(self.expected_size_bytes)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> Optional[bool]:
        try:
            result = self.file.__exit__(exc_type, exc_val, exc_tb)
        finally:
            self.io_end.emit()
        return result

    def _processed(self, byte_count: int):
        self._total_bytes_processed += byte_count
        self.total_bytes_processed.emit(self._total_bytes_processed)

    def seek(self, __offset: int, __whence: int = None):
        self.file.seek(__offset, __whence)
        self._total_bytes_processed = __offset
        self.total_bytes_processed.emit(self._total_bytes_processed)

    def read(self, __size: Optional[int] = None) -> bytes:
        buffer = self.file.read(__size)
        self._processed(len(buffer))
        return buffer

    def read1(self, __size: int = None) -> bytes:
        buffer = self.file.read1(__size)
        self._processed(len(buffer))
        return buffer

    def readinto(self, __buffer) -> int:
        bytes_read = self.file.readinto(__buffer)
        self._processed(bytes_read)
        return bytes_read

    def readinto1(self, __buffer) -> int:
        bytes_read = self.file.readinto1(__buffer)
        self._processed(bytes_read)
        return bytes_read

    def readline(self, __size: Optional[int] = None) -> bytes:
        line = self.file.readline(__size)
        self._processed(len(line))
        return line

    def readlines(self, __hint: int = None) -> List[bytes]:
        lines = self.file.readlines(__hint)
        total_bytes = sum(map(len, lines))
        self._processed(total_bytes)
        return lines

    def write(self, __buffer) -> int:
        bytes_written = self.file.write(__buffer)
        self._processed(bytes_written)
        return bytes_written

    def writelines(self, __lines: Iterable[bytes]) -> None:
        def _monitor(__lines: Iterable[bytes]):
            for line in __lines:
                yield line
                self._processed(len(line))
        self.file.writelines(_monitor(__lines))
