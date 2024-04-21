# Copyright (C) 2022-2023 Thomas Hess <thomas.hess@udo.edu>
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
This script generates Python stubs for the UI types
"""

import argparse
import ast
import textwrap
from pathlib import Path
import shutil
import subprocess
from typing import Tuple, NamedTuple, TypeVar, Iterable, Union, Type, List, Any

SOURCE_ROOT = Path(__file__).parent.parent  # Checkout root directory
UI_SOURCE_PATH = SOURCE_ROOT / "mtg_proxy_printer/resources/ui"  # UI files live here
TARGET_PATH = SOURCE_ROOT / "mtg_proxy_printer/ui/generated"  # Package containing generated modules/type hinting stubs
T = TypeVar("T")


class Assignment(NamedTuple):
    attribute: str
    type: str

    def __str__(self):
        return f"{self.attribute}: {self.type}"


class Namespace(NamedTuple):
    full: bool
    purge_existing: bool


def parse_args() -> Namespace:
    parser = argparse.ArgumentParser(
        description="Compiles the Qt designer UI files into importable Python modules "
        "or type hinting stubs. Generates type hinting stubs by default."
    )
    parser.add_argument(
        "-f", "--full", action="store_true",
        help="Compile UI into importable Python modules."
    )
    parser.add_argument(
        "-p", "--purge-existing", action="store_true",
        help="Remove any already existing compiled or generated files."
    )
    args = parser.parse_args()
    return args


def type_filter(any_: Iterable[Any], types: [Union[Type[T], Tuple[Type[T], ...]]]) -> Iterable[T]:
    return filter(lambda x: isinstance(x, types), any_)


def create_python_package(location: Path, /):
    """Creates an empty Python package at the given Path"""
    location.mkdir(parents=True, exist_ok=True)
    (location/"__init__.py").touch(exist_ok=True)


def compile_ui_files(args: Namespace, target_path: Path = TARGET_PATH, source_path: Path = UI_SOURCE_PATH):
    """
    Compiles all UI files found in source_path to Python types, storing results in target_path.

    Recursively finds UI files under source_path, replicates the found directory tree as a Python package hierarchy and
    populates it with the compiled Ui types.
    """
    if args.purge_existing and target_path.is_dir():
        shutil.rmtree(target_path)
    create_python_package(target_path)
    for ui_file in source_path.rglob("*.ui"):
        compiled = compile_ui_file(ui_file)
        parent_dir = (target_path/ui_file.relative_to(source_path)).parent
        create_python_package(parent_dir)
        (parent_dir/f"{ui_file.stem}.py").write_text(compiled, "utf-8")


def create_ui_type_stubs(args: Namespace, target_path: Path = TARGET_PATH, source_path: Path = UI_SOURCE_PATH):
    """
    Creates type hinting stubs for all UI files found in source_path, storing results in target_path.

    Recursively finds UI files under source_path, replicates the found directory tree as a Python package hierarchy and
    populates it with the created type hints.
    """
    if args.purge_existing and target_path.is_dir():
        shutil.rmtree(target_path)
    create_python_package(target_path)
    for ui_file in source_path.rglob("*.ui"):
        compiled = compile_ui_file(ui_file)
        stub = generate_stub(compiled, ui_file)
        parent_dir = (target_path/ui_file.relative_to(source_path)).parent
        create_python_package(parent_dir)
        (parent_dir/f"{ui_file.stem}.pyi").write_text(stub, "utf-8")


def compile_ui_file(path: Path) -> str:
    command = ("pyside6-uic", "--generator", "python", str(path))
    return subprocess.check_output(command, encoding="utf-8")


def generate_stub(compiled_ui: str, ui_file: Path) -> str:
    root_node = ast.parse(compiled_ui)
    header = f"# Automatically generated type hinting stub for '{ui_file.name}'. Do not modify."
    # Keep all imports unmodified
    imports = "\n".join(
        map(
            ast.unparse,
            type_filter(root_node.body, (ast.ImportFrom, ast.Import))
        )
    )
    class_stubs = "\n\n\n".join(
        map(
            generate_class_stub,
            type_filter(root_node.body, ast.ClassDef)
        ))

    return "\n\n".join((header, imports, class_stubs)) + "\n"


def generate_class_stub(class_root: ast.ClassDef) -> str:
    header = generate_class_header(class_root)

    for item in class_root.body:
        if item.name == "setupUi":
            setup_ui = item
            break
    else:
        raise RuntimeError(f"No setupUi() definition found in class {class_root.name}")
    function_signatures = textwrap.indent(
        "\n\n".join(map(
            get_function_stub,
            type_filter(class_root.body, ast.FunctionDef)
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
    base_classes = ", ".join(base.id for base in class_root.bases)
    return f"class {class_root.name}({base_classes}):"


def get_assignments(function_body: ast.FunctionDef) -> List[Assignment]:
    return [
        Assignment(
            assignment.targets[0].attr,
            assignment.value.func.id
        )
        for assignment
        in type_filter(function_body, ast.Assign)
        if hasattr(assignment.targets[0], "attr")  # Filter out local variables
    ]


def get_function_stub(function_body: ast.FunctionDef):
    old_body = function_body.body
    function_body.body = [ast.Constant(Ellipsis)]
    result = ast.unparse(function_body)
    function_body.body = old_body
    return result


def main():
    args = parse_args()
    if args.full:
        compile_ui_files(args)
    else:
        create_ui_type_stubs(args)


if __name__ == "__main__":
    main()
