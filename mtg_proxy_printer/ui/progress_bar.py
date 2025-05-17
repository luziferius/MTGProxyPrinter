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
import weakref
from functools import partial

from PyQt5.QtCore import pyqtSlot as Slot, Qt
from PyQt5.QtWidgets import QWidget,QHBoxLayout

from mtg_proxy_printer.runner import AsyncTask

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
        self.task = weakref.ref(task)
        self.ui = ui = Ui_ProgressBar()
        self.can_cancel = task.can_cancel
        ui.setupUi(self)
        ui.progress_bar.setValue(0)
        ui.cancel_button.hide()
        ui.cancel_button.clicked.connect(task.cancel)
        self.set_progress = ui.progress_bar.setValue
        task.begin_task.connect(self.begin_progress)
        task.set_progress.connect(ui.progress_bar.setValue)
        task.advance_progress.connect(self.advance_progress)
        task.task_completed.connect(self.hide)

    @Slot(int)
    @Slot(int, str)
    def begin_progress(self, upper_limit: int, ui_hint: str = ""):
        ui = self.ui
        label = ui.task_label
        label.setText(ui_hint)
        label.setVisible(bool(ui_hint))
        progress_bar = ui.progress_bar
        progress_bar.setMaximum(upper_limit)
        ui.cancel_button.setVisible(self.can_cancel)

    @Slot()
    @Slot(int)
    def advance_progress(self, amount: int = 1):
        bar = self.ui.progress_bar
        bar.setValue(bar.value() + amount)


class ProgressBarManager(QWidget):
    """Displays progress bars of currently running async tasks in the status bar."""
    def __init__(self, parent: QWidget = None, flags=Qt.WindowType()):
        super().__init__(parent, flags)
        self.setLayout(self._setup_layout())

    def _setup_layout(self) -> QHBoxLayout:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        return layout

    @Slot(AsyncTask)
    def add_task(self, task: AsyncTask):
        """Create a new progress bar for the given task"""
        bar = ProgressBar(task, self)
        layout = self.layout()
        task.task_deleted.connect(partial(layout.removeWidget, bar))
        task.task_deleted.connect(partial(bar.setParent, None))
        layout.addWidget(bar)
