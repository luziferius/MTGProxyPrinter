# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""

from pathlib import Path
import subprocess

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
        command = ("pyside6-rcc", "--compress", "9", "--generator", "python", str(resources_source))
        compiled = subprocess.check_output(command, universal_newlines=True)  # type: str
        target_file.write_text(compiled, "utf-8")
        return target_file

    @staticmethod
    def generate_ui_classes(base_dir: Path):
        source_ui_files_dir = Path(main_package, "resources", "ui").resolve()
        target_dir = base_dir / "generated"
        target_dir.mkdir(exist_ok=True)
        (target_dir/"__init__.py").touch()  # Create a proper package

        for ui_file in source_ui_files_dir.rglob("*.ui"):
            rel_path = ui_file.relative_to(source_ui_files_dir)
            # Create proper subpackages, mimicking the input file hierarchy
            parent_dir = (target_dir/rel_path).parent
            parent_dir.mkdir(exist_ok=True)
            (target_dir/"__init__.py").touch(exist_ok=True)
            command = (
                "pyside6-uic", "--generator", "python",
                "--output", str(parent_dir/f"{ui_file.stem}.py"),
                str(ui_file)
            )
            if result := subprocess.check_call(command):
                raise RuntimeError(f"UI class generation failed with return value {result}. Command: {command}")

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
