# Copyright (C) 2020, 2021 Thomas Hess <thomas.hess@udo.edu>

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

import dataclasses
import typing
import unittest.mock

from hamcrest import *
import pytest

from mtg_proxy_printer.card_info_downloader import SetWackinessScore
from mtg_proxy_printer.model.carddb import CardDatabase
from .helpers import assert_model_is_empty, fill_card_database_with_json_card, load_json, assert_relation_is_empty, \
    fill_card_database_with_json_cards


class DatabasePrintingData(typing.NamedTuple):
    """Rows stored in the Printing relation"""
    collector_number: str
    scryfall_id: str
    is_oversized: bool
    highres_image: bool


class DatabaseCardFaceData(typing.NamedTuple):
    """Rows stored in the CardFace relation"""
    image_uri: str
    is_front: bool
    face_number: int


class DatabaseSetData(typing.NamedTuple):
    """Row data stored in the Set relation"""
    set_code: str
    set_name: str
    set_uri: str
    release_date: str


class DatabaseVisiblePrintingsData(typing.NamedTuple):
    """Row retrieved via VisiblePrintings view"""
    name: str
    set_code: str
    language: str
    collector_number: str
    scryfall_id: str
    highres_image: bool
    image_uri: str
    is_front: bool
    is_oversized: bool


@dataclasses.dataclass(frozen=True)
class FaceData:
    """Contains all data that is unique per card face."""
    # Implementation note: Implemented as a frozen dataclass,
    # because this is not meant to be fed directly into an _assert_* method expecting a list of tuples.
    name: str
    image_uri: str
    is_front: bool


@dataclasses.dataclass(frozen=True)
class TestCaseData:
    """
    Contains the JSON document name and all card data parsed from the JSON. This is sufficient to construct a test
    case and contains all validation data. The methods db_*() return lists of tuples suitable to test database content.
    """
    # Implementation note: Implemented as a frozen dataclass,
    # because this is not meant to be fed directly into an _assert_* method expecting a list of tuples.
    json_name: str
    highres_image: bool
    face_data: typing.Tuple[FaceData, ...]
    set: DatabaseSetData
    language: str
    collector_number: str
    scryfall_id: str
    oracle_id: str
    is_oversized: bool

    __test__ = False  # Instruct PyTest to not collect this as a Test class, even if the name starts with "Test"

    def db_card(self) -> typing.List[typing.Tuple[str]]:
        return [(self.oracle_id,)]

    def db_set(self):
        return [self.set]

    def db_print_language(self):
        return [(self.language,)]

    def db_face_name(self) -> typing.List[typing.Tuple[str]]:
        # De-duplicate face names, in case both sides of a double-faced card have the same name. This is true for
        # art series cards, certain double-faced tokens (for example the C16 Saproling token) and similar.
        return list(set((face.name,) for face in self.face_data))

    def db_card_face(self) -> typing.List[DatabaseCardFaceData]:
        return [
            DatabaseCardFaceData(
                face.image_uri, face.is_front, face_number)
            for face_number, face in enumerate(self.face_data)
        ]

    def db_all_printings(self) -> typing.List[DatabaseVisiblePrintingsData]:
        return [
            DatabaseVisiblePrintingsData(
                face.name, self.set.set_code, self.language, self.collector_number, self.scryfall_id,
                self.highres_image, face.image_uri, face.is_front, self.is_oversized)
            for face in self.face_data
        ]

    def db_printing(self) -> typing.List[DatabasePrintingData]:
        return [
            DatabasePrintingData(self.collector_number, self.scryfall_id, self.is_oversized, self.highres_image)
        ]


def _assert_card_contains(card_db: CardDatabase, test_case: TestCaseData):
    """Checks Oracle_id"""
    assert_that(
        data := card_db.db.execute('SELECT oracle_id FROM Card').fetchall(),
        contains_inanyorder(*test_case.db_card()),
        f"Card relation contains unexpected data: {data}")


def _assert_print_language_contains(
        card_db: CardDatabase, test_case: TestCaseData):
    """Checks language"""
    assert_that(
        data := card_db.db.execute(f'SELECT "language" FROM PrintLanguage').fetchall(),
        contains_inanyorder(*test_case.db_print_language()),
        f"PrintLanguage relation contains unexpected data: {data}")


def _assert_set_contains(card_db: CardDatabase, test_case: TestCaseData):
    """Checks "set", set_name, scryfall_set_uri, release_date"""
    assert_that(
        card_db.db.execute("SELECT set_code, set_name, set_uri, release_date FROM MTGSet").fetchall(),
        contains_inanyorder(*test_case.db_set()),
        f"Set relation contains unexpected data")


def _assert_face_name_contains(card_db: CardDatabase, test_case: TestCaseData):
    """Checks card_name"""
    assert_that(
        data := card_db.db.execute("SELECT card_name FROM FaceName").fetchall(),
        contains_inanyorder(*test_case.db_face_name()),
        f"FaceName relation contains unexpected data: {data}")


def _assert_printing_contains(card_db: CardDatabase, test_case: TestCaseData, *, is_hidden: bool = False):
    """Checks collector_number, scryfall_id, is_oversized, highres_image"""
    assert_that(
        data := [
            (collector_number, scryfall_id, bool(is_oversized), bool(highres_image))
            for collector_number, scryfall_id, is_oversized, highres_image
            in card_db.db.execute(
                "SELECT collector_number, scryfall_id, is_oversized, highres_image FROM Printing")
         ],
        contains_inanyorder(*test_case.db_printing()),
        f"Printing relation contains unexpected data: {data}")
    for item in data:
        assert_that(
            bool(card_db.db.execute(
                "SELECT is_hidden FROM Printing WHERE scryfall_id = ?\n",
                (item[1],)).fetchone()[0]),
            is_(is_hidden)
        )


