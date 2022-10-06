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
    IsIdentifyingDeckUrlValidator, DecklistDownloader, TappedOutDownloader, MoxfieldDownloader


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
    yield TappedOutDownloader, "https://tappedout.net/mtg-decks/mtgproxyprinter-test-deck/", textwrap.dedent("""\
    Board,Qty,Name,Printing,Foil,Alter,Signed,Condition,Language
    main,1,Forest,,,,,,
    main,1,Island,,,,,,
    main,1,Mountain,UNF,,,,,
    """)
    yield MoxfieldDownloader, "https://www.moxfield.com/decks/g1i2wHXC3kW0lanwY4Llkw", textwrap.dedent("""\
        count,scryfall_id,lang,name,set_code,collector_number
        1,bc883e4e-e5f5-4823-ac2a-9ff8b7772926,en,"Zamriel, Seraph of Steel",gn3,1
        1,e9d36855-c38a-4bba-a642-cff3f81e057e,en,Path to Exile,2xm,25
        2,85d2ecc7-4a49-48f1-9036-6c3f0f0296c3,en,Banisher Priest,c20,77
        1,52c5c5cf-0ed6-4953-a03a-af51038e3f54,en,Strength of Arms,soi,40
        1,8e3c18f5-89cd-4d33-8d5b-12dacad9f9b3,en,Captain of the Watch,m13,8
        1,99263917-25ca-4d54-b1f9-d6d316747088,en,Swords to Plowshares,40k,190
        1,ce5391bc-6b50-49b0-96a1-df944a55d62e,en,"Danitha Capashen, Paragon",cmr,370
        2,65998e94-15a0-41f1-8288-730b957f81df,en,Valorous Stance,frf,28
        1,c17056e7-95c6-4bed-a747-3b40dcda275a,en,Forbidding Spirit,rna,9
        1,084d66a3-5248-4ca9-82ed-5c510c2df40f,en,Vow of Duty,cma,29
        1,88549b0e-063a-4faf-984e-efff33522f14,en,Heavenly Blademaster,c18,3
        1,fb1b7468-85f9-472e-9f7c-b268f84aea1c,en,Argentum Armor,afc,198
        2,88e2315e-41d9-4e46-bee4-c8f92e91e2a9,en,Kitesail Apprentice,wwk,10
        1,fa35b2b5-3e91-4a6c-90b1-8581b4ecaf8b,en,Colossus Hammer,m20,223
        2,d7cd85ac-e826-4b16-b9ab-864ae2cabed1,en,Kor Duelist,mm2,22
        1,63b4041d-7c95-4cb9-a18b-6568db05942b,en,Greatsword,m12,209
        2,00006596-1166-4a79-8443-ca9f82e6db4e,en,Kor Outfitter,zen,21
        1,a4ace878-6d15-4276-9bfb-2f23667c6d7e,en,Moonsilver Spear,afc,212
        2,c86714f5-e909-413f-8eb6-99dbea4d1897,en,Pilgrim of the Ages,stx,22
        1,1ee2e94f-5b06-4df0-ba87-4499b1ee4dba,en,Ring of Thune,m13,213
        2,d56afc99-5168-4853-afbb-eab32d62c472,en,Serra Angel,dvd,10
        1,032af060-4d49-4a0a-8841-9eb2d45a4b77,en,Sword of Vengeance,cmr,475
        1,5e635346-63e1-4e71-be1d-bd53afbaa037,en,Howling Golem,gn2,54
        2,86c9838e-aa72-49fc-bae2-f880bcbc9313,en,Trusty Machete,zen,209
        2,2ba18114-af6c-48cd-82c9-eb6541d566bf,en,Ancestral Blade,m20,3
        26,116a7806-1513-44b9-ae95-cbedb7e96b89,en,Plains,und,87
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

