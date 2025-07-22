<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="de" sourcelanguage="en-US">
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
      <location filename="../ui/about_dialog.ui" line="214"/>
      <source>Changelog</source>
      <translation>Änderungsprotokoll</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="228"/>
      <source>License</source>
      <translation>Lizenzvereinbarung</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="239"/>
      <source>Third party licenses</source>
      <translation>Drittanbieter-Lizenzen</translation>
    </message>
  </context>
  <context>
    <name>ActionAddCard</name>
    <message numerus="yes">
      <location filename="../../document_controller/card_actions.py" line="161"/>
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
      <location filename="../../document_controller/compact_document.py" line="109"/>
      <source>Compact document, removing %n page(s)</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>
        <numerusform>Kompaktiere Dokument, entferne %n Seite</numerusform>
        <numerusform>Kompaktiere Dokument, entferne %n Seiten</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionEditCustomCard</name>
    <message>
      <location filename="../../document_controller/edit_custom_card.py" line="85"/>
      <source>Edit custom card, set {column_header_text} to {new_value}</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Inoffizielle Karte bearbeiten, {column_header_text} auf {new_value} setzen</translation>
    </message>
  </context>
  <context>
    <name>ActionEditDocumentSettings</name>
    <message>
      <location filename="../../document_controller/edit_document_settings.py" line="133"/>
      <source>Update document settings</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Dokumenteneinstellungen ändern</translation>
    </message>
  </context>
  <context>
    <name>ActionImportDeckList</name>
    <message numerus="yes">
      <location filename="../../document_controller/import_deck_list.py" line="82"/>
      <source>Import a deck list containing %n card(s)</source>
      <comment>Undo/redo tooltip text. Option to delete the current document disabled.</comment>
      <translation>
        <numerusform>Deckliste mit %n Karte importieren</numerusform>
        <numerusform>Deckliste mit %n Karten importieren</numerusform>
      </translation>
    </message>
    <message numerus="yes">
      <location filename="../../document_controller/import_deck_list.py" line="77"/>
      <source>Replace document with imported deck list containing %n card(s)</source>
      <comment>Undo/redo tooltip text. Option to delete the current document enabled.</comment>
      <translation>
        <numerusform>Ersetze Dokument durch importierte Deckliste mit einer Karte</numerusform>
        <numerusform>Ersetze Dokument durch importierte Deckliste mit %n Karten</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionLoadDocument</name>
    <message numerus="yes">
      <location filename="../../document_controller/load_document.py" line="94"/>
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
    <name>ActionLoadDocument. Card total</name>
    <message numerus="yes">
      <location filename="../../document_controller/load_document.py" line="90"/>
      <source>with %n card(s) total</source>
      <comment>Undo/redo tooltip text. Will be inserted as {cards_total}</comment>
      <translation>
        <numerusform>und insgesamt %n Karte</numerusform>
        <numerusform>und insgesamt %n Karten</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionMoveCards</name>
    <message numerus="yes">
      <location filename="../../document_controller/move_cards.py" line="140"/>
      <source>Move %n card(s) from page {source_page} to {target_page}</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>
        <numerusform>Verschiebe %n Karte von Seite {source_page} zu {target_page}</numerusform>
        <numerusform>Verschiebe %n Karten von Seite {source_page} zu {target_page}</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionNewDocument</name>
    <message>
      <location filename="../../document_controller/new_document.py" line="69"/>
      <source>Create new document</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Neues Dokument erstellen</translation>
    </message>
  </context>
  <context>
    <name>ActionNewPage</name>
    <message numerus="yes">
      <location filename="../../document_controller/page_actions.py" line="82"/>
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
      <location filename="../../document_controller/card_actions.py" line="219"/>
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
      <location filename="../../document_controller/page_actions.py" line="182"/>
      <source>%n card(s) total</source>
      <comment>Undo/redo tooltip text. The total number of cards removed. Used as {formatted_card_count}</comment>
      <translation>
        <numerusform>mit einer Karte</numerusform>
        <numerusform>mit %n Karten</numerusform>
      </translation>
    </message>
    <message numerus="yes">
      <location filename="../../document_controller/page_actions.py" line="188"/>
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
      <location filename="../../document_controller/replace_card.py" line="99"/>
      <source>Replace card {old_card} on page {page_number} with {new_card}</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Ersetze {old_card} auf Seite {page_number} durch {new_card}</translation>
    </message>
  </context>
  <context>
    <name>ActionSaveDocument</name>
    <message>
      <location filename="../../document_controller/save_document.py" line="169"/>
      <source>Save document to &apos;{save_file_path}&apos;.</source>
      <translation>Dokument in &apos;{save_file_path}&apos; speichern.</translation>
    </message>
  </context>
  <context>
    <name>ActionShuffleDocument</name>
    <message>
      <location filename="../../document_controller/shuffle_document.py" line="102"/>
      <source>Shuffle document</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Dokument mischen</translation>
    </message>
  </context>
  <context>
    <name>CacheCleanupWizard</name>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="458"/>
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
      <location filename="../../model/card_list.py" line="89"/>
      <source>Card name</source>
      <translation>Kartenname</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="90"/>
      <source>Set</source>
      <translation>Set</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="91"/>
      <source>Collector #</source>
      <translation>Sammler #</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="92"/>
      <source>Language</source>
      <translation>Sprache</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="93"/>
      <source>Side</source>
      <translation>Seite</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="130"/>
      <source>Front</source>
      <translation>Vorderseite</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="130"/>
      <source>Back</source>
      <translation>Rückseite</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="134"/>
      <source>Beware: Potentially oversized card!
This card may not fit in your deck.</source>
      <translation>Achtung: Potenziell übergroße Karte!
Diese Karte könnte nicht in Ihr Deck passen.</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="324"/>
      <source>Double-click on entries to
switch the selected printing.</source>
      <translation>Doppelklicken Sie auf Einträge, um den Ausdruck
zu wechseln.</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="88"/>
      <source>Copies</source>
      <translation>Kopien</translation>
    </message>
  </context>
  <context>
    <name>CardSideSelectionDelegate</name>
    <message>
      <location filename="../../ui/item_delegates.py" line="100"/>
      <source>Front</source>
      <translation>Vorderseite</translation>
    </message>
    <message>
      <location filename="../../ui/item_delegates.py" line="101"/>
      <source>Back</source>
      <translation>Rückseite</translation>
    </message>
  </context>
  <context>
    <name>ColumnarCentralWidget</name>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="61"/>
      <source>All pages:</source>
      <translation>Alle Seiten:</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="68"/>
      <source>Current page:</source>
      <translation>Aktuelle Seite:</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="78"/>
      <source>Remove selected</source>
      <translation>Ausgewählte entfernen</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="88"/>
      <source>Add new cards:</source>
      <translation>Karten hinzufügen:</translation>
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
  </context>
  <context>
    <name>DatabaseImportWorker</name>
    <message>
      <location filename="../../card_info_downloader.py" line="425"/>
      <source>Error during import from file:
{path}</source>
      <translation>Fehler beim Import aus Datei:
{path}</translation>
    </message>
    <message>
      <location filename="../../card_info_downloader.py" line="436"/>
      <source>Updating card data from Scryfall:</source>
      <comment>Progress bar label text</comment>
      <translation>Kartendaten von Scryfall aktualisieren:</translation>
    </message>
    <message>
      <location filename="../../card_info_downloader.py" line="446"/>
      <source>Reading from socket failed: {error}</source>
      <translation>Lesen von Socket fehlgeschlagen: {error}</translation>
    </message>
    <message>
      <location filename="../../card_info_downloader.py" line="462"/>
      <source>Importing card data from disk:</source>
      <comment>Progress bar label text</comment>
      <translation>Kartendaten aus Datei importieren:</translation>
    </message>
    <message>
      <location filename="../../card_info_downloader.py" line="482"/>
      <source>Failed to parse data from Scryfall. Reported error: {error}</source>
      <translation>Fehler beim Verarbeiten der Scryfall-Daten. Fehler: {error}</translation>
    </message>
    <message>
      <location filename="../../card_info_downloader.py" line="526"/>
      <source>Post-processing card data:</source>
      <translation>Kartendaten nachbearbeiten:</translation>
    </message>
  </context>
  <context>
    <name>DatabaseMigrationRunner</name>
    <message>
      <location filename="../../carddb_migrations.py" line="792"/>
      <source>Running database migrations:</source>
      <translation>Datenbankmigrationen durchführen:</translation>
    </message>
    <message numerus="yes">
      <location filename="../../carddb_migrations.py" line="808"/>
      <source>Migrate to version %n:</source>
      <comment>The numeric parameter is a version number, and not countable.</comment>
      <translation>
        <numerusform>Migrieren zu Version %n:</numerusform>
        <numerusform>Migrieren zu Version %n:</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>DebugSettingsPage</name>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="129"/>
      <source>Debug settings</source>
      <translation>Fehlersuche (Debug)</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="129"/>
      <source>Things useful for investigating bugs in the application</source>
      <translation>Nützliche Dinge, um Fehler in der Anwendung zu untersuchen</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="184"/>
      <source>Select download location</source>
      <translation>Download-Verzeichnis auswählen</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="192"/>
      <source>Selected location is not a directory</source>
      <translation>Ausgewählter Ort ist kein Verzeichnis</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="192"/>
      <source>Cannot write the card data at the given location, because it is not a directory:
{location}</source>
      <translation>Die Kartendaten können nicht an den angegebenen Ort geschrieben werden, da es kein Verzeichnis ist:
{location}</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="205"/>
      <source>Import previously downloaded card data obtained from Scryfall</source>
      <translation>Zuvor von Scryfall heruntergeladene Kartendaten importieren</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="205"/>
      <source>Scryfall card data (*.json, *.json.gz)</source>
      <translation>Scryfall-Kartendaten (*.json, *.json.gz)</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="215"/>
      <source>Selected location is not a file</source>
      <translation>Ausgewählter Ort ist keine Datei</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="215"/>
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
      <location filename="../../ui/deck_import_wizard.py" line="611"/>
      <source>Import a deck list</source>
      <translation>Deckliste importieren</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="633"/>
      <source>Oversized cards present</source>
      <translation>Übergroße Karten vorhanden</translation>
    </message>
    <message numerus="yes">
      <location filename="../../ui/deck_import_wizard.py" line="633"/>
      <source>There are %n possibly oversized cards in the deck list that may not fit into a deck, when printed out.

