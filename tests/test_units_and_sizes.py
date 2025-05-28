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


import pytest
from hamcrest import *

from tests.helpers import quantity_close_to
from mtg_proxy_printer.units_and_sizes import UUID, CardSizes, CardSize, PageType, ConfigParser, unit_registry
from tests.hasgetter import has_getters


@pytest.fixture()
def config_parser():
    return ConfigParser({"Test": "1 mm"})


def test_ConfigParser_has_get_quantity(config_parser: ConfigParser):
    assert_that(config_parser, has_property("get_quantity"))
    assert_that(config_parser.get_quantity("DEFAULT", "Test"), quantity_close_to(1*unit_registry.mm))


def test_SectionProxy_has_get_quantity(config_parser: ConfigParser):
    proxy = config_parser["DEFAULT"]
    assert_that(proxy, has_property("get_quantity"))
    assert_that(proxy.get_quantity("Test"), quantity_close_to(1*unit_registry.mm))


@pytest.mark.parametrize("input_str", [
    "2c6e5b25-b721-45ee-894a-697de1310b8c",
    "1b9ec782-0ba1-41f1-bc39-d3302494ecb3",
])
def test_uuid_with_valid_inputs(input_str: str):
    assert_that(
        UUID(input_str),
        is_(instance_of(UUID))
    )


@pytest.mark.parametrize("input_str", [
    "",
    "gc6e5b25-b721-45ee-894a-697de1310b8c",
    "2c6e5b253-b721-45ee-894a-697de1310b8c",
    "2c6e5b2-b721-45ee-894a-697de1310b8c",
    "2c6e5b25-b721-b721-45ee-894a-697de1310b8c",
    "2c6e5b25-b72-45ee-894a-697de1310b8c",
    "2c6e5b25-b7212-45ee-894a-697de1310b8c",
    "2c6e5b25-b721-45eee-894a-697de1310b8c",
    "2c6e5b25-b721-45e-894a-697de1310b8c",
    "2c6e5b25-b721-45ee-89423-697de1310b8c",
    "2c6e5b25-b721-45ee-894-697de1310b8c",
    "2c6e5b25-b721-45ee-894a-4697de1310b8c",
    "2c6e5b25-b721-45ee-894a-97de1310b8c",
])
def test_uuid_with_invalid_input_raises_value_error(input_str: str):
    assert_that(
        calling(UUID).with_args(input_str),
        raises(ValueError)
    )


@pytest.mark.parametrize("input_, expected", [
    (PageType.OVERSIZED, CardSizes.OVERSIZED),
    (PageType.REGULAR, CardSizes.REGULAR),
    (PageType.UNDETERMINED, CardSizes.REGULAR),
    (PageType.MIXED, CardSizes.REGULAR),
])
def test_card_sizes_for_page_type(input_: PageType, expected: CardSize):
    assert_that(CardSizes.for_page_type(input_), is_(expected))


@pytest.mark.parametrize("input_, expected", [(True, CardSizes.OVERSIZED), (False, CardSizes.REGULAR)])
def test_card_sizes_from_bool(input_: bool, expected: CardSize):
    assert_that(CardSizes.from_bool(input_), is_(expected))


@pytest.mark.parametrize("size, width, height", [
    (CardSizes.REGULAR, 745, 1040),
    (CardSizes.OVERSIZED, 1040, 1490),
])
def test_as_qsize_px(size: CardSize, width: int, height: int):
    assert_that(
        size.as_qsize_px(),
        has_getters({
            "width": equal_to(width),
            "height": equal_to(height),
        })
    )
