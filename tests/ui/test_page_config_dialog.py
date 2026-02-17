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


import pytest

from PySide6.QtWidgets import QDialogButtonBox
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.ui.dialogs import DocumentSettingsDialog
StandardButton = QDialogButtonBox.StandardButton


def test__init__(document_light: Document):
    """Ensure that the dialog can be instantiated"""
    DocumentSettingsDialog(document_light)


@pytest.mark.parametrize("button_role", [StandardButton.Save])
def test_saving_actions_modify_document_settings(
        qtbot: QtBot, document_light: Document, button_role: StandardButton):
    dialog = DocumentSettingsDialog(document_light)
    qtbot.add_widget(dialog)
    with qtbot.wait_exposed(dialog):
        dialog.show()
    button_box = dialog.ui.button_box
    button = button_box.button(button_role)
    with qtbot.wait_signal(document_light.action_applied):
        button.click()


@pytest.mark.parametrize("button_role", [StandardButton.Reset, StandardButton.Cancel, StandardButton.RestoreDefaults])
def test_reverting_actions_do_not_alter_the_document_settings(
        qtbot: QtBot, document_light: Document, button_role: StandardButton):
    dialog = DocumentSettingsDialog(document_light)
    qtbot.add_widget(dialog)
    with qtbot.wait_exposed(dialog):
        dialog.show()
    button_box = dialog.ui.button_box
    button = button_box.button(button_role)
    with qtbot.assert_not_emitted(document_light.action_applied):
        button.click()
