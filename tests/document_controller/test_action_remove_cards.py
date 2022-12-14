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

import unittest.mock

import pytest
from hamcrest import *

from mtg_proxy_printer.model.carddb import Card, MTGSet
from mtg_proxy_printer.model.document_page import CardContainer, Page
from mtg_proxy_printer.document_controller import IllegalStateError, DocumentAction
from mtg_proxy_printer.document_controller.card_actions import ActionRemoveCards

from .test_action_new_page import append_new_pages


def create_card_in_container(page: Page, name: str):
    return CardContainer(
        page,
        Card(name, MTGSet("", ""), "", "", "", True, "", "", True, False, 0, None)
    )


def test___init___raises_exception_with_epty_cards_to_remove_parameter():
    assert_that(calling(ActionRemoveCards).with_args([]), raises(ValueError))


@pytest.mark.parametrize("sequence, expected", [
    ([1], [(1, 1)]),
    ([1, 2], [(1, 2)]),
    ([1, 2, 3], [(1, 3)]),
    ([1, 3], [(1, 1), (3, 3)]),
    ([1, 3, 4], [(1, 1), (3, 4)]),
])
def test___init___correctly_converts_index_list_to_ranges_list(sequence, expected):
    action = ActionRemoveCards(sequence)
    assert_that(action.card_ranges_to_remove, is_(equal_to(expected)))


def test_apply_removes_two_1_card_ranges(qtbot, document_light):
    page = document_light.pages[0]
    page.append(create_card_in_container(page, "Removed 1"))
    page.append(create_card_in_container(page, "Remaining"))
    page.append(create_card_in_container(page, "Removed 2"))
    action = ActionRemoveCards([0, 2])
    with qtbot.wait_signals([document_light.rowsAboutToBeRemoved, document_light.rowsRemoved], timeout=100):
        assert_that(action.apply(document_light), is_(instance_of(DocumentAction)))
    assert_that(
        page,
        contains_exactly(
            has_properties({
                "parent": equal_to(page),
                "card": has_property("name", equal_to("Remaining")),
            })
        )
    )
    assert_that(
        action.removed_cards,
        contains_exactly(
            contains_exactly(
                has_properties({
                    "parent": equal_to(page),
                    "card": has_property("name", equal_to("Removed 1")),
                })
            ),
            contains_exactly(
                has_properties({
                    "parent": equal_to(page),
                    "card": has_property("name", equal_to("Removed 2")),
                })
            ),
        )
    )


def test_apply_removes_one_2_card_range(qtbot, document_light):
    page = document_light.pages[0]
    page.append(create_card_in_container(page, "Removed 1"))
    page.append(create_card_in_container(page, "Removed 2"))
    page.append(create_card_in_container(page, "Remaining"))
    action = ActionRemoveCards([0, 1])
    with qtbot.wait_signals([document_light.rowsAboutToBeRemoved, document_light.rowsRemoved], timeout=100):
        assert_that(action.apply(document_light), is_(instance_of(DocumentAction)))
    assert_that(
        page,
        contains_exactly(
            has_properties({
                "parent": equal_to(page),
                "card": has_property("name", equal_to("Remaining")),
            })
        )
    )
    assert_that(
        action.removed_cards,
        contains_exactly(
            contains_exactly(
                has_properties({
                    "parent": equal_to(page),
                    "card": has_property("name", equal_to("Removed 1")),
                }),
                has_properties({
                    "parent": equal_to(page),
                    "card": has_property("name", equal_to("Removed 2")),
                })
            ),
        )
    )


def test_undo_restores_two_1_card_ranges(qtbot, document_light):
    page = document_light.pages[0]
    page.append(create_card_in_container(page, "Remaining"))
    action = ActionRemoveCards([0, 2], page_number=0)
    action.removed_cards.append([create_card_in_container(page, "Removed 1")])
    action.removed_cards.append([create_card_in_container(page, "Removed 2")])

    with qtbot.wait_signals([document_light.rowsAboutToBeInserted, document_light.rowsInserted], timeout=100):
        assert_that(action.undo(document_light), is_(instance_of(DocumentAction)))
    assert_that(
        page,
        contains_exactly(
            has_properties({
                "parent": equal_to(page),
                "card": has_property("name", equal_to("Removed 1")),
            }),
            has_properties({
                "parent": equal_to(page),
                "card": has_property("name", equal_to("Remaining")),
            }),
            has_properties({
                "parent": equal_to(page),
                "card": has_property("name", equal_to("Removed 2")),
            }),
        )
    )


def test_undo_restores_one_2_card_range(qtbot, document_light):
    page = document_light.pages[0]
    page.append(create_card_in_container(page, "Remaining"))
    action = ActionRemoveCards([0, 1], page_number=0)
    action.removed_cards.append(
        [create_card_in_container(page, "Removed 1"), create_card_in_container(page, "Removed 2")]
    )
    with qtbot.wait_signals([document_light.rowsAboutToBeInserted, document_light.rowsInserted], timeout=100):
        assert_that(action.undo(document_light), is_(instance_of(DocumentAction)))
    assert_that(
        page,
        contains_exactly(
            has_properties({
                "parent": equal_to(page),
                "card": has_property("name", equal_to("Removed 1")),
            }),
            has_properties({
                "parent": equal_to(page),
                "card": has_property("name", equal_to("Removed 2")),
            }),
            has_properties({
                "parent": equal_to(page),
                "card": has_property("name", equal_to("Remaining")),
            }),
        )
    )


def test_undo_without_page_index_raises_exception(qtbot, document_light):
    action = ActionRemoveCards([1])
    assert_that(calling(action.undo).with_args(document_light), raises(IllegalStateError))
