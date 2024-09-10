<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="en-US" sourcelanguage="en-US">
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
      <location filename="../ui/about_dialog.ui" line="59"/>
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

</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="84"/>
      <source>Python runtime version</source>
      <translation>Python runtime version</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="94"/>
      <source>Python Version:</source>
      <translation>Python Version:</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="101"/>
      <source>Application Version:</source>
      <translation>Application Version:</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="134"/>
      <source>Application version</source>
      <translation>Application version</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="153"/>
      <source>Last card update:</source>
      <translation>Last card update:</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="173"/>
      <source>Changelog</source>
      <translation>Changelog</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="187"/>
      <source>License</source>
      <translation>License</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="198"/>
      <source>Third party licenses</source>
      <translation>Third Party licenses</translation>
    </message>
  </context>
  <context>
    <name>ActionAddCard</name>
    <message numerus="yes">
      <location filename="../../document_controller/card_actions.py" line="158"/>
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
      <location filename="../../document_controller/compact_document.py" line="108"/>
      <source>Compact document, removing %n page(s)</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>
        <numerusform>Compact document, removing %n page</numerusform>
        <numerusform>Compact document, removing %n pages</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionEditDocumentSettings</name>
    <message>
      <location filename="../../document_controller/edit_document_settings.py" line="132"/>
      <source>Update document settings</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Update document settings</translation>
    </message>
  </context>
  <context>
    <name>ActionImportDeckList</name>
    <message numerus="yes">
      <location filename="../../document_controller/import_deck_list.py" line="72"/>
      <source>Wipe document and import a deck list containing %n card(s)</source>
      <comment>Undo/redo tooltip text. Option to delete the current document enabled.</comment>
      <translation>
        <numerusform>Wipe document and import a deck list containing %n card</numerusform>
        <numerusform>Wipe document and import a deck list containing %n cards</numerusform>
      </translation>
    </message>
    <message numerus="yes">
      <location filename="../../document_controller/import_deck_list.py" line="77"/>
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
      <location filename="../../document_controller/load_document.py" line="75"/>
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
    <name>ActionLoadDocument. Card total</name>
    <message numerus="yes">
      <location filename="../../document_controller/load_document.py" line="71"/>
      <source>with %n card(s) total</source>
      <comment>Undo/redo tooltip text. Will be inserted as {cards_total}</comment>
      <translation>
        <numerusform>with %n card total</numerusform>
        <numerusform>with %n cards total</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionMoveCards</name>
    <message numerus="yes">
      <location filename="../../document_controller/move_cards.py" line="139"/>
      <source>Move %n card(s) from page {source_page} to {target_page}</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>
        <numerusform>Move %n card from page {source_page} to {target_page}</numerusform>
        <numerusform>Move %n cards from page {source_page} to {target_page}</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionNewDocument</name>
    <message>
      <location filename="../../document_controller/new_document.py" line="68"/>
      <source>Create new document</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Create new document</translation>
    </message>
  </context>
  <context>
    <name>ActionNewPage</name>
    <message numerus="yes">
      <location filename="../../document_controller/page_actions.py" line="81"/>
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
      <location filename="../../document_controller/card_actions.py" line="216"/>
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
      <location filename="../../document_controller/page_actions.py" line="181"/>
      <source>%n card(s) total</source>
      <comment>Undo/redo tooltip text. The total number of cards removed. Used as {formatted_card_count}</comment>
      <translation>
        <numerusform>%n card total</numerusform>
        <numerusform>%n cards total</numerusform>
      </translation>
    </message>
    <message numerus="yes">
      <location filename="../../document_controller/page_actions.py" line="187"/>
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
      <location filename="../../document_controller/replace_card.py" line="98"/>
      <source>Replace card {old_card} on page {page_number} with {new_card}</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Replace card {old_card} on page {page_number} with {new_card}</translation>
    </message>
  </context>
  <context>
    <name>ActionShuffleDocument</name>
    <message>
      <location filename="../../document_controller/shuffle_document.py" line="101"/>
      <source>Shuffle document</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Shuffle document</translation>
    </message>
  </context>
  <context>
    <name>CacheCleanupWizard</name>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="471"/>
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
    <name>CardInfoDatabaseImportWorker</name>
    <message>
      <location filename="../../card_info_downloader.py" line="369"/>
      <source>Error during import from file:
{path}</source>
      <translation>Error during import from file:
{path}</translation>
    </message>
    <message>
      <location filename="../../card_info_downloader.py" line="380"/>
      <source>Updating card data from Scryfall:</source>
      <comment>Progress bar label text</comment>
      <translation>Updating card data from Scryfall:</translation>
    </message>
    <message>
      <location filename="../../card_info_downloader.py" line="390"/>
      <source>Reading from socket failed: {error}</source>
      <translation>Reading from socket failed: {error}</translation>
    </message>
    <message>
      <location filename="../../card_info_downloader.py" line="426"/>
      <source>Importing card data from disk:</source>
      <comment>Progress bar label text</comment>
      <translation>Importing card data from disk:</translation>
    </message>
    <message>
      <location filename="../../card_info_downloader.py" line="446"/>
      <source>Failed to parse data from Scryfall. Reported error: {error}</source>
      <translation>Failed to parse data from Scryfall. Reported error: {error}</translation>
    </message>
    <message>
      <location filename="../../card_info_downloader.py" line="490"/>
      <source>Post-processing card data:</source>
      <translation>Post-processing card data:</translation>
    </message>
  </context>
  <context>
    <name>CardInfoFileDownloadWorker</name>
    <message>
      <location filename="../../card_info_downloader.py" line="186"/>
      <source>Downloading card data:</source>
      <comment>Progress bar label text</comment>
      <translation>Downloading card data:</translation>
    </message>
  </context>
  <context>
    <name>CardListModel</name>
    <message>
      <location filename="../../model/card_list.py" line="59"/>
      <source>Card name</source>
      <translation>Card name</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="60"/>
      <source>Set</source>
      <translation>Set</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="61"/>
      <source>Collector #</source>
      <translation>Collector #</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="62"/>
      <source>Language</source>
      <translation>Language</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="63"/>
      <source>Side</source>
      <translation>Side</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="95"/>
      <source>Front</source>
      <translation>Front</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="95"/>
      <source>Back</source>
      <translation>Back</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="98"/>
      <source>Beware: Potentially oversized card!
This card may not fit in your deck.</source>
      <translation>Beware: Potentially oversized card!
This card may not fit in your deck.</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="236"/>
      <source>Double-click on entries to
switch the selected printing.</source>
      <translation>Double-click on entries to
