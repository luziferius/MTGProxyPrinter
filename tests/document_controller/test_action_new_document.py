# Copyright (C) 2022 Thomas Hess <thomas.hess@udo.edu>

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

import pathlib
from unittest.mock import patch

import pytest
from hamcrest import *

import mtg_proxy_printer.document_controller.new_document
from mtg_proxy_printer.document_controller.page_actions import ActionRemovePage
from mtg_proxy_printer.document_controller.edit_document_settings import ActionEditDocumentSettings
from mtg_proxy_printer.document_controller.new_document import ActionNewDocument


def test_apply(qtbot, document_light):
    save_path = document_light.save_file_path = pathlib.PurePath("Test")
    action = ActionNewDocument()

    action.apply(document_light)
    assert_that(
        document_light.save_file_path, is_(none())
    )

    assert_that(action.old_save_path, is_(equal_to(save_path)))
    assert_that(action.reset_settings_action, is_(instance_of(ActionEditDocumentSettings)))
    assert_that(action.remove_pages_action, is_(instance_of(ActionRemovePage)))
    assert_that(action.remove_pages_action.removed_pages, has_length(1))
    assert_that(action.new_page_layout, is_(not_none()))


def test_apply_applies_internal_actions(qtbot, document_light):
    action = ActionNewDocument()
    with patch("mtg_proxy_printer.document_controller.new_document.ActionRemovePage.apply") as remove_apply_mock, \
            patch("mtg_proxy_printer.document_controller.new_document.ActionEditDocumentSettings.apply") as \
            edit_settings_apply_mock:
        action.apply(document_light)
    remove_apply_mock.assert_called_once_with(document_light)
    edit_settings_apply_mock.assert_called_once_with(document_light)


def test_undo_undoes_internal_actions(qtbot, document_light):
    action = ActionNewDocument()
    action.apply(document_light)
    old_save_path = action.old_save_path = pathlib.PurePath("Test")

    with patch("mtg_proxy_printer.document_controller.new_document.ActionRemovePage.undo") as remove_undo_mock, \
            patch("mtg_proxy_printer.document_controller.new_document.ActionEditDocumentSettings.undo") as \
            edit_settings_undo_mock:
        action.undo(document_light)
    remove_undo_mock.assert_called_once_with(document_light)
    edit_settings_undo_mock.assert_called_once_with(document_light)
    assert_that(document_light.save_file_path, is_(equal_to(old_save_path)))