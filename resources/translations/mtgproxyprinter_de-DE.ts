<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" sourcelanguage="en_US" language="de">
  <context>
    <name>AboutDialog</name>
    <message>
      <location filename="../ui/about_dialog.ui" line="14"/>
      <source>About MTGProxyPrinter</source>
      <translation>Über MTGProxyPrinter</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="27"/>
      <source>About</source>
      <translation>Über</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="39"/>
      <source>Application Version:</source>
      <translation>Anwendungsversion:</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="55"/>
      <source>Last card update:</source>
      <translation>Letzte Kartenaktualisierung:</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="62"/>
      <source>Application version</source>
      <translation>Anwendungsversion</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="87"/>
      <source>Python Version:</source>
      <translation>Python-Version:</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="107"/>
      <source>Python runtime version</source>
      <translation>Benutzte Python-Version</translation>
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
      <translation>{application_name} erlaubt das Drucken von 
[Magic: The Gathering](https://magic.wizards.com/) Karten zum Zwecke des Testens.

{application_name} ist inoffizieller Fan-Inhalt, der unter der 
[Fan-Inhaltsrichtlinie](https://company.wizards.com/fancontentpolicy) erlaubt ist. Nicht
genehmigt/bestätigt von Wizards. Teile der verwendeten Materialien sind Eigentum von
Wizards of the Coast. ©️[Wizards of the Coast LLC](https://company.wizards.com/).

Im Rahmen der Fan-Inhaltsrichtlinie dürfen Sie die mit diesem Programm heruntergeladenen und erstellten Daten, einschließlich der Kartendatenbankinhalte und heruntergeladenen Kartenbilder sowie aller Dokumente, die sowohl in digitaler als auch physischer Form erstellt wurden, nicht verkaufen.

Projekt-Website: [{application_name} Homepage]({application_home_page})

Anwendungsicon von [islanders2013](https://www.reddit.com/user/islanders2013/)

</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="206"/>
      <location filename="../ui/about_dialog.ui" line="215"/>
      <source>Changelog</source>
      <translation>Änderungsprotokoll</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="229"/>
      <source>License</source>
      <translation>Lizenzvereinbarung</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="240"/>
      <source>Third party licenses</source>
      <translation>Drittanbieter-Lizenzen</translation>
    </message>
  </context>
  <context>
    <name>ActionAddCard</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/card_actions.py" line="165"/>
      <source>Add {count} × {card_display_string} to page {target}</source>
      <comment>Undo/redo tooltip text. Plural form refers to {target}, not {count}. {target} can be multiple ranges of multiple pages each</comment>
      <translation>
        <numerusform>Füge {count} × {card_display_string} zu Seite {target} hinzu</numerusform>
        <numerusform>Füge {count} × {card_display_string} zu Seiten {target} hinzu</numerusform>
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
        <numerusform>Minimiere Seitenzahl, entferne eine Seite</numerusform>
        <numerusform>Minimiere Seitenzahl, entferne %n Seiten</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionEditCustomCard</name>
    <message>
      <location filename="../../mtg_proxy_printer/document_controller/edit_custom_card.py" line="90"/>
      <source>Edit custom card, set {column_header_text} to {new_value}</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Inoffizielle Karte bearbeiten, {column_header_text} auf {new_value} setzen</translation>
    </message>
  </context>
  <context>
    <name>ActionEditDocumentSettings</name>
    <message>
      <location filename="../../mtg_proxy_printer/document_controller/edit_document_settings.py" line="139"/>
      <source>Update document settings</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Dokumenteneinstellungen ändern</translation>
    </message>
  </context>
  <context>
    <name>ActionImportDeckList</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/import_deck_list.py" line="82"/>
      <source>Replace document with imported deck list containing %n card(s)</source>
      <comment>Undo/redo tooltip text. Option to delete the current document enabled.</comment>
      <translation>
        <numerusform>Ersetze Dokument durch importierte Deckliste mit einer Karte</numerusform>
        <numerusform>Ersetze Dokument durch importierte Deckliste mit %n Karten</numerusform>
      </translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/import_deck_list.py" line="86"/>
      <source>Import a deck list containing %n card(s)</source>
      <comment>Undo/redo tooltip text. Option to delete the current document disabled.</comment>
      <translation>
        <numerusform>Deckliste mit %n Karte importieren</numerusform>
        <numerusform>Deckliste mit %n Karten importieren</numerusform>
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
        <numerusform>mit einer Karte</numerusform>
        <numerusform>und insgesamt %n Karten</numerusform>
      </translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/load_document.py" line="82"/>
      <source>Load document from &apos;{save_path}&apos;,
containing %n page(s) {cards_total}</source>
      <comment>Undo/redo tooltip text.</comment>
      <translation>
        <numerusform>Lade Dokument von &apos;{save_path}&apos;,
mit %n Seite {cards_total}</numerusform>
        <numerusform>Lade Dokument von &apos;{save_path}&apos;,
mit %n Seiten {cards_total}</numerusform>
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
        <numerusform>Verschiebe Karte von Seite {source_page} nach {target_page}</numerusform>
        <numerusform>Verschiebe %n Karten von Seite {source_page} nach {target_page}</numerusform>
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
        <numerusform>Eine Karte auf Seite {page} an eine andere Position verschieben</numerusform>
        <numerusform>%n Karten auf Seite {page} umsortieren</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionMovePage</name>
    <message>
      <location filename="../../mtg_proxy_printer/document_controller/move_page.py" line="89"/>
      <source>Move page {source_page} to position {target_page}</source>
      <comment>Both parameters are page numbers, like in &apos;Move page 3 to position 7&apos;</comment>
      <translation>Verschiebe Seite {source_page} nach {target_page}</translation>
    </message>
  </context>
  <context>
    <name>ActionNewDocument</name>
    <message>
      <location filename="../../mtg_proxy_printer/document_controller/new_document.py" line="73"/>
      <source>Create new document</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Neues Dokument erstellen</translation>
    </message>
  </context>
  <context>
    <name>ActionNewPage</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/page_actions.py" line="88"/>
      <source>Add page(s) {pages}</source>
      <comment>Undo/redo tooltip text. Translations should drop the %n placeholder</comment>
      <translation>
        <numerusform>Seite {pages} hinzufügen</numerusform>
        <numerusform>Seiten {pages} hinzufügen</numerusform>
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
        <numerusform>Entferne %n Karte von Seite {page_number}</numerusform>
        <numerusform>Entferne %n Karten von Seite {page_number}</numerusform>
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
        <numerusform>mit einer Karte</numerusform>
        <numerusform>mit %n Karten</numerusform>
      </translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/page_actions.py" line="195"/>
      <source>Remove page(s) {formatted_pages} containing {formatted_card_count}</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>
        <numerusform>Seite {formatted_pages} {formatted_card_count} entfernt</numerusform>
        <numerusform>Seiten {formatted_pages} {formatted_card_count} entfernt</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionReplaceCard</name>
    <message>
      <location filename="../../mtg_proxy_printer/document_controller/replace_card.py" line="103"/>
      <source>Replace card {old_card} on page {page_number} with {new_card}</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Ersetze {old_card} auf Seite {page_number} durch {new_card}</translation>
    </message>
  </context>
  <context>
    <name>ActionSaveDocument</name>
    <message>
      <location filename="../../mtg_proxy_printer/document_controller/save_document.py" line="175"/>
      <source>Save document to &apos;{save_file_path}&apos;.</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Dokument unter &apos;{save_file_path}&apos; speichern.</translation>
    </message>
  </context>
  <context>
    <name>ActionShuffleDocument</name>
    <message>
      <location filename="../../mtg_proxy_printer/document_controller/shuffle_document.py" line="99"/>
      <source>Shuffle document</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Dokument mischen</translation>
    </message>
  </context>
  <context>
    <name>ApiStreamTask</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="332"/>
      <source>Requesting the number of available cards on Scryfall failed: 
{error}</source>
      <comment>Error message shown in a message box</comment>
      <translation>Die Anzahl der auf Scryfall verfügbaren Karten konnte nicht angefordert werden: 
{error}</translation>
    </message>
  </context>
  <context>
    <name>ApplicationUpdateCheckTask</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/update_checker.py" line="171"/>
      <source>Application update check: </source>
      <comment>Progress bar label text</comment>
      <translation>App-Update-Prüfung: </translation>
    </message>
  </context>
  <context>
    <name>BatchDownloadTask</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/image_downloader.py" line="234"/>
      <source>Importing deck list:</source>
      <comment>Progress bar label text</comment>
      <translation>Deckliste importieren:</translation>
    </message>
  </context>
  <context>
    <name>CacheCleanupWizard</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="481"/>
      <source>Cleanup locally stored card images</source>
      <comment>Dialog window title</comment>
      <translation>Lokal gespeicherte Kartenbilder bereinigen</translation>
    </message>
  </context>
  <context>
    <name>CardFilterPage</name>
    <message>
      <location filename="../ui/cache_cleanup_wizard/card_filter_page.ui" line="14"/>
      <source>Select images for removal</source>
      <translation>Bilder zum Löschen auswählen</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/card_filter_page.ui" line="17"/>
      <source>Click on entries in the tables below to mark or un-mark them for removal. All selected entries will be removed.</source>
      <translation>Klicken Sie auf Einträge in den Tabellen unten, um diese zum Löschen auszuwählen. Alle ausgewählten Einträge werden entfernt.</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/card_filter_page.ui" line="30"/>
      <source>All images currently stored on disk:</source>
      <translation>Alle aktuell auf der Festplatte gespeicherten Bilder:</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/card_filter_page.ui" line="69"/>
      <source>Images found on disk that can not be associated with any card.</source>
      <translation>Auf der Festplatte gefundene Bilder, die mit keiner Karte verknüpft werden können.</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/card_filter_page.ui" line="72"/>
      <source>Unknown images:</source>
      <translation>Unbekannte Bilder:</translation>
    </message>
  </context>
  <context>
    <name>CardListModel</name>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="89"/>
      <source>Copies</source>
      <comment>Table header for card lists. Number of copies that will be added</comment>
      <translation>Kopien</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="91"/>
      <source>Card name</source>
      <comment>Table header for card lists</comment>
      <translation>Kartenname</translation>
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
      <translation>Sammler #</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="97"/>
      <source>Language</source>
      <comment>Table header for card lists. Card language.</comment>
      <translation>Sprache</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="99"/>
      <source>Side</source>
      <comment>Table header for card lists. Side of the card</comment>
      <translation>Seite</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="136"/>
      <source>Front</source>
      <comment>Magic card side</comment>
      <translation>Vorderseite</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="137"/>
      <source>Back</source>
      <comment>Magic card side</comment>
      <translation>Rückseite</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="145"/>
      <source>Beware: Potentially oversized card!
This card may not fit in your deck.</source>
      <comment>Tooltip shown on cards that, according to API results, have double the physical size. The actual image may still have regular size.</comment>
      <translation>Achtung: Potenziell übergroße Karte!
Diese Karte könnte nicht in Ihr Deck passen.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="332"/>
      <source>Double-click on entries to
switch the selected printing.</source>
      <comment>Tooltip text</comment>
      <translation>Doppelklicken Sie auf Einträge, um die Version
zu wechseln.</translation>
    </message>
  </context>
  <context>
    <name>CardSideSelectionDelegate</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/item_delegates.py" line="96"/>
      <source>Front</source>
      <comment>Magic card side</comment>
      <translation>Vorderseite</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/item_delegates.py" line="97"/>
      <source>Back</source>
      <comment>Magic card side</comment>
      <translation>Rückseite</translation>
    </message>
  </context>
  <context>
    <name>ColumnarCentralWidget</name>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="23"/>
      <source>Move up</source>
      <translation>Schiebe hoch</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="33"/>
      <source>Current page:</source>
      <translation>Aktuelle Seite:</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="69"/>
      <source>Remove selected</source>
      <translation>Ausgewählte entfernen</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="79"/>
      <source>Add new cards:</source>
      <translation>Karten hinzufügen:</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="120"/>
      <source>Move down</source>
      <translation>Schiebe runter</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="158"/>
      <source>All pages:</source>
      <translation>Alle Seiten:</translation>
    </message>
  </context>
  <context>
    <name>CustomCardImportDialog</name>
    <message>
      <location filename="../ui/custom_card_import_dialog.ui" line="14"/>
      <source>Import custom cards</source>
      <translation>Inoffizielle Karten importieren</translation>
    </message>
    <message>
      <location filename="../ui/custom_card_import_dialog.ui" line="20"/>
      <source>Set Copies to …</source>
      <translation>Kopien auf … setzen</translation>
    </message>
    <message>
      <location filename="../ui/custom_card_import_dialog.ui" line="40"/>
      <source>Remove selected</source>
      <translation>Ausgewählte entfernen</translation>
    </message>
    <message>
      <location filename="../ui/custom_card_import_dialog.ui" line="50"/>
      <source>Load images</source>
      <translation>Bilder laden</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/custom_card_import_dialog.py" line="101"/>
      <source>Import custom cards</source>
      <comment>File selection dialog window title</comment>
      <translation>Inoffizielle Karten importieren</translation>
    </message>
  </context>
  <context>
    <name>DatabaseImportTask</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="393"/>
      <source>Import card data from File:</source>
      <comment>Progress bar label text</comment>
      <translation>Kartendaten aus Datei importieren:</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="398"/>
      <source>Update card data from Scryfall:</source>
      <comment>Progress bar label text</comment>
      <translation>Kartendaten von Scryfall aktualisieren:</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="409"/>
      <source>Error during import from file:
{path}</source>
      <comment>Error message shown in a message box</comment>
      <translation>Fehler beim Import aus Datei:
{path}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="414"/>
      <source>Error during update from Scryfall</source>
      <comment>Error message shown in a message box</comment>
      <translation>Fehler beim Aktualisieren der Kartendaten von Scryfall</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="440"/>
      <source>Failed to parse data from Scryfall. Reported error: {error}</source>
      <comment>Error message shown in a message box</comment>
      <translation>Fehler beim Verarbeiten der Scryfall-Daten. Fehler: {error}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="488"/>
      <source>Post-processing card data:</source>
      <comment>Progress bar label text</comment>
      <translation>Kartendaten nachbearbeiten:</translation>
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
      <translation>Kartendatenbank-Migration fehlgeschlagen! Es wird versucht, sie neu zu erstellen.
Dies löscht alle zuvor heruntergeladenen Kartendaten und erfordert einen erneuten Download.
Fehlermeldung:

{error_message}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/carddb_migrations.py" line="803"/>
      <source>Running database migrations:</source>
      <translation>Datenbankmigrationen durchführen:</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/carddb_migrations.py" line="818"/>
      <source>Migrate to version %n:</source>
      <comment>The numeric parameter is a version number, and not countable.</comment>
      <translation>Migrieren zu Version %n:</translation>
    </message>
  </context>
  <context>
    <name>DebugSettingsPage</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="125"/>
      <source>Debug settings</source>
      <translation>Fehlersuche (Debug)</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="127"/>
      <source>Things useful for investigating bugs in the application</source>
      <translation>Nützliche Dinge, um Fehler in der Anwendung zu untersuchen</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="180"/>
      <source>Select download location</source>
      <translation>Download-Verzeichnis auswählen</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="188"/>
      <source>Selected location is not a directory</source>
      <translation>Ausgewählter Ort ist kein Verzeichnis</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="191"/>
      <source>Cannot write the card data at the given location, because it is not a directory:
{location}</source>
      <translation>Die Kartendaten können nicht an den angegebenen Ort geschrieben werden, da es kein Verzeichnis ist:
{location}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="201"/>
      <source>Import previously downloaded card data obtained from Scryfall</source>
      <translation>Zuvor von Scryfall heruntergeladene Kartendaten importieren</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="203"/>
      <source>Scryfall card data (*.json, *.json.gz)</source>
      <translation>Scryfall-Kartendaten (*.json, *.json.gz)</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="211"/>
      <source>Selected location is not a file</source>
      <translation>Ausgewählter Ort ist keine Datei</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="212"/>
      <source>Cannot find the selected file:
{location}</source>
      <translation>Die ausgewählte Datei konnte nicht gefunden werden:
{location}</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="17"/>
      <source>Open debug log directory</source>
      <translation>Debug-Protokollverzeichnis öffnen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="27"/>
      <source>Enable writing a log file to disk</source>
      <translation>Aktiviere das Schreiben einer Protokolldatei</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="34"/>
      <source>Cutelog is a live log event viewer that can be used to monitor events in real-time.</source>
      <translation>Cutelog ist ein Live-Protokoll-Ereignisbetrachter, der genutzt werden kann, um Ereignisse im Programm in Echtzeit zu überwachen.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="37"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;See &lt;a href=&quot;https://github.com/busimus/cutelog&quot;&gt;&lt;span style=&quot; text-decoration: underline; color:#2980b9;&quot;&gt;https://github.com/busimus/cutelog&lt;/span&gt;&lt;/a&gt; for details about Cutelog.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Siehe &lt;a href=&quot;https://github.com/busimus/cutelog&quot;&gt;&lt;span style=&quot; text-decoration: underline; color:#2980b9;&quot;&gt;https://github.com/busimus/cutelog&lt;/span&gt;&lt;/a&gt; für Details zu Cutelog.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="40"/>
      <source>Enable Cutelog integration</source>
      <translation>Cutelog-Integration aktivieren</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="47"/>
      <source>Download card data as file</source>
      <translation>Kartendaten als Datei herunterladen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="64"/>
      <source>Event severity that gets logged to file:</source>
      <translation>Ereignis-Schweregrad, ab dem in Datei protokolliert wird:</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="74"/>
      <source>Only write events with the given severity level and higher to the log file.</source>
      <translation>Schreibt nur Ereignisse mit dem angegebenen oder höherem Schweregrad ins Protokoll.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="81"/>
      <source>Debug settings (Changing these require an application restart)</source>
      <translation>Fehlersuch-Einstellungen (Ändern dieser Einstellungen erfordert einen Neustart der Anwendung)</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="101"/>
      <source>Import card data from file</source>
      <translation>Kartendaten aus Datei importieren</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="117"/>
      <source>Open the Cutelog homepage</source>
      <translation>Öffne die Cutelog-Homepage</translation>
    </message>
  </context>
  <context>
    <name>DeckImportWizard</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="648"/>
      <source>Import a deck list</source>
      <comment>Window title</comment>
      <translation>Deckliste importieren</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="675"/>
      <source>Oversized cards present</source>
      <comment>Message box title. Shown when the deck list contains likely unwanted oversized cards.</comment>
      <translation>Übergroße Karten vorhanden</translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="681"/>
      <source>There are %n possibly oversized cards in the deck list that may not fit into a deck, when printed out.

Continue and use these cards as-is?</source>
      <comment>Message box body text. Shown when the deck list contains likely unwanted oversized cards.</comment>
      <translation>
        <numerusform>Es gibt eine möglicherweise übergroße Karte in der Deckliste, die nach dem Ausdrucken nicht in ein Deck passen könnte.

Trotzdem mit der Deckliste fortfahren?</numerusform>
        <numerusform>Es gibt %n möglicherweise übergroße Karten in der Deckliste, die nach dem Ausdrucken nicht in ein Deck passen könnten.

Trotzdem mit der Deckliste fortfahren?</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="690"/>
      <source>Incompatible file selected</source>
      <comment>Message box title. Shown when trying to parse a deck list returns no results.</comment>
      <translation>Inkompatible Datei ausgewählt</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="694"/>
      <source>Unable to parse the given deck list, no results were obtained.
Maybe you selected the wrong deck list type?</source>
      <comment>Message box body text. Shown when trying to parse a deck list returns no results.</comment>
      <translation>Die gegebene Deck-Liste konnte nicht analysiert werden. Es wurden keine Karten gefunden.
Vielleicht haben Sie den falschen Decklistentyp ausgewählt?</translation>
    </message>
  </context>
  <context>
    <name>DecklistImportSettingsPage</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="223"/>
      <source>Deck list import</source>
      <translation>Decklisten-Import</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="223"/>
      <source>Configure the deck list importer</source>
      <translation>Den Decklisten-Import konfigurieren</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="233"/>
      <source>Select default deck list search path</source>
      <translation>Wähle den Standardsuchpfad für Decklisten</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="17"/>
      <source>Browse …</source>
      <translation>Durchsuchen …</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="30"/>
      <source>Deck list search path</source>
      <translation>Suchpfad für Decklisten</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="37"/>
      <source>The import wizard can remove basic lands fully- or semi-automatic.
These settings control the removal behavior.</source>
      <translation>Diese Einstellungen steuern ob, und wie der Importassistent Standardländer vollständig oder halbautomatisch entfernt.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="41"/>
      <source>Control the one-click or automatic basic land removal</source>
      <translation>Konfiguriert die automatische Entfernung von Standardländern</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="47"/>
      <source>If enabled, basic lands are automatically removed from deck lists.
If disabled, the deck import wizard keeps them by default,
but offers the removal via a single button click.</source>
      <extracomment>Tooltip</extracomment>
      <translation>Falls aktiviert, werden Standardländer automatisch aus Decklisten entfernt.
Wenn deaktiviert, behält der Decklisten-Import-Assistent Standardländer bei
und bietet das Entfernen mit einem Klick an.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="52"/>
      <source>Fully automatically remove basic lands</source>
      <translation>Standardländer vollständig automatisch entfernen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="59"/>
      <source>When enabled, treat Wastes like any other basic land</source>
      <extracomment>Tooltip</extracomment>
      <translation>Wenn aktiviert, behandele Ödnisse wie jedes andere Standardland</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="62"/>
      <source>Removal includes Wastes</source>
      <translation>Auch Ödnisse entfernen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="69"/>
      <source>When enabled, treat Snow-Covered basic lands like any other basic land</source>
      <extracomment>Tooltip</extracomment>
      <translation>Wenn aktiviert, behandele schneebedeckte Standardländer wie jedes andere Standardland</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="72"/>
      <source>Removal includes Snow-Covered Basic lands</source>
      <translation>Auch Schneebedeckte Standardländer entfernen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="82"/>
      <source>These options control the deck list import function.</source>
      <translation>Diese Optionen steuern die Importfunktion für Decklisten.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="89"/>
      <source>Not all deck list formats always contain complete data.
These options set the default behavior when encountering ambiguous card</source>
      <translation>Nicht alle Decklistenformate enthalten immer vollständige Daten.
Diese Optionen setzen das Standardverhalten bei mehrdeutigen Karten</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="93"/>
      <source>Control print selection in ambiguous cases</source>
      <translation>Druckauswahl in mehrdeutigen Fällen steuern</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="102"/>
      <source>When automatically selecting a printing, prefer printings with already downloaded images over other possible printings.</source>
      <translation>Beim automatischen Auswählen eines Druckes solche mit bereits heruntergeladenen Bildern bevorzugen.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="105"/>
      <source>Prefer printings with already downloaded images</source>
      <translation>Bevorzuge Drucke mit bereits heruntergeladenen Bildern</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="112"/>
      <source>Always enable automatic deck list translation when importing deck lists.
This avoids adding foreign language cards, if the deck list happens to contain some.</source>
      <translation>Beim Import von Decklisten immer die automatische Übersetzung aktivieren.
Dies vermeidet das Hinzufügen von Karten in Fremdsprachen, falls die Deckliste einige enthält.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="116"/>
      <source>Enable translating imported deck lists by default</source>
      <translation>Importierte Decklisten standardmäßig übersetzen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="123"/>
      <source>Not all deck list formats always contain complete data to identify exact printings.
If enabled, choose an arbitrary printing, instead of failing to identify such cards.
With some deck list formats, this option is always enabled.</source>
      <translation>Nicht alle Decklistenformate enthalten immer vollständige Daten, um Drucke exakt zu identifizieren.
Wenn aktiviert, wählt die Anwendung einen beliebigen, passenden Druck, anstatt solche Karten nicht zu identifizieren.
Bei einigen Decklistenformaten ist diese Option immer aktiviert.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="128"/>
      <source>Automatically select a printing</source>
      <translation>Automatisch einen Druck auswählen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="138"/>
      <source>If set, use this as the default location for loading deck lists. Your webbrowser’s download directory is a good choice.</source>
      <translation>Standardpfad zum Laden von Decklisten. Das Downloadverzeichnis Ihres Webbrowsers ist eine gute Wahl.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="144"/>
      <source>Path to a directory</source>
      <translation>Pfad zu einem Verzeichnis</translation>
    </message>
  </context>
  <context>
    <name>DefaultDocumentLayoutSettingsPage</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="513"/>
      <source>Default document settings</source>
      <translation>Standardeinstellungen für Dokumente</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="516"/>
      <source>Set the default document settings used for new documents,
like page size, margins, spacings, etc.</source>
      <translation>Standardeinstellungen für Dokumente setzen,
wie Papiergröße, Randabstände, Kartenabstände, usw.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="520"/>
      <source>Default settings for new documents</source>
      <translation>Standardeinstellungen für neue Dokumente</translation>
    </message>
  </context>
  <context>
    <name>Document</name>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="107"/>
      <source>Card name</source>
      <comment>Table header</comment>
      <translation>Kartenname</translation>
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
      <translation>Sammler #</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="110"/>
      <source>Language</source>
      <comment>Table header</comment>
      <translation>Sprache</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="111"/>
      <source>Image</source>
      <comment>Table header</comment>
      <translation>Bild</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="112"/>
      <source>Side</source>
      <comment>Table header</comment>
      <translation>Seite</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="204"/>
      <source>Double-click on entries to
switch the selected printing.</source>
      <translation>Doppelklicken Sie auf Einträge, um den Ausdruck
zu wechseln.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="416"/>
      <source>Page {current}/{total}</source>
      <comment>Tooltip. Shown when hovering over a page in the page list</comment>
      <translation>Seite {current}/{total}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="448"/>
      <source>Front</source>
      <comment>Magic card side</comment>
      <translation>Vorderseite</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="448"/>
      <source>Back</source>
      <comment>Magic card side</comment>
      <translation>Rückseite</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="513"/>
      <source>Empty Placeholder</source>
      <comment>Card name of the blank placeholder that can be added to keep slots on a page free.</comment>
      <translation>Leerer Platzhalter</translation>
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
      <translation>Einstellungen des aktuellen Dokuments ändern</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="395"/>
      <source>These settings only affect the current document</source>
      <comment>Shown within the dialog to indicate the scope of the presented settings</comment>
      <translation>Diese Einstellungen betreffen nur das aktuelle Dokument</translation>
    </message>
  </context>
  <context>
    <name>ExportCardImagesDialog</name>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="17"/>
      <source>Export card images</source>
      <translation>Kartenbilder exportieren</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="29"/>
      <source>Browse …</source>
      <translation>Durchsuchen …</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="52"/>
      <source>Custom cards</source>
      <translation>Inoffizielle Karten</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="66"/>
      <source>Output directory:</source>
      <translation>Speicherort:</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="73"/>
      <source>Official cards</source>
      <translation>Offizielle Karten</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="83"/>
      <source>Which card images should be exported?</source>
      <translation>Welche Karten sollen exportiert werden?</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="93"/>
      <source>Path to a directory</source>
      <translation>Pfad zu einem Verzeichnis</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="472"/>
      <source>Select card image export location</source>
      <comment>File dialog window title</comment>
      <translation>Speicherort für Kartenbild-Export auswählen</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="523"/>
      <source>Copy failed for {card_name}! Disk detached/full? Aborting.</source>
      <comment>Error message shown to the user when exporting cards to a directory fails.</comment>
      <translation>Kopieren von {card_name} fehlgeschlagen! Speicherziel entfernt/voll? Breche ab.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="555"/>
      <source>Write failed for {card_name}! Disk detached/full? Aborting.</source>
      <comment>Error message shown to the user when exporting cards to a directory fails.</comment>
      <translation>Schreiben des Bilds von {card_name} fehlgeschlagen! Speicherziel entfernt/voll? Breche ab.</translation>
    </message>
  </context>
  <context>
    <name>ExportSettingsPage</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="589"/>
      <source>Export settings</source>
      <translation>Exporteinstellungen</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="589"/>
      <source>Configure the PDF/PNG export</source>
      <translation>PDF/PNG-Export konfigurieren</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="629"/>
      <source>Select default export location</source>
      <translation>Standardpfad für Exporte auswählen</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="639"/>
      <source>Select PNG background color</source>
      <translation>PNG-Hintergrundfarbe wählen</translation>
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
      <translation>PDF-Dokumente automatisch aufteilen, wenn sie länger als diese Anzahl von Seiten werden.
Setzen Sie den Wert auf Null, um dies zu deaktivieren.


Wenn Sie PDF-Dokumente über ein direkt an den Drucker angeschlossenes USB-Flash-Laufwerk drucken,
weigert sich der Drucker möglicherweise, Dokumente zu drucken, die eine gewisse Größenbeschränkung überschreiten.
Um diese Einschränkung zu umgehen, können Sie diese Option aktivieren,
und die Anzahl der Seiten pro PDF begrenzen. Wenn das Dokument mehr Seiten hat,
wird es automatisch in mehrere PDF-Dokumente exportiert.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="34"/>
      <source> pages</source>
      <translation> Seiten</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="44"/>
      <source>Browse…</source>
      <translation>Durchsuchen …</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="57"/>
      <source>If enabled, landscape documents are rotated by 90° to portrait mode during export.
Enable this, if printing from PDFs in landscape format results in portrait printouts with cropped-off sides.

Enabling this may cause the cut helper lines to flicker or not show in some PDF viewers.
So only enable this, if actually required.</source>
      <translation>Wenn aktiviert, werden Querformat-Dokumente stattdessenum 90° gedreht im Hochformat exportiert.
Aktivieren Sie dies, wenn das Drucken von Querformat-Dokumenten zu Ausdrucken im Hochformat mit abgeschnittenen Seiten führt.

Aktivieren kann dazu führen, dass die Schnitthilfslinien in einigen PDF-Anzeigeprogrammen fehlerhaft oder gar nicht angezeigt werden.
Aktivieren Sie dies also nur, wenn es tatsächlich erforderlich ist.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="64"/>
      <source>Enable landscape workaround: Rotate landscape pages by 90°</source>
      <translation>Querformat-Workaround: Querformat-Dokumente um 90° drehen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="74"/>
      <location filename="../ui/settings_window/export_settings_page.ui" line="90"/>
      <source>If set, use this as the default location for saving exported PDF documents.</source>
      <translation>Standard-Speicherort für exportierte PDFs.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="80"/>
      <source>Path to a directory</source>
      <translation>Pfad zu einem Verzeichnis</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="93"/>
      <source>Export path</source>
      <translation>Exportpfad</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="116"/>
      <source>PNG background color</source>
      <translation>PNG Hintergrundfarbe</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="137"/>
      <source>Split PDF documents longer than</source>
      <translation>PDF-Dokumente länger als … aufteilen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="154"/>
      <source>Background color used for documents exported as PNG images.</source>
      <translation>Hintergrundfarbe für als PNG exportierte Dokumente.</translation>
    </message>
  </context>
  <context>
    <name>FileDownloadTask</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="161"/>
      <source>Downloading card data:</source>
      <comment>Progress bar label text</comment>
      <translation>Kartendaten herunterladen:</translation>
    </message>
  </context>
  <context>
    <name>FileStreamTask</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="265"/>
      <source>Importing card data from disk:</source>
      <comment>Progress bar label text</comment>
      <translation>Kartendaten aus Datei importieren:</translation>
    </message>
  </context>
  <context>
    <name>FilterSetupPage</name>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="14"/>
      <source>Cleanup locally stored card images</source>
      <translation>Lokal gespeicherte Kartenbilder bereinigen</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="17"/>
      <source>This wizard can be used to remove unwanted card images currently stored on your computer. You can enable automatic cleanup conditions below, to preselect images for removal.</source>
      <translation>Dieser Assistent kann benutzt werden, um lokal gespeicherte, aber unerwünschte Kartenbilder zu löschen. Sie können die Auswahlkriterien aktivieren, um automatisch Bilder zur Löschung vorauszuwählen.</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="23"/>
      <source>Delete everything</source>
      <translation>Alle gespeicherten Bilder löschen</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="33"/>
      <source>Select images for removal based on any matching criterion.</source>
      <translation>Wählen Sie Bilder zum Entfernen auf der Grundlage eines zutreffenden Kriteriums.</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="36"/>
      <source>Select images for deletion, that are …</source>
      <translation>Wählen Sie Bilder zum Löschen aus, die … sind.</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="42"/>
      <source>Used in prints and PDFs less often than:</source>
      <translation>In Ausdrucken und exportierten PDFs seltener verwendet als:</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="49"/>
      <source>Not used in prints for:</source>
      <translation>Nicht in Ausdrucken verwendet seit:</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="59"/>
      <source> days</source>
      <translation> Tage</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="75"/>
      <source> times</source>
      <translation> mal</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="88"/>
      <source>Card images may become unknown, if printings are removed by Scryfall.
This filter also applies to cards and printings hidden by a card filter in the settings.
For example, if you downloaded images of silver-bordered cards and then configured the program to hide those,
all these images become hidden and will be removed.</source>
      <translation>Kartenbilder können verwaisen, wenn Drucke durch Scryfall entfernt werden.
Dieser Filter gilt auch für Karten und Drucke, die durch einen Kartenfilter in den Einstellungen versteckt sind.
Zum Beispiel, wenn Sie Bilder von silberrandigen Karten heruntergeladen und dann das Programm so konfiguriert haben, dass diese versteckt werden, sind all diese Bilder versteckt und werden entfernt.</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="94"/>
      <source>Unknown or belong to hidden printings</source>
      <translation>Unbekannt oder zu versteckten Drucken gehörend</translation>
    </message>
  </context>
  <context>
    <name>GeneralSettingsPage</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="292"/>
      <source>General settings</source>
      <translation>Allgemeine Einstellungen</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="299"/>
      <source>Horizontal layout</source>
      <translation>Horizontales Layout</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="300"/>
      <source>Columnar layout</source>
      <translation>Spaltenlayout</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="301"/>
      <source>Tabbed layout</source>
      <translation>Layout in Tabs</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="304"/>
      <source>System default</source>
      <translation>Standardsprache des Systems</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="305"/>
      <source>English (US) [{progress}%]</source>
      <translation>Englisch (US) [{progress}%]</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="306"/>
      <source>German [{progress}%]</source>
      <translation>Deutsch [{progress}%]</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="307"/>
      <source>French [{progress}%]</source>
      <translation>Französisch [{progress}%]</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="316"/>
      <source>Select default save location</source>
      <comment>File picker title text</comment>
      <translation>Standardspeicherort auswählen</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="324"/>
      <source>Select custom card search path</source>
      <comment>File picker title text</comment>
      <translation>Suchpfad für Bilder inoffizieller Karten wählen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="17"/>
      <source>Look &amp;&amp; Feel (Changing most of these require an application restart)</source>
      <extracomment>Settings section header</extracomment>
      <translation>Look &amp;&amp; Feel (Ändern der meisten dieser Einstellungen erfordert einen Neustart der Anwendung)</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="23"/>
      <source>Application language</source>
      <translation>Sprache der Anwendung</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="30"/>
      <source>Main window layout</source>
      <translation>Hauptfenster-Layout</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="40"/>
      <source>Open the main window maximized</source>
      <extracomment>On/off setting</extracomment>
      <translation>Hauptfenster maximiert öffnen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="53"/>
      <source>Horizontal adds a wide, horizontal search area above the currently edited page, and is best for taller screens, like 4:3 or 3:2.
Columnar organizes the main window content in four columns, and is best for (ultra-)wide screens.
Tabbed uses tabs to only show parts of the main window at a time. Best used with small screens in portrait mode (i.e. 9:16), otherwise not recommended.</source>
      <extracomment>Tooltip for the main window layout selector. References the values by name</extracomment>
      <translation>"Horizontal" fügt einen breiten, horizontalen Suchbereich über der gerade bearbeiteten Seite hinzu und ist am besten für höhere Bildschirme, wie z.B. 4:3 oder 3:2.
"Spalten" organisiert den Inhalt des Hauptfensters in vier Spalten und eignet sich am besten für (ultra)weite Bildschirme.
"Tabs" verwendet Tabs, um jederzeit nur einen Teil des Hauptfensters anzuzeigen. Am besten mit kleinen Bildschirmen im Hochformat (z.B. 9:16), ansonsten nicht empfohlen.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="69"/>
      <source>Open all wizards and dialogs maximized</source>
      <extracomment>On/off setting</extracomment>
      <translation>Alle Assistenten und Dialoge maximiert öffnen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="79"/>
      <source>Double-faced cards</source>
      <extracomment>Settings section header</extracomment>
      <translation>Doppelseitige Karten</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="85"/>
      <source>When adding double-faced cards, automatically add the same number of copies of the other side.
Uses the appropriate, matching other card side.
Uncheck to disable this automatism.</source>
      <translation>Beim Hinzufügen von doppelseitigen Karten automatisch die gleiche Anzahl von Kopien der anderen Seite hinzufügen.
Verwendet die zugehörige, passende andere Kartenseite.
Deaktivieren um diesen Automatismus zu deaktivieren.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="90"/>
      <source>Automatically add the other side of double-faced cards</source>
      <translation>Automatisch die andere Seite von doppelseitigen Karten hinzufügen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="100"/>
      <source>These paths are selected by default when browsing the file system for files</source>
      <translation>Diese Pfade werden standardmäßig beim Durchsuchen des Dateisystems nach Dateien ausgewählt</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="103"/>
      <source>Default save paths</source>
      <extracomment>Settings section header</extracomment>
      <translation>Standardspeicherpfade</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="109"/>
      <location filename="../ui/settings_window/general_settings_page.ui" line="270"/>
      <source>Browse…</source>
      <extracomment>Button tooltip</extracomment>
      <translation>Durchsuchen…</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="122"/>
      <source>Document save path</source>
      <translation>Dokumentenspeicherpfad</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="132"/>
      <source>If set, use this as the default location for saving documents.</source>
      <translation>Wenn gesetzt, verwende dies als Standard-Speicherort für Dokumente.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="138"/>
      <location filename="../ui/settings_window/general_settings_page.ui" line="260"/>
      <source>Path to a directory</source>
      <extracomment>Line editor placeholder text</extracomment>
      <translation>Pfad zu einem Verzeichnis</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="154"/>
      <source>Automatic update checks</source>
      <extracomment>Settings section header</extracomment>
      <translation>Automatisch nach Aktualisierungen suchen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="160"/>
      <source>Update checks are performed at application start, if enabled.</source>
      <translation>Suche nach Aktualisierungen wird beim Anwendungsstart durchgeführt, sofern aktiviert.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="167"/>
      <source>If enabled, check for application updates, and notify if new updates are available for installation.</source>
      <translation>Falls aktiviert, beim Start automatisch nach Anwendungsaktualisierungen suchen und bei verfügbaren Aktualisierungen benachrichtigen.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="170"/>
      <source>Check for application updates</source>
      <translation>Nach Anwendungsaktualisierungen suchen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="180"/>
      <source>If enabled, query the Scryfall API if new cards are available. If so, offer to update the local card data.</source>
      <translation>Falls aktiviert, frage automatisch die Scryfall API ab, ob neue Karten verfügbar sind. Wenn ja, bieten wir an, die lokalen Kartendaten zu aktualisieren.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="183"/>
      <source>Check for new card data</source>
      <translation>Nach Aktualisierungen für die Kartendaten suchen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="202"/>
      <source>Language choices will default to the chosen language here.
Entries use the language codes as listed on Scryfall.

Note: Cards in deck lists use the language as given by the deck list. To overwrite, use the deck list translation option.</source>
      <translation>Kartenauswahl wird standardmäßig die hier gewählte Sprache verwenden.
Einträge verwenden die Sprachcodes wie auf Scryfall.

Hinweis: Decklistenimports verwenden die Sprache, wie in der Deckliste angegeben. Zum Überschreiben verwenden Sie die Option der Decklistenübersetzung.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="225"/>
      <source>Card language selected at application start and default language when enabling deck list translations</source>
      <translation>Beim Start der Anwendung ausgewählte Kartensprache und Standardsprache beim Aktivieren der Decklistenübersetzung</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="228"/>
      <source>Preferred card language:</source>
      <translation>Bevorzugte Kartensprache:</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="238"/>
      <source>Custom cards</source>
      <extracomment>Settings section header</extracomment>
      <translation>Inoffizielle Karten</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="244"/>
      <source>Default search path</source>
      <extracomment>Label next to a directory selector for custom cards</extracomment>
      <translation>Standardsuchpfad für inoffizielle Karten</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="254"/>
      <source>If set, search here for custom card images</source>
      <extracomment>Tooltip text</extracomment>
      <translation>Wenn gesetzt, wird standardmäßig hier nach Bildern von inoffiziellen Karten gesucht</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="283"/>
      <source>Enforce rounded corners for all imported custom cards</source>
      <extracomment>Tooltip text</extracomment>
      <translation>Erzwinge abgerundete Ecken für alle importierten, inoffiziellen Karten</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="286"/>
      <source>Force round corners</source>
      <extracomment>Custom card import related on/off setting.</extracomment>
      <translation>Runde Ecken erzwingen</translation>
    </message>
  </context>
  <context>
    <name>GroupedCentralWidget</name>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="20"/>
      <source>Add new cards:</source>
      <translation>Karten hinzufügen:</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="62"/>
      <source>All pages:</source>
      <translation>Alle Seiten:</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="72"/>
      <source>Move down</source>
      <translation>Schiebe runter</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="85"/>
      <source>Move up</source>
      <translation>Schiebe hoch</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="98"/>
      <source>Remove selected</source>
      <translation>Ausgewählte entfernen</translation>
    </message>
  </context>
  <context>
    <name>HidePrintingsPage</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="453"/>
      <source>Hide printings</source>
      <translation>Drucke verbergen</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="453"/>
      <source>Hide unwanted printings</source>
      <translation>Unerwünschte Kartenvarianten verbergen</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="475"/>
      <source>View cards hidden by this filter on the Scryfall website.</source>
      <comment>Tooltip text on a button next to a printing filter</comment>
      <translation>Sehen Sie sich die durch diesen Filter versteckten Karten auf Scryfall an.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/hide_printings_page.ui" line="17"/>
      <source>These options allow hiding unwanted cards and printings. Hidden printings are treated as though they don’t exist. They can’t be found in the card search and are automatically replaced in loaded documents or imported deck lists, if possible. If all printings of a card are hidden, it won’t be available at all.</source>
      <translation>Diese Optionen erlauben das Verstecken unerwünschter Karten und Drucke. Diese werden so behandelt, als gäbe es sie nicht. Sie können nicht in der Kartensuche gefunden werden und werden nach Möglichkeit automatisch in geladenen Dokumenten oder importierten Decklisten ersetzt. Wenn alle Ausdrucke einer Karte versteckt sind, wird sie überhaupt nicht verfügbar sein.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/hide_printings_page.ui" line="46"/>
      <source>Hide specific sets: Add set codes as listed on Scryfall, for example LEA or 2X2. Separate multiple entries with spaces or line breaks. All words not matching an exact set code are ignored.</source>
      <translation>Verstecke bestimmte Sets: Füge Set-Codes hinzu, wie auf Scryfall aufgeführt, zum Beispiel LEA oder 2X2. Trennen Sie mehrere Einträge mit Leerzeichen oder Zeilenumbrüchen. Alle Wörter, die keinem exakten Code entsprechen, werden ignoriert.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/hide_printings_page.ui" line="62"/>
      <source>Example:

LEA DDU TC13 J21</source>
      <translation>Beispiel:

LEA DDU TC13 J21</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/hide_printings_page.ui" line="70"/>
      <source>No sets currently hidden.</source>
      <translation>Derzeit sind keine Sets versteckt.</translation>
    </message>
  </context>
  <context>
    <name>HorizontalAddCardWidget</name>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="35"/>
      <source>Language:</source>
      <extracomment>Card language. Next to the language selection widget</extracomment>
      <translation>Sprache:</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="51"/>
      <source>Card Name</source>
      <translation>Kartenname</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="57"/>
      <source>Filter the list below. Use  % (Percent signs) as wildcards matching any number of characters.</source>
      <translation>Filter für die Liste unten. Verwenden Sie % (Prozentzeichen) als Platzhalter
für beliebig viele Zeichen.</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="60"/>
      <source>Filter card names</source>
      <translation>Kartennamen filtern</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="70"/>
      <source>The filtered list of card names in the currently selected language. Click on an entry to select it and choose a printing.</source>
      <translation>Die gefilterte Liste der Kartennamen in der aktuell ausgewählten Sprache. Klicken Sie auf einen Eintrag, um einen Druck dieser Karte auszuwählen.</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="95"/>
      <source>The sets in which the currently selected card was printed.</source>
      <translation>Die Sets, in denen die aktuell ausgewählte Karte gedruckt wurde.</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="98"/>
      <source>Set</source>
      <translation>Set</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="104"/>
      <source>Filter set names</source>
      <translation>Setnamen filtern</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="136"/>
      <source>Collector Number</source>
      <translation>Sammlernummer</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="164"/>
      <source>Copies:</source>
      <extracomment>Number of copies to add. Next to the number input field</extracomment>
      <translation>Kopien:</translation>
    </message>
  </context>
  <context>
    <name>ImageDownloadTask</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/image_downloader.py" line="135"/>
      <source>Downloading &apos;{card_name}&apos;:</source>
      <comment>Progress bar label text</comment>
      <translation>Lade '{card_name}' herunter:</translation>
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
      <translation>Sammler #</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="145"/>
      <source>Is Hidden</source>
      <comment>Table header. Shows if this printing is hidden by a card filter</comment>
      <translation>Versteckt</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="147"/>
      <source>Front/Back</source>
      <comment>Table header. Shows if this is the front or back side of a card</comment>
      <translation>Vorder-/Rückseite</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="149"/>
      <source>High resolution?</source>
      <comment>Table header. Shows if the card has high-res images</comment>
      <translation>Hohe Qualität?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="151"/>
      <source>Size</source>
      <comment>Table header. File size in KiB/MiB</comment>
      <translation>Größe</translation>
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
      <translation>Dateipfad</translation>
    </message>
  </context>
  <context>
    <name>KnownCardRow</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="100"/>
      <source>Yes</source>
      <comment>This card is hidden by a card filter</comment>
      <translation>Ja</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="102"/>
      <source>No</source>
      <comment>This card is visible and not affected by a card filter</comment>
      <translation>Nein</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="106"/>
      <source>This printing is hidden by an enabled card filter
and is thus unavailable for printing.</source>
      <comment>Tooltip for cells with hidden cards</comment>
      <translation>Dieser Druck wird durch einen aktivierten Kartenfilter
versteckt und ist daher nicht verfügbar.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="109"/>
      <source>Front</source>
      <comment>Card side</comment>
      <translation>Vorderseite</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="110"/>
      <source>Back</source>
      <comment>Card side</comment>
      <translation>Rückseite</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="116"/>
      <source>Yes</source>
      <comment>This card has high-resolution images available</comment>
      <translation>Ja</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="118"/>
      <source>No</source>
      <comment>This card only has low-resolution images available.</comment>
      <translation>Nein</translation>
    </message>
  </context>
  <context>
    <name>LoadDocumentDialog</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="229"/>
      <source>Load MTGProxyPrinter document</source>
      <comment>File dialog window title</comment>
      <translation>MTGProxyPrinter-Dokument laden</translation>
    </message>
  </context>
  <context>
    <name>LoadListPage</name>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="17"/>
      <source>Import a deck list for printing</source>
      <translation>Deckliste zum Drucken importieren</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="20"/>
      <source>Load a deck file from disk or paste deck list in the text field below</source>
      <translation>Laden Sie eine Deckliste von der Festplatte oder fügen Sie eine in das folgende Textfeld ein</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="42"/>
      <source>Paste a link to a public deck list here. Hover to see supported sites.</source>
      <translation>Fügen Sie hier einen Link zu einer öffentlichen Deckliste ein. Hover um unterstützte Seiten zu sehen.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="52"/>
      <source>Scryfall search query</source>
      <translation>Scryfall-Suchanfrage</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="59"/>
      <source>If checked, choose an arbitrary printing, if a unique printing is not identified.
If unchecked, each ambiguous card is ignored and reported as unrecognized.</source>
      <translation>Wenn aktiviert, wähle einen beliebigen Druck, wenn kein Druck eindeutig identifiziert wird.
Wenn deaktiviert, wird jede mehrdeutige Karte ignoriert und als unbekannt betrachtet.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="63"/>
      <source>Guess printings for ambiguous entries in the deck list</source>
      <translation>Bei mehrdeutigen Einträge in der Deck-Liste automatisch einen Druck auswählen</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="79"/>
      <source>Download result</source>
      <extracomment>Download the entered Scryfall search query as a deck list</extracomment>
      <translation>Ergebnis herunterladen</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="89"/>
      <source>Paste your deck list here or use one of the actions above</source>
      <translation>Fügen Sie hier Ihre Deckliste ein oder laden Sie eine Datei mit den obigen Aktionen</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="99"/>
      <source>When an exact printing is not determined or card translation is requested, choose a printing that is already downloaded, if possible.
Enabling this can potentially save disk space and download volume, based on the images already downloaded.</source>
      <translation>Wenn ein exakter Druck nicht ermittelt wird oder eine Kartenübersetzung verlangt wird, wähle nach Möglichkeit einen Druck, der bereits heruntergeladen wurde.
Aktivieren kann möglicherweise Speicherplatz auf der Festplatte und Datenvolumen sparen, basierend auf den bereits heruntergeladenen Bildern.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="103"/>
      <source>When choosing a printing, prefer ones with already downloaded images</source>
      <translation>Bevorzuge beim automatischen Auswählen oder Übersetzen Drucke mit bereits heruntergeladenen Bildern</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="116"/>
      <source>Translate deck list to:</source>
      <translation>Deckliste übersetzen in:</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="130"/>
      <source>Opens a file picker and lets you load a deck file from disk.</source>
      <translation>Öffnet eine Datei-Auswahl und lässt Sie eine Deckliste von der Festplatte laden.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="133"/>
      <source>Select deck list file</source>
      <extracomment>Lets the user select a file, and loads the content as a deck list</extracomment>
      <translation>Decklisten-Datei auswählen</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="152"/>
      <source>View result</source>
      <extracomment>View the entered Scryfall search query on the Scryfall website</extracomment>
      <translation>Ergebnis anzeigen</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="171"/>
      <source>Download deck list</source>
      <extracomment>On pressing the button, the deck list given by the entered URL is downloaded</extracomment>
      <translation>Deckliste herunterladen</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="119"/>
      <source>Supported websites:
{supported_sites}</source>
      <comment>Tooltip text</comment>
      <translation>Unterstützte Webseiten:
{supported_sites}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="169"/>
      <source>Overwrite existing deck list?</source>
      <comment>Message box title</comment>
      <translation>Vorhandene Deckliste überschreiben?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="170"/>
      <source>Selecting a file will overwrite the existing deck list. Continue?</source>
      <comment>Message box body text</comment>
      <translation>Das Auswählen einer Datei überschreibt die vorhandene Deckliste. Fortfahren?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="177"/>
      <source>Select deck file</source>
      <comment>File selection dialog window title</comment>
      <translation>Decklisten-Datei auswählen</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="187"/>
      <source>All files (*)</source>
      <comment>File type filter value</comment>
      <translation>Alle Dateien (*)</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="198"/>
      <source>All Supported </source>
      <comment>File type filter value</comment>
      <translation>Alle unterstützten </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="213"/>
      <source>Verify that the URL is valid, reachable, and that the deck list is set to public.
This program cannot download private deck lists. Please note, that setting deck lists to
public may take a minute or two to apply.</source>
      <comment>Error message shown when trying to download a deck list from a seemingly valid URL fails</comment>
      <translation>Vergewissern Sie sich, dass die URL gültig und erreichbar ist, und dass die Deckliste öffentlich zugänglich ist.
Dieses Programm kann private Decklisten nicht herunterladen.
Bitte beachten Sie, dass das Anwenden der Umstellung auf
Öffentlich etwas dauern kann.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="220"/>
      <source>Overwrite existing deck list?</source>
      <comment>Message box title. Shown when loading a deck list would overwrite existing text</comment>
      <translation>Vorhandene Deckliste überschreiben?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="223"/>
      <source>Downloading a deck list will overwrite the existing deck list. Continue?</source>
      <comment>Message box body text. Shown when loading a deck list would overwrite existing text</comment>
      <translation>Das Herunterladen einer Deckliste überschreibt die vorhandene Deckliste. Fortfahren?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="235"/>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="243"/>
      <source>Deck list download failed</source>
      <comment>Message box title. Shown when downloading failed</comment>
      <translation>Download der Deckliste fehlgeschlagen</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="238"/>
      <source>Download failed with HTTP error {http_error_code}.

{bad_request_msg}</source>
      <comment>Message box body text. Shown when the server returns an error code</comment>
      <translation>Download fehlgeschlagen mit HTTP-Fehler {http_error_code}.

{bad_request_msg}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="249"/>
      <source>Download failed.

Check your internet connection, verify that the URL is valid, reachable, and that the deck list is set to public. This program cannot download private deck lists. If this persists, please report a bug in the issue tracker on the homepage.</source>
      <comment>Message box body text. Shown when an unknown error occurred.</comment>
      <translation>Download fehlgeschlagen.

Überprüfen Sie Ihre Internetverbindung, ob die URL gültig und erreichbar ist, und dass die Deckliste öffentlich ist. Dieses Programm kann keine privaten Deck-Listen herunterladen. Falls das Problem weiterhin besteht, melden Sie bitte einen Fehler im Issue-Tracker auf der Homepage.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="265"/>
      <source>Invalid Scryfall query entered, no result obtained</source>
      <comment>Message box body text</comment>
      <translation>Ungültige Scryfall-Abfrage eingegeben, keine Karten gefunden</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="278"/>
      <source>Unable to read file content</source>
      <comment>Message box title. Shown when the user-selected file is unreadable.</comment>
      <translation>Dateiinhalt konnte nicht gelesen werden</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="281"/>
      <source>Unable to read the content of file {file_path} as plain text.
Failed to load the content.</source>
      <comment>Message box body text. Shown when the user-selected file is unreadable.</comment>
      <translation>Kann den Inhalt der Datei {file_path} nicht als Text lesen.
Fehler beim Laden des Inhalts.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="293"/>
      <source>Load large file?</source>
      <comment>Message box title. Shown when the user-selected file is unreasonably large.</comment>
      <translation>Große Datei laden?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="297"/>
      <source>The selected file {file_path} is unexpectedly large ({formatted_size}). Load anyways?</source>
      <comment>Message box body text. Shown when the user-selected file is unreasonably large.</comment>
      <translation>Die ausgewählte Datei {file_path} ist mit {formatted_size} unerwartet groß. Trotzdem laden?</translation>
    </message>
  </context>
  <context>
    <name>LoadSaveDialog</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="186"/>
      <source>MTGProxyPrinter document (*.{default_save_suffix})</source>
      <comment>File type filter</comment>
      <translation>MTGProxyPrinter-Dokument (*.{default_save_suffix})</translation>
    </message>
  </context>
  <context>
    <name>MTGArenaParser</name>
    <message>
      <location filename="../../mtg_proxy_printer/decklist_parser/re_parsers.py" line="202"/>
      <source>Magic Arena deck file</source>
      <translation>Magic Arena Deckliste</translation>
    </message>
  </context>
  <context>
    <name>MTGOnlineParser</name>
    <message>
      <location filename="../../mtg_proxy_printer/decklist_parser/re_parsers.py" line="236"/>
      <source>Magic Online (MTGO) deck file</source>
      <translation>Magic Online (MTGO) Deckliste</translation>
    </message>
  </context>
  <context>
    <name>MagicWorkstationDeckDataFormatParser</name>
    <message>
      <location filename="../../mtg_proxy_printer/decklist_parser/re_parsers.py" line="180"/>
      <source>Magic Workstation Deck Data Format</source>
      <translation>Magic Workstation Deck Data (mwDeck)</translation>
    </message>
  </context>
  <context>
    <name>MainWindow</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="227"/>
      <source>Undo:
{top_entry}</source>
      <translation>Rückgängig:
{top_entry}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="229"/>
      <source>Redo:
{top_entry}</source>
      <translation>Wiederholen:
{top_entry}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="284"/>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="298"/>
      <source>printing</source>
      <comment>This is passed as the {action} when asking the user about compacting the document if that can save pages</comment>
      <translation>dem Drucken</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="310"/>
      <source>exporting as a PDF</source>
      <comment>This is passed as the {action} when asking the user about compacting the document if that can save pages</comment>
      <translation>dem PDF-Export</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="323"/>
      <source>exporting as a PNG image sequence</source>
      <comment>This is passed as the {action} when asking the user about compacting the document if that can save pages</comment>
      <translation>exportieren als PNG-Bildsequenz</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="346"/>
      <source>Network error</source>
      <translation>Netzwerkfehler</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="348"/>
      <source>Operation failed, because a network error occurred.
Check your internet connection. Reported error message:

{message}</source>
      <translation>Vorgang fehlgeschlagen, da ein Netzwerkfehler aufgetreten ist.
Überprüfen Sie Ihre Internetverbindung. Fehlermeldung:

{message}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="354"/>
      <source>Error</source>
      <translation>Fehler</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="356"/>
      <source>Operation failed, because an internal error occurred.
Reported error message:

{message}</source>
      <translation>Vorgang fehlgeschlagen, da ein interner Fehler aufgetreten ist.
Berichtete Fehlermeldung:

{message}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="362"/>
      <source>Saving pages possible</source>
      <translation>Einsparen von Seiten möglich</translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="365"/>
      <source>It is possible to save %n pages when printing this document.
Do you want to compact the document now to minimize the page count prior to {action}?</source>
      <translation>
        <numerusform>Es ist möglich, %n Seite beim Drucken dieses Dokuments zu sparen.
Möchten Sie das Dokument jetzt komprimieren, um die Seitenanzahl vor {action} zu minimieren?</numerusform>
        <numerusform>Es ist möglich, %n Seiten beim Drucken dieses Dokuments zu sparen.
Möchten Sie das Dokument jetzt komprimieren, um die Seitenanzahl vor {action} zu minimieren?</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="378"/>
      <source>Download required Card data from Scryfall?</source>
      <translation>Benötigte Kartendaten von Scryfall herunterladen?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="383"/>
      <source>This program requires downloading additional card data from Scryfall to operate the card search.
Download the required data from Scryfall now?
Without the data, you can only print custom cards by drag&amp;dropping the image files onto the main window.</source>
      <translation>Dieses Programm erfordert das Herunterladen zusätzlicher Kartendaten von Scryfall, um die Kartensuche zu ermöglichen.
Jetzt die benötigten Daten von Scryfall herunterladen?
Ohne die Daten können Sie nur nutzererstellte Karten drucken, indem Sie die Bilddateien per Drag &amp; Drop in das Hauptfenster ziehen.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="427"/>
      <source>Document loading failed</source>
      <translation>Laden des Dokuments fehlgeschlagen</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="431"/>
      <source>Loading file &quot;{failed_path}&quot; failed. The file was not recognized as a {program_name} document. If you want to load a deck list, use the &quot;{function_text}&quot; function instead.
Reported failure reason: {reason}</source>
      <translation>Laden der Datei "{failed_path}" fehlgeschlagen. Die Datei wurde nicht als {program_name}-Dokument erkannt. Wenn Sie eine Deckliste laden möchten, verwenden Sie die "{function_text}"-Funktion stattdessen.
Berichteter Fehlergrund: {reason}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="440"/>
      <source>Unavailable printings replaced</source>
      <translation>Nicht verfügbare Drucke ersetzt</translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="444"/>
      <source>The document contained %n unavailable printings of cards that were automatically replaced with other printings. The replaced printings are unavailable, because they match a configured card filter.</source>
      <translation>
        <numerusform>Das Dokument enthielt einen nicht verfügbaren Druck einer Karte, der automatisch durch einen anderen Druck ersetzt wurden. Der ausgetauschten Druck ist nicht verfügbar, da er mit einem konfigurierten Kartenfilter übereinstimmt.</numerusform>
        <numerusform>Das Dokument enthielt %n nicht verfügbare Drucke von Karten, die automatisch durch andere Drucke ersetzt wurden. Die ausgetauschten Drucke sind nicht verfügbar, da sie mit einem konfigurierten Kartenfilter übereinstimmen.</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="449"/>
      <source>Unrecognized cards in loaded document found</source>
      <translation>Nicht erkannte Karten im geladenen Dokument gefunden</translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="453"/>
      <source>Skipped %n unrecognized cards in the loaded document. Saving the document will remove these entries permanently.

The locally stored card data may be outdated or the document was tampered with.</source>
      <translation>
        <numerusform>Eine unbekannte Karte im geladenen Dokument übersprungen. Speichern des Dokuments wird diese dauerhaft entfernen.

Die lokalen Kartendaten sind möglicherweise veraltet oder das Dokument wurde manipuliert.</numerusform>
        <numerusform>%n unbekannte Karten im geladenen Dokument übersprungen. Speichern des Dokuments wird diese dauerhaft entfernen.

Die lokalen Kartendaten sind möglicherweise veraltet oder das Dokument wurde manipuliert.</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="459"/>
      <source>Application update available. Visit website?</source>
      <translation>Anwendungsaktualisierung verfügbar. Website besuchen?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="463"/>
      <source>An application update is available: Version {newer_version}
You are currently using version {current_version}.

Open the {program_name} website in your web browser to download the new version?</source>
      <translation>Ein Anwendungs-Update ist verfügbar: Version {newer_version}
Sie verwenden derzeit Version {current_version}.

Die {program_name}-Webseite mit Ihrem Web-Browser besuchen, um die neue Version herunterzuladen?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="474"/>
      <source>New card data available</source>
      <translation>Neue Kartendaten verfügbar</translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="477"/>
      <source>There are %n new printings available on Scryfall. Update the local data now?</source>
      <translation>
        <numerusform>Es ist %n neue Karte auf Scryfall verfügbar. Lokale Daten jetzt aktualisieren?</numerusform>
        <numerusform>Es sind %n neue Karten auf Scryfall verfügbar. Lokale Daten jetzt aktualisieren?</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="490"/>
      <source>Check for application updates?</source>
      <translation>Nach Anwendungsaktualisierungen suchen?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="492"/>
      <source>Automatically check for application updates whenever you start {program_name}?</source>
      <translation>Beim Anwendungsstart automatisch nach Updates suchen?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="502"/>
      <source>Check for card data updates?</source>
      <translation>Suche nach Kartendaten-Updates?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="504"/>
      <source>Automatically check for card data updates on Scryfall whenever you start {program_name}?</source>
      <translation>Automatisch nach Kartenupdates auf Scryfall prüfen, wann immer Sie {program_name} starten?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="513"/>
      <source>{question}
You can change this later in the settings.</source>
      <translation>{question}
Sie können dies später in den Einstellungen ändern.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="14"/>
      <source>MTGProxyPrinter</source>
      <translation>MTGProxyPrinter</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="31"/>
      <source>Fi&amp;le</source>
      <translation>&amp;Datei</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="35"/>
      <source>Export</source>
      <translation>Exportieren …</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="59"/>
      <source>Application</source>
      <translation>Anwendung</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="73"/>
      <source>Edit</source>
      <translation>Bearbeiten</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="89"/>
      <source>Web links</source>
      <translation>Weblinks</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="106"/>
      <location filename="../ui/main_window.ui" line="327"/>
      <source>Show toolbar</source>
      <translation>Werkzeugleiste anzeigen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="135"/>
      <source>&amp;Quit</source>
      <translation>&amp;Beenden</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="138"/>
      <source>Ctrl+Q</source>
      <translation>Strg+Q</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="149"/>
      <source>&amp;Print</source>
      <translation>&amp;Drucken</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="152"/>
      <source>Print the current document</source>
      <translation>Aktuelles Dokument drucken</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="155"/>
      <source>Ctrl+P</source>
      <translation>Strg+P</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="163"/>
      <source>&amp;Show print preview</source>
      <translation>Druckvorschau</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="166"/>
      <source>Show print preview window</source>
      <translation>Druckvorschau anzeigen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="174"/>
      <source>&amp;Create PDF</source>
      <translation>PDF erzeugen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="177"/>
      <source>Create a PDF document</source>
      <translation>Als PDF-Dokument exportieren</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="185"/>
      <source>Discard page</source>
      <translation>Seite verwerfen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="188"/>
      <source>Discard this page.</source>
      <translation>Diese Seite verwerfen.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="196"/>
      <source>Settings</source>
      <translation>Einstellungen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="207"/>
      <source>Update card data</source>
      <translation>Kartendaten aktualisieren</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="215"/>
      <source>New Page</source>
      <translation>Neue Seite</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="218"/>
      <source>Add a new, empty page.</source>
      <translation>Neue, leere Seite hinzufügen.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="226"/>
      <source>Save</source>
      <translation>Speichern</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="229"/>
      <source>Ctrl+S</source>
      <translation>Strg+S</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="237"/>
      <source>New</source>
      <translation>Neu</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="240"/>
      <source>Ctrl+N</source>
      <translation>Strg+N</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="248"/>
      <source>Load</source>
      <translation>Laden</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="251"/>
      <source>Ctrl+L</source>
      <translation>Strg+L</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="259"/>
      <source>Save as …</source>
      <translation>Speichern unter …</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="264"/>
      <source>About …</source>
      <translation>Über …</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="272"/>
      <source>Show Changelog</source>
      <translation>Änderungsprotokoll anzeigen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="280"/>
      <source>Compact document</source>
      <translation>Dokument kompaktieren</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="283"/>
      <source>Minimize page count: Fill empty slots on pages by moving cards from the end of the document</source>
      <translation>Seitenzahl minimieren: Leerstellen auf Seiten durch das Verschieben von Karten vom Dokumentenende füllen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="291"/>
      <source>Edit document settings</source>
      <translation>Einstellungen dieses Dokuments</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="294"/>
      <source>Configure page size, margins, image spacings for the currently edited document.</source>
      <translation>Einstellungen des aktuellen Dokuments, wie Papiergröße, Rand- und Bildabstände anpassen.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="302"/>
      <source>Import deck list</source>
      <translation>Deckliste importieren</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="305"/>
      <source>Import a deck list from online sources</source>
      <translation>Eine Deckliste aus dem Internet importieren</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="313"/>
      <source>Cleanup card images</source>
      <translation>Kartenbilder bereinigen/löschen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="316"/>
      <source>Delete locally stored card images you no longer need.</source>
      <translation>Nicht mehr benötigte, gespeicherte Kartenbilder löschen.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="330"/>
      <source>Ctrl+M</source>
      <translation>Strg+M</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="338"/>
      <source>Download missing card images</source>
      <translation>Fehlende Kartenbilder herunterladen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="346"/>
      <source>Shuffle document</source>
      <translation>Dokument mischen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="349"/>
      <source>Randomly rearrange all card image.
If you want to quickly print a full deck for playing,
use this to reduce the initial deck shuffling required</source>
      <translation>Alle Karten zufällig neu anordnen.
Wenn Sie schnell ein komplettes Deck für das Spielen drucken möchten,
können Sie dies verwenden, um den Aufwand beim initialen Mischen zu reduzieren</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="362"/>
      <source>Undo</source>
      <translation>Rückgängig</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="373"/>
      <source>Redo</source>
      <translation>Wiederholen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="381"/>
      <source>Add empty card to page</source>
      <translation>Leere Karte zur Seite hinzufügen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="384"/>
      <source>Add an empty spacer filling a card slot</source>
      <translation>Ein Feld auf der aktuellen Seite leer halten</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="392"/>
      <source>Add custom cards</source>
      <translation>Inoffizielle Karten hinzufügen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="400"/>
      <source>Export as image sequence</source>
      <translation>Als Bildsequenz exportieren</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="403"/>
      <source>Export document as an image sequence</source>
      <translation>Dokument als Bildsequenz exportieren</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="411"/>
      <source>Export individual card images</source>
      <translation>Einzelne Kartenbilder exportieren</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="414"/>
      <source>Export all card images to a directory</source>
      <translation>Alle Kartenbilder in ein Verzeichnis exportieren</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="422"/>
      <source>Source Code</source>
      <translation>Quellcode</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="430"/>
      <source>Source Code (GitHub)</source>
      <translation>Quellcode (GitHub)</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="438"/>
      <source>Contribute Translations</source>
      <translation>Übersetzungen beitragen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="443"/>
      <source>Support development on Ko-Fi</source>
      <translation>Unterstütze die Entwicklung auf Ko-Fi</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="451"/>
      <source>Project on PyPI</source>
      <translation>Projekt auf PyPI</translation>
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
        <numerusform>Kann ein fehlendes Kartenbild nicht herunterladen.
Es wird in exportierten oder gedruckten Dokumenten fehlen.</numerusform>
        <numerusform>Kann %n fehlende Kartenbilder nicht herunterladen.
Diese werden in exportierten oder gedruckten Dokumenten fehlen.</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ObtainMissingImagesTask</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/image_downloader.py" line="279"/>
      <source>Fetching missing images:</source>
      <comment>Progress bar label text</comment>
      <translation>Fehlende Bilder herunterladen:</translation>
    </message>
  </context>
  <context>
    <name>PNGRenderer</name>
    <message>
      <location filename="../../mtg_proxy_printer/print.py" line="87"/>
      <source>Export as PNGs:</source>
      <comment>Progress bar label text</comment>
      <translation>Als PNGs exportieren:</translation>
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
        <numerusform>Kopie hinzufügen</numerusform>
        <numerusform>%n Kopien hinzufügen</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="122"/>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="140"/>
      <source>Add copies …</source>
      <comment>Context menu action: Add additional card copies to the document. User will be asked for a number</comment>
      <translation>Kopien hinzufügen …</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="125"/>
      <source>Generate DFC check card</source>
      <translation>Platzhalterkarte generieren</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="152"/>
      <source>All related cards</source>
      <translation>Alle zugehörigen Karten</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="161"/>
      <source>Add copies</source>
      <translation>Kopien hinzufügen</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="163"/>
      <source>Add copies of {card_name}</source>
      <comment>Asks the user for a number. Does not need plural forms</comment>
      <translation>Kopien von {card_name} hinzufügen</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="187"/>
      <source>Export image</source>
      <translation>Bild exportieren</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="203"/>
      <source>Save card image</source>
      <translation>Kartenbild speichern</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="203"/>
      <source>Images (*.png *.bmp *.jpg)</source>
      <translation>Bilder (*.png *.bmp *.jpg)</translation>
    </message>
  </context>
  <context>
    <name>PageConfigPreviewArea</name>
    <message>
      <location filename="../ui/page_config_preview_area.ui" line="29"/>
      <location filename="../ui/page_config_preview_area.ui" line="36"/>
      <source> cards</source>
      <translation> Karten</translation>
    </message>
    <message>
      <location filename="../ui/page_config_preview_area.ui" line="43"/>
      <source>Regular</source>
      <translation>Regulär</translation>
    </message>
    <message>
      <location filename="../ui/page_config_preview_area.ui" line="53"/>
      <source>Oversized</source>
      <translation>Übergroß</translation>
    </message>
  </context>
  <context>
    <name>PageConfigWidget</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="89"/>
      <source>Disabled</source>
      <comment>A cut marker style</comment>
      <translation>Deaktiviert</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="90"/>
      <source>Solid lines</source>
      <comment>A cut marker style</comment>
      <translation>Durchgezogene Linien</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="91"/>
      <source>Dashed lines</source>
      <comment>A cut marker style</comment>
      <translation>Gestrichelte Linien</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="92"/>
      <source>Dotted lines</source>
      <comment>A cut marker style</comment>
      <translation>Gepunktete Linien</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="96"/>
      <source>Disabled</source>
      <comment>A print/cut registration marker style</comment>
      <translation>Deaktiviert</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="97"/>
      <source>Bullseye</source>
      <comment>A print/cut registration marker style</comment>
      <translation>Passer</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="100"/>
      <source>Silhouette cutter (Cameo-compatible)</source>
      <comment>A print/cut registration marker style</comment>
      <translation>Silhouette-Schneider (Cameo-kompatibel)</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="205"/>
      <source>Select watermark text color</source>
      <translation>Wasserzeichen-Textfarbe auswählen</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="223"/>
      <source>Select cut marker color</source>
      <translation>Schneidlinienfarbe wählen</translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="240"/>
      <source>%n regular card(s)</source>
      <comment>Display of the resulting page capacity for regular-sized cards</comment>
      <translation>
        <numerusform>%n reguläre Karte</numerusform>
        <numerusform>%n reguläre Karten</numerusform>
      </translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="244"/>
      <source>%n oversized card(s)</source>
      <comment>Display of the resulting page capacity for oversized cards</comment>
      <translation>
        <numerusform>%n übergroße Karte</numerusform>
        <numerusform>%n übergroße Karten</numerusform>
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
      <translation>Standardeinstellungen für neue Dokumente</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="35"/>
      <source>Show Preview</source>
      <translation>Vorschau anzeigen</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="53"/>
      <source>The document name is printed on each page and can help you keep track
of different printed sheets and to which deck they belong.

Leave empty to disable.</source>
      <translation>Der Dokumentenname wird auf jeder Seite gedruckt,
um Stapel gedruckter Seiten auseinanderhalten zu können.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="62"/>
      <source>Document/deck name</source>
      <translation>Dokument-/Deckname</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="72"/>
      <source>If enabled, the page number is printed on each page. Makes it easier to notice missing pages in a stack.</source>
      <translation>Wenn aktiviert, wird die Seitennummer auf jeder Seite ausgedruckt. Dadurch wird es einfacher, fehlende Seiten in einem Stapel zu bemerken.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="75"/>
      <source>Print page numbers</source>
      <translation>Seitennummern drucken</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="82"/>
      <source>Document name</source>
      <translation>Dokumentenname</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="92"/>
      <source>Draw 90° card corners, instead of round ones</source>
      <translation>90°-Kartenecken zeichnen</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="116"/>
      <source>Paper dimensions</source>
      <translation>Papiermaße</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="122"/>
      <source>Draw an additional border around cards to ease cutting.</source>
      <translation>Einen zusätzlichen Rand um die Karten zeichnen, um das Schneiden zu erleichtern.</translation>
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
      <translation>Unterer Rand</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="148"/>
      <source>Right margin</source>
      <translation>Rechter Rand</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="161"/>
      <source>Top margin</source>
      <translation>Oberer Rand</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="183"/>
      <source>Paper width in millimeters.
Must match the size of the sheets in the printer.
Otherwise, scaling may be applied by the printer driver.</source>
      <translation>Papierbreite in Millimetern.
Muss mit der Größe der Blätter im Drucker übereinstimmen.
Andernfalls könnte der Druckertreiber das Dokument skalieren.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="207"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the right paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Mindestspanne zwischen dem rechten Papierrand und dem Seiteninhalt.&lt;/p&gt;&lt;p&gt;Die meisten Drucker haben eine Mindestspanne von 3 bis 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="223"/>
      <source>Left margin</source>
      <translation>Linker Rand</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="236"/>
      <source>Paper height</source>
      <translation>Seitenhöhe</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="249"/>
      <source>Card bleed</source>
      <translation>Kartenumrandung</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="268"/>
      <source>Paper height in millimeters.
Must match the size of the sheets in the printer.
Otherwise, scaling may be applied by the printer driver.</source>
      <translation>Papierhöhe in Millimetern.
Muss mit der Größe der Blätter im Drucker übereinstimmen.
Andernfalls könnte der Druckertreiber das Dokument skalieren.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="286"/>
      <source>Resulting page capacity:</source>
      <translation>Seitenkapazität:</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="296"/>
      <source>Paper width</source>
      <translation>Seitenbreite</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="309"/>
      <source>Number of cards fitting on each page,
based on the page size and spacings configured</source>
      <translation>Anzahl der regulären Karten auf jeder Seite,
basierend auf der Seitengröße und den konfigurierten Rand- und Kartenabständen</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="326"/>
      <source>Switch between portrait and landscape mode</source>
      <translation>Zwischen Hoch- und Querformat wechseln</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="329"/>
      <source>Flip</source>
      <translation>Drehen</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="345"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the bottom paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Mindestabstand zwischen dem unteren Papierrand und dem Seiteninhalt.&lt;/p&gt;&lt;p&gt;Die meisten Drucker haben einen Mindestabstand von 3 bis 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="358"/>
      <source>Column spacing</source>
      <translation>Spaltenabstand</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="377"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the left paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Mindestspanne zwischen dem linken Papierrand und dem Seiteninhalt.&lt;/p&gt;&lt;p&gt;Die meisten Drucker haben eine Mindestspanne von 3 bis 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="396"/>
      <source>Space between image rows in mm.
If set to zero, you only need one cut to separate two images,
otherwise you need two cuts but require less precision hitting the exact middle.</source>
      <translation>Abstand zwischen den Bildzeilen in mm.
Wenn Sie diesen Wert auf null setzen, benötigen Sie nur einen Schnitt, um zwei Zeilen zu trennen.
Andernfalls sind zwei Schnitte erforderlich, die jedoch weniger Präzision erfordern.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="411"/>
      <source>Row spacing</source>
      <translation>Zeilenabstand</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="430"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the top paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Mindestabstand zwischen dem oberen Papierrand und dem Seiteninhalt.&lt;/p&gt;&lt;p&gt;Die meisten Drucker haben einen Mindestabstand von 3 bis 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="449"/>
      <source>Space between image columns in mm.
If set to zero, you only need one cut to separate two images,
otherwise you need two cuts but require less precision hitting the exact middle.</source>
      <translation>Abstand zwischen den Bildspalten in mm.
Wenn Sie diesen Wert auf null setzen, benötigen Sie nur einen Schnitt, um zwei Spalten zu trennen.
Andernfalls sind zwei Schnitte erforderlich, die jedoch weniger Präzision erfordern.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="464"/>
      <source>Paper size</source>
      <translation>Papierformat</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="475"/>
      <source>Cut markers</source>
      <translation>Schnitthilfen</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="484"/>
      <source>Draw cut helper lines above card images, instead of below them</source>
      <translation>Schnitthilfslinien über Karten zeichnen</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="487"/>
      <source>Draw above cards</source>
      <translation>Über Karten zeichnen</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="494"/>
      <source>The default width of 0 draws a thin line, regardless of zoom level.</source>
      <translation>Die Standardbreite von 0 zeichnet eine dünne Linie, unabhängig von der Zoomstufe.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="510"/>
      <source>Cut helper lines</source>
      <translation>Schnitthilfslinien</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="520"/>
      <location filename="../ui/page_config_widget.ui" line="721"/>
      <source>Select a color</source>
      <translation>Farbe wählen</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="543"/>
      <source>Line width</source>
      <translation>Linienbreite</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="566"/>
      <source>Color and opacity</source>
      <translation>Farbe und Deckkraft</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="595"/>
      <source>Print registration marks</source>
      <translation>Registrierungsmarkenstil</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="606"/>
      <source>Watermark</source>
      <translation>Wasserzeichen</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="612"/>
      <source>X position</source>
      <translation>X-Position</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="622"/>
      <source>Y position</source>
      <translation>Y-Position</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="632"/>
      <source>Watermark text</source>
      <translation>Wasserzeichentext</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="655"/>
      <source>Rotation angle</source>
      <translation>Drehwinkel</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="681"/>
      <source>Font size</source>
      <translation>Schriftgröße</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="691"/>
      <source>Text color and opacity</source>
      <translation>Textfarbe und Deckkraft</translation>
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
      <translation>Mit Strg+Mausrad zoomen.
Verwendbare Tastaturkürzel sind:
Zoom in: {zoom_in_shortcuts}
Zoom aus: {zoom_out_shortcuts}</translation>
    </message>
  </context>
  <context>
    <name>ParserBase</name>
    <message>
      <location filename="../../mtg_proxy_printer/decklist_parser/common.py" line="72"/>
      <source>All files (*)</source>
      <comment>File type filter</comment>
      <translation>Alle Dateien (*)</translation>
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
      <translation>Druckereinstellungen</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="538"/>
      <source>Configure the printer</source>
      <translation>Drucker konfigurieren</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/printer_settings_page.ui" line="17"/>
      <source>Horizontal printing offset</source>
      <translation>Horizontaler Druckversatz</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/printer_settings_page.ui" line="24"/>
      <source>Globally shifts the printing area to correct physical offsets in the printer.
Positive values shift to the right.
Negative offsets shift to the left.</source>
      <translation>Verschiebt den Druckbereich, um einen physikalischen Versatz im Drucker auszugleichen und die Zentrierung zu verbessern.
Positive Werte verschieben nach rechts, negative nach links.</translation>
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
      <translation>Wenn aktiviert, werden Querformat-Dokumente stattdessen im Hochformat mit allen Inhalten um 90° gedreht ausgedruckt.
Aktivieren Sie dies, wenn das Drucken von Querformat-Dokumenten zu Ausdrucken im Hochformat mit abgeschnittenen Seiten führt.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/printer_settings_page.ui" line="52"/>
      <source>Enable landscape workaround: Rotate prints by 90°</source>
      <translation>Querformat-Workaround: Drucke um 90° drehen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/printer_settings_page.ui" line="62"/>
      <source>When enabled, instruct the printer to use borderless mode and let MTGProxyPrinter manage the printing margins.
Disable this, if your printer keeps scaling print-outs up or down.

When disabled, managing the page margins is delegated to the printer driver,
which should increase compatibility, at the expense of drawing shorter cut helper lines.</source>
      <translation>Wenn diese Option aktiviert ist, wird der Drucker angewiesen, den randlosen Modus zu verwenden und MTGProxyPrinter die Verwaltung der Druckränder zu überlassen.
Deaktivieren Sie diese Option, wenn Ihr Drucker die Ausdrucke ständig hoch- oder herunterskaliert.

Wenn deaktiviert, wird die Verwaltung der Seitenränder an den Druckertreiber delegiert.
Dies sollte die Kompatibilität erhöhen, allerdings auf Kosten des Zeichnens kürzerer Hilfslinien.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/printer_settings_page.ui" line="69"/>
      <source>Configure printer for borderless printing</source>
      <translation>Drucker auf randloses Drucken einstellen</translation>
    </message>
  </context>
  <context>
    <name>PrintingFilterModel</name>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="79"/>
      <source>Hide cards banned in the {format} format</source>
      <comment>Tooltip text</comment>
      <translation>Im {format}-Format gebannte Karten ausblenden</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="83"/>
      <source>General filters</source>
      <comment>Display text. Printing filter section header</comment>
      <translation>Allgemeine Filter</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="84"/>
      <source>Hide printings based on general card properties</source>
      <comment>Tooltip text</comment>
      <translation>Drucke aufgrund allgemeiner Karteneigenschaften ausblenden</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="86"/>
      <source>Hide cards depicting racism</source>
      <comment>Display text</comment>
      <translation>Karten mit rassistischen Darstellungen ausblenden</translation>
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
      <translation>Verstecke wegen Rassismus gebannte Karten.
Hintergrund: Einige Karten wurden von Wizards of the Coast gebannt,
weil sie Verweise auf umstrittene oder religiöse Ereignisse aus der
realen Welt darstellen oder durch Kombinationen von Karteneffekten,
Namen und Kunstwerken Rassismus darstellen.
Diese Karten sind in allen sanktionierten Turnierformaten und
verschiedenen Gemeinschaftsformaten wie Commander,
Oathbreaker und anderen gebannt.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="98"/>
      <source>Hide cards with placeholder images</source>
      <comment>Display text</comment>
      <translation>Karten mit Platzhalter-Bildern ausblenden</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="102"/>
      <source>Hide non-English cards with low-resolution,
English placeholder images containing an overlay text stating
“This card is not available in the selected language.”</source>
      <comment>Tooltip text</comment>
      <translation>Verstecke Platzhalter in englischer Sprache für nicht-englische Karten ohne verfügbare Bilder.
Diese haben eine niedrige Qualität und ein Overlay-Text „Diese Karte ist nicht in der gewählten Sprache verfügbar.“</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="106"/>
      <source>Hide “funny” cards</source>
      <comment>Display text</comment>
      <translation>„Lustige“ Karten ausblenden</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="111"/>
      <source>“Funny” cards, not legal in any constructed format.
This includes silver-bordered cards, full-art Contraptions from Unstable,
cards with acorn-shaped security stamps from Unfinity (and newer Un-Sets),
some black-bordered promotional cards with non-standard back faces,
and potentially others.</source>
      <comment>Tooltip text</comment>
      <translation>„Lustige“ Karten, nicht legal in allen konstruierten Formaten.
Enthält silberrandige Karten, Contraptions aus Unstable,
Karten mit Eichelförmigen Sicherheitsstempeln aus Unfinity (und neueren Un-Sets),
einige schwarzrandige Promotionkarten mit nicht standardmäßigen Rückseiten,
und potentiell weitere.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="115"/>
      <source>Hide digital-only cards or printings</source>
      <comment>Display text</comment>
      <translation>Nur auf Digitalplattformen verfügbare Karten oder Drucke ausblenden</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="118"/>
      <source>Hide cards and printings that are only available on digital platforms. This includes all kinds of digital printings.</source>
      <comment>Tooltip text</comment>
      <translation>Verstecke Karten und Drucke, die nur auf digitalen Plattformen erhältlich sind, inklusive aller Arten von Digitaldrucken.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="122"/>
      <source>Hide reversible cards</source>
      <comment>Display text</comment>
      <translation>Umdrehbare Karten ausblenden</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="125"/>
      <source>Some single-sided cards are re-printed as two-sided, reversible cards in some Secret Lair releases.
This filter hides those.</source>
      <comment>Tooltip text</comment>
      <translation>Einige einseitige Karten werden in einigen „Secret Lair“-Produkten als zweiseitige, wendbare Karten neu gedruckt.
Dieser Filter versteckt diese.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="129"/>
      <source>Border style</source>
      <comment>Display text. Printing filter section header</comment>
      <translation>Rahmenstil</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="132"/>
      <source>Hide white-bordered cards</source>
      <comment>Display text</comment>
      <translation>Weißrandige Karten ausblenden</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="137"/>
      <source>Hide gold-bordered cards</source>
      <comment>Display text</comment>
      <translation>Goldrandinge Karten ausblenden</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="142"/>
      <source>Some “collectible” sets, like full reprints of tournament-winning decks were printed with golden borders.
Many also have printed signatures of the involved players in the text box.

These are not tournament legal</source>
      <comment>Tooltip text</comment>
      <translation>Einige „Sammler“-Sets wie vollständige Nachdrucke der Decks von Turniersiegern wurden mit goldenen Rändern verkauft.
Viele haben auch Unterschriften der beteiligten Spieler in der Textbox gedruckt.

Diese sind nicht Turnier-legal</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="146"/>
      <source>Hide borderless cards</source>
      <comment>Display text</comment>
      <translation>Randlose Karten ausblenden</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="149"/>
      <source>Hide cards without a defined, solid-color border.
Those require higher cutting precision to get right.</source>
      <comment>Tooltip text</comment>
      <translation>Karten ohne definierten, einfarbigen Rand ausblenden.
Diese benötigen beim Schneiden eine höhere Präzision.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="153"/>
      <source>Hide extended-art cards</source>
      <comment>Display text</comment>
      <translation>Karten mit erweiterten Artworks ausblenden</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="156"/>
      <source>Hide cards with artwork extending to the left and right card border.
Similar to borderless cards, these require higher precision during the cutting process.</source>
      <comment>Tooltip text</comment>
      <translation>Verstecke Karten mit Artworks, die sich bis zum linken und rechten Kartenrand erstrecken.
Ähnlich wie randlose Karten erfordern diese während des Schneidenvorgangs eine höhere Präzision.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="160"/>
      <source>Non-traditional cards</source>
      <comment>Display text. Printing filter section header</comment>
      <translation>Nichttraditionelle Karten</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="163"/>
      <source>Hide oversized cards</source>
      <comment>Display text</comment>
      <translation>Übergroße Karten ausblenden</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="167"/>
      <source>These cards are larger than regular Magic cards and can’t be included in decks.
Includes Archenemy schemes, Planechase planes and
oversized commander creature or Planeswalker cards included in some pre-constructed Commander decks.</source>
      <comment>Tooltip text</comment>
      <translation>Diese Karten sind größer als normale Magic-Karten und können nicht in Decks enthalten sein.
Enthält Archenemy-Schemen, Planechase-Karten und
übergroße Kommandeur- oder Planeswalker-Karten, die in einigen vorgefertigten Commander-Decks enthalten sind.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="171"/>
      <source>Hide Tokens</source>
      <comment>Display text</comment>
      <translation>Token ausblenden</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="174"/>
      <source>The official Tokens, used to represent permanents created by card effects.
Not part of deck-building. Obscure ones can be relatively rare</source>
      <comment>Tooltip text</comment>
      <translation>Die offiziellen Token, die verwendet werden, um durch Karteneffekte erzeugte Permanente zu repräsentieren.
Nicht Teil des Deckbaus</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="178"/>
      <source>Hide Art Series cards</source>
      <comment>Display text</comment>
      <translation>Artwork-Karten ausblenden</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="180"/>
      <source>Artwork cards that can be found in Set Boosters or Play Boosters</source>
      <comment>Tooltip text</comment>
      <translation>Artwork-Karten, die in Set-Booster oder Play-Booster gefunden werden können</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/printing_filter_model.py" line="185"/>
      <source>Format bans: Hide cards banned in specific formats</source>
      <comment>Display text. Section header above MTG format ban filters</comment>
      <translation>Format-Banns: In bestimmten Formaten gebannte Karten ausblenden</translation>
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
      <translation>Verarbeite aktualisierte Kartenfilter:</translation>
    </message>
  </context>
  <context>
    <name>ProgressBar</name>
    <message>
      <location filename="../ui/progress_bar.ui" line="36"/>
      <source>Cancel</source>
      <translation>Abbrechen</translation>
    </message>
  </context>
  <context>
    <name>SaveDocumentAsDialog</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="197"/>
      <source>Save document as …</source>
      <comment>File dialog window title</comment>
      <translation>Dokument speichern unter …</translation>
    </message>
  </context>
  <context>
    <name>SavePDFDialog</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="96"/>
      <source>Export as PDF</source>
      <comment>File dialog window title</comment>
      <translation>Als PDF exportieren</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="97"/>
      <source>PDF documents (*.pdf)</source>
      <comment>File type filter</comment>
      <translation>PDF-Dokument (*.pdf)</translation>
    </message>
  </context>
  <context>
    <name>SavePNGDialog</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="141"/>
      <source>Export as PNG</source>
      <comment>File dialog window title</comment>
      <translation>Als PNG exportieren</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="142"/>
      <source>PNG images (*.png)</source>
      <comment>File type filter</comment>
      <translation>PNG-Bilder (*.png)</translation>
    </message>
  </context>
  <context>
    <name>ScryfallCSVParser</name>
    <message>
      <location filename="../../mtg_proxy_printer/decklist_parser/csv_parsers.py" line="117"/>
      <source>Scryfall CSV export</source>
      <translation>Scryfall CSV-Export</translation>
    </message>
  </context>
  <context>
    <name>SelectDeckParserPage</name>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="14"/>
      <source>Import a deck list for printing</source>
      <translation>Deckliste zum Drucken importieren</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="17"/>
      <source>Select which kind of deck list you want to import.</source>
      <translation>Wählen Sie aus, welche Art von Deckliste Sie importieren möchten.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="26"/>
      <source>This is a Tappedout-specific section of the deck.
It may contain the deck list author’s buy-list or anything else.</source>
      <translation>Dies ist ein Tappedout-spezifischer Abschnitt des Decks.
Er kann die Kaufliste des Autors oder irgendetwas anderes enthalten.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="30"/>
      <source>Include “Acquire-Board”</source>
      <translation>„Ankaufliste“ einschließen</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="53"/>
      <source>A simple list, containing one card name per line</source>
      <translation>Eine einfache Liste mit einem Kartennamen pro Zeile</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="56"/>
      <source>List with card names</source>
      <translation>Liste mit Kartennamen</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="92"/>
      <source>CSV exports from Scryfall’s own deck builder.
Gives very accurate results, unless the imported deck list contains ignored items
matching an enabled card filter.</source>
      <translation>CSV, exportiert von Scryfalls eigenem Deck-Builder.
Ergibt sehr genaue Ergebnisse, es sei denn, die importierte Deckliste enthält durch Kartenfilter versteckte Drucke.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="97"/>
      <source>Scryfall.com deck lists (CSV export)</source>
      <translation>Scryfall.com Decklisten (CSV-Export)</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="104"/>
      <source>Deck list files, stored in XMage’s native format.
Because XMage closely follows Scryfall regarding Magic sets,
this should give very accurate results.</source>
      <translation>Decklisten-Dateien, gespeichert im XMage-eigenen Format.
Da XMage in Bezug auf Magic-Sets eng an Scryfall angelehnt ist,
sollte dies sehr genaue Ergebnisse liefern.</translation>
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
      <translation>Geben Sie einen benutzerdefinierten regulären Ausdruck im Eingabefeld unten an. Er wird verwendet, um jede Decklistenzeile zu analysieren.
Sie können die Schaltflächen unten benutzen, um Grundbausteine einzufügen. 
Sie müssen die Bausteine mit den „Kontrollstrukturen“ des Listenformats trennen, wie z.B. Leerzeichen, genau so, wie sie in Ihrer Deckliste verwendet werden.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="121"/>
      <source>Custom regular expression based parser:</source>
      <translation>Benutzerdefinierter Parser basierend auf regulären Ausdrücken:</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="128"/>
      <source>CSV exports can be downloaded from Tappedout by choosing the appropriate deck export option.</source>
      <translation>CSV-Exporte können von Tappedout heruntergeladen werden, indem Sie die entsprechende Deck-Export-Option wählen.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="131"/>
      <source>tappedout.net deck list (CSV export)</source>
      <translation>tappedout.net Deckliste (CSV-Export)</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="138"/>
      <source>The simplistic format used by Magic Online. It does not specify exact printings, so may not give the best results.</source>
      <translation>Das einfache Format, das von Magic Online verwendet wird und keine genauen Ausdrucke angibt. Liefert daher nicht die besten Ergebnisse.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="141"/>
      <source>Magic Online</source>
      <translation>Magic-Online</translation>
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
      <translation>Magic Arena, und Exporte von kompatiblen Webseiten, wie moxfield.com
Beachten Sie, dass diese Option nicht auf Karten in Standard/Historic beschränkt ist,
da das Format für jede Karte funktioniert.</translation>
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
      <translation>Dies ist ein Tappedout-spezifischer Abschnitt des Decks.
Er könnte Karten enthalten, die der Ersteller der Liste in Erwägung zieht, basierend auf der Meta oder anderen Präferenzen, wie z. B. dem Kartenpreis.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="175"/>
      <source>Include “Maybe-Board”</source>
      <translation>"Maybe-Board" einschließen</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="200"/>
      <source>Appends a matcher for a card name to the input field above.</source>
      <translation>Fügt einen Matcher für einen Kartennamen dem obigen Eingabefeld zu.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="203"/>
      <source>Card name matcher</source>
      <translation>Matcher für Kartenname</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="213"/>
      <source>Appends a sample matcher for a collector number to the input field above</source>
      <translation>Fügt einen Beispiel-Matcher für eine Sammlernummer dem obigen Eingabefeld zu</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="216"/>
      <source>Collector number matcher</source>
      <translation>Matcher für Sammlernummer einfügen</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="226"/>
      <source>Appends a matcher for the  card language to the input field above.
If a language field is not present in the deck list, the card language is guessed.</source>
      <translation>Fügt einen Matcher für die Kartensprache an das obige Eingabefeld an.
Wenn ein Sprachfeld in der Deckliste nicht vorhanden ist, wird die Kartensprache erraten.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="230"/>
      <source>Language matcher</source>
      <translation>Matcher für Sprache</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="240"/>
      <source>Appends a sample matcher for a set code to the input field above.</source>
      <translation>Fügt einen Beispiel-Matcher für ein Setkürzel dem obigen Eingabefeld zu.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="243"/>
      <source>Set code matcher</source>
      <translation>Set-Matcher einfügen</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="253"/>
      <source>Appends a matcher for the number of card copies to the input field above.
If a card count field is not present in the deck list, 1 card copy per line is assumed</source>
      <translation>Fügt einen Matcher für die Kartenanzahl an das obige Eingabefeld an.
Wenn ein Feld für die Anzahl nicht vorhanden ist, wird eine Karte pro Zeile angenommen</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="257"/>
      <source>Copies matcher</source>
      <translation>Matcher für Kopien</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="267"/>
      <source>Appends a matcher for the Scryfall ID to the input field above.
This may be used by deck lists that closely integrate with the Scryfall website.
Most deck lists won’t use this.</source>
      <translation>Fügt einen Matcher für die Scryfall-ID an das obige Eingabefeld an.
Dies kann von Decklisten verwendet werden, die sich eng mit der Scryfall-Website verbinden.
Die meisten Decklisten werden dies nicht verwenden.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="272"/>
      <source>Scryfall ID matcher</source>
      <translation>Matcher für Scryfall ID</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="282"/>
      <source>Enter a Regular Expression containing at least one supported, named group.

Supported named groups are: {group_names}

See the &apos;What’s this?&apos; (?-Button) help for details.</source>
      <translation>Geben Sie einen regulären Ausdruck ein, der mindestens eine unterstützte, benannte Gruppe enthält.

Unterstützte benannte Gruppen sind: {group_names}

Siehe "Was ist das?"-Hilfe (?-Button) für Details.</translation>
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
      <translation>Sie können einen regulären Ausdruck (in Python-Syntax) eingeben, um die Zeilen ihrer Deckliste zu analysieren. Verwenden Sie *benannte Gruppen* um die einzelnen Karteneigenschaften aus den einzelnen Zeilen der Deckliste zu extrahieren.
Eine benannte Gruppe sieht folgendermaßen aus:
**(?P\&lt;GruppenName&gt;RE)**, wobei RE ein regulärer Ausdruck ist, der dem zu extrahierenden Teil entspricht, und GruppenName eine der folgenden Gruppen ist:

- `copies`: Die Anzahl der Kartenkopien. Standardwert 1 wenn nicht vorhanden
- `name`: Der Kartenname
- `set_code`: Der 3 (oder mehr) Buchstaben-Code, der das Set bestimmt
- `collector_number`: Die Sammlernummer der Karte
- `language`: Die Kartensprache, unter Verwendung eines zweistelligen Sprachcodes. Falls nicht angegeben, versuche die Sprache anhand des Kartennamens zu bestimmen. Standardwerte &quot;en&quot; für Englisch, falls nicht möglich.

Nicht alle Gruppen sind für eine erfolgreiche Identifizierung erforderlich. Zum Beispiel reichen `set_code` und `collector_number` für die exakte Identifizierung meist aus.
Tipp: Möglicherweise möchten Sie einen Online-Editor für reguläre Ausdrücke verwenden, wie z.B. [](https://regex101.com/).</translation>
    </message>
  </context>
  <context>
    <name>SetEditor</name>
    <message>
      <location filename="../ui/set_editor_widget.ui" line="35"/>
      <source>Set name</source>
      <translation>Setname</translation>
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
      <translation>Einstellungen auf das aktuelle Dokument anwenden?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="203"/>
      <source>The new default settings differ from the settings used by the current document.
Apply the new settings to the current document?</source>
      <translation>Die neuen Standardeinstellungen unterscheiden sich von den Einstellungen des aktuellen Dokuments.
Neue Einstellungen auf das aktuelle Dokument anwenden?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="215"/>
      <source>Reset unsaved changes?</source>
      <translation>Ungespeicherte Änderungen zurücksetzen?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="216"/>
      <source>Reset unsaved changes on the current page or on all pages?</source>
      <translation>Ungespeicherte Änderungen auf der aktuellen Seite oder auf allen Seiten zurücksetzen?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="219"/>
      <source>Reset everything</source>
      <translation>Alles zurücksetzen</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="220"/>
      <source>Reset current page</source>
      <translation>Diese Seite</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="249"/>
      <source>Restore defaults for the current page or everything?</source>
      <translation>Standardwerte für die aktuelle Seite oder für alle Seiten wiederherstellen?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="250"/>
      <source>Restore the settings on the current page or on all pages to their default values?</source>
      <translation>Einstellungen auf der aktuellen Seite oder auf allen Seiten auf ihre Standardwerte zurücksetzen?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="253"/>
      <source>Restore everything</source>
      <translation>Alle Seiten</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="254"/>
      <source>Restore current page</source>
      <translation>Diese Seite</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/settings_window.ui" line="17"/>
      <source>Settings</source>
      <translation>Einstellungen</translation>
    </message>
  </context>
  <context>
    <name>SummaryPage</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="461"/>
      <source>Images about to be deleted: {count}</source>
      <translation>Zu löschende Bilder: {count}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="462"/>
      <source>Disk space that will be freed: {disk_space_freed}</source>
      <translation>Frei werdender Speicherplatz: {disk_space_freed}</translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="504"/>
      <source>Beware: The card list currently contains %n potentially oversized card(s).</source>
      <comment>Warning emitted, if at least 1 card has the oversized flag set. The Scryfall server *may* still return a regular-sized image, so not *all* printings marked as oversized are actually so when fetched.</comment>
      <translation>
        <numerusform>Achtung: Die Deckliste enthält derzeit %n potenziell übergroße Karte.</numerusform>
        <numerusform>Achtung: Die Deckliste enthält derzeit %n potenziell übergroße Karten.</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="511"/>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="529"/>
      <source>Replace document content with the identified cards</source>
      <comment>Wizard Accept button tooltip, if replacing the document with the loaded list is enabled.</comment>
      <translation>Dokumenteninhalt durch identifizierte Karten ersetzen</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="517"/>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="535"/>
      <source>Append identified cards to the document</source>
      <comment>Wizard Accept button tooltip, if replacing the document with the loaded list is disabled.</comment>
      <translation>Identifizierte Karten an das Dokument anhängen</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="571"/>
      <source>Remove basic lands</source>
      <comment>Button text</comment>
      <translation>Standardländer entfernen</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="573"/>
      <source>Remove all basic lands in the deck list above</source>
      <comment>Button tooltip</comment>
      <translation>Entferne alle Standardländer in der obrigen Deckliste</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="579"/>
      <source>Remove selected</source>
      <comment>Button text. Clicking removes all selected cards in the table</comment>
      <translation>Ausgewählte entfernen</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="581"/>
      <source>Remove all selected cards in the deck list above</source>
      <comment>Button tooltip</comment>
      <translation>Entferne alle ausgewählten Karten in der obrigen Deckliste</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/summary_page.ui" line="14"/>
      <source>Summary</source>
      <translation>Überblick</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="6"/>
      <source>Import a deck list for printing</source>
      <translation>Deckliste zum Drucken importieren</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="9"/>
      <source>The cards shown in the table will be imported. Double-click the Set, Collector# or Language cells to change selected printings. The text field shows all lines from the input that were not identified as cards.</source>
      <translation>Die hier gezeigten Karten werden importiert. Doppelklicken Sie auf Set, Sammler#-, oder Sprachzellen, um die ausgewählten Drucke zu ändern. Das Textfeld zeigt alle Zeilen der Eingabe, die nicht als Karten identifiziert wurden.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="15"/>
      <source>If checked, clear all cards in the current document, replacing everything with the list below.
If unchecked, append the cards found below to the document.</source>
      <translation>Wenn aktiviert, lösche alle Karten im aktuellen Dokument und ersetze sie durch die Liste unten.
Wenn nicht ausgewählt, füge die unten gefundenen Karten dem Dokument an.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="19"/>
      <source>Replace the current document content with the found cards</source>
      <translation>Den aktuellen Dokumenteninhalt durch die gefundenen Karten ersetzen</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="29"/>
      <source>These cards were successfully identified:</source>
      <translation>Nichts. Alle Karten erfolgreich identifiziert:</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="61"/>
      <source>These lines from the deck list were not identified as cards:</source>
      <translation>Diese Zeilen aus der Deckliste wurden nicht als Karten identifiziert:</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="83"/>
      <source>Nothing. All cards were successfully identified!</source>
      <translation>Nichts. Alle Karten erfolgreich identifiziert!</translation>
    </message>
  </context>
  <context>
    <name>TabbedCentralWidget</name>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="33"/>
      <source>All pages</source>
      <translation>Alle Seiten</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="54"/>
      <source>Move up</source>
      <translation>Schiebe hoch</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="67"/>
      <source>Move down</source>
      <translation>Schiebe runter</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="88"/>
      <source>Add new cards</source>
      <translation>Karten hinzufügen</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="93"/>
      <source>Current page</source>
      <translation>Aktuelle Seite</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="145"/>
      <source>Remove selected</source>
      <translation>Ausgewählte entfernen</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="156"/>
      <source>Preview</source>
      <translation>Vorschau</translation>
    </message>
  </context>
  <context>
    <name>TappedOutCSVParser</name>
    <message>
      <location filename="../../mtg_proxy_printer/decklist_parser/csv_parsers.py" line="196"/>
      <source>Tappedout CSV export</source>
      <translation>Tappedout CSV-Export</translation>
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
      <translation>Vorder-/Rückseite</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="279"/>
      <source>High resolution?</source>
      <comment>Table header. Shows if the card has high-res images</comment>
      <translation>Hohe Qualität?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="281"/>
      <source>Size</source>
      <comment>Table header. File size in KiB/MiB</comment>
      <translation>Größe</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="283"/>
      <source>Path</source>
      <comment>Table header. File system path</comment>
      <translation>Dateipfad</translation>
    </message>
  </context>
  <context>
    <name>UnknownCardRow</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="245"/>
      <source>Front</source>
      <comment>Magic card side</comment>
      <translation>Vorderseite</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="247"/>
      <source>Back</source>
      <comment>Magic card side</comment>
      <translation>Rückseite</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="253"/>
      <source>Yes</source>
      <comment>Card has high-resolution images available</comment>
      <translation>Ja</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="255"/>
      <source>No</source>
      <comment>Card only has low-resolution images available</comment>
      <translation>Nein</translation>
    </message>
  </context>
  <context>
    <name>VerticalAddCardWidget</name>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="26"/>
      <source>The sets in which the currently selected card was printed.</source>
      <translation>Die Sets, in denen die aktuell ausgewählte Karte gedruckt wurde.</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="29"/>
      <source>Set</source>
      <translation>Set</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="35"/>
      <source>Filter set names</source>
      <translation>Setnamen filtern</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="67"/>
      <source>Collector Number</source>
      <translation>Sammlernummer</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="92"/>
      <source>Card Name</source>
      <translation>Kartenname</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="98"/>
      <source>Filter the list below. Use  % (Percent signs) as wildcards matching any number of characters.</source>
      <translation>Filter für die Liste unten. Verwenden Sie % (Prozentzeichen) als Platzhalter, die beliebig viele Zeichen enthalten.</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="101"/>
      <source>Filter card names</source>
      <translation>Kartennamen filtern</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="111"/>
      <source>The filtered list of card names in the currently selected language. Click on an entry to select it and choose a printing.</source>
      <translation>Die gefilterte Liste der Kartennamen in der aktuell ausgewählten Sprache. Klicken Sie auf einen Eintrag, um ihn auszuwählen und einen Druck auszuwählen.</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="136"/>
      <source>Language:</source>
      <extracomment>Card language. Next to the language selection widget</extracomment>
      <translation>Sprache:</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="152"/>
      <source>Copies:</source>
      <extracomment>Number of copies to add. Next to the number input field</extracomment>
      <translation>Kopien:</translation>
    </message>
  </context>
  <context>
    <name>XMageParser</name>
    <message>
      <location filename="../../mtg_proxy_printer/decklist_parser/re_parsers.py" line="258"/>
      <source>XMage Deck file</source>
      <translation>XMage Deck-Datei</translation>
    </message>
  </context>
  <context>
    <name>export_pdf</name>
    <message>
      <location filename="../../mtg_proxy_printer/print.py" line="132"/>
      <source>Write PDF:</source>
      <comment>Progress label</comment>
      <translation>PDF schreiben:</translation>
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
