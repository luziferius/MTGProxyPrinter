# Copyright (C) 2021 Thomas Hess <thomas.hess@udo.edu>

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

import sys

from cx_Freeze import setup, Executable

import setup as setup_py


base = "Win32GUI" if sys.platform == "win32" else None
setup_py.setup_parameters["executables"] = [
    Executable("mtg_proxy_printer/__main__.py", base=base),
]

# Make sure that the dynamically loaded ijson backends are discovered.
setup_py.setup_parameters["options"] = {
    "build_exe": {
        "packages": ["ijson.backends"],
        "excludes": ["tkinter"],
    },
}


if __name__ == "__main__":
    setup(**setup_py.setup_parameters)
