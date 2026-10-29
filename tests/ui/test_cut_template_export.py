"""Current-page capture, real Qt wiring and transactional single-file saving."""

from copy import copy
from pathlib import Path
from unittest.mock import Mock, patch
from xml.etree import ElementTree

import pytest
from PySide6.QtCore import QIODevice, QSaveFile, QStringListModel
from PySide6.QtWidgets import QFileDialog, QWidget

from mtg_proxy_printer.cut_template_svg import serialize_cut_template_svg
from mtg_proxy_printer.document_controller.page_actions import ActionNewPage
from mtg_proxy_printer.model.carddb import CardDatabase
from mtg_proxy_printer.model.page_geometry import build_page_geometry
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.ui import dialogs, main_window
from mtg_proxy_printer.ui.dialogs import SaveCutTemplateDialog
from mtg_proxy_printer.ui.main_window import MainWindow
from mtg_proxy_printer.units_and_sizes import CardSizes, unit_registry
from tests.helpers import create_card


class ExportHost(QWidget):
    on_action_export_cut_template_triggered = MainWindow.on_action_export_cut_template_triggered
    on_dialog_finished = MainWindow.on_dialog_finished

    def __init__(self, document):
        super().__init__()
        self.document = document
        self.current_dialog = None
        self.on_error_occurred = Mock()
        self.request_run_async_task = Mock()
        self.missing_images_manager = Mock()
        self._ask_user_about_compacting_document = Mock(side_effect=AssertionError("No compaction preflight"))


@pytest.fixture
def host(qtbot, document_light, monkeypatch, tmp_path):
    monkeypatch.setattr(main_window, "UI_LOCK_SEMAPHORE", 0)
    monkeypatch.setattr(dialogs, "read_path", lambda *args: str(tmp_path))
    # Test widget control only: production retains Qt's native-dialog choice.
    original = SaveCutTemplateDialog.__init__
    def non_native(self, *args, **kwargs):
        original(self, *args, **kwargs)
        self.setOption(QFileDialog.Option.DontUseNativeDialog, True)
    monkeypatch.setattr(SaveCutTemplateDialog, "__init__", non_native)
    document_light.page_layout = PageLayoutSettings(paper_size="A4")
    widget = ExportHost(document_light)
    qtbot.addWidget(widget)
    yield widget
    if widget.current_dialog is not None:
        widget.current_dialog.reject()


def expected_bytes(document):
    page = document.currently_edited_page
    geometry = build_page_geometry(document.page_layout, page.page_type(), len(page))
    return serialize_cut_template_svg(geometry).encode("utf-8")


@pytest.mark.parametrize("size,count", [(CardSizes.REGULAR, 4), (CardSizes.OVERSIZED, 3)])
def test_captures_selected_later_page_and_preserves_document(host, tmp_path, size, count):
    document = host.document
    placeholder = create_card("Empty Placeholder", size, pixmap=document.image_db.get_blank(size))
    document.apply(ActionNewPage(content=[[placeholder]*count]))
    document.set_currently_edited_page(document.pages[1])
    document.save_file_path = tmp_path / "Deck.v2.mtgproxies"
    expected = expected_bytes(document)
    before = (list(document.pages), [list(p) for p in document.pages], tuple(document.undo_stack),
              tuple(document.redo_stack), document.currently_edited_page, copy(document.page_layout),
              document.save_file_path)
    with patch.object(document, "apply", side_effect=AssertionError("No document action")), \
            patch.object(document, "get_missing_image_cards", side_effect=AssertionError("No artwork acquisition")):
        host.on_action_export_cut_template_triggered()
        dialog = host.current_dialog
        assert dialog.page_number == 2
        assert dialog.windowTitle() == "Export cut template for page 2"
        assert Path(dialog.selectedFiles()[0]).name == "Deck.v2-page-2-cut.svg"
        destination = tmp_path / "選択-page.svg"
        dialog.selectFile(str(destination))
        dialog.accept()
    assert destination.read_bytes() == expected
    assert len(ElementTree.fromstring(expected)) == count  # Placeholders remain occupied.
    assert host.current_dialog is None
    assert (list(document.pages), [list(p) for p in document.pages], tuple(document.undo_stack),
            tuple(document.redo_stack), document.currently_edited_page, document.page_layout,
            document.save_file_path) == before
    host.request_run_async_task.assert_not_called()
    host.missing_images_manager.obtain_missing_images.assert_not_called()
    host._ask_user_about_compacting_document.assert_not_called()
    host.on_error_occurred.assert_not_called()


