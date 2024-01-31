# Copyright (C) 2020-2024 Thomas Hess <thomas.hess@udo.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import pathlib
import platform
import typing

from PyQt5.QtCore import QFile, QUrl, QObject, QSize
from PyQt5.QtWidgets import QLabel, QWizard, QWidget
from PyQt5.QtGui import QIcon
# noinspection PyUnresolvedReferences
from PyQt5 import uic

from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

__all__ = [
    "RESOURCE_PATH_PREFIX",
    "ICON_PATH_PREFIX",
    "HAS_COMPILED_RESOURCES",
    "BlockedSignals",
    "set_url_label",
    "load_ui_from_file",
    "format_size",
    "WizardBase",
]

try:
    import mtg_proxy_printer.ui.compiled_resources
except ModuleNotFoundError:
    RESOURCE_PATH_PREFIX = str(pathlib.Path(__file__).resolve().parent.parent / "resources")
    ICON_PATH_PREFIX = str(pathlib.Path(__file__).resolve().parent.parent / "resources" / "icons")
    HAS_COMPILED_RESOURCES = False
else:
    import atexit
    # Compiled resources found, so use it.
    RESOURCE_PATH_PREFIX = ":"
    ICON_PATH_PREFIX = ":/icons"
    HAS_COMPILED_RESOURCES = True
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
    Returns the Ui class type from uic.loadUiType(), loading the ui file with the given name.

    :param name:Path to the UI file
    :return: class implementing the requested Ui
    :raises FileNotFoundError: If the given ui file does not exist
    """
    file_path = f"{RESOURCE_PATH_PREFIX}/ui/{name}.ui"
    if not QFile.exists(file_path):
        error_message = f"UI file not found: {file_path}"
        logger.error(error_message)
        raise FileNotFoundError(error_message)
    base_type, _ = uic.loadUiType(file_path, from_imports=True)
    return base_type


def format_size(size: float) -> str:
    for unit in ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB'):
        if -1024 < size < 1024:
            return f"{size:3.2f} {unit}"
        size /= 1024
    return f"{size:.2f} YiB"


class WizardBase(QWizard):
    """Base class for wizards based on QWizard"""
    BUTTON_ICONS: typing.Dict[QWizard.WizardButton, str] = {}

    def __init__(self, window_size: QSize, parent: QWidget, flags):
        super().__init__(parent, flags)
        if platform.system() == "Windows":
            # Avoid Aero style on Windows, which does not support dark mode
            target_style = QWizard.WizardStyle.ModernStyle
            logger.debug(f"Creating a QWizard on Windows, explicitly setting style to {target_style}")
            self.setWizardStyle(target_style)
        self._set_default_size(window_size)
        self._setup_dialog_button_icons()

    def _set_default_size(self, size: QSize):
        new_width = size.width()
        new_height = size.height()
        if (parent := self.parent()) is not None:
            parent_pos = parent.pos()
            available_space = self.screen().availableGeometry()
            new_width = min(available_space.width(), new_width)
            new_height = min(available_space.height(), new_height)
            # Clamp the window position to the screen so that it avoids
            # positioning the window decoration above the screen border.
            target_x = max(0, min(
                available_space.x()+available_space.width()-new_width,
                parent_pos.x() + (parent.width() - new_width)//2))
            target_y = max(0, min(  # This excludes the window decoration title bar
                available_space.y()+available_space.height()-new_height,
                parent_pos.y() + (parent.height() - new_height)//2))
            style = self.style()
            target_y += style.pixelMetric(style.PixelMetric.PM_TitleBarHeight)
            self.setGeometry(target_x, target_y, new_width, new_height)
        else:
            self.resize(new_width, new_height)

    def _setup_dialog_button_icons(self):
        for role, icon in self.BUTTON_ICONS.items():
            button = self.button(role)
            if button.icon().isNull():
                button.setIcon(QIcon.fromTheme(icon))
