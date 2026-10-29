"""Software QPrinter adapter tests; never submit NativeFormat jobs."""
from unittest.mock import Mock, patch
from types import SimpleNamespace

import pytest
from pypdf import PdfReader
from PySide6.QtCore import QMarginsF, QRectF, Qt
from PySide6.QtGui import QPainter, QImage, QColor, QPageLayout, QPageSize
from PySide6.QtPrintSupport import QPrinter

import mtg_proxy_printer.print as printing
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.page_scene.page_scene import PageScene, RenderMode
from mtg_proxy_printer.settings import settings
from mtg_proxy_printer.units_and_sizes import CardSizes, unit_registry, PageSizeManager
from tests.test_export_mapping import export_document, card, image_placements, bounds

mm = unit_registry.mm


def software_printer(document, path, dpi=300, margins=None, rotate=False):
    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
    printer.setOutputFileName(str(path))
    printer.setResolution(dpi)
    with patch.dict(settings['printer'], {'landscape-compatibility-workaround': str(rotate)}):
        layout = document.page_layout.to_page_layout(RenderMode.NATIVE_PRINT)
    layout.setMode(QPageLayout.Mode.FullPageMode if margins is None else QPageLayout.Mode.StandardMode)
    assert layout.setMargins(margins or QMarginsF())
    assert printer.setPageLayout(layout)
    return printer


@pytest.mark.parametrize('dpi', [300, 600])
@pytest.mark.parametrize('standard', [False, True])
def test_native_physical_coordinates(export_document, tmp_path, dpi, standard):
    d = export_document
    d.apply(ActionAddCard(card(), 1))
    printer = software_printer(d, tmp_path/'native.pdf', dpi,
                               QMarginsF(3.17, 5.23, 7.41, 9.67) if standard else None)
    with patch.dict(settings['printer'], {'landscape-compatibility-workaround': 'False', 'horizontal-offset': '0 mm'}):
        renderer = printing.Renderer(d)
        assert renderer.scene.x_offset == 0
        assert renderer.scene.width() == 2480
        assert renderer.print_document(printer)
    page = PdfReader(tmp_path/'native.pdf').pages[0]
    measured = bounds(image_placements(page)[0])
    expected = [10.3716667,16.4253333,63.0766667,88.0533333]
    if standard:
        # Independent Qt backend pageMatrix uses integral paintRectPixels origins.
        layout = printer.pageLayout()
        physical = layout.paintRect(QPageLayout.Unit.Millimeter)
        device = layout.paintRectPixels(dpi)
        residual = (device.x()*25.4/dpi-physical.x(), device.y()*25.4/dpi-physical.y())
        assert max(abs(v) for v in residual) <= .5*25.4/dpi
        expected[0] += residual[0]
        expected[1] += residual[1]
    assert measured == pytest.approx(expected, abs=.01)


@pytest.mark.parametrize('custom', [False, True])
@pytest.mark.parametrize('rotate', [False, True])
def test_native_landscape_target_pages(export_document, tmp_path, custom, rotate):
    d = export_document
    d.page_layout.paper_orientation = 'Landscape'
    if custom:
        d.page_layout.paper_size = 'Custom'
        d.page_layout.custom_page_width = 12*unit_registry.inch
        d.page_layout.custom_page_height = 8*unit_registry.inch
    d.page_layout.margin_left = 13*mm
    d.page_layout.margin_top = 7*mm
    d.apply(ActionAddCard(card(), 1))
    d.apply(ActionNewPage(count=3, content=[[card('blue',CardSizes.OVERSIZED)]*2, [card()]*3, []]))
    selected = d.currently_edited_page
    printer = software_printer(d, tmp_path/'pages.pdf', rotate=rotate)
    with patch.dict(settings['printer'], {'landscape-compatibility-workaround': str(rotate), 'horizontal-offset': '2 mm'}):
        renderer = printing.Renderer(d)
        assert renderer.print_document(printer)
    assert d.currently_edited_page is selected
    pages = PdfReader(tmp_path/'pages.pdf').pages
    assert len(pages) == 4
    assert [len(image_placements(p)) for p in pages] == [1,2,3,0]
    for number, page in enumerate(pages):
        renderer.scene.on_current_page_changed(d.index(number,0))
        g = renderer.scene.geometry
        for actual, placement in zip(image_placements(page), g.placements):
            r = placement.trim_mm
            correction = 24*25.4/300
            expected = (g.sheet_height_mm-r.y-r.height+correction,r.x,r.height,r.width) if rotate else (r.x+correction,r.y,r.width,r.height)
            assert bounds(actual) == pytest.approx(expected,abs=.01)


