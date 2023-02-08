# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>

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

import collections
import dataclasses
import itertools
import math
import pathlib
import sqlite3
import textwrap
import typing

from PyQt5.QtCore import QObject, pyqtSignal as Signal, QThread
from hamcrest import assert_that, all_of, instance_of, greater_than_or_equal_to, matches_regexp, is_in, \
    has_properties, greater_than, is_

try:
    from hamcrest import contains_exactly
except ImportError:
    # Compatibility with PyHamcrest < 1.10
    from hamcrest import contains as contains_exactly

import mtg_proxy_printer.settings
import mtg_proxy_printer.sqlite_helpers
from mtg_proxy_printer.model.carddb import CardDatabase, CardIdentificationData, CardList
from mtg_proxy_printer.model.imagedb import ImageDatabase, ImageDownloader
from mtg_proxy_printer.stop_thread import stop_thread
from mtg_proxy_printer.logger import get_logger
from mtg_proxy_printer.units_and_sizes import PageType, CardSize, CardSizes
from mtg_proxy_printer.document_controller import DocumentAction

if typing.TYPE_CHECKING:
    from mtg_proxy_printer.model.document import Document
logger = get_logger(__name__)
del get_logger

__all__ = [
    "DocumentSaveFormat",
    "DocumentLoader",
    "PageLayoutSettings"
]

# ASCII encoded 'MTGP' for 'MTG proxies'. Stored in the Application ID file header field of the created save files
SAVE_FILE_MAGIC_NUMBER = 41325044
DocumentSaveFormat = typing.Iterable[typing.Tuple[int, int, str, bool]]
T = typing.TypeVar("T")


def split_iterable(iterable: typing.Iterable[T], chunk_size: int, /) -> typing.Iterable[typing.Tuple[T, ...]]:
    """Split the given iterable into chunks of size chunk_size. Does not add padding values to the last item."""
    iterable = iter(iterable)
    return iter(lambda: tuple(itertools.islice(iterable, chunk_size)), ())


@dataclasses.dataclass
class PageLayoutSettings:
    """Stores all page layout attributes, like paper size, margins and spacings"""
    page_height: int = 0
    page_width: int = 0
    margin_top: int = 0
    margin_bottom: int = 0
    margin_left: int = 0
    margin_right: int = 0
    image_spacing_horizontal: int = 0
    image_spacing_vertical: int = 0
    draw_cut_markers: bool = False
    draw_sharp_corners: bool = False

    @classmethod
    def create_from_settings(cls):
        document_settings = mtg_proxy_printer.settings.settings["documents"]
        return cls(
            document_settings.getint("paper-height-mm"),
            document_settings.getint("paper-width-mm"),
            document_settings.getint("margin-top-mm"),
            document_settings.getint("margin-bottom-mm"),
            document_settings.getint("margin-left-mm"),
            document_settings.getint("margin-right-mm"),
            document_settings.getint("image-spacing-horizontal-mm"),
            document_settings.getint("image-spacing-vertical-mm"),
            document_settings.getboolean("print-cut-marker"),
            document_settings.getboolean("print-sharp-corners")
        )

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"'<' not supported between instances of '{self.__class__.__name__}' and '{other.__class__.__name__}'")
        return self.compute_page_card_capacity(PageType.REGULAR) \
            < other.compute_page_card_capacity(PageType.REGULAR) \
            or self.compute_page_card_capacity(PageType.OVERSIZED) \
            < other.compute_page_card_capacity(PageType.OVERSIZED)

    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"'>' not supported between instances of '{self.__class__.__name__}' and '{other.__class__.__name__}'")
        return self.compute_page_card_capacity(PageType.REGULAR) \
            > other.compute_page_card_capacity(PageType.REGULAR) \
            or self.compute_page_card_capacity(PageType.OVERSIZED) \
            > other.compute_page_card_capacity(PageType.OVERSIZED)

    def compute_page_column_count(self, page_type: PageType = PageType.REGULAR) -> int:
        """Returns the total number of card columns that fit on this page."""
        card_size: CardSize = CardSizes.for_page_type(page_type)
        card_width = card_size.as_mm(card_size.width)
        total_width = self.page_width
        margins = self.margin_left + self.margin_right
        spacing = self.image_spacing_horizontal

        total_width -= margins
        if total_width < card_width:
            return 0
        total_width -= card_width
        cards = total_width / (card_width+spacing) + 1
        return math.floor(cards)

    def compute_page_row_count(self, page_type: PageType = PageType.REGULAR) -> int:
        """Returns the total number of card rows that fit on this page."""
        card_size: CardSize = CardSizes.for_page_type(page_type)
        card_height = card_size.as_mm(card_size.height)
        total_height = self.page_height
        margins = self.margin_top + self.margin_bottom
        spacing = self.image_spacing_vertical
        total_height -= margins
        if total_height < card_height:
            return 0
        total_height -= card_height
        cards = total_height / (card_height+spacing) + 1
        return math.floor(cards)

    def compute_page_card_capacity(self, page_type: PageType = PageType.REGULAR) -> int:
        """Returns the total number of card images that fit on a single page."""
        return self.compute_page_row_count(page_type) * self.compute_page_column_count(page_type)


