"""Registration ownership, preserved graphics and actual-page placement."""
import copy
import gc

import pytest
from PySide6.QtCore import QPointF, QRectF, QPersistentModelIndex, Qt
from PySide6.QtGui import QImage, QPainter, QPalette, QColorConstants, QPen
from PySide6.QtWidgets import (QGraphicsScene, QGraphicsLineItem, QGraphicsSimpleTextItem,
                              QGraphicsRectItem, QGraphicsItemGroup)

from mtg_proxy_printer.document_controller.card_actions import ActionAddCard
from mtg_proxy_printer.document_controller.edit_document_settings import ActionEditDocumentSettings
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage, ActionRemovePage
from mtg_proxy_printer.model.page_geometry import build_page_geometry
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.page_scene.items import BullseyeMarkItem, CutMarkSquareItem, CutMarkAngleItem, RenderLayers
from mtg_proxy_printer.page_scene.page_scene import PageScene, RenderMode
from mtg_proxy_printer.page_scene.registration_profiles import get_registration_profile
from mtg_proxy_printer.registration_profile_ids import RegistrationProfileId
from mtg_proxy_printer.units_and_sizes import PageType, CardSizes, unit_registry
from tests.helpers import create_card_with_pixmap

mm = unit_registry.mm


@pytest.fixture
def profile_document(document_light):
    document_light.page_layout = PageLayoutSettings(
        paper_size="A4", margin_left=.04*mm, margin_top=5.04*mm,
        print_registration_marks_style="Bullseye", cut_marker_style="Solid",
        document_name="Owned text check", draw_page_numbers=True)
    return document_light


@pytest.mark.parametrize("style,types", [
    ("None", []), ("Bullseye", [BullseyeMarkItem]*3),
    ("Cut marker", [CutMarkSquareItem, CutMarkAngleItem, CutMarkAngleItem]),
])
@pytest.mark.parametrize("paper", ["portrait", "landscape", "custom"])
def test_fresh_roots_preserved_graphics_and_anchors(qtbot, style, types, paper):
    layout = PageLayoutSettings(paper_size="A4", margin_left=.04*mm, margin_top=5.04*mm)
    if paper == "landscape":
        layout.paper_orientation = "Landscape"
    elif paper == "custom":
        layout.paper_size = "Custom"
        layout.custom_page_width, layout.custom_page_height = 12*unit_registry.inch, 8*unit_registry.inch
    geometry = build_page_geometry(layout, PageType.REGULAR, 1)
    profile = get_registration_profile(style)
    items, fresh = profile.create_items(), profile.create_items()
    assert [type(item) for item in items] == types
    assert all(item.parentItem() is None and item.scene() is None for item in items)
    assert not any(item in fresh for item in items)
    profile.place_items(items, geometry, legacy_x_offset_px=24)
    frame = geometry.margin_frame_px
    anchors = [(frame.x+24, frame.y), (frame.right+24, frame.y), (frame.x+24, frame.bottom)]
    if style == "Bullseye":
        for item, (x, y), origin in zip(items, anchors, [(0, 0), (32, 0), (0, 32)]):
            assert item.scale() == pytest.approx(3+285/256000)
            assert item.transformOriginPoint() == QPointF(*origin)
            assert item.pos().toTuple() == pytest.approx((x*256105/256000, y*256105/256000))
    elif style == "Cut marker":
        assert all(item.pen().style() == Qt.PenStyle.NoPen and item.brush().color() == QColorConstants.Black
                   for item in items)
        assert items[0].rect() == QRectF(0, 0, 65, 65)
        assert items[0].pos() == QPointF(*anchors[0])
        assert [p.toTuple() for p in items[1].polygon()] == [
            (0, 0), (213, 0), (213, 213), (201, 213), (201, 12), (0, 12), (0, 0)]
        assert items[1].pos() == QPointF(anchors[1][0]-213, anchors[1][1])
        assert items[2].pos() == QPointF(anchors[2][0]+213, anchors[2][1])
        assert [item.rotation() for item in items] == [0, 0, 180]
    assert all(item.opacity() == 1 and item.zValue() == RenderLayers.CUT_LINES_BELOW.value for item in items)


