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

import typing
import pathlib

if typing.TYPE_CHECKING:
    from mtg_proxy_printer.model.document import Document

from mtg_proxy_printer.model.document_loader import PageLayoutSettings
from ._interface import DocumentAction
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

    def __init__(self):
        super().__init__()
        self.old_save_path: typing.Optional[pathlib.Path] = None
        self.remove_pages_action: typing.Optional[ActionRemovePage] = None
        self.reset_settings_action: typing.Optional[ActionEditDocumentSettings] = None
        # The page layout settings have to be saved here to not break continuity in corner cases.
        # Potential issue mitigated by keeping the settings as of creation time:
        # User creates a new document, fills a page, then un-does all actions including this action,
        # then alters the document settings and then re-does all actions via the redo button. Keeping a copy of
        # the page layout settings here keeps the redo stack consistent across settings changes.
        self.new_page_layout = PageLayoutSettings.create_from_settings()

    def apply(self, document: "Document"):
        self.old_save_path = document.save_file_path
        document.save_file_path = None
        self.remove_pages_action = ActionRemovePage(0, document.rowCount()).apply(document)
        self.reset_settings_action = ActionEditDocumentSettings(self.new_page_layout).apply(
            document)
        return self

    def undo(self, document: "Document"):
        document.save_file_path = self.old_save_path
        self.remove_pages_action.undo(document)
        self.reset_settings_action.undo(document)
        self.old_save_path = self.remove_pages_action = self.reset_settings_action = None
        return self

    def __eq__(self, other):
        return isinstance(other, ActionNewDocument) \
            and other.old_save_path == self.old_save_path \
            and other.remove_pages_action == self.remove_pages_action \
            and other.reset_settings_action == self.reset_settings_action
