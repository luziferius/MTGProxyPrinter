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


import typing

from PyQt5.QtCore import QRunnable, QObject, pyqtSignal as Signal

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

__all__ = [
    "Runnable",
    "ProgressSignalContainer"
]


class ProgressSignalContainer(QObject):
    begin_update = Signal(int, str)
    progress = Signal(int)
    update_completed = Signal()
    advance_progress = Signal()
    ui_update_required = Signal()
    error_occurred = Signal(str)


class Runnable(QRunnable):
    INSTANCES: typing.Dict[int, "Runnable"] = {}

    def __init__(self):
        super().__init__()
        Runnable.INSTANCES[id(self)] = self

    def release_instance(self):
        logger.debug(f"Releasing instance {self}")
        del Runnable.INSTANCES[id(self)]

    def cancel(self):
        pass

    @classmethod
    def cancel_all_runners(cls):
        if not cls.INSTANCES:
            return
        logger.info(f"Cancelling {len(cls.INSTANCES)} running tasks.")
        for item in list(cls.INSTANCES.values()):
            logger.debug(f"Cancel task {item}")
            item.cancel()
