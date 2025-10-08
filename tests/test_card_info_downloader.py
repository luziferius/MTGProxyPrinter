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


import dataclasses
import sqlite3
from typing import NamedTuple
import unittest.mock
from unittest.mock import MagicMock

from hamcrest import *
import pytest

import mtg_proxy_printer.async_tasks.card_info_downloader
from mtg_proxy_printer.async_tasks.card_info_downloader import SetWackinessScore
from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.model.card import MTGSet, Card
from mtg_proxy_printer.units_and_sizes import UUID, CardSizes

from .helpers import assert_model_is_empty, fill_card_database_with_json_card, load_json, assert_relation_is_empty, \
    fill_card_database_with_json_cards, CardDataType


class DatabasePrintingData(NamedTuple):
    """Rows stored in the Printing relation"""
    collector_number: str
    scryfall_id: UUID
    is_oversized: bool
    highres_image: bool


class DatabaseCardFaceData(NamedTuple):
    """Rows stored in the CardFace relation"""
    image_uri: str
    is_front: bool
    face_number: int


class DatabaseSetData(NamedTuple):
    """Row data stored in the Set relation"""
    set_code: str
    set_name: str
    set_uri: str
    release_date: str


class DatabaseVisiblePrintingsData(NamedTuple):
    """Row retrieved via VisiblePrintings view"""
    name: str
    set_code: str
    language: str
    collector_number: str
    scryfall_id: UUID
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

    __test__ = False  # Instruct PyTest to not collect this as a Test class, even if the name starts with "Test"

    @property
    def json_dict(self) -> CardDataType:
        # Note: load_json already caches the result, so no need to worry about performance
        return load_json(self.json_name)

    @property
    def highres_image(self) -> bool:
        return self.json_dict["highres_image"]

    @property
    def language(self) -> str:
        return self.json_dict["lang"]

    @property
    def collector_number(self) -> str:
        return self.json_dict["collector_number"]

    @property
    def scryfall_id(self) -> UUID:
        return self.json_dict["id"]

    @property
    def oracle_id(self) -> UUID:
        card = self.json_dict
        return card.get("oracle_id") or card["card_faces"][0]["oracle_id"]

    @property
    def is_oversized(self) -> bool:
        return self.json_dict["oversized"]

    @property
    def face_data(self) -> list[FaceData]:
        card = self.json_dict
        if faces := card.get("card_faces"):
            result = []
            for face in faces:
                name = face.get("printed_name", face["name"])
                images = card.get("image_uris") or face["image_uris"]
                result.append(FaceData(name, (png_uri := images["png"]), "/front/" in png_uri))
            return result
        return [FaceData(card.get("printed_name", card["name"]), card["image_uris"]["png"], True)]

    @property
    def set(self) -> DatabaseSetData:
        card = self.json_dict
        return DatabaseSetData(card["set"], card["set_name"], card["scryfall_set_uri"], card["released_at"])

    def db_card(self) -> list[tuple[str]]:
        return [(self.oracle_id,)]

    def db_set(self):
        return [self.set]

    def db_print_language(self):
        return [(self.language,)]

    def db_face_name(self) -> list[tuple[str]]:
        # De-duplicate face names, in case both sides of a double-faced card have the same name. This is true for
        # art series cards, certain double-faced tokens (for example the C16 Saproling token) and similar.
        return list(set((face.name,) for face in self.face_data))

    def db_card_face(self) -> list[DatabaseCardFaceData]:
        return [
            DatabaseCardFaceData(
                face.image_uri, face.is_front, face_number)
            for face_number, face in enumerate(self.face_data)
        ]

    def db_all_printings(self) -> list[DatabaseVisiblePrintingsData]:
        return [
            DatabaseVisiblePrintingsData(
                face.name, self.set.set_code, self.language, self.collector_number, self.scryfall_id,
                self.highres_image, face.image_uri, face.is_front, self.is_oversized)
            for face in self.face_data
        ]

    def db_printing(self) -> list[DatabasePrintingData]:
        return [
            DatabasePrintingData(self.collector_number, self.scryfall_id, self.is_oversized, self.highres_image)
        ]

    def as_card(self, face_id: int = 1) -> Card:
        cd = self.json_dict
        card_set = MTGSet(cd["set"], cd["set_name"])
        oracle_id = cd.get("oracle_id") or cd["card_faces"][0]["oracle_id"]
        face_id -= 1
        size = CardSizes.from_bool(cd["oversized"])
        if (faces := cd.get("card_faces")) is not None:
            face = faces[face_id]
            image_uris = cd.get("image_uris") or face["image_uris"]
            last_image_uris = cd.get("image_uris") or cd["card_faces"][-1]["image_uris"]
            return Card(
                face.get("printed_name") or face["name"], card_set,
                cd["collector_number"],  cd["lang"], cd["id"], "/front/" in image_uris["png"], oracle_id,
                image_uris["png"], cd["highres_image"],
                size, face_id, "/back/" in last_image_uris["png"], None
            )
        return Card(
            cd.get("printed_name") or cd["name"], card_set,
            cd["collector_number"],  cd["lang"], cd["id"], True, oracle_id,
            cd["image_uris"]["png"], cd["highres_image"],
            size, 0, False, None
        )


