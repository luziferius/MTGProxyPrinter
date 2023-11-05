# Copyright (C) 2018-2023 Thomas Hess <thomas.hess@udo.edu>
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

from hamcrest import *
import pytest
from PySide6.QtWidgets import QWidget
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.ui.progress_bar import ProgressBar
from tests.hasgetter import has_getters


INNER_ELEMENTS = ["inner_progress_bar", "inner_progress_label"]
OUTER_ELEMENTS = ["outer_progress_bar", "outer_progress_label"]
INDEPENDENT_ELEMENTS = ["independent_bar", "independent_label"]
ALL_ELEMENTS = INNER_ELEMENTS + OUTER_ELEMENTS + INDEPENDENT_ELEMENTS


@pytest.fixture()
def bar(qtbot: QtBot) -> ProgressBar:
    progress_bar = ProgressBar()
    qtbot.add_widget(progress_bar)
    with qtbot.wait_exposed(progress_bar):
        progress_bar.show()
    yield progress_bar
    progress_bar.hide()


@pytest.mark.parametrize("element", ALL_ELEMENTS)
def test___init___hides_ui(bar: ProgressBar, element: str):
    widget: QWidget = getattr(bar.ui, element)
    assert_that(widget.isHidden(), is_(True))


def test_begin_outer_progress_configures_label(bar: ProgressBar):
    bar.begin_outer_progress(10, "Test")
    assert_that(
        bar.ui.outer_progress_label,
        has_getters({
            "isVisible": is_(True),
            "text": equal_to("Test"),
        })
    )


def test_begin_outer_progress_configures_progress_bar(bar: ProgressBar):
    bar.begin_outer_progress(10, "Test")
    assert_that(
        bar.ui.outer_progress_bar,
        has_getters({
            "isVisible": is_(True),
            "value": is_(0),
            "maximum": is_(10),
        })
    )


def test_begin_outer_progress_resets_progress(bar: ProgressBar):
    bar.ui.outer_progress_bar.setValue(5)
    bar.begin_outer_progress(10, "Test")
    assert_that(bar.ui.outer_progress_bar.value(), is_(0))


def test_begin_inner_progress_configures_label(bar: ProgressBar):
    bar.begin_inner_progress(10, "Test")
    assert_that(
        bar.ui.inner_progress_label,
        has_getters({
            "isVisible": is_(True),
            "text": equal_to("Test"),
        })
    )


def test_begin_inner_progress_configures_progress_bar(bar: ProgressBar):
    bar.begin_inner_progress(10, "Test")
    assert_that(
        bar.ui.inner_progress_bar,
        has_getters({
            "isVisible": is_(True),
            "value": is_(0),
            "maximum": is_(10),
        })
    )


def test_begin_inner_progress_resets_progress(bar: ProgressBar):
    bar.ui.inner_progress_bar.setValue(5)
    bar.begin_inner_progress(10, "Test")
    assert_that(bar.ui.inner_progress_bar.value(), is_(0))


def test_begin_independent_progress_configures_label(bar: ProgressBar):
    bar.begin_independent_progress(10, "Test")
    assert_that(
        bar.ui.independent_label,
        has_getters({
            "isVisible": is_(True),
            "text": equal_to("Test"),
        })
    )


def test_begin_independent_progress_configures_progress_bar(bar: ProgressBar):
    bar.begin_independent_progress(10, "Test")
    assert_that(
        bar.ui.independent_bar,
        has_getters({
            "isVisible": is_(True),
            "value": is_(0),
            "maximum": is_(10),
        })
    )


def test_begin_independent_progress_resets_progress(bar: ProgressBar):
    bar.ui.independent_bar.setValue(5)
    bar.begin_independent_progress(10, "Test")
    assert_that(bar.ui.independent_bar.value(), is_(0))


@pytest.mark.parametrize("value", [0, 5, 10])
def test_set_outer_progress(bar: ProgressBar, value: int):
    bar.set_outer_progress(value)
    assert_that(bar.ui.outer_progress_bar.value(), is_(equal_to(value)))


@pytest.mark.parametrize("value", [0, 5, 10])
def test_set_inner_progress(bar: ProgressBar, value: int):
    bar.set_inner_progress(value)
    assert_that(bar.ui.inner_progress_bar.value(), is_(equal_to(value)))


@pytest.mark.parametrize("value", [0, 5, 10])
def test_independent_progress(bar: ProgressBar, value: int):
    bar.set_independent_progress(value)
    assert_that(bar.ui.independent_bar.value(), is_(equal_to(value)))
