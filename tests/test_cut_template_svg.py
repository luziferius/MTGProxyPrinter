"""Inspect serialized XML and one actual PDF, without recalculating layout."""

from copy import deepcopy
from dataclasses import replace
import subprocess
import sys
from unittest.mock import PropertyMock, patch
from xml.etree import ElementTree

import pytest
from pypdf import PdfReader

from mtg_proxy_printer.cut_template_svg import serialize_cut_template_svg
from mtg_proxy_printer.model.page_geometry import (
    CardPlacement, Rectangle, build_page_geometry,
)
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.units_and_sizes import PageType, unit_registry

mm = unit_registry.mm
SVG = "{http://www.w3.org/2000/svg}"


def parse(geometry):
    root = ElementTree.fromstring(serialize_cut_template_svg(geometry))
    assert root.tag == SVG + "svg"
    assert set(root.attrib) == {"version", "width", "height", "viewBox"}
    assert root.attrib["version"] == "1.1"
    assert root.attrib["width"].endswith("mm")
    assert root.attrib["height"].endswith("mm")
    width, height = root.attrib["width"][:-2], root.attrib["height"][:-2]
    assert root.attrib["viewBox"] == f"0 0 {width} {height}"
    assert (float(width), float(height)) == pytest.approx(
        (geometry.sheet_width_mm, geometry.sheet_height_mm), abs=1e-6, rel=0)
    assert [path.attrib["id"] for path in root] == [
        f"card-{p.slot_index}" for p in geometry.placements]
    for path in root:
        assert path.tag == SVG + "path" and len(path) == 0
        assert set(path.attrib) == {"id", "d", "fill", "stroke", "stroke-width"}
        assert (path.attrib["fill"], path.attrib["stroke"], path.attrib["stroke-width"]) == (
            "none", "black", "0.1")
    return root


def vertices(path):
    return [values[-2:] for command,values in path_commands(path) if values]


def path_commands(path):
    tokens = iter(path.attrib['d'].split())
    result = []
    for command in tokens:
        count = {'M':2,'L':2,'A':7,'Z':0}[command]
        result.append((command,tuple(float(next(tokens)) for _ in range(count))))
    return result


def path_bounds(path):
    points = vertices(path)
    xs,ys = zip(*points)
    return min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys)


@pytest.mark.parametrize("layout,page_type,count,sheet", [
    (PageLayoutSettings(paper_size="Letter"), PageType.REGULAR, 9, (215.9, 279.4)),
    (PageLayoutSettings(paper_size="A4", paper_orientation="Landscape"), PageType.REGULAR, 8, (297, 210)),
    (PageLayoutSettings(paper_size="Custom", paper_orientation="Landscape",
                        custom_page_width=8*unit_registry.inch, custom_page_height=12*unit_registry.inch),
     PageType.REGULAR, 6, (203.2, 304.8)),
    (PageLayoutSettings(paper_size="A4", margin_left=50*mm, margin_top=65*mm,
                        margin_right=3.1*mm, margin_bottom=2.3*mm,
                        column_spacing=1.234*mm, row_spacing=2.345*mm),
     PageType.REGULAR, 3, (210, 297)),
    (PageLayoutSettings(paper_size="A4"), PageType.REGULAR, 4, (210, 297)),
    (PageLayoutSettings(paper_size="A4"), PageType.OVERSIZED, 3, (210, 297)),
])
def test_representative_layouts(layout, page_type, count, sheet):
    geometry = build_page_geometry(layout, page_type, count)
    root = parse(geometry)
    assert (geometry.sheet_width_mm, geometry.sheet_height_mm) == pytest.approx(sheet, abs=1e-6, rel=0)
    assert len(root) == count
    for path, placement in zip(root, geometry.placements):
        trim = placement.trim_mm
        assert path_bounds(path) == pytest.approx((trim.x,trim.y,trim.width,trim.height),abs=1e-6,rel=0)
        radius = 2.5 if page_type == PageType.REGULAR else 0
        if radius:
            expected = [(trim.x+radius,trim.y),(trim.right-radius,trim.y),
                        (trim.right,trim.y+radius),(trim.right,trim.bottom-radius),
                        (trim.right-radius,trim.bottom),(trim.x+radius,trim.bottom),
                        (trim.x,trim.bottom-radius),(trim.x,trim.y+radius),(trim.x+radius,trim.y)]
            assert [c for c,v in path_commands(path)] == ['M','L','A','L','A','L','A','L','A','Z']
            arcs = [v for c,v in path_commands(path) if c == 'A']
            assert len(arcs) == 4
            assert all(v[:5] == (2.5,2.5,0,0,1) for v in arcs)
        else:
            expected = [(trim.x, trim.y), (trim.right, trim.y),
                        (trim.right, trim.bottom), (trim.x, trim.bottom)]
            assert [c for c,v in path_commands(path)] == ['M','L','L','L','Z']
        assert len(vertices(path)) == len(expected)
        for actual, point in zip(vertices(path), expected):
            assert actual == pytest.approx(point, abs=1e-6, rel=0)
    full = build_page_geometry(layout, page_type, geometry.capacity)
    assert [p.trim_px for p in geometry.placements] == [p.trim_px for p in full.placements[:count]]


