# Copyright (C) 2020 Thomas Hess <thomas.hess@udo.edu>

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
from pathlib import Path
import dataclasses

import mtg_proxy_printer.card_info_importer
import mtg_proxy_printer.model.carddb


@dataclasses.dataclass()
class Namespace:
    database_path: Path
    card_data: Path


def parse_args() -> Namespace:
    parser = argparse.ArgumentParser(description="Benchmark card database import speed")
    parser.add_argument(
        "database_path", type=Path,
        help="Path to the test database. Beware: Any file at that location will be deleted without prompt!")
    parser.add_argument(
        "card_data",type=Path,
        help="'All cards' bulk data export from the Scryfall API. May be plain-text JSON or GZIP compressed JSON.")
    return parser.parse_args()


to_be_profiled_functions = {
    mtg_proxy_printer.card_info_importer.CardInfoDownloader: [
        "populate_database",
    ],
    mtg_proxy_printer.card_info_importer: [
        "_insert_language",
        "_insert_card",
        "_insert_set",
        "_insert_face_name",
        "_insert_card_faces",
        "_insert_language",
        "_should_skip_card",
    ],
}


def is_running_with_kernprof() -> bool:
    """Determine if the script was called using kernprof."""
    # Implementation detail: On the author’s machine, kernprof not only injects the profiler
    # with name 'profile" into the globals, but also changes the type of __builtins__ from 'module' to 'dict'…!
    if isinstance(__builtins__, dict):
        running_with_kernprof = "profile" in __builtins__.keys()
    else:
        running_with_kernprof = hasattr(__builtins__, "profile")
    return running_with_kernprof


def inject_line_profiler():
    if isinstance(__builtins__, dict):
        profile = __builtins__["profile"]
    else:
        profile = __builtins__.profile
    for module_, function_list in to_be_profiled_functions.items():
        for func_name in function_list:
            try:
                func = getattr(module_, func_name)
            except AttributeError:
                import warnings
                warnings.warn(f"""Function "{func_name}" in module/class "{module_.__name__}" not found, skipping.""")
            else:
                func = profile(func)
                setattr(module_, func_name, func)


if __name__ == "__main__":
    if is_running_with_kernprof():
        print("Running with kernprof. Injecting profile decorator.")
        inject_line_profiler()
    args = parse_args()
    if args.database_path.exists():
        print("Deleting existing database…")
        args.database_path.unlink()
    print("Creating new database…")
    cdb = mtg_proxy_printer.model.carddb.CardDatabase(args.database_path)
    cid = mtg_proxy_printer.card_info_importer.CardInfoDownloader(cdb)
    print("Creating JSON data generator…")
    json_data = cid.read_json_card_data(args.card_data)
    print("Starting benchmark…")
    cid.populate_database(cdb, json_data)
    print("Done")

