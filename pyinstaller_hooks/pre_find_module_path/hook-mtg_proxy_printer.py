# Copyright (C) 2020, 2021 Thomas Hess <thomas.hess@udo.edu>

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
This hook compiles the Qt resources into the compiled_resources.py module.
When performing a regular installation using pip3, the module is generated during the setup by setup.py.

When bundling MTGProxyPrinter using PyInstaller, the compilation has to be performed before the imports are determined,
so use the pre_find_module_path hook to generate it at the very beginning of the packaging process.
"""

import atexit
from pathlib import Path
import sys

from PyInstaller.utils.hooks import logger

# Make sure to insert the checkout root to the path. Without this, the import below may find an installed version
# instead of the checkout, if this program is already installed via pip. This is required to properly determine
# the save path for the compiled resources.
root_dir = str(Path(__file__).parent.parent.parent.absolute().resolve())
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import mtg_proxy_printer.ui  # noqa


def pre_find_module_path(api):
    logger.info("About to compile the Qt resource file")
    import setup
    # ui.__file__ points to the package’s __init__.py. Go a level up to get the package directory path
    target_path = Path(mtg_proxy_printer.ui.__file__).parent/"compiled_resources.py"
    atexit.register(target_path.unlink)
    setup.compile_resources(target_path)
    logger.info("Compiling resource file finished")
