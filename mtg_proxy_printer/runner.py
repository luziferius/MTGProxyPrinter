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

from PyQt5.QtCore import QRunnable, QObject, pyqtSignal as Signal, pyqtSlot as Slot

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

__all__ = [
    "Runnable",
    "ProgressSignalContainer",
    "AsyncTask",
    "AsyncTaskRunner",
]


class ProgressSignalContainer(QObject):
    begin_task = Signal(int, str)
    set_progress = Signal(int)
    advance_progress = Signal()
    task_completed = Signal()
    ui_update_required = Signal()
    error_occurred = Signal(str)

    @property
    def can_cancel(self) -> bool:
        return False

    @Slot()
    def cancel(self):
        pass

class AsyncTask(ProgressSignalContainer):
    """Base class for asynchronous tasks with progress reporting"""
    def run(self):
        pass


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


class AsyncTaskRunner(Runnable):
    """A QRunnable that executes an AsyncTask instance"""
    def __init__(self, task: AsyncTask):
        super().__init__()
        self.task = task

    def run(self):
        try:
            self.task.run()
        finally:
            self.release_instance()