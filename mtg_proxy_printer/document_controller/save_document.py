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

import functools
import sqlite3
from pathlib import Path
import typing

if typing.TYPE_CHECKING:
    from mtg_proxy_printer.model.document import Document

from ._interface import DocumentAction, Self
from mtg_proxy_printer.sqlite_helpers import open_database, cached_dedent
from mtg_proxy_printer.units_and_sizes import CardSizes
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.model.card import AnyCardType
from mtg_proxy_printer.model.document_loader import CardType
from mtg_proxy_printer.save_file_migrations import migrate_database

from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger
__all__ = [
    "ActionSaveDocument",
]


class ActionSaveDocument(DocumentAction):
    """
    Save the document to a save file.
    """
    COMPARISON_ATTRIBUTES = []

    def __init__(self, file_path: Path):
        super().__init__()
        self.file_path = file_path

    def apply(self, document: "Document") -> Self:
        logger.debug(f"About to save document to {self.file_path}")
        layout = document.page_layout
        with open_database(self.file_path, "document-v7") as db:
            db.execute("BEGIN IMMEDIATE TRANSACTION  -- apply()\n")
            migrate_database(db, layout)
            self._clear_cards_and_pages(db)
            self._save_pages(db, document)
            self._save_cards(db, document)
            self.save_settings(db, layout)
            self._clean_unused_custom_cards(db)
            db.commit()
            if db.execute(cached_dedent("""\
                SELECT cast(freelist_count AS real)/page_count > 0.1 AS "should vacuum" -- apply() 
                  FROM pragma_page_count
                  INNER JOIN pragma_freelist_count
                """)).fetchone()[0]:
                db.execute("VACUUM -- apply()\n")
        logger.debug("Database saved and closed.")

    @staticmethod
    def save_settings(save_file: sqlite3.Connection, layout: PageLayoutSettings):
        settings, dimensions = layout.to_save_file_data()
        save_file.executemany(
            'INSERT OR REPLACE INTO DocumentSettings ("key", value) VALUES (?, ?) -- save_settings()\n',
            settings)
        save_file.executemany(
            'INSERT OR REPLACE INTO DocumentDimensions ("key", value) VALUES (?, ?) -- save_settings()\n',
            dimensions)
        logger.debug("Written document settings")

    @staticmethod
    def _clear_cards_and_pages(save_file: sqlite3.Connection):
        save_file.execute("DELETE FROM Card -- _clear_cards_and_pages()\n")
        save_file.execute("DELETE FROM Page -- _clear_cards_and_pages()\n")

    @staticmethod
    def _save_pages(save_file: sqlite3.Connection, document: "Document"):
        pages = (
            (number, CardSizes.for_page_type(page.page_type()).to_save_data())
            for number, page in enumerate(document.pages, start=1)
            if page
        )
        save_file.executemany(
            "INSERT INTO Page (page, image_size) VALUES (?, ?) -- _save_pages()\n",
            pages
        )

    @staticmethod
    def _save_cards(save_file: sqlite3.Connection, document: "Document"):
        empty_slot = cached_dedent("""\
        INSERT INTO Card (page, slot, is_front, type) -- _save_cards()
            VALUES (?, ? ,?, ?)\n""")
        official_card = cached_dedent("""\
        INSERT INTO Card (page, slot, is_front, type, scryfall_id) -- _save_cards()
            VALUES (?, ?, ? ,?, ?)\n""")
        for page_number, page in enumerate(document.pages, start=1):
            for slot, container in enumerate(page, start=1):
                card = container.card
                if card.image_file is document.image_db.get_blank(card.size):
                    # Empty slot
                    save_file.execute(
                        empty_slot,(page_number, slot, card.is_front, CardType.from_card(card))
                    )
                elif card.is_custom_card:
                    ActionSaveDocument._save_custom_card(save_file, page_number, slot, card)
                else:
                    save_file.execute(
                        official_card,
                        (page_number, slot, card.is_front, CardType.from_card(card), card.scryfall_id)
                    )
        logger.debug(f"Written {save_file.execute('SELECT count(1) FROM Card').fetchone()[0]} cards.")

    @staticmethod
    def _save_custom_card(save_file: sqlite3.Connection, page_number: int, slot: int, card: AnyCardType):
        custom_card_data = (
            card.scryfall_id, card.source_image_file, card.name, card.set.name, card.set_code,
            card.collector_number, card.is_front)
        save_file.execute(cached_dedent("""\
            INSERT INTO CustomCardData -- _save_custom_card()
                (card_id, image, name, set_name, set_code, collector_number, is_front)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (card_id) DO UPDATE
                    SET name = excluded.name,
                        set_name = excluded.set_name,
                        set_code = excluded.set_code,
                        collector_number = excluded.collector_number,
                        is_front = excluded.is_front
                    WHERE name <> excluded.name
                       OR set_name <> excluded.set_name
                       OR set_code <> excluded.set_code
                       OR collector_number <> excluded.collector_number
                       OR is_front <> excluded.is_front
                """),
            custom_card_data
        )
        card_data = (page_number, slot, card.is_front, CardType.from_card(card), card.scryfall_id)
        save_file.execute(cached_dedent("""\
            INSERT INTO Card (page, slot, is_front, type, custom_card_id) -- _save_custom_card()
                VALUES (?, ?, ? ,?, ?)\n"""),
            card_data
        )

    @staticmethod
    def _clean_unused_custom_cards(save_file: sqlite3.Connection):
        save_file.execute(cached_dedent("""\
            DELETE FROM CustomCardData  -- _clean_unused_custom_cards()
              WHERE card_id NOT IN (
                SELECT custom_card_id
                  FROM Card
                  WHERE custom_card_id IS NOT NULL)
            """))

    def undo(self, document: "Document") -> Self:
        raise NotImplementedError("Undoing saving to disk is unsupported.")

    @functools.cached_property
    def as_str(self):
        return self.translate(
            "ActionSaveDocument", "Save document to '{save_file_path}'."
        ).format(save_file_path=self.file_path)
