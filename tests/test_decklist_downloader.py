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
import textwrap
import typing

import pytest
from hamcrest import *

from mtg_proxy_printer.decklist_downloader import ScryfallDownloader, MTGGoldfishDownloader, MTGWTFDownloader, \
    IsIdentifyingDeckUrlValidator, DecklistDownloader, TappedOutDownloader, MoxfieldDownloader, DeckstatsDownloader


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


ACCEPTABLE_MTG_WTF_URLS = [
    "https://mtg.wtf/deck/c21/prismari-performance",
    "https://mtg.wtf/deck/c21/prismari-performance/",
]


@pytest.mark.parametrize("url", ACCEPTABLE_MTG_WTF_URLS)
def test_mtg_wtf_url_re(url: str):
    assert_that(
        MTGWTFDownloader.DECKLIST_PATH_RE.match(url),
        is_(not_none())
    )


@pytest.mark.parametrize("url", itertools.chain(
    ACCEPTABLE_MTGGOLDFISH_URLS,
    ACCEPTABLE_SCRYFALL_URLS,
    ACCEPTABLE_MTG_WTF_URLS,
))
def test_IsIdentifyingDeckUrlValidator_validate(url: str):
    validator = IsIdentifyingDeckUrlValidator()
    assert_that(
        validator.validate(url),
        contains_exactly(IsIdentifyingDeckUrlValidator.Acceptable, url, 0),
    )


def generate_test_cases_for_test_deck_list_download() \
        -> typing.Generator[typing.Tuple[typing.Type[DecklistDownloader], str, str], None, None]:
    """
    Yields tuples with Parser class, deck list url and a snippet of the deck list content.
    It does not include the full deck list, because reported printings or price information may change over time,
    causing test failures. The tests should pass as long as the website returns some plausible data.
    """
    yield MTGWTFDownloader, "https://mtg.wtf/deck/c21/prismari-performance/", "1 Jaya Ballard"
    yield ScryfallDownloader, "https://scryfall.com/@luziferius/decks/e1a9af19-cfff-48c4-ae74-ed2dd78cb736", "Island"
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/deck/5136573", "1 Ancestral Recall"
    yield TappedOutDownloader, "https://tappedout.net/mtg-decks/mtgproxyprinter-test-deck/", "Island"
    yield MoxfieldDownloader, "https://www.moxfield.com/decks/g1i2wHXC3kW0lanwY4Llkw", '"Zamriel, Seraph of Steel"'
    yield DeckstatsDownloader, "https://deckstats.net/decks/44867/576160-br-control-kld", "2 Blighted Fen"


@pytest.mark.skip("Skipping network-hitting tests")
@pytest.mark.parametrize("downloader_class, url, expected", generate_test_cases_for_test_deck_list_download())
def test_deck_list_download(downloader_class: typing.Type[DecklistDownloader], url: str, expected: str):
    downloader = downloader_class()
    result = downloader.download(url)
    assert_that(result, is_(str))
    assert_that(
        result,
        contains_string(expected),
    )
