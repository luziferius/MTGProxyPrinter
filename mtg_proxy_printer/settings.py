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


def read_settings_from_file():
    global settings, DEFAULT_SETTINGS
    if not config_file_path.exists():
        settings = DEFAULT_SETTINGS
    else:
        settings.read(config_file_path)
        all_known_sections = set(DEFAULT_SETTINGS.sections())
        for section in settings.sections():
            # Filter and remove outdated sections
            if section not in all_known_sections:
                settings.remove_section(section)
        for section in DEFAULT_SETTINGS.sections():
            if not settings.has_section(section):
                # Copy new section into the opened settings.
                settings.add_section(section)
                for option, value in DEFAULT_SETTINGS[section].items():
                    settings[section][option]=value


def write_settings_to_file():
    global settings
    if not config_file_path.parent.exists():
        config_file_path.parent.mkdir(parents=True)
    with config_file_path.open("w") as config_file:
        settings.write(config_file)
