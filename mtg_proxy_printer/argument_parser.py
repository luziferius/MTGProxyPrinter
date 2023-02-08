# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>

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

import argparse
import dataclasses
import pathlib
import typing

from . import meta_data

__all__ = [
    "parse_args",
    "Namespace",
]


@dataclasses.dataclass()
class Namespace:
    """Namespace used to mock parsed arguments for type-hinting purposes"""
    file: pathlib.Path = None
    card_data: pathlib.Path = None
    test_exit_on_launch: bool = False


def generate_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(meta_data.PROGRAMNAME)
    parser.add_argument(
        "file", action="store", nargs="?", type=pathlib.Path,
        help="Document to open at program start"
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version=f"{meta_data.PROGRAMNAME} Version {meta_data.__version__}",
        help="Show program version and exit"
    )
    parser.add_argument(
        "--test-exit-on-launch", action="store_true",
        help=f"Used for testing purposes. Causes {meta_data.PROGRAMNAME} to exit immediately after start."
    )
    parser.add_argument(
        "--card-data", type=pathlib.Path,
        help="Populate the internal card database using the 'All cards' bulk data export from the Scryfall API. "
             "Path to a plain-text JSON or GZIP compressed JSON file. See https://scryfall.com/docs/api/bulk-data for "
             "more details about the supported file format and download links."
    )
    return parser


def parse_args(args: typing.List[str] = None) -> Namespace:
    parser = generate_argument_parser()
    return parser.parse_args(args)
