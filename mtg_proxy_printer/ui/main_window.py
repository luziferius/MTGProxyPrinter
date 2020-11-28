# Copyright (C) 2018, 2019 Thomas Hess <thomas.hess@udo.edu>

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


from PyQt5.QtCore import pyqtSlot, pyqtSignal, QStringListModel, QModelIndex, Qt, QItemSelectionModel
from PyQt5.QtGui import QCloseEvent, QResizeEvent
from PyQt5.QtWidgets import QApplication, QTableView, QMessageBox, QProgressBar

import mtg_proxy_printer.card_info_importer
import mtg_proxy_printer.model.carddb
import mtg_proxy_printer.model.imagedb
import mtg_proxy_printer.model.document
import mtg_proxy_printer.settings
from mtg_proxy_printer.ui.common import inherits_from_ui_file_with_name
from mtg_proxy_printer.ui.document_view import DocumentView
from mtg_proxy_printer.ui.page_renderer import PageRenderer
from mtg_proxy_printer.ui.add_card import AddCardWidget

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


class MainWindow(*inherits_from_ui_file_with_name("main_window")):

    should_update_languages = pyqtSignal()
    current_page_changed = pyqtSignal(mtg_proxy_printer.model.document.Page)

    def __init__(self, card_db: mtg_proxy_printer.model.carddb.CardDatabase, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.hide()
        self.card_database: mtg_proxy_printer.model.carddb.CardDatabase = card_db
        self.image_downloader = mtg_proxy_printer.model.imagedb.ImageDatabase(parent=self)
        self.statusBar().addPermanentWidget(self.progress_bar)
        preferred_language = mtg_proxy_printer.settings.settings["images"]["preferred-language"]
        self.language_model = QStringListModel([preferred_language], self)
        self.nothing_happens_box = QMessageBox(
            QMessageBox.Warning, "Not implemented", "Nothing happened.", QMessageBox.Ok, self)
        self.document = mtg_proxy_printer.model.document.Document(parent=self)
        self.current_page = self.document.pages[0]
        self._setup_add_card_widget()
        self._setup_document_view()
        self.action_new_page.triggered.connect(self.document.add_page)
        self.page_card_table_view: QTableView
        self.page_renderer: PageRenderer
        self.should_update_languages.connect(self.update_language_model)
        self.should_update_languages.connect(self.add_card_widget.update_selected_language)
        self.current_page_changed.connect(self.page_card_table_view.setModel)
        self.current_page_changed.connect(self.page_renderer.set_page)
        #
        self.on_selected_page_changed(self.document.createIndex(0,0))
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _setup_add_card_widget(self):
        self.add_card_widget: AddCardWidget
        self.add_card_widget.set_card_database(self.card_database)
        self.add_card_widget.card_added.connect(self.image_downloader.get_image)
        self.add_card_widget.card_added.connect(self.current_page.add_card)
        self.add_card_widget.set_language_model(self.language_model)

    def _setup_document_view(self):
        self.document_view: DocumentView
        self.document_view.setModel(self.document)
        self.document_view.selectionModel().currentChanged.connect(self.on_selected_page_changed)
        self.document_view.selectionModel().select(self.document.createIndex(0, 0), QItemSelectionModel.Select)

    def resizeEvent(self, event: QResizeEvent):
        self.page_renderer.on_resize_event_triggered()
        super(MainWindow, self).resizeEvent(event)

    @pyqtSlot()
    def update_language_model(self):
        self.language_model.setStringList(self.card_database.get_all_languages())

    def closeEvent(self, event: QCloseEvent):
        """
        This function is automatically called when the window is closed using the close [X] button in the window
        decorations or by right clicking in the system window list and using the close action, or similar ways to close
        the window.
        Just ignore this event and simulate that the user used action_quit instead.

        To quote the Qt5 QCloseEvent documentation: If you do not want your widget to be hidden, or want some special
        handling, you should reimplement the event handler and ignore() the event.
        """
        event.ignore()
        # Be safe and emit this signal, because it might be connected to multiple slots.
        self.action_quit.triggered.emit()

    @pyqtSlot()
    def on_action_quit_triggered(self):
        logger.debug(f"User wants to quit.")
        # Prevent a loop, because shutdown() closes this window, causing closeEvent to fire, in turn causing this to be
        # called again. So just disconnect the signal. The connection won’t be needed during application shutdown.
        logger.debug("Quit action confirmed. Exiting…")
        self.action_quit.triggered.disconnect(self.on_action_quit_triggered)
        QApplication.instance().shutdown()

    @pyqtSlot()
    def on_action_print_triggered(self):
        logger.debug(f"User prints the current document.")
        self.nothing_happens_box.show()

    @pyqtSlot()
    def on_action_print_pdf_triggered(self):
        logger.debug(f"User prints the current document to PDF.")
        self.nothing_happens_box.show()

    @pyqtSlot()
    def on_action_download_card_data_triggered(self):
        logger.debug(f"User downloads the card data from Scryfall.")
        # Prevent the action from triggering multiple times, by preventing the user to trigger the action while this
        # already runs.
        self.action_download_card_data.setDisabled(True)
        should_download = QMessageBox.question(
            None, "Download Card data",
            "The local card database is empty. Download the required data from Scryfall now?\n"
            "Downloading might take some time. If you decline, no cards can be searched and printed.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.Yes
        if should_download:
            self.download_card_data()
            self.should_update_languages.emit()
        self.action_download_card_data.setDisabled(self.card_database.has_data())

    @pyqtSlot(int)
    def show_progress_bar(self, expected_total_item_count: int):
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(expected_total_item_count)
        self.progress_bar.show()

    @pyqtSlot()
    def process_events_during_long_operations(self):
        QApplication.instance().processEvents()

    def download_card_data(self):
        importer = mtg_proxy_printer.card_info_importer.CardInfoDownloader(self.card_database, parent=self)
        importer.download_begins.connect(self.show_progress_bar)
        importer.download_finished.connect(self.progress_bar.hide)
        importer.download_progress.connect(self.progress_bar.setValue)
        importer.download_progress.connect(self.process_events_during_long_operations)
        card_data = importer.read_json_card_data_from_url()
        importer.populate_database(self.card_database, card_data)
        self.card_database.commit()

    @pyqtSlot(QModelIndex, QModelIndex)
    def on_selected_page_changed(self, selected: QModelIndex, deselected: QModelIndex = None):
        self.add_card_widget.card_added.disconnect(self.current_page.add_card)
        self.current_page = self.document.data(selected, Qt.EditRole)
        self.add_card_widget.card_added.connect(self.current_page.add_card)
        self.current_page_changed.emit(self.current_page)

    @pyqtSlot()
    def on_action_discard_page_triggered(self):
        self.document_view: DocumentView
        to_be_deleted = self.document_view.selectedIndexes()
        self.document.remove_pages(to_be_deleted)
        new_row_selection = self.document.createIndex(
            min(to_be_deleted[0].row(), self.document.rowCount()-1),
            0
        )
        self.document_view.selectionModel().select(
            new_row_selection, QItemSelectionModel.ClearAndSelect)
        self.on_selected_page_changed(new_row_selection)
