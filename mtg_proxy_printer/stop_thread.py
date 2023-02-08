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

from logging import Logger

from PyQt5.QtCore import QThread


from mtg_proxy_printer.logger import get_logger

default_logger = get_logger(__name__)
del get_logger


def stop_thread(thread: QThread, logger: Logger = default_logger):
    """Stops a running QThread with logging."""
    if not thread.isRunning():
        return
    thread.quit()
    if not thread.wait(1000):
        logger.error("Background thread still running after quit()!")
        thread.setTerminationEnabled(True)
        thread.terminate()
        if not thread.wait(10000):
            logger.critical("Background thread still running after terminate()!")
    logger.info(f"Background worker stopped. Result: {thread.isRunning()=}")
