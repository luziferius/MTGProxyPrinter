"""M15 synthetic output measurements, faithful composition and route lifecycle."""
from copy import copy, deepcopy
from unittest.mock import Mock, patch

import pytest
from pypdf import PdfReader
from PySide6.QtCore import QMarginsF, Qt
from PySide6.QtWidgets import QFileDialog
from PySide6.QtGui import QColor, QImage, QPen, QPainter

from mtg_proxy_printer import print as printing
from mtg_proxy_printer.document_controller.card_actions import ActionAddCard
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.page_scene.page_scene import PageScene, RenderMode
from mtg_proxy_printer.settings import settings
from mtg_proxy_printer.siser_registration import resolve_siser_page_marks
from mtg_proxy_printer.ui import dialogs, main_window
from mtg_proxy_printer.units_and_sizes import CardSizes, unit_registry, distance_to_px
from tests.test_export_mapping import card, pdf, image_placements, bounds, red_bounds, Progress
from tests.test_native_print_mapping import software_printer
from tests.test_siser_registration import RouteHost, rect_values
from tests.test_cut_template_svg import parse, path_bounds

mm = unit_registry.mm


def configure(d,paper='Letter',**kwargs):
    d.page_layout = PageLayoutSettings(paper_size=paper,
        paper_orientation='Landscape' if paper=='A4' else 'Portrait',
        print_registration_marks_style='Siser',draw_sharp_corners=True,**kwargs)
    return d


def black_bars(page):
    """Only opaque black straight fills in these synthetic Qt pages; not image Do."""
    result,points,stack = [],[],[]
    state = {'color':(0.,0.,0.),'alpha':1.}
    height = float(page.mediabox.height)
    def visit(op,args,cm,tm):
        nonlocal state,points
        def point(x,y):
            a,b,c,d,e,f = cm
            return ((a*x+c*y+e)*25.4/72,(height-b*x-d*y-f)*25.4/72)
        if op==b'q': stack.append(state.copy())
        elif op==b'Q': state=stack.pop()
        elif op in (b'rg',b'g',b'scn'):
            try: state['color']=tuple(map(float,args))
            except (ValueError,TypeError): state['color']=()
        elif op==b'gs':
            state['alpha']=float(page['/Resources']['/ExtGState'][args[0]].get('/ca',1))
        elif op in (b'm',b'l'): points.append(point(*map(float,args)))
        elif op==b're':
            x,y,w,h=map(float,args)
            points.extend(point(x1,y1) for x1,y1 in [(x,y),(x+w,y),(x+w,y+h),(x,y+h)])
        elif op in (b'f',b'f*'):
            if points and state['alpha']==1 and state['color'] in ((0.,),(0.,0.,0.)):
                result.append(bounds(points))
            points=[]
        elif op in (b'n',b'S',b's'): points=[]
    page.extract_text(visitor_operand_before=visit)
    return sorted(result)


def transformed(rect,g,rotate=False,dx=0,dy=0):
    x,y,w,h=rect_values(rect)
    return (g.sheet_height_mm-y-h+dx,x+dy,h,w) if rotate else (x+dx,y+dy,w,h)


def assert_bars(page,g,rotate=False,dx=0,dy=0,tolerance=.001):
    observed=black_bars(page)
    expected=sorted(transformed(b.bounds_mm,g,rotate,dx,dy) for b in resolve_siser_page_marks(g).bars)
    assert len(observed)==len(expected)==8
    for a,b in zip(observed,expected): assert a==pytest.approx(b,abs=tolerance,rel=0)


