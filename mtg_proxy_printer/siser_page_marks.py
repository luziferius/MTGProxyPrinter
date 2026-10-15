"""Measured Page Marks convention and geometric diagnostics, without rendering.

All rectangles are page-relative millimetres. Explicit registration frames are
independent of nominal sheets and output-device boundaries. No camera clearance
or hardware qualification is implied by an empty issue tuple.
"""

from dataclasses import dataclass
import math

from mtg_proxy_printer.model.page_geometry import PageGeometry, Rectangle

CONSTRUCTION_INSET_MM = 6.0
BAR_LENGTH_MM = 13.0
BAR_THICKNESS_MM = 1.0
COMPARISON_EPSILON_MM = 1e-9


@dataclass(frozen=True)
class RegistrationBar:
    bar_id: str
    bounds_mm: Rectangle


@dataclass(frozen=True)
class SiserPageMarks:
    frame_width_mm: float
    frame_height_mm: float
    bars: tuple[RegistrationBar, ...]


@dataclass(frozen=True)
class MarkClearanceIssue:
    code: str
    slot_index: int | None
    bar_id: str | None


def _finite_number(value) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _validate_rectangle(rect: Rectangle) -> None:
    if (any(not _finite_number(v) for v in (rect.x, rect.y, rect.width, rect.height, rect.right, rect.bottom))
            or rect.width <= 0 or rect.height <= 0):
        raise ValueError('Rectangle bounds must be finite with positive dimensions')


def build_siser_page_marks(frame_width_mm: float, frame_height_mm: float) -> SiserPageMarks:
    """Build eight bars in stable corner/horizontal-vertical order.

    Each frame dimension must exceed 38 mm to separate opposing mark groups.
    This is a geometric constraint, not a minimum supported cutter media size.
    """
    minimum = 2 * (CONSTRUCTION_INSET_MM + BAR_LENGTH_MM)
    if any(not _finite_number(v) or v <= minimum for v in (frame_width_mm, frame_height_mm)):
        raise ValueError(f'Registration frame dimensions must be finite and exceed {minimum:g} mm')
    width, height = float(frame_width_mm), float(frame_height_mm)
    inset, length, thickness = CONSTRUCTION_INSET_MM, BAR_LENGTH_MM, BAR_THICKNESS_MM
    half = thickness / 2
    bars = []
    for vertical, y in (('top', inset), ('bottom', height - inset)):
        for horizontal, x in (('left', inset), ('right', width - inset)):
            prefix = f'{vertical}-{horizontal}'
            bars.append(RegistrationBar(prefix + '-horizontal',
                Rectangle(x if horizontal == 'left' else x - length, y - half, length, thickness)))
            bars.append(RegistrationBar(prefix + '-vertical',
                Rectangle(x - half, y if vertical == 'top' else y - length, thickness, length)))
    for bar in bars:
        _validate_rectangle(bar.bounds_mm)
    return SiserPageMarks(width, height, tuple(bars))


def _outside_sheet(rect: Rectangle, width: float, height: float) -> bool:
    epsilon = COMPARISON_EPSILON_MM
    return rect.x < -epsilon or rect.y < -epsilon or rect.right > width + epsilon or rect.bottom > height + epsilon


def _touches(a: Rectangle, b: Rectangle) -> bool:
    epsilon = COMPARISON_EPSILON_MM
    return (a.x <= b.right + epsilon and a.right >= b.x - epsilon
            and a.y <= b.bottom + epsilon and a.bottom >= b.y - epsilon)


def assess_siser_clearance(geometry: PageGeometry, marks: SiserPageMarks, *,
                           extra_clearance_mm: float = 0.0) -> tuple[MarkClearanceIssue, ...]:
    """Assess occupied bleed envelopes only, with optional axis-aligned padding.

    Issue order: outside bars in supplied order, then occupied placements in
    supplied order (outside sheet followed by each bar's actual/padded contact).
    Actual contact takes precedence over padding for the same slot/bar pair.
    Guides, titles/page numbers, watermarks, other graphics, opaque pixels,
    output clipping and hardware margins are outside this model's coverage.
    """
    if not _finite_number(extra_clearance_mm) or extra_clearance_mm < 0:
        raise ValueError('Additional clearance must be finite and nonnegative')
    width, height = geometry.sheet_width_mm, geometry.sheet_height_mm
    if any(not _finite_number(v) or v <= 0 for v in (width, height)):
        raise ValueError('Nominal sheet dimensions must be finite and positive')
    padded = []
    issues = []
    for bar in marks.bars:
        rect = bar.bounds_mm
        _validate_rectangle(rect)
        expanded = Rectangle(rect.x - extra_clearance_mm, rect.y - extra_clearance_mm,
                             rect.width + 2 * extra_clearance_mm, rect.height + 2 * extra_clearance_mm)
        _validate_rectangle(expanded)
        padded.append(expanded)
        if _outside_sheet(rect, width, height):
            issues.append(MarkClearanceIssue('registration_bar_outside_sheet', None, bar.bar_id))
    for placement in geometry.placements:
        envelope = placement.bleed_envelope_mm
        _validate_rectangle(envelope)
        slot = placement.slot_index
        if _outside_sheet(envelope, width, height):
            issues.append(MarkClearanceIssue('printed_envelope_outside_sheet', slot, None))
        for bar, expanded in zip(marks.bars, padded):
            if _touches(envelope, bar.bounds_mm):
                issues.append(MarkClearanceIssue('printed_envelope_intersects_mark', slot, bar.bar_id))
            elif extra_clearance_mm > 0 and _touches(envelope, expanded):
                issues.append(MarkClearanceIssue('printed_envelope_within_requested_clearance', slot, bar.bar_id))
    return tuple(issues)
