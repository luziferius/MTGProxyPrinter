"""Measure files written by the exporters, independently of their mapping helper."""
from unittest.mock import Mock, patch

import pytest
from pypdf import PdfReader
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor, QImage, QPixmap, QPainter

import mtg_proxy_printer.print as printing
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.page_scene.page_scene import PageScene, RenderMode
from mtg_proxy_printer.settings import settings
from mtg_proxy_printer.units_and_sizes import CardSizes, RESOLUTION, unit_registry
from tests.helpers import create_card

mm = unit_registry.mm

class Progress(QObject):
    advance = Signal()

@pytest.fixture
def export_document(document_light):
    document_light.page_layout = PageLayoutSettings(paper_size='A4', draw_sharp_corners=True)
    return document_light


def card(color='red', size=CardSizes.REGULAR):
    image = QImage(size.as_qsize_px(), QImage.Format.Format_RGB888)
    image.fill(QColor(color))
    return create_card(color, size, pixmap=QPixmap.fromImage(image))


def pdf(document, path, dpi=300, rotate=False, index=0, limit=None):
    progress = Progress()
    with patch.dict(settings['export'], {'landscape-compatibility-workaround': str(rotate)}):
        writer = printing.PDFPrinter(document, str(path), progress.advance, document_index=index, pages_to_print=limit)
        writer.setResolution(dpi)
        writer.run()
    assert not writer.painter.isActive()
    return writer


def image_placements(page):
    """Only synthetic Qt image Do operations; pypdf resolves the surrounding CTM."""
    result = []
    height = float(page.mediabox.height)
    def visit(operator, operands, cm, tm):
        if operator != b'Do':
            return
        obj = page['/Resources']['/XObject'][operands[0]].get_object()
        if obj['/Subtype'] != '/Image':
            return
        a,b,c,d,e,f = cm
        points = [(e, f), (a+e,b+f), (c+e,d+f), (a+c+e,b+d+f)]
        result.append([(x*25.4/72, (height-y)*25.4/72) for x,y in points])
    page.extract_text(visitor_operand_before=visit)
    return result


def bounds(points):
    xs,ys=zip(*points)
    return min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys)


