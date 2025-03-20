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


import collections
import enum
import functools
import itertools
import pathlib
import sqlite3
import textwrap
import typing
from unittest.mock import patch

import pint
from PySide6.QtGui import QPageLayout, QPageSize
from PySide6.QtCore import QObject, Signal, QThreadPool, Qt
from hamcrest import assert_that, all_of, instance_of, greater_than_or_equal_to, matches_regexp, is_in, \
    has_properties, is_, any_of

try:
    from hamcrest import contains_exactly
except ImportError:
    # Compatibility with PyHamcrest < 1.10
    from hamcrest import contains as contains_exactly

import mtg_proxy_printer.settings
import mtg_proxy_printer.sqlite_helpers
from mtg_proxy_printer.model.carddb import CardIdentificationData, CardList, Card, CheckCard, AnyCardType, SCHEMA_NAME
from mtg_proxy_printer.model.imagedb import ImageDownloader
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.logger import get_logger
from mtg_proxy_printer.units_and_sizes import PageType, unit_registry, QuantityT
from mtg_proxy_printer.document_controller import DocumentAction
from mtg_proxy_printer.runner import Runnable
from mtg_proxy_printer.save_file_migrations import migrate_database

if typing.TYPE_CHECKING:
    from mtg_proxy_printer.model.document import Document
logger = get_logger(__name__)
del get_logger

__all__ = [
    "DocumentSaveFormat",
    "DocumentLoader",
    "CardType",
]

# ASCII encoded 'MTGP' for 'MTG proxies'. Stored in the Application ID file header field of the created save files
SAVE_FILE_MAGIC_NUMBER = 41325044


class CardType(str, enum.Enum):
    REGULAR = "r"
    CHECK_CARD = "d"

    @classmethod
    def from_card(cls, card: AnyCardType) -> "CardType":
        if isinstance(card, Card):
            return cls.REGULAR
        elif isinstance(card, CheckCard):
            return cls.CHECK_CARD
        else:
            raise NotImplementedError()


DocumentSaveFormat = typing.List[typing.Tuple[int, int, str, bool, CardType]]
T = typing.TypeVar("T")


def split_iterable(iterable: typing.Iterable[T], chunk_size: int, /) -> typing.Iterable[typing.Tuple[T, ...]]:
    """Split the given iterable into chunks of size chunk_size. Does not add padding values to the last item."""
    iterable = iter(iterable)
    return iter(lambda: tuple(itertools.islice(iterable, chunk_size)), ())


class LoaderSignals(QObject):
    """
    These Qt signals are used to communicate loading progress.
    They are shared by the API and backend classes.
    """
    finished = Signal()
    unknown_scryfall_ids_found = Signal(int, int)
    loading_file_failed = Signal(pathlib.Path, str)

    begin_loading_loop = Signal(int, str)
    progress_loading_loop = Signal(int)
    # Emitted when downloading required images during the loading process failed due to network issues.
    network_error_occurred = Signal(str)
    load_requested = Signal(DocumentAction)


class DocumentLoader(LoaderSignals):
    """
    Implements asynchronous background document loading.
    Loading a document can take a long time, if it includes downloading all card images and still takes a noticeable
    time when the card images have to be loaded from a slow hard disk.

    This class uses an internal worker to push that work off the GUI thread to keep the application
    responsive during a loading process.
    """

    loading_state_changed = Signal(bool)
    MIN_SUPPORTED_SQLITE_VERSION = (3, 31, 0)

    def __init__(self, document: "Document", db: sqlite3.Connection = None):  # db parameter used by test code
        super().__init__(None)
        self.document = document
        self.db = db
        self.finished.connect(functools.partial(self.loading_state_changed.emit, False), Qt.ConnectionType.DirectConnection)

    def load_document(self, save_file_path: pathlib.Path):
        logger.info(f"Loading document from {save_file_path}")
        self.loading_state_changed.emit(True)
        QThreadPool.globalInstance().start(LoaderRunner(save_file_path, self))

    def on_loading_file_successful(self, file_path: pathlib.Path):
        logger.info(f"Loading document from {file_path} successful.")
        self.document.save_file_path = file_path

    @staticmethod
    def cancel():
        for instance in LoaderRunner.INSTANCES:
            if isinstance(instance, LoaderRunner):
                instance.cancel()


