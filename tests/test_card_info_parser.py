# Copyright (C) 2020 Thomas Hess <thomas.hess@udo.edu>

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

import json
import pkg_resources
import typing
from unittest.mock import patch

from hamcrest import *

import mtg_proxy_printer.model.carddb
import mtg_proxy_printer.settings
import mtg_proxy_printer.card_info_importer
from mtg_proxy_printer.card_info_importer import JSONType


def load_json(name: str) -> typing.Generator[JSONType, None, None]:
    yield json.loads(
        pkg_resources.resource_string(f"tests.json_samples", f"{name}.json").decode("utf-8")
    )


def _assert_set_contains(
        model: mtg_proxy_printer.model.carddb.CardDatabase,
        values: typing.Iterable[typing.Tuple[str, str, str]]):
    db_content = model.db.execute('SELECT "set", set_name, set_uri FROM "Set"').fetchall()
    assert_that(
        db_content,
        contains_inanyorder(
            *values
        ),
        f"Set relation contains unexpected data"
    )


def _assert_card_contains(
        model: mtg_proxy_printer.model.carddb.CardDatabase,
        values: typing.Iterable[typing.Tuple[str, str, str, str, str, bool]]):
    db_content = model.db.execute(
        'SELECT scryfall_id, oracle_id, "set", collector_number, language, highres_image FROM Card').fetchall()
    assert_that(
        db_content,
        contains_inanyorder(
            *values
        ),
        "Card relation contains unexpected data"
    )


def _assert_card_faces_contains(
        model: mtg_proxy_printer.model.carddb.CardDatabase,
        values: typing.Sequence[typing.Tuple[str, str, str]]):
    db_content = model.db.execute("SELECT scryfall_id, card_name, png_image_uri FROM CardFace").fetchall()
    assert_that(
        db_content,
        contains_inanyorder(
            *values
        ),
        "CardFaces relation contains unexpected data"
    )


def populate_database(model, data):
    # Don’t bother the Scryfall API when running tests, so mock the web-accessing parts of the constructor.
    with patch("mtg_proxy_printer.card_info_importer.CardInfoDownloader.get_scryfall_bulk_card_data_url") as mock:
        # The URL is not used to fetch data, as the test data directly supplies the JSON document.
        mock.return_value = ("http://example.com", 1)
        cid = mtg_proxy_printer.card_info_importer.CardInfoDownloader(model)
        cid.populate_database(model, data)


def _populate_database_with_specific_download_setting(model, data, option, value):
    """Sets a specific setting in the downloads section during the card import."""
    with patch.dict(mtg_proxy_printer.settings.settings["downloads"], {option: value}):
        populate_database(model, data)


