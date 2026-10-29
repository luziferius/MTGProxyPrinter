"""Low-ink, static calibration output over captured nominal page geometry."""

import math
import sys

from PySide6.QtCore import QBuffer, QIODevice, QMarginsF, QSizeF, QThread, Qt
from PySide6.QtGui import QBrush, QFont, QPageLayout, QPageSize, QPainter, QPdfWriter, QPen
from PySide6.QtWidgets import QApplication, QGraphicsScene

from mtg_proxy_printer.model.page_geometry import PageGeometry
from mtg_proxy_printer.page_scene.registration_profiles import get_registration_profile
from mtg_proxy_printer.print import _render_graphics_scene
from mtg_proxy_printer.trim_contour import trim_contour
from mtg_proxy_printer.registration_profile_ids import RegistrationProfileId
from mtg_proxy_printer.siser_registration import resolve_siser_page_marks
from mtg_proxy_printer.units_and_sizes import RESOLUTION, distance_to_px, unit_registry


def _build_calibration_scene(geometry: PageGeometry, registration_style: str):
    if registration_style == RegistrationProfileId.SISER.value:
        resolve_siser_page_marks(geometry)
    scene = QGraphicsScene()
    scene.setSceneRect(0, 0, geometry.scene_width_px, geometry.scene_height_px)
    px = lambda value: distance_to_px(value * unit_registry.mm)
    pen = QPen(Qt.GlobalColor.black)
    pen.setWidthF(px(.1))
    pen.setCosmetic(False)
    pen.setCapStyle(Qt.PenCapStyle.FlatCap)
    font = QFont("sans-serif")
    font.setPixelSize(round(6 * RESOLUTION.magnitude / 72))

    def text(value, x, y):
        item = scene.addSimpleText(value, font)
        item.setBrush(QBrush(Qt.GlobalColor.black))
        item.setPos(x, y)
        return item

    for placement in geometry.placements:
        trim, physical = placement.trim_px, placement.trim_mm
        contour = trim_contour(physical,geometry.page_type)
        scene.addPath(contour.painter_path(px), pen, QBrush(Qt.BrushStyle.NoBrush))
        cx, cy = trim.x + trim.width / 2, trim.y + trim.height / 2
        scene.addLine(cx-px(2.5), cy, cx+px(2.5), cy, pen)
        scene.addLine(cx, cy-px(2.5), cx, cy+px(2.5), pen)
        labels = [f"Slot {placement.slot_index+1}", f"X {physical.x:.6f} mm",
                  f"Y {physical.y:.6f} mm", f"W {physical.width:.6f} mm", f"H {physical.height:.6f} mm"]
        for row, label in enumerate(labels):
            text(label, trim.x+px(2), trim.y+px(2+3*row))
    if geometry.placements:
        first = geometry.placements[0].trim_px
        x0, y0, d = first.x+px(6), first.bottom-px(8), px(50)
        scene.addLine(x0, y0, x0+d, y0, pen)
        scene.addLine(x0, y0-d, x0, y0, pen)
        for x in (x0, x0+d):
            scene.addLine(x, y0-px(1), x, y0+px(1), pen)
        for y in (y0-d, y0):
            scene.addLine(x0-px(1), y, x0+px(1), y, pen)
        text("50 mm", x0+px(20), y0+px(1))
        text("50 mm", x0-px(4), y0-px(18)).setRotation(-90)
    profile = get_registration_profile(registration_style)
    roots = profile.create_items()
    for root in roots:
        scene.addItem(root)
    profile.place_items(roots, geometry, legacy_x_offset_px=0)
    return scene, roots


def render_calibration_pdf(geometry: PageGeometry, registration_style: str,
                           *, output_dpi: int | None = None) -> bytes:
    """Prepare one nominal, unrotated PDF on the existing application's GUI thread.

    No live document, preferences, event processing, artwork, or filesystem I/O
    is involved. Returned bytes belong to this invocation, independent of metadata
    differences between separately rendered PDFs.
    """
    app = QApplication.instance()
    if not isinstance(app, QApplication) or QThread.currentThread() != app.thread():
        raise RuntimeError("Calibration PDF requires the existing QApplication GUI thread")
    dpi = round(RESOLUTION.magnitude) if output_dpi is None else output_dpi
    if isinstance(dpi, bool) or not isinstance(dpi, int) or dpi <= 0:
        raise ValueError("Calibration output resolution must be a positive integer")
    dimensions = (geometry.sheet_width_mm, geometry.sheet_height_mm)
    if any(not math.isfinite(value) or value <= 0 for value in dimensions):
        raise ValueError("Calibration paper dimensions must be finite and positive")
    paper = QPageSize(QSizeF(*dimensions), QPageSize.Unit.Millimeter, "", QPageSize.SizeMatchPolicy.ExactMatch)
    if not paper.isValid() or paper.sizePoints().width() <= 0 or paper.sizePoints().height() <= 0:
        raise ValueError("Calibration paper dimensions cannot be represented by Qt")
    buffer = QBuffer()
    writer = painter = scene = None
    roots = []
    try:
        if not buffer.open(QIODevice.OpenModeFlag.WriteOnly):
            raise RuntimeError("Cannot open calibration PDF memory buffer")
        writer = QPdfWriter(buffer)
        writer.setResolution(dpi)
        layout = QPageLayout(paper, QPageLayout.Orientation.Portrait, QMarginsF(), QPageLayout.Unit.Millimeter)
        if not writer.setPageLayout(layout):
            raise RuntimeError("Calibration PDF rejected the requested paper layout")
        emitted = writer.pageLayout().fullRect(QPageLayout.Unit.Millimeter)
        if any(abs(actual-wanted) > 25.4/72 for actual, wanted in
               zip((emitted.width(), emitted.height()), dimensions)):
            raise RuntimeError("Calibration PDF paper differs from requested dimensions")
        scene, roots = _build_calibration_scene(geometry, registration_style)
        painter = QPainter()
        if not painter.begin(writer):
            raise RuntimeError("Cannot start calibration PDF painter")
        painter.setRenderHint(QPainter.RenderHint.LosslessImageRendering)
        _render_graphics_scene(scene, geometry, painter, dpi, dpi)
        if not painter.end():
            raise RuntimeError("Cannot finalize calibration PDF painter")
        painter = None
        writer = None  # Finalize the writer while its QBuffer is still alive.
        return bytes(buffer.data())
    finally:
        primary_failure = sys.exc_info()[0] is not None
        cleanup_error = None
        try:
            if painter is not None and painter.isActive():
                painter.end()
        except Exception as error:
            cleanup_error = error
        painter = writer = None
        for cleanup in (buffer.close, scene.clear if scene is not None else lambda: None):
            try:
                cleanup()
            except Exception as error:
                if cleanup_error is None:
                    cleanup_error = error
        roots.clear()
        if cleanup_error is not None and not primary_failure:
            raise cleanup_error
