"""Capture one calibration render, save its bytes, and preserve document state."""

from copy import copy
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from pypdf import PdfReader
from PySide6.QtCore import QStringListModel
from PySide6.QtWidgets import QFileDialog, QWidget

from mtg_proxy_printer.document_controller.page_actions import ActionNewPage
from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.ui import dialogs, main_window
from mtg_proxy_printer.ui.dialogs import SaveCalibrationPDFDialog
from mtg_proxy_printer.ui.main_window import MainWindow
from tests.helpers import create_card


class CalibrationHost(QWidget):
    on_action_export_calibration_triggered = MainWindow.on_action_export_calibration_triggered
    on_dialog_finished = MainWindow.on_dialog_finished

    def __init__(self, document):
        super().__init__()
        self.document = document
        self.current_dialog = None
        self.on_error_occurred = Mock()
        self.request_run_async_task = Mock()
        self.missing_images_manager = Mock()
        self._ask_user_about_compacting_document = Mock(side_effect=AssertionError('No compaction'))


@pytest.fixture
def host(qtbot, document_light, monkeypatch, tmp_path):
    monkeypatch.setattr(main_window,'UI_LOCK_SEMAPHORE',0)
    monkeypatch.setattr(dialogs,'read_path',lambda *args: str(tmp_path))
    original=SaveCalibrationPDFDialog.__init__
    def local_dialog(self,*args,**kwargs):
        original(self,*args,**kwargs)
        self.setOption(QFileDialog.Option.DontUseNativeDialog,True)
    monkeypatch.setattr(SaveCalibrationPDFDialog,'__init__',local_dialog)
    document_light.page_layout=PageLayoutSettings(paper_size='A4')
    widget=CalibrationHost(document_light)
    qtbot.addWidget(widget)
    yield widget
    if widget.current_dialog is not None:
        widget.current_dialog.reject()


def test_captured_render_naming_and_later_changes(host,tmp_path):
    document=host.document
    document.apply(ActionNewPage(content=[[create_card('no artwork')]*4]))
    document.set_currently_edited_page(document.pages[1])
    document.save_file_path=tmp_path/'Deck.v2.mtgproxies'
    document.page_layout.print_registration_marks_style='Cut marker'
    before=(list(document.pages),[list(p) for p in document.pages],tuple(document.undo_stack),
            tuple(document.redo_stack),document.currently_edited_page,copy(document.page_layout),document.save_file_path)
    with patch.object(main_window,'render_calibration_pdf',wraps=main_window.render_calibration_pdf) as render, \
            patch.object(document,'apply',side_effect=AssertionError('No document action')), \
            patch.object(document,'get_missing_image_cards',side_effect=AssertionError('No images')):
        host.on_action_export_calibration_triggered()
        dialog=host.current_dialog
        captured=dialog.pdf_bytes
        assert render.call_count==1
        assert len(render.call_args.args[0].placements)==4
        assert render.call_args.args[1]=='Cut marker'
        assert (list(document.pages),[list(p) for p in document.pages],tuple(document.undo_stack),
                tuple(document.redo_stack),document.currently_edited_page,document.page_layout,document.save_file_path)==before
        assert not hasattr(dialog,'document')
        assert dialog.page_number==2 and dialog.windowTitle()=='Export calibration sheet for page 2'
        assert Path(dialog.selectedFiles()[0]).name=='Deck.v2-page-2-calibration.pdf'
        document.set_currently_edited_page(document.pages[0])
        document.page_layout.paper_orientation='Landscape'
        document.page_layout.print_registration_marks_style='None'
        document.save_file_path=tmp_path/'Changed.mtgproxies'
        destination=tmp_path/'測定.pdf'
        dialog.selectFile(str(destination))
        dialog.accept()
        assert destination.read_bytes()==captured
        assert render.call_count==1  # Save never renders again.
        assert host.current_dialog is None
        page=PdfReader(BytesIO(captured)).pages[0]
        assert (float(page.mediabox.width),float(page.mediabox.height))==(595,842)
    host.request_run_async_task.assert_not_called()
    host.missing_images_manager.obtain_missing_images.assert_not_called()
    host._ask_user_about_compacting_document.assert_not_called()
    host.on_error_occurred.assert_not_called()


