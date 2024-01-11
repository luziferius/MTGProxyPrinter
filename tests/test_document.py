# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import copy
import dataclasses
import pathlib
import typing
import unittest.mock
from tempfile import TemporaryDirectory
import textwrap

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from hamcrest import *

try:
    from hamcrest import contains_exactly
except ImportError:
    # Compatibility with PyHamcrest < 1.10
    from hamcrest import contains as contains_exactly
import pytest
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.model.card_list import PageColumns
from mtg_proxy_printer.sqlite_helpers import open_database, create_in_memory_database
from mtg_proxy_printer.units_and_sizes import PageType
from mtg_proxy_printer.model.carddb import Card, MTGSet, CheckCard
from mtg_proxy_printer.model.document import Document, Page, CardContainer
from mtg_proxy_printer.model.document_loader import DocumentLoader, PageLayoutSettings, CardType
from mtg_proxy_printer.model.imagedb import ImageKey

from mtg_proxy_printer.document_controller import DocumentAction
from mtg_proxy_printer.document_controller.new_document import ActionNewDocument
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard
from mtg_proxy_printer.document_controller.edit_document_settings import ActionEditDocumentSettings

from .document_controller.helpers import insert_card_in_page, create_card

ItemDataRole = Qt.ItemDataRole


class DummyAction(DocumentAction):
    """A dummy DocumentAction that does nothing. apply() and undo() are replaced with MagicMock instances."""
    apply: unittest.mock.MagicMock
    undo: unittest.mock.MagicMock
    COMPARISON_ATTRIBUTES = ["value"]

    def __init__(self, value: int = 0):
        super().__init__()
        self.value = value
        self.apply = unittest.mock.MagicMock(return_value=self)
        self.undo = unittest.mock.MagicMock(return_value=self)

    @property
    def as_str(self):
        return f"{self.__class__.__name__}"


def append_new_card_in_page(page: Page, name: str, oversized: bool = False) -> Card:
    card = Card(name, MTGSet("", ""), "", "", "", True, "", "", True, oversized, 0, False, None)
    page.append(CardContainer(
        page,
        card
    ))
    return card


@pytest.mark.parametrize("first, second, matcher", [
    (1, 1, is_),
    (0, 1, is_not),
])
def test_dummy_action_eq(first: int, second: int, matcher):
    a_1 = DummyAction(first)
    a_2 = DummyAction(second)
    assert_that(a_1, is_(equal_to(a_1)))
    assert_that(a_2, is_(equal_to(a_2)))
    assert_that(a_1, matcher(equal_to(a_2)))


def assert_unused(action: DummyAction):
    action.apply.assert_not_called()
    action.undo.assert_not_called()


def assert_applied(action: DummyAction, document: Document):
    action.apply.assert_called_once_with(document)
    action.undo.assert_not_called()


def assert_undone(action: DummyAction, document: Document):
    action.apply.assert_not_called()
    action.undo.assert_called_once_with(document)


def test_apply_on_empty_undo_stack_empty_redo_stack(qtbot: QtBot, document_light: Document):
    action = DummyAction()
    with qtbot.wait_signals([document_light.undo_available_changed, document_light.action_applied], timeout=1000), \
            qtbot.assert_not_emitted(document_light.redo_available_changed), \
            qtbot.assert_not_emitted(document_light.action_undone):
        document_light.apply(action)

    assert_that(document_light.redo_stack, is_(empty()))
    assert_that(document_light.undo_stack, contains_exactly(action))

    assert_applied(action, document_light)


def test_apply_on_empty_undo_stack_filled_redo_stack(qtbot: QtBot, document_light: Document):
    document_light.redo_stack.append(redo_dummy := DummyAction(1))
    action = DummyAction(0)
    with qtbot.wait_signals([
                document_light.undo_available_changed,
                document_light.redo_available_changed,
                document_light.action_applied], timeout=1000), \
            qtbot.assert_not_emitted(document_light.action_undone):
        document_light.apply(action)

    assert_that(document_light.redo_stack, is_(empty()))
    assert_that(document_light.undo_stack, contains_exactly(action))

    assert_unused(redo_dummy)
    assert_applied(action, document_light)


