# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>
import typing
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

from functools import partial

from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger


class ProgressMeter:

    def __init__(
            self, maximum: int, message: str,
            start_signal: typing.Callable[[int, str], None],
            progress_signal: typing.Callable[[int], None],
            end_signal: typing.Callable[[], None]):
        self._maximum = maximum
        self._progress = 0
        start_signal(maximum, message)
        self.progress_signal = progress_signal
        self.finish = end_signal

    def advance(self):
        self._progress += 1
        self.progress_signal(self._progress)

    def __del__(self):
        if self._progress != self._maximum:
            logger.warning(
                f"Progress meter did not advance to 100%. Expected target {self._maximum}, advanced to {self._progress}"
            )
        if hasattr(super(), "__del__"):
            super().__del__()
