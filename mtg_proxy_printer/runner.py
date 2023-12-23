# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>
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
import typing
from functools import partial

from PyQt5.QtCore import QRunnable, QTimer

__all__ = [
    "Runnable",
]


class Runnable(QRunnable):
    INSTANCES: typing.List["Runnable"] = []

    def __init__(self):
        super().__init__()
        self.INSTANCES.append(self)

    def release_instance(self):
        QTimer.singleShot(100, partial(self.INSTANCES.remove, self))

    def cancel(self):
        pass

    @classmethod
    def cancel_all_runners(cls):
        for item in cls.INSTANCES:
            item.cancel()
