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
            output_path = Path(self.build_lib, main_package, "ui", "compiled_resources.py").resolve()
            if not output_path.exists():
                self.mkpath(str(output_path.parent))
                self.compile_resources(output_path)
        super(BuildWithQtResources, self).run()

    @staticmethod
    def get_resources_qrc_file_path() -> Path:
        source_root = Path(__file__).resolve().parent / main_package
        resources_file = source_root / "resources" / "resources.qrc"
        return resources_file

    @staticmethod
    def compile_resources(target_file: Path):
        resources_source = BuildWithQtResources.get_resources_qrc_file_path()
        command = ("pyrcc5", "-compress", "9", str(resources_source))  # noqa  # "pyrcc5" is a program name, not a typo
        compiled = subprocess.check_output(command, universal_newlines=True)  # type: str
        with target_file.open("wt") as compiled_qt_resources_file:
            compiled_qt_resources_file.write(compiled)
        return compiled


setup_parameters = dict(
    cmdclass={
        'build_py': BuildWithQtResources,
    },
)

if __name__ == "__main__":
    setup(**setup_parameters)
