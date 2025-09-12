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


from collections.abc import Iterable
import xml.etree.ElementTree
import os
from pathlib import Path

from hamcrest import *
import pytest
from mtg_proxy_printer.ui.common import RESOURCE_PATH_PREFIX


if os.getenv("MTGPROXYPRINTER_SKIP_RESOURCE_TESTS"):
    pytest.skip(
        "Skipping raw resource file tests when running tests using compiled resources",
        allow_module_level=True
    )

def list_dir(directory: Path) -> Iterable[Path]:
    walker = os.walk(directory)
    for subdir, _, files in walker:
        for file_name in files:
            yield Path(os.path.relpath(subdir, directory), file_name)


@pytest.fixture
def resource_path() -> Path:
    directory = Path(RESOURCE_PATH_PREFIX)
    qrc_file = directory / "resources.qrc"
    return qrc_file


def test_resource_registry_exists(resource_path: Path):
    assert_that(resource_path.is_file(), is_(True))


def test_all_resources_listed_in_resources_qrc_exist_as_files(resource_path: Path):
    resource_document = xml.etree.ElementTree.ElementTree(file=resource_path)
    file_nodes = resource_document.findall("qresource/file")
    base_dir = resource_path.parent
    for node in file_nodes:
        path = base_dir/node.text
        assert_that(path.exists(), is_(True), f"Listed entry does not exist: {path}")
        assert_that(path.is_file(), is_(True), f"Listed entry not a regular file {path}")


def test_no_duplicates_in_resources_qrc(resource_path: Path):
    resource_document = xml.etree.ElementTree.ElementTree(file=resource_path)
    listed_paths = list(node.text for node in resource_document.findall("qresource/file"))
    deduplicated = set(listed_paths)
    assert_that(listed_paths, has_length(len(deduplicated)), "resources.qrc contains unexpected duplicates")


def test_all_resource_files_are_listed_in_resources_qrc(resource_path: Path):
    base_dir = resource_path.parent
    resource_document = xml.etree.ElementTree.ElementTree(file=resource_path)
    listed_paths = set(Path(node.text) for node in resource_document.findall("qresource/file"))
    existing_files = list_dir(base_dir)
    for file in existing_files:
        suffix = file.suffix.casefold()
        if file.name == "resources.qrc" or suffix in {".ui", ".ts", ".rtf", ".qm"}:
            continue
        assert_that(file, is_in(listed_paths), "File not listed in resources.qrc")