def test_apply_on_filled_undo_stack_empty_redo_stack(qtbot: QtBot, document_light: Document):
    document_light.undo_stack.append(previous_action := DummyAction())
    action = DummyAction()
    with qtbot.assert_not_emitted(document_light.undo_available_changed), \
            qtbot.assert_not_emitted(document_light.redo_available_changed), \
            qtbot.assert_not_emitted(document_light.action_undone), \
            qtbot.wait_signal(document_light.action_applied, timeout=1000):
        document_light.apply(action)

    assert_that(document_light.redo_stack, is_(empty()))
    assert_that(document_light.undo_stack, contains_exactly(previous_action, action))

    assert_unused(previous_action)
    assert_applied(action, document_light)


def test_apply_on_filled_undo_stack_filled_redo_stack(qtbot: QtBot, document_light: Document):
    document_light.undo_stack.append(previous_action := DummyAction())
    document_light.redo_stack.append(redo_dummy := DummyAction(1))
    action = DummyAction(0)
    expected_signals = [document_light.redo_available_changed, document_light.action_applied]
    with qtbot.wait_signals(expected_signals, timeout=1000), \
            qtbot.assert_not_emitted(document_light.undo_available_changed), \
            qtbot.assert_not_emitted(document_light.action_undone):
        document_light.apply(action)

    assert_that(document_light.redo_stack, is_(empty()))
    assert_that(document_light.undo_stack, contains_exactly(previous_action, action))

    assert_unused(redo_dummy)
    assert_unused(previous_action)
    assert_applied(action, document_light)


def test_apply_same_action_as_on_redo_stack_does_keep_remaining_redo_stack(qtbot: QtBot, document_light: Document):
    document_light.redo_stack.append(should_stay := DummyAction(2))
    document_light.redo_stack.append(DummyAction(1))
    action = DummyAction(1)
    expected_signals = [document_light.undo_available_changed, document_light.action_applied]
    with qtbot.wait_signals(expected_signals, timeout=1000), \
            qtbot.assert_not_emitted(document_light.redo_available_changed), \
            qtbot.assert_not_emitted(document_light.action_undone):
        document_light.apply(action)
    assert_that(document_light.redo_stack, contains_exactly(should_stay))
    assert_that(document_light.undo_stack, contains_exactly(action))


def test_undo_on_empty_redo_stack_2_elements_on_undo_stack(qtbot: QtBot, document_light: Document):
    document_light.undo_stack.append(first := DummyAction())
    document_light.undo_stack.append(second := DummyAction())
    expected_signals = [document_light.redo_available_changed, document_light.action_undone,]
    with qtbot.wait_signals(expected_signals, timeout=1000), \
            qtbot.assert_not_emitted(document_light.undo_available_changed), \
            qtbot.assert_not_emitted(document_light.action_applied):
        document_light.undo()

    assert_that(document_light.undo_stack, contains_exactly(first))
    assert_that(document_light.redo_stack, contains_exactly(second))

    assert_unused(first)
    assert_undone(second, document_light)


def test_undo_on_empty_redo_stack_1_element_on_undo_stack(qtbot: QtBot, document_light: Document):
    document_light.undo_stack.append(first := DummyAction())
    expected_signals = [
        document_light.redo_available_changed, document_light.undo_available_changed, document_light.action_undone,
    ]
    with qtbot.wait_signals(expected_signals, timeout=1000), \
            qtbot.assert_not_emitted(document_light.action_applied):
        document_light.undo()

    assert_that(document_light.undo_stack, is_(empty()))
    assert_that(document_light.redo_stack, contains_exactly(first))

    assert_undone(first, document_light)


def test_undo_on_filled_redo_stack_1_element_on_undo_stack(qtbot: QtBot, document_light: Document):
    document_light.redo_stack.append(redo_dummy := DummyAction())
    document_light.undo_stack.append(first := DummyAction())
    expected_signals = [document_light.undo_available_changed, document_light.action_undone,]
    with qtbot.wait_signals(expected_signals, timeout=1000), \
            qtbot.assert_not_emitted(document_light.redo_available_changed), \
            qtbot.assert_not_emitted(document_light.action_applied):
        document_light.undo()

    assert_that(document_light.undo_stack, is_(empty()))
    assert_that(document_light.redo_stack, contains_exactly(redo_dummy, first))

    assert_unused(redo_dummy)
    assert_undone(first, document_light)


