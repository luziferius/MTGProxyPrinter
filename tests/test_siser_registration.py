"""M14 integration only: faithful calibration, preview recovery and route guards."""
from copy import deepcopy
from dataclasses import replace
from io import BytesIO
from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import Qt, QPointF, QPersistentModelIndex
from PySide6.QtGui import QColorConstants, QPalette, QPen
from PySide6.QtWidgets import QWidget
from pypdf import PdfReader

from mtg_proxy_printer import calibration, print as printing
from mtg_proxy_printer.calibration import render_calibration_pdf
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard
from mtg_proxy_printer.model.page_geometry import build_page_geometry
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.page_scene.items import RenderLayers
from mtg_proxy_printer.page_scene.page_scene import PageScene, RenderMode
from mtg_proxy_printer.page_scene.registration_profiles import get_registration_profile
from mtg_proxy_printer.siser_registration import resolve_siser_page_marks
from mtg_proxy_printer.ui import dialogs, main_window
from mtg_proxy_printer.ui.main_window import MainWindow
from mtg_proxy_printer.units_and_sizes import PageType, unit_registry, distance_to_px
from tests.helpers import create_card_with_pixmap
from tests.test_calibration_pdf import stroked_paths, stroked_commands, bounds

mm = unit_registry.mm


def layout(paper='Letter', **kwargs):
    return PageLayoutSettings(paper_size=paper,print_registration_marks_style='Siser',**kwargs)


def geometry(paper='Letter',count=9,**kwargs):
    return build_page_geometry(layout(paper,**kwargs),PageType.REGULAR,count)


def rect_values(r):
    return r.x,r.y,r.width,r.height


def filled_bounds(page):
    """Only the eight straight filled rectangles in these synthetic PDFs."""
    result, points = [], []
    height = float(page.mediabox.height)
    def visit(op,args,cm,tm):
        nonlocal points
        def point(x,y):
            a,b,c,d,e,f = cm
            return ((a*x+c*y+e)*25.4/72,(height-b*x-d*y-f)*25.4/72)
        if op in (b'm',b'l'):
            points.append(point(*map(float,args)))
        elif op == b're':
            x,y,w,h = map(float,args)
            points.extend(point(x1,y1) for x1,y1 in [(x,y),(x+w,y),(x+w,y+h),(x,y+h)])
        elif op in (b'f',b'f*'):
            if points:
                result.append(bounds(points))
            points = []
        elif op in (b'n',b'S',b's'):
            points = []
    page.extract_text(visitor_operand_before=visit)
    return sorted(result)


@pytest.mark.parametrize('sheet,frame',[
    ((215.9,279.4),(215.9,279.4)),
    ((297,210),(296.96832909999995,209.97333756666666)),
])
def test_resolver_custom_identity_tolerance_and_unchanged_snapshot(sheet,frame):
    g = build_page_geometry(layout('Custom',custom_page_width=sheet[0]*mm,custom_page_height=sheet[1]*mm),PageType.REGULAR,0)
    original = deepcopy(g)
    marks = resolve_siser_page_marks(g)
    assert (marks.frame_width_mm,marks.frame_height_mm) == frame
    assert g == original and (g.sheet_width_mm,g.sheet_height_mm) == sheet
    assert resolve_siser_page_marks(replace(g,sheet_width_mm=sheet[0]+.5e-6)) == marks
    with pytest.raises(ValueError,match='Supported configurations'):
        resolve_siser_page_marks(replace(g,sheet_width_mm=sheet[0]+2e-6))


@pytest.mark.parametrize('paper,orientation',[('Letter','Landscape'),('A4','Portrait')])
def test_unsupported_orientation_is_not_transposed(paper,orientation):
    g = geometry(paper,0,paper_orientation=orientation)
    with pytest.raises(ValueError,match='does not support'):
        resolve_siser_page_marks(g)