@pytest.mark.parametrize("style", ["None", "Bullseye", "Cut marker"])
def test_render_matches_accepted_six_item_construction(profile_document, style):
    """Independent M06 construction: all six roots, inactive styles transparent."""
    d = profile_document
    d.page_layout.print_registration_marks_style = "None"
    d.page_layout.cut_marker_style = "None"
    d.page_layout.document_name = ""
    d.page_layout.draw_page_numbers = False
    scene = PageScene(d, RenderMode.ON_PAPER | RenderMode.FILE_EXPORT)
    reference = QGraphicsScene(scene.sceneRect())
    legacy = [BullseyeMarkItem(False, False), BullseyeMarkItem(True, False), BullseyeMarkItem(False, True),
              CutMarkSquareItem(), CutMarkAngleItem(False), CutMarkAngleItem(True)]
    frame = scene.geometry.margin_frame_px
    positions = [QPointF(frame.x, frame.y), QPointF(frame.right, frame.y), QPointF(frame.x, frame.bottom)]
    for index, item in enumerate(legacy):
        reference.addItem(item)
        item.setOpacity(style == ("Bullseye" if index < 3 else "Cut marker"))
        item.setPos(positions[index % 3])
    # Replacing a profile after a guide exists must retain M06's guide-above-mark order.
    for source in (scene, reference):
        line = source.addLine(frame.x, frame.y+40, frame.x+150, frame.y+40,
                              QPen(QColorConstants.Red, 11))
        line.setZValue(RenderLayers.CUT_LINES_BELOW.value)
    d.page_layout.print_registration_marks_style = style
    scene._update_print_markers()
    images = []
    for source in (scene, reference):
        image = QImage(620, 877, QImage.Format.Format_ARGB32)
        image.fill(QColorConstants.White)
        painter = QPainter(image)
        try:
            source.render(painter, QRectF(0, 0, 620, 877), scene.sceneRect(), Qt.AspectRatioMode.IgnoreAspectRatio)
        finally:
            painter.end()
        images.append(image)
    assert images[0] == images[1]


@pytest.mark.parametrize("style", ["Bullseye", "Cut marker"])
def test_actual_page_refresh_reuses_roots_and_empty_retains_marks(profile_document, style):
    d = profile_document
    d.page_layout.print_registration_marks_style = style
    regular = create_card_with_pixmap("Regular")
    oversized = create_card_with_pixmap("Oversized", CardSizes.OVERSIZED)
    d.apply(ActionAddCard(regular, 1))
    d.apply(ActionNewPage(count=3, content=[[oversized]*2, [regular]*4, []]))
    scene = PageScene(d, RenderMode.ON_PAPER | RenderMode.FILE_EXPORT)
    roots = scene.print_markers.copy()
    for page, occupancy in [(1, 2), (2, 4), (3, 0), (0, 1)]:
        scene.on_current_page_changed(QPersistentModelIndex(d.index(page, 0)))
        assert len(scene.geometry.placements) == occupancy
        assert scene.print_markers == roots
        assert all(root.scene() is scene for root in roots)
    d.apply(ActionRemovePage(0))
    assert len(scene.print_markers) == 3
    d.undo()
    assert len(scene.print_markers) == 3


class CompositeProfile:
    """Test-only non-cutter profile probes the generic ownership boundary."""
    profile_id = RegistrationProfileId.BULLSEYE

    def create_items(self):
        group = QGraphicsItemGroup()
        QGraphicsLineItem(0, 0, 9, 9, group)
        QGraphicsSimpleTextItem("Child label", group)
        roots = [QGraphicsLineItem(0, 0, 15, 15), QGraphicsSimpleTextItem("Root label"),
                 QGraphicsRectItem(0, 0, 20, 20), group]
        for root in roots:
            root.setZValue(RenderLayers.CUT_LINES_BELOW.value)
        return roots

    def place_items(self, items, geometry, *, legacy_x_offset_px=0):
        for index, root in enumerate(items):
            root.setPos(QPointF(geometry.margin_frame_px.x+legacy_x_offset_px+index*30,
                                geometry.margin_frame_px.y))