def test_undo_on_filled_redo_stack_2_elements_on_undo_stack(qtbot: QtBot, document_light: Document):
    document_light.redo_stack.append(redo_dummy := DummyAction())
    document_light.undo_stack.append(first := DummyAction())
    document_light.undo_stack.append(second := DummyAction())

    with qtbot.assert_not_emitted(document_light.undo_available_changed), \
            qtbot.assert_not_emitted(document_light.redo_available_changed), \
            qtbot.assert_not_emitted(document_light.action_applied), \
            qtbot.wait_signal(document_light.action_undone, timeout=1000):
        document_light.undo()

    assert_that(document_light.undo_stack, contains_exactly(first))
    assert_that(document_light.redo_stack, contains_exactly(redo_dummy, second))

    assert_unused(redo_dummy)
    assert_unused(first)
    assert_undone(second, document_light)


def test_redo_on_empty_undo_stack_1_element_on_redo_stack(qtbot: QtBot, document_light: Document):
    document_light.redo_stack.append(first := DummyAction())
    expected_signals = [
        document_light.undo_available_changed, document_light.redo_available_changed, document_light.action_applied
    ]
    with qtbot.wait_signals(
            expected_signals, timeout=1000), \
            qtbot.assert_not_emitted(document_light.action_undone):
        document_light.redo()

    assert_that(document_light.redo_stack, is_(empty()))
    assert_that(document_light.undo_stack, contains_exactly(first))

    assert_applied(first, document_light)


def test_redo_on_empty_undo_stack_2_elements_on_redo_stack(qtbot: QtBot, document_light: Document):
    document_light.redo_stack.append(first := DummyAction())
    document_light.redo_stack.append(second := DummyAction())

    expected_signals = [document_light.undo_available_changed, document_light.action_applied]
    with qtbot.wait_signals(expected_signals, timeout=1000), \
            qtbot.assert_not_emitted(document_light.redo_available_changed), \
            qtbot.assert_not_emitted(document_light.action_undone):
        document_light.redo()

    assert_that(document_light.redo_stack, contains_exactly(first))
    assert_that(document_light.undo_stack, contains_exactly(second))

    assert_unused(first)
    assert_applied(second, document_light)


def test_redo_on_filled_undo_stack_1_element_on_redo_stack(qtbot: QtBot, document_light: Document):
    document_light.redo_stack.append(first := DummyAction())
    document_light.undo_stack.append(undo_dummy := DummyAction())
    expected_signals = [document_light.redo_available_changed, document_light.action_applied]
    with qtbot.wait_signals(expected_signals, timeout=1000), \
            qtbot.assert_not_emitted(document_light.undo_available_changed), \
            qtbot.assert_not_emitted(document_light.action_undone):
        document_light.redo()

    assert_that(document_light.undo_stack, contains_exactly(undo_dummy, first))
    assert_that(document_light.redo_stack, is_(empty()))

    assert_unused(undo_dummy)
    assert_applied(first, document_light)


def test_redo_on_filled_undo_stack_2_elements_on_redo_stack(qtbot: QtBot, document_light: Document):
    document_light.redo_stack.append(first := DummyAction())
    document_light.redo_stack.append(second := DummyAction())
    document_light.undo_stack.append(undo_dummy := DummyAction())

    with qtbot.assert_not_emitted(document_light.undo_available_changed), \
            qtbot.assert_not_emitted(document_light.redo_available_changed), \
            qtbot.assert_not_emitted(document_light.action_undone), \
            qtbot.wait_signal(document_light.action_applied, timeout=1000):
        document_light.redo()

    assert_that(document_light.undo_stack, contains_exactly(undo_dummy, second))
    assert_that(document_light.redo_stack, contains_exactly(first))

    assert_unused(undo_dummy)
    assert_unused(first)
    assert_applied(second, document_light)


