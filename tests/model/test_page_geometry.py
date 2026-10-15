from dataclasses import FrozenInstanceError, fields
import subprocess
import sys

import pytest

from mtg_proxy_printer.model.page_geometry import (
    build_page_geometry, Rectangle, SideDistances, logical_px_to_mm,
)
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.units_and_sizes import CardSizes, PageType, unit_registry

mm = unit_registry.mm


def layout(**changes):
    return PageLayoutSettings(paper_size="A4", **changes)


def test_legacy_a4_anchors_and_units():
    geometry = build_page_geometry(layout(), PageType.REGULAR, 9)
    assert (geometry.sheet_width_mm, geometry.sheet_height_mm) == (210, 297)
    assert (geometry.scene_width_px, geometry.scene_height_px) == (2480, 3508)
    assert (geometry.rows, geometry.columns, geometry.capacity) == (3, 3, 9)
    assert [p.trim_px.x for p in geometry.placements[:3]] == [122.5, 867.5, 1612.5]
    assert [p.trim_px.y for p in geometry.placements[::3]] == [194, 1234, 2274]
    assert geometry.grid_bounds_px == Rectangle(122.5, 194, 2235, 3120)
    assert geometry.placements[0].trim_mm.x == pytest.approx(10.371666666666666)
    assert geometry.card_width_mm == pytest.approx(63.07666666666667)
    assert logical_px_to_mm(300) == pytest.approx(25.4)
    assert geometry.margin_frame_mm.width != geometry.sheet_width_mm


@pytest.mark.parametrize("settings,page_type,scene,grid,origin,card", [
    (PageLayoutSettings(paper_size="Letter"), PageType.REGULAR, (2550, 3300), (3, 3), (157.5, 90), (745, 1040)),
    (layout(paper_orientation="Landscape"), PageType.REGULAR, (3508, 2480), (2, 4), (264, 200), (745, 1040)),
    (PageLayoutSettings(paper_size="Custom", custom_page_width=300*mm, custom_page_height=200*mm,
                        paper_orientation="Portrait"), PageType.REGULAR, (3543, 2362), (2, 4), (281.5, 141), (745, 1040)),
    (layout(), PageType.OVERSIZED, (2480, 3508), (2, 2), (200, 264), (1040, 1490)),
])
def test_paper_and_card_configurations(settings, page_type, scene, grid, origin, card):
    result = build_page_geometry(settings, page_type, 1)
    assert (result.scene_width_px, result.scene_height_px) == scene
    assert (result.rows, result.columns) == grid
    assert result.placements[0].trim_px == Rectangle(*origin, *card)


def test_asymmetric_margin_clamping_and_frame():
    result = build_page_geometry(layout(margin_left=50*mm, margin_top=65*mm), PageType.REGULAR, 1)
    assert (result.columns, result.rows) == (2, 2)
    assert result.placements[0].trim_px == Rectangle(591, 768, 745, 1040)
    assert result.margin_frame_px == Rectangle(591, 768, 1889, 2740)
    assert result.margins_mm == SideDistances(50, 65, 0, 0)
    right_only = build_page_geometry(layout(margin_right=80*mm), PageType.REGULAR, 1)
    assert right_only.columns == 2
    assert right_only.placements[0].trim_px.x == 495  # full-sheet centering, not the available margin frame


def test_partial_occupancy_keeps_full_grid():
    full = build_page_geometry(layout(), PageType.REGULAR, 9)
    for count in (1, 4, 5):
        partial = build_page_geometry(layout(), PageType.REGULAR, count)
        assert partial.grid_bounds_px == full.grid_bounds_px
        assert partial.grid_x_edges_px == full.grid_x_edges_px
        assert [p.trim_px for p in partial.placements] == [p.trim_px for p in full.placements[:count]]
        assert [(p.slot_index, p.row, p.column) for p in partial.placements] == [
            (p.slot_index, p.row, p.column) for p in full.placements[:count]]


def test_bleed_occupancy_and_rounding_before_minimum():
    settings = layout(card_bleed=3*mm, column_spacing=0.1016*mm, row_spacing=5*mm)
    result = build_page_geometry(settings, PageType.REGULAR, 4)
    assert result.placements[0].bleed_px == SideDistances(35, 35, 1, 30)
    assert result.placements[1].bleed_px == SideDistances(1, 35, 1, 35)
    assert result.placements[2].bleed_px == SideDistances(1, 35, 35, 35)
    assert result.placements[3].bleed_px == SideDistances(35, 30, 35, 35)
    first = result.placements[0]
    assert first.bleed_envelope_px == Rectangle(first.trim_px.x-35, first.trim_px.y-35, 781, 1105)
    assert first.bleed_envelope_mm.width == pytest.approx(781*25.4/300)
    assert first.bleed_mm.right == pytest.approx(25.4/300)
    settings.card_bleed = 0*mm
    no_bleed = build_page_geometry(settings, PageType.REGULAR, 4)
    assert result.capacity == no_bleed.capacity
    assert [p.trim_px for p in result.placements] == [p.trim_px for p in no_bleed.placements]


