"""Scene integration risks not characterized by the legacy position tests."""
import copy
from unittest.mock import patch

import pytest
from PySide6.QtCore import QPersistentModelIndex, Qt, QRectF
from PySide6.QtGui import QImage, QPainter, QColorConstants

from mtg_proxy_printer.document_controller.card_actions import ActionAddCard, ActionRemoveCards
from mtg_proxy_printer.document_controller.edit_document_settings import ActionEditDocumentSettings
from mtg_proxy_printer.document_controller.move_cards import ActionMoveCardsBetweenPages, ActionMoveCardsWithinPage
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage, ActionRemovePage
from mtg_proxy_printer.document_controller.new_document import ActionNewDocument
from mtg_proxy_printer.document_controller.move_page import ActionMovePage
from mtg_proxy_printer.document_controller.replace_card import ActionReplaceCard
from mtg_proxy_printer.model.page_geometry import build_page_geometry
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.model.document_page import PageColumns
from mtg_proxy_printer.page_scene.page_scene import PageScene, RenderMode
from mtg_proxy_printer.settings import settings
from mtg_proxy_printer.units_and_sizes import CardSizes, PageType, distance_to_rounded_px, unit_registry
from tests.helpers import create_card_with_pixmap

mm = unit_registry.mm


@pytest.fixture
def scene_document(document_light):
    document_light.page_layout = PageLayoutSettings(
        paper_size="A4", card_bleed=2*mm, row_spacing=1*mm, column_spacing=1*mm,
        cut_marker_style="Solid", document_name="Geometry check", draw_page_numbers=True,
        print_registration_marks_style="Bullseye",
    )
    return document_light


def check_scene(scene, expected_rows=None):
    expected = build_page_geometry(scene.document.page_layout, scene.selected_page.data(Qt.ItemDataRole.UserRole),
                                   scene.document.rowCount(scene.selected_page))
    assert scene.geometry == expected
    assert not scene.geometry_pending and scene.geometry_unavailable_reason is None
    assert len(scene.print_markers) == 3
    assert all(item.scene() is scene for item in scene.print_markers)
    rows = [item.index.row() for item in scene.card_items]
    assert sorted(rows) == (list(range(len(expected.placements))) if expected_rows is None else expected_rows)
    for item in scene.card_items:
        p = expected.placements[item.index.row()]
        assert item.pos() == scene._presentation_position(p.trim_px.x, p.trim_px.y)
        assert abs(item.bleeds.left.transform().m11()) == p.bleed_px.left
        assert abs(item.bleeds.right.transform().m11()) == p.bleed_px.right
        assert abs(item.bleeds.top.transform().m22()) == p.bleed_px.top
        assert abs(item.bleeds.bottom.transform().m22()) == p.bleed_px.bottom
    vertical = sorted(line.x() for line in scene.cut_lines if line.line().dx() == 0)
    horizontal = sorted(line.y() for line in scene.cut_lines if line.line().dy() == 0)
    assert vertical == [scene._presentation_position(edge, 0).x() for edge in expected.grid_x_edges_px]
    assert horizontal == [scene._presentation_position(0, edge).y() for edge in expected.grid_y_edges_px]


@pytest.mark.parametrize("mode", [RenderMode.ON_SCREEN, RenderMode.ON_PAPER,
                                 RenderMode.ON_SCREEN | RenderMode.IMPLICIT_MARGINS,
                                 RenderMode.ON_PAPER | RenderMode.FILE_EXPORT,
                                 RenderMode.ON_PAPER | RenderMode.NATIVE_PRINT,
                                 RenderMode.ON_PAPER | RenderMode.IMPLICIT_MARGINS])
