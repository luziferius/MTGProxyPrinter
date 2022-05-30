# MTGProxyPrinter

Print Magic: The Gathering cards for play-testing purposes.


## Requirements


- Python >= 3.8


### Python libraries

These external libraries are used in the code. They can be installed from PyPI.

- `appdirs`
- `ijson`
- `pint`
- `PyQt5`
- `delegateto`
- `PyHamcrest`
- `cx_Freeze` (Stand-alone bundles only. Used by the installer for Windows®-based platforms.)

### System libraries

- `SQLite3` >= 3.35.0

### Test Requirements

These libraries are required to run the unit tests.

- `tox` (Also used to build redistributable archives/installers)
- `pytest`
- `pytest-qt`
- `pytest-cov` (Optional, for code coverage reports).

## Install

To install from a fossil checkout or a downloaded and unpacked source code archive, execute `pip install .` 
from the repository root directory (where `setup.py`, `setup.cfg` and `pyproject.toml` are located).

To install the newest, released version from source, execute  
`pip install http://1337net.duckdns.org:8080/MTGProxyPrinter/zip/MTGProxyPrinter.zip?r=release`  
To install the latest development snapshot, execute  
`pip install http://1337net.duckdns.org:8080/MTGProxyPrinter/zip/MTGProxyPrinter.zip?r=trunk`  


## Usage

Execute `mtg-proxy-printer` to start the GUI.

When starting, an empty document is created. You can add any number of pages, if you need more than one page to print.
The left-most panel in the main window shows an overview over all pages with a summary of what is on each page.
Click on a page to show it’s content in detail and select it for editing.
The top-right area is used to find cards by name or set and add them to the current page.
Below is a preview rendering of the current page, and a table with details about the cards in the opened page.
You can select images and remove them, if you accidentally added the wrong cards.

You can save and load documents to continue working on your documents later and create PDF documents for printing.

### Important note about printing with PDF documents

Before printing, make sure to disable any kind of scaling, like “fit to page”, “scale to fit” or 
similar settings in your printer’s settings and your PDF viewer’s printer settings.  
The created documents contain images precisely sized to be exactly the size of Magic cards.
If your printer scales them down (intended to not “lose” the border around the page),
the images will be too small, so do a single-page test run the first time you use this program.

These scaling options are enabled by default and are intended to prevent cropping with borderless photo prints,
but do more harm than good for any document that is not a full-page, borderless photo.

#### Ink saving tip

Before you print for the first time with a given printer or PDF viewer, enable the “Print cut markers” in the 
MTGProxyPrinter settings and then print or export a single empty page. If a real Magic card fits precisely into
one cell of the printed grid, your system is set up correctly for high quality, non-scaled print-outs.

## License


Copyright (C) 2020-2022 Thomas Hess <thomas.hess@udo.edu>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

See the LICENSE file for details.


## Icon License

Copyright (C) 2014 Uri Herrera <uri_herrera@nitrux.in> and others

The icons shipped in the directory mtg_proxy_printer/resources/icons/ are used as a fallback if no
system theme is present, and are sourced from Breeze icon theme created by the KDE project.
These fall under the LGPL either version 3 of the License, or
(at your option) any later version.

See the [ThirdPartyLicenses.md](./ThirdPartyLicenses.md) file for details.
