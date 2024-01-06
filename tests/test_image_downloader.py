# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from io import BytesIO
import socket
import urllib.error
from unittest.mock import patch, MagicMock

import pytest
from hamcrest import *
from pytestqt.qtbot import QtBot

from mtg_proxy_printer.document_controller.card_actions import ActionAddCard
from mtg_proxy_printer.document_controller.replace_card import ActionReplaceCard
from mtg_proxy_printer.document_controller.import_deck_list import ActionImportDeckList
from mtg_proxy_printer.model.carddb import Card, MTGSet
from mtg_proxy_printer.model.imagedb import ImageDatabase, ImageKey, ImageDownloader
from .test_image_db import qpixmap_to_bytes_io

CARD_IN_CACHE = ImageKey("scryfall_id", True, True)


def create_card_in_cache() -> Card:
    return Card(
        "", MTGSet("", ""), "", "",
        CARD_IN_CACHE.scryfall_id, CARD_IN_CACHE.is_front, "", "", CARD_IN_CACHE.is_high_resolution,
        False, 1, None
    )


def create_card_not_in_cache() -> Card:
    return Card(
        "", MTGSet("", ""), "", "",
        CARD_IN_CACHE.scryfall_id, not CARD_IN_CACHE.is_front, "", "", CARD_IN_CACHE.is_high_resolution,
        False, 1, None
    )


@pytest.fixture()
def image_downloader(image_db: ImageDatabase):
    downloader = ImageDownloader(image_db)
    image_db.loaded_images[CARD_IN_CACHE] = image_db.blank_image
    yield downloader


@pytest.mark.parametrize("action", [
    ActionAddCard(create_card_in_cache()),
    ActionReplaceCard(create_card_in_cache(), 1, 1),
])
def test_fill_document_action_image_with_cached_image(qtbot: QtBot, image_downloader, action):
    with qtbot.wait_signal(image_downloader.request_action), \
            patch.object(image_downloader, "_download_from_scryfall") as _download_from_scryfall:
        image_downloader.fill_document_action_image(action)
    _download_from_scryfall.assert_not_called()
    assert_that(
        action.card.image_file,
        is_(same_instance(image_downloader.image_database.blank_image))
    )


@pytest.mark.parametrize("action", [
    ActionAddCard(create_card_not_in_cache()),
    ActionReplaceCard(create_card_not_in_cache(), 1, 1),
])
def test_fill_document_action_image_with_not_yet_fetched_image(qtbot: QtBot, image_downloader, action):
    blank = image_downloader.image_database.blank_image
    card = action.card
    image_key = ImageKey(card.scryfall_id, card.is_front, card.highres_image)
    blank_file = qpixmap_to_bytes_io(blank)
    expected_signals = [image_downloader.request_action, image_downloader.download_finished]
    with qtbot.wait_signals(expected_signals), \
            patch.object(
                image_downloader, "read_from_url", return_value=(blank_file, MagicMock())) as read_from_url:
        image_downloader.fill_document_action_image(action)
    read_from_url.assert_called_once()
    ''' # Can't easily compare QPixmap instances in PyQt5
    assert_that(
        action.card.image_file,
        is_(equal_to(blank))
    )
    '''
    assert_that(
        image_downloader.image_database.loaded_images,
        has_key(image_key)
    )
    assert_that(
        image_downloader.image_database.images_on_disk,
        has_item(image_key)
    )


@pytest.mark.parametrize("action", [
    ActionImportDeckList([create_card_in_cache(), create_card_in_cache()], False),
])
def test_fill_batch_document_action_image_with_cached_image(qtbot: QtBot, image_downloader, action):
    blank = image_downloader.image_database.blank_image
    expected_signals = [image_downloader.batch_processing_state_changed] * 2 + [
        image_downloader.download_finished, image_downloader.request_action]
    with qtbot.wait_signals(expected_signals), \
            patch.object(image_downloader, "_download_from_scryfall") as _download_from_scryfall:
        image_downloader.fill_batch_document_action_images(action)
    _download_from_scryfall.assert_not_called()
    assert_that(
        action.cards,
        contains_exactly(
            *[has_property("image_file", is_(same_instance(blank)))]*len(action.cards),
        )
    )