def _assert_card_contains(card_db: CardDatabase, test_case: TestCaseData):
    """Checks Oracle_id"""
    assert_that(
        data := card_db.db.execute('SELECT oracle_id FROM Card').fetchall(),
        contains_inanyorder(*test_case.db_card()),
        f"Card relation contains unexpected data: {data}")


def _assert_print_language_contains(card_db: CardDatabase, test_case: TestCaseData):
    """Assert that the card's language is stored in the database"""
    assert_that(
        data := card_db.db.execute(f'SELECT "language" FROM PrintLanguage').fetchall(),
        contains_inanyorder(*test_case.db_print_language()),
        f"PrintLanguage relation contains unexpected data: {data}")


def _assert_set_contains(card_db: CardDatabase, test_case: TestCaseData):
    """
    Asserts that the card's set is stored in the database.
    Checks columns set_code, set_name, set_uri, release_date
    """
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


def test_test_case_data():
    case = TestCaseData("oversized_card")
    assert_that(
        case, has_properties({
            "highres_image": True,
            "language": "en",
            "collector_number": "28",
            "scryfall_id": "650722b4-d72b-4745-a1a5-00a34836282b",
            "oracle_id": "7e6b9b59-cd68-4e3c-827b-38833c92d6eb",
            "is_oversized": True,
            "face_data": contains_exactly(
                FaceData("Atraxa, Praetors' Voice", "https://cards.scryfall.io/png/front/6/5/650722b4-d72b-4745-a1a5-00a34836282b.png?1561757296", True)
            ),
            "set": DatabaseSetData("oc16", "Commander 2016 Oversized", "https://scryfall.com/sets/oc16?utm_source=api", "2016-11-11")
        })
    )


def generate_test_cases_for_test_card_import():
    yield TestCaseData("non_english_double_faced_card")  # Chinese "Growing Rites of Itlimoc // Itlimoc, Cradle of the Sun"
    yield TestCaseData("split_card")  # Korean "Cut // Ribbons"
    yield TestCaseData("english_double_faced_art_series_card")  # English art series card "Clearwater Pathway // Clearwater Pathway"
    yield TestCaseData("regular_english_card")  # English "Fury Sliver" from Time Spiral
    yield TestCaseData("reversible_card")  # English special printing of Stitch in Time // Stitch in Time, which has the same card on both sides
    yield TestCaseData("The_Ring")
    yield TestCaseData("Undercity")
    yield TestCaseData("Dungeon_of_the_Mad_Mage")


@pytest.mark.parametrize("test_case", generate_test_cases_for_test_card_import())
def test_card_import(qtbot, card_db: CardDatabase, test_case: TestCaseData):
    fill_card_database_with_json_card(qtbot, card_db, test_case.json_dict)
    assert_visible_import(card_db, test_case)