switch the selected printing.</translation>
    </message>
  </context>
  <context>
    <name>CentralWidget</name>
    <message numerus="yes">
      <location filename="../../ui/central_widget.py" line="154"/>
      <source>Add %n copies</source>
      <comment>Context menu action: Add additional card copies to the document</comment>
      <translation>
        <numerusform>Add %n copy</numerusform>
        <numerusform>Add %n copies</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../ui/central_widget.py" line="160"/>
      <source>Add copies …</source>
      <comment>Context menu action: Add additional card copies to the document. User will be asked for a number</comment>
      <translation>Add copies …</translation>
    </message>
    <message>
      <location filename="../../ui/central_widget.py" line="166"/>
      <source>Generate DFC check card</source>
      <translation>Generate DFC check card</translation>
    </message>
    <message>
      <location filename="../../ui/central_widget.py" line="170"/>
      <source>All related cards</source>
      <translation>All related cards</translation>
    </message>
    <message>
      <location filename="../../ui/central_widget.py" line="178"/>
      <source>Add copies</source>
      <translation>Add copies</translation>
    </message>
    <message>
      <location filename="../../ui/central_widget.py" line="178"/>
      <source>Add copies of {card_name}</source>
      <comment>Asks the user for a number. Does not need plural forms</comment>
      <translation>Add copies of {card_name}</translation>
    </message>
    <message>
      <location filename="../../ui/central_widget.py" line="204"/>
      <source>Export image</source>
      <translation>Export image</translation>
    </message>
    <message>
      <location filename="../../ui/central_widget.py" line="219"/>
      <source>Save card image</source>
      <translation>Save card image</translation>
    </message>
    <message>
      <location filename="../../ui/central_widget.py" line="219"/>
      <source>Images (*.png *.bmp *.jpg)</source>
      <translation>Images (*.png *.bmp *.jpg)</translation>
    </message>
  </context>
  <context>
    <name>ColumnarCentralWidget</name>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="64"/>
      <source>All pages:</source>
      <translation>All pages:</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="71"/>
      <source>Current page:</source>
      <translation>Current page:</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="81"/>
      <source>Remove selected</source>
      <translation>Remove selected</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="91"/>
      <source>Add new cards:</source>
      <translation>Add new cards:</translation>
    </message>
  </context>
  <context>
    <name>DebugSettingsPage</name>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="118"/>
      <source>Debug settings</source>
      <translation>Debug settings</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="118"/>
      <source>Things useful for investigating bugs in the application</source>
      <translation>Things useful for investigating bugs in the application</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="173"/>
      <source>Select download location</source>
      <translation>Select download location</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="181"/>
      <source>Selected location is not a directory</source>
      <translation>Selected location is not a directory</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="181"/>
      <source>Cannot write the card data at the given location, because it is not a directory:
{location}</source>
      <translation>Cannot write the card data at the given location, because it is not a directory:
{location}</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="194"/>
      <source>Import previously downloaded card data obtained from Scryfall</source>
      <translation>Import previously downloaded card data obtained from Scryfall</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="194"/>
      <source>Scryfall card data (*.json, *.json.gz)</source>
      <translation>Scryfall card data (*.json, *.json.gz)</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="204"/>
      <source>Selected location is not a file</source>
      <translation>Selected location is not a file</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="204"/>
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
      <location filename="../ui/settings_window/debug_settings_page.ui" line="28"/>
      <source>Enable writing a log file to disk</source>
      <translation>Enable writing a log file to disk</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="35"/>
      <source>Cutelog is a live log event viewer that can be used to monitor events in real-time.</source>
      <translation>Cutelog is a live log event viewer that can be used to monitor events in real-time.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="38"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;See &lt;a href=&quot;https://github.com/busimus/cutelog&quot;&gt;&lt;span style=&quot; text-decoration: underline; color:#2980b9;&quot;&gt;https://github.com/busimus/cutelog&lt;/span&gt;&lt;/a&gt; for details about Cutelog.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;See &lt;a href=&quot;https://github.com/busimus/cutelog&quot;&gt;&lt;span style=&quot; text-decoration: underline; color:#2980b9;&quot;&gt;https://github.com/busimus/cutelog&lt;/span&gt;&lt;/a&gt; for details about Cutelog.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="41"/>
      <source>Enable Cutelog integration</source>
      <translation>Enable Cutelog integration</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="48"/>
      <source>Download card data as file</source>
      <translation>Download card data as file</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="66"/>
      <source>Event severity that gets logged to file:</source>
      <translation>Event severity that gets logged to file:</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="76"/>
      <source>Only write events with the given severity level and higher to the log file.</source>
      <translation>Only write events with the given severity level and higher to the log file.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="83"/>
      <source>Debug settings (Changing these require an application restart)</source>
      <translation>Debug settings (Changing these require an application restart)</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="103"/>
      <source>Import card data from file</source>
      <translation>Import card data from file</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="120"/>
      <source>Open the Cutelog homepage</source>
      <translation>Open the Cutelog homepage</translation>
    </message>
  </context>
  <context>
    <name>DeckImportWizard</name>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="618"/>
      <source>Import a deck list</source>
      <translation>Import a deck list</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="639"/>
      <source>Oversized cards present</source>
      <translation>Oversized cards present</translation>
    </message>
    <message numerus="yes">
      <location filename="../../ui/deck_import_wizard.py" line="639"/>
      <source>There are %n possibly oversized cards in the deck list that may not fit into a deck, when printed out.

Continue and use these cards as-is?</source>
      <translation>
        <numerusform>There is %n possibly oversized card in the deck list that may not fit into a deck, when printed out.

Continue and use the card as-is?</numerusform>
        <numerusform>There are %n possibly oversized cards in the deck list that may not fit into a deck, when printed out.

Continue and use these cards as-is?</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="650"/>
      <source>Incompatible file selected</source>
      <translation>Incompatible file selected</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="650"/>
      <source>Unable to parse the given deck list, no results were obtained.
Maybe you selected the wrong deck list type?</source>
      <translation>Unable to parse the given deck list, no results were obtained.
Maybe you selected the wrong deck list type?</translation>
    </message>
  </context>
  <context>
    <name>DecklistImportSettingsPage</name>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="217"/>
      <source>Deck list import</source>
      <translation>Deck list import</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="217"/>
      <source>Configure the deck list importer</source>
      <translation>Configure the deck list importer</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="227"/>
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
      <location filename="../../ui/settings_window_pages.py" line="474"/>
      <source>Default document settings</source>
      <translation>Default document settings</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="474"/>
      <source>Set the default document settings used for new documents,
like page size, margins, spacings, etc.</source>
      <translation>Set the default document settings used for new documents,
like page size, margins, spacings, etc.</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="482"/>
      <source>Default settings for new documents</source>
      <translation>Default settings for new documents</translation>
    </message>
  </context>
  <context>
    <name>Document</name>
    <message>
      <location filename="../../model/document.py" line="90"/>
      <source>Card name</source>
      <translation>Card name</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="91"/>
      <source>Set</source>
      <translation>Set</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="92"/>
      <source>Collector #</source>
      <translation>Collector #</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="93"/>
      <source>Language</source>
      <translation>Language</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="94"/>
      <source>Image</source>
      <translation>Image</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="95"/>
      <source>Side</source>
      <translation>Side</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="173"/>
      <source>Double-click on entries to
switch the selected printing.</source>
      <translation>Double-click on entries to
switch the selected printing.</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="282"/>
      <source>Page {current}/{total}</source>
      <translation>Page {current}/{total}</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="311"/>
      <source>Front</source>
      <translation>Front</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="311"/>
      <source>Back</source>
      <translation>Back</translation>
    </message>
    <message numerus="yes">
      <location filename="../../model/document.py" line="316"/>
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
      <location filename="../../document_controller/_interface.py" line="104"/>
      <source>{first}-{last}</source>
      <comment>Inclusive, formatted number range, from first to last</comment>
      <translation>{first}-{last}</translation>
    </message>
  </context>
  <context>
    <name>DocumentSettingsDialog</name>
    <message>
      <location filename="../../ui/dialogs.py" line="320"/>
      <source>These settings only affect the current document</source>
      <translation>These settings only affect the current document</translation>
    </message>
    <message>
      <location filename="../ui/document_settings_dialog.ui" line="14"/>
      <source>Set Document settings</source>
      <translation>Set Document settings</translation>
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
    <name>FormatPrintingFilter</name>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="14"/>
      <source>Hide cards banned in specific Formats</source>
      <translation>Hide cards banned in specific Formats</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="20"/>
      <source>Pioneer</source>
      <translation>Pioneer</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="27"/>
      <source>Modern</source>
      <translation>Modern</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="34"/>
      <source>Historic</source>
      <translation>Historic</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="41"/>
      <source>Vintage</source>
      <translation>Vintage</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="257"/>
      <source>View cards hidden by this filter on the Scryfall website.</source>
      <translation>View cards hidden by this filter on the Scryfall website.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="64"/>
      <source>Penny</source>
      <translation>Penny</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="71"/>
      <source>Standard</source>
      <translation>Standard</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="94"/>
      <source>Pauper</source>
      <translation>Pauper</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="101"/>
      <source>Commander</source>
      <translation>Commander</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="140"/>
      <source>Brawl</source>
      <translation>Brawl</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="227"/>
      <source>Legacy</source>
      <translation>Legacy</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="250"/>
      <source>Oathbreaker</source>
      <translation>Oathbreaker</translation>
    </message>
  </context>
  <context>
    <name>GeneralPrintingFilter</name>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="14"/>
      <source>General printing filters</source>
      <translation>General printing filters</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="327"/>
      <source>View cards hidden by this filter on the Scryfall website.</source>
      <translation>View cards hidden by this filter on the Scryfall website.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="71"/>
      <source>Hide cards without a defined, solid-color border.
