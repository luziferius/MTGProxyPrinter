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
import functools
import json
import os
import sqlite3
from numbers import Real
from pathlib import Path
from typing import Literal, Any, Callable
from unittest.mock import patch, MagicMock

from pint import Quantity
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest import assert_that, is_, empty, contains_inanyorder, has_properties, equal_to, any_of, instance_of, \
    close_to, all_of, greater_than_or_equal_to, less_than_or_equal_to
from hamcrest.core.description import Description
from hamcrest.core.matcher import Matcher
from pytestqt.qtbot import QtBot

import mtg_proxy_printer.model
import mtg_proxy_printer.model.carddb
import mtg_proxy_printer.card_info_downloader
from mtg_proxy_printer.document_controller.save_document import ActionSaveDocument
from mtg_proxy_printer.model.document_loader import CardType
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.printing_filter_updater import PrintingFilterUpdater
from mtg_proxy_printer.units_and_sizes import CardDataType, StrDict, Quantity, CardSize
import mtg_proxy_printer.logger
import mtg_proxy_printer.settings
from mtg_proxy_printer.sqlite_helpers import read_resource_text, open_database


def _should_skip_network_tests() -> bool:
    result = os.getenv("MTGPROXYPRINTER_RUN_NETWORK_TESTS", "0")
    try:
        result = int(result)
    except ValueError:
        result = True
    else:
        result = bool(result)
    return not result


SHOULD_SKIP_NETWORK_TESTS = _should_skip_network_tests()
close_to_: Callable[[Real], Matcher[Real]] = functools.partial(close_to, delta=0.005)


def setup_logging_for_testing():
    with patch.dict(
            mtg_proxy_printer.logger.mtg_proxy_printer.settings.settings["debug"],
            {"write-log-file": "False"}):
        mtg_proxy_printer.logger.configure_root_logger(output_stdout=False)
    mtg_proxy_printer.logger.root_logger.info("Configured logging system for test runs.")
    mtg_proxy_printer.logger.root_logger.info(__name__)


def setup_settings_for_testing():
    # Make sure that the tests don’t overwrite the settings stored on disk. Raise an exception, should that occur.
    mtg_proxy_printer.settings.write_settings_to_file = MagicMock()
    mtg_proxy_printer.settings.write_settings_to_file.side_effect = AssertionError(
        "mtg_proxy_printer.settings.write_settings_to_file() called within test code!"
    )
    mtg_proxy_printer.settings.settings.read_dict(mtg_proxy_printer.settings.DEFAULT_SETTINGS)
    section = mtg_proxy_printer.settings.settings["card-filter"]
    for setting in section.keys():
        # Turn off all card filters, so that the defaults don’t affect the test cases
        section[setting] = str(False)


def populate_database(qtbot: QtBot, card_db: mtg_proxy_printer.model.carddb.CardDatabase, data, filter_settings: StrDict):
    # Explicitly share the in-memory database connection
    dw = mtg_proxy_printer.card_info_downloader.DatabaseImportWorker(card_db, card_db.db)
    section = mtg_proxy_printer.settings.settings["card-filter"]
    with qtbot.assertNotEmitted(dw.error_occurred), qtbot.assertNotEmitted(dw.network_error_occurred):
        settings_to_use = update_database_printing_filters(card_db, filter_settings)
        with patch.dict(section, settings_to_use):

            dw.populate_database(data)


def update_database_printing_filters(
        card_db: mtg_proxy_printer.model.carddb.CardDatabase, filter_settings: StrDict) -> StrDict:
    section = mtg_proxy_printer.settings.settings["card-filter"]
    settings_to_use = {filter_name: "False" for filter_name in section.keys()}
    if filter_settings:
        settings_to_use.update(filter_settings)
    section = mtg_proxy_printer.settings.settings["card-filter"]
    with patch.dict(section, settings_to_use):
        PrintingFilterUpdater(card_db, card_db.db, force_update_hidden_column=True).run()
    return settings_to_use


@functools.lru_cache()
def load_json(name: str) -> CardDataType:
    data = read_resource_text("tests.json_samples", f"{name}.json")
    return json.loads(data)


def load_multiple_json_cards(json_files_or_names: list[str | CardDataType]) -> list[CardDataType]:
    return [
        load_json(json_file_or_name) if isinstance(json_file_or_name, str) else json_file_or_name
        for json_file_or_name in json_files_or_names
    ]


def fill_card_database_with_json_cards(
        qtbot: QtBot,
        card_db: mtg_proxy_printer.model.carddb.CardDatabase,
        json_files_or_names: list[str | CardDataType],
        filter_settings: dict[str, str] = None) -> mtg_proxy_printer.model.carddb.CardDatabase:
    data = load_multiple_json_cards(json_files_or_names)
    populate_database(qtbot, card_db, data, filter_settings)
    return card_db


def fill_card_database_with_json_card(
        qtbot: QtBot,
        card_db: mtg_proxy_printer.model.carddb.CardDatabase,
        json_file_or_name: str | CardDataType,
        filter_settings: dict[str, str] = None) -> mtg_proxy_printer.model.carddb.CardDatabase:
    return fill_card_database_with_json_cards(qtbot, card_db, [json_file_or_name], filter_settings)


