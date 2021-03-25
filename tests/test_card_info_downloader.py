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

import typing

from hamcrest import *
import pytest

import mtg_proxy_printer.model.carddb
import mtg_proxy_printer.card_info_downloader
from .helpers import create_new_card_database_with_json_card


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
    """Checks "set", set_name, scryfall_set_uri"""
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


def test_import_double_faced():
    """
    Double faced card. Any transform/meld/modal double faced card.
    """
    # Loads Chinese printing of "Growing Rites of Itlimoc // Itlimoc, Cradle of the Sun"
    model = create_new_card_database_with_json_card("non_english_double_faced_card")
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
    # Loads Korean printing of "Cut // Ribbons"
    model = create_new_card_database_with_json_card("split_card")
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
    # Loads English art series card "Clearwater Pathway // Clearwater Pathway"
    model = create_new_card_database_with_json_card("english_double_faced_card")
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
    # Loads "Fury Sliver" from Time Spiral
    model = create_new_card_database_with_json_card("regular_english_card")
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
    # Loads German printing of "Crusade"
    model = create_new_card_database_with_json_card("depicting_racism", "download-cards-depicting-racism", "False")
    _assert_model_is_empty(model)


def test_import_card_depicting_racism_if_enabled():
    """
    Test if the importer imports cards banned for depicting racism,
    if the option to download these in the setting is enabled.
    """
    # Loads German printing of "Crusade"
    model = create_new_card_database_with_json_card("depicting_racism", "download-cards-depicting-racism", "True")
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
    model = create_new_card_database_with_json_card("funny_card", "download-funny-cards", "False")
    _assert_model_is_empty(model)


def test_import_funny_card_if_enabled():
    model = create_new_card_database_with_json_card("funny_card", "download-funny-cards", "True")
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
    model = create_new_card_database_with_json_card("gold_bordered_card", "download-gold-bordered", "False")
    _assert_model_is_empty(model)


def test_import_gold_bordered_card_if_enabled():
    model = create_new_card_database_with_json_card("gold_bordered_card", "download-gold-bordered", "True")
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
    model = create_new_card_database_with_json_card("white_bordered_card", "download-white-bordered", "False")
    _assert_model_is_empty(model)


def test_import_white_bordered_card_if_enabled():
    model = create_new_card_database_with_json_card("white_bordered_card", "download-white-bordered", "True")
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
    model = create_new_card_database_with_json_card("banned_in_brawl", "download-banned-in-brawl", "False")
    _assert_model_is_empty(model)


