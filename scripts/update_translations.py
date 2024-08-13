#!/usr/bin/env python

# Copyright (C) 2024 Thomas Hess <thomas.hess@udo.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
Management script for application translations
"""

import argparse
import itertools
import pathlib
import subprocess
from typing import Callable, NamedTuple

# Mapping between source locales, as provided by Crowdin, and the target, as expected/loaded by Qt.
# TODO: Investigate, how systems behave in locales requiring the country as disambiguation, like en or zh.
LOCALES = {
    "de-DE": "de",
    "en-GB": "en_GB",
    "en-US": "en_US",
    "es-ES": "es",
    "fr-FR": "fr",
    "it-IT": "it",
    "ja-JP": "ja",
    "ko-KR": "ko",
    "pt-PT": "pt",
    "ru-RU": "ru",
    "zh-CN": "zh_CN",
    "zh-TW": "zh_TW",
}
TRANSLATIONS_DIR = pathlib.Path("mtg_proxy_printer/resources/translations/")

class Namespace(NamedTuple):
    """Mock namespace for type hinting"""
    command: Callable[["Namespace"], None]


def parse_args() -> Namespace:
    command_table: dict[str, Callable[[Namespace], None]] = {
        "upload": upload_raw_strings,
        "download": download_new_translations,
        "compile": compile_translations,
        "clean": clean_translations,
    }
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(required=True, dest="command", help="Action to perform")
    upload_parser = commands.add_parser("upload", help="Run Qt lupdate to extract new strings and upload them to Crowdin. Requires an API key")
    download_parser = commands.add_parser("download", help="Download translation updates from Crowdin")
    compile_parser = commands.add_parser("compile", help="Compile translations into the importable binary format for distribution")
    clean_parser = commands.add_parser("clean", help="Delete compiled, binary translation files")
    args = parser.parse_args()
    # It seems that it is not possible to set the subcommand entry function directly,
    # (like in store_const=<function_object>)
    # so look it up and set it in the Namespace object after the parsing step.
    args.command = command_table[args.command]
    return args
    

def verify_crowdin_cli_present():
    try:
        subprocess.check_output("crowdin")
    except FileNotFoundError as e:
        raise RuntimeError("The required Crowdin CLI client is not installed in the PATH, exiting.") from e


def register_new_raw_strings():
    TRANSLATIONS_DIR.mkdir(parents=True, exist_ok=True)
    # PyQt5
    package = pathlib.Path("mtg_proxy_printer")
    files = list(itertools.chain(package.rglob("*.py"), package.rglob("*.ui")))
    subprocess.call([
        "pylupdate5",
        "-noobsolete", "-verbose",
        *files,
        "-ts", TRANSLATIONS_DIR/"mtgproxyprinter_en-US.ts"
    ])
    ''' PySide6
    subprocess.call([
        "pyside6-lupdate",
        "-source-language", "en_US",
        "-recursive", "-no-obsolete",
        "-extensions", "py,ui",
        "mtg_proxy_printer",
        "-ts", TRANSLATIONS_DIR/"mtgproxyprinter_en-US.ts"
    ])
    '''


def upload_raw_strings(args: Namespace):
    register_new_raw_strings()
    verify_crowdin_cli_present()
    subprocess.call([
        "crowdin", "upload"
    ])


def download_new_translations(args: Namespace):

    verify_crowdin_cli_present()
    subprocess.call([
        "crowdin", "download"
    ])


def get_lrelease():
    try:
        subprocess.check_output("lrelease")
    except FileNotFoundError:
        print("lrelease not found on PATH. Falling back to the executable supplied by PySide2.")
        import sys
        exe = pathlib.Path(sys.executable)
        venv = exe.parent.parent
        lrelease = venv / "Lib" / "site-packages" / "PySide2" / "lrelease.exe"
        return lrelease
    else:
        return "lrelease"


def compile_translations(args: Namespace):
    lrelease = get_lrelease()
    for source_name, target_name in LOCALES.items():
        source = TRANSLATIONS_DIR / f"mtgproxyprinter_{source_name}.ts"
        target = TRANSLATIONS_DIR / f"mtgproxyprinter_{target_name}.qm"
        subprocess.call([
            lrelease, "-compress",
            source, "-qm", target
        ])


def clean_translations(args: Namespace):
    target = TRANSLATIONS_DIR.glob("mtgproxyprinter_*.qm")
    for file in target:
        file.unlink()


def main():
    args = parse_args()
    args.command(args)


if __name__ == "__main__":
    main()