@pytest.mark.parametrize("additional_pages", range(3))
def test_rowCount_without_index_parameter_return_page_count(document_light, additional_pages: int):
    if additional_pages:
        document_light.apply(ActionNewPage(count=additional_pages))
    assert_that(document_light.pages, has_length(1+additional_pages), "Test setup failed")
    assert_that(document_light.rowCount(), is_(1+additional_pages), "Wrong rowCount() returned")


def test_rowCount_with_valid_index_returns_card_count_on_page_given_by_index(document_light):
    document_light.apply(ActionNewPage(count=3))
    for count in range(1, 4):
        document_light.set_currently_edited_page(document_light.pages[count])
        document_light.apply(
            ActionAddCard(Card("", MTGSet("", ""), "", "", "", True, "", "", True, False, 0, None), count=count)
        )
        assert_that(document_light.currently_edited_page, has_length(count), "Test setup failed")
    for page in range(4):
        assert_that(
            document_light.rowCount(document_light.index(page, 0)),
            is_(equal_to(page)),
            f"Wrong rowCount() returned for page {page}"
        )


@pytest.mark.parametrize("page_type, parent_row, child_rows", [
    (PageType.REGULAR, 0, [0]),
    (PageType.OVERSIZED, 2, [0, 1]),
])
def test_get_card_indices_of_type(document_light, page_type: PageType, parent_row: int, child_rows: typing.List[int]):
    ActionNewPage(count=2).apply(document_light)
    append_new_card_in_page(document_light.pages[0], "Normal", False)
    append_new_card_in_page(document_light.pages[2], "Oversized", True)
    append_new_card_in_page(document_light.pages[2], "Oversized", True)
    indices = list(document_light.get_card_indices_of_type(page_type))
    assert_that(indices, has_length(len(child_rows)))
    for index, expected_row in zip(indices, child_rows):
        assert_that(index.row(), is_(expected_row))
        assert_that(index.parent().row(), is_(parent_row))
        card: Card = index.data(ItemDataRole.UserRole)
        assert_that(card.requested_page_type(), is_(page_type))


@pytest.fixture
def document_custom_layout(document: Document) -> Document:
    custom_layout = PageLayoutSettings(
        page_height=300, page_width=200,
        margin_top=20, margin_bottom=19, margin_left=18, margin_right=17,
        row_spacing=3, column_spacing=2,
        draw_cut_markers=True, draw_sharp_corners=False,
    )
    document.apply(ActionEditDocumentSettings(custom_layout))
    yield document
    document.__dict__.clear()


def test_document_reset_clears_modified_page_layout(qtbot: QtBot, document_custom_layout: Document):
    default_layout = PageLayoutSettings.create_from_settings()
    assert_that(
        document_custom_layout,
        has_property("page_layout", not_(equal_to(default_layout)))
    )
    assert_that(
        document_custom_layout.page_layout.compute_page_row_count(),
        is_not(equal_to(default_layout.compute_page_card_capacity())),
        "Test setup failed."
    )
    with qtbot.waitSignal(document_custom_layout.page_layout_changed, timeout=1000):
        document_custom_layout.apply(ActionNewDocument())

    assert_that(
        document_custom_layout,
        has_property("page_layout", equal_to(default_layout))
    )


def test_document_is_created_empty(document_light: Document):
    capacity = document_light.page_layout.compute_page_card_capacity()
    assert_that(capacity, is_(greater_than_or_equal_to(1)))
    assert_that(document_light.rowCount(), is_(equal_to(1)), "Expected creation of a single, empty page.")
    assert_that(
        document_light.pages,
        contains_exactly(empty()),
        "Expected creation of a single, empty page."
    )
    assert_that(
        document_light.rowCount(document_light.index(0, 0)), is_(equal_to(0)),
        "Expected empty page, but it is not empty")
    assert_that(
        document_light.pages[0].page_type(), is_(PageType.UNDETERMINED),
        "Empty page should have an undetermined page type"
    )


@pytest.mark.parametrize("source_version", [2, 3, 4, 5])
def test_save_migration(document: Document, source_version: int):
    """Tests migration of existing saves to the newest schema revision on save."""
    card = document.card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    capacity = document.page_layout.compute_page_card_capacity(card.requested_page_type())
    document.apply(ActionAddCard(card, capacity))
    with TemporaryDirectory() as temp_dir:
        document.save_file_path = _create_save_file(pathlib.Path(temp_dir), source_version)
        document.save_to_disk()
        _validate_database_schema(document.save_file_path)
        _validate_saved_document_settings(document)


