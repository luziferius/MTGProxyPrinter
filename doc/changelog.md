# Changelog

# Version 0.21.0 (2023-02-08)  <a name="v0_21_0"></a>

## New features

- Added Undo and Redo actions. It is now possible to undo changes to the document, and also redo undone changes.
  - The undo and redo button tooltip shows a short description
    of the change that is performed when the button is clicked.

## Changed features

- Temporarily disable automatic dark mode rendering on Windows 10, if dark mode rendering for applications is active,
  because of rendering issues in the deck import wizard and card image cleanup wizard.
  The feature will return with better rendering at some point in the future.
  - Linux is unaffected by this change, as following the system color scheme generally just works there.

## Fixed issues

- Fixed crash in the settings validation logic, introduced in version 0.19.0, that may occur when
  manually fiddling with the app configuration file creates an invalid document page size.
- Fixed crash when shuffling a document that contains both regular-sized and over-sized cards.
  Individual cards of the same size will be shuffled around across pages, but regular and over-sized card pages
  will stay in their relative order and position.
- After completing a card data update, properly hide cards which got banned in a format
  for which hiding banned cards is enabled in the settings. This prevents potential crashes when trying to add
  these cards to the document. (Cards already added to the document are unaffected by such a card data update)
- Optimized the document renderer and improved rendering quality
  - Fixed location of horizontal cut helper lines for over-sized cards, which were off by one pixel
  - Fixed a sub-pixel overlap of card images when image spacing is set to zero (the default).
  - Images are now always placed on full pixels, avoiding aliasing artifacts.

# Version 0.20.1 (2022-10-27)  <a name="v0_20_1"></a>

- Fixed crash in the card data importer: The importer now handles double faced cards with missing back face images.
  These cards are skipped during the import.

## Other

- Rewritten GUI handling. This results in a slightly faster application startup

# Version 0.20.0 (2022-10-09)  <a name="v0_20_0"></a>

## New features