class DocumentLoader(QObject):
    """
    Implements asynchronous background document loading.
    Loading a document can take a long time, if it includes downloading all card images and still takes a noticeable
    time when the card images have to be loaded from a slow hard disk.

    This class uses a QThread with a background worker to push that work off the GUI thread to keep the application
    responsive during a loading process.
    """

    MIN_SUPPORTED_SQLITE_VERSION = (3, 31, 0)

    loading_state_changed = Signal(bool)
    unknown_scryfall_ids_found = Signal(int, int)
    loading_file_failed = Signal(pathlib.Path, str)
    # Emitted when downloading required images during the loading process failed due to network issues.
    network_error_occurred = Signal(str)
    load_requested = Signal(DocumentAction)

    class Worker(QObject):
        """
        This is the worker object that runs inside the DocumentLoader’s internal QThread.

        It iterates over the loaded data and creates a stream of events that, when executed sequentially,
        load the document. It does not directly edit the Document instance.
        Events are created by simply emitting the defined Qt Signals. The DocumentLoader living in the GUI thread will
        receive these and update the document living in the same thread accordingly.
        This prevents issues with QObject instances getting parents assigned across threads.

        Because the thread emits the signals after each long-running I/O process (image loading or downloading)
        finished, processing the generated events in the GUI thread is fast.
        """

        # These signals are used to enqueue a stream of commands across thread boundaries.
        finished = Signal()
        loading_file_failed = Signal(pathlib.Path, str)
        unknown_scryfall_ids_found = Signal(int, int)
        loading_file_successful = Signal(pathlib.Path)
        network_error_occurred = Signal(str)
        load_requested = Signal(DocumentAction)

        def __init__(self, card_db: CardDatabase, image_db: ImageDatabase, document: "Document"):
            super(DocumentLoader.Worker, self).__init__(None)
            self.card_db = card_db
            self.image_db = image_db
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
            self.document = document
            self.save_path = pathlib.Path()
            self.should_run: bool = True
            self.unknown_ids = 0
            self.migrated_ids = 0
            document.action_applied.connect(self.on_document_action_applied)

        def propagate_errors_during_load(self):
            if error_count := sum(self.network_errors_during_load.values()):
                logger.warning(f"{error_count} errors occurred during document load, reporting to the user")
                self.network_error_occurred.emit(
                    f"Some cards may be missing images, proceeed with caution.\n"
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
            except AssertionError as e:
                logger.exception(
                    "Selected file is not a known MTGProxyPrinter document or contains invalid data. Not loading it.")
                self.loading_file_failed.emit(self.save_path, str(e))
                self.finished.emit()

        def on_document_action_applied(self, action: DocumentAction):
            # Imported here to break a circular import. TODO: Investigate a better fix
            from mtg_proxy_printer.document_controller.load_document import ActionLoadDocument
            if isinstance(action, ActionLoadDocument):
                if self.unknown_ids or self.migrated_ids:
                    self.unknown_scryfall_ids_found.emit(self.unknown_ids, self.migrated_ids)
                    self.unknown_ids = self.migrated_ids = 0
                self.loading_file_successful.emit(self.save_path)
                self.finished.emit()

        def _load_document(self):
            # Imported here to break a circular import. TODO: Investigate a better fix
            from mtg_proxy_printer.document_controller.load_document import ActionLoadDocument
            card_data, page_settings = self._read_data_from_save_path(self.save_path)
            pages, self.migrated_ids, self.unknown_ids = self._parse_into_cards(card_data)
            self._fix_mixed_pages(pages, page_settings)
            action = ActionLoadDocument(self.save_path, pages, page_settings)
            self.load_requested.emit(action)

        def _parse_into_cards(self, card_data: DocumentSaveFormat) -> (typing.List[CardList], int, int):
            prefer_already_downloaded = mtg_proxy_printer.settings.settings["decklist-import"].getboolean(
                "prefer-already-downloaded-images")

            current_page_index = 1
            unknown_ids = 0
            migrated_ids = 0
            pages: typing.List[CardList] = [[]]
            current_page = pages[-1]
            for page_number, slot, scryfall_id, is_front in card_data:
                if not self.should_run:
                    logger.info("Cancel request received, stop processing the card list.")
                    return unknown_ids, migrated_ids
                if current_page_index != page_number:
                    current_page_index = page_number
                    current_page: CardList = []
                    pages.append(current_page)
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
        def _read_data_from_save_path(save_file_path: pathlib.Path):
            """
            Reads the data from disk into a list.

            :raises AssertionError: If the save file structure is invalid or contains invalid data.
            """
            logger.info(f"Reading data from save file {save_file_path}")

            with mtg_proxy_printer.sqlite_helpers.open_database(
                    save_file_path, "document-v4", DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION) as db:
                user_version = DocumentLoader.Worker._validate_database_schema(db)
                card_data = DocumentLoader.Worker._read_card_data_from_database(db, user_version)
                settings = DocumentLoader.Worker._read_page_layout_data_from_database(db, user_version)
            return card_data, settings

        @staticmethod
        def _read_card_data_from_database(db: sqlite3.Connection, user_version: int) -> DocumentSaveFormat:
            card_data = []
            if user_version == 2:
                query = textwrap.dedent("""\
                    SELECT page, slot, scryfall_id, 1 AS is_front
                        FROM Card
                        ORDER BY page ASC, slot ASC""")
            elif user_version in {3, 4, 5}:
                query = textwrap.dedent("""\
                    SELECT page, slot, scryfall_id, is_front
                        FROM Card
                        ORDER BY page ASC, slot ASC""")
            else:
                raise AssertionError(f"Unknown database schema version: {user_version}")
            for row_number, row_data in enumerate(db.execute(query)):
                assert_that(row_data, contains_exactly(
                    all_of(instance_of(int), greater_than_or_equal_to(0)),
                    all_of(instance_of(int), greater_than_or_equal_to(0)),
                    all_of(instance_of(str), matches_regexp(r"[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}")),
                    is_in((0, 1))
                ), f"Invalid data found in the save data at row {row_number}. Aborting")
                page, slot, scryfall_id, is_front = row_data
                card_data.append((page, slot, scryfall_id, bool(is_front)))
            return card_data

        @staticmethod
        def _read_page_layout_data_from_database(db, user_version):
            if user_version >= 4:
                document_settings_query = textwrap.dedent(f"""\
                    SELECT page_height, page_width,
                           margin_top, margin_bottom, margin_left, margin_right,
                           image_spacing_horizontal, image_spacing_vertical, draw_cut_markers,
                           {'1' if user_version == 4 else 'draw_sharp_corners'}
                        FROM DocumentSettings
                        WHERE rowid == 1
                    """)
                assert_that(
                    db.execute("SELECT COUNT(*) FROM DocumentSettings").fetchone(),
                    contains_exactly(1),
                )
                settings = PageLayoutSettings(*db.execute(document_settings_query).fetchone())
                assert_that(
                    settings,
                    has_properties(
                        page_height=all_of(instance_of(int), greater_than(0)),
                        page_width=all_of(instance_of(int), greater_than(0)),
                        margin_top=all_of(instance_of(int), greater_than_or_equal_to(0)),
                        margin_bottom=all_of(instance_of(int), greater_than_or_equal_to(0)),
                        margin_left=all_of(instance_of(int), greater_than_or_equal_to(0)),
                        margin_right=all_of(instance_of(int), greater_than_or_equal_to(0)),
                        image_spacing_horizontal=all_of(instance_of(int), greater_than_or_equal_to(0)),
                        image_spacing_vertical=all_of(instance_of(int), greater_than_or_equal_to(0)),
                        draw_cut_markers=is_in((0, 1)),
                        draw_sharp_corners=is_in((0, 1)),
                    ),
                    "Document settings contain invalid data or data types"
                )
                assert_that(
                    settings.compute_page_card_capacity(),
                    is_(greater_than_or_equal_to(1)),
                    "Document settings invalid: At least one card has to fit on a page."
                )
                settings.draw_cut_markers = bool(settings.draw_cut_markers)
                settings.draw_sharp_corners = bool(settings.draw_sharp_corners)
            else:
                settings = PageLayoutSettings.create_from_settings()
            return settings

        @staticmethod
        def _validate_database_schema(db_unsafe: sqlite3.Connection) -> int:
            """
            Validates the database schema of the user-provided file against a known-good schema.

            :raises AssertionError: If the provided file contains an invalid schema
            :returns: Database schema version
            """
            assert_that(
                db_unsafe.execute("PRAGMA application_id").fetchone(),
                contains_exactly(SAVE_FILE_MAGIC_NUMBER),
                "Application ID mismatch. Not an MTGProxyPrinter save file!"
            )
            user_schema_version = db_unsafe.execute("PRAGMA user_version").fetchone()[0]
            try:
                db_known_good = mtg_proxy_printer.sqlite_helpers.create_in_memory_database(
                    f"document-v{user_schema_version}", DocumentLoader.MIN_SUPPORTED_SQLITE_VERSION)
            except FileNotFoundError as e:
                raise AssertionError(f"Unknown save file version: {user_schema_version}") from e
            tables_and_views_query = textwrap.dedent("""\
                SELECT   s.type, s.name,
                         p.cid AS column_id, p.name AS column_name, p.type AS column_type,
                         p."notnull" AS column_not_null_constraint_enabled, p.dflt_value AS column_default_value,
                         p.pk AS column_primary_key_component
                  FROM   sqlite_schema AS s
                  JOIN   pragma_table_info(s.name) AS p
                 WHERE   s.type IN ('table', 'view')
                   AND   s.name NOT LIKE 'sqlite_%'
                ORDER BY s.name, column_id
                ;""")
            indices_query = textwrap.dedent("""\
                -- Note: Also include the “sqlite_autoindex*” indices that are
                -- automatically created for UNIQUE and PRIMARY KEY constraints.
                SELECT   s.name AS index_name,
                         p.seqno AS index_column_sequence_number,
                         p.cid AS column_id,
                         p.name AS column_name
                  FROM   sqlite_schema AS s
                  JOIN   pragma_index_info(s.name) AS p
                 WHERE   s.type = 'index'
                ORDER BY index_name ASC, index_column_sequence_number ASC
                ;""")
            with db_known_good:
                assert_that(
                    db_unsafe.execute(tables_and_views_query).fetchall(),
                    contains_exactly(*db_known_good.execute(tables_and_views_query).fetchall()),
                    "Given save file inconsistent: Unexpected tables or views")
                assert_that(
                    db_unsafe.execute(indices_query).fetchall(),
                    contains_exactly(*db_known_good.execute(indices_query).fetchall()),
                    "Given save file inconsistent: Unexpected indices")
            return user_schema_version

        def cancel_running_operations(self):
            self.should_run = False
            if self.image_loader.currently_opened_file is not None:
                # Force aborting the download by closing the input stream
                self.image_loader.currently_opened_file.close()

    def __init__(self, card_db: CardDatabase, image_db: ImageDatabase, document: "Document"):
        super(DocumentLoader, self).__init__(None)
        self.document = document
        self.worker_thread = QThread()
        self.worker_thread.setObjectName(f"{self.__class__.__name__} background worker")
        self.worker_thread.finished.connect(lambda: logger.debug(f"{self.worker_thread.objectName()} stopped."))
        self.worker = self.Worker(card_db, image_db, document)
        self.worker.moveToThread(self.worker_thread)
        self.worker.load_requested.connect(self.load_requested)
        # Relay two errors/warnings. Can be used to notify the user by displaying some message box with relevant info
        self.worker.loading_file_failed.connect(self.loading_file_failed)
        self.worker.unknown_scryfall_ids_found.connect(self.unknown_scryfall_ids_found)
        self.worker.loading_file_successful.connect(self.on_loading_file_successful)
        self.worker.network_error_occurred.connect(self.network_error_occurred)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(lambda: self.loading_state_changed.emit(False))
        self.worker_thread.started.connect(self.worker.load_document)

    def is_running(self) -> bool:
        return self.worker_thread.isRunning()

    def load_document(self, save_file_path: pathlib.Path):
        logger.info(f"Loading document from {save_file_path}")
        self.loading_state_changed.emit(True)
        self.worker.save_path = save_file_path
        self.worker_thread.start()

    def on_loading_file_successful(self, file_path: pathlib.Path):
        logger.info(f"Loading document from {file_path} successful.")
        self.document.save_file_path = file_path

    def cancel_running_operations(self):
        """
        Can be called to cancel loading a document.
        This forces the worker thread to abort any running image downloads.
        """
        if not self.worker_thread.isRunning():
            return
        self.worker.cancel_running_operations()

    def quit_background_thread(self):
        if self.worker_thread.isRunning():
            logger.info(f"Quitting {self.__class__.__name__} background worker thread")
            stop_thread(self.worker_thread, logger)
