#!/usr/bin/env python

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


"""
Management script for application translations
"""

import argparse
import json
import math
import pathlib
import re
import subprocess
import sys
from typing import Callable, NamedTuple
from xml.etree import ElementTree

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.resolve()))
from mtg_proxy_printer.settings import VALID_LANGUAGES

# Mapping between source locales, as provided by Crowdin, and the target, as expected/loaded by Qt.
# TODO: Investigate, how systems behave in locales requiring the country as disambiguation, like en or zh.
LOCALES = {
    "de-DE": "de",
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

ROOT_DIR = pathlib.Path(__file__).parent.parent.resolve()
TRANSLATIONS_DIR = ROOT_DIR / "resources/translations"
crowdin_yml_path = ROOT_DIR / "crowdin.yml"
SOURCES_PATH = pathlib.Path(
    # Fetch the name of the sources .ts file from crowdin.yml.
    # (Since Python does not come with a YAML parser, use a simple RE for data extraction)
    re.search(
        r'"source":\s*"(?P<path>.+)",',
        crowdin_yml_path.read_text("utf-8")
    )["path"]
)


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
    commands.add_parser("upload", help="Run Qt lupdate to extract new strings and upload them to Crowdin. Requires an API key")
    commands.add_parser("download", help="Download translation updates from Crowdin. Requires an API key")
    commands.add_parser("compile", help="Compile translations into the importable binary format for distribution")
    commands.add_parser("clean", help="Delete compiled, binary translation files")
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
    subprocess.call([
        "pyside6-lupdate",
        "-source-language", "en_US",
        "-recursive", "-no-obsolete",
        "-extensions", "py,ui",
        "mtg_proxy_printer",
        "-ts", SOURCES_PATH
    ])


def upload_raw_strings(args: Namespace):
    """Updates the sources .ts from code, then uploads it to the Crowdin API"""
    register_new_raw_strings()
    verify_crowdin_cli_present()
    subprocess.call([
        "crowdin", "upload"
    ])


def download_new_translations(args: Namespace):
    """Downloads translated .ts files from Crowdin via the API, and updates the translation progress dict"""
    verify_crowdin_cli_present()
    subprocess.call([
        "crowdin", "download"
    ])
    translation_progress: dict[str, int] = {}
    for file in TRANSLATIONS_DIR.glob("*.ts"):  # type: pathlib.Path
        # Use get() to keep the mtgproxyprinter_sources.ts file by mapping it to the "System locale" value (empty str)
        if (locale := LOCALES.get(file.stem.split("_")[1], "")) not in VALID_LANGUAGES:
            # Strip all translations that are not registered as valid locale setting
            file.unlink()
        elif locale:
            translation_progress[locale] = read_translation_progress(file)
    with (TRANSLATIONS_DIR / "progress.json").open("wt") as progress_file:
        json.dump(translation_progress, progress_file, indent=4, sort_keys=True, allow_nan=False)
        progress_file.write("\n")


def read_translation_progress(file):
    tree = ElementTree.parse(file)
    all_translations = sum(1 for _ in tree.iterfind(".//translation"))
    finished = all_translations -  sum(1 for _ in tree.iterfind(".//translation[@type='unfinished']"))
    return math.floor(100 * finished / all_translations)


def get_lrelease():
    """
    Determine the lrelease binary name. Tries to find in on $PATH, or falls back to using the PySide2-supplied binary
    from the virtual environment.
    """
    try:
        subprocess.check_output(["lrelease", "-version"])
    except FileNotFoundError:
        print("lrelease not found on PATH. Falling back to the executable supplied by PySide2.")
        import sys
        exe = pathlib.Path(sys.executable)
        venv = exe.parent.parent
        lrelease6 = venv / "Lib" / "site-packages" / "PySide6" / "lrelease.exe"
        if not lrelease6.is_file():
            raise RuntimeError("No fallback lrelease executable found")
        return lrelease6
    else:
        return "lrelease"


def compile_translations(args: Namespace):
    """Compiles .ts files into importable, binary translation files with .qm suffix."""
    lrelease = get_lrelease()
    # Iterate over the defined locales, and not the directory. This skips the sources .ts file
    for source_name, target_name in LOCALES.items():
        source = TRANSLATIONS_DIR / f"mtgproxyprinter_{source_name}.ts"
        if not source.is_file():
            continue
        target = TRANSLATIONS_DIR / f"mtgproxyprinter_{target_name}.qm"
        subprocess.call([
            lrelease, "-compress",
            source, "-qm", target
        ])


def clean_translations(args: Namespace):
    """Deletes all compiled translation files. Keeps .ts files in place"""
    target = TRANSLATIONS_DIR.glob("mtgproxyprinter_*.qm")
    for file in target:
        file.unlink()


def main():
    args = parse_args()
    args.command(args)


if __name__ == "__main__":
    main()
