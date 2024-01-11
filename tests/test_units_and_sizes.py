# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import pytest
from hamcrest import *

from mtg_proxy_printer.units_and_sizes import UUID


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
def test_uuid_with_invalid_input_raises_valueerror(input_str: str):
    assert_that(
        calling(UUID).with_args(input_str),
        raises(ValueError)
    )
