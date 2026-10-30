#  Copyright © 2020-2026  Thomas Hess <thomas.hess@udo.edu>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
The icon theme manager ensures that the built-in icon theme is properly colored based on the system color scheme.

Based on my research, the "proper" way is to include a compiled C++ plugin to achieve this result, similar to the one
the KDE project ships.
But this would require writing such a plugin and providing wheels containing the built library, so building wheels for
Win32 x86_64, Win32 aarch64, macOS aarch64, and potentially also Linux wheels for various architectures.
With the latter, the plugin may clash with the one from KDE, if the user happens to have that installed.

So the taken approach is to generate icon themes on-demand based on the built-in one. Whenever a
QEvent.Type.ApplicationPaletteChange or QEvent.Type.ThemeChange event arrives, the new palette is used to generate
a new icon theme with the colors set by the palette.
"""

import hashlib
import json
import os
import typing
from pathlib import Path
import re
import tempfile
import xml.etree.ElementTree as ET

from PySide6.QtCore import QDir, QEvent, QObject, Signal, Slot, Qt
from PySide6.QtGui import QColor, QIcon, QPalette
from PySide6.QtWidgets import QApplication

import mtg_proxy_printer
from mtg_proxy_printer.app_dirs import data_directories
from mtg_proxy_printer.ui.common import load_file
from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger

# Increment when changing the generated theme format or recoloring behavior.
_CACHE_VERSION = 1

_CURRENT_COLOR = re.compile(r"\bcurrentColor\b", re.IGNORECASE)
_STYLE_COLOR = re.compile(
    r"(?:^|;)\s*color\s*:\s*([^;]+)",
    re.IGNORECASE,
)
ColorGroup = QPalette.ColorGroup
ColorRole = QPalette.ColorRole
DirFilter = QDir.Filter
EventType = QEvent.Type
ThemingEvents = (EventType.ApplicationPaletteChange, EventType.ThemeChange)
ThemeWalkFilters = DirFilter.Files | DirFilter.Dirs | DirFilter.NoDotAndDotDot | DirFilter.NoSymLinks


class ColorSchemeCurrentColors(typing.TypedDict):
    Text: str
    Background: str
    Highlight: str
    HighlightedText: str
    ButtonText: str
    ButtonBackground: str
    ViewText: str
    ViewBackground: str
    Link: str
    VisitedLink: str
    Focus: str
    Hover: str


def _read_theme(root: str) -> dict[str, bytes]:
    """Read a filesystem or Qt-resource theme without following symlinks."""
    files: dict[str, bytes] = {}

    def visit(directory: str, relative: str = "") -> None:
        entries = QDir(directory).entryInfoList(ThemeWalkFilters)

        for entry in entries:
            name = entry.fileName()
            relative_path = f"{relative}/{name}" if relative else name
            full_path = f"{directory}/{name}"

            if entry.isDir():
                visit(full_path, relative_path)
            elif entry.isFile():
                files[relative_path] = load_file(full_path)

    if not QDir(root).exists():
        raise FileNotFoundError(f"Icon theme directory does not exist: {root}")

    visit(root.rstrip("/"))

    if "index.theme" not in files:
        msg = f"BUG: Icon theme has no index.theme: {root}"
        logger.critical(msg)
        raise ValueError(msg)

    return files


def _palette_colors(palette: QPalette) -> ColorSchemeCurrentColors:
    """Map common semantic classes to application palette colors."""

    def color_name(role: ColorRole, group: ColorGroup = ColorGroup.Active) -> str:
        return palette.color(group, role).name()

    return ColorSchemeCurrentColors(
        Text=color_name(ColorRole.WindowText),
        Background=color_name(ColorRole.Window),
        Highlight=color_name(ColorRole.Highlight),
        HighlightedText=color_name(ColorRole.HighlightedText),
        ButtonText=color_name(ColorRole.ButtonText),
        ButtonBackground=color_name(ColorRole.Button),
        ViewText=color_name(ColorRole.Text),
        ViewBackground=color_name(ColorRole.Base),
        Link=color_name(ColorRole.Link),
        VisitedLink=color_name(ColorRole.LinkVisited),
        Focus=color_name(ColorRole.Highlight),
        Hover=color_name(ColorRole.Highlight),
    )


def _recolor_svg(data: bytes, colors: ColorSchemeCurrentColors) -> bytes:
    """
    Recolor the given SVG icon by replacing currentColor with an explicit value
    based on the CSS class and the current palette.
    """
    if not _CURRENT_COLOR.search(data.decode("utf-8")):
        return data

    root = ET.fromstring(data)

    def visit(element: ET.Element, inherited_color: str) -> None:
        current_color = inherited_color

        # Breeze icons normally use one semantic class per element.
        for class_name in element.get("class", "").split():
            short_name = class_name.removeprefix("ColorScheme-")
            if short_name in colors:
                current_color = colors[short_name]

        explicit_color = element.get("color")
        style_color = _STYLE_COLOR.search(element.get("style", ""))
        if style_color:
            explicit_color = style_color.group(1).strip()

        if explicit_color:
            parsed = QColor(explicit_color)
            if parsed.isValid():
                current_color = parsed.name()

        # Resolve paint values explicitly rather than depending on Qt SVG's
        # support for CSS currentColor.
        for attribute, value in tuple(element.attrib.items()):
            if _CURRENT_COLOR.search(value):
                element.set(
                    attribute,
                    _CURRENT_COLOR.sub(current_color, value),
                )

        for child in element:
            visit(child, current_color)

    visit(root, colors["Text"])
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        dir=path.parent,
    )
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
        os.replace(temporary_name, path)
    finally:
        Path(temporary_name).unlink(missing_ok=True)


class PaletteIconTheme(QObject):
    """Maintain a generated icon theme matching QApplication.palette().

    source_theme:
        Directory containing index.theme, including a Qt resource directory
        such as ":/icons/breeze".

    cache_directory:
        Parent directory in which generated themes are stored. Defaults to a
        subdirectory of QStandardPaths.CacheLocation.

    The source theme is read once. Generated themes are reused across runs
    when both their source content and palette colors match.
    """
    theme_change_detected = Signal()

    def __init__(self, app: QApplication, source_theme: str, *, cache_directory: str | Path | None = None) -> None:
        super().__init__(app)
        self._app = app
        self._files = _read_theme(source_theme)
        self._active_theme = ""

        source_hash = hashlib.sha256()
        for name, data in sorted(self._files.items()):
            source_hash.update(name.encode("utf-8"))
            source_hash.update(b"\0")
            source_hash.update(hashlib.sha256(data).digest())
        self._source_digest = source_hash.hexdigest()

        if cache_directory is None:
            cache_directory = data_directories.user_cache_path / f"{mtg_proxy_printer.meta_data.PROGRAMNAME}-icon-themes"
        self._cache_directory = cache_directory = Path(cache_directory).resolve()
        cache_directory.mkdir(parents=True, exist_ok=True)

        search_path = str(cache_directory)
        paths = QIcon.themeSearchPaths()
        if search_path not in paths:
            QIcon.setThemeSearchPaths([search_path, *paths])

        # A queued connection ensures that the icon update happens in the next event loop iteration
        self.theme_change_detected.connect(self._refresh_after_event, Qt.ConnectionType.QueuedConnection)

        # Fail immediately if initial theme generation fails.
        self.refresh()
        app.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() in ThemingEvents:
            self.theme_change_detected.emit()
        return False

    @Slot
    def _refresh_after_event(self) -> None:
        try:
            self.refresh()
        except Exception:
            # Keep the previous working theme if regeneration fails.
            logger.exception("Could not update the palette-aware icon theme")

    def refresh(self) -> None:
        """Generate/select the theme for the current application palette."""

        colors = _palette_colors(QApplication.palette())
        identity = json.dumps(
            {
                "version": _CACHE_VERSION,
                "source": self._source_digest,
                "colors": colors,
            },
            sort_keys=True,
        ).encode("utf-8")

        digest = hashlib.sha256(identity).hexdigest()
        theme_name = f"palette-{digest}"

        if theme_name == self._active_theme and QIcon.themeName() == theme_name:
            return

        destination = self._cache_directory / theme_name
        complete_marker = destination / ".complete"

        if not complete_marker.is_file():
            for name, data in sorted(self._files.items()):
                if name.lower().endswith(".svg"):
                    data = _recolor_svg(data, colors)
                _write_atomic(destination / name, data)

            # Written last so interrupted generations can be repaired.
            _write_atomic(complete_marker, b"complete\n")

        QIcon.setThemeName(theme_name)
        self._active_theme = theme_name

        # Theme-backed QIcons can resolve against the newly selected theme.
        # Widgets still need a repaint to request the new pixmaps.
        for widget in self._app.topLevelWidgets():
            widget.update()

        logger.debug(f"Selected palette-aware icon theme {theme_name}")