class LoaderRunner(Runnable):
    def __init__(self, path: pathlib.Path, parent: DocumentLoader):
        super().__init__()
        self.parent = parent
        self.path = path
        self.worker = None

    def run(self):
        try:
            self.worker = self._create_worker()
            self.worker.load_document()
        finally:
            self.release_instance()

    def _create_worker(self):
        parent = self.parent
        worker = Worker(parent.document, self.path)
        if parent.db is not None:  # Used by tests to explicitly set the database
            worker._db = parent.db
        # The blocking connection causes the worker to wait for the document in the main thread to complete the loading
        worker.load_requested.connect(parent.load_requested, Qt.ConnectionType.BlockingQueuedConnection)
        worker.loading_file_failed.connect(parent.loading_file_failed)
        worker.unknown_scryfall_ids_found.connect(parent.unknown_scryfall_ids_found)
        worker.loading_file_successful.connect(parent.on_loading_file_successful)
        worker.network_error_occurred.connect(parent.network_error_occurred)
        worker.finished.connect(parent.finished)
        worker.begin_loading_loop.connect(parent.begin_loading_loop)
        worker.progress_loading_loop.connect(parent.progress_loading_loop)
        return worker

    def cancel(self):
        try:
            self.worker.cancel_running_operations()
        except AttributeError:
            pass