def test_create_save(document_custom_layout: Document):
    """Tests that saving a new document uses the newest database schema version"""
    card = document_custom_layout.card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    capacity = document_custom_layout.page_layout.compute_page_card_capacity(card.requested_page_type())
    document_custom_layout.apply(ActionAddCard(card, capacity))
    with TemporaryDirectory() as temp_dir:
        save_dir = pathlib.Path(temp_dir)/"test.mtgproxies"
        document_custom_layout.save_as(save_dir)
        _validate_database_schema(save_dir)
        _validate_saved_document_settings(document_custom_layout)


@pytest.mark.parametrize("is_front", [True, False])
def test_save_as_saves_regular_card(document: Document, is_front: bool):
    card = document.card_db.get_card_with_scryfall_id("b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", is_front)
    document.apply(ActionAddCard(card))
    with TemporaryDirectory() as temp_dir:
        save_file = pathlib.Path(temp_dir)/"test.mtgproxies"
        document.save_as(save_file)
        with open_database(
                save_file, "document-v6", DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION, False) as con:
            content = con.execute("SELECT page, slot, scryfall_id, is_front, type FROM Card").fetchall()
        # Deleting the connection is required on Windows. It releases the file lock that otherwise prevents the
        # temp_dir context manager from cleaning up the disk
        del con
    assert_that(
        content, contains_exactly(
            contains_exactly(1, 1, "b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", is_front, CardType.REGULAR.value)
        )
    )


def test_save_as_saves_check_card(document: Document):
    card = CheckCard(
        document.card_db.get_card_with_scryfall_id("b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", True),
        document.card_db.get_card_with_scryfall_id("b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", False),
    )
    document.apply(ActionAddCard(card))
    with TemporaryDirectory() as temp_dir:
        save_file = pathlib.Path(temp_dir)/"test.mtgproxies"
        document.save_as(save_file)
        with open_database(
                save_file, "document-v6", DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION, False) as con:
            content = con.execute("SELECT page, slot, scryfall_id, is_front, type FROM Card").fetchall()
        # Deleting the connection is required on Windows. It releases the file lock that otherwise prevents the
        # temp_dir context manager from cleaning up the disk
        del con
    assert_that(
        content, contains_exactly(
            contains_exactly(1, 1, "b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", True, CardType.CHECK_CARD.value)
        )
    )


def test_subsequent_save_updates_settings(tmp_path: pathlib.Path, qtbot: QtBot, document_custom_layout: Document):
    """Tests that saving a new document uses the newest database schema version"""
    layout = copy.copy(document_custom_layout.page_layout)
    layout.page_height = 1000
    card = document_custom_layout.card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    # Prevent network access when re-loading the document
    document_custom_layout.image_db.loaded_images[
        ImageKey(card.scryfall_id, card.is_front, card.highres_image)] = document_custom_layout.image_db.blank_image
    cards_per_page = document_custom_layout.page_layout.compute_page_card_capacity(card.requested_page_type())
    document_custom_layout.apply(ActionAddCard(card, cards_per_page))

    save_dir = pathlib.Path(tmp_path)/"test.mtgproxies"
    document_custom_layout.save_as(save_dir)
    _validate_database_schema(save_dir)
    _validate_saved_document_settings(document_custom_layout)
    with qtbot.waitSignal(document_custom_layout.page_layout_changed):
        document_custom_layout.apply(ActionEditDocumentSettings(layout))
    document_custom_layout.save_to_disk()
    with qtbot.waitSignals([document_custom_layout.loading_state_changed]*2,
                           check_params_cbs=[lambda value: value, lambda value: not value]):
        document_custom_layout.loader.load_document(save_dir)
    assert_that(document_custom_layout.page_layout.page_height, is_(equal_to(1000)))


def _create_save_file(temp_path: pathlib.Path, source_version: int):
    """Creates an empty document save file at the given path and using the given schema version."""
    save_file_path = temp_path/"test.mtgproxies"
    open_database(save_file_path, f"document-v{source_version}", DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION).close()
    return save_file_path