def _assert_card_face_contains(card_db: CardDatabase, test_case: TestCaseData, relation_name: str = "CardFace"):
    """Checks png_image_uri, is_front, face_number"""
    assert_that(
        data := card_db.db.execute(f"SELECT png_image_uri, is_front, face_number FROM {relation_name}").fetchall(),
        contains_inanyorder(*test_case.db_card_face()),
        f"CardFace relation contains unexpected data: {data}")


def _assert_visible_printings_contains(card_db: CardDatabase, test_case: TestCaseData):
    """
    Checks
      card_name, set_code, "language", collector_number, scryfall_id,
      highres_image, png_image_uri, is_front, is_oversized
    """
    assert_that(
        data := card_db.db.execute(
            'SELECT card_name, set_code, "language", collector_number, scryfall_id, highres_image, '
            'png_image_uri, is_front, is_oversized FROM VisiblePrintings').fetchall(),
        contains_inanyorder(*test_case.db_all_printings()),
        f"VisiblePrintings relation contains unexpected data: {data}")


def assert_visible_import(card_db: CardDatabase, test_case: TestCaseData):
    """
    Verifies that the printing is both correctly stored, and visible in all VIEWs that filter out unwanted printings.
    """
    _assert_printing_contains(card_db, test_case, is_hidden=False)
    _assert_card_face_contains(card_db, test_case)
    _assert_face_name_contains(card_db, test_case)
    _assert_set_contains(card_db, test_case)
    _assert_card_contains(card_db, test_case)
    _assert_print_language_contains(card_db, test_case)
    _assert_visible_printings_contains(card_db, test_case)


def assert_hidden_import(card_db: CardDatabase, test_case: TestCaseData):
    """
    Verifies that the printing is correctly stored, but invisible in all VIEWs that filter out unwanted printings.
    """
    _assert_print_language_contains(card_db, test_case)
    _assert_printing_contains(card_db, test_case, is_hidden=True)
    _assert_card_face_contains(card_db, test_case)
    _assert_face_name_contains(card_db, test_case)
    _assert_set_contains(card_db, test_case)
    _assert_card_contains(card_db, test_case)
    for filtered_view in (
            "VisiblePrintings",
            ):
        assert_relation_is_empty(card_db, filtered_view)