Continue and use these cards as-is?</source>
      <translation>
        <numerusform>Es gibt eine möglicherweise übergroße Karte in der Deckliste, die nach dem Ausdrucken nicht in ein Deck passen könnte.

Trotzdem mit der Deckliste fortfahren?</numerusform>
        <numerusform>Es gibt %n möglicherweise übergroße Karten in der Deckliste, die nach dem Ausdrucken nicht in ein Deck passen könnten.

Trotzdem mit der Deckliste fortfahren?</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="644"/>
      <source>Incompatible file selected</source>
      <translation>Inkompatible Datei ausgewählt</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="644"/>
      <source>Unable to parse the given deck list, no results were obtained.
Maybe you selected the wrong deck list type?</source>
      <translation>Die gegebene Deck-Liste konnte nicht analysiert werden. Es wurden keine Ergebnisse abgerufen.
Vielleicht haben Sie den falschen Deck-Listentyp ausgewählt?</translation>
    </message>
  </context>
  <context>
    <name>DecklistImportSettingsPage</name>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="228"/>
      <source>Deck list import</source>
      <translation>Decklisten-Import</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="228"/>
      <source>Configure the deck list importer</source>
      <translation>Den Decklisten-Import konfigurieren</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="238"/>
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
      <location filename="../../ui/settings_window_pages.py" line="481"/>
      <source>Default document settings</source>
      <translation>Standardeinstellungen für Dokumente</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="481"/>
      <source>Set the default document settings used for new documents,
like page size, margins, spacings, etc.</source>
      <translation>Standardeinstellungen für Dokumente setzen,
wie Papiergröße, Randabstände, Kartenabstände, usw.</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="489"/>
      <source>Default settings for new documents</source>
      <translation>Standardeinstellungen für neue Dokumente</translation>
    </message>
  </context>
  <context>
    <name>Document</name>
    <message>
      <location filename="../../model/document.py" line="92"/>
      <source>Card name</source>
      <translation>Kartenname</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="93"/>
      <source>Set</source>
      <translation>Set</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="94"/>
      <source>Collector #</source>
      <translation>Sammler #</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="95"/>
      <source>Language</source>
      <translation>Sprache</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="96"/>
      <source>Image</source>
      <translation>Bild</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="97"/>
      <source>Side</source>
      <translation>Seite</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="175"/>
      <source>Double-click on entries to
switch the selected printing.</source>
      <translation>Doppelklicken Sie auf Einträge, um den Ausdruck
zu wechseln.</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="288"/>
      <source>Page {current}/{total}</source>
      <translation>Seite {current}/{total}</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="319"/>
      <source>Front</source>
      <translation>Vorderseite</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="319"/>
      <source>Back</source>
      <translation>Rückseite</translation>
    </message>
    <message numerus="yes">
      <location filename="../../model/document.py" line="325"/>
      <source>%n× {name}</source>
      <comment>Used to display a card name and amount of copies in the page overview. Only needs translation for RTL language support</comment>
      <translation>
        <numerusform>%n× {name}</numerusform>
        <numerusform>%n× {name}</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="382"/>
      <source>Empty Placeholder</source>
      <translation>Leerer Platzhalter</translation>
    </message>
  </context>
  <context>
    <name>DocumentAction</name>
    <message>
      <location filename="../../document_controller/_interface.py" line="105"/>
      <source>{first}-{last}</source>
      <comment>Inclusive, formatted number range, from first to last</comment>
      <translation>{first}-{last}</translation>
    </message>
  </context>
  <context>
    <name>DocumentSettingsDialog</name>
    <message>
      <location filename="../../ui/dialogs.py" line="379"/>
      <source>These settings only affect the current document</source>
      <translation>Diese Einstellungen betreffen nur das aktuelle Dokument</translation>
    </message>
    <message>
      <location filename="../ui/document_settings_dialog.ui" line="6"/>
      <source>Set Document settings</source>
      <translation>Einstellungen dieses Dokuments</translation>
    </message>
  </context>
  <context>
    <name>ExportCardImagesDialog</name>
    <message>
      <location filename="../../ui/dialogs.py" line="455"/>
      <source>Select card image export location</source>
      <translation>Speicherort für Kartenbild-Export auswählen</translation>
    </message>
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
      <location filename="../../ui/dialogs.py" line="502"/>
      <source>Copy failed for {card_name}! Disk detached/full? Aborting.</source>
      <translation>Kopieren von {card_name} fehlgeschlagen! Ziel entfernt/voll? Breche ab.</translation>
    </message>
    <message>
      <location filename="../../ui/dialogs.py" line="531"/>
      <source>Write failed for {card_name}! Disk detached/full? Aborting.</source>
      <translation>Schreiben des Bilds von {card_name} fehlgeschlagen! Ziel entfernt/voll? Breche ab.</translation>
    </message>
  </context>
  <context>
    <name>ExportSettingsPage</name>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="558"/>
      <source>Export settings</source>
      <translation>Exporteinstellungen</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="558"/>
      <source>Configure the PDF/PNG export</source>
      <translation>PDF/PNG-Export konfigurieren</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="598"/>
      <source>Select default export location</source>
      <translation>Standardpfad für Exporte auswählen</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="607"/>
      <source>Select PNG background color</source>
      <translation>PNG-Hintergrundfarbe wählen</translation>
    </message>
    <message>
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
    <name>FileDownloadWorker</name>
    <message>
      <location filename="../../card_info_downloader.py" line="189"/>
      <source>Downloading card data:</source>
      <comment>Progress bar label text</comment>
      <translation>Kartendaten herunterladen:</translation>
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
    <name>FormatPrintingFilter</name>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="14"/>
      <source>Hide cards banned in specific Formats</source>
      <translation>In bestimmten Formaten gebannte Karten ausblenden</translation>
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
      <translation>Sehen Sie sich die durch diesen Filter versteckten Karten auf Scryfall an.</translation>
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
      <translation>Allgemeine Druckfilter</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="327"/>
      <source>View cards hidden by this filter on the Scryfall website.</source>
      <translation>Sehen Sie sich die durch diesen Filter versteckten Karten auf Scryfall an.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="71"/>
      <source>Hide cards without a defined, solid-color border.
Those require higher cutting precision to get right.</source>
      <translation>Karten ohne definierten, einfarbigen Rand ausblenden.
Diese benötigen beim Schneiden eine höhere Präzision.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="75"/>
      <source>Hide borderless cards</source>
      <translation>Randlose Karten ausblenden</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="82"/>
      <source>Hide Token cards</source>
      <translation>Spielsteinkarten ausblenden</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="105"/>
      <source>Some single-sided cards are re-printed as two-sided, reversible cards in some Secret Lair releases.
This filter hides those.</source>
      <translation>Einige einseitige Karten werden in einigen „Secret Lair“-Produkten als zweiseitige, wendbare Karten neu gedruckt.
Dieser Filter versteckt diese.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="109"/>
      <source>Hide reversible cards</source>
      <translation>Umdrehbare Karten ausblenden</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="148"/>
      <source>Hide cards and printings that are only available on digital platforms. This includes all kinds of digital printings.</source>
      <translation>Verstecke Karten und Drucke, die nur auf digitalen Plattformen erhältlich sind, inklusive aller Arten von Digitaldrucken.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="151"/>
      <source>Hide digital cards</source>
      <translation>Digitale Karten ausblenden</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="158"/>
      <source>“Funny” cards, not legal in any constructed format.
This includes full-art Contraptions from Unstable,
cards with acorn-shaped security stamps from Unfinity (and newer Un-Sets),
some black-bordered promotional cards with non-standard back faces,
and all silver-bordered cards.</source>
      <translation>„Lustige“ Karten, nicht legal in allen konstruierten Formaten.
Enthält Contraptions aus Unstable,
Karten mit Eichelförmigen Sicherheitsstempeln aus Unfinity (und neueren Un-Sets),
einige schwarzrandige Promotionkarten mit nicht standardmäßigen Rückseiten,
und allen silberrandigen Karten.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="165"/>
      <source>Hide “funny” cards</source>
      <translation>„Lustige“ Karten ausblenden</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="172"/>
      <source>These cards are larger than regular Magic cards and can’t be included in decks.
