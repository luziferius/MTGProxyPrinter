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

import functools
from PyQt5.QtGui import QColor, QPalette

"""
This script was used to dump the Breeze Dark color palette.

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QColor, QPalette
import itertools
app = QApplication(["foo"])
p = app.palette()
groups = "QPalette.Disabled, QPalette.Active, QPalette.Inactive".split(", ")
roles = "QPalette.Window, QPalette.Background, QPalette.WindowText, QPalette.Foreground, QPalette.Base, " \
        "QPalette.AlternateBase, QPalette.ToolTipBase, QPalette.ToolTipText, QPalette.PlaceholderText, " \
        "QPalette.Text, QPalette.Button, QPalette.ButtonText, QPalette.BrightText, QPalette.Light, " \
        "QPalette.Midlight, QPalette.Dark, QPalette.Mid, QPalette.Shadow, QPalette.Highlight, " \
        "QPalette.HighlightedText, QPalette.Link, QPalette.LinkVisited, QPalette.NoRole".split(", ")

for group, role in itertools.product(groups, roles):
    group_value = eval(group)
    role_value = eval(role)
    c = p.color(group_value, role_value)
    print(f"breeze_dark_palette.setColor({group}, {role}, QColor{c.red(), c.green(), c.blue()})")
"""


@functools.lru_cache(maxsize=1)
def get_dark_palette():
    breeze_dark_palette = QPalette()

    breeze_dark_palette.setColor(QPalette.Disabled, QPalette.Window, QColor(40, 44, 48))
    breeze_dark_palette.setColor(QPalette.Disabled, QPalette.Background, QColor(40, 44, 48))
    breeze_dark_palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(110, 113, 115))
    breeze_dark_palette.setColor(QPalette.Disabled, QPalette.Foreground, QColor(110, 113, 115))
    breeze_dark_palette.setColor(QPalette.Disabled, QPalette.Base, QColor(26, 29, 31))
    breeze_dark_palette.setColor(QPalette.Disabled, QPalette.AlternateBase, QColor(33, 36, 39))
    breeze_dark_palette.setColor(QPalette.Disabled, QPalette.ToolTipBase, QColor(49, 54, 59))
    breeze_dark_palette.setColor(QPalette.Disabled, QPalette.ToolTipText, QColor(252, 252, 252))
    breeze_dark_palette.setColor(QPalette.Disabled, QPalette.PlaceholderText, QColor(252, 252, 252))
    breeze_dark_palette.setColor(QPalette.Disabled, QPalette.Text, QColor(101, 103, 104))
    breeze_dark_palette.setColor(QPalette.Disabled, QPalette.Button, QColor(47, 51, 56))
    breeze_dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(114, 118, 121))
    breeze_dark_palette.setColor(QPalette.Disabled, QPalette.BrightText, QColor(255, 255, 255))
    breeze_dark_palette.setColor(QPalette.Disabled, QPalette.Light, QColor(62, 68, 74))
    breeze_dark_palette.setColor(QPalette.Disabled, QPalette.Midlight, QColor(53, 58, 63))
    breeze_dark_palette.setColor(QPalette.Disabled, QPalette.Dark, QColor(24, 26, 28))
    breeze_dark_palette.setColor(QPalette.Disabled, QPalette.Mid, QColor(35, 39, 42))
    breeze_dark_palette.setColor(QPalette.Disabled, QPalette.Shadow, QColor(17, 19, 20))
    breeze_dark_palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(40, 44, 48))
    breeze_dark_palette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(110, 113, 115))
    breeze_dark_palette.setColor(QPalette.Disabled, QPalette.Link, QColor(26, 70, 101))
    breeze_dark_palette.setColor(QPalette.Disabled, QPalette.LinkVisited, QColor(68, 48, 81))
    breeze_dark_palette.setColor(QPalette.Disabled, QPalette.NoRole, QColor(0, 0, 0))

    breeze_dark_palette.setColor(QPalette.Active, QPalette.Window, QColor(42, 46, 50))
    breeze_dark_palette.setColor(QPalette.Active, QPalette.Background, QColor(42, 46, 50))
    breeze_dark_palette.setColor(QPalette.Active, QPalette.WindowText, QColor(252, 252, 252))
    breeze_dark_palette.setColor(QPalette.Active, QPalette.Foreground, QColor(252, 252, 252))
    breeze_dark_palette.setColor(QPalette.Active, QPalette.Base, QColor(27, 30, 32))
    breeze_dark_palette.setColor(QPalette.Active, QPalette.AlternateBase, QColor(35, 38, 41))
    breeze_dark_palette.setColor(QPalette.Active, QPalette.ToolTipBase, QColor(49, 54, 59))
    breeze_dark_palette.setColor(QPalette.Active, QPalette.ToolTipText, QColor(252, 252, 252))
    breeze_dark_palette.setColor(QPalette.Active, QPalette.PlaceholderText, QColor(252, 252, 252))
    breeze_dark_palette.setColor(QPalette.Active, QPalette.Text, QColor(252, 252, 252))
    breeze_dark_palette.setColor(QPalette.Active, QPalette.Button, QColor(49, 54, 59))
    breeze_dark_palette.setColor(QPalette.Active, QPalette.ButtonText, QColor(252, 252, 252))
    breeze_dark_palette.setColor(QPalette.Active, QPalette.BrightText, QColor(255, 255, 255))
    breeze_dark_palette.setColor(QPalette.Active, QPalette.Light, QColor(64, 70, 76))
    breeze_dark_palette.setColor(QPalette.Active, QPalette.Midlight, QColor(54, 59, 64))
    breeze_dark_palette.setColor(QPalette.Active, QPalette.Dark, QColor(25, 27, 29))
    breeze_dark_palette.setColor(QPalette.Active, QPalette.Mid, QColor(37, 41, 44))
    breeze_dark_palette.setColor(QPalette.Active, QPalette.Shadow, QColor(18, 20, 21))
    breeze_dark_palette.setColor(QPalette.Active, QPalette.Highlight, QColor(61, 174, 233))
    breeze_dark_palette.setColor(QPalette.Active, QPalette.HighlightedText, QColor(252, 252, 252))
    breeze_dark_palette.setColor(QPalette.Active, QPalette.Link, QColor(29, 153, 243))
    breeze_dark_palette.setColor(QPalette.Active, QPalette.LinkVisited, QColor(155, 89, 182))
    breeze_dark_palette.setColor(QPalette.Active, QPalette.NoRole, QColor(0, 0, 0))

    breeze_dark_palette.setColor(QPalette.Inactive, QPalette.Window, QColor(42, 46, 50))
    breeze_dark_palette.setColor(QPalette.Inactive, QPalette.Background, QColor(42, 46, 50))
    breeze_dark_palette.setColor(QPalette.Inactive, QPalette.WindowText, QColor(252, 252, 252))
    breeze_dark_palette.setColor(QPalette.Inactive, QPalette.Foreground, QColor(252, 252, 252))
    breeze_dark_palette.setColor(QPalette.Inactive, QPalette.Base, QColor(27, 30, 32))
    breeze_dark_palette.setColor(QPalette.Inactive, QPalette.AlternateBase, QColor(35, 38, 41))
    breeze_dark_palette.setColor(QPalette.Inactive, QPalette.ToolTipBase, QColor(49, 54, 59))
    breeze_dark_palette.setColor(QPalette.Inactive, QPalette.ToolTipText, QColor(252, 252, 252))
    breeze_dark_palette.setColor(QPalette.Inactive, QPalette.PlaceholderText, QColor(252, 252, 252))
    breeze_dark_palette.setColor(QPalette.Inactive, QPalette.Text, QColor(252, 252, 252))
    breeze_dark_palette.setColor(QPalette.Inactive, QPalette.Button, QColor(49, 54, 59))
    breeze_dark_palette.setColor(QPalette.Inactive, QPalette.ButtonText, QColor(252, 252, 252))
    breeze_dark_palette.setColor(QPalette.Inactive, QPalette.BrightText, QColor(255, 255, 255))
    breeze_dark_palette.setColor(QPalette.Inactive, QPalette.Light, QColor(64, 70, 76))
    breeze_dark_palette.setColor(QPalette.Inactive, QPalette.Midlight, QColor(54, 59, 64))
    breeze_dark_palette.setColor(QPalette.Inactive, QPalette.Dark, QColor(25, 27, 29))
    breeze_dark_palette.setColor(QPalette.Inactive, QPalette.Mid, QColor(37, 41, 44))
    breeze_dark_palette.setColor(QPalette.Inactive, QPalette.Shadow, QColor(18, 20, 21))
    breeze_dark_palette.setColor(QPalette.Inactive, QPalette.Highlight, QColor(31, 72, 94))
    breeze_dark_palette.setColor(QPalette.Inactive, QPalette.HighlightedText, QColor(252, 252, 252))
    breeze_dark_palette.setColor(QPalette.Inactive, QPalette.Link, QColor(29, 153, 243))
    breeze_dark_palette.setColor(QPalette.Inactive, QPalette.LinkVisited, QColor(155, 89, 182))
    breeze_dark_palette.setColor(QPalette.Inactive, QPalette.NoRole, QColor(0, 0, 0))

    return breeze_dark_palette