@pytest.mark.parametrize('name', ['A4','Ledger','Custom'])
@pytest.mark.parametrize('rotate', [False, True])
def test_paper_conversion_units_and_intrinsic_orientation(name, rotate):
    layout = PageLayoutSettings(paper_size=name, paper_orientation='Portrait',
                                custom_page_width=12*unit_registry.inch, custom_page_height=8*unit_registry.inch,
                                margin_left=1*mm,margin_top=2*mm,margin_right=3*mm,margin_bottom=4*mm)
    intended = (layout.page_width.to(mm).magnitude, layout.page_height.to(mm).magnitude)
    if rotate and intended[0] > intended[1]:
        intended = intended[::-1]
    with patch.dict(settings['printer'], {'landscape-compatibility-workaround': str(rotate)}):
        actual = layout.to_page_layout(RenderMode.IMPLICIT_MARGINS)
    full = actual.fullRect(QPageLayout.Unit.Millimeter)
    assert (full.width(),full.height()) == pytest.approx(intended, abs=25.4/72)
    assert actual.margins(QPageLayout.Unit.Millimeter) == QMarginsF(1,2,3,4)
    if name != 'Custom':
        assert actual.pageSize().id() == PageSizeManager.PageSize[name]


@pytest.mark.parametrize('rotate', [False, True])
@pytest.mark.parametrize('correction', [24,-24])
def test_observable_anisotropic_mapping_and_clip(export_document, rotate, correction):
    d = export_document
    d.page_layout.paper_orientation = 'Landscape' if rotate else 'Portrait'
    scene = PageScene(d, RenderMode.ON_PAPER|RenderMode.NATIVE_PRINT)
    image = QImage(800,600,QImage.Format.Format_RGB888)
    image.fill(QColor('white'))
    painter = QPainter(image)
    painter.setClipRect(QRectF(0,0,450,500))
    original = painter.transform()
    observed = []
    def render(p, **kwargs):
        observed.append((p.transform().map(122.5,194),p.transform().map(867.5,1234),p.clipBoundingRect()))
        # Draw outside accepted paint area to verify the initial device clip is retained.
        p.fillRect(QRectF(-10000,-10000,20000,20000),QColor('red'))
        assert kwargs['source'] == kwargs['target']
        assert kwargs['aspectRatioMode'] == Qt.AspectRatioMode.IgnoreAspectRatio
    try:
        with patch.object(scene,'render',side_effect=render):
            printing._render_page(scene,painter,600,300,rotate,QRectF(3.17,5.23,20,30),correction)
        assert painter.transform() == original
    finally:
        painter.end()
    first,second,_ = observed[0]
    # Known A4 floating height for rotation is 210 mm, not the rounded 2480 extent.
    if rotate:
        expected = ((210-16.4253333+correction*25.4/300-3.17)*600/25.4,
                    (10.3716667-5.23)*300/25.4)
        delta = (-88.0533333*600/25.4,63.0766667*300/25.4)
    else:
        expected = ((10.3716667+correction*25.4/300-3.17)*600/25.4,
                    (16.4253333-5.23)*300/25.4)
        delta = (63.0766667*600/25.4,88.0533333*300/25.4)
    assert first == pytest.approx(expected,abs=.001)
    assert (second[0]-first[0],second[1]-first[1]) == pytest.approx(delta,abs=.001)
    assert image.pixelColor(400,200) == QColor('red')
    assert image.pixelColor(460,200) == QColor('white')  # existing clip is narrower than native clip
    assert image.pixelColor(500,200) == QColor('white')
    assert image.pixelColor(200,400) == QColor('white')

class SetupPrinter:
    """Small driver-policy stub, never a hardware paint device."""
    def __init__(self, valid=True, reject=False):
        self.valid, self.reject = valid, reject
        self.events = []
        self.layout = QPageLayout(QPageSize(QPageSize.PageSizeId.Letter),
                                  QPageLayout.Orientation.Portrait, QMarginsF(), QPageLayout.Unit.Millimeter)
    def isValid(self):
        return self.valid
    def setOutputFormat(self, value):
        self.events.append(('format',value))
    def setResolution(self, value):
        self.events.append(('resolution',value))
    def setDuplex(self, value):
        self.events.append(('duplex',value))
    def setFullPage(self, value):
        self.events.append(('full',value))
        self.layout.setMode(QPageLayout.Mode.FullPageMode)
    def setPageOrientation(self, value):
        self.events.append(('orientation',value))
        self.layout.setOrientation(value)
        return True
    def setPageSize(self, value):
        self.events.append(('size',value))
        if self.reject:
            return False
        self.layout.setPageSize(value, QMarginsF(3.17,5.23,7.41,9.67))
        return True
    def pageLayout(self):
        return QPageLayout(self.layout)
    def setPageLayout(self, value):
        self.events.append(('layout',value))
        self.layout = QPageLayout(value)
        return True


