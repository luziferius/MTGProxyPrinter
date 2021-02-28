#!/usr/bin/env python3

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
Thin wrapper to run main() from the source checkout.
"""

import pathlib
import sys

# Make sure to find this checkout, and not any system- or user-wide installed versions that may be present
root_path = pathlib.Path(__file__).parent.absolute().resolve()
sys.path.insert(0, str(root_path))

from mtg_proxy_printer.__main__ import main  # noqa

main()
