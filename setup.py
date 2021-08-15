# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""

from pathlib import Path
import subprocess

from setuptools import setup, find_packages
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
    project_urls={
        "Bug Tracker": "http://1337net.duckdns.org:8080/MTGProxyPrinter/ticket",
    },
    cmdclass={
        'build_py': BuildWithQtResources,
    },
    extras_require={
        "dev": [
            'cx_Freeze >= 6.6',
            'pytest-runner',
            'pytest',
            'pytest-cov',
            'pytest-xdist',
            'pytest-timeout',
            'pytest-qt',
            'PyHamcrest >= 1.8.1',
            'PyQt5-stubs',  # Install the stubs used for type hinting when creating the development environment
            "sip",
            "build",
        ]
    },
    test_suite="pytest",
)

if __name__ == "__main__":
    setup(**setup_parameters)
