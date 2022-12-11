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

from unittest.mock import MagicMock

from hamcrest import *
import pytest

from mtg_proxy_printer.model.document import Page, CardContainer, Card
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage, IllegalStateError


def insert_mock_in_page(page: Page, count: int = 1):
    """
    Inserts the given amount of mock cards into the given page to make it distinguishable from other pages.
    """
    for _ in range(count):
        page.append(CardContainer(page, MagicMock(spec=Card)))


def verify_page_index_cache_is_valid(document_light):
    expected_index = {id(page): index for index, page in enumerate(document_light.pages)}
    assert_that(
        document_light.page_index_cache,
        is_(equal_to(expected_index)),
        "Index of page id to page number not updated properly"
    )


def append_new_pages(document, count: int):
    for _ in range(count):
        document.pages.append(Page())
    document.recreate_page_index_cache()
        

def test_apply_without_position_appends_new_page(qtbot, document_light):
    insert_mock_in_page(document_light.pages[0])
    action = ActionNewPage()
    with qtbot.wait_signal(document_light.rowsAboutToBeInserted), qtbot.wait_signal(document_light.rowsInserted):
        assert_that(action.apply(document_light), is_(same_instance(action)))
    assert_that(
        document_light.pages,
        contains_exactly(
            all_of(instance_of(Page), contains_exactly(instance_of(CardContainer))),
            all_of(instance_of(Page), is_(empty())),
        ),
        "Page not appended correctly"
    )
    verify_page_index_cache_is_valid(document_light)


@pytest.mark.parametrize("count", [1, 3])
def test_apply_without_position_appends_count_new_pages(qtbot, document_light, count):
    insert_mock_in_page(document_light.pages[0])
    action = ActionNewPage(count=count)
    with qtbot.wait_signal(document_light.rowsAboutToBeInserted), qtbot.wait_signal(document_light.rowsInserted):
        assert_that(action.apply(document_light), is_(same_instance(action)))
    assert_that(
        document_light.pages,
        contains_exactly(
            all_of(instance_of(Page), contains_exactly(instance_of(CardContainer))),
            *[all_of(instance_of(Page), is_(empty()))]*count,
        ),
        "Page not appended correctly"
    )
    verify_page_index_cache_is_valid(document_light)


def test_apply_with_position_inserts_new_page_at_the_given_position(qtbot, document_light):
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
def test_apply_with_position_inserts_count_new_pages_at_the_given_position(qtbot, document_light, count: int):
    append_new_pages(document_light, 1)
    insert_mock_in_page(document_light.pages[0], 2)
    insert_mock_in_page(document_light.pages[1], 1)
    action = ActionNewPage(1, count=count)
    with qtbot.wait_signal(document_light.rowsAboutToBeInserted), qtbot.wait_signal(document_light.rowsInserted):
        assert_that(action.apply(document_light), is_(same_instance(action)))
    assert_that(
        document_light.pages,
        contains_exactly(
            all_of(instance_of(Page), contains_exactly(*[instance_of(CardContainer)]*2)),
            *[all_of(instance_of(Page), is_(empty()))]*count,
            all_of(instance_of(Page), contains_exactly(instance_of(CardContainer))),
        ),
        "Page not inserted at the specified position"
    )
    verify_page_index_cache_is_valid(document_light)


def test_undo_without_position_raises_exception(document_light):
    document_light.pages.append(Page())
    insert_mock_in_page(document_light.pages[0])
    action = ActionNewPage()
    assert_that(calling(action.undo).with_args(document_light), raises(IllegalStateError))


def test_undo_with_position_removes_inserted_page(qtbot, document_light):
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


def test_undo_removes_count_pages(qtbot, document_light):
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
