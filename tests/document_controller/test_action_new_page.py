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


from typing import List
from unittest.mock import MagicMock

from hamcrest import *
import pytest
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.model.card import Card, CardList
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.document_page import CardContainer, Page
from mtg_proxy_printer.document_controller import IllegalStateError
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage
from mtg_proxy_printer.units_and_sizes import CardSizes

from .helpers import append_new_card_in_page, card_container_with, append_new_pages, verify_page_index_cache_is_valid, \
    create_card

OVERSIZED = CardSizes.OVERSIZED


def insert_mock_in_page(page: Page, count: int = 1):
    """
    Inserts the given amount of mock cards into the given page to make it distinguishable from other pages.
    """
    for _ in range(count):
        page.append(MagicMock(spec=Card))


@pytest.mark.parametrize("count", [-10, -1, 0])
def test_init_with_non_positive_count_raises_exception(count: int):
    assert_that(calling(ActionNewPage).with_args(count=count), raises(ValueError))


@pytest.mark.parametrize("count, content", [
    (1, [[], []]),
    (3, [[], []]),
    (2, [[]]),
    (2, [[], [], []]),
])
def test_init_with_content_length_unequal_count_raises_exception(
        document_light: Document, count: int, content: List[CardList]):
    assert_that(calling(ActionNewPage).with_args(count=count, content=content), raises(ValueError))


@pytest.mark.parametrize("count", range(1, 4))
def test_init_initializes_length_content_to_count_if_not_given(count: int):
    action = ActionNewPage(count=count)
    assert_that(
        action.content,
        all_of(
        has_length(count),
            only_contains(empty())
    ))


@pytest.mark.parametrize("content", [
    [[create_card("P1")], [], [create_card("P3-1", OVERSIZED), create_card("P3-2")]],
    [[create_card("P1", OVERSIZED)], [], [create_card("P3-1"), create_card("P3-2", OVERSIZED)]],
])
def test_init_with_content_rejects_creating_mixed_size_pages(content: List[CardList]):
    assert_that(calling(ActionNewPage).with_args(count=len(content), content=content), raises(ValueError))


def test_apply_without_position_appends_new_page(qtbot: QtBot, document_light: Document):
    pages = document_light.pages
    card = append_new_card_in_page(pages[0], "Card")
    action = ActionNewPage()
    with qtbot.wait_signal(document_light.rowsAboutToBeInserted), qtbot.wait_signal(document_light.rowsInserted):
        assert_that(action.apply(document_light), is_(same_instance(action)))
    assert_that(
        pages,
        contains_exactly(
            all_of(instance_of(Page), contains_exactly(card_container_with(card, pages[0]))),
            all_of(instance_of(Page), is_(empty())),
        ),
        "Page not appended correctly"
    )
    verify_page_index_cache_is_valid(document_light)


@pytest.mark.parametrize("count", [1, 3])
def test_apply_without_position_appends_count_new_pages(qtbot: QtBot, document_light: Document, count: int):
    pages = document_light.pages
    card = append_new_card_in_page(pages[0], "Card")
    action = ActionNewPage(count=count)
    with qtbot.wait_signal(document_light.rowsAboutToBeInserted), qtbot.wait_signal(document_light.rowsInserted):
        assert_that(action.apply(document_light), is_(same_instance(action)))
    assert_that(
        pages,
        contains_exactly(
            all_of(instance_of(Page), contains_exactly(card_container_with(card, pages[0]))),
            *[all_of(instance_of(Page), is_(empty()))]*count,
        ),
        "Page not appended correctly"
    )
    verify_page_index_cache_is_valid(document_light)


def test_apply_with_position_inserts_new_page_at_the_given_position(qtbot: QtBot, document_light: Document):
    append_new_pages(document_light, 1)
    insert_mock_in_page(document_light.pages[0], 2)
    insert_mock_in_page(document_light.pages[1], 1)
    action = ActionNewPage(1)
    with qtbot.wait_signal(document_light.rowsAboutToBeInserted), qtbot.wait_signal(document_light.rowsInserted):
        assert_that(action.apply(document_light), is_(same_instance(action)))
    assert_that(
        document_light.pages,
        contains_exactly(
            all_of(instance_of(Page), contains_exactly(*[instance_of(CardContainer)]*2)),
            all_of(instance_of(Page), is_(empty())),
            all_of(instance_of(Page), contains_exactly(instance_of(CardContainer))),
        ),
        "Page not inserted at the specified position"
    )
    verify_page_index_cache_is_valid(document_light)


