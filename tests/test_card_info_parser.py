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


def _assert_card_contains(
        model: mtg_proxy_printer.model.carddb.CardDatabase,
        values: typing.Iterable[typing.Tuple[str]]):
    """Checks Oracle_id"""
    db_content = model.db.execute('SELECT oracle_id FROM Card').fetchall()
    assert_that(db_content, contains_inanyorder(*values), f"Card relation contains unexpected data")


def _assert_print_language_contains(
        model: mtg_proxy_printer.model.carddb.CardDatabase,
        values: typing.Iterable[typing.Tuple[str]]):
    """Checks language"""
    db_content = model.db.execute('SELECT "language" FROM PrintLanguage').fetchall()
    assert_that(db_content, contains_inanyorder(*values), f"PrintLanguage relation contains unexpected data")


def _assert_set_contains(
        model: mtg_proxy_printer.model.carddb.CardDatabase,
        values: typing.Iterable[typing.Tuple[str, str, str]]):
    """Checks "set", set_name, set_uri"""
    db_content = model.db.execute('SELECT "set", set_name, set_uri FROM "Set"').fetchall()
    assert_that(db_content, contains_inanyorder(*values), f"Set relation contains unexpected data")


def _assert_face_name_contains(
        model: mtg_proxy_printer.model.carddb.CardDatabase,
        values: typing.Sequence[typing.Tuple[str]]):
    """Checks card_name"""
    db_content = model.db.execute('SELECT card_name FROM FaceName').fetchall()
    assert_that(db_content, contains_inanyorder(*values), f"FaceName relation contains unexpected data")


def _assert_card_face_contains(
        model: mtg_proxy_printer.model.carddb.CardDatabase,
        values: typing.Sequence[typing.Tuple[str, str, bool, str, bool]]):
    """Checks collector_number, scryfall_id, highres_image, png_image_uri, is_front"""
    db_content = model.db.execute(
        "SELECT collector_number, scryfall_id, highres_image, png_image_uri, is_front FROM CardFace").fetchall()
    assert_that(db_content, contains_inanyorder(*values), "CardFace relation contains unexpected data")


def _assert_all_printings_contains(
        model: mtg_proxy_printer.model.carddb.CardDatabase,
        values: typing.Sequence[typing.Tuple[str, str, str,str, str, bool, str, bool]]):
    """Checks card_name, "set", "language", collector_number, scryfall_id, highres_image, png_image_uri"""
    db_content = model.db.execute(
        'SELECT card_name, "set", "language", collector_number, scryfall_id, highres_image, png_image_uri, is_front '
        'FROM AllPrintings').fetchall()
    assert_that(db_content, contains_inanyorder(*values), "CardFace relation contains unexpected data")


def _assert_relation_is_empty(model: mtg_proxy_printer.model.carddb.CardDatabase, name: str):
    assert_that(
        model.db.execute(f"SELECT * FROM {name}").fetchall(),
        is_(empty()), f"{name} contains unexpected data"
    )


def _assert_model_is_empty(model: mtg_proxy_printer.model.carddb.CardDatabase):
    """
    Checks, if the model is empty. This is used by tests that check if cards are properly skipped based on
    download settings.
    """
    _assert_relation_is_empty(model, "PrintLanguage")
    _assert_relation_is_empty(model, "Card")
    _assert_relation_is_empty(model, "FaceName")
    _assert_relation_is_empty(model, "CardFace")
    _assert_relation_is_empty(model, '"Set"')
    _assert_relation_is_empty(model, "AllPrintings")


