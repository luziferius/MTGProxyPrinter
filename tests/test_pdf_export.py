
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

from hamcrest import *

from tests.hasgetter import has_getters

from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.print import PDFPrinter



def test_pdf_export_does_not_raise_exception(tmp_path: Path, document: Document):
    pdf_path = tmp_path/"test.pdf"
    printer = PDFPrinter(document, str(pdf_path))
    printer.print_document()
    assert_that(
        pdf_path,
        has_getters({
            "is_file": equal_to(True),
            "stat": has_property("st_size", greater_than(0)),
        })
    )
