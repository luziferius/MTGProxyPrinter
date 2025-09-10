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


import socket
import time
import typing
import urllib.error
import urllib.request
from unittest.mock import patch, MagicMock, DEFAULT
import http.client


from hamcrest import *
import pytest
from pytestqt.qtbot import QtBot

import mtg_proxy_printer.http_file
MeteredSeekableHTTPFile = mtg_proxy_printer.http_file.MeteredSeekableHTTPFile


@pytest.fixture
def http_file():
    with patch("mtg_proxy_printer.http_file.MeteredSeekableHTTPFile._urlopen",
               return_value=MagicMock(spec=http.client.HTTPResponse)) as mock:
        file = mock()
        file.getheader.return_value = -1
        file.isclosed.return_value = False
        yield mtg_proxy_printer.http_file.MeteredSeekableHTTPFile("")
    file.__dict__.clear()


def set_file_size(http_file: MeteredSeekableHTTPFile, size: int):
    file_mock = http_file._urlopen()
    file_mock.getheader.return_value = size
    http_file.content_length = size


@pytest.mark.parametrize("expected_size", [123, 1])
def test_read_content_length_with_file(http_file: MeteredSeekableHTTPFile, expected_size: int):
    set_file_size(http_file, expected_size)
    assert_that(http_file._read_content_length(http_file.file), is_(expected_size))
    assert_that(http_file.content_length, is_(equal_to(expected_size)))


def test_read_content_length_without_file(http_file: MeteredSeekableHTTPFile):
    http_file.file = None
    expected_size = -1
    assert_that(http_file._read_content_length(http_file.file), is_(expected_size))


@pytest.mark.parametrize("expected_size", [123, 1])
@pytest.mark.parametrize("ui_hint", ["", "Test hint"])
def test___enter___emits_io_begin_signal(
        http_file: MeteredSeekableHTTPFile, qtbot: QtBot, ui_hint: str, expected_size: int):
    set_file_size(http_file, expected_size)
    http_file.ui_hint = ui_hint
    if ui_hint:
        with qtbot.wait_signal(
                (http_file.io_begin, "io_begin"),
                check_params_cb=lambda size, hint: size == expected_size and hint == ui_hint):
            http_file.__enter__()
    else:
        with qtbot.assert_not_emitted(http_file.io_begin):
            http_file.__enter__()


@pytest.mark.parametrize("expected_size", [123, 1])
def test___exit___emits_signals_on_regular_closure(
        http_file: MeteredSeekableHTTPFile, qtbot: QtBot, expected_size: int):
    set_file_size(http_file, expected_size)
    http_file.read_bytes = expected_size
    with qtbot.wait_signals(
            [http_file.total_bytes_processed, http_file.io_finished],
            check_params_cbs=[lambda size: size == expected_size, lambda: True]):
        http_file.__exit__(None, None, None)


@pytest.mark.parametrize("error_on_exit", [AssertionError, IOError, urllib.error.URLError])
@pytest.mark.parametrize("expected_size", [123, 1])
def test___exit___emits_signals_on_exception_during_closure(
        http_file: MeteredSeekableHTTPFile, qtbot: QtBot, expected_size: int, error_on_exit: type[Exception]):
    set_file_size(http_file, expected_size)
    http_file.file.__exit__.side_effect = error_on_exit("")
    http_file.read_bytes = expected_size
    with qtbot.wait_signals(
            [http_file.total_bytes_processed, http_file.io_finished],
            check_params_cbs=[lambda size: size == expected_size, lambda: True]):
        assert_that(calling(http_file.__exit__).with_args(None, None, None), raises(error_on_exit))


@pytest.mark.parametrize("pos", [0, 10, 100])
def test_tell(http_file: MeteredSeekableHTTPFile, pos: int):
    http_file._pos = pos
    assert_that(http_file.tell(), is_(equal_to(pos)))


@pytest.mark.parametrize("offset", [-1, 0, 1])
@pytest.mark.parametrize("whence", [0, 1, 2])
def test_seek_raises_error_if_connection_is_not_seekable(http_file: MeteredSeekableHTTPFile, offset: int, whence: int):
    with patch.object(http_file, "seekable", return_value=False):
        assert_that(calling(http_file.seek).with_args(offset, whence), raises(OSError))