@pytest.mark.parametrize("action", [
    ActionImportDeckList([create_card_not_in_cache(), create_card_not_in_cache()], False),
])
def test_fill_batch_document_action_image_with_not_yet_fetched_image(qtbot: QtBot, image_downloader, action):
    card = action.cards[0]
    image_key = ImageKey(card.scryfall_id, card.is_front, card.highres_image)
    blank = image_downloader.image_database.blank_image
    blank_file = qpixmap_to_bytes_io(blank)
    expected_signals = [image_downloader.batch_processing_state_changed]*2 + [
        image_downloader.download_finished, image_downloader.request_action]
    with qtbot.wait_signals(expected_signals), \
            patch.object(
                image_downloader, "read_from_url", return_value=(blank_file, MagicMock())) as read_from_url:
        image_downloader.fill_batch_document_action_images(action)
    read_from_url.assert_called_once()
    ''' # Can't easily compare QPixmap instances in PyQt5
    assert_that(
        action.cards,
        contains_exactly(
            *[has_property("image_file", is_(equal_to(blank)))]*len(action.cards),
        )
    )
    '''
    assert_that(
        image_downloader.image_database.loaded_images,
        has_key(image_key)
    )
    assert_that(
        image_downloader.image_database.images_on_disk,
        has_item(image_key)
    )


def test_obtain_missing_images(qtbot, image_downloader, document_light):
    card1, card2 = create_card_not_in_cache(), create_card_not_in_cache()
    card1.image_file = card2.image_file = blank = image_downloader.image_database.blank_image
    new_image = blank.copy()
    ActionAddCard(card1).apply(document_light)
    ActionAddCard(card2).apply(document_light)
    page_index = document_light.index(0, 0)
    card_indices = [document_light.index(0, 0, page_index), document_light.index(1, 0, page_index)]
    expected_signals = [image_downloader.batch_processing_state_changed]*2 + [image_downloader.download_finished]
    with qtbot.wait_signals(expected_signals), \
            patch.object(image_downloader, "_download_from_scryfall", return_value=new_image) as _download_from_scryfall:
        image_downloader.obtain_missing_images(card_indices)
    assert_that(
        document_light.pages[0],
        contains_exactly(
            *[has_property("card", has_property("image_file", is_(same_instance(new_image))))]*len(card_indices),
        )
    )
    assert_that(image_downloader.last_error_message, is_(empty()))


@pytest.mark.parametrize("action", [
    ActionAddCard(create_card_not_in_cache()),
    ActionReplaceCard(create_card_not_in_cache(), 1, 1),
])
@pytest.mark.parametrize("exception_class, reason", [
    (urllib.error.URLError, "Test reason"),
    (socket.timeout, "Test error"),
])
def test_error_during_single_download_relays_error_message(qtbot, image_downloader, action, exception_class, reason):
    blank = image_downloader.image_database.blank_image
    exception = exception_class(reason)
    with patch.object(image_downloader, "_download_from_scryfall", side_effect=exception), \
            qtbot.wait_signal(image_downloader.network_error_occurred, check_params_cb=lambda param: reason in param), \
            qtbot.wait_signal(image_downloader.download_finished):
        image_downloader.fill_document_action_image(action)
    assert_that(
        action.card.image_file,
        is_(same_instance(blank)),
    )
    assert_that(image_downloader.last_error_message, is_(empty()))


@pytest.mark.parametrize("action", [
    ActionImportDeckList([create_card_not_in_cache(), create_card_not_in_cache()], False),
])
@pytest.mark.parametrize("exception_class, reason", [
    (urllib.error.URLError, "Test reason"),
    (socket.timeout, "Test error"),
])
def test_error_during_batch_process_relays_error_message(qtbot, image_downloader, action, exception_class, reason):
    blank = image_downloader.image_database.blank_image
    exception = exception_class(reason)
    with patch.object(image_downloader, "_download_from_scryfall", side_effect=exception), \
            qtbot.wait_signal(image_downloader.network_error_occurred, check_params_cb=lambda param: reason in param), \
            qtbot.wait_signal(image_downloader.download_finished):
        image_downloader.fill_batch_document_action_images(action)
    assert_that(
        action.cards,
        contains_exactly(
            *[has_property("image_file", is_(same_instance(blank)))] * len(action.cards),
        )
    )
    assert_that(image_downloader.last_error_message, is_(empty()))


