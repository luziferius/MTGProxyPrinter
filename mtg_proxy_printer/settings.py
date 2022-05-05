# Copyright (C) 2020, 2021 Thomas Hess <thomas.hess@udo.edu>

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

__all__ = [
    "settings",
    "DEFAULT_SETTINGS",
    "read_settings_from_file",
    "write_settings_to_file",
    "validate_settings",
    "update_version_string",
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

# TODO: Single-source these properties somewhere. The Document class holds similar constants.
CARD_WIDTH = 63
CARD_HEIGHT = 88

VERSION_CHECK_RE = re.compile(
    # sourced from https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

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
}
DEFAULT_SETTINGS["default-save-paths"] = {
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
DEFAULT_SETTINGS["print-guessing"] = {
    "enable-guessing": "True",
    "prefer-already-downloaded": "True",
    "always-translate-deck-lists": "False",
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


def update_version_string():
    settings["application"]["last-used-version"] = DEFAULT_SETTINGS["application"]["last-used-version"]


def validate_settings(read_settings: configparser.ConfigParser):
    """
    Called after reading the settings from disk. Ensures that all settings contain valid values and expected types.
    I.e. checks that settings that should contain booleans do contain valid booleans, options that should contain
    non-negative integers do so, etc. If an option contains an invalid value, the default value is restored.
    """
    _validate_card_filter_section(read_settings["card-filter"])
    _validate_images_section(read_settings["images"])
    _validate_documents_section(read_settings["documents"])
    _validate_application_section(read_settings["application"])
    _validate_gui_section(read_settings["gui"])
    _validate_debug_section(read_settings["debug"])
    _validate_print_guessing_section(read_settings["print-guessing"])
    _validate_default_save_paths_section(read_settings["default-save-paths"])


def _validate_card_filter_section(section: configparser.SectionProxy):
    defaults = DEFAULT_SETTINGS["card-filter"]
    for key in section.keys():
        _validate_boolean(section, defaults, key)


def _validate_images_section(section: configparser.SectionProxy):
    defaults = DEFAULT_SETTINGS["images"]
    for key in ("automatically-add-opposing-faces",):
        _validate_boolean(section, defaults, key)
    language = section["preferred-language"]
    if not re.fullmatch(r"[a-z]{2}", language):
        # Only syntactic validation: Language contains a string of exactly two lower case ascii letters
        _restore_default(section, defaults, "preferred-language")


def _validate_documents_section(section: configparser.SectionProxy):
    defaults = DEFAULT_SETTINGS["documents"]
    _validate_boolean(section, defaults, "print-cut-marker")
    # Check syntax
    for key in section.keys():
        if key in ("print-cut-marker",):
            continue
        _validate_non_negative_int(section, defaults, key)
    # Check some semantic properties
    available_height = section.getint("paper-height-mm") - \
        (section.getint("margin-top-mm") + section.getint("margin-bottom-mm"))
    available_width = section.getint("paper-width-mm") - \
        (section.getint("margin-left-mm") + section.getint("margin-right-mm"))

    if available_height < CARD_HEIGHT:
        # Can not fit a single card on a page
        section["paper-height-mm"] = defaults["paper-height-mm"]
        section["margin-top-mm"] = defaults["margin-top-mm"]
        section["margin-bottom-mm"] = defaults["margin-bottom-mm"]
    if available_width < CARD_WIDTH:
        # Can not fit a single card on a page
        section["paper-width-mm"] = defaults["paper-width-mm"]
        section["margin-left-mm"] = defaults["margin-left-mm"]
        section["margin-right-mm"] = defaults["margin-right-mm"]

    # Re-calculate, if width or height was reset
    available_height = section.getint("paper-height-mm") - \
        (section.getint("margin-top-mm") + section.getint("margin-bottom-mm"))
    available_width = section.getint("paper-width-mm") - \
        (section.getint("margin-left-mm") + section.getint("margin-right-mm"))

    if section.getint("image-spacing-vertical-mm") > (available_spacing_vertical := available_height - CARD_HEIGHT):
        # Prevent vertical spacing from overlapping with bottom margin
        section["image-spacing-vertical-mm"] = str(available_spacing_vertical)
    if section.getint("image-spacing-horizontal-mm") > (available_spacing_horizontal := available_width - CARD_WIDTH):
        # Prevent horizontal spacing from overlapping with right margin
        section["image-spacing-horizontal-mm"] = str(available_spacing_horizontal)


def _validate_application_section(section: configparser.SectionProxy):
    defaults = DEFAULT_SETTINGS["application"]
    if not VERSION_CHECK_RE.fullmatch(section["last-used-version"]):
        section["last-used-version"] = defaults["last-used-version"]
    for option in ("check-for-application-updates", "check-for-card-data-updates"):
        _validate_three_valued_boolean(section, defaults, option)


def _validate_gui_section(section: configparser.SectionProxy):
    defaults = DEFAULT_SETTINGS["gui"]
    _validate_string_is_in_set(section, defaults, VALID_SEARCH_WIDGET_LAYOUTS, "central-widget-layout")
    _validate_boolean(section, defaults, "show-toolbar")


def _validate_debug_section(section: configparser.SectionProxy):
    defaults = DEFAULT_SETTINGS["debug"]
    _validate_boolean(section, defaults, "cutelog-integration")
    _validate_boolean(section, defaults, "write-log-file")
    _validate_string_is_in_set(section, defaults, VALID_LOG_LEVELS, "log-level")


def _validate_print_guessing_section(section: configparser.SectionProxy):
    defaults = DEFAULT_SETTINGS["print-guessing"]
    for key in section.keys():
        _validate_boolean(section, defaults, key)


def _validate_default_save_paths_section(section: configparser.SectionProxy):
    defaults = DEFAULT_SETTINGS["default-save-paths"]
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
        

# Read the settings from file during module import
# This has to be performed before any modules containing GUI classes are imported.
read_settings_from_file()