def create_save_database_with(
        path_or_connection: Path | Literal[":memory:"] | sqlite3.Connection,
        pages: list[tuple[int, CardSize]],
        cards: list[tuple[int, int, bool, str, CardType]],
        settings: PageLayoutSettings) -> sqlite3.Connection:
    save = path_or_connection if isinstance(path_or_connection, sqlite3.Connection) \
        else open_database(path_or_connection, "document-v7")
    ActionSaveDocument.save_settings(save, settings)
    save.executemany(
        "INSERT INTO Page (page, image_size) VALUES (?, ?)",
        pages
    )
    save.executemany(
        'INSERT INTO "Card" (page, slot, is_front, scryfall_id, type) VALUES (?, ?, ?, ?, ?)',
        cards
    )
    return save


def assert_relation_is_empty(card_db: mtg_proxy_printer.model.carddb.CardDatabase, name: str):
    assert_that(
        card_db.db.execute(f'SELECT * FROM "{name}"').fetchall(),
        is_(empty()), f"{name} contains unexpected data"
    )


def assert_model_is_empty(card_db: mtg_proxy_printer.model.carddb.CardDatabase, test_case=None):
    """
    Checks, if the model is empty. This is used by tests that check if cards are properly skipped based on
    download settings.
    If a test case data object is passed in, it is assumed that the printing it represents was excluded during the
    import. So also check that RemovedPrintings table contains the correct data.
    """
    relations_to_check = ["PrintLanguage", "Card", "FaceName", "CardFace", "MTGSet", "VisiblePrintings"]
    if test_case is None:
        relations_to_check.append("RemovedPrintings")
    else:
        assert_that(
            card_db.db.execute("SELECT scryfall_id, language, oracle_id FROM RemovedPrintings"),
            contains_inanyorder((test_case.scryfall_id, test_case.language, test_case.oracle_id))
        )
    for relation in relations_to_check:
        assert_relation_is_empty(card_db, relation)


class is_dataclass_equal_to(BaseMatcher):

    def __init__(self, expected: dataclasses.dataclass):
        self.expected = expected

    def _matches(self, item: dataclasses.dataclass) -> bool:
        return self._has_annotations(item) and self._has_equal_keys(item) and self._has_equal_values(item)

    @staticmethod
    def _has_annotations(item: dataclasses.dataclass):
        return hasattr(item, "__annotations__")

    def _has_equal_keys(self, item: dataclasses.dataclass) -> bool:
        return contains_inanyorder(
            *self.expected.__annotations__.keys()
        ).matches(item.__annotations__.keys())

    def _has_equal_values(self, item: dataclasses.dataclass) -> bool:
        return has_properties({
            key: equal_to(getattr(self.expected, key))
            for key in self.expected.__annotations__.keys()
        }).matches(item)

    def describe_to(self, description: Description) -> None:
        description.append_text(f"dataclass instance containing values equal to {self.expected} ")

    def describe_mismatch(self, item: dataclasses.dataclass, mismatch_description: Description) -> None:
        if not self._has_annotations(item):
            mismatch_description.append_text(f"{item} instance has no __annotations__ attribute")
            return
        if not self._has_equal_keys(item):
            expected_keys = set(self.expected.__annotations__.keys())
            got_keys = set(item.__annotations__.keys())
            if missing_keys := expected_keys-got_keys:
                mismatch_description.append_text(f"Missing attributes: {sorted(missing_keys)},")
            if excess_keys := got_keys-expected_keys:
                mismatch_description.append_text(f"Excess attributes: {sorted(excess_keys)},")
            return
        mismatched_values = {
            key: (expected, got)
            for key in self.expected.__annotations__.keys()
            if (expected := (getattr(self.expected, key))) != (got := getattr(item, key))
        }
        mismatch_description.append_text(
            f"Got unequal attributes: \n" +
            "\n  ".join(
                f"attribute={key}, {expected=}, {got=}"
                for key, (expected, got)
                in mismatched_values.items()
            )
        )


class matches_type_annotation(BaseMatcher):

    def _matches(self, item: dataclasses.dataclass) -> bool:
        return hasattr(item, "__annotations__") and has_properties({
                key: self._get_matcher(annotated_type)
                for key, annotated_type in item.__annotations__.items()
            }).matches(item)

    @staticmethod
    def _get_matcher(value: Any):
        if hasattr(value, "__args__"):  # Unpack typing.Optional[Something], typing.Union[TypeList]
            return any_of(*(instance_of(type_union_member) for type_union_member in value.__args__))
        return instance_of(value)

    def describe_to(self, description: Description) -> None:
        description.append_text(f"dataclass instance containing correct types")


def quantity_close_to(value: Quantity):
    return has_properties(units=equal_to(value.units), magnitude=close_to(value.magnitude, 0.001))


def number_between(lower: float, upper: float):
    return all_of(greater_than_or_equal_to(lower), less_than_or_equal_to(upper))


def quantity_between(lower: Quantity, upper: Quantity):
    assert_that(lower.units, equal_to(upper.units), "Setup failed. Bounds have different units!")
    return has_properties(
        units=equal_to(lower.units),
        magnitude=all_of(
            greater_than_or_equal_to(lower.magnitude),
            less_than_or_equal_to(upper.magnitude)
        )
    )
