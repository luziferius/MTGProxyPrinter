# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""

from pathlib import Path
import subprocess

import PyQt5.uic
from setuptools import setup
import setuptools.command.build_py

main_package = "mtg_proxy_printer"


class BuildWithQtResources(setuptools.command.build_py.build_py):
    """Try to build the Qt resources file for MTGProxyPrinter."""
    def run(self):
        if not self.dry_run:  # Obey the --dry-run switch
            target_dir = Path(self.build_lib, main_package, "ui").resolve()
            target_dir.mkdir(exist_ok=True, parents=True)
            self.compile_resources(target_dir)
            self.generate_ui_classes(target_dir)
        super(BuildWithQtResources, self).run()

    @staticmethod
    def get_resources_qrc_file_path() -> Path:
        source_root = Path(__file__).resolve().parent / main_package
        resources_file = source_root / "resources" / "resources.qrc"
        return resources_file

    @staticmethod
    def compile_resources(target_dir: Path):
        target_file = target_dir / "compiled_resources.py"
        resources_source = BuildWithQtResources.get_resources_qrc_file_path()
        command = ("pyrcc5", "-compress", "9", str(resources_source))  # noqa  # "pyrcc5" is a program name, not a typo
        compiled = subprocess.check_output(command, universal_newlines=True)  # type: str
        target_file.write_text(compiled, "utf-8")
        return target_file

    @staticmethod
    def generate_ui_classes(base_dir: Path):
        source_ui_files_dir = Path(main_package, "resources", "ui").resolve()
        target_dir = base_dir / "generated"
        target_dir.mkdir(exist_ok=True)

        def map_to_output(directory, file_name):
            dir_path = Path(directory).relative_to(source_ui_files_dir)
            return target_dir/dir_path, file_name
        
        # Workaroud PyQt5 bug: compileUiDir calls open() without setting an encoding.
        # This breaks with UTF-8 encoded UI files on Windows machines.
        # So simply enforce utf-8 by replacing the open function in the uic module.
        # The issue is reported, so hopefully gets fixed at some point, rendering this obsolete
        import functools
        PyQt5.uic.open = functools.partial(open, encoding="utf-8")
        PyQt5.uic.compileUiDir(str(source_ui_files_dir), recurse=True, map=map_to_output)
        BuildWithQtResources.create_proper_package(target_dir)

    @staticmethod
    def create_proper_package(target_dir: Path):
        (target_dir/"__init__.py").touch(exist_ok=True)
        for entry in target_dir.rglob("*"):
            if entry.is_dir():
                (entry/"__init__.py").touch(exist_ok=True)


setup_parameters = dict(
    cmdclass={
        'build_py': BuildWithQtResources,
    },
)

if __name__ == "__main__":
    setup(**setup_parameters)
