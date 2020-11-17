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

from PyQt5.QtWidgets import QWidget


from mtg_proxy_printer.ui.common import inherits_from_ui_file_with_name

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


class AddCardWidget(*inherits_from_ui_file_with_name("add_card_widget")):

    def __init__(self, parent: QWidget = None):
        super(AddCardWidget, self).__init__(parent)
        self.setupUi(self)
        logger.info(f"Created {self.__class__.__name__} instance.")
