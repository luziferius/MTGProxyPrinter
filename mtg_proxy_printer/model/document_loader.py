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
from typing import Counter, Dict, Generator, Iterable, List, NamedTuple, Optional, Tuple, TYPE_CHECKING, TypeVar
from unittest.mock import patch

import pint
from PyQt5.QtCore import QObject, pyqtSignal as Signal, QThreadPool, Qt
from hamcrest import assert_that, all_of, instance_of, greater_than_or_equal_to, matches_regexp, is_in, \
    has_properties, is_


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
from mtg_proxy_printer.units_and_sizes import PageType, QuantityT, UUID
from mtg_proxy_printer.document_controller import DocumentAction
from mtg_proxy_printer.runner import Runnable
from mtg_proxy_printer.save_file_migrations import migrate_database

if TYPE_CHECKING:
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


class DatabaseLoadResult(NamedTuple):
    card: AnyCardType
    was_migrated: bool


class DocumentSaveRow(NamedTuple):
    page: int
    slot: int
    is_front: bool
    card_type: CardType
    scryfall_id: UUID
    custom_card_id: UUID


DocumentSaveFormat = List[DocumentSaveRow]
T = TypeVar("T")


def split_iterable(iterable: Iterable[T], chunk_size: int, /) -> Iterable[Tuple[T, ...]]:
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
        disable_loading_state_on_completion = functools.partial(self.loading_state_changed.emit, False)
        self.finished.connect(disable_loading_state_on_completion, Qt.ConnectionType.DirectConnection)

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
        self.network_errors_during_load: Counter[str] = collections.Counter()
        self.finished.connect(self.propagate_errors_during_load)
        self.should_run: bool = True
        self.unknown_ids = 0
        self.migrated_ids = 0
        self.current_progress = 0
        self.prefer_already_downloaded = mtg_proxy_printer.settings.settings["decklist-import"].getboolean(
            "prefer-already-downloaded-images")

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
        with patch.object(self.card_db, "db", self.db):
            save_db = self._open_validate_and_migrate_save_file(self.save_path)
            total_steps = 2 + save_db.execute("SELECT count(1) FROM Card").fetchone()[0]
            self.begin_loading_loop.emit(total_steps, "Loading document:")
            page_layout = self._load_document_settings(save_db)
            self._advance_progress()
            pages = self._load_cards(save_db)
            self._fix_mixed_pages(pages, page_layout)
            self._advance_progress()
        action = ActionLoadDocument(self.save_path, pages, page_layout)
        self.load_requested.emit(action)
        self._complete_loading()

    def _advance_progress(self):
        self.current_progress += 1
        self.progress_loading_loop.emit(self.current_progress)

    @staticmethod
    def _open_validate_and_migrate_save_file(save_path: pathlib.Path) -> sqlite3.Connection:
        """
        Opens the save database, validates the schema and migrates the content to the newest
        save file version.

        :param save_path: File system path to open
        :return: The opened database connection."""
        db = mtg_proxy_printer.sqlite_helpers.open_database(
            save_path, f"document-v7", DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION
        )
        user_version = Worker._validate_database_schema(db)
        if user_version not in range(2, 8):
            raise AssertionError(f"Unknown database schema version: {user_version}")
        logger.info(f"Save file version is {user_version}")
        migrate_database(db, PageLayoutSettings.create_from_settings())
        return db


    def _load_cards(self, save_db: sqlite3.Connection) -> List[CardList]:
        custom_cards: Dict[str, Card] = {}
        total_cards = save_db.execute("SELECT count(1) FROM Card").fetchone()[0]
        self.begin_loading_loop.emit(total_cards, "Loading document:")
        rows = self._load_rows(save_db)
        pages = self._split_into_pages(rows)
        return list(map(self._load_cards_on_page, pages, itertools.repeat(custom_cards)))

    @staticmethod
    def _load_rows(save_db: sqlite3.Connection) -> Generator[DocumentSaveRow, None, None]:
        query = textwrap.dedent("""\
            SELECT page, slot, is_front, type, scryfall_id, custom_card_id -- _load_rows()
                FROM Card
                ORDER BY page ASC, slot ASC""")
        return (
            DocumentSaveRow(page, slot, bool(is_front), CardType(card_type), scryfall_id, custom_card_id)
            for page, slot, is_front, card_type, scryfall_id, custom_card_id
            in save_db.execute(query))

    @staticmethod
    def _split_into_pages(rows: Iterable[DocumentSaveRow]) -> Generator[List[DocumentSaveRow], None, None]:
        page = []
        previous = -1
        for row in rows:
            if row.page != previous:
                if page:
                    yield page
                page = []
            page.append(row)
        yield page

    def _load_cards_on_page(self, page: List[DocumentSaveRow], custom_cards: Dict[str, Card]) -> CardList:
        card_db = self.card_db
        result: CardList = []
        for item in page:
            if card_id := item.custom_card_id:
                if card_id in custom_cards:
                    result.append(custom_cards[card_id])
                else:
                    card = self._load_custom_card_from_save(item)
                    if card.image_file:
                        result.append(card)
                        custom_cards[card_id] = card
            elif card_id := item.scryfall_id:
                result.append(self._load_official_card_from_card_db(item, self.prefer_already_downloaded))
            else:
                # Empty slot.

                pass
            self._advance_progress()
        return result

    def _load_official_card_from_card_db(self, data: DocumentSaveRow, prefer_already_downloaded: bool) -> Optional[DatabaseLoadResult]:
        if data.card_type == CardType.CHECK_CARD:
            return self._load_check_card(data, prefer_already_downloaded)
        else:
            return self._load_official_card(data, prefer_already_downloaded)

    def _load_check_card(self, data: DocumentSaveRow, prefer_already_downloaded: bool) -> Optional[DatabaseLoadResult]:
        """
        Loads a check card. Retuns None if the given scryfall id does not belong to a DFC.
        If the front is unavailable, try to find a replacement.
        Returns None, if the back of the found replacement is unavailable.
        """
        migrated = False
        scryfall_id = data.data.scryfall_id
        if not self.card_db.is_dfc(scryfall_id):
            logger.warning("Requested loading check card for non-DFC card, skipping it.")
            return None
        front = self.card_db.get_card_with_scryfall_id(scryfall_id, True)
        if front is None:
            front = self._find_replacement_card(scryfall_id, True, prefer_already_downloaded)
            if front is None:
                logger.info("Unable to find suitable replacement card. Skipping it.")
                return None
            migrated = True
        back = self.card_db.get_card_with_scryfall_id(front.scryfall_id, False)
        if back is None:
            logger.info("Unable to find suitable replacement card. Skipping it.")
            return None
        card = CheckCard(front, back)
        self.image_loader.get_image_synchronous(card)
        return DatabaseLoadResult(card, migrated)

    def _load_official_card(self, data: DocumentSaveRow, prefer_already_downloaded: bool) -> Optional[DatabaseLoadResult]:
        migrated = False
        scryfall_id = data.data.scryfall_id
        is_front = data.data.is_front
        if (card := self.card_db.get_card_with_scryfall_id(data.data.scryfall_id, is_front)) is None:
            card = self._find_replacement_card(scryfall_id, is_front, prefer_already_downloaded)
            migrated = True
        if card is None:
            logger.info("Unable to find suitable replacement card. Skipping it.")
            return None
        self.image_loader.get_image_synchronous(card)
        return DatabaseLoadResult(card, migrated)

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

    def _fix_mixed_pages(self, pages: List[CardList], page_settings: PageLayoutSettings):
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
                save_file_path, "document-v7", DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION) as db:
            user_version = Worker._validate_database_schema(db)
            if user_version not in range(2, 8):
                raise AssertionError(f"Unknown database schema version: {user_version}")
            logger.info(f"Save file version is {user_version}")
            migrate_database(db, settings)
            card_data = Worker._read_card_data_from_database(db)
            settings = Worker._read_page_layout_data_from_database(db, user_version)
        return card_data, settings

    @staticmethod
    def _read_card_data_from_database(db: sqlite3.Connection) -> DocumentSaveFormat:
        result: DocumentSaveFormat = []
        # TODO: Ignore custom cards for now
        query = textwrap.dedent("""\
            SELECT page, slot, scryfall_id, is_front, type, custom_card_id
                FROM Card
                WHERE scryfall_id IS NOT NULL
                ORDER BY page ASC, slot ASC""")
        supported_card_types: List[str] = list(item.value for item in CardType)
        for row_number, row_data in enumerate(db.execute(query)):
            if row_data[2] is not None:
                result.append(Worker._append_official_card(row_data, row_number, supported_card_types))
            else:
                pass
        return result

    @staticmethod
    def _append_official_card(row_data, row_number, supported_card_types) -> DocumentSaveRow:
        assert_that(row_data, contains_exactly(
            all_of(instance_of(int), greater_than_or_equal_to(0)),
            all_of(instance_of(int), greater_than_or_equal_to(0)),
            matches_regexp(r"[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}"),
            is_in((0, 1)),
            is_in(supported_card_types)
        ), f"Invalid data found in the save data at row {row_number}. Aborting")
        page, slot, scryfall_id, is_front, card_type = row_data
        return DocumentSaveRow(
            page, slot, CardType(card_type),
            CardIdentificationData(scryfall_id=scryfall_id, is_front=is_front))

    @staticmethod
    def _load_document_settings(db: sqlite3.Connection) -> PageLayoutSettings:
        settings = PageLayoutSettings.create_from_settings()
        logger.debug("Reading document settings …")
        keys =  ", ".join(
            f"'{key}'" for key, value in settings.__annotations__.items() if value is not QuantityT)
        document_settings_query = textwrap.dedent(f"""\
            SELECT "key", value
                FROM DocumentSettings
                WHERE "key" in ({keys})
            """)
        settings.update(db.execute(document_settings_query))
        keys = ", ".join(
            f"'{key}'" for key, value in settings.__annotations__.items() if value is QuantityT)
        document_dimensions_query = textwrap.dedent(f"""\
            SELECT "key", value
                FROM DocumentDimensions
                WHERE "key" in ({keys})
            """)
        settings.update(db.execute(document_dimensions_query))
        is_number = instance_of(pint.Quantity)
        assert_that(
            settings,
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
                draw_cut_markers=is_in(("True", "False")),
                draw_sharp_corners=is_in(("True", "False")),
                draw_page_numbers=is_in(("True", "False")),
                document_name=instance_of(str),
            ),
            "Document settings contain invalid data or data types"
        )

        for key, annotated_type in PageLayoutSettings.__annotations__.items():
            value = getattr(settings, key)
            if annotated_type is bool:
                value = mtg_proxy_printer.settings.settings._convert_to_boolean(value)
            elif annotated_type is QuantityT:
                # TODO: Handle invalid, non-length units
                # Ensure all floats are within the allowed bounds.
                value = mtg_proxy_printer.settings.clamp_to_supported_range(
                    value, mtg_proxy_printer.settings.MIN_SIZE, mtg_proxy_printer.settings.MAX_SIZE)
            elif annotated_type is str:
                 pass
            setattr(settings, key, value)
        assert_that(
            settings.compute_page_card_capacity(),
            is_(greater_than_or_equal_to(1)),
            "Document settings invalid: At least one card has to fit on a page."
        )
        return settings

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
