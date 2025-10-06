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


"""
This module provides support for freezing the application using cx_Freeze.
"""
import pathlib
import re
import sys

from cx_Freeze import setup, Executable

ROOT_DIR = pathlib.Path(__file__).parent
resource_path = ROOT_DIR / "resources"
main_package = "mtg_proxy_printer"
meta_data = (ROOT_DIR/main_package/"meta_data.py").read_text()
version = re.search(
    r"""^__version__\s*=\s*"(.*)"\s*""",
    meta_data,
    re.M
    ).group(1)
project_name = re.search(
    r"""^PROGRAMNAME\s*=\s*"(.*)"\s*""",
    meta_data,
    re.M
    ).group(1)


base = "Win32GUI" if sys.platform == "win32" else None

excludes  = [
    f"{main_package}.resources",  # Do not include the raw resources as individual files
    "distutils",
    "ijson.benchmark",  # Ignore the benchmark script added after ijson 3.2.3
    "importlib_metadata",
    "lib2to3",
    "pep517",
    "pint.testsuite",  # Ignore the internal test suite
    "pydoc_data",
    "pytest",
    "sqlite3.test",  # Ignore the internal test suite
    "tkinter",
    "toml",
    # Empty package with readme and download scripts
    "ctypes.test",
    # Unused PySide6 components
    "PySide6.glue",
    "PySide6.include",
    "PySide6.metatypes",
    "PySide6.plugins.assetimporters",
    "PySide6.plugins.canbus",
    "PySide6.plugins.designer",
    "PySide6.plugins.geometryloaders",
    "PySide6.plugins.geoservices",
    "PySide6.plugins.multimedia",
    "PySide6.plugins.networkinformation",
    "PySide6.plugins.position",
    "PySide6.plugins.qmltooling",
    "PySide6.plugins.scxmldatamodel",
    "PySide6.plugins.sensors",
    "PySide6.plugins.sqldrivers",  # Use Python native sqlite3 module instead
    "PySide6.plugins.tls",
    "PySide6.qml",
    "PySide6.QtAsyncio",
    "PySide6.resources",
    "PySide6.scripts",
    "PySide6.support",
    "PySide6.translations.qtwebengine_locales",
    "PySide6.typesystems",
]

if sys.platform == "win32":
    excludes += [
        "platformdirs.android",
        "platformdirs.macos",
        "platformdirs.unix",
    ]


def get_icon() -> str:
    icon_path = resource_path / "icons" / "MTGPP.png"
    if sys.platform == "win32":
        dest = ROOT_DIR/"MTGPP.ico"
        if not dest.exists():
            from PIL import Image
            with Image.open(icon_path) as src:
                src.save(dest, "ICO")
        return str(dest)
    else:
        return str(icon_path)


icon = get_icon()

setup_parameters = {
    "executables": [
        Executable(
            f"{main_package}/__main__.py",
            base=base,
            target_name=project_name,
            shortcut_name=project_name,
            shortcut_dir='StartMenuFolder',
            icon=icon,
            copyright="© 2020-2024 Thomas Hess <thomas.hess@udo.edu>",
        ),
    ],
    "options": {
        "bdist_msi": {
            # The GUID upgrade_code token is used by Windows to identify the application being installed.
            # When another MSI package with a known, installed GUID is installed, it is assumed to be an update,
            # causing the removal of the previous package, allowing smooth updates. It has to be enclosed in {}.
            "upgrade_code": "{15a9e385-f6ab-4aa4-8ef1-3f2cf5c193a8}",
            "target_name": project_name,
            "skip_build": True,
            "install_icon": icon,
            "license_file": resource_path / "gpl-3.0.rtf"
        },
        "build_exe": {
            "packages": [
                # Make sure that the dynamically loaded ijson backends are discovered.
                "ijson.backends",
            ],
            "excludes": excludes,
            "optimize": 2,
        },
    },
}


if __name__ == "__main__":
    setup(**setup_parameters)
