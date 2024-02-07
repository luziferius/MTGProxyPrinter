# Copyright (C) 2020-2024 Thomas Hess <thomas.hess@udo.edu>
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

from PyQt5.QtCore import pyqtSlot as Slot, Qt
from PyQt5.QtWidgets import QWidget, QLabel, QProgressBar

try:
    from mtg_proxy_printer.ui.generated.progress_bar import Ui_ProgressBar
except ModuleNotFoundError:
    from mtg_proxy_printer.ui.common import load_ui_from_file
    Ui_ProgressBar = load_ui_from_file("progress_bar")

from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger
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
        
    @staticmethod
    def _set_retain_size_policy(wigdget: QWidget, value: bool):
        policy = wigdget.sizePolicy()
        policy.setRetainSizeWhenHidden(value)
        wigdget.setSizePolicy(policy)

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
    def end_outer_progress(self):
        progress_bar = self.ui.outer_progress_bar
        if (current := progress_bar.value()) != (maximum := progress_bar.maximum()):
            logger.warning(f"Outer progress bar missed 100% upon completion. {current=}, {maximum=}")
        progress_bar.hide()
        self.ui.outer_progress_label.hide()

    @Slot()
    def end_inner_progress(self):
        progress_bar = self.ui.inner_progress_bar
        if (current := progress_bar.value()) != (maximum := progress_bar.maximum()):
            logger.warning(f"Inner progress bar missed 100% upon completion. {current=}, {maximum=}")
        progress_bar.hide()
        self.ui.inner_progress_label.hide()

    @Slot()
    def end_independent_progress(self):
        progress_bar = self.ui.independent_bar
        if (current := progress_bar.value()) != (maximum := progress_bar.maximum()):
            logger.warning(f"Independent progress bar missed 100% upon completion. {current=}, {maximum=}")
        progress_bar.hide()
        self.ui.independent_label.hide()
