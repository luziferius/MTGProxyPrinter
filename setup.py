# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""

from pathlib import Path
import re
import subprocess

from setuptools import setup, find_packages
import setuptools.command.build_py

project_name = "MTGProxyPrinter"
main_package = "mtg_proxy_printer"
script_file = "{main_package}/meta_data.py".format(main_package=main_package)
description = "MTGProxyPrinter allows efficient printing of Magic: The Gathering cards for playtesting purposes."


with open(script_file, "r", encoding="utf-8") as opened_script_file:
    version = re.search(
        r"""^__version__\s*=\s*"(.*)"\s*""",
        opened_script_file.read(),
        re.M
        ).group(1)


with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()


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
        command = ("pyrcc5", str(resources_source))  # noqa  # "pyrcc5" is a program name, not a typo
        compiled = subprocess.check_output(command, universal_newlines=True)  # type: str
        with target_file.open("wt") as compiled_qt_resources_file:
            compiled_qt_resources_file.write(compiled)
        return compiled


setup_parameters = dict(
    name=project_name,
    packages=find_packages(exclude=["tests*", "venv", ".pytest_cache", "pyinstaller_hooks*"]),
    include_package_data=True,  # Database schema is included as package data.
    entry_points={
        "gui_scripts": [
            "mtg-proxy-printer = {main_package}.__main__:main".format(main_package=main_package),
        ],
    },
    version=version,
    description=description,
    long_description=long_description,
    python_requires=">=3.8",
    author="Thomas Hess",
    author_email="thomas.hess@udo.edu",
    url="http://1337net.duckdns.org:8080/MTGProxyPrinter/index",
    project_urls={
        "Bug Tracker": "http://1337net.duckdns.org:8080/MTGProxyPrinter/ticket",
    },
    cmdclass={
        'build_py': BuildWithQtResources,
    },
    license="GPLv3+",
    install_requires=[
        "appdirs >= 1.4.3",  # 1.4.3 is the first version Supporting Python >= 3.6
        "PyQt5",
        "ijson >= 3.1.0",
        "pint",
        "delegateto >= 1.5",
    ],
    setup_requires=[
        'setuptools >= 30.3.0',
        "wheel",
        "PyQt5",  # includes the "pyrcc5" resource compiler used during the build process. See BuildWithQtResources
    ],
    extras_require={
        "dev": [
            'cx_Freeze >= 6.6',
            'pytest-runner',
            'pytest',
            'pytest-cov',
            'pytest-xdist',
            'PyHamcrest >= 1.8.1',
            'PyQt5-stubs',  # Install the stubs used for type hinting when creating the development environment
            "PyInstaller >= 4.0",
            "pyinstaller-hooks-contrib >= 2020.11",  # First version that contains the upstreamed hook for ijson
            "sip",
            "build",
        ]
    },
    test_suite="pytest",
    # list of classifiers: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Environment :: X11 Applications :: Qt',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Games/Entertainment :: Board Games',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
    ],
)

if __name__ == "__main__":
    setup(**setup_parameters)
