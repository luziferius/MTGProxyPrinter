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


from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from hamcrest import *

from .helpers import SHOULD_SKIP_NETWORK_TESTS

from mtg_proxy_printer.async_tasks.decklist_downloader import ScryfallDownloader, MTGGoldfishDownloader, MTGWTFDownloader, \
    IsIdentifyingDeckUrlValidator, DecklistDownloader, TappedOutDownloader, MoxfieldDownloader, DeckstatsDownloader, \
    MtgDecksNetDownloader, ArchidektDownloader, TCGPlayerDownloader, MTGTop8Downloader, MTGAZoneDownloader, \
    CubeCobraDownloader, ManaboxDownloader


UrlTestData = tuple[type[DecklistDownloader], str]


def generate_tests_for_test_re_matcher_matches_acceptable_url() -> Generator[UrlTestData, None, None]:
    # MTGGoldfish
    # Deck links
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/deck/5077398#paper"
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/deck/5077398#arena"
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/deck/5077398#online"
    # Download links
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/deck/download/5077398"
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/deck/download/5077398?output=mtggoldfish&type=tabletop"
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/deck/download/5077398?output=mtggoldfish&type=arena"
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/deck/download/5077398?output=mtggoldfish&type=online"
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/deck/download/5077398?output=dek&type=online"
    # Deck archetype links
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/archetype/legacy-led-dredge#paper"
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/archetype/legacy-led-dredge#arena"
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/archetype/legacy-led-dredge#online"

    # Scryfall deck lists
    yield ScryfallDownloader, "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3/"
    yield ScryfallDownloader, "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3/?with=eur"
    yield ScryfallDownloader, "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3/?with=tix"
    yield ScryfallDownloader, "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3/?with=arena"
    yield ScryfallDownloader, "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3/?with=cah"
    yield ScryfallDownloader, "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3/?as=visual"
    yield ScryfallDownloader, "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3/?as=visual&with=eur"
    yield ScryfallDownloader, "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3"
    yield ScryfallDownloader, "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3?with=eur"
    yield ScryfallDownloader, "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3?with=tix"
    yield ScryfallDownloader, "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3?with=arena"
    yield ScryfallDownloader, "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3?with=cah"
    yield ScryfallDownloader, "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3?as=visual"
    yield ScryfallDownloader, "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e8-bfdea0951ce3?as=visual&with=eur"
    # Scryfall API searches
    yield ScryfallDownloader, "https://api.scryfall.com/cards/search?q=e%3Arex+cn%E2%89%A527+cn%E2%89%A445&format=csv"
    yield ScryfallDownloader, "https://api.scryfall.com/cards/search?format=csv&q=e%3Arex+cn%E2%89%A527+cn%E2%89%A445"

    # mtg.wtf
    yield MTGWTFDownloader, "https://mtg.wtf/deck/c21/prismari-performance"
    yield MTGWTFDownloader, "https://mtg.wtf/deck/c21/prismari-performance/"

    # MTG Arena Zone (mtgazone.com)
    yield MTGAZoneDownloader, "https://mtgazone.com/deck/orzhov-phyrexians-march-of-the-machine-theorycraft/"
    yield MTGAZoneDownloader, "https://mtgazone.com/deck/orzhov-phyrexians-march-of-the-machine-theorycraft"

    # MTGTop8
    yield MTGTop8Downloader, "http://mtgtop8.com/event?e=9011&d=251345&f=BL"
    yield MTGTop8Downloader, "http://mtgtop8.com/event?e=9011&d=251345"
    yield MTGTop8Downloader, "http://www.mtgtop8.com/event?e=9011&d=251345&f=BL"
    yield MTGTop8Downloader, "http://www.mtgtop8.com/event?e=9011&d=251345"

    # mtgdecks.net
    yield MtgDecksNetDownloader, "https://mtgdecks.net/Premodern/false-cure-decklist-by-pol-tavarone-1544582"
    yield MtgDecksNetDownloader, "https://mtgdecks.net/Premodern/false-cure-decklist-by-pol-tavarone-1544582/"

    # Moxfield
    yield MoxfieldDownloader, "https://moxfield.com/decks/70auYSm75E-Iwf4Oc0g7Lg"
    yield MoxfieldDownloader, "https://moxfield.com/decks/70auYSm75E-Iwf4Oc0g7Lg/"
    yield MoxfieldDownloader, "https://www.moxfield.com/decks/70auYSm75E-Iwf4Oc0g7Lg"
    yield MoxfieldDownloader, "https://www.moxfield.com/decks/70auYSm75E-Iwf4Oc0g7Lg/"

    # TappedOut
    yield TappedOutDownloader, "https://tappedout.net/mtg-decks/mtgproxyprinter-test-deck"
    yield TappedOutDownloader, "https://tappedout.net/mtg-decks/mtgproxyprinter-test-deck/"
    yield TappedOutDownloader, "https://tappedout.net/mtg-decks/mtgproxyprinter-test-deck/?cat=subtype&sort=name&cb=1665072266"
    yield TappedOutDownloader, "https://tappedout.net/mtg-decks/mtgproxyprinter-test-deck/?cat=custom&sort=rarity&cb=1665072266"
    yield TappedOutDownloader, "https://tappedout.net/mtg-decks/mtgproxyprinter-test-deck?cat=subtype&sort=name&cb=1665072266"
    yield TappedOutDownloader, "https://tappedout.net/mtg-decks/mtgproxyprinter-test-deck?cat=custom&sort=rarity&cb=1665072266"

    # Deckstats
    yield DeckstatsDownloader, "https://deckstats.net/decks/57872/450232-tapland/de"
    yield DeckstatsDownloader, "https://deckstats.net/decks/57872/450232-tapland/"
    yield DeckstatsDownloader, "https://deckstats.net/decks/57872/450232-tapland"
    yield DeckstatsDownloader, "https://deckstats.net/decks/57872/450232-tapland#show__stats"
    yield DeckstatsDownloader, "https://deckstats.net/decks/57872/450232-tapland#show__spoiler"
    yield DeckstatsDownloader, "https://deckstats.net/decks/51910/1430827-"  # An untitled deck
    yield DeckstatsDownloader, "https://deckstats.net/decks/51910/1430827"  # Missing required hyphen, added internally

    # Archidekt
    yield ArchidektDownloader, "https://archidekt.com/decks/8"
    yield ArchidektDownloader, "https://archidekt.com/decks/4296325"
    yield ArchidektDownloader, "https://archidekt.com/decks/4296325/some_name"
    yield ArchidektDownloader, "https://www.archidekt.com/decks/4296325"
    yield ArchidektDownloader, "https://www.archidekt.com/decks/4296325/some_name"

    # TCGPlayer Infinite
    yield TCGPlayerDownloader, "https://infinite.tcgplayer.com/magic-the-gathering/deck/Azorius-Hammer/468532"
    yield TCGPlayerDownloader, "https://infinite.tcgplayer.com/magic-the-gathering/deck/Azorius-Hammer/468532/"

    # CubeCobra
    yield CubeCobraDownloader, "https://cubecobra.com/cube/list/gilpauper"
    yield CubeCobraDownloader, "https://cubecobra.com/cube/overview/gilpauper"
    yield CubeCobraDownloader, "https://cubecobra.com/cube/overview/5124b9d5-d921-4fd9-85bb-346aa06814e2"
    yield CubeCobraDownloader, "https://cubecobra.com/cube/list/gilpauper/"
    yield CubeCobraDownloader, "https://cubecobra.com/cube/overview/gilpauper/"
    yield CubeCobraDownloader, "https://cubecobra.com/cube/overview/5124b9d5-d921-4fd9-85bb-346aa06814e2/"

    yield CubeCobraDownloader, "https://www.cubecobra.com/cube/list/gilpauper"
    yield CubeCobraDownloader, "https://www.cubecobra.com/cube/overview/gilpauper"
    yield CubeCobraDownloader, "https://www.cubecobra.com/cube/overview/5124b9d5-d921-4fd9-85bb-346aa06814e2"
    yield CubeCobraDownloader, "https://www.cubecobra.com/cube/list/gilpauper/"
    yield CubeCobraDownloader, "https://www.cubecobra.com/cube/overview/gilpauper/"
    yield CubeCobraDownloader, "https://www.cubecobra.com/cube/overview/5124b9d5-d921-4fd9-85bb-346aa06814e2/"

    # ManaBox
    yield ManaboxDownloader, "https://manabox.app/decks/xa1hXTCXQoiNkmp_TPwW8w"
    yield ManaboxDownloader, "https://manabox.app/decks/xa1hXTCXQoiNkmp_TPwW8w/"
    yield ManaboxDownloader, "https://www.manabox.app/decks/xa1hXTCXQoiNkmp_TPwW8w"
    yield ManaboxDownloader, "https://www.manabox.app/decks/xa1hXTCXQoiNkmp_TPwW8w/"


