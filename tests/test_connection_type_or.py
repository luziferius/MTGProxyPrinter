
import functools
import itertools
import operator

from PySide6.QtCore import Qt

import pytest
from hamcrest import *

ConnectionType = Qt.ConnectionType

def powerset(iterable):
    "Subsequences of the iterable from shortest to longest."
    # Taken from https://docs.python.org/3.13/library/itertools.html#itertools-recipes
    # powerset([1,2,3]) → (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    s = list(iterable)
    # Modified the range to start at 1 to suppress the empty set
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(1, len(s)+1))


def generate_test_cases_for_test_ConnectionType___or___valid():
    non_flag_items = [ct for ct in ConnectionType if ct.value < 0x8]
    flag_items = [ct for ct in ConnectionType if ct.value >= 0x8]
    combined_flags = [
        ConnectionType(functools.reduce(operator.or_, (flag.value for flag in flag_combination), 0))
        for flag_combination in powerset(flag_items)
    ]
    for item in itertools.chain(non_flag_items, combined_flags):  # Identity pairs
        yield item, item, item.value
    for first, second in itertools.chain(
            itertools.product(non_flag_items, combined_flags),  # Combine non-flag item with any flag combination
            itertools.permutations(combined_flags, 2)):  # Any pair of flag combinations
        combined = first.value | second.value
        # Results in any order
        yield first, second, combined
        yield second, first, combined


@pytest.mark.parametrize("first, second, expected", generate_test_cases_for_test_ConnectionType___or___valid())
def test_ConnectionType___or___valid(first: ConnectionType, second: ConnectionType, expected: int):
    assert_that(first.__or__(second), has_property("value", equal_to(expected)))

@pytest.mark.parametrize("first, second", itertools.permutations(
    [item for item in ConnectionType if item.value < 0x8], 2))
def test_ConnectionType___or___invalid(first: ConnectionType, second: ConnectionType):
    assert_that(calling(first.__or__).with_args(second), raises(ValueError))

