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
It uses the existing setup.py and extends the parameters to allow building stand-alone executables using cx_Freeze.
"""
import atexit
import pathlib
import re
import sys

from cx_Freeze import setup, Executable

import setup as setup_py

meta_data = pathlib.Path(f"{setup_py.main_package}/meta_data.py").read_text()
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
setup_py.setup_parameters["executables"] = [
    Executable(
        f"{setup_py.main_package}/__main__.py",
        base=base,
        target_name='MTGProxyPrinter',
        shortcut_name='MTGProxyPrinter',
        shortcut_dir='StartMenuFolder',
    ),
]


setup_py.setup_parameters["options"] = {
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
        "excludes": [
            f"{setup_py.main_package}.resources",  # Do not include the raw resources as individual files
            "distutils",
            "lib2to3",
            "pep517",
            "pytest",
            "pydoc_data",
            "tkinter",
            "toml",
            "unittest",
            "sqlite3.test",  # Ignore the internal test suite
            "pint.testsuite",  # Ignore the internal test suite
            "importlib_metadata",
            "ctypes.macholib",  # Empty package with readme and download scripts
            "ctypes.test",
            # Unused PySide6 components
            "PySide6.plugins.assetimporters",
            "PySide6.plugins.sqldrivers",  # Use Python native sqlite3 module instead
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
        ],
        "optimize": 2,
    },
}


if __name__ == "__main__":
    # Perform in-tree resource compilation.
    resources_path = pathlib.Path(__file__).parent / setup_py.main_package / "ui"
    resources_path = resources_path.resolve()
    resources_file = setup_py.BuildWithQtResources.compile_resources(resources_path)
    atexit.register(resources_file.unlink, True)
    setup(**setup_py.setup_parameters)
