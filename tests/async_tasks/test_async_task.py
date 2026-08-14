#  Copyright © 2020-2026  Thomas Hess <thomas.hess@udo.edu>
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

from mtg_proxy_printer.async_tasks.base import AsyncTask, TaskCanceled

from hamcrest import *
import pytest


class NonCancelableTask(AsyncTask):
    def run(self):
        self.raise_if_canceled()


class CancelableTask(AsyncTask):
    @AsyncTask.cancelable
    def run(self):
        self.raise_if_canceled()


def test___init__():
    task = AsyncTask()
    assert_that(task._should_run, is_(True))
    assert_that(task._running, is_(False))


@pytest.mark.parametrize("task_class, expected", [
    (CancelableTask, True),
    (NonCancelableTask, False),
])
def test_can_cancel(task_class, expected: bool):
    task = task_class()
    assert_that(task.can_cancel, is_(expected))


@pytest.mark.parametrize("task_class", [
    CancelableTask,
    NonCancelableTask,
])
def test_cancel(task_class):
    task = task_class()
    assert_that(task._should_run, is_(True))
    task.cancel()
    assert_that(task._should_run, is_(False))


@pytest.mark.parametrize("task_class", [
    CancelableTask,
    NonCancelableTask,
])
def test_raise_if_canceled(task_class):
    task = task_class()
    task.raise_if_canceled()
    task.cancel()
    assert_that(calling(task.raise_if_canceled), raises(TaskCanceled))


@pytest.mark.parametrize("task_class, exception_swallowed", [
    (CancelableTask, True),
    (NonCancelableTask, False),
])
def test_cancelable_decorator(task_class, exception_swallowed: bool):
    task = task_class()
    task.cancel()
    if exception_swallowed:
        task.run()
    else:
        assert_that(calling(task.run), raises(TaskCanceled))