def test_cancel_and_loading_guard(host,tmp_path,monkeypatch):
    path=tmp_path/'protected.pdf'
    path.write_bytes(b'original')
    monkeypatch.setattr(main_window,'UI_LOCK_SEMAPHORE',1)
    host.on_action_export_calibration_triggered()
    assert host.current_dialog is None
    monkeypatch.setattr(main_window,'UI_LOCK_SEMAPHORE',0)
    host.on_action_export_calibration_triggered()
    retained=host.current_dialog
    with patch.object(main_window,'render_calibration_pdf') as render:
        host.on_action_export_calibration_triggered()
    render.assert_not_called()
    assert host.current_dialog is retained
    retained.selectFile(str(path))
    with patch.object(dialogs,'QSaveFile',side_effect=AssertionError('Cancel does no I/O')):
        retained.reject()
    assert path.read_bytes()==b'original' and host.current_dialog is None
    host.on_error_occurred.assert_not_called()


@pytest.mark.parametrize('source,page,name',[
    (None,1,'page-1-calibration.pdf'),(Path('Deck.v2.mtgproxies'),2,'Deck.v2-page-2-calibration.pdf')])
def test_filename_and_options(host,source,page,name):
    dialog=SaveCalibrationPDFDialog(host,b'captured',source,page)
    assert Path(dialog.selectedFiles()[0]).name==name
    assert dialog.nameFilters()==['PDF documents (*.pdf)']
    assert dialog.defaultSuffix()=='pdf'
    assert dialog.acceptMode()==QFileDialog.AcceptMode.AcceptSave
    assert dialog.fileMode()==QFileDialog.FileMode.AnyFile
    assert not dialog.testOption(QFileDialog.Option.DontConfirmOverwrite)


@pytest.mark.parametrize('error',[ValueError('bad geometry'),RuntimeError('render rejected')])
def test_preparation_failure_opens_no_dialog(host,error):
    with patch.object(main_window,'render_calibration_pdf',side_effect=error), \
            patch.object(main_window,'SaveCalibrationPDFDialog') as constructor:
        host.on_action_export_calibration_triggered()
    constructor.assert_not_called()
    host.on_error_occurred.assert_called_once_with(str(error))
    assert host.current_dialog is None


def test_save_error_is_reported_without_success(host,tmp_path):
    path=tmp_path/'kept.pdf'
    path.write_bytes(b'original')
    host.on_action_export_calibration_triggered()
    dialog=host.current_dialog
    dialog.selectFile(str(path))
    with patch.object(dialogs,'_write_prepared_file',side_effect=OSError('disk failure')), \
            patch.object(dialogs.logger,'info') as success:
        dialog.on_accept()
    assert path.read_bytes()==b'original'
    success.assert_not_called()
    host.on_error_occurred.assert_called_once()
    assert 'disk failure' in host.on_error_occurred.call_args.args[0]
    assert path.as_posix() in host.on_error_occurred.call_args.args[0]


def test_real_action_menu_autoconnection_and_lock(qtbot,host):
    with patch.object(CardDatabase,'main_instance',host.document.card_db), \
            patch.object(MainWindow,'_setup_central_widget'):
        window=MainWindow(host.document.image_db,host.document,QStringListModel(['en']))
    qtbot.addWidget(window)
    window.is_running=False
    action=window.ui.action_export_calibration
    actions=window.ui.menu_export.actions()
    assert actions.index(action)==actions.index(window.ui.action_print_pdf)+1
    assert actions.index(window.ui.action_export_png)==actions.index(action)+1
    assert actions.index(window.ui.action_export_cut_template)==actions.index(window.ui.action_export_png)+1
    assert action.text()=='Export current page calibration sheet (PDF)…'
    assert 'without card artwork' in action.toolTip()
    assert action in window._get_widgets_and_actions_disabled_in_loading_state()
    with patch.object(SaveCalibrationPDFDialog,'open') as opened, \
            patch.object(main_window,'SaveCalibrationPDFDialog',wraps=SaveCalibrationPDFDialog) as constructor:
        action.trigger()
        constructor.assert_called_once()
        opened.assert_called_once()
    window.current_dialog.reject()
    assert window.current_dialog is None
    window.ui_lock_acquire()
    try:
        assert not action.isEnabled()
        window.on_action_export_calibration_triggered()
        assert window.current_dialog is None
    finally:
        window.ui_lock_release()
    assert action.isEnabled()
