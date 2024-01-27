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

import enum

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QGraphicsView, QWidget, QAction
from PyQt5.QtGui import QWheelEvent, QKeySequence, QPalette, QResizeEvent

from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.logger import get_logger
from mtg_proxy_printer.ui.page_scene import RenderMode, PageScene

logger = get_logger(__name__)
del get_logger


__all__ = [
    "PageRenderer",
]


@enum.unique
class ZoomDirection(enum.Enum):
    IN = enum.auto()
    OUT = enum.auto()

    @classmethod
    def from_bool(cls, value: bool, /):
        return cls.IN if value else cls.OUT


class PageRenderer(QGraphicsView):
    """
    This class displays an internally held PageScene instance on screen.
    """
    MAX_UI_ZOOM = 16.0

    def __init__(self, parent: QWidget = None):
        super(PageRenderer, self).__init__(parent=parent)
        self.document: Document = None
        self.automatic_scaling = True
        self.setCursor(Qt.SizeAllCursor)
        self.zoom_in_action = QAction(self)
        self.zoom_in_action.setShortcuts(QKeySequence.keyBindings(QKeySequence.ZoomIn))
        self.zoom_in_action.triggered.connect(lambda: self._perform_zoom_step(ZoomDirection.IN))
        self.zoom_out_action = QAction(self)
        self.zoom_out_action.setShortcuts(QKeySequence.keyBindings(QKeySequence.ZoomOut))
        self.zoom_out_action.triggered.connect(lambda: self._perform_zoom_step(ZoomDirection.OUT))
        self.addActions((self.zoom_in_action, self.zoom_out_action))
        self.setToolTip(
            # TODO Find a better way to handle translation of the Ctrl key in the first line
            f"Use {QKeySequence('Ctrl+A').toString(QKeySequence.NativeText).split('+')[0]}+Mouse wheel to zoom.\n"
            f"Usable keyboard shortcuts are:\n"
            f"Zoom in: {', '.join(shortcut.toString(QKeySequence.NativeText) for shortcut in self.zoom_in_action.shortcuts())}\n"
            f"Zoom out: {', '.join(shortcut.toString(QKeySequence.NativeText) for shortcut in self.zoom_out_action.shortcuts())}"
        )
        self._update_background_brush()
        logger.info(f"Created {self.__class__.__name__} instance.")

    def scene(self) -> PageScene:
        return super().scene()

    def changeEvent(self, event: QEvent) -> None:
        if event.type() in {QEvent.ApplicationPaletteChange, QEvent.PaletteChange}:
            self._update_background_brush()
            self.scene().setPalette(self.palette())
            event.accept()
        else:
            super().changeEvent(event)

    def _update_background_brush(self):
        self.setBackgroundBrush(self.palette().color(QPalette.Active, QPalette.Window))

    def set_document(self, document: Document):
        logger.info("Document instance received, creating PageScene.")
        self.document = document
        self.setScene(scene := PageScene(document, RenderMode.ON_SCREEN, self))
        scene.scene_size_changed.connect(self.resizeEvent)

    def _perform_zoom_step(self, direction: ZoomDirection):
        scaling_factor = 1.1 if direction is ZoomDirection.IN else 0.9
        if scaling_factor * self.transform().m11() > self.MAX_UI_ZOOM:
            return
        self.automatic_scaling = self.scene_fully_visible(scaling_factor)
        self.setDragMode(QGraphicsView.NoDrag if self.automatic_scaling else QGraphicsView.ScrollHandDrag)
        if self.automatic_scaling:
            self.fitInView(self.scene().sceneRect(), Qt.KeepAspectRatio)
        else:
            # The initial tooltip text showing the zoom options is rather large, so clear it once the user triggered a
            # zoom action for the first time. This is done to un-clutter the area around the mouse cursor.
            self.setToolTip("")
            old_anchor = self.transformationAnchor()
            self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
            self.scale(scaling_factor, scaling_factor)
            self.setTransformationAnchor(old_anchor)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.modifiers() & Qt.ControlModifier:
            direction = ZoomDirection.from_bool(event.angleDelta().y() > 0)
            self._perform_zoom_step(direction)
            event.accept()
            return
        super().wheelEvent(event)

    def resizeEvent(self, event: QResizeEvent = None) -> None:
        if self.automatic_scaling or self.scene_fully_visible():
            self.automatic_scaling = True
            self.setDragMode(QGraphicsView.NoDrag)
            self.fitInView(self.scene().sceneRect(), Qt.KeepAspectRatio)
        if event is not None:
            super().resizeEvent(event)

    def scene_fully_visible(self, additional_scaling_factor: float = 1.0, /) -> bool:
        scale = self.transform().m11() * additional_scaling_factor
        scene_rect = self.sceneRect()
        content_rect = self.contentsRect()
        return round(scene_rect.width()*scale) <= content_rect.width() \
            and round(scene_rect.height()*scale) <= content_rect.height()
