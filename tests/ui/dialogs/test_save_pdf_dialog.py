#  Copyright © 2020-2025.  Thomas Hess <thomas.hess@udo.edu>
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
from unittest.mock import MagicMock

import pytest
from hamcrest import *

from mtg_proxy_printer.ui.dialogs import SavePDFDialog


@pytest.mark.parametrize("save_path, expected_name", [
    (None, ""),
    (Path("/tmp/foo"), "foo"),
    (Path("/tmp/foo.mtgproxies"), "foo"),
    (Path("/tmp/foo.bar.mtgproxies"), "foo.bar.pdf"),
])
def test_default_pdf_file_name(save_path: Path, expected_name: str):
    document = MagicMock()
    document.save_file_path = save_path
    assert_that(
        SavePDFDialog.get_preferred_file_name(document),
        is_(equal_to(expected_name))
    )
