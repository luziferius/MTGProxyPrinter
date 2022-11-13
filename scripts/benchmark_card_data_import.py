# Copyright (C) 2020-2022 Thomas Hess <thomas.hess@udo.edu>

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
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mtg_proxy_printer.card_info_downloader
import mtg_proxy_printer.model.carddb


@dataclasses.dataclass()
class Namespace:
    """Mock argparse Namespace used for type hinting."""
    database_path: Path
    card_data: Path
    keep: bool
    log_db_path: Path


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
    parser.add_argument(
        "--log-db", type=Path, default=Path(__file__).parent.parent/"benchmark-logs.db",
        dest="log_db_path",
        help="Database location used to store benchmark results. Stores overall time usage, "
             "Python platform and other basic metrics. Defaults to '%(default)s'."
    )
    return parser.parse_args()


to_be_profiled_functions = {
    mtg_proxy_printer.card_info_downloader.CardInfoDatabaseImportWorker: [
        "_populate_database",
        "_parse_single_printing",
        "_insert_set",
        "_insert_card_faces",
        "_get_card_filter_data",
        "_insert_card_filters",
        "_clean_unused_data",
        "_insert_card",
        "_insert_printing",
        "_insert_face_name",
    ],
}


def is_running_with_kernprof() -> bool:
    """Determine if the script was called using kernprof. It is, if "profile" is present in the global scope."""
    try:
        profile
    except (AttributeError, NameError):
        return False
    else:
        return True


def inject_line_profiler():
    for module_, function_list in to_be_profiled_functions.items():
        for func_name in function_list:
            try:
                func = getattr(module_, func_name)
            except AttributeError:
                import warnings
                warnings.warn(f"""Function "{func_name}" in module/class "{module_.__name__}" not found, skipping.""")
            else:
                # Bypass any functools LRU cache
                if hasattr(func, "__wrapped__"):
                    func.__wrapped__ = profile(func.__wrapped__)
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
    cid = mtg_proxy_printer.card_info_downloader.CardInfoDatabaseImportWorker(cdb)
    print("Starting benchmark…")
    cid.import_card_data_from_local_file(args.card_data)
    print("Done")
