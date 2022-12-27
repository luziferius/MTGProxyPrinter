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

import copy
import functools
from unittest.mock import patch

import pytest
from hamcrest import *

from mtg_proxy_printer.model.carddb import Card, MTGSet
from mtg_proxy_printer.units_and_sizes import PageType
from mtg_proxy_printer.model.document_loader import PageLayoutSettings
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard
from mtg_proxy_printer.document_controller.move_cards import ActionMoveCards
from mtg_proxy_printer.document_controller.edit_document_settings import ActionEditDocumentSettings

card_container_with = functools.partial(has_property, "card")


def card(name: str, oversized: bool = False):
    return Card(name, MTGSet("", ""), "", "", "", True, "", "", True, oversized, 0, None)


def test_create_action_raises_value_error_on_zero_page_capacity():
    assert_that(calling(ActionEditDocumentSettings).with_args(PageLayoutSettings()), raises(ValueError))


def test_apply_emits_settings_changed_signal(qtbot, document_light):
    old_settings = copy.copy(document_light.page_layout)
    new_settings = copy.copy(document_light.page_layout)
    new_settings.page_height += 1  # Ensure that the new settings differ from the previous ones
    action = ActionEditDocumentSettings(copy.copy(new_settings))
    with patch(
            "mtg_proxy_printer.document_controller.edit_document_settings.ActionEditDocumentSettings._reflow_document"
            ) as reflow_mock, qtbot.wait_signals([document_light.page_layout_changed], timeout=100):
        action.apply(document_light)
        reflow_mock.assert_not_called()
    assert_that(action.old_settings, is_(equal_to(old_settings)))
    assert_that(action.new_settings, is_(equal_to(new_settings)))
    assert_that(document_light.page_layout, is_(equal_to(new_settings)))


@pytest.mark.parametrize("initial_h_spacing, new_h_spacing", [
    (0, 10),  # Regular cards overflow, oversized do not
    (10, 25),  # Oversized cards overflow, regular do not
    (0, 30),  # Both sizes overflow
])
def test_page_capacity_reduction_reflows_document(qtbot, document_light, initial_h_spacing: int, new_h_spacing: int):
    document_light.page_layout.image_spacing_horizontal = initial_h_spacing
    new_settings = copy.copy(document_light.page_layout)
    new_settings.image_spacing_horizontal = new_h_spacing
    action = ActionEditDocumentSettings(copy.copy(new_settings))
    with patch(
            "mtg_proxy_printer.document_controller.edit_document_settings.ActionEditDocumentSettings._reflow_document"
            ) as reflow_mock, qtbot.wait_signals([document_light.page_layout_changed], timeout=100):
        action.apply(document_light)
        reflow_mock.assert_called_once()


def test_reflow_moves_card_on_later_page(qtbot, document_light):
    assert_that(document_light.page_layout.compute_page_card_capacity(PageType.REGULAR), is_(9), "Test setup failed")

    ActionNewPage().apply(document_light)
    ActionAddCard(card("Stays on 0"), 6).apply(document_light)
    ActionAddCard(card("Moves to 1"), 3).apply(document_light)
    assert_that(document_light.pages[0], has_length(9), "Test setup failed")
    stay_on_0 = document_light.pages[0][:6]
    move_to_1 = document_light.pages[0][6:]
    assert_that(stay_on_0, has_length(6), "Test setup failed")
    assert_that(move_to_1, has_length(3), "Test setup failed")

    new_layout = copy.copy(document_light.page_layout)
    new_layout.image_spacing_horizontal = 30
    assert_that(new_layout.compute_page_card_capacity(PageType.REGULAR), is_(6), "Test setup failed")

    action = ActionEditDocumentSettings(new_layout)
    action.apply(document_light)
    assert_that(
        document_light.pages,
        contains_exactly(
            contains_exactly(*stay_on_0),
            contains_exactly(*move_to_1),
        ),
        "Reflow failed"
    )