Includes Archenemy schemes, Planechase planes and
oversized commander creature or Planeswalker cards included in some pre-constructed Commander decks.</source>
      <translation>Diese Karten sind größer als normale Magic-Karten und können nicht in Decks enthalten sein.
Enthält Archenemy-Schemen, Planechase-Karten und
übergroße Kommandeur- oder Planeswalker-Karten, die in einigen vorgefertigten Commander-Decks enthalten sind.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="177"/>
      <source>Hide oversized cards</source>
      <translation>Übergroße Karten ausblenden</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="184"/>
      <source>Some “collectible” sets, like full reprints of tournament-winning decks were printed with golden borders.
Many also have printed signatures of the involved players in the text box.

These are not tournament legal</source>
      <translation>Einige „Sammler“-Sets wie vollständige Nachdrucke der Decks von Turniersiegern wurden mit goldenen Rändern verkauft.
Viele haben auch Unterschriften der beteiligten Spieler in der Textbox gedruckt.

Diese sind nicht Turnier-legal</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="190"/>
      <source>Hide gold-bordered cards</source>
      <translation>Goldrandinge Karten ausblenden</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="197"/>
      <source>Hide white-bordered cards</source>
      <translation>Weißrandige Karten ausblenden</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="204"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Hide cards banned for depicting racism.&lt;/p&gt;&lt;p&gt;Background:&lt;/p&gt;&lt;p&gt;Some cards were banned by Wizards of the Coast, because they depict references to controversial real-world events, religion or contain combinations of card effect, name and artwork that, when viewed together, depict racism. These cards are banned in all sanctioned tournament formats and several community formats like Commander, Oathbreaker and others.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Verstecke wegen Rassismus gebannte Karten.&lt;/p&gt;&lt;p&gt;Hintergrund:&lt;/p&gt;&lt;p&gt;Einige Karten wurden von Wizards of the Coast gebannt, weil sie Verweise auf umstrittene oder religiöse Ereignisse aus der realen Welt darstellen oder durch Kombinationen von Karteneffekten, Namen und Kunstwerken Rassismus darstellen. Diese Karten sind in allen sanktionierten Turnierformaten und verschiedenen Gemeinschaftsformaten wie Commander, Oathbreaker und anderen verboten.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="207"/>
      <source>Hide cards depicting racism</source>
      <translation>Karten mit rassistischen Darstellungen ausblenden</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="230"/>
      <source>Hide non-English cards with low-resolution,
English placeholder images with an overlay text stating
“This card is not available in the selected language.”</source>
      <translation>Verstecke Platzhalter in englischer Sprache für nicht-englische Karten ohne verfügbare Bilder.
Diese haben eine niedrige Qualität und ein Overlay-Text „Diese Karte ist nicht in der gewählten Sprache verfügbar.“</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="235"/>
      <source>Hide cards with placeholder images</source>
      <translation>Karten mit Platzhalter-Bildern ausblenden</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="300"/>
      <source>Hide cards with artwork extending to the left and right card border.
Similar to borderless cards, these require higher precision during the cutting process.</source>
      <translation>Verstecke Karten mit Artworks, die sich bis zum linken und rechten Kartenrand erstrecken.
Ähnlich wie randlose Karten erfordern diese während des Schneidenvorgangs eine höhere Präzision.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="304"/>
      <source>Hide extended art cards</source>
      <translation>Karten mit erweiterten Artworks ausblenden</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="311"/>
      <source>Artwork cards that can be found in Set Boosters or Play Boosters</source>
      <translation>Artwork-Karten, die in Set-Booster oder Play-Booster gefunden werden können</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="314"/>
      <source>Hide Art Series cards</source>
      <translation>Artwork-Karten ausblenden</translation>
    </message>
  </context>
  <context>
    <name>GeneralSettingsPage</name>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="295"/>
      <source>General settings</source>
      <translation>Allgemeine Einstellungen</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="302"/>
      <source>Horizontal layout</source>
      <translation>Horizontales Layout</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="303"/>
      <source>Columnar layout</source>
      <translation>Spaltenlayout</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="304"/>
      <source>Tabbed layout</source>
      <translation>Layout in Tabs</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="307"/>
      <source>System default</source>
      <translation>Standardsprache des Systems</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="318"/>
      <source>Select default save location</source>
      <translation>Standardspeicherort auswählen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="45"/>
      <source>Horizontal adds a wide, horizontal search area above the currently edited page, and is best for taller screens, like 4:3 or 3:2.
Columnar organizes the main window content in four columns, and is best for (ultra-)wide screens.
Tabbed uses tabs to only show parts of the main window at a time. Best used with small screens in portrait mode (i.e. 9:16), otherwise not recommended.</source>
      <translation>"Horizontal" fügt einen breiten, horizontalen Suchbereich über der gerade bearbeiteten Seite hinzu und ist am besten für höhere Bildschirme, wie z.B. 4:3 oder 3:2.
"Spalten" organisiert den Inhalt des Hauptfensters in vier Spalten und eignet sich am besten für (ultra)weite Bildschirme.
"Tabs" verwendet Tabs, um jederzeit nur einen Teil des Hauptfensters anzuzeigen. Am besten mit kleinen Bildschirmen im Hochformat (z.B. 9:16), ansonsten nicht empfohlen.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="22"/>
      <source>Main window layout</source>
      <translation>Hauptfenster-Layout</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="15"/>
      <source>Application language</source>
      <translation>Sprache der Anwendung</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="83"/>
      <source>Double-faced cards</source>
      <translation>Doppelseitige Karten</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="89"/>
      <source>When adding double-faced cards, automatically add the same number of copies of the other side.
Uses the appropriate, matching other card side.
Uncheck to disable this automatism.</source>
      <translation>Beim Hinzufügen von doppelseitigen Karten automatisch die gleiche Anzahl von Kopien der anderen Seite hinzufügen.
Verwendet die zugehörige, passende andere Kartenseite.
Deaktivieren um diesen Automatismus zu deaktivieren.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="94"/>
      <source>Automatically add the other side of double-faced cards</source>
      <translation>Automatisch die andere Seite von doppelseitigen Karten hinzufügen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="107"/>
      <source>Preferred card language:</source>
      <translation>Bevorzugte Kartensprache:</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="120"/>
      <source>Automatic update checks</source>
      <translation>Automatisch nach Aktualisierungen suchen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="126"/>
      <source>Update checks are performed at application start, if enabled.</source>
      <translation>Suche nach Aktualisierungen wird beim Anwendungsstart durchgeführt, sofern aktiviert.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="133"/>
      <source>If enabled, check for application updates, and notify if new updates are available for installation.</source>
      <translation>Falls aktiviert, beim Start automatisch nach Anwendungsaktualisierungen suchen und bei verfügbaren Aktualisierungen benachrichtigen.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="136"/>
      <source>Check for application updates</source>
      <translation>Nach Anwendungsaktualisierungen suchen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="146"/>
      <source>If enabled, query the Scryfall API if new cards are available. If so, offer to update the local card data.</source>
      <translation>Falls aktiviert, frage automatisch die Scryfall API ab, ob neue Karten verfügbar sind. Wenn ja, bieten wir an, die lokalen Kartendaten zu aktualisieren.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="149"/>
      <source>Check for new card data</source>
      <translation>Nach Aktualisierungen für die Kartendaten suchen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="162"/>
      <source>These paths are selected by default when browsing the file system for files</source>
      <translation>Diese Pfade werden standardmäßig beim Durchsuchen des Dateisystems nach Dateien ausgewählt</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="165"/>
      <source>Default save paths</source>
      <translation>Standardspeicherpfade</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="171"/>
      <source>Browse…</source>
      <translation>Durchsuchen…</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="184"/>
      <source>Document save path</source>
      <translation>Dokumentenspeicherpfad</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="194"/>
      <source>If set, use this as the default location for saving documents.</source>
      <translation>Wenn gesetzt, verwende dies als Standard-Speicherort für Dokumente.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="200"/>
      <source>Path to a directory</source>
      <translation>Pfad zu einem Verzeichnis</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="73"/>
      <source>Language choices will default to the chosen language here.
Entries use the language codes as listed on Scryfall.

Note: Cards in deck lists use the language as given by the deck list. To overwrite, use the deck list translation option.</source>
      <translation>Kartenauswahl wird standardmäßig die hier gewählte Sprache verwenden.
Einträge verwenden die Sprachcodes wie auf Scryfall.

