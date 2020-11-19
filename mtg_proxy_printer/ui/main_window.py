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


from PyQt5.QtCore import pyqtSlot, pyqtSignal, QStringListModel
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QWidget, QApplication, QTableView, QMessageBox

import mtg_proxy_printer.card_info_importer
import mtg_proxy_printer.model.carddb
import mtg_proxy_printer.settings
from mtg_proxy_printer.ui.common import inherits_from_ui_file_with_name
from mtg_proxy_printer.ui.page_list_view import PageListView
from mtg_proxy_printer.ui.page_view import PageRenderer
from mtg_proxy_printer.ui.add_card import AddCardWidget

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


class MainWindow(*inherits_from_ui_file_with_name("main_window")):

    should_update_languages = pyqtSignal()

    def __init__(self, parent: QWidget = None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        preferred_language = mtg_proxy_printer.settings.settings["images"]["preferred-language"]

        self.language_model = QStringListModel([preferred_language], self)

        self.nothing_happens_box = QMessageBox(
            QMessageBox.Warning, "Not implemented", "Nothing happened.", QMessageBox.Ok, self)
        self.dirty: bool = False
        self.page_list_view: PageListView
        self.page_card_table_view: QTableView
        self.page_renderer: PageRenderer
        self.add_card_widget: AddCardWidget
        self.add_card_widget.set_language_model(self.language_model)
        self.should_update_languages.connect(self.update_language_model)
        self.should_update_languages.connect(self.add_card_widget.update_selected_language)
        logger.info(f"Created {self.__class__.__name__} instance.")

    @pyqtSlot()
    def update_language_model(self):
        card_db: mtg_proxy_printer.model.carddb.CardDatabase = QApplication.instance().card_db
        self.language_model.setStringList(card_db.get_all_languages())

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
        if self.dirty:
            # TODO: Unsaved changes. Ask the user what to do: Save and exit, Discard and exit, or keep running?
            pass
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
    def on_action_discard_page_triggered(self):
        logger.debug(f"User prints the current document to PDF.")
        self.nothing_happens_box.show()

    @pyqtSlot()
    def on_action_download_card_data_triggered(self):
        logger.debug(f"User downloads the card data from Scryfall.")
        should_download = QMessageBox.question(
            None, "Download Card data",
            "The local card database is empty. Download the required data from Scryfall now?\n"
            "Downloading might take some time. If you decline, no cards can be searched and printed.",
            QMessageBox.Yes|QMessageBox.No, QMessageBox.Yes) == QMessageBox.Yes
        card_db: mtg_proxy_printer.model.carddb.CardDatabase = QApplication.instance().card_db
        if should_download:
            self.download_card_data(card_db)
            self.should_update_languages.emit()
        self.action_download_card_data.setDisabled(card_db.has_data())

    def download_card_data(self, card_db: mtg_proxy_printer.model.carddb.CardDatabase):
        download_url = mtg_proxy_printer.card_info_importer.get_scryfall_bulk_card_data_url()
        card_data = mtg_proxy_printer.card_info_importer.read_json_card_data_from_url(download_url)
        mtg_proxy_printer.card_info_importer.populate_database(card_db, card_data)
        card_db.commit()
