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
import itertools
from pathlib import Path
import textwrap
import typing

if typing.TYPE_CHECKING:
    from mtg_proxy_printer.model.document import Document

from ._interface import DocumentAction, Self
import mtg_proxy_printer.sqlite_helpers
from mtg_proxy_printer.model.document_loader import DocumentSaveFormat, CardType
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
        layout = document.page_layout
        pages = enumerate(document.pages, start=1)
        cards = (
            zip(itertools.repeat(page_index), enumerate((
                container.card for container in page), start=1))
            for page_index, page in pages
        )
        flattened_data: DocumentSaveFormat = [
            (page, slot, card.scryfall_id, card.is_front, CardType.from_card(card))
            for (page, (slot, card))
            in itertools.chain.from_iterable(cards)
            # TODO: For now, custom cards have an empty id. Until saving them is implemented, skip custom cards
            #   so that the document can still be loaded
            if card.scryfall_id
        ]
        logger.debug(f"About to save document to {self.file_path}")
        with mtg_proxy_printer.sqlite_helpers.open_database(
                self.file_path, "document-v6", document.loader.MIN_SUPPORTED_SQLITE_VERSION) as db:
            db.execute("BEGIN IMMEDIATE TRANSACTION")
            migrate_database(db, layout)
            db.execute("DELETE FROM Card")
            db.executemany(
                "INSERT INTO Card (page, slot, scryfall_id, is_front, type) VALUES (?, ?, ?, ?, ?)",
                flattened_data
            )
            logger.debug(f"Written {db.execute('SELECT count() FROM Card').fetchone()[0]} cards.")
            settings = layout.to_save_file_data()
            db.executemany(
                textwrap.dedent("""\
                            INSERT OR REPLACE INTO DocumentSettings (key, value)
                              VALUES (?, ?)
                            """),
                settings)
            logger.debug("Written document settings")
            db.commit()
            db.execute("VACUUM")
        logger.debug("Database saved and closed.")

    def undo(self, document: "Document") -> Self:
        raise NotImplementedError("Undoing saving to disk is unsupported.")

    @functools.cached_property
    def as_str(self):
        return self.translate(
            "ActionSaveDocument", "Save document to '{save_file_path}'."
        ).format(save_file_path=self.file_path)