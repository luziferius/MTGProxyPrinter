"""M16 offline help only: real action, resource modes and read-only lifecycle."""

from copy import deepcopy
from pathlib import Path
import shutil
import subprocess
import sys
from unittest.mock import Mock, patch
from xml.etree import ElementTree

import pytest
from PySide6.QtCore import QResource, QStringListModel, QUrl, Qt
from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QWidget

from mtg_proxy_printer.settings import settings
from mtg_proxy_printer.ui import common, main_window
from mtg_proxy_printer.ui.siser_guide_dialog import SiserGuideDialog, GUIDE_PATH, PREVIEW_PATH


@pytest.fixture
def window(document_light, qtbot):
    # Keep the real designer menu, auto-connected slot and MainWindow initialization.
    # Unrelated database/download/progress collaborators are not needed for help.
    with patch.dict(main_window.Ui_MainWindow.setupUi.__globals__, {'CentralWidget': QWidget}), \
            patch.object(main_window.MainWindow, '_create_about_dialog', return_value=Mock()), \
            patch.object(main_window.MainWindow, '_create_missing_images_manager', return_value=Mock()), \
            patch.object(main_window.MainWindow, '_create_progress_bar_manager', return_value=Mock()), \
            patch.object(main_window.MainWindow, '_setup_central_widget'), \
            patch.object(main_window.MainWindow, 'on_action_quit_triggered'):
        result = main_window.MainWindow(document_light.image_db, document_light, QStringListModel(['en']))
        qtbot.addWidget(result)
        yield result


def snapshot(document):
    return (list(document.pages), [list(page) for page in document.pages],
            tuple(document.undo_stack), tuple(document.redo_stack), document.currently_edited_page,
            deepcopy(document.page_layout), document.save_file_path,
            {section: dict(settings[section]) for section in settings.sections()})


def assert_readable(dialog):
    assert not dialog.isModal() and dialog.browser.isReadOnly()
    text = dialog.browser.toPlainText()
    assert 'Siser Print & Cut Guide' in text and 'counterclockwise' in text
    assert '1 mm' in text and 'actual size / 100%' in text
    image = dialog.browser.document().resource(QTextDocument.ResourceType.ImageResource,
                                               QUrl('images/a4-portrait-feed.png'))
    assert image is not None and not image.isNull()
    assert dialog.browser.verticalScrollBar().maximum() > 0


def test_real_action_reuses_help_close_reopen_and_preserves_state(window, qtbot):
    window.show()
    retained = QDialog(window)
    window.current_dialog = retained
    before = snapshot(window.document)
    action = window.ui.action_show_siser_guide
    assert action in window.ui.menu_application.actions()
    assert action.text() == 'Siser Print & Cut Guide'
    with patch.object(main_window, 'SiserGuideDialog', wraps=SiserGuideDialog) as constructor, \
            qtbot.assertNotEmitted(window.request_run_async_task):
        action.trigger()
        guide = window.siser_guide_dialog
        qtbot.waitUntil(guide.isVisible)
        assert_readable(guide)
        action.trigger()
        assert window.siser_guide_dialog is guide and constructor.call_count == 1
        guide.browser.verticalScrollBar().setValue(guide.browser.verticalScrollBar().maximum())
        assert guide.browser.verticalScrollBar().value() > 0
        qtbot.mouseClick(guide.close_buttons.button(QDialogButtonBox.StandardButton.Close), Qt.MouseButton.LeftButton)
        assert not guide.isVisible()
        action.trigger()
        assert guide.isVisible() and window.siser_guide_dialog is guide
        assert constructor.call_count == 1
    assert window.current_dialog is retained
    assert snapshot(window.document) == before
    window.missing_images_manager.obtain_missing_images.assert_not_called()


def test_development_resources_work_away_from_checkout(qtbot, monkeypatch, tmp_path):
    prefix = Path(__file__).resolve().parents[2] / 'resources'
    monkeypatch.setattr(common, 'HAS_COMPILED_RESOURCES', False)
    monkeypatch.setattr(common, 'RESOURCE_PATH_PREFIX', str(prefix))
    monkeypatch.chdir(tmp_path)
    guide = SiserGuideDialog()
    qtbot.addWidget(guide)
    guide.show()
    assert_readable(guide)
    assert guide.browser.document().baseUrl().isLocalFile()


def test_minimal_compiled_help_resources(qtbot, monkeypatch, tmp_path):
    root = Path(__file__).resolve().parents[2]
    registered = {item.text for item in ElementTree.parse(root / 'resources/resources.qrc').iter('file')}
    assert {GUIDE_PATH, PREVIEW_PATH} <= registered
    qrc = tmp_path / 'help.qrc'
    tree = ElementTree.Element('RCC')
    resource = ElementTree.SubElement(tree, 'qresource', prefix='/')
    for path in (GUIDE_PATH, PREVIEW_PATH):
        ElementTree.SubElement(resource, 'file', alias=path).text = str(root / 'resources' / path)
    ElementTree.ElementTree(tree).write(qrc, encoding='utf-8')
    binary = tmp_path / 'help.rcc'
    compiler = shutil.which('pyside6-rcc', path=str(Path(sys.executable).parent))
    if compiler is None:
        compiler = shutil.which('pyside6-rcc')
    if compiler is None:
        pytest.fail('pyside6-rcc was not found. Use the existing PySide6 development '
                    'environment and make its tools available on PATH.')
    subprocess.run([compiler, '--binary', str(qrc), '-o', str(binary)], check=True,
                   capture_output=True, timeout=15)
    assert QResource.registerResource(str(binary))
    try:
        monkeypatch.setattr(common, 'HAS_COMPILED_RESOURCES', True)
        monkeypatch.setattr(common, 'RESOURCE_PATH_PREFIX', ':')
        monkeypatch.chdir(tmp_path)
        guide = SiserGuideDialog()
        qtbot.addWidget(guide)
        guide.show()
        assert_readable(guide)
        assert guide.browser.document().baseUrl() == QUrl('qrc:/help/')
        assert common.load_file(GUIDE_PATH) == (root / 'resources' / GUIDE_PATH).read_bytes()
        assert common.load_file(PREVIEW_PATH) == (root / 'resources' / PREVIEW_PATH).read_bytes()
        guide.close()
    finally:
        assert QResource.unregisterResource(str(binary))


@pytest.mark.parametrize('missing', [GUIDE_PATH, PREVIEW_PATH])
def test_missing_resource_reports_useful_failure(window, qtbot, missing):
    load = common.load_file
    with patch.object(common, 'load_file', side_effect=lambda path: b'' if path == missing else load(path)), \
            patch.object(window, 'on_error_occurred') as error, \
            qtbot.assertNotEmitted(window.request_run_async_task):
        window.ui.action_show_siser_guide.trigger()
        window.ui.action_show_siser_guide.trigger()
    assert window.siser_guide_dialog is None
    assert error.call_count == 2
    assert 'Siser guide unavailable' in error.call_args.args[0]
    assert missing in error.call_args.args[0]
    assert not window.findChildren(SiserGuideDialog)