def test_reflow_moves_card_on_later_page_stepping_over_different_card_size_page(qtbot, document_light):
    ActionNewPage(count=2).apply(document_light)
    ActionAddCard(card("Stays on 0"), 6).apply(document_light)
    ActionAddCard(card("Moves to 2"), 3).apply(document_light)
    document_light._set_currently_edited_page(document_light.pages[1])
    ActionAddCard(card("Stays on 1", oversized=True)).apply(document_light)

    stay_on_0 = document_light.pages[0][:6]
    stay_on_1 = document_light.pages[1][:]
    move_to_2 = document_light.pages[0][6:]

    new_layout = copy.copy(document_light.page_layout)
    new_layout.image_spacing_horizontal = 30

    action = ActionEditDocumentSettings(new_layout)
    action.apply(document_light)
    assert_that(
        document_light.pages,
        contains_exactly(
            contains_exactly(*stay_on_0),
            contains_exactly(*stay_on_1),
            contains_exactly(*move_to_2),
        ),
        "Reflow failed"
    )


def test_reflow_appends_new_page_if_required(qtbot, document_light):
    ActionAddCard(card("Stays on 0"), 6).apply(document_light)
    ActionAddCard(card("Moves to 1"), 3).apply(document_light)
    stay_on_0 = document_light.pages[0][:6]
    move_to_1 = document_light.pages[0][6:]

    new_layout = copy.copy(document_light.page_layout)
    new_layout.image_spacing_horizontal = 30

    action = ActionEditDocumentSettings(new_layout)
    action.apply(document_light)
    assert_that(
        document_light.pages,
        contains_exactly(
            contains_exactly(*stay_on_0),
            contains_exactly(*move_to_1),
        ),
        "Reflow failed"
    )


def test_reflow_does_not_append_empty_pages(qtbot, document_light):
    """The issue of trailing empty pages was discovered on a document with at least four full pages"""
    ActionAddCard((card_inserted := card("Card")), 4*9).apply(document_light)
    assert_that(
        document_light.pages,
        contains_exactly(
            *[contains_exactly(*[card_container_with(card_inserted)]*9)]*4
        )
    )

    new_layout = copy.copy(document_light.page_layout)
    new_layout.image_spacing_horizontal = 30

    action = ActionEditDocumentSettings(new_layout)
    action.apply(document_light)

    assert_that(document_light.pages, has_length(6), f"Unexpected length: {len(document_light.pages)}")
    assert_that(
        document_light.pages,
        contains_exactly(
            *[contains_exactly(*[card_container_with(card_inserted)]*6)]*6
        )
    )


def test_undo_restores_old_page_layout(qtbot, document_light):
    # Alter the settings and store that in the action as the new settings, while keeping a backup in the old_settings
    # undo() should then restore the old values
    old_settings = copy.copy(document_light.page_layout)
    document_light.page_layout.page_height += 1
    new_settings = copy.copy(document_light.page_layout)

    action = ActionEditDocumentSettings(new_settings)
    action.old_settings = old_settings

    with patch(
            "mtg_proxy_printer.document_controller.edit_document_settings.ActionEditDocumentSettings._reflow_document"
            ) as reflow_mock, qtbot.wait_signals([document_light.page_layout_changed], timeout=100):
        action.undo(document_light)
    reflow_mock.assert_not_called()
    assert_that(document_light.page_layout, is_(equal_to(old_settings)))
    assert_that(action.reflow_actions, is_(empty()))
    assert_that(action.old_settings, is_(none()))


def test_undo_restores_old_page_content(qtbot, document_light):
    new_page = ActionNewPage(1).apply(document_light)
    ActionAddCard((card_1 := card("Stays on 0")), 6).apply(document_light)
    document_light._set_currently_edited_page(document_light.pages[1])
    ActionAddCard((card_2 := card("Moves to 0")), 3).apply(document_light)

    action = ActionEditDocumentSettings(document_light.page_layout)
    old_settings = action.old_settings = copy.copy(document_light.page_layout)
    document_light.page_layout.page_height += 1
    action.reflow_actions += [
        new_page,
        ActionMoveCards(0, range(7, 10), 1)
    ]

    with qtbot.wait_signals([document_light.page_layout_changed]):
        action.undo(document_light)

    assert_that(document_light.page_layout, is_(equal_to(old_settings)))
    assert_that(
        document_light.pages,
        contains_exactly(
            contains_exactly(*[card_container_with(card_1)]*6 + [card_container_with(card_2)]*3)
        )
    )
    assert_that(action.reflow_actions, is_(empty()))
    assert_that(action.old_settings, is_(none()))