# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import configparser
import logging
import pathlib
import re
import typing

from PyQt5.QtCore import QStandardPaths

import mtg_proxy_printer.app_dirs
import mtg_proxy_printer.meta_data
import mtg_proxy_printer.natsort
from mtg_proxy_printer.units_and_sizes import CardSizes

__all__ = [
    "settings",
    "DEFAULT_SETTINGS",
    "read_settings_from_file",
    "write_settings_to_file",
    "validate_settings",
    "update_stored_version_string",
]


config_file_path = pathlib.Path(mtg_proxy_printer.app_dirs.data_directories.user_config_dir, "MTGProxyPrinter.ini")
settings = configparser.ConfigParser()
DEFAULT_SETTINGS = configparser.ConfigParser()
# Support three-valued boolean logic by adding values that parse to None, instead of True/False.
# This will be used to store “unset” boolean settings.
configparser.ConfigParser.BOOLEAN_STATES.update({
    "-1": None,
    "unknown": None,
    "none": None,
})

VERSION_CHECK_RE = re.compile(
    # sourced from https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][\da-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][\da-zA-Z-]*))*))?"
    r"(?:\+(?P<buildmetadata>[\da-zA-Z-]+(?:\.[\da-zA-Z-]+)*))?$"
)

# Below are the default application settings. How to define new ones:
# - Add a key-value pair (String keys and values only) to a section or add a new section
# - If adding a new section, also add a validator function for that section.
# - Add the new key to the validator of the section it’s in. The validator has to check that the value can be properly
#   cast into the expected type and perform a value range check.
# - Add the option to the Settings window UI
# - Wire up save and load functionality for the new key in the Settings UI
# - The Settings GUI class has to also do a value range check.

DEFAULT_SETTINGS["images"] = {
    "preferred-language": "en",
    "automatically-add-opposing-faces": "True",
}
DEFAULT_SETTINGS["card-filter"] = {
    "hide-cards-depicting-racism": "True",
    "hide-cards-without-images": "True",
    "hide-oversized-cards": "False",
    "hide-banned-in-brawl": "False",
    "hide-banned-in-commander": "False",
    "hide-banned-in-historic": "False",
    "hide-banned-in-legacy": "False",
    "hide-banned-in-modern": "False",
    "hide-banned-in-pauper": "False",
    "hide-banned-in-penny": "False",
    "hide-banned-in-pioneer": "False",
    "hide-banned-in-standard": "False",
    "hide-banned-in-vintage": "False",
    "hide-white-bordered": "False",
    "hide-gold-bordered": "False",
    "hide-funny-cards": "False",
    "hide-token": "False",
    "hide-digital-cards": "True",
}
DEFAULT_SETTINGS["documents"] = {
    "paper-height-mm": "297",
    "paper-width-mm": "210",
    "margin-top-mm": "10",
    "margin-bottom-mm": "10",
    "margin-left-mm": "7",
    "margin-right-mm": "7",
    "image-spacing-horizontal-mm": "0",
    "image-spacing-vertical-mm": "0",
    "print-cut-marker": "False",
    "pdf-page-count-limit": "0",
    "print-sharp-corners": "False",
}
DEFAULT_SETTINGS["default-filesystem-paths"] = {
    "document-save-path": QStandardPaths.locate(QStandardPaths.DocumentsLocation, "", QStandardPaths.LocateDirectory),
    "pdf-export-path": QStandardPaths.locate(QStandardPaths.DocumentsLocation, "", QStandardPaths.LocateDirectory),
    "deck-list-search-path": QStandardPaths.locate(QStandardPaths.DownloadLocation, "", QStandardPaths.LocateDirectory),
}
DEFAULT_SETTINGS["gui"] = {
    "central-widget-layout": "columnar",
    "show-toolbar": "True",
}
VALID_SEARCH_WIDGET_LAYOUTS = {"horizontal", "columnar", "tabbed"}
DEFAULT_SETTINGS["debug"] = {
    "cutelog-integration": "False",
    "write-log-file": "True",
    "log-level": "INFO"
}
VALID_LOG_LEVELS = set(map(logging.getLevelName, range(10, 60, 10)))
DEFAULT_SETTINGS["decklist-import"] = {
    "enable-print-guessing-by-default": "True",
    "prefer-already-downloaded-images": "True",
    "always-translate-deck-lists": "False",
    "remove-basic-wastes": "False",
    "remove-snow-basics": "False",
}
DEFAULT_SETTINGS["application"] = {
    "last-used-version": mtg_proxy_printer.meta_data.__version__,
    "check-for-application-updates": "None",
    "check-for-card-data-updates": "None",
}


def read_settings_from_file():
    global settings, DEFAULT_SETTINGS
    settings.clear()
    if not config_file_path.exists():
        settings.read_dict(DEFAULT_SETTINGS)
    else:
        settings.read(config_file_path)
        migrate_settings(settings)
        read_sections = set(settings.sections())
        known_sections = set(DEFAULT_SETTINGS.sections())
        # Synchronize sections
        for outdated in read_sections - known_sections:
            settings.remove_section(outdated)
        for new in sorted(known_sections - read_sections):
            settings.add_section(new)
        # Synchronize individual options
        for section in known_sections:
            read_options = set(settings[section].keys())
            known_options = set(DEFAULT_SETTINGS[section].keys())
            for outdated in read_options - known_options:
                del settings[section][outdated]
            for new in sorted(known_options - read_options):
                settings[section][new] = DEFAULT_SETTINGS[section][new]
    validate_settings(settings)


