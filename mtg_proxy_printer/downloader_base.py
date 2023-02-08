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

import gzip

from PyQt5.QtCore import QObject, pyqtSignal as Signal

import mtg_proxy_printer.http_file
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

# Offer accepting gzip, as that is supported by the Scryfall server and reduces network data use by 80-90%
supported_encodings = ("gzip", "identity")


class DownloaderBase(QObject):
    """
    Base class for classes that are able to download data from the Internet.
    """

    other_error_occurred = Signal(str)  # Emitted when database population failed due to non-network issues.
    network_error_occurred = Signal(str)  # Emitted when downloading failed due to network issues.
    download_finished = Signal()  # Emitted when the input data is exhausted and processing finished
    download_begins = Signal(int, str)  # Emitted when the download starts. Data represents the expected total data
    download_progress = Signal(int)  # Emits the total number of processed data after processing each item

    def read_from_url(self, url: str, ui_hint: str = ""):
        """
        Reads a given URL and returns a file-like object that can and should be used as a context manager.
        GZip-Streams are implicitly decompressed.
        :param url: URL to fetch
        :param ui_hint: Display text shown in the UI next to the progress bar. If empty, no progress bar is shown at all
        """
        monitor = self._open_url(url, ui_hint)
        encoding = monitor.content_encoding()
        if encoding == "gzip":
            data = gzip.open(monitor, "rb")
        elif encoding in ("identity", None):  # Implicit "identity" if the Content-Encoding header is missing.
            data = monitor
        else:
            raise RuntimeError(f"Server returned unsupported encoding: {encoding}")
        return data, monitor

    def _open_url(self, url: str, ui_hint: str) -> mtg_proxy_printer.http_file.MeteredSeekableHTTPFile:
        headers = {"Accept-Encoding": ", ".join(supported_encodings)}
        response = mtg_proxy_printer.http_file.MeteredSeekableHTTPFile(url, headers, self, ui_hint=ui_hint)
        if (response_code := response.getcode()) >= 300:
            raise RuntimeError(f"Error from server! Error code: {response_code}")
        if ui_hint:  # Without a display text for the UI, there is no meaningful progress report. So skip if not given
            response.total_bytes_processed.connect(self.download_progress)
            response.io_begin.connect(self.download_begins)
        return response