@pytest.mark.parametrize("count", [1, 3])
def test_apply_with_position_inserts_count_new_pages_at_the_given_position(
        qtbot: QtBot, document_light: Document, count: int):
    append_new_pages(document_light, 1)
    insert_mock_in_page(document_light.pages[0], 2)
    insert_mock_in_page(document_light.pages[1], 1)
    action = ActionNewPage(1, count=count)
    with qtbot.wait_signal(document_light.rowsAboutToBeInserted), qtbot.wait_signal(document_light.rowsInserted):
        assert_that(action.apply(document_light), is_(same_instance(action)))
    assert_that(document_light.pages, only_contains(instance_of(Page)))
    assert_that(
        document_light.pages,
        contains_exactly(
            contains_exactly(*[instance_of(CardContainer)]*2),
            *[is_(empty())]*count,
            contains_exactly(instance_of(CardContainer)),
        ),
        "Page not inserted at the specified position"
    )
    verify_page_index_cache_is_valid(document_light)


@pytest.mark.parametrize("content", [
    [[create_card("P1")], [], [create_card("P3-1"), create_card("P3-2")]],
    [[create_card("P1", OVERSIZED)], [], [create_card("P3-1"), create_card("P3-2")]],
    [[create_card("P1")], [], [create_card("P3-1", OVERSIZED), create_card("P3-2", OVERSIZED)]],
])
def test_apply_with_content_populates_created_pages(qtbot: QtBot, document_light: Document, content: List[CardList]):
    action = ActionNewPage(count=len(content), content=content)
    with qtbot.wait_signal(document_light.rowsAboutToBeInserted), qtbot.wait_signal(document_light.rowsInserted):
        assert_that(action.apply(document_light), is_(same_instance(action)))
    assert_that(document_light.pages, only_contains(instance_of(Page)))
    assert_that(
        document_light.pages,
        contains_exactly(
            empty(),
            contains_exactly(
                card_container_with(content[0][0], document_light.pages[1])),
            empty(),
            contains_exactly(
                card_container_with(content[2][0], document_light.pages[3]),
                card_container_with(content[2][1], document_light.pages[3])),
        )
    )


def test_undo_without_position_raises_exception(document_light):
    document_light.pages.append(Page())
    insert_mock_in_page(document_light.pages[0])
    action = ActionNewPage()
    assert_that(calling(action.undo).with_args(document_light), raises(IllegalStateError))


def test_undo_with_position_removes_inserted_page(qtbot: QtBot, document_light: Document):
    append_new_pages(document_light, 2)
    insert_mock_in_page(document_light.pages[0])
    insert_mock_in_page(document_light.pages[2])
    action = ActionNewPage(1)
    with qtbot.wait_signal(document_light.rowsAboutToBeRemoved), qtbot.wait_signal(document_light.rowsRemoved):
        assert_that(action.undo(document_light), is_(same_instance(action)))
    assert_that(
        document_light.pages,
        contains_exactly(
            all_of(instance_of(Page), contains_exactly(instance_of(CardContainer))),
            all_of(instance_of(Page), contains_exactly(instance_of(CardContainer))),
        )
    )
    verify_page_index_cache_is_valid(document_light)


def test_undo_removes_count_pages(qtbot: QtBot, document_light: Document):
    append_new_pages(document_light, 3)
    insert_mock_in_page(document_light.pages[0])
    insert_mock_in_page(document_light.pages[3])
    action = ActionNewPage(1, count=2)
    with qtbot.wait_signal(document_light.rowsAboutToBeRemoved), qtbot.wait_signal(document_light.rowsRemoved):
        assert_that(action.undo(document_light), is_(same_instance(action)))
    assert_that(
        document_light.pages,
        contains_exactly(
            all_of(instance_of(Page), contains_exactly(instance_of(CardContainer))),
            all_of(instance_of(Page), contains_exactly(instance_of(CardContainer))),
        )
    )
    verify_page_index_cache_is_valid(document_light)