Those require higher cutting precision to get right.</source>
      <translation>Hide cards without a defined, solid-color border.
Those require higher cutting precision to get right.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="75"/>
      <source>Hide borderless cards</source>
      <translation>Hide borderless cards</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="82"/>
      <source>Hide Token cards</source>
      <translation>Hide Token cards</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="105"/>
      <source>Some single-sided cards are re-printed as two-sided, reversible cards in some Secret Lair releases.
This filter hides those.</source>
      <translation>Some single-sided cards are re-printed as two-sided, reversible cards in some Secret Lair releases.
This filter hides those.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="109"/>
      <source>Hide reversible cards</source>
      <translation>Hide reversible cards</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="148"/>
      <source>Hide cards and printings that are only available on digital platforms. This includes all kinds of digital printings.</source>
      <translation>Hide cards and printings that are only available on digital platforms. This includes all kinds of digital printings.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="151"/>
      <source>Hide digital cards</source>
      <translation>Hide digital cards</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="158"/>
      <source>“Funny” cards, not legal in any constructed format.
This includes full-art Contraptions from Unstable,
cards with acorn-shaped security stamps from Unfinity (and newer Un-Sets),
some black-bordered promotional cards with non-standard back faces,
and all silver-bordered cards.</source>
      <translation>“Funny” cards, not legal in any constructed format.
This includes full-art Contraptions from Unstable,
cards with acorn-shaped security stamps from Unfinity (and newer Un-Sets),
some black-bordered promotional cards with non-standard back faces,
and all silver-bordered cards.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="165"/>
      <source>Hide “funny” cards</source>
      <translation>Hide “funny” cards</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="172"/>
      <source>These cards are larger than regular Magic cards and can’t be included in decks.
Includes Archenemy schemes, Planechase planes and
oversized commander creature or Planeswalker cards included in some pre-constructed Commander decks.</source>
      <translation>These cards are larger than regular Magic cards and can’t be included in decks.
Includes Archenemy schemes, Planechase planes and
oversized commander creature or Planeswalker cards included in some pre-constructed Commander decks.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="177"/>
      <source>Hide oversized cards</source>
      <translation>Hide oversized cards</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="184"/>
      <source>Some “collectible” sets, like full reprints of tournament-winning decks were printed with golden borders.
Many also have printed signatures of the involved players in the text box.

These are not tournament legal</source>
      <translation>Some “collectible” sets, like full reprints of tournament-winning decks were printed with golden borders.
Many also have printed signatures of the involved players in the text box.

These are not tournament legal</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="190"/>
      <source>Hide gold-bordered cards</source>
      <translation>Hide gold-bordered cards</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="197"/>
      <source>Hide white-bordered cards</source>
      <translation>Hide white-bordered cards</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="204"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Hide cards banned for depicting racism.&lt;/p&gt;&lt;p&gt;Background:&lt;/p&gt;&lt;p&gt;Some cards were banned by Wizards of the Coast, because they depict references to controversial real-world events, religion or contain combinations of card effect, name and artwork that, when viewed together, depict racism. These cards are banned in all sanctioned tournament formats and several community formats like Commander, Oathbreaker and others.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Hide cards banned for depicting racism.&lt;/p&gt;&lt;p&gt;Background:&lt;/p&gt;&lt;p&gt;Some cards were banned by Wizards of the Coast, because they depict references to controversial real-world events, religion or contain combinations of card effect, name and artwork that, when viewed together, depict racism. These cards are banned in all sanctioned tournament formats and several community formats like Commander, Oathbreaker and others.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="207"/>
      <source>Hide cards depicting racism</source>
      <translation>Hide cards depicting racism</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="230"/>
      <source>Hide non-English cards with low-resolution,
English placeholder images with an overlay text stating
“This card is not available in the selected language.”</source>
      <translation>Hide non-English cards with low-resolution,
English placeholder images with an overlay text stating
“This card is not available in the selected language.”</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="235"/>
      <source>Hide cards with placeholder images</source>
      <translation>Hide cards with placeholder images</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="300"/>
      <source>Hide cards with artwork extending to the left and right card border.
Similar to borderless cards, these require higher precision during the cutting process.</source>
      <translation>Hide cards with artwork extending to the left and right card border.
Similar to borderless cards, these require higher precision during the cutting process.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="304"/>
      <source>Hide extended art cards</source>
      <translation>Hide extended art cards</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="311"/>
      <source>Artwork cards that can be found in Set Boosters or Play Boosters</source>
      <translation>Artwork cards that can be found in Set Boosters or Play Boosters</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="314"/>
      <source>Hide Art Series cards</source>
      <translation>Hide Art Series cards</translation>
    </message>
  </context>
  <context>
    <name>GeneralSettingsPage</name>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="284"/>
      <source>General settings</source>
      <translation>General settings</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="291"/>
      <source>Horizontal layout</source>
      <translation>Horizontal layout</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="292"/>
      <source>Columnar layout</source>
      <translation>Columnar layout</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="293"/>
      <source>Tabbed layout</source>
      <translation>Tabbed layout</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="295"/>
      <source>System default</source>
      <translation>System default</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="296"/>
      <source>English (US)</source>
      <translation>English (US)</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="297"/>
      <source>German</source>
      <translation>German</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="308"/>
      <source>Select default save location</source>
      <translation>Select default save location</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="17"/>
      <source>Look &amp;&amp; Feel (Changing this requires an application restart)</source>
      <translation>Look &amp;&amp; Feel (Changing this requires an application restart)</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="29"/>
      <source>Horizontal adds a wide, horizontal search area above the currently edited page, and is best for taller screens, like 4:3 or 3:2.
Columnar organizes the main window content in four columns, and is best for (ultra-)wide screens.
Tabbed uses tabs to only show parts of the main window at a time. Best used with small screens in portrait mode (i.e. 9:16), otherwise not recommended.</source>
      <translation>Horizontal adds a wide, horizontal search area above the currently edited page, and is best for taller screens, like 4:3 or 3:2.
Columnar organizes the main window content in four columns, and is best for (ultra-)wide screens.
Tabbed uses tabs to only show parts of the main window at a time. Best used with small screens in portrait mode (i.e. 9:16), otherwise not recommended.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="38"/>
      <source>Main window layout</source>
      <translation>Main window layout</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="51"/>
      <source>Application language</source>
      <translation>Application language</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="67"/>
      <source>Language choices will default to the chosen language here.

Entries use the language codes as listed on Scryfall.</source>
      <translation>Language choices will default to the chosen language here.

Entries use the language codes as listed on Scryfall.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="76"/>
      <source>Double-faced cards</source>
      <translation>Double-faced cards</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="82"/>
      <source>When adding double-faced cards, automatically add the same number of copies of the other side.