def _validate_database_schema(db_path: pathlib.Path):
    """
    Validates the database schema of the user-provided file against a known-good schema.

    :raises AssertionError: If the provided file contains an invalid schema
    :returns: Database schema version
    """
    target_schema_version = 6
    db_unsafe = open_database(
        db_path, f"document-v{target_schema_version}", DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION)
    if db_unsafe.execute("PRAGMA application_id").fetchone()[0] != 41325044:
        raise AssertionError("Not an MTGProxyPrinter save file!")
    user_schema_version = db_unsafe.execute("PRAGMA user_version").fetchone()[0]
    assert_that(user_schema_version, is_(equal_to(target_schema_version)))
    db_known_good = create_in_memory_database(
        f"document-v{target_schema_version}", DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION)
    tables_and_views_query = textwrap.dedent("""\
        SELECT   s.type, s.name,
                 p.cid AS column_id, p.name AS column_name, p.type AS column_type,
                 p."notnull" AS column_not_null_constraint_enabled, p.dflt_value AS column_default_value,
                 p.pk AS column_primary_key_component
          FROM   sqlite_schema AS s
          JOIN   pragma_table_info(s.name) AS p
         WHERE   s.type IN ('table', 'view')
           AND   s.name NOT LIKE 'sqlite_%'
        ORDER BY s.name, column_id
        ;""")
    indices_query = textwrap.dedent("""\
        -- Note: Also include the “sqlite_autoindex*” indices that are
        -- automatically created for UNIQUE and PRIMARY KEY constraints.
        SELECT   s.name AS index_name,
                 p.seqno AS index_column_sequence_number,
                 p.cid AS column_id,
                 p.name AS column_name
          FROM   sqlite_schema AS s
          JOIN   pragma_index_info(s.name) AS p
         WHERE   s.type = 'index'
        ORDER BY index_name ASC, index_column_sequence_number ASC
        ;""")
    with db_known_good:
        assert_that(
            db_unsafe.execute(tables_and_views_query).fetchall(),
            contains_exactly(*db_known_good.execute(tables_and_views_query).fetchall()),
            "Given save file inconsistent: Unexpected tables or views")
        assert_that(
            db_unsafe.execute(indices_query).fetchall(),
            contains_exactly(*db_known_good.execute(indices_query).fetchall()),
            "Given save file inconsistent: Unexpected indices")


def _validate_saved_document_settings(document: Document):
    with open_database(document.save_file_path, "document-v6", DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION) as save:
        assert_that(
            save.execute("SELECT COUNT(*) FROM DocumentSettings").fetchone(),
            contains_exactly(len(dataclasses.astuple(document.page_layout)))
        )
        keys = ", ".join(map("'{}'".format, document.page_layout.__annotations__.keys()))
        query = textwrap.dedent(f"""\
            SELECT value
              FROM DocumentSettings
              WHERE key IN ({keys})
              ORDER BY key ASC
            """)
        page_layout: PageLayoutSettings = document.page_layout
        assert_that(
            [value for value, in save.execute(query).fetchall()],
            contains_exactly(
                page_layout.column_spacing,
                page_layout.document_name,
                int(page_layout.draw_cut_markers),
                int(page_layout.draw_sharp_corners),
                int(page_layout.draw_page_numbers),
                page_layout.duplex_mode.value,
                page_layout.margin_bottom,
                page_layout.margin_left,
                page_layout.margin_right,
                page_layout.margin_top,
                page_layout.page_height,
                page_layout.page_width,
                page_layout.row_spacing,
            )
        )


def test_get_missing_image_cards(document_light: Document):
    blank_image = document_light.image_db.blank_image
    expected = create_card("Placeholder Image")
    expected.image_file = blank_image
    unexpected = create_card("Other Image")
    unexpected.image_file = QPixmap(blank_image)  # Create a new, distinct image by copying the blank image
    document_light.apply(ActionAddCard(expected, 2))
    document_light.apply(ActionAddCard(unexpected, 2))
    assert_that(
        result := list(document_light.get_missing_image_cards()),
        has_length(2)
    )
    cards = [i.data(ItemDataRole.UserRole) for i in result]
    assert_that(cards, only_contains(expected))