def write_settings_to_file():
    global settings
    if not config_file_path.parent.exists():
        config_file_path.parent.mkdir(parents=True)
    with config_file_path.open("w") as config_file:
        settings.write(config_file)


def update_stored_version_string():
    """Sets the version string stored in the configuration file to the version of the currently running instance."""
    settings["application"]["last-used-version"] = DEFAULT_SETTINGS["application"]["last-used-version"]


def was_application_updated() -> bool:
    """
    Returns True, if the application was updated since last start, i.e. if the internal version number
    is greater than the version string stored in the configuration file. Returns False otherwise.
    """
    return mtg_proxy_printer.natsort.str_less_than(
        settings["application"]["last-used-version"],
        mtg_proxy_printer.meta_data.__version__
    )


def validate_settings(read_settings: configparser.ConfigParser):
    """
    Called after reading the settings from disk. Ensures that all settings contain valid values and expected types.
    I.e. checks that settings that should contain booleans do contain valid booleans, options that should contain
    non-negative integers do so, etc. If an option contains an invalid value, the default value is restored.
    """
    _validate_card_filter_section(read_settings)
    _validate_images_section(read_settings)
    _validate_documents_section(read_settings)
    _validate_application_section(read_settings)
    _validate_gui_section(read_settings)
    _validate_debug_section(read_settings)
    _validate_decklist_import_section(read_settings)
    _validate_default_filesystem_paths_section(read_settings)


def _validate_card_filter_section(settings: configparser.ConfigParser, section_name: str = "card-filter"):
    section = settings[section_name]
    defaults = DEFAULT_SETTINGS[section_name]
    for key in section.keys():
        _validate_boolean(section, defaults, key)


def _validate_images_section(settings: configparser.ConfigParser, section_name: str = "images"):
    section = settings[section_name]
    defaults = DEFAULT_SETTINGS[section_name]
    for key in ("automatically-add-opposing-faces",):
        _validate_boolean(section, defaults, key)
    language = section["preferred-language"]
    if not re.fullmatch(r"[a-z]{2}", language):
        # Only syntactic validation: Language contains a string of exactly two lower case ascii letters
        _restore_default(section, defaults, "preferred-language")


def _validate_documents_section(settings: configparser.ConfigParser, section_name: str = "documents"):
    card_size = mtg_proxy_printer.units_and_sizes.CardSizes.OVERSIZED
    card_height = card_size.as_mm(card_size.height)
    card_width = card_size.as_mm(card_size.width)
    section = settings[section_name]
    defaults = DEFAULT_SETTINGS[section_name]
    boolean_settings = {"print-cut-marker", "print-sharp-corners"}
    # Check syntax
    for key in section.keys():
        if key in boolean_settings:
            _validate_boolean(section, defaults, key)
        else:
            _validate_non_negative_int(section, defaults, key)
    # Check some semantic properties
    available_height = section.getint("paper-height-mm") - \
        (section.getint("margin-top-mm") + section.getint("margin-bottom-mm"))
    available_width = section.getint("paper-width-mm") - \
        (section.getint("margin-left-mm") + section.getint("margin-right-mm"))

    if available_height < card_height:
        # Can not fit a single card on a page
        section["paper-height-mm"] = defaults["paper-height-mm"]
        section["margin-top-mm"] = defaults["margin-top-mm"]
        section["margin-bottom-mm"] = defaults["margin-bottom-mm"]
    if available_width < card_width:
        # Can not fit a single card on a page
        section["paper-width-mm"] = defaults["paper-width-mm"]
        section["margin-left-mm"] = defaults["margin-left-mm"]
        section["margin-right-mm"] = defaults["margin-right-mm"]

    # Re-calculate, if width or height was reset
    available_height = section.getint("paper-height-mm") - \
        (section.getint("margin-top-mm") + section.getint("margin-bottom-mm"))
    available_width = section.getint("paper-width-mm") - \
        (section.getint("margin-left-mm") + section.getint("margin-right-mm"))

    if section.getint("image-spacing-vertical-mm") > (available_spacing_vertical := available_height - card_height):
        # Prevent vertical spacing from overlapping with bottom margin
        section["image-spacing-vertical-mm"] = str(available_spacing_vertical)
    if section.getint("image-spacing-horizontal-mm") > (available_spacing_horizontal := available_width - card_width):
        # Prevent horizontal spacing from overlapping with right margin
        section["image-spacing-horizontal-mm"] = str(available_spacing_horizontal)


def _validate_application_section(settings: configparser.ConfigParser, section_name: str = "application"):
    section = settings[section_name]
    defaults = DEFAULT_SETTINGS[section_name]
    if not VERSION_CHECK_RE.fullmatch(section["last-used-version"]):
        section["last-used-version"] = defaults["last-used-version"]
    for option in ("check-for-application-updates", "check-for-card-data-updates"):
        _validate_three_valued_boolean(section, defaults, option)


