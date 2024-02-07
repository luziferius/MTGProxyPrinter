# Copyright (C) 2020-2024 Thomas Hess <thomas.hess@udo.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys

import platformdirs

from mtg_proxy_printer.meta_data import PROGRAMNAME

data_directories = platformdirs.PlatformDirs(PROGRAMNAME)


def migrate_from_old_appdirs():
    # Skip migration, if not applicable
    old_logs = data_directories.user_cache_path / "log"
    if sys.platform != "linux" or not old_logs.exists():
        return
    import shutil
    data_directories.user_log_path.mkdir(parents=True, exist_ok=True)
    new_log_path = data_directories.user_log_path
    for item in old_logs.glob("*"):
        if (new_log_path/item).exists():
            item.unlink()  # New location already exists, cannot migrate. Simply prune the old log file
        else:
            shutil.move(item, new_log_path)
    old_logs.rmdir()