def test_profile_fresh_filled_roots_and_fractional_geometry(qtbot):
    profile = get_registration_profile('Siser')
    items, other = profile.create_items(),profile.create_items()
    assert len(items) == len(other) == 8 and not any(i in other for i in items)
    assert all(i.parentItem() is None and i.scene() is None for i in items)
    g = geometry()
    profile.place_items(items,g)
    for item,bar in zip(items,resolve_siser_page_marks(g).bars):
        x,y,w,h = (distance_to_px(v*mm) for v in rect_values(bar.bounds_mm))
        assert item.pos() == QPointF(x,y)
        assert (item.rect().x(),item.rect().y(),item.rect().width(),item.rect().height()) == (0,0,w,h)
        assert item.pen().style() == Qt.PenStyle.NoPen
        assert item.brush().color() == QColorConstants.Black
        assert item.zValue() == RenderLayers.CUT_LINES_BELOW.value
        assert item.scale() == 1 and item.rotation() == 0 and item.transform().isIdentity()
    assert items[0].rect().height() != round(items[0].rect().height())
    with pytest.raises(ValueError,match='legacy horizontal offset'):
        profile.place_items(items,g,legacy_x_offset_px=1)
    assert get_registration_profile('unknown') is get_registration_profile('None')


def test_scene_supported_unsupported_palette_invalid_recovery(document_light,qtbot):
    d = document_light
    d.page_layout = layout()
    scene = PageScene(d,RenderMode.ON_SCREEN)
    roots = scene.print_markers.copy()
    assert len(roots) == 8 and not scene.geometry.placements
    d.apply(ActionAddCard(create_card_with_pixmap('Local'),1))
    assert scene.print_markers == roots
    assert len(roots) == 8 and len(scene.card_items) == 1
    palette = QPalette(scene.palette())
    palette.setColor(QPalette.ColorRole.Base,QColorConstants.DarkGray)
    scene.setPalette(palette)
    assert scene.background.brush().color() == QColorConstants.White
    d.page_layout = layout('A4',paper_orientation='Landscape')
    d.page_layout_changed.emit(d.page_layout)
    assert scene.print_markers == roots and not scene.registration_unavailable_reason
    d.page_layout = layout('A4')
    d.page_layout_changed.emit(d.page_layout)  # Expected failure must not escape a Qt slot.
    assert scene.geometry is not None and not scene.geometry_pending
    assert scene.registration_unavailable_reason and not scene.print_markers
    assert len(scene.card_items) == 1 and all(root.scene() is None for root in roots)
    d.page_layout = layout()
    d.page_layout_changed.emit(d.page_layout)
    assert len(scene.print_markers) == 8 and scene.registration_unavailable_reason is None
    d.page_layout = layout('Custom',custom_page_width=20*mm,custom_page_height=20*mm)
    d.page_layout_changed.emit(d.page_layout)
    assert scene.geometry is None and not scene.print_markers
    d.page_layout = layout()
    d.page_layout_changed.emit(d.page_layout)
    assert len(scene.print_markers) == 8 and scene.geometry is not None
    d.page_layout.print_registration_marks_style = 'None'
    d.page_layout_changed.emit(d.page_layout)
    assert not scene.print_markers and scene.background.brush().color() == QColorConstants.DarkGray
    d.page_layout.print_registration_marks_style = 'Siser'
    d.page_layout_changed.emit(d.page_layout)
    assert len(scene.print_markers) == 8 and scene.background.brush().color() == QColorConstants.White
    scene.clear()


