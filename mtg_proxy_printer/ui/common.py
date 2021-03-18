# Copyright (C) 2018 Thomas Hess <thomas.hess@udo.edu>

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

import pathlib

from PyQt5.QtCore import QFile, QUrl, QObject
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel
from PyQt5 import uic

from mtg_proxy_printer.meta_data import PROGRAMNAME
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

try:
    import mtg_proxy_printer.ui.compiled_resources
except ModuleNotFoundError:
    import warnings
    # No compiled resource module found. Load bare files from disk instead.
    warn_msg = f"Compiled Qt resources file not found. If {PROGRAMNAME} is launched directly from the source " \
               "directory, this is expected and harmless. If not, this indicates a failure in the resource compilation."
    warnings.warn(warn_msg)
    RESOURCE_PATH_PREFIX = str(pathlib.Path(__file__).resolve().parent.parent / "resources")
    ICON_PATH_PREFIX = str(pathlib.Path(__file__).resolve().parent.parent / "resources" / "icons")
else:
    import atexit
    # Compiled resources found, so use it.
    RESOURCE_PATH_PREFIX = ":"
    ICON_PATH_PREFIX = ":/icons"
    atexit.register(mtg_proxy_printer.ui.compiled_resources.qCleanupResources)


class BlockedSignals:
    """
    Context manager used to temporarily prevent any QObject-derived object from emitting Qt signals.
    This can be used to break signal trigger loops or unwanted trigger chains.
    """
    def __init__(self, qobject: QObject):
        self.qobject = qobject

    def __enter__(self):
        self.qobject.blockSignals(True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.qobject.blockSignals(False)


def set_url_label(label: QLabel, path: pathlib.Path, display_text: str = None):

    url = QUrl.fromLocalFile(str(path.expanduser()))
    if not label.openExternalLinks():
        # The openExternalLinks property is not set in the UI file, so fail fast instead of doing workarounds.
        raise ValueError(
            f"QLabel with disabled openExternalLinks property used to display an external URL. This won’t work, so "
            f"fail now. Label: {label}, Text: {label.text()}")
    if not display_text:
        display_text = str(path)
    label.setText(f"""<a href="{url.path(QUrl.FullyEncoded):s}">{display_text:s}</a>""")


def load_ui_from_file(name: str):
    """
    Returns a tuple from uic.loadUiType(), loading the ui file with the given name.
    :param name:
    :return:
    """
    file_path = f"{RESOURCE_PATH_PREFIX}/ui/{name}.ui"
    ui_file = QFile(file_path)
    if not ui_file.exists():
        error_message = f"UI file not found: {file_path}"
        logger.error(error_message)
        raise FileNotFoundError(error_message)
    try:
        ui_file.open(QFile.ReadOnly)
        base_type = uic.loadUiType(ui_file, from_imports=True)
    finally:
        ui_file.close()
    return base_type


"""
This renamed function is supposed to be used during class definition to make the intention clear.
Usage example:

class SomeWidget(*inherits_from_ui_file_with_name("SomeWidgetUiFileName")):
    def __init__(self, parent):
        super(SomeWidget, self).__init__(parent)
        self.setupUi(self)

"""
inherits_from_ui_file_with_name = load_ui_from_file