Hinweis: Decklistenimports verwenden die Sprache, wie in der Deckliste angegeben. Zum Überschreiben verwenden Sie die Option der Decklistenübersetzung.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="104"/>
      <source>Card language selected at application start and default language when enabling deck list translations</source>
      <translation>Beim Start der Anwendung ausgewählte Kartensprache und Standardsprache beim Aktivieren der Decklistenübersetzung</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="308"/>
      <source>English (US) [{progress}%]</source>
      <translation>Englisch (US) [{progress}%]</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="309"/>
      <source>German [{progress}%]</source>
      <translation>Deutsch [{progress}%]</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="310"/>
      <source>French [{progress}%]</source>
      <translation>Französisch [{progress}%]</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="32"/>
      <source>Open the main window maximized</source>
      <translation>Hauptfenster maximiert öffnen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="9"/>
      <source>Look &amp;&amp; Feel (Changing most of these require an application restart)</source>
      <translation>Look &amp;&amp; Feel (Ändern der meisten dieser Einstellungen erfordert einen Neustart der Anwendung)</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="57"/>
      <source>Open all wizards maximized</source>
      <translation>Alle Wizards maximiert öffnen</translation>
    </message>
  </context>
  <context>
    <name>GroupedCentralWidget</name>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="58"/>
      <source>Remove selected</source>
      <translation>Ausgewählte entfernen</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="103"/>
      <source>All pages:</source>
      <translation>Alle Seiten:</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="110"/>
      <source>Add new cards:</source>
      <translation>Karten hinzufügen:</translation>
    </message>
  </context>
  <context>
    <name>HidePrintingsPage</name>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="438"/>
      <source>Hide printings</source>
      <translation>Drucke verbergen</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="438"/>
      <source>Hide unwanted printings</source>
      <translation>Unerwünschte Kartenvarianten verbergen</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/hide_printings_page.ui" line="17"/>
      <source>These options allow hiding unwanted cards and printings. Hidden printings are treated as though they don’t exist. They can’t be found in the card search and are automatically replaced in loaded documents or imported deck lists, if possible. If all printings of a card are hidden, it won’t be available at all.</source>
      <translation>Diese Optionen erlauben das Verstecken unerwünschter Karten und Drucke. Diese werden so behandelt, als gäbe es sie nicht. Sie können nicht in der Kartensuche gefunden werden und werden nach Möglichkeit automatisch in geladenen Dokumenten oder importierten Decklisten ersetzt. Wenn alle Ausdrucke einer Karte versteckt sind, wird sie überhaupt nicht verfügbar sein.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/hide_printings_page.ui" line="33"/>
      <source>Hide specific sets: Add set codes as listed on Scryfall, for example LEA or 2X2. Separate multiple entries with spaces or line breaks. All words not matching an exact set code are ignored.</source>
      <translation>Verstecke bestimmte Sets: Füge Set-Codes hinzu, wie auf Scryfall aufgeführt, zum Beispiel LEA oder 2X2. Trennen Sie mehrere Einträge mit Leerzeichen oder Zeilenumbrüchen. Alle Wörter, die keinem exakten Code entsprechen, werden ignoriert.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/hide_printings_page.ui" line="43"/>
      <source>Example:

LEA DDU TC13 J21</source>
      <translation>Beispiel:

LEA DDU TC13 J21</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/hide_printings_page.ui" line="51"/>
      <source>No sets currently hidden.</source>
      <translation>Derzeit sind keine Sets versteckt.</translation>
    </message>
  </context>
  <context>
    <name>HorizontalAddCardWidget</name>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="35"/>
      <source>Language:</source>
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
      <translation>Kopien:</translation>
    </message>
  </context>
  <context>
    <name>ImageDownloader</name>
    <message>
      <location filename="../../model/imagedb.py" line="309"/>
      <source>Importing deck list</source>
      <comment>Progress bar label text</comment>
      <translation>Deckliste importieren</translation>
    </message>
    <message>
      <location filename="../../model/imagedb.py" line="329"/>
      <source>Fetching missing images</source>
      <comment>Progress bar label text</comment>
      <translation>Abrufen fehlender Bilder</translation>
    </message>
    <message>
      <location filename="../../model/imagedb.py" line="424"/>
      <source>Downloading &apos;{card_name}&apos;</source>
      <comment>Progress bar label text</comment>
      <translation>Lade '{card_name}' herunter</translation>
    </message>
  </context>
  <context>
    <name>KnownCardImageModel</name>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="133"/>
      <source>Name</source>
      <translation>Name</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="134"/>
      <source>Set</source>
      <translation>Set</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="135"/>
      <source>Collector #</source>
      <translation>Sammler #</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="136"/>
      <source>Is Hidden</source>
      <translation>Versteckt</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="137"/>
      <source>Front/Back</source>
      <translation>Vorder-/Rückseite</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="138"/>
      <source>High resolution?</source>
      <translation>Hohe Qualität?</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="139"/>
      <source>Size</source>
      <translation>Größe</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="140"/>
      <source>Scryfall ID</source>
      <translation>Scryfall ID</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="141"/>
      <source>Path</source>
      <translation>Dateipfad</translation>
    </message>
  </context>
  <context>
    <name>KnownCardRow</name>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="112"/>
      <source>Yes</source>
      <translation>Ja</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="112"/>
      <source>No</source>
      <translation>Nein</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="100"/>
      <source>This printing is hidden by an enabled card filter
and is thus unavailable for printing.</source>
      <comment>Tooltip for cells with hidden cards</comment>
      <translation>Dieser Druck wird durch einen aktivierten Kartenfilter
versteckt und ist daher nicht verfügbar.</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="106"/>
      <source>Front</source>
      <comment>Card side</comment>
      <translation>Vorderseite</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="106"/>
      <source>Back</source>
      <comment>Card side</comment>
      <translation>Rückseite</translation>
    </message>
  </context>
  <context>
    <name>LoadDocumentDialog</name>
    <message>
      <location filename="../../ui/dialogs.py" line="220"/>
      <source>Load MTGProxyPrinter document</source>
      <translation>MTGProxyPrinter-Dokument laden</translation>
    </message>
  </context>
  <context>
    <name>LoadListPage</name>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="116"/>
      <source>Supported websites:
{supported_sites}</source>
      <translation>Unterstützte Webseiten:
{supported_sites}</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="212"/>
      <source>Overwrite existing deck list?</source>
      <translation>Vorhandene Deckliste überschreiben?</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="166"/>
      <source>Selecting a file will overwrite the existing deck list. Continue?</source>
      <translation>Das Auswählen einer Datei überschreibt die vorhandene Deckliste. Fortfahren?</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="174"/>
      <source>Select deck file</source>
      <translation>Decklisten-Datei auswählen</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="184"/>
      <source>All files (*)</source>
      <translation>Alle Dateien (*)</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="195"/>
      <source>All Supported </source>
      <translation>Alle unterstützten </translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="212"/>
      <source>Downloading a deck list will overwrite the existing deck list. Continue?</source>
      <translation>Das Herunterladen einer Deckliste überschreibt die vorhandene Deckliste. Fortfahren?</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="225"/>
      <source>Download failed with HTTP error {http_error_code}.

{bad_request_msg}</source>
      <translation>Download fehlgeschlagen mit HTTP-Fehler {http_error_code}.

{bad_request_msg}</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="236"/>
      <source>Deck list download failed</source>
      <translation>Download der Deckliste fehlgeschlagen</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="231"/>
      <source>Download failed.

Check your internet connection, verify that the URL is valid, reachable, and that the deck list is set to public. This program cannot download private deck lists. If this persists, please report a bug in the issue tracker on the homepage.</source>
      <translation>Download fehlgeschlagen.

Überprüfen Sie Ihre Internetverbindung, ob die URL gültig und erreichbar ist, und dass die Deckliste öffentlich ist. Dieses Programm kann keine privaten Deck-Listen herunterladen. Falls das Problem weiterhin besteht, melden Sie bitte einen Fehler im Issue-Tracker auf der Homepage.</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="262"/>
      <source>Unable to read file content</source>
      <translation>Dateiinhalt konnte nicht gelesen werden</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="262"/>
      <source>Unable to read the content of file {file_path} as plain text.
Failed to load the content.</source>
      <translation>Kann den Inhalt der Datei {file_path} nicht als Text lesen.
Fehler beim Laden des Inhalts.</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="274"/>
      <source>Load large file?</source>
      <translation>Große Datei laden?</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="274"/>
      <source>The selected file {file_path} is unexpectedly large ({formatted_size}). Load anyway?</source>
      <translation>Die ausgewählte Datei {file_path} ist mit {formatted_size} unerwartet groß. Trotzdem laden?</translation>
    </message>
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
      <translation>Decklisten-Datei auswählen</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="152"/>
      <source>View result</source>
      <translation>Ergebnis anzeigen</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="171"/>
      <source>Download deck list</source>
      <translation>Deckliste herunterladen</translation>
    </message>
  </context>
  <context>
    <name>LoadSaveDialog</name>
    <message>
      <location filename="../../ui/dialogs.py" line="177"/>
      <source>MTGProxyPrinter document (*.{default_save_suffix})</source>
      <comment>Human-readable file type name</comment>
      <translation>MTGProxyPrinter-Dokument (*.{default_save_suffix})</translation>
    </message>
  </context>
  <context>
    <name>MTGArenaParser</name>
    <message>
      <location filename="../../decklist_parser/re_parsers.py" line="201"/>
      <source>Magic Arena deck file</source>
      <translation>Magic Arena Deckliste</translation>
    </message>
  </context>
  <context>
    <name>MTGOnlineParser</name>
    <message>
      <location filename="../../decklist_parser/re_parsers.py" line="235"/>
      <source>Magic Online (MTGO) deck file</source>
      <translation>Magic Online (MTGO) Deckliste</translation>
    </message>
  </context>
  <context>
    <name>MagicWorkstationDeckDataFormatParser</name>
    <message>
      <location filename="../../decklist_parser/re_parsers.py" line="179"/>
      <source>Magic Workstation Deck Data Format</source>
      <translation>Magic Workstation Deck Data (mwDeck)</translation>
    </message>
  </context>
  <context>
    <name>MainWindow</name>
    <message>
      <location filename="../../ui/main_window.py" line="237"/>
      <source>Undo:
{top_entry}</source>
      <translation>Rückgängig:
{top_entry}</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="239"/>
      <source>Redo:
{top_entry}</source>
      <translation>Wiederholen:
{top_entry}</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="303"/>
      <source>printing</source>
      <comment>This is passed as the {action} when asking the user about compacting the document if that can save pages</comment>
      <translation>dem Drucken</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="315"/>
      <source>exporting as a PDF</source>
      <comment>This is passed as the {action} when asking the user about compacting the document if that can save pages</comment>
      <translation>dem PDF-Export</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="350"/>
      <source>Network error</source>
      <translation>Netzwerkfehler</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="350"/>
      <source>Operation failed, because a network error occurred.
