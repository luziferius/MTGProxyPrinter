# Copyright (C) 2022 Thomas Hess <thomas.hess@udo.edu>

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
import itertools

import pytest
from hamcrest import *

from mtg_proxy_printer.decklist_downloader import ScryfallDownloader, MTGGoldfishDownloader, IsIdentifyingDeckUrlValidator


ACCEPTABLE_MTGGOLDFISH_URLS = [
    "https://www.mtggoldfish.com/deck/5077398#paper",
    "https://www.mtggoldfish.com/deck/5077398#arena",
    "https://www.mtggoldfish.com/deck/5077398#online",
    "https://www.mtggoldfish.com/deck/download/5077398",
    "https://www.mtggoldfish.com/deck/download/5077398?output=mtggoldfish&type=tabletop",
    "https://www.mtggoldfish.com/deck/download/5077398?output=mtggoldfish&type=arena",
    "https://www.mtggoldfish.com/deck/download/5077398?output=mtggoldfish&type=online",
    "https://www.mtggoldfish.com/deck/download/5077398?output=dek&type=online",
]


@pytest.mark.parametrize("url", ACCEPTABLE_MTGGOLDFISH_URLS)
def test_mtggoldfish_url_re(url: str):
    assert_that(
        MTGGoldfishDownloader.DECKLIST_PATH_RE.match(url),
        is_(not_none())
    )


ACCEPTABLE_SCRYFALL_URLS = [
    "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3/",
    "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3/?with=eur",
    "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3/?with=tix",
    "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3/?with=arena",
    "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3/?with=cah",
    "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3/?as=visual",
    "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3/?as=visual&with=eur",
    "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3",
    "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3?with=eur",
    "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3?with=tix",
    "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3?with=arena",
    "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3?with=cah",
    "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3?as=visual",
    "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3?as=visual&with=eur",
]

@pytest.mark.parametrize("url", ACCEPTABLE_SCRYFALL_URLS)
def test_scryfall_url_re(url: str):
    assert_that(
        ScryfallDownloader.DECKLIST_PATH_RE.match(url),
        is_(not_none())
    )


@pytest.mark.parametrize("url", itertools.chain(ACCEPTABLE_MTGGOLDFISH_URLS, ACCEPTABLE_SCRYFALL_URLS))
def test_IsIdentifyingDeckUrlValidator_validate(url: str):
    validator = IsIdentifyingDeckUrlValidator()
    assert_that(
        validator.validate(url),
        contains_exactly(IsIdentifyingDeckUrlValidator.Acceptable, url, 0),
    )
