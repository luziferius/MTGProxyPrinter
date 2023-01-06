import copy

import pytest
from hamcrest import *

from mtg_proxy_printer.units_and_sizes import PageType
from mtg_proxy_printer.model.carddb import Card, MTGSet, CardList
from mtg_proxy_printer.model.document import Page, CardContainer
from mtg_proxy_printer.document_controller import IllegalStateError
from mtg_proxy_printer.document_controller.shuffle_document import ActionShuffleDocument


def append_new_card_in_page(page: Page, name: str, oversized: bool = False) -> Card:
    card = Card(name, MTGSet("", ""), "", "", "", True, "", "", True, oversized, 0, None)
    page.append(CardContainer(
        page,
        card
    ))
    return card


def cards_on_page(page: Page) -> CardList:
    return [container.card for container in page]


def test_apply(qtbot, document_light):
    action = ActionShuffleDocument()
    action.random_seed = b"1"
    page = document_light.pages[0]
    append_new_card_in_page(page, "Card 1")
    append_new_card_in_page(page, "Card 2")
    append_new_card_in_page(page, "Card 3")
    old_page_content = cards_on_page(page)
    card_count = len(old_page_content)
    assert_that(old_page_content, contains_exactly(
        has_property("name", equal_to("Card 1")),
        has_property("name", equal_to("Card 2")),
        has_property("name", equal_to("Card 3")),
    ))
    with qtbot.wait_signals([document_light.dataChanged] * card_count, timeout=100):
        action.apply(document_light)
    new_page_content = cards_on_page(page)
    assert_that(new_page_content, contains_inanyorder(*old_page_content))
    assert_that(new_page_content, not_(contains_exactly(*old_page_content)))


def test_apply_with_existing_state_raises_exception(document_light):
    action = ActionShuffleDocument()
    action.shuffle_order[PageType.REGULAR] = [0]
    assert_that(calling(action.apply).with_args(document_light), raises(IllegalStateError))


def test_undo(qtbot, document_light):
    pytest.skip("Not implemented")
    action = ActionShuffleDocument()
    action.undo(document_light)
    assert_that(action.shuffle_order, is_(empty()))



def test_second_apply_produces_same_order(qtbot, document_light):
    pytest.skip("Required undo() not implemented")
    action = ActionShuffleDocument()
    action.random_seed = b"1"
    page = document_light.pages[0]
    append_new_card_in_page(page, "Card 1")
    append_new_card_in_page(page, "Card 2")
    append_new_card_in_page(page, "Card 3")
    old_page_content = cards_on_page(page)
    card_count = len(old_page_content)
    with qtbot.wait_signals([document_light.dataChanged] * card_count, timeout=100):
        action.apply(document_light)
    new_page_content = cards_on_page(page)
    with qtbot.wait_signals([document_light.dataChanged] * card_count, timeout=100):
        action.undo(document_light)
    assert_that(cards_on_page(page), contains_exactly(*old_page_content), "Setup failed: undo() broken")
    with qtbot.wait_signals([document_light.dataChanged] * card_count, timeout=100):
        action.apply(document_light)
    assert_that(cards_on_page(page), contains_exactly(*new_page_content), "Second apply() produced different order")
