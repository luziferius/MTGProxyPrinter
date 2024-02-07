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


try:
    from functools import cache
except ImportError:
    from functools import lru_cache as cache
import http.client
import socket
import time
import typing
from typing import List, Optional, Dict
import urllib.error
import urllib.request

from PyQt5.QtCore import QObject, pyqtSignal as Signal
import delegateto

from mtg_proxy_printer.meta_data import USER_AGENT
from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger
__all__ = [
    "MeteredSeekableHTTPFile",
]


@delegateto.delegate(
    "file",
    "getheader", "info", "getcode",  # HTTPResponse methods
    "readable", "writable", "writelines", "truncate", "isatty", "flush", "fileno")  # IOBase methods
class MeteredSeekableHTTPFile(QObject):
    """
    Takes an HTTP(S) URL and provides a monitored, seekable file-like object.
    Seeking is implemented using the HTTP "range" header.

    If the using code seeks backwards and reads a portion of the underlying file multiple times, the total bytes
    read carried by the io_progressed signal may exceed the expected total file size carried by the io_begin signal and
    the content_length attribute.

    If the total file size can not be determined, because the remote server does not emit the proper HTTP header,
    the content length carried by the io_begin signal and the content_length attribute will be -1.

    If the remote server does not advertise support for the HTTP “range” header by replying to the initial request
    without adding the “Accept-Ranges” header field with value “bytes”, seeking will be disabled.
    In this case, linear reading with progress reports can still be performed.
    """
    INSTANCES: typing.List["MeteredSeekableHTTPFile"] = []

    io_begin = Signal(int, str)  # Emitted in __enter__, carries the total file size in bytes. -1, if unknown
    io_finished = Signal()  # Emitted in __exit__, when the file is closed
    total_bytes_processed = Signal(int)  # Emitted after each read chunk, carries the total number of bytes read
    getcode: typing.Callable[[], int]

    def __init__(self, url: str, headers: Dict[str, str] = None, parent: QObject = None, *,
                 ui_hint: str = "", retry_limit: int = 10):
        """
        :param url: The URL to fetch
        :param headers: A dict containing HTTP header key/value pairs.
        :param parent: parent QObject
        :param ui_hint: Carried verbatim by the io_begin signal. A connected progress meter UI can use this as display text.
        :param retry_limit: The downloader will re-establish the connection this many times before failing
        """
        super(MeteredSeekableHTTPFile, self).__init__(parent)
        self.INSTANCES.append(self)
        self.retry_limit = retry_limit
        self.ui_hint = ui_hint
        self.url = url
        self.headers = {} if headers is None else headers.copy()
        self.headers["User-Agent"] = USER_AGENT
        self.closed = False
        # _urlopen() internally accesses file, so this assignment has to stay here
        self.file: Optional[http.client.HTTPResponse] = None
        self.file = self._urlopen()
        self.content_length = self._read_content_length(self.file)
        self._pos = 0
        self.read_bytes = 0
        logger.info(f"Created {self.__class__.__name__} instance.")

    @staticmethod
    def _read_content_length(file) -> int:
        if file:
            return int(file.getheader("Content-Length", -1))
        else:
            return -1

    def content_encoding(self) -> Optional[str]:
        if self.file:
            return self.file.info().get("Content-Encoding")
        return None

    def __enter__(self):
        self.io_begin.emit(self.content_length, self.ui_hint)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.file.__exit__(exc_type, exc_val, exc_tb)
        finally:
            self.total_bytes_processed.emit(self.read_bytes)
            self.io_finished.emit()
            self.INSTANCES.remove(self)

    @cache
    def seekable(self) -> bool:
        return self.content_length > 0 and self.file.getheader("Accept-Ranges", "none").lower() == "bytes"

    def seek(self, offset, whence=0):
        if not self.seekable():
            raise OSError
        old_pos = self.tell()
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
            self.file = self._urlopen(self._pos)
        return self.tell()

    def read(self, count: int = None, /) -> bytes:
        if self.closed:
            logger.error(msg := "I/O operation on closed file.")
            raise ValueError(msg)
        last_error = None
        for retry in range(self.retry_limit or 1):
            try:
                buffer = self.file.read(count)
            except (ConnectionAbortedError, socket.timeout) as e:
                last_error = e
                self.file = self._urlopen(self.tell(), outer_retries=retry)
            except AttributeError as e:
                # underlying file deleted, probably because the app force-deleted it during shutdown.
                self.close()
                raise ValueError("I/o operation on deleted file.") from e
            else:
                buffer_length = len(buffer)
                self._store_and_report_read_progress(buffer_length)
                return buffer
        if last_error is not None:
            raise last_error

    def read1(self, count: int = None, /) -> bytes:
        buffer = self.file.read1(count)
        self._store_and_report_read_progress(len(buffer))
        return buffer

    def tell(self) -> int:
        return self._pos

    def readinto(self, buffer, /) -> int:
        if self.closed:
            logger.error(msg := "I/O operation on closed file.")
            raise ValueError(msg)
        last_error = None
        for retry in range(self.retry_limit or 1):
            try:
                buffer_length = self.file.readinto(buffer)
            except (ConnectionAbortedError, socket.timeout) as e:
                last_error = e
                self.file = self._urlopen(self.tell(), outer_retries=retry)
            else:
                self._store_and_report_read_progress(buffer_length)
                return buffer_length
        if last_error is not None:
            raise last_error

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

    def _urlopen(self, first_byte: int = 0, /, *, outer_retries: int = 0) -> http.client.HTTPResponse:
        """
        Opens the stored URL, returning the Response object, which can be used as a context manager.

        :param first_byte: Optional. If given, start downloading at this byte position by using the HTTP range header.
        :raises: Any error raised by urllib.request.urlopen(), if the retries exceeded the retry count
        """
        # Passing None or zero as first_byte causes a full-range read by not setting the range header
        if self.file is not None:
            self.file.close()
        headers = self.headers.copy()
        if first_byte > 0:
            headers["range"] = f"bytes={first_byte}-{self.content_length-1}"
        request = urllib.request.Request(self.url, headers=headers)
        last_error = None
        for retry in range(outer_retries, self.retry_limit or 1):
            try:
                response: http.client.HTTPResponse = urllib.request.urlopen(request)
            except urllib.error.URLError as e:
                # URLError is most likely caused by being offline,
                # so wait a bit to not immediately burn all remaining retries
                if self.closed:
                    # Do not sleep, if this instance was closed externally. Just break in that case.
                    break
                time.sleep(5)
                last_error = e
            else:
                return response
        if last_error is not None:
            logger.exception(last_error)
            raise last_error

    def close(self):
        self.closed = True
        try:
            self.file.close()
        except AttributeError:
            # When force-closing the connection, the file attribute may never be set to something. In that case,
            # simply ignore that self.file has no close()
            pass

    @classmethod
    def close_all_instances(cls):
        if not cls.INSTANCES:
            return
        logger.info(f"Force closing {len(cls.INSTANCES)} still open file downloads.")
        for instance in cls.INSTANCES:
            instance.retry_limit = 1
            instance.close()
        logger.debug("Closed all file downloads")