def test_independent_a4_coordinates():
    geometry = build_page_geometry(PageLayoutSettings(paper_size="A4"), PageType.REGULAR, 1)
    assert path_bounds(parse(geometry)[0]) == pytest.approx(
        (10.3716666667, 16.4253333333, 63.0766666667, 88.0533333333), abs=1e-6, rel=0)


@pytest.mark.parametrize("zero_capacity", [False, True])
def test_empty_page(zero_capacity):
    layout = PageLayoutSettings(paper_size="A4", margin_left=(200 if zero_capacity else 0)*mm)
    geometry = build_page_geometry(layout, PageType.UNDETERMINED, 0)
    assert len(parse(geometry)) == 0
    assert (geometry.capacity == 0) == zero_capacity


@pytest.mark.parametrize("spacing", [0, .01])
def test_coincident_edges_keep_individual_paths(spacing):
    layout = PageLayoutSettings(paper_size="A4", row_spacing=spacing*mm, column_spacing=spacing*mm)
    geometry = build_page_geometry(layout, PageType.REGULAR, 4)
    paths = parse(geometry)
    assert len(paths) == 4
    a, b, below = vertices(paths[0]), vertices(paths[1]), vertices(paths[3])
    assert a[2] == b[7] and a[3] == b[6]
    assert a[5] == below[0] and a[4] == below[1]


def test_bleed_corners_and_determinism():
    layout = PageLayoutSettings(paper_size="A4", column_spacing=.1016*mm, row_spacing=5*mm)
    geometry = build_page_geometry(layout, PageType.REGULAR, 4)
    before = deepcopy(geometry)
    original = serialize_cut_template_svg(geometry)
    layout.card_bleed = 3*mm
    layout.draw_sharp_corners = True
    changed = build_page_geometry(layout, PageType.REGULAR, 4)
    assert geometry.placements[0].bleed_px != changed.placements[0].bleed_px
    assert serialize_cut_template_svg(changed) == original
    assert serialize_cut_template_svg(geometry) == original
    assert geometry == before


def test_nominal_overhang_and_placement_order_are_preserved():
    layout = PageLayoutSettings(paper_size="Custom", custom_page_width=127.16*mm,
                                custom_page_height=180*mm, margin_left=1*mm)
    geometry = build_page_geometry(layout, PageType.REGULAR, 4)
    assert geometry.placements[1].trim_mm.right > geometry.sheet_width_mm
    # Ordering is supplied by the snapshot; no sorting or empty-slot filling.
    geometry = replace(geometry, placements=geometry.placements[::-1])
    root = parse(geometry)
    x,y,w,h = path_bounds(root[2])
    assert x+w > geometry.sheet_width_mm


@pytest.mark.parametrize("field", ["sheet_width_mm", "sheet_height_mm"])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf"), 0, -1, .0000001])
def test_invalid_sheet_dimensions(field, value):
    geometry = build_page_geometry(PageLayoutSettings(paper_size="A4"), PageType.REGULAR, 0)
    with pytest.raises(ValueError):
        serialize_cut_template_svg(replace(geometry, **{field: value}))


