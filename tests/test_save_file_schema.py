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
from hamcrest import *

import mtg_proxy_printer.model.document


@pytest.mark.parametrize(
    "document_schema",
    Path(mtg_proxy_printer.model.document.__file__).parent.glob("document-v*.sql")
)
def test_user_version_in_schema_matches_version_in_file_name(document_schema: Path):
    schema_version = document_schema.name.split("-v")[1].split(".")[0]
    content = document_schema.read_text("utf-8")
    assert_that(
        content,
        has_string(matches_regexp(rf"PRAGMA user_version\s*=\s*{schema_version};")),
        "Version mismatch between file name and user_version"
    )

