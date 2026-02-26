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


import copy
import itertools
from unittest.mock import patch

import pytest
from hamcrest import *
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.units_and_sizes import PageType, unit_registry, CardSizes
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard
from mtg_proxy_printer.document_controller.move_cards import ActionMoveCards
from mtg_proxy_printer.document_controller.edit_document_settings import ActionEditDocumentSettings

from .helpers import create_card, card_container_with, append_new_card_in_page


def test_create_action_raises_value_error_on_zero_page_capacity():
    assert_that(calling(ActionEditDocumentSettings).with_args(PageLayoutSettings()), raises(ValueError))


def test_apply_emits_settings_changed_signal(qtbot: QtBot, document_light: Document):
    old_settings = copy.copy(document_light.page_layout)
    new_settings = copy.copy(document_light.page_layout)
    new_settings.page_height += 1*unit_registry.mm  # Ensure that the new settings differ from the previous ones
    action = ActionEditDocumentSettings(copy.copy(new_settings))
    with patch(
            "mtg_proxy_printer.document_controller.edit_document_settings.ActionEditDocumentSettings._reflow_document"
            ) as reflow_mock, qtbot.wait_signals([document_light.page_layout_changed], timeout=1000):
        action.apply(document_light)
        reflow_mock.assert_not_called()
    assert_that(action.old_settings, is_(equal_to(old_settings)))
    assert_that(action.new_settings, is_(equal_to(new_settings)))
    assert_that(document_light.page_layout, is_(equal_to(new_settings)))


@pytest.mark.parametrize("initial_row_spacing, new_row_spacing", [
    (0, 15),  # Regular cards overflow, oversized do not
    (10, 25),  # Oversized cards overflow, regular do not
    (0, 30),  # Both sizes overflow
])
def test_page_capacity_reduction_reflows_document(
        qtbot: QtBot, document_light: Document, initial_row_spacing: int, new_row_spacing: int):
    document_light.page_layout.row_spacing = initial_row_spacing*unit_registry.mm
    initial_capacity = (document_light.page_layout.compute_page_card_capacity(PageType.REGULAR),
                        document_light.page_layout.compute_page_card_capacity(PageType.OVERSIZED))
    new_settings = copy.copy(document_light.page_layout)
    new_settings.row_spacing = new_row_spacing*unit_registry.mm
    new_capacity = (new_settings.compute_page_card_capacity(PageType.REGULAR),
                    new_settings.compute_page_card_capacity(PageType.OVERSIZED))
    assert_that(new_capacity, is_(less_than(initial_capacity)), "Setup failed, capacity not decreased")
    action = ActionEditDocumentSettings(copy.copy(new_settings))
    with patch(
            "mtg_proxy_printer.document_controller.edit_document_settings.ActionEditDocumentSettings._reflow_document"
            ) as reflow_mock, qtbot.wait_signals([document_light.page_layout_changed], timeout=1000):
        action.apply(document_light)
        reflow_mock.assert_called_once()


@pytest.mark.parametrize("initial_row_spacing, new_row_spacing", [
    (0, 10),  # Regular cards overflow, oversized do not
    (10, 25),  # Oversized cards overflow, regular do not
    (0, 30),  # Both sizes overflow
])
def test_reflow_keeps_total_card_order(
        document_light: Document, initial_row_spacing: int, new_row_spacing: int):
    document_light.page_layout.row_spacing = initial_row_spacing*unit_registry.mm
    ActionNewPage(count=2).apply(document_light)
    names = []
    for num in range(document_light.page_layout.compute_page_card_capacity(PageType.REGULAR)):
        names.append(name := f"A{num+1}")
        append_new_card_in_page(document_light.pages[0], name, CardSizes.REGULAR)
    for num in range(document_light.page_layout.compute_page_card_capacity(PageType.OVERSIZED)):
        names.append(name := f"B{num+1}")
        append_new_card_in_page(document_light.pages[1], name, CardSizes.OVERSIZED)
    for num in range(document_light.page_layout.compute_page_card_capacity(PageType.REGULAR)):
        names.append(name := f"C{num+1}")
        append_new_card_in_page(document_light.pages[2], name, CardSizes.REGULAR)
    new_settings = copy.copy(document_light.page_layout)
    new_settings.row_spacing = new_row_spacing*unit_registry.mm
    action = ActionEditDocumentSettings(copy.copy(new_settings))
    action.apply(document_light)
    names_after_action = [c.card.name for c in itertools.chain.from_iterable(document_light.pages)]
    assert_that(
        names_after_action, contains_exactly(*names), f"Order not kept: {names_after_action}"
    )
    for index, page in enumerate(document_light.pages):
        assert_that(
            page.page_type(),
            is_in((PageType.REGULAR, PageType.OVERSIZED)),
            f"Page {index} has unexpected page type")


