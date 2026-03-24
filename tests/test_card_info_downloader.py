#  Copyright © 2020-2026  Thomas Hess <thomas.hess@udo.edu>
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
import datetime
import sqlite3
from collections.abc import Sequence
from typing import NamedTuple, Callable
import unittest.mock
from unittest.mock import MagicMock

from hamcrest import *
import pytest

import mtg_proxy_printer.async_tasks.card_info_downloader
from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.model.card import MTGSet, Card
from mtg_proxy_printer.units_and_sizes import UUID, CardSizes

from .helpers import assert_model_is_empty, fill_card_database_with_json_card, load_json, assert_relation_is_empty, \
    fill_card_database_with_json_cards, CardDataType


def row_cursor(db: sqlite3.Connection) -> sqlite3.Cursor:
    """
    Returns a cursor for the given database, with sqlite3.Row as the row factory.

    Used in Tests where using Key/value-based lookups result in
    cleaner test code over brittle 10-tuple unpacking.
    """
    cursor = db.cursor()
    cursor.row_factory = sqlite3.Row
    return cursor


class DatabasePrintingData(NamedTuple):
    """Rows stored in the Printing relation"""
    collector_number: str
    language: str
    scryfall_id: UUID
    is_oversized: bool
    is_highres_image: bool
    is_dfc: bool


class DatabaseCardFaceData(NamedTuple):
    """Rows stored in the CardFace relation"""
    face_name: str
    image_uri: str
    is_front: bool


class DatabaseSetData(NamedTuple):
    """Row data stored in the Set relation"""
    set_code: str
    set_name: str
    release_date: datetime.datetime
    set_scryfall_id: UUID


class DatabaseVisiblePrintingsData(NamedTuple):
    """Row retrieved via VisiblePrintings view"""
    face_name: str
    is_front: bool
    set_code: str
    set_name: str
    collector_number: str
    release_date: datetime.datetime
    scryfall_id: UUID
    png_image_uri: str
    oracle_id: UUID
    language: str
    is_oversized: bool
    is_highres_image: bool
    is_dfc: bool


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
    def is_dfc(self) -> bool:
        card = self.json_dict
        return "card_faces" in card and "image_uris" not in card

    @property
    def is_oversized(self) -> bool:
        return self.json_dict["oversized"]

    @property
    def face_data(self) -> list[FaceData]:
        card = self.json_dict
        card_name = card.get("printed_name") or card["name"]
        match card:
            case {"card_faces": [{"image_uris": {"png": first_image}, "printed_name": f}, {"image_uris": {"png": second_image}, "printed_name": b}]}:
                # non-English DFC
                return [
                    FaceData(f, first_image, "/front/" in first_image),
                    FaceData(b, second_image, "/front/" in second_image),
                ]
            case {"card_faces": [{"image_uris": {"png": first_image}, "name": f}, {"image_uris": {"png": second_image}, "name": b}]}:
                # English DFC
                return [
                    FaceData(f, first_image, "/front/" in first_image),
                    FaceData(b, second_image, "/front/" in second_image),
                ]
            # Single-sided cards have a top-level "image_uris" key.
            case {"card_faces": [{"printed_name": f}, {"printed_name": b}], "image_uris": {"png": first_image}}:
                # Non-English names
                # card_faces array without image_uris: Split card, Adventure, Omen, etc…
                return [FaceData(f"{f} // {b}", first_image, True)]
            case {"card_faces": [{"name": f}, {"name": b}], "image_uris": {"png": first_image}}:
                # English names
                # card_faces array without image_uris: Split card, Adventure, Omen, etc…
                return [FaceData(f"{f} // {b}", first_image, True)]
            case {"image_uris": {"png": first_image}}:
                # Regular card
                return [FaceData(card_name, first_image, True)]
            case _:
                raise RuntimeError(f"Unexpected structure in case {self.json_name}")

    @property
    def set(self) -> DatabaseSetData:
        card = self.json_dict
        release_date = datetime.datetime.fromisoformat(card["released_at"])
        return DatabaseSetData(card["set"], card["set_name"], release_date, card["set_id"])

    def db_card(self) -> tuple[str]:
        return self.oracle_id,

    def db_set(self):
        return self.set

    def db_printing_face(self) -> list[DatabaseCardFaceData]:
        return [
            DatabaseCardFaceData(face.name, face.image_uri, face.is_front)
            for face in self.face_data
        ]

    def db_all_printings(self) -> list[DatabaseVisiblePrintingsData]:
        set_ = self.set
        return [
            DatabaseVisiblePrintingsData(
                face.name, face.is_front, set_.set_code, set_.set_name, self.collector_number, set_.release_date,
                self.scryfall_id,
                face.image_uri, self.oracle_id, self.language, self.is_oversized, self.highres_image, self.is_dfc
            )
            for face in self.face_data
        ]

    def db_printing(self) -> DatabasePrintingData:
        return DatabasePrintingData(
            self.collector_number, self.language, self.scryfall_id, self.is_oversized, self.highres_image, self.is_dfc)

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
                name=face.get("printed_name") or face["name"], set=card_set, collector_number=cd["collector_number"],
                language=cd["lang"], scryfall_id=cd["id"], is_front="/front/" in image_uris["png"],
                oracle_id=oracle_id, image_uri=image_uris["png"], highres_image=cd["highres_image"],
                size=size, is_dfc="/back/" in last_image_uris["png"]
            )
        return Card(
            name=cd.get("printed_name") or cd["name"], set=card_set, collector_number=cd["collector_number"],
            language=cd["lang"], scryfall_id=cd["id"], is_front=True,
            oracle_id=oracle_id, image_uri=cd["image_uris"]["png"], highres_image=cd["highres_image"],
            size=size, is_dfc=False
        )