Check your internet connection. Reported error message:

{message}</source>
      <translation>Vorgang fehlgeschlagen, da ein Netzwerkfehler aufgetreten ist.
Überprüfen Sie Ihre Internetverbindung. Fehlermeldung:

{message}</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="358"/>
      <source>Error</source>
      <translation>Fehler</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="358"/>
      <source>Operation failed, because an internal error occurred.
Reported error message:

{message}</source>
      <translation>Vorgang fehlgeschlagen, da ein interner Fehler aufgetreten ist.
Berichtete Fehlermeldung:

{message}</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="367"/>
      <source>Saving pages possible</source>
      <translation>Einsparen von Seiten möglich</translation>
    </message>
    <message numerus="yes">
      <location filename="../../ui/main_window.py" line="367"/>
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
      <location filename="../../ui/main_window.py" line="383"/>
      <source>Download required Card data from Scryfall?</source>
      <translation>Benötigte Kartendaten von Scryfall herunterladen?</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="383"/>
      <source>This program requires downloading additional card data from Scryfall to operate the card search.
Download the required data from Scryfall now?
Without the data, you can only print custom cards by drag&amp;dropping the image files onto the main window.</source>
      <translation>Dieses Programm erfordert das Herunterladen zusätzlicher Kartendaten von Scryfall, um die Kartensuche zu ermöglichen.
Jetzt die benötigten Daten von Scryfall herunterladen?
Ohne die Daten können Sie nur nutzererstellte Karten drucken, indem Sie die Bilddateien per Drag &amp; Drop in das Hauptfenster ziehen.</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="431"/>
      <source>Document loading failed</source>
      <translation>Laden des Dokuments fehlgeschlagen</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="431"/>
      <source>Loading file &quot;{failed_path}&quot; failed. The file was not recognized as a {program_name} document. If you want to load a deck list, use the &quot;{function_text}&quot; function instead.
Reported failure reason: {reason}</source>
      <translation>Laden der Datei "{failed_path}" fehlgeschlagen. Die Datei wurde nicht als {program_name}-Dokument erkannt. Wenn Sie eine Deckliste laden möchten, verwenden Sie die "{function_text}"-Funktion stattdessen.
Berichteter Fehlergrund: {reason}</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="444"/>
      <source>Unavailable printings replaced</source>
      <translation>Nicht verfügbare Drucke ersetzt</translation>
    </message>
    <message numerus="yes">
      <location filename="../../ui/main_window.py" line="444"/>
      <source>The document contained %n unavailable printings of cards that were automatically replaced with other printings. The replaced printings are unavailable, because they match a configured card filter.</source>
      <translation>
        <numerusform>Das Dokument enthielt einen nicht verfügbaren Druck einer Karte, der automatisch durch einen anderen Druck ersetzt wurden. Der ausgetauschten Druck ist nicht verfügbar, da er mit einem konfigurierten Kartenfilter übereinstimmt.</numerusform>
        <numerusform>Das Dokument enthielt %n nicht verfügbare Drucke von Karten, die automatisch durch andere Drucke ersetzt wurden. Die ausgetauschten Drucke sind nicht verfügbar, da sie mit einem konfigurierten Kartenfilter übereinstimmen.</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="453"/>
      <source>Unrecognized cards in loaded document found</source>
      <translation>Nicht erkannte Karten im geladenen Dokument gefunden</translation>
    </message>
    <message numerus="yes">
      <location filename="../../ui/main_window.py" line="453"/>
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
      <location filename="../../ui/main_window.py" line="463"/>
      <source>Application update available. Visit website?</source>
      <translation>Anwendungsaktualisierung verfügbar. Website besuchen?</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="463"/>
      <source>An application update is available: Version {newer_version}
You are currently using version {current_version}.

Open the {program_name} website in your web browser to download the new version?</source>
      <translation>Ein Anwendungs-Update ist verfügbar: Version {newer_version}
Sie verwenden derzeit Version {current_version}.

Die {program_name}-Webseite mit Ihrem Web-Browser besuchen, um die neue Version herunterzuladen?</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="478"/>
      <source>New card data available</source>
      <translation>Neue Kartendaten verfügbar</translation>
    </message>
    <message numerus="yes">
      <location filename="../../ui/main_window.py" line="478"/>
      <source>There are %n new printings available on Scryfall. Update the local data now?</source>
      <translation>
        <numerusform>Es ist %n neue Karte auf Scryfall verfügbar. Lokale Daten jetzt aktualisieren?</numerusform>
        <numerusform>Es sind %n neue Karten auf Scryfall verfügbar. Lokale Daten jetzt aktualisieren?</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="494"/>
      <source>Check for application updates?</source>
      <translation>Nach Anwendungsaktualisierungen suchen?</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="494"/>
      <source>Automatically check for application updates whenever you start {program_name}?</source>
      <translation>Beim Anwendungsstart automatisch nach Updates suchen?</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="506"/>
      <source>Check for card data updates?</source>
      <translation>Suche nach Kartendaten-Updates?</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="506"/>
      <source>Automatically check for card data updates on Scryfall whenever you start {program_name}?</source>
      <translation>Automatisch nach Kartenupdates auf Scryfall prüfen, wann immer Sie {program_name} starten?</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="516"/>
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
      <location filename="../ui/main_window.ui" line="195"/>
      <source>Settings</source>
      <translation>Einstellungen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="73"/>
      <source>Edit</source>
      <translation>Bearbeiten</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="326"/>
      <source>Show toolbar</source>
      <translation>Werkzeugleiste anzeigen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="134"/>
      <source>&amp;Quit</source>
      <translation>&amp;Beenden</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="137"/>
      <source>Ctrl+Q</source>
      <translation>Strg+Q</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="148"/>
      <source>&amp;Print</source>
      <translation>&amp;Drucken</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="151"/>
      <source>Print the current document</source>
      <translation>Aktuelles Dokument drucken</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="154"/>
      <source>Ctrl+P</source>
      <translation>Strg+P</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="162"/>
      <source>&amp;Show print preview</source>
      <translation>Druckvorschau</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="165"/>
      <source>Show print preview window</source>
      <translation>Druckvorschau anzeigen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="173"/>
      <source>&amp;Create PDF</source>
      <translation>PDF erzeugen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="176"/>
      <source>Create a PDF document</source>
      <translation>Als PDF-Dokument exportieren</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="184"/>
      <source>Discard page</source>
      <translation>Seite verwerfen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="187"/>
      <source>Discard this page.</source>
      <translation>Diese Seite verwerfen.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="206"/>
      <source>Update card data</source>
      <translation>Kartendaten aktualisieren</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="214"/>
      <source>New Page</source>
      <translation>Neue Seite</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="217"/>
      <source>Add a new, empty page.</source>
      <translation>Neue, leere Seite hinzufügen.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="225"/>
      <source>Save</source>
      <translation>Speichern</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="228"/>
      <source>Ctrl+S</source>
      <translation>Strg+S</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="236"/>
      <source>New</source>
      <translation>Neu</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="239"/>
      <source>Ctrl+N</source>
      <translation>Strg+N</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="247"/>
      <source>Load</source>
      <translation>Laden</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="250"/>
      <source>Ctrl+L</source>
      <translation>Strg+L</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="258"/>
      <source>Save as …</source>
      <translation>Speichern unter …</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="263"/>
      <source>About …</source>
      <translation>Über …</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="271"/>
      <source>Show Changelog</source>
      <translation>Änderungsprotokoll anzeigen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="279"/>
      <source>Compact document</source>
      <translation>Dokument kompaktieren</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="282"/>
      <source>Minimize page count: Fill empty slots on pages by moving cards from the end of the document</source>
      <translation>Seitenzahl minimieren: Leerstellen auf Seiten durch das Verschieben von Karten vom Dokumentenende füllen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="290"/>
      <source>Edit document settings</source>
      <translation>Einstellungen dieses Dokuments</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="293"/>
      <source>Configure page size, margins, image spacings for the currently edited document.</source>
      <translation>Einstellungen des aktuellen Dokuments, wie Papiergröße, Rand- und Bildabstände anpassen.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="304"/>
      <source>Import a deck list from online sources</source>
      <translation>Eine Deckliste aus dem Internet importieren</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="312"/>
      <source>Cleanup card images</source>
      <translation>Kartenbilder bereinigen/löschen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="315"/>
      <source>Delete locally stored card images you no longer need.</source>
      <translation>Nicht mehr benötigte, gespeicherte Kartenbilder löschen.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="329"/>
      <source>Ctrl+M</source>
      <translation>Strg+M</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="337"/>
      <source>Download missing card images</source>
      <translation>Fehlende Kartenbilder herunterladen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="345"/>
      <source>Shuffle document</source>
      <translation>Dokument mischen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="348"/>
      <source>Randomly rearrange all card image.
