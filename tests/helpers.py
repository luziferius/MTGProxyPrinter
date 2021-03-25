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

import json
import typing
from unittest.mock import patch

import pkg_resources

import mtg_proxy_printer.model.carddb
import mtg_proxy_printer.card_info_downloader
import mtg_proxy_printer.logger
import mtg_proxy_printer.settings


def setup_logging_for_testing():
    mtg_proxy_printer.logger.configure_root_logger()
    mtg_proxy_printer.logger.root_logger.info("Configured logging system for test runs.")
    mtg_proxy_printer.logger.root_logger.info(__name__)


def setup_settings_for_testing():
    mtg_proxy_printer.settings.settings = mtg_proxy_printer.settings.DEFAULT_SETTINGS


def populate_database(model, data):
    mtg_proxy_printer.card_info_downloader.CardInfoDownloadWorker(model).populate_database(data)


def load_json(name: str) -> typing.Generator[mtg_proxy_printer.card_info_downloader.JSONType, None, None]:
    yield json.loads(
        pkg_resources.resource_string(f"tests.json_samples", f"{name}.json").decode("utf-8")
    )


def create_new_card_database_with_json_card(
        json_file_name: str, option: str = None, value: str = None) -> mtg_proxy_printer.model.carddb.CardDatabase:
    new_model = mtg_proxy_printer.model.carddb.CardDatabase(":memory:")
    data = load_json(json_file_name)

    # Either both None or both set non-empty
    assert (option is None and value is None) or (bool(option) and bool(value))
    if option is None:
        populate_database(new_model, data)
    else:
        with patch.dict(mtg_proxy_printer.settings.settings["downloads"], {option: value}):
            populate_database(new_model, data)
    return new_model
