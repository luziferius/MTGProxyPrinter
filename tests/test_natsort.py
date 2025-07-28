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


from typing import Union

import pytest
from hamcrest import *

import mtg_proxy_printer.natsort


@pytest.mark.parametrize("input_, expected", [
    ("A", "A"),
    ("1", 1),
    ("0", 0),
    ("-1", -1),
    ("+1", 1),
    ("1.0", "1.0"),
])
def test_try_convert_int(input_: str | int, expected: str | int):
    assert_that(
        mtg_proxy_printer.natsort.try_convert_int(input_),
        is_(equal_to(expected))
    )


@pytest.mark.parametrize("result", [True, False])
@pytest.mark.parametrize("first, other", [
    ("2", "10"),
    ("A2", "A10"),
    ("A", "B"),
])
def test_str_less_than(first: str, other: str, result: bool):
    # Note: All provided first/other pairs return True when passed as-is in str_less_than().
    # When result == False is passed in, reverse the input order, so that str_less_than returns False
    if not result:
        other, first = first, other
    assert_that(
        mtg_proxy_printer.natsort.str_less_than(first, other),
        is_(result)
    )


@pytest.mark.parametrize("first", ["", "ABC"])
def test_str_less_than_on_equal_strings_returns_False(first):
    assert_that(
        mtg_proxy_printer.natsort.str_less_than(first, first),
        is_(False)
    )


@pytest.mark.parametrize("reverse", [True, False])
@pytest.mark.parametrize("reversed_input", [True, False])
@pytest.mark.parametrize("first, other", [
    ("2", "10"),
    ("A2", "A10"),
    ("A", "B"),
])
def test_natural_sorted(first: str, other: str, reversed_input: bool, reverse: bool):
    expected = [first, other]
    if reverse:
        expected.reverse()
    input_ = [first, other]
    if reversed_input:
        input_.reverse()
    assert_that(
        mtg_proxy_printer.natsort.natural_sorted(input_, reverse),
        contains_exactly(*expected)
    )
