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

# This list was extracted from ijson.backends._default_backend()
# The module imports one of those at run-time and then deletes the list of available backends,
# therefore it is saved here, as it is inaccessible at runtime using the inspect module
backends = ('yajl2_c', 'yajl2_cffi', 'yajl2', 'yajl', 'python')

hiddenimports = [
    "ijson.backends"
]
hiddenimports += [f"ijson.backends.{backend}" for backend in backends]
