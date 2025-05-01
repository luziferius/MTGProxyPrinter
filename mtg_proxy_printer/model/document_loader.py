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
from typing import Counter, Dict, Iterable, List, NamedTuple, Optional, Tuple, TYPE_CHECKING, TypeVar

import pint
from PyQt5.QtCore import QObject, pyqtSignal as Signal, QThreadPool, Qt
from hamcrest import assert_that, all_of, instance_of, greater_than_or_equal_to, matches_regexp, is_in, \
    has_properties, is_, any_of, none, has_item, has_property, equal_to

try:
    from hamcrest import contains_exactly
except ImportError:
    # Compatibility with PyHamcrest < 1.10
    from hamcrest import contains as contains_exactly

import mtg_proxy_printer.settings
from mtg_proxy_printer.sqlite_helpers import cached_dedent, open_database, validate_database_schema
from mtg_proxy_printer.model.carddb import CardIdentificationData, CardDatabase
from mtg_proxy_printer.model.card import Card, CheckCard, CardList, AnyCardType, CustomCard
from mtg_proxy_printer.model.imagedb import ImageDownloader
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.logger import get_logger
from mtg_proxy_printer.units_and_sizes import PageType, QuantityT, UUID, CardSizes, OptStr, unit_registry, CardSize
from mtg_proxy_printer.document_controller import DocumentAction
from mtg_proxy_printer.runner import Runnable
from mtg_proxy_printer.save_file_migrations import migrate_database

if TYPE_CHECKING:
    from mtg_proxy_printer.model.document import Document
logger = get_logger(__name__)
del get_logger