@pytest.mark.parametrize('full_page',[False,True])
def test_initial_setup_order_refreshed_minima_and_rejection(export_document, full_page, caplog):
    renderer = printing.Renderer(export_document)
    for reject in (False,True):
        device = SetupPrinter(reject=reject)
        with patch.object(printing,'QPrinter',side_effect=lambda *args: device) as factory, patch.dict(settings['printer'], {'borderless-printing':str(full_page),'landscape-compatibility-workaround':'False'}):
            # Preserve enum access on the patched constructor.
            factory.PrinterMode = QPrinter.PrinterMode
            factory.OutputFormat = QPrinter.OutputFormat
            factory.DuplexMode = QPrinter.DuplexMode
            assert printing.create_printer(renderer) is device
        names = [name for name,_ in device.events]
        assert names[0] == 'format'
        assert names.index('orientation') < names.index('size') < names.index('layout')
        assert device.layout.mode() == (QPageLayout.Mode.FullPageMode if full_page else QPageLayout.Mode.StandardMode)
        if not reject:
            assert device.layout.margins(QPageLayout.Unit.Millimeter) == (QMarginsF() if full_page else QMarginsF(3.17,5.23,7.41,9.67))
    assert 'rejected paper' in caplog.text.lower()
    invalid = SetupPrinter(valid=False)
    with patch.object(printing,'QPrinter',side_effect=lambda *args: invalid) as factory:
        factory.PrinterMode = QPrinter.PrinterMode
        factory.OutputFormat = QPrinter.OutputFormat
        assert printing.create_printer(renderer) is invalid
    assert [name for name,_ in invalid.events] == ['format']


def test_accepted_resolution_and_choices_are_preserved(export_document,tmp_path):
    export_document.apply(ActionAddCard(card(),1))
    printer = software_printer(export_document,tmp_path/'accepted.pdf',600,QMarginsF(3.17,5.23,7.41,9.67))
    before = QPageLayout(printer.pageLayout())
    setter = Mock(wraps=printer.setResolution)
    printer.setResolution = setter
    with patch.dict(settings['printer'], {'landscape-compatibility-workaround':'False','horizontal-offset':'0 mm','borderless-printing':'True'}):
        printing.Renderer(export_document).print_document(printer)
    setter.assert_called_once_with(600)
    assert printer.resolution() == 600
    assert printer.pageLayout() == before


@pytest.mark.parametrize('difference,accepted',[(.3,True),(.36,False),(5,False)])
def test_paper_allowance_before_painter_start(export_document,tmp_path,difference,accepted):
    printer = software_printer(export_document,tmp_path/'tolerance.pdf')
    layout = printer.pageLayout()
    # Independent accepted layout description avoids QPageSize identity/snapping in this policy test.
    metrics = Mock(wraps=layout)
    metrics.fullRect.return_value = QRectF(0,0,210+difference,297)
    metrics.paintRect.return_value = QRectF(0,0,210,297)
    printer.pageLayout = lambda: metrics
    renderer = printing.Renderer(export_document)
    with patch.dict(settings['printer'], {'landscape-compatibility-workaround':'False'}), patch.object(printing,'QPainter') as factory:
        if accepted:
            factory.return_value.begin.return_value = False
            with pytest.raises(RuntimeError,match='Cannot start printer painter'):
                renderer.print_document(printer)
            factory.return_value.begin.assert_called_once()
        else:
            with pytest.raises(RuntimeError,match='Required paper.*Choose matching paper'):
                renderer.print_document(printer)
            factory.return_value.begin.assert_not_called()


