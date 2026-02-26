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

from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QSpinBox, QWidget, QStyleOptionViewItem
import pytest
from hamcrest import *
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.model.card import MTGSet
from mtg_proxy_printer.ui.item_delegates import BoundedCopiesSpinboxDelegate, SetEditorDelegate

from tests.hasgetter import has_getters


@pytest.fixture()
def bounded_copies_spinbox(qtbot: QtBot) -> QSpinBox:
    parent = QWidget()
    qtbot.add_widget(parent)
    delegate = BoundedCopiesSpinboxDelegate()
    editor = delegate.createEditor(parent, QStyleOptionViewItem(), QModelIndex())
    yield editor


def test_BoundedCopiesSpinboxDelegate_createEditor_returns_correct_type(bounded_copies_spinbox: QSpinBox):
    assert_that(bounded_copies_spinbox, is_(instance_of(QSpinBox)))

def test_BoundedCopiesSpinboxDelegate_createEditor_has_correct_limits(bounded_copies_spinbox: QSpinBox):
    assert_that(bounded_copies_spinbox, has_getters(minimum=1, maximum=100))


@pytest.mark.parametrize("mtg_set", [MTGSet("BAR", "bar"), MTGSet("FOO", "foo")])
def test_CustomCardSetEditor_set_data(qtbot: QtBot, mtg_set: MTGSet):
    editor = SetEditorDelegate.CustomCardSetEditor()
    qtbot.add_widget(editor)
    editor.set_data(mtg_set)
    assert_that(editor.ui.name_editor.text(), is_(equal_to(mtg_set.name)))
    assert_that(editor.ui.code_edit.text(), is_(equal_to(mtg_set.code)))


@pytest.mark.parametrize("mtg_set", [MTGSet("BAR", "bar"), MTGSet("FOO", "foo")])
def test_CustomCardSetEditor_to_mtg_set(qtbot: QtBot, mtg_set: MTGSet):
    editor = SetEditorDelegate.CustomCardSetEditor()
    qtbot.add_widget(editor)
    editor.ui.name_editor.setText(mtg_set.name)
    editor.ui.code_edit.setText(mtg_set.code)
    assert_that(editor.to_mtg_set(), is_(equal_to(mtg_set)))
