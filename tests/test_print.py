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

from pathlib import Path

import pytest

import mtg_proxy_printer.print
from mtg_proxy_printer.model.document import Document

from hamcrest import *

from mtg_proxy_printer.ui.dialogs import SavePDFDialog
from mtg_proxy_printer.ui.main_window import MainWindow
from tests.ui.test_main_window import main_window


@pytest.fixture
def save_pdf_dialog(main_window: MainWindow) -> SavePDFDialog:
    dialog = SavePDFDialog(main_window, main_window.document)
    return dialog


def test_export_pdf_creates_a_pdf_file(tmp_path: Path, save_pdf_dialog: SavePDFDialog):
    main_window = save_pdf_dialog.parent()
    file_path = tmp_path/"test.pdf"
    mtg_proxy_printer.print.export_pdf(main_window.document, str(file_path), save_pdf_dialog)
    assert_that(file_path.is_file(), is_(True))
    assert_that(file_path.read_bytes()[:5], equal_to(b"%PDF-"))
