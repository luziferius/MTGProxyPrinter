# Copyright (C) 2018,2019 Thomas Hess <thomas.hess@udo.edu>

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

import logging
import logging.handlers
import sys

from .meta_data import PROGRAMNAME

root_logger = logging.getLogger(PROGRAMNAME)
LOG_FORMAT = "%(asctime)s %(levelname)s - %(name)s - %(message)s"


def get_logger(full_module_path: str) -> logging.Logger:
    """
    Returns a logger instance for the given module __name__.
    """
    module_path = ".".join(full_module_path.split(".")[1:])
    return root_logger.getChild(module_path)


def configure_root_logger(args):
    """
    Initialize the logging system.
    :param args: Namespace object, parsed command line arguments
    """
    root_logger.setLevel(1)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    root_logger.addHandler(handler)
    if args.cutelog_integration:
        socket_handler = logging.handlers.SocketHandler("127.0.0.1", 19996)  # default listening address
        root_logger.addHandler(socket_handler)
        root_logger.info(f"""Connected logger "{root_logger.name}" to local log server.""")