@pytest.mark.parametrize("offset, whence, start_pos, expected", [
    (0, 0, 10, 0),
    (6, 0, 10, 6),
    (10, 0, 10, 10),

    (0, 1, 10, 10),
    (1, 1, 10, 11),
    (-1, 1, 10, 9),

    (0, 2, 10, 100),
    (-1, 2, 10, 99),
    (0, 2, 99, 100),
])
def test_seek_moves_to_expected_position(
        http_file: MeteredSeekableHTTPFile,  offset: int, whence: int, start_pos: int, expected: int):
    http_file.content_length = 100
    http_file._pos = start_pos
    with patch.object(http_file, "seekable", return_value=True):
        http_file.seek(offset, whence)
    assert_that(http_file.tell(), is_(equal_to(expected)))
    # The setup code contributes 2 calls to the _urlopen() call_count
    expected_urlopen_call_count = 2 + (start_pos != expected)  # Only re-open connection, if the seek distance is != 0
    assert_that(
        http_file._urlopen.call_count,
        is_(equal_to(expected_urlopen_call_count))
    )


@pytest.mark.parametrize("size", [1, 10])
def test_readinto1(http_file: MeteredSeekableHTTPFile, size: int):
    buffer = bytearray(size)
    http_file.file.readinto1.return_value = size
    with patch.object(http_file, "_store_and_report_read_progress") as store_progress_mock:
        assert_that(http_file.readinto1(buffer), is_(equal_to(size)))
    http_file.file.readinto1.assert_called_with(buffer)
    store_progress_mock.assert_called_with(size)


@pytest.mark.parametrize("size", [1, 10])
def test_read1(http_file: MeteredSeekableHTTPFile, size: int):
    buffer = bytearray(size)
    http_file.file.read1.return_value = buffer
    with patch.object(http_file, "_store_and_report_read_progress") as store_progress_mock:
        assert_that(http_file.read1(size), is_(same_instance(buffer)))
    http_file.file.read1.assert_called_with(size)
    store_progress_mock.assert_called_with(size)


@pytest.mark.parametrize("size", [1, 10])
def test_readline(http_file: MeteredSeekableHTTPFile, size: int):
    buffer = bytearray(size)
    http_file.file.readline.return_value = buffer
    with patch.object(http_file, "_store_and_report_read_progress") as store_progress_mock:
        assert_that(http_file.readline(size), is_(same_instance(buffer)))
    http_file.file.readline.assert_called_with(size)
    store_progress_mock.assert_called_with(size)


@pytest.mark.parametrize("hint", [2, 5])
@pytest.mark.parametrize("size", [1, 10])
def test_readlines(http_file: MeteredSeekableHTTPFile, size: int, hint: int):
    line_length = 7
    buffers = [bytearray(line_length)]*size
    http_file.file.readlines.return_value = buffers
    with patch.object(http_file, "_store_and_report_read_progress") as store_progress_mock:
        assert_that(http_file.readlines(hint), contains_exactly(*buffers))
    http_file.file.readlines.assert_called_with(hint)
    store_progress_mock.assert_called_with(line_length*size)


@pytest.mark.parametrize("pos", [0, 10])
@pytest.mark.parametrize("total_read_bytes", [1, 11])
@pytest.mark.parametrize("progress", [0, 5])
def test__store_and_report_read_progress(
        http_file: MeteredSeekableHTTPFile, qtbot: QtBot, pos: int, total_read_bytes: int, progress: int):
    http_file._pos = pos
    http_file.read_bytes = total_read_bytes
    with qtbot.wait_signal(
            http_file.total_bytes_processed, check_params_cb=lambda total: total == total_read_bytes + progress):
        http_file._store_and_report_read_progress(progress)
    assert_that(http_file.tell(), is_(equal_to(pos + progress)))
    assert_that(http_file.read_bytes, is_(total_read_bytes + progress))


def test_close(http_file: MeteredSeekableHTTPFile):
    assert_that(http_file.closed, is_(False))
    http_file.close()
    assert_that(http_file.closed, is_(True))
    http_file.file.close.assert_called_once()


def test_close_twice(http_file: MeteredSeekableHTTPFile):
    assert_that(http_file.closed, is_(False))
    http_file.close()
    http_file.close()
    assert_that(http_file.closed, is_(True))
    assert_that(http_file.file.close.call_count, is_(2))


@pytest.mark.parametrize("method", [
    "getheader", "info", "getcode", "readable", "writable",
    "writelines", "truncate", "isatty", "flush", "fileno",
])
def test_delegates(http_file: MeteredSeekableHTTPFile, method):
    file_method = getattr(http_file.file, method)
    if method in {"getheader"}:  # Used by setup code, reset call_count value.
        file_method.call_count = 0
    getattr(http_file, method)()
    file_method.assert_called_once()
    assert_that(
        http_file,
        has_property(
            method, same_instance(file_method)
        )
    )


def test_content_encoding_without_file(http_file: MeteredSeekableHTTPFile):
    http_file.file = None
    assert_that(http_file.content_encoding(), is_(none()))