Uses the appropriate, matching other card side.
Uncheck to disable this automatism.</source>
      <translation>When adding double-faced cards, automatically add the same number of copies of the other side.
Uses the appropriate, matching other card side.
Uncheck to disable this automatism.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="87"/>
      <source>Automatically add the other side of double-faced cards</source>
      <translation>Automatically add the other side of double-faced cards</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="97"/>
      <source>Preferred card language:</source>
      <translation>Preferred card language:</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="110"/>
      <source>Automatic update checks</source>
      <translation>Automatic update checks</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="116"/>
      <source>Update checks are performed at application start, if enabled.</source>
      <translation>Update checks are performed at application start, if enabled.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="123"/>
      <source>If enabled, check for application updates, and notify if new updates are available for installation.</source>
      <translation>If enabled, check for application updates, and notify if new updates are available for installation.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="126"/>
      <source>Check for application updates</source>
      <translation>Check for application updates</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="136"/>
      <source>If enabled, query the Scryfall API if new cards are available. If so, offer to update the local card data.</source>
      <translation>If enabled, query the Scryfall API if new cards are available. If so, offer to update the local card data.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="139"/>
      <source>Check for new card data</source>
      <translation>Check for new card data</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="152"/>
      <source>These paths are selected by default when browsing the file system for files</source>
      <translation>These paths are selected by default when browsing the file system for files</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="155"/>
      <source>Default save paths</source>
      <translation>Default save paths</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="161"/>
      <source>Browse…</source>
      <translation>Browse…</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="175"/>
      <source>Document save path</source>
      <translation>Document save path</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="185"/>
      <source>If set, use this as the default location for saving documents.</source>
      <translation>If set, use this as the default location for saving documents.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="191"/>
      <source>Path to a directory</source>
      <translation>Path to a directory</translation>
    </message>
  </context>
  <context>
    <name>GroupedCentralWidget</name>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="58"/>
      <source>Remove selected</source>
      <translation>Remove selected</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="106"/>
      <source>All pages:</source>
      <translation>All pages:</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="113"/>
      <source>Add new cards:</source>
      <translation>Add new cards:</translation>
    </message>
  </context>
  <context>
    <name>HidePrintingsPage</name>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="431"/>
      <source>Hide printings</source>
      <translation>Hide printings</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="431"/>
      <source>Hide unwanted printings</source>
      <translation>Hide unwanted printings</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/hide_printings_page.ui" line="17"/>
      <source>These options allow hiding unwanted cards and printings. Hidden printings are treated as though they don’t exist. They can’t be found in the card search and are automatically replaced in loaded documents or imported deck lists, if possible. If all printings of a card are hidden, it won’t be available at all.</source>
      <translation>These options allow hiding unwanted cards and printings. Hidden printings are treated as though they don’t exist. They can’t be found in the card search and are automatically replaced in loaded documents or imported deck lists, if possible. If all printings of a card are hidden, it won’t be available at all.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/hide_printings_page.ui" line="33"/>
      <source>Hide specific sets: Add set codes as listed on Scryfall, for example LEA or 2X2. Separate multiple entries with spaces or line breaks. All words not matching an exact set code are ignored.</source>
      <translation>Hide specific sets: Add set codes as listed on Scryfall, for example LEA or 2X2. Separate multiple entries with spaces or line breaks. All words not matching an exact set code are ignored.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/hide_printings_page.ui" line="43"/>
      <source>Example:

LEA DDU TC13 J21</source>
      <translation>Example:

LEA DDU TC13 J21</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/hide_printings_page.ui" line="51"/>
      <source>No sets currently hidden.</source>
      <translation>No sets currently hidden.</translation>
    </message>
  </context>
  <context>
    <name>HorizontalAddCardWidget</name>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="35"/>
      <source>Language:</source>
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
      <translation>Copies:</translation>
    </message>
  </context>
  <context>
    <name>ImageDownloader</name>
    <message>
      <location filename="../../model/imagedb.py" line="338"/>
      <source>Importing deck list</source>
      <comment>Progress bar label text</comment>
      <translation>Importing deck list</translation>
    </message>
    <message>
      <location filename="../../model/imagedb.py" line="358"/>
      <source>Fetching missing images</source>
      <comment>Progress bar label text</comment>
      <translation>Fetching missing images</translation>
    </message>
    <message>
      <location filename="../../model/imagedb.py" line="452"/>
      <source>Downloading &apos;{card_name}&apos;</source>
      <comment>Progress bar label text</comment>
      <translation>Downloading &apos;{card_name}&apos;</translation>
    </message>
  </context>
  <context>
    <name>KnownCardImageModel</name>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="146"/>
      <source>Name</source>
      <translation>Name</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="147"/>
      <source>Set</source>
      <translation>Set</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="148"/>
      <source>Collector #</source>
      <translation>Collector #</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="149"/>
      <source>Is Hidden</source>
      <translation>Is Hidden</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="150"/>
      <source>Front/Back</source>
      <translation>Front/Back</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="151"/>
      <source>High resolution?</source>
      <translation>High resolution?</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="152"/>
      <source>Size</source>
      <translation>Size</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="153"/>
      <source>Scryfall ID</source>
      <translation>Scryfall ID</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="154"/>
      <source>Path</source>
      <translation>Path</translation>
    </message>
  </context>
  <context>
    <name>KnownCardRow</name>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="125"/>
      <source>Yes</source>
      <translation>Yes</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="125"/>
      <source>No</source>
      <translation>No</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="113"/>
      <source>This printing is hidden by an enabled card filter
and is thus unavailable for printing.</source>
      <comment>Tooltip for cells with hidden cards</comment>
      <translation>This printing is hidden by an enabled card filter
and is thus unavailable for printing.</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="119"/>
      <source>Front</source>
      <comment>Card side</comment>
      <translation>Front</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="119"/>
      <source>Back</source>
      <comment>Card side</comment>
      <translation>Back</translation>
    </message>
  </context>
  <context>
    <name>LoadDocumentDialog</name>
    <message>
      <location filename="../../ui/dialogs.py" line="163"/>
      <source>Load MTGProxyPrinter document</source>
      <translation>Load MTGProxyPrinter document</translation>
    </message>
  </context>
  <context>
    <name>LoadListPage</name>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="120"/>
      <source>Supported websites:
{supported_sites}</source>
      <translation>Supported websites:
{supported_sites}</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="216"/>
      <source>Overwrite existing deck list?</source>
      <translation>Overwrite existing deck list?</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="170"/>
      <source>Selecting a file will overwrite the existing deck list. Continue?</source>
      <translation>Selecting a file will overwrite the existing deck list. Continue?</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="178"/>
      <source>Select deck file</source>
      <translation>Select deck file</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="188"/>
      <source>All files (*)</source>
      <translation>All files (*)</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="199"/>
      <source>All Supported </source>
      <translation>All Supported </translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="216"/>
      <source>Downloading a deck list will overwrite the existing deck list. Continue?</source>
      <translation>Downloading a deck list will overwrite the existing deck list. Continue?</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="229"/>
      <source>Download failed with HTTP error {http_error_code}.

{bad_request_msg}</source>
      <translation>Download failed with HTTP error {http_error_code}.

{bad_request_msg}</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="240"/>
      <source>Deck list download failed</source>
      <translation>Deck list download failed</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="235"/>
      <source>Download failed.

Check your internet connection, verify that the URL is valid, reachable, and that the deck list is set to public. This program cannot download private deck lists. If this persists, please report a bug in the issue tracker on the homepage.</source>
      <translation>Download failed.

