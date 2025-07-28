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
This is a test module for the set of custom PyHamcrest matchers in tests/helpers.py
"""

import dataclasses
from typing import Optional

import pytest
from hamcrest import *

from .helpers import is_dataclass_equal_to, matches_type_annotation


@dataclasses.dataclass
class Dataclass:
    attr1: str
    attr2: str | int
    attr3: str | None


@dataclasses.dataclass
class Dataclass2:
    attr1: str
    attr2: str | int


@pytest.mark.parametrize("instance", [
    Dataclass(123, "attr2", "attr3"),
    Dataclass("attr1", 123.4, "attr3"),
    Dataclass(123, "attr2", None),
    Dataclass("attr1", 123.4, None),
    Dataclass("attr1", "attr2", 123),
])
def test_matches_type_annotation_raises_wrong_types(instance: Dataclass):
    assert_that(
        calling(assert_that).with_args(instance, matches_type_annotation()),
        raises(AssertionError)
    )


@pytest.mark.parametrize("instance", [
    Dataclass("attr1", "attr2", "attr3"),
    Dataclass("attr1", "attr2", None),
    Dataclass("attr1", 123, "attr3"),
    Dataclass("attr1", 123, None),
])
def test_matches_type_annotation_passes_with_correct_types(instance: Dataclass):
    assert_that(
        instance, matches_type_annotation()
    )


@pytest.mark.parametrize("instance, expected", [
    (Dataclass("", "", ""), Dataclass("", 1, "")),
    (Dataclass("", "", None), Dataclass("", "", "")),
    (Dataclass("abc", "", ""), Dataclass("xyz", "", "")),
    (Dataclass("a", "x", "a"), Dataclass("a", "x", "b")),
    (Dataclass("", 1, None), Dataclass("", 2, None)),
    ("foo", Dataclass("", 2, None)),
    (Dataclass2("", ""), Dataclass("", "", "")),
    (Dataclass("", "", ""), Dataclass2("", "")),
])
def test_is_dataclass_equal_to_raises_with_unequal_instances(instance: Dataclass, expected: Dataclass):
    assert_that(
        calling(assert_that).with_args(instance, is_dataclass_equal_to(expected)),
        raises(AssertionError)
    )


@pytest.mark.parametrize("instance", [
    Dataclass("", "", ""),
    Dataclass("", "", None),
    Dataclass("", 1, ""),
    Dataclass("", 1, None),
    Dataclass("uenrude", "ueue", "aeea"),
    Dataclass(1.1, object(), "abc"),
])
def test_is_dataclass_equal_to_passes_with_equal_instances(instance: Dataclass):
    assert_that(
        instance, is_dataclass_equal_to(instance)
    )
