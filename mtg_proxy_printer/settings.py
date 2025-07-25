#  Copyright © 2020-2025  Thomas Hess <thomas.hess@udo.edu>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.


import logging
import math
import pathlib
import re
import typing
import tokenize
from collections import defaultdict

import pint
from PyQt5.QtCore import QStandardPaths, QLocale
from PyQt5.QtGui import QPageSize, QPageLayout, QColor
from PyQt5.QtPrintSupport import QPrinterInfo

import mtg_proxy_printer.app_dirs
import mtg_proxy_printer.meta_data
import mtg_proxy_printer.natsort
from mtg_proxy_printer.units_and_sizes import \
    CardSizes, ConfigParser, SectionProxy, unit_registry, T, QuantityT, PageSizeManager, is_acceptable_page_size, \
    Unit

StandardLocation = QStandardPaths.StandardLocation
LocateOption = QStandardPaths.LocateOption
Territory = QLocale.Country  # TODO: Adjust for PySide6
PageSizeId = QPageSize.PageSizeId
Orientation = QPageLayout.Orientation

__all__ = [
    "settings",
    "DEFAULT_SETTINGS",
    "read_settings_from_file",
    "write_settings_to_file",
    "validate_settings",
    "update_stored_version_string",
    "get_boolean_card_filter_keys",
    "parse_card_set_filters",
]


Letter = QPageSize.PageSizeId.Letter
# https://www.unicode.org/cldr/charts/47/supplemental/territory_information.html
LOCATION_PAPER_SIZE_TABLE = defaultdict(lambda: PageSizeId.A4, {
    Territory.Belize: Letter,
    Territory.Canada: Letter,
    Territory.Chile: Letter,
    Territory.Colombia: Letter,
    Territory.CostaRica: Letter,
    Territory.DominicanRepublic: Letter,
    Territory.ElSalvador: Letter,
    Territory.Guatemala: Letter,
    Territory.Guyana: Letter,
    Territory.Nicaragua: Letter,
    Territory.Panama: Letter,
    Territory.Philippines: Letter,
    Territory.PuertoRico: Letter,
    Territory.UnitedStates: Letter,
    Territory.UnitedStatesMinorOutlyingIslands: Letter,
    Territory.UnitedStatesVirginIslands: Letter,
    Territory.Venezuela: Letter,
})


def get_default_paper_size() -> str:
    system_country = QLocale.system().country()
    default = PageSizeManager.PageSizeReverse[LOCATION_PAPER_SIZE_TABLE[system_country]]
    printer_info = QPrinterInfo.defaultPrinter()
    if printer_info.isNull():
        return default
    page_size = printer_info.defaultPageSize()
    if page_size.isValid() and is_acceptable_page_size(page_size):
        return PageSizeManager.PageSizeReverse[page_size.id()]
    return default


class QuantityLimits(typing.NamedTuple):
    """
    Defines acceptable values for Pint quantities.
    - Minimum and maximum define the acceptable, inclusive range.
    - Acceptable_units defines the acceptable units for the desired unit dimensionality.
      For example, inch and mm can be acceptable lengths, light years, parsecs, and other expressions evaluating
      to a length are not.
    - target_unit is the fallback unit, if the dimensionality is compatible, but the unit is not acceptable:
      "1N*1s²/10kg" is a length (100mm), but not of an acceptable unit, so it will be converted to the target unit
    """
    minimum: QuantityT
    maximum: QuantityT
    acceptable_units: typing.Set[Unit]
    target_unit: Unit


mm = unit_registry.mm
point = unit_registry.point
degree = unit_registry.degree

