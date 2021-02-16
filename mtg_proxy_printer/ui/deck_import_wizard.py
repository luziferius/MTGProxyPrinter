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

from PyQt5.QtWidgets import QWizard, QWizardPage

from mtg_proxy_printer.model.carddb import CardDatabase


class LoadListPage(QWizardPage):
    pass


class ChooseListFormatPage(QWizardPage):
    pass


class SummaryPage(QWizardPage):
    pass


class DeckImportWizard(QWizard):
    def __init__(self, card_db: CardDatabase, *args, **kwargs):
        super(DeckImportWizard, self).__init__(*args, **kwargs)
        self.card_db = card_db
        self.addPage(LoadListPage())
        self.addPage(ChooseListFormatPage())
        self.addPage(SummaryPage())
        self.setWindowTitle("Import a deck list")
