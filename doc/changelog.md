# Changelog


# Version 0.5.0 (unreleased, in development)

## Implemented features

- Added optional, automatic splitting of generated PDF documents,
  based on a page count limit set in the settings. If enabled,
  documents with more pages than the set limit will be exported to multiple PDF files.
  This can be used when exported PDFs exceed the printer’s internal file size limit.
- Added document compacting: Completely fill partially filled pages by moving images from the end into free slots.
  This may help reducing the page count and therefore reduce wasted paper when printing.

## Fixed issues

- When changing document settings decreases the page capacity,
  move images from then overflowing pages to free slots or new pages.

## Optimizations

- Further reduced document file size for newly created documents.


# Version 0.4.0 (2021-01-05)

## Implemented features

- Added option to remove images from the current page.
  There is a new button below the table showing the current page content
  that can be used to remove all selected images from the current page.
- Added optional drawing and printing of cut helper lines.
  These lines can help machine-cutting the printed pages.
  They are disabled by default and can be enabled in the settings.

## Optimizations

- Reduced document file sizes. This mainly benefits documents with few pages,
  where new documents take about 10% of the disk space when compared to documents saved with version 0.3.


# Version 0.3.0 (2020-12-18)

- Implemented saving and loading documents to and from disk.
  The created files do not contain the image data and are therefore small.
- Added an About… dialog that shows a message box with the application name, version, homepage and the license text.
- Suppress showing a CMD console window on Windows while MTGProxyPrinter runs.


# Version 0.2.1 (2020-12-02)

This version incorporates major performance optimisations.

## Important notice

When Updating to `0.2.1`, please delete the old `CardDataCache.sqlite3` file in your user account’s cache directory 
and let MTGProxyPrinter re-create it from scratch.

## Fixed issues

- Improved card search speed by roughly factor 100 and card data import speed by factor ~ 40.
  Searching cards should now feel instant, as the up-to one second delay after each key press is gone for good.
- Decreased the card database size. The new database roughly takes two/thirds the space previously required.


# Version 0.2.0 (2020-12-01)

This is the second alpha version of MTGProxyPrinter.

## Implemented features

- Filter cards during the card data import based on criteria stored in the settings. You can now skip "funny" 
(silver-bordered), gold-bordered, white-bordered cards and cards banned or illegal in various constructed formats.

  Additional filters may come in the future.

## Fixed bugs

- Fixed down-scaling of card images when exporting PDFs. Generated PDF documents should now have the proper size.


# Version 0.1.1 (2020-11-30)

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
