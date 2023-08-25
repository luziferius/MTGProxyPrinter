# Copyright (C) 2023 Thomas Hess <thomas.hess@udo.edu>
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

import logging
from unittest.mock import NonCallableMagicMock


import pytest
from PyQt5.QtCore import QThread

from mtg_proxy_printer.stop_thread import stop_thread


@pytest.fixture
def mock_thread():
    mock = NonCallableMagicMock(spec=QThread)
    yield mock


@pytest.fixture
def mock_logger():
    mock = NonCallableMagicMock(spec=logging.Logger)
    yield mock


def test_stop_thread_does_nothing_on_stopped_thread(mock_thread, mock_logger):
    mock_thread.isRunning.return_value = False
    stop_thread(mock_thread, mock_logger)

    mock_thread.isRunning.assert_called()
    mock_thread.quit.assert_not_called()
    mock_thread.terminate.assert_not_called()
    mock_thread.setTerminationEnabled.assert_not_called()

    mock_logger.info.assert_not_called()
    mock_logger.error.assert_not_called()
    mock_logger.critical.assert_not_called()


def test_stop_thread_stops_running_thread_gracefully(mock_thread, mock_logger):
    mock_thread.isRunning.return_value = True
    mock_thread.wait.side_effect = [True, True]
    stop_thread(mock_thread, mock_logger)

    mock_thread.isRunning.assert_called()
    mock_thread.quit.assert_called_once()
    mock_thread.terminate.assert_not_called()
    mock_thread.setTerminationEnabled.assert_not_called()

    mock_logger.info.assert_called_once()
    mock_logger.error.assert_not_called()
    mock_logger.critical.assert_not_called()


def test_stop_thread_terminates_not_responding_thread(mock_thread, mock_logger):
    mock_thread.isRunning.return_value = True
    mock_thread.wait.side_effect = [False, True]
    stop_thread(mock_thread, mock_logger)

    mock_thread.isRunning.assert_called()
    mock_thread.quit.assert_called_once()
    mock_thread.terminate.assert_called_once()
    mock_thread.setTerminationEnabled.assert_called_once_with(True)

    mock_logger.info.assert_called_once()
    mock_logger.error.assert_called_once()
    mock_logger.critical.assert_not_called()


def test_stop_thread_logs_failure_in_terminate(mock_thread, mock_logger):
    mock_thread.isRunning.return_value = True
    mock_thread.wait.side_effect = [False, False]
    stop_thread(mock_thread, mock_logger)

    mock_thread.isRunning.assert_called()
    mock_thread.quit.assert_called_once()
    mock_thread.terminate.assert_called_once()
    mock_thread.setTerminationEnabled.assert_called_once_with(True)

    mock_logger.info.assert_called_once()
    mock_logger.error.assert_called_once()
    mock_logger.critical.assert_called_once()