def _assert_card_contains(card_db: CardDatabase, test_case: TestCaseData):
    """Checks oracle_id"""
    data: Sequence[tuple[str]] = card_db.db.execute('SELECT oracle_id FROM Card\n').fetchall()
    assert_that(
        data, contains_exactly(test_case.db_card()),
        f"Card relation contains unexpected data: {data}")


def _assert_set_contains(card_db: CardDatabase, test_case: TestCaseData):
    """
    Asserts that the card's set is stored in the database.
    Checks columns set_code, set_name, release_date, set_scryfall_id
    """
    data: Sequence[DatabaseSetData] = [
        DatabaseSetData(**dict(row)) for row in row_cursor(card_db.db).execute(
            "SELECT set_code, set_name, release_date, set_scryfall_id FROM MTGSet\n")]
    assert_that(
        data, contains_exactly(test_case.db_set()),
        "Set relation contains unexpected data")


def _assert_printing_contains(card_db: CardDatabase, test_case: TestCaseData, *, is_visible: bool = True):
    cursor = row_cursor(card_db.db)
    data: Sequence[DatabasePrintingData] = [
        DatabasePrintingData(**dict(row)) for row
        in cursor.execute("""\
        SELECT collector_number, language, scryfall_id, 
               is_oversized, is_highres_image, is_dfc
          FROM Printing""")
    ]
    assert_that(
        data, contains_exactly(test_case.db_printing()),
        f"Printing relation contains unexpected data: {data}")
    visible_data: Sequence[bool] = [
        row["is_visible"] for row
        in cursor.execute(
            "SELECT is_visible FROM Printing WHERE scryfall_id = ?\n",
            (test_case.scryfall_id,))
    ]
    assert_that(visible_data, contains_exactly(is_visible), "Wrong Printing visibility")


def _assert_printing_face_contains(card_db: CardDatabase, test_case: TestCaseData):
    data: Sequence[tuple[str, str, bool, int, int | None, int]] = card_db.db.execute("""\
        SELECT face_name, png_image_uri, is_front, usage_count, last_use_timestamp, currently_downloaded
          FROM PrintingFace""").fetchall()
    expected = [contains_exactly(*face, 0, none(), 0) for face in test_case.db_printing_face()]
    assert_that(
        data,
        contains_inanyorder(*expected),
        f"CardFace relation contains unexpected data: {data}"
    )


def _assert_visible_printings_contains(card_db: CardDatabase, test_case: TestCaseData):
    """
    Checks
      face_name, set_code, set_name, collector_number, release_date, scryfall_id,
      png_image_uri, oracle_id, "language", is_front, is_oversized, is_highres_image, is_dfc
    """
    data = [
        DatabaseVisiblePrintingsData(**dict(row))
        for row in row_cursor(card_db.db).execute("""\
    SELECT face_name, is_front, set_code, set_name, collector_number, release_date, scryfall_id, 
     png_image_uri, oracle_id, "language", is_oversized, is_highres_image, is_dfc
      FROM VisiblePrintings
    """)]
    assert_that(
        data, contains_inanyorder(*test_case.db_all_printings()),
        f"VisiblePrintings relation contains unexpected data: {data}"
    )


