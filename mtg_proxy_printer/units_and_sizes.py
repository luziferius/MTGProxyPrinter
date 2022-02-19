# Copyright (C) 2022 Thomas Hess <thomas.hess@udo.edu>

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

"""Contains some constants, like the card size"""
import pint

unit_registry = pint.UnitRegistry()
DPI: pint.Quantity = 300 / unit_registry.inch
IMAGE_WIDTH: pint.Quantity = unit_registry("63 millimeter")
IMAGE_HEIGHT: pint.Quantity = unit_registry("88 millimeter")
