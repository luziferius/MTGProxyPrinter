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

from unittest.mock import MagicMock

from PySide6.QtCore import QObject
import pytest
from hamcrest import *
from mtg_proxy_printer.document_controller import IllegalStateError, DocumentAction


@pytest.fixture()
def action() -> DocumentAction:
    return DocumentAction()


def test_init_sets_parent():
    action = DocumentAction(object_ := QObject())
    assert_that(action.parent(), is_(same_instance(object_)))


def test_apply_sets_already_applied(action: DocumentAction):
    action._already_applied = False
    action.apply(MagicMock())
    assert_that(action._already_applied, is_(True))


def test_apply_twice_raises_exception(action: DocumentAction):
    action.apply(MagicMock())
    assert_that(calling(action.apply).with_args(MagicMock()), raises(IllegalStateError))


def test_undo_sets_already_applied(action: DocumentAction):
    action._already_applied = True
    action.undo(MagicMock())
    assert_that(action._already_applied, is_(False))


def test_undo_twice_raises_exception(action: DocumentAction):
    action._already_applied = True
    action.undo(MagicMock())
    assert_that(calling(action.undo).with_args(MagicMock()), raises(IllegalStateError))


def test_apply_undo_cycles_work(action: DocumentAction):
    mock = MagicMock()
    action.apply(mock)
    action.undo(mock)
    action.apply(mock)
    action.undo(mock)