Check your internet connection, verify that the URL is valid, reachable, and that the deck list is set to public. This program cannot download private deck lists. If this persists, please report a bug in the issue tracker on the homepage.</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="266"/>
      <source>Unable to read file content</source>
      <translation>Unable to read file content</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="266"/>
      <source>Unable to read the content of file {file_path} as plain text.
Failed to load the content.</source>
      <translation>Unable to read the content of file {file_path} as plain text.
Failed to load the content.</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="278"/>
      <source>Load large file?</source>
      <translation>Load large file?</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="278"/>
      <source>The selected file {file_path} is unexpectedly large ({formatted_size}). Load anyway?</source>
      <translation>The selected file {file_path} is unexpectedly large ({formatted_size}). Load anyway?</translation>
    </message>
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
      <translation>Select deck list file</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="152"/>
      <source>View result</source>
      <translation>View result</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="171"/>
      <source>Download deck list</source>
      <translation>Download deck list</translation>
    </message>
  </context>
  <context>
    <name>LoadSaveDialog</name>
    <message>
      <location filename="../../ui/dialogs.py" line="120"/>
      <source>MTGProxyPrinter document (*.{default_save_suffix})</source>
      <comment>Human-readable file type name</comment>
      <translation>MTGProxyPrinter document (*.{default_save_suffix})</translation>
    </message>
  </context>
  <context>
    <name>MTGArenaParser</name>
    <message>
      <location filename="../../decklist_parser/re_parsers.py" line="199"/>
      <source>Magic Arena deck file</source>
      <translation>Magic Arena deck file</translation>
    </message>
  </context>
  <context>
    <name>MTGOnlineParser</name>
    <message>
      <location filename="../../decklist_parser/re_parsers.py" line="233"/>
      <source>Magic Online (MTGO) deck file</source>
      <translation>Magic Online (MTGO) deck file</translation>
    </message>
  </context>
  <context>
    <name>MagicWorkstationDeckDataFormatParser</name>
    <message>
      <location filename="../../decklist_parser/re_parsers.py" line="177"/>
      <source>Magic Workstation Deck Data Format</source>
      <translation>Magic Workstation Deck Data Format</translation>
    </message>
  </context>
  <context>
    <name>MainWindow</name>
    <message>
      <location filename="../../ui/main_window.py" line="216"/>
      <source>Undo:
{top_entry}</source>
      <translation>Undo:
{top_entry}</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="218"/>
      <source>Redo:
{top_entry}</source>
      <translation>Redo:
{top_entry}</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="274"/>
      <source>printing</source>
      <comment>This is passed as the {action} when asking the user about compacting the document if that can save pages</comment>
      <translation>printing</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="286"/>
      <source>exporting as a PDF</source>
      <comment>This is passed as the {action} when asking the user about compacting the document if that can save pages</comment>
      <translation>exporting as a PDF</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="296"/>
      <source>Network error</source>
      <translation>Network error</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="296"/>
      <source>Operation failed, because a network error occurred.
Check your internet connection. Reported error message:

{message}</source>
      <translation>Operation failed, because a network error occurred.
Check your internet connection. Reported error message:

{message}</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="304"/>
      <source>Error</source>
      <translation>Error</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="304"/>
      <source>Operation failed, because an internal error occurred.
Reported error message:

{message}</source>
      <translation>Operation failed, because an internal error occurred.
Reported error message:

{message}</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="313"/>
      <source>Saving pages possible</source>
      <translation>Saving pages possible</translation>
    </message>
    <message numerus="yes">
      <location filename="../../ui/main_window.py" line="313"/>
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
      <location filename="../../ui/main_window.py" line="329"/>
      <source>Download required Card data from Scryfall?</source>
      <translation>Download required Card data from Scryfall?</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="329"/>
      <source>This program requires downloading additional card data from Scryfall to operate the card search.
Download the required data from Scryfall now?
Without the data, you can only print custom cards by drag&amp;dropping the image files onto the main window.</source>
      <translation>This program requires downloading additional card data from Scryfall to operate the card search.
Download the required data from Scryfall now?
Without the data, you can only print custom cards by drag&amp;dropping the image files onto the main window.</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="377"/>
      <source>Document loading failed</source>
      <translation>Document loading failed</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="377"/>
      <source>Loading file &quot;{failed_path}&quot; failed. The file was not recognized as a {program_name} document. If you want to load a deck list, use the &quot;{function_text}&quot; function instead.
Reported failure reason: {reason}</source>
      <translation>Loading file &quot;{failed_path}&quot; failed. The file was not recognized as a {program_name} document. If you want to load a deck list, use the &quot;{function_text}&quot; function instead.
Reported failure reason: {reason}</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="390"/>
      <source>Unavailable printings replaced</source>
      <translation>Unavailable printings replaced</translation>
    </message>
    <message numerus="yes">
      <location filename="../../ui/main_window.py" line="390"/>
      <source>The document contained %n unavailable printings of cards that were automatically replaced with other printings. The replaced printings are unavailable, because they match a configured card filter.</source>
      <translation>
        <numerusform>The document contained %n unavailable printing of a card that was automatically replaced with another printing. The replaced printing is unavailable, because it matches a configured card filter.</numerusform>
        <numerusform>The document contained %n unavailable printings of cards that were automatically replaced with other printings. The replaced printings are unavailable, because they match a configured card filter.</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="399"/>
      <source>Unrecognized cards in loaded document found</source>
      <translation>Unrecognized cards in loaded document found</translation>
    </message>
    <message numerus="yes">
      <location filename="../../ui/main_window.py" line="399"/>
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
      <location filename="../../ui/main_window.py" line="409"/>
      <source>Application update available. Visit website?</source>
      <translation>Application update available. Visit website?</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="409"/>
      <source>An application update is available: Version {newer_version}
You are currently using version {current_version}.

Open the {program_name} website in your web browser to download the new version?</source>
      <translation>An application update is available: Version {newer_version}
You are currently using version {current_version}.

