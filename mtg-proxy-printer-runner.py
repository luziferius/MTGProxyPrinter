#!/usr/bin/env python3

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
Thin wrapper to run main() from the source checkout.
"""

import pathlib
import sys

# Make sure to find this checkout, and not any system- or user-wide installed versions that may be present
root_path = pathlib.Path(__file__).parent.absolute().resolve()
sys.path.insert(0, str(root_path))

import mtg_proxy_printer.model.carddb
import mtg_proxy_printer.ui.page_scene
from mtg_proxy_printer.__main__ import main


# These methods are wrapped by the profile() function
# if this script is run using the kernprof line profiler.
to_be_profiled_functions = {
    #mtg_proxy_printer.model.carddb.CardDatabase: [
    #    "get_all_languages",
    #    "get_card_names",
    #    "is_valid_and_unique_card",
    #    "get_cards_from_data",
    #    "get_replacement_card_for_unknown_printing",
    #    "_get_cards_from_data",
    #    "find_collector_numbers_matching",
    #    "find_sets_matching",
    #    "find_related_cards",
    #    "get_card_with_scryfall_id",
    #    "get_opposing_face",
    #    "guess_language_from_name",
    #    "translate_card_name",
    #    "is_removed_printing",
    #    "cards_not_used_since",
    #    "cards_used_less_often_then",
    #    "_translate_card",
    #    "store_current_printing_filters",
    #    "_update_cached_data",
    #    "get_all_cards_from_image_cache",
    #],
    mtg_proxy_printer.ui.page_scene.CardBleeds: [
        "update_bleeds",
        "from_card",
    ],
    mtg_proxy_printer.ui.page_scene.CardItem: [
        "__init__",
    ],
    mtg_proxy_printer.ui.page_scene.PageScene: [
        "remove_cut_markers",
        "draw_cut_markers",
        "_draw_cards",
        "update_card_bleeds",
        "draw_card",
        "_compute_position_for_image",
        "compute_page_column_count",
        "_has_neighbors",
    ],
}


def is_running_with_kernprof() -> bool:
    """
    Determine if the script was called using kernprof.
    It is, if "profile" is present in the global scope.
    """
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
    main()
