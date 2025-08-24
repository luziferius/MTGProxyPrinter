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

from collections.abc import Iterable
import itertools
import sys

import pytest
from hamcrest import *

import mtg_proxy_printer.argument_parser


def powerset(*items: list[str]) -> Iterable[tuple[list[str], ...]]:
    length = len(items)
    return itertools.chain.from_iterable(
        itertools.combinations(items, subset)
        for subset
        in range(length+1)
    )


def generate_command_lines():
    # All command line options as lists of strings
    subsets = powerset(
        ["--test-exit-on-launch"],
        ["--card-data", "/card_data.json.gz"],
        ["/path/to/save.mtgproxies"],
    )
    return map(list, map(itertools.chain.from_iterable, subsets))


@pytest.mark.parametrize("argv", generate_command_lines())
def test_argument_parser_namespace_only_contains_known_keys(argv: list[str]):

    args = mtg_proxy_printer.argument_parser.parse_args(argv)
    annotations = mtg_proxy_printer.argument_parser.Namespace.__annotations__
    assert_that(
        args.__dict__, only_contains(*annotations)
    )


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires Python 3.9 or higher")
@pytest.mark.parametrize("argv", generate_command_lines())
def test_argument_parser_namespace_matches_annotated_namespace(argv: list[str]):
    args = mtg_proxy_printer.argument_parser.parse_args(argv)
    annotations = mtg_proxy_printer.argument_parser.Namespace.__annotations__
    # This isn't optimal for non-optional
    for key, value in args.__dict__.items():
        expected = annotations[key]
        # Cannot use hamcrest instance_of(), as that cannot handle typing.Optional and related
        assert_that(isinstance(value, expected), f"Type mismatch. {expected=}, got {type(value)=}")
