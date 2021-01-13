# Copyright (C) 2021 Thomas Hess <thomas.hess@udo.edu>

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


from typing import Iterable, List, Optional, TYPE_CHECKING

from io import BufferedIOBase
from PyQt5.QtCore import QObject, pyqtSignal

from delegateto import delegate

if TYPE_CHECKING:
    from _typeshed import WriteableBuffer, ReadableBuffer

__all__ = [
    "MeteredFile",
]


@delegate(
    "file",
    # IOBase and BufferedIOBase methods
    "seekable", "seek", "readable", "writable", "close", "fileno", "flush", "isatty", "tell", "truncate", "detach",
    # Context manager
    "__enter__", "__exit__",
)
class MeteredFile(QObject):
    """Takes a file-like object and monitors read and write progress."""
    bytes_read = pyqtSignal(int)
    bytes_written = pyqtSignal(int)

    def __init__(self, file: BufferedIOBase, expected_size_bytes: int = None, parent: QObject = None):
        super(MeteredFile, self).__init__(parent)
        self.file = file
        self.expected_size_bytes = expected_size_bytes

    def read(self, __size: Optional[int] = None) -> bytes:
        buffer = self.file.read(__size)
        self.bytes_read.emit(len(buffer))
        return buffer

    def read1(self, __size: int = None) -> bytes:
        buffer = self.file.read1(__size)
        self.bytes_read.emit(len(buffer))
        return buffer

    def readinto(self, __buffer) -> int:
        bytes_read = self.file.readinto(__buffer)
        self.bytes_read.emit(bytes_read)
        return bytes_read

    def readinto1(self, __buffer) -> int:
        bytes_read = self.file.readinto1(__buffer)
        self.bytes_read.emit(bytes_read)
        return bytes_read

    def readline(self, __size: Optional[int] = ...) -> bytes:
        line = self.file.readline(__size)
        self.bytes_read.emit((len(line)))
        return line

    def readlines(self, __hint: int = None) -> List[bytes]:
        lines = self.file.readlines(__hint)
        self.bytes_read.emit(sum(map(len, lines)))
        return lines

    def write(self, __buffer) -> int:
        bytes_written = self.file.write(__buffer)
        self.bytes_written.emit(bytes_written)
        return bytes_written

    def writelines(self, __lines: Iterable[bytes]) -> None:
        def _monitor(__lines: Iterable[ReadableBuffer]):
            for line in __lines:
                yield line
                self.bytes_written.emit(len(line))
        self.file.writelines(_monitor(__lines))


