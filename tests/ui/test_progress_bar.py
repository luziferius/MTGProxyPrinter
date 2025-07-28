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

from hamcrest import *
import pytesSide6.QtWidgets
from import QWidgePyt
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.runner import AsyncTask
from mtg_proxy_printer.ui.progress_bar import ProgressBar, ProgressBarManager

from tests.hasgetter import has_getter, has_getters


@pytest.fixture()
def bar(qtbot: QtBot) -> ProgressBar:
    task = AsyncTask()
    progress_bar = ProgressBar(task)
    qtbot.add_widget(progress_bar)
    with qtbot.wait_exposed(progress_bar):
        progress_bar.show()
    return progress_bar


def test___init___initializes_hidden_state(bar: ProgressBar):
    ui = bar.ui
    assert_that(ui.cancel_button.isHidden(), is_(True))
    assert_that(ui.task_label.isVisible(), is_(True))
    assert_that(ui.progress_bar.isVisible(), is_(True))


@pytest.mark.parametrize("text, visible", [
    ("Test task", True),
    ("Other", True),
    ("", False),
])
def test_begin_task_signal_sets_ui_label(bar: ProgressBar, text: str, visible: bool):
    bar.task.begin_task.emit(123, text)
    label = bar.ui.task_label
    assert_that(
        label, has_getters({
            "text": equal_to(text),
            "isVisible": equal_to(visible),
        })
    )


@pytest.mark.parametrize("value", [1, 10, 1000])
def test_begin_task_signal_sets_progress_bar_maximum(bar: ProgressBar, value: int):
    bar.task.begin_task.emit(value, "")
    progress_bar = bar.ui.progress_bar
    assert_that(
        progress_bar, has_getters({
            "minimum": equal_to(0),
            "maximum": equal_to(value),
            "value": equal_to(0),
        })
    )


def test_advance_progress_signal_advances_progress_by_1(bar: ProgressBar):
    bar.task.begin_task.emit(10, "")
    for value in range(1, 11):
        bar.task.advance_progress.emit()
        progress_bar = bar.ui.progress_bar
        assert_that(
            progress_bar, has_getters({
                "minimum": equal_to(0),
                "maximum": equal_to(10),
                "value": equal_to(value),
            })
        )


@pytest.mark.parametrize("value", [1, 10, 100])
def test_set_progress_signal_sets_progress(bar: ProgressBar, value: int):
    bar.task.begin_task.emit(1000, "")
    bar.task.set_progress.emit(value)
    progress_bar = bar.ui.progress_bar
    assert_that(
        progress_bar, has_getters({
            "minimum": equal_to(0),
            "maximum": equal_to(1000),
            "value": equal_to(value),
        })
    )

def test_task_completed_hides_itself(bar: ProgressBar):
    bar.task.task_completed.emit()
    assert_that(bar.isHidden(), is_(True))

def test_task_begin_shows_itself(bar: ProgressBar):
    bar.task.task_completed.emit()
    assert_that(bar.isHidden(), is_(True), "Test setup failed")
    bar.task.begin_task.emit(123, "Test")
    assert_that(bar.isVisible(), is_(True))
    assert_that(bar.ui, has_properties({
        "progress_bar": has_getter("isVisible", equal_to(True)),
        "task_label": has_getter("isVisible", equal_to(True)),
    }))



@pytest.fixture()
def manager(qtbot: QtBot) -> ProgressBarManager:
    manager = ProgressBarManager()
    qtbot.add_widget(manager)
    return manager


def test_manager_is_initially_empty(manager: ProgressBarManager):
    assert_that(manager, has_getter("layout", has_getter("isEmpty", equal_to(True))))


@pytest.mark.parametrize("count", [1, 5])
def test_manager_adds_bar_for_each_task(manager: ProgressBarManager, count: int):
    for _ in range(count):
        task = AsyncTask()
        manager.add_task(task)
    assert_that(
        manager.layout().count(), is_(count)
    )


def test_task_deletion_removes_task(manager: ProgressBarManager):
    manager.add_task(task1 := AsyncTask())
    manager.add_task(task2 := AsyncTask())
    task1.setObjectName("Completed")
    task2.setObjectName("Still running")
    task1.task_deleted.emit()
    assert_that(manager.findChildren(ProgressBar), contains_exactly(has_property("task", equal_to(task2))))
