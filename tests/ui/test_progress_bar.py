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
import pytest
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.runner import ProgressSignalContainer
from mtg_proxy_printer.ui.progress_bar import ProgressBar, ProgressBarManager
from tests.hasgetter import has_getters


@pytest.fixture()
def bar(qtbot: QtBot) -> ProgressBar:
    task = ProgressSignalContainer()
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


@pytest.fixture()
def manager(qtbot: QtBot) -> ProgressBarManager:
    manager = ProgressBarManager()
    qtbot.add_widget(manager)
    with qtbot.wait_exposed(manager):
        manager.show()
    return manager

# TODO: Unit tests for ProgressBarManager