def test_composite_ownership_stacking_recovery_and_switching(profile_document, monkeypatch, qtlog):
    import mtg_proxy_printer.page_scene.page_scene as scene_module
    resolver = get_registration_profile
    composite = CompositeProfile()
    monkeypatch.setattr(scene_module, "get_registration_profile",
                        lambda style: composite if style == "Bullseye" else resolver(style))
    d = profile_document
    d.apply(ActionAddCard(create_card_with_pixmap("Card"), 2))
    scene = PageScene(d, RenderMode.ON_SCREEN)
    roots = scene.print_markers.copy()
    owned = roots + roots[-1].childItems()
    assert len(roots) == 4
    assert not any(item in scene.cut_lines + scene.text_items for item in owned)
    label = roots[1]
    label_state = label.text(), label.pos(), label.brush()
    child_label = next(item for item in roots[-1].childItems() if isinstance(item, QGraphicsSimpleTextItem))
    child_state = child_label.text(), child_label.pos(), child_label.brush()
    line_state = roots[0].line(), roots[0].pen(), roots[0].pos()

    def check_stacking():
        gc.collect()  # No temporary guide/card wrappers should keep scene items alive.
        ascending = scene.items(Qt.SortOrder.AscendingOrder)
        assert len(scene.cut_lines) == len(scene.geometry.grid_x_edges_px) + len(scene.geometry.grid_y_edges_px)
        for root in scene.print_markers:
            assert all(ascending.index(root) < ascending.index(guide) for guide in scene.cut_lines
                       if root.zValue() == guide.zValue())
        assert len(scene.card_items) == 2
        del ascending
        gc.collect()
        assert len(scene.cut_lines) == len(scene.geometry.grid_x_edges_px) + len(scene.geometry.grid_y_edges_px)
        assert len(scene.card_items) == 2

    for _ in range(3):
        scene.remove_cut_markers()
        assert all(item.scene() is scene for item in owned)
        scene.draw_cut_markers()
        scene.setPalette(QPalette())
        scene._update_text_items(d.page_layout)
        scene._refresh_actual_geometry()
        assert scene.print_markers == roots
        assert (label.text(), label.pos(), label.brush()) == label_state
        assert (child_label.text(), child_label.pos(), child_label.brush()) == child_state
        assert (roots[0].line(), roots[0].pen(), roots[0].pos()) == line_state
        check_stacking()
    valid = d.page_layout
    invalid = copy.copy(valid)
    invalid.paper_size = "Custom"
    invalid.custom_page_width = invalid.custom_page_height = 20*mm
    d.page_layout = invalid
    d.page_layout_changed.emit(invalid)
    assert scene.geometry is None and not scene.print_markers and scene._registration_profile is None
    assert all(item.scene() is None for item in owned)
    d.page_layout = valid
    d.page_layout_changed.emit(valid)
    assert len(scene.print_markers) == 4
    assert not any(item in scene.items() for item in owned)
    check_stacking()
    for style, count in [("Cut marker", 3), ("None", 0), ("Bullseye", 4), ("unknown", 0), ("Bullseye", 4)]:
        old = scene.print_markers.copy()
        layout = copy.copy(d.page_layout)
        layout.print_registration_marks_style = style
        d.apply(ActionEditDocumentSettings(layout))
        assert len(scene.print_markers) == count
        assert all(item.scene() is None for item in old)
        assert d.page_layout.print_registration_marks_style == style
        check_stacking()
        d.undo()
        assert len(scene.print_markers) in (0, 3, 4)
        d.redo()
        assert len(scene.print_markers) == count
    assert sum(scene._is_registration_item(item) for item in scene.items()) == 6
    assert not [record.message for record in qtlog.records if "QGraphicsScene::addItem" in record.message]


def test_unknown_in_memory_style_is_disabled_without_mutation(profile_document):
    profile_document.page_layout.print_registration_marks_style = "Future profile"
    scene = PageScene(profile_document, RenderMode.ON_SCREEN)
    assert not scene.print_markers
    assert scene._registration_profile.profile_id is RegistrationProfileId.NONE
    assert profile_document.page_layout.print_registration_marks_style == "Future profile"