@pytest.mark.parametrize('failure',['begin','geometry','transition','dpi','backend-paper','end'])
def test_native_failures_cleanup(export_document,tmp_path,failure):
    d = export_document
    d.apply(ActionAddCard(card(),1))
    d.apply(ActionNewPage())
    printer = software_printer(d,tmp_path/'fail.pdf')
    renderer = printing.Renderer(d)
    painter = Mock()
    painter.begin.return_value = failure != 'begin'
    painter.isActive.return_value = failure not in ('begin','geometry')
    painter.end.return_value = failure != 'end'
    if failure == 'geometry':
        renderer.scene.require_geometry_ready = Mock(side_effect=RuntimeError('unresolved geometry'))
    if failure == 'dpi':
        printer.logicalDpiX = lambda: 0
    if failure == 'transition':
        printer.newPage = lambda: False
    if failure == 'backend-paper':
        original = printer.pageLayout
        calls = 0
        def layout():
            nonlocal calls
            calls += 1
            if calls > 1:
                return QPageLayout(QPageSize(QPageSize.PageSizeId.Letter),QPageLayout.Orientation.Portrait,QMarginsF(),QPageLayout.Unit.Millimeter)
            return original()
        printer.pageLayout = layout
    with patch.dict(settings['printer'], {'landscape-compatibility-workaround':'False'}), patch.object(printing,'QPainter',return_value=painter), patch.object(renderer.scene,'render') as render:
        with pytest.raises(RuntimeError) as error:
            renderer.print_document(printer)
        if failure != 'end':
            assert 'output page' in str(error.value)
        if failure in ('begin','geometry','dpi','backend-paper'):
            render.assert_not_called()
    if failure not in ('begin','geometry'):
        painter.end.assert_called_once()


def test_primary_render_failure_survives_cleanup(export_document,tmp_path):
    renderer = printing.Renderer(export_document)
    printer = software_printer(export_document,tmp_path/'primary.pdf')
    painter = Mock()
    painter.begin.return_value = True
    painter.isActive.return_value = True
    painter.end.side_effect = RuntimeError('secondary cleanup')
    with patch.dict(settings['printer'], {'landscape-compatibility-workaround':'False'}), patch.object(printing,'QPainter',return_value=painter), patch.object(renderer.scene,'render',side_effect=RuntimeError('primary rejected render')):
        with pytest.raises(RuntimeError,match='primary rejected render'):
            renderer.print_document(printer)
    painter.end.assert_called_once()


def test_print_and_preview_reporting_recovery_and_count(export_document,tmp_path,qtbot):
    from mtg_proxy_printer.ui.dialogs import PrintDialog, PrintPreviewDialog
    printer = software_printer(export_document,tmp_path/'dialog.pdf')
    wrong = QPageLayout(printer.pageLayout())
    wrong.setPageSize(QPageSize(QPageSize.PageSizeId.Letter))
    assert printer.setPageLayout(wrong)
    with patch.object(printing,'create_printer',return_value=printer):
        dialog = PrintDialog(export_document)
        preview = PrintPreviewDialog(export_document)
    qtbot.addWidget(dialog)
    qtbot.addWidget(preview)
    counts, errors, preview_errors = Mock(),Mock(),Mock()
    dialog.request_run_async_task.connect(counts)
    dialog.error_occurred.connect(errors)
    preview.error_occurred.connect(preview_errors)
    with patch.dict(settings['printer'], {'landscape-compatibility-workaround':'False','horizontal-offset':'0 mm'}):
        dialog._print_accepted(printer)
        preview._render_preview(printer)
        assert 'Choose matching paper' in errors.call_args.args[0]
        preview_errors.assert_called_once()
        counts.assert_not_called()
        assert printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        dialog._print_accepted(printer)
        counts.assert_called_once()
        preview._render_preview(printer)
        counts.assert_called_once()


def test_empty_model_no_job_and_ui_wording(export_document,qtbot):
    renderer = printing.Renderer(export_document)
    with patch.object(export_document,'rowCount',return_value=0), patch.object(printing,'QPainter') as painter:
        assert renderer.print_document(Mock()) is False
        painter.assert_not_called()
    from mtg_proxy_printer.ui.common import load_ui_from_file
    from PySide6.QtWidgets import QWidget
    widget = QWidget()
    qtbot.addWidget(widget)
    ui = load_ui_from_file('settings_window/printer_settings_page')()
    ui.setupUi(widget)
    assert ui.printer_use_borderless_printing.text() == 'Use full-page printer coordinates'
    assert 'printer driver' in ui.printer_use_borderless_printing.toolTip()
    assert 'after landscape rotation' in ui.horizontal_offset.toolTip()

