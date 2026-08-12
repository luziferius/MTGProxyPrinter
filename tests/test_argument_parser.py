#  Copyright © 2020-2026  Thomas Hess <thomas.hess@udo.edu>
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

# All command line options as lists of strings
command_lines: list[list[str]] = list(map(list, map(itertools.chain.from_iterable, powerset(
    ["--test-exit-on-launch"],
    ["--card-data", "/card_data.json.gz"],
    ["/path/to/save.mtgproxies"],
))))


@pytest.mark.parametrize("argv", command_lines)
def test_argument_parser_namespace_only_contains_known_keys(argv: list[str]):
    args = mtg_proxy_printer.argument_parser.parse_args(argv)
    annotations = mtg_proxy_printer.argument_parser.Namespace.__annotations__
    assert_that(
        args.__dict__, only_contains(*annotations)
    )


@pytest.mark.parametrize("argv", command_lines)
def test_argument_parser_namespace_matches_annotated_namespace(argv: list[str]):
    args = mtg_proxy_printer.argument_parser.parse_args(argv)
    annotations = mtg_proxy_printer.argument_parser.Namespace.__annotations__
    for key, value in args.__dict__.items():
        expected = annotations[key]
        # Cannot use hamcrest instance_of(), as that cannot handle typing.Optional and related
        assert_that(isinstance(value, expected), f"Type mismatch. {expected=}, got {type(value)=}")