@pytest.mark.parametrize('paper,dpi,rotate',[('Letter',300,False),('A4',600,False),('A4',300,True)])
def test_actual_pdf_each_page_artwork_marks_svg_and_transforms(document_light,tmp_path,paper,dpi,rotate):
    d=configure(document_light,paper)
    d.apply(ActionAddCard(card('red'),2))
    d.apply(ActionNewPage(count=2,content=[[card('blue',CardSizes.OVERSIZED)],[]]))
    selected=d.currently_edited_page
    writer=pdf(d,tmp_path/'art.pdf',dpi=dpi,rotate=rotate)
    pages=PdfReader(tmp_path/'art.pdf').pages
    assert len(pages)==3 and [len(image_placements(p)) for p in pages]==[2,1,0]
    assert d.currently_edited_page is selected
    for index,page in enumerate(pages):
        writer._switch_to_page(index)
        g=writer.scene.geometry
        assert_bars(page,g,rotate)
        svg=parse(g)
        for measured,placement,path in zip(image_placements(page),g.placements,svg):
            assert bounds(measured)==pytest.approx(transformed(placement.trim_mm,g,rotate),abs=.01,rel=0)
            assert path_bounds(path)==pytest.approx(rect_values(placement.trim_mm),abs=.01,rel=0)
    assert d.currently_edited_page is selected


@pytest.mark.parametrize('paper,background,pixels',[
    ('Letter','#00000000',(2550,3300)),('A4','#ff245070',(3508,2480))])
def test_png_physical_marks_artwork_alpha_and_numbering(document_light,tmp_path,paper,background,pixels):
    d=configure(document_light,paper)
    d.apply(ActionAddCard(card('red'),1))
    d.apply(ActionNewPage(count=1,content=[[]]))
    selected=d.currently_edited_page
    task=printing.PNGRenderer(None,d,str(tmp_path/'page.png'))
    with patch.dict(settings['export'],{'png-background-color':background}): task.run()
    assert sorted(p.name for p in tmp_path.glob('page-*.png'))==['page-1.png','page-2.png']
    for number in (1,2):
        image=QImage(str(tmp_path/f'page-{number}.png'))
        assert (image.width(),image.height())==pixels
        assert image.dotsPerMeterX()==image.dotsPerMeterY()==11811 and image.devicePixelRatio()==1
        assert image.pixelColor(0,0)==QColor(background)
        g=task.document.page_layout
        from mtg_proxy_printer.model.page_geometry import build_page_geometry
        from mtg_proxy_printer.units_and_sizes import PageType
        geom=build_page_geometry(g,PageType.REGULAR,1)
        for bar in resolve_siser_page_marks(geom).bars:
            r=bar.bounds_mm
            x,y=round(distance_to_px((r.x+r.width/2)*mm)),round(distance_to_px((r.y+r.height/2)*mm))
            assert image.pixelColor(x,y)==QColor('black')
        if number==1:
            r=geom.placements[0].trim_px
            assert red_bounds(image)==pytest.approx((r.x,r.y,r.right,r.bottom),abs=1,rel=0)
        else: assert red_bounds(image) is None
    assert d.currently_edited_page is selected


@pytest.mark.parametrize('paper,standard,rotate,correction',[
    ('Letter',False,False,'0 mm'),('A4',False,False,'0 mm'),
    ('Letter',True,False,'0 mm'),('A4',False,True,'2 mm')])
def test_real_native_pdf_marks_artwork_and_existing_origin_residual(document_light,tmp_path,paper,standard,rotate,correction):
    d=configure(document_light,paper); d.apply(ActionAddCard(card('red'),1))
    margins=QMarginsF(3.17,5.23,7.41,9.67) if standard else None
    printer=software_printer(d,tmp_path/'native.pdf',margins=margins,rotate=rotate)
    renderer=printing.Renderer(d)
    with patch.dict(settings['printer'],{'horizontal-offset':correction,'landscape-compatibility-workaround':str(rotate)}):
        assert renderer.print_document(printer)
    g=renderer.scene.geometry
    dx=24*25.4/300 if correction=='2 mm' else 0.; dy=0.
    if standard:
        from PySide6.QtGui import QPageLayout
        accepted=printer.pageLayout()
        physical=accepted.paintRect(QPageLayout.Unit.Millimeter); device=accepted.paintRectPixels(printer.resolution())
        dx+=device.x()*25.4/printer.resolution()-physical.x()
        dy+=device.y()*25.4/printer.resolution()-physical.y()
    page=PdfReader(tmp_path/'native.pdf').pages[0]
    assert_bars(page,g,rotate,dx,dy)
    assert bounds(image_placements(page)[0])==pytest.approx(transformed(g.placements[0].trim_mm,g,rotate,dx,dy),abs=.01,rel=0)


