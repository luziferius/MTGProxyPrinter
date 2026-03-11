#!/usr/bin/env python

#  Copyright © 2020-2026  Thomas Hess <thomas.hess@udo.edu>
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
This script compiles Qt Ui files.
It has two usage modes:
- Compiling into importable Python modules. This is used for built deliverables,
  like Python wheels and application bundles created via cx_Freeze.
- Creation of type hinting stubs with suffix ".pyi". These are used during development,
  to provide type hinting and autocompletion for the Ui classes defined by the UI files.
"""

import argparse
import ast
import asyncio
import asyncio.subprocess
import itertools
try:
    from os import process_cpu_count
except ImportError:  # Python < 3.13
    from os import cpu_count as process_cpu_count
import textwrap
from pathlib import Path
import shutil
from typing import NamedTuple, TypeVar, Iterable, Type, Any, Callable, Coroutine

SOURCE_ROOT = Path(__file__).parent.parent  # Checkout root directory
MAIN_PACKAGE = SOURCE_ROOT / "mtg_proxy_printer"
UI_SOURCE_PATH = SOURCE_ROOT / "resources/ui"  # UI files live here
TARGET_PATH = MAIN_PACKAGE / "ui/generated"  # Package containing generated modules/type hinting stubs
T = TypeVar("T")
ClassRegistry = dict[str, ast.ImportFrom]
UsedClasses = set[str]
Statements = list[ast.stmt]
STDIN = asyncio.subprocess.DEVNULL
STDOUT = asyncio.subprocess.PIPE
STDERR = asyncio.subprocess.STDOUT
thread_count = process_cpu_count() or 2
TaskThrottle = asyncio.BoundedSemaphore(thread_count)


class Assignment(NamedTuple):
    attribute: str
    type: str

    def __str__(self):
        return f"{self.attribute}: {self.type}"


Assignments = list[Assignment]


class Namespace:
    command: Callable[["Namespace"], Coroutine[None, None, None]]
    purge_existing: bool


def parse_args() -> Namespace:
    parser = argparse.ArgumentParser(
        description="Compiles the Qt designer UI files into importable Python modules "
        "or type hinting stubs. Generates type hinting stubs by default."
    )
    parser.add_argument(
        "-p", "--purge-existing", action="store_true",
        help="Remove any already existing compiled or generated files."
    )
    commands = parser.add_subparsers(dest="command", help="Command to run:", required=True)
    commands.add_parser(
        "generate_importable_modules",
        help="Generate importable Python modules. Used for packaging"
    )
    commands.add_parser(
        "generate_stubs",
        help="Generate type hinting stubs. Used for development"
    )
    parsed = parser.parse_args()
    parsed.command = globals()[parsed.command]
    return parsed


def type_filter(any_: Iterable[Any], types: Type[T] | tuple[Type[T], ...]) -> Iterable[T]:
    return filter(lambda x: isinstance(x, types), any_)


def create_python_package(location: Path, /):
    """Creates an empty Python package at the given Path"""
    location.mkdir(parents=True, exist_ok=True)
    (location/"__init__.py").touch(exist_ok=True)


async def compile_ui_file(path: Path):
    command = "pyside6-uic", "--generator", "python", str(path)
    await TaskThrottle.acquire()
    subprocess = await asyncio.subprocess.create_subprocess_exec(
        *command, stdin=STDIN, stdout=STDOUT, stderr=STDERR)
    stdout, stderr = await subprocess.communicate()
    TaskThrottle.release()
    return stdout, stderr, path


async def compile_ui_files(source_path: Path = UI_SOURCE_PATH):
    return asyncio.as_completed(map(compile_ui_file, source_path.rglob("*.ui")))


async def generate_importable_modules(
        args: Namespace, target_path: Path = TARGET_PATH, source_path: Path = UI_SOURCE_PATH):
    """
    Compiles all UI files found in source_path to Python types, storing results in target_path.

    Recursively finds UI files under source_path,
    replicates the found directory tree as a Python package hierarchy and
    populates it with the compiled Ui types.
    """
    if args.purge_existing and target_path.is_dir():
        shutil.rmtree(target_path)
    create_python_package(target_path)
    for task in await compile_ui_files(source_path):
        stdout, stderr, ui_file = await task
        if stderr:
            raise RuntimeError(f"Error in compiler task for {ui_file}: {stderr.decode('utf-8')}")
        parent_dir = (target_path/ui_file.relative_to(source_path)).parent
        create_python_package(parent_dir)
        (parent_dir / f"{ui_file.stem}.py").write_bytes(stdout)


async def generate_stubs(args: Namespace, target_path: Path = TARGET_PATH, source_path: Path = UI_SOURCE_PATH):
    """
    Creates type hinting stubs for all UI files found in source_path, storing results in target_path.

    Recursively finds UI files under source_path,
    replicates the found directory tree as a Python package hierarchy and
    populates it with the created type hints.
    """
    if args.purge_existing and target_path.is_dir():
        shutil.rmtree(target_path)
    class_registry = build_class_registry(MAIN_PACKAGE)
    create_python_package(target_path)
    for task in await compile_ui_files(source_path):
        stdout, stderr, ui_file = await task
        if stderr:
            raise RuntimeError(f"Error in compiler task for {ui_file}: {stderr.decode('utf-8')}")
        parent_dir = (target_path/ui_file.relative_to(source_path)).parent
        create_python_package(parent_dir)
        stub = generate_stub(stdout.decode('utf-8'), ui_file, class_registry)
        (parent_dir/f"{ui_file.stem}.pyi").write_text(stub, "utf-8")


def build_class_registry(package_path: Path) -> ClassRegistry:
    """Scan the source tree for classes and build a dict from class name to import path"""
    result: ClassRegistry = {}
    for py_file in package_path.rglob("*.py"):
        module_path = ".".join((py_file.parent.relative_to(package_path.parent) / py_file.stem).parts)
        content = py_file.read_text("utf-8")
        root_node = ast.parse(content, py_file)
        for class_def in type_filter(root_node.body, ast.ClassDef):
            result[class_def.name] = ast.ImportFrom(module_path, [ast.alias(class_def.name)], 0)
    return result


def generate_stub(compiled_ui: str, ui_file: Path, class_registry: ClassRegistry) -> str:
    root_node = ast.parse(compiled_ui)
    header = f"# Automatically generated type hinting stub for '{ui_file.name}'. Do not modify."
    # Keep all imports unmodified
    imports = "import typing\n\n"
    imports += "\n".join(
        map(
            ast.unparse,
            type_filter(root_node.body, (ast.ImportFrom, ast.Import))
        )
    )
    found_class_uses: UsedClasses = set()
    class_stubs = "\n\n\n".join(
        map(
            generate_class_stub,
            type_filter(root_node.body, ast.ClassDef),
            itertools.repeat(found_class_uses)
        ))
    type_hinting_imports = [
        ast.unparse(class_registry[used_class])
        for used_class in found_class_uses.intersection(class_registry)
    ] or ["pass"]
    type_hinting_import_str = "if typing.TYPE_CHECKING:\n"
    type_hinting_import_str += textwrap.indent(
        "\n".join(type_hinting_imports),
        " "*4
    )
    return "\n\n".join((header, imports, type_hinting_import_str, class_stubs)) + "\n"


def generate_class_stub(class_root: ast.ClassDef, found_class_uses: UsedClasses) -> str:
    header = generate_class_header(class_root)

    for item in class_root.body:
        if item.name == "setupUi":
            setup_ui: ast.FunctionDef = item
            break
    else:
        raise RuntimeError(f"No setupUi() definition found in class {class_root.name}")
    function_signatures = textwrap.indent(
        "\n\n".join(map(
            get_function_stub,
            type_filter(class_root.body, ast.FunctionDef),
            itertools.repeat(found_class_uses)
        )), " "*4
    )
    assignment_body = textwrap.indent(
        "\n".join(map(
            str, get_assignments(setup_ui.body)
        )),
        " "*4
    )

    return "\n\n".join((header, function_signatures, assignment_body))


def generate_class_header(class_root: ast.ClassDef) -> str:
    bases: list[ast.Name] = class_root.bases
    base_classes = ", ".join(base.id for base in bases)
    return f"class {class_root.name}({base_classes}):"


def get_assignments(function_body: Statements) -> Assignments:
    return [
        Assignment(
            assignment.targets[0].attr,
            assignment.value.func.id
        )
        for assignment
        in type_filter(function_body, ast.Assign)
        if hasattr(assignment.targets[0], "attr")  # Filter out local variables
    ]


def get_function_stub(function_body: ast.FunctionDef, found_class_uses: UsedClasses):
    for index, arg in enumerate(function_body.args.args):
        if arg.arg == "self":
            continue
        found_class_uses.add(arg.arg)
        arg.annotation = ast.Constant(arg.arg)
        arg.arg = f"arg{index}"

    old_body = function_body.body
    function_body.body = [ast.Constant(Ellipsis)]
    result = ast.unparse(function_body)
    function_body.body = old_body
    return result


async def main():
    args = parse_args()
    await args.command(args)


if __name__ == "__main__":
    asyncio.run(main())