def test_changes_after_invocation_do_not_change_export(host, tmp_path):
    document = host.document
    placeholder = create_card("Empty Placeholder", CardSizes.OVERSIZED,
                              pixmap=document.image_db.get_blank(CardSizes.OVERSIZED))
    document.apply(ActionNewPage(content=[[placeholder]*2]))
    document.set_currently_edited_page(document.pages[1])
    document.save_file_path = tmp_path / "Captured.mtgproxies"
    original = expected_bytes(document)
    host.on_action_export_cut_template_triggered()
    dialog = host.current_dialog
    assert not hasattr(dialog, "document")
    document.set_currently_edited_page(document.pages[0])
    document.page_layout.paper_orientation = "Landscape"
    document.save_file_path = tmp_path / "Changed.mtgproxies"
    assert dialog.svg_bytes == original
    assert dialog.page_number == 2 and dialog.source_path.name == "Captured.mtgproxies"
    path = tmp_path / "captured.svg"
    dialog.selectFile(str(path))
    dialog.accept()
    assert path.read_bytes() == original
    host.on_action_export_cut_template_triggered()
    assert host.current_dialog.svg_bytes == expected_bytes(document) != original
    assert host.current_dialog.page_number == 1


def test_valid_empty_page_exports_and_cancellation_does_no_io(host, tmp_path):
    path = tmp_path / "empty.svg"
    host.on_action_export_cut_template_triggered()
    dialog = host.current_dialog
    dialog.selectFile(str(path))
    dialog.accept()
    assert len(ElementTree.fromstring(path.read_bytes())) == 0
    existing = path.read_bytes()
    host.on_action_export_cut_template_triggered()
    host.current_dialog.selectFile(str(path))
    with patch.object(dialogs, "QSaveFile", side_effect=AssertionError("Cancel must not write")):
        host.current_dialog.reject()
    assert host.current_dialog is None and path.read_bytes() == existing
    host.on_error_occurred.assert_not_called()


@pytest.mark.parametrize("source,page,name", [
    (None, 1, "page-1-cut.svg"),
    (Path("Deck.mtgproxies"), 2, "Deck-page-2-cut.svg"),
    (Path("Deck.v2.mtgproxies"), 2, "Deck.v2-page-2-cut.svg"),
])
def test_dialog_conventions_and_filename(qtbot, tmp_path, source, page, name):
    with patch.object(dialogs, "read_path", return_value=str(tmp_path)) as read:
        dialog = SaveCutTemplateDialog(None, b"prepared", source, page)
    qtbot.addWidget(dialog)
    dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
    read.assert_called_once_with("export", "export-path")
    assert dialog.directory().absolutePath() == str(tmp_path).replace("\\", "/")
    assert Path(dialog.selectedFiles()[0]).name == name
    assert dialog.acceptMode() == QFileDialog.AcceptMode.AcceptSave
    assert dialog.fileMode() == QFileDialog.FileMode.AnyFile
    assert dialog.defaultSuffix() == "svg"
    assert dialog.nameFilters() == ["SVG cut templates (*.svg)"]
    assert not dialog.testOption(QFileDialog.Option.DontConfirmOverwrite)


def test_success_replaces_existing_file_with_exact_bytes(host, tmp_path):
    path = tmp_path / "existing.svg"
    path.write_bytes(b"old destination")
    expected = expected_bytes(host.document)
    host.on_action_export_cut_template_triggered()
    dialog = host.current_dialog
    dialog.selectFile(str(path))
    # Bypass interactive overwrite confirmation for this real QSaveFile write.
    with patch.object(dialogs.logger, "info") as success:
        dialog.on_accept()
    assert path.read_bytes() == expected
    success.assert_called_once()
    host.on_error_occurred.assert_not_called()


@pytest.mark.parametrize("failure", ["open", "short", "commit"])
def test_write_failure_preserves_destination_and_reports_error(host, tmp_path, failure):
    path = tmp_path / "protected.svg"
    path.write_bytes(b"original destination")
    host.on_action_export_cut_template_triggered()
    dialog = host.current_dialog
    dialog.selectFile(str(path))
    calls = []
    class FaultySaveFile:
        def __init__(self, destination):
            self.real = QSaveFile(destination)
        def setDirectWriteFallback(self, enabled):
            calls.append(("fallback", enabled))
            self.real.setDirectWriteFallback(enabled)
        def open(self, mode):
            calls.append(("open", mode))
            return False if failure == "open" else self.real.open(mode)
        def write(self, data):
            calls.append(("write", data))
            return self.real.write(data[:-1] if failure == "short" else data)
        def commit(self):
            calls.append(("commit",))
            return False  # Inject failure before replacement.
        def errorString(self):
            return "injected " + failure + " failure"
        def cancelWriting(self):
            calls.append(("cancel",))
            self.real.cancelWriting()
            self.real = None  # Release the test wrapper's temporary-file owner.
    with patch.object(dialogs, "QSaveFile", FaultySaveFile), patch.object(dialogs.logger, "info") as success:
        dialog.on_accept()
    assert path.read_bytes() == b"original destination"
    assert list(tmp_path.iterdir()) == [path]
    success.assert_not_called()
    host.on_error_occurred.assert_called_once()
    message = host.on_error_occurred.call_args.args[0]
    assert path.as_posix() in message and "injected " + failure in message
    assert calls[0] == ("fallback", False)
    assert calls[1] == ("open", QIODevice.OpenModeFlag.WriteOnly)
    assert calls[-1] == ("cancel",)
    assert (("commit",) in calls) == (failure == "commit")
    dialog.reject()
    assert host.current_dialog is None


