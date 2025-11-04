<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" sourcelanguage="en_US" language="en-US">
  <context>
    <name>AboutDialog</name>
    <message>
      <location filename="../ui/about_dialog.ui" line="14"/>
      <source>About MTGProxyPrinter</source>
      <translation>About MTGProxyPrinter</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="27"/>
      <source>About</source>
      <translation>About</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="39"/>
      <source>Application Version:</source>
      <translation>Application Version:</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="55"/>
      <source>Last card update:</source>
      <translation>Last card update:</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="62"/>
      <source>Application version</source>
      <translation>Application version</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="87"/>
      <source>Python Version:</source>
      <translation>Python Version:</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="107"/>
      <source>Python runtime version</source>
      <translation>Python runtime version</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="123"/>
      <source>{application_name} allows printing
[Magic: The Gathering](https://magic.wizards.com/) cards for play-testing
purposes.

{application_name} is unofficial Fan Content permitted under the
[Fan Content Policy](https://company.wizards.com/fancontentpolicy). Not
approved/endorsed by Wizards. Portions of the materials used are property of
Wizards of the Coast. ©[Wizards of the Coast LLC](https://company.wizards.com/).

Under the Fan Content Policy, you may neither sell the data downloaded using
this program, including the card database content and downloaded card images,
nor any documents created, both in digital and physical form.

Project Website: [{application_name} home page]({application_home_page})

Application icon by [islanders2013](https://www.reddit.com/user/islanders2013/)

</source>
      <translation>{application_name} allows printing
[Magic: The Gathering](https://magic.wizards.com/) cards for play-testing
purposes.

{application_name} is unofficial Fan Content permitted under the
[Fan Content Policy](https://company.wizards.com/fancontentpolicy). Not
approved/endorsed by Wizards. Portions of the materials used are property of
Wizards of the Coast. ©[Wizards of the Coast LLC](https://company.wizards.com/).

Under the Fan Content Policy, you may neither sell the data downloaded using
this program, including the card database content and downloaded card images,
nor any documents created, both in digital and physical form.

Project Website: [{application_name} home page]({application_home_page})

Application icon by [islanders2013](https://www.reddit.com/user/islanders2013/)

</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="206"/>
      <location filename="../ui/about_dialog.ui" line="215"/>
      <source>Changelog</source>
      <translation>Changelog</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="229"/>
      <source>License</source>
      <translation>License</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="240"/>
      <source>Third party licenses</source>
      <translation>Third Party licenses</translation>
    </message>
  </context>
  <context>
    <name>ActionAddCard</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/card_actions.py" line="165"/>
      <source>Add {count} × {card_display_string} to page {target}</source>
      <comment>Undo/redo tooltip text. Plural form refers to {target}, not {count}. {target} can be multiple ranges of multiple pages each</comment>
      <translation>
        <numerusform>Add {count} × {card_display_string} to page {target}</numerusform>
        <numerusform>Add {count} × {card_display_string} to pages {target}</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionCompactDocument</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/compact_document.py" line="113"/>
      <source>Compact document, removing %n page(s)</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>
        <numerusform>Compact document, removing %n page</numerusform>
        <numerusform>Compact document, removing %n pages</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionEditCustomCard</name>
    <message>
      <location filename="../../mtg_proxy_printer/document_controller/edit_custom_card.py" line="90"/>
      <source>Edit custom card, set {column_header_text} to {new_value}</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Edit custom card, set {column_header_text} to {new_value}</translation>
    </message>
  </context>
  <context>
    <name>ActionEditDocumentSettings</name>
    <message>
      <location filename="../../mtg_proxy_printer/document_controller/edit_document_settings.py" line="139"/>
      <source>Update document settings</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Update document settings</translation>
    </message>
  </context>
  <context>
    <name>ActionImportDeckList</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/import_deck_list.py" line="82"/>
      <source>Replace document with imported deck list containing %n card(s)</source>
      <comment>Undo/redo tooltip text. Option to delete the current document enabled.</comment>
      <translation>
        <numerusform>Replace document with imported deck list containing %n card</numerusform>
        <numerusform>Replace document with imported deck list containing %n cards</numerusform>
      </translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/import_deck_list.py" line="86"/>
      <source>Import a deck list containing %n card(s)</source>
      <comment>Undo/redo tooltip text. Option to delete the current document disabled.</comment>
      <translation>
        <numerusform>Import a deck list containing %n card</numerusform>
        <numerusform>Import a deck list containing %n cards</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionLoadDocument</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/load_document.py" line="78"/>
      <source>with %n card(s) total</source>
      <comment>Part of the undo/redo tooltip text. Will be inserted as {cards_total}</comment>
      <translation>
        <numerusform>with one card</numerusform>
        <numerusform>with %n cards total</numerusform>
      </translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/load_document.py" line="82"/>
      <source>Load document from &apos;{save_path}&apos;,
containing %n page(s) {cards_total}</source>
      <comment>Undo/redo tooltip text.</comment>
      <translation>
        <numerusform>Load document from &apos;{save_path}&apos;,
containing %n page {cards_total}</numerusform>
        <numerusform>Load document from &apos;{save_path}&apos;,
containing %n pages {cards_total}</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionMoveCardsBetweenPages</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/move_cards.py" line="144"/>
      <source>Move %n card(s) from page {source_page} to {target_page}</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>
        <numerusform>Move a card from page {source_page} to {target_page}</numerusform>
        <numerusform>Move %n cards from page {source_page} to {target_page}</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionMoveCardsWithinPage</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/move_cards.py" line="260"/>
      <source>Reorder %n card(s) on page {page}</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>
        <numerusform>Move a card on page {page}</numerusform>
        <numerusform>Reorder %n cards on page {page}</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionMovePage</name>
    <message>
      <location filename="../../mtg_proxy_printer/document_controller/move_page.py" line="89"/>
      <source>Move page {source_page} to position {target_page}</source>
      <comment>Both parameters are page numbers, like in &apos;Move page 3 to position 7&apos;</comment>
      <translation>Move page {source_page} to position {target_page}</translation>
    </message>
  </context>
  <context>
    <name>ActionNewDocument</name>
    <message>
      <location filename="../../mtg_proxy_printer/document_controller/new_document.py" line="73"/>
      <source>Create new document</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Create new document</translation>
    </message>
  </context>
  <context>
    <name>ActionNewPage</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/page_actions.py" line="88"/>
      <source>Add page(s) {pages}</source>
      <comment>Undo/redo tooltip text. Translations should drop the %n placeholder</comment>
      <translation>
        <numerusform>Add page {pages}</numerusform>
        <numerusform>Add pages {pages}</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionRemoveCards</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/card_actions.py" line="223"/>
      <source>Remove %n card(s) from page {page_number}</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>
        <numerusform>Remove %n card from page {page_number}</numerusform>
        <numerusform>Remove %n cards from page {page_number}</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionRemovePage</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/page_actions.py" line="189"/>
      <source>%n card(s) total</source>
      <comment>Undo/redo tooltip text. The total number of cards removed. Used as {formatted_card_count}</comment>
      <translation>
        <numerusform>%n card total</numerusform>
        <numerusform>%n cards total</numerusform>
      </translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/page_actions.py" line="195"/>
      <source>Remove page(s) {formatted_pages} containing {formatted_card_count}</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>
        <numerusform>Remove page {formatted_pages} containing {formatted_card_count}</numerusform>
        <numerusform>Remove pages {formatted_pages} containing {formatted_card_count}</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionReplaceCard</name>
    <message>
      <location filename="../../mtg_proxy_printer/document_controller/replace_card.py" line="103"/>
      <source>Replace card {old_card} on page {page_number} with {new_card}</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Replace card {old_card} on page {page_number} with {new_card}</translation>
    </message>
  </context>
  <context>
    <name>ActionSaveDocument</name>
    <message>
      <location filename="../../mtg_proxy_printer/document_controller/save_document.py" line="175"/>
      <source>Save document to &apos;{save_file_path}&apos;.</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Save document to &apos;{save_file_path}&apos;.</translation>
    </message>
  </context>
  <context>
    <name>ActionShuffleDocument</name>
    <message>
      <location filename="../../mtg_proxy_printer/document_controller/shuffle_document.py" line="99"/>
      <source>Shuffle document</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Shuffle document</translation>
    </message>
  </context>
  <context>
    <name>ApiStreamTask</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="332"/>
      <source>Requesting the number of available cards on Scryfall failed: 
{error}</source>
      <comment>Error message shown in a message box</comment>
      <translation>Requesting the number of available cards on Scryfall failed: 
{error}</translation>
    </message>
  </context>
  <context>
    <name>ApplicationUpdateCheckTask</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/update_checker.py" line="171"/>
      <source>Application update check: </source>
      <comment>Progress bar label text</comment>
      <translation>Application update check: </translation>
    </message>
  </context>
  <context>
    <name>BatchDownloadTask</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/image_downloader.py" line="234"/>
      <source>Importing deck list:</source>
      <comment>Progress bar label text</comment>
      <translation>Importing deck list:</translation>
    </message>
  </context>
  <context>
    <name>CacheCleanupWizard</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="481"/>
      <source>Cleanup locally stored card images</source>
      <comment>Dialog window title</comment>
      <translation>Cleanup locally stored card images</translation>
    </message>
  </context>
  <context>
    <name>CardFilterPage</name>
    <message>
      <location filename="../ui/cache_cleanup_wizard/card_filter_page.ui" line="14"/>
      <source>Select images for removal</source>
      <translation>Select images for removal</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/card_filter_page.ui" line="17"/>
      <source>Click on entries in the tables below to mark or un-mark them for removal. All selected entries will be removed.</source>
      <translation>Click on entries in the tables below to mark or un-mark them for removal. All selected entries will be removed.</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/card_filter_page.ui" line="30"/>
      <source>All images currently stored on disk:</source>
      <translation>All images currently stored on disk:</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/card_filter_page.ui" line="69"/>
      <source>Images found on disk that can not be associated with any card.</source>
      <translation>Images found on disk that can not be associated with any card.</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/card_filter_page.ui" line="72"/>
      <source>Unknown images:</source>
      <translation>Unknown images:</translation>
    </message>
  </context>
  <context>
    <name>CardListModel</name>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="89"/>
      <source>Copies</source>
      <comment>Table header for card lists. Number of copies that will be added</comment>
      <translation>Copies</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="91"/>
      <source>Card name</source>
      <comment>Table header for card lists</comment>
      <translation>Card name</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="93"/>
      <source>Set</source>
      <comment>Table header for card lists. Magic set containing the card</comment>
      <translation>Set</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="95"/>
      <source>Collector #</source>
      <comment>Table header for card lists</comment>
      <translation>Collector #</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="97"/>
      <source>Language</source>
      <comment>Table header for card lists. Card language.</comment>
      <translation>Language</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="99"/>
      <source>Side</source>
      <comment>Table header for card lists. Side of the card</comment>
      <translation>Side</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="136"/>
      <source>Front</source>
      <comment>Magic card side</comment>
      <translation>Front</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="137"/>
      <source>Back</source>
      <comment>Magic card side</comment>
      <translation>Back</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="145"/>
      <source>Beware: Potentially oversized card!
This card may not fit in your deck.</source>
      <comment>Tooltip shown on cards that, according to API results, have double the physical size. The actual image may still have regular size.</comment>
      <translation>Beware: Potentially oversized card!
This card may not fit in your deck.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="332"/>
      <source>Double-click on entries to
switch the selected printing.</source>
      <comment>Tooltip text</comment>
      <translation>Double-click on entries to
switch the selected printing.</translation>
    </message>
  </context>
  <context>
    <name>CardSideSelectionDelegate</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/item_delegates.py" line="96"/>
      <source>Front</source>
      <comment>Magic card side</comment>
      <translation>Front</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/item_delegates.py" line="97"/>
      <source>Back</source>
      <comment>Magic card side</comment>
      <translation>Back</translation>
    </message>
  </context>
  <context>
    <name>ColumnarCentralWidget</name>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="23"/>
      <source>Move up</source>
      <translation>Move up</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="33"/>
      <source>Current page:</source>
      <translation>Current page:</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="69"/>
      <source>Remove selected</source>
      <translation>Remove selected</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="79"/>
      <source>Add new cards:</source>
      <translation>Add new cards:</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="120"/>
      <source>Move down</source>
      <translation>Move down</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="158"/>
      <source>All pages:</source>
      <translation>All pages:</translation>
    </message>
  </context>
  <context>
    <name>CustomCardImportDialog</name>
    <message>
      <location filename="../ui/custom_card_import_dialog.ui" line="14"/>
      <source>Import custom cards</source>
      <translation>Import custom cards</translation>
    </message>
    <message>
      <location filename="../ui/custom_card_import_dialog.ui" line="20"/>
      <source>Set Copies to …</source>
      <translation>Set Copies to …</translation>
    </message>
    <message>
      <location filename="../ui/custom_card_import_dialog.ui" line="40"/>
      <source>Remove selected</source>
      <translation>Remove selected</translation>
    </message>
    <message>
      <location filename="../ui/custom_card_import_dialog.ui" line="50"/>
      <source>Load images</source>
      <translation>Load images</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/custom_card_import_dialog.py" line="101"/>
      <source>Import custom cards</source>
      <comment>File selection dialog window title</comment>
      <translation>Import custom cards</translation>
    </message>
  </context>
  <context>
    <name>DatabaseImportTask</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="393"/>
      <source>Import card data from File:</source>
      <comment>Progress bar label text</comment>
      <translation>Import card data from File:</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="398"/>
      <source>Update card data from Scryfall:</source>
      <comment>Progress bar label text</comment>
      <translation>Update card data from Scryfall:</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="409"/>
      <source>Error during import from file:
{path}</source>
      <comment>Error message shown in a message box</comment>
      <translation>Error during import from file:
{path}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="414"/>
      <source>Error during update from Scryfall</source>
      <comment>Error message shown in a message box</comment>
      <translation>Error during update from Scryfall</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="440"/>
      <source>Failed to parse data from Scryfall. Reported error: {error}</source>
      <comment>Error message shown in a message box</comment>
      <translation>Failed to parse data from Scryfall. Reported error: {error}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="488"/>
      <source>Post-processing card data:</source>
      <comment>Progress bar label text</comment>
      <translation>Post-processing card data:</translation>
    </message>
  </context>
  <context>
    <name>DatabaseMigrationRunner</name>
    <message>
      <location filename="../../mtg_proxy_printer/carddb_migrations.py" line="787"/>
      <source>Card database migration failed! Will try to re-create it from scratch.
This will wipe any previously downloaded card data and require re-downloading it.
Reported error message:

{error_message}</source>
      <comment>Applying card database migrations required after an app upgrade failed, presumably because the data on disk got corrupted somehow.</comment>
      <translation>Card database migration failed! Will try to re-create it from scratch.
This will wipe any previously downloaded card data and require re-downloading it.
Reported error message:

{error_message}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/carddb_migrations.py" line="803"/>
      <source>Running database migrations:</source>
      <translation>Running database migrations:</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/carddb_migrations.py" line="818"/>
      <source>Migrate to version %n:</source>
      <comment>The numeric parameter is a version number, and not countable.</comment>
      <translation type="unfinished">Migrate to version %n:</translation>
    </message>
  </context>
  <context>
    <name>DebugSettingsPage</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="125"/>
      <source>Debug settings</source>
      <translation>Debug settings</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="127"/>
      <source>Things useful for investigating bugs in the application</source>
      <translation>Things useful for investigating bugs in the application</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="180"/>
      <source>Select download location</source>
      <translation>Select download location</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="188"/>
      <source>Selected location is not a directory</source>
      <translation>Selected location is not a directory</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="191"/>
      <source>Cannot write the card data at the given location, because it is not a directory:
{location}</source>
      <translation>Cannot write the card data at the given location, because it is not a directory:
{location}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="201"/>
      <source>Import previously downloaded card data obtained from Scryfall</source>
      <translation>Import previously downloaded card data obtained from Scryfall</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="203"/>
      <source>Scryfall card data (*.json, *.json.gz)</source>
      <translation>Scryfall card data (*.json, *.json.gz)</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="211"/>
      <source>Selected location is not a file</source>
      <translation>Selected location is not a file</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="212"/>
      <source>Cannot find the selected file:
{location}</source>
      <translation>Cannot find the selected file:
{location}</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="17"/>
      <source>Open debug log directory</source>
      <translation>Open debug log directory</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="27"/>
      <source>Enable writing a log file to disk</source>
      <translation>Enable writing a log file to disk</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="34"/>
      <source>Cutelog is a live log event viewer that can be used to monitor events in real-time.</source>
      <translation>Cutelog is a live log event viewer that can be used to monitor events in real-time.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="37"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;See &lt;a href=&quot;https://github.com/busimus/cutelog&quot;&gt;&lt;span style=&quot; text-decoration: underline; color:#2980b9;&quot;&gt;https://github.com/busimus/cutelog&lt;/span&gt;&lt;/a&gt; for details about Cutelog.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;See &lt;a href=&quot;https://github.com/busimus/cutelog&quot;&gt;&lt;span style=&quot; text-decoration: underline; color:#2980b9;&quot;&gt;https://github.com/busimus/cutelog&lt;/span&gt;&lt;/a&gt; for details about Cutelog.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="40"/>
      <source>Enable Cutelog integration</source>
      <translation>Enable Cutelog integration</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="47"/>
      <source>Download card data as file</source>
      <translation>Download card data as file</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="64"/>
      <source>Event severity that gets logged to file:</source>
      <translation>Event severity that gets logged to file:</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="74"/>
      <source>Only write events with the given severity level and higher to the log file.</source>
      <translation>Only write events with the given severity level and higher to the log file.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="81"/>
      <source>Debug settings (Changing these require an application restart)</source>
      <translation>Debug settings (Changing these require an application restart)</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="101"/>
      <source>Import card data from file</source>
      <translation>Import card data from file</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="117"/>
      <source>Open the Cutelog homepage</source>
      <translation>Open the Cutelog homepage</translation>
    </message>
  </context>
  <context>
    <name>DeckImportWizard</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="648"/>
      <source>Import a deck list</source>
      <comment>Window title</comment>
      <translation>Import a deck list</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="675"/>
      <source>Oversized cards present</source>
      <comment>Message box title. Shown when the deck list contains likely unwanted oversized cards.</comment>
      <translation>Oversized cards present</translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="681"/>
      <source>There are %n possibly oversized cards in the deck list that may not fit into a deck, when printed out.

Continue and use these cards as-is?</source>
      <comment>Message box body text. Shown when the deck list contains likely unwanted oversized cards.</comment>
      <translation>
        <numerusform>There is a possibly oversized card in the deck list that may not fit into a deck, when printed out.

Continue and use the list as-is?</numerusform>
        <numerusform>There are %n possibly oversized cards in the deck list that may not fit into a deck, when printed out.

Continue and use these cards as-is?</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="690"/>
      <source>Incompatible file selected</source>
      <comment>Message box title. Shown when trying to parse a deck list returns no results.</comment>
      <translation>Incompatible file selected</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="694"/>
      <source>Unable to parse the given deck list, no results were obtained.
Maybe you selected the wrong deck list type?</source>
      <comment>Message box body text. Shown when trying to parse a deck list returns no results.</comment>
      <translation>Unable to parse the given deck list, no results were obtained.
Maybe you selected the wrong deck list type?</translation>
    </message>
  </context>
  <context>
    <name>DecklistImportSettingsPage</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="223"/>
      <source>Deck list import</source>
      <translation>Deck list import</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="223"/>
      <source>Configure the deck list importer</source>
      <translation>Configure the deck list importer</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="233"/>
      <source>Select default deck list search path</source>
      <translation>Select default deck list search path</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="17"/>
      <source>Browse …</source>
      <translation>Browse …</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="30"/>
      <source>Deck list search path</source>
      <translation>Deck list search path</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="37"/>
      <source>The import wizard can remove basic lands fully- or semi-automatic.
These settings control the removal behavior.</source>
      <translation>The import wizard can remove basic lands fully- or semi-automatic.
These settings control the removal behavior.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="41"/>
      <source>Control the one-click or automatic basic land removal</source>
      <translation>Control the one-click or automatic basic land removal</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="47"/>
      <source>If enabled, basic lands are automatically removed from deck lists.
If disabled, the deck import wizard keeps them by default,
but offers the removal via a single button click.</source>
      <extracomment>Tooltip</extracomment>
      <translation>If enabled, basic lands are automatically removed from deck lists.
If disabled, the deck import wizard keeps them by default,
but offers the removal via a single button click.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="52"/>
      <source>Fully automatically remove basic lands</source>
      <translation>Fully automatically remove basic lands</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="59"/>
      <source>When enabled, treat Wastes like any other basic land</source>
      <extracomment>Tooltip</extracomment>
      <translation>When enabled, treat Wastes like any other basic land</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="62"/>
      <source>Removal includes Wastes</source>
      <translation>Removal includes Wastes</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="69"/>
      <source>When enabled, treat Snow-Covered basic lands like any other basic land</source>
      <extracomment>Tooltip</extracomment>
      <translation>When enabled, treat Snow-Covered basic lands like any other basic land</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="72"/>
      <source>Removal includes Snow-Covered Basic lands</source>
      <translation>Removal includes Snow-Covered Basic lands</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="82"/>
      <source>These options control the deck list import function.</source>
      <translation>These options control the deck list import function.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="89"/>
      <source>Not all deck list formats always contain complete data.
These options set the default behavior when encountering ambiguous card</source>
      <translation>Not all deck list formats always contain complete data.
These options set the default behavior when encountering ambiguous card</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="93"/>
      <source>Control print selection in ambiguous cases</source>
      <translation>Control print selection in ambiguous cases</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="102"/>
      <source>When automatically selecting a printing, prefer printings with already downloaded images over other possible printings.</source>
      <translation>When automatically selecting a printing, prefer printings with already downloaded images over other possible printings.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="105"/>
      <source>Prefer printings with already downloaded images</source>
      <translation>Prefer printings with already downloaded images</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="112"/>
      <source>Always enable automatic deck list translation when importing deck lists.
This avoids adding foreign language cards, if the deck list happens to contain some.</source>
      <translation>Always enable automatic deck list translation when importing deck lists.
This avoids adding foreign language cards, if the deck list happens to contain some.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="116"/>
      <source>Enable translating imported deck lists by default</source>
      <translation>Enable translating imported deck lists by default</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="123"/>
      <source>Not all deck list formats always contain complete data to identify exact printings.
If enabled, choose an arbitrary printing, instead of failing to identify such cards.
With some deck list formats, this option is always enabled.</source>
      <translation>Not all deck list formats always contain complete data to identify exact printings.
If enabled, choose an arbitrary printing, instead of failing to identify such cards.
With some deck list formats, this option is always enabled.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="128"/>
      <source>Automatically select a printing</source>
      <translation>Automatically select a printing</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="138"/>
      <source>If set, use this as the default location for loading deck lists. Your webbrowser’s download directory is a good choice.</source>
      <translation>If set, use this as the default location for loading deck lists. Your webbrowser’s download directory is a good choice.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="144"/>
      <source>Path to a directory</source>
      <translation>Path to a directory</translation>
    </message>
  </context>
  <context>
    <name>DefaultDocumentLayoutSettingsPage</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="513"/>
      <source>Default document settings</source>
      <translation>Default document settings</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="516"/>
      <source>Set the default document settings used for new documents,
like page size, margins, spacings, etc.</source>
      <translation>Set the default document settings used for new documents,
like page size, margins, spacings, etc.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="520"/>
      <source>Default settings for new documents</source>
      <translation>Default settings for new documents</translation>
    </message>
  </context>
  <context>
    <name>Document</name>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="107"/>
      <source>Card name</source>
      <comment>Table header</comment>
      <translation>Card name</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="108"/>
      <source>Set</source>
      <comment>Table header</comment>
      <translation>Set</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="109"/>
      <source>Collector #</source>
      <comment>Table header</comment>
      <translation>Collector #</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="110"/>
      <source>Language</source>
      <comment>Table header</comment>
      <translation>Language</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="111"/>
      <source>Image</source>
      <comment>Table header</comment>
      <translation>Image</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="112"/>
      <source>Side</source>
      <comment>Table header</comment>
      <translation>Side</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="204"/>
      <source>Double-click on entries to
switch the selected printing.</source>
      <translation>Double-click on entries to
switch the selected printing.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="416"/>
      <source>Page {current}/{total}</source>
      <comment>Tooltip. Shown when hovering over a page in the page list</comment>
      <translation>Page {current}/{total}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="448"/>
      <source>Front</source>
      <comment>Magic card side</comment>
      <translation>Front</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="448"/>
      <source>Back</source>
      <comment>Magic card side</comment>
      <translation>Back</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="513"/>
      <source>Empty Placeholder</source>
      <comment>Card name of the blank placeholder that can be added to keep slots on a page free.</comment>
      <translation>Empty Placeholder</translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/model/document.py" line="456"/>
      <source>%n× {name}</source>
      <comment>Used to display a card name and amount of copies in the page overview. Only needs translation for RTL language support</comment>
      <translation>
        <numerusform>%n× {name}</numerusform>
        <numerusform>%n× {name}</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>DocumentAction</name>
    <message>
      <location filename="../../mtg_proxy_printer/document_controller/_interface.py" line="113"/>
      <source>{first}-{last}</source>
      <comment>Inclusive, formatted number range, from first to last</comment>
      <translation>{first}-{last}</translation>
    </message>
  </context>
  <context>
    <name>DocumentSettingsDialog</name>
    <message>
      <location filename="../ui/document_settings_dialog.ui" line="6"/>
      <source>Configure the current document</source>
      <translation>Configure the current document</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="395"/>
      <source>These settings only affect the current document</source>
      <comment>Shown within the dialog to indicate the scope of the presented settings</comment>
      <translation>These settings only affect the current document</translation>
    </message>
  </context>
  <context>
    <name>ExportCardImagesDialog</name>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="17"/>
      <source>Export card images</source>
      <translation>Export card images</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="29"/>
      <source>Browse …</source>
      <translation>Browse …</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="52"/>
      <source>Custom cards</source>
      <translation>Custom cards</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="66"/>
      <source>Output directory:</source>
      <translation>Output directory:</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="73"/>
      <source>Official cards</source>
      <translation>Official cards</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="83"/>
      <source>Which card images should be exported?</source>
      <translation>Which card images should be exported?</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="93"/>
      <source>Path to a directory</source>
      <translation>Path to a directory</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="472"/>
      <source>Select card image export location</source>
      <comment>File dialog window title</comment>
      <translation>Select card image export location</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="523"/>
      <source>Copy failed for {card_name}! Disk detached/full? Aborting.</source>
      <comment>Error message shown to the user when exporting cards to a directory fails.</comment>
      <translation>Copy failed for {card_name}! Disk detached/full? Aborting.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="555"/>
      <source>Write failed for {card_name}! Disk detached/full? Aborting.</source>
      <comment>Error message shown to the user when exporting cards to a directory fails.</comment>
      <translation>Write failed for {card_name}! Disk detached/full? Aborting.</translation>
    </message>
  </context>
  <context>
    <name>ExportSettingsPage</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="589"/>
      <source>Export settings</source>
      <translation>Export settings</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="589"/>
      <source>Configure the PDF/PNG export</source>
      <translation>Configure the PDF/PNG export</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="629"/>
      <source>Select default export location</source>
      <translation>Select default export location</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="639"/>
      <source>Select PNG background color</source>
      <translation>Select PNG background color</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="23"/>
      <location filename="../ui/settings_window/export_settings_page.ui" line="126"/>
      <source>Automatically split PDF documents, if they get longer than this many pages.
Set to zero to disable splitting.


When printing PDFs using a USB flash drive directly connected to the printer,
the printer may refuse to print documents exceeding some arbitrary size limit.
To work around this limitation, you can enable this option,
and limit the number of pages per PDF. If the document has more pages,
it will be exported into multiple PDF documents automatically.</source>
      <translation>Automatically split PDF documents, if they get longer than this many pages.
Set to zero to disable splitting.


When printing PDFs using a USB flash drive directly connected to the printer,
the printer may refuse to print documents exceeding some arbitrary size limit.
To work around this limitation, you can enable this option,
and limit the number of pages per PDF. If the document has more pages,
it will be exported into multiple PDF documents automatically.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="34"/>
      <source> pages</source>
      <translation> pages</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="44"/>
      <source>Browse…</source>
      <translation>Browse…</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="57"/>
      <source>If enabled, landscape documents are rotated by 90° to portrait mode during export.
Enable this, if printing from PDFs in landscape format results in portrait printouts with cropped-off sides.

Enabling this may cause the cut helper lines to flicker or not show in some PDF viewers.
So only enable this, if actually required.</source>
      <translation>If enabled, landscape documents are rotated by 90° to portrait mode during export.
Enable this, if printing from PDFs in landscape format results in portrait printouts with cropped-off sides.

Enabling this may cause the cut helper lines to flicker or not show in some PDF viewers.
So only enable this, if actually required.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="64"/>
      <source>Enable landscape workaround: Rotate landscape pages by 90°</source>
      <translation>Enable landscape workaround: Rotate landscape pages by 90°</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="74"/>
      <location filename="../ui/settings_window/export_settings_page.ui" line="90"/>
      <source>If set, use this as the default location for saving exported PDF documents.</source>
      <translation>If set, use this as the default location for saving exported PDF documents.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="80"/>
      <source>Path to a directory</source>
      <translation>Path to a directory</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="93"/>
      <source>Export path</source>
      <translation>Export path</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="116"/>
      <source>PNG background color</source>
      <translation>PNG background color</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="137"/>
      <source>Split PDF documents longer than</source>
      <translation>Split PDF documents longer than</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="154"/>
      <source>Background color used for documents exported as PNG images.</source>
      <translation>Background color used for documents exported as PNG images.</translation>
    </message>
  </context>
  <context>
    <name>FileDownloadTask</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="161"/>
      <source>Downloading card data:</source>
      <comment>Progress bar label text</comment>
      <translation>Downloading card data:</translation>
    </message>
  </context>
  <context>
    <name>FileStreamTask</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="265"/>
      <source>Importing card data from disk:</source>
      <comment>Progress bar label text</comment>
      <translation>Importing card data from disk:</translation>
    </message>
  </context>
  <context>
    <name>FilterSetupPage</name>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="14"/>
      <source>Cleanup locally stored card images</source>
      <translation>Cleanup locally stored card images</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="17"/>
      <source>This wizard can be used to remove unwanted card images currently stored on your computer. You can enable automatic cleanup conditions below, to preselect images for removal.</source>
      <translation>This wizard can be used to remove unwanted card images currently stored on your computer. You can enable automatic cleanup conditions below, to preselect images for removal.</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="23"/>
      <source>Delete everything</source>
      <translation>Delete everything</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="33"/>
      <source>Select images for removal based on any matching criterion.</source>
      <translation>Select images for removal based on any matching criterion.</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="36"/>
      <source>Select images for deletion, that are …</source>
      <translation>Select images for deletion, that are …</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="42"/>
      <source>Used in prints and PDFs less often than:</source>
      <translation>Used in prints and PDFs less often than:</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="49"/>
      <source>Not used in prints for:</source>
      <translation>Not used in prints for:</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="59"/>
      <source> days</source>
      <translation> days</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="75"/>
      <source> times</source>
      <translation> times</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="88"/>
      <source>Card images may become unknown, if printings are removed by Scryfall.
This filter also applies to cards and printings hidden by a card filter in the settings.
For example, if you downloaded images of silver-bordered cards and then configured the program to hide those,
all these images become hidden and will be removed.</source>
      <translation>Card images may become unknown, if printings are removed by Scryfall.
This filter also applies to cards and printings hidden by a card filter in the settings.
For example, if you downloaded images of silver-bordered cards and then configured the program to hide those,
all these images become hidden and will be removed.</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="94"/>
      <source>Unknown or belong to hidden printings</source>
      <translation>Unknown or belong to hidden printings</translation>
    </message>
  </context>
  <context>
    <name>GeneralSettingsPage</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="292"/>
      <source>General settings</source>
      <translation>General settings</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="299"/>
      <source>Horizontal layout</source>
      <translation>Horizontal layout</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="300"/>
      <source>Columnar layout</source>
      <translation>Columnar layout</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="301"/>
      <source>Tabbed layout</source>
      <translation>Tabbed layout</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="304"/>
      <source>System default</source>
      <translation>System default</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="305"/>
      <source>English (US) [{progress}%]</source>
      <translation>English (US) [{progress}%]</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="306"/>
      <source>German [{progress}%]</source>
      <translation>German [{progress}%]</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="307"/>
      <source>French [{progress}%]</source>
      <translation>French [{progress}%]</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="316"/>
      <source>Select default save location</source>
      <comment>File picker title text</comment>
      <translation>Select default save location</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="324"/>
      <source>Select custom card search path</source>
      <comment>File picker title text</comment>
      <translation>Select custom card search path</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="17"/>
      <source>Look &amp;&amp; Feel (Changing most of these require an application restart)</source>
      <extracomment>Settings section header</extracomment>
      <translation>Look &amp;&amp; Feel (Changing most of these require an application restart)</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="23"/>
      <source>Application language</source>
      <translation>Application language</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="30"/>
      <source>Main window layout</source>
      <translation>Main window layout</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="40"/>
      <source>Open the main window maximized</source>
      <extracomment>On/off setting</extracomment>
      <translation>Open the main window maximized</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="53"/>
      <source>Horizontal adds a wide, horizontal search area above the currently edited page, and is best for taller screens, like 4:3 or 3:2.
Columnar organizes the main window content in four columns, and is best for (ultra-)wide screens.
Tabbed uses tabs to only show parts of the main window at a time. Best used with small screens in portrait mode (i.e. 9:16), otherwise not recommended.</source>
      <extracomment>Tooltip for the main window layout selector. References the values by name</extracomment>
      <translation>Horizontal adds a wide, horizontal search area above the currently edited page, and is best for taller screens, like 4:3 or 3:2.
Columnar organizes the main window content in four columns, and is best for (ultra-)wide screens.
Tabbed uses tabs to only show parts of the main window at a time. Best used with small screens in portrait mode (i.e. 9:16), otherwise not recommended.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="69"/>
      <source>Open all wizards and dialogs maximized</source>
      <extracomment>On/off setting</extracomment>
      <translation>Open all wizards and dialogs maximized</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="79"/>
      <source>Double-faced cards</source>
      <extracomment>Settings section header</extracomment>
      <translation>Double-faced cards</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="85"/>
      <source>When adding double-faced cards, automatically add the same number of copies of the other side.
Uses the appropriate, matching other card side.
Uncheck to disable this automatism.</source>
      <translation>When adding double-faced cards, automatically add the same number of copies of the other side.
Uses the appropriate, matching other card side.
Uncheck to disable this automatism.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="90"/>
      <source>Automatically add the other side of double-faced cards</source>
      <translation>Automatically add the other side of double-faced cards</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="100"/>
      <source>These paths are selected by default when browsing the file system for files</source>
      <translation>These paths are selected by default when browsing the file system for files</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="103"/>
      <source>Default save paths</source>
      <extracomment>Settings section header</extracomment>
      <translation>Default save paths</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="109"/>
      <location filename="../ui/settings_window/general_settings_page.ui" line="270"/>
      <source>Browse…</source>
      <extracomment>Button tooltip</extracomment>
      <translation>Browse…</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="122"/>
      <source>Document save path</source>
      <translation>Document save path</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="132"/>
      <source>If set, use this as the default location for saving documents.</source>
      <translation>If set, use this as the default location for saving documents.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="138"/>
      <location filename="../ui/settings_window/general_settings_page.ui" line="260"/>
      <source>Path to a directory</source>
      <extracomment>Line editor placeholder text</extracomment>
      <translation>Path to a directory</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="154"/>
      <source>Automatic update checks</source>
      <extracomment>Settings section header</extracomment>
      <translation>Automatic update checks</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="160"/>
      <source>Update checks are performed at application start, if enabled.</source>
      <translation>Update checks are performed at application start, if enabled.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="167"/>
      <source>If enabled, check for application updates, and notify if new updates are available for installation.</source>
      <translation>If enabled, check for application updates, and notify if new updates are available for installation.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="170"/>
      <source>Check for application updates</source>
      <translation>Check for application updates</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="180"/>
      <source>If enabled, query the Scryfall API if new cards are available. If so, offer to update the local card data.</source>
      <translation>If enabled, query the Scryfall API if new cards are available. If so, offer to update the local card data.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="183"/>
      <source>Check for new card data</source>
      <translation>Check for new card data</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="202"/>
      <source>Language choices will default to the chosen language here.
Entries use the language codes as listed on Scryfall.

Note: Cards in deck lists use the language as given by the deck list. To overwrite, use the deck list translation option.</source>
      <translation>Language choices will default to the chosen language here.
Entries use the language codes as listed on Scryfall.

Note: Cards in deck lists use the language as given by the deck list. To overwrite, use the deck list translation option.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="225"/>
      <source>Card language selected at application start and default language when enabling deck list translations</source>
      <translation>Card language selected at application start and default language when enabling deck list translations</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="228"/>
      <source>Preferred card language:</source>
      <translation>Preferred card language:</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="238"/>
      <source>Custom cards</source>
      <extracomment>Settings section header</extracomment>
      <translation>Custom cards</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="244"/>
      <source>Default search path</source>
      <extracomment>Label next to a directory selector for custom cards</extracomment>
      <translation>Default search path</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="254"/>
      <source>If set, search here for custom card images</source>
      <extracomment>Tooltip text</extracomment>
      <translation>If set, search here for custom card images</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="283"/>
      <source>Enforce rounded corners for all imported custom cards</source>
      <extracomment>Tooltip text</extracomment>
      <translation>Enforce rounded corners for all imported custom cards</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="286"/>
      <source>Force round corners</source>
      <extracomment>Custom card import related on/off setting.</extracomment>
      <translation>Force round corners</translation>
    </message>
  </context>
  <context>
    <name>GroupedCentralWidget</name>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="20"/>
      <source>Add new cards:</source>
      <translation>Add new cards:</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="62"/>
      <source>All pages:</source>
      <translation>All pages:</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="72"/>
      <source>Move down</source>
      <translation>Move down</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="85"/>
      <source>Move up</source>
      <translation>Move up</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="98"/>
      <source>Remove selected</source>
      <translation>Remove selected</translation>
    </message>
  </context>
  <context>
    <name>HidePrintingsPage</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="453"/>
      <source>Hide printings</source>
      <translation>Hide printings</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="453"/>
      <source>Hide unwanted printings</source>
      <translation>Hide unwanted printings</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="475"/>
      <source>View cards hidden by this filter on the Scryfall website.</source>
      <comment>Tooltip text on a button next to a printing filter</comment>
      <translation>View cards hidden by this filter on the Scryfall website.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/hide_printings_page.ui" line="17"/>
      <source>These options allow hiding unwanted cards and printings. Hidden printings are treated as though they don’t exist. They can’t be found in the card search and are automatically replaced in loaded documents or imported deck lists, if possible. If all printings of a card are hidden, it won’t be available at all.</source>
      <translation>These options allow hiding unwanted cards and printings. Hidden printings are treated as though they don’t exist. They can’t be found in the card search and are automatically replaced in loaded documents or imported deck lists, if possible. If all printings of a card are hidden, it won’t be available at all.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/hide_printings_page.ui" line="46"/>
      <source>Hide specific sets: Add set codes as listed on Scryfall, for example LEA or 2X2. Separate multiple entries with spaces or line breaks. All words not matching an exact set code are ignored.</source>
      <translation>Hide specific sets: Add set codes as listed on Scryfall, for example LEA or 2X2. Separate multiple entries with spaces or line breaks. All words not matching an exact set code are ignored.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/hide_printings_page.ui" line="62"/>
      <source>Example:

LEA DDU TC13 J21</source>
      <translation>Example:

LEA DDU TC13 J21</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/hide_printings_page.ui" line="70"/>
      <source>No sets currently hidden.</source>
      <translation>No sets currently hidden.</translation>
    </message>
  </context>
  <context>
    <name>HorizontalAddCardWidget</name>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="35"/>
      <source>Language:</source>
      <extracomment>Card language. Next to the language selection widget</extracomment>
      <translation>Language:</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="51"/>
      <source>Card Name</source>
      <translation>Card Name</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="57"/>
      <source>Filter the list below. Use  % (Percent signs) as wildcards matching any number of characters.</source>
      <translation>Filter the list below. Use  % (Percent signs) as wildcards matching any number of characters.</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="60"/>
      <source>Filter card names</source>
      <translation>Filter card names</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="70"/>
      <source>The filtered list of card names in the currently selected language. Click on an entry to select it and choose a printing.</source>
      <translation>The filtered list of card names in the currently selected language. Click on an entry to select it and choose a printing.</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="95"/>
      <source>The sets in which the currently selected card was printed.</source>
      <translation>The sets in which the currently selected card was printed.</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="98"/>
      <source>Set</source>
      <translation>Set</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="104"/>
      <source>Filter set names</source>
      <translation>Filter set names</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="136"/>
      <source>Collector Number</source>
      <translation>Collector Number</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="164"/>
      <source>Copies:</source>
      <extracomment>Number of copies to add. Next to the number input field</extracomment>
      <translation>Copies:</translation>
    </message>
  </context>
  <context>
    <name>ImageDownloadTask</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/image_downloader.py" line="135"/>
      <source>Downloading &apos;{card_name}&apos;:</source>
      <comment>Progress bar label text</comment>
      <translation>Downloading &apos;{card_name}&apos;:</translation>
    </message>
  </context>
  <context>
    <name>KnownCardImageModel</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="139"/>
      <source>Name</source>
      <comment>Table header. Card name</comment>
      <translation>Name</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="141"/>
      <source>Set</source>
      <comment>Table header. Magic set name</comment>
      <translation>Set</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="143"/>
      <source>Collector #</source>
      <comment>Table header</comment>
      <translation>Collector #</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="145"/>
      <source>Is Hidden</source>
      <comment>Table header. Shows if this printing is hidden by a card filter</comment>
      <translation>Is Hidden</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="147"/>
      <source>Front/Back</source>
      <comment>Table header. Shows if this is the front or back side of a card</comment>
      <translation>Front/Back</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="149"/>
      <source>High resolution?</source>
      <comment>Table header. Shows if the card has high-res images</comment>
      <translation>High resolution?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="151"/>
      <source>Size</source>
      <comment>Table header. File size in KiB/MiB</comment>
      <translation>Size</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="153"/>
      <source>Scryfall ID</source>
      <comment>Table header. Shows UUID identifying this card in the Scryfall database</comment>
      <translation>Scryfall ID</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="155"/>
      <source>Path</source>
      <comment>Table header. File system path</comment>
      <translation>Path</translation>
    </message>
  </context>
  <context>
    <name>KnownCardRow</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="100"/>
      <source>Yes</source>
      <comment>This card is hidden by a card filter</comment>
      <translation>Yes</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="102"/>
      <source>No</source>
      <comment>This card is visible and not affected by a card filter</comment>
      <translation>No</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="106"/>
      <source>This printing is hidden by an enabled card filter
and is thus unavailable for printing.</source>
      <comment>Tooltip for cells with hidden cards</comment>
      <translation>This printing is hidden by an enabled card filter
and is thus unavailable for printing.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="109"/>
      <source>Front</source>
      <comment>Card side</comment>
      <translation>Front</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="110"/>
      <source>Back</source>
      <comment>Card side</comment>
      <translation>Back</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="116"/>
      <source>Yes</source>
      <comment>This card has high-resolution images available</comment>
      <translation>Yes</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="118"/>
      <source>No</source>
      <comment>This card only has low-resolution images available.</comment>
      <translation>No</translation>
    </message>
  </context>
  <context>
    <name>LoadDocumentDialog</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="229"/>
      <source>Load MTGProxyPrinter document</source>
      <comment>File dialog window title</comment>
      <translation>Load MTGProxyPrinter document</translation>
    </message>
  </context>
  <context>
    <name>LoadListPage</name>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="17"/>
      <source>Import a deck list for printing</source>
      <translation>Import a deck list for printing</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="20"/>
      <source>Load a deck file from disk or paste deck list in the text field below</source>
      <translation>Load a deck file from disk or paste deck list in the text field below</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="42"/>
      <source>Paste a link to a public deck list here. Hover to see supported sites.</source>
      <translation>Paste a link to a public deck list here. Hover to see supported sites.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="52"/>
      <source>Scryfall search query</source>
      <translation>Scryfall search query</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="59"/>
      <source>If checked, choose an arbitrary printing, if a unique printing is not identified.
If unchecked, each ambiguous card is ignored and reported as unrecognized.</source>
      <translation>If checked, choose an arbitrary printing, if a unique printing is not identified.
If unchecked, each ambiguous card is ignored and reported as unrecognized.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="63"/>
      <source>Guess printings for ambiguous entries in the deck list</source>
      <translation>Choose printings for ambiguous entries in the deck list</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="79"/>
      <source>Download result</source>
      <extracomment>Download the entered Scryfall search query as a deck list</extracomment>
      <translation>Download result</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="89"/>
      <source>Paste your deck list here or use one of the actions above</source>
      <translation>Paste your deck list here or use one of the actions above</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="99"/>
      <source>When an exact printing is not determined or card translation is requested, choose a printing that is already downloaded, if possible.
Enabling this can potentially save disk space and download volume, based on the images already downloaded.</source>
      <translation>When an exact printing is not determined or card translation is requested, choose a printing that is already downloaded, if possible.
Enabling this can potentially save disk space and download volume, based on the images already downloaded.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="103"/>
      <source>When choosing a printing, prefer ones with already downloaded images</source>
      <translation>When choosing a printing, prefer ones with already downloaded images</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="116"/>
      <source>Translate deck list to:</source>
      <translation>Translate deck list to:</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="130"/>
      <source>Opens a file picker and lets you load a deck file from disk.</source>
      <translation>Opens a file picker and lets you load a deck file from disk.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="133"/>
      <source>Select deck list file</source>
      <extracomment>Lets the user select a file, and loads the content as a deck list</extracomment>
      <translation>Select deck list file</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="152"/>
      <source>View result</source>
      <extracomment>View the entered Scryfall search query on the Scryfall website</extracomment>
      <translation>View result</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="171"/>
      <source>Download deck list</source>
      <extracomment>On pressing the button, the deck list given by the entered URL is downloaded</extracomment>
      <translation>Download deck list</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="119"/>
      <source>Supported websites:
{supported_sites}</source>
      <comment>Tooltip text</comment>
      <translation>Supported websites:
{supported_sites}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="169"/>
      <source>Overwrite existing deck list?</source>
      <comment>Message box title</comment>
      <translation>Overwrite existing deck list?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="170"/>
      <source>Selecting a file will overwrite the existing deck list. Continue?</source>
      <comment>Message box body text</comment>
      <translation>Selecting a file will overwrite the existing deck list. Continue?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="177"/>
      <source>Select deck file</source>
      <comment>File selection dialog window title</comment>
      <translation>Select deck file</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="187"/>
      <source>All files (*)</source>
      <comment>File type filter value</comment>
      <translation>All files (*)</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="198"/>
      <source>All Supported </source>
      <comment>File type filter value</comment>
      <translation>All Supported </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="213"/>
      <source>Verify that the URL is valid, reachable, and that the deck list is set to public.
This program cannot download private deck lists. Please note, that setting deck lists to
public may take a minute or two to apply.</source>
      <comment>Error message shown when trying to download a deck list from a seemingly valid URL fails</comment>
      <translation>Verify that the URL is valid, reachable, and that the deck list is set to public.
This program cannot download private deck lists. Please note, that setting deck lists to
public may take a minute or two to apply.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="220"/>
      <source>Overwrite existing deck list?</source>
      <comment>Message box title. Shown when loading a deck list would overwrite existing text</comment>
      <translation>Overwrite existing deck list?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="223"/>
      <source>Downloading a deck list will overwrite the existing deck list. Continue?</source>
      <comment>Message box body text. Shown when loading a deck list would overwrite existing text</comment>
      <translation>Downloading a deck list will overwrite the existing deck list. Continue?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="235"/>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="243"/>
      <source>Deck list download failed</source>
      <comment>Message box title. Shown when downloading failed</comment>
      <translation>Deck list download failed</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="238"/>
      <source>Download failed with HTTP error {http_error_code}.

{bad_request_msg}</source>
      <comment>Message box body text. Shown when the server returns an error code</comment>
      <translation>Download failed with HTTP error {http_error_code}.

{bad_request_msg}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="249"/>
      <source>Download failed.

Check your internet connection, verify that the URL is valid, reachable, and that the deck list is set to public. This program cannot download private deck lists. If this persists, please report a bug in the issue tracker on the homepage.</source>
      <comment>Message box body text. Shown when an unknown error occurred.</comment>
      <translation>Download failed.

Check your internet connection, verify that the URL is valid, reachable, and that the deck list is set to public. This program cannot download private deck lists. If this persists, please report a bug in the issue tracker on the homepage.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="265"/>
      <source>Invalid Scryfall query entered, no result obtained</source>
      <comment>Message box body text</comment>
      <translation>Invalid Scryfall query entered, no result obtained</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="278"/>
      <source>Unable to read file content</source>
      <comment>Message box title. Shown when the user-selected file is unreadable.</comment>
      <translation>Unable to read file content</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="281"/>
      <source>Unable to read the content of file {file_path} as plain text.
Failed to load the content.</source>
      <comment>Message box body text. Shown when the user-selected file is unreadable.</comment>
      <translation>Unable to read the content of file {file_path} as plain text.
Failed to load the content.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="293"/>
      <source>Load large file?</source>
      <comment>Message box title. Shown when the user-selected file is unreasonably large.</comment>
      <translation>Load large file?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="297"/>
      <source>The selected file {file_path} is unexpectedly large ({formatted_size}). Load anyways?</source>
      <comment>Message box body text. Shown when the user-selected file is unreasonably large.</comment>
      <translation>The selected file {file_path} is unexpectedly large ({formatted_size}). Load anyways?</translation>
    </message>
  </context>
  <context>
    <name>LoadSaveDialog</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="186"/>
      <source>MTGProxyPrinter document (*.{default_save_suffix})</source>
      <comment>File type filter</comment>
      <translation>MTGProxyPrinter document (*.{default_save_suffix})</translation>
    </message>
  </context>
  <context>
    <name>MTGArenaParser</name>
    <message>
      <location filename="../../mtg_proxy_printer/decklist_parser/re_parsers.py" line="202"/>
      <source>Magic Arena deck file</source>
      <translation>Magic Arena deck file</translation>
    </message>
  </context>
  <context>
    <name>MTGOnlineParser</name>
    <message>
      <location filename="../../mtg_proxy_printer/decklist_parser/re_parsers.py" line="236"/>
      <source>Magic Online (MTGO) deck file</source>
      <translation>Magic Online (MTGO) deck file</translation>
    </message>
  </context>
  <context>
    <name>MagicWorkstationDeckDataFormatParser</name>
    <message>
      <location filename="../../mtg_proxy_printer/decklist_parser/re_parsers.py" line="180"/>
      <source>Magic Workstation Deck Data Format</source>
      <translation>Magic Workstation Deck Data Format</translation>
    </message>
  </context>
  <context>
    <name>MainWindow</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="227"/>
      <source>Undo:
{top_entry}</source>
      <translation>Undo:
{top_entry}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="229"/>
      <source>Redo:
{top_entry}</source>
      <translation>Redo:
{top_entry}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="284"/>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="298"/>
      <source>printing</source>
      <comment>This is passed as the {action} when asking the user about compacting the document if that can save pages</comment>
      <translation>printing</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="310"/>
      <source>exporting as a PDF</source>
      <comment>This is passed as the {action} when asking the user about compacting the document if that can save pages</comment>
      <translation>exporting as a PDF</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="323"/>
      <source>exporting as a PNG image sequence</source>
      <comment>This is passed as the {action} when asking the user about compacting the document if that can save pages</comment>
      <translation>exporting as a PNG image sequence</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="346"/>
      <source>Network error</source>
      <translation>Network error</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="348"/>
      <source>Operation failed, because a network error occurred.
Check your internet connection. Reported error message:

{message}</source>
      <translation>Operation failed, because a network error occurred.
Check your internet connection. Reported error message:

{message}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="354"/>
      <source>Error</source>
      <translation>Error</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="356"/>
      <source>Operation failed, because an internal error occurred.
Reported error message:

{message}</source>
      <translation>Operation failed, because an internal error occurred.
Reported error message:

{message}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="362"/>
      <source>Saving pages possible</source>
      <translation>Saving pages possible</translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="365"/>
      <source>It is possible to save %n pages when printing this document.
Do you want to compact the document now to minimize the page count prior to {action}?</source>
      <translation>
        <numerusform>It is possible to save %n page when printing this document.
Do you want to compact the document now to minimize the page count prior to {action}?</numerusform>
        <numerusform>It is possible to save %n pages when printing this document.
Do you want to compact the document now to minimize the page count prior to {action}?</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="378"/>
      <source>Download required Card data from Scryfall?</source>
      <translation>Download required Card data from Scryfall?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="383"/>
      <source>This program requires downloading additional card data from Scryfall to operate the card search.
Download the required data from Scryfall now?
Without the data, you can only print custom cards by drag&amp;dropping the image files onto the main window.</source>
      <translation>This program requires downloading additional card data from Scryfall to operate the card search.
Download the required data from Scryfall now?
Without the data, you can only print custom cards by drag&amp;dropping the image files onto the main window.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="427"/>
      <source>Document loading failed</source>
      <translation>Document loading failed</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="431"/>
      <source>Loading file &quot;{failed_path}&quot; failed. The file was not recognized as a {program_name} document. If you want to load a deck list, use the &quot;{function_text}&quot; function instead.
Reported failure reason: {reason}</source>
      <translation>Loading file &quot;{failed_path}&quot; failed. The file was not recognized as a {program_name} document. If you want to load a deck list, use the &quot;{function_text}&quot; function instead.
Reported failure reason: {reason}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="440"/>
      <source>Unavailable printings replaced</source>
      <translation>Unavailable printings replaced</translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="444"/>
      <source>The document contained %n unavailable printings of cards that were automatically replaced with other printings. The replaced printings are unavailable, because they match a configured card filter.</source>
      <translation>
        <numerusform>The document contained %n unavailable printing of a card that was automatically replaced with another printing. The replaced printing is unavailable, because it matches a configured card filter.</numerusform>
        <numerusform>The document contained %n unavailable printings of cards that were automatically replaced with other printings. The replaced printings are unavailable, because they match a configured card filter.</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="449"/>
      <source>Unrecognized cards in loaded document found</source>
      <translation>Unrecognized cards in loaded document found</translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="453"/>
      <source>Skipped %n unrecognized cards in the loaded document. Saving the document will remove these entries permanently.

The locally stored card data may be outdated or the document was tampered with.</source>
      <translation>
        <numerusform>Skipped %n unrecognized card in the loaded document. Saving the document will remove this entry permanently.

The locally stored card data may be outdated or the document was tampered with.</numerusform>
        <numerusform>Skipped %n unrecognized cards in the loaded document. Saving the document will remove these entries permanently.

The locally stored card data may be outdated or the document was tampered with.</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="459"/>
      <source>Application update available. Visit website?</source>
      <translation>Application update available. Visit website?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="463"/>
      <source>An application update is available: Version {newer_version}
You are currently using version {current_version}.

Open the {program_name} website in your web browser to download the new version?</source>
      <translation>An application update is available: Version {newer_version}
You are currently using version {current_version}.

Open the {program_name} website in your web browser to download the new version?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="474"/>
      <source>New card data available</source>
      <translation>New card data available</translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="477"/>
      <source>There are %n new printings available on Scryfall. Update the local data now?</source>
      <translation>
        <numerusform>There is %n new printing available on Scryfall. Update the local data now?</numerusform>
        <numerusform>There are %n new printings available on Scryfall. Update the local data now?</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="490"/>
      <source>Check for application updates?</source>
      <translation>Check for application updates?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="492"/>
      <source>Automatically check for application updates whenever you start {program_name}?</source>
      <translation>Automatically check for application updates whenever you start {program_name}?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="502"/>
      <source>Check for card data updates?</source>
      <translation>Check for card data updates?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="504"/>
      <source>Automatically check for card data updates on Scryfall whenever you start {program_name}?</source>
      <translation>Automatically check for card data updates on Scryfall whenever you start {program_name}?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="513"/>
      <source>{question}
You can change this later in the settings.</source>
      <translation>{question}
You can change this later in the settings.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="14"/>
      <source>MTGProxyPrinter</source>
      <translation>MTGProxyPrinter</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="31"/>
      <source>Fi&amp;le</source>
      <translation>Fi&amp;le</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="35"/>
      <source>Export</source>
      <translation>Export</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="59"/>
      <source>Application</source>
      <translation>Application</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="73"/>
      <source>Edit</source>
      <translation>Edit</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="89"/>
      <source>Web links</source>
      <translation>Web links</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="106"/>
      <location filename="../ui/main_window.ui" line="327"/>
      <source>Show toolbar</source>
      <translation>Show toolbar</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="135"/>
      <source>&amp;Quit</source>
      <translation>&amp;Quit</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="138"/>
      <source>Ctrl+Q</source>
      <translation>Ctrl+Q</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="149"/>
      <source>&amp;Print</source>
      <translation>&amp;Print</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="152"/>
      <source>Print the current document</source>
      <translation>Print the current document</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="155"/>
      <source>Ctrl+P</source>
      <translation>Ctrl+P</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="163"/>
      <source>&amp;Show print preview</source>
      <translation>&amp;Show print preview</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="166"/>
      <source>Show print preview window</source>
      <translation>Show print preview window</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="174"/>
      <source>&amp;Create PDF</source>
      <translation>&amp;Create PDF</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="177"/>
      <source>Create a PDF document</source>
      <translation>Create a PDF document</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="185"/>
      <source>Discard page</source>
      <translation>Discard page</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="188"/>
      <source>Discard this page.</source>
      <translation>Discard this page.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="196"/>
      <source>Settings</source>
      <translation>Settings</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="207"/>
      <source>Update card data</source>
      <translation>Update card data</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="215"/>
      <source>New Page</source>
      <translation>New Page</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="218"/>
      <source>Add a new, empty page.</source>
      <translation>Add a new, empty page.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="226"/>
      <source>Save</source>
      <translation>Save</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="229"/>
      <source>Ctrl+S</source>
      <translation>Ctrl+S</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="237"/>
      <source>New</source>
      <translation>New</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="240"/>
      <source>Ctrl+N</source>
      <translation>Ctrl+N</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="248"/>
      <source>Load</source>
      <translation>Load</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="251"/>
      <source>Ctrl+L</source>
      <translation>Ctrl+L</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="259"/>
      <source>Save as …</source>
      <translation>Save as …</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="264"/>
      <source>About …</source>
      <translation>About …</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="272"/>
      <source>Show Changelog</source>
      <translation>Show change-log</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="280"/>
      <source>Compact document</source>
      <translation>Compact document</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="283"/>
      <source>Minimize page count: Fill empty slots on pages by moving cards from the end of the document</source>
      <translation>Minimize page count: Fill empty slots on pages by moving cards from the end of the document</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="291"/>
      <source>Edit document settings</source>
      <translation>Edit document settings</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="294"/>
      <source>Configure page size, margins, image spacings for the currently edited document.</source>
      <translation>Configure page size, margins, image spacings for the currently edited document.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="302"/>
      <source>Import deck list</source>
      <translation>Import deck list</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="305"/>
      <source>Import a deck list from online sources</source>
      <translation>Import a deck list from online sources</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="313"/>
      <source>Cleanup card images</source>
      <translation>Cleanup card images</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="316"/>
      <source>Delete locally stored card images you no longer need.</source>
      <translation>Delete locally stored card images you no longer need.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="330"/>
      <source>Ctrl+M</source>
      <translation>Ctrl+M</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="338"/>
      <source>Download missing card images</source>
      <translation>Download missing card images</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="346"/>
      <source>Shuffle document</source>
      <translation>Shuffle document</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="349"/>
      <source>Randomly rearrange all card image.
If you want to quickly print a full deck for playing,
use this to reduce the initial deck shuffling required</source>
      <translation>Randomly rearrange all card image.
If you want to quickly print a full deck for playing,
use this to reduce the initial deck shuffling required</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="362"/>
      <source>Undo</source>
      <translation>Undo</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="373"/>
      <source>Redo</source>
      <translation>Redo</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="381"/>
      <source>Add empty card to page</source>
      <translation>Add empty card to page</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="384"/>
      <source>Add an empty spacer filling a card slot</source>
      <translation>Add an empty spacer filling a card slot</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="392"/>
      <source>Add custom cards</source>
      <translation>Add custom cards</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="400"/>
      <source>Export as image sequence</source>
      <translation>Export as image sequence</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="403"/>
      <source>Export document as an image sequence</source>
      <translation>Export document as an image sequence</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="411"/>
      <source>Export individual card images</source>
      <translation>Export individual card images</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="414"/>
      <source>Export all card images to a directory</source>
      <translation>Export all card images to a directory</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="422"/>
      <source>Source Code</source>
      <translation>Source Code</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="430"/>
      <source>Source Code (GitHub)</source>
      <translation>Source Code (GitHub)</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="438"/>
      <source>Contribute Translations</source>
      <translation>Contribute Translations</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="443"/>
      <source>Support development on Ko-Fi</source>
      <translation>Support development on Ko-Fi</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="451"/>
      <source>Project on PyPI</source>
      <translation>Project on PyPI</translation>
    </message>
  </context>
  <context>
    <name>MissingImagesManager</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/missing_images_manager.py" line="67"/>
      <source>Unable to obtain %n missing card image(s).
These will be missing in exported or printed documents.</source>
      <comment>Warning message. A last attempt at trying to download images of cards with missing images failed.</comment>
      <translation>
        <numerusform>Unable to obtain a missing card image.
It will be missing in exported or printed documents.</numerusform>
        <numerusform>Unable to obtain %n missing card images.
These will be missing in exported or printed documents.</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ObtainMissingImagesTask</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/image_downloader.py" line="279"/>
      <source>Fetching missing images:</source>
      <comment>Progress bar label text</comment>
      <translation>Fetching missing images:</translation>
    </message>
  </context>
  <context>
    <name>PNGRenderer</name>
    <message>
      <location filename="../../mtg_proxy_printer/print.py" line="87"/>
      <source>Export as PNGs:</source>
      <comment>Progress bar label text</comment>
      <translation>Export as PNGs:</translation>
    </message>
  </context>
  <context>
    <name>PageCardTableView</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="114"/>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="134"/>
      <source>Add %n copies</source>
      <comment>Context menu action: Add additional card copies to the document</comment>
      <translation>
        <numerusform>Add %n copy</numerusform>
        <numerusform>Add %n copies</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="122"/>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="140"/>
      <source>Add copies …</source>
      <comment>Context menu action: Add additional card copies to the document. User will be asked for a number</comment>
      <translation>Add copies …</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="125"/>
      <source>Generate DFC check card</source>
      <translation>Generate DFC check card</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="152"/>
      <source>All related cards</source>
      <translation>All related cards</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="161"/>
      <source>Add copies</source>
      <translation>Add copies</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="163"/>
      <source>Add copies of {card_name}</source>
      <comment>Asks the user for a number. Does not need plural forms</comment>
      <translation>Add copies of {card_name}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="187"/>
      <source>Export image</source>
      <translation>Export image</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="203"/>
      <source>Save card image</source>
      <translation>Save card image</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="203"/>
      <source>Images (*.png *.bmp *.jpg)</source>
      <translation>Images (*.png *.bmp *.jpg)</translation>
    </message>
  </context>
  <context>
    <name>PageConfigPreviewArea</name>
    <message>
      <location filename="../ui/page_config_preview_area.ui" line="29"/>
      <location filename="../ui/page_config_preview_area.ui" line="36"/>
      <source> cards</source>
      <translation> cards</translation>
    </message>
    <message>
      <location filename="../ui/page_config_preview_area.ui" line="43"/>
      <source>Regular</source>
      <translation>Regular</translation>
    </message>
    <message>
      <location filename="../ui/page_config_preview_area.ui" line="53"/>
      <source>Oversized</source>
      <translation>Oversized</translation>
    </message>
  </context>
  <context>
    <name>PageConfigWidget</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="89"/>
      <source>Disabled</source>
      <comment>A cut marker style</comment>
      <translation>Disabled</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="90"/>
      <source>Solid lines</source>
      <comment>A cut marker style</comment>
      <translation>Solid lines</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="91"/>
      <source>Dashed lines</source>
      <comment>A cut marker style</comment>
      <translation>Dashed lines</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="92"/>
      <source>Dotted lines</source>
      <comment>A cut marker style</comment>
      <translation>Dotted lines</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="96"/>
      <source>Disabled</source>
      <comment>A print/cut registration marker style</comment>
      <translation>Disabled</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="97"/>
      <source>Bullseye</source>
      <comment>A print/cut registration marker style</comment>
      <translation>Bullseye</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="100"/>
      <source>Silhouette cutter (Cameo-compatible)</source>
      <comment>A print/cut registration marker style</comment>
      <translation>Silhouette cutter (Cameo-compatible)</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="205"/>
      <source>Select watermark text color</source>
      <translation>Select watermark text color</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="223"/>
      <source>Select cut marker color</source>
      <translation>Select cut marker color</translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="240"/>
      <source>%n regular card(s)</source>
      <comment>Display of the resulting page capacity for regular-sized cards</comment>
      <translation>
        <numerusform>%n regular card</numerusform>
        <numerusform>%n regular cards</numerusform>
      </translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="244"/>
      <source>%n oversized card(s)</source>
      <comment>Display of the resulting page capacity for oversized cards</comment>
      <translation>
        <numerusform>%n oversized card</numerusform>
        <numerusform>%n oversized cards</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="249"/>
      <source>{regular_text}, {oversized_text}</source>
      <comment>Combination of the page capacities for regular, and oversized cards</comment>
      <translation>{regular_text}, {oversized_text}</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="14"/>
      <source>Default settings for new documents</source>
      <translation>Default settings for new documents</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="35"/>
      <source>Show Preview</source>
      <translation>Show Preview</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="53"/>
      <source>The document name is printed on each page and can help you keep track
of different printed sheets and to which deck they belong.

Leave empty to disable.</source>
      <translation>The document name is printed on each page and can help you keep track
of different printed sheets and to which deck they belong.

Leave empty to disable.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="62"/>
      <source>Document/deck name</source>
      <translation>Document/deck name</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="72"/>
      <source>If enabled, the page number is printed on each page. Makes it easier to notice missing pages in a stack.</source>
      <translation>If enabled, the page number is printed on each page. Makes it easier to notice missing pages in a stack.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="75"/>
      <source>Print page numbers</source>
      <translation>Print page numbers</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="82"/>
      <source>Document name</source>
      <translation>Document name</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="92"/>
      <source>Draw 90° card corners, instead of round ones</source>
      <translation>Draw 90° card corners, instead of round ones</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="116"/>
      <source>Paper dimensions</source>
      <translation>Paper dimensions</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="122"/>
      <source>Draw an additional border around cards to ease cutting.</source>
      <translation>Draw an additional border around cards to ease cutting.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="125"/>
      <location filename="../ui/page_config_widget.ui" line="188"/>
      <location filename="../ui/page_config_widget.ui" line="210"/>
      <location filename="../ui/page_config_widget.ui" line="273"/>
      <location filename="../ui/page_config_widget.ui" line="348"/>
      <location filename="../ui/page_config_widget.ui" line="380"/>
      <location filename="../ui/page_config_widget.ui" line="401"/>
      <location filename="../ui/page_config_widget.ui" line="433"/>
      <location filename="../ui/page_config_widget.ui" line="454"/>
      <source> mm</source>
      <translation> mm</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="135"/>
      <source>Bottom margin</source>
      <translation>Bottom margin</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="148"/>
      <source>Right margin</source>
      <translation>Right margin</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="161"/>
      <source>Top margin</source>
      <translation>Top margin</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="183"/>
      <source>Paper width in millimeters.
Must match the size of the sheets in the printer.
Otherwise, scaling may be applied by the printer driver.</source>
      <translation>Paper width in millimeters.
Must match the size of the sheets in the printer.
Otherwise, scaling may be applied by the printer driver.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="207"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the right paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the right paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="223"/>
      <source>Left margin</source>
      <translation>Left margin</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="236"/>
      <source>Paper height</source>
      <translation>Paper height</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="249"/>
      <source>Card bleed</source>
      <translation>Card bleed</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="268"/>
      <source>Paper height in millimeters.
Must match the size of the sheets in the printer.
Otherwise, scaling may be applied by the printer driver.</source>
      <translation>Paper height in millimeters.
Must match the size of the sheets in the printer.
Otherwise, scaling may be applied by the printer driver.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="286"/>
      <source>Resulting page capacity:</source>
      <translation>Resulting page capacity:</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="296"/>
      <source>Paper width</source>
      <translation>Paper width</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="309"/>
      <source>Number of cards fitting on each page,
based on the page size and spacings configured</source>
      <translation>Number of cards fitting on each page,
based on the page size and spacings configured</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="326"/>
      <source>Switch between portrait and landscape mode</source>
      <translation>Switch between portrait and landscape mode</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="329"/>
      <source>Flip</source>
      <translation>Flip</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="345"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the bottom paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the bottom paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="358"/>
      <source>Column spacing</source>
      <translation>Column spacing</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="377"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the left paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the left paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="396"/>
      <source>Space between image rows in mm.
If set to zero, you only need one cut to separate two images,
otherwise you need two cuts but require less precision hitting the exact middle.</source>
      <translation>Space between image rows in mm.
If set to zero, you only need one cut to separate two images,
otherwise you need two cuts but require less precision hitting the exact middle.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="411"/>
      <source>Row spacing</source>
      <translation>Row spacing</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="430"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the top paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the top paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="449"/>
      <source>Space between image columns in mm.
If set to zero, you only need one cut to separate two images,
otherwise you need two cuts but require less precision hitting the exact middle.</source>
      <translation>Space between image columns in mm.
If set to zero, you only need one cut to separate two images,
otherwise you need two cuts but require less precision hitting the exact middle.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="464"/>
      <source>Paper size</source>
      <translation>Paper size</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="475"/>
      <source>Cut markers</source>
      <translation>Cut markers</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="484"/>
      <source>Draw cut helper lines above card images, instead of below them</source>
      <translation>Draw cut helper lines above card images, instead of below them</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="487"/>
      <source>Draw above cards</source>
      <translation>Draw above cards</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="494"/>
      <source>The default width of 0 draws a thin line, regardless of zoom level.</source>
      <translation>The default width of 0 draws a thin line, regardless of zoom level.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="510"/>
      <source>Cut helper lines</source>
      <translation>Cut helper lines</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="520"/>
      <location filename="../ui/page_config_widget.ui" line="721"/>
      <source>Select a color</source>
      <translation>Select a color</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="543"/>
      <source>Line width</source>
      <translation>Line width</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="566"/>
      <source>Color and opacity</source>
      <translation>Color and opacity</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="595"/>
      <source>Print registration marks</source>
      <translation>Print registration marks</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="606"/>
      <source>Watermark</source>
      <translation>Watermark</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="612"/>
      <source>X position</source>
      <translation>X position</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="622"/>
      <source>Y position</source>
      <translation>Y position</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="632"/>
      <source>Watermark text</source>
      <translation>Watermark text</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="655"/>
      <source>Rotation angle</source>
      <translation>Rotation angle</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="681"/>
      <source>Font size</source>
      <translation>Font size</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="691"/>
      <source>Text color and opacity</source>
      <translation>Text color and opacity</translation>
    </message>
  </context>
  <context>
    <name>PageRenderer</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_renderer.py" line="70"/>
      <source>Use Ctrl+Mouse wheel to zoom.
Usable keyboard shortcuts are:
Zoom in: {zoom_in_shortcuts}
Zoom out: {zoom_out_shortcuts}</source>
      <translation>Use Ctrl+Mouse wheel to zoom.
Usable keyboard shortcuts are:
Zoom in: {zoom_in_shortcuts}
Zoom out: {zoom_out_shortcuts}</translation>
    </message>
  </context>
  <context>
    <name>ParserBase</name>
    <message>
      <location filename="../../mtg_proxy_printer/decklist_parser/common.py" line="72"/>
      <source>All files (*)</source>
      <comment>File type filter</comment>
      <translation>All files (*)</translation>
    </message>
  </context>
  <context>
    <name>PrettySetListModel</name>
    <message>
      <location filename="../../mtg_proxy_printer/model/string_list.py" line="36"/>
      <source>Set</source>
      <comment>MTG set name</comment>
      <translation>Set</translation>
    </message>
  </context>
  <context>
    <name>PrinterSettingsPage</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="538"/>
      <source>Printer settings</source>
      <translation>Printer settings</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="538"/>
      <source>Configure the printer</source>
      <translation>Configure the printer</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/printer_settings_page.ui" line="17"/>
      <source>Horizontal printing offset</source>
      <translation>Horizontal printing offset</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/printer_settings_page.ui" line="24"/>
      <source>Globally shifts the printing area to correct physical offsets in the printer.
Positive values shift to the right.
Negative offsets shift to the left.</source>
      <translation>Globally shifts the printing area to correct physical offsets in the printer.
Positive values shift to the right.
Negative offsets shift to the left.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/printer_settings_page.ui" line="32"/>
      <source> mm</source>
      <translation> mm</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/printer_settings_page.ui" line="48"/>
      <source>If enabled, print landscape documents in portrait mode with all content rotated by 90°.
Enable this, if printing landscape documents results in portrait printouts with cropped-off sides.</source>
      <translation>If enabled, print landscape documents in portrait mode with all content rotated by 90°.
Enable this, if printing landscape documents results in portrait printouts with cropped-off sides.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/printer_settings_page.ui" line="52"/>
      <source>Enable landscape workaround: Rotate prints by 90°</source>
      <translation>Enable landscape workaround: Rotate prints by 90°</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/printer_settings_page.ui" line="62"/>
      <source>When enabled, instruct the printer to use borderless mode and let MTGProxyPrinter manage the printing margins.
Disable this, if your printer keeps scaling print-outs up or down.

When disabled, managing the page margins is delegated to the printer driver,
which should increase compatibility, at the expense of drawing shorter cut helper lines.</source>
      <translation>When enabled, instruct the printer to use borderless mode and let MTGProxyPrinter manage the printing margins.
Disable this, if your printer keeps scaling print-outs up or down.

When disabled, managing the page margins is delegated to the printer driver,
which should increase compatibility, at the expense of drawing shorter cut helper lines.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/printer_settings_page.ui" line="69"/>
      <source>Configure printer for borderless printing</source>
      <translation>Configure printer for borderless printing</translation>
    </message>
  </context>
  <context>
    <name>PrintingFilterModel</name>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="79"/>
      <source>Hide cards banned in the {format} format</source>
      <comment>Tooltip text</comment>
      <translation>Hide cards banned in the {format} format</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="83"/>
      <source>General filters</source>
      <comment>Display text. Printing filter section header</comment>
      <translation>General filters</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="84"/>
      <source>Hide printings based on general card properties</source>
      <comment>Tooltip text</comment>
      <translation>Hide printings based on general card properties</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="86"/>
      <source>Hide cards depicting racism</source>
      <comment>Display text</comment>
      <translation>Hide cards depicting racism</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="94"/>
      <source>Hide cards banned for depicting racism.

Background: Some cards were banned by Wizards of the Coast,
because they depict references to controversial real-world events,
religion or contain combinations of card effect, name and artwork that,
when viewed together, depict racism or are otherwise inappropriate.
These cards are banned in all sanctioned tournament formats and several
community formats like Commander, Oathbreaker and others.</source>
      <comment>Tooltip text</comment>
      <translation>Hide cards banned for depicting racism.

Background: Some cards were banned by Wizards of the Coast,
because they depict references to controversial real-world events,
religion or contain combinations of card effect, name and artwork that,
when viewed together, depict racism or are otherwise inappropriate.
These cards are banned in all sanctioned tournament formats and several
community formats like Commander, Oathbreaker and others.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="98"/>
      <source>Hide cards with placeholder images</source>
      <comment>Display text</comment>
      <translation>Hide cards with placeholder images</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="102"/>
      <source>Hide non-English cards with low-resolution,
English placeholder images containing an overlay text stating
“This card is not available in the selected language.”</source>
      <comment>Tooltip text</comment>
      <translation>Hide non-English cards with low-resolution,
English placeholder images containing an overlay text stating
“This card is not available in the selected language.”</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="106"/>
      <source>Hide “funny” cards</source>
      <comment>Display text</comment>
      <translation>Hide “funny” cards</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="111"/>
      <source>“Funny” cards, not legal in any constructed format.
This includes silver-bordered cards, full-art Contraptions from Unstable,
cards with acorn-shaped security stamps from Unfinity (and newer Un-Sets),
some black-bordered promotional cards with non-standard back faces,
and potentially others.</source>
      <comment>Tooltip text</comment>
      <translation>“Funny” cards, not legal in any constructed format.
This includes silver-bordered cards, full-art Contraptions from Unstable,
cards with acorn-shaped security stamps from Unfinity (and newer Un-Sets),
some black-bordered promotional cards with non-standard back faces,
and potentially others.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="115"/>
      <source>Hide digital-only cards or printings</source>
      <comment>Display text</comment>
      <translation>Hide digital-only cards or printings</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="118"/>
      <source>Hide cards and printings that are only available on digital platforms. This includes all kinds of digital printings.</source>
      <comment>Tooltip text</comment>
      <translation>Hide cards and printings that are only available on digital platforms. This includes all kinds of digital printings.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="122"/>
      <source>Hide reversible cards</source>
      <comment>Display text</comment>
      <translation>Hide reversible cards</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="125"/>
      <source>Some single-sided cards are re-printed as two-sided, reversible cards in some Secret Lair releases.
This filter hides those.</source>
      <comment>Tooltip text</comment>
      <translation>Some single-sided cards are re-printed as two-sided, reversible cards in some Secret Lair releases.
This filter hides those.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="129"/>
      <source>Border style</source>
      <comment>Display text. Printing filter section header</comment>
      <translation>Border style</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="132"/>
      <source>Hide white-bordered cards</source>
      <comment>Display text</comment>
      <translation>Hide white-bordered cards</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="137"/>
      <source>Hide gold-bordered cards</source>
      <comment>Display text</comment>
      <translation>Hide gold-bordered cards</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="142"/>
      <source>Some “collectible” sets, like full reprints of tournament-winning decks were printed with golden borders.
Many also have printed signatures of the involved players in the text box.

These are not tournament legal</source>
      <comment>Tooltip text</comment>
      <translation>Some “collectible” sets, like full reprints of tournament-winning decks were printed with golden borders.
Many also have printed signatures of the involved players in the text box.

These are not tournament legal</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="146"/>
      <source>Hide borderless cards</source>
      <comment>Display text</comment>
      <translation>Hide borderless cards</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="149"/>
      <source>Hide cards without a defined, solid-color border.
Those require higher cutting precision to get right.</source>
      <comment>Tooltip text</comment>
      <translation>Hide cards without a defined, solid-color border.
Those require higher cutting precision to get right.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="153"/>
      <source>Hide extended-art cards</source>
      <comment>Display text</comment>
      <translation>Hide extended-art cards</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="156"/>
      <source>Hide cards with artwork extending to the left and right card border.
Similar to borderless cards, these require higher precision during the cutting process.</source>
      <comment>Tooltip text</comment>
      <translation>Hide cards with artwork extending to the left and right card border.
Similar to borderless cards, these require higher precision during the cutting process.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="160"/>
      <source>Non-traditional cards</source>
      <comment>Display text. Printing filter section header</comment>
      <translation>Non-traditional cards</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="163"/>
      <source>Hide oversized cards</source>
      <comment>Display text</comment>
      <translation>Hide oversized cards</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="167"/>
      <source>These cards are larger than regular Magic cards and can’t be included in decks.
Includes Archenemy schemes, Planechase planes and
oversized commander creature or Planeswalker cards included in some pre-constructed Commander decks.</source>
      <comment>Tooltip text</comment>
      <translation>These cards are larger than regular Magic cards and can’t be included in decks.
Includes Archenemy schemes, Planechase planes and
oversized commander creature or Planeswalker cards included in some pre-constructed Commander decks.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="171"/>
      <source>Hide Tokens</source>
      <comment>Display text</comment>
      <translation>Hide Tokens</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="174"/>
      <source>The official Tokens, used to represent permanents created by card effects.
Not part of deck-building. Obscure ones can be relatively rare</source>
      <comment>Tooltip text</comment>
      <translation>The official Tokens, used to represent permanents created by card effects.
Not part of deck-building. Obscure ones can be relatively rare</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="178"/>
      <source>Hide Art Series cards</source>
      <comment>Display text</comment>
      <translation>Hide Art Series cards</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="180"/>
      <source>Artwork cards that can be found in Set Boosters or Play Boosters</source>
      <comment>Tooltip text</comment>
      <translation>Artwork cards that can be found in Set Boosters or Play Boosters</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="185"/>
      <source>Format bans: Hide cards banned in specific formats</source>
      <comment>Display text. Section header above MTG format ban filters</comment>
      <translation>Format bans: Hide cards banned in specific formats</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="188"/>
      <source>Brawl</source>
      <comment>Display text. Magic format name. Translations (if one exists) should probably also include the English name like {translated name}(&lt;english name&gt;)</comment>
      <translation>Brawl</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="192"/>
      <source>Commander</source>
      <comment>Display text. Magic format name. Translations (if one exists) should probably also include the English name like {translated name}(&lt;english name&gt;)</comment>
      <translation>Commander</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="196"/>
      <source>Historic</source>
      <comment>Display text. Magic format name. Translations (if one exists) should probably also include the English name like {translated name}(&lt;english name&gt;)</comment>
      <translation>Historic</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="200"/>
      <source>Legacy</source>
      <comment>Display text. Magic format name. Translations (if one exists) should probably also include the English name like {translated name}(&lt;english name&gt;)</comment>
      <translation>Legacy</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="204"/>
      <source>Modern</source>
      <comment>Display text. Magic format name. Translations (if one exists) should probably also include the English name like {translated name}(&lt;english name&gt;)</comment>
      <translation>Modern</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="208"/>
      <source>Oathbreaker</source>
      <comment>Display text. Magic format name. Translations (if one exists) should probably also include the English name like {translated name}(&lt;english name&gt;)</comment>
      <translation>Oathbreaker</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="212"/>
      <source>Pauper</source>
      <comment>Display text. Magic format name. Translations (if one exists) should probably also include the English name like {translated name}(&lt;english name&gt;)</comment>
      <translation>Pauper</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="216"/>
      <source>Pioneer</source>
      <comment>Display text. Magic format name. Translations (if one exists) should probably also include the English name like {translated name}(&lt;english name&gt;)</comment>
      <translation>Pioneer</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="220"/>
      <source>Standard</source>
      <comment>Display text. Magic format name. Translations (if one exists) should probably also include the English name like {translated name}(&lt;english name&gt;)</comment>
      <translation>Standard</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="224"/>
      <source>Vintage</source>
      <comment>Display text. Magic format name. Translations (if one exists) should probably also include the English name like {translated name}(&lt;english name&gt;)</comment>
      <translation>Vintage</translation>
    </message>
  </context>
  <context>
    <name>PrintingFilterUpdater.store_current_printing_filters()</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/printing_filter_updater.py" line="92"/>
      <source>Processing updated card filters:</source>
      <translation>Processing updated card filters:</translation>
    </message>
  </context>
  <context>
    <name>ProgressBar</name>
    <message>
      <location filename="../ui/progress_bar.ui" line="36"/>
      <source>Cancel</source>
      <translation>Cancel</translation>
    </message>
  </context>
  <context>
    <name>SaveDocumentAsDialog</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="197"/>
      <source>Save document as …</source>
      <comment>File dialog window title</comment>
      <translation>Save document as …</translation>
    </message>
  </context>
  <context>
    <name>SavePDFDialog</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="96"/>
      <source>Export as PDF</source>
      <comment>File dialog window title</comment>
      <translation>Export as PDF</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="97"/>
      <source>PDF documents (*.pdf)</source>
      <comment>File type filter</comment>
      <translation>PDF documents (*.pdf)</translation>
    </message>
  </context>
  <context>
    <name>SavePNGDialog</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="141"/>
      <source>Export as PNG</source>
      <comment>File dialog window title</comment>
      <translation>Export as PNG</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="142"/>
      <source>PNG images (*.png)</source>
      <comment>File type filter</comment>
      <translation>PNG images (*.png)</translation>
    </message>
  </context>
  <context>
    <name>ScryfallCSVParser</name>
    <message>
      <location filename="../../mtg_proxy_printer/decklist_parser/csv_parsers.py" line="117"/>
      <source>Scryfall CSV export</source>
      <translation>Scryfall CSV export</translation>
    </message>
  </context>
  <context>
    <name>SelectDeckParserPage</name>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="14"/>
      <source>Import a deck list for printing</source>
      <translation>Import a deck list for printing</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="17"/>
      <source>Select which kind of deck list you want to import.</source>
      <translation>Select which kind of deck list you want to import.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="26"/>
      <source>This is a Tappedout-specific section of the deck.
It may contain the deck list author’s buy-list or anything else.</source>
      <translation>This is a Tappedout-specific section of the deck.
It may contain the deck list author’s buy-list or anything else.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="30"/>
      <source>Include “Acquire-Board”</source>
      <translation>Include “Acquire-Board”</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="53"/>
      <source>A simple list, containing one card name per line</source>
      <translation>A simple list, containing one card name per line</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="56"/>
      <source>List with card names</source>
      <translation>List with card names</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="92"/>
      <source>CSV exports from Scryfall’s own deck builder.
Gives very accurate results, unless the imported deck list contains ignored items
matching an enabled card filter.</source>
      <translation>CSV exports from Scryfall’s own deck builder.
Gives very accurate results, unless the imported deck list contains ignored items
matching an enabled card filter.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="97"/>
      <source>Scryfall.com deck lists (CSV export)</source>
      <translation>Scryfall.com deck lists (CSV export)</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="104"/>
      <source>Deck list files, stored in XMage’s native format.
Because XMage closely follows Scryfall regarding Magic sets,
this should give very accurate results.</source>
      <translation>Deck list files, stored in XMage’s native format.
Because XMage closely follows Scryfall regarding Magic sets,
this should give very accurate results.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="109"/>
      <source>XMage</source>
      <translation>XMage</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="116"/>
      <source>Specify a custom regular expression in the input field below. It will be used to parse each deck list line.
You can use the buttons below to insert basic building blocks.
You have to separate them with the “control structures”, like spaces, as used in your deck list.</source>
      <translation>Specify a custom regular expression in the input field below. It will be used to parse each deck list line.
You can use the buttons below to insert basic building blocks.
You have to separate them with the “control structures”, like spaces, as used in your deck list.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="121"/>
      <source>Custom regular expression based parser:</source>
      <translation>Custom regular expression based parser:</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="128"/>
      <source>CSV exports can be downloaded from Tappedout by choosing the appropriate deck export option.</source>
      <translation>CSV exports can be downloaded from Tappedout by choosing the appropriate deck export option.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="131"/>
      <source>tappedout.net deck list (CSV export)</source>
      <translation>tappedout.net deck list (CSV export)</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="138"/>
      <source>The simplistic format used by Magic Online. It does not specify exact printings, so may not give the best results.</source>
      <translation>The simplistic format used by Magic Online. It does not specify exact printings, so may not give the best results.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="141"/>
      <source>Magic Online</source>
      <translation>Magic Online</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="148"/>
      <source>Magic Workstation Deck Data (mwDeck)</source>
      <translation>Magic Workstation Deck Data (mwDeck)</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="155"/>
      <source>Magic Arena and exports from compatible websites, like moxfield.com
Note that this option is not limited to cards in Standard/Historic,
as the format works for any card.</source>
      <translation>Magic Arena and exports from compatible websites, like moxfield.com
Note that this option is not limited to cards in Standard/Historic,
as the format works for any card.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="160"/>
      <source>MTG Arena</source>
      <translation>MTG Arena</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="170"/>
      <source>This is a Tappedout-specific section of the deck.
It may contain cards that the deck list creator considers for inclusion, based on the meta
or any other preference, like card price.</source>
      <translation>This is a Tappedout-specific section of the deck.
It may contain cards that the deck list creator considers for inclusion, based on the meta
or any other preference, like card price.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="175"/>
      <source>Include “Maybe-Board”</source>
      <translation>Include “Maybe-Board”</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="200"/>
      <source>Appends a matcher for a card name to the input field above.</source>
      <translation>Appends a matcher for a card name to the input field above.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="203"/>
      <source>Card name matcher</source>
      <translation>Card name matcher</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="213"/>
      <source>Appends a sample matcher for a collector number to the input field above</source>
      <translation>Appends a sample matcher for a collector number to the input field above</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="216"/>
      <source>Collector number matcher</source>
      <translation>Collector number matcher</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="226"/>
      <source>Appends a matcher for the  card language to the input field above.
If a language field is not present in the deck list, the card language is guessed.</source>
      <translation>Appends a matcher for the  card language to the input field above.
If a language field is not present in the deck list, the card language is guessed.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="230"/>
      <source>Language matcher</source>
      <translation>Language matcher</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="240"/>
      <source>Appends a sample matcher for a set code to the input field above.</source>
      <translation>Appends a sample matcher for a set code to the input field above.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="243"/>
      <source>Set code matcher</source>
      <translation>Set code matcher</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="253"/>
      <source>Appends a matcher for the number of card copies to the input field above.
If a card count field is not present in the deck list, 1 card copy per line is assumed</source>
      <translation>Appends a matcher for the number of card copies to the input field above.
If a card count field is not present in the deck list, 1 card copy per line is assumed</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="257"/>
      <source>Copies matcher</source>
      <translation>Copies matcher</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="267"/>
      <source>Appends a matcher for the Scryfall ID to the input field above.
This may be used by deck lists that closely integrate with the Scryfall website.
Most deck lists won’t use this.</source>
      <translation>Appends a matcher for the Scryfall ID to the input field above.
This may be used by deck lists that closely integrate with the Scryfall website.
Most deck lists won’t use this.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="272"/>
      <source>Scryfall ID matcher</source>
      <translation>Scryfall ID matcher</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="282"/>
      <source>Enter a Regular Expression containing at least one supported, named group.

Supported named groups are: {group_names}

See the &apos;What’s this?&apos; (?-Button) help for details.</source>
      <translation>Enter a Regular Expression containing at least one supported, named group.

Supported named groups are: {group_names}

See the &apos;What’s this?&apos; (?-Button) help for details.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="289"/>
      <source>You can enter a custom Regular Expression (in Python syntax) to parse the lines of your deck list. Use *named groups* to extract the individual card properties from the individual lines of the deck list.
A named group looks like this:
**(?P\&lt;GroupName&gt;RE)**, where RE is a Regular Expression matching the part you want to extract, and GroupName is one of the following:

- `copies`: The number of card copies. Defaults to 1, if not present
- `name`: The card name
- `set_code`: The 3 (or more) letter code identifying the set
- `collector_number`: The collector number of the card
- `language`: The card language, using a two-letter language code. If not given, the importer tries to determine the language from the card name. Defaults to &quot;en&quot; for English, if not possible.

Not all groups are required for a successful match. For example, `set_code` and `collector_number` is sufficient for exact identification most of the time.
Hint: You may want to use an online Regular Expression editor, like [](https://regex101.com/), for example.</source>
      <translation>You can enter a custom Regular Expression (in Python syntax) to parse the lines of your deck list. Use *named groups* to extract the individual card properties from the individual lines of the deck list.
A named group looks like this:
**(?P\&lt;GroupName&gt;RE)**, where RE is a Regular Expression matching the part you want to extract, and GroupName is one of the following:

- `copies`: The number of card copies. Defaults to 1, if not present
- `name`: The card name
- `set_code`: The 3 (or more) letter code identifying the set
- `collector_number`: The collector number of the card
- `language`: The card language, using a two-letter language code. If not given, the importer tries to determine the language from the card name. Defaults to &quot;en&quot; for English, if not possible.

Not all groups are required for a successful match. For example, `set_code` and `collector_number` is sufficient for exact identification most of the time.
Hint: You may want to use an online Regular Expression editor, like [](https://regex101.com/), for example.</translation>
    </message>
  </context>
  <context>
    <name>SetEditor</name>
    <message>
      <location filename="../ui/set_editor_widget.ui" line="35"/>
      <source>Set name</source>
      <translation>Set name</translation>
    </message>
    <message>
      <location filename="../ui/set_editor_widget.ui" line="61"/>
      <source>CODE</source>
      <translation>CODE</translation>
    </message>
  </context>
  <context>
    <name>SettingsWindow</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="201"/>
      <source>Apply settings to the current document?</source>
      <translation>Apply settings to the current document?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="203"/>
      <source>The new default settings differ from the settings used by the current document.
Apply the new settings to the current document?</source>
      <translation>The new default settings differ from the settings used by the current document.
Apply the new settings to the current document?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="215"/>
      <source>Reset unsaved changes?</source>
      <translation>Reset unsaved changes?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="216"/>
      <source>Reset unsaved changes on the current page or on all pages?</source>
      <translation>Reset unsaved changes on the current page or on all pages?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="219"/>
      <source>Reset everything</source>
      <translation>Reset everything</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="220"/>
      <source>Reset current page</source>
      <translation>Reset current page</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="249"/>
      <source>Restore defaults for the current page or everything?</source>
      <translation>Restore defaults for the current page or everything?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="250"/>
      <source>Restore the settings on the current page or on all pages to their default values?</source>
      <translation>Restore the settings on the current page or on all pages to their default values?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="253"/>
      <source>Restore everything</source>
      <translation>Restore everything</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="254"/>
      <source>Restore current page</source>
      <translation>Restore current page</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/settings_window.ui" line="17"/>
      <source>Settings</source>
      <translation>Settings</translation>
    </message>
  </context>
  <context>
    <name>SummaryPage</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="461"/>
      <source>Images about to be deleted: {count}</source>
      <translation>Images about to be deleted: {count}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="462"/>
      <source>Disk space that will be freed: {disk_space_freed}</source>
      <translation>Disk space that will be freed: {disk_space_freed}</translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="504"/>
      <source>Beware: The card list currently contains %n potentially oversized card(s).</source>
      <comment>Warning emitted, if at least 1 card has the oversized flag set. The Scryfall server *may* still return a regular-sized image, so not *all* printings marked as oversized are actually so when fetched.</comment>
      <translation>
        <numerusform>Beware: The card list currently contains a potentially oversized card.</numerusform>
        <numerusform>Beware: The card list currently contains %n potentially oversized cards.</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="511"/>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="529"/>
      <source>Replace document content with the identified cards</source>
      <comment>Wizard Accept button tooltip, if replacing the document with the loaded list is enabled.</comment>
      <translation>Replace document content with the identified cards</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="517"/>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="535"/>
      <source>Append identified cards to the document</source>
      <comment>Wizard Accept button tooltip, if replacing the document with the loaded list is disabled.</comment>
      <translation>Append identified cards to the document</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="571"/>
      <source>Remove basic lands</source>
      <comment>Button text</comment>
      <translation>Remove basic lands</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="573"/>
      <source>Remove all basic lands in the deck list above</source>
      <comment>Button tooltip</comment>
      <translation>Remove all basic lands in the deck list above</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="579"/>
      <source>Remove selected</source>
      <comment>Button text. Clicking removes all selected cards in the table</comment>
      <translation>Remove selected</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="581"/>
      <source>Remove all selected cards in the deck list above</source>
      <comment>Button tooltip</comment>
      <translation>Remove all selected cards in the deck list above</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/summary_page.ui" line="14"/>
      <source>Summary</source>
      <translation>Summary</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="6"/>
      <source>Import a deck list for printing</source>
      <translation>Import a deck list for printing</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="9"/>
      <source>The cards shown in the table will be imported. Double-click the Set, Collector# or Language cells to change selected printings. The text field shows all lines from the input that were not identified as cards.</source>
      <translation>The cards shown in the table will be imported. Double-click the Set, Collector# or Language cells to change selected printings. The text field shows all lines from the input that were not identified as cards.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="15"/>
      <source>If checked, clear all cards in the current document, replacing everything with the list below.
If unchecked, append the cards found below to the document.</source>
      <translation>If checked, clear all cards in the current document, replacing everything with the list below.
If unchecked, append the cards found below to the document.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="19"/>
      <source>Replace the current document content with the found cards</source>
      <translation>Replace the current document content with the found cards</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="29"/>
      <source>These cards were successfully identified:</source>
      <translation>These cards were successfully identified:</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="61"/>
      <source>These lines from the deck list were not identified as cards:</source>
      <translation>These lines from the deck list were not identified as cards:</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="83"/>
      <source>Nothing. All cards were successfully identified!</source>
      <translation>Nothing. All cards were successfully identified!</translation>
    </message>
  </context>
  <context>
    <name>TabbedCentralWidget</name>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="33"/>
      <source>All pages</source>
      <translation>All pages</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="54"/>
      <source>Move up</source>
      <translation>Move up</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="67"/>
      <source>Move down</source>
      <translation>Move down</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="88"/>
      <source>Add new cards</source>
      <translation>Add new cards</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="93"/>
      <source>Current page</source>
      <translation>Current page</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="145"/>
      <source>Remove selected</source>
      <translation>Remove selected</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="156"/>
      <source>Preview</source>
      <translation>Preview</translation>
    </message>
  </context>
  <context>
    <name>TappedOutCSVParser</name>
    <message>
      <location filename="../../mtg_proxy_printer/decklist_parser/csv_parsers.py" line="196"/>
      <source>Tappedout CSV export</source>
      <translation>Tappedout CSV export</translation>
    </message>
  </context>
  <context>
    <name>UnknownCardImageModel</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="275"/>
      <source>Scryfall ID</source>
      <comment>Table header. Shows UUID identifying this card in the Scryfall database</comment>
      <translation>Scryfall ID</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="277"/>
      <source>Front/Back</source>
      <comment>Table header. Shows if this is the front or back side of a card</comment>
      <translation>Front/Back</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="279"/>
      <source>High resolution?</source>
      <comment>Table header. Shows if the card has high-res images</comment>
      <translation>High resolution?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="281"/>
      <source>Size</source>
      <comment>Table header. File size in KiB/MiB</comment>
      <translation>Size</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="283"/>
      <source>Path</source>
      <comment>Table header. File system path</comment>
      <translation>Path</translation>
    </message>
  </context>
  <context>
    <name>UnknownCardRow</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="245"/>
      <source>Front</source>
      <comment>Magic card side</comment>
      <translation>Front</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="247"/>
      <source>Back</source>
      <comment>Magic card side</comment>
      <translation>Back</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="253"/>
      <source>Yes</source>
      <comment>Card has high-resolution images available</comment>
      <translation>Yes</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="255"/>
      <source>No</source>
      <comment>Card only has low-resolution images available</comment>
      <translation>No</translation>
    </message>
  </context>
  <context>
    <name>VerticalAddCardWidget</name>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="26"/>
      <source>The sets in which the currently selected card was printed.</source>
      <translation>The sets in which the currently selected card was printed.</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="29"/>
      <source>Set</source>
      <translation>Set</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="35"/>
      <source>Filter set names</source>
      <translation>Filter set names</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="67"/>
      <source>Collector Number</source>
      <translation>Collector Number</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="92"/>
      <source>Card Name</source>
      <translation>Card Name</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="98"/>
      <source>Filter the list below. Use  % (Percent signs) as wildcards matching any number of characters.</source>
      <translation>Filter the list below. Use  % (Percent signs) as wildcards matching any number of characters.</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="101"/>
      <source>Filter card names</source>
      <translation>Filter card names</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="111"/>
      <source>The filtered list of card names in the currently selected language. Click on an entry to select it and choose a printing.</source>
      <translation>The filtered list of card names in the currently selected language. Click on an entry to select it and choose a printing.</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="136"/>
      <source>Language:</source>
      <extracomment>Card language. Next to the language selection widget</extracomment>
      <translation>Language:</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="152"/>
      <source>Copies:</source>
      <extracomment>Number of copies to add. Next to the number input field</extracomment>
      <translation>Copies:</translation>
    </message>
  </context>
  <context>
    <name>XMageParser</name>
    <message>
      <location filename="../../mtg_proxy_printer/decklist_parser/re_parsers.py" line="258"/>
      <source>XMage Deck file</source>
      <translation>XMage Deck file</translation>
    </message>
  </context>
  <context>
    <name>export_pdf</name>
    <message>
      <location filename="../../mtg_proxy_printer/print.py" line="132"/>
      <source>Write PDF:</source>
      <comment>Progress label</comment>
      <translation>Write PDF:</translation>
    </message>
  </context>
  <context>
    <name>format_size</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/common.py" line="185"/>
      <source>{size} {unit}</source>
      <comment>A formatted file size in SI bytes</comment>
      <translation>{size} {unit}</translation>
    </message>
  </context>
</TS>