@pytest.mark.parametrize("style", ["Bullseye", "Cut marker"])
def test_fractional_margins_offsets_labels_and_registration(scene_document, mode, style):
    d = scene_document
    d.page_layout.margin_left = .04*mm
    d.page_layout.margin_right = .04*mm
    d.page_layout.margin_top = 5.04*mm
    d.page_layout.print_registration_marks_style = style
    with patch.dict(settings['printer'], {'horizontal-offset': '2 mm'}):
        scene = PageScene(d, mode)
        d.apply(ActionAddCard(create_card_with_pixmap("Cyan", color=QColorConstants.Cyan), 4))
        check_scene(scene)
        assert scene.x_offset == (0 if mode & (RenderMode.ON_SCREEN | RenderMode.FILE_EXPORT | RenderMode.NATIVE_PRINT) else 24)
        expected_width = 2479 if RenderMode.IMPLICIT_MARGINS in mode else 2480
        assert scene.width() == expected_width  # subtraction precedes rounding for implicit extent
        frame = scene.geometry.margin_frame_px
        assert len(scene.print_markers) == 3
        factor = 256105/256000 if style == "Bullseye" else 1
        assert scene.print_markers[0].pos().x() == pytest.approx((frame.x + scene.x_offset) * factor)
        assert scene.print_markers[0].pos().y() == pytest.approx(frame.y * factor)
        edges = scene.vertical_cut_line_locations[PageType.REGULAR]
        assert scene.document_title_text.x() == round(edges[0])
        expected_y = 2 + 24 + round(max(
            scene.horizontal_cut_line_locations[PageType.REGULAR][-1],
            scene.horizontal_cut_line_locations[PageType.OVERSIZED][-1]))
        assert scene.page_number_text.y() == expected_y


@pytest.mark.parametrize("target", [1, 2, 3])
def test_hidden_output_scene_uses_target_occupancy_not_ui(scene_document, target):
    d = scene_document
    regular = create_card_with_pixmap("Regular")
    oversized = create_card_with_pixmap("Oversized", CardSizes.OVERSIZED)
    d.apply(ActionAddCard(regular, 1))
    d.apply(ActionNewPage(count=3, content=[[oversized]*3, [regular]*4, []]))
    ui_page = d.currently_edited_page
    scene = PageScene(d, RenderMode.ON_PAPER)
    scene.on_current_page_changed(QPersistentModelIndex(d.index(target, 0)))
    check_scene(scene)
    assert d.currently_edited_page is ui_page
    assert scene.geometry.page_type == [PageType.OVERSIZED, PageType.REGULAR, PageType.UNDETERMINED][target-1]
    assert len(scene.geometry.placements) == [3, 4, 0][target-1]
    # Switching to another same-type target must refresh count.
    scene.on_current_page_changed(QPersistentModelIndex(d.index(0, 0)))
    check_scene(scene)
    assert len(scene.geometry.placements) == 1


def test_missing_pixmap_slot_can_become_available_and_replaced(scene_document):
    d = scene_document
    scene = PageScene(d, RenderMode.ON_SCREEN)
    missing = create_card_with_pixmap("Missing")
    missing.image_file = None
    d.apply(ActionNewPage(content=[[missing, create_card_with_pixmap("Second")]]))
    scene.on_current_page_changed(QPersistentModelIndex(d.index(1, 0)))
    check_scene(scene, [1])
    original_second = scene.card_items[0]
    replacement = create_card_with_pixmap("Replacement", color=QColorConstants.Magenta)
    d.apply(ActionReplaceCard(replacement, 1, 0))
    check_scene(scene)
    assert next(item for item in scene.card_items if item.index.row() == 1) is original_second
    d.undo()
    check_scene(scene, [1])
    missing.image_file = create_card_with_pixmap("Now available").image_file
    image_index = d.index(0, PageColumns.Image, d.index(1, 0))
    d.dataChanged.emit(image_index, image_index, [Qt.ItemDataRole.DisplayRole])
    check_scene(scene)


def test_incremental_moves_removal_undo_and_redo(scene_document):
    d = scene_document
    scene = PageScene(d, RenderMode.ON_SCREEN)
    d.apply(ActionAddCard(create_card_with_pixmap("Card"), 5))
    retained = {id(item.index.internalPointer()): item for item in scene.card_items}
    d.apply(ActionMoveCardsWithinPage(0, [0], 4))
    check_scene(scene)
    assert all(retained[id(item.index.internalPointer())] is item for item in scene.card_items)
    d.apply(ActionNewPage())
    d.apply(ActionMoveCardsBetweenPages(0, [1, 2], 1))
    check_scene(scene)
    d.undo()
    check_scene(scene)
    d.redo()
    check_scene(scene)
    d.apply(ActionRemoveCards([0], 0))
    check_scene(scene)
    d.undo()
    check_scene(scene)


