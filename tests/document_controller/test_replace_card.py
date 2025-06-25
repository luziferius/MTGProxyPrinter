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
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.document_controller.card_actions import ActionAddCard, ActionRemoveCards
from mtg_proxy_printer.document_controller.replace_card import ActionReplaceCard
from mtg_proxy_printer.model.document_page import CardContainer
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.units_and_sizes import PageType, CardSizes

from .helpers import card_container_with, create_card, append_new_card_in_page, append_new_pages


REGULAR = CardSizes.REGULAR
OVERSIZED = CardSizes.OVERSIZED


def test_replacing_regular_with_oversized_on_otherwise_filled_card_moves_oversized_away(
        qtbot: QtBot, document_light: Document):
    append_new_pages(document_light, 1)
    pages = document_light.pages
    to_replace = append_new_card_in_page(pages[0], "Normal 1", REGULAR)
    stay_on_0 = append_new_card_in_page(pages[0], "Normal 2", REGULAR)
    stay_on_1 = append_new_card_in_page(pages[1], "Oversized", OVERSIZED)
    replacement = create_card("Replacement", OVERSIZED)
    action = ActionReplaceCard(replacement, 0, 0)
    with qtbot.assert_not_emitted(document_light.page_type_changed):
        assert_that(action.apply(document_light), is_(same_instance(action)))
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(stay_on_0, pages[0]),
            ),
            contains_exactly(
                card_container_with(stay_on_1, pages[1]),
                card_container_with(replacement, pages[1]),
            ),
        )
    )
    assert_that(action.old_card, is_(to_replace))
    assert_that(
        action.size_change_actions,
        contains_exactly(
            all_of(
                instance_of(ActionRemoveCards),
                has_properties({
                    "card_ranges_to_remove": contains_exactly(contains_exactly(0, 0)),
                    "page_number": 0,
                    "removed_cards": contains_exactly(contains_exactly(card_container_with(to_replace, pages[0]))),
                }),
            ),
            all_of(
                instance_of(ActionAddCard),
                has_properties({
                    "card": replacement,
                    "count": 1,
                    "added_new_pages": 0,
                    "added_cards_to_existing_pages": contains_exactly(contains_exactly(1, 1)),
                }),
            ),
        )
    )
    assert_that(pages[0].page_type(), is_(PageType.REGULAR))
    assert_that(pages[1].page_type(), is_(PageType.OVERSIZED))


def test_replacing_regular_with_oversized_on_otherwise_empty_page_keeps_card_on_same_page(
        qtbot: QtBot, document_light: Document):
    append_new_pages(document_light, 1)
    pages = document_light.pages
    to_replace = append_new_card_in_page(pages[0], "Normal 1", REGULAR)
    stay_on_1 = append_new_card_in_page(pages[1], "Oversized", OVERSIZED)
    replacement = create_card("Replacement", OVERSIZED)
    action = ActionReplaceCard(replacement, 0, 0)
    assert_that(pages[0].page_type(), is_(PageType.REGULAR), "Test setup failed")
    with qtbot.wait_signal(document_light.page_type_changed, timeout=1000,
                           check_params_cb=lambda index: index.row() == 0 and not index.parent().isValid()):
        assert_that(action.apply(document_light), is_(same_instance(action)))
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(replacement, pages[0]),
            ),
            contains_exactly(
                card_container_with(stay_on_1, pages[1]),
            )
        )
    )

    assert_that(action.old_card, is_(to_replace))
    assert_that(action.size_change_actions, is_(empty()))
    assert_that(pages[0].page_type(), is_(PageType.OVERSIZED))
    assert_that(pages[1].page_type(), is_(PageType.OVERSIZED))


def test_undo_replacing_regular_with_oversized_on_otherwise_filled_card_moves_card_back_to_original_page(
        qtbot: QtBot, document_light: Document):
    append_new_pages(document_light, 1)
    pages = document_light.pages
    original = create_card("Normal 1", REGULAR)
    stay_on_0 = append_new_card_in_page(pages[0], "Normal 2", REGULAR)
    stay_on_1 = append_new_card_in_page(pages[1], "Oversized", OVERSIZED)
    replacement = append_new_card_in_page(pages[1], "Replacement", OVERSIZED)
    action = ActionReplaceCard(replacement, 0, 0)
    action.old_card = original
    remove_action = ActionRemoveCards([0], 0)
    remove_action.removed_cards[:] = [[CardContainer(pages[0], original)]]
    add_action = ActionAddCard(replacement, 1)
    add_action.added_cards_to_existing_pages[:] = [(1, 1)]
    action.size_change_actions[:] = [remove_action, add_action]

    with qtbot.assert_not_emitted(document_light.page_type_changed):
        assert_that(action.undo(document_light), is_(same_instance(action)))

    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(original, pages[0]),
                card_container_with(stay_on_0, pages[0]),
            ),
            contains_exactly(
                card_container_with(stay_on_1, pages[1]),
            ),
        )
    )


def test_undo_replacing_regular_with_oversized_on_otherwise_empty_page_keeps_card_on_same_page(
        qtbot: QtBot, document_light: Document):
    append_new_pages(document_light, 1)
    pages = document_light.pages
    original = create_card("Normal 1", REGULAR)
    replacement = append_new_card_in_page(pages[0], "Replacement", OVERSIZED)
    stay_on_1 = append_new_card_in_page(pages[1], "Oversized", OVERSIZED)
    assert_that(pages[0].page_type(), is_(PageType.OVERSIZED), "Setup failed")
    assert_that(pages[1].page_type(), is_(PageType.OVERSIZED), "Setup failed")

    action = ActionReplaceCard(replacement, 0, 0)
    action.old_card = original

    with qtbot.wait_signal(document_light.page_type_changed, timeout=1000,
                           check_params_cb=lambda index: index.row() == 0 and not index.parent().isValid()):
        assert_that(action.undo(document_light), is_(same_instance(action)))
    assert_that(
        pages,
        contains_exactly(
            contains_exactly(
                card_container_with(original, pages[0]),
            ),
            contains_exactly(
                card_container_with(stay_on_1, pages[1]),
            )
        )
    )
    assert_that(pages[0].page_type(), is_(PageType.REGULAR))
    assert_that(pages[1].page_type(), is_(PageType.OVERSIZED))
