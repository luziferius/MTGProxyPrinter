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

import typing

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

    def advance(self, step_size: int = 1):
        """Advance the progress by the given step size, defaulting to 1."""
        if (result := self._progress + step_size) < 0:
            raise ValueError(f"Progress below 0%: {result}")
        self._progress = result
        if result > self._maximum:
            logger.error(f"Overshot 100% progress! Maximum steps is {self._maximum}, reached {result}")
        self.progress_signal(result)

    def __del__(self):
        # This is present to emit a warning, if this object gets garbage collected without reaching 100% progress
        if self._progress != self._maximum:
            logger.warning(
                f"Progress meter did not advance to 100%. Expected target {self._maximum}, advanced to {self._progress}"
            )
        # __del__ documentation says to call the super() implementation. Do so, if it exists.
        getattr(super(), "__del__", lambda: None)()
