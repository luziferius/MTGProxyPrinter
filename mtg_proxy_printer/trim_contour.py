"""Selected cutting contour over unchanged nominal trim bounds; no output state."""

from dataclasses import dataclass
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mtg_proxy_printer.model.page_geometry import Rectangle
    from mtg_proxy_printer.units_and_sizes import PageType

REGULAR_RADIUS_MM = 2.5


@dataclass(frozen=True)
class TrimContour:
    bounds: "Rectangle"
    radius_mm: float

    def commands(self):
        """Clockwise absolute mm commands; circular SVG arcs retain true radii."""
        b, r = self.bounds, self.radius_mm
        x, y, right, bottom = b.x, b.y, b.right, b.bottom
        if not r:
            return [('M', (x,y)), ('L', (right,y)), ('L', (right,bottom)),
                    ('L', (x,bottom)), ('Z', ())]
        return [('M', (x+r,y)), ('L', (right-r,y)),
                ('A', (r,r,0,0,1,right,y+r)), ('L', (right,bottom-r)),
                ('A', (r,r,0,0,1,right-r,bottom)), ('L', (x+r,bottom)),
                ('A', (r,r,0,0,1,x,bottom-r)), ('L', (x,y+r)),
                ('A', (r,r,0,0,1,x+r,y)), ('Z', ())]

    def painter_path(self, to_device):
        """Qt represents circular quarters as cubic curves, at the same tangents."""
        # Lazy import keeps SVG serialization independent of Qt/application state.
        from PySide6.QtCore import QRectF, Qt
        from PySide6.QtGui import QPainterPath
        b = self.bounds
        rect = QRectF(*(to_device(v) for v in (b.x,b.y,b.width,b.height)))
        path = QPainterPath()
        if self.radius_mm:
            radius = to_device(self.radius_mm)
            path.addRoundedRect(rect,radius,radius,Qt.SizeMode.AbsoluteSize)
        else:
            path.addRect(rect)
        return path


def trim_contour(trim: "Rectangle", page_type: "PageType") -> TrimContour:
    """2.5 mm project specification for regular cards; oversized remains square."""
    if any(not math.isfinite(v) for v in (trim.x,trim.y,trim.width,trim.height,trim.right,trim.bottom)):
        raise ValueError('Trim bounds must be finite')
    if trim.width <= 0 or trim.height <= 0:
        raise ValueError('Trim dimensions must be positive')
    nominal = REGULAR_RADIUS_MM if page_type.name == 'REGULAR' else 0.
    return TrimContour(trim,min(nominal,trim.width/2,trim.height/2))
