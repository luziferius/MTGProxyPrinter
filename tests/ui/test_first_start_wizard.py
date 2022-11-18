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

import typing
import unittest.mock

import pytest
from hamcrest import *
from pytestqt.qtbot import QtBot

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox, QLabel, QWizardPage

from mtg_proxy_printer.settings import settings
import mtg_proxy_printer.ui.first_start_wizard as fsw

T = typing.TypeVar("T")


def create_widget(qtbot: QtBot, widget_class: typing.Type[T]) -> T:
    widget = widget_class()
    qtbot.add_widget(widget)
    with qtbot.waitExposed(widget):
        widget.show()
    return widget


@pytest.mark.parametrize("template, result", [
    ("Prefix {replace}{replace} Suffix", "Prefix abcabc Suffix"),
])
def test_format_label_text(qtbot: QtBot, template: str, result: str):
    label = QLabel(template)
    qtbot.add_widget(label)
    fsw.format_label_text(label, {"replace": "abc"})
    assert_that(label.text(), is_(result))


@pytest.mark.parametrize("page_class", [
    fsw.FirstPage, fsw.CardDBPage, fsw.UpdateCheckPage
])
def test_no_placeholder_texts_are_shown_to_user(qtbot: QtBot, page_class: typing.Type[QWizardPage]):
    """
    Verifies that no placeholders (identifiers enclosed in {}) are shown to users in any QLabel.
    A failing test indicates that a label with placeholder is not properly formatted.
    """
    page: QWizardPage = create_widget(qtbot, page_class)
    child: QLabel
    for child in page.findChildren(QLabel):
        assert_that(
            child.text(),
            not_(matches_regexp(r"{[a-zA-Z_]+}"))
        )


def test_first_start_wizard_relays_card_data_download_request_signal(qtbot: QtBot):
    wizard = create_widget(qtbot, fsw.FirstStartWizard)
    wizard.next()
    page: fsw.CardDBPage = wizard.currentPage()
    assert_that(page, is_(instance_of(fsw.CardDBPage)), "Wrong page order, fix test")
    with qtbot.waitSignal(wizard.card_data_download_requested):
        page.ui.download_card_data_button.click()


@pytest.mark.parametrize("field, settings_key", [
    ("application_update_choice", "check-for-application-updates"),
    ("card_data_update_choice", "check-for-card-data-updates")])
@pytest.mark.parametrize("value", range(3))
def test_first_start_wizard_accept_stores_settings(qtbot: QtBot, field: str, settings_key: str, value: int):
    wizard = create_widget(qtbot, fsw.FirstStartWizard)
    settings_value = fsw.COMBO_BOX_CHOICES[value][1]
    section = settings["application"]
    wizard.setField(field, value)
    with unittest.mock.patch.dict(
            section, {
                "check-for-application-updates": "None",
                "check-for-card-data-updates": "None",
            }):
        wizard.accept()
        assert_that(section, has_entry(settings_key, settings_value))


def test_card_database_page_download_request_button_emits_signal(qtbot: QtBot,):
    page = create_widget(qtbot, fsw.CardDBPage)
    assert_that(page.ui, is_(not_none()))
    assert_that(page.ui.download_card_data_button, is_(not_none()))
    with qtbot.waitSignal(page.card_data_download_requested):
        page.ui.download_card_data_button.click()


@pytest.mark.parametrize("combo_box_name", [
    "application_update_selection_combo_box", "card_data_update_selection_combo_box"
])
def test_update_check_page_combo_box_items_contain_expected_entries(qtbot: QtBot, combo_box_name: str):
    page = create_widget(qtbot, fsw.UpdateCheckPage)
    combo_box: QComboBox = getattr(page.ui, combo_box_name)
    assert_that(combo_box.model().rowCount(), is_(len(fsw.COMBO_BOX_CHOICES)))
    for index in range(len(fsw.COMBO_BOX_CHOICES)):
        assert_that(combo_box.itemData(index, Qt.DisplayRole), is_(fsw.COMBO_BOX_CHOICES[index][0]))
        assert_that(combo_box.itemData(index, Qt.UserRole), is_(fsw.COMBO_BOX_CHOICES[index][1]))


@pytest.mark.parametrize("combo_box_name, field_name", [
    ("application_update_selection_combo_box", "application_update_choice"),
    ("card_data_update_selection_combo_box", "card_data_update_choice"),
])
@pytest.mark.parametrize("choice", range(3))
def test_update_check_page__changing_combobox_entry_updates_associated_field(
        qtbot: QtBot, choice: int,
        combo_box_name: str, field_name: str):
    wizard = create_widget(qtbot, fsw.FirstStartWizard)
    wizard.next()
    wizard.next()
    page: fsw.UpdateCheckPage = wizard.currentPage()
    assert_that(page, is_(instance_of(fsw.UpdateCheckPage)))
    combo_box: QComboBox = getattr(page.ui, combo_box_name)
    combo_box.setCurrentIndex(choice)
    assert_that(
        page.field(field_name),
        is_(equal_to(choice))
    )