@pytest.mark.parametrize("downloader, url", generate_tests_for_test_re_matcher_matches_acceptable_url())
def test_re_matcher_matches_acceptable_url(downloader, url: str):
    assert_that(
        downloader.DECKLIST_PATH_RE.match(url),
        is_(not_none())
    )


@pytest.mark.parametrize("downloader, url", generate_tests_for_test_re_matcher_matches_acceptable_url())
def test_IsIdentifyingDeckUrlValidator_validate(downloader, url: str):
    validator = IsIdentifyingDeckUrlValidator()
    assert_that(
        validator.validate(url),
        contains_exactly(IsIdentifyingDeckUrlValidator.Acceptable, url, 0),
    )


def generate_tests_for_test_re_matcher_rejects_unacceptable_url() -> Generator[UrlTestData, None, None]:
    # MTGGoldfish
    # Deck links
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/deck"
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/deck/"
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/deck/#online"
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com"
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/"
    # Download links
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/deck/download/"
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/deck/download/?output=mtggoldfish&type=tabletop"
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/deck/download?output=mtggoldfish&type=arena"
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/deck/download"
    # Deck archetype links
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/archetype/#paper"
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/archetype#arena"
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/archetype/"
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/archetype"

    # Scryfall
    yield ScryfallDownloader, "https://scryfall.com/@user/8c02b4b2-50e2-4431-83e8-bfdea0951ce3/"  # missing /deck
    # Invalid/missing UUIDS
    yield ScryfallDownloader, "https://scryfall.com/@user/decks/8c02b4b2-50e2-4431-83e-8-bfdea0951ce3/?with=eur"
    yield ScryfallDownloader, "https://scryfall.com/@user/decks/8c02b4b2-50e2-xyza-83e8-bfdea0951ce3/?with=tix"
    yield ScryfallDownloader, "https://scryfall.com/@user/decks/?with=arena"
    # API search without query
    yield ScryfallDownloader, "https://api.scryfall.com/cards/search?format=csv"

    # mtg.wtf
    yield MTGWTFDownloader, "https://mtg.wtf/deck/c21"
    yield MTGWTFDownloader, "https://mtg.wtf/deck/c21/"

    # MTG Arena Zone (mtgazone.com)
    yield MTGAZoneDownloader, "https://mtgazone.com/deck"
    yield MTGAZoneDownloader, "https://mtgazone.com/"
    yield MTGAZoneDownloader, "https://mtgazone.com/orzhov-phyrexians-march-of-the-machine-theorycraft"

    # MTGTop8
    yield MTGTop8Downloader, "http://mtgtop8.com/event?d=251345&f=BL"
    yield MTGTop8Downloader, "http://mtgtop8.com/event?e=9011"
    yield MTGTop8Downloader, "http://mtgtop8.com/event?d=251345&"
    yield MTGTop8Downloader, "http://mtgtop8.com/event?e=9011&f=BL"
    yield MTGTop8Downloader, "http://mtgtop8.com/event"
    yield MTGTop8Downloader, "http://mtgtop8.com/"

    # mtgdecks.net
    yield MtgDecksNetDownloader, "https://mtgdecks.net/Premodern/"
    yield MtgDecksNetDownloader, "https://mtgdecks.net/Premodern"

    # Moxfield
    yield MoxfieldDownloader, "https://moxfield.com/decks"
    yield MoxfieldDownloader, "https://moxfield.com/"
    yield MoxfieldDownloader, "https://www.moxfield.com/decks"
    yield MoxfieldDownloader, "https://www.moxfield.com/"
    yield MoxfieldDownloader, "https://ww.moxfield.com/decks/70auYSm75E-Iwf4Oc0g7Lg"

    # TappedOut
    yield TappedOutDownloader, "https://tappedout.net/mtg-decks"
    yield TappedOutDownloader, "https://tappedout.net/mtg-decks/"
    yield TappedOutDownloader, "https://tappedout.net/mtg-decks/?cat=subtype&sort=name&cb=1665072266"
    yield TappedOutDownloader, "https://tappedout.net/mtg-decks?cat=custom&sort=rarity&cb=1665072266"

    # Deckstats
    yield DeckstatsDownloader, "https://deckstats.net"
    yield DeckstatsDownloader, "https://deckstats.net/decks/57872/"
    yield DeckstatsDownloader, "https://deckstats.net/decks/"
    yield DeckstatsDownloader, "https://deckstats.net/decks/57872"

    # Archidekt
    yield ArchidektDownloader, "https://archidekt.com/decks/"
    yield ArchidektDownloader, "https://archidekt.com/decks"
    yield ArchidektDownloader, "https://archidekt.com/"
    yield ArchidektDownloader, "https://archidekt.com"

    # TCGPlayer Infinite
    yield TCGPlayerDownloader, "https://infinite.tcgplayer.com/magic-the-gathering/deck/Azorius-Hammer"

    # CubeCobra
    yield CubeCobraDownloader, "https://cubecobra.com/cube/5124b9d5-d921-4fd9-85bb-346aa06814e2"
    yield CubeCobraDownloader, "https://cubecobra.com/list/5124b9d5-d921-4fd9-85bb-346aa06814e2"
    yield CubeCobraDownloader, "https://cubecobra.com/cube/overview/"
    yield CubeCobraDownloader, "https://cubecobra.com/cube/"
    yield CubeCobraDownloader, "https://cubecobra.com/"
    yield CubeCobraDownloader, "https://cubecobra.com"

    # ManaBox
    yield ManaboxDownloader, "https://manabox.app/decks/xa1hXTCXQoi"
    yield ManaboxDownloader, "https://manabox.app/decks/xa1hXTCXQow/"
    yield ManaboxDownloader, "https://manabox.app/decks/"
    yield ManaboxDownloader, "https://manabox.app/decks"
    yield ManaboxDownloader, "https://manabox.app/"


