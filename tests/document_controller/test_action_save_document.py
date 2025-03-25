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

import copy
import dataclasses
from pathlib import Path
import textwrap

from hamcrest import *
from PySide6.QtCore import QModelIndex, Qt
import pytest
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.sqlite_helpers import open_database, create_in_memory_database
from mtg_proxy_printer.units_and_sizes import unit_registry, UnitT, CardSizes
from mtg_proxy_printer.model.carddb import CheckCard
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.document_loader import DocumentLoader, CardType
from mtg_proxy_printer.model.imagedb import ImageKey
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard
from mtg_proxy_printer.document_controller.edit_document_settings import ActionEditDocumentSettings
from mtg_proxy_printer.document_controller.save_document import ActionSaveDocument

from tests.test_document import document_custom_layout
from tests.helpers import close_to_

ItemDataRole = Qt.ItemDataRole
mm: UnitT = unit_registry.mm

def validate_qt_model_signal_parameter(
        expected_first: int, expected_last: int,
        parent: QModelIndex, first: int, last: int) -> bool:
    return not parent.isValid() and first == expected_first and last == expected_last


def test_apply(qtbot, document_light):
    pass


@pytest.mark.parametrize("source_version", [2, 3, 4, 5])
def test_save_migration(tmp_path: Path, document: Document, source_version: int):
    """Tests migration of existing saves to the newest schema revision on save."""
    card = document.card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    capacity = document.page_layout.compute_page_card_capacity(card.requested_page_type())
    document.apply(ActionAddCard(card, capacity))
    action = ActionSaveDocument(_create_save_file(Path(tmp_path), source_version))
    action.apply(document)
    _validate_database_schema(action.file_path)
    _validate_saved_document_settings(document, action.file_path)


def test_create_save(tmp_path: Path, document_custom_layout: Document):
    """Tests that saving a new document uses the newest database schema version"""
    card = document_custom_layout.card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    capacity = document_custom_layout.page_layout.compute_page_card_capacity(card.requested_page_type())
    document_custom_layout.apply(ActionAddCard(card, capacity))
    save_file = tmp_path / "test.mtgproxies"
    action = ActionSaveDocument(save_file)
    action.apply(document_custom_layout)
    _validate_database_schema(save_file)
    _validate_saved_document_settings(document_custom_layout, save_file)


@pytest.mark.parametrize("is_front", [True, False])
def test_save_as_saves_regular_card(tmp_path: Path, document: Document, is_front: bool):
    card = document.card_db.get_card_with_scryfall_id("b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", is_front)
    document.apply(ActionAddCard(card))
    save_file = tmp_path/"test.mtgproxies"
    action = ActionSaveDocument(save_file)
    action.apply(document)
    with open_database(
            save_file, "document-v6", DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION, False) as con:
        content = con.execute("SELECT page, slot, scryfall_id, is_front, type FROM Card").fetchall()
    del con
    assert_that(
        content, contains_exactly(
            contains_exactly(1, 1, "b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", is_front, CardType.REGULAR.value)
        )
    )


def test_save_as_saves_check_card(tmp_path: Path, document: Document):
    card = CheckCard(
        document.card_db.get_card_with_scryfall_id("b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", True),
        document.card_db.get_card_with_scryfall_id("b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", False),
    )
    document.apply(ActionAddCard(card))
    save_file = tmp_path / "test.mtgproxies"
    action = ActionSaveDocument(save_file)
    action.apply(document)
    with open_database(
            save_file, "document-v6", DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION, False) as con:
        content = con.execute("SELECT page, slot, scryfall_id, is_front, type FROM Card").fetchall()
    del con
    assert_that(
        content, contains_exactly(
            contains_exactly(1, 1, "b3b87bfc-f97f-4734-94f6-e3e2f335fc4d", True, CardType.CHECK_CARD.value)
        )
    )


def test_subsequent_save_updates_settings(tmp_path: Path, qtbot: QtBot, document_custom_layout: Document):
    """Tests that saving a new document uses the newest database schema version"""
    layout = copy.copy(document_custom_layout.page_layout)
    layout.page_height = 1000*mm
    card = document_custom_layout.card_db.get_card_with_scryfall_id("0000579f-7b35-4ed3-b44c-db2a538066fe", True)
    # Prevent network access when re-loading the document
    blank = document_custom_layout.image_db.get_blank(CardSizes.REGULAR)
    document_custom_layout.image_db.loaded_images[ImageKey(card.scryfall_id, card.is_front, card.highres_image)] = blank
    cards_per_page = document_custom_layout.page_layout.compute_page_card_capacity(card.requested_page_type())
    document_custom_layout.apply(ActionAddCard(card, cards_per_page))

    save_file = Path(tmp_path)/"test.mtgproxies"
    action = ActionSaveDocument(save_file)
    action.apply(document_custom_layout)
    _validate_database_schema(save_file)
    _validate_saved_document_settings(document_custom_layout, save_file)
    with qtbot.waitSignal(document_custom_layout.page_layout_changed):
        document_custom_layout.apply(ActionEditDocumentSettings(layout))
    action.apply(document_custom_layout)
    with qtbot.waitSignals([document_custom_layout.loading_state_changed]*2,
                           check_params_cbs=[lambda value: value, lambda value: not value]):
        document_custom_layout.loader.load_document(save_file)
    assert_that(
        document_custom_layout.page_layout.page_height.to(mm).magnitude,
        is_(close_to_(1000)))


def _create_save_file(temp_path: Path, source_version: int):
    """Creates an empty document save file at the given path and using the given schema version."""
    save_file_path = temp_path/"test.mtgproxies"
    open_database(save_file_path, f"document-v{source_version}", DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION).close()
    return save_file_path


def _validate_database_schema(db_path: Path):
    """
    Validates the database schema of the user-provided file against a known-good schema.

    :raises AssertionError: If the provided file contains an invalid schema
    :returns: Database schema version
    """
    target_schema_version = 6
    db_unsafe = open_database(
        db_path, f"document-v{target_schema_version}", DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION)
    assert_that(
        db_unsafe.execute("PRAGMA application_id").fetchone(), contains_exactly(41325044),
        "Not an MTGProxyPrinter save file!"
    )
    assert_that(db_unsafe.execute("PRAGMA user_version").fetchone(), contains_exactly(target_schema_version))
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


def _validate_saved_document_settings(document: Document, save_file: Path):
    layout = document.page_layout
    with open_database(save_file, "document-v6", DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION) as save:
        assert_that(
            save.execute("SELECT COUNT(*) FROM DocumentSettings").fetchone(),
            contains_exactly(len(dataclasses.astuple(layout)))
        )
        keys = ", ".join(map("'{}'".format, layout.__annotations__.keys()))
        query = textwrap.dedent(f"""\
            SELECT value
              FROM DocumentSettings
              WHERE key IN ({keys})
              ORDER BY key ASC
            """)
        # TODO: Use the unit-aware matchers!
        assert_that(
            [value for value, in save.execute(query).fetchall()],
            contains_exactly(
                close_to_(layout.card_bleed.magnitude),
                close_to_(layout.column_spacing.magnitude),
                layout.document_name,
                int(layout.draw_cut_markers),
                int(layout.draw_sharp_corners),
                int(layout.draw_page_numbers),
                close_to_(layout.margin_bottom.magnitude),
                close_to_(layout.margin_left.magnitude),
                close_to_(layout.margin_right.magnitude),
                close_to_(layout.margin_top.magnitude),
                close_to_(layout.page_height.magnitude),
                close_to_(layout.page_width.magnitude),
                close_to_(layout.row_spacing.magnitude),
            )
        )