__all__ = [
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
        if isinstance(card, (Card, CustomCard)):
            return cls.REGULAR
        elif isinstance(card, CheckCard):
            return cls.CHECK_CARD
        else:
            raise NotImplementedError()


class DatabaseLoadResult(NamedTuple):
    card: AnyCardType
    was_migrated: bool


class CardRow(NamedTuple):
    is_front: bool
    card_type: CardType
    scryfall_id: Optional[UUID]
    custom_card_id: Optional[UUID]


sqlite3.register_adapter(CardType, lambda item: item.value)
CustomCards = Dict[str, Card]
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

    def __init__(self, document: "Document"):
        super().__init__(None)
        self.document = document
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
        self.card_db = self._open_carddb(document)
        self.image_db = image_db = document.image_db
        # Create our own ImageDownloader, instead of using the ImageDownloader embedded in the ImageDatabase.
        # That one lives in its own thread and runs asynchronously and is thus unusable for loading documents.
        # So create a separate instance and use it synchronously inside this worker thread.
        self.image_loader = image_loader = ImageDownloader(image_db, self)
        image_loader.download_begins.connect(image_db.card_download_starting)
        image_loader.download_finished.connect(image_db.card_download_finished)
        image_loader.download_progress.connect(image_db.card_download_progress)
        image_loader.network_error_occurred.connect(self.on_network_error_occurred)
        self.network_errors_during_load: Counter[str] = collections.Counter()
        self.finished.connect(self.propagate_errors_during_load)
        self.should_run: bool = True
        self.unknown_ids = 0
        self.migrated_ids = 0
        self.current_progress = 0
        self.prefer_already_downloaded = mtg_proxy_printer.settings.settings["decklist-import"].getboolean(
            "prefer-already-downloaded-images")

    def _open_carddb(self, document: "Document") -> CardDatabase:
        db_path = document.card_db.db_path
        card_db = CardDatabase(db_path, self, register_exit_hooks=False)
        if db_path == ":memory:":  # For testing, copy the in-memory database of the passed card database instance
            document.card_db.db.backup(card_db.db)
        return card_db

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
            self.finished.emit()  # Release UI in failure case. _load_document() emits this during regular operation
        finally:
            self.card_db.db.rollback()
            self.card_db.db.close()
            self.card_db = None

    def _complete_loading(self):
        if self.unknown_ids or self.migrated_ids:
            self.unknown_scryfall_ids_found.emit(self.unknown_ids, self.migrated_ids)
            self.unknown_ids = self.migrated_ids = 0
        self.loading_file_successful.emit(self.save_path)
        self.finished.emit()

    def _load_document(self):
        # Imported here to break a circular import. TODO: Investigate a better fix
        from mtg_proxy_printer.document_controller.load_document import ActionLoadDocument
        additional_steps = 2
        save_db = self._open_validate_and_migrate_save_file(self.save_path)
        total_cards = save_db.execute("SELECT count(1) FROM Card").fetchone()[0]
        self.begin_loading_loop.emit(total_cards+additional_steps, "Loading document:")
        page_layout = self._load_document_settings(save_db)
        self._advance_progress()
        logger.debug(f"About to load {total_cards} cards.")
        pages = self._load_cards(save_db) if total_cards else []
        save_db.rollback()
        save_db.close()
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
        db = open_database(save_path, f"document-v7")
        try:
            user_version = Worker._validate_database_schema(db)
            if user_version not in range(2, 8):
                raise AssertionError(f"Unknown database schema version: {user_version}")
            logger.info(f"Save file version is {user_version}")
            migrate_database(db, PageLayoutSettings.create_from_settings())
        except Exception:
            db.rollback()
            db.close()
            raise
        return db


    def _load_cards(self, save_db: sqlite3.Connection) -> List[CardList]:
        custom_cards: CustomCards = {}
        assert_that(
            save_db.execute("SELECT min(page) FROM Page").fetchone(),
            contains_exactly(all_of(instance_of(int), greater_than_or_equal_to(1))
        ))
        pages: List[CardList] = []
        allowed_sizes = {CardSizes.REGULAR.to_save_data(), CardSizes.OVERSIZED.to_save_data()}
        for page, expected_size in save_db.execute(
                "SELECT page, image_size FROM Page ORDER BY page ASC").fetchall():  # type: int, str
            assert_that(page, is_(instance_of(int)))
            assert_that(expected_size, is_in(allowed_sizes))
            pages.append(self._load_cards_on_page(save_db, page, expected_size, custom_cards))
        return pages

    def _load_cards_on_page(
            self, save_db: sqlite3.Connection, page: int, expected_size: str, custom_cards: CustomCards) -> CardList:
        query = textwrap.dedent("""\
            SELECT slot, is_front, type, scryfall_id, custom_card_id -- _load_cards_on_page()
                FROM Card
                WHERE page = ?
                ORDER BY page ASC, slot ASC""")
        db_data: Iterable[Tuple[int, bool, str, OptStr, OptStr]] = save_db.execute(query, (page,))
        valid_card_types = {v.value for v in CardType}
        is_positive_int = all_of(instance_of(int), greater_than_or_equal_to(1))
        result: CardList = []
        card_size = CardSizes.REGULAR if expected_size == CardSizes.REGULAR.to_save_data() else CardSizes.OVERSIZED
        for item in db_data:
            self._validate_save_db_card_row(is_positive_int, item, valid_card_types)
            slot, is_front, card_type_str, scryfall_id, custom_card_id = item
            card_row = CardRow(is_front, CardType(card_type_str), scryfall_id, custom_card_id)
            if custom_card_id:
                if custom_card_id in custom_cards:
                    result.append(custom_cards[custom_card_id])
                else:
                    card = self._load_custom_card_from_save(save_db, card_size, card_row)
                    if card.image_file:
                        result.append(card)
                        custom_cards[custom_card_id] = card
                    else:
                        logger.warning("Skipping loading custom card with invalid image")
                        continue

            elif scryfall_id:
                loaded = self._load_official_card_from_card_db(card_row)
                result.append(loaded.card)
                if loaded.was_migrated:
                    self.migrated_ids += 1
            else:
                result.append(self.document.get_empty_card_for_size(card_size))
            self._advance_progress()
        return result

    @staticmethod
    def _validate_save_db_card_row(is_positive_int, item, valid_card_types):
        assert_that(item, contains_exactly(
            is_positive_int,
            is_in({True, False}),
            is_in(valid_card_types),
            any_of(none(), matches_regexp(UUID.uuid_re.pattern)),
            any_of(none(), matches_regexp(UUID.uuid_re.pattern)),
        ))
        _, _, card_type_str, scryfall_id, custom_card_id = item
        card_type = CardType(card_type_str)
        if card_type == CardType.CHECK_CARD and custom_card_id:
            raise AssertionError("Check cards for custom DFCs currently not supported.")
        assert_that(
            (scryfall_id, custom_card_id), has_item(none()),
            "Scryfall ID and custom card ID must not be both present")

    def _load_official_card_from_card_db(self, data: CardRow) -> Optional[DatabaseLoadResult]:
        if data.card_type == CardType.CHECK_CARD:
            return self._load_check_card(data)
        else:
            return self._load_official_card(data)

    def _load_check_card(self, data: CardRow) -> Optional[DatabaseLoadResult]:
        """
        Loads a check card. Retuns None if the given scryfall id does not belong to a DFC.
        If the front is unavailable, try to find a replacement.
        Returns None, if the back of the found replacement is unavailable.
        """
        migrated = False
        scryfall_id = data.scryfall_id
        if not self.card_db.is_dfc(scryfall_id):
            logger.warning("Requested loading check card for non-DFC card, skipping it.")
            return None
        front = self.card_db.get_card_with_scryfall_id(scryfall_id, True)
        if front is None:
            front = self._find_replacement_card(scryfall_id, True, self.prefer_already_downloaded)
            if front is None:
                logger.info("Unable to find suitable replacement card. Skipping it.")
                return None
            migrated = True
        # To obtain the back side, use the scryfall id of the returned front, not the one in the input data.
        # This ensures that the matching back face is loaded, if the front was migrated.
        back = self.card_db.get_card_with_scryfall_id(front.scryfall_id, False)
        if back is None:
            logger.error(
                "Unable to find suitable replacement card for the DFC back. This should not happen. Skipping it.")
            return None
        card = CheckCard(front, back)
        self.image_loader.get_image_synchronous(card)
        return DatabaseLoadResult(card, migrated)

    def _load_official_card(self, data: CardRow) -> Optional[DatabaseLoadResult]:
        migrated = False
        scryfall_id = data.scryfall_id
        is_front = data.is_front
        if (card := self.card_db.get_card_with_scryfall_id(scryfall_id, is_front)) is None:
            card = self._find_replacement_card(scryfall_id, is_front, self.prefer_already_downloaded)
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

    def _load_custom_card_from_save(self, save_db: sqlite3.Connection, card_size: CardSize, card_row: CardRow) -> CustomCard:
        query = cached_dedent("""\
        SELECT name, set_code, set_name, collector_number, image
          FROM CustomCardData 
          WHERE card_id = ? AND is_front = ?
        """)
        name, set_code, set_name, collector_number, image_bytes = save_db.execute(
            query, (card_row.custom_card_id, card_row.is_front)
        ).fetchone()  # type: str, str, str, str, bytes
        return self.card_db.get_custom_card(
            name, set_code, set_name, collector_number, card_size, card_row.is_front, image_bytes)

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
        is_distance = all_of(
            instance_of(pint.Quantity),
            has_property("dimensionality", equal_to(unit_registry.mm.dimensionality)))
        is_bool_str = is_in(("True", "False"))
        assert_that(
            settings,
            has_properties(
                card_bleed=is_distance,
                page_height=is_distance,
                page_width=is_distance,
                margin_top=is_distance,
                margin_bottom=is_distance,
                margin_left=is_distance,
                margin_right=is_distance,
                row_spacing=is_distance,
                column_spacing=is_distance,
                draw_cut_markers=is_bool_str,
                draw_sharp_corners=is_bool_str,
                draw_page_numbers=is_bool_str,
                document_name=instance_of(str),
            ),
            "Document settings contain invalid data or data types"
        )
        for key, annotated_type in PageLayoutSettings.__annotations__.items():
            value = getattr(settings, key)
            if annotated_type is bool:
                value = mtg_proxy_printer.settings.settings._convert_to_boolean(value)
            elif annotated_type is QuantityT:
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
        return validate_database_schema(
            db_unsafe, SAVE_FILE_MAGIC_NUMBER, f"document-v{user_schema_version}",
            "Application ID mismatch. Not an MTGProxyPrinter save file!",
        )

    def cancel_running_operations(self):
        self.should_run = False
        if self.image_loader.currently_opened_file is not None:
            # Force aborting the download by closing the input stream
            self.image_loader.currently_opened_file.close()