def generate_test_cases_for_test_print_hiding_filters():
    yield TestCaseData("depicting_racism"), "hide-cards-depicting-racism"  # German printing of "Crusade"
    yield TestCaseData("placeholder_image"), "hide-cards-without-images"  # Spanish printing of "Air Elemental"
    yield TestCaseData("oversized_card"), "hide-oversized-cards"  # Oversized printing of "Atraxa, Praetors' Voice"
    yield TestCaseData("funny_card_with_silver_border"), "hide-funny-cards"  # Silver-bordered "Aesthetic Consultation" from Unhinged
    yield TestCaseData("funny_card_with_acorn_security_stamp"), "hide-funny-cards"  # Black-bordered "Form of the Approach of the Second Sun" from Unfinity
    yield TestCaseData("Food_Token"), "hide-token"
    yield TestCaseData("Undercity"), "hide-token"   # Double-faced Dungeon / The Initiative marker card
    yield TestCaseData("The_Ring"), "hide-token"   # Double-faced Emblem
    yield TestCaseData("gold_bordered_card"), "hide-gold-bordered"
    yield TestCaseData("white_bordered_card"), "hide-white-bordered"
    yield TestCaseData("banned_in_brawl"), "hide-banned-in-brawl"
    yield TestCaseData("banned_in_commander"), "hide-banned-in-commander"
    yield TestCaseData("banned_in_historic"), "hide-banned-in-historic"
    yield TestCaseData("banned_in_legacy"), "hide-banned-in-legacy"
    yield TestCaseData("banned_in_modern"), "hide-banned-in-modern"
    yield TestCaseData("banned_in_oathbreaker"), "hide-banned-in-oathbreaker"
    yield TestCaseData("banned_in_pauper"), "hide-banned-in-pauper"
    yield TestCaseData("banned_in_penny"), "hide-banned-in-penny"  # The format has zero banned cards. The JSON document was altered to fake a banned card for testing purposes.
    yield TestCaseData("banned_in_pioneer"), "hide-banned-in-pioneer"
    yield TestCaseData("banned_in_standard"), "hide-banned-in-standard"
    yield TestCaseData("banned_in_vintage"), "hide-banned-in-vintage"
    yield TestCaseData("digital_only_card"), "hide-digital-cards"
    yield TestCaseData("digital_reprint"), "hide-digital-cards"
    yield TestCaseData("borderless_card"), "hide-borderless"
    yield TestCaseData("extended_art"), "hide-extended-art"
    yield TestCaseData("reversible_card"), "hide-reversible-cards"  # English special printing of Stitch in Time // Stitch in Time, which has the same card on both sides
    yield TestCaseData("english_double_faced_art_series_card"), "hide-art-series-cards"


@pytest.mark.parametrize("filter_enabled", [True, False])
@pytest.mark.parametrize("test_case, filter_name", generate_test_cases_for_test_print_hiding_filters())
def test_boolean_print_hiding_filters(
        qtbot, card_db: CardDatabase, test_case: TestCaseData, filter_name: str, filter_enabled: bool):
    fill_card_database_with_json_card(qtbot, card_db, test_case.json_dict, {filter_name: str(filter_enabled)})
    if filter_enabled:
        assert_hidden_import(card_db, test_case)
    else:
        assert_visible_import(card_db, test_case)


def generate_test_cases_for_test_set_code_filters():
    sliver = TestCaseData("regular_english_card")  # English "Fury Sliver" from Time Spiral
    yield sliver, "TSP", True
    yield sliver, "tsp", True
    yield sliver, "ABC", False
    yield sliver, "", False


@pytest.mark.parametrize("test_case, filter_value, is_hidden", generate_test_cases_for_test_set_code_filters())
def test_set_code_filters(qtbot, card_db: CardDatabase, test_case: TestCaseData, filter_value: str, is_hidden: bool):
    fill_card_database_with_json_card(qtbot, card_db, test_case.json_dict, {"hidden-sets": filter_value})
    if is_hidden:
        assert_hidden_import(card_db, test_case)
    else:
        assert_visible_import(card_db, test_case)


