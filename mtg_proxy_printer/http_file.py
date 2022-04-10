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

import functools
import http.client
from io import BufferedIOBase
from typing import List, Optional, BinaryIO, Union, Dict
import urllib.error
import urllib.request

from PyQt5.QtCore import QObject, pyqtSignal
import delegateto

from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger
__all__ = [
    "MeteredSeekableHTTPFile",
]
WrappedIoType = Union[BufferedIOBase, BinaryIO]


@delegateto.delegate(
    "file",
    "getheader", "info", "getcode",  # HTTPResponse methods
    "readable", "writable", "writelines", "truncate", "isatty", "flush", "fileno", "close")  # IOBase methods
class MeteredSeekableHTTPFile(QObject):
    """
    Takes an HTTP(S) URL and provides a monitored, seekable file-like object.
    Seeking is implemented using the HTTP "range" header.

    If the using code seeks backwards and reads a portion of the underlying file multiple times, the total bytes
    read carried by the io_progressed signal may exceed the expected total file size carried by the io_begin signal and
    the content_length attribute.

    If the total file size can not be determined, because the remote server doesn’t emit the proper HTTP header,
    the content length carried by the io_begin signal and the content_length attribute will be -1.

    If the remote server does not advertise support for the HTTP “range” header by replying to the initial request
    without adding the “Accept-Ranges” header field with value “bytes”, seeking will be disabled.
    In this case, linear reading with progress reports can still be performed.
    """

    io_begin = pyqtSignal(int)  # Emitted in __enter__, carries the total file size in bytes. -1, if unknown
    io_finished = pyqtSignal()  # Emitted in __exit__, when the file is closed
    total_bytes_processed = pyqtSignal(int)  # Emitted after each read chunk, carries the total number of bytes read

    def __init__(self, url: str, headers: Dict[str, str] = None, parent: QObject = None):
        super(MeteredSeekableHTTPFile, self).__init__(parent)
        self.url = url
        self.headers = {} if headers is None else headers
        self.file = None
        self.file = self._urlopen()
        self.content_length = self._read_content_length(self.file)
        self._pos = 0
        self.read_bytes = 0

    def _read_content_length(self, file) -> int:
        if self.file:
            return int(file.getheader("Content-Length", -1))
        else:
            return -1

    def content_encoding(self) -> Optional[str]:
        if self.file:
            return self.file.info().get("Content-Encoding")
        return None

    def __enter__(self):
        self.io_begin.emit(self.content_length)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            result = self.file.__exit__(exc_type, exc_val, exc_tb)
        finally:
            self.total_bytes_processed.emit(self.read_bytes)
            self.io_finished.emit()
        return result

    @functools.lru_cache()
    def seekable(self) -> bool:
        return self.content_length > 0 and self.file.getheader("Accept-Ranges", "none").lower() == "bytes"

    def seek(self, offset, whence=0):
        if not self.seekable():
            raise OSError
        old_pos = self._pos
        if whence == 0:
            self._pos = 0
        elif whence == 1:
            pass
        elif whence == 2:
            self._pos = self.content_length - 1
        self._pos += offset
        if self._pos != old_pos:
            # Ignore the seek() call, if seeking distance is zero.
            # This is an optimization that prevents unnecessarily starting new server connections.
            self._urlopen(self._pos)
        return self._pos

    def read(self, count: int = None, /) -> bytes:
        buffer = self.file.read(count)
        self._store_and_report_read_progress(len(buffer))
        return buffer

    def read1(self, count: int = None, /) -> bytes:
        buffer = self.file.read1(count)
        self._store_and_report_read_progress(len(buffer))
        return buffer

    def tell(self) -> int:
        return self._pos

    def readinto(self, buffer, /) -> int:
        block_length = self.file.readinto(buffer)
        self._store_and_report_read_progress(block_length)
        return block_length

    def readinto1(self, buffer, /) -> int:
        block_length = self.file.readinto1(buffer)
        self._store_and_report_read_progress(block_length)
        return block_length

    def readline(self, __size: Optional[int] = None) -> bytes:
        line = self.file.readline(__size)
        self._store_and_report_read_progress(len(line))
        return line

    def readlines(self, __hint: int = None) -> List[bytes]:
        lines = self.file.readlines(__hint)
        total_bytes = sum(map(len, lines))
        self._store_and_report_read_progress(total_bytes)
        return lines

    def _store_and_report_read_progress(self, block_length: int, /):
        self._pos += block_length
        self.read_bytes += block_length
        self.total_bytes_processed.emit(self.read_bytes)

    def _urlopen(self, first_byte: int = 0, /) -> http.client.HTTPResponse:
        """
        Opens the stored URL, returning the Response object, which can be used as a context manager.

        :param first_byte: Optional. If given, start downloading at this byte position by using a HTTP range header.
        """
        # Passing None or zero as first_byte causes a full-range read by not setting the range header
        if self.file is not None and not self.file.isclosed():
            self.file.close()
        headers = self.headers.copy()
        if first_byte > 0:
            headers["range"] = f"bytes={first_byte}-{self.content_length-1}"
        request = urllib.request.Request(self.url, headers=headers)
        return urllib.request.urlopen(request)
