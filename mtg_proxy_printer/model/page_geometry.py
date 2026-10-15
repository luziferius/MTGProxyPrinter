"""Immutable nominal page geometry, independent of rendering and output adapters."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from mtg_proxy_printer.units_and_sizes import (
    CardSizes, PageType, distance_to_mm, distance_to_rounded_px, unit_registry,
)

if TYPE_CHECKING:
    from mtg_proxy_printer.model.page_layout import PageLayoutSettings


def logical_px_to_mm(value: float) -> float:
    """Convert canonical 300-DPI coordinates, retaining fractional pixels."""
    return float(distance_to_mm(value * unit_registry.pixel))


@dataclass(frozen=True)
class Rectangle:
    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    def to_mm(self) -> "Rectangle":
        return Rectangle(*(logical_px_to_mm(v) for v in (self.x, self.y, self.width, self.height)))


@dataclass(frozen=True)
class SideDistances:
    left: float
    top: float
    right: float
    bottom: float

    def to_mm(self) -> "SideDistances":
        return SideDistances(*(logical_px_to_mm(v) for v in (self.left, self.top, self.right, self.bottom)))


@dataclass(frozen=True)
class CardPlacement:
    slot_index: int
    row: int
    column: int
    trim_px: Rectangle
    bleed_px: SideDistances

    @property
    def bleed_envelope_px(self) -> Rectangle:
        trim, bleed = self.trim_px, self.bleed_px
        return Rectangle(trim.x - bleed.left, trim.y - bleed.top,
                         trim.width + bleed.left + bleed.right, trim.height + bleed.top + bleed.bottom)

    @property
    def trim_mm(self) -> Rectangle:
        return self.trim_px.to_mm()

    @property
    def bleed_mm(self) -> SideDistances:
        return self.bleed_px.to_mm()

    @property
    def bleed_envelope_mm(self) -> Rectangle:
        return self.bleed_envelope_px.to_mm()


@dataclass(frozen=True)
class PageGeometry:
    sheet_width_mm: float
    sheet_height_mm: float
    margins_mm: SideDistances
    scene_width_px: int
    scene_height_px: int
    page_type: PageType
    card_width_px: int
    card_height_px: int
    rows: int
    columns: int
    capacity: int
    margin_frame_px: Rectangle
    grid_bounds_px: Rectangle | None
    placements: tuple[CardPlacement, ...]
    grid_x_edges_px: tuple[float, ...]
    grid_y_edges_px: tuple[float, ...]

    @property
    def card_width_mm(self) -> float:
        return logical_px_to_mm(self.card_width_px)

    @property
    def card_height_mm(self) -> float:
        return logical_px_to_mm(self.card_height_px)

    @property
    def margin_frame_mm(self) -> Rectangle:
        return self.margin_frame_px.to_mm()

    @property
    def grid_bounds_mm(self) -> Rectangle | None:
        return self.grid_bounds_px.to_mm() if self.grid_bounds_px is not None else None

    @property
    def grid_x_edges_mm(self) -> tuple[float, ...]:
        return tuple(map(logical_px_to_mm, self.grid_x_edges_px))

    @property
    def grid_y_edges_mm(self) -> tuple[float, ...]:
        return tuple(map(logical_px_to_mm, self.grid_y_edges_px))


def _grid_edges(origin: float, size: int, spacing: int, count: int) -> tuple[float, ...]:
    return tuple(sorted({edge for slot in range(count)
                         for edge in (origin + slot * (size + spacing),
                                      origin + slot * (size + spacing) + size)}))


def build_page_geometry(layout: "PageLayoutSettings", page_type: PageType, card_count: int) -> PageGeometry:
    """Snapshot a sequential page without consulting document or printer state.

    Reject unsupported/transient nonempty pages rather than guessing a layout.
    Capacity and exact-fit behavior are inherited from PageLayoutSettings.
    """
    if page_type not in (PageType.REGULAR, PageType.OVERSIZED, PageType.UNDETERMINED):
        raise ValueError("Page geometry requires REGULAR, OVERSIZED, or empty UNDETERMINED")
    if card_count < 0:
        raise ValueError("Card count must be nonnegative")
    if page_type == PageType.UNDETERMINED and card_count:
        raise ValueError("UNDETERMINED pages must be empty")
    columns = layout.compute_page_column_count(page_type)
    rows = layout.compute_page_row_count(page_type)
    capacity = layout.compute_page_card_capacity(page_type)
    if card_count > capacity:
        raise ValueError(f"Card count {card_count} exceeds page capacity {capacity}")

    width, height = layout.page_width, layout.page_height
    scene_width, scene_height = distance_to_rounded_px(width), distance_to_rounded_px(height)
    margins = (layout.margin_left, layout.margin_top, layout.margin_right, layout.margin_bottom)
    margins_mm = SideDistances(*(float(distance_to_mm(value)) for value in margins))
    left, top, right, bottom = map(distance_to_rounded_px, margins)
    margin_frame = Rectangle(left, top, scene_width - left - right, scene_height - top - bottom)
    card_size = CardSizes.for_page_type(page_type)
    card_width, card_height = round(card_size.width.magnitude), round(card_size.height.magnitude)
    column_spacing = distance_to_rounded_px(layout.column_spacing)
    row_spacing = distance_to_rounded_px(layout.row_spacing)
    full_bleed = distance_to_rounded_px(layout.card_bleed)
    inner_x = distance_to_rounded_px(min(layout.column_spacing / 2, layout.card_bleed))
    inner_y = distance_to_rounded_px(min(layout.row_spacing / 2, layout.card_bleed))
    grid = None
    placements = []
    x_edges = y_edges = ()
    if capacity:
        grid_width = card_width * columns + column_spacing * (columns - 1)
        grid_height = card_height * rows + row_spacing * (rows - 1)
        x = max(max(scene_width - grid_width, 0) / 2, left)
        y = max(max(scene_height - grid_height, 0) / 2, top)
        grid = Rectangle(x, y, grid_width, grid_height)
        x_edges = _grid_edges(x, card_width, column_spacing, columns)
        y_edges = _grid_edges(y, card_height, row_spacing, rows)
        for index in range(card_count):
            row, column = divmod(index, columns)
            trim = Rectangle(x + column * (card_width + column_spacing),
                             y + row * (card_height + row_spacing), card_width, card_height)
            bleed = SideDistances(
                inner_x if column > 0 else full_bleed,
                inner_y if index >= columns else full_bleed,
                inner_x if column + 1 != columns and index + 1 < card_count else full_bleed,
                inner_y if index + columns < card_count else full_bleed,
            )
            placements.append(CardPlacement(index, row, column, trim, bleed))
    return PageGeometry(float(distance_to_mm(width)), float(distance_to_mm(height)), margins_mm,
                        scene_width, scene_height, page_type, card_width, card_height,
                        rows, columns, capacity, margin_frame, grid, tuple(placements), x_edges, y_edges)