Open the {program_name} website in your web browser to download the new version?</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="424"/>
      <source>New card data available</source>
      <translation>New card data available</translation>
    </message>
    <message numerus="yes">
      <location filename="../../ui/main_window.py" line="424"/>
      <source>There are %n new printings available on Scryfall. Update the local data now?</source>
      <translation>
        <numerusform>There is %n new printing available on Scryfall. Update the local data now?</numerusform>
        <numerusform>There are %n new printings available on Scryfall. Update the local data now?</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="440"/>
      <source>Check for application updates?</source>
      <translation>Check for application updates?</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="440"/>
      <source>Automatically check for application updates whenever you start {name}?</source>
      <translation>Automatically check for application updates whenever you start {name}?</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="450"/>
      <source>Check for card data updates?</source>
      <translation>Check for card data updates?</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="450"/>
      <source>Automatically check for card data updates on Scryfall whenever you start {program_name}?</source>
      <translation>Automatically check for card data updates on Scryfall whenever you start {program_name}?</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="460"/>
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
      <location filename="../ui/main_window.ui" line="169"/>
      <source>Settings</source>
      <translation>Settings</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="59"/>
      <source>Edit</source>
      <translation>Edit</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="300"/>
      <source>Show toolbar</source>
      <translation>Show toolbar</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="108"/>
      <source>&amp;Quit</source>
      <translation>&amp;Quit</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="111"/>
      <source>Ctrl+Q</source>
      <translation>Ctrl+Q</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="122"/>
      <source>&amp;Print</source>
      <translation>&amp;Print</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="125"/>
      <source>Print the current document</source>
      <translation>Print the current document</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="128"/>
      <source>Ctrl+P</source>
      <translation>Ctrl+P</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="136"/>
      <source>&amp;Show print preview</source>
      <translation>&amp;Show print preview</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="139"/>
      <source>Show print preview window</source>
      <translation>Show print preview window</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="147"/>
      <source>&amp;Create PDF</source>
      <translation>&amp;Create PDF</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="150"/>
      <source>Create a PDF document</source>
      <translation>Create a PDF document</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="158"/>
      <source>Discard page</source>
      <translation>Discard page</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="161"/>
      <source>Discard this page.</source>
      <translation>Discard this page.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="180"/>
      <source>Update card data</source>
      <translation>Update card data</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="188"/>
      <source>New Page</source>
      <translation>New Page</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="191"/>
      <source>Add a new, empty page.</source>
      <translation>Add a new, empty page.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="199"/>
      <source>Save</source>
      <translation>Save</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="202"/>
      <source>Ctrl+S</source>
      <translation>Ctrl+S</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="210"/>
      <source>New</source>
      <translation>New</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="213"/>
      <source>Ctrl+N</source>
      <translation>Ctrl+N</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="221"/>
      <source>Load</source>
      <translation>Load</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="224"/>
      <source>Ctrl+L</source>
      <translation>Ctrl+L</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="232"/>
      <source>Save as …</source>
      <translation>Save as …</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="237"/>
      <source>About …</source>
      <translation>About …</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="245"/>
      <source>Show Changelog</source>
      <translation>Show change-log</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="253"/>
      <source>Compact document</source>
      <translation>Compact document</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="256"/>
      <source>Minimize page count: Fill empty slots on pages by moving cards from the end of the document</source>
      <translation>Minimize page count: Fill empty slots on pages by moving cards from the end of the document</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="264"/>
      <source>Edit document settings</source>
      <translation>Edit document settings</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="267"/>
      <source>Configure page size, margins, image spacings for the currently edited document.</source>
      <translation>Configure page size, margins, image spacings for the currently edited document.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="275"/>
      <source>Import Deck list</source>
      <translation>Import Deck list</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="278"/>
      <source>Import a deck list from online sources</source>
      <translation>Import a deck list from online sources</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="286"/>
      <source>Cleanup card images</source>
      <translation>Cleanup card images</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="289"/>
      <source>Delete locally stored card images you no longer need.</source>
      <translation>Delete locally stored card images you no longer need.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="303"/>
      <source>Ctrl+M</source>
      <translation>Ctrl+M</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="311"/>
      <source>Download missing card images</source>
      <translation>Download missing card images</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="319"/>
      <source>Shuffle document</source>
      <translation>Shuffle document</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="322"/>
      <source>Randomly rearrange all card image.
If you want to quickly print a full deck for playing,
use this to reduce the initial deck shuffling required</source>
      <translation>Randomly rearrange all card image.
If you want to quickly print a full deck for playing,
use this to reduce the initial deck shuffling required</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="335"/>
      <source>Undo</source>
      <translation>Undo</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="346"/>
      <source>Redo</source>
      <translation>Redo</translation>
    </message>
  </context>
  <context>
    <name>PDFSettingsPage</name>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="534"/>
      <source>PDF export settings</source>
      <translation>PDF export settings</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="534"/>
      <source>Configure the PDF export</source>
      <translation>Configure the PDF export</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="568"/>
      <source>Select default PDF export location</source>
      <translation>Select default PDF export location</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/pdf_settings_page.ui" line="17"/>
      <source>If set, use this as the default location for saving exported PDF documents.</source>
      <translation>If set, use this as the default location for saving exported PDF documents.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/pdf_settings_page.ui" line="23"/>
      <source>Path to a directory</source>
      <translation>Path to a directory</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/pdf_settings_page.ui" line="46"/>
      <source>PDF export path</source>
      <translation>PDF export path</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/pdf_settings_page.ui" line="56"/>
      <source>Browse…</source>
      <translation>Browse…</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/pdf_settings_page.ui" line="96"/>
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
      <location filename="../ui/settings_window/pdf_settings_page.ui" line="80"/>
      <source>Split PDF documents longer than</source>
      <translation>Split PDF documents longer than</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/pdf_settings_page.ui" line="107"/>
      <source> pages</source>
      <translation> page(s)</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/pdf_settings_page.ui" line="117"/>
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
      <location filename="../ui/settings_window/pdf_settings_page.ui" line="124"/>
      <source>Enable landscape workaround: Rotate landscape PDFs by 90°</source>
      <translation>Enable landscape workaround: Rotate landscape PDFs by 90°</translation>
    </message>
  </context>
  <context>
    <name>PageConfigPreviewArea</name>
    <message>
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
    <message numerus="yes">
      <location filename="../../ui/page_config_widget.py" line="105"/>
      <source>%n regular card(s)</source>
      <comment>Display of the resulting page capacity for regular-sized cards</comment>
      <translation>
        <numerusform>%n regular card</numerusform>
        <numerusform>%n regular cards</numerusform>
      </translation>
    </message>
    <message numerus="yes">
      <location filename="../../ui/page_config_widget.py" line="109"/>
      <source>%n oversized card(s)</source>
      <comment>Display of the resulting page capacity for oversized cards</comment>
      <translation>
        <numerusform>%n oversized card</numerusform>
        <numerusform>%n oversized cards</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../ui/page_config_widget.py" line="114"/>
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
      <location filename="../ui/page_config_widget.ui" line="20"/>
      <source>Number of cards fitting on each page,
based on the page size and spacings configured</source>
      <translation>Number of cards fitting on each page,
based on the page size and spacings configured</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="57"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the left paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the left paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="423"/>
      <source> mm</source>
      <translation> mm</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="76"/>
      <source>Paper height in millimeters.
Must match the size of the sheets in the printer.
Otherwise, scaling may be applied by the printer driver.</source>
      <translation>Paper height in millimeters.
Must match the size of the sheets in the printer.
Otherwise, scaling may be applied by the printer driver.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="94"/>
      <source>Top margin</source>
      <translation>Top margin</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="113"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the right paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the right paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="126"/>
      <source>If enabled, the page number is printed on each page. Makes it easier to notice missing pages in a stack.</source>
      <translation>If enabled, the page number is printed on each page. Makes it easier to notice missing pages in a stack.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="129"/>
      <source>Print page numbers</source>
      <translation>Print page numbers</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="136"/>
      <source>Resulting page capacity:</source>
      <translation>Resulting page capacity:</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="146"/>
      <source>Card bleed</source>
      <translation>Card bleed</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="165"/>
      <source>Paper width in millimeters.
Must match the size of the sheets in the printer.
Otherwise, scaling may be applied by the printer driver.</source>
      <translation>Paper width in millimeters.
Must match the size of the sheets in the printer.
Otherwise, scaling may be applied by the printer driver.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="183"/>
      <source>Enable printing additional lines to aid cutting the printed sheets.</source>
      <translation>Enable printing additional lines to aid cutting the printed sheets.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="186"/>
      <source>Print cut markers</source>
      <translation>Print cut markers</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="199"/>
      <source>Space between image rows in mm.
If set to zero, you only need one cut to separate two images,
otherwise you need two cuts but require less precision hitting the exact middle.</source>
      <translation>Space between image rows in mm.
If set to zero, you only need one cut to separate two images,
otherwise you need two cuts but require less precision hitting the exact middle.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="214"/>
      <source>Draw 90° card corners, instead of round ones</source>
      <translation>Draw 90° card corners, instead of round ones</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="227"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the top paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the top paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="240"/>
      <source>Document name</source>
      <translation>Document name</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="250"/>
      <source>Row spacing</source>
      <translation>Row spacing</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="263"/>
      <source>The document name is printed on each page and can help you keep track
of different printed sheets and to which deck they belong.