def _validate_gui_section(settings: configparser.ConfigParser, section_name: str = "gui"):
    section = settings[section_name]
    defaults = DEFAULT_SETTINGS[section_name]
    _validate_string_is_in_set(section, defaults, VALID_SEARCH_WIDGET_LAYOUTS, "central-widget-layout")
    _validate_boolean(section, defaults, "show-toolbar")


def _validate_debug_section(settings: configparser.ConfigParser, section_name: str = "debug"):
    section = settings[section_name]
    defaults = DEFAULT_SETTINGS[section_name]
    _validate_boolean(section, defaults, "cutelog-integration")
    _validate_boolean(section, defaults, "write-log-file")
    _validate_string_is_in_set(section, defaults, VALID_LOG_LEVELS, "log-level")


def _validate_decklist_import_section(settings: configparser.ConfigParser, section_name: str = "decklist-import"):
    section = settings[section_name]
    defaults = DEFAULT_SETTINGS[section_name]
    for key in section.keys():
        _validate_boolean(section, defaults, key)


def _validate_default_filesystem_paths_section(
        settings: configparser.ConfigParser, section_name: str = "default-filesystem-paths"):
    section = settings[section_name]
    defaults = DEFAULT_SETTINGS[section_name]
    for key in section.keys():
        _validate_path_to_directory(section, defaults, key)


def _validate_path_to_directory(section: configparser.SectionProxy, defaults: configparser.SectionProxy, key: str):
    try:
        if not pathlib.Path(section[key]).resolve().is_dir():
            raise ValueError
    except Exception:
        _restore_default(section, defaults, key)


def _validate_boolean(section: configparser.SectionProxy, defaults: configparser.SectionProxy, key: str):
    try:
        if section.getboolean(key) is None:
            raise ValueError
    except ValueError:
        _restore_default(section, defaults, key)


def _validate_three_valued_boolean(section: configparser.SectionProxy, defaults: configparser.SectionProxy, key: str):
    try:
        section.getboolean(key)
    except ValueError:
        _restore_default(section, defaults, key)


def _validate_non_negative_int(section: configparser.SectionProxy, defaults: configparser.SectionProxy, key: str):
    try:
        if section.getint(key) < 0:
            raise ValueError
    except ValueError:
        _restore_default(section, defaults, key)


def _validate_string_is_in_set(
        section: configparser.SectionProxy, defaults: configparser.SectionProxy,
        valid_options: typing.Set[str], key: str):
    """Checks if the value of the option is one of the allowed values, as determined by the given set of strings."""
    if section[key] not in valid_options:
        _restore_default(section, defaults, key)


def _restore_default(section: configparser.SectionProxy, defaults: configparser.SectionProxy, key: str):
    section[key] = defaults[key]


def migrate_settings(settings: configparser.ConfigParser):
    _migrate_layout_setting(settings)
    _migrate_download_settings(settings)
    _migrate_default_save_paths_settings(settings)


def _migrate_layout_setting(settings: configparser.ConfigParser):
    try:
        gui_section = settings["gui"]
        layout = gui_section["search-widget-layout"]
    except KeyError:
        return
    else:
        if layout == "vertical":
            layout = "columnar"
        gui_section["central-widget-layout"] = layout
        
        
def _migrate_download_settings(settings: configparser.ConfigParser):
    target_section_name = "card-filter"
    if settings.has_section(target_section_name) or not settings.has_section("downloads"):
        return
    download_section = settings["downloads"]
    settings.add_section(target_section_name)
    filter_section = settings[target_section_name]
    for source_setting in settings["downloads"].keys():
        target_setting = source_setting.replace("download-", "hide-")
        try:
            new_value = not download_section.getboolean(source_setting)
        except ValueError:
            pass
        else:
            filter_section[target_setting] = str(new_value)


def _migrate_default_save_paths_settings(settings: configparser.ConfigParser):
    source_section_name = "default-save-paths"
    target_section_name = "default-filesystem-paths"
    if settings.has_section(target_section_name) or not settings.has_section(source_section_name):
        return
    settings.add_section(target_section_name)
    settings[target_section_name].update(settings[source_section_name])


def _migrate_print_guessing_settings(settings: configparser.ConfigParser):
    source_section_name = "print-guessing"
    target_section_name = "decklist-import"
    if settings.has_section(target_section_name) or not settings.has_section(source_section_name):
        return
    settings.add_section(target_section_name)
    target = settings[target_section_name]
    source = settings[source_section_name]
    # Force-overwrite with the new default when migrating. Having this disabled has negative UX impact, so should not
    # be disabled by default.
    target["enable-print-guessing-by-default"] = "True"
    target["prefer-already-downloaded-images"] = source["prefer-already-downloaded"]
    target["always-translate-deck-lists"] = source["always-translate-deck-lists"]


# Read the settings from file during module import
# This has to be performed before any modules containing GUI classes are imported.
read_settings_from_file()
