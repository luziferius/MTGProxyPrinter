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
    IsIdentifyingDeckUrlValidator, DecklistDownloader


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
    yield MTGWTFDownloader, "https://mtg.wtf/deck/c21/prismari-performance/", textwrap.dedent("""\
        // NAME: Prismari Performance - Commander 2021 Commander Deck
        // URL: http://mtg.wtf/deck/c21/prismari-performance
        // DATE: 2021-04-23
        COMMANDER: 1 Zaffai, Thunder Conductor
        1 Jaya Ballard
        1 Veyran, Voice of Duality
        1 Dazzling Sphinx
        1 Octavia, Living Thesis
        1 Sly Instigator
        1 Inferno Project
        1 Radiant Performer
        1 Rionya, Fire Dancer
        1 Diluvian Primordial
        1 Naru Meha, Master Wizard
        1 Talrand, Sky Summoner
        1 Charmbreaker Devils
        1 Dualcaster Mage
        1 Erratic Cyclops
        1 Etali, Primal Storm
        1 Wildfire Devils
        1 Storm-Kiln Artist
        1 Rootha, Mercurial Artist
        1 Living Lore
        1 Humble Defector
        1 Crackling Drake
        1 Inspiring Refrain
        1 Muse Vortex
        1 Creative Technique
        1 Fiery Encore
        1 Rousing Refrain
        1 Surge to Victory
        1 Aether Gale
        1 Apex of Power
        1 Blasphemous Act
        1 Volcanic Vision
        1 Call the Skybreaker
        1 Epic Experiment
        1 Elemental Masterpiece
        1 Expressive Iteration
        1 Ponder
        1 Serum Visions
        1 Treasure Cruise
        1 Faithless Looting
        1 Mana Geyser
        1 Reinterpret
        1 Aetherspouts
        1 Dig Through Time
        1 Resculpt
        1 Brainstorm
        1 Traumatic Visions
        1 Fiery Fall
        1 Seething Song
        1 Letter of Acceptance
        1 Arcane Signet
        1 Hedron Archive
        1 Izzet Signet
        1 Mind Stone
        1 Sol Ring
        1 Talisman of Creativity
        1 Metallurgic Summonings
        1 Swarm Intelligence
        1 Exotic Orchard
        1 Scavenger Grounds
        1 Shivan Reef
        1 Temple of Epiphany
        1 Prismari Campus
        1 Study Hall
        1 Blighted Cataract
        1 Command Tower
        1 Desert of the Fervent
        1 Desert of the Mindful
        1 Forgotten Cave
        1 Izzet Boilerworks
        1 Lonely Sandbar
        1 Mage-Ring Network
        1 Memorial to Genius
        1 Myriad Landscape
        1 Reliquary Tower
        1 Temple of the False God
        10 Island
        9 Mountain
        1 Elementalist's Palette
        1 Mind's Desire
        1 Brass's Bounty
        1 Sunbird's Invocation
        1 Pyromancer's Goggles
        """)
    yield ScryfallDownloader, "https://scryfall.com/@luziferius/decks/e1a9af19-cfff-48c4-ae74-ed2dd78cb736", textwrap.dedent("""\
        section,count,name,mana_cost,type,set,set_code,collector_number,lang,rarity,artist,foil,usd_price,eur_price,tix_price,scryfall_uri,scryfall_id
        columna,1,Island,"",Basic Land — Island,Dominaria United,dmu,265,en,common,Seb McKinnon,false,0.1,0.1,0.1,https://scryfall.com/card/dmu/265/island,8bafc217-3d83-4551-b2e3-3494ec14b2f9
        columna,1,Forest,"",Basic Land — Forest,Streets of New Capenna,snc,281,fr,common,WFlemming Illustration,true,0.05,0.02,0.01,https://scryfall.com/card/snc/281/fr/for%C3%AAt,71cfabd0-8c54-419e-b220-501b21d6ae08
        columna,1,Mountain,"",Basic Land — Mountain,"Warhammer 40,000",40k,315,en,common,Diego Gisbert,false,0.8,0.11,0.01,https://scryfall.com/card/40k/315/mountain,a1ba2d4f-7a9b-4cf7-98fd-17b1b8c70bcd
        """)
    yield MTGGoldfishDownloader, "https://www.mtggoldfish.com/deck/5136573", textwrap.dedent("""\
        1 Ancestral Recall
        1 Black Lotus
        1 Brainstorm
        1 Dig Through Time
        1 Dreadhorde Arcanist
        4 Expressive Iteration
        4 Flooded Strand
        2 Force of Negation
        4 Force of Will
        1 Gitaxian Probe
        1 Lavinia, Azorius Renegade
        1 Mental Misstep
        1 Merchant Scroll
        4 Mishra's Bauble
        1 Mox Pearl
        1 Mox Ruby
        1 Mox Sapphire
        1 Ponder
        4 Preordain
        4 Prismatic Ending
        4 Ragavan, Nimble Pilferer
        4 Scalding Tarn
        1 Strip Mine
        1 Time Walk
        1 Treasure Cruise
        2 Tundra
        4 Volcanic Island
        4 Wasteland
        
        1 Force of Negation
        1 Lurrus of the Dream-Den
        2 Pyroblast
        1 Red Elemental Blast
        4 Shattering Spree
        2 Swords to Plowshares
        4 Tormod's Crypt
        """)


@pytest.mark.skip("Skipping network-hitting tests")
@pytest.mark.parametrize("downloader_class, url, expected", generate_test_cases_for_test_deck_list_download())
def test_deck_list_download(downloader_class: typing.Type[DecklistDownloader], url: str, expected: str):
    downloader = downloader_class()
    assert_that(
        downloader.download(url),
        is_(all_of(
                expected,
                instance_of(str),
            )
        )
    )