def test_reflow_moves_card_on_later_page(document_light: Document):
    assert_that(document_light.page_layout.compute_page_card_capacity(PageType.REGULAR), is_(9), "Test setup failed")

    ActionNewPage().apply(document_light)
    ActionAddCard(create_card("Stays on 0"), 6).apply(document_light)
    ActionAddCard(create_card("Moves to 1"), 3).apply(document_light)
    assert_that(document_light.pages[0], has_length(9), "Test setup failed")
    stay_on_0 = document_light.pages[0][:6]
    move_to_1 = document_light.pages[0][6:]
    assert_that(stay_on_0, has_length(6), "Test setup failed")
    assert_that(move_to_1, has_length(3), "Test setup failed")

    new_layout = copy.copy(document_light.page_layout)
    new_layout.row_spacing = 30*unit_registry.mm
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


def test_reflow_does_not_append_empty_pages(qtbot: QtBot, document_light: Document):
    """The issue of trailing empty pages was discovered on a document with at least four full pages"""
    pages = document_light.pages
    ActionAddCard((card_inserted := create_card("Card")), 4*9).apply(document_light)
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(*[card_container_with(card_inserted, pages[0])]*9),
            contains_exactly(*[card_container_with(card_inserted, pages[1])]*9),
            contains_exactly(*[card_container_with(card_inserted, pages[2])]*9),
            contains_exactly(*[card_container_with(card_inserted, pages[3])]*9),
        )
    )

    new_layout = copy.copy(document_light.page_layout)
    new_layout.row_spacing = 30*unit_registry.mm

    action = ActionEditDocumentSettings(new_layout)
    action.apply(document_light)

    assert_that(pages, has_length(6), f"Unexpected length: {len(pages)}")
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(*[card_container_with(card_inserted, pages[0])]*6),
            contains_exactly(*[card_container_with(card_inserted, pages[1])]*6),
            contains_exactly(*[card_container_with(card_inserted, pages[2])]*6),
            contains_exactly(*[card_container_with(card_inserted, pages[3])]*6),
            contains_exactly(*[card_container_with(card_inserted, pages[4])]*6),
            contains_exactly(*[card_container_with(card_inserted, pages[5])]*6),
        )
    )


def test_undo_restores_old_page_layout(qtbot: QtBot, document_light: Document):
    # Alter the settings and store that in the action as the new settings, while keeping a backup in the old_settings
    # undo() should then restore the old values
    old_settings = copy.copy(document_light.page_layout)
    document_light.page_layout.page_height += 1*unit_registry.mm
    new_settings = copy.copy(document_light.page_layout)

    action = ActionEditDocumentSettings(new_settings)
    action.old_settings = old_settings

    with patch(
            "mtg_proxy_printer.document_controller.edit_document_settings.ActionEditDocumentSettings._reflow_document"
            ) as reflow_mock, qtbot.wait_signals([document_light.page_layout_changed], timeout=1000):
        action.undo(document_light)
    reflow_mock.assert_not_called()
    assert_that(document_light.page_layout, is_(equal_to(old_settings)))
    assert_that(action.reflow_actions, is_(empty()))
    assert_that(action.old_settings, is_(none()))


def test_undo_restores_old_page_content(qtbot: QtBot, document_light: Document):
    pages = document_light.pages
    new_page = ActionNewPage(1).apply(document_light)
    ActionAddCard((card_1 := create_card("Stays on 0")), 6).apply(document_light)
    document_light.set_currently_edited_page(pages[1])
    ActionAddCard((card_2 := create_card("Moves to 0")), 3).apply(document_light)

    action = ActionEditDocumentSettings(document_light.page_layout)
    old_settings = action.old_settings = copy.copy(document_light.page_layout)
    document_light.page_layout.page_height += 1*unit_registry.mm
    action.reflow_actions += [
        new_page,
        ActionMoveCards(0, range(7, 10), 1)
    ]
    action.new_settings = document_light.page_layout

    with qtbot.wait_signals([document_light.page_layout_changed]):
        action.undo(document_light)

    assert_that(document_light.page_layout, is_(equal_to(old_settings)))
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                *[card_container_with(card_1, pages[0])]*6,
                *[card_container_with(card_2, pages[0])]*3
            )
        )
    )
    assert_that(action.reflow_actions, is_(empty()))
    assert_that(action.old_settings, is_(none()))