@pytest.mark.parametrize("trim", [
    Rectangle(float("nan"), 0, 1, 1), Rectangle(0, float("inf"), 1, 1),
    Rectangle(0, 0, float("inf"), 1), Rectangle(0, 0, 1, float("nan")),
    Rectangle(0, 0, 0, 1), Rectangle(0, 0, 1, -1),
    Rectangle(0, 0, .0000001, 1), Rectangle(0, 0, 1, .0000001),
    Rectangle(1.7e308, 0, 1.7e308, 1), Rectangle(0, 1.7e308, 1, 1.7e308),
])
def test_invalid_trim_and_derived_coordinates(trim):
    geometry = build_page_geometry(PageLayoutSettings(paper_size="A4"), PageType.REGULAR, 1)
    # Inject pathological millimetre views to exercise the serialization boundary,
    # including overflow that an ordinary supported builder layout cannot create.
    with patch.object(CardPlacement, "trim_mm", new_callable=PropertyMock, return_value=trim):
        with pytest.raises(ValueError):
            serialize_cut_template_svg(geometry)


def test_decimal_formatting_and_unrounded_endpoint_calculation():
    geometry = build_page_geometry(PageLayoutSettings(paper_size="A4"), PageType.OVERSIZED, 1)
    trim = Rectangle(-.0000001, 1.2345674, 1.2345674, 1.2345674)
    with patch.object(CardPlacement, "trim_mm", new_callable=PropertyMock, return_value=trim):
        text = serialize_cut_template_svg(geometry)
    root = ElementTree.fromstring(text)
    assert root[0].attrib["d"] == "M 0 1.234567 L 1.234567 1.234567 L 1.234567 2.469135 L 0 2.469135 Z"
    assert "-0" not in root[0].attrib["d"] and "e-" not in root[0].attrib["d"]


@pytest.mark.parametrize('width,height,radius',[(3,8,1.5),(8,2,1),(5,5,2.5)])
def test_small_trim_radius_clamps_without_changing_bounds(width,height,radius):
    from mtg_proxy_printer.trim_contour import trim_contour
    trim = Rectangle(10,20,width,height)
    contour = trim_contour(trim,PageType.REGULAR)
    assert contour.bounds == trim and contour.radius_mm == radius
    geometry = build_page_geometry(PageLayoutSettings(paper_size='A4'),PageType.REGULAR,1)
    with patch.object(CardPlacement,'trim_mm',new_callable=PropertyMock,return_value=trim):
        path = parse(geometry)[0]
    assert path_bounds(path) == pytest.approx((10,20,width,height),abs=1e-6,rel=0)
    assert [v[:2] for c,v in path_commands(path) if c == 'A'] == [(radius,radius)]*4


def test_serializer_without_application_or_settings_access():
    code = '''
import sys
from unittest.mock import patch
from mtg_proxy_printer.cut_template_svg import serialize_cut_template_svg
assert "mtg_proxy_printer.settings" not in sys.modules
from PySide6.QtWidgets import QApplication
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.model.page_geometry import build_page_geometry
from mtg_proxy_printer.units_and_sizes import PageType
g = build_page_geometry(PageLayoutSettings(paper_size="A4"), PageType.REGULAR, 1)
with patch("mtg_proxy_printer.model.page_geometry.build_page_geometry", side_effect=AssertionError):
    assert 'card-0' in serialize_cut_template_svg(g)
assert QApplication.instance() is None
assert "mtg_proxy_printer.model.document" not in sys.modules
assert "mtg_proxy_printer.page_scene.page_scene" not in sys.modules
'''
    subprocess.run([sys.executable, "-c", code], check=True, capture_output=True, text=True)


def test_svg_matches_measured_unrotated_600_dpi_pdf(document_light, tmp_path):
    from mtg_proxy_printer.document_controller.card_actions import ActionAddCard
    from tests.test_export_mapping import card, pdf, image_placements, bounds

    document = document_light
    document.page_layout = PageLayoutSettings(paper_size="A4", draw_sharp_corners=True, card_bleed=0*mm)
    document.apply(ActionAddCard(card(), 1))
    geometry = build_page_geometry(document.page_layout, PageType.REGULAR, 1)
    root = parse(geometry)
    path = tmp_path / "agreement.pdf"
    pdf(document, path, dpi=600, rotate=False)
    reader = PdfReader(path)
    assert len(reader.pages) == 1
    placements = image_placements(reader.pages[0])
    assert len(placements) == 1
    assert path_bounds(root[0]) == pytest.approx(bounds(placements[0]), abs=.01, rel=0)
    # Nominal SVG paper is separate from Qt's whole-point PDF boundary.
    assert root.attrib["viewBox"] == "0 0 210 297"
    assert (float(reader.pages[0].mediabox.width), float(reader.pages[0].mediabox.height)) == (595, 842)