Leave empty to disable.</source>
      <translation>The document name is printed on each page and can help you keep track
of different printed sheets and to which deck they belong.

Leave empty to disable.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="272"/>
      <source>Document/deck name</source>
      <translation>Document/deck name</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="282"/>
      <source>Page height</source>
      <translation>Page height</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="295"/>
      <source>Draw an additional border around cards to ease cutting.</source>
      <translation>Draw an additional border around cards to ease cutting.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="308"/>
      <source>Bottom Margin</source>
      <translation>Bottom Margin</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="321"/>
      <source>Left margin</source>
      <translation>Left margin</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="340"/>
      <source>Space between image columns in mm.
If set to zero, you only need one cut to separate two images,
otherwise you need two cuts but require less precision hitting the exact middle.</source>
      <translation>Space between image columns in mm.
If set to zero, you only need one cut to separate two images,
otherwise you need two cuts but require less precision hitting the exact middle.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="361"/>
      <source>Switch between portrait and landscape mode</source>
      <translation>Switch between portrait and landscape mode</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="364"/>
      <source>Flip</source>
      <translation>Flip</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="375"/>
      <source>Column spacing</source>
      <translation>Column spacing</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="388"/>
      <source>Right margin</source>
      <translation>Right margin</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="401"/>
      <source>Page width</source>
      <translation>Page width</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="420"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the bottom paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the bottom paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="448"/>
      <source>Show Preview</source>
      <translation>Show Preview</translation>
    </message>
  </context>
  <context>
    <name>PageRenderer</name>
    <message>
      <location filename="../../ui/page_renderer.py" line="64"/>
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
      <location filename="../../decklist_parser/common.py" line="67"/>
      <source>All files (*)</source>
      <translation>All files (*)</translation>
    </message>
  </context>
  <context>
    <name>PrettySetListModel</name>
    <message>
      <location filename="../../model/string_list.py" line="36"/>
      <source>Set</source>
      <comment>MTG set name</comment>
      <translation>Set</translation>
    </message>
  </context>
  <context>
    <name>PrinterSettingsPage</name>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="500"/>
      <source>Printer settings</source>
      <translation>Printer settings</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="500"/>
      <source>Configure the printer</source>
      <translation>Configure the printer</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/printer_settings_page.ui" line="17"/>
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
      <location filename="../ui/settings_window/printer_settings_page.ui" line="24"/>
      <source>Configure printer for borderless printing</source>
      <translation>Configure printer for borderless printing</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/printer_settings_page.ui" line="31"/>
      <source>If enabled, print landscape documents in portrait mode with all content rotated by 90°.
Enable this, if printing landscape documents results in portrait printouts with cropped-off sides.</source>
      <translation>If enabled, print landscape documents in portrait mode with all content rotated by 90°.
Enable this, if printing landscape documents results in portrait printouts with cropped-off sides.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/printer_settings_page.ui" line="35"/>
      <source>Enable landscape workaround: Rotate prints by 90°</source>
      <translation>Enable landscape workaround: Rotate prints by 90°</translation>
    </message>
  </context>
  <context>
    <name>PrintingFilterUpdater.store_current_printing_filters()</name>
    <message>
      <location filename="../../printing_filter_updater.py" line="126"/>
      <source>Processing updated card filters:</source>
      <translation>Processing updated card filters:</translation>
    </message>
  </context>
  <context>
    <name>SaveDocumentAsDialog</name>
    <message>
      <location filename="../../ui/dialogs.py" line="133"/>
      <source>Save document as …</source>
      <translation>Save document as …</translation>
    </message>
  </context>
  <context>
    <name>SavePDFDialog</name>
    <message>
      <location filename="../../ui/dialogs.py" line="79"/>
      <source>Export as PDF</source>
      <translation>Export as PDF</translation>
    </message>
    <message>
      <location filename="../../ui/dialogs.py" line="80"/>
      <source>PDF documents (*.pdf)</source>
      <translation>PDF documents (*.pdf)</translation>
    </message>
  </context>
  <context>
    <name>ScryfallCSVParser</name>
    <message>
      <location filename="../../decklist_parser/csv_parsers.py" line="116"/>
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
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="23"/>
      <source>Deck list files, stored in XMage’s native format.
Because XMage closely follows Scryfall regarding Magic sets,
this should give very accurate results.</source>
      <translation>Deck list files, stored in XMage’s native format.
Because XMage closely follows Scryfall regarding Magic sets,
this should give very accurate results.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="28"/>
      <source>XMage</source>
      <translation>XMage</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="38"/>
      <source>This is a Tappedout-specific section of the deck.
It may contain the deck list author’s buy-list or anything else.</source>
      <translation>This is a Tappedout-specific section of the deck.
It may contain the deck list author’s buy-list or anything else.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="42"/>
      <source>Include “Acquire-Board”</source>
      <translation>Include “Acquire-Board”</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="49"/>
      <source>The simplistic format used by Magic Online. It does not specify exact printings, so may not give the best results.</source>
      <translation>The simplistic format used by Magic Online. It does not specify exact printings, so may not give the best results.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="52"/>
      <source>Magic Online</source>
      <translation>Magic Online</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="94"/>
      <source>This is a Tappedout-specific section of the deck.
It may contain cards that the deck list creator considers for inclusion, based on the meta
or any other preference, like card price.</source>
      <translation>This is a Tappedout-specific section of the deck.
It may contain cards that the deck list creator considers for inclusion, based on the meta
or any other preference, like card price.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="99"/>
      <source>Include “Maybe-Board”</source>
      <translation>Include “Maybe-Board”</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="106"/>
      <source>CSV exports from Scryfall’s own deck builder.
Gives very accurate results, unless the imported deck list contains ignored items
matching an enabled card filter.</source>
      <translation>CSV exports from Scryfall’s own deck builder.
Gives very accurate results, unless the imported deck list contains ignored items
matching an enabled card filter.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="111"/>
      <source>Scryfall.com deck lists (CSV export)</source>
      <translation>Scryfall.com deck lists (CSV export)</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="131"/>
      <source>CSV exports can be downloaded from Tappedout by choosing the appropriate deck export option.</source>
      <translation>CSV exports can be downloaded from Tappedout by choosing the appropriate deck export option.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="134"/>
      <source>tappedout.net deck list (CSV export)</source>
      <translation>tappedout.net deck list (CSV export)</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="146"/>
      <source>Appends a sample matcher for a set code to the input field above.</source>
      <translation>Appends a sample matcher for a set code to the input field above.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="149"/>
      <source>Set code matcher</source>
      <translation>Set code matcher</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="159"/>
      <source>Appends a sample matcher for a collector number to the input field above</source>
      <translation>Appends a sample matcher for a collector number to the input field above</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="162"/>
      <source>Collector number matcher</source>
      <translation>Collector number matcher</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="172"/>
      <source>Appends a matcher for the number of card copies to the input field above.
If a card count field is not present in the deck list, 1 card copy per line is assumed</source>
      <translation>Appends a matcher for the number of card copies to the input field above.
If a card count field is not present in the deck list, 1 card copy per line is assumed</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="176"/>
      <source>Copies matcher</source>
      <translation>Copies matcher</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="186"/>
      <source>Appends a matcher for a card name to the input field above.</source>
      <translation>Appends a matcher for a card name to the input field above.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="189"/>
      <source>Card name matcher</source>
      <translation>Card name matcher</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="199"/>
      <source>Appends a matcher for the Scryfall ID to the input field above.
This may be used by deck lists that closely integrate with the Scryfall website.
Most deck lists won’t use this.</source>
      <translation>Appends a matcher for the Scryfall ID to the input field above.
