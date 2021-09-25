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

import gzip
import http.client
import typing
import urllib.request

from PyQt5.QtCore import QObject, pyqtSignal

import mtg_proxy_printer.metered_file

# Offer accepting gzip, as that is supported by the Scryfall server and reduces network data use by 80-90%
supported_encodings = ("gzip", "identity")


class DownloaderBase(QObject):
    """
    Base class for classes that are able to download data from the Internet.
    """

    other_error_occurred = pyqtSignal(str)  # Emitted when database population failed due to non-network issues.
    network_error_occurred = pyqtSignal(str)  # Emitted when downloading failed due to network issues.
    download_finished = pyqtSignal()  # Emitted when the input data is exhausted and processing finished
    download_begins = pyqtSignal(int)  # Emitted when the download starts. Data represents the expected total data
    download_progress = pyqtSignal(int)  # Emits the total number of processed data after processing each item

    def read_from_url(self, url: str):
        """
        Reads a given URL and returns a file-like object that can and should be used as a context manager.
        """
        response, encoding, size_bytes = self._open_url(url)
        metered_reader = self._wrap_in_metered_file(response, size_bytes)
        if encoding == "gzip":
            data = gzip.open(metered_reader, "rb")
        elif encoding in ("identity", None):  # Implicit "identity" if the Content-Encoding header is missing.
            data = metered_reader
        else:
            raise RuntimeError(f"Server returned unsupported encoding: {encoding}")
        return data, metered_reader

    @staticmethod
    def _open_url(url: str) -> typing.Tuple[typing.BinaryIO, str, int]:
        headers = {"Accept-Encoding": ", ".join(supported_encodings)}
        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request)  # type: http.client.HTTPResponse
        if (response_code := response.getcode()) >= 300:
            raise RuntimeError(f"Error from server! Error code: {response_code}")
        encoding = response.info().get("Content-Encoding")
        size_bytes = int(response.info().get("Content-Length", "0"))
        return response, encoding, size_bytes

    def _wrap_in_metered_file(self, raw_file, file_size):
        monitor = mtg_proxy_printer.metered_file.MeteredFile(raw_file, file_size, self)
        monitor.total_bytes_processed.connect(self.download_progress)
        monitor.io_begin.connect(self.download_begins)
        return monitor
