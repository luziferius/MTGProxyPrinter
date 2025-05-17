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
from typing import List

from PyQt5.QtCore import QRunnable, QObject, pyqtSignal as Signal, pyqtSlot as Slot

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

__all__ = [
    "Runnable",
    "AsyncTask",
    "AsyncTask",
    "AsyncTaskRunner",
]

class AsyncTask(QObject):
    """Base class for asynchronous tasks with progress reporting"""

    begin_task = Signal(int, str)  # Task begin. Carries the expected work steps and a UI display string
    set_progress = Signal(int)  # Progress is set to the value carried by the signal
    advance_progress = Signal()  # Progress advances by exactly one step
    task_completed = Signal()  # The work completed, but progress may restart
    ui_update_required = Signal()  # Card database related work completed. UI needs to re-populate the card search
    error_occurred = Signal(str)  # A general error occurred. The signal carries the error description for display
    network_error_occurred = Signal(str)  # A network error occurred. Only applicable for network-facing tasks
    task_deleted = Signal()  # The ProgressBarManager uses this to delete the associated progress bar for this task
    # Can be used by a task to register progress bars for sub-tasks. Carries AsyncTask,
    # but that can't be specified here, because the name is still undefined in the static class context
    request_register_subtask = Signal(QObject)

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.inner_tasks: List[AsyncTask] = []

    def emit_delete_recursive(self):
        """Emits the task_deleted signal for all inner child tasks, then for itself.
        Called by the AsyncTaskRunner to clean up the progress bars in the main window"""
        for item in self.inner_tasks:
            item.emit_delete_recursive()
        self.task_deleted.emit()

    @property
    def can_cancel(self) -> bool:
        return False

    @Slot()
    def cancel(self):
        pass

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
    """A Runnable that executes an AsyncTask instance"""
    def __init__(self, task: AsyncTask):
        super().__init__()
        self.task = task

    def run(self):
        try:
            self.task.run()
        finally:
            self.task.emit_delete_recursive()
            self.release_instance()