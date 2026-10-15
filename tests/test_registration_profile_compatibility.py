"""Persisted registration strings stay compatible at existing boundaries."""
import pytest

import mtg_proxy_printer.settings as app_settings
from mtg_proxy_printer.async_tasks.document_loader import DocumentLoader
from mtg_proxy_printer.document_controller.save_document import ActionSaveDocument
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.registration_profile_ids import RegistrationProfileId
from mtg_proxy_printer.ui.page_config_widget import PageConfigWidget
from mtg_proxy_printer.units_and_sizes import ConfigParser


def test_identity_values_and_plain_string_validation():
    assert [item.value for item in RegistrationProfileId] == ["None", "Bullseye", "Cut marker", "Siser"]
    assert app_settings.VALID_PRINT_REGISTRATION_MARKS_STYLES == {"None", "Bullseye", "Cut marker", "Siser"}
    assert isinstance(app_settings.VALID_PRINT_REGISTRATION_MARKS_STYLES, set)
    assert all(type(value) is str for value in app_settings.VALID_PRINT_REGISTRATION_MARKS_STYLES)


@pytest.mark.parametrize("style", ["None", "Bullseye", "Cut marker", "Siser"])
def test_real_settings_save_load_and_ui_strings(qtbot, empty_save_database, style):
    layout = PageLayoutSettings(paper_size="A4", print_registration_marks_style=style)
    ActionSaveDocument.save_settings(empty_save_database, layout)
    value, = empty_save_database.execute(
        "SELECT value FROM DocumentSettings WHERE key='print_registration_marks_style'").fetchone()
    assert type(value) is str and value == style
    loaded = DocumentLoader._load_document_settings(empty_save_database)
    assert type(loaded.print_registration_marks_style) is str
    assert loaded.print_registration_marks_style == style
    widget = PageConfigWidget()
    qtbot.addWidget(widget)
    widget.load_from_page_layout(loaded)
    combo = widget.ui.print_registration_marks_style
    assert [combo.itemData(index) for index in range(combo.count())] == ["None", "Bullseye", "Cut marker", "Siser"]
    assert combo.currentData() == style
    combo.setCurrentIndex((combo.currentIndex()+1) % 4)
    assert type(widget.page_layout.print_registration_marks_style) is str
    assert widget.page_layout.print_registration_marks_style == combo.currentData()


def test_unknown_loader_string_rejected(qtbot, empty_save_database):
    ActionSaveDocument.save_settings(empty_save_database,
                                    PageLayoutSettings(paper_size="A4", print_registration_marks_style="unknown"))
    with pytest.raises(AssertionError, match="invalid data"):
        DocumentLoader._load_document_settings(empty_save_database)


def test_unknown_global_default_restored(qtbot):
    configuration = ConfigParser()
    configuration.read_dict(app_settings.DEFAULT_SETTINGS)
    configuration["documents"]["print-registration-marks-style"] = "unknown"
    app_settings._validate_documents_section(configuration)
    assert configuration["documents"]["print-registration-marks-style"] == \
        app_settings.DEFAULT_SETTINGS["documents"]["print-registration-marks-style"]


def test_siser_global_default_validated(qtbot):
    configuration = ConfigParser()
    configuration.read_dict(app_settings.DEFAULT_SETTINGS)
    configuration['documents']['print-registration-marks-style'] = RegistrationProfileId.SISER.value
    app_settings._validate_documents_section(configuration)
    assert PageLayoutSettings.create_from_settings(configuration).print_registration_marks_style == 'Siser'