@pytest.mark.parametrize("boundary", ["selection", "geometry", "serializer"])
def test_invalid_preparation_reports_before_dialog(host, boundary):
    target = {"selection": (host.document, "get_current_page_index"),
              "geometry": (main_window, "build_page_geometry"),
              "serializer": (main_window, "serialize_cut_template_svg")}[boundary]
    with patch.object(*target, side_effect=ValueError("rejected " + boundary)), \
            patch.object(main_window, "SaveCutTemplateDialog") as constructor:
        host.on_action_export_cut_template_triggered()
    constructor.assert_not_called()
    host.on_error_occurred.assert_called_once_with("rejected " + boundary)
    assert host.current_dialog is None


def test_invalid_actual_geometry_does_not_open_dialog(host):
    host.document.page_layout = PageLayoutSettings(paper_size="Custom",
                                                  custom_page_width=0*unit_registry.mm,
                                                  custom_page_height=100*unit_registry.mm)
    host.on_action_export_cut_template_triggered()
    assert host.current_dialog is None
    host.on_error_occurred.assert_called_once()


def test_active_lock_or_retained_dialog_blocks_another_export(host, monkeypatch):
    monkeypatch.setattr(main_window, "UI_LOCK_SEMAPHORE", 1)
    with patch.object(main_window, "build_page_geometry") as build:
        host.on_action_export_cut_template_triggered()
    build.assert_not_called()
    assert host.current_dialog is None
    monkeypatch.setattr(main_window, "UI_LOCK_SEMAPHORE", 0)
    host.on_action_export_cut_template_triggered()
    retained = host.current_dialog
    with patch.object(main_window, "SaveCutTemplateDialog") as constructor:
        host.on_action_export_cut_template_triggered()
    constructor.assert_not_called()
    assert host.current_dialog is retained
    retained.reject()
    assert host.current_dialog is None


def test_real_action_autoconnection_menu_and_loading_lock(qtbot, host):
    # One controlled arrangement, without the broad parametrized main-window fixture.
    with patch.object(CardDatabase, "main_instance", host.document.card_db), \
            patch.object(MainWindow, "_setup_central_widget"), \
            patch.object(MainWindow, "on_action_quit_triggered"):
        window = MainWindow(host.document.image_db, host.document, QStringListModel(["en"]))
    qtbot.addWidget(window)
    window.is_running = False
    action = window.ui.action_export_cut_template
    menu_actions = window.ui.menu_export.actions()
    assert action.objectName() == "action_export_cut_template"
    assert action.text() == "Export current page cut template (SVG)…"
    assert action.toolTip() == ("Export rounded regular card outlines and square oversized card outlines at the document’s paper size. "
                                "Registration marks and printer corrections are not included.")
    assert menu_actions.index(action) == menu_actions.index(window.ui.action_export_png) + 1
    assert menu_actions[menu_actions.index(action)+1].isSeparator()
    assert action in window._get_widgets_and_actions_disabled_in_loading_state()
    assert action.shortcut().isEmpty()
    with patch.object(SaveCutTemplateDialog, "open") as opened, \
            patch.object(main_window, "SaveCutTemplateDialog", wraps=SaveCutTemplateDialog) as constructor:
        action.trigger()
        constructor.assert_called_once()
        opened.assert_called_once()
        retained = window.current_dialog
        action.trigger()
        assert window.current_dialog is retained and constructor.call_count == 1
    retained.reject()
    assert window.current_dialog is None
    window.ui_lock_acquire()
    try:
        assert not action.isEnabled()
        window.on_action_export_cut_template_triggered()
        assert window.current_dialog is None
    finally:
        window.ui_lock_release()
    assert action.isEnabled()
