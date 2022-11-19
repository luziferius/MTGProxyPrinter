# Copyright (C) 2022 Thomas Hess <thomas.hess@udo.edu>

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

import typing

from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtWidgets import QWidget, QWizard, QWizardPage, QLabel, QComboBox

from mtg_proxy_printer.settings import settings, write_settings_to_file
from mtg_proxy_printer.ui.common import load_ui_from_file
from mtg_proxy_printer import meta_data
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

try:
    from mtg_proxy_printer.ui.generated.first_start_wizard.first_page import Ui_WizardPage as Ui_FirstPage
    from mtg_proxy_printer.ui.generated.first_start_wizard.card_database_page import Ui_WizardPage as Ui_CardDBPage
    from mtg_proxy_printer.ui.generated.first_start_wizard.update_check_page import Ui_WizardPage as Ui_UpdateCheckPage
except ModuleNotFoundError:
    Ui_FirstPage = load_ui_from_file("first_start_wizard/first_page")
    Ui_CardDBPage = load_ui_from_file("first_start_wizard/card_database_page")
    Ui_UpdateCheckPage = load_ui_from_file("first_start_wizard/update_check_page")

__all__ = [
    "FirstStartWizard",

    "FirstPage",
    "CardDBPage",
    "UpdateCheckPage",
]
ComboBoxItems = typing.List[typing.Tuple[str, str]]
COMBO_BOX_CHOICES: ComboBoxItems = [
    ("Ask later", "None"),
    ("Yes", "True"),
    ("No", "False"),
]


class FirstStartWizard(QWizard):

    card_data_download_requested = Signal()

    def __init__(self, *args, disable_card_data_download_button: bool = False):
        super().__init__(*args)
        self.addPage(FirstPage(self))
        self.addPage(card_db_page := CardDBPage(disable_card_data_download_button, self))
        card_db_page.card_data_download_requested.connect(self.card_data_download_requested)
        self.addPage(UpdateCheckPage(self))

    def accept(self) -> None:
        update_section = settings["application"]
        update_section["check-for-application-updates"] = COMBO_BOX_CHOICES[self.field("application_update_choice")][1]
        update_section["check-for-card-data-updates"] = COMBO_BOX_CHOICES[self.field("card_data_update_choice")][1]
        write_settings_to_file()
        super().accept()


def format_label_text(label: QLabel, values: typing.Dict[str, str]):
    """
    Takes a QLabel with text containing placeholder strings and a mapping from these to concrete strings.
    The label text is then formatted using the given mapping.
    """
    formatted = label.text().format_map(values)
    label.setText(formatted)


class FirstPage(QWizardPage):

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_FirstPage()
        self.ui.setupUi(self)
        format_label_text(self.ui.introduction_label, {"application_name": meta_data.PROGRAMNAME})


class CardDBPage(QWizardPage):

    card_data_download_requested = Signal()

    def __init__(self, disable_card_db_download_button: bool = False, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_CardDBPage()
        self.ui.setupUi(self)
        format_label_text(self.ui.carddb_description_label, {
            "application_name": meta_data.PROGRAMNAME,
            "download": f"“{self.ui.download_card_data_button.text()}”"
        })
        if disable_card_db_download_button:
            self.ui.download_card_data_button.setDisabled(True)
            self.ui.download_card_data_button.setToolTip("Download disabled. An import is already running")
        self.ui.download_card_data_button.clicked.connect(self.card_data_download_requested)


class UpdateCheckPage(QWizardPage):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = Ui_UpdateCheckPage()
        self.ui.setupUi(self)
        format_label_text(self.ui.update_label, {"application_name": meta_data.PROGRAMNAME})

        for field_name, combo_box in [
            ("application_update_choice", self.ui.application_update_selection_combo_box),
            ("card_data_update_choice", self.ui.card_data_update_selection_combo_box),
        ]:
            self._setup_combo_box_items(combo_box, COMBO_BOX_CHOICES)
            self.registerField(field_name, combo_box, "currentIndex", combo_box.currentIndexChanged)

    @staticmethod
    def _setup_combo_box_items(combo_box: QComboBox, choices: ComboBoxItems):
        for choice in choices:
            combo_box.addItem(*choice)
