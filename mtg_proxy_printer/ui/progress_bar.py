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


from PyQt5.QtCore import pyqtSlot as Slot, Qt
from PyQt5.QtWidgets import QWidget, QLabel, QProgressBar

from mtg_proxy_printer.runner import ProgressSignalContainer

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
    "ProgressBar",
]


class ProgressBar(QWidget):

    def __init__(self, parent: QWidget = None, flags=Qt.WindowType()):
        super().__init__(parent, flags)
        self.ui = ui = Ui_ProgressBar()
        ui.setupUi(self)
        self.set_outer_progress = ui.outer_progress_bar.setValue
        self.set_inner_progress = ui.inner_progress_bar.setValue
        self.set_independent_progress = ui.independent_bar.setValue
        for item in (ui.inner_progress_bar, ui.inner_progress_label):
            self._set_retain_size_policy(item, True)
            item.hide()
        for item in (ui.outer_progress_bar, ui.outer_progress_label, ui.independent_bar, ui.independent_label):
            item.hide()

    def connect_inner_progress(self, sender: ProgressSignalContainer, con_type: ConnectionType = QueuedConnection):
        self._connect_progress_slots(
            sender, con_type,
            self.begin_inner_progress, self.set_inner_progress, self.advance_inner_progress, self.end_inner_progress
        )

    def connect_outer_progress(self, sender: ProgressSignalContainer, con_type: ConnectionType = QueuedConnection):
        self._connect_progress_slots(
            sender, con_type,
            self.begin_outer_progress, self.set_outer_progress, self.advance_outer_progress, self.end_outer_progress
        )

    def connect_independent_progress(self, sender: ProgressSignalContainer, con_type: ConnectionType = QueuedConnection):
        self._connect_progress_slots(
            sender, con_type,
            self.begin_independent_progress, self.set_independent_progress, self.advance_independent_progress,
            self.end_independent_progress
        )

    @staticmethod
    def _connect_progress_slots(
            sender: ProgressSignalContainer, con_type: ConnectionType,
            begin_slot, set_progress_slot, advance_progress_slot, end_slot):
        sender.begin_task.connect(begin_slot, con_type)
        sender.set_progress.connect(set_progress_slot, con_type)
        sender.advance_progress.connect(advance_progress_slot, con_type)
        sender.task_completed.connect(end_slot, con_type)

    @staticmethod
    def _set_retain_size_policy(widget: QWidget, value: bool):
        policy = widget.sizePolicy()
        policy.setRetainSizeWhenHidden(value)
        widget.setSizePolicy(policy)

    @Slot(int)
    @Slot(int, str)
    def begin_outer_progress(self, upper_limit: int, ui_hint: str = ""):
        self._begin_progress(self.ui.outer_progress_bar, self.ui.outer_progress_label, upper_limit, ui_hint)

    @Slot(int)
    @Slot(int, str)
    def begin_inner_progress(self, upper_limit: int, ui_hint: str = ""):
        self._begin_progress(self.ui.inner_progress_bar, self.ui.inner_progress_label, upper_limit, ui_hint)

    @Slot(int)
    @Slot(int, str)
    def begin_independent_progress(self, upper_limit: int, ui_hint: str = ""):
        self._begin_progress(self.ui.independent_bar, self.ui.independent_label, upper_limit, ui_hint)

    @staticmethod
    def _begin_progress(progress_bar: QProgressBar, label: QLabel, upper_limit: int, ui_hint: str):
        label.setText(ui_hint)
        label.setVisible(bool(ui_hint))
        progress_bar.setValue(0)
        progress_bar.setMaximum(upper_limit)
        progress_bar.setVisible(True)

    @Slot()
    @Slot(int)
    def advance_outer_progress(self, amount: int = 1):
        self._advance_progress(self.ui.outer_progress_bar, amount)

    @Slot()
    @Slot(int)
    def advance_inner_progress(self, amount: int = 1):
        self._advance_progress(self.ui.inner_progress_bar, amount)

    @Slot()
    @Slot(int)
    def advance_independent_progress(self, amount: int = 1):
        self._advance_progress(self.ui.independent_bar, amount)

    @staticmethod
    def _advance_progress(progress_bar: QProgressBar, amount: int):
        progress_bar.setValue(progress_bar.value() + amount)

    @Slot()
    def end_outer_progress(self):
        ui = self.ui
        self._end_progress(ui.outer_progress_bar, ui.outer_progress_label, "Outer")

    @Slot()
    def end_inner_progress(self):
        ui = self.ui
        self._end_progress(ui.inner_progress_bar, ui.inner_progress_label, "Inner")

    @Slot()
    def end_independent_progress(self):
        ui = self.ui
        self._end_progress(ui.independent_bar, ui.independent_label, "Independent")

    @staticmethod
    def _end_progress(progress_bar: QProgressBar, label: QLabel, log_name: str):
        if (current := progress_bar.value()) != (maximum := progress_bar.maximum()):
            logger.warning(f"{log_name} progress bar missed 100% upon completion. {current=}, {maximum=}")
        progress_bar.hide()
        label.hide()