@pytest.mark.parametrize("size", [CardSizes.REGULAR, CardSizes.OVERSIZED])
def test_empty_size_transition_and_sole_replacement(scene_document, size):
    d = scene_document
    scene = PageScene(d, RenderMode.ON_SCREEN)
    d.apply(ActionAddCard(create_card_with_pixmap("First", size)))
    check_scene(scene)
    other = CardSizes.OVERSIZED if size == CardSizes.REGULAR else CardSizes.REGULAR
    d.apply(ActionReplaceCard(create_card_with_pixmap("Other", other), 0, 0))
    check_scene(scene)
    d.undo()
    check_scene(scene)
    d.redo()
    check_scene(scene)
    d.apply(ActionRemoveCards([0], 0))
    check_scene(scene)
    assert scene.geometry.page_type == PageType.UNDETERMINED
    d.undo()  # reinsertion has no separate page_type_changed signal
    check_scene(scene)


def test_reflow_temporary_destination_overflow_recovers(scene_document):
    d = scene_document
    d.page_layout.column_spacing = d.page_layout.row_spacing = 0*mm
    d.apply(ActionAddCard(create_card_with_pixmap("Card"), 27))
    scene = PageScene(d, RenderMode.ON_SCREEN)
    scene.on_current_page_changed(QPersistentModelIndex(d.index(1, 0)))
    unavailable = []
    d.rowsMoved.connect(lambda *_: unavailable.append(scene.geometry_unavailable_reason))
    smaller = copy.copy(d.page_layout)
    smaller.margin_left = smaller.margin_right = 20*mm
    d.apply(ActionEditDocumentSettings(smaller))
    assert any(reason and 'capacity' in reason for reason in unavailable)
    assert sum(map(len, d.pages)) == 27
    assert all(len(p) <= 6 for p in d.pages)
    check_scene(scene)
    d.undo()
    assert [len(p) for p in d.pages] == [9, 9, 9]
    check_scene(scene)
    d.redo()
    assert sum(map(len, d.pages)) == 27
    check_scene(scene)


def test_invalid_geometry_rejects_render_then_recovers(scene_document):
    d = scene_document
    scene = PageScene(d, RenderMode.ON_SCREEN)
    d.apply(ActionAddCard(create_card_with_pixmap("Card"), 2))
    valid_layout = d.page_layout
    d.page_layout = PageLayoutSettings(paper_size="Custom", custom_page_width=20*mm, custom_page_height=20*mm,
                                      document_name="Hidden", draw_page_numbers=True, cut_marker_style="Solid")
    d.page_layout_changed.emit(d.page_layout)
    assert scene.geometry is None and scene.geometry_pending
    assert not scene.print_markers and scene._registration_profile is None
    assert not scene.card_items and not scene.cut_lines
    assert not scene.page_number_text.isVisible() and not scene.document_title_text.isVisible()
    image = QImage(100, 100, QImage.Format.Format_ARGB32)
    painter = QPainter(image)
    try:
        with pytest.raises(RuntimeError, match='capacity 0'):
            scene.render(painter, QRectF(0, 0, 100, 100), QRectF(), Qt.AspectRatioMode.KeepAspectRatio)
    finally:
        painter.end()
    d.page_layout = valid_layout
    d.page_layout_changed.emit(valid_layout)
    check_scene(scene)
    assert scene.page_number_text.isVisible()


def test_mixed_unavailable_and_direct_action_recovery(scene_document):
    d = scene_document
    scene = PageScene(d, RenderMode.ON_SCREEN)
    d.apply(ActionAddCard(create_card_with_pixmap("Regular")))
    page = d.index(0, 0)
    d.beginInsertRows(page, 1, 1)
    d.pages[0].append(create_card_with_pixmap("Large", CardSizes.OVERSIZED))
    d.endInsertRows()
    assert scene.geometry is None and 'requires' in scene.geometry_unavailable_reason
    assert not scene.print_markers and scene._registration_profile is None
    with pytest.raises(RuntimeError):
        scene.require_geometry_ready()
    ActionRemoveCards([1], 0).apply(d)  # no final action_applied signal
    check_scene(scene)