@pytest.mark.parametrize("exception_class, reason", [
    (urllib.error.URLError, "Test reason"),
    (socket.timeout, "Test error"),
])
def test_obtain_missing_images_handles_network_error(qtbot, image_downloader, document_light, exception_class, reason):
    exception = exception_class(reason)
    card1, card2 = create_card_not_in_cache(), create_card_not_in_cache()
    card1.image_file = card2.image_file = blank = image_downloader.image_database.blank_image
    ActionAddCard(card1).apply(document_light)
    ActionAddCard(card2).apply(document_light)
    page_index = document_light.index(0, 0)
    card_indices = [document_light.index(0, 0, page_index), document_light.index(1, 0, page_index)]
    expected_signals = [image_downloader.batch_processing_state_changed]*2 + [
        image_downloader.network_error_occurred, image_downloader.missing_images_obtained,
        image_downloader.download_finished]
    with qtbot.wait_signals(expected_signals), \
            patch.object(image_downloader, "_download_from_scryfall", side_effect=exception):
        image_downloader.obtain_missing_images(card_indices)
    assert_that(
        document_light.pages[0],
        contains_exactly(
            *[has_property("card", has_property("image_file", is_(same_instance(blank))))]*len(card_indices),
        )
    )
    assert_that(image_downloader.last_error_message, is_(empty()))


def test__download_image_from_scryfall_moves_successful_downloaded_image_to_storage(qtbot, image_downloader):
    image_downloader.should_run = True
    card = create_card_not_in_cache()
    download_source_mock = MagicMock()
    temp_file_path = image_downloader.image_database.db_path / f"{card.scryfall_id}.png"
    target_file_path = MagicMock()
    with patch("mtg_proxy_printer.model.imagedb.shutil.copyfileobj",) as copy_mock, \
            patch("mtg_proxy_printer.model.imagedb.shutil.move") as move_mock, \
            patch.object(image_downloader.image_database, "db_path") as db_path_mock, \
            patch.object(image_downloader, "read_from_url", return_value=(download_source_mock, MagicMock())):
        image_downloader._download_from_scryfall(card, target_file_path)
    copy_mock.assert_called_once_with(download_source_mock, (db_path_mock/temp_file_path).open().__enter__())
    move_mock.assert_called_once_with(db_path_mock/temp_file_path, target_file_path)


@pytest.mark.parametrize("error", [socket.timeout("Test reason"), urllib.error.URLError("Test reason")])
def test__download_image_from_scryfall_does_not_move_image_to_storage_on_download_failure(
        qtbot, image_downloader, error):
    image_downloader.should_run = True
    card = create_card_not_in_cache()
    download_source_mock = MagicMock()
    temp_file_path = image_downloader.image_database.db_path / f"{card.scryfall_id}.png"
    target_file_path = MagicMock()
    with patch("mtg_proxy_printer.model.imagedb.shutil.copyfileobj", side_effect=error) as copy_mock, \
            patch("mtg_proxy_printer.model.imagedb.shutil.move") as move_mock, \
            patch("mtg_proxy_printer.model.imagedb.logger.exception") as logger_mock, \
            patch.object(image_downloader.image_database, "db_path") as db_path_mock, \
            patch.object(image_downloader, "read_from_url", return_value=(download_source_mock, MagicMock())):
        image_downloader._download_from_scryfall(card, target_file_path)
    copy_mock.assert_called_once_with(download_source_mock, (db_path_mock/temp_file_path).open().__enter__())
    move_mock.assert_not_called()
    logger_mock.assert_called_once()
