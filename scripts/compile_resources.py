#!/usr/bin/env python

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


"""
This script compiles the resources listed in the Qt resources registry under
mtg_proxy_printer/resources/resources.qrc into an importable Python module for packaging.

For development, the codebase loads the files directly from disk,
which allows working on them without intermediate compilation steps.

Deliverables (both Python wheel files and executable bundles created via cx_Freeze)
load the resources from the compiled resources module instead.
This ensures that the Qt resources framework has access to the icon theme, translations,
and other resources (if any), regardless of packaging or installation method,
as this approach does not rely on filesystem paths.
"""

import argparse
import itertools
from pathlib import Path
import subprocess
from typing import NamedTuple, TypeVar, Iterable, Callable


main_package = "mtg_proxy_printer"
PACKAGE_PATH = (Path(__file__).parent.with_name(main_package)).resolve()
SOURCES_PATH = PACKAGE_PATH / "resources" / "resources.qrc"
TARGET_PATH = PACKAGE_PATH / "ui" / "compiled_resources.py"
T = TypeVar("T")


class Namespace(NamedTuple):
    command: Callable[[], None]


def parse_args(args: list[str] = None)-> Namespace:
    parser = argparse.ArgumentParser(
        description="Compile Qt resources into an importable module. "
                    "Compilation must be run during the packaging process"
    )
    commands = parser.add_subparsers(dest="command", help="Command to run:", required=True)
    commands.add_parser(
        "compile",
        help="Compile the resource files into an importable module"
    )
    commands.add_parser(
        "clean",
        help="Delete the compiled resources module"
    )
    parsed = parser.parse_args(args)
    parsed.command = globals()[parsed.command]
    return parsed


def split_iterable(iterable: Iterable[T], chunk_size: int, /) -> list[tuple[T, ...]]:
    """Split the given iterable into chunks of size chunk_size. Does not add padding values to the last item."""
    iterable = iter(iterable)
    return list(iter(lambda: tuple(itertools.islice(iterable, chunk_size)), ()))


def compile():
    command = ("pyside6-rcc", "--compress", "9", "--generator", "python", str(SOURCES_PATH))
    compiled = subprocess.check_output(command, universal_newlines=True)  # type: str
    # The resource compiler outputs > 15000 lines with extremely low line length.
    # Reduce the file size by removing a good percentage of those line breaks
    blocks = compiled.split("\\\n")
    chunks = split_iterable(blocks, 7)
    joined_chunks = ("".join(items) for items in chunks)
    compiled = "\\\n".join(joined_chunks)
    TARGET_PATH.write_text(compiled, "utf-8")


def clean():
    TARGET_PATH.unlink(missing_ok=True)


def main():
    args = parse_args()
    args.command()


if __name__ == "__main__":
    main()