def test_crowded_composition_bleed_guides_watermark_no_assessment(document_light,tmp_path):
    d=configure(document_light,card_bleed=1.5*mm,cut_marker_style='Solid',cut_marker_width=.3*mm,
        cut_marker_color=QColor('blue'),document_name='Siser composition',draw_page_numbers=True,
        watermark_text='Overlap',watermark_color=QColor('white'),watermark_font_size=12*unit_registry.point)
    d.apply(ActionAddCard(card('red'),9))
    original=deepcopy(d.page_layout); pages_before=d.currently_edited_page
    with patch('mtg_proxy_printer.siser_page_marks.assess_siser_clearance',side_effect=AssertionError('No mandatory assessment')):
        writer=pdf(d,tmp_path/'crowded.pdf')
        task=printing.PNGRenderer(None,d,str(tmp_path/'crowded.png')); task.run()
    page=PdfReader(tmp_path/'crowded.pdf').pages[0]
    assert_bars(page,writer.scene.geometry)
    assert len(image_placements(page))>9  # Trim artwork and configured per-edge bleed are painted.
    assert 'Siser composition' in page.extract_text() and 'Overlap' in page.extract_text()
    assert writer.scene.cut_lines and writer.scene.text_items
    assert d.page_layout==original and d.currently_edited_page is pages_before
    image=QImage(str(tmp_path/'crowded-1.png'))
    # A normal guide overlays mark ink, and actual opaque bleed obscures another part.
    guide_pixel=image.pixelColor(int(distance_to_px(13.335*mm)),round(distance_to_px(6*mm)))
    assert guide_pixel.red()==guide_pixel.green()==0 and guide_pixel.blue()>200  # Subpixel stroke coverage over black ink.
    assert image.pixelColor(round(distance_to_px(14*mm)),round(distance_to_px(6.3*mm)))==QColor('red')


def test_output_readiness_and_pdf_nominal_size_consistency(document_light,tmp_path):
    d=configure(document_light);d.apply(ActionAddCard(card(),1))
    scene=PageScene(d,RenderMode.ON_SCREEN)
    d.page_layout.paper_size='A4';d.page_layout_changed.emit(d.page_layout)
    assert scene.geometry is not None and scene.registration_unavailable_reason
    scene.require_geometry_ready()
    with pytest.raises(RuntimeError,match='Registration unavailable'): scene.require_output_ready()
    with patch.object(printing,'_render_graphics_scene',side_effect=AssertionError('No drawing')):
        with pytest.raises(RuntimeError): printing._render_page(scene,Mock(),300,300)
    with pytest.raises(RuntimeError): scene.render(Mock())
    d.page_layout.paper_orientation='Landscape';d.page_layout_changed.emit(d.page_layout)
    scene.require_output_ready()
    progress=Progress();writer=printing.PDFPrinter(d,str(tmp_path/'changed.pdf'),progress.advance)
    d.page_layout.paper_size='Letter';d.page_layout.paper_orientation='Portrait'
    with patch.object(printing.QPainter,'begin',side_effect=AssertionError('No startup')):
        with pytest.raises(RuntimeError,match='Restart the PDF export'): writer.run()
    assert not writer.painter.isActive()


def test_failed_png_page_not_encoded_and_lock_lifecycle(document_light,tmp_path,qtbot):
    d=configure(document_light);d.apply(ActionAddCard(card(),1))
    task=printing.PNGRenderer(None,d,str(tmp_path/'failed.png'))
    locks,errors,complete=[],[],[]
    task.ui_lock_acquire.connect(lambda:locks.append('acquire'))
    task.ui_lock_release.connect(lambda:locks.append('release'))
    task.error_occurred.connect(errors.append);task.task_completed.connect(lambda:complete.append(True))
    with patch.object(printing,'_render_export_page',side_effect=RuntimeError('synthetic rejected page')), \
            patch.object(task,'_compress_single_image',side_effect=AssertionError('No encoder')):
        task.run()
    assert locks==['acquire','release'] and len(errors)==len(complete)==1
    assert not list(tmp_path.glob('failed*.png'))


