# Copyright (C) 2021-2023 Thomas Hess <thomas.hess@udo.edu>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
This module provides support for freezing the application using cx_Freeze.
"""
import pathlib
import re
import sys

from cx_Freeze import setup, Executable


main_package = "mtg_proxy_printer"
meta_data = pathlib.Path(f"{main_package}/meta_data.py").read_text()
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
    "lib2to3",
    "pep517",
    "pytest",
    "pydoc_data",
    "tkinter",
    "toml",
    "sqlite3.test",  # Ignore the internal test suite
    "pint.testsuite",  # Ignore the internal test suite
    "ijson.benchmark",  # Ignore the benchmark script added after ijson 3.2.3
    "importlib_metadata",
    # Empty package with readme and download scripts
    "ctypes.test",
    # Unused PySide6 components
    "PySide6.plugins.achssetimporters",
    "PySide6.plugibns.sqldrivers",  # Use Python native sqlite3 module instead
    "PySide6.plugins.qmltooling",
    "PySide6.plugins.designer",
    "PySide6.plugins.tls",
    "PySide6.glue",
    "PySide6.include",
    "PySide6.scripts",
    "PySide6.support",
    "PySide6.metatypes",
    "PySide6.qml",
    "PySide6.typesystems",
    "PySide6.resources",
    # Unused PySide6 modules
    "PySide6.QtSql",
    "PySide6.QtDBus",
    "PySide6.QtDesigner",
    "PySide6.QtTest",
    "PySide6.QtQml",
    "PySide6.QtQuick",
    "PySide6.QtQuickControls2",
    "PySide6.QtQuickWidgets",
    "PySide6.QtNetwork",
    "PySide6.QtLanguageServer",

]

if sys.platform == "win32":
    excludes += [
        "platformdirs.android",
        "platformdirs.macos",
        "platformdirs.unix",
    ]


setup_parameters = {
    "executables": [
        Executable(
            f"{main_package}/__main__.py",
            base=base,
            target_name=project_name,
            shortcut_name=project_name,
            shortcut_dir='StartMenuFolder',
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
