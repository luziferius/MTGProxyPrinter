# Copyright (C) 2021 Thomas Hess <thomas.hess@udo.edu>

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
import itertools
import time
from unittest.mock import MagicMock

from hamcrest import *
import pytest

from mtg_proxy_printer.model.carddb import CardDatabase, Card
from mtg_proxy_printer.model.document import Document, CardContainer

from .helpers import create_new_card_database_with_json_card


@pytest.fixture()
def card_db() -> CardDatabase:
    return create_new_card_database_with_json_card("regular_english_card")


def test_document_two_overflow_events_only_add_one_new_page(card_db: CardDatabase):
    card = card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    document = Document(card_db, MagicMock())
    document.add_card(card, document.total_cards_per_page)
    assert_that(document.rowCount(), is_(equal_to(1)))
    for _ in range(document.total_cards_per_page):
        document.add_card(card, 1)
        assert_that(document.pages, has_length(2), "Unexpected page break occurred")


def test_clear_database_not_clearing_last_image_use_timestamps(card_db: CardDatabase):
    card = card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    document = Document(card_db, MagicMock())
    # Add two copies. Should only count as one usage
    document.add_card(card, 2)
    document.store_image_usage()
    usages = card_db.db.execute(
        "SELECT scryfall_id, is_front, usage_count, CAST(strftime('%s', last_use_date) AS INT) "
        "FROM LastImageUseTimestamps").fetchall()
    end = int(time.time())
    assert_that(
        usages,
        contains_exactly(
            contains_exactly("0000579f-7b35-4ed3-b44c-db2a538066fe", True, 1, close_to(end, 1)))
    )


def test_document_is_created_empty(card_db: CardDatabase):
    document = Document(card_db, MagicMock())
    assert_that(document.compute_page_card_capacity(), is_(greater_than_or_equal_to(1)))
    assert_that(document.total_cards_per_page, is_(equal_to(document.compute_page_card_capacity())))
    assert_that(document.rowCount(), is_(equal_to(1)), "Expected creation of a single, empty page.")
    assert_that(document.pages, has_length(1), "Expected creation of a single, empty page.")
    assert_that(document.rowCount(document.index(0, 0)), is_(equal_to(0)), "Expected empty page, but it is not empty")
    assert_that(document.pages[0], is_(empty()), "Expected empty page, but it is not empty")


@pytest.mark.parametrize("pages_to_fill", range(1, 5))
def test_add_card_and_rowCount(card_db: CardDatabase, pages_to_fill: int):
    card = card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    document = Document(card_db, MagicMock())
    document.add_card(card, pages_to_fill*document.total_cards_per_page)
    assert_that(
        document.pages,
        has_length(pages_to_fill),
        "Unexpected page count"
    )
    assert_that(document.rowCount(), is_(equal_to(pages_to_fill)))
    for page_row, page in enumerate(document.pages):
        assert_that(
            page,
            has_length(document.total_cards_per_page),
            "Unexpected number of cards in page."
        )
        assert_that(document.index(page_row, 0).isValid(), is_(True))
        assert_that(
            document.index(page_row, 0).internalPointer(),
            is_(page),
            "Root element internal pointer not referring the page data list."
        )
        assert_that(
            document.rowCount(document.index(page_row, 0)),
            is_(equal_to(document.total_cards_per_page)),
            f"rowCount() of parent index at row {page_row} wrong."
        )
        for card_index in range(document.total_cards_per_page):
            assert_that(
                document.index(page_row, 0).child(card_index, 0).internalPointer(),
                all_of(
                    instance_of(CardContainer),
                    has_property("parent", is_(page)),
                    has_property(
                        "card", all_of(
                            instance_of(Card),
                            has_property("scryfall_id", equal_to("0000579f-7b35-4ed3-b44c-db2a538066fe")),
                        ),
                    ),
                ),
                "Parent relationship broken"
            )


def test_remove_pages_removes_middle_page(card_db: CardDatabase):
    document = Document(card_db, MagicMock())
    pages_to_create = 10
    for _ in range(pages_to_create-1):  # Create one less, because the document has one page by default
        document.add_page()
    assert_that(document.rowCount(), is_(equal_to(pages_to_create)), "Unexpected page count before deletion.")
    assert_that(document.pages, has_length(pages_to_create), "Unexpected page count before deletion.")
    page_to_delete = document.pages[5]
    document.remove_pages([document.index(5, 0)])
    assert_that(document.rowCount(), is_(equal_to(pages_to_create-1)), "Unexpected page count after deletion.")
    assert_that(document.pages, has_length(pages_to_create-1), "Unexpected page count after deletion.")
    assert_that(
        calling(document.find_page_list_index).with_args(page_to_delete),
        raises(ValueError), "Wrong page deleted."
    )


@pytest.mark.timeout(0.5)
def test_compacting_document(card_db):
    pages_to_fill = 5
    card = card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    document = Document(card_db, MagicMock())
    document.add_card(card, pages_to_fill*document.total_cards_per_page)
    cards_to_remove = 6
    for page_index in range(1, 4):
        document.remove_cards(
            list(map(document.index(page_index, 0).child, range(cards_to_remove), itertools.repeat(0)))
        )
        assert_that(document.pages[page_index], has_length(document.total_cards_per_page-cards_to_remove))
    for page_index in (0, 4):
        assert_that(document.pages[page_index], has_length(document.total_cards_per_page))
    document.compact_pages()
    assert_that(document.pages, has_length(3), "Unexpected page count after compacting")
    for index, page in enumerate(document.pages):
        assert_that(page, has_length(document.total_cards_per_page), "Unexpected card count found on a page")
        for card_container in page:
            assert_that(
                card_container.parent,
                same_instance(page),
                f"Parent relationship incorrect on page {index}"
            )




