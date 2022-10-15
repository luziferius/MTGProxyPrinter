# MTGProxyPrinter

Print Magic: The Gathering cards for play-testing purposes.


## Feature overview

- Create, save and load documents
- Export documents as PDFs
  - Optional, automatic splitting into configurable chunks to accommodate file size limits present in various printers.
- Direct printing using your operating system’s printing support. Can use any available and suitable printer
- Obtains high-quality images from Scryfall (where available)
  - Images are cached locally for faster loading times when printing the same cards again
- Import deck lists in various formats, like Magic Arena deck lists and XMage deck files (see below for a list of supported formats)
  - Automatic download of deck lists from various deck list database websites (see below for a list)
  - One-click removal of basic lands (optionally also including Wastes and Snow-covered basic lands)
  - Optional, automatic deck list translation. Translate all cards in the deck list to your preferred language. (Depending on image availability.)
  - Manually override chosen card printings, if you dislike the printing choices made in the deck list
  - When importing a deck list that contains excluded printings (see below), MTGProxyPrinter tries to replace them with suitable surrogates, where possible
- Supports double-faced cards and split cards
  - Both front and back are searchable by all names printed on the card
  - Automatic handling of opposing card faces: MTGProxyPrinter automatically adds the same number of copies of the other face. (This feature can be disabled)
- Hide cards using various card and printing filters. Hidden cards are treated as though they do not exist.
  - Bans in various formats supported by Scryfall
  - Border color (white-bordered, gold-bordered)
  - Funny cards (Silver-bordered and other black-bordered promotional cards, like the “Heroes of the Realm” cards. Also cards from Un-sets with acorn-shaped security stamp.)
  - Image availability (for non-English cards)
  - Being oversized
  - Digital printings (includes both Magic Online promotional card versions, MTG Arena digital-only cards and other digital printings)
- Supports cards in all languages supported by Scryfall
- Supports the official tokens (As offered by Scryfall, which is currently English only. If Scryfall starts to offer localized tokens, these will be become available, too.)
- Adjustable paper size, page margins, image spacing
- Optional printing of cut helper lines to aid machine-cutting printed sheets
- Full support for oversized cards, like Archenemy Scheme cards or Planechase Planes. 
  - Regular-size cards and oversized cards are kept on separate pages to ensure consistent image spacing and proper rendering of cut helper lines.


### Supported deck list formats

- Magic Arena
- Magic Online (MTGO)
- [XMage](http://xmage.de)
- [Tappedout.net](https://tappedout.net) deck lists (choose CSV export)
- [Scryfall.com](https://scryfall.com) deck lists (choose CSV export)
- Any other deck list format containing one card per line, by supplying a matching regular expression to parse the file (this is an advanced feature).


### Supported deck list database sites

MTGProxyPrinter can directly fetch public deck lists from these websites.

- [Scryfall](https://scryfall.com)
- [MTGGoldfish](https://www.mtggoldfish.com/)
- [mtg.wtf](https://mtg.wtf/)
- [TappedOut](https://tappedout.net/)
- [Moxfield](https://www.moxfield.com/)
- [Deckstats](https://deckstats.net/)

Except for Scryfall, these websites do not offer a stable, public Web API. Support is offered on a
“best effort” base and may break at any time, if a website decides to re-design their code.

## Requirements

- Python >= 3.8

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
from the repository root directory (where `setup.py` and `pyproject.toml` are located).


## Usage

Execute `mtg-proxy-printer` to start the GUI. The Windows MSI package places a starter in the Start menu.

At first start and at somewhat regular intervals, MTGProxyPrinter requires downloading the MTG card data
from the Scryfall API. This dataset containing the information about the available 380k+ printings is roughly 250-300 MiB large.

When starting, an empty document is created. You can add any number of pages, if you need more than one page to print.
The left-most panel in the main window shows an overview over all pages with a summary of what is on each page.
Click on a page to show it’s content in detail and select it for editing.
The top-right area is used to find cards by name or set and add them to the current page.
Below is a preview rendering of the current page, and a table with details about the cards in the opened page.
You can select images and remove them, if you accidentally added the wrong cards.

If you don’t want to use the built-in card search, MTGProxyPrinter can import deck lists from disk and from a set of
card database websites. The import wizard is available from the File menu in the main window. After loading the list,
the cards are presented in a table, where you can re-select printings, remove cards,
and one-click remove all basic lands, before finishing the import.

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