def generate_test_cases_for_test_card_import():
    yield TestCaseData(  # Chinese "Growing Rites of Itlimoc // Itlimoc, Cradle of the Sun"
        "non_english_double_faced_card", False, (
            FaceData("伊替莫成长仪式", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/000847d3-ebde-4580-a00e-61d501e99485.png?1562549619", True),
            FaceData("烈阳育所伊替莫", "https://c1.scryfall.com/file/scryfall-cards/png/back/0/0/000847d3-ebde-4580-a00e-61d501e99485.png?1562549619", False),
        ), DatabaseSetData("xln", "Ixalan", "https://scryfall.com/sets/xln?utm_source=api", "2017-09-29"),
        "zhs", "191", "000847d3-ebde-4580-a00e-61d501e99485", "ea9c459a-6047-43aa-968f-a582be4000e8", False,
    )
    yield TestCaseData(  # Korean "Cut // Ribbons"
        "split_card", False, (
            FaceData("절단", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/00031562-3818-49f9-b45c-ab28a521284c.png?1540283200", True),
            FaceData("띠", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/00031562-3818-49f9-b45c-ab28a521284c.png?1540283200", True),
        ), DatabaseSetData("akh", "Amonkhet", "https://scryfall.com/sets/akh?utm_source=api", "2017-04-28"),
        "ko", "223", "00031562-3818-49f9-b45c-ab28a521284c", "98a5bf1a-1088-4339-9a9b-6ee5e4956cf1", False,
    )
    yield TestCaseData(  # English art series card "Clearwater Pathway // Clearwater Pathway"
        "english_double_faced_art_series_card", False, (
            FaceData("Clearwater Pathway", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/002ad179-ddf4-4f48-9504-cfa02e11a52e.png?1600982859", True),
            FaceData("Clearwater Pathway", "https://c1.scryfall.com/file/scryfall-cards/png/back/0/0/002ad179-ddf4-4f48-9504-cfa02e11a52e.png?1600982859", False),
        ), DatabaseSetData("aznr", "Zendikar Rising Art Series", "https://scryfall.com/sets/aznr?utm_source=api", "2020-09-25"),
        "en", "25", "002ad179-ddf4-4f48-9504-cfa02e11a52e", "a755add5-04ec-4e37-9eb6-152d52cfa46d", False,
    )
    yield TestCaseData(  # English "Fury Sliver" from Time Spiral
        "regular_english_card", True, (
            FaceData("Fury Sliver", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979", True),
        ), DatabaseSetData("tsp", "Time Spiral", "https://scryfall.com/sets/tsp?utm_source=api", "2006-10-06"),
        "en", "157", "0000579f-7b35-4ed3-b44c-db2a538066fe", "44623693-51d6-49ad-8cd7-140505caf02f", False,
    )
    yield TestCaseData(  # English special printing of Stitch in Time // Stitch in Time, which has the same card on both sides
        "double_faced_card_without_top_level_oracle_id", False, (
            FaceData("Stitch in Time", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/8/087c3a0d-c710-4451-989e-596b55352184.png?1637270835", True),
            FaceData("Stitch in Time", "https://c1.scryfall.com/file/scryfall-cards/png/back/0/8/087c3a0d-c710-4451-989e-596b55352184.png?1637270835", False),
        ), DatabaseSetData("sld", "Secret Lair Drop", "https://scryfall.com/sets/sld?utm_source=api","2022-04-22"),
        "en", "382", "087c3a0d-c710-4451-989e-596b55352184", "59b2a90e-542f-4fb0-b290-ac79dc2892a4", False,
    )


@pytest.mark.parametrize("test_case", generate_test_cases_for_test_card_import())
def test_card_import(qtbot, card_db: CardDatabase, test_case: TestCaseData):
    fill_card_database_with_json_card(qtbot, card_db, test_case.json_name)
    assert_visible_import(card_db, test_case)


def generate_test_cases_for_test_download_filters():
    yield TestCaseData(  # German printing of "Crusade"
        "depicting_racism", False, (
            FaceData("Kreuzzug", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/00809cb0-b152-441f-a0be-1bc1048dad92.png?1559603956", True),
        ), DatabaseSetData("4ed", "Fourth Edition", "https://scryfall.com/sets/4ed?utm_source=api", "1995-04-01"),
        "de", "20", "00809cb0-b152-441f-a0be-1bc1048dad92", "4692740f-be90-459f-8d90-c4ae71771595", False,
    ), "hide-cards-depicting-racism"
    yield TestCaseData(  # Spanish printing of "Air Elemental"
        "placeholder_image", False, (
            FaceData("Elemental del aire", "https://c1.scryfall.com/file/scryfall-cards/png/front/5/a/5a93fe66-620a-4f47-8a07-cff887c1e5d4.png?1557431149", True),
        ), DatabaseSetData("4bb", "Fourth Edition Foreign Black Border", "https://scryfall.com/sets/4bb?utm_source=api", "1995-04-01"),
        "es", "59", "5a93fe66-620a-4f47-8a07-cff887c1e5d4", "7744bae4-a8b7-44a5-9b4c-0048ad4cc448", False,
    ), "hide-cards-without-images"
    yield TestCaseData(  # Oversized printing of "Atraxa, Praetors' Voice"
        "oversized_card", True, (
            FaceData("Atraxa, Praetors' Voice", "https://c1.scryfall.com/file/scryfall-cards/png/front/6/5/650722b4-d72b-4745-a1a5-00a34836282b.png?1561757296", True),
        ), DatabaseSetData("oc16", "Commander 2016 Oversized", "https://scryfall.com/sets/oc16?utm_source=api", "2016-11-11"),
        "en", "28", "650722b4-d72b-4745-a1a5-00a34836282b", "7e6b9b59-cd68-4e3c-827b-38833c92d6eb", True,
    ), "hide-oversized-cards"
    yield TestCaseData(  # Silver-bordered "Aesthetic Consultation" from Unhinged
        "funny_card_with_silver_border", True, (
            FaceData("Aesthetic Consultation", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/4/0464a507-20e5-42d5-8aca-12504a869f21.png?1562487441", True),
        ), DatabaseSetData("unh", "Unhinged", "https://scryfall.com/sets/unh?utm_source=api", "2004-11-19"),
        "en", "48", "0464a507-20e5-42d5-8aca-12504a869f21", "8789d5fa-101c-457a-90ec-5cf067f5289b", False,
    ), "hide-funny-cards"
    yield TestCaseData(  # Black-bordered "Form of the Approach of the Second Sun" from Unfinity
        "funny_card_with_acorn_security_stamp", True, (
            FaceData("Form of the Approach of the Second Sun", "https://cards.scryfall.io/png/front/2/1/2149da9d-35ad-4f32-8072-fb515100b2fd.png?1673913099", True),
        ), DatabaseSetData("unf", "Unfinity", "https://scryfall.com/sets/unf?utm_source=api", "2022-10-07"),
        "en", "9", "2149da9d-35ad-4f32-8072-fb515100b2fd", "6e3a97ee-472f-49a8-908a-8e71f815edab", False,
    ), "hide-funny-cards"
    yield TestCaseData(
        "gold_bordered_card", True, (
            FaceData("Abduction", "https://c1.scryfall.com/file/scryfall-cards/png/front/2/a/2afb04a3-2940-4860-a4be-223aca0bac4b.png?1562904104", True),
        ), DatabaseSetData("wc97", "World Championship Decks 1997", "https://scryfall.com/sets/wc97?utm_source=api", "1997-08-13"),
        "en", "pm30", "2afb04a3-2940-4860-a4be-223aca0bac4b", "d0e1904e-1a37-41f6-8582-b9ea794bb886", False,
    ), "hide-gold-bordered"
    yield TestCaseData(
        "white_bordered_card", True, (
            FaceData("Abomination", "https://c1.scryfall.com/file/scryfall-cards/png/front/a/3/a363bc91-8278-448e-9d5c-564e4b51eb62.png?1559603880", True),
        ), DatabaseSetData("4ed", "Fourth Edition", "https://scryfall.com/sets/4ed?utm_source=api", "1995-04-01"),
        "en", "117", "a363bc91-8278-448e-9d5c-564e4b51eb62", "2c57c4e9-0a46-45d6-92db-9203fb722b60", False,
    ), "hide-white-bordered"
    yield TestCaseData(
        "banned_in_brawl", True, (
            FaceData("Oko, Thief of Crowns", "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
        ), DatabaseSetData("eld", "Throne of Eldraine", "https://scryfall.com/sets/eld?utm_source=api", "2019-10-04"),
        "en", "197", "3462a3d0-5552-49fa-9eb7-100960c55891", "60c60923-ff1b-43f7-8768-731499fcffc9", False,
    ), "hide-banned-in-brawl"
    yield TestCaseData(
        "banned_in_commander", True, (
            FaceData("Worldfire", "https://c1.scryfall.com/file/scryfall-cards/png/front/2/e/2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11.png?1562552052", True),
        ), DatabaseSetData("m13", "Magic 2013", "https://scryfall.com/sets/m13?utm_source=api", "2012-07-13"),
        "en", "158", "2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11", "ae0b8c13-0a71-4a60-bf9f-6e2da9503e9c", False,
    ), "hide-banned-in-commander"
    yield TestCaseData(
        "banned_in_historic", True, (
            FaceData("Oko, Thief of Crowns", "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
        ), DatabaseSetData("eld", "Throne of Eldraine", "https://scryfall.com/sets/eld?utm_source=api", "2019-10-04"),
        "en", "197", "3462a3d0-5552-49fa-9eb7-100960c55891", "60c60923-ff1b-43f7-8768-731499fcffc9", False,
    ), "hide-banned-in-historic"
    yield TestCaseData(
        "banned_in_legacy", True, (
            FaceData("Falling Star", "https://c1.scryfall.com/file/scryfall-cards/png/front/f/2/f2b9983e-20d4-4d12-9e2c-ec6d9a345787.png?1562861838", True),
        ), DatabaseSetData("leg", "Legends", "https://scryfall.com/sets/leg?utm_source=api", "1994-06-01"),
        "en", "145", "f2b9983e-20d4-4d12-9e2c-ec6d9a345787", "f5ca7b13-8003-4361-b827-7095c89f2750", False,
    ), "hide-banned-in-legacy"
    yield TestCaseData(
        "banned_in_modern", True, (
            FaceData("Oko, Thief of Crowns", "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
        ), DatabaseSetData("eld", "Throne of Eldraine", "https://scryfall.com/sets/eld?utm_source=api", "2019-10-04"),
        "en", "197", "3462a3d0-5552-49fa-9eb7-100960c55891", "60c60923-ff1b-43f7-8768-731499fcffc9", False,
    ), "hide-banned-in-modern"
    yield TestCaseData(
        "banned_in_pauper", True, (
            FaceData("Expedition Map", "https://c1.scryfall.com/file/scryfall-cards/png/front/5/5/551c0a45-9515-4e51-84e5-79703832a661.png?1599709184", True),
        ), DatabaseSetData("2xm", "Double Masters", "https://scryfall.com/sets/2xm?utm_source=api", "2020-08-07"),
        "en", "255", "551c0a45-9515-4e51-84e5-79703832a661", "8fcf50cd-e6d0-4516-850f-d42ee75dcc3a", False,
    ), "hide-banned-in-pauper"
    yield TestCaseData(  # The format has zero banned cards. The JSON document was altered to fake a banned card for testing purposes.
        "banned_in_penny", True, (
            FaceData("Falling Star", "https://c1.scryfall.com/file/scryfall-cards/png/front/f/2/f2b9983e-20d4-4d12-9e2c-ec6d9a345787.png?1562861838", True),
        ), DatabaseSetData("leg", "Legends", "https://scryfall.com/sets/leg?utm_source=api", "1994-06-01"),
        "en", "145", "f2b9983e-20d4-4d12-9e2c-ec6d9a345787", "f5ca7b13-8003-4361-b827-7095c89f2750", False,
    ), "hide-banned-in-penny"
    yield TestCaseData(
        "banned_in_pioneer", True, (
            FaceData("Oko, Thief of Crowns", "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
        ), DatabaseSetData("eld", "Throne of Eldraine", "https://scryfall.com/sets/eld?utm_source=api", "2019-10-04"),
        "en", "197", "3462a3d0-5552-49fa-9eb7-100960c55891", "60c60923-ff1b-43f7-8768-731499fcffc9", False,
    ), "hide-banned-in-pioneer"
    yield TestCaseData(
        "banned_in_standard", True, (
            FaceData("Oko, Thief of Crowns", "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
        ), DatabaseSetData("eld", "Throne of Eldraine", "https://scryfall.com/sets/eld?utm_source=api", "2019-10-04"),
        "en", "197", "3462a3d0-5552-49fa-9eb7-100960c55891", "60c60923-ff1b-43f7-8768-731499fcffc9", False,
    ), "hide-banned-in-standard"
    yield TestCaseData(
        "banned_in_vintage", True, (
            FaceData("Falling Star", "https://c1.scryfall.com/file/scryfall-cards/png/front/f/2/f2b9983e-20d4-4d12-9e2c-ec6d9a345787.png?1562861838", True),
        ), DatabaseSetData("leg", "Legends", "https://scryfall.com/sets/leg?utm_source=api", "1994-06-01"),
        "en", "145", "f2b9983e-20d4-4d12-9e2c-ec6d9a345787", "f5ca7b13-8003-4361-b827-7095c89f2750", False,
    ), "hide-banned-in-vintage"
    yield TestCaseData(
        "digital_only_card", False, (
            FaceData("Angel of Eternal Dawn", "https://c1.scryfall.com/file/scryfall-cards/png/front/7/a/7a7640d4-72e0-42e4-96ea-eaedc7ffb304.png?1645416649", True),
        ), DatabaseSetData("y22", "Alchemy: Innistrad", "https://scryfall.com/sets/y22?utm_source=api", "2021-12-09"),
        "en", "1", "7a7640d4-72e0-42e4-96ea-eaedc7ffb304", "9fb2f004-96a4-49ba-9f62-ba60fa27c895", False,
    ), "hide-digital-cards"
    yield TestCaseData(
        "digital_reprint", False, (
            FaceData("Serra Ascendant", "https://c1.scryfall.com/file/scryfall-cards/png/front/b/7/b72e71c7-a65c-481d-8ad7-77bfb5d66d73.png?1576794512", True),
        ), DatabaseSetData("ha1", "Historic Anthology 1", "https://scryfall.com/sets/ha1?utm_source=api", "2019-11-21"),
        "en", "1", "b72e71c7-a65c-481d-8ad7-77bfb5d66d73", "27ad3e00-6ffb-48f7-8469-8868d066d1e2", False,
    ), "hide-digital-cards"
    yield TestCaseData(
        "borderless_card", True, (
            FaceData("Absorb", "https://cards.scryfall.io/png/front/8/7/87a7ff06-32b7-48cd-99bb-a91f7f43538d.png?1682713062", True),
        ), DatabaseSetData("dmr", "Dominaria Remastered", "https://scryfall.com/sets/dmr?utm_source=api", "2023-01-13"),
        "en", "443", "87a7ff06-32b7-48cd-99bb-a91f7f43538d", "132ca99a-a3c7-4ed6-b4d0-0edcd7140ca2", False,
    ), "hide-borderless"
    TestCaseData(  # English special printing of Stitch in Time // Stitch in Time, which has the same card on both sides
        "double_faced_card_without_top_level_oracle_id", False, (
            FaceData("Stitch in Time", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/8/087c3a0d-c710-4451-989e-596b55352184.png?1637270835", True),
            FaceData("Stitch in Time", "https://c1.scryfall.com/file/scryfall-cards/png/back/0/8/087c3a0d-c710-4451-989e-596b55352184.png?1637270835", False),
        ), DatabaseSetData("sld", "Secret Lair Drop", "https://scryfall.com/sets/sld?utm_source=api", "2022-04-22"),
        "en", "382", "087c3a0d-c710-4451-989e-596b55352184", "59b2a90e-542f-4fb0-b290-000000000000", False,
    ), "hide-reversible-cards"


@pytest.mark.parametrize("filter_setting", [True, False])
@pytest.mark.parametrize("test_case, filter_name", generate_test_cases_for_test_download_filters())
def test_download_filters(
        qtbot, card_db: CardDatabase, test_case: TestCaseData, filter_name: str, filter_setting: bool):
    fill_card_database_with_json_card(qtbot, card_db, test_case.json_name, {filter_name: str(filter_setting)})
    if filter_setting:
        assert_hidden_import(card_db, test_case)
    else:
        assert_visible_import(card_db, test_case)


def generate_test_cases_for_test_download_filters_does_not_affect_unexpected_cards():
    yield TestCaseData(  # Black-bordered "Aerialephant" from Unfinity
        "funny_legal_card", True, (
            FaceData("Aerialephant", "https://cards.scryfall.io/png/front/1/a/1a2f4abd-089e-4015-a207-8a62616668b1.png?1673912986", True),
        ), DatabaseSetData("unf", "Unfinity", "https://scryfall.com/sets/unf?utm_source=api", "2022-10-07"),
        "en", "2", "1a2f4abd-089e-4015-a207-8a62616668b1", "20046568-b067-49fb-93b4-2ee86421f14b", False,
    ), "hide-funny-cards"


@pytest.mark.parametrize("filter_setting", [True, False])
@pytest.mark.parametrize(
    "test_case, filter_name", generate_test_cases_for_test_download_filters_does_not_affect_unexpected_cards())
def test_download_filters_does_not_affect_unexpected_cards(
        qtbot, card_db: CardDatabase, test_case: TestCaseData, filter_name: str, filter_setting: bool):
    fill_card_database_with_json_card(qtbot, card_db, test_case.json_name, {filter_name: str(filter_setting)})
    assert_visible_import(card_db, test_case)


@pytest.mark.parametrize("test_case", [
    TestCaseData(
        "missing_image_double_faced_card", False, tuple(), DatabaseSetData("", "", "", ""), "en", "",
        "b120e3c2-21b1-43e3-b685-9cf62bd7aa07", "9110339d-72ba-4132-801f-cd2fd738b71d", False),
    TestCaseData(  # Crash discovered Oct 27th, 2022. The back face of this double faced card has no image_uris key
        "double_faced_card_with_missing_back_images", False, tuple(),  DatabaseSetData("", "", "", ""), "en", "",
        "003b8c93-54d2-4f23-961e-a52d63d0a54b", "9d9b52b2-2edc-4f7f-a8d9-e024b1398847", False),

])
def test_import_card_skips_import_of_card_with_missing_image(qtbot, card_db: CardDatabase, test_case: TestCaseData):
    fill_card_database_with_json_card(qtbot, card_db, test_case.json_name)
    assert_model_is_empty(card_db, test_case)


def test_two_imports_having_the_same_filtered_out_card_work(qtbot, card_db: CardDatabase):
    fill_card_database_with_json_card(qtbot, card_db, "missing_image_double_faced_card")
    assert_model_is_empty(
        card_db, TestCaseData(
            "", False, tuple(), DatabaseSetData("", "", "", ""), "en", "",
            "b120e3c2-21b1-43e3-b685-9cf62bd7aa07", "9110339d-72ba-4132-801f-cd2fd738b71d", False))
    fill_card_database_with_json_card(qtbot, card_db, "missing_image_double_faced_card")
    assert_model_is_empty(
        card_db, TestCaseData(
            "", False, tuple(), DatabaseSetData("", "", "", ""), "en", "",
            "b120e3c2-21b1-43e3-b685-9cf62bd7aa07", "9110339d-72ba-4132-801f-cd2fd738b71d", False))


def test_re_import_with_enabled_download_filter_removes_card(qtbot, card_db: CardDatabase):
    test_case = TestCaseData(  # Oversized printing of "Atraxa, Praetors' Voice"
        "oversized_card", True, (
            FaceData("Atraxa, Praetors' Voice", "https://c1.scryfall.com/file/scryfall-cards/png/front/6/5/650722b4-d72b-4745-a1a5-00a34836282b.png?1561757296", True),
        ), DatabaseSetData("oc16", "Commander 2016 Oversized", "https://scryfall.com/sets/oc16?utm_source=api", "2016-11-11"),
        "en", "28", "650722b4-d72b-4745-a1a5-00a34836282b", "7e6b9b59-cd68-4e3c-827b-38833c92d6eb", True,
    )
    filter_name = "hide-oversized-cards"
    # Pass 1: Populate the database and include the card. The card should be in the database afterwards
    fill_card_database_with_json_card(qtbot, card_db, test_case.json_name, {filter_name: "False"})
    assert_visible_import(card_db, test_case)
    # Pass 2: Re-Populate the database, but exclude the card now.
    fill_card_database_with_json_card(qtbot, card_db, test_case.json_name, {filter_name: "True"})
    # The card should not be visible
    assert_hidden_import(card_db, test_case)


def test_re_import_with_disabled_download_filter_removes_removed_printings_entry(qtbot, card_db: CardDatabase):
    test_case = TestCaseData(  # Oversized printing of "Atraxa, Praetors' Voice"
        "oversized_card", True, (
            FaceData("Atraxa, Praetors' Voice", "https://c1.scryfall.com/file/scryfall-cards/png/front/6/5/650722b4-d72b-4745-a1a5-00a34836282b.png?1561757296", True),
        ), DatabaseSetData("oc16", "Commander 2016 Oversized", "https://scryfall.com/sets/oc16?utm_source=api", "2016-11-11"),
        "en", "28", "650722b4-d72b-4745-a1a5-00a34836282b", "7e6b9b59-cd68-4e3c-827b-38833c92d6eb", True,
    )
    filter_name = "hide-oversized-cards"
    # Pass 1: Populate the database and exclude the card. The card should not be visible
    fill_card_database_with_json_card(qtbot, card_db, test_case.json_name, {filter_name: "True"})
    assert_hidden_import(card_db, test_case)
    # Pass 2: Re-Populate the database, but include the card now.
    fill_card_database_with_json_card(qtbot, card_db, test_case.json_name)
    # The card should be in the database. The RemovedPrintings table should be empty
    assert_visible_import(card_db, test_case)
    assert_that(
        card_db.db.execute("SELECT scryfall_id, oracle_id FROM RemovedPrintings").fetchall(),
        is_(empty()),
        "RemovedPrintings table not properly cleaned up."
    )


@pytest.mark.parametrize("test_case_data", [
    TestCaseData(  # English "Fury Sliver" from Time Spiral
        "regular_english_card", True, (
            FaceData("Fury Sliver", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979", True),
        ), DatabaseSetData("tsp", "Time Spiral", "https://scryfall.com/sets/tsp?utm_source=api", "2006-10-06"),
        "en", "157", "0000579f-7b35-4ed3-b44c-db2a538066fe", "44623693-51d6-49ad-8cd7-140505caf02f", False,
    ),
])
def test_re_import_after_card_ban_hides_it(qtbot, card_db: CardDatabase, test_case_data: TestCaseData):
    card_json = load_json(test_case_data.json_name)
    with unittest.mock.patch.dict(card_json["legalities"], {"commander": "banned"}):
        fill_card_database_with_json_card(qtbot, card_db, card_json, {"hide-banned-in-commander": "True"})
        assert_hidden_import(card_db, test_case_data)
    fill_card_database_with_json_card(qtbot, card_db, card_json, {"hide-banned-in-commander": "True"})
    assert_visible_import(card_db, test_case_data)


@pytest.mark.parametrize("test_case_data", [
    TestCaseData(  # English "Fury Sliver" from Time Spiral
        "regular_english_card", True, (
            FaceData("Fury Sliver", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979", True),
        ), DatabaseSetData("tsp", "Time Spiral", "https://scryfall.com/sets/tsp?utm_source=api", "2006-10-06"),
        "en", "157", "0000579f-7b35-4ed3-b44c-db2a538066fe", "44623693-51d6-49ad-8cd7-140505caf02f", False,
    ),
])
def test_re_import_after_unban_makes_card_visible(qtbot, card_db: CardDatabase, test_case_data: TestCaseData):
    card_json = load_json(test_case_data.json_name)
    fill_card_database_with_json_card(qtbot, card_db, card_json, {"hide-banned-in-commander": "True"})
    assert_visible_import(card_db, test_case_data)
    with unittest.mock.patch.dict(card_json["legalities"], {"commander": "banned"}):
        fill_card_database_with_json_card(qtbot, card_db, card_json, {"hide-banned-in-commander": "True"})
        assert_hidden_import(card_db, test_case_data)


def test_updates_language(qtbot, card_db: CardDatabase):
    test_case = TestCaseData(  # English "Fury Sliver" from Time Spiral. Modified the language
        "regular_english_card", True, (
            FaceData("Fury Sliver",
                     "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979",
                     True),
        ), DatabaseSetData("tsp", "Time Spiral", "https://scryfall.com/sets/tsp?utm_source=api", "2006-10-06"),
        "pl", "157", "0000579f-7b35-4ed3-b44c-db2a538066fe", "44623693-51d6-49ad-8cd7-140505caf02f", False,
    )
    json_data = load_json(test_case.json_name)
    fill_card_database_with_json_card(qtbot, card_db, json_data)
    with unittest.mock.patch.dict(json_data, {"lang": test_case.language}):
        fill_card_database_with_json_card(qtbot, card_db, json_data)
    assert_visible_import(card_db, test_case)


@pytest.mark.parametrize("test_case", [
    TestCaseData(  # English "Fury Sliver" from Time Spiral. Modified the oracle_id ID
        "regular_english_card", True, (
            FaceData("Fury Sliver",
                     "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979",
                     True),
        ), DatabaseSetData("tsp", "Time Spiral", "https://scryfall.com/sets/tsp?utm_source=api", "2006-10-06"),
        "en", "157", "0000579f-7b35-4ed3-b44c-db2a538066fe", "44623693-51d6-49ad-8cd7-000000000000", False,
    ),
    TestCaseData(  # English special printing of Stitch in Time // Stitch in Time, which has the same card on both sides
        "double_faced_card_without_top_level_oracle_id", False, (
            FaceData("Stitch in Time", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/8/087c3a0d-c710-4451-989e-596b55352184.png?1637270835", True),
            FaceData("Stitch in Time", "https://c1.scryfall.com/file/scryfall-cards/png/back/0/8/087c3a0d-c710-4451-989e-596b55352184.png?1637270835", False),
        ), DatabaseSetData("sld", "Secret Lair Drop", "https://scryfall.com/sets/sld?utm_source=api", "2022-04-22"),
        "en", "382", "087c3a0d-c710-4451-989e-596b55352184", "59b2a90e-542f-4fb0-b290-000000000000", False,
    )
])
def test_updates_card_oracle_id(qtbot, card_db: CardDatabase, test_case: TestCaseData):
    json_data = load_json(test_case.json_name)
    fill_card_database_with_json_card(qtbot, card_db, json_data)
    with unittest.mock.patch.dict(json_data, {"oracle_id": test_case.oracle_id}):
        fill_card_database_with_json_card(qtbot, card_db, json_data)
    assert_visible_import(card_db, test_case)


def test_updates_set_code(qtbot, card_db: CardDatabase):
    test_case = TestCaseData(  # English "Fury Sliver" from Time Spiral. Modified set code
        "regular_english_card", True, (
            FaceData("Fury Sliver",
                     "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979",
                     True),
        ), DatabaseSetData("tsa", "Time Spiral", "https://scryfall.com/sets/tsp?utm_source=api", "2006-10-06"),
        "en", "157", "0000579f-7b35-4ed3-b44c-db2a538066fe", "44623693-51d6-49ad-8cd7-140505caf02f", False,
    )
    json_data = load_json(test_case.json_name)
    fill_card_database_with_json_card(qtbot, card_db, json_data)
    with unittest.mock.patch.dict(json_data, {"set": test_case.set.set_code}):
        fill_card_database_with_json_card(qtbot, card_db, json_data)
    assert_visible_import(card_db, test_case)


def test_updates_set_name(qtbot, card_db: CardDatabase):
    test_case = TestCaseData(  # English "Fury Sliver" from Time Spiral. Modified the set name
        "regular_english_card", True, (
            FaceData("Fury Sliver",
                     "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979",
                     True),
        ), DatabaseSetData("tsp", "Time Spiral Altered", "https://scryfall.com/sets/tsp?utm_source=api", "2006-10-06"),
        "en", "157", "0000579f-7b35-4ed3-b44c-db2a538066fe", "44623693-51d6-49ad-8cd7-140505caf02f", False,
    )
    json_data = load_json(test_case.json_name)
    fill_card_database_with_json_card(qtbot, card_db, json_data)
    with unittest.mock.patch.dict(json_data, {"set_name": test_case.set.set_name}):
        fill_card_database_with_json_card(qtbot, card_db, json_data)
    assert_visible_import(card_db, test_case)


def test_updates_set_uri(qtbot, card_db: CardDatabase):
    test_case = TestCaseData(  # English "Fury Sliver" from Time Spiral. Modified the set URI
        "regular_english_card", True, (
            FaceData("Fury Sliver",
                     "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979",
                     True),
        ), DatabaseSetData("tsp", "Time Spiral", "https://scryfall.com/sets/tsa", "2006-10-06"),
        "en", "157", "0000579f-7b35-4ed3-b44c-db2a538066fe", "44623693-51d6-49ad-8cd7-140505caf02f", False,
    )
    json_data = load_json(test_case.json_name)
    fill_card_database_with_json_card(qtbot, card_db, json_data)
    with unittest.mock.patch.dict(json_data, {"scryfall_set_uri": test_case.set.set_uri}):
        fill_card_database_with_json_card(qtbot, card_db, json_data)
    assert_visible_import(card_db, test_case)


def test_updates_printing_collector_number(qtbot, card_db: CardDatabase):
    test_case = TestCaseData(  # English "Fury Sliver" from Time Spiral. Modified the collector_number
        "regular_english_card", True, (
            FaceData("Fury Sliver",
                     "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979",
                     True),
        ), DatabaseSetData("tsp", "Time Spiral", "https://scryfall.com/sets/tsp?utm_source=api", "2006-10-06"),
        "en", "1234", "0000579f-7b35-4ed3-b44c-db2a538066fe", "44623693-51d6-49ad-8cd7-140505caf02f", False,
    )
    json_data = load_json(test_case.json_name)
    fill_card_database_with_json_card(qtbot, card_db, json_data)
    with unittest.mock.patch.dict(json_data, {"collector_number": test_case.collector_number}):
        fill_card_database_with_json_card(qtbot, card_db, json_data)
    assert_visible_import(card_db, test_case)


def test_updates_printing_is_oversized(qtbot, card_db: CardDatabase):
    test_case = TestCaseData(  # English "Fury Sliver" from Time Spiral. Modified the oversized boolean
        "regular_english_card", True, (
            FaceData("Fury Sliver",
                     "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979",
                     True),
        ), DatabaseSetData("tsp", "Time Spiral", "https://scryfall.com/sets/tsp?utm_source=api", "2006-10-06"),
        "en", "157", "0000579f-7b35-4ed3-b44c-db2a538066fe", "44623693-51d6-49ad-8cd7-140505caf02f", True,
    )
    json_data = load_json(test_case.json_name)
    fill_card_database_with_json_card(qtbot, card_db, json_data)
    with unittest.mock.patch.dict(json_data, {"oversized": test_case.is_oversized}):
        fill_card_database_with_json_card(qtbot, card_db, json_data)
    assert_visible_import(card_db, test_case)


def test_updates_printing_highres_image(qtbot, card_db: CardDatabase):
    test_case = TestCaseData(  # English "Fury Sliver" from Time Spiral. Modified the highres_image boolean
        "regular_english_card", False, (
            FaceData("Fury Sliver",
                     "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979",
                     True),
        ), DatabaseSetData("tsp", "Time Spiral", "https://scryfall.com/sets/tsp?utm_source=api", "2006-10-06"),
        "en", "157", "0000579f-7b35-4ed3-b44c-db2a538066fe", "44623693-51d6-49ad-8cd7-140505caf02f", False,
    )
    json_data = load_json(test_case.json_name)
    fill_card_database_with_json_card(qtbot, card_db, json_data)
    with unittest.mock.patch.dict(json_data, {"highres_image": test_case.highres_image}):
        fill_card_database_with_json_card(qtbot, card_db, json_data)
    assert_visible_import(card_db, test_case)


@pytest.mark.parametrize("json_name, expected_score", [
    ("regular_english_card", SetWackinessScore.REGULAR),
    ("german_basic_Forest", SetWackinessScore.REGULAR),
    ("prerelease_promo_card", SetWackinessScore.PROMOTIONAL),
    ("white_bordered_card", SetWackinessScore.WHITE_BORDERED),
    ("funny_card_with_silver_border", SetWackinessScore.FUNNY),
    ("gold_bordered_card", SetWackinessScore.GOLD_BORDERED),
    ("digital_only_card", SetWackinessScore.DIGITAL),
    ("english_double_faced_art_series_card", SetWackinessScore.ART_SERIES),
    ("oversized_card", SetWackinessScore.OVERSIZED),
])
def test_set_wackiness_score(qtbot, card_db: CardDatabase, json_name: str, expected_score: SetWackinessScore):
    fill_card_database_with_json_card(qtbot, card_db, json_name)
    assert_that(
        card_db.db.execute('SELECT wackiness_score FROM MTGSet').fetchall(),
        contains_exactly(
            (expected_score,)
        )
    )

def test_related_printings(qtbot, card_db: CardDatabase):
    db = card_db.db
    cards = [
        "The_Underworld_Cookbook",
        "Food_Token",
        "Asmoranomardicadaistinaculdacar",
        "Bake_into_a_Pie",
        "Asmoranomardicadaistinaculdacar_2",
        "Food_Token_2",
    ]
    # Cards always relate to exact printings, but which one is chosen is rather arbitrary. E.g. The Underworld Cookbook
    # and Back into a Pie both create a Food token, but are set to different printings of that token card.
    fill_card_database_with_json_cards(qtbot, card_db, cards)
    assert_that(
        db.execute("SELECT card_id, related_id FROM RelatedPrintings").fetchall(),
        contains_inanyorder(
            # The Food token (card id 2) is never a source, as that would pull all cards creating that token
            (3, 1),  # Asmoranomardicadaistinaculdacar references The Underworld Cookbook by name
            (1, 3),  # Back relation
            (1, 2),  # Card mentions Food token
            (4, 2),  # Card mentions Food token
        )
    )
