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

from pathlib import Path
import urllib.request

import ijson


def read_json_card_data_from_url(url: str):
    """
    Parses the bulk card data json from https://scryfall.com/docs/api/bulk-data into individual objects.
    This function takes a URL pointing to the card data json object in the Scryfall API.

    The all cards json document is quite large (> 1GiB in 2020-11) and requires about 4GiB RAM to parse in one go.
    So use this iterative parser to generate and yield individual card objects, without having to store the whole
    document in memory.
    """
    with urllib.request.urlopen(url) as file_like:
        yield from _read_json_card_data_from_open_file(file_like)


def read_json_card_data_from_path(path: Path):
    """
    Parses the bulk card data json from https://scryfall.com/docs/api/bulk-data into individual objects.
    This function takes a file path to a locally stored json document. Mainly for testing purposes.

    The all cards json document is quite large (> 1GiB in 2020-11) and requires about 4GiB RAM to parse in one go.
    So use this iterative parser to generate and yield individual card objects, without having to store the whole
    document in memory.
    """
    with path.open("rb") as file:
        yield from _read_json_card_data_from_open_file(file)


def _read_json_card_data_from_open_file(file):
    parser = ijson.basic_parse(file)
    # Throw away the outer json array [] that encapsulates the whole data set
    next(parser)
    # Tracks the current nesting depth. Whenever it reaches 0, an object is fully read and can be yielded.
    nesting_depth = 0
    object_builder = ijson.ObjectBuilder()
    for event, value in parser:
        if event in("start_map", "start_array"):
            nesting_depth += 1
        elif event in ("end_map", "end_array"):
            nesting_depth -= 1
        if nesting_depth == -1:
            # End of the outer json array reached, so stop iterating
            break
        object_builder.event(event, value)
        if nesting_depth == 0:
            yield object_builder.value  # value is dynamically created whenever the parser gathered a full object
            object_builder = ijson.ObjectBuilder()
