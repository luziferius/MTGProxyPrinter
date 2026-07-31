#  Copyright © 2020-2026  Thomas Hess <thomas.hess@udo.edu>
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

import itertools

import PySide6.QtCore

from mtg_proxy_printer.meta_data import __version__

BlockingQueuedConnection = PySide6.QtCore.Qt.ConnectionType.BlockingQueuedConnection

# Fallback for itertools.batched which was added in Python 3.12
if not hasattr(itertools, 'batched'):
    def _batched(iterable, n):
        """Batch data into tuples of length n. The last batch may be shorter."""
        it = iter(iterable)
        while batch := tuple(itertools.islice(it, n)):
            yield batch
    itertools.batched = _batched
    del _batched
