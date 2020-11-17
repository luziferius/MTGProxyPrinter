# Copyright (C) 2020 Thomas Hess <thomas.hess@udo.edu>

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

from PyQt5.QtWidgets import QWidget, QDialogButtonBox, QLineEdit, QSpinBox


from mtg_proxy_printer.ui.common import inherits_from_ui_file_with_name

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


class AddCardWidget(*inherits_from_ui_file_with_name("add_card_widget")):

    def __init__(self, parent: QWidget = None):
        super(AddCardWidget, self).__init__(parent)
        self.setupUi(self)
        self.card_name_search: QLineEdit
        self.set_name_search: QLineEdit
        self.collectors_number_search: QLineEdit
        self.copies_input: QSpinBox
        self.scryfall_url_input: QLineEdit
        self._connect_reset_button()
        self.button_box.button(QDialogButtonBox.Ok).clicked.connect(self.on_ok_button_triggered)

        logger.info(f"Created {self.__class__.__name__} instance.")

    def _connect_reset_button(self):
        logger.debug("User reset the add_card_widget form.")
        self.button_box: QDialogButtonBox
        reset_button_clicked_signal = self.button_box.button(QDialogButtonBox.Reset).clicked
        reset_button_clicked_signal.connect(self.card_name_search.clearEditText)
        reset_button_clicked_signal.connect(self.set_name_search.clearEditText)
        reset_button_clicked_signal.connect(self.collectors_number_search.clearEditText)
        reset_button_clicked_signal.connect(lambda: self.copies_input.setValue(1))
        reset_button_clicked_signal.connect(self.scryfall_url_input.clear)

    def on_ok_button_triggered(self):
        logger.debug("User clicked OK and adds a new card to the current page.")
        pass
