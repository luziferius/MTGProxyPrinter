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


from unittest.mock import MagicMock, patch

import pytest
from hamcrest import *

from mtg_proxy_printer.progress_meter import ProgressMeter


@pytest.fixture
def progress_meter():
    return ProgressMeter(3, "Test Message", MagicMock(), MagicMock(), MagicMock())


@pytest.mark.parametrize("count, step", [
    (4, 1),
    (1, 4),
])
def test_error_reported_when_overshooting(progress_meter: ProgressMeter, count, step):
    with patch("mtg_proxy_printer.progress_meter.logger") as logger:
        for i in range(count):
            progress_meter.advance(step)
    logger.error.assert_called()


@pytest.mark.parametrize("initial_value, step", [
    (0, -1),
    (1, -2),
])
def test_negative_step_to_negative_total_progress_raises_exception(progress_meter, initial_value, step):
    progress_meter._progress = initial_value
    assert_that(calling(progress_meter.advance).with_args(step), raises(ValueError))


@pytest.mark.parametrize("initial_value, step", [
    (0, 0), (3, 0),
    # Negative step
    (1, -1), (2, -1), (2, -2),
    # Positive step
    (0, 1), (0, 2), (1, 2),
    # Overshooting works
    (1, 10),
])
def test_advance_within_range_works(qtbot, progress_meter, initial_value, step):
    progress_meter._progress = initial_value
    target = initial_value + step
    progress_meter.advance(step)
    progress_meter.progress_signal.assert_called_with(target)
    assert_that(progress_meter._progress, is_(target))
