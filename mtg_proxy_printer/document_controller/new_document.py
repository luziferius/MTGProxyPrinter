# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>

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

import pathlib
import typing

if typing.TYPE_CHECKING:
    from mtg_proxy_printer.model.document import Document

from mtg_proxy_printer.model.document_loader import PageLayoutSettings
from ._interface import DocumentAction, Self
from .page_actions import ActionRemovePage
from .edit_document_settings import ActionEditDocumentSettings
from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger
__all__ = [
    "ActionNewDocument",
]


class ActionNewDocument(DocumentAction):
    """Create a new document"""

    COMPARISON_ATTRIBUTES = ["old_save_path", "remove_pages_action", "reset_settings_action"]

    def __init__(self):
        self.old_save_path: typing.Optional[pathlib.Path] = None
        self.remove_pages_action: typing.Optional[ActionRemovePage] = None
        self.reset_settings_action: typing.Optional[ActionEditDocumentSettings] = None
        # The page layout settings have to be saved here to not break continuity in corner cases.
        # Potential issue mitigated by keeping the settings as of creation time:
        # User creates a new document, fills a page, then un-does all actions including this action,
        # then alters the document settings and then re-does all actions via the redo button. Keeping a copy of
        # the page layout settings here keeps the redo stack consistent across settings changes.
        self.new_page_layout = PageLayoutSettings.create_from_settings()

    def apply(self, document: "Document") -> Self:
        self.old_save_path = document.save_file_path
        document.save_file_path = None
        self.remove_pages_action = ActionRemovePage(0, document.rowCount()).apply(document)
        self.reset_settings_action = ActionEditDocumentSettings(self.new_page_layout).apply(
            document)
        return super().apply(document)

    def undo(self, document: "Document") -> Self:
        document.save_file_path = self.old_save_path
        self.remove_pages_action.undo(document)
        self.reset_settings_action.undo(document)
        self.old_save_path = self.remove_pages_action = self.reset_settings_action = None
        return self

    @property
    def as_str(self):
        return "Create new document"
