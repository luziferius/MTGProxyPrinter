
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