@pytest.mark.parametrize("filter_setting", [True, False])
@pytest.mark.parametrize("test_case, filter_name", [
    (TestCaseData("funny_legal_card"), "hide-funny-cards"),  # Black-bordered, eternal-legal "Aerialephant" from Unfinity
])
def test_download_filters_does_not_affect_unexpected_cards(
        qtbot, card_db: CardDatabase, test_case: TestCaseData, filter_name: str, filter_setting: bool):
    fill_card_database_with_json_card(qtbot, card_db, test_case.json_dict, {filter_name: str(filter_setting)})
    assert_visible_import(card_db, test_case)


@pytest.mark.parametrize("test_case", [
    TestCaseData("missing_image_double_faced_card"),
    TestCaseData("double_faced_card_with_missing_back_images"),  # Crash discovered Oct 27th, 2022. The back face of this double faced card has no image_uris key
])
def test_import_card_skips_import_of_card_with_missing_image(qtbot, card_db: CardDatabase, test_case: TestCaseData):
    fill_card_database_with_json_card(qtbot, card_db, test_case.json_dict)
    assert_model_is_empty(card_db, test_case)


def test_two_imports_having_the_same_filtered_out_card_work(qtbot, card_db: CardDatabase):
    case = TestCaseData("missing_image_double_faced_card")
    fill_card_database_with_json_card(qtbot, card_db, case.json_dict)
    assert_model_is_empty(card_db, case)
    fill_card_database_with_json_card(qtbot, card_db, case.json_dict)
    assert_model_is_empty(card_db, case)


@pytest.mark.parametrize("filter_name, visible_value, hidden_value", [
    ("hide-oversized-cards", "False", "True"),
    ("hidden-sets", "", "OC16"),
])
def test_re_import_with_enabled_download_filter_removes_card(
        qtbot, card_db: CardDatabase, filter_name: str, visible_value: str, hidden_value: str):
    test_case = TestCaseData("oversized_card")  # Oversized printing of "Atraxa, Praetors' Voice"
    # Pass 1: Populate the database and include the card. The card should be in the database afterward
    fill_card_database_with_json_card(qtbot, card_db, test_case.json_dict, {filter_name: visible_value})
    assert_visible_import(card_db, test_case)
    # Pass 2: Re-Populate the database, but exclude the card now.
    fill_card_database_with_json_card(qtbot, card_db, test_case.json_dict, {filter_name: hidden_value})
    # The card should not be visible
    assert_hidden_import(card_db, test_case)


@pytest.mark.parametrize("filter_name, visible_value, hidden_value", [
    ("hide-oversized-cards", "False", "True"),
    ("hidden-sets", "", "OC16"),
])
def test_re_import_with_disabled_download_filter_removes_removed_printings_entry(
        qtbot, card_db: CardDatabase, filter_name: str, visible_value: str, hidden_value: str):
    test_case = TestCaseData("oversized_card")  # Oversized printing of "Atraxa, Praetors' Voice"
    # Pass 1: Populate the database and exclude the card. The card should not be visible
    fill_card_database_with_json_card(qtbot, card_db, test_case.json_dict, {filter_name: hidden_value})
    assert_hidden_import(card_db, test_case)
    # Pass 2: Re-Populate the database, but include the card now.
    fill_card_database_with_json_card(qtbot, card_db, test_case.json_dict, {filter_name: visible_value})
    # The card should be in the database. The RemovedPrintings table should be empty
    assert_visible_import(card_db, test_case)
    assert_that(
        card_db.db.execute("SELECT scryfall_id, oracle_id FROM RemovedPrintings").fetchall(),
        is_(empty()),
        "RemovedPrintings table not properly cleaned up."
    )


