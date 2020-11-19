# Copyright (C) 2019 Thomas Hess <thomas.hess@udo.edu>

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

import typing

import mtg_proxy_printer.logger


class Namespace(typing.NamedTuple):
    """Mocks parsed command line arguments."""
    verbose: bool
    cutelog_integration: bool


def setup_logging_for_testing():
    mtg_proxy_printer.logger.configure_root_logger(Namespace(verbose=False, cutelog_integration=True))
    mtg_proxy_printer.logger.root_logger.info("Configured logging system for test runs.")
    mtg_proxy_printer.logger.root_logger.info(__name__)
