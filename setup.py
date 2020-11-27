# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""


import re
from setuptools import setup, find_packages

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


with open("README.rst", "r", encoding="utf-8") as f:
    long_description = f.read()


setup(
    name=project_name,
    packages=find_packages(exclude=("tests", ".pytest_cache")),
    include_package_data=True,  # Database schema is included as package data.
    entry_points={
        "gui_scripts": [
            "mtg-proxy-printer = {main_package}.__main__:main".format(main_package=main_package)
        ]
    },
    version=version,
    description=description,
    long_description=long_description,
    python_requires=">=3.8",
    author="Thomas Hess",
    author_email="thomas.hess@udo.edu",
    url="http://1337net.duckdns.org:8080/mtg-proxy-printer/",
    license="GPLv3+",
    install_requires=[
        "appdirs >= 1.4.3",  # 1.4.3 is the first version Supporting Python >= 3.6
        "PyQt5",
        "ijson >= 3.1.0",
        "pint",
    ],
    setup_requires=[
        'setuptools >= 30.3.0',
    ],
    extras_require={
        "dev": [
            'pytest-runner',
            'pytest',
            'pytest-cov',
            'pytest-xdist',
            'PyHamcrest >= 1.8.1',
        ]
    },
    test_suite="pytest",
    # list of classifiers: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 1 - Planning',
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
        '',
    ],
)