@pytest.mark.parametrize("test_case_data", [
    TestCaseData("regular_english_card"),  # English "Fury Sliver" from Time Spiral
])
def test_re_import_after_card_ban_hides_it(qtbot, card_db: CardDatabase, test_case_data: TestCaseData):
    card_json = test_case_data.json_dict
    with unittest.mock.patch.dict(card_json["legalities"], {"commander": "banned"}):
        fill_card_database_with_json_card(qtbot, card_db, card_json, {"hide-banned-in-commander": "True"})
    assert_hidden_import(card_db, test_case_data)
    fill_card_database_with_json_card(qtbot, card_db, card_json, {"hide-banned-in-commander": "True"})
    assert_visible_import(card_db, test_case_data)


@pytest.mark.parametrize("test_case_data", [
    TestCaseData("regular_english_card"),  # English "Fury Sliver" from Time Spiral
])
def test_re_import_after_unban_makes_card_visible(qtbot, card_db: CardDatabase, test_case_data: TestCaseData):
    card_json = test_case_data.json_dict
    fill_card_database_with_json_card(qtbot, card_db, card_json, {"hide-banned-in-commander": "True"})
    assert_visible_import(card_db, test_case_data)
    with unittest.mock.patch.dict(card_json["legalities"], {"commander": "banned"}):
        fill_card_database_with_json_card(qtbot, card_db, card_json, {"hide-banned-in-commander": "True"})
    assert_hidden_import(card_db, test_case_data)


DataPath = list[str | int]


@pytest.mark.parametrize("test_case, dict_path, value", [
    (TestCaseData("regular_english_card"), ["lang"], "pl"),  # English "Fury Sliver" from Time Spiral
    (TestCaseData("regular_english_card"), ["oracle_id"], "59b2a90e-542f-4fb0-b290-000000000000"),
    (TestCaseData("reversible_card"), ["card_faces", 0, "oracle_id"], "59b2a90e-542f-4fb0-b290-000000000000"),
    (TestCaseData("regular_english_card"), ["set"], "tsa"),
    (TestCaseData("regular_english_card"), ["set_name"], "Time Spiral Altered"),
    (TestCaseData("regular_english_card"), ["scryfall_set_uri"], "https://scryfall.com/sets/tsa"),
    (TestCaseData("regular_english_card"), ["released_at"], "2000-01-01"),  # Dating back is allowed.
    (TestCaseData("regular_english_card"), ["collector_number"], "1234"),
    (TestCaseData("regular_english_card"), ["oversized"], True),
    (TestCaseData("regular_english_card"), ["highres_image"], False),
    (TestCaseData("regular_english_card"), ["image_uris", "png"], "https://c1.scryfall.com/file/front/invalid.png"),
])
def test_updates_changed_value_on_re_import(
        qtbot, card_db: CardDatabase, test_case: TestCaseData, dict_path: DataPath, value):
    json_data = test_case.json_dict
    to_patch = json_data
    for item in dict_path[:-1]:
        to_patch = to_patch[item]
    assert_that(to_patch, is_(instance_of(dict)), "Setup failed: Walking path did not end in a dict to patch")
    fill_card_database_with_json_card(qtbot, card_db, json_data)
    with unittest.mock.patch.dict(to_patch, {dict_path[-1]: value}):
        fill_card_database_with_json_card(qtbot, card_db, json_data)
        # Assert within patched context, so that it can see the changed data in the test case data.
        assert_visible_import(card_db, test_case)


@pytest.mark.parametrize("test_case, dict_path, value", [
    # Some sets got additional cards appended to them after initial release. Those have a later release date,
    # which would shift the whole set release date. Do not allow updating the release date to a later date
    (TestCaseData("regular_english_card"), ["released_at"], "2020-01-01"),  # English "Fury Sliver" from Time Spiral
])
def test_updates_ignores_changed_value_on_re_import(
        qtbot, card_db: CardDatabase, test_case: TestCaseData, dict_path: DataPath, value):
    json_data = test_case.json_dict
    to_patch = json_data
    for item in dict_path[:-1]:
        to_patch = to_patch[item]
    assert_that(to_patch, is_(instance_of(dict)), "Setup failed: Walking path did not end in a dict to patch")
    fill_card_database_with_json_card(qtbot, card_db, json_data)
    with unittest.mock.patch.dict(to_patch, {dict_path[-1]: value}):
        fill_card_database_with_json_card(qtbot, card_db, json_data)
    # Outside the patched context to validate against the original data.
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