def red_bounds(image, rgb=b"\xff\x00\x00"):
    image = image.convertToFormat(QImage.Format.Format_RGB888)
    raw = bytes(image.constBits())
    stride = image.bytesPerLine()
    rows = []
    for y in range(image.height()):
        row = raw[y*stride:y*stride+image.width()*3]
        start,end = row.find(rgb),row.rfind(rgb)
        if start >= 0:
            rows.append((y,start//3,end//3))
    if not rows:
        return None
    return min(r[1] for r in rows),rows[0][0],max(r[2] for r in rows)+1,rows[-1][0]+1

PAPERS = [
    ('A4','Portrait',None,(210,297),(2480,3508),(595,842)),
    ('A4','Landscape',None,(297,210),(3508,2480),(842,595)),
    ('Letter','Portrait',None,(215.9,279.4),(2550,3300),(612,792)),
    ('Custom','Portrait',(12*unit_registry.inch,8*unit_registry.inch),(304.8,203.2),(3600,2400),(864,576)),
    ('Custom','Landscape',(304.8*mm,203.2*mm),(304.8,203.2),(3600,2400),(864,576)),
    ('Custom','Landscape',(210.6*mm,297.6*mm),(210.6,297.6),(2487,3515),(597,844)),
]

@pytest.mark.parametrize('name,orientation,custom,physical,pixels,points', PAPERS)
def test_paper_files(export_document,tmp_path,name,orientation,custom,physical,pixels,points):
    d=export_document
    d.page_layout.paper_size=name
    d.page_layout.paper_orientation=orientation
    if custom:
        d.page_layout.custom_page_width,d.page_layout.custom_page_height=custom
    d.apply(ActionAddCard(card(),1))
    pdf(d,tmp_path/'paper.pdf')
    page=PdfReader(tmp_path/'paper.pdf').pages[0]
    assert (float(page.mediabox.width),float(page.mediabox.height)) == points
    scene=PageScene(d,RenderMode.ON_PAPER|RenderMode.FILE_EXPORT)
    assert (scene.geometry.sheet_width_mm,scene.geometry.sheet_height_mm) == pytest.approx(physical)
    trim = scene.geometry.placements[0].trim_mm
    assert bounds(image_placements(page)[0]) == pytest.approx(
        (trim.x, trim.y, trim.width, trim.height), abs=.01)
    task=printing.PNGRenderer(None,d,str(tmp_path/'paper.png'))
    task.run()
    image=QImage(str(tmp_path/'paper-1.png'))
    assert (image.width(),image.height()) == pixels
    assert image.dotsPerMeterX() == image.dotsPerMeterY() == 11811
    assert image.devicePixelRatio() == 1

@pytest.mark.parametrize('dpi',[300,600])
def test_independent_a4_card_coordinates(export_document,tmp_path,dpi):
    d=export_document
    d.apply(ActionAddCard(card(),1))
    pdf(d,tmp_path/'card.pdf',dpi)
    page=PdfReader(tmp_path/'card.pdf').pages[0]
    assert bounds(image_placements(page)[0]) == pytest.approx((10.3716667,16.4253333,63.0766667,88.0533333),abs=.01)
    task=printing.PNGRenderer(None,d,str(tmp_path/'card.png'))
    task._output_dpi=dpi
    task.run()
    image=QImage(str(tmp_path/'card-1.png'))
    expected=(122.5,194,867.5,1234)
    assert red_bounds(image) == pytest.approx(tuple(v*dpi/300 for v in expected),abs=1)
    assert image.dotsPerMeterX() == image.dotsPerMeterY() == round(dpi/.0254)
    assert RESOLUTION.magnitude == 300

@pytest.mark.parametrize('rotate',[False,True])
@pytest.mark.parametrize('custom',[False,True])
def test_rotation_and_target_pages(export_document,tmp_path,rotate,custom):
    d=export_document
    d.page_layout.paper_orientation='Landscape'
    if custom:
        d.page_layout.paper_size='Custom'
        d.page_layout.custom_page_width=12*unit_registry.inch
        d.page_layout.custom_page_height=8*unit_registry.inch
    d.page_layout.margin_left=13*mm
    d.page_layout.margin_top=7*mm
    d.apply(ActionAddCard(card(),1))
    d.apply(ActionNewPage(count=3,content=[[card('blue',CardSizes.OVERSIZED)]*2,[card()]*3,[]]))
    selected=d.currently_edited_page
    writer=pdf(d,tmp_path/'pages.pdf',rotate=rotate)
    reader=PdfReader(tmp_path/'pages.pdf')
    assert len(reader.pages)==4
    assert d.currently_edited_page is selected
    assert [len(image_placements(p)) for p in reader.pages] == [1,2,3,0]
    for number,page in enumerate(reader.pages):
        writer._switch_to_page(number)
        g=writer.scene.geometry
        box=((576,864) if rotate else (864,576)) if custom else ((595,842) if rotate else (842,595))
        assert (float(page.mediabox.width),float(page.mediabox.height)) == box
        for actual,placement in zip(image_placements(page),g.placements):
            r=placement.trim_mm
            expected=(g.sheet_height_mm-r.y-r.height,r.x,r.height,r.width) if rotate else (r.x,r.y,r.width,r.height)
            assert bounds(actual) == pytest.approx(expected,abs=.01)
            # Image unit-square x edge runs down after a clockwise turn, right without it.
            dx,dy=actual[1][0]-actual[0][0],actual[1][1]-actual[0][1]
            assert (dx,dy) == pytest.approx((0,r.width) if rotate else (r.width,0),abs=.01)
            dx,dy=actual[2][0]-actual[0][0],actual[2][1]-actual[0][1]
            # Qt maps the PDF image unit-square Y edge from bottom to top.
            assert (dx,dy) == pytest.approx((r.height,0) if rotate else (0,-r.height),abs=.01)
    task=printing.PNGRenderer(None,d,str(tmp_path/'pages.png'))
    task.run()
    assert sorted(p.name for p in tmp_path.glob('pages-*.png')) == [f'pages-{i}.png' for i in range(1,5)]
    assert red_bounds(QImage(str(tmp_path/'pages-4.png'))) is None
    assert red_bounds(QImage(str(tmp_path/'pages-3.png'))) is not None
    assert QImage(str(tmp_path/'pages-1.png')).size().width()==(3600 if custom else 3508)
    for number in range(3):
        writer._switch_to_page(number)
        trims=[p.trim_px for p in writer.scene.geometry.placements]
        expected=(min(r.x for r in trims),min(r.y for r in trims),
                  max(r.right for r in trims),max(r.bottom for r in trims))
        image=QImage(str(tmp_path/f'pages-{number+1}.png'))
        rgb=b'\x00\x00\xff' if number==1 else b'\xff\x00\x00'
        assert red_bounds(image,rgb) == pytest.approx(expected,abs=1)

@pytest.mark.parametrize('transparent',[False,True])
def test_preferences_alpha_and_split(export_document,tmp_path,transparent):
    d=export_document
    d.apply(ActionAddCard(card(),1))
    d.apply(ActionNewPage(count=2,content=[[card('blue')],[]]))
    with patch.dict(settings['printer'],{'horizontal-offset':'10 mm','borderless-printing':'False','landscape-compatibility-workaround':'True'}), patch.dict(settings['export'],{'png-background-color':'#00000000' if transparent else '#ffffffff'}):
        assert PageScene(d,RenderMode.ON_PAPER).x_offset == 118
        assert PageScene(d,RenderMode.ON_PAPER|RenderMode.FILE_EXPORT).x_offset == 0
        pdf(d,tmp_path/'split.pdf',index=0,limit=2)
        pdf(d,tmp_path/'split.pdf',index=1,limit=2)
        assert [len(PdfReader(p).pages) for p in sorted(tmp_path.glob('split-*.pdf'))] == [2,1]
        page=PdfReader(tmp_path/'split-1.pdf').pages[0]
        assert bounds(image_placements(page)[0])[0] == pytest.approx(10.3716667,abs=.01)
        task=printing.PNGRenderer(None,d,str(tmp_path/'alpha.png'))
        task.run()
    image=QImage(str(tmp_path/'alpha-1.png'))
    assert image.hasAlphaChannel() == transparent
    assert image.pixelColor(0,0).alpha() == (0 if transparent else 255)
    assert red_bounds(image) == pytest.approx((122.5,194,867.5,1234),abs=1)


def test_failure_cleanup(export_document,tmp_path,monkeypatch):
    d=export_document
    d.apply(ActionAddCard(card(),1))
    progress=Progress()
    advanced=Mock()
    progress.advance.connect(advanced)
    writer=printing.PDFPrinter(d,str(tmp_path/'fail.pdf'),progress.advance)
    with patch.object(PageScene,'render',side_effect=RuntimeError('synthetic rejected geometry')):
        with pytest.raises(RuntimeError,match='page 1.*rejected geometry'):
            writer.run()
    assert not writer.painter.isActive()
    advanced.assert_not_called()
    task=printing.PNGRenderer(None,d,str(tmp_path/'fail.png'))
    acquired,released,completed,error=Mock(),Mock(),Mock(),Mock()
    task.ui_lock_acquire.connect(acquired)
    task.ui_lock_release.connect(released)
    task.task_completed.connect(completed)
    task.error_occurred.connect(error)
    painters=[]
    def make_painter():
        painter=QPainter()
        painters.append(painter)
        return painter
    with patch.object(printing,'QPainter',side_effect=make_painter), patch.object(PageScene,'render',side_effect=RuntimeError('synthetic rejected geometry')),patch.object(task,'_compress_single_image') as compress:
        task.run()
    acquired.assert_called_once()
    released.assert_called_once()
    completed.assert_called_once()
    assert 'rejected geometry' in error.call_args.args[0]
    compress.assert_not_called()
    assert not task._running
    assert painters and all(not painter.isActive() for painter in painters)
    assert not list(tmp_path.glob('fail-*.png'))


def test_helper_restores_active_painter(export_document):
    export_document.page_layout.paper_orientation='Landscape'
    scene=PageScene(export_document,RenderMode.ON_PAPER|RenderMode.FILE_EXPORT)
    image=QImage(100,100,QImage.Format.Format_RGB888)
    painter=QPainter(image)
    painter.translate(3,4)
    original=painter.transform()
    try:
        with patch.object(scene,'render',side_effect=RuntimeError('failed')):
            with pytest.raises(RuntimeError):
                printing._render_export_page(scene,painter,600,True)
        assert painter.transform()==original
    finally:
        painter.end()


def test_unresolved_geometry_and_started_encoder_cleanup(export_document,tmp_path):
    d=export_document
    d.apply(ActionAddCard(card(),1))
    progress=Progress()
    advanced=Mock()
    progress.advance.connect(advanced)
    writer=printing.PDFPrinter(d,str(tmp_path/'invalid.pdf'),progress.advance)
    writer.scene.require_geometry_ready=Mock(side_effect=RuntimeError('unresolved geometry'))
    with pytest.raises(RuntimeError,match='unresolved geometry'):
        writer.run()
    assert not writer.painter.isActive()
    advanced.assert_not_called()
    # A previously submitted page must finish; a rejected second page must never be submitted.
    d.apply(ActionNewPage(content=[[card()]]))
    task=printing.PNGRenderer(None,d,str(tmp_path/'partial.png'))
    errors=[]
    success=[]
    task.error_occurred.connect(errors.append)
    task.advance_progress.connect(lambda: success.append(True))
    original=printing._render_export_page
    calls=0
    def fail_second(*args,**kwargs):
        nonlocal calls
        calls+=1
        if calls==2:
            raise RuntimeError('second page rejected')
        return original(*args,**kwargs)
    with patch.object(printing,'_render_export_page',side_effect=fail_second):
        task.run()
    from PySide6.QtWidgets import QApplication
    QApplication.processEvents()
    assert len(errors)==1 and 'second page rejected' in errors[0]
    assert success==[True]
    assert (tmp_path/'partial-1.png').exists()
    assert not (tmp_path/'partial-2.png').exists()


def test_pdf_progress_and_dialog_failure(export_document,tmp_path):
    from types import SimpleNamespace
    from mtg_proxy_printer.ui.dialogs import SavePDFDialog
    tasks=[]
    main=SimpleNamespace(progress_bar_manager=SimpleNamespace(add_task=tasks.append),on_error_occurred=Mock())
    class ExportParent(QObject):
        def parent(self):
            return main
    parent=ExportParent()
    with patch.object(printing.PDFPrinter,'run',side_effect=RuntimeError('render rejected')):
        with pytest.raises(RuntimeError,match='render rejected'):
            printing.export_pdf(export_document,str(tmp_path/'fail.pdf'),parent)
    assert len(tasks)==1 and not tasks[0]._running
    fake=SimpleNamespace(document=export_document,selectedFiles=lambda:[str(tmp_path/'dialog.pdf')],
                         parent=lambda:main,request_run_async_task=Mock())
    with patch.object(printing,'export_pdf',side_effect=RuntimeError('render rejected')):
        SavePDFDialog.on_accept(fake)
    main.on_error_occurred.assert_called_once_with('render rejected')
    fake.request_run_async_task.emit.assert_not_called()


def test_portrait_unchanged_with_rotation_enabled(export_document,tmp_path):
    export_document.apply(ActionAddCard(card(),1))
    pdf(export_document,tmp_path/'portrait.pdf',600,True)
    page=PdfReader(tmp_path/'portrait.pdf').pages[0]
    assert (float(page.mediabox.width),float(page.mediabox.height)) == (595,842)
    assert bounds(image_placements(page)[0]) == pytest.approx((10.3716667,16.4253333,63.0766667,88.0533333),abs=.01)


def test_png_two_digit_numbering(export_document,tmp_path):
    d=export_document
    d.apply(ActionNewPage(count=9))
    task=printing.PNGRenderer(None,d,str(tmp_path/'number.png'))
    task._output_dpi=30  # Small blank files suffice to verify unchanged numbering.
    task.run()
    assert sorted(p.name for p in tmp_path.glob('number-*.png')) == [f'number-{i:02}.png' for i in range(1,11)]


def test_nominal_edge_clipping_and_guides(export_document,tmp_path):
    from PySide6.QtCore import Qt, QSize
    d=export_document
    d.page_layout.cut_marker_style='Solid'
    d.page_layout.cut_marker_width=.2*mm
    d.apply(ActionAddCard(card(),1))
    pdf(d,tmp_path/'guides.pdf')
    task=printing.PNGRenderer(None,d,str(tmp_path/'guides.png'))
    task.run()
    scene=PageScene(d,RenderMode.ON_PAPER|RenderMode.FILE_EXPORT)
    g=scene.geometry
    from mtg_proxy_printer.units_and_sizes import distance_to_px
    w,h=distance_to_px(g.sheet_width_mm*mm),distance_to_px(g.sheet_height_mm*mm)
    scene.addRect(w-10,h-10,20,20,Qt.PenStyle.NoPen,QColor('red'))
    image=printing.PNGRenderer._create_image(QSize(round(w),round(h)),QColor('white'),11811)
    painter=QPainter(image)
    try:
        printing._render_export_page(scene,painter,300)
    finally:
        painter.end()
    image.save(str(tmp_path/'clipped.png'))
    loaded=QImage(str(tmp_path/'clipped.png'))
    assert loaded.pixelColor(loaded.width()-1,loaded.height()-1)==QColor('red')
    assert loaded.pixelColor(loaded.width()-12,loaded.height()-12)==QColor('white')


def test_pdf_startup_and_paper_setup_failures(export_document,tmp_path):
    progress=Progress()
    success=Mock()
    progress.advance.connect(success)
    writer=printing.PDFPrinter(export_document,str(tmp_path/'startup.pdf'),progress.advance)
    writer.painter=Mock()
    writer.painter.begin.return_value=False
    writer.painter.isActive.return_value=False
    with pytest.raises(RuntimeError,match='Cannot start PDF painter'):
        writer.run()
    success.assert_not_called()
    with patch.object(printing.PDFPrinter,'setPageLayout',return_value=False):
        with pytest.raises(RuntimeError,match='rejected the requested paper'):
            printing.PDFPrinter(export_document,str(tmp_path/'paper-failure.pdf'),progress.advance)