def test_empty_zero_capacity_is_renderable_blank_geometry(scene_document):
    d = scene_document
    d.page_layout = PageLayoutSettings(paper_size="Custom", custom_page_width=20*mm, custom_page_height=20*mm,
                                      document_name="Hidden footer", draw_page_numbers=True, cut_marker_style="Solid")
    scene = PageScene(d, RenderMode.ON_PAPER)
    assert scene.geometry.capacity == 0 and not scene.geometry_pending
    assert not scene.cut_lines and not scene.card_items
    assert not scene.page_number_text.isVisible() and not scene.document_title_text.isVisible()
    image = QImage(100, 100, QImage.Format.Format_ARGB32)
    image.fill(QColorConstants.White)
    painter = QPainter(image)
    try:
        scene.render(painter)
    finally:
        painter.end()
    assert image.pixelColor(50, 50) == QColorConstants.White


def test_selected_page_removal_and_blank_document_replacement(scene_document):
    d = scene_document
    scene = PageScene(d, RenderMode.ON_SCREEN)
    d.apply(ActionAddCard(create_card_with_pixmap("Card"), 4))
    d.apply(ActionRemovePage(0))
    check_scene(scene)
    assert scene.geometry.page_type == PageType.UNDETERMINED and not scene.card_items
    d.undo()
    check_scene(scene)


def test_new_document_replacement_undo_and_redo(scene_document):
    d = scene_document
    scene = PageScene(d, RenderMode.ON_SCREEN)
    d.apply(ActionAddCard(create_card_with_pixmap("Card"), 5))
    action = ActionNewDocument()
    action.new_page_layout = copy.copy(d.page_layout)  # explicit paper settings, independent of defaults
    d.apply(action)
    check_scene(scene)
    assert not scene.card_items and len(d.pages) == 1
    d.undo()
    check_scene(scene)
    assert len(scene.card_items) == 5
    d.redo()
    check_scene(scene)
    assert not scene.card_items


def test_root_changes_preserve_selected_identity_and_page_number(scene_document):
    d = scene_document
    d.apply(ActionAddCard(create_card_with_pixmap("Card"), 2))
    scene = PageScene(d, RenderMode.ON_SCREEN)
    selected = d.pages[0]
    d.apply(ActionNewPage(0))
    assert scene.selected_page.row() == 1
    assert scene.page_number_text.text() == '2/2'
    check_scene(scene)
    d.apply(ActionMovePage(1, 0))
    assert d.pages[scene.selected_page.row()] is selected
    assert scene.page_number_text.text() == '1/2'
    check_scene(scene)


def test_hidden_selected_page_removed_by_direct_action_recovers(scene_document):
    d = scene_document
    d.apply(ActionNewPage(content=[[create_card_with_pixmap("Other")]]))
    scene = PageScene(d, RenderMode.ON_PAPER)
    scene.on_current_page_changed(QPersistentModelIndex(d.index(1, 0)))
    ActionRemovePage(1).apply(d)  # UI's different page is retained; no action completion signal
    check_scene(scene)
    assert scene.selected_page.row() == 0 and not scene.card_items


def test_tiny_spacing_unique_guides_without_count_redraw(scene_document):
    d = scene_document
    d.page_layout.row_spacing = d.page_layout.column_spacing = .01*mm
    scene = PageScene(d, RenderMode.ON_SCREEN)
    d.apply(ActionAddCard(create_card_with_pixmap("Card")))
    with patch.object(scene, 'draw_cut_markers', wraps=scene.draw_cut_markers) as draw:
        d.apply(ActionAddCard(create_card_with_pixmap("Card")))
        draw.assert_not_called()
    check_scene(scene)
    assert len(scene.cut_lines) == 8
