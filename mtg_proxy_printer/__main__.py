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


# Import and implicitly load the settings first, before importing any modules that pull in GUI classes.
import mtg_proxy_printer.settings
import mtg_proxy_printer.application


# Workaround that puts the Application instance into the module scope. This prevents issues with the garbage collector
# when main() is left. Without, the Python GC interferes with Qt’s memory management and may cause segmentation faults
# on application exit.
_app = None


def main():
    global _app
    _app = mtg_proxy_printer.application.Application()


if __name__ == "__main__":
    main()
