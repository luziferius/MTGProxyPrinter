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


from mtg_proxy_printer.meta_data import __version__

from PySide6.QtCore import Qt
ConnectionType = Qt.ConnectionType


def ConnectionType__or__(self: ConnectionType, other: ConnectionType) -> ConnectionType:
    if not isinstance(other, ConnectionType):
        raise TypeError(
            f"unsupported operand type(s) for |: '{ConnectionType.__name__}' and '{other.__class__.__name__}")
    if self == other:
        return self
    non_flag_self = self.value & 0x7
    non_flag_other = other.value & 0x7
    self_is_flags_only = self.value and not non_flag_self
    other_is_flags_only = other.value and not non_flag_other
    if non_flag_self != non_flag_other and not (self_is_flags_only or other_is_flags_only):
        raise ValueError(
            f"Cannot combine two distinct members of {ConnectionType.__name__}: '{self}' and '{other}'")
    return ConnectionType(self.value | other.value)


ConnectionType.__or__ = ConnectionType__or__
AutoConnection: ConnectionType = ConnectionType.AutoConnection | ConnectionType.UniqueConnection
DirectConnection: ConnectionType = ConnectionType.DirectConnection | ConnectionType.UniqueConnection
QueuedConnection: ConnectionType = ConnectionType.QueuedConnection | ConnectionType.UniqueConnection
BlockingQueuedConnection: ConnectionType = ConnectionType.BlockingQueuedConnection | ConnectionType.UniqueConnection