def test_import_card_banned_in_brawl_if_enabled():
    model = create_new_card_database_with_json_card("banned_in_brawl", "download-banned-in-brawl", "True")
    _assert_print_language_contains(model, [("en",)])
    _assert_card_contains(model, [("60c60923-ff1b-43f7-8768-731499fcffc9",)])
    _assert_set_contains(model, [
        ("eld", "Throne of Eldraine", "https://scryfall.com/sets/eld?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("Oko, Thief of Crowns",),
    ])
    _assert_card_face_contains(model, [
        ("197", "3462a3d0-5552-49fa-9eb7-100960c55891", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
    ])
    _assert_all_printings_contains(model, [
        ("Oko, Thief of Crowns", "eld", "en", "197", "3462a3d0-5552-49fa-9eb7-100960c55891", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
    ])


def test_import_skips_card_banned_in_commander_if_disabled():
    model = create_new_card_database_with_json_card("banned_in_commander", "download-banned-in-commander", "False")
    _assert_model_is_empty(model)


def test_import_card_banned_in_commander_if_enabled():
    model = create_new_card_database_with_json_card("banned_in_commander", "download-banned-in-commander", "True")
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
    model = create_new_card_database_with_json_card("banned_in_historic", "download-banned-in-historic", "False")
    _assert_model_is_empty(model)


def test_import_card_banned_in_historic_if_enabled():
    model = create_new_card_database_with_json_card("banned_in_historic", "download-banned-in-historic", "True")
    _assert_print_language_contains(model, [("en",)])
    _assert_card_contains(model, [("60c60923-ff1b-43f7-8768-731499fcffc9",)])
    _assert_set_contains(model, [
        ("eld", "Throne of Eldraine", "https://scryfall.com/sets/eld?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("Oko, Thief of Crowns",),
    ])
    _assert_card_face_contains(model, [
        ("197", "3462a3d0-5552-49fa-9eb7-100960c55891", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
    ])
    _assert_all_printings_contains(model, [
        ("Oko, Thief of Crowns", "eld", "en", "197", "3462a3d0-5552-49fa-9eb7-100960c55891", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
    ])


def test_import_skips_card_banned_in_legacy_if_disabled():
    model = create_new_card_database_with_json_card("banned_in_legacy", "download-banned-in-legacy", "False")
    _assert_model_is_empty(model)


def test_import_card_banned_in_legacy_if_enabled():
    model = create_new_card_database_with_json_card("banned_in_legacy", "download-banned-in-legacy", "True")
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
    model = create_new_card_database_with_json_card("banned_in_modern", "download-banned-in-modern", "False")
    _assert_model_is_empty(model)


def test_import_card_banned_in_modern_if_enabled():
    model = create_new_card_database_with_json_card("banned_in_modern", "download-banned-in-modern", "True")
    _assert_print_language_contains(model, [("en",)])
    _assert_card_contains(model, [("60c60923-ff1b-43f7-8768-731499fcffc9",)])
    _assert_set_contains(model, [
        ("eld", "Throne of Eldraine", "https://scryfall.com/sets/eld?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("Oko, Thief of Crowns",),
    ])
    _assert_card_face_contains(model, [
        ("197", "3462a3d0-5552-49fa-9eb7-100960c55891", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
    ])
    _assert_all_printings_contains(model, [
        ("Oko, Thief of Crowns", "eld", "en", "197", "3462a3d0-5552-49fa-9eb7-100960c55891", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
    ])


def test_import_skips_card_banned_in_pauper_if_disabled():
    model = create_new_card_database_with_json_card("banned_in_pauper", "download-banned-in-pauper", "False")
    _assert_model_is_empty(model)


def test_import_card_banned_in_pauper_if_enabled():
    model = create_new_card_database_with_json_card("banned_in_pauper", "download-banned-in-pauper", "True")
    _assert_print_language_contains(model, [("en",)])
    _assert_card_contains(model, [("8fcf50cd-e6d0-4516-850f-d42ee75dcc3a",)])
    _assert_set_contains(model, [
        ("2xm", "Double Masters", "https://scryfall.com/sets/2xm?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("Expedition Map",),
    ])
    _assert_card_face_contains(model, [
        ("255", "551c0a45-9515-4e51-84e5-79703832a661", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/5/5/551c0a45-9515-4e51-84e5-79703832a661.png?1599709184", True),
    ])
    _assert_all_printings_contains(model, [
        ("Expedition Map", "2xm", "en", "255", "551c0a45-9515-4e51-84e5-79703832a661", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/5/5/551c0a45-9515-4e51-84e5-79703832a661.png?1599709184", True),
    ])


def test_import_skips_card_banned_in_penny_if_disabled():
    model = create_new_card_database_with_json_card("banned_in_penny", "download-banned-in-penny", "False")
    _assert_model_is_empty(model)


def test_import_card_banned_in_penny_if_enabled():
    model = create_new_card_database_with_json_card("banned_in_penny", "download-banned-in-penny", "True")
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
    model = create_new_card_database_with_json_card("banned_in_pioneer", "download-banned-in-pioneer", "False")
    _assert_model_is_empty(model)


def test_import_card_banned_in_pioneer_if_enabled():
    model = create_new_card_database_with_json_card("banned_in_pioneer", "download-banned-in-pioneer", "True")
    _assert_print_language_contains(model, [("en",)])
    _assert_card_contains(model, [("60c60923-ff1b-43f7-8768-731499fcffc9",)])
    _assert_set_contains(model, [
        ("eld", "Throne of Eldraine", "https://scryfall.com/sets/eld?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("Oko, Thief of Crowns",),
    ])
    _assert_card_face_contains(model, [
        ("197", "3462a3d0-5552-49fa-9eb7-100960c55891", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
    ])
    _assert_all_printings_contains(model, [
        ("Oko, Thief of Crowns", "eld", "en", "197", "3462a3d0-5552-49fa-9eb7-100960c55891", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
    ])


def test_import_skips_card_banned_in_standard_if_disabled():
    model = create_new_card_database_with_json_card("banned_in_standard", "download-banned-in-standard", "False")
    _assert_model_is_empty(model)


def test_import_card_banned_in_standard_if_enabled():
    model = create_new_card_database_with_json_card("banned_in_standard", "download-banned-in-standard", "True")
    _assert_print_language_contains(model, [("en",)])
    _assert_card_contains(model, [("60c60923-ff1b-43f7-8768-731499fcffc9",)])
    _assert_set_contains(model, [
        ("eld", "Throne of Eldraine", "https://scryfall.com/sets/eld?utm_source=api"),
    ])
    _assert_face_name_contains(model, [
        ("Oko, Thief of Crowns",),
    ])
    _assert_card_face_contains(model, [
        ("197", "3462a3d0-5552-49fa-9eb7-100960c55891", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
    ])
    _assert_all_printings_contains(model, [
        ("Oko, Thief of Crowns", "eld", "en", "197", "3462a3d0-5552-49fa-9eb7-100960c55891", True, "https://c1.scryfall.com/file/scryfall-cards/png/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.png?1613387000", True),
    ])


def test_import_skips_card_banned_in_vintage_if_disabled():
    model = create_new_card_database_with_json_card("banned_in_vintage", "download-banned-in-vintage", "False")
    _assert_model_is_empty(model)


def test_import_card_banned_in_vintage_if_enabled():
    model = create_new_card_database_with_json_card("banned_in_vintage", "download-banned-in-vintage", "True")
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
