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

from hamcrest import *

import mtg_proxy_printer.model.carddb
from mtg_proxy_printer.card_info_importer import populate_database, JSONType


def load_json(name: str) -> typing.Generator[JSONType, None, None]:
    yield json.loads(
        pkg_resources.resource_string(f"tests.json_samples", f"{name}.json").decode("utf-8")
    )


def _assert_set_contains(
        model: mtg_proxy_printer.model.carddb.CardDatabase,
        values: typing.Iterable[typing.Tuple[str, str, str]]):
    assert_that(
        model.db.execute('SELECT "set", set_name, set_uri FROM "Set"').fetchall(),
        contains_inanyorder(
            *values
        ),
        "Set relation contains unexpected data"
    )


def _assert_card_contains(
        model: mtg_proxy_printer.model.carddb.CardDatabase,
        values: typing.Iterable[typing.Tuple[str, str, str, str, str, bool]]):
    assert_that(
        model.db.execute(
            'SELECT scryfall_id, oracle_id, "set", collector_number, language, highres_image FROM Card').fetchall(),
        contains_inanyorder(
            *values
        ),
        "Card relation contains unexpected data"
    )


def _assert_card_faces_contains(
        model: mtg_proxy_printer.model.carddb.CardDatabase,
        values: typing.Iterable[typing.Tuple[str, str, str]]):
    assert_that(
        model.db.execute("SELECT scryfall_id, card_name, png_image_uri FROM CardFace").fetchall(),
        contains_inanyorder(
            *values
        ),
        "CardFaces relation contains unexpected data"
    )

def test_import_double_faced():
    """
    Double faced card. Any transform/meld/modal double faced card.
    """
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("double_faced")
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
        ("ahk", "Amonkhet", "https://scryfall.com/sets/akh?utm_source=api"),
    ])
    _assert_card_contains(model, [
        ("00031562-3818-49f9-b45c-ab28a521284c", "98a5bf1a-1088-4339-9a9b-6ee5e4956cf1", "akh", "223", "ko", False),
    ])
    _assert_card_faces_contains(model, [
        ("00031562-3818-49f9-b45c-ab28a521284c", "절단", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/00031562-3818-49f9-b45c-ab28a521284c.png?1540283200"),
        ("00031562-3818-49f9-b45c-ab28a521284c", "띠", "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/00031562-3818-49f9-b45c-ab28a521284c.png?1540283200"),
    ])


"""
Assert-template:

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