@pytest.mark.parametrize("result", [True, False])
def test_has_missing_images(document_light: Document, result: bool):
    blank_image = document_light.image_db.blank_image
    blank_image_card = create_card("Placeholder Image")
    blank_image_card.image_file = blank_image
    other_card = create_card("Other Image")
    other_card.image_file = QPixmap(blank_image)  # Create a new, distinct image by copying the blank image
    if result:
        document_light.apply(ActionAddCard(blank_image_card, 2))
    document_light.apply(ActionAddCard(other_card, 2))
    assert_that(
        document_light.has_missing_images(),
        is_(result)
    )


@pytest.mark.parametrize("pages_content, expected", [
    ([], 0),
    ([None, None], 1),
    ([create_card("Regular", False)], 0),
    ([create_card("Regular", False)]*2, 1),
    ([create_card("Regular", False), create_card("Oversized", True)], 0),
    ([create_card("Regular", False), create_card("Oversized", True)]*2, 2),
    ([create_card("Regular", False), create_card("Oversized", True), None]*2, 4),
])
def test_compute_pages_saved_by_compacting(
        document_light: Document, pages_content: typing.List[typing.Optional[Card]], expected: int):
    if len(pages_content) > 1:
        document_light.apply(ActionNewPage(count=len(pages_content)-1))
    for page, card in zip(document_light.pages, pages_content):
        if card is not None:
            insert_card_in_page(page, card)
    assert_that(
        document_light.compute_pages_saved_by_compacting(),
        is_(equal_to(expected))
    )


def test_update_page_layout_copies_the_passed_in_instance(document_light: Document):
    layout = copy.copy(document_light.page_layout)
    layout.row_spacing = 1
    document_light.apply(ActionEditDocumentSettings(layout))
    layout.row_spacing = 2
    assert_that(document_light.page_layout, has_property("row_spacing", equal_to(1)))


@pytest.mark.parametrize("page_type, column_spacing, row_spacing, expected", [
    (PageType.REGULAR, 0, 0, 9),
    (PageType.REGULAR, 17, 0, 6),
    (PageType.REGULAR, 0, 10, 6),
    (PageType.OVERSIZED, 0, 0, 4),
    (PageType.OVERSIZED, 0, 10, 4),
    (PageType.OVERSIZED, 0, 25, 2),
])
def test_page_layout_compute_page_card_capacity(
        page_type: PageType, column_spacing: int, row_spacing: int, expected: int):
    layout = PageLayoutSettings.create_from_settings()
    layout.row_spacing = row_spacing
    layout.column_spacing = column_spacing
    assert_that(layout.compute_page_card_capacity(page_type), is_(expected))


@pytest.mark.parametrize("invalid_page_row", [2])
def test_document__data_page_logs_error_on_invalid_index(document_light, invalid_page_row: int):
    index = document_light.createIndex(invalid_page_row, 0, None)
    with unittest.mock.patch("mtg_proxy_printer.model.document.logger.error") as logger_mock:
        assert_that(document_light._data_page(index), is_(None))
        logger_mock.assert_called_once()


@pytest.mark.parametrize("invalid_card_row", [2])
def test_document__data_card_logs_error_on_invalid_index_row(document_light, invalid_card_row: int):
    append_new_card_in_page(document_light.pages[0], "Card")
    index = document_light.createIndex(invalid_card_row, 0, document_light.pages[0][0])
    with unittest.mock.patch("mtg_proxy_printer.model.document.logger.error") as logger_mock:
        assert_that(document_light._data_card(index), is_(None))
        logger_mock.assert_called_once()


@pytest.mark.parametrize("invalid_card_column", [len(PageColumns)])
def test_document__data_card_logs_error_on_invalid_index_column(document_light, invalid_card_column: int):
    append_new_card_in_page(document_light.pages[0], "Card")
    index = document_light.createIndex(0, invalid_card_column, document_light.pages[0][0])
    with unittest.mock.patch("mtg_proxy_printer.model.document.logger.error") as logger_mock:
        assert_that(document_light._data_card(index), is_(None))
        logger_mock.assert_called_once()
