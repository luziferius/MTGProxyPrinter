"""Serialize occupied nominal trim contours without output or GUI state."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING
from xml.etree import ElementTree

from mtg_proxy_printer.trim_contour import trim_contour

if TYPE_CHECKING:
    from mtg_proxy_printer.model.page_geometry import PageGeometry


def _format_mm(value: float, *, dimension: bool = False) -> str:
    """Format only at the XML boundary; dimensions must remain positive."""
    if not math.isfinite(value):
        raise ValueError("SVG millimetre values must be finite")
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    if text == "-0":
        text = "0"
    if dimension and (value <= 0 or text == "0"):
        raise ValueError("SVG dimensions must be positive at six-decimal precision")
    return text


def serialize_cut_template_svg(geometry: PageGeometry) -> str:
    """Return one closed trim path, regular rounded/oversized square, in mm.

    The caller owns snapshot construction and UTF-8 file writing. Coordinates
    remain nominal, including coincident edges and any paper-edge overhang.
    """
    width = _format_mm(geometry.sheet_width_mm, dimension=True)
    height = _format_mm(geometry.sheet_height_mm, dimension=True)
    root = ElementTree.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg",
        "version": "1.1",
        "width": f"{width}mm",
        "height": f"{height}mm",
        "viewBox": f"0 0 {width} {height}",
    })
    for placement in geometry.placements:
        trim = placement.trim_mm
        _format_mm(trim.width, dimension=True)
        _format_mm(trim.height, dimension=True)
        contour = trim_contour(trim,geometry.page_type)
        commands = ' '.join(command + (' ' + ' '.join(map(_format_mm,values)) if values else '')
                            for command,values in contour.commands())
        ElementTree.SubElement(root, "path", {
            "id": f"card-{placement.slot_index}",
            "d": commands,
            "fill": "none",
            "stroke": "black",
            "stroke-width": "0.1",
        })
    return ElementTree.tostring(root, encoding="unicode", xml_declaration=True)
