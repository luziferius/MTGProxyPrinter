# Copyright (C) 2021 Thomas Hess <thomas.hess@udo.edu>

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


from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWizard, QWizardPage, QFileDialog, QPlainTextEdit, QMessageBox

from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.ui.common import inherits_from_ui_file_with_name


class LoadListPage(*inherits_from_ui_file_with_name("load_list_page")):
    def __init__(self, *args, **kwargs):
        super(LoadListPage, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.registerField("deck_list*", self.deck_list, "plainText", self.deck_list.textChanged)

    @pyqtSlot()
    def on_deck_list_browse_button_clicked(self):
        self.deck_list: QPlainTextEdit
        if not self.deck_list.toPlainText() \
                or QMessageBox.question(
                        self, "Overwrite existing deck list?",
                        "Selecting a file will overwrite the existing deck list. Continue?",
                        QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            # Ignore the used file type filter (second return value)
            selected_file, _ = QFileDialog.getOpenFileName(self, "Select deck file")
            if selected_file:
                print(selected_file)
                self.deck_list.clear()
                with open(selected_file, "rt") as opened_file:
                    self.deck_list.setPlainText(opened_file.read())


class ChooseListFormatPage(QWizardPage):
    def __init__(self, *args, **kwargs):
        super(ChooseListFormatPage, self).__init__(*args, **kwargs)
        # self.setupUi(self)


class SummaryPage(QWizardPage):
    def __init__(self, *args, **kwargs):
        super(SummaryPage, self).__init__(*args, **kwargs)
        # self.setupUi(self)


class DeckImportWizard(QWizard):
    def __init__(self, card_db: CardDatabase, *args, **kwargs):
        super(DeckImportWizard, self).__init__(*args, **kwargs)
        self.card_db = card_db
        self.addPage(ChooseListFormatPage())
        self.addPage(LoadListPage())
        self.addPage(SummaryPage())
        self.setWindowTitle("Import a deck list")