class Worker(LoaderSignals):
    """
    This worker creates ActionLoadDocument instances from saved documents.
    """
    loading_file_successful = Signal(pathlib.Path)

    def __init__(self, document: "Document", path: pathlib.Path):
        super().__init__(None)
        self.document = document
        self.save_path = path
        self.card_db = document.card_db
        self.image_db = image_db = document.image_db
        self._db: sqlite3.Connection = None
        # Create our own ImageDownloader, instead of using the ImageDownloader embedded in the ImageDatabase.
        # That one lives in its own thread and runs asynchronously and is thus unusable for loading documents.
        # So create a separate instance and use it synchronously inside this worker thread.
        self.image_loader = ImageDownloader(image_db, self)
        self.image_loader.download_begins.connect(image_db.card_download_starting)
        self.image_loader.download_finished.connect(image_db.card_download_finished)
        self.image_loader.download_progress.connect(image_db.card_download_progress)
        self.image_loader.network_error_occurred.connect(self.on_network_error_occurred)
        self.network_errors_during_load: typing.Counter[str] = collections.Counter()
        self.finished.connect(self.propagate_errors_during_load)
        self.should_run: bool = True
        self.unknown_ids = 0
        self.migrated_ids = 0

    @property
    def db(self) -> sqlite3.Connection:
        # Delay connection creation until first access.
        # Avoids opening connections that aren't actually used and opens the connection
        # in the thread that actually uses it.
        if self._db is None:
            self._db = mtg_proxy_printer.sqlite_helpers.open_database(
                self.card_db.db_path, SCHEMA_NAME, self.card_db.MIN_SUPPORTED_SQLITE_VERSION)
        return self._db

    def propagate_errors_during_load(self):
        if error_count := sum(self.network_errors_during_load.values()):
            logger.warning(f"{error_count} errors occurred during document load, reporting to the user")
            self.network_error_occurred.emit(
                f"Some cards may be missing images, proceed with caution.\n"
                f"Error count: {error_count}. Most common error message:\n"
                f"{self.network_errors_during_load.most_common(1)[0][0]}"
            )
            self.network_errors_during_load.clear()
        else:
            logger.info("No errors occurred during document load")

    def on_network_error_occurred(self, error: str):
        self.network_errors_during_load[error] += 1

    def load_document(self):
        self.should_run = True
        try:
            self._load_document()
        except (AssertionError, sqlite3.DatabaseError) as e:
            logger.exception(
                "Selected file is not a known MTGProxyPrinter document or contains invalid data. Not loading it.")
            self.loading_file_failed.emit(self.save_path, str(e))
            self.finished.emit()
        finally:
            self.db.close()
            self._db = None

    def _complete_loading(self):
        if self.unknown_ids or self.migrated_ids:
            self.unknown_scryfall_ids_found.emit(self.unknown_ids, self.migrated_ids)
            self.unknown_ids = self.migrated_ids = 0
        self.loading_file_successful.emit(self.save_path)
        self.finished.emit()

    def _load_document(self):
        # Imported here to break a circular import. TODO: Investigate a better fix
        from mtg_proxy_printer.document_controller.load_document import ActionLoadDocument
        card_data, page_settings = self._read_data_from_save_path(self.save_path, self.document.page_layout)
        with patch.object(self.card_db, "db", self.db):
            pages, self.migrated_ids, self.unknown_ids = self._parse_into_cards(card_data)
        self._fix_mixed_pages(pages, page_settings)
        action = ActionLoadDocument(self.save_path, pages, page_settings)
        self.load_requested.emit(action)
        self._complete_loading()

    def _parse_into_cards(self, card_data: DocumentSaveFormat) -> (typing.List[CardList], int, int):
        prefer_already_downloaded = mtg_proxy_printer.settings.settings["decklist-import"].getboolean(
            "prefer-already-downloaded-images")

        current_page_index = 1
        unknown_ids = 0
        migrated_ids = 0
        pages: typing.List[CardList] = [[]]
        current_page = pages[-1]
        self.begin_loading_loop.emit(len(card_data), "Loading document:")
        for item_number, (page_number, slot, scryfall_id, is_front, card_type) in enumerate(card_data):
            self.progress_loading_loop.emit(item_number)  # Emit at loop begin, so that each item advances the progress
            if not self.should_run:
                logger.info("Cancel request received, stop processing the card list.")
                return pages, unknown_ids, migrated_ids
            if current_page_index != page_number:
                current_page_index = page_number
                current_page: CardList = []
                pages.append(current_page)
            if card_type == CardType.CHECK_CARD:
                if not self.card_db.is_dfc(scryfall_id):
                    logger.warning("Requested loading check card for non-DFC card, skipping it.")
                    self.unknown_ids += 1
                    continue
                card = CheckCard(
                    self.card_db.get_card_with_scryfall_id(scryfall_id, True),
                    self.card_db.get_card_with_scryfall_id(scryfall_id, False)
                )
            else:
                card = self.card_db.get_card_with_scryfall_id(scryfall_id, is_front)
            if card is None:
                card = self._find_replacement_card(scryfall_id, is_front, prefer_already_downloaded)
                if card:
                    migrated_ids += 1
                else:
                    # If the save file was tampered with or the database used to save contained more cards than the
                    # currently used one, the save may contain unknown Scryfall IDs. So skip all unknown data.
                    unknown_ids += 1
                    logger.info("Unable to find suitable replacement card. Skipping it.")
                    continue
            self.image_loader.get_image_synchronous(card)
            current_page.append(card)
        self.progress_loading_loop.emit(len(card_data))
        return pages, migrated_ids, unknown_ids

    def _find_replacement_card(self, scryfall_id: str, is_front: bool, prefer_already_downloaded: bool):
        logger.info(f"Unknown card scryfall ID found in document:  {scryfall_id=}, {is_front=}")
        card = None
        identification_data = CardIdentificationData(scryfall_id=scryfall_id, is_front=is_front)
        choices = self.card_db.get_replacement_card_for_unknown_printing(
            identification_data, order_by_print_count=prefer_already_downloaded)
        if choices:
            filtered_choices = []
            if prefer_already_downloaded:
                filtered_choices = self.image_db.filter_already_downloaded(choices)
            card = filtered_choices[0] if filtered_choices else choices[0]
            logger.info(f"Found suitable replacement card: {card}")
        return card

    def _fix_mixed_pages(self, pages: typing.List[CardList], page_settings: PageLayoutSettings):
        """
        Documents saved with older versions (or specifically crafted save files) can contain images with mixed
        sizes on the same page.
        This method is called when the document loading finishes and moves cards away from these mixed pages so that
        all pages only contain a single image size.
        """
        mixed_pages = list(filter(self._is_mixed_page, pages))
        logger.info(f"Fixing {len(mixed_pages)} mixed pages by moving cards away")
        regular_cards_to_distribute: CardList = []
        oversized_cards_to_distribute: CardList = []
        for page in mixed_pages:
            regular_rows = []
            oversized_rows = []
            for row, card in enumerate(page):
                if card.requested_page_type() == PageType.REGULAR:
                    regular_rows.append(row)
                else:
                    oversized_rows.append(row)
            card_rows_to_move, target_list = (regular_rows, regular_cards_to_distribute) \
                if len(regular_rows) < len(oversized_rows) \
                else (oversized_rows, oversized_cards_to_distribute)
            card_rows_to_move.reverse()
            for row in card_rows_to_move:
                target_list.append(page[row])
                del page[row]
        if regular_cards_to_distribute:
            logger.debug(f"Moving {len(regular_cards_to_distribute)} regular cards from mixed pages")
            pages += split_iterable(
                regular_cards_to_distribute, page_settings.compute_page_card_capacity(PageType.REGULAR))
        if oversized_cards_to_distribute:
            logger.debug(f"Moving {len(oversized_cards_to_distribute)} oversized cards from mixed pages")
            pages += split_iterable(
                oversized_cards_to_distribute, page_settings.compute_page_card_capacity(PageType.OVERSIZED)
            )

    @staticmethod
    def _is_mixed_page(page: CardList) -> bool:
        return len(set(card.requested_page_type() for card in page)) > 1

    @staticmethod
    def _read_data_from_save_path(save_file_path: pathlib.Path, settings: PageLayoutSettings):
        """
        Reads the data from disk into a list.

        :raises AssertionError: If the save file structure is invalid or contains invalid data.
        """
        logger.info(f"Reading data from save file {save_file_path}")

        with mtg_proxy_printer.sqlite_helpers.open_database(
                save_file_path, "document-v6", DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION) as db:
            user_version = Worker._validate_database_schema(db)
            if user_version not in range(2, 7):
                raise AssertionError(f"Unknown database schema version: {user_version}")
            logger.info(f"Save file version is {user_version}")
            migrate_database(db, settings)
            card_data = Worker._read_card_data_from_database(db)
            settings = Worker._read_page_layout_data_from_database(db, user_version)
        return card_data, settings

    @staticmethod
    def _read_card_data_from_database(db: sqlite3.Connection) -> DocumentSaveFormat:
        card_data: DocumentSaveFormat = []
        query = textwrap.dedent("""\
            SELECT page, slot, scryfall_id, is_front, type
                FROM Card
                ORDER BY page ASC, slot ASC""")
        supported_card_types: typing.List[str] = list(item.value for item in CardType)
        for row_number, row_data in enumerate(db.execute(query)):
            assert_that(row_data, contains_exactly(
                all_of(instance_of(int), greater_than_or_equal_to(0)),
                all_of(instance_of(int), greater_than_or_equal_to(0)),
                all_of(instance_of(str), matches_regexp(r"[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}")),
                is_in((0, 1)),
                is_in(supported_card_types)
            ), f"Invalid data found in the save data at row {row_number}. Aborting")
            page, slot, scryfall_id, is_front, card_type = row_data
            card_data.append((page, slot, scryfall_id, bool(is_front), CardType(card_type)))
        return card_data

    @staticmethod
    def _read_page_layout_data_from_database(db, user_version):
        default_settings = PageLayoutSettings.create_from_settings()
        if user_version >= 4:
            settings = Worker._read_document_settings(db, default_settings)
        else:
            settings = default_settings
        logger.debug(f"Loaded document settings: {settings}")
        return settings

    @staticmethod
    def _read_document_settings(
            db: sqlite3.Connection, default_settings: PageLayoutSettings) -> PageLayoutSettings:
        logger.debug("Reading document settings …")
        keys = ", ".join(map("'{}'".format, default_settings.__annotations__.keys()))
        document_settings_query = textwrap.dedent(f"""\
            SELECT key, value
                FROM DocumentSettings
                WHERE key in ({keys})
                ORDER BY key ASC
            """)
        default_settings.update(db.execute(document_settings_query))
        is_number = any_of(instance_of(float), instance_of(int), instance_of(pint.Quantity))
        assert_that(
            default_settings,
            has_properties(
                card_bleed=is_number,
                page_height=is_number,
                page_width=is_number,
                margin_top=is_number,
                margin_bottom=is_number,
                margin_left=is_number,
                margin_right=is_number,
                row_spacing=is_number,
                column_spacing=is_number,
                draw_cut_markers=is_in((0, 1)),
                draw_sharp_corners=is_in((0, 1)),
                draw_page_numbers=is_in((0, 1)),
                # TODO: Values column should have TEXT affinity, in order to preserve numerical-looking titles as-is
                document_name=(any_of(instance_of(str), instance_of(int))),
            ),
            "Document settings contain invalid data or data types"
        )
        # Numerical column affinity coerces document titles like "1" to integers, so convert to str in those cases.
        # This does lose leading zeros and zero decimals (e.g. "1.000", however.
        # Also coerce integer values into the annotated float or boolean types
        for key, annotated_type in PageLayoutSettings.__annotations__.items():
            value = getattr(default_settings, key)
            if annotated_type is bool:
                value = annotated_type(value)
            elif annotated_type is QuantityT and not isinstance(value, pint.Quantity):
                # TODO: Currently implicitly interpreting values as millimeters. Replace this with save version 7.
                # Ensure all floats are within the allowed bounds.
                value = mtg_proxy_printer.settings.clamp_to_supported_range(
                    value*unit_registry.mm, mtg_proxy_printer.settings.MIN_SIZE, mtg_proxy_printer.settings.MAX_SIZE)
            elif annotated_type is str:
                 value = annotated_type(value)
            setattr(default_settings, key, value)
        assert_that(
            default_settings.compute_page_card_capacity(),
            is_(greater_than_or_equal_to(1)),
            "Document settings invalid: At least one card has to fit on a page."
        )
        return default_settings

    @staticmethod
    def _validate_database_schema(db_unsafe: sqlite3.Connection) -> int:
        user_schema_version = db_unsafe.execute("PRAGMA user_version").fetchone()[0]
        return mtg_proxy_printer.sqlite_helpers.validate_database_schema(
            db_unsafe, SAVE_FILE_MAGIC_NUMBER, f"document-v{user_schema_version}",
            DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION,
            "Application ID mismatch. Not an MTGProxyPrinter save file!",
        )

    def cancel_running_operations(self):
        self.should_run = False
        if self.image_loader.currently_opened_file is not None:
            # Force aborting the download by closing the input stream
            self.image_loader.currently_opened_file.close()
