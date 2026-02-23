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

Element = ElementTree.Element
pytest.mark.skipif(
    HAS_COMPILED_RESOURCES, reason="Cannot test UI files in compiled mode, as they are unavailable"
)


@pytest.mark.parametrize("ui_file_path", (Path(RESOURCE_PATH_PREFIX)/"ui").rglob("*.ui"))
def test_button_icons_do_not_have_normaloff_value(ui_file_path: Path):
    """
    The Qt5 Designer program adds invalid "normaloff" attributes to set icons when loading UI files.
    This seems to be fixed in the Qt6 Designer, but keep this test for now.

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


def _format_signal_slot_connection(item: Element) -> str:
    return (f"{item.find('sender').text}.{item.find('signal').text}"
            f"→{item.find('receiver').text}.{item.find('slot').text}")


@pytest.mark.parametrize("ui_file_path", (Path(RESOURCE_PATH_PREFIX)/"ui").rglob("*.ui"))
def test_ui_files_have_no_hints(ui_file_path: Path):
    """
    Qt Designer automatically adds optional <hints> sections like these for Signal/Slot connections:

    <hints>
    <hint type="sourcelabel">
     <x>20</x>
     <y>20</y>
    </hint>
    <hint type="destinationlabel">
     <x>20</x>
     <y>20</y>
    </hint>
    </hints>

    Ensure that the UI files are minimal, and fail if those are present.
    """
    tree = ElementTree.parse(ui_file_path)
    assert_that(
        (items := tree.findall(".//hints/..")),
        is_(empty()),
        f"Affected connections: {', '.join(map(_format_signal_slot_connection, items))}"
    )
