# Copyright (C) 2019 Thomas Hess <thomas.hess@udo.edu>

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

import functools
import json
import typing
from unittest.mock import patch, MagicMock
import pkg_resources

import ijson
from hamcrest import assert_that, is_, empty, has_key

import mtg_proxy_printer.model
import mtg_proxy_printer.model.carddb
import mtg_proxy_printer.card_info_downloader
import mtg_proxy_printer.logger
import mtg_proxy_printer.settings


def setup_logging_for_testing():
    mtg_proxy_printer.logger.configure_root_logger()
    mtg_proxy_printer.logger.root_logger.info("Configured logging system for test runs.")
    mtg_proxy_printer.logger.root_logger.info(__name__)


def setup_settings_for_testing():
    # Make sure that the tests don’t overwrite the settings stored on disk. Raise an exception, should that occur.
    mtg_proxy_printer.settings.write_settings_to_file = MagicMock()
    mtg_proxy_printer.settings.write_settings_to_file.side_effect = AssertionError(
        "mtg_proxy_printer.settings.write_settings_to_file() called within test code!"
    )
    mtg_proxy_printer.settings.settings.read_dict(mtg_proxy_printer.settings.DEFAULT_SETTINGS)
    for setting in mtg_proxy_printer.settings.settings["downloads"].keys():
        # Turn off all download filters, so that the defaults don’t affect the test cases
        mtg_proxy_printer.settings.settings["downloads"][setting] = str(True)


def populate_database(card_db: mtg_proxy_printer.model.carddb.CardDatabase, data):
    mtg_proxy_printer.card_info_downloader.CardInfoDownloadWorker(card_db).populate_database(data)


@functools.lru_cache()
def load_json(name: str) -> mtg_proxy_printer.card_info_downloader.JSONType:
    return json.loads(pkg_resources.resource_string("tests.json_samples", f"{name}.json").decode("utf-8"))


def fill_card_database_with_json_cards(
        card_db: mtg_proxy_printer.model.carddb.CardDatabase,
        json_files_or_names: typing.List[typing.Union[str, mtg_proxy_printer.card_info_downloader.JSONType]],
        option: str = None, value: str = None) -> mtg_proxy_printer.model.carddb.CardDatabase:
    data = [
        load_json(json_file_or_name) if isinstance(json_file_or_name, str) else json_file_or_name
        for json_file_or_name in json_files_or_names
    ]
    # Either both None or both set non-empty
    assert (option is None and value is None) or (bool(option) and bool(value))
    if option is None:
        populate_database(card_db, data)
    else:
        assert_that(
            mtg_proxy_printer.settings.settings["downloads"],
            has_key(option),
            f"Test setup failed: Download settings do not contain expected setting: {option}"
        )
        with patch.dict(mtg_proxy_printer.settings.settings["downloads"], {option: value}):
            populate_database(card_db, data)
    return card_db


def fill_card_database_with_json_card(
        card_db: mtg_proxy_printer.model.carddb.CardDatabase,
        json_file_or_name: typing.Union[str, mtg_proxy_printer.card_info_downloader.JSONType],
        option: str = None, value: str = None) -> mtg_proxy_printer.model.carddb.CardDatabase:
    return fill_card_database_with_json_cards(card_db, [json_file_or_name], option, value)


def assert_relation_is_empty(card_db: mtg_proxy_printer.model.carddb.CardDatabase, name: str):
    assert_that(
        card_db.db.execute(f'SELECT * FROM "{name}"').fetchall(),
        is_(empty()), f"{name} contains unexpected data"
    )


def assert_model_is_empty(card_db: mtg_proxy_printer.model.carddb.CardDatabase):
    """
    Checks, if the model is empty. This is used by tests that check if cards are properly skipped based on
    download settings.
    """
    for relation in ("PrintLanguage", "Card", "FaceName", "CardFace", "Set", "AllPrintings"):
        assert_relation_is_empty(card_db, relation)
