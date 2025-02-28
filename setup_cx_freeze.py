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
resource_path = ROOT_DIR / "resources.bak"
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

    # All unused PyQt components
    "PyQt5.QtXmlPatterns",
    "PyQt5.QtNfc",
    "PyQt5.QtQml",
    "PyQt5.QtSql",
    "PyQt5.Qt3DAnimation",
    "PyQt5.Qt3DCore",
    "PyQt5.Qt3DExtras",
    "PyQt5.Qt3DInput",
    "PyQt5.Qt3DLogic",
    "PyQt5.Qt3DRender",
    "PyQt5.QtBluetooth",
    "PyQt5.QtChart",
    "PyQt5.QtDataVisualisation",
    "PyQt5.QtLocation",
    "PyQt5.QtMultimedia",
    "PyQt5.QtMultimediaWidgets",
    "PyQt5.QtNetwork",
    "PyQt5.QtNetworkAuth",
    "PyQt5.QtOpenGL",
    "PyQt5.QtPositioning",
    "PyQt5.QtPurchasing",
    "PyQt5.QtQuick",
    "PyQt5.QtQuickWidgets",
    "PyQt5.QtRemoteObjects",
    "PyQt5.QtSensors",
    "PyQt5.QtSerialPort",
    "PyQt5.QtTest",
    "PyQt5.QtWebChannel",
    "PyQt5.QtWebEngine",
    "PyQt5.QtWebEngineCore",
    "PyQt5.QtWebEngineWidgets",
    "PyQt5.QtWebKit",
    "PyQt5.QtWebKitWidgets",
    "PyQt5.QtWebSockets",
    "PyQt5.uic.port_v2",
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
