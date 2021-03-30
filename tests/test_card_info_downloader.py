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

from hamcrest import *
import pytest

import mtg_proxy_printer.model.carddb
import mtg_proxy_printer.card_info_downloader
from .helpers import create_new_card_database_with_json_card, assert_model_is_empty


class DatabaseCardFaceData(typing.NamedTuple):
    """Rows stored in the CardFace relation"""
    collector_number: str
    scryfall_id: str
    highres_image: bool
    image_uri: str
    is_front: bool


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


@dataclasses.dataclass(frozen=True)
class FaceData:
    """Contains all data that is unique per card face."""
    # Implementation note: Implemented as a frozen dataclass,
    # because this is not meant to be fed directly into an _assert_* method expecting a list of tuples.
    name: str
    highres_image: bool
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
    face_data: typing.Union[typing.Tuple[FaceData], typing.Tuple[FaceData, FaceData]]
    set: DatabaseSetData
    language: str
    collector_number: str
    scryfall_id: str
    oracle_id: str

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
                self.collector_number, self.scryfall_id, face.highres_image, face.image_uri, face.is_front)
            for face in self.face_data
        ]

    def db_all_printings(self) -> typing.List[DatabaseAllPrintingsData]:
        return [
            DatabaseAllPrintingsData(
                face.name, self.set.set_code, self.language, self.collector_number, self.scryfall_id,
                face.highres_image, face.image_uri, face.is_front)
            for face in self.face_data
        ]


def _assert_card_contains(model: mtg_proxy_printer.model.carddb.CardDatabase, test_case: TestCaseData):
    """Checks Oracle_id"""
    assert_that(
        model.db.execute('SELECT oracle_id FROM Card').fetchall(),
        contains_inanyorder(*test_case.db_card()),
        f"Card relation contains unexpected data")


def _assert_print_language_contains(model: mtg_proxy_printer.model.carddb.CardDatabase, test_case: TestCaseData):
    """Checks language"""
    assert_that(
        model.db.execute('SELECT "language" FROM PrintLanguage').fetchall(),
        contains_inanyorder(*test_case.db_print_language()),
        f"PrintLanguage relation contains unexpected data")


def _assert_set_contains(model: mtg_proxy_printer.model.carddb.CardDatabase, test_case: TestCaseData):
    """Checks "set", set_name, scryfall_set_uri"""
    assert_that(
        model.db.execute('SELECT "set", set_name, set_uri FROM "Set"').fetchall(),
        contains_inanyorder(*test_case.db_set()),
        f"Set relation contains unexpected data")


def _assert_face_name_contains(model: mtg_proxy_printer.model.carddb.CardDatabase, test_case: TestCaseData):
    """Checks card_name"""
    assert_that(
        model.db.execute('SELECT card_name FROM FaceName').fetchall(),
        contains_inanyorder(*test_case.db_face_name()),
        f"FaceName relation contains unexpected data")


def _assert_card_face_contains(model: mtg_proxy_printer.model.carddb.CardDatabase, test_case: TestCaseData):
    """Checks collector_number, scryfall_id, highres_image, png_image_uri, is_front"""
    assert_that(
        model.db.execute(
            "SELECT collector_number, scryfall_id, highres_image, png_image_uri, is_front FROM CardFace").fetchall(),
        contains_inanyorder(*test_case.db_card_face()),
        "CardFace relation contains unexpected data")


def _assert_all_printings_contains(model: mtg_proxy_printer.model.carddb.CardDatabase, test_case: TestCaseData):
    """Checks card_name, "set", "language", collector_number, scryfall_id, highres_image, png_image_uri, is_front"""
    assert_that(
        model.db.execute(
            'SELECT card_name, "set", "language", collector_number, scryfall_id, highres_image, '
            'png_image_uri, is_front FROM AllPrintings').fetchall(),
        contains_inanyorder(*test_case.db_all_printings()),
        "CardFace relation contains unexpected data")


def assert_successful_import(model: mtg_proxy_printer.model.carddb.CardDatabase, test_case: TestCaseData):
    _assert_print_language_contains(model, test_case)
    _assert_card_contains(model, test_case)
    _assert_set_contains(model, test_case)
    _assert_face_name_contains(model, test_case)
    _assert_card_face_contains(model, test_case)
    _assert_all_printings_contains(model, test_case)


