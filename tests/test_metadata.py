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
import re

from hamcrest import *
import pytest

import mtg_proxy_printer
from mtg_proxy_printer import meta_data


def _skip_if_not_release_version(changelog_first_entry):
    if re.match(r'# Next version.+', changelog_first_entry):
        pytest.skip("Not on a release check-in.")


def test_application_version_in_sync_with_changelog():
    """
    This test verifies that the version mentioned in the top-most changelog entry matches the version in the metadata.
    It automatically skips, if the top-most changelog entry is not that of a released version
    """
    changelog_file = Path(mtg_proxy_printer.__file__).parent.parent/"doc"/"changelog.md"
    assert_that(changelog_file.is_file(), is_(True), "Setup failed. Changelog not found.")
    changelog_text = changelog_file.read_text("utf-8")
    changelog_first_entry = changelog_text.splitlines()[2]
    is_released = re.match(r"# Version (?P<version>(\d+\.){2}\d+).+", changelog_first_entry)
    _skip_if_not_release_version(changelog_first_entry)
    if not is_released:
        pytest.fail("Changelog header malformed.")
    version_prefix = meta_data.__version__.split("+")[0]
    assert_that(
        is_released["version"],
        is_(equal_to(version_prefix)),
        "Version in metadata.py does not match the latest changelog entry header"
    )


def test_changelog_versions_match_header_name_reference():
    """
    This test verifies that the version mentioned in the top-most changelog entry matches the version anchor.
    It automatically skips, if the top-most changelog entry is not that of a released version
    """
    changelog_file = Path(mtg_proxy_printer.__file__).parent.parent/"doc"/"changelog.md"
    assert_that(changelog_file.is_file(), is_(True), "Setup failed. Changelog not found.")
    changelog_text = changelog_file.read_text("utf-8")
    changelog_first_entry = changelog_text.splitlines()[2]
    _skip_if_not_release_version(changelog_first_entry)

    section_re = re.match(
        r'^# Version (?P<version>(\d+\.){2}\d+) (\(\d{4}-\d{2}-\d{2}\)) {2}'
        r'<a name="v(?P<version_ref>(\d+_){2}\d+)"></a>$', changelog_first_entry)
    if not section_re:
        pytest.fail("Header malformed, Version not found")
    assert_that(
        section_re["version"].split("."),
        contains_exactly(*section_re["version_ref"].split("_")),
        f"Changelog header reference does not match version in line: {changelog_first_entry}"
    )