@pytest.mark.parametrize("cards, expected_pairs", [
    ([
        "The_Underworld_Cookbook",
        "Food_Token",
        "Asmoranomardicadaistinaculdacar",
        "Bake_into_a_Pie",
        "Asmoranomardicadaistinaculdacar_2",
        "Food_Token_2",
     ], [
        # The Food token (card id 2) is never a source, as that would pull all cards creating that token
        (3, 1),  # Asmoranomardicadaistinaculdacar references The Underworld Cookbook by name
        (1, 3),  # Back relation
        (1, 2),  # Card mentions Food token
        (4, 2),  # Card mentions Food token
    ]),
    ([
         "Dungeon_of_the_Mad_Mage", "Zombie_Ogre", "Dungeon_Skeleton_Token",
     ],[
        (1, 3),  # The Dungeon itself can create a Skeleton Token
        (2, 1),  # Zombie Ogre has Venture into the Dungeon
        # Nothing else here:
        # The Skeleton must not link to the Dungeon, and the Dungeon must not link to the Zombie Ogre
    ]),
])
def test_related_printings(
        qtbot, card_db: CardDatabase,
        cards: list[str], expected_pairs: list[tuple[int, int]]):
    db = card_db.db

    # Cards always relate to exact printings, but which one is chosen is rather arbitrary. E.g. The Underworld Cookbook
    # and Back into a Pie both create a Food token, but are set to different printings of that token card.
    fill_card_database_with_json_cards(qtbot, card_db, cards)
    assert_that(
        db.execute("SELECT card_id, related_id FROM RelatedPrintings").fetchall(),
        contains_inanyorder(
            *expected_pairs
        )
    )


@pytest.mark.parametrize("cards", [
    ["Undercity", "Explore_the_Underdark", "Trailblazers_Torch"],
    ["Dungeon_of_the_Mad_Mage", "Zombie_Ogre", "Bar_the_Gate"],
    ["The_Ring", "Samwise_the_Stouthearted", "Elrond_Lord_of_Rivendell"],
])
def test_update_deletes_outdated_related_printing(qtbot, card_db: CardDatabase, cards: list[str]):
    db = card_db.db
    fill_card_database_with_json_cards(qtbot, card_db, cards)
    assert_that(
        db.execute("SELECT card_id, related_id FROM RelatedPrintings").fetchall(),
        contains_inanyorder((2, 1), (3, 1)),
        "Test setup failed"
    )
    db.executemany(
        # This inserts the back relation (token → card). These should not exist, and get purged during the next update
        "INSERT INTO RelatedPrintings (card_id, related_id) VALUES (?, ?)",
        [(1, 2), (1, 3)]
    )
    fill_card_database_with_json_cards(qtbot, card_db, cards)
    assert_that(
        db.execute("SELECT card_id, related_id FROM RelatedPrintings").fetchall(),
        contains_inanyorder((2, 1), (3, 1)),
        "Old related printings not cleaned up"
    )


@pytest.mark.parametrize("exception", [sqlite3.Error, Exception])
def test_import_works_after_network_error_during_first_try(qtbot, card_db, exception):
    dw = mtg_proxy_printer.async_tasks.card_info_downloader.DatabaseImportTask(MagicMock(), card_db.db)
    data_raising_exception = unittest.mock.MagicMock().__iter__.side_effect = exception()
    with unittest.mock.patch("mtg_proxy_printer.async_tasks.card_info_downloader.logger.exception") as logger_mock:
        dw.populate_database(data_raising_exception)
    logger_mock.assert_called()
    fill_card_database_with_json_card(qtbot, card_db, "regular_english_card")