- Automatic deck list downloads. The deck list import wizard now has an input field that accepts
  links to deck lists on various deck list database websites. 
  - Currently supported are [Scryfall](https://scryfall.com),
    [MTGGoldfish](https://www.mtggoldfish.com/),
    [mtg.wtf](https://mtg.wtf/), [TappedOut](https://tappedout.net/),
    [Moxfield](https://www.moxfield.com/) and
    [Deckstats](https://deckstats.net/)

## Changed features

- Re-structured the deck list import wizard. The deck list input is now the first step.

# Version 0.19.0 (2022-10-02)  <a name="v0_19_0"></a>

## New features

- Implemented optional drawing of 90° card corners. This can be enabled for all new documents
  globally in the application settings or individually in the document settings.
- The one-click basic land removal in the deck list import is now configurable in the application settings:
  You can now individually enable the automatic removal of Wastes and Snow-Covered basic lands in
  addition to plain basic lands.

## Fixed issues

- Fixed HTTP 403 errors when attempting to download card data or images. The new hoster used by Scryfall rejects the
  previously used HTTP User-Agent value, so set it to a new one that isn’t blocked. 
- Fixed crashes when accepting to open the Application website in the update notification. This now works properly
- Fixed card images overlapping by one pixel when image spacing is set to zero.

# Version 0.18.0 (2022-07-09)  <a name="v0_18_0"></a>

## New features

- Proper, full support for oversized cards, like Archenemy schemes or Planechase plane cards. Regular cards and larger
  cards are always kept on separate pages to ensure that drawn cut marker lines (if enabled) are always 100% accurate.
  - Note: Some cards, like the Legacy Championship winner rewards, are tagged as being oversized, but are then served
    with regular-size images by Scryfall.
    When the image is downloaded, it will be treated as a regular card, even if the deck import wizard warns
    about it being potentially oversized.

## Fixed issues

- Significantly optimized card database size and import speed.
  (The database now takes roughly 25% less time to update on fast internet connections
  and uses about 30% less disk space)
- Fixed the “Remove selected” cards button in the deck list importer unexpectedly staying active
  when clicked while multiple cells of the same row in the card table were selected.
- Fixed unintended immediate removal of freshly-downloaded low-resolution images. These should only be removed, if
  a high-resolution image becomes available.

# Version 0.17.0 (2022-06-13)  <a name="v0_17_0"></a>

## New features

- Added card removal feature to the deck import wizard: It is now possible to remove selected cards or all basic lands
  from the deck list before finishing the import.
- Added Deck shuffling: A new button in the Edit menu allows shuffling the cards in the document. Use this to reduce
  shuffling effort required after putting the printed deck in sleeves. Beware: The shuffling currently separates front 
  and back faces of double faced cards. This may be improved in future versions.

## Changed features

- The “New” document button will now ask for confirmation, before replacing the currently edited document with a new one.
- Improved the advanced deck list parser that allows defining a custom regular expression to parse the deck list:
  - Added buttons that insert preset regular expression building blocks. This reduces typing effort required to build
    a working RE.
  - The wizard only accepts the input regular expression, if it deems it being able to extract sufficient information
    for card identification.

## Fixed issues

- Fixed broken file type filters when loading deck lists. The file selection dialog now properly filters for deck
  list files instead of showing nothing.
- Fixed potential crash when exiting the application while a card image download runs

# Version 0.16.1 (2022-05-23)  <a name="v0_16_1"></a>

## Changed features

- The application update checker now offers visiting the project website, if an update is available.

## Fixed issues

- Improved deck list translation when the source deck list is not in English.
- Improved card translation when the card in the target language has multiple translations. 
- Improved operation while offline or with flaky internet connection: MTGProxyPrinter will now attempt to re-download
  missing images when trying to print or export the current document to PDF. 
  Additionally, a warning is issued, if obtaining the missing images fails.
- Enable basic dark mode rendering on Windows. Proper system theme support is only available on Linux, because the
  used GUI toolkit doesn’t fully support the dark mode setting on Windows yet. 

# Version 0.16.0 (2022-05-06)  <a name="v0_16_0"></a>

After upgrading to this version, re-downloading the card data from Scryfall is required to use the new or enhanced
capabilities.

## New features

- The page preview can now be zoomed in for a better card view. Zooming can be triggered using `[Ctrl]+Mouse wheel`,
  or the platform dependant default zoom keyboard shortcut (`[Ctrl]+[+]` and `[Ctrl]+[-]` on most systems)
- Improved dark mode and global color theme compatibility: The page preview now follows the systems global color theme.
  On dark mode, the page background is dark and the optional cut marker lines are light (if enabled).
  (This does of course *not* affect the print preview, exported PDFs and printed pages.)
- Added short descriptions when the progress bar is shown at the bottom of the main window.
- In the settings window, the card filters check boxes now have buttons next to them that open a web browser showing
  the Scryfall query highlighting the cards affected by the corresponding filter.

## Changed features

- Card download filters are now filters used to hide printings.
  - Updating the settings no longer requires re-downloading the data from Scryfall.
  - Inverted the display: Instead of specifying which cards or printings are included,
    the settings now state which printings are hidden. (Settings saved with previous versions are migrated.)
- The deck list import wizard now shows only matching files when browsing the file system for a deck list to load.
  The filtering can be disabled by switching to the “All files” filter.
- When the deck list import wizard has the freedom of printing choice, it will now prefer the newest, regular,
  tournament-legal printings over others like oversized cards or art series cards,
  even if those are not hidden in the settings. You can still access them, but these printings won’t be automatically
  chosen.
- The document and PDF save path now defaults to the local Documents directory.
- Improved card name translation consistency, if the to-be translated name is ambiguous. There are a few cards with name
  clashes in translations, i.e. different cards being translated to the same name across different sets. In this case,
  context information is used to obtain a correct translation, if available. Otherwise, a majority vote is performed
  to guess the most likely meaning of a given card name.

## Fixed issues

- Added potentially missing icons to buttons in the document settings dialog.
- Fixed the incomplete Magic Arena deck list parser.
  - Added support for the simple and more common card list format that does not specify the exact printing.
    (I.e. the parser now accept valid entries like `5 Island` instead of only accepting `5 Island (SNC) 265`)
  - Also recognizes the segment headers that may be present in the deck list, 
    that are “Deck”, “Commander”, “Companion” and “Sideboard”,
    and will no longer complain that these are unidentified cards.
- Mitigate crashes when using the wrong CSV deck list parser with a given CSV file. An error message is now shown in
  this case.

# Version 0.15.1 (2022-04-13) <a name="v0_15_1"></a>

## Changed features

- Improved the user interface of the Image Cache cleanup wizard: Increased default window size. Removed unnecessary 
  columns in the card listing table. Also adjusted the column widths to make better use of the available space.
- Adjustments to default column widths of the table in the deck import wizard to better fit card and set names.
- The card data download and card image download now resume interrupted downloads caused by a flaky internet connection,
  making the download process more reliable. If MTGProxyPrinter encounters a network error,
  it will re-try the network operation up to 10 times.

## Fixed issues

- Reduced RAM usage by around 190 MiB while downloading the card data from Scryfall.
- Improved the hit rate of the Scryfall deck list importer, when the deck list contains cards affected by enabled
  download filters. The importer will now use suitable replacement printings, where possible, instead of failing to
  import affected cards.
- Fixed bug in the deck import wizard that caused the wizard to perform a deck list translation,
  even if that option was disabled.
- The deck import wizard now shows an error message when a binary file is selected for loading from disk,
  instead of silently failing or crashing.
- The deck import wizard now asks for confirmation, if an unexpectedly large file is selected.

# Version 0.15.0 (2022-04-03) <a name="v0_15_0"></a>

## Implemented features

- Document settings, like paper size, margins, spacings are now stored in saved documents. When loading a document,
  the stored settings overwrite the default values set in the application settings.
  - The Edit menu in the main window has a new option to edit these document settings for the current document only.
  - Older save files do not contain the relevant data and have to be saved explicitly to perform a save file migration.
- Added new card download filter that allows excluding digital cards.
  The new filter matches both digital “reprints” of existing cards
  (for example Magic Online-exclusive promotional card versions)
  and digital-only cards that aren’t available as physical cards at all (like the Magic Arena Alchemy cards).
- Added a new user interface layout that uses tabs to only show one part of the main window at a time.
  This is mainly useful for small and high-DPI monitors in portrait mode, i.e. when using 
  a monitor with an aspect ratio of 9:16.
- The card table in the deck import wizard is now sortable by clicking on any of the header cells. When sorted, the
  cards will be added to the document in the same order.
- When loading a document that contains printings matching a download filter, the affected printings are now
  replaced with other, available printings, if possible. When migrating from older versions of MTGProxyPrinter,
  the internal card database has to be refreshed for this to work.

## Changed features

- Smarter printing selection when the option to prefer already downloaded printings is enabled:
  MTGProxyPrinter will now prefer printings that were printed/exported more often over less often used printings.
  Uses image usage information already available since version 0.9.0
- Renamed the “vertical” user interface variant in the settings. It is now referred to as “Columnar”,
  because it shows the main window content in four columns.
- Improved sorting behaviour in the image cache cleanup wizard, when sorting the image table by collector number.
- Re-grouped and moved some settings in the settings window, resulting in a more logical options grouping
- It is now possible to open the log directory from the debug settings tab, to ease log file access,
  when the option to write log files to disk is enabled. 

## Fixed issues

- MTGProxyPrinter now validates the document save file format when loading documents
  to prevent Denial of Service attacks via maliciously crafted save files.
- It is now possible to retry downloading card data updates, 
  if the download fails due to a flaky internet connection.
- Fixed broken custom regular expression deck parser option in the deck import wizard. The option now works as intended.
- Fixed broken Tappedout deck list parser. The options to include the maybe-board and acquire-board
  did nothing when enabled and now work as intended.
- Added icons to buttons that were missing them on Windows.

# Version 0.14.2 (2022-01-22) <a name="v0_14_2"></a>

## Fixed issues

- Fixed broken card data download, which was caused by a change in the Scryfall API.
- Prevent application crashes should the card data format received from the API change again in the future.
  The application will now show an error message if it is unable to process the data.

# Version 0.14.1 (2021-09-29) <a name="v0_14_1"></a>

## Fixed issues

- Fixed bug in database migration code that prevented upgrading the application from ancient alpha versions.
- The download progress bar properly disappears, after images finish downloading during the document loading process.
- Removed online requirement for the card database update when upgrading from version 0.13.0 or before.
- Fixed broken image cache cleanup for locally stored low resolution images, if the equivalent high resolution
  image is available for download from Scryfall.

# Version 0.14.0 (2021-09-23) <a name="v0_14_0"></a>

## Implemented features

- Show warnings in the deck import wizard, if oversized cards are present in the imported card list.

## Changed features

- Show copyright notices for many of the used software libraries in the About window.
- Improved the accuracy of the card data update checker, if it is enabled in the settings.
  It should now only report available updates, if Scryfall actually has new data.
- Reduced application bundle size for Windows by 25%.

## Fixed issues

- Fixed broken printing selection in the deck list import wizard. Although it looked like it selected another printing,
  the import wizard actually imported the unedited deck list, completely discarding any edits done. This now works
  as expected.
- Fixed potentially wrong card translations for cards having multiple names, like double-faced cards or split cards.
- The card information download no longer locks up the application if a database error occurs. This might happen, if
  two instances of MTGProxyPrinter try to write to the internal, local card database at the same time.

## Other

- Support importing card data from a file via command line argument `--card-data`.
  Mostly useful for debugging, but can also be used to update the card database of a PC without internet access.
- Larger re-write of the on-disk card database structure. Older versions will not be able to run, after
  the database is migrated to the latest version. Downgrading the application will require deleting the database file. 

# Version 0.13.0 (2021-08-09) <a name="v0_13_0"></a>

## Implemented features

- Implemented optional, automatic deck list translations. When enabled, the deck list import wizard will try to 
  automatically translate all cards in the list into the selected language, where images are available.
  This can be enabled by default in the settings.
- Automatically replace locally stored low resolution card images with better images, when Scryfall upgrades the
  provided images to high-resolution scans. Low-resolution card images fetched during set spoilers no longer stay in
  the image cache indefinitely.

## Changed features

- Optimized the card data update process to update the local data in-place instead of
  wiping everything and starting from scratch. This speeds up the import process and reduces disk writes.

## Fixed issues

- Fixed duplication of imported deck list entries when going back and forward in the deck
  list import wizard after viewing the parsing result. (Bug was introduced in [version 0.12.0](#v0_12_0).)
- The page preview now renders correctly after changing paper sizes in the settings.
- PDFs exported now use the actual, configured paper size, instead of defaulting to the system default value.
  Exporting documents in landscape mode or using esoteric paper sizes now creates usable, correct PDF files.
- Printing documents in landscape mode now works as expected, outputting correctly scaled printouts. Additionally, 
  the print preview dialog now has the appropriate mode (portrait or landscape) pre-selected, 
  based on the configured paper size.

# Version 0.12.1 (2021-07-31) <a name="v0_12_1"></a>

## Implemented features

- While changing the paper size settings, the settings window displays the resulting page capacity in cards. 
- The settings window now informs, if changed settings will cause existing pages to overflow and move cards around
  automatically. The user now has the choice to cancel saving the settings, if they don’t wish for this to happen.

## Changed features

- Application and card data update checks now run in the background, if enabled. This reduces application startup time.

## Fixed issues

- Fixed interface inconsistency when clicking on the "New Document" button.
- Prevent the user from entering invalid combinations of paper sizes and margins that result in a page capacity of zero.
  This prevents the application from entering an invalid state that causes crashes or infinite loops.

# Version 0.12.0 (2021-07-28) <a name="v0_12_0"></a>

## Implemented features

- Implemented re-selecting printings of added cards by double-clicking
  the set or collector number in the table showing the current page.
- Implemented re-selecting printings in the deck import wizard by double-clicking
  the set or collector number in the table showing the parsing result.

## Fixed issues

- Fixed crash, when trying to quit the application while a document loads.

## Other

- Larger re-write of internal data structures
- Reduced local card database size

# Version 0.11.1 (2021-05-17) <a name="v0_11_1"></a>

## Fixed issues

- Fixed crashes when adding art-series cards (again).

# Version 0.11.0 (2021-05-12) <a name="v0_11_0"></a>

## Implemented features

- Suggest a PDF document file name based on the loaded document’s file name, if the current document was saved to
  or loaded from disk.
- Added optional, automatic update checks, both for MTGProxyPrinter itself and the card data from Scryfall.
  - The application asks for consent for both when starting the application for the first time or
    when updating from prior versions
  - For now, the application update check only notifies about updates, and does not perform any automatic update.
- Integrated the changelog into the application, as a new tab in the About dialog.
  - Automatically show the changelog once after each application update.

## Changed Features

- Use cx_Freeze instead of PyInstaller for stand-alone distributions. This yields cleaner, but larger builds,
  and an actual installer for Windows. The application can now be installed and uninstalled using standard OS
  features on Windows.

## Fixed issues

- The application now handles offline operation and network outages during download processes.
  - Shows a message box whenever a download fails
  - The card database will revert to the last state, if downloading fresh card data fails.
  - When downloading card images fails, the card will be added to the document using a blank placeholder.
    The user can save the document and load it the next time network access is available to fetch the missing images.

# Version 0.10.0 (2021-04-21) <a name="v0_10_0"></a>

## Implemented features

- Added a "New document" entry to the File menu and the toolbar.
  It closes the currently edited document and creates a new one.
- The toolbar can now be hidden/shown using an entry in the Settings menu, which can be useful when MTGProxyPrinter is
  used on very small screens. This setting is saved across application restarts.
- Implemented optional print guessing when importing deck lists. This can increase the hit-rate during import at the
  expense of some accuracy.
- When guessing printings, added option to prefer printings with already downloaded images.

## Changed Features

- Clearing the document when importing a deck list now creates a new document, as if the "New document" button was used.
  I.e. it also forgets the association with the previously loaded document, if one was loaded from disk before.
- Use platform-dependent default keyboard shortcuts for some common menu entries. These adjust to the operating system’s
  default values.

## Fixed issues

- Canceling a directory selection dialog for default save paths in the settings window no longer clears the previously
  selected directory, if any was selected.
- Art-Series cards can now be added to the document and be printed.


# Version 0.9.4 (2021-04-03) <a name="v0_9_4"></a>

## Implemented features

- New, enabled by default download filter for cards with placeholder images. Skips import of card printings for
  which no proper images are available, because these can’t be printed.
- New, disabled by default download filter for oversized cards. Enable to not import any oversized cards.

## Fixed issues

- Fixed crash during card data import caused by cards without images. These may occur in the Scryfall database 
  during running spoilers for new sets. Such cards will be skipped during card data import.
- Fixed blurry icons on platforms without native icon theme support.
- Enabled high DPI monitor support. The application will now properly scale on high DPI displays.
- The Deck import wizard uses better validation when using the custom RE parser. The user-supplied RE is now required to
  have at least one meaningful named group, matching a known card property.
  REs that do nothing at all are no longer accepted.


# Version 0.9.3 (2021-03-17) <a name="v0_9_3"></a>

## Fixed issues

- Deck list import: Fixed import of cards with letters or symbols in collector numbers.
- Fixed wrong item order in the `Settings` menu when using the horizontal search layout
- Fixed several missing icons on platforms without icon theme support, like Windows, or with incomplete icon themes
- Fixed unintended display of empty rows in the current page content table, if changing page layout settings decreases
  the page capacity below the number of cards on the current page. The table now properly trims the empty slots caused
  by moving away overflowing images.


# Version 0.9.2 (2021-03-16) <a name="v0_9_2"></a>

## Changed Features

- The card table shown in the cache cleanup wizard is now sortable by all columns and also shows the card image
  as a tooltip when hovering over the card name.

## Fixed issues

- Reworded some displayed texts and fixed minor issues in strings.
- Show an error message if the user tries to load a file that is not a valid document.
- Show a warning if the loaded document contains unknown entries that were skipped during the loading process.
- Optimized the card data import. It should run a bit faster on slow CPUs or really fast internet connections.
- Fixed potential issues during import when the user re-downloads the card data multiple times in a row.
- Unified the handling of long-running background operations. All three (loading documents, importing decks and
  downloading card data) now behave in the same way and disable most buttons in the main window during the process
- During a long-running background operation, also disable the print preview button and the cache cleanup button to
  prevent issues.
- Optimized GUI responsiveness while a document is being loaded.
- Reduced CPU load during the document loading process.
- Fixed application crashes when directly upgrading from version [`0.3.0`](#v0_3_0).


# Version 0.9.1 (2021-03-04) <a name="v0_9_1"></a>

## Fixed issues

- Prevent the printing dialog from opening twice in a row on Windows systems.
- Ask the user if they want to compact documents prior to printing, when that saves pages, similarly to exporting PDFs.


# Version 0.9.0 (2021-03-04) <a name="v0_9_0"></a>

## Implemented features

- Added direct printing support. The user can now directly print documents using a physical printer attached to the
  computer. It uses the systems native printing support, where available.
- Added command line arguments: The application now accepts a document path as a positional argument.
  This allows opening documents when starting the application.
  - On Windows, this can be used to drag&drop saved documents onto the EXE and load the file, and it can be used
    to associate the file type with the program and then automatically open saved documents by clicking on them.
- When changing download filter settings, ask the user if they want to re-download the card data. The user can do so
  when asked or any time later.
- Implemented a way to trim down the locally stored images: Added a wizard to the Settings menu that allows deletion
  of unused or seldom used card images based on configurable criteria.
  If the user wishes, they can exactly select which images to delete.

## Changed Features

- The card database download now runs in the background. Most of the UI elements stay disabled while the download runs.

## Fixed issues

- Fixed issues when trying to load invalid documents. The application will now do nothing, if the file can not be read
  instead of locking up the GUI.
- Custom RE-based deck importer: Handle user-supplied regular expressions that causes a RecursionError in the parser.
  Such input is now treated as invalid and can’t be entered into the input text field.


# Version 0.8.2 (2021-02-28) <a name="v0_8_2"></a>

## Implemented Features

- Configurable application logging for debugging purposes

## Changed Features

- Moved most long-running operations (downloading images, importing deck lists and loading documents)
  to a background thread. The UI is now more responsive during these operations.
- Disable some buttons and menu entries in the main window while a document is being loaded to prevent possible issues,
  like printing partially loaded documents or saving a partially loaded document over itself.
- Added some more information to the About dialog window and re-designed the information display.

## Fixed issues

- Adding multiple cards in quick succession, for example by double-clicking the "Add" button,
  no longer freezes the GUI. The cards are now properly added in the correct order
- Adding a card that requires an image download and then adding the same card again, while the download is still
  in progress no longer downloads the image twice and no longer inserts a broken, blank card into the current page
- Fixed application hangs until a long-running operation is completed when trying to quit the application
  while a document is being loaded or a deck list import is running
- Fixed the PyInstaller Hooks. It is now possible to build a PyInstaller bundle, even if the application is installed 
  via pip.


# Version 0.8.1 (2021-02-24) <a name="v0_8_1"></a>

## Fixed issues

- Fixed Crash on startup, if the card image cache is not present.
- Make sure to not install the PyInstaller hooks in the user’s Python `site-packages`, when installing via pip.
  In previous versions, these files were placed there unintentionally. These don’t do anything outside PyInstaller
  and only pollute the `site-packages` directory.


# Version 0.8.0 (2021-02-24) <a name="v0_8_0"></a>

## Changed features

- Re-written the card search to use a hierarchical search, focussing primarily on the card name.
  The card search now shows a list of suggestions that can be filtered using a search term,
  including basic wildcard support. When a card name is selected from the suggestion list,
  a specific printing can be selected. The search selects a random printing as a suggestion by default 
  to speed up the process,  if the user doesn’t care about the specific printing used.
  - The new search displays sets using their human-readable English name.
  - The search does not reset itself anymore, when adding a card.
- Added a setting to choose between a horizontal search area layout above the currently edited page and a
  vertical search area that sits between the page list and the currently edited page.
  - The horizontal layout resembles a traditional search bar, as used in other programs, looking more familiar
  - The vertical layout makes better use of the available screen space, requires less mouse movement
    and works better on widescreen monitors
  - Switching the layout requires an application restart.
- The overview table showing the cards of the current page now shows the full, 
  human-readable English set name plus the short, three(-or-more)-letter set code,
  instead of showing only the cryptic set code.

## Fixed issues

- Vastly improved accuracy of all download progress bars, especially for the card data download.
- Prevent inserting damaged PNG files into the local image cache, if the image transfer is interrupted for any reason.
- Improved deck list importer hit rate when importing MTG Arena deck lists from [tappedout.net](https://tappedout.net).
- If manual editing of the configuration file causes a setting to have an invalid value, the default will be restored,
  instead of crashing the application while it tries to parse the invalid data.
- Fixed missing icons in the deck list import wizard when used on Windows 


# Version 0.7.1 (2012-02-18) <a name="v0_7_1"></a>

## Fixed issues

- Fixed a bug that prevented MTGProxyPrinter from starting when it was installed.


# Version 0.7.0 (2012-02-18) <a name="v0_7_0"></a>

## Implemented features

- Implemented automatic deck list imports
  - Implemented as a multi-page wizard that guides the user through the process.
    Accessible via an entry in the File menu.
  - Supports Magic Online, MTG Arena and XMage deck files (And Websites that export compatible files)
  - Appends the imported list to the currently edited document or optionally completely replaces it.
  - Current limitation: Cards have to be matched exactly. Cards that do not specify a unique printing are not imported.
  
## Fixed issues

- Fixed that when the current page overflows, each card batch got added to a completely new page,
  even if the next pages had free slots. Now, free slots on pages after the currently viewed page are used up,
  before adding new pages.


# Version 0.6.0 (2021-02-17) <a name="v0_6_0"></a>

## Implemented features

- When adding a double-faced card, automatically add it’s opposing face.
  This automatically adds the appropriate other side, matching set, art style, 
  border style, etc, if multiple choices are available. Can be disabled in the settings.
- Configurable default storage location for Proxy documents and PDF documents.
  The locations can be set in the settings window.
- Added optional download filter for token cards to exclude all tokens from the card database.
- When compacting the current document will save pages,
  ask the user if they want to compact the document prior to exporting it as a PDF.

## Changed features

- Adjusted the download filters to only exclude explicitly banned cards, when filtering cards banned in certain formats.

## Fixed issues

- Properly remove trailing, empty pages when compacting a document.


# Version 0.5.0 (2021-02-15) <a name="v0_5_0"></a>

## Implemented features

- Added optional, automatic splitting of generated PDF documents, based on a new page count limit setting.
  If enabled, documents with more pages than the set limit will be exported as multiple PDF files.
  This can be used when exported PDFs exceed the printer’s internal file size limit.
- Added document compacting: Completely fill partially filled pages by moving images from the end into free slots.
  This may help reduce the page count and therefore reduce wasted paper when printing.
- Lifted the limitations on the amount of card copies that can be added at once.
  It is now possible to add up to 99 copies of cards at once.
  If the added cards do not fit on the current page, any remaining copies are automatically put on new pages.

## Fixed issues

- When changing document settings decreases the page capacity,
  move images from any overflowing pages to free slots on existing pages or new pages.
- Display card image download progress when an image has to be downloaded from Scryfall instead of freezing the GUI
- Fixed broken rendering of cut markers, if image spacing is active.
- Fixed that the maximum number of card copies possible to add to the current page
  did not increase when cards were deleted from the current page. This limiting was completely removed, so it is now
  always possible to add cards, even if the current page is full.
- Fixed handling of double-faced cards. It is now possible to add both sides of double-faced cards.
  Additionally, support for those was added to the document format,
  so documents including those can be saved and loaded.

## Optimizations

- Further reduced document file size for newly created documents.


# Version 0.4.0 (2021-01-05) <a name="v0_4_0"></a>

## Implemented features

- Added option to remove images from the current page.
  There is a new button below the table showing the current page content
  that can be used to remove all selected images from the current page.
- Added optional drawing and printing of cut helper lines.
  These lines can help machine-cutting the printed pages.
  They are disabled by default and can be enabled in the settings.

## Optimizations

- Reduced document file sizes. This mainly benefits documents with few pages,
  where new documents take about 10% of the disk space when compared to documents saved with version [0.3](#v0_3_0).


# Version 0.3.0 (2020-12-18) <a name="v0_3_0"></a>

- Implemented saving and loading documents to and from disk.
  The created files do not contain the image data and are therefore small.
- Added an About… dialog that shows a message box with the application name, version, homepage and the license text.
- Suppress showing a CMD console window on Windows while MTGProxyPrinter runs.


# Version 0.2.1 (2020-12-02) <a name="v0_2_1"></a>

This version incorporates major performance optimisations.

## Important notice

When Updating to `0.2.1`, please delete the old `CardDataCache.sqlite3` file in your user account’s cache directory 
and let MTGProxyPrinter re-create it from scratch.

## Fixed issues

- Improved card search speed by roughly factor 100 and card data import speed by factor ~ 40.
  Searching cards should now feel instant, as the up-to one-second delay after each key press is gone for good.
- Decreased the card database size. The new database roughly takes two/thirds the space previously required.


# Version 0.2.0 (2020-12-01) <a name="v0_2_0"></a>

This is the second alpha version of MTGProxyPrinter.

## Implemented features

- Filter cards during the card data import based on criteria stored in the settings. You can now skip "funny" 
(silver-bordered), gold-bordered, white-bordered cards and cards banned or illegal in various constructed formats.

  Additional filters may come in the future.

## Fixed bugs

- Fixed down-scaling of card images when exporting PDFs. Generated PDF documents should now have the proper size.


# Version 0.1.1 (2020-11-30) <a name="v0_1_0"></a>

This version fixes a bug that prevents MTGProxyPrinter from running on Windows using Python 3.8.

# Fixed bugs

- Fixed issue that prevented 0.1.0 from running under Windows when using Python 3.8.6, as obtained from python.org
- Fixed missing application icons when run in Windows. Now the main toolbar and menus show the icons as intended.


# Version 0.1.0 (2020-11-30)

This is the first alpha version of MTGProxyPrinter.

## Implemented features

- Obtaining the card information and images for all [Magic](https://magic.wizards.com/) cards in all languages
  from the [Scryfall](https://scryfall.com/) API
- Creating a multi-page document and adding card images to each page
- Searching cards by language, name, set and collector number
- Application settings to specify the preferred language, 
  and document settings like default page size, paper margins and spacing between images
- Automatically determine how many images fit a page considering the document layout settings
- Exporting the created document to high-quality PDF documents.
