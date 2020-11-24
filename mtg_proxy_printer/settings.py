# Copyright (C) 2020 Thomas Hess <thomas.hess@udo.edu>

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
import pathlib

import mtg_proxy_printer.meta_data

__all__ = [
    "settings",
    "DEFAULT_SETTINGS",
    "read_settings_from_file",
    "write_settings_to_file"
]

config_file_path = pathlib.Path(mtg_proxy_printer.meta_data.data_directories.user_config_dir, "MTGProxyPrinter.ini")
settings = configparser.ConfigParser()
DEFAULT_SETTINGS = configparser.ConfigParser()


DEFAULT_SETTINGS["images"] = {
    "preferred-language": "en",
    "avoid-low-resolution-images": 'false'
}
DEFAULT_SETTINGS["downloads"] = {
    "download-cards-depicting-racism": 'false'
}
DEFAULT_SETTINGS["documents"] = {
    "paper-height-mm": "297",
    "paper-width-mm": "210",
    "margin-top-mm": "5",
    "margin-bottom-mm": "5",
    "margin-left-mm": "5",
    "margin-right-mm": "5",
    "image-spacing-horizontal-mm": "0",
    "image-spacing-vertical-mm": "0",
}


def read_settings_from_file():
    global settings, DEFAULT_SETTINGS
    if not config_file_path.exists():
        settings = DEFAULT_SETTINGS
    else:
        settings.read(config_file_path)
        read_sections = set(settings.sections())
        known_sections = set(DEFAULT_SETTINGS.sections())
        # Synchronise sections
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


def write_settings_to_file():
    global settings
    if not config_file_path.parent.exists():
        config_file_path.parent.mkdir(parents=True)
    with config_file_path.open("w") as config_file:
        settings.write(config_file)
