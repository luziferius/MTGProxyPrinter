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


from PyQt5.QtWidgets import QWidget, QWizard, QWizardPage

from mtg_proxy_printer.ui.common import inherits_from_ui_file_with_name, load_icon
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger


class FilterSetupPage(*inherits_from_ui_file_with_name("cache_cleanup_wizard/filter_setup_page")):

    def __init__(self, parent: QWidget = None):
        super(FilterSetupPage, self).__init__(parent)
        self.setupUi(self)


class CardFilterPage(*inherits_from_ui_file_with_name("cache_cleanup_wizard/card_filter_page")):

    def __init__(self, parent: QWidget = None):
        super(CardFilterPage, self).__init__(parent)
        self.setupUi(self)


class CacheCleanupWizard(QWizard):

    def __init__(self, *args, **kwargs):
        super(CacheCleanupWizard, self).__init__(*args, **kwargs)
        self.addPage(FilterSetupPage(self))
        self.addPage(CardFilterPage(self))
        self.setWindowTitle("Cleanup the local image cache")
        logger.info(f"Created {self.__class__.__name__} instance.")