def assert_visible_import(card_db: CardDatabase, test_case: TestCaseData):
    """
    Verifies that the printing is both correctly stored, and visible in all VIEWs that filter out unwanted printings.
    """
    _assert_printing_contains(card_db, test_case, is_visible=True)
    _assert_printing_face_contains(card_db, test_case)
    _assert_set_contains(card_db, test_case)
    _assert_card_contains(card_db, test_case)
    _assert_visible_printings_contains(card_db, test_case)


def assert_hidden_import(card_db: CardDatabase, test_case: TestCaseData):
    """
    Verifies that the printing is correctly stored, but invisible in all VIEWs that filter out unwanted printings.
    """
    _assert_printing_contains(card_db, test_case, is_visible=False)
    _assert_printing_face_contains(card_db, test_case)
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
            "set": DatabaseSetData("oc16", "Commander 2016 Oversized", datetime.datetime.fromisoformat("2016-11-11"), UUID("caa8f8c4-d0bf-4848-9c66-e2fcabd1585c"))
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
    yield sliver, "TSP", assert_hidden_import
    yield sliver, "tsp", assert_hidden_import
    yield sliver, "embedded tsp in other words still works", assert_hidden_import
    yield sliver, "ABC", assert_visible_import
    yield sliver, "", assert_visible_import


@pytest.mark.parametrize("test_case, filter_value, expected_result", generate_test_cases_for_test_set_code_filters())
def test_set_code_filters(
        qtbot, card_db: CardDatabase, test_case: TestCaseData, filter_value: str,
        expected_result: Callable[[CardDatabase, TestCaseData], None]):
    fill_card_database_with_json_card(qtbot, card_db, test_case.json_dict, {"hidden-sets": filter_value})
    expected_result(card_db, test_case)


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
def test_re_import_after_unban_makes_card_visible(qtbot, card_db: CardDatabase, test_case_data: TestCaseData):
    card_json = test_case_data.json_dict
    with unittest.mock.patch.dict(card_json["legalities"], {"commander": "banned"}):
        fill_card_database_with_json_card(qtbot, card_db, card_json, {"hide-banned-in-commander": "True"})
    assert_hidden_import(card_db, test_case_data)
    fill_card_database_with_json_card(qtbot, card_db, card_json, {"hide-banned-in-commander": "True"})
    assert_visible_import(card_db, test_case_data)


@pytest.mark.parametrize("test_case_data", [
    TestCaseData("regular_english_card"),  # English "Fury Sliver" from Time Spiral
])
def test_re_import_after_card_ban_hides_it(qtbot, card_db: CardDatabase, test_case_data: TestCaseData):
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
     ], [
        (1, 3),  # The Dungeon itself can create a Skeleton Token
        (2, 1),  # Zombie Ogre has Venture into the Dungeon
        # Nothing else here:
        # The Skeleton must not link to the Dungeon, and the Dungeon must not link to the Zombie Ogre
    ]),
])
def test_related_printings(
        qtbot, card_db: CardDatabase,
        cards: list[str], expected_pairs: list[tuple[int, int]]):
    # Cards always relate to exact printings, but which one is chosen is rather arbitrary. E.g. The Underworld Cookbook
    # and Back into a Pie both create a Food token, but are set to different printings of that token card.
    fill_card_database_with_json_cards(qtbot, card_db, cards)

    assert_that(
       card_db.db.execute("SELECT card_id, related_id FROM RelatedCards").fetchall(),
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
        db.execute("SELECT card_id, related_id FROM RelatedCards").fetchall(),
        contains_inanyorder((2, 1), (3, 1)),
        "Test setup failed"
    )
    db.executemany(
        # This inserts the back relation (token → card). These should not exist, and get purged during the next update
        "INSERT INTO RelatedCards (card_id, related_id) VALUES (?, ?)",
        [(1, 2), (1, 3)]
    )
    fill_card_database_with_json_cards(qtbot, card_db, cards)
    assert_that(
        db.execute("SELECT card_id, related_id FROM RelatedCards").fetchall(),
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
