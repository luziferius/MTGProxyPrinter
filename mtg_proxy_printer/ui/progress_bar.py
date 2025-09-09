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

from functools import partial
from typing import Callable

from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import QWidget,QHBoxLayout

from mtg_proxy_printer.async_tasks.base import AsyncTask

try:
    from mtg_proxy_printer.ui.generated.progress_bar import Ui_ProgressBar
except ModuleNotFoundError:
    from mtg_proxy_printer.ui.common import load_ui_from_file
    Ui_ProgressBar = load_ui_from_file("progress_bar")

from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger
ConnectionType = Qt.ConnectionType
QueuedConnection = ConnectionType.QueuedConnection
__all__ = [
    "ProgressBarManager",
]

class ProgressBar(QWidget):
    def __init__(self, task: AsyncTask, parent: QWidget = None, flags=Qt.WindowType()):
        super().__init__(parent, flags)
        self.task = task
        self.ui = ui = Ui_ProgressBar()
        ui.setupUi(self)
        policy = self.sizePolicy()
        policy.setRetainSizeWhenHidden(True)  # Prevent jitter when batch tasks hide/show subtask progress bars.
        self.setSizePolicy(policy)
        ui.progress_bar.setValue(0)
        ui.cancel_button.hide()
        ui.cancel_button.clicked.connect(task.cancel)
        task.task_begins.connect(self.begin_progress)
        task.set_progress.connect(ui.progress_bar.setValue)
        task.advance_progress.connect(self.advance_progress)
        task.task_completed.connect(self.hide)
        self.hide()

    @Slot(int)
    @Slot(int, str)
    def begin_progress(self, upper_limit: int, ui_hint: str = ""):
        ui = self.ui
        self.show()  # Support re-use
        label = ui.task_label
        label.setText(ui_hint)
        label.setVisible(bool(ui_hint))
        progress_bar = ui.progress_bar
        progress_bar.setMaximum(upper_limit)
        progress_bar.show()  # Support re-use
        ui.cancel_button.setVisible(self.task.can_cancel)

    @Slot()
    @Slot(int)
    def advance_progress(self, amount: int = 1):
        bar = self.ui.progress_bar
        bar.setValue(bar.value() + amount)


class ProgressBarManager(QWidget):
    """Displays progress bars of currently running async tasks in the status bar."""
    layout: Callable[[], QHBoxLayout]

    def __init__(self, parent: QWidget = None, flags=Qt.WindowType.Widget):
        super().__init__(parent, flags)
        self.setLayout(self._setup_layout())

    def _setup_layout(self) -> QHBoxLayout:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        return layout

    @Slot(AsyncTask)
    def add_task(self, task: AsyncTask):
        """Create a new progress bar for the given task"""
        logger.debug(f"Adding progress bar for task {task}")
        bar = ProgressBar(task, self)
        layout = self.layout()
        task.request_register_subtask.connect(lambda subtask: logger.debug(f"Registering subtask {subtask}"))
        task.request_register_subtask.connect(self.add_task)
        task.task_deleted.connect(lambda: logger.debug(f"Deleting progress bar for task {task}"))
        task.task_deleted.connect(partial(layout.removeWidget, bar))
        task.task_deleted.connect(partial(bar.setParent, None))
        layout.insertWidget(0, bar)