@pytest.mark.parametrize('dpi',[300,600])
@pytest.mark.parametrize('paper,orientation,count,box',[
    ('Letter','Portrait',9,(612,792)),('A4','Landscape',4,(842,595)),
])
def test_actual_pdf_bars_rounded_trims_rulers(qtbot,dpi,paper,orientation,count,box):
    g = geometry(paper,count,paper_orientation=orientation)
    page = PdfReader(BytesIO(render_calibration_pdf(g,'Siser',output_dpi=dpi))).pages[0]
    assert (float(page.mediabox.width),float(page.mediabox.height)) == box
    actual = filled_bounds(page)
    expected = sorted(rect_values(b.bounds_mm) for b in resolve_siser_page_marks(g).bars)
    assert len(actual) == len(expected) == 8
    for a,b in zip(actual,expected):
        assert a == pytest.approx(b,abs=.001,rel=0)
    contours = [commands for commands,closed in stroked_commands(page) if closed]
    assert len(contours) == count and all(sum(c=='C' for c,p in commands)==4 for commands in contours)
    for observed,placement in zip([bounds(p) for p,closed in stroked_paths(page) if closed],g.placements):
        assert observed == pytest.approx(rect_values(placement.trim_mm),abs=.01,rel=0)
    rulers = [max(bounds(p)[2:]) for p,closed in stroked_paths(page) if not closed and len(p)==2 and max(bounds(p)[2:])>49]
    assert rulers == pytest.approx([50,50],abs=.01,rel=0)


def test_conflicting_bleed_graphic_contact_and_overhang_export_without_assessment(qtbot):
    g = geometry(card_bleed=1.5*mm)
    original = deepcopy(g)
    builder = calibration._build_calibration_scene
    def overlapping(*args):
        scene,roots = builder(*args)
        # Printed line contacts a bar and extends beyond the nominal page.
        scene.addLine(-distance_to_px(2*mm),distance_to_px(6*mm),distance_to_px(20*mm),distance_to_px(6*mm),
                      QPen(QColorConstants.Black,distance_to_px(.1*mm)))
        return scene,roots
    with patch('mtg_proxy_printer.siser_page_marks.assess_siser_clearance',side_effect=AssertionError('No mandatory assessment')), \
            patch.object(calibration,'_build_calibration_scene',side_effect=overlapping):
        page = PdfReader(BytesIO(render_calibration_pdf(g,'Siser'))).pages[0]
    assert len(filled_bounds(page)) == 8 and g == original
    assert min(p[0] for points,closed in stroked_paths(page) for p in points) < 0
    for got,placement in zip([bounds(p) for p,closed in stroked_paths(page) if closed],g.placements):
        assert got == pytest.approx(rect_values(placement.trim_mm),abs=.01,rel=0)


def test_empty_and_oversized_calibration_remain_available(qtbot):
    for kind,count in [(PageType.UNDETERMINED,0),(PageType.OVERSIZED,1)]:
        g = build_page_geometry(layout(),kind,count)
        page = PdfReader(BytesIO(render_calibration_pdf(g,'Siser'))).pages[0]
        assert len(filled_bounds(page)) == 8
        assert all(not any(c=='C' for c,p in commands) for commands,closed in stroked_commands(page) if closed)
    with pytest.raises(ValueError,match='Supported configurations'):
        render_calibration_pdf(geometry('A4',0),'Siser')


def test_direct_output_guards_and_png_lifecycle(document_light,tmp_path,qtbot):
    d = document_light; d.page_layout = layout('A4')
    path = tmp_path/'untouched.pdf'; path.write_bytes(b'original')
    signal = Mock()
    with pytest.raises(RuntimeError,match='does not support'):
        printing.PDFPrinter(d,str(path),signal)
    assert path.read_bytes() == b'original'
    with pytest.raises(RuntimeError):
        printing.export_pdf(d,str(path),Mock())
    with pytest.raises(RuntimeError):
        printing.Renderer(d)
    task = printing.PNGRenderer(None,d,str(tmp_path/'out.png'))
    errors,completed,locks,progress = [],[],[],[]
    task.error_occurred.connect(errors.append)
    task.task_completed.connect(lambda:completed.append(True))
    task.ui_lock_acquire.connect(lambda:locks.append(True))
    task.advance_progress.connect(lambda:progress.append(True))
    with patch.object(printing,'QThreadPool',side_effect=AssertionError('No encoders')):
        task.run()
    assert len(errors) == len(completed) == 1 and not locks and not progress
    assert not list(tmp_path.glob('out*.png'))