@pytest.mark.parametrize("spacing,expected", [
    (0*mm, (122.5, 867.5, 1612.5, 2357.5)),
    (0.01*mm, (122.5, 867.5, 1612.5, 2357.5)),
    (1*mm, (110.5, 855.5, 867.5, 1612.5, 1624.5, 2369.5)),
])
def test_grid_edges_unique_and_within_bounds(spacing, expected):
    result = build_page_geometry(layout(column_spacing=spacing), PageType.REGULAR, 0)
    assert result.grid_x_edges_px == expected
    assert result.grid_y_edges_px == (194, 1234, 2274, 3314)
    assert result.grid_x_edges_mm == pytest.approx(tuple(v*25.4/300 for v in expected))
    assert result.placements == ()
    assert result.grid_x_edges_px[-1] == result.grid_bounds_px.right


@pytest.mark.parametrize("page_type,count,message", [
    (PageType.MIXED, 0, "requires"),
    (PageType.REGULAR, -1, "nonnegative"),
    (PageType.REGULAR, 10, "exceeds"),
    (PageType.UNDETERMINED, 1, "must be empty"),
])
def test_invalid_inputs(page_type, count, message):
    with pytest.raises(ValueError, match=message):
        build_page_geometry(layout(), page_type, count)


def test_empty_fallback_and_zero_capacity_exact_fit():
    regular = build_page_geometry(layout(), PageType.REGULAR, 0)
    empty = build_page_geometry(layout(), PageType.UNDETERMINED, 0)
    assert empty.page_type == PageType.UNDETERMINED
    assert empty.grid_bounds_px == regular.grid_bounds_px
    assert empty.grid_x_edges_px == regular.grid_x_edges_px
    settings = PageLayoutSettings(paper_size="Custom", custom_page_width=CardSizes.REGULAR.width.to(mm, "print"),
                                  custom_page_height=CardSizes.REGULAR.height.to(mm, "print"))
    zero = build_page_geometry(settings, PageType.REGULAR, 0)
    assert zero.capacity == 0  # preserved exact-one-card-fit behavior
    assert zero.grid_bounds_px is None
    assert zero.placements == zero.grid_x_edges_px == zero.grid_y_edges_px == ()
    assert zero.grid_bounds_mm is None
    with pytest.raises(ValueError, match="capacity 0"):
        build_page_geometry(settings, PageType.REGULAR, 1)


def test_neighbor_bleed_is_capped_by_full_bleed():
    result = build_page_geometry(layout(card_bleed=1*mm, column_spacing=5*mm, row_spacing=5*mm),
                                 PageType.REGULAR, 4)
    assert all(p.bleed_px == SideDistances(12, 12, 12, 12) for p in result.placements)


def test_empty_zero_capacity_with_one_nonzero_axis():
    result = build_page_geometry(layout(margin_left=200*mm), PageType.UNDETERMINED, 0)
    assert (result.columns, result.rows, result.capacity) == (0, 3, 0)
    assert result.grid_bounds_px is None
    assert result.grid_x_edges_px == result.grid_y_edges_px == result.placements == ()


def test_snapshot_is_frozen_independent_and_not_serialized():
    settings = layout()
    before_fields = tuple(f.name for f in fields(settings))
    result = build_page_geometry(settings, PageType.REGULAR, 1)
    with pytest.raises(FrozenInstanceError):
        result.scene_width_px = 1
    with pytest.raises(FrozenInstanceError):
        result.placements[0].trim_px.x = 1
    settings.margin_left = 50*mm
    assert result.placements[0].trim_px.x == 122.5
    rebuilt = build_page_geometry(settings, PageType.REGULAR, 1)
    assert rebuilt is not result and rebuilt.placements[0].trim_px.x == 591
    assert tuple(f.name for f in fields(settings)) == before_fields


def test_calculation_without_qapplication_or_document_imports():
    code = '''
import sys
from PySide6.QtWidgets import QApplication
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.model.page_geometry import build_page_geometry
from mtg_proxy_printer.units_and_sizes import PageType
assert QApplication.instance() is None
result = build_page_geometry(PageLayoutSettings(paper_size="A4"), PageType.REGULAR, 1)
assert result.placements[0].trim_px.x == 122.5
assert QApplication.instance() is None
assert "mtg_proxy_printer.model.document" not in sys.modules
assert "mtg_proxy_printer.page_scene.page_scene" not in sys.modules
'''
    subprocess.run([sys.executable, "-c", code], check=True, capture_output=True, text=True)
