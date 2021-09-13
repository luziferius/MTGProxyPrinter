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

import argparse
from pathlib import Path
import dataclasses

import mtg_proxy_printer.card_info_downloader
import mtg_proxy_printer.model.carddb


@dataclasses.dataclass()
class Namespace:
    database_path: Path
    card_data: Path
    keep: bool


def parse_args() -> Namespace:
    parser = argparse.ArgumentParser(description="Benchmark card database import speed")
    parser.add_argument(
        "database_path", type=Path,
        help="Path to the test database. Beware: Any file at that location will be deleted without prompt!")
    parser.add_argument(
        "card_data", type=Path,
        help="'All cards' bulk data export from the Scryfall API. May be plain-text JSON or GZIP compressed JSON.")
    parser.add_argument(
        "-k", "--keep", action="store_true",
        help="Re-use an existing database, performing an in-place card data update, "
             "instead of populating an empty, new database.")
    return parser.parse_args()


to_be_profiled_functions = {
    mtg_proxy_printer.card_info_downloader.CardInfoDownloadWorker: [
        "populate_database",
    ],
    mtg_proxy_printer.card_info_downloader: [
        "_insert_set",
        "_insert_card_faces",
        "_should_skip_card",
        "_clean_unused_data",
        "_remove_card"
    ],
    # Bypass the lru_cache
    mtg_proxy_printer.card_info_downloader._insert_card: [
        "__wrapped__",
    ],
    mtg_proxy_printer.card_info_downloader._insert_printing: [
        "__wrapped__",
    ],
    mtg_proxy_printer.card_info_downloader._insert_face_name: [
        "__wrapped__",
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
    if args.database_path.exists() and not args.keep:
        print("Deleting existing database…")
        args.database_path.unlink()
    if not args.database_path.exists():
        print("Creating new database…")
    elif args.keep:
        print("Re-use existing database…")
    cdb = mtg_proxy_printer.model.carddb.CardDatabase(args.database_path)
    cid = mtg_proxy_printer.card_info_downloader.CardInfoDownloadWorker(cdb)
    print("Starting benchmark…")
    cid.download_card_data(args.card_data)
    print("Done")
