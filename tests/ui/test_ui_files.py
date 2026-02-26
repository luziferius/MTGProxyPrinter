#  Copyright © 2020-2026  Thomas Hess <thomas.hess@udo.edu>
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
from xml.etree import ElementTree

import pytest
from hamcrest import *


from mtg_proxy_printer.ui.common import RESOURCE_PATH_PREFIX, HAS_COMPILED_RESOURCES

pytest.mark.skipif(
    HAS_COMPILED_RESOURCES, reason="Cannot test UI files in compiled mode, as they are unavailable"
)


@pytest.mark.parametrize("ui_file_path", (Path(RESOURCE_PATH_PREFIX)/"ui").rglob("*.ui"))
def test_button_icons_do_not_have_normaloff_value(ui_file_path: Path):
    """
    The Qt Designer program adds invalid "normaloff" attributes to set icons when loading UI files.
    The value defaults to the path relative to the resources/ui, so "." for most, and "settings_window" for UI files
    present in the "settings_window" directory.
    It is meant to be an icon variant for the "normal, disabled state", but is somehow broken.
    This test ensures that no icons have this set.
    """
    tree = ElementTree.parse(ui_file_path)
    assert_that(
        (items := tree.findall(".//normaloff/..")),
        is_(empty()),
        f"Affected icons: {', '.join(item.attrib['theme'] for item in items)}"
    )