def test_content_encoding_with_file(http_file: MeteredSeekableHTTPFile):
    expected = http_file.file.info().get("Content-Encoding")
    assert_that(http_file.content_encoding(), is_(equal_to(expected)))


@pytest.mark.parametrize("content_length, ranges_header_value, expected", [
    (0, "none", False),
    (0, "foo", False),
    (0, "bytes", False),
    (10, "none", False),
    (10, "foo", False),
    (10, "bytes", True),
    (10, "BYTES", True),
])
def test_seekable(http_file: MeteredSeekableHTTPFile, content_length: int, ranges_header_value: str, expected: bool):
    http_file.file.getheader.call_count = 0
    http_file.content_length = content_length
    http_file.file.getheader.return_value = ranges_header_value
    # Run test twice, verify the value is cached
    assert_that(http_file.seekable(), is_(expected))
    assert_that(http_file.seekable(), is_(expected))
    assert_that(http_file.file.getheader.call_count, is_(less_than_or_equal_to(1)))


@pytest.mark.parametrize("exception_class", [None, socket.timeout, ConnectionAbortedError])
@pytest.mark.parametrize("size", [1, 10])
def test_read_raises_value_error_if_closed(
        http_file: MeteredSeekableHTTPFile, size: int, exception_class):
    http_file.close()
    if exception_class is not None:
        http_file.file.read.side_effect = exception_class("")
    assert_that(calling(http_file.read).with_args(size), raises(ValueError))


@pytest.mark.parametrize("retry", [10, 11])
@pytest.mark.parametrize("exception_class", [socket.timeout, ConnectionAbortedError])
@pytest.mark.parametrize("size", [1, 10])
def test_read_re_raises_error_on_exceeded_retries(
        http_file: MeteredSeekableHTTPFile, size: int, exception_class, retry: int):
    http_file.file.read.side_effect = [exception_class("")]*retry
    assert_that(calling(http_file.read).with_args(size), raises(exception_class))


@pytest.mark.parametrize("size", [1, 10])
def test_read_returns_bytes_from_internal_file(http_file: MeteredSeekableHTTPFile, size: int):
    buffer = bytearray(size)
    http_file.file.read.return_value = buffer
    assert_that(http_file.read(size), is_(equal_to(buffer)))


def test_read_returns_incomplete_internal_reads(http_file: MeteredSeekableHTTPFile):
    available = bytes(10)
    requested = len(available) + 5
    http_file.file.read.return_value = available
    assert_that(http_file.read(requested), is_(equal_to(available)))


@pytest.mark.parametrize("exception_class", [socket.timeout, ConnectionAbortedError])
@pytest.mark.parametrize("retries", [10, 11])
def test_read_aborts_after_exhausting_retries(
        http_file: MeteredSeekableHTTPFile, retries: int, exception_class):
    http_file.file.read.side_effect = [exception_class("")] * retries
    assert_that(calling(http_file.read), raises(exception_class))


@pytest.mark.parametrize("exception_class", [socket.timeout, ConnectionAbortedError])
@pytest.mark.parametrize("retries", range(10))
def test_read_returns_data_after_multiple_retries(
        http_file: MeteredSeekableHTTPFile, retries: int, exception_class):
    read_request_bytes = 10
    available = bytes(read_request_bytes)
    http_file.file.read.side_effect = [exception_class("")] + [available]
    with patch.object(http_file, "_store_and_report_read_progress") as store_progress_mock:
        assert_that(http_file.read(read_request_bytes), is_(equal_to(available)))
    store_progress_mock.assert_called_once_with(read_request_bytes)


@pytest.mark.parametrize("exception_class", [None, socket.timeout, ConnectionAbortedError])
@pytest.mark.parametrize("size", [1, 10])
def test_readinto_raises_value_error_if_closed(
        http_file: MeteredSeekableHTTPFile, size: int, exception_class):
    http_file.close()
    buffer = bytearray(size)
    if exception_class is not None:
        http_file.file.readinto.side_effect = exception_class("")
    assert_that(calling(http_file.readinto).with_args(buffer), raises(ValueError))


@pytest.mark.parametrize("exception_class", [socket.timeout, ConnectionAbortedError])
@pytest.mark.parametrize("retries", [10, 11])
def test_readinto_aborts_after_exhausting_retries(
        http_file: MeteredSeekableHTTPFile, retries: int, exception_class):
    http_file.file.readinto.side_effect = [exception_class("")] * retries
    assert_that(calling(http_file.readinto).with_args(bytearray(10)), raises(exception_class))