If you want to quickly print a full deck for playing,
use this to reduce the initial deck shuffling required</source>
      <translation>Alle Karten zufällig neu anordnen.
Wenn Sie schnell ein komplettes Deck für das Spielen drucken möchten,
können Sie dies verwenden, um den Aufwand beim initialen Mischen zu reduzieren</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="361"/>
      <source>Undo</source>
      <translation>Rückgängig</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="372"/>
      <source>Redo</source>
      <translation>Wiederholen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="301"/>
      <source>Import deck list</source>
      <translation>Deckliste importieren</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="380"/>
      <source>Add empty card to page</source>
      <translation>Leere Karte zur Seite hinzufügen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="383"/>
      <source>Add an empty spacer filling a card slot</source>
      <translation>Ein Feld auf der aktuellen Seite leer halten</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="391"/>
      <source>Add custom cards</source>
      <translation>Inoffizielle Karten hinzufügen</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="327"/>
      <source>exporting as a PNG image sequence</source>
      <comment>This is passed as the {action} when asking the user about compacting the document if that can save pages</comment>
      <translation>exportieren als PNG-Bildsequenz</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="402"/>
      <source>Export document as an image sequence</source>
      <translation>Dokument als Bildsequenz exportieren</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="413"/>
      <source>Export all card images to a directory</source>
      <translation>Alle Kartenbilder in ein Verzeichnis exportieren</translation>
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
      <location filename="../ui/main_window.ui" line="399"/>
      <source>Export as image sequence</source>
      <translation>Als Bildsequenz exportieren</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="410"/>
      <source>Export individual card images</source>
      <translation>Einzelne Kartenbilder exportieren</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="89"/>
      <source>Web links</source>
      <translation>Weblinks</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="421"/>
      <source>Source Code</source>
      <translation>Quellcode</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="429"/>
      <source>Source Code (GitHub)</source>
      <translation>Quellcode (GitHub)</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="437"/>
      <source>Contribute Translations</source>
      <translation>Übersetzungen beitragen</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="445"/>
      <source>Project on PyPI</source>
      <translation>Projekt auf PyPI</translation>
    </message>
  </context>
  <context>
    <name>PNGRenderer</name>
    <message>
      <location filename="../../print.py" line="85"/>
      <source>Export as PNGs</source>
      <translation>Als PNGs exportieren</translation>
    </message>
  </context>
  <context>
    <name>PageCardTableView</name>
    <message numerus="yes">
      <location filename="../../ui/page_card_table_view.py" line="128"/>
      <source>Add %n copies</source>
      <comment>Context menu action: Add additional card copies to the document</comment>
      <translation>
        <numerusform>Kopie hinzufügen</numerusform>
        <numerusform>%n Kopien hinzufügen</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../ui/page_card_table_view.py" line="134"/>
      <source>Add copies …</source>
      <comment>Context menu action: Add additional card copies to the document. User will be asked for a number</comment>
      <translation>Kopien hinzufügen …</translation>
    </message>
    <message>
      <location filename="../../ui/page_card_table_view.py" line="121"/>
      <source>Generate DFC check card</source>
      <translation>Platzhalterkarte generieren</translation>
    </message>
    <message>
      <location filename="../../ui/page_card_table_view.py" line="148"/>
      <source>All related cards</source>
      <translation>Alle zugehörigen Karten</translation>
    </message>
    <message>
      <location filename="../../ui/page_card_table_view.py" line="156"/>
      <source>Add copies</source>
      <translation>Kopien hinzufügen</translation>
    </message>
    <message>
      <location filename="../../ui/page_card_table_view.py" line="156"/>
      <source>Add copies of {card_name}</source>
      <comment>Asks the user for a number. Does not need plural forms</comment>
      <translation>Kopien von {card_name} hinzufügen</translation>
    </message>
    <message>
      <location filename="../../ui/page_card_table_view.py" line="182"/>
      <source>Export image</source>
      <translation>Bild exportieren</translation>
    </message>
    <message>
      <location filename="../../ui/page_card_table_view.py" line="197"/>
      <source>Save card image</source>
      <translation>Kartenbild speichern</translation>
    </message>
    <message>
      <location filename="../../ui/page_card_table_view.py" line="197"/>
      <source>Images (*.png *.bmp *.jpg)</source>
      <translation>Bilder (*.png *.bmp *.jpg)</translation>
    </message>
  </context>
  <context>
    <name>PageConfigPreviewArea</name>
    <message>
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
    <message numerus="yes">
      <location filename="../../ui/page_config_widget.py" line="172"/>
      <source>%n regular card(s)</source>
      <comment>Display of the resulting page capacity for regular-sized cards</comment>
      <translation>
        <numerusform>%n reguläre Karte</numerusform>
        <numerusform>%n reguläre Karten</numerusform>
      </translation>
    </message>
    <message numerus="yes">
      <location filename="../../ui/page_config_widget.py" line="176"/>
      <source>%n oversized card(s)</source>
      <comment>Display of the resulting page capacity for oversized cards</comment>
      <translation>
        <numerusform>%n übergroße Karte</numerusform>
        <numerusform>%n übergroße Karten</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../ui/page_config_widget.py" line="181"/>
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
      <location filename="../ui/page_config_widget.ui" line="396"/>
      <source>Number of cards fitting on each page,
based on the page size and spacings configured</source>
      <translation>Anzahl der regulären Karten auf jeder Seite,
basierend auf der Seitengröße und den konfigurierten Rand- und Kartenabständen</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="309"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the left paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Mindestspanne zwischen dem linken Papierrand und dem Seiteninhalt.&lt;/p&gt;&lt;p&gt;Die meisten Drucker haben eine Mindestspanne von 3 bis 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="386"/>
      <source> mm</source>
      <translation> mm</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="80"/>
      <source>Paper height in millimeters.
Must match the size of the sheets in the printer.
Otherwise, scaling may be applied by the printer driver.</source>
      <translation>Papierhöhe in Millimetern.
Muss mit der Größe der Blätter im Drucker übereinstimmen.
Andernfalls könnte der Druckertreiber das Dokument skalieren.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="234"/>
      <source>Top margin</source>
      <translation>Oberer Rand</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="328"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the right paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Mindestspanne zwischen dem rechten Papierrand und dem Seiteninhalt.&lt;/p&gt;&lt;p&gt;Die meisten Drucker haben eine Mindestspanne von 3 bis 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="629"/>
      <source>If enabled, the page number is printed on each page. Makes it easier to notice missing pages in a stack.</source>
      <translation>Wenn aktiviert, wird die Seitennummer auf jeder Seite ausgedruckt. Dadurch wird es einfacher, fehlende Seiten in einem Stapel zu bemerken.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="632"/>
      <source>Print page numbers</source>
      <translation>Seitennummern drucken</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="211"/>
      <source>Resulting page capacity:</source>
      <translation>Seitenkapazität:</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="124"/>
      <source>Card bleed</source>
      <translation>Kartenumrandung</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="285"/>
      <source>Paper width in millimeters.
Must match the size of the sheets in the printer.
Otherwise, scaling may be applied by the printer driver.</source>
      <translation>Papierbreite in Millimetern.
Muss mit der Größe der Blätter im Drucker übereinstimmen.
Andernfalls könnte der Druckertreiber das Dokument skalieren.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="606"/>
      <source>Enable printing additional lines to aid cutting the printed sheets.</source>
      <translation>Aktivieren Sie das Drucken zusätzlicher Schneidhilfslinien, um das Schneiden der gedruckten Seiten zu erleichtern.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="609"/>
      <source>Print cut markers</source>
      <translation>Schnittmarkierungen drucken</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="368"/>
      <source>Space between image rows in mm.
If set to zero, you only need one cut to separate two images,
otherwise you need two cuts but require less precision hitting the exact middle.</source>
      <translation>Abstand zwischen den Bildzeilen in mm.
Wenn Sie diesen Wert auf null setzen, benötigen Sie nur einen Schnitt, um zwei Zeilen zu trennen.
Andernfalls sind zwei Schnitte erforderlich, die jedoch weniger Präzision erfordern.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="639"/>
      <source>Draw 90° card corners, instead of round ones</source>
      <translation>90°-Kartenecken zeichnen</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="169"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the top paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Mindestabstand zwischen dem oberen Papierrand und dem Seiteninhalt.&lt;/p&gt;&lt;p&gt;Die meisten Drucker haben einen Mindestabstand von 3 bis 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="596"/>
      <source>Document name</source>
      <translation>Dokumentenname</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="150"/>
      <source>Row spacing</source>
      <translation>Zeilenabstand</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="26"/>
      <source>The document name is printed on each page and can help you keep track
of different printed sheets and to which deck they belong.

Leave empty to disable.</source>
      <translation>Der Dokumentenname wird auf jeder Seite gedruckt,