config_file_path = mtg_proxy_printer.app_dirs.data_directories.user_config_path / "MTGProxyPrinter.ini"
settings = ConfigParser()
DEFAULT_SETTINGS = ConfigParser()
# Support three-valued boolean logic by adding values that parse to None, instead of True/False.
# This will be used to store “unset” boolean settings.
ConfigParser.BOOLEAN_STATES.update({
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
#   - If adding a new section, also add a validator function for that section.
# - Add the new key to the validator of the section it’s in. The validator has to check that the value can be properly
#   cast into the expected type and perform a value range check.
# - Add the option to the Settings window UI
# - Wire up save and load functionality for the new key in the Settings UI
# - The Settings GUI class has to also do a value range check.

DEFAULT_SETTINGS["cards"] = {
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
    "hide-banned-in-oathbreaker": "False",
    "hide-banned-in-pauper": "False",
    "hide-banned-in-penny": "False",
    "hide-banned-in-pioneer": "False",
    "hide-banned-in-standard": "False",
    "hide-banned-in-vintage": "False",
    "hide-white-bordered": "False",
    "hide-gold-bordered": "False",
    "hide-borderless": "False",
    "hide-extended-art": "False",
    "hide-funny-cards": "False",
    "hide-token": "False",
    "hide-digital-cards": "True",
    "hide-reversible-cards": "False",
    "hide-art-series-cards": "False",
    "hidden-sets": "",
}

DEFAULT_MARGINS = 5*mm
DEFAULT_SETTINGS["documents"] = {
    "card-bleed": "0 mm",
    "paper-orientation": PageSizeManager.PageOrientationReverse[Orientation.Portrait],
    "paper-size": get_default_paper_size(),
    "custom-page-height": "297 mm",
    "custom-page-width": "210 mm",
    "margin-top": str(DEFAULT_MARGINS),
    "margin-bottom": str(DEFAULT_MARGINS),
    "margin-left": str(DEFAULT_MARGINS),
    "margin-right": str(DEFAULT_MARGINS),
    "row-spacing": "0 mm",
    "column-spacing": "0 mm",
    "print-cut-marker": "False",
    "print-sharp-corners": "False",
    "print-page-numbers": "False",
    "default-document-name": "",
    "watermark-text": "",
    "watermark-font-size": "30 points",
    "watermark-pos-x": "10 mm",
    "watermark-pos-y": "5 mm",
    "watermark-angle": "0 degree",
    "watermark-color": "#ffff0000",
}

DEFAULT_LENGTH_LIMIT = QuantityLimits(0*mm, 10000*mm, {mm}, mm)
DOCUMENT_SETTINGS_QUANTITY_LIMITS = {
    # Value range limits and permissible units per settings key.
    "card-bleed": DEFAULT_LENGTH_LIMIT,
    "custom-page-height": DEFAULT_LENGTH_LIMIT,
    "custom-page-width": DEFAULT_LENGTH_LIMIT,
    "margin-top": DEFAULT_LENGTH_LIMIT,
    "margin-bottom": DEFAULT_LENGTH_LIMIT,
    "margin-left": DEFAULT_LENGTH_LIMIT,
    "margin-right": DEFAULT_LENGTH_LIMIT,
    "row-spacing": DEFAULT_LENGTH_LIMIT,
    "column-spacing": DEFAULT_LENGTH_LIMIT,
    "watermark-font-size": QuantityLimits(0*point, 1000*point, {point}, point),
    "watermark-pos-x": QuantityLimits(-100*mm, 100*mm, {mm}, mm),
    "watermark-pos-y": QuantityLimits(-100*mm, 100*mm, {mm}, mm),
    "watermark-angle": QuantityLimits(-360*degree, 360*degree, {degree}, degree),
}


DEFAULT_SETTINGS["default-filesystem-paths"] = {
    "document-save-path": QStandardPaths.locate(StandardLocation.DocumentsLocation, "", LocateOption.LocateDirectory),
    "deck-list-search-path": QStandardPaths.locate(StandardLocation.DownloadLocation, "", LocateOption.LocateDirectory),
}
DEFAULT_SETTINGS["gui"] = {
    "central-widget-layout": "columnar",
    "show-toolbar": "True",
    "language": "",
    "gui-open-maximized": "True",
    "wizards-open-maximized": "False",
}
VALID_SEARCH_WIDGET_LAYOUTS = {"horizontal", "columnar", "tabbed"}
VALID_LANGUAGES = {
    "", "de", "en_US", "fr",
}
DEFAULT_SETTINGS["debug"] = {
    "cutelog-integration": "False",
    "write-log-file": "True",
    "log-level": "INFO",
}
VALID_LOG_LEVELS = set(map(logging.getLevelName, range(10, 60, 10)))
DEFAULT_SETTINGS["decklist-import"] = {
    "enable-print-guessing-by-default": "True",
    "prefer-already-downloaded-images": "True",
    "always-translate-deck-lists": "False",
    "remove-basic-wastes": "False",
    "remove-snow-basics": "False",
    "automatically-remove-basic-lands": "False",
}
DEFAULT_SETTINGS["update-checks"] = {
    "last-used-version": mtg_proxy_printer.meta_data.__version__,
    "check-for-application-updates": "None",
    "check-for-card-data-updates": "None",
}
DEFAULT_SETTINGS["printer"] = {
    "borderless-printing": "True",
    "landscape-compatibility-workaround": "False",
    "horizontal-offset": "0 mm",
}
DEFAULT_SETTINGS["export"] = {
    "export-path": QStandardPaths.locate(StandardLocation.DocumentsLocation, "", LocateOption.LocateDirectory),
    "pdf-page-count-limit": "0",
    "landscape-compatibility-workaround": "False",
    "png-background-color": "#ffffffff",
}
MAX_DOCUMENT_NAME_LENGTH = 200





def round_to_nearest_multiple(value: T, multiple: T) -> T:
    """Rounds the given value to the nearest multiple of "multiple"."""
    return round(value/multiple)*multiple


def clamp_to_supported_range(value: QuantityT, limits: QuantityLimits) -> QuantityT:
    """Clamps numerical document settings to the supported value range"""
    return min(max(value, limits.minimum),  limits.maximum)


def get_boolean_card_filter_keys():
    """Returns all keys for boolean card filter settings."""
    keys = DEFAULT_SETTINGS["card-filter"].keys()
    keys = [item for item in keys if item.startswith("hide-")]
    return keys


def parse_card_set_filters(input_settings: ConfigParser = settings) -> typing.Set[str]:
    """Parses the hidden sets filter setting into a set of lower-case MTG set codes."""
    raw = input_settings["card-filter"]["hidden-sets"]
    raw = raw.lower()
    deduplicated = set(raw.split())
    return deduplicated


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
    settings["update-checks"]["last-used-version"] = DEFAULT_SETTINGS["update-checks"]["last-used-version"]


def was_application_updated() -> bool:
    """
    Returns True, if the application was updated since last start, i.e. if the internal version number
    is greater than the version string stored in the configuration file. Returns False otherwise.
    """
    return mtg_proxy_printer.natsort.str_less_than(
        settings["update-checks"]["last-used-version"],
        mtg_proxy_printer.meta_data.__version__
    )


def validate_settings(read_settings: ConfigParser):
    """
    Called after reading the settings from disk. Ensures that all settings contain valid values and expected types.
    I.e. checks that settings that should contain booleans do contain valid booleans, options that should contain
    non-negative integers do so, etc. If an option contains an invalid value, the default value is restored.
    """
    _validate_card_filter_section(read_settings)
    _validate_images_section(read_settings)
    _validate_documents_section(read_settings)
    _validate_update_checks_section(read_settings)
    _validate_gui_section(read_settings)
    _validate_debug_section(read_settings)
    _validate_decklist_import_section(read_settings)
    _validate_default_filesystem_paths_section(read_settings)
    _validate_printer_section(read_settings)
    _validate_export_section(read_settings)


def _validate_card_filter_section(to_validate: ConfigParser, section_name: str = "card-filter"):
    section = to_validate[section_name]
    defaults = DEFAULT_SETTINGS[section_name]
    boolean_keys = get_boolean_card_filter_keys()
    for key in boolean_keys:
        _validate_boolean(section, defaults, key)


def _validate_images_section(to_validate: ConfigParser, section_name: str = "cards"):
    section = to_validate[section_name]
    defaults = DEFAULT_SETTINGS[section_name]
    for key in ("automatically-add-opposing-faces",):
        _validate_boolean(section, defaults, key)
    language = section["preferred-language"]
    if not re.fullmatch(r"[a-z]{2}", language):
        # Only syntactic validation: Language contains a string of exactly two lower case ascii letters
        _restore_default(section, defaults, "preferred-language")


def _validate_documents_section(to_validate: ConfigParser, section_name: str = "documents"):
    card_size = mtg_proxy_printer.units_and_sizes.CardSizes.OVERSIZED
    card_height = card_size.height.to(mm, "print")
    card_width = card_size.width.to(mm, "print")
    section = to_validate[section_name]
    if (document_name := section["default-document-name"]) and len(document_name) > MAX_DOCUMENT_NAME_LENGTH:
        section["default-document-name"] = document_name[:MAX_DOCUMENT_NAME_LENGTH-1] + "…"
    defaults = DEFAULT_SETTINGS[section_name]
    boolean_settings = {"print-cut-marker", "print-sharp-corners", "print-page-numbers", }
    string_settings = {"default-document-name", "paper-size", "paper-orientation", "watermark-text", }
    color_settings = {"watermark-color", }
    for key in section.keys():
        if key in DOCUMENT_SETTINGS_QUANTITY_LIMITS:
            _validate_quantity(section, defaults, key, DOCUMENT_SETTINGS_QUANTITY_LIMITS[key])
        elif key in boolean_settings:
            _validate_boolean(section, defaults, key)
        elif key in string_settings:
            pass
        elif key in color_settings:
            _validate_color(section, defaults, key)
        else:
            raise RuntimeError(f"BUG: Unhandled key found: {key}")

    if section["paper-size"] not in PageSizeManager.PageSize:
        _restore_default(section, defaults, "paper-size")
    if section["paper-orientation"] not in PageSizeManager.PageOrientation:
        _restore_default(section, defaults, "paper-orientation")
    # Check some semantic properties
    available_height = section.get_quantity("custom-page-height") - \
        (section.get_quantity("margin-top") + section.get_quantity("margin-bottom"))
    available_width = section.get_quantity("custom-page-width") - \
        (section.get_quantity("margin-left") + section.get_quantity("margin-right"))

    if available_height < card_height:
        # Can not fit a single card on a page
        section["custom-page-height"] = defaults["custom-page-height"]
        section["margin-top"] = defaults["margin-top"]
        section["margin-bottom"] = defaults["margin-bottom"]
    if available_width < card_width:
        # Can not fit a single card on a page
        section["custom-page-width"] = defaults["custom-page-width"]
        section["margin-left"] = defaults["margin-left"]
        section["margin-right"] = defaults["margin-right"]

    # Re-calculate, if width or height was reset
    available_height = section.get_quantity("custom-page-height") - \
        (section.get_quantity("margin-top") + section.get_quantity("margin-bottom"))
    available_width = section.get_quantity("custom-page-width") - \
        (section.get_quantity("margin-left") + section.get_quantity("margin-right"))
    # FIXME: This looks like a dimensional error. Validate and test!
    if section.get_quantity("column-spacing") > (available_spacing_vertical := available_height - card_height):
        # Prevent column spacing from overlapping with bottom margin
        section["column-spacing"] = str(available_spacing_vertical)
    if section.get_quantity("row-spacing") > (available_spacing_horizontal := available_width - card_width):
        # Prevent row spacing from overlapping with right margin
        section["row-spacing"] = str(available_spacing_horizontal)


def _validate_update_checks_section(to_validate: ConfigParser, section_name: str = "update-checks"):
    section = to_validate[section_name]
    defaults = DEFAULT_SETTINGS[section_name]
    if not VERSION_CHECK_RE.fullmatch(section["last-used-version"]):
        section["last-used-version"] = defaults["last-used-version"]
    for option in ("check-for-application-updates", "check-for-card-data-updates"):
        _validate_three_valued_boolean(section, defaults, option)


def _validate_gui_section(to_validate: ConfigParser, section_name: str = "gui"):
    section = to_validate[section_name]
    defaults = DEFAULT_SETTINGS[section_name]
    _validate_string_is_in_set(section, defaults, VALID_SEARCH_WIDGET_LAYOUTS, "central-widget-layout")
    for key in ("show-toolbar", "gui-open-maximized", "wizards-open-maximized"):
        _validate_boolean(section, defaults, key)
    _validate_string_is_in_set(section, defaults, VALID_LANGUAGES, "language")


def _validate_debug_section(to_validate: ConfigParser, section_name: str = "debug"):
    section = to_validate[section_name]
    defaults = DEFAULT_SETTINGS[section_name]
    _validate_boolean(section, defaults, "cutelog-integration")
    _validate_boolean(section, defaults, "write-log-file")
    _validate_string_is_in_set(section, defaults, VALID_LOG_LEVELS, "log-level")


def _validate_decklist_import_section(to_validate: ConfigParser, section_name: str = "decklist-import"):
    section = to_validate[section_name]
    defaults = DEFAULT_SETTINGS[section_name]
    for key in section.keys():
        _validate_boolean(section, defaults, key)


def _validate_default_filesystem_paths_section(
        to_validate: ConfigParser, section_name: str = "default-filesystem-paths"):
    section = to_validate[section_name]
    defaults = DEFAULT_SETTINGS[section_name]
    for key in section.keys():
        _validate_path_to_directory(section, defaults, key)


def _validate_printer_section(to_validate: ConfigParser, section_name: str = "printer"):
    section = to_validate[section_name]
    defaults = DEFAULT_SETTINGS[section_name]
    for key, default in defaults.items():
        if default in {"True", "False"}:
            _validate_boolean(section, defaults, key)
        else:
            limit = QuantityLimits(-100*mm, 100*mm, {mm}, mm)
            _validate_quantity(section, defaults, key, limit)


def _validate_export_section(to_validate: ConfigParser, section_name: str = "export"):
    section = to_validate[section_name]
    defaults = DEFAULT_SETTINGS[section_name]
    _validate_path_to_directory(section, defaults, "export-path")
    _validate_non_negative_int(section, defaults, "pdf-page-count-limit")
    _validate_boolean(section, defaults, "landscape-compatibility-workaround")
    _validate_color(section, defaults, "png-background-color")


def _validate_path_to_directory(section: SectionProxy, defaults: SectionProxy, key: str):
    try:
        if not pathlib.Path(section[key]).resolve().is_dir():
            raise ValueError()
    except Exception:
        _restore_default(section, defaults, key)


def _validate_boolean(section: SectionProxy, defaults: SectionProxy, key: str):
    try:
        if section.getboolean(key) is None:
            raise ValueError()
    except ValueError:
        _restore_default(section, defaults, key)


def _validate_three_valued_boolean(section: SectionProxy, defaults: SectionProxy, key: str):
    try:
        section.getboolean(key)
    except ValueError:
        _restore_default(section, defaults, key)


def _validate_non_negative_int(section: SectionProxy, defaults: SectionProxy, key: str):
    try:
        if section.getint(key) < 0:
            raise ValueError()
    except ValueError:
        _restore_default(section, defaults, key)


def _validate_quantity(section: SectionProxy, defaults: SectionProxy, key: str, limits: QuantityLimits):
    try:
        value = section.get_quantity(key)
        if unit_conversion_required := (value.units not in limits.acceptable_units):
            value = value.to(limits.target_unit, "print")
        clamped = clamp_to_supported_range(value, limits)
        # Both value and clamped share the same unit, so comparing magnitudes is fine.
        if unit_conversion_required or not math.isclose(value.magnitude, clamped.magnitude):
            section[key] = str(clamped)
    # Unit-less values raise AttributeError, non-length values, like grams or seconds, raise DimensionalityError
    # Invalid expressions raise TokenError
    except (ValueError, pint.DimensionalityError, AttributeError, tokenize.TokenError):
        _restore_default(section, defaults, key)


def _validate_string_is_in_set(section: SectionProxy, defaults: SectionProxy, valid_options: typing.Set[str], key: str):
    """Checks if the value of the option is one of the allowed values, as determined by the given set of strings."""
    if section[key] not in valid_options:
        _restore_default(section, defaults, key)


def _validate_color(section: SectionProxy, defaults: SectionProxy, key: str):
    if not QColor.isValidColor(section.get(key)):
        _restore_default(section, defaults, key)


def _restore_default(section: SectionProxy, defaults: SectionProxy, key: str):
    section[key] = defaults[key]


def migrate_settings(to_migrate: ConfigParser):
    """Run setting file migrations."""
    _01_migrate_layout_setting(to_migrate)
    _02_migrate_download_settings(to_migrate)
    _03_migrate_default_save_paths_settings(to_migrate)
    _04_migrate_print_guessing_settings(to_migrate)
    _05_migrate_image_spacing_settings(to_migrate)
    _06_migrate_to_pdf_export_section(to_migrate)
    _07_migrate_document_settings_to_pint(to_migrate)
    _08_migrate_images_to_cards_section(to_migrate)
    _09_migrate_application_to_update_checks_section(to_migrate)
    _10_migrate_export_section(to_migrate)
    _11_migrate_custom_paper_size_keys(to_migrate)


def _01_migrate_layout_setting(to_migrate: ConfigParser):
    try:
        gui_section = to_migrate["gui"]
        layout = gui_section["search-widget-layout"]
    except KeyError:
        return
    else:
        if layout == "vertical":
            layout = "columnar"
        gui_section["central-widget-layout"] = layout
        
        
def _02_migrate_download_settings(to_migrate: ConfigParser):
    target_section_name = "card-filter"
    if to_migrate.has_section(target_section_name) or not to_migrate.has_section("downloads"):
        return
    download_section = to_migrate["downloads"]
    to_migrate.add_section(target_section_name)
    filter_section = to_migrate[target_section_name]
    for source_setting in to_migrate["downloads"].keys():
        target_setting = source_setting.replace("download-", "hide-")
        try:
            new_value = not download_section.getboolean(source_setting)
        except ValueError:
            pass
        else:
            filter_section[target_setting] = str(new_value)


def _03_migrate_default_save_paths_settings(to_migrate: ConfigParser):
    source_section_name = "default-save-paths"
    target_section_name = "default-filesystem-paths"
    if to_migrate.has_section(target_section_name) or not to_migrate.has_section(source_section_name):
        return
    to_migrate.add_section(target_section_name)
    to_migrate[target_section_name].update(to_migrate[source_section_name])


def _04_migrate_print_guessing_settings(to_migrate: ConfigParser):
    source_section_name = "print-guessing"
    target_section_name = "decklist-import"
    if to_migrate.has_section(target_section_name) or not to_migrate.has_section(source_section_name):
        return
    to_migrate.add_section(target_section_name)
    target = to_migrate[target_section_name]
    source = to_migrate[source_section_name]
    # Force-overwrite with the new default when migrating. Having this disabled has negative UX impact, so should not
    # be disabled by default.
    target["enable-print-guessing-by-default"] = "True"
    target["prefer-already-downloaded-images"] = source["prefer-already-downloaded"]
    target["always-translate-deck-lists"] = source.get("always-translate-deck-lists", "False")


def _05_migrate_image_spacing_settings(to_migrate: ConfigParser):
    section = to_migrate["documents"]
    if "image-spacing-horizontal-mm" not in section:
        return
    section["row-spacing-mm"] = section["image-spacing-horizontal-mm"]
    section["column-spacing-mm"] = section["image-spacing-vertical-mm"]
    del section["image-spacing-horizontal-mm"]
    del section["image-spacing-vertical-mm"]


def _06_migrate_to_pdf_export_section(to_migrate: ConfigParser):
    section_name = "pdf-export"
    if to_migrate.has_section(section_name) or to_migrate.has_section("export"):
        return
    to_migrate.add_section(section_name)
    target = to_migrate[section_name]
    target["pdf-page-count-limit"] = to_migrate["documents"].get("pdf-page-count-limit", "0")
    try:
        del to_migrate["documents"]["pdf-page-count-limit"]
    except KeyError:
        pass
    if to_migrate.has_section("default-filesystem-paths"):
        try:
            target["pdf-export-path"] = to_migrate["default-filesystem-paths"]["pdf-export-path"]
            del to_migrate["default-filesystem-paths"]["pdf-export-path"]
        except KeyError:
            pass
    else:
        target["pdf-export-path"] = DEFAULT_SETTINGS["export"]["export-path"]


def _07_migrate_document_settings_to_pint(to_migrate: ConfigParser):
    section = to_migrate["documents"]
    if "margin-top-mm" not in section:
        return
    for key in ("card-bleed", "paper-height", "paper-width",
            "margin-top", "margin-bottom", "margin-left", "margin-right",
            "row-spacing", "column-spacing"):
        old_key = f"{key}-mm"
        if old_key in section:
            section[key] = f"{section[old_key]} mm"
            del section[old_key]
        else:
            section[key] = "0 mm"


def _08_migrate_images_to_cards_section(to_migrate: ConfigParser):
    if "images" not in to_migrate:
        return
    to_migrate["cards"] = to_migrate["images"]
    del to_migrate["images"]


def _09_migrate_application_to_update_checks_section(to_migrate: ConfigParser):
    if "application" not in to_migrate:
        return
    to_migrate["update-checks"] = to_migrate["application"]
    del to_migrate["application"]


def _10_migrate_export_section(to_migrate: ConfigParser):
    if "pdf-export" not in to_migrate:
        return
    if "export" in to_migrate:  # New and old section present, just discard the old. Should not happen normally.
        del to_migrate["pdf-export"]
        return
    to_migrate["export"] = to_migrate["pdf-export"]
    del to_migrate["pdf-export"]
    section = to_migrate["export"]
    section["export-path"] = section["pdf-export-path"]
    del section["pdf-export-path"]


def _11_migrate_custom_paper_size_keys(to_migrate: ConfigParser):
    section = to_migrate["documents"]
    for key in ("paper-width", "paper-height"):
        if key in section:
            _, dim = key.split("-")
            section[f"custom-page-{dim}"] = section[key]
            del section[key]


# Read the settings from file during module import
# This has to be performed before any modules containing GUI classes are imported.
read_settings_from_file()
