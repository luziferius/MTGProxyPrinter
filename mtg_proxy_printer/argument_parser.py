# Copyright (C) 2021 Thomas Hess <thomas.hess@udo.edu>

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

import mtg_proxy_printer.meta_data

__all__ = [
    "parse_args",
    "Namespace",
]


@dataclasses.dataclass()
class Namespace:
    """Namespace used to mock parsed arguments for type-hinting purposes"""
    file: pathlib.Path = None


def generate_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(mtg_proxy_printer.meta_data.PROGRAMNAME)
    parser.add_argument(
        "file", action="store", nargs="?", type=pathlib.Path,
        help="Document to open at program start"
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version=f"{mtg_proxy_printer.meta_data.PROGRAMNAME} Version {mtg_proxy_printer.meta_data.__version__}",
        help="Show program version and exit"
    )
    return parser


def parse_args(args: typing.List[str] = None) -> Namespace:
    parser = generate_argument_parser()
    return parser.parse_args(args)