@pytest.mark.parametrize('action_name',['on_action_print_triggered','on_action_print_preview_triggered',
    'on_action_print_pdf_triggered','on_action_export_png_triggered'])
def test_supported_ui_bypasses_compaction_keeps_acquisition_and_dialog(document_light,tmp_path,qtbot,monkeypatch,action_name):
    monkeypatch.setattr(main_window,'UI_LOCK_SEMAPHORE',0)
    monkeypatch.setattr(dialogs,'read_path',lambda *a:str(tmp_path))
    d=configure(document_light);d.apply(ActionAddCard(card(),1))
    host=RouteHost(d);qtbot.addWidget(host)
    printer=software_printer(d,tmp_path/'dialog.pdf')
    with patch.object(printing,'create_printer',return_value=printer):
        getattr(host,action_name)()
    assert host.current_dialog is not None
    host._ask_user_about_compacting_document.assert_not_called()
    host.missing_images_manager.obtain_missing_images.assert_called_once()
    retained=host.current_dialog
    getattr(host,action_name)()
    assert host.current_dialog is retained
    host.missing_images_manager.obtain_missing_images.assert_called_once()
    retained.reject();assert host.current_dialog is None


def test_siser_native_dialog_counts_only_success_preview_never_counts(document_light,tmp_path,qtbot):
    d=configure(document_light);d.apply(ActionAddCard(card(),1))
    printer=software_printer(d,tmp_path/'dialog.pdf')
    with patch.object(printing,'create_printer',return_value=printer):
        dialog=dialogs.PrintDialog(d);preview=dialogs.PrintPreviewDialog(d)
    qtbot.addWidget(dialog);qtbot.addWidget(preview)
    counts,errors,preview_errors=Mock(),Mock(),Mock()
    dialog.request_run_async_task.connect(counts);dialog.error_occurred.connect(errors)
    preview.error_occurred.connect(preview_errors)
    d.page_layout.paper_size='A4'
    with patch.object(printing.QPainter,'begin',side_effect=AssertionError('No unsupported startup')):
        dialog._print_accepted(printer);preview._render_preview(printer)
    counts.assert_not_called();errors.assert_called_once();preview_errors.assert_called_once()
    d.page_layout.paper_size='Letter'
    with patch.dict(settings['printer'],{'horizontal-offset':'0 mm','landscape-compatibility-workaround':'False'}):
        dialog._print_accepted(printer);counts.assert_called_once()
        preview._render_preview(printer);counts.assert_called_once()


def test_nonsiser_compaction_and_synchronous_pdf_failure_no_counts(document_light,tmp_path,qtbot,monkeypatch):
    monkeypatch.setattr(main_window,'UI_LOCK_SEMAPHORE',0)
    monkeypatch.setattr(dialogs,'read_path',lambda *a:str(tmp_path))
    d=configure(document_light);d.page_layout.print_registration_marks_style='None'
    host=RouteHost(d);qtbot.addWidget(host)
    host._ask_user_about_compacting_document=Mock(return_value=main_window.StandardButton.Cancel)
    host.on_action_print_pdf_triggered();host._ask_user_about_compacting_document.assert_called_once()
    assert host.current_dialog is None
    d.page_layout.print_registration_marks_style='Siser'
    dialog=dialogs.SavePDFDialog(host,d);qtbot.addWidget(dialog)
    dialog.setOption(QFileDialog.Option.DontUseNativeDialog,True)
    dialog.selectFile(str(tmp_path/'no.pdf'))
    d.page_layout.paper_size='A4'
    with qtbot.assertNotEmitted(dialog.request_run_async_task): dialog.on_accept()
    host.on_error_occurred.assert_called_once();assert not (tmp_path/'no.pdf').exists()