def generate_test_cases_for_test_card_import():
    yield TestCaseData(  # Chinese "Growing Rites of Itlimoc // Itlimoc, Cradle of the Sun"
        "non_english_double_faced_card", (
            FaceData("伊替莫成长仪式", False, "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/000847d3-ebde-4580-a00e-61d501e99485.png?1562549619", True),
            FaceData("烈阳育所伊替莫", False, "https://c1.scryfall.com/file/scryfall-cards/png/back/0/0/000847d3-ebde-4580-a00e-61d501e99485.png?1562549619", False),
        ), DatabaseSetData("xln", "Ixalan", "https://scryfall.com/sets/xln?utm_source=api"),
        "zhs", "191", "000847d3-ebde-4580-a00e-61d501e99485", "ea9c459a-6047-43aa-968f-a582be4000e8"
    )
    yield TestCaseData(  # Korean "Cut // Ribbons"
        "split_card", (
            FaceData("절단", False, "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/00031562-3818-49f9-b45c-ab28a521284c.png?1540283200", True),
            FaceData("띠", False, "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/00031562-3818-49f9-b45c-ab28a521284c.png?1540283200", True),
        ), DatabaseSetData("akh", "Amonkhet", "https://scryfall.com/sets/akh?utm_source=api"),
        "ko", "223", "00031562-3818-49f9-b45c-ab28a521284c", "98a5bf1a-1088-4339-9a9b-6ee5e4956cf1"
    )
    yield TestCaseData(  # English art series card "Clearwater Pathway // Clearwater Pathway"
        "english_double_faced_art_series_card", (
            FaceData("Clearwater Pathway", False, "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/002ad179-ddf4-4f48-9504-cfa02e11a52e.png?1600982859", True),
            FaceData("Clearwater Pathway", False, "https://c1.scryfall.com/file/scryfall-cards/png/back/0/0/002ad179-ddf4-4f48-9504-cfa02e11a52e.png?1600982859", False),
        ), DatabaseSetData("aznr", "Zendikar Rising Art Series", "https://scryfall.com/sets/aznr?utm_source=api"),
        "en", "25", "002ad179-ddf4-4f48-9504-cfa02e11a52e", "a755add5-04ec-4e37-9eb6-152d52cfa46d"
    )
    yield TestCaseData(  # English "Fury Sliver" from Time Spiral
        "regular_english_card", (
            FaceData("Fury Sliver", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979", True),
        ), DatabaseSetData("tsp", "Time Spiral", "https://scryfall.com/sets/tsp?utm_source=api"),
        "en", "157", "0000579f-7b35-4ed3-b44c-db2a538066fe", "44623693-51d6-49ad-8cd7-140505caf02f"
    )


@pytest.mark.parametrize("test_case", generate_test_cases_for_test_card_import())
def test_card_import(test_case: TestCaseData):
    model = create_new_card_database_with_json_card(test_case.json_name)
    assert_successful_import(model, test_case)


def generate_test_cases_for_test_download_filters():
    yield TestCaseData(  # German printing of "Crusade"
        "depicting_racism", (
            FaceData("Kreuzzug", False, "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/00809cb0-b152-441f-a0be-1bc1048dad92.png?1559603956", True),
        ), DatabaseSetData("4ed", "Fourth Edition", "https://scryfall.com/sets/4ed?utm_source=api"),
        "de", "20", "00809cb0-b152-441f-a0be-1bc1048dad92", "4692740f-be90-459f-8d90-c4ae71771595"
    ), "download-cards-depicting-racism"
    yield TestCaseData(  # Spanish printing of "Air Elemental"
        "placeholder_image", (
            FaceData("Elemental del aire", False, "https://c1.scryfall.com/file/scryfall-cards/png/front/5/a/5a93fe66-620a-4f47-8a07-cff887c1e5d4.png?1557431149", True),
        ), DatabaseSetData("4bb", "Fourth Edition Foreign Black Border", "https://scryfall.com/sets/4bb?utm_source=api"),
        "es", "59", "5a93fe66-620a-4f47-8a07-cff887c1e5d4", "7744bae4-a8b7-44a5-9b4c-0048ad4cc448"
    ), "download-cards-without-images"
    yield TestCaseData(  # Silver-bordered "Aesthetic Consultation" from Unhinged
        "funny_card", (
            FaceData("Aesthetic Consultation", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/0/4/0464a507-20e5-42d5-8aca-12504a869f21.png?1562487441", True),
        ), DatabaseSetData("unh", "Unhinged", "https://scryfall.com/sets/unh?utm_source=api"),
        "en", "48", "0464a507-20e5-42d5-8aca-12504a869f21", "8789d5fa-101c-457a-90ec-5cf067f5289b"
    ), "download-funny-cards"
    yield TestCaseData(
        "gold_bordered_card", (
            FaceData("Abduction", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/2/a/2afb04a3-2940-4860-a4be-223aca0bac4b.png?1562904104", True),
        ), DatabaseSetData("wc97", "World Championship Decks 1997", "https://scryfall.com/sets/wc97?utm_source=api"),
        "en", "pm30", "2afb04a3-2940-4860-a4be-223aca0bac4b", "d0e1904e-1a37-41f6-8582-b9ea794bb886"
    ), "download-gold-bordered"
    yield TestCaseData(
        "white_bordered_card", (
            FaceData("Abomination", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/a/3/a363bc91-8278-448e-9d5c-564e4b51eb62.png?1559603880", True),
        ), DatabaseSetData("4ed", "Fourth Edition", "https://scryfall.com/sets/4ed?utm_source=api"),
        "en", "117", "a363bc91-8278-448e-9d5c-564e4b51eb62", "2c57c4e9-0a46-45d6-92db-9203fb722b60"
    ), "download-white-bordered"
    yield TestCaseData(
        "banned_in_brawl", (
            FaceData("Oko, Thief of Crowns", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
        ), DatabaseSetData("eld", "Throne of Eldraine", "https://scryfall.com/sets/eld?utm_source=api"),
        "en", "197", "3462a3d0-5552-49fa-9eb7-100960c55891", "60c60923-ff1b-43f7-8768-731499fcffc9"
    ), "download-banned-in-brawl"
    yield TestCaseData(
        "banned_in_commander", (
            FaceData("Worldfire", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/2/e/2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11.png?1562552052", True),
        ), DatabaseSetData("m13", "Magic 2013", "https://scryfall.com/sets/m13?utm_source=api"),
        "en", "158", "2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11", "ae0b8c13-0a71-4a60-bf9f-6e2da9503e9c"
    ), "download-banned-in-commander"
    yield TestCaseData(
        "banned_in_historic", (
            FaceData("Oko, Thief of Crowns", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
        ), DatabaseSetData("eld", "Throne of Eldraine", "https://scryfall.com/sets/eld?utm_source=api"),
        "en", "197", "3462a3d0-5552-49fa-9eb7-100960c55891", "60c60923-ff1b-43f7-8768-731499fcffc9"
    ), "download-banned-in-historic"
    yield TestCaseData(
        "banned_in_legacy", (
            FaceData("Falling Star", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/f/2/f2b9983e-20d4-4d12-9e2c-ec6d9a345787.png?1562861838", True),
        ), DatabaseSetData("leg", "Legends", "https://scryfall.com/sets/leg?utm_source=api"),
        "en", "145", "f2b9983e-20d4-4d12-9e2c-ec6d9a345787", "f5ca7b13-8003-4361-b827-7095c89f2750"
    ), "download-banned-in-legacy"
    yield TestCaseData(
        "banned_in_modern", (
            FaceData("Oko, Thief of Crowns", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
        ), DatabaseSetData("eld", "Throne of Eldraine", "https://scryfall.com/sets/eld?utm_source=api"),
        "en", "197", "3462a3d0-5552-49fa-9eb7-100960c55891", "60c60923-ff1b-43f7-8768-731499fcffc9"
    ), "download-banned-in-modern"
    yield TestCaseData(
        "banned_in_pauper", (
            FaceData("Expedition Map", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/5/5/551c0a45-9515-4e51-84e5-79703832a661.png?1599709184", True),
        ), DatabaseSetData("2xm", "Double Masters", "https://scryfall.com/sets/2xm?utm_source=api"),
        "en", "255", "551c0a45-9515-4e51-84e5-79703832a661", "8fcf50cd-e6d0-4516-850f-d42ee75dcc3a"
    ), "download-banned-in-pauper"
    yield TestCaseData(  # The format has zero banned cards. The JSON document was altered to fake a banned card for testing purposes.
        "banned_in_penny", (
            FaceData("Falling Star", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/f/2/f2b9983e-20d4-4d12-9e2c-ec6d9a345787.png?1562861838", True),
        ), DatabaseSetData("leg", "Legends", "https://scryfall.com/sets/leg?utm_source=api"),
        "en", "145", "f2b9983e-20d4-4d12-9e2c-ec6d9a345787", "f5ca7b13-8003-4361-b827-7095c89f2750"
    ), "download-banned-in-penny"
    yield TestCaseData(
        "banned_in_pioneer", (
            FaceData("Oko, Thief of Crowns", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
        ), DatabaseSetData("eld", "Throne of Eldraine", "https://scryfall.com/sets/eld?utm_source=api"),
        "en", "197", "3462a3d0-5552-49fa-9eb7-100960c55891", "60c60923-ff1b-43f7-8768-731499fcffc9"
    ), "download-banned-in-pioneer"
    yield TestCaseData(
        "banned_in_standard", (
            FaceData("Oko, Thief of Crowns", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
        ), DatabaseSetData("eld", "Throne of Eldraine", "https://scryfall.com/sets/eld?utm_source=api"),
        "en", "197", "3462a3d0-5552-49fa-9eb7-100960c55891", "60c60923-ff1b-43f7-8768-731499fcffc9"
    ), "download-banned-in-standard"
    yield TestCaseData(
        "banned_in_vintage", (
            FaceData("Falling Star", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/f/2/f2b9983e-20d4-4d12-9e2c-ec6d9a345787.png?1562861838", True),
        ), DatabaseSetData("leg", "Legends", "https://scryfall.com/sets/leg?utm_source=api"),
        "en", "145", "f2b9983e-20d4-4d12-9e2c-ec6d9a345787", "f5ca7b13-8003-4361-b827-7095c89f2750"
    ), "download-banned-in-vintage"


@pytest.mark.parametrize("filter_setting", [True, False])
@pytest.mark.parametrize("test_case, filter_name", generate_test_cases_for_test_download_filters())
def test_download_filters(test_case: TestCaseData, filter_name: str, filter_setting: bool):
    model = create_new_card_database_with_json_card(test_case.json_name, filter_name, str(filter_setting))
    if filter_setting:
        assert_successful_import(model, test_case)
    else:
        assert_model_is_empty(model)