def test_operation_time_guards_and_existing_pdf_success(document_light,tmp_path,qtbot):
    d = document_light; d.page_layout = PageLayoutSettings(paper_size='Letter')
    d.apply(ActionAddCard(create_card_with_pixmap('Local'),1))
    from tests.test_pdf_export import AdvanceSignal
    signal = AdvanceSignal()
    writer = printing.PDFPrinter(d,str(tmp_path/'good.pdf'),signal.advance_progress)
    writer.run()
    assert len(PdfReader(tmp_path/'good.pdf').pages) == 1
    renderer = printing.Renderer(d)
    pending = printing.PDFPrinter(d,str(tmp_path/'pending.pdf'),signal.advance_progress)
    task = printing.PNGRenderer(None,d,str(tmp_path/'pending.png'))
    d.page_layout.print_registration_marks_style = 'Siser'
    d.page_layout.paper_size = 'A4'
    with patch.object(printing.QPainter,'begin',side_effect=AssertionError('No painter startup')):
        with pytest.raises(RuntimeError): pending.run()
        with pytest.raises(RuntimeError): renderer.print_document(Mock())
    with qtbot.waitSignal(task.error_occurred): task.run()


class RouteHost(QWidget):
    _artwork_output_allowed = MainWindow._artwork_output_allowed
    on_action_print_triggered = MainWindow.on_action_print_triggered
    on_action_print_preview_triggered = MainWindow.on_action_print_preview_triggered
    on_action_print_pdf_triggered = MainWindow.on_action_print_pdf_triggered
    on_action_export_png_triggered = MainWindow.on_action_export_png_triggered
    on_action_export_calibration_triggered = MainWindow.on_action_export_calibration_triggered
    on_action_export_cut_template_triggered = MainWindow.on_action_export_cut_template_triggered
    on_dialog_finished = MainWindow.on_dialog_finished

    def __init__(self,document):
        super().__init__(); self.document = document; self.current_dialog = None
        self.on_error_occurred = Mock(); self.missing_images_manager = Mock()
        self.request_run_async_task = Mock()
        self._ask_user_about_compacting_document = Mock(side_effect=AssertionError('No compaction'))


def test_ui_guards_and_calibration_svg_access(document_light,qtbot,monkeypatch,tmp_path):
    monkeypatch.setattr(main_window,'UI_LOCK_SEMAPHORE',0)
    monkeypatch.setattr(dialogs,'read_path',lambda *a:str(tmp_path))
    d = document_light; d.page_layout = layout('A4',card_bleed=1.5*mm)
    d.apply(ActionAddCard(create_card_with_pixmap('Local'),9))
    host = RouteHost(d); qtbot.addWidget(host)
    for action in (host.on_action_print_triggered,host.on_action_print_preview_triggered,
                   host.on_action_print_pdf_triggered,host.on_action_export_png_triggered):
        action()
    assert host.on_error_occurred.call_count == 4
    host.missing_images_manager.obtain_missing_images.assert_not_called()
    d.page_layout.paper_size = 'Letter'
    with patch.object(dialogs.SaveCalibrationPDFDialog,'open'):
        host.on_action_export_calibration_triggered()
    assert host.current_dialog is not None
    host.current_dialog.reject()
    with patch.object(dialogs.SaveCutTemplateDialog,'open'):
        host.on_action_export_cut_template_triggered()
    assert host.current_dialog is not None
    host.current_dialog.reject()
    assert host.on_error_occurred.call_count == 4


def test_png_dialog_rechecks_before_tasks_and_print_count(document_light,qtbot,monkeypatch,tmp_path):
    monkeypatch.setattr(dialogs,'read_path',lambda *a:str(tmp_path))
    host = RouteHost(document_light); qtbot.addWidget(host)
    document_light.page_layout = PageLayoutSettings(paper_size='Letter')
    dialog = dialogs.SavePNGDialog(host,document_light); qtbot.addWidget(dialog)
    document_light.page_layout.print_registration_marks_style = 'Siser'
    document_light.page_layout.paper_size = 'A4'
    with qtbot.assertNotEmitted(dialog.request_run_async_task):
        dialog.on_accept()
    host.on_error_occurred.assert_called_once()