um Stapel gedruckter Seiten auseinanderhalten zu können.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="35"/>
      <source>Document/deck name</source>
      <translation>Dokument-/Deckname</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="383"/>
      <source>Draw an additional border around cards to ease cutting.</source>
      <translation>Einen zusätzlichen Rand um die Karten zeichnen, um das Schneiden zu erleichtern.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="221"/>
      <source>Left margin</source>
      <translation>Linker Rand</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="347"/>
      <source>Space between image columns in mm.
If set to zero, you only need one cut to separate two images,
otherwise you need two cuts but require less precision hitting the exact middle.</source>
      <translation>Abstand zwischen den Bildspalten in mm.
Wenn Sie diesen Wert auf null setzen, benötigen Sie nur einen Schnitt, um zwei Spalten zu trennen.
Andernfalls sind zwei Schnitte erforderlich, die jedoch weniger Präzision erfordern.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="61"/>
      <source>Switch between portrait and landscape mode</source>
      <translation>Zwischen Hoch- und Querformat wechseln</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="64"/>
      <source>Flip</source>
      <translation>Drehen</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="198"/>
      <source>Column spacing</source>
      <translation>Spaltenabstand</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="98"/>
      <source>Right margin</source>
      <translation>Rechter Rand</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="266"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the bottom paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Mindestabstand zwischen dem unteren Papierrand und dem Seiteninhalt.&lt;/p&gt;&lt;p&gt;Die meisten Drucker haben einen Mindestabstand von 3 bis 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="584"/>
      <source>Show Preview</source>
      <translation>Vorschau anzeigen</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="111"/>
      <source>Paper size</source>
      <translation>Papierformat</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="182"/>
      <source>Paper height</source>
      <translation>Seitenhöhe</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="137"/>
      <source>Paper width</source>
      <translation>Seitenbreite</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="49"/>
      <source>Paper dimensions</source>
      <translation>Papiermaße</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="247"/>
      <source>Bottom margin</source>
      <translation>Unterer Rand</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="408"/>
      <source>Watermark</source>
      <translation>Wasserzeichen</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="414"/>
      <source>X position</source>
      <translation>X-Position</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="424"/>
      <source>Y position</source>
      <translation>Y-Position</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="434"/>
      <source>Watermark text</source>
      <translation>Wasserzeichentext</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="457"/>
      <source>Rotation angle</source>
      <translation>Drehwinkel</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="483"/>
      <source>Font size</source>
      <translation>Schriftgröße</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="493"/>
      <source>Text color and opacity</source>
      <translation>Textfarbe und Deckkraft</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="519"/>
      <source>Select a color</source>
      <translation>Farbe wählen</translation>
    </message>
  </context>
  <context>
    <name>PageRenderer</name>
    <message>
      <location filename="../../ui/page_renderer.py" line="65"/>
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
      <location filename="../../decklist_parser/common.py" line="71"/>
      <source>All files (*)</source>
      <translation>Alle Dateien (*)</translation>
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
      <location filename="../../ui/settings_window_pages.py" line="507"/>
      <source>Printer settings</source>
      <translation>Druckereinstellungen</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="507"/>
      <source>Configure the printer</source>
      <translation>Drucker konfigurieren</translation>
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
  </context>
  <context>
    <name>PrintingFilterUpdater.store_current_printing_filters()</name>
    <message>
      <location filename="../../printing_filter_updater.py" line="118"/>
      <source>Processing updated card filters:</source>
      <translation>Verarbeite aktualisierte Kartenfilter:</translation>
    </message>
  </context>
  <context>
    <name>SaveDocumentAsDialog</name>
    <message>
      <location filename="../../ui/dialogs.py" line="190"/>
      <source>Save document as …</source>
      <translation>Dokument speichern unter …</translation>
    </message>
  </context>
  <context>
    <name>SavePDFDialog</name>
    <message>
      <location filename="../../ui/dialogs.py" line="91"/>
      <source>Export as PDF</source>
      <translation>Als PDF exportieren</translation>
    </message>
    <message>
      <location filename="../../ui/dialogs.py" line="92"/>
      <source>PDF documents (*.pdf)</source>
      <translation>PDF-Dokument (*.pdf)</translation>
    </message>
  </context>
  <context>
    <name>SavePNGDialog</name>
    <message>
      <location filename="../../ui/dialogs.py" line="133"/>
      <source>Export as PNG</source>
      <translation>Als PNG exportieren</translation>
    </message>
    <message>
      <location filename="../../ui/dialogs.py" line="134"/>
      <source>PNG images (*.png)</source>
      <translation>PNG-Bilder (*.png)</translation>
    </message>
  </context>
  <context>
    <name>ScryfallCSVParser</name>
    <message>
      <location filename="../../decklist_parser/csv_parsers.py" line="118"/>
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
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="228"/>
      <source>Deck list files, stored in XMage’s native format.
Because XMage closely follows Scryfall regarding Magic sets,
this should give very accurate results.</source>
      <translation>Decklisten-Dateien, gespeichert im XMage-eigenen Format.
Da XMage in Bezug auf Magic-Sets eng an Scryfall angelehnt ist,
sollte dies sehr genaue Ergebnisse liefern.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="233"/>
      <source>XMage</source>
      <translation>XMage</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="69"/>
      <source>This is a Tappedout-specific section of the deck.
It may contain the deck list author’s buy-list or anything else.</source>
      <translation>Dies ist ein Tappedout-spezifischer Abschnitt des Decks.
Er kann die Kaufliste des Autors oder irgendetwas anderes enthalten.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="73"/>
      <source>Include “Acquire-Board”</source>
      <translation>„Ankaufliste“ einschließen</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="240"/>
      <source>The simplistic format used by Magic Online. It does not specify exact printings, so may not give the best results.</source>
      <translation>Das einfache Format, das von Magic Online verwendet wird und keine genauen Ausdrucke angibt. Liefert daher nicht die besten Ergebnisse.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="243"/>
      <source>Magic Online</source>
      <translation>Magic-Online</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="26"/>
      <source>This is a Tappedout-specific section of the deck.
It may contain cards that the deck list creator considers for inclusion, based on the meta
or any other preference, like card price.</source>
      <translation>Dies ist ein Tappedout-spezifischer Abschnitt des Decks.
Er könnte Karten enthalten, die der Ersteller der Liste in Erwägung zieht, basierend auf der Meta oder anderen Präferenzen, wie z. B. dem Kartenpreis.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="31"/>
      <source>Include “Maybe-Board”</source>
      <translation>"Maybe-Board" einschließen</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="54"/>
      <source>CSV exports from Scryfall’s own deck builder.
Gives very accurate results, unless the imported deck list contains ignored items
matching an enabled card filter.</source>
      <translation>CSV, exportiert von Scryfalls eigenem Deck-Builder.
Ergibt sehr genaue Ergebnisse, es sei denn, die importierte Deckliste enthält durch Kartenfilter versteckte Drucke.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="59"/>
      <source>Scryfall.com deck lists (CSV export)</source>
      <translation>Scryfall.com Decklisten (CSV-Export)</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="257"/>
      <source>CSV exports can be downloaded from Tappedout by choosing the appropriate deck export option.</source>
      <translation>CSV-Exporte können von Tappedout heruntergeladen werden, indem Sie die entsprechende Deck-Export-Option wählen.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="260"/>
      <source>tappedout.net deck list (CSV export)</source>
      <translation>tappedout.net Deckliste (CSV-Export)</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="154"/>
      <source>Appends a sample matcher for a set code to the input field above.</source>
      <translation>Fügt einen Beispiel-Matcher für ein Setkürzel dem obigen Eingabefeld zu.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="157"/>
      <source>Set code matcher</source>
      <translation>Set-Matcher einfügen</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="99"/>
      <source>Appends a sample matcher for a collector number to the input field above</source>
      <translation>Fügt einen Beispiel-Matcher für eine Sammlernummer dem obigen Eingabefeld zu</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="102"/>
      <source>Collector number matcher</source>
      <translation>Matcher für Sammlernummer einfügen</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="140"/>
      <source>Appends a matcher for the number of card copies to the input field above.
If a card count field is not present in the deck list, 1 card copy per line is assumed</source>
      <translation>Fügt einen Matcher für die Kartenanzahl an das obige Eingabefeld an.
Wenn ein Feld für die Anzahl nicht vorhanden ist, wird eine Karte pro Zeile angenommen</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="144"/>
      <source>Copies matcher</source>
      <translation>Matcher für Kopien</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="112"/>
      <source>Appends a matcher for a card name to the input field above.</source>
      <translation>Fügt einen Matcher für einen Kartennamen dem obigen Eingabefeld zu.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="115"/>
      <source>Card name matcher</source>
      <translation>Matcher für Kartenname</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="125"/>
      <source>Appends a matcher for the Scryfall ID to the input field above.
This may be used by deck lists that closely integrate with the Scryfall website.
Most deck lists won’t use this.</source>
      <translation>Fügt einen Matcher für die Scryfall-ID an das obige Eingabefeld an.
Dies kann von Decklisten verwendet werden, die sich eng mit der Scryfall-Website verbinden.
Die meisten Decklisten werden dies nicht verwenden.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="130"/>
      <source>Scryfall ID matcher</source>
      <translation>Matcher für Scryfall ID</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="85"/>
      <source>Appends a matcher for the  card language to the input field above.