def populate_database(model, data):
    # Don’t bother the Scryfall API when running tests, so mock the web-accessing parts of the constructor.
    with patch("mtg_proxy_printer.card_info_importer.CardInfoDownloader.get_scryfall_bulk_card_data_url") as mock:
        # The URL is not used to fetch data, as the test data directly supplies the JSON document.
        mock.return_value = ("http://example.com", 1)
        cid = mtg_proxy_printer.card_info_importer.CardInfoDownloader(model)
        cid.populate_database(data)


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
    _assert_print_language_contains(model, [("zhs",)])
    _assert_card_contains(model, [("ea9c459a-6047-43aa-968f-a582be4000e8",)])
    _assert_set_contains(model, [
        ("xln", "Ixalan", "https://scryfall.com/sets/xln?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("伊替莫成长仪式",),
        ("烈阳育所伊替莫",),
    ])
    _assert_card_face_contains(model, [
        ("191", "000847d3-ebde-4580-a00e-61d501e99485", False, "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/000847d3-ebde-4580-a00e-61d501e99485.png?1562549619", True),
        ("191", "000847d3-ebde-4580-a00e-61d501e99485", False, "https://c1.scryfall.com/file/scryfall-cards/png/back/0/0/000847d3-ebde-4580-a00e-61d501e99485.png?1562549619", False),
    ])
    _assert_all_printings_contains(model, [
        ("伊替莫成长仪式", "xln", "zhs", "191", "000847d3-ebde-4580-a00e-61d501e99485", False, "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/000847d3-ebde-4580-a00e-61d501e99485.png?1562549619", True),
        ("烈阳育所伊替莫", "xln", "zhs", "191", "000847d3-ebde-4580-a00e-61d501e99485", False, "https://c1.scryfall.com/file/scryfall-cards/png/back/0/0/000847d3-ebde-4580-a00e-61d501e99485.png?1562549619", False),
    ])


def test_import_split_card():
    """Has two or more smaller cards on one side."""
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    # Loads Korean printing of "Cut // Ribbons"
    data = load_json("split_card")
    populate_database(model, data)
    _assert_print_language_contains(model, [("ko",)])
    _assert_card_contains(model, [("98a5bf1a-1088-4339-9a9b-6ee5e4956cf1",)])
    _assert_set_contains(model, [
        ("akh", "Amonkhet", "https://scryfall.com/sets/akh?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("절단",),
        ("띠",),
    ])
    _assert_card_face_contains(model, [
        ("223", "00031562-3818-49f9-b45c-ab28a521284c", False, "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/00031562-3818-49f9-b45c-ab28a521284c.png?1540283200", True),
        ("223", "00031562-3818-49f9-b45c-ab28a521284c", False, "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/00031562-3818-49f9-b45c-ab28a521284c.png?1540283200", True),
    ])
    _assert_all_printings_contains(model, [
        ("절단", "akh", "ko", "223", "00031562-3818-49f9-b45c-ab28a521284c", False, "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/00031562-3818-49f9-b45c-ab28a521284c.png?1540283200", True),
        ("띠", "akh", "ko", "223", "00031562-3818-49f9-b45c-ab28a521284c", False, "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/00031562-3818-49f9-b45c-ab28a521284c.png?1540283200", True),
    ])


def test_import_english_double_faced_art_card():
    """Has a printing on both sides."""
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    # Loads English art series card "Clearwater Pathway // Clearwater Pathway"
    data = load_json("english_double_faced_card")
    populate_database(model, data)
    _assert_print_language_contains(model, [("en",)])
    _assert_card_contains(model, [("a755add5-04ec-4e37-9eb6-152d52cfa46d",)])
    _assert_set_contains(model, [
        ("aznr", "Zendikar Rising Art Series", "https://scryfall.com/sets/aznr?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("Clearwater Pathway",),
    ])
    _assert_card_face_contains(model, [
        ("25", "002ad179-ddf4-4f48-9504-cfa02e11a52e", False, "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/002ad179-ddf4-4f48-9504-cfa02e11a52e.png?1600982859", True),
        ("25", "002ad179-ddf4-4f48-9504-cfa02e11a52e", False, "https://c1.scryfall.com/file/scryfall-cards/png/back/0/0/002ad179-ddf4-4f48-9504-cfa02e11a52e.png?1600982859", False),
    ])
    _assert_all_printings_contains(model, [
        ("Clearwater Pathway", "aznr", "en", "25", "002ad179-ddf4-4f48-9504-cfa02e11a52e", False, "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/002ad179-ddf4-4f48-9504-cfa02e11a52e.png?1600982859", True),
        ("Clearwater Pathway", "aznr", "en", "25", "002ad179-ddf4-4f48-9504-cfa02e11a52e", False, "https://c1.scryfall.com/file/scryfall-cards/png/back/0/0/002ad179-ddf4-4f48-9504-cfa02e11a52e.png?1600982859", False),
    ])


def test_import_regular_english_card():
    """Tests import with a simple, regular, English card."""
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    # Loads "Fury Sliver" from Time Spiral
    data = load_json("regular_english_card")
    populate_database(model, data)
    _assert_print_language_contains(model, [("en",)])
    _assert_card_contains(model, [("44623693-51d6-49ad-8cd7-140505caf02f",)])
    _assert_set_contains(model, [
        ("tsp", "Time Spiral", "https://scryfall.com/sets/tsp?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("Fury Sliver",),
    ])
    _assert_card_face_contains(model, [
        ("157", "0000579f-7b35-4ed3-b44c-db2a538066fe", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979", True),
    ])
    _assert_all_printings_contains(model, [
        ("Fury Sliver", "tsp", "en", "157", "0000579f-7b35-4ed3-b44c-db2a538066fe", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979", True),
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
    _assert_model_is_empty(model)


def test_import_card_depicting_racism_if_enabled():
    """
    Test if the importer imports cards banned for depicting racism,
    if the option to download these in the setting is enabled.
    """
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    # Loads German printing of "Crusade"
    data = load_json("depicting_racism")
    _populate_database_with_specific_download_setting(model, data, "download-cards-depicting-racism", "True")
    _assert_print_language_contains(model, [("de",)])
    _assert_card_contains(model, [("4692740f-be90-459f-8d90-c4ae71771595",)])
    _assert_set_contains(model, [
        ("4ed", "Fourth Edition", "https://scryfall.com/sets/4ed?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("Kreuzzug",),
    ])
    _assert_card_face_contains(model, [
        ("20", "00809cb0-b152-441f-a0be-1bc1048dad92", False, "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/00809cb0-b152-441f-a0be-1bc1048dad92.png?1559603956", True),
    ])
    _assert_all_printings_contains(model, [
        ("Kreuzzug", "4ed", "de", "20", "00809cb0-b152-441f-a0be-1bc1048dad92", False, "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/00809cb0-b152-441f-a0be-1bc1048dad92.png?1559603956", True),
    ])


def test_import_skips_funny_card_if_disabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("funny_card")
    _populate_database_with_specific_download_setting(model, data, "download-funny-cards", "False")
    _assert_model_is_empty(model)


def test_import_funny_card_if_enabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("funny_card")
    _populate_database_with_specific_download_setting(model, data, "download-funny-cards", "True")
    _assert_print_language_contains(model, [("en",)])
    _assert_card_contains(model, [("8789d5fa-101c-457a-90ec-5cf067f5289b",)])
    _assert_set_contains(model, [
        ("unh", "Unhinged", "https://scryfall.com/sets/unh?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("Aesthetic Consultation",),
    ])
    _assert_card_face_contains(model, [
        ("48", "0464a507-20e5-42d5-8aca-12504a869f21", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/0/4/0464a507-20e5-42d5-8aca-12504a869f21.png?1562487441", True),
    ])
    _assert_all_printings_contains(model, [
        ("Aesthetic Consultation", "unh", "en", "48", "0464a507-20e5-42d5-8aca-12504a869f21", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/0/4/0464a507-20e5-42d5-8aca-12504a869f21.png?1562487441", True),
    ])


def test_import_skips_gold_bordered_card_if_disabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("gold_bordered_card")
    _populate_database_with_specific_download_setting(model, data, "download-gold-bordered", "False")
    _assert_model_is_empty(model)


def test_import_gold_bordered_card_if_enabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("gold_bordered_card")
    _populate_database_with_specific_download_setting(model, data, "download-gold-bordered", "True")
    _assert_print_language_contains(model, [("en",)])
    _assert_card_contains(model, [("d0e1904e-1a37-41f6-8582-b9ea794bb886",)])
    _assert_set_contains(model, [
        ("wc97", "World Championship Decks 1997", "https://scryfall.com/sets/wc97?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("Abduction",),
    ])
    _assert_card_face_contains(model, [
        ("pm30", "2afb04a3-2940-4860-a4be-223aca0bac4b", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/2/a/2afb04a3-2940-4860-a4be-223aca0bac4b.png?1562904104", True),
    ])
    _assert_all_printings_contains(model, [
        ("Abduction", "wc97", "en", "pm30", "2afb04a3-2940-4860-a4be-223aca0bac4b", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/2/a/2afb04a3-2940-4860-a4be-223aca0bac4b.png?1562904104", True),
    ])


def test_import_skips_white_bordered_card_if_disabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("white_bordered_card")
    _populate_database_with_specific_download_setting(model, data, "download-white-bordered", "False")
    _assert_model_is_empty(model)


def test_import_white_bordered_card_if_enabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("white_bordered_card")
    _populate_database_with_specific_download_setting(model, data, "download-white-bordered", "True")
    _assert_print_language_contains(model, [("en",)])
    _assert_card_contains(model, [("2c57c4e9-0a46-45d6-92db-9203fb722b60",)])
    _assert_set_contains(model, [
        ("4ed", "Fourth Edition", "https://scryfall.com/sets/4ed?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("Abomination",),
    ])
    _assert_card_face_contains(model, [
        ("117", "a363bc91-8278-448e-9d5c-564e4b51eb62", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/a/3/a363bc91-8278-448e-9d5c-564e4b51eb62.png?1559603880", True),
    ])
    _assert_all_printings_contains(model, [
        ("Abomination", "4ed", "en", "117", "a363bc91-8278-448e-9d5c-564e4b51eb62", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/a/3/a363bc91-8278-448e-9d5c-564e4b51eb62.png?1559603880", True),
    ])


def test_import_skips_card_banned_in_brawl_if_disabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("illegal_in_brawl")
    _populate_database_with_specific_download_setting(model, data, "download-illegal-in-brawl", "False")
    _assert_model_is_empty(model)


def test_import_card_banned_in_brawl_if_enabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("illegal_in_brawl")
    _populate_database_with_specific_download_setting(model, data, "download-illegal-in-brawl", "True")
    _assert_print_language_contains(model, [("en",)])
    _assert_card_contains(model, [("ae0b8c13-0a71-4a60-bf9f-6e2da9503e9c",)])
    _assert_set_contains(model, [
        ("m13", "Magic 2013", "https://scryfall.com/sets/m13?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("Worldfire",),
    ])
    _assert_card_face_contains(model, [
        ("158", "2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/2/e/2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11.png?1562552052", True),
    ])
    _assert_all_printings_contains(model, [
        ("Worldfire", "m13", "en", "158", "2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/2/e/2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11.png?1562552052", True),
    ])


def test_import_skips_card_banned_in_commander_if_disabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("illegal_in_commander")
    _populate_database_with_specific_download_setting(model, data, "download-illegal-in-commander", "False")
    _assert_model_is_empty(model)


def test_import_card_banned_in_commander_if_enabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("illegal_in_commander")
    _populate_database_with_specific_download_setting(model, data, "download-illegal-in-commander", "True")
    _assert_print_language_contains(model, [("en",)])
    _assert_card_contains(model, [("ae0b8c13-0a71-4a60-bf9f-6e2da9503e9c",)])
    _assert_set_contains(model, [
        ("m13", "Magic 2013", "https://scryfall.com/sets/m13?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("Worldfire",),
    ])
    _assert_card_face_contains(model, [
        ("158", "2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/2/e/2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11.png?1562552052", True),
    ])
    _assert_all_printings_contains(model, [
        ("Worldfire", "m13", "en", "158", "2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/2/e/2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11.png?1562552052", True),
    ])


def test_import_skips_card_banned_in_historic_if_disabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("illegal_in_historic")
    _populate_database_with_specific_download_setting(model, data, "download-illegal-in-historic", "False")
    _assert_model_is_empty(model)


def test_import_card_banned_in_historic_if_enabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("illegal_in_historic")
    _populate_database_with_specific_download_setting(model, data, "download-illegal-in-historic", "True")
    _assert_print_language_contains(model, [("en",)])
    _assert_card_contains(model, [("ae0b8c13-0a71-4a60-bf9f-6e2da9503e9c",)])
    _assert_set_contains(model, [
        ("m13", "Magic 2013", "https://scryfall.com/sets/m13?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("Worldfire",),
    ])
    _assert_card_face_contains(model, [
        ("158", "2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/2/e/2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11.png?1562552052", True),
    ])
    _assert_all_printings_contains(model, [
        ("Worldfire", "m13", "en", "158", "2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/2/e/2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11.png?1562552052", True),
    ])


def test_import_skips_card_banned_in_legacy_if_disabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("illegal_in_legacy")
    _populate_database_with_specific_download_setting(model, data, "download-illegal-in-legacy", "False")
    _assert_model_is_empty(model)


def test_import_card_banned_in_legacy_if_enabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("illegal_in_legacy")
    _populate_database_with_specific_download_setting(model, data, "download-illegal-in-legacy", "True")
    _assert_print_language_contains(model, [("en",)])
    _assert_card_contains(model, [("f5ca7b13-8003-4361-b827-7095c89f2750",)])
    _assert_set_contains(model, [
        ("leg", "Legends", "https://scryfall.com/sets/leg?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("Falling Star",),
    ])
    _assert_card_face_contains(model, [
        ("145", "f2b9983e-20d4-4d12-9e2c-ec6d9a345787", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/f/2/f2b9983e-20d4-4d12-9e2c-ec6d9a345787.png?1562861838", True),
    ])
    _assert_all_printings_contains(model, [
        ("Falling Star", "leg", "en", "145", "f2b9983e-20d4-4d12-9e2c-ec6d9a345787", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/f/2/f2b9983e-20d4-4d12-9e2c-ec6d9a345787.png?1562861838", True),
    ])


def test_import_skips_card_banned_in_modern_if_disabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("illegal_in_modern")
    _populate_database_with_specific_download_setting(model, data, "download-illegal-in-modern", "False")
    _assert_model_is_empty(model)


def test_import_card_banned_in_modern_if_enabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("illegal_in_modern")
    _populate_database_with_specific_download_setting(model, data, "download-illegal-in-modern", "True")
    _assert_print_language_contains(model, [("en",)])
    _assert_card_contains(model, [("f5ca7b13-8003-4361-b827-7095c89f2750",)])
    _assert_set_contains(model, [
        ("leg", "Legends", "https://scryfall.com/sets/leg?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("Falling Star",),
    ])
    _assert_card_face_contains(model, [
        ("145", "f2b9983e-20d4-4d12-9e2c-ec6d9a345787", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/f/2/f2b9983e-20d4-4d12-9e2c-ec6d9a345787.png?1562861838", True),
    ])
    _assert_all_printings_contains(model, [
        ("Falling Star", "leg", "en", "145", "f2b9983e-20d4-4d12-9e2c-ec6d9a345787", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/f/2/f2b9983e-20d4-4d12-9e2c-ec6d9a345787.png?1562861838", True),
    ])


def test_import_skips_card_banned_in_pauper_if_disabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("illegal_in_pauper")
    _populate_database_with_specific_download_setting(model, data, "download-illegal-in-pauper", "False")
    _assert_model_is_empty(model)


def test_import_card_banned_in_pauper_if_enabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("illegal_in_pauper")
    _populate_database_with_specific_download_setting(model, data, "download-illegal-in-pauper", "True")
    _assert_print_language_contains(model, [("en",)])
    _assert_card_contains(model, [("ae0b8c13-0a71-4a60-bf9f-6e2da9503e9c",)])
    _assert_set_contains(model, [
        ("m13", "Magic 2013", "https://scryfall.com/sets/m13?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("Worldfire",),
    ])
    _assert_card_face_contains(model, [
        ("158", "2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/2/e/2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11.png?1562552052", True),
    ])
    _assert_all_printings_contains(model, [
        ("Worldfire", "m13", "en", "158", "2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/2/e/2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11.png?1562552052", True),
    ])


def test_import_skips_card_banned_in_penny_if_disabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("illegal_in_penny")
    _populate_database_with_specific_download_setting(model, data, "download-illegal-in-penny", "False")
    _assert_model_is_empty(model)


def test_import_card_banned_in_penny_if_enabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("illegal_in_penny")
    _populate_database_with_specific_download_setting(model, data, "download-illegal-in-penny", "True")
    _assert_print_language_contains(model, [("en",)])
    _assert_card_contains(model, [("f5ca7b13-8003-4361-b827-7095c89f2750",)])
    _assert_set_contains(model, [
        ("leg", "Legends", "https://scryfall.com/sets/leg?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("Falling Star",),
    ])
    _assert_card_face_contains(model, [
        ("145", "f2b9983e-20d4-4d12-9e2c-ec6d9a345787", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/f/2/f2b9983e-20d4-4d12-9e2c-ec6d9a345787.png?1562861838", True),
    ])
    _assert_all_printings_contains(model, [
        ("Falling Star", "leg", "en", "145", "f2b9983e-20d4-4d12-9e2c-ec6d9a345787", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/f/2/f2b9983e-20d4-4d12-9e2c-ec6d9a345787.png?1562861838", True),
    ])


def test_import_skips_card_banned_in_pioneer_if_disabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("illegal_in_pioneer")
    _populate_database_with_specific_download_setting(model, data, "download-illegal-in-pioneer", "False")
    _assert_model_is_empty(model)


def test_import_card_banned_in_pioneer_if_enabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("illegal_in_pioneer")
    _populate_database_with_specific_download_setting(model, data, "download-illegal-in-pioneer", "True")
    _assert_print_language_contains(model, [("en",)])
    _assert_card_contains(model, [("ae0b8c13-0a71-4a60-bf9f-6e2da9503e9c",)])
    _assert_set_contains(model, [
        ("m13", "Magic 2013", "https://scryfall.com/sets/m13?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("Worldfire",),
    ])
    _assert_card_face_contains(model, [
        ("158", "2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/2/e/2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11.png?1562552052", True),
    ])
    _assert_all_printings_contains(model, [
        ("Worldfire", "m13", "en", "158", "2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/2/e/2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11.png?1562552052", True),
    ])


def test_import_skips_card_banned_in_standard_if_disabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("illegal_in_standard")
    _populate_database_with_specific_download_setting(model, data, "download-illegal-in-standard", "False")
    _assert_model_is_empty(model)


def test_import_card_banned_in_standard_if_enabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("illegal_in_standard")
    _populate_database_with_specific_download_setting(model, data, "download-illegal-in-standard", "True")
    _assert_print_language_contains(model, [("en",)])
    _assert_card_contains(model, [("ae0b8c13-0a71-4a60-bf9f-6e2da9503e9c",)])
    _assert_set_contains(model, [
        ("m13", "Magic 2013", "https://scryfall.com/sets/m13?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("Worldfire",),
    ])
    _assert_card_face_contains(model, [
        ("158", "2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/2/e/2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11.png?1562552052", True),
    ])
    _assert_all_printings_contains(model, [
        ("Worldfire", "m13", "en", "158", "2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/2/e/2ef3d4b5-0453-4bf0-b018-23b0c3b9ae11.png?1562552052", True),
    ])


def test_import_skips_card_banned_in_vintage_if_disabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("illegal_in_vintage")
    _populate_database_with_specific_download_setting(model, data, "download-illegal-in-vintage", "False")
    _assert_model_is_empty(model)


def test_import_card_banned_in_vintage_if_enabled():
    model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json("illegal_in_vintage")
    _populate_database_with_specific_download_setting(model, data, "download-illegal-in-vintage", "True")
    _assert_print_language_contains(model, [("en",)])
    _assert_card_contains(model, [("f5ca7b13-8003-4361-b827-7095c89f2750",)])
    _assert_set_contains(model, [
        ("leg", "Legends", "https://scryfall.com/sets/leg?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("Falling Star",),
    ])
    _assert_card_face_contains(model, [
        ("145", "f2b9983e-20d4-4d12-9e2c-ec6d9a345787", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/f/2/f2b9983e-20d4-4d12-9e2c-ec6d9a345787.png?1562861838", True),
    ])
    _assert_all_printings_contains(model, [
        ("Falling Star", "leg", "en", "145", "f2b9983e-20d4-4d12-9e2c-ec6d9a345787", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/f/2/f2b9983e-20d4-4d12-9e2c-ec6d9a345787.png?1562861838", True),
    ])


"""
Assert-template: (Use for quick copy&paste when adding new test cases.)

_assert_print_language_contains(model, [("",)])
_assert_card_contains(model, [("",)])
_assert_set_contains(model, [
    ("", "", ""),
])
_assert_face_name_contains(model, [
    ("",),
])
_assert_card_face_contains(model, [
    ("", "", ""),
])
_assert_all_printings_contains(model, [
    ("", "", "", "", "", ""),
])

"""