This may be used by deck lists that closely integrate with the Scryfall website.
Most deck lists won’t use this.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="204"/>
      <source>Scryfall ID matcher</source>
      <translation>Scryfall ID matcher</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="214"/>
      <source>Appends a matcher for the  card language to the input field above.
If a language field is not present in the deck list, the card language is guessed.</source>
      <translation>Appends a matcher for the  card language to the input field above.
If a language field is not present in the deck list, the card language is guessed.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="218"/>
      <source>Language matcher</source>
      <translation>Language matcher</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="227"/>
      <source>Specify a custom regular expression in the input field below. It will be used to parse each deck list line.
You can use the buttons below to insert basic building blocks.
You have to separate them with the “control structures”, like spaces, as used in your deck list.</source>
      <translation>Specify a custom regular expression in the input field below. It will be used to parse each deck list line.
You can use the buttons below to insert basic building blocks.
You have to separate them with the “control structures”, like spaces, as used in your deck list.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="232"/>
      <source>Custom regular expression based parser:</source>
      <translation>Custom regular expression based parser:</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="268"/>
      <source>Magic Arena and exports from compatible websites, like moxfield.com
Note that this option is not limited to cards in Standard/Historic,
as the format works for any card.</source>
      <translation>Magic Arena and exports from compatible websites, like moxfield.com
Note that this option is not limited to cards in Standard/Historic,
as the format works for any card.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="273"/>
      <source>MTG Arena</source>
      <translation>MTG Arena</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="283"/>
      <source>Enter a Regular Expression containing at least one supported, named group.

Supported named groups are: {group_names}

See the 'What’s this?' (?-Button) help for details.</source>
      <translation>Enter a Regular Expression containing at least one supported, named group.

Supported named groups are: {group_names}

See the 'What’s this?' (?-Button) help for details.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="290"/>
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
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="317"/>
      <source>Magic Workstation Deck Data (mwDeck)</source>
      <translation>Magic Workstation Deck Data (mwDeck)</translation>
    </message>
  </context>
  <context>
    <name>SettingsWindow</name>
    <message>
      <location filename="../../ui/settings_window.py" line="206"/>
      <source>Apply settings to the current document?</source>
      <translation>Apply settings to the current document?</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="206"/>
      <source>The new default settings differ from the settings used by the current document.
Apply the new settings to the current document?</source>
      <translation>The new default settings differ from the settings used by the current document.
Apply the new settings to the current document?</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="219"/>
      <source>Reset unsaved changes?</source>
      <translation>Reset unsaved changes?</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="219"/>
      <source>Reset unsaved changes on the current page or on all pages?</source>
      <translation>Reset unsaved changes on the current page or on all pages?</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="225"/>
      <source>Reset everything</source>
      <translation>Reset everything</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="226"/>
      <source>Reset current page</source>
      <translation>Reset current page</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="253"/>
      <source>Restore defaults for the current page or everything?</source>
      <translation>Restore defaults for the current page or everything?</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="253"/>
      <source>Restore the settings on the current page or on all pages to their default values?</source>
      <translation>Restore the settings on the current page or on all pages to their default values?</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="259"/>
      <source>Restore everything</source>
      <translation>Restore everything</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="260"/>
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
      <location filename="../../ui/cache_cleanup_wizard.py" line="451"/>
      <source>Images about to be deleted: {count}</source>
      <translation>Images about to be deleted: {count}</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="452"/>
      <source>Disk space that will be freed: {disk_space_freed}</source>
      <translation>Disk space that will be freed: {disk_space_freed}</translation>
    </message>
    <message numerus="yes">
      <location filename="../../ui/deck_import_wizard.py" line="469"/>
      <source>Beware: The card list currently contains %n potentially oversized card(s).</source>
      <comment>Warning emitted, if at least 1 card has the oversized flag set. The Scryfall server *may* still return a regular-sized image, so not *all* printings marked as oversized are actually so when fetched.</comment>
      <translation>
        <numerusform>Beware: The card list currently contains %n potentially oversized card.</numerusform>
        <numerusform>Beware: The card list currently contains %n potentially oversized cards.</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="489"/>
      <source>Replace document content with the identified cards</source>
      <translation>Replace document content with the identified cards</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="492"/>
      <source>Append identified cards to the document</source>
      <translation>Append identified cards to the document</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="543"/>
      <source>Remove basic lands</source>
      <translation>Remove basic lands</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="544"/>
      <source>Remove all basic lands in the deck list above</source>
      <translation>Remove all basic lands in the deck list above</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="549"/>
      <source>Remove selected</source>
      <translation>Remove selected</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="550"/>
      <source>Remove all selected cards in the deck list above</source>
      <translation>Remove all selected cards in the deck list above</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/summary_page.ui" line="14"/>
      <source>Summary</source>
      <translation>Summary</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="14"/>
      <source>Import a deck list for printing</source>
      <translation>Import a deck list for printing</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="17"/>
      <source>The cards shown here will be imported. Double-click the Set Collector# or Language cells to change selected printings. The text field shows all lines from the input that were not identified as cards.</source>
      <translation>The cards shown here will be imported. Double-click the Set Collector# or Language cells to change selected printings. The text field shows all lines from the input that were not identified as cards.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="23"/>
      <source>If checked, clear all cards in the current document, replacing everything with the list below.
If unchecked, append the cards found below to the document.</source>
      <translation>If checked, clear all cards in the current document, replacing everything with the list below.
If unchecked, append the cards found below to the document.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="27"/>
      <source>Replace the current document content with the found cards</source>
      <translation>Replace the current document content with the found cards</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="37"/>
      <source>These cards were successfully identified:</source>
      <translation>These cards were successfully identified:</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="66"/>
      <source>These lines from the deck list were not identified as cards:</source>
      <translation>These lines from the deck list were not identified as cards:</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="85"/>
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
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="38"/>
      <source>Add new cards</source>
      <translation>Add new cards</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="43"/>
      <source>Current page</source>
      <translation>Current page</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="92"/>
      <source>Remove selected</source>
      <translation>Remove selected</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="103"/>
      <source>Preview</source>
      <translation>Preview</translation>
    </message>
  </context>
  <context>
    <name>TappedOutCSVParser</name>
    <message>
      <location filename="../../decklist_parser/csv_parsers.py" line="195"/>
      <source>Tappedout CSV export</source>
      <translation>Tappedout CSV export</translation>
    </message>
  </context>
  <context>
    <name>UnknownCardImageModel</name>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="269"/>
      <source>Scryfall ID</source>
      <translation>Scryfall ID</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="270"/>
      <source>Front/Back</source>
      <translation>Front/Back</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="271"/>
      <source>High resolution?</source>
      <translation>High resolution?</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="272"/>
      <source>Size</source>
      <translation>Size</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="273"/>
      <source>Path</source>
      <translation>Path</translation>
    </message>
  </context>
  <context>
    <name>UnknownCardRow</name>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="243"/>
      <source>Front</source>
      <translation>Front</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="243"/>
      <source>Back</source>
      <translation>Back</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="249"/>
      <source>Yes</source>
      <translation>Yes</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="249"/>
      <source>No</source>
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
      <translation>Language:</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="152"/>
      <source>Copies:</source>
      <translation>Copies:</translation>
    </message>
  </context>
  <context>
    <name>XMageParser</name>
    <message>
      <location filename="../../decklist_parser/re_parsers.py" line="255"/>
      <source>XMage Deck file</source>
      <translation>XMage Deck file</translation>
    </message>
  </context>
  <context>
    <name>format_size</name>
    <message>
      <location filename="../../ui/common.py" line="117"/>
      <source>{size} {unit}</source>
      <comment>A formatted file size in SI bytes</comment>
      <translation>{size} {unit}</translation>
    </message>
  </context>
</TS>