@pytest.mark.parametrize("downloader, url", generate_tests_for_test_re_matcher_rejects_unacceptable_url())
def test_re_matcher_rejects_unacceptable_url(downloader, url: str):
    assert_that(
        downloader.DECKLIST_PATH_RE.match(url),
        is_(none())
    )


@pytest.mark.parametrize("downloader, url", generate_tests_for_test_re_matcher_rejects_unacceptable_url())
def test_IsIdentifyingDeckUrlValidator_validate_returns_Intermediate_or_Invalid_on_unacceptable_urls(
        downloader, url: str):
    validator = IsIdentifyingDeckUrlValidator()
    assert_that(
        validator.validate(url),
        contains_exactly(
            any_of(IsIdentifyingDeckUrlValidator.Intermediate, IsIdentifyingDeckUrlValidator.Invalid), url, 0),
    )


def generate_test_cases_for_test_deck_list_download() \
        -> Generator[tuple[type[DecklistDownloader], str, str], None, None]:
    """
    Yields tuples with Parser class, deck list url and a snippet of the deck list content.
    It does not include the full deck list, because reported printings or price information may change over time,
    causing test failures. The tests should pass as long as the website returns some plausible data.
    """
    yield MTGWTFDownloader, "https://mtg.wtf/deck/c21/prismari-performance/", "1 Jaya Ballard"
    # Deck list
    yield ScryfallDownloader, "https://scryfall.com/@luziferius/decks/e1a9af19-cfff-48c4-ae74-ed2dd78cb736", "Island"
    # API search
    yield ScryfallDownloader, "https://api.scryfall.com/cards/search?format=csv&q=e%3Arex+cn%E2%89%A527+cn%E2%89%A445", "f197b176-8fa0-451b-a981-a7a942890296"
    yield MTGAZoneDownloader, "https://mtgazone.com/deck/orzhov-phyrexians-march-of-the-machine-theorycraft/", "3 Cut Down"
    yield MTGTop8Downloader, "http://mtgtop8.com/event?e=9011&d=251345&f=BL", "4 [KTK] Abzan Charm"
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/deck/5136573", "1 Ancestral Recall"
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/archetype/legacy-led-dredge", "4 Lion's Eye Diamond"
    yield TappedOutDownloader, "https://tappedout.net/mtg-decks/mtgproxyprinter-test-deck/", "Island"
    yield MoxfieldDownloader, "https://www.moxfield.com/decks/g1i2wHXC3kW0lanwY4Llkw", '"Zamriel, Seraph of Steel"'
    yield DeckstatsDownloader, "https://deckstats.net/decks/44867/576160-br-control-kld", "2 Blighted Fen"
    yield MtgDecksNetDownloader, "https://mtgdecks.net/Premodern/false-cure-decklist-by-pol-tavarone-1544582", "4 Cabal Therapy"
    yield ArchidektDownloader, "https://archidekt.com/decks/8", "Mirror Entity"
    yield TCGPlayerDownloader, "https://infinite.tcgplayer.com/magic-the-gathering/deck/Azorius-Hammer/468532/", "4,en,Esper Sentinel"
    yield CubeCobraDownloader, "https://cubecobra.com/cube/overview/1lb", "1 [MBS:2] Ardent Recruit"
    yield ManaboxDownloader, "https://manabox.app/decks/xa1hXTCXQoiNkmp_TPwW8w/", "Air Elemental"


@pytest.mark.skipif(SHOULD_SKIP_NETWORK_TESTS, reason="Skipping network-hitting tests")
@pytest.mark.parametrize("downloader_class, url, expected", generate_test_cases_for_test_deck_list_download())
def test_deck_list_download(downloader_class: type[DecklistDownloader], url: str, expected: str):
    downloader = downloader_class()
    result = downloader.download(url)
    assert_that(result, is_(str))
    assert_that(
        result,
        contains_string(expected),
    )


@pytest.mark.parametrize("deck_list, expected", [
    (b"4 Fire/Ice\r\n", "4 Fire // Ice\n"),
])
def test_decklists_net_post_process(deck_list: bytes, expected: str):
    """
    The MTGO exports of split cards contain entries in the form of "Front/Back", instead of
    the more common "Front // Back". Verify that the downloader normalizes the entries.
    """
    downloader = MtgDecksNetDownloader()
    stream = MagicMock()
    stream.read.return_value = deck_list
    with patch("mtg_proxy_printer.async_tasks.decklist_downloader.MtgDecksNetDownloader.read_from_url") as reader:
        reader.return_value = stream, MagicMock()
        result = downloader.download("")
    assert_that(result, is_(equal_to(expected)))