def test_import_double_faced():
    """
    Double faced card. Any transform/meld/modal double faced card.
    """
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    # Loads Chinese printing of "Growing Rites of Itlimoc // Itlimoc, Cradle of the Sun"
    data = load_json("non_english_double_faced_card")
    populate_database(model, data)
    _assert_set_contains(model, [
        ("xln", "Ixalan", "https://scryfall.com/sets/xln?utm_source=api"),
    ])
    _assert_card_contains(model, [
        ("000847d3-ebde-4580-a00e-61d501e99485", "ea9c459a-6047-43aa-968f-a582be4000e8", "xln", "191", "zhs", False),
    ])
    _assert_card_faces_contains(model, [
        ("000847d3-ebde-4580-a00e-61d501e99485", "伊替莫成长仪式", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/000847d3-ebde-4580-a00e-61d501e99485.png?1562549619"),
        ("000847d3-ebde-4580-a00e-61d501e99485", "烈阳育所伊替莫", "https://c1.scryfall.com/file/scryfall-cards/png/back/0/0/000847d3-ebde-4580-a00e-61d501e99485.png?1562549619"),
    ])


def test_import_split_card():
    """Has two or more smaller cards on one side."""
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    # Loads Korean printing of "Cut // Ribbons"
    data = load_json("split_card")
    populate_database(model, data)
    _assert_set_contains(model, [
        ("akh", "Amonkhet", "https://scryfall.com/sets/akh?utm_source=api"),
    ])
    _assert_card_contains(model, [
        ("00031562-3818-49f9-b45c-ab28a521284c", "98a5bf1a-1088-4339-9a9b-6ee5e4956cf1", "akh", "223", "ko", False),
    ])
    _assert_card_faces_contains(model, [
        ("00031562-3818-49f9-b45c-ab28a521284c", "절단", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/00031562-3818-49f9-b45c-ab28a521284c.png?1540283200"),
        ("00031562-3818-49f9-b45c-ab28a521284c", "띠", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/00031562-3818-49f9-b45c-ab28a521284c.png?1540283200"),
    ])


def test_import_english_double_faced_art_card():
    """Has two or more smaller cards on one side."""
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    # Loads English art series card "Clearwater Pathway // Clearwater Pathway"
    data = load_json("english_double_faced_card")
    populate_database(model, data)
    _assert_set_contains(model, [
        ("aznr", "Zendikar Rising Art Series", "https://scryfall.com/sets/aznr?utm_source=api"),
    ])
    _assert_card_contains(model, [
        ("002ad179-ddf4-4f48-9504-cfa02e11a52e", "a755add5-04ec-4e37-9eb6-152d52cfa46d", "aznr", "25", "en", False),
    ])
    _assert_card_faces_contains(model, [
        ("002ad179-ddf4-4f48-9504-cfa02e11a52e", "Clearwater Pathway", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/002ad179-ddf4-4f48-9504-cfa02e11a52e.png?1600982859"),
        ("002ad179-ddf4-4f48-9504-cfa02e11a52e", "Clearwater Pathway", "https://c1.scryfall.com/file/scryfall-cards/png/back/0/0/002ad179-ddf4-4f48-9504-cfa02e11a52e.png?1600982859"),
    ])


def test_import_regular_english_card():
    """Has two or more smaller cards on one side."""
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    # Loads English art series card "Clearwater Pathway // Clearwater Pathway"
    data = load_json("regular_english_card")
    populate_database(model, data)
    _assert_set_contains(model, [
        ("tsp", "Time Spiral", "https://scryfall.com/sets/tsp?utm_source=api"),
    ])
    _assert_card_contains(model, [
        ("0000579f-7b35-4ed3-b44c-db2a538066fe", "44623693-51d6-49ad-8cd7-140505caf02f", "tsp", "157", "en", True),
    ])
    _assert_card_faces_contains(model, [
        ("0000579f-7b35-4ed3-b44c-db2a538066fe", "Fury Sliver", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979"),
    ])


def test_import_skips_card_depicting_racism_if_disabled():
    """
    Test if the importer skips cards banned for depicting racism,
    if the option to download these in the setting is disabled.
    """
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    # Loads German printing of "Crusade"
    data = load_json("depicting_racism")
    _populate_database_with_specific_download_setting(model, data, "download-cards-depicting-racism", "False")
    assert_that(
        model.db.execute('SELECT "set", set_name, set_uri FROM "Set"').fetchall(),
        is_(empty()), f"Set relation contains unexpected data"
    )
    assert_that(
        model.db.execute(
            'SELECT scryfall_id, oracle_id, "set", collector_number, language, highres_image FROM Card').fetchall(),
        is_(empty()), "Card relation contains unexpected data"
    )
    assert_that(
        model.db.execute("SELECT scryfall_id, card_name, png_image_uri FROM CardFace").fetchall(),
        is_(empty()), "CardFaces relation contains unexpected data"
    )


def test_import_card_depicting_racism_if_enabled():
    """
    Test if the importer imports cards banned for depicting racism,
    if the option to download these in the setting is enabled.
    """
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    # Loads German printing of "Crusade"
    data = load_json("depicting_racism")
    _populate_database_with_specific_download_setting(model, data, "download-cards-depicting-racism", "True")
    _assert_set_contains(model, [
        ("4ed", "Fourth Edition", "https://scryfall.com/sets/4ed?utm_source=api"),
    ])
    _assert_card_contains(model, [
        ("00809cb0-b152-441f-a0be-1bc1048dad92", "4692740f-be90-459f-8d90-c4ae71771595", "4ed", "20", "de", False),
    ])
    _assert_card_faces_contains(model, [
        ("00809cb0-b152-441f-a0be-1bc1048dad92", "Kreuzzug", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/00809cb0-b152-441f-a0be-1bc1048dad92.png?1559603956"),
    ])





"""
Assert-template: (Use for quick copy&paste when adding new test cases.)

_assert_set_contains(model, [
    ("", "", ""),
])
_assert_card_contains(model, [
    ("", "", "", "", "", True),
])
_assert_card_faces_contains(model, [
    ("", "", ""),
    ("", "", ""),
])

"""
