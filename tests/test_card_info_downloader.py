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

from mtg_proxy_printer.model.carddb import CardDatabase
from .helpers import assert_model_is_empty, fill_card_database_with_json_card, load_json


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


class DatabaseAllPrintingsData(typing.NamedTuple):
    """Row retrieved via AllPrintings view"""
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

    def db_all_printings(self) -> typing.List[DatabaseAllPrintingsData]:
        return [
            DatabaseAllPrintingsData(
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


def _assert_print_language_contains(card_db: CardDatabase, test_case: TestCaseData):
    """Checks language"""
    assert_that(
        data := card_db.db.execute('SELECT "language" FROM PrintLanguage').fetchall(),
        contains_inanyorder(*test_case.db_print_language()),
        f"PrintLanguage relation contains unexpected data: {data}")


def _assert_set_contains(card_db: CardDatabase, test_case: TestCaseData):
    """Checks "set", set_name, scryfall_set_uri"""
    assert_that(
        card_db.db.execute('SELECT "set", set_name, set_uri FROM "Set"').fetchall(),
        contains_inanyorder(*test_case.db_set()),
        f"Set relation contains unexpected data")


def _assert_face_name_contains(card_db: CardDatabase, test_case: TestCaseData):
    """Checks card_name"""
    assert_that(
        data := card_db.db.execute('SELECT card_name FROM FaceName').fetchall(),
        contains_inanyorder(*test_case.db_face_name()),
        f"FaceName relation contains unexpected data: {data}")


def _assert_printing_contains(card_db: CardDatabase, test_case: TestCaseData):
    """Checks collector_number, scryfall_id, is_oversized, highres_image"""
    assert_that(
        data := [
            (collector_number, scryfall_id, bool(is_oversized), bool(highres_image))
            for collector_number, scryfall_id, is_oversized, highres_image
            in card_db.db.execute('SELECT collector_number, scryfall_id, is_oversized, highres_image FROM Printing')
         ],
        contains_inanyorder(*test_case.db_printing()),
        f"Printing relation contains unexpected data: {data}")


def _assert_card_face_contains(card_db: CardDatabase, test_case: TestCaseData):
    """Checks png_image_uri, is_front, face_number"""
    assert_that(
        data := card_db.db.execute("SELECT png_image_uri, is_front, face_number FROM CardFace").fetchall(),
        contains_inanyorder(*test_case.db_card_face()),
        f"CardFace relation contains unexpected data: {data}")


def _assert_all_printings_contains(card_db: CardDatabase, test_case: TestCaseData):
    """
    Checks
      card_name, set_code, "language", collector_number, scryfall_id,
      highres_image, png_image_uri, is_front, is_oversized
    """
    assert_that(
        data := card_db.db.execute(
            'SELECT card_name, set_code, "language", collector_number, scryfall_id, highres_image, '
            'png_image_uri, is_front, is_oversized FROM AllPrintings').fetchall(),
        contains_inanyorder(*test_case.db_all_printings()),
        f"AllPrintings relation contains unexpected data: {data}")


def assert_successful_import(card_db: CardDatabase, test_case: TestCaseData):
    _assert_all_printings_contains(card_db, test_case)
    _assert_printing_contains(card_db, test_case)
    _assert_card_face_contains(card_db, test_case)
    _assert_face_name_contains(card_db, test_case)
    _assert_set_contains(card_db, test_case)
    _assert_card_contains(card_db, test_case)
    _assert_print_language_contains(card_db, test_case)


def generate_test_cases_for_test_card_import():
    yield TestCaseData(  # Chinese "Growing Rites of Itlimoc // Itlimoc, Cradle of the Sun"
        "non_english_double_faced_card", False, (
            FaceData("伊替莫成长仪式", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/000847d3-ebde-4580-a00e-61d501e99485.png?1562549619", True),
            FaceData("烈阳育所伊替莫", "https://c1.scryfall.com/file/scryfall-cards/png/back/0/0/000847d3-ebde-4580-a00e-61d501e99485.png?1562549619", False),
        ), DatabaseSetData("xln", "Ixalan", "https://scryfall.com/sets/xln?utm_source=api"),
        "zhs", "191", "000847d3-ebde-4580-a00e-61d501e99485", "ea9c459a-6047-43aa-968f-a582be4000e8", False,
    )
    yield TestCaseData(  # Korean "Cut // Ribbons"
        "split_card", False, (
            FaceData("절단", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/00031562-3818-49f9-b45c-ab28a521284c.png?1540283200", True),
            FaceData("띠", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/00031562-3818-49f9-b45c-ab28a521284c.png?1540283200", True),
        ), DatabaseSetData("akh", "Amonkhet", "https://scryfall.com/sets/akh?utm_source=api"),
        "ko", "223", "00031562-3818-49f9-b45c-ab28a521284c", "98a5bf1a-1088-4339-9a9b-6ee5e4956cf1", False,
    )
    yield TestCaseData(  # English art series card "Clearwater Pathway // Clearwater Pathway"
        "english_double_faced_art_series_card", False, (
            FaceData("Clearwater Pathway", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/002ad179-ddf4-4f48-9504-cfa02e11a52e.png?1600982859", True),
            FaceData("Clearwater Pathway", "https://c1.scryfall.com/file/scryfall-cards/png/back/0/0/002ad179-ddf4-4f48-9504-cfa02e11a52e.png?1600982859", False),
        ), DatabaseSetData("aznr", "Zendikar Rising Art Series", "https://scryfall.com/sets/aznr?utm_source=api"),
        "en", "25", "002ad179-ddf4-4f48-9504-cfa02e11a52e", "a755add5-04ec-4e37-9eb6-152d52cfa46d", False,
    )
    yield TestCaseData(  # English "Fury Sliver" from Time Spiral
        "regular_english_card", True, (
            FaceData("Fury Sliver", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979", True),
        ), DatabaseSetData("tsp", "Time Spiral", "https://scryfall.com/sets/tsp?utm_source=api"),
        "en", "157", "0000579f-7b35-4ed3-b44c-db2a538066fe", "44623693-51d6-49ad-8cd7-140505caf02f", False,
    )
    yield TestCaseData(  # English special printing of Stitch in Time // Stitch in Time, which has the same card on both sides
        "double_faced_card_without_top_level_oracle_id", False, (
            FaceData("Stitch in Time", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/8/087c3a0d-c710-4451-989e-596b55352184.png?1637270835", True),
            FaceData("Stitch in Time", "https://c1.scryfall.com/file/scryfall-cards/png/back/0/8/087c3a0d-c710-4451-989e-596b55352184.png?1637270835", False),
        ), DatabaseSetData("sld", "Secret Lair Drop", "https://scryfall.com/sets/sld?utm_source=api"),
        "en", "382", "087c3a0d-c710-4451-989e-596b55352184", "59b2a90e-542f-4fb0-b290-ac79dc2892a4", False,
    )


@pytest.mark.parametrize("test_case", generate_test_cases_for_test_card_import())
def test_card_import(card_db: CardDatabase, test_case: TestCaseData):
    fill_card_database_with_json_card(card_db, test_case.json_name)
    assert_successful_import(card_db, test_case)


def generate_test_cases_for_test_download_filters():
    yield TestCaseData(  # German printing of "Crusade"
        "depicting_racism", False, (
            FaceData("Kreuzzug", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/00809cb0-b152-441f-a0be-1bc1048dad92.png?1559603956", True),
        ), DatabaseSetData("4ed", "Fourth Edition", "https://scryfall.com/sets/4ed?utm_source=api"),
        "de", "20", "00809cb0-b152-441f-a0be-1bc1048dad92", "4692740f-be90-459f-8d90-c4ae71771595", False,
    ), "download-cards-depicting-racism"
    yield TestCaseData(  # Spanish printing of "Air Elemental"
        "placeholder_image", False, (
            FaceData("Elemental del aire", "https://c1.scryfall.com/file/scryfall-cards/png/front/5/a/5a93fe66-620a-4f47-8a07-cff887c1e5d4.png?1557431149", True),
        ), DatabaseSetData("4bb", "Fourth Edition Foreign Black Border", "https://scryfall.com/sets/4bb?utm_source=api"),
        "es", "59", "5a93fe66-620a-4f47-8a07-cff887c1e5d4", "7744bae4-a8b7-44a5-9b4c-0048ad4cc448", False,
    ), "download-cards-without-images"
    yield TestCaseData(  # Oversized printing of "Atraxa, Praetors' Voice"
        "oversized_card", True, (
            FaceData("Atraxa, Praetors' Voice", "https://c1.scryfall.com/file/scryfall-cards/png/front/6/5/650722b4-d72b-4745-a1a5-00a34836282b.png?1561757296", True),
        ), DatabaseSetData("oc16", "Commander 2016 Oversized", "https://scryfall.com/sets/oc16?utm_source=api"),
        "en", "28", "650722b4-d72b-4745-a1a5-00a34836282b", "7e6b9b59-cd68-4e3c-827b-38833c92d6eb", True,
    ), "download-oversized-cards"
    yield TestCaseData(  # Silver-bordered "Aesthetic Consultation" from Unhinged
        "funny_card", True, (
            FaceData("Aesthetic Consultation", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/4/0464a507-20e5-42d5-8aca-12504a869f21.png?1562487441", True),
        ), DatabaseSetData("unh", "Unhinged", "https://scryfall.com/sets/unh?utm_source=api"),
        "en", "48", "0464a507-20e5-42d5-8aca-12504a869f21", "8789d5fa-101c-457a-90ec-5cf067f5289b", False,
    ), "download-funny-cards"
    yield TestCaseData(
        "gold_bordered_card", True, (
            FaceData("Abduction", "https://c1.scryfall.com/file/scryfall-cards/png/front/2/a/2afb04a3-2940-4860-a4be-223aca0bac4b.png?1562904104", True),
        ), DatabaseSetData("wc97", "World Championship Decks 1997", "https://scryfall.com/sets/wc97?utm_source=api"),
        "en", "pm30", "2afb04a3-2940-4860-a4be-223aca0bac4b", "d0e1904e-1a37-41f6-8582-b9ea794bb886", False,
    ), "download-gold-bordered"
    yield TestCaseData(
        "white_bordered_card", True, (
            FaceData("Abomination", "https://c1.scryfall.com/file/scryfall-cards/png/front/a/3/a363bc91-8278-448e-9d5c-564e4b51eb62.png?1559603880", True),
        ), DatabaseSetData("4ed", "Fourth Edition", "https://scryfall.com/sets/4ed?utm_source=api"),
        "en", "117", "a363bc91-8278-448e-9d5c-564e4b51eb62", "2c57c4e9-0a46-45d6-92db-9203fb722b60", False,
    ), "download-white-bordered"
    yield TestCaseData(
        "banned_in_brawl", True, (
            FaceData("Oko, Thief of Crowns", "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
        ), DatabaseSetData("eld", "Throne of Eldraine", "https://scryfall.com/sets/eld?utm_source=api"),
        "en", "197", "3462a3d0-5552-49fa-9eb7-100960c55891", "60c60923-ff1b-43f7-8768-731499fcffc9", False,
    ), "download-banned-in-brawl"
    yield TestCaseData(
        "banned_in_commander", True, (
            FaceData("Worldfire", "https://c1.scryfall.com/file/scryfall-cards/png/front/2/e/2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11.png?1562552052", True),
        ), DatabaseSetData("m13", "Magic 2013", "https://scryfall.com/sets/m13?utm_source=api"),
        "en", "158", "2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11", "ae0b8c13-0a71-4a60-bf9f-6e2da9503e9c", False,
    ), "download-banned-in-commander"
    yield TestCaseData(
        "banned_in_historic", True, (
            FaceData("Oko, Thief of Crowns", "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
        ), DatabaseSetData("eld", "Throne of Eldraine", "https://scryfall.com/sets/eld?utm_source=api"),
        "en", "197", "3462a3d0-5552-49fa-9eb7-100960c55891", "60c60923-ff1b-43f7-8768-731499fcffc9", False,
    ), "download-banned-in-historic"
    yield TestCaseData(
        "banned_in_legacy", True, (
            FaceData("Falling Star", "https://c1.scryfall.com/file/scryfall-cards/png/front/f/2/f2b9983e-20d4-4d12-9e2c-ec6d9a345787.png?1562861838", True),
        ), DatabaseSetData("leg", "Legends", "https://scryfall.com/sets/leg?utm_source=api"),
        "en", "145", "f2b9983e-20d4-4d12-9e2c-ec6d9a345787", "f5ca7b13-8003-4361-b827-7095c89f2750", False,
    ), "download-banned-in-legacy"
    yield TestCaseData(
        "banned_in_modern", True, (
            FaceData("Oko, Thief of Crowns", "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
        ), DatabaseSetData("eld", "Throne of Eldraine", "https://scryfall.com/sets/eld?utm_source=api"),
        "en", "197", "3462a3d0-5552-49fa-9eb7-100960c55891", "60c60923-ff1b-43f7-8768-731499fcffc9", False,
    ), "download-banned-in-modern"
    yield TestCaseData(
        "banned_in_pauper", True, (
            FaceData("Expedition Map", "https://c1.scryfall.com/file/scryfall-cards/png/front/5/5/551c0a45-9515-4e51-84e5-79703832a661.png?1599709184", True),
        ), DatabaseSetData("2xm", "Double Masters", "https://scryfall.com/sets/2xm?utm_source=api"),
        "en", "255", "551c0a45-9515-4e51-84e5-79703832a661", "8fcf50cd-e6d0-4516-850f-d42ee75dcc3a", False,
    ), "download-banned-in-pauper"
    yield TestCaseData(  # The format has zero banned cards. The JSON document was altered to fake a banned card for testing purposes.
        "banned_in_penny", True, (
            FaceData("Falling Star", "https://c1.scryfall.com/file/scryfall-cards/png/front/f/2/f2b9983e-20d4-4d12-9e2c-ec6d9a345787.png?1562861838", True),
        ), DatabaseSetData("leg", "Legends", "https://scryfall.com/sets/leg?utm_source=api"),
        "en", "145", "f2b9983e-20d4-4d12-9e2c-ec6d9a345787", "f5ca7b13-8003-4361-b827-7095c89f2750", False,
    ), "download-banned-in-penny"
    yield TestCaseData(
        "banned_in_pioneer", True, (
            FaceData("Oko, Thief of Crowns", "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
        ), DatabaseSetData("eld", "Throne of Eldraine", "https://scryfall.com/sets/eld?utm_source=api"),
        "en", "197", "3462a3d0-5552-49fa-9eb7-100960c55891", "60c60923-ff1b-43f7-8768-731499fcffc9", False,
    ), "download-banned-in-pioneer"
    yield TestCaseData(
        "banned_in_standard", True, (
            FaceData("Oko, Thief of Crowns", "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
        ), DatabaseSetData("eld", "Throne of Eldraine", "https://scryfall.com/sets/eld?utm_source=api"),
        "en", "197", "3462a3d0-5552-49fa-9eb7-100960c55891", "60c60923-ff1b-43f7-8768-731499fcffc9", False,
    ), "download-banned-in-standard"
    yield TestCaseData(
        "banned_in_vintage", True, (
            FaceData("Falling Star", "https://c1.scryfall.com/file/scryfall-cards/png/front/f/2/f2b9983e-20d4-4d12-9e2c-ec6d9a345787.png?1562861838", True),
        ), DatabaseSetData("leg", "Legends", "https://scryfall.com/sets/leg?utm_source=api"),
        "en", "145", "f2b9983e-20d4-4d12-9e2c-ec6d9a345787", "f5ca7b13-8003-4361-b827-7095c89f2750", False,
    ), "download-banned-in-vintage"
    yield TestCaseData(
        "digital_only_card", False, (
            FaceData("Angel of Eternal Dawn", "https://c1.scryfall.com/file/scryfall-cards/png/front/7/a/7a7640d4-72e0-42e4-96ea-eaedc7ffb304.png?1645416649", True),
        ), DatabaseSetData("y22", "Alchemy: Innistrad", "https://scryfall.com/sets/y22?utm_source=api"),
        "en", "1", "7a7640d4-72e0-42e4-96ea-eaedc7ffb304", "9fb2f004-96a4-49ba-9f62-ba60fa27c895", False,
    ), "download-digital-cards"
    yield TestCaseData(
        "digital_reprint", False, (
            FaceData("Serra Ascendant", "https://c1.scryfall.com/file/scryfall-cards/png/front/b/7/b72e71c7-a65c-481d-8ad7-77bfb5d66d73.png?1576794512", True),
        ), DatabaseSetData("ha1", "Historic Anthology 1", "https://scryfall.com/sets/ha1?utm_source=api"),
        "en", "1", "b72e71c7-a65c-481d-8ad7-77bfb5d66d73", "27ad3e00-6ffb-48f7-8469-8868d066d1e2", False,
    ), "download-digital-cards"


@pytest.mark.parametrize("filter_setting", [True, False])
@pytest.mark.parametrize("test_case, filter_name", generate_test_cases_for_test_download_filters())
def test_download_filters(card_db: CardDatabase, test_case: TestCaseData, filter_name: str, filter_setting: bool):
    fill_card_database_with_json_card(card_db, test_case.json_name, filter_name, str(filter_setting))
    if filter_setting:
        assert_successful_import(card_db, test_case)
    else:
        assert_model_is_empty(card_db, test_case)


def test_import_card_skips_import_of_card_with_missing_image(card_db: CardDatabase):
    fill_card_database_with_json_card(card_db, "missing_image_double_faced_card")
    assert_model_is_empty(
        card_db, TestCaseData(
            "", False, tuple(), DatabaseSetData("", "", ""), "", "",
            "b120e3c2-21b1-43e3-b685-9cf62bd7aa07", "9110339d-72ba-4132-801f-cd2fd738b71d", False))


def test_re_import_with_enabled_download_filter_removes_card(card_db: CardDatabase):
    test_case = TestCaseData(  # Oversized printing of "Atraxa, Praetors' Voice"
        "oversized_card", True, (
            FaceData("Atraxa, Praetors' Voice", "https://c1.scryfall.com/file/scryfall-cards/png/front/6/5/650722b4-d72b-4745-a1a5-00a34836282b.png?1561757296", True),
        ), DatabaseSetData("oc16", "Commander 2016 Oversized", "https://scryfall.com/sets/oc16?utm_source=api"),
        "en", "28", "650722b4-d72b-4745-a1a5-00a34836282b", "7e6b9b59-cd68-4e3c-827b-38833c92d6eb", True,
    )
    filter_name = "download-oversized-cards"
    # Pass 1: Populate the database and include the card. The card should be in the database afterwards
    fill_card_database_with_json_card(card_db, test_case.json_name, filter_name, "True")
    assert_successful_import(card_db, test_case)
    # Pass 2: Re-Populate the database, but exclude the card now.
    fill_card_database_with_json_card(card_db, test_case.json_name, filter_name, "False")
    # The card should not be in the database.
    assert_model_is_empty(card_db, test_case)


def test_re_import_with_disabled_download_filter_removes_removed_printings_entry(card_db: CardDatabase):
    test_case = TestCaseData(  # Oversized printing of "Atraxa, Praetors' Voice"
        "oversized_card", True, (
            FaceData("Atraxa, Praetors' Voice", "https://c1.scryfall.com/file/scryfall-cards/png/front/6/5/650722b4-d72b-4745-a1a5-00a34836282b.png?1561757296", True),
        ), DatabaseSetData("oc16", "Commander 2016 Oversized", "https://scryfall.com/sets/oc16?utm_source=api"),
        "en", "28", "650722b4-d72b-4745-a1a5-00a34836282b", "7e6b9b59-cd68-4e3c-827b-38833c92d6eb", True,
    )
    filter_name = "download-oversized-cards"
    # Pass 1: Populate the database and exclude the card. The card should not be in the database afterwards
    fill_card_database_with_json_card(card_db, test_case.json_name, filter_name, "False")
    assert_model_is_empty(card_db, test_case)
    # Pass 2: Re-Populate the database, but include the card now.
    fill_card_database_with_json_card(card_db, test_case.json_name, filter_name, "True")
    # The card should be in the database. The RemovedPrintings table should be empty
    assert_successful_import(card_db, test_case)
    assert_that(
        card_db.db.execute("SELECT scryfall_id, oracle_id FROM RemovedPrintings").fetchall(),
        is_(empty()),
        "RemovedPrintings table not properly cleaned up."
    )



def test_updates_language(card_db: CardDatabase):
    test_case = TestCaseData(  # English "Fury Sliver" from Time Spiral. Modified the language
        "regular_english_card", True, (
            FaceData("Fury Sliver",
                     "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979",
                     True),
        ), DatabaseSetData("tsp", "Time Spiral", "https://scryfall.com/sets/tsp?utm_source=api"),
        "pl", "157", "0000579f-7b35-4ed3-b44c-db2a538066fe", "44623693-51d6-49ad-8cd7-140505caf02f", False,
    )
    json_data = load_json(test_case.json_name)
    fill_card_database_with_json_card(card_db, json_data)
    with unittest.mock.patch.dict(json_data, {"lang": test_case.language}):
        fill_card_database_with_json_card(card_db, json_data)
    assert_successful_import(card_db, test_case)


@pytest.mark.parametrize("test_case", [
    TestCaseData(  # English "Fury Sliver" from Time Spiral. Modified the oracle_id ID
        "regular_english_card", True, (
            FaceData("Fury Sliver",
                     "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979",
                     True),
        ), DatabaseSetData("tsp", "Time Spiral", "https://scryfall.com/sets/tsp?utm_source=api"),
        "en", "157", "0000579f-7b35-4ed3-b44c-db2a538066fe", "44623693-51d6-49ad-8cd7-000000000000", False,
    ),
    TestCaseData(  # English special printing of Stitch in Time // Stitch in Time, which has the same card on both sides
        "double_faced_card_without_top_level_oracle_id", False, (
            FaceData("Stitch in Time", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/8/087c3a0d-c710-4451-989e-596b55352184.png?1637270835", True),
            FaceData("Stitch in Time", "https://c1.scryfall.com/file/scryfall-cards/png/back/0/8/087c3a0d-c710-4451-989e-596b55352184.png?1637270835", False),
        ), DatabaseSetData("sld", "Secret Lair Drop", "https://scryfall.com/sets/sld?utm_source=api"),
        "en", "382", "087c3a0d-c710-4451-989e-596b55352184", "59b2a90e-542f-4fb0-b290-000000000000", False,
    )
])
def test_updates_card_oracle_id(card_db: CardDatabase, test_case: TestCaseData):
    json_data = load_json(test_case.json_name)
    fill_card_database_with_json_card(card_db, json_data)
    with unittest.mock.patch.dict(json_data, {"oracle_id": test_case.oracle_id}):
        fill_card_database_with_json_card(card_db, json_data)
    assert_successful_import(card_db, test_case)


def test_updates_set_code(card_db: CardDatabase):
    test_case = TestCaseData(  # English "Fury Sliver" from Time Spiral. Modified set code
        "regular_english_card", True, (
            FaceData("Fury Sliver",
                     "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979",
                     True),
        ), DatabaseSetData("tsa", "Time Spiral", "https://scryfall.com/sets/tsp?utm_source=api"),
        "en", "157", "0000579f-7b35-4ed3-b44c-db2a538066fe", "44623693-51d6-49ad-8cd7-140505caf02f", False,
    )
    json_data = load_json(test_case.json_name)
    fill_card_database_with_json_card(card_db, json_data)
    with unittest.mock.patch.dict(json_data, {"set": test_case.set.set_code}):
        fill_card_database_with_json_card(card_db, json_data)
    assert_successful_import(card_db, test_case)


def test_updates_set_name(card_db: CardDatabase):
    test_case = TestCaseData(  # English "Fury Sliver" from Time Spiral. Modified the set name
        "regular_english_card", True, (
            FaceData("Fury Sliver",
                     "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979",
                     True),
        ), DatabaseSetData("tsp", "Time Spiral Altered", "https://scryfall.com/sets/tsp?utm_source=api"),
        "en", "157", "0000579f-7b35-4ed3-b44c-db2a538066fe", "44623693-51d6-49ad-8cd7-140505caf02f", False,
    )
    json_data = load_json(test_case.json_name)
    fill_card_database_with_json_card(card_db, json_data)
    with unittest.mock.patch.dict(json_data, {"set_name": test_case.set.set_name}):
        fill_card_database_with_json_card(card_db, json_data)
    assert_successful_import(card_db, test_case)


def test_updates_set_uri(card_db: CardDatabase):
    test_case = TestCaseData(  # English "Fury Sliver" from Time Spiral. Modified the set URI
        "regular_english_card", True, (
            FaceData("Fury Sliver",
                     "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979",
                     True),
        ), DatabaseSetData("tsp", "Time Spiral", "https://scryfall.com/sets/tsa"),
        "en", "157", "0000579f-7b35-4ed3-b44c-db2a538066fe", "44623693-51d6-49ad-8cd7-140505caf02f", False,
    )
    json_data = load_json(test_case.json_name)
    fill_card_database_with_json_card(card_db, json_data)
    with unittest.mock.patch.dict(json_data, {"scryfall_set_uri": test_case.set.set_uri}):
        fill_card_database_with_json_card(card_db, json_data)
    assert_successful_import(card_db, test_case)


def test_updates_printing_collector_number(card_db: CardDatabase):
    test_case = TestCaseData(  # English "Fury Sliver" from Time Spiral. Modified the collector_number
        "regular_english_card", True, (
            FaceData("Fury Sliver",
                     "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979",
                     True),
        ), DatabaseSetData("tsp", "Time Spiral", "https://scryfall.com/sets/tsp?utm_source=api"),
        "en", "1234", "0000579f-7b35-4ed3-b44c-db2a538066fe", "44623693-51d6-49ad-8cd7-140505caf02f", False,
    )
    json_data = load_json(test_case.json_name)
    fill_card_database_with_json_card(card_db, json_data)
    with unittest.mock.patch.dict(json_data, {"collector_number": test_case.collector_number}):
        fill_card_database_with_json_card(card_db, json_data)
    assert_successful_import(card_db, test_case)


def test_updates_printing_is_oversized(card_db: CardDatabase):
    test_case = TestCaseData(  # English "Fury Sliver" from Time Spiral. Modified the oversized boolean
        "regular_english_card", True, (
            FaceData("Fury Sliver",
                     "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979",
                     True),
        ), DatabaseSetData("tsp", "Time Spiral", "https://scryfall.com/sets/tsp?utm_source=api"),
        "en", "157", "0000579f-7b35-4ed3-b44c-db2a538066fe", "44623693-51d6-49ad-8cd7-140505caf02f", True,
    )
    json_data = load_json(test_case.json_name)
    fill_card_database_with_json_card(card_db, json_data)
    with unittest.mock.patch.dict(json_data, {"oversized": test_case.is_oversized}):
        fill_card_database_with_json_card(card_db, json_data)
    assert_successful_import(card_db, test_case)


def test_updates_printing_highres_image(card_db: CardDatabase):
    test_case = TestCaseData(  # English "Fury Sliver" from Time Spiral. Modified the highres_image boolean
        "regular_english_card", False, (
            FaceData("Fury Sliver",
                     "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979",
                     True),
        ), DatabaseSetData("tsp", "Time Spiral", "https://scryfall.com/sets/tsp?utm_source=api"),
        "en", "157", "0000579f-7b35-4ed3-b44c-db2a538066fe", "44623693-51d6-49ad-8cd7-140505caf02f", False,
    )
    json_data = load_json(test_case.json_name)
    fill_card_database_with_json_card(card_db, json_data)
    with unittest.mock.patch.dict(json_data, {"highres_image": test_case.highres_image}):
        fill_card_database_with_json_card(card_db, json_data)
    assert_successful_import(card_db, test_case)
