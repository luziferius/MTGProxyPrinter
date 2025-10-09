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

import abc

from PySide6.QtCore import QRunnable, QObject, Signal, Slot

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

__all__ = [
    "AsyncTaskRunner",
    "AsyncTask",
]

"""
# Design

- Async background tasks are classes that use a custom base class (AsyncTask)
  derived from QObject to inherit Qt's Signal & Slot mechanism, and a fixed API to launch them
- The AsyncTask base class holds Qt signals for progress reporting, and are started by the tasks run() method. Signals are:
  - Starting a task with expected task size and UI string to display
  - advancing a task by 1, or setting progress to any number
  - finishing a task with ability to re-start
  - and removing a finished task completely.
- AsyncTasks can have nested sub-tasks. These are synchronous within the task, but can report individual progress.
  - Example: A sequence of card image downloads can be triggered by a document load or deck list import
- Cancelable async tasks have can_cancel() return True
  - For these, a cancel button is shown next to the progress bar
  - Triggering the cancel button is connected to the cancel() slot. How that cancels the operation is up to the task
- A method in the Application class handles launching them
  - It wraps them in the AsyncTaskRunner QRunnable subclass
  - Registers it in the ProgressBarManager to create progress bar for it to display progress
  - Then pushes the task into the global QThreadPool
- The ProgressBarManager sets up a progress bar widget in the main window status bar,
  and connects the tasks progress signals with the appropriate slots

# TODO: 
- Some export tasks require locking the UI, because they take time during which the document must be immutable.
- Implement tasks that lock the UI
  - Add `is_locking: bool` to the AsyncTask class.
  - Default to False
  - If True, lock the main window UI when such a task starts, and unlock when it finishes
  - To be completely safe, use a Semaphore or similar to count the number of active UI locks,
    and unlock when the lock count is zero.
  - Locking can use the normal progress signals. When `is_locking` is True, simply connect the begin_progress and 
    finish_progress signals to the lock/unlock methods. The task dispatch method can handle those connections


"""


class AsyncTask(QObject):
    # TODO: Introduce a "blocking UI" flag. A blocking task disables most of the GUI
    """
    Base class for asynchronous tasks with progress reporting.
    """

    task_begins = Signal(int, str)  # Carries the expected work steps and a UI display string
    set_progress = Signal(int)  # Progress is set to the value carried by the signal
    advance_progress = Signal()  # Progress advances by exactly one step
    task_completed = Signal()  # The work completed, but progress may restart
    ui_update_required = Signal()  # Card database related work completed. UI needs to re-populate the card search
    # TODO: Unify both error signals? Introduce an ErrorType enum (General, Network, etc) and pass that as a parameter
    error_occurred = Signal(str)  # A general error occurred. The signal carries the error description for display
    network_error_occurred = Signal(str)  # A network error occurred. Only applicable for network-facing tasks
    task_deleted = Signal()  # Task gone for good. Progress bars can be deleted from the UI
    ui_lock_acquire = Signal()  # Task enters a critical section during which the document must be immutable
    ui_lock_release = Signal()  # Task leaves a critical section

    # Can be used by a task to register progress bars for sub-tasks. Carries AsyncTask,
    # but that can't be specified here, because the name is still undefined in the static class context
    request_register_subtask = Signal(QObject)

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.inner_tasks: list[AsyncTask] = []
        self._running = False
        self._ui_hint = ""
        self.task_begins.connect(self._on_task_begins)
        self.task_completed.connect(self._on_task_completed)

    @Slot(int, str)
    def _on_task_begins(self, _: int, ui_hint: str):
        self._ui_hint = ui_hint
        self._running = True
        logger.debug(f"Work begins for {self}")

    @Slot()
    def _on_task_completed(self):
        self._ui_hint = ""
        self._running = False

    def emit_delete_recursive(self):
        """Emits the task_deleted signal for all inner child tasks, then for itself.
        Called by the AsyncTaskRunner to clean up the progress bars in the main window"""
        for item in self.inner_tasks:
            item.emit_delete_recursive()
        try:
            self.task_deleted.emit()
        except RuntimeError:
            # When shutdown is stalled by I/O, the task may be deleted during the emit process.
            # Simply ignore this.
            pass

    @property
    def report_progress(self) -> bool:
        """If True, the task progress should be shown in the UI via a progress bar."""
        return True

    @property
    def can_cancel(self) -> bool:
        return False

    @Slot()
    def cancel(self):
        msg = f"cancel() called on task {self.__class__.__name__} with {self.can_cancel=}"
        logger.critical(msg)
        raise NotImplementedError(msg)

    @abc.abstractmethod
    def run(self):
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}. Running: {self._running}, Processing task:'{self._ui_hint}'"


class AsyncTaskRunner(QRunnable):
    """A QRunnable that executes an AsyncTask instance"""

    INSTANCES: dict[int, "AsyncTaskRunner"] = {}

    def __init__(self, task: AsyncTask):
        super().__init__()
        self.task = task
        AsyncTaskRunner.INSTANCES[id(self)] = self

    def run(self):
        """
        Executes the saved task.

        When the task run() returns,
        emits the tasks emit_delete_recursive signal to clean up progress bars.

        Implicitly called by QThreadPool.start()
        """
        try:
            logger.debug(f"Entering {self.task.__class__.__name__}.run()")
            self.task.run()
        finally:
            self.task.emit_delete_recursive()
            logger.debug(f"Releasing {self.__class__.__name__} instance for completed {self.task}")
            try:
                del AsyncTaskRunner.INSTANCES[id(self)]
            except KeyError:
                pass

    @classmethod
    def cancel_all_tasks(cls):
        if not cls.INSTANCES:
            return
        logger.info(f"Cancelling {len(cls.INSTANCES)} running tasks.")
        for item in list(cls.INSTANCES.values()):
            task = item.task
            logger.debug(f"Cancel task {task}")
            if task.can_cancel:
                task.cancel()
        cls.INSTANCES.clear()