@pytest.mark.parametrize('rotate',[False,True])
def test_correction_moves_cards_guides_marks_title_and_labels_once(export_document,rotate):
    d = export_document
    d.page_layout.paper_orientation = 'Landscape' if rotate else 'Portrait'
    d.page_layout.document_name = 'Mapping title'
    d.page_layout.draw_page_numbers = True
    d.page_layout.cut_marker_style = 'Solid'
    d.page_layout.print_registration_marks_style = 'Bullseye'
    d.apply(ActionAddCard(card(),1))
    with patch.dict(settings['printer'], {'horizontal-offset':'5 mm'}):
        scene = PageScene(d,RenderMode.ON_PAPER|RenderMode.NATIVE_PRINT)
    assert scene.x_offset == 0
    assert scene.document_title_text.text()
    items = scene.card_items + scene.cut_lines + scene.print_markers + [scene.document_title_text,scene.page_number_text]
    image = QImage(100,100,QImage.Format.Format_RGB888)
    painter = QPainter(image)
    samples = []
    def inspect(p,**kwargs):
        samples.append([p.transform().map(item.scenePos()) for item in items])
    try:
        with patch.object(scene,'render',side_effect=inspect):
            printing._render_page(scene,painter,600,300,rotate,QRectF(3.17,5.23,100,100),0)
            printing._render_page(scene,painter,600,300,rotate,QRectF(3.17,5.23,100,100),24)
    finally:
        painter.end()
    for before,after in zip(*samples):
        assert (after.x()-before.x(),after.y()-before.y()) == pytest.approx((48,0),abs=1e-8)


@pytest.mark.parametrize('preview',[False,True])
def test_main_window_reports_construction_failure(preview):
    import mtg_proxy_printer.ui.main_window as module
    from PySide6.QtWidgets import QMessageBox
    fake = SimpleNamespace(document=Mock(),current_dialog='retained',tr=lambda text,*args:text,
                           _ask_user_about_compacting_document=lambda action:QMessageBox.StandardButton.No,
                           _artwork_output_allowed=lambda: True, on_error_occurred=Mock())
    name = 'PrintPreviewDialog' if preview else 'PrintDialog'
    method = module.MainWindow.on_action_print_preview_triggered if preview else module.MainWindow.on_action_print_triggered
    with patch.object(module,name,side_effect=RuntimeError('construction failure')):
        method(fake)
    fake.on_error_occurred.assert_called_once_with('construction failure')
    assert fake.current_dialog == 'retained'

@pytest.mark.parametrize('rotate',[False,True])
def test_marked_native_software_example(export_document,tmp_path,rotate):
    d = export_document
    d.page_layout.paper_orientation = 'Landscape' if rotate else 'Portrait'
    d.page_layout.document_name = 'M06 mapping'
    d.page_layout.draw_page_numbers = True
    d.page_layout.cut_marker_style = 'Solid'
    d.page_layout.cut_marker_width = .2*mm
    d.page_layout.print_registration_marks_style = 'Bullseye'
    d.page_layout.margin_left = d.page_layout.margin_top = 10*mm
    d.page_layout.margin_right = d.page_layout.margin_bottom = 10*mm
    d.apply(ActionAddCard(card(),2))
    printer = software_printer(d,tmp_path/'marked.pdf',600,QMarginsF(3.17,5.23,7.41,9.67),rotate)
    with patch.dict(settings['printer'],{'landscape-compatibility-workaround':str(rotate),'horizontal-offset':'2 mm'}):
        assert printing.Renderer(d).print_document(printer)
    page = PdfReader(tmp_path/'marked.pdf').pages[0]
    # Existing Bullseye marks are raster images too; distinguish the card-sized operations.
    cards = [bounds(points) for points in image_placements(page) if min(bounds(points)[2:]) > 50]
    assert len(cards) == 2
    assert page.mediabox.width < page.mediabox.height


@pytest.mark.parametrize('bad',['resolution','paint','mode'])
def test_unusable_accepted_metrics_rejected(export_document,tmp_path,bad):
    printer = software_printer(export_document,tmp_path/'bad.pdf')
    if bad == 'resolution':
        printer.resolution = lambda: 0
    else:
        layout = printer.pageLayout()
        metrics = Mock(wraps=layout)
        metrics.mode.return_value = layout.mode() if bad != 'mode' else -1
        if bad == 'paint':
            metrics.paintRect.return_value = QRectF(0,0,0,10)
        printer.pageLayout = lambda: metrics
    with patch.object(printing,'QPainter') as painter:
        with pytest.raises(RuntimeError,match='positive|unusable'):
            printing.Renderer(export_document).print_document(printer)
        painter.return_value.begin.assert_not_called()