@pytest.mark.parametrize("exception_class", [socket.timeout, ConnectionAbortedError])
@pytest.mark.parametrize("retries", range(10))
def test_readinto_returns_data_after_multiple_retries(
        http_file: MeteredSeekableHTTPFile, retries: int, exception_class):
    available = 10
    http_file.file.readinto.side_effect = [exception_class("")] + [available]
    with patch.object(http_file, "_store_and_report_read_progress") as store_progress_mock:
        assert_that(http_file.readinto(bytearray(available)), is_(equal_to(available)))
    store_progress_mock.assert_called_once_with(available)


@pytest.mark.parametrize("retries", range(10))
@patch.multiple("mtg_proxy_printer.http_file.urllib.request", autospec=True, Request=DEFAULT, urlopen=DEFAULT)
@patch("mtg_proxy_printer.http_file.time.sleep", MagicMock(spec=time.sleep))
def test__urlopen_in_init_works_with_multiple_retries(
        retries: int, urlopen: MagicMock = None, Request: MagicMock = None):
    urlopen.side_effect = [urllib.error.URLError("Test error")]*retries + [MagicMock(spec=http.client.HTTPResponse)]
    MeteredSeekableHTTPFile("")
    Request.assert_called()


@pytest.mark.parametrize("retries", range(10, 12))
@patch.multiple("mtg_proxy_printer.http_file.urllib.request", autospec=True, Request=DEFAULT, urlopen=DEFAULT)
@patch("mtg_proxy_printer.http_file.time.sleep", MagicMock(spec=time.sleep))
def test__urlopen_in_init_raises_exception_after_exceeded_retries(
        retries: int, urlopen: MagicMock = None, Request: MagicMock = None):
    urlopen.side_effect = [urllib.error.URLError("Test error")]*retries + [MagicMock(spec=http.client.HTTPResponse)]
    assert_that(calling(MeteredSeekableHTTPFile).with_args(""), raises(urllib.error.URLError))
    Request.assert_called()


@pytest.mark.parametrize("retries", range(10))
@patch.multiple("mtg_proxy_printer.http_file.urllib.request", autospec=True, Request=DEFAULT, urlopen=DEFAULT)
@patch("mtg_proxy_printer.http_file.time.sleep", MagicMock(spec=time.sleep))
def test__urlopen_in_read_works_with_multiple_retries(
        retries: int, urlopen: MagicMock = None, Request: MagicMock = None):
    urlopen.side_effect = ([MagicMock(spec=http.client.HTTPResponse)]
                                + [urllib.error.URLError("Test error")]*retries
                                + [MagicMock(spec=http.client.HTTPResponse)])
    file = MeteredSeekableHTTPFile("")
    file.file.read.side_effect = socket.timeout
    file.read(10)
    Request.assert_called()


@pytest.mark.parametrize("retries", range(10, 12))
@patch.multiple("mtg_proxy_printer.http_file.urllib.request", autospec=True, Request=DEFAULT, urlopen=DEFAULT)
@patch("mtg_proxy_printer.http_file.time.sleep", MagicMock(spec=time.sleep))
def test__urlopen_in_read_raises_exception_when_exceeding_retries(
        retries: int, urlopen: MagicMock = None, Request: MagicMock = None):
    urlopen.side_effect = ([MagicMock(spec=http.client.HTTPResponse)]
                                + [urllib.error.URLError("Test error")] * retries
                                + [MagicMock(spec=http.client.HTTPResponse)])
    file = MeteredSeekableHTTPFile("")
    file.file.read.side_effect = socket.timeout
    assert_that(calling(file.read), raises(urllib.error.URLError))
    Request.assert_called()


@patch.multiple("mtg_proxy_printer.http_file.urllib.request", autospec=True, Request=DEFAULT, urlopen=DEFAULT)
def test__urlopen_not_includes_range_header_by_default(urlopen: MagicMock = None, Request: MagicMock = None):
    MeteredSeekableHTTPFile("")
    assert_that(
        Request.call_args[1],
        has_entry("headers", all_of(
            has_key("User-Agent"),
            not_(has_key("Accept-Range")),
        ))
    )
    urlopen.assert_called()


@patch.multiple("mtg_proxy_printer.http_file.urllib.request", autospec=True, Request=DEFAULT, urlopen=DEFAULT)
def test__urlopen_includes_range_header_when_seeking_to_non_zero_pos(urlopen: MagicMock = None, Request: MagicMock = None):
    file = MeteredSeekableHTTPFile("")
    file.content_length = 10
    position = 1
    with patch.object(file, "seekable", return_value=True):
        file.seek(position)
    assert_that(
        Request.call_args[1],
        has_entry("headers", all_of(
            has_key("User-Agent"),
            has_entry("range", equal_to(f"bytes={position}-{file.content_length-1}")),
        ))
    )
    urlopen.assert_called()