If a language field is not present in the deck list, the card language is guessed.</source>
      <translation>Fügt einen Matcher für die Kartensprache an das obige Eingabefeld an.
Wenn ein Sprachfeld in der Deckliste nicht vorhanden ist, wird die Kartensprache erraten.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="89"/>
      <source>Language matcher</source>
      <translation>Matcher für Sprache</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="267"/>
      <source>Specify a custom regular expression in the input field below. It will be used to parse each deck list line.
You can use the buttons below to insert basic building blocks.
You have to separate them with the “control structures”, like spaces, as used in your deck list.</source>
      <translation>Geben Sie einen benutzerdefinierten regulären Ausdruck im Eingabefeld unten an. Er wird verwendet, um jede Decklistenzeile zu analysieren.
Sie können die Schaltflächen unten benutzen, um Grundbausteine einzufügen. 
Sie müssen die Bausteine mit den „Kontrollstrukturen“ des Listenformats trennen, wie z.B. Leerzeichen, genau so, wie sie in Ihrer Deckliste verwendet werden.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="272"/>
      <source>Custom regular expression based parser:</source>
      <translation>Benutzerdefinierter Parser basierend auf regulären Ausdrücken:</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="216"/>
      <source>Magic Arena and exports from compatible websites, like moxfield.com
Note that this option is not limited to cards in Standard/Historic,
as the format works for any card.</source>
      <translation>Magic Arena, und Exporte von kompatiblen Webseiten, wie moxfield.com
Beachten Sie, dass diese Option nicht auf Karten in Standard/Historic beschränkt ist,
da das Format für jede Karte funktioniert.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="221"/>
      <source>MTG Arena</source>
      <translation>MTG Arena</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="167"/>
      <source>Enter a Regular Expression containing at least one supported, named group.

Supported named groups are: {group_names}

See the 'What’s this?' (?-Button) help for details.</source>
      <translation>Geben Sie einen regulären Ausdruck ein, der mindestens eine unterstützte, benannte Gruppe enthält.

Unterstützte benannte Gruppen sind: {group_names}

Siehe "Was ist das?"-Hilfe (?-Button) für Details.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="174"/>
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
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="250"/>
      <source>Magic Workstation Deck Data (mwDeck)</source>
      <translation>Magic Workstation Deck Data (mwDeck)</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="308"/>
      <source>A simple list, containing one card name per line</source>
      <translation>Eine einfache Liste mit einem Kartennamen pro Zeile</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="311"/>
      <source>List with card names</source>
      <translation>Liste mit Kartennamen</translation>
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
      <location filename="../../ui/settings_window.py" line="207"/>
      <source>Apply settings to the current document?</source>
      <translation>Einstellungen auf das aktuelle Dokument anwenden?</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="207"/>
      <source>The new default settings differ from the settings used by the current document.
Apply the new settings to the current document?</source>
      <translation>Die neuen Standardeinstellungen unterscheiden sich von den Einstellungen des aktuellen Dokuments.
Neue Einstellungen auf das aktuelle Dokument anwenden?</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="220"/>
      <source>Reset unsaved changes?</source>
      <translation>Ungespeicherte Änderungen zurücksetzen?</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="220"/>
      <source>Reset unsaved changes on the current page or on all pages?</source>
      <translation>Ungespeicherte Änderungen auf der aktuellen Seite oder auf allen Seiten zurücksetzen?</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="226"/>
      <source>Reset everything</source>
      <translation>Alles zurücksetzen</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="227"/>
      <source>Reset current page</source>
      <translation>Diese Seite</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="254"/>
      <source>Restore defaults for the current page or everything?</source>
      <translation>Standardwerte für die aktuelle Seite oder für alle Seiten wiederherstellen?</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="254"/>
      <source>Restore the settings on the current page or on all pages to their default values?</source>
      <translation>Einstellungen auf der aktuellen Seite oder auf allen Seiten auf ihre Standardwerte zurücksetzen?</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="260"/>
      <source>Restore everything</source>
      <translation>Alle Seiten</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="261"/>
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
    <message numerus="yes">
      <location filename="../../ui/deck_import_wizard.py" line="479"/>
      <source>Beware: The card list currently contains %n potentially oversized card(s).</source>
      <comment>Warning emitted, if at least 1 card has the oversized flag set. The Scryfall server *may* still return a regular-sized image, so not *all* printings marked as oversized are actually so when fetched.</comment>
      <translation>
        <numerusform>Achtung: Die Deckliste enthält derzeit %n potenziell übergroße Karte.</numerusform>
        <numerusform>Achtung: Die Deckliste enthält derzeit %n potenziell übergroße Karten.</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="499"/>
      <source>Replace document content with the identified cards</source>
      <translation>Dokumenteninhalt durch identifizierte Karten ersetzen</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="502"/>
      <source>Append identified cards to the document</source>
      <translation>Identifizierte Karten an das Dokument anhängen</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="538"/>
      <source>Remove basic lands</source>
      <translation>Standardländer entfernen</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="539"/>
      <source>Remove all basic lands in the deck list above</source>
      <translation>Entferne alle Standardländer in der obrigen Deckliste</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="544"/>
      <source>Remove selected</source>
      <translation>Ausgewählte entfernen</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="545"/>
      <source>Remove all selected cards in the deck list above</source>
      <translation>Entferne alle ausgewählten Karten in der obrigen Deckliste</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="438"/>
      <source>Images about to be deleted: {count}</source>
      <translation>Zu löschende Bilder: {count}</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="439"/>
      <source>Disk space that will be freed: {disk_space_freed}</source>
      <translation>Frei werdender Speicherplatz: {disk_space_freed}</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/summary_page.ui" line="14"/>
      <source>Summary</source>
      <translation>Überblick</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="14"/>
      <source>Import a deck list for printing</source>
      <translation>Deckliste zum Drucken importieren</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="17"/>
      <source>The cards shown here will be imported. Double-click the Set Collector# or Language cells to change selected printings. The text field shows all lines from the input that were not identified as cards.</source>
      <translation>Die hier gezeigten Karten werden importiert. Doppelklicken Sie auf Set, Sammler#-, oder Sprachzellen, um die ausgewählten Drucke zu ändern. Das Textfeld zeigt alle Zeilen der Eingabe, die nicht als Karten identifiziert wurden.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="23"/>
      <source>If checked, clear all cards in the current document, replacing everything with the list below.
If unchecked, append the cards found below to the document.</source>
      <translation>Wenn aktiviert, lösche alle Karten im aktuellen Dokument und ersetze sie durch die Liste unten.
Wenn nicht ausgewählt, füge die unten gefundenen Karten dem Dokument an.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="27"/>
      <source>Replace the current document content with the found cards</source>
      <translation>Den aktuellen Dokumenteninhalt durch die gefundenen Karten ersetzen</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="37"/>
      <source>These cards were successfully identified:</source>
      <translation>Nichts. Alle Karten erfolgreich identifiziert:</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="66"/>
      <source>These lines from the deck list were not identified as cards:</source>
      <translation>Diese Zeilen aus der Deckliste wurden nicht als Karten identifiziert:</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="85"/>
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
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="38"/>
      <source>Add new cards</source>
      <translation>Karten hinzufügen</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="43"/>
      <source>Current page</source>
      <translation>Aktuelle Seite</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="89"/>
      <source>Remove selected</source>
      <translation>Ausgewählte entfernen</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="100"/>
      <source>Preview</source>
      <translation>Vorschau</translation>
    </message>
  </context>
  <context>
    <name>TappedOutCSVParser</name>
    <message>
      <location filename="../../decklist_parser/csv_parsers.py" line="197"/>
      <source>Tappedout CSV export</source>
      <translation>Tappedout CSV-Export</translation>
    </message>
  </context>
  <context>
    <name>UnknownCardImageModel</name>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="256"/>
      <source>Scryfall ID</source>
      <translation>Scryfall ID</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="257"/>
      <source>Front/Back</source>
      <translation>Vorder-/Rückseite</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="258"/>
      <source>High resolution?</source>
      <translation>Hohe Qualität?</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="259"/>
      <source>Size</source>
      <translation>Größe</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="260"/>
      <source>Path</source>
      <translation>Dateipfad</translation>
    </message>
  </context>
  <context>
    <name>UnknownCardRow</name>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="230"/>
      <source>Front</source>
      <translation>Vorderseite</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="230"/>
      <source>Back</source>
      <translation>Rückseite</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="236"/>
      <source>Yes</source>
      <translation>Ja</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="236"/>
      <source>No</source>
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
      <translation>Sprache:</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="152"/>
      <source>Copies:</source>
      <translation>Kopien:</translation>
    </message>
  </context>
  <context>
    <name>XMageParser</name>
    <message>
      <location filename="../../decklist_parser/re_parsers.py" line="257"/>
      <source>XMage Deck file</source>
      <translation>XMage Deck-Datei</translation>
    </message>
  </context>
  <context>
    <name>format_size</name>
    <message>
      <location filename="../../ui/common.py" line="180"/>
      <source>{size} {unit}</source>
      <comment>A formatted file size in SI bytes</comment>
      <translation>{size} {unit}</translation>
    </message>
  </context>
</TS>
