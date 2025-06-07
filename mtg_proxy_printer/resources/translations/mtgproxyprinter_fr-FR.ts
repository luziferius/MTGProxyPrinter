<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="fr" sourcelanguage="en-US">
  <context>
    <name>AboutDialog</name>
    <message>
      <location filename="../ui/about_dialog.ui" line="14"/>
      <source>About MTGProxyPrinter</source>
      <translation>À propos de MTGProxyPrinter</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="27"/>
      <source>About</source>
      <translation>À propos</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="39"/>
      <source>Application Version:</source>
      <translation>Version de l'application :</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="55"/>
      <source>Last card update:</source>
      <translation>Dernière mise à jour des cartes :</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="62"/>
      <source>Application version</source>
      <translation>Version de l'application</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="87"/>
      <source>Python Version:</source>
      <translation>Version de Python :</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="107"/>
      <source>Python runtime version</source>
      <translation>Version du runtime Python</translation>
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
      <translation>{application_name} permets d'imprimer des cartes [Magic : The Gathering](https://magic.wizards.com/) pour tester des decks.

{application_name} est une application non-officielle créé par des fans suivant la [Politique de Wizards of the Coast sur les contenus de fans](https://company.wizards.com/fancontentpolicy). Elle n'est donc pas supporté/approuvé officiellement par Wizards of the Coast. Une partie des éléments utilisés par ce programme sont des propriétés de Wizards of the Coast. ©[Wizards of the Coast LLC](https://company.wizards.com/).

De part la Politique de Wizards of the Coast sur les contenus de fans, vous ne pouvez vendre ni les données téléchargées, incluant le contenu de la base de données des cartes et les images de cartes téléchargées, ni les documents générés, physiquement ou sous forme numérique, via ce programme.

Site du projet : [Page d'accueil de {application_name}]({application_home_page})

Icône du projet par [islanders2013](https://www.reddit.com/user/islanders2013/)
</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="214"/>
      <source>Changelog</source>
      <translation>Historique des modifications</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="228"/>
      <source>License</source>
      <translation>Licence</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="239"/>
      <source>Third party licenses</source>
      <translation>Licences tierces</translation>
    </message>
  </context>
  <context>
    <name>ActionAddCard</name>
    <message numerus="yes">
      <location filename="../../document_controller/card_actions.py" line="161"/>
      <source>Add {count} × {card_display_string} to page {target}</source>
      <comment>Undo/redo tooltip text. Plural form refers to {target}, not {count}. {target} can be multiple ranges of multiple pages each</comment>
      <translation>
        <numerusform>Ajouter {count} × {card_display_string} à la page {target}</numerusform>
        <numerusform>Ajouter {count} × {card_display_string} à la page {target}</numerusform>
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
        <numerusform>Compression du document, %n page(s) seront supprimées</numerusform>
        <numerusform>Compression du document, %n page(s) seront supprimées</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionEditCustomCard</name>
    <message>
      <location filename="../../document_controller/edit_custom_card.py" line="85"/>
      <source>Edit custom card, set {column_header_text} to {new_value}</source>
      <comment>Undo/redo tooltip text</comment>
      <translation type="unfinished">Edit custom card, set {column_header_text} to {new_value}</translation>
    </message>
  </context>
  <context>
    <name>ActionEditDocumentSettings</name>
    <message>
      <location filename="../../document_controller/edit_document_settings.py" line="133"/>
      <source>Update document settings</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Mettre à jour les paramètres du document</translation>
    </message>
  </context>
  <context>
    <name>ActionImportDeckList</name>
    <message numerus="yes">
      <location filename="../../document_controller/import_deck_list.py" line="82"/>
      <source>Import a deck list containing %n card(s)</source>
      <comment>Undo/redo tooltip text. Option to delete the current document disabled.</comment>
      <translation>
        <numerusform>Import d'une liste de cartes contenant %n carte(s)</numerusform>
        <numerusform>Import d'une liste de cartes contenant %n carte(s)</numerusform>
      </translation>
    </message>
    <message numerus="yes">
      <location filename="../../document_controller/import_deck_list.py" line="77"/>
      <source>Replace document with imported deck list containing %n card(s)</source>
      <comment>Undo/redo tooltip text. Option to delete the current document enabled.</comment>
      <translation>
        <numerusform>Remplacer le document par la liste de cartes importée contenant %n carte(s)</numerusform>
        <numerusform>Remplacer le document par la liste de cartes importée contenant %n carte(s)</numerusform>
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
        <numerusform>Charger le document depuis &apos;{save_path}&apos;, contenant %n page(s) {cards_total}</numerusform>
        <numerusform>Charger le document depuis &apos;{save_path}&apos;, contenant %n page(s) {cards_total}</numerusform>
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
        <numerusform>avec un total de %n carte(s)</numerusform>
        <numerusform>avec un total de %n carte(s)</numerusform>
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
        <numerusform>Déplacer %n carte(s) de la page {source_page} à la page {target_page}</numerusform>
        <numerusform>Déplacer %n carte(s) de la page {source_page} à la page {target_page}</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionNewDocument</name>
    <message>
      <location filename="../../document_controller/new_document.py" line="69"/>
      <source>Create new document</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Créer un nouveau document</translation>
    </message>
  </context>
  <context>
    <name>ActionNewPage</name>
    <message numerus="yes">
      <location filename="../../document_controller/page_actions.py" line="82"/>
      <source>Add page(s) {pages}</source>
      <comment>Undo/redo tooltip text. Translations should drop the %n placeholder</comment>
      <translation>
        <numerusform>Ajouter {pages} page(s)</numerusform>
        <numerusform>Ajouter {pages} page(s)</numerusform>
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
        <numerusform>Supprimer %n carte(s) de la page {page_number}</numerusform>
        <numerusform>Supprimer %n carte(s) de la page {page_number}</numerusform>
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
        <numerusform>%n carte(s) au total</numerusform>
        <numerusform>%n carte(s) au total</numerusform>
      </translation>
    </message>
    <message numerus="yes">
      <location filename="../../document_controller/page_actions.py" line="188"/>
      <source>Remove page(s) {formatted_pages} containing {formatted_card_count}</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>
        <numerusform>Supprimer la/les page(s) {formatted_pages} contenant {formatted_card_count}</numerusform>
        <numerusform>Supprimer la/les page(s) {formatted_pages} contenant {formatted_card_count}</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionReplaceCard</name>
    <message>
      <location filename="../../document_controller/replace_card.py" line="99"/>
      <source>Replace card {old_card} on page {page_number} with {new_card}</source>
      <comment>Undo/redo tooltip text</comment>
      <translation type="unfinished">Replace card {old_card} on page {page_number} with {new_card}</translation>
    </message>
  </context>
  <context>
    <name>ActionSaveDocument</name>
    <message>
      <location filename="../../document_controller/save_document.py" line="169"/>
      <source>Save document to &apos;{save_file_path}&apos;.</source>
      <translation type="unfinished">Save document to &apos;{save_file_path}&apos;.</translation>
    </message>
  </context>
  <context>
    <name>ActionShuffleDocument</name>
    <message>
      <location filename="../../document_controller/shuffle_document.py" line="102"/>
      <source>Shuffle document</source>
      <comment>Undo/redo tooltip text</comment>
      <translation type="unfinished">Shuffle document</translation>
    </message>
  </context>
  <context>
    <name>CacheCleanupWizard</name>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="458"/>
      <source>Cleanup locally stored card images</source>
      <comment>Dialog window title</comment>
      <translation type="unfinished">Cleanup locally stored card images</translation>
    </message>
  </context>
  <context>
    <name>CardFilterPage</name>
    <message>
      <location filename="../ui/cache_cleanup_wizard/card_filter_page.ui" line="14"/>
      <source>Select images for removal</source>
      <translation>Sélectionner les images à supprimer</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/card_filter_page.ui" line="17"/>
      <source>Click on entries in the tables below to mark or un-mark them for removal. All selected entries will be removed.</source>
      <translation>Cliquez sur les entrées dans les tableaux ci-dessous pour les sélectionner ou les désélectionner. Toutes les entrées sélectionnées seront supprimées.</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/card_filter_page.ui" line="30"/>
      <source>All images currently stored on disk:</source>
      <translation>Toutes les images stockées sur le disque :</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/card_filter_page.ui" line="69"/>
      <source>Images found on disk that can not be associated with any card.</source>
      <translation type="unfinished">Images found on disk that can not be associated with any card.</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/card_filter_page.ui" line="72"/>
      <source>Unknown images:</source>
      <translation>Images inconnues :</translation>
    </message>
  </context>
  <context>
    <name>CardListModel</name>
    <message>
      <location filename="../../model/card_list.py" line="89"/>
      <source>Card name</source>
      <translation type="unfinished">Card name</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="90"/>
      <source>Set</source>
      <translation type="unfinished">Set</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="91"/>
      <source>Collector #</source>
      <translation>Numéro de collection</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="92"/>
      <source>Language</source>
      <translation>Langage</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="93"/>
      <source>Side</source>
      <translation>Côté</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="130"/>
      <source>Front</source>
      <translation type="unfinished">Front</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="130"/>
      <source>Back</source>
      <translation type="unfinished">Back</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="134"/>
      <source>Beware: Potentially oversized card!
This card may not fit in your deck.</source>
      <translation type="unfinished">Beware: Potentially oversized card!
This card may not fit in your deck.</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="324"/>
      <source>Double-click on entries to
switch the selected printing.</source>
      <translation type="unfinished">Double-click on entries to
switch the selected printing.</translation>
    </message>
    <message>
      <location filename="../../model/card_list.py" line="88"/>
      <source>Copies</source>
      <translation type="unfinished">Copies</translation>
    </message>
  </context>
  <context>
    <name>CardSideSelectionDelegate</name>
    <message>
      <location filename="../../ui/item_delegates.py" line="100"/>
      <source>Front</source>
      <translation type="unfinished">Front</translation>
    </message>
    <message>
      <location filename="../../ui/item_delegates.py" line="101"/>
      <source>Back</source>
      <translation type="unfinished">Back</translation>
    </message>
  </context>
  <context>
    <name>ColumnarCentralWidget</name>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="61"/>
      <source>All pages:</source>
      <translation type="unfinished">All pages:</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="68"/>
      <source>Current page:</source>
      <translation>Page en cours :</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="78"/>
      <source>Remove selected</source>
      <translation>Supprimer la sélection</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="88"/>
      <source>Add new cards:</source>
      <translation>Ajouter de nouvelles cartes :</translation>
    </message>
  </context>
  <context>
    <name>CustomCardImportDialog</name>
    <message>
      <location filename="../ui/custom_card_import_dialog.ui" line="14"/>
      <source>Import custom cards</source>
      <translation type="unfinished">Import custom cards</translation>
    </message>
    <message>
      <location filename="../ui/custom_card_import_dialog.ui" line="20"/>
      <source>Set Copies to …</source>
      <translation type="unfinished">Set Copies to …</translation>
    </message>
    <message>
      <location filename="../ui/custom_card_import_dialog.ui" line="40"/>
      <source>Remove selected</source>
      <translation type="unfinished">Remove selected</translation>
    </message>
    <message>
      <location filename="../ui/custom_card_import_dialog.ui" line="50"/>
      <source>Load images</source>
      <translation type="unfinished">Load images</translation>
    </message>
  </context>
  <context>
    <name>DatabaseImportWorker</name>
    <message>
      <location filename="../../card_info_downloader.py" line="425"/>
      <source>Error during import from file:
{path}</source>
      <translation type="unfinished">Error during import from file:
{path}</translation>
    </message>
    <message>
      <location filename="../../card_info_downloader.py" line="436"/>
      <source>Updating card data from Scryfall:</source>
      <comment>Progress bar label text</comment>
      <translation type="unfinished">Updating card data from Scryfall:</translation>
    </message>
    <message>
      <location filename="../../card_info_downloader.py" line="446"/>
      <source>Reading from socket failed: {error}</source>
      <translation type="unfinished">Reading from socket failed: {error}</translation>
    </message>
    <message>
      <location filename="../../card_info_downloader.py" line="462"/>
      <source>Importing card data from disk:</source>
      <comment>Progress bar label text</comment>
      <translation type="unfinished">Importing card data from disk:</translation>
    </message>
    <message>
      <location filename="../../card_info_downloader.py" line="482"/>
      <source>Failed to parse data from Scryfall. Reported error: {error}</source>
      <translation type="unfinished">Failed to parse data from Scryfall. Reported error: {error}</translation>
    </message>
    <message>
      <location filename="../../card_info_downloader.py" line="526"/>
      <source>Post-processing card data:</source>
      <translation type="unfinished">Post-processing card data:</translation>
    </message>
  </context>
  <context>
    <name>DatabaseMigrationRunner</name>
    <message>
      <location filename="../../carddb_migrations.py" line="792"/>
      <source>Running database migrations:</source>
      <translation type="unfinished">Running database migrations:</translation>
    </message>
    <message numerus="yes">
      <location filename="../../carddb_migrations.py" line="808"/>
      <source>Migrate to version %n:</source>
      <comment>The numeric parameter is a version number, and not countable.</comment>
      <translation type="unfinished">
        <numerusform>Migrate to version %n:</numerusform>
        <numerusform>Migrate to version %n:</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>DebugSettingsPage</name>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="128"/>
      <source>Debug settings</source>
      <translation>Paramètres de débogage</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="128"/>
      <source>Things useful for investigating bugs in the application</source>
      <translation type="unfinished">Things useful for investigating bugs in the application</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="183"/>
      <source>Select download location</source>
      <translation type="unfinished">Select download location</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="191"/>
      <source>Selected location is not a directory</source>
      <translation type="unfinished">Selected location is not a directory</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="191"/>
      <source>Cannot write the card data at the given location, because it is not a directory:
{location}</source>
      <translation type="unfinished">Cannot write the card data at the given location, because it is not a directory:
{location}</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="204"/>
      <source>Import previously downloaded card data obtained from Scryfall</source>
      <translation type="unfinished">Import previously downloaded card data obtained from Scryfall</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="204"/>
      <source>Scryfall card data (*.json, *.json.gz)</source>
      <translation type="unfinished">Scryfall card data (*.json, *.json.gz)</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="214"/>
      <source>Selected location is not a file</source>
      <translation type="unfinished">Selected location is not a file</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="214"/>
      <source>Cannot find the selected file:
{location}</source>
      <translation type="unfinished">Cannot find the selected file:
{location}</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="17"/>
      <source>Open debug log directory</source>
      <translation>Ouvrir le répertoire des journaux de débogage</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="27"/>
      <source>Enable writing a log file to disk</source>
      <translation>Activer l'écriture d'un fichier journal sur le disque</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="34"/>
      <source>Cutelog is a live log event viewer that can be used to monitor events in real-time.</source>
      <translation type="unfinished">Cutelog is a live log event viewer that can be used to monitor events in real-time.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="37"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;See &lt;a href=&quot;https://github.com/busimus/cutelog&quot;&gt;&lt;span style=&quot; text-decoration: underline; color:#2980b9;&quot;&gt;https://github.com/busimus/cutelog&lt;/span&gt;&lt;/a&gt; for details about Cutelog.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation type="unfinished">&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;See &lt;a href=&quot;https://github.com/busimus/cutelog&quot;&gt;&lt;span style=&quot; text-decoration: underline; color:#2980b9;&quot;&gt;https://github.com/busimus/cutelog&lt;/span&gt;&lt;/a&gt; for details about Cutelog.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="40"/>
      <source>Enable Cutelog integration</source>
      <translation>Activer l'intégration Cutelog</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="47"/>
      <source>Download card data as file</source>
      <translation>Télécharger les données de la carte en tant que fichier</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="64"/>
      <source>Event severity that gets logged to file:</source>
      <translation>Sévérité des évènements qui seront enregistrés dans le fichier :</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="74"/>
      <source>Only write events with the given severity level and higher to the log file.</source>
      <translation type="unfinished">Only write events with the given severity level and higher to the log file.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="81"/>
      <source>Debug settings (Changing these require an application restart)</source>
      <translation>Paramètres de débogage (Changer ceux-ci nécessite un redémarrage de l'application)</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="101"/>
      <source>Import card data from file</source>
      <translation>Importer les données de cartes depuis un fichier</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="117"/>
      <source>Open the Cutelog homepage</source>
      <translation type="unfinished">Open the Cutelog homepage</translation>
    </message>
  </context>
  <context>
    <name>DeckImportWizard</name>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="611"/>
      <source>Import a deck list</source>
      <translation type="unfinished">Import a deck list</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="633"/>
      <source>Oversized cards present</source>
      <translation type="unfinished">Oversized cards present</translation>
    </message>
    <message numerus="yes">
      <location filename="../../ui/deck_import_wizard.py" line="633"/>
      <source>There are %n possibly oversized cards in the deck list that may not fit into a deck, when printed out.

Continue and use these cards as-is?</source>
      <translation type="unfinished">
        <numerusform>There are %n possibly oversized cards in the deck list that may not fit into a deck, when printed out.

Continue and use these cards as-is?</numerusform>
        <numerusform>There are %n possibly oversized cards in the deck list that may not fit into a deck, when printed out.

Continue and use these cards as-is?</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="644"/>
      <source>Incompatible file selected</source>
      <translation>Fichier sélectionné incompatible</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="644"/>
      <source>Unable to parse the given deck list, no results were obtained.
Maybe you selected the wrong deck list type?</source>
      <translation type="unfinished">Unable to parse the given deck list, no results were obtained.
Maybe you selected the wrong deck list type?</translation>
    </message>
  </context>
  <context>
    <name>DecklistImportSettingsPage</name>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="227"/>
      <source>Deck list import</source>
      <translation>Import de liste de cartes</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="227"/>
      <source>Configure the deck list importer</source>
      <translation type="unfinished">Configure the deck list importer</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="237"/>
      <source>Select default deck list search path</source>
      <translation type="unfinished">Select default deck list search path</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="17"/>
      <source>Browse …</source>
      <translation type="unfinished">Browse …</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="30"/>
      <source>Deck list search path</source>
      <translation>Chemin de recherche de listes de cartes</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="37"/>
      <source>The import wizard can remove basic lands fully- or semi-automatic.
These settings control the removal behavior.</source>
      <translation type="unfinished">The import wizard can remove basic lands fully- or semi-automatic.
These settings control the removal behavior.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="41"/>
      <source>Control the one-click or automatic basic land removal</source>
      <translation>Contrôlez l'enlèvement de terrain de base en un clic ou automatique</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="47"/>
      <source>If enabled, basic lands are automatically removed from deck lists.
If disabled, the deck import wizard keeps them by default,
but offers the removal via a single button click.</source>
      <translation type="unfinished">If enabled, basic lands are automatically removed from deck lists.
If disabled, the deck import wizard keeps them by default,
but offers the removal via a single button click.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="52"/>
      <source>Fully automatically remove basic lands</source>
      <translation>Supprimer automatiquement les terrains de base</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="59"/>
      <source>When enabled, treat Wastes like any other basic land</source>
      <translation type="unfinished">When enabled, treat Wastes like any other basic land</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="62"/>
      <source>Removal includes Wastes</source>
      <translation type="unfinished">Removal includes Wastes</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="69"/>
      <source>When enabled, treat Snow-Covered basic lands like any other basic land</source>
      <translation type="unfinished">When enabled, treat Snow-Covered basic lands like any other basic land</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="72"/>
      <source>Removal includes Snow-Covered Basic lands</source>
      <translation type="unfinished">Removal includes Snow-Covered Basic lands</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="82"/>
      <source>These options control the deck list import function.</source>
      <translation>Ces options contrôles les fonctions d'importation des listes de cartes.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="89"/>
      <source>Not all deck list formats always contain complete data.
These options set the default behavior when encountering ambiguous card</source>
      <translation type="unfinished">Not all deck list formats always contain complete data.
These options set the default behavior when encountering ambiguous card</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="93"/>
      <source>Control print selection in ambiguous cases</source>
      <translation type="unfinished">Control print selection in ambiguous cases</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="102"/>
      <source>When automatically selecting a printing, prefer printings with already downloaded images over other possible printings.</source>
      <translation type="unfinished">When automatically selecting a printing, prefer printings with already downloaded images over other possible printings.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="105"/>
      <source>Prefer printings with already downloaded images</source>
      <translation>Préférer les impressions avec des images déjà téléchargées</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="112"/>
      <source>Always enable automatic deck list translation when importing deck lists.
This avoids adding foreign language cards, if the deck list happens to contain some.</source>
      <translation type="unfinished">Always enable automatic deck list translation when importing deck lists.
This avoids adding foreign language cards, if the deck list happens to contain some.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="116"/>
      <source>Enable translating imported deck lists by default</source>
      <translation>Activer la traduction des listes de cartes importées par défaut</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="123"/>
      <source>Not all deck list formats always contain complete data to identify exact printings.
If enabled, choose an arbitrary printing, instead of failing to identify such cards.
With some deck list formats, this option is always enabled.</source>
      <translation type="unfinished">Not all deck list formats always contain complete data to identify exact printings.
If enabled, choose an arbitrary printing, instead of failing to identify such cards.
With some deck list formats, this option is always enabled.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="128"/>
      <source>Automatically select a printing</source>
      <translation type="unfinished">Automatically select a printing</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="138"/>
      <source>If set, use this as the default location for loading deck lists. Your webbrowser’s download directory is a good choice.</source>
      <translation type="unfinished">If set, use this as the default location for loading deck lists. Your webbrowser’s download directory is a good choice.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="144"/>
      <source>Path to a directory</source>
      <translation>Chemin vers un répertoire</translation>
    </message>
  </context>
  <context>
    <name>DefaultDocumentLayoutSettingsPage</name>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="480"/>
      <source>Default document settings</source>
      <translation>Paramètres du document par défaut</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="480"/>
      <source>Set the default document settings used for new documents,
like page size, margins, spacings, etc.</source>
      <translation type="unfinished">Set the default document settings used for new documents,
like page size, margins, spacings, etc.</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="488"/>
      <source>Default settings for new documents</source>
      <translation>Paramètres par défaut pour les nouveaux documents</translation>
    </message>
  </context>
  <context>
    <name>Document</name>
    <message>
      <location filename="../../model/document.py" line="92"/>
      <source>Card name</source>
      <translation type="unfinished">Card name</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="93"/>
      <source>Set</source>
      <translation type="unfinished">Set</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="94"/>
      <source>Collector #</source>
      <translation type="unfinished">Collector #</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="95"/>
      <source>Language</source>
      <translation type="unfinished">Language</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="96"/>
      <source>Image</source>
      <translation type="unfinished">Image</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="97"/>
      <source>Side</source>
      <translation type="unfinished">Side</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="175"/>
      <source>Double-click on entries to
switch the selected printing.</source>
      <translation type="unfinished">Double-click on entries to
switch the selected printing.</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="288"/>
      <source>Page {current}/{total}</source>
      <translation type="unfinished">Page {current}/{total}</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="319"/>
      <source>Front</source>
      <translation type="unfinished">Front</translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="319"/>
      <source>Back</source>
      <translation type="unfinished">Back</translation>
    </message>
    <message numerus="yes">
      <location filename="../../model/document.py" line="325"/>
      <source>%n× {name}</source>
      <comment>Used to display a card name and amount of copies in the page overview. Only needs translation for RTL language support</comment>
      <translation type="unfinished">
        <numerusform>%n× {name}</numerusform>
        <numerusform>%n× {name}</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../model/document.py" line="382"/>
      <source>Empty Placeholder</source>
      <translation type="unfinished">Empty Placeholder</translation>
    </message>
  </context>
  <context>
    <name>DocumentAction</name>
    <message>
      <location filename="../../document_controller/_interface.py" line="105"/>
      <source>{first}-{last}</source>
      <comment>Inclusive, formatted number range, from first to last</comment>
      <translation type="unfinished">{first}-{last}</translation>
    </message>
  </context>
  <context>
    <name>DocumentSettingsDialog</name>
    <message>
      <location filename="../../ui/dialogs.py" line="379"/>
      <source>These settings only affect the current document</source>
      <translation type="unfinished">These settings only affect the current document</translation>
    </message>
    <message>
      <location filename="../ui/document_settings_dialog.ui" line="6"/>
      <source>Set Document settings</source>
      <translation>Modifier les paramètres du document</translation>
    </message>
  </context>
  <context>
    <name>ExportCardImagesDialog</name>
    <message>
      <location filename="../../ui/dialogs.py" line="455"/>
      <source>Select card image export location</source>
      <translation type="unfinished">Select card image export location</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="17"/>
      <source>Export card images</source>
      <translation type="unfinished">Export card images</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="29"/>
      <source>Browse …</source>
      <translation type="unfinished">Browse …</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="52"/>
      <source>Custom cards</source>
      <translation type="unfinished">Custom cards</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="66"/>
      <source>Output directory:</source>
      <translation type="unfinished">Output directory:</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="73"/>
      <source>Official cards</source>
      <translation type="unfinished">Official cards</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="83"/>
      <source>Which card images should be exported?</source>
      <translation type="unfinished">Which card images should be exported?</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="93"/>
      <source>Path to a directory</source>
      <translation type="unfinished">Path to a directory</translation>
    </message>
    <message>
      <location filename="../../ui/dialogs.py" line="502"/>
      <source>Copy failed for {card_name}! Disk detached/full? Aborting.</source>
      <translation type="unfinished">Copy failed for {card_name}! Disk detached/full? Aborting.</translation>
    </message>
    <message>
      <location filename="../../ui/dialogs.py" line="531"/>
      <source>Write failed for {card_name}! Disk detached/full? Aborting.</source>
      <translation type="unfinished">Write failed for {card_name}! Disk detached/full? Aborting.</translation>
    </message>
  </context>
  <context>
    <name>FileDownloadWorker</name>
    <message>
      <location filename="../../card_info_downloader.py" line="189"/>
      <source>Downloading card data:</source>
      <comment>Progress bar label text</comment>
      <translation type="unfinished">Downloading card data:</translation>
    </message>
  </context>
  <context>
    <name>FilterSetupPage</name>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="14"/>
      <source>Cleanup locally stored card images</source>
      <translation>Nettoyer les images de carte stockées localement</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="17"/>
      <source>This wizard can be used to remove unwanted card images currently stored on your computer. You can enable automatic cleanup conditions below, to preselect images for removal.</source>
      <translation>Cet assistant peut être utilisé pour supprimer des images de carte non désirées stockées sur votre ordinateur. Vous pouvez activer différentes conditions de nettoyage automatique ci-dessous, pour présélectionner des images pour suppression.</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="23"/>
      <source>Delete everything</source>
      <translation>Supprimer tout</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="33"/>
      <source>Select images for removal based on any matching criterion.</source>
      <translation type="unfinished">Select images for removal based on any matching criterion.</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="36"/>
      <source>Select images for deletion, that are …</source>
      <translation>Sélectionner les images à supprimer, qui sont …</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="42"/>
      <source>Used in prints and PDFs less often than:</source>
      <translation>Utilisées dans des impressions et des PDF moins de :</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="49"/>
      <source>Not used in prints for:</source>
      <translation>Non utilisé dans des impressions depuis :</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="59"/>
      <source> days</source>
      <translation> jours</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="75"/>
      <source> times</source>
      <translation> fois</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="88"/>
      <source>Card images may become unknown, if printings are removed by Scryfall.
This filter also applies to cards and printings hidden by a card filter in the settings.
For example, if you downloaded images of silver-bordered cards and then configured the program to hide those,
all these images become hidden and will be removed.</source>
      <translation type="unfinished">Card images may become unknown, if printings are removed by Scryfall.
This filter also applies to cards and printings hidden by a card filter in the settings.
For example, if you downloaded images of silver-bordered cards and then configured the program to hide those,
all these images become hidden and will be removed.</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="94"/>
      <source>Unknown or belong to hidden printings</source>
      <translation>Inconnues ou appartenant à des impressions cachées</translation>
    </message>
  </context>
  <context>
    <name>FormatPrintingFilter</name>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="14"/>
      <source>Hide cards banned in specific Formats</source>
      <translation>Cacher les cartes interdites dans des formats spécifiques</translation>
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
      <translation type="unfinished">View cards hidden by this filter on the Scryfall website.</translation>
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
      <translation>Filtres d'impression généraux</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="327"/>
      <source>View cards hidden by this filter on the Scryfall website.</source>
      <translation type="unfinished">View cards hidden by this filter on the Scryfall website.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="71"/>
      <source>Hide cards without a defined, solid-color border.
Those require higher cutting precision to get right.</source>
      <translation type="unfinished">Hide cards without a defined, solid-color border.
Those require higher cutting precision to get right.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="75"/>
      <source>Hide borderless cards</source>
      <translation>Cacher les cartes sans bordure</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="82"/>
      <source>Hide Token cards</source>
      <translation>Cacher les cartes jeton</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="105"/>
      <source>Some single-sided cards are re-printed as two-sided, reversible cards in some Secret Lair releases.
This filter hides those.</source>
      <translation type="unfinished">Some single-sided cards are re-printed as two-sided, reversible cards in some Secret Lair releases.
This filter hides those.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="109"/>
      <source>Hide reversible cards</source>
      <translation>Cacher les cartes réversibles</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="148"/>
      <source>Hide cards and printings that are only available on digital platforms. This includes all kinds of digital printings.</source>
      <translation type="unfinished">Hide cards and printings that are only available on digital platforms. This includes all kinds of digital printings.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="151"/>
      <source>Hide digital cards</source>
      <translation>Cacher les cartes numériques</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="158"/>
      <source>“Funny” cards, not legal in any constructed format.
This includes full-art Contraptions from Unstable,
cards with acorn-shaped security stamps from Unfinity (and newer Un-Sets),
some black-bordered promotional cards with non-standard back faces,
and all silver-bordered cards.</source>
      <translation type="unfinished">“Funny” cards, not legal in any constructed format.
This includes full-art Contraptions from Unstable,
cards with acorn-shaped security stamps from Unfinity (and newer Un-Sets),
some black-bordered promotional cards with non-standard back faces,
and all silver-bordered cards.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="165"/>
      <source>Hide “funny” cards</source>
      <translation>Cacher les cartes « drôles »</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="172"/>
      <source>These cards are larger than regular Magic cards and can’t be included in decks.
Includes Archenemy schemes, Planechase planes and
oversized commander creature or Planeswalker cards included in some pre-constructed Commander decks.</source>
      <translation type="unfinished">These cards are larger than regular Magic cards and can’t be included in decks.
Includes Archenemy schemes, Planechase planes and
oversized commander creature or Planeswalker cards included in some pre-constructed Commander decks.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="177"/>
      <source>Hide oversized cards</source>
      <translation>Masquer les cartes surdimensionnées</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="184"/>
      <source>Some “collectible” sets, like full reprints of tournament-winning decks were printed with golden borders.
Many also have printed signatures of the involved players in the text box.

These are not tournament legal</source>
      <translation type="unfinished">Some “collectible” sets, like full reprints of tournament-winning decks were printed with golden borders.
Many also have printed signatures of the involved players in the text box.

These are not tournament legal</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="190"/>
      <source>Hide gold-bordered cards</source>
      <translation>Cacher les cartes avec des bordures dorées</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="197"/>
      <source>Hide white-bordered cards</source>
      <translation>Cacher les cartes avec des bordures blanches</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="204"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Hide cards banned for depicting racism.&lt;/p&gt;&lt;p&gt;Background:&lt;/p&gt;&lt;p&gt;Some cards were banned by Wizards of the Coast, because they depict references to controversial real-world events, religion or contain combinations of card effect, name and artwork that, when viewed together, depict racism. These cards are banned in all sanctioned tournament formats and several community formats like Commander, Oathbreaker and others.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation type="unfinished">&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Hide cards banned for depicting racism.&lt;/p&gt;&lt;p&gt;Background:&lt;/p&gt;&lt;p&gt;Some cards were banned by Wizards of the Coast, because they depict references to controversial real-world events, religion or contain combinations of card effect, name and artwork that, when viewed together, depict racism. These cards are banned in all sanctioned tournament formats and several community formats like Commander, Oathbreaker and others.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="207"/>
      <source>Hide cards depicting racism</source>
      <translation>Cacher les cartes dépeignant du racisme</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="230"/>
      <source>Hide non-English cards with low-resolution,
English placeholder images with an overlay text stating
“This card is not available in the selected language.”</source>
      <translation type="unfinished">Hide non-English cards with low-resolution,
English placeholder images with an overlay text stating
“This card is not available in the selected language.”</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="235"/>
      <source>Hide cards with placeholder images</source>
      <translation>Cacher les cartes avec des images temporaires</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="300"/>
      <source>Hide cards with artwork extending to the left and right card border.
Similar to borderless cards, these require higher precision during the cutting process.</source>
      <translation type="unfinished">Hide cards with artwork extending to the left and right card border.
Similar to borderless cards, these require higher precision during the cutting process.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="304"/>
      <source>Hide extended art cards</source>
      <translation>Cacher les cartes avec arts étendus</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="311"/>
      <source>Artwork cards that can be found in Set Boosters or Play Boosters</source>
      <translation type="unfinished">Artwork cards that can be found in Set Boosters or Play Boosters</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="314"/>
      <source>Hide Art Series cards</source>
      <translation>Cacher les cartes Art Series</translation>
    </message>
  </context>
  <context>
    <name>GeneralSettingsPage</name>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="294"/>
      <source>General settings</source>
      <translation>Paramètres généraux</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="301"/>
      <source>Horizontal layout</source>
      <translation type="unfinished">Horizontal layout</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="302"/>
      <source>Columnar layout</source>
      <translation>Disposition des colonnes</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="303"/>
      <source>Tabbed layout</source>
      <translation type="unfinished">Tabbed layout</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="306"/>
      <source>System default</source>
      <translation type="unfinished">System default</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="317"/>
      <source>Select default save location</source>
      <translation type="unfinished">Select default save location</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="45"/>
      <source>Horizontal adds a wide, horizontal search area above the currently edited page, and is best for taller screens, like 4:3 or 3:2.
Columnar organizes the main window content in four columns, and is best for (ultra-)wide screens.
Tabbed uses tabs to only show parts of the main window at a time. Best used with small screens in portrait mode (i.e. 9:16), otherwise not recommended.</source>
      <translation type="unfinished">Horizontal adds a wide, horizontal search area above the currently edited page, and is best for taller screens, like 4:3 or 3:2.
Columnar organizes the main window content in four columns, and is best for (ultra-)wide screens.
Tabbed uses tabs to only show parts of the main window at a time. Best used with small screens in portrait mode (i.e. 9:16), otherwise not recommended.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="22"/>
      <source>Main window layout</source>
      <translation>Disposition de la fenêtre principale</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="15"/>
      <source>Application language</source>
      <translation>Langage de l'application</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="83"/>
      <source>Double-faced cards</source>
      <translation>Cartes à deux côtés</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="89"/>
      <source>When adding double-faced cards, automatically add the same number of copies of the other side.
Uses the appropriate, matching other card side.
Uncheck to disable this automatism.</source>
      <translation type="unfinished">When adding double-faced cards, automatically add the same number of copies of the other side.
Uses the appropriate, matching other card side.
Uncheck to disable this automatism.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="94"/>
      <source>Automatically add the other side of double-faced cards</source>
      <translation>Ajouter automatiquement l'autre côté des cartes à deux côtés</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="107"/>
      <source>Preferred card language:</source>
      <translation>Langage de carte préférée :</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="120"/>
      <source>Automatic update checks</source>
      <translation>Vérifications automatiques des mises à jour</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="126"/>
      <source>Update checks are performed at application start, if enabled.</source>
      <translation>Les vérifications de mise à jour sont effectuées au démarrage de l'application, si activé.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="133"/>
      <source>If enabled, check for application updates, and notify if new updates are available for installation.</source>
      <translation type="unfinished">If enabled, check for application updates, and notify if new updates are available for installation.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="136"/>
      <source>Check for application updates</source>
      <translation>Vérifier les mises à jour de l'application</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="146"/>
      <source>If enabled, query the Scryfall API if new cards are available. If so, offer to update the local card data.</source>
      <translation type="unfinished">If enabled, query the Scryfall API if new cards are available. If so, offer to update the local card data.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="149"/>
      <source>Check for new card data</source>
      <translation>Vérifier les nouvelles données de carte</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="162"/>
      <source>These paths are selected by default when browsing the file system for files</source>
      <translation type="unfinished">These paths are selected by default when browsing the file system for files</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="165"/>
      <source>Default save paths</source>
      <translation>Chemins de sauvegarde par défaut</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="171"/>
      <source>Browse…</source>
      <translation type="unfinished">Browse…</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="184"/>
      <source>Document save path</source>
      <translation>Chemin de sauvegarde du document</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="194"/>
      <source>If set, use this as the default location for saving documents.</source>
      <translation type="unfinished">If set, use this as the default location for saving documents.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="200"/>
      <source>Path to a directory</source>
      <translation>Chemin vers un répertoire</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="73"/>
      <source>Language choices will default to the chosen language here.
Entries use the language codes as listed on Scryfall.

Note: Cards in deck lists use the language as given by the deck list. To overwrite, use the deck list translation option.</source>
      <translation type="unfinished">Language choices will default to the chosen language here.
Entries use the language codes as listed on Scryfall.

Note: Cards in deck lists use the language as given by the deck list. To overwrite, use the deck list translation option.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="104"/>
      <source>Card language selected at application start and default language when enabling deck list translations</source>
      <translation type="unfinished">Card language selected at application start and default language when enabling deck list translations</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="307"/>
      <source>English (US) [{progress}%]</source>
      <translation>Anglais (États-Unis) [{progress}%]</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="308"/>
      <source>German [{progress}%]</source>
      <translation>Allemand [{progress}%]</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="309"/>
      <source>French [{progress}%]</source>
      <translation>Français [{progress}%]</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="32"/>
      <source>Open the main window maximized</source>
      <translation type="unfinished">Open the main window maximized</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="9"/>
      <source>Look &amp;&amp; Feel (Changing most of these require an application restart)</source>
      <translation type="unfinished">Look &amp;&amp; Feel (Changing most of these require an application restart)</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="57"/>
      <source>Open all wizards maximized</source>
      <translation type="unfinished">Open all wizards maximized</translation>
    </message>
  </context>
  <context>
    <name>GroupedCentralWidget</name>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="58"/>
      <source>Remove selected</source>
      <translation type="unfinished">Remove selected</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="103"/>
      <source>All pages:</source>
      <translation>Toutes les pages :</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="110"/>
      <source>Add new cards:</source>
      <translation type="unfinished">Add new cards:</translation>
    </message>
  </context>
  <context>
    <name>HidePrintingsPage</name>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="437"/>
      <source>Hide printings</source>
      <translation>Cacher des impressions</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="437"/>
      <source>Hide unwanted printings</source>
      <translation type="unfinished">Hide unwanted printings</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/hide_printings_page.ui" line="17"/>
      <source>These options allow hiding unwanted cards and printings. Hidden printings are treated as though they don’t exist. They can’t be found in the card search and are automatically replaced in loaded documents or imported deck lists, if possible. If all printings of a card are hidden, it won’t be available at all.</source>
      <translation>Ces options permettent de masquer les cartes et les impressions indésirables. Les impressions cachées sont traitées comme si elles n’existaient pas. Elles ne peuvent pas être trouvés dans la recherche de carte et sont automatiquement remplacés dans des documents chargés ou des listes de cartes importées, si possible. Si toutes les impressions d'une carte sont cachées, elles ne seront pas du tout disponibles.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/hide_printings_page.ui" line="33"/>
      <source>Hide specific sets: Add set codes as listed on Scryfall, for example LEA or 2X2. Separate multiple entries with spaces or line breaks. All words not matching an exact set code are ignored.</source>
      <translation>Cacher des extensions spécifiques : Ajoutez des codes d'extension comme listés sur Scryfall, par exemple LEA ou 2X2. Séparez plusieurs entrées avec des espaces ou des retours à la ligne. Tous les mots ne correspondant pas à un code d'extension exact seront ignorés.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/hide_printings_page.ui" line="43"/>
      <source>Example:

LEA DDU TC13 J21</source>
      <translation type="unfinished">Example:

LEA DDU TC13 J21</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/hide_printings_page.ui" line="51"/>
      <source>No sets currently hidden.</source>
      <translation>Pas d'extensions actuellement cachées.</translation>
    </message>
  </context>
  <context>
    <name>HorizontalAddCardWidget</name>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="35"/>
      <source>Language:</source>
      <translation>Langage :</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="51"/>
      <source>Card Name</source>
      <translation>Nom de la carte</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="57"/>
      <source>Filter the list below. Use  % (Percent signs) as wildcards matching any number of characters.</source>
      <translation type="unfinished">Filter the list below. Use  % (Percent signs) as wildcards matching any number of characters.</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="60"/>
      <source>Filter card names</source>
      <translation>Filtrer le nom des cartes</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="70"/>
      <source>The filtered list of card names in the currently selected language. Click on an entry to select it and choose a printing.</source>
      <translation type="unfinished">The filtered list of card names in the currently selected language. Click on an entry to select it and choose a printing.</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="95"/>
      <source>The sets in which the currently selected card was printed.</source>
      <translation type="unfinished">The sets in which the currently selected card was printed.</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="98"/>
      <source>Set</source>
      <translation>Extension</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="104"/>
      <source>Filter set names</source>
      <translation>Filtrer le nom des extensions</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="136"/>
      <source>Collector Number</source>
      <translation>Numéro de collection</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="164"/>
      <source>Copies:</source>
      <translation>Copies :</translation>
    </message>
  </context>
  <context>
    <name>ImageDownloader</name>
    <message>
      <location filename="../../model/imagedb.py" line="309"/>
      <source>Importing deck list</source>
      <comment>Progress bar label text</comment>
      <translation type="unfinished">Importing deck list</translation>
    </message>
    <message>
      <location filename="../../model/imagedb.py" line="329"/>
      <source>Fetching missing images</source>
      <comment>Progress bar label text</comment>
      <translation type="unfinished">Fetching missing images</translation>
    </message>
    <message>
      <location filename="../../model/imagedb.py" line="424"/>
      <source>Downloading &apos;{card_name}&apos;</source>
      <comment>Progress bar label text</comment>
      <translation type="unfinished">Downloading &apos;{card_name}&apos;</translation>
    </message>
  </context>
  <context>
    <name>KnownCardImageModel</name>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="133"/>
      <source>Name</source>
      <translation type="unfinished">Name</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="134"/>
      <source>Set</source>
      <translation type="unfinished">Set</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="135"/>
      <source>Collector #</source>
      <translation type="unfinished">Collector #</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="136"/>
      <source>Is Hidden</source>
      <translation type="unfinished">Is Hidden</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="137"/>
      <source>Front/Back</source>
      <translation type="unfinished">Front/Back</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="138"/>
      <source>High resolution?</source>
      <translation type="unfinished">High resolution?</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="139"/>
      <source>Size</source>
      <translation type="unfinished">Size</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="140"/>
      <source>Scryfall ID</source>
      <translation type="unfinished">Scryfall ID</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="141"/>
      <source>Path</source>
      <translation type="unfinished">Path</translation>
    </message>
  </context>
  <context>
    <name>KnownCardRow</name>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="112"/>
      <source>Yes</source>
      <translation type="unfinished">Yes</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="112"/>
      <source>No</source>
      <translation type="unfinished">No</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="100"/>
      <source>This printing is hidden by an enabled card filter
and is thus unavailable for printing.</source>
      <comment>Tooltip for cells with hidden cards</comment>
      <translation type="unfinished">This printing is hidden by an enabled card filter
and is thus unavailable for printing.</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="106"/>
      <source>Front</source>
      <comment>Card side</comment>
      <translation type="unfinished">Front</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="106"/>
      <source>Back</source>
      <comment>Card side</comment>
      <translation type="unfinished">Back</translation>
    </message>
  </context>
  <context>
    <name>LoadDocumentDialog</name>
    <message>
      <location filename="../../ui/dialogs.py" line="220"/>
      <source>Load MTGProxyPrinter document</source>
      <translation type="unfinished">Load MTGProxyPrinter document</translation>
    </message>
  </context>
  <context>
    <name>LoadListPage</name>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="116"/>
      <source>Supported websites:
{supported_sites}</source>
      <translation type="unfinished">Supported websites:
{supported_sites}</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="212"/>
      <source>Overwrite existing deck list?</source>
      <translation>Écraser la liste de cartes existante ?</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="166"/>
      <source>Selecting a file will overwrite the existing deck list. Continue?</source>
      <translation>Choisir un fichier écrasera la liste actuelle. Continuer ?</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="174"/>
      <source>Select deck file</source>
      <translation type="unfinished">Select deck file</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="184"/>
      <source>All files (*)</source>
      <translation type="unfinished">All files (*)</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="195"/>
      <source>All Supported </source>
      <translation type="unfinished">All Supported </translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="212"/>
      <source>Downloading a deck list will overwrite the existing deck list. Continue?</source>
      <translation>Télécharger une nouvelle liste de carte écrasera la liste actuelle. Continuer ?</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="225"/>
      <source>Download failed with HTTP error {http_error_code}.

{bad_request_msg}</source>
      <translation type="unfinished">Download failed with HTTP error {http_error_code}.

{bad_request_msg}</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="236"/>
      <source>Deck list download failed</source>
      <translation type="unfinished">Deck list download failed</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="231"/>
      <source>Download failed.

Check your internet connection, verify that the URL is valid, reachable, and that the deck list is set to public. This program cannot download private deck lists. If this persists, please report a bug in the issue tracker on the homepage.</source>
      <translation type="unfinished">Download failed.

Check your internet connection, verify that the URL is valid, reachable, and that the deck list is set to public. This program cannot download private deck lists. If this persists, please report a bug in the issue tracker on the homepage.</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="262"/>
      <source>Unable to read file content</source>
      <translation type="unfinished">Unable to read file content</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="262"/>
      <source>Unable to read the content of file {file_path} as plain text.
Failed to load the content.</source>
      <translation type="unfinished">Unable to read the content of file {file_path} as plain text.
Failed to load the content.</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="274"/>
      <source>Load large file?</source>
      <translation type="unfinished">Load large file?</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="274"/>
      <source>The selected file {file_path} is unexpectedly large ({formatted_size}). Load anyway?</source>
      <translation type="unfinished">The selected file {file_path} is unexpectedly large ({formatted_size}). Load anyway?</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="17"/>
      <source>Import a deck list for printing</source>
      <translation type="unfinished">Import a deck list for printing</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="20"/>
      <source>Load a deck file from disk or paste deck list in the text field below</source>
      <translation>Charger un fichier de liste de carte depuis le disque ou coller une liste dans le champ de texte ci-dessous</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="42"/>
      <source>Paste a link to a public deck list here. Hover to see supported sites.</source>
      <translation type="unfinished">Paste a link to a public deck list here. Hover to see supported sites.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="52"/>
      <source>Scryfall search query</source>
      <translation type="unfinished">Scryfall search query</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="59"/>
      <source>If checked, choose an arbitrary printing, if a unique printing is not identified.
If unchecked, each ambiguous card is ignored and reported as unrecognized.</source>
      <translation type="unfinished">If checked, choose an arbitrary printing, if a unique printing is not identified.
If unchecked, each ambiguous card is ignored and reported as unrecognized.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="63"/>
      <source>Guess printings for ambiguous entries in the deck list</source>
      <translation type="unfinished">Guess printings for ambiguous entries in the deck list</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="79"/>
      <source>Download result</source>
      <translation type="unfinished">Download result</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="89"/>
      <source>Paste your deck list here or use one of the actions above</source>
      <translation type="unfinished">Paste your deck list here or use one of the actions above</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="99"/>
      <source>When an exact printing is not determined or card translation is requested, choose a printing that is already downloaded, if possible.
Enabling this can potentially save disk space and download volume, based on the images already downloaded.</source>
      <translation type="unfinished">When an exact printing is not determined or card translation is requested, choose a printing that is already downloaded, if possible.
Enabling this can potentially save disk space and download volume, based on the images already downloaded.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="103"/>
      <source>When choosing a printing, prefer ones with already downloaded images</source>
      <translation type="unfinished">When choosing a printing, prefer ones with already downloaded images</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="116"/>
      <source>Translate deck list to:</source>
      <translation type="unfinished">Translate deck list to:</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="130"/>
      <source>Opens a file picker and lets you load a deck file from disk.</source>
      <translation type="unfinished">Opens a file picker and lets you load a deck file from disk.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="133"/>
      <source>Select deck list file</source>
      <translation>Sélectionner un fichier de liste de cartes</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="152"/>
      <source>View result</source>
      <translation type="unfinished">View result</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="171"/>
      <source>Download deck list</source>
      <translation type="unfinished">Download deck list</translation>
    </message>
  </context>
  <context>
    <name>LoadSaveDialog</name>
    <message>
      <location filename="../../ui/dialogs.py" line="177"/>
      <source>MTGProxyPrinter document (*.{default_save_suffix})</source>
      <comment>Human-readable file type name</comment>
      <translation type="unfinished">MTGProxyPrinter document (*.{default_save_suffix})</translation>
    </message>
  </context>
  <context>
    <name>MTGArenaParser</name>
    <message>
      <location filename="../../decklist_parser/re_parsers.py" line="201"/>
      <source>Magic Arena deck file</source>
      <translation type="unfinished">Magic Arena deck file</translation>
    </message>
  </context>
  <context>
    <name>MTGOnlineParser</name>
    <message>
      <location filename="../../decklist_parser/re_parsers.py" line="235"/>
      <source>Magic Online (MTGO) deck file</source>
      <translation type="unfinished">Magic Online (MTGO) deck file</translation>
    </message>
  </context>
  <context>
    <name>MagicWorkstationDeckDataFormatParser</name>
    <message>
      <location filename="../../decklist_parser/re_parsers.py" line="179"/>
      <source>Magic Workstation Deck Data Format</source>
      <translation type="unfinished">Magic Workstation Deck Data Format</translation>
    </message>
  </context>
  <context>
    <name>MainWindow</name>
    <message>
      <location filename="../../ui/main_window.py" line="224"/>
      <source>Undo:
{top_entry}</source>
      <translation type="unfinished">Undo:
{top_entry}</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="226"/>
      <source>Redo:
{top_entry}</source>
      <translation type="unfinished">Redo:
{top_entry}</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="290"/>
      <source>printing</source>
      <comment>This is passed as the {action} when asking the user about compacting the document if that can save pages</comment>
      <translation type="unfinished">printing</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="302"/>
      <source>exporting as a PDF</source>
      <comment>This is passed as the {action} when asking the user about compacting the document if that can save pages</comment>
      <translation type="unfinished">exporting as a PDF</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="337"/>
      <source>Network error</source>
      <translation>Erreur réseau</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="337"/>
      <source>Operation failed, because a network error occurred.
Check your internet connection. Reported error message:

{message}</source>
      <translation type="unfinished">Operation failed, because a network error occurred.
Check your internet connection. Reported error message:

{message}</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="345"/>
      <source>Error</source>
      <translation type="unfinished">Error</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="345"/>
      <source>Operation failed, because an internal error occurred.
Reported error message:

{message}</source>
      <translation type="unfinished">Operation failed, because an internal error occurred.
Reported error message:

{message}</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="354"/>
      <source>Saving pages possible</source>
      <translation>Sauvegarde possible des pages</translation>
    </message>
    <message numerus="yes">
      <location filename="../../ui/main_window.py" line="354"/>
      <source>It is possible to save %n pages when printing this document.
Do you want to compact the document now to minimize the page count prior to {action}?</source>
      <translation type="unfinished">
        <numerusform>It is possible to save %n pages when printing this document.
Do you want to compact the document now to minimize the page count prior to {action}?</numerusform>
        <numerusform>It is possible to save %n pages when printing this document.
Do you want to compact the document now to minimize the page count prior to {action}?</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="370"/>
      <source>Download required Card data from Scryfall?</source>
      <translation type="unfinished">Download required Card data from Scryfall?</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="370"/>
      <source>This program requires downloading additional card data from Scryfall to operate the card search.
Download the required data from Scryfall now?
Without the data, you can only print custom cards by drag&amp;dropping the image files onto the main window.</source>
      <translation type="unfinished">This program requires downloading additional card data from Scryfall to operate the card search.
Download the required data from Scryfall now?
Without the data, you can only print custom cards by drag&amp;dropping the image files onto the main window.</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="418"/>
      <source>Document loading failed</source>
      <translation type="unfinished">Document loading failed</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="418"/>
      <source>Loading file &quot;{failed_path}&quot; failed. The file was not recognized as a {program_name} document. If you want to load a deck list, use the &quot;{function_text}&quot; function instead.
Reported failure reason: {reason}</source>
      <translation type="unfinished">Loading file &quot;{failed_path}&quot; failed. The file was not recognized as a {program_name} document. If you want to load a deck list, use the &quot;{function_text}&quot; function instead.
Reported failure reason: {reason}</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="431"/>
      <source>Unavailable printings replaced</source>
      <translation type="unfinished">Unavailable printings replaced</translation>
    </message>
    <message numerus="yes">
      <location filename="../../ui/main_window.py" line="431"/>
      <source>The document contained %n unavailable printings of cards that were automatically replaced with other printings. The replaced printings are unavailable, because they match a configured card filter.</source>
      <translation type="unfinished">
        <numerusform>The document contained %n unavailable printings of cards that were automatically replaced with other printings. The replaced printings are unavailable, because they match a configured card filter.</numerusform>
        <numerusform>The document contained %n unavailable printings of cards that were automatically replaced with other printings. The replaced printings are unavailable, because they match a configured card filter.</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="440"/>
      <source>Unrecognized cards in loaded document found</source>
      <translation type="unfinished">Unrecognized cards in loaded document found</translation>
    </message>
    <message numerus="yes">
      <location filename="../../ui/main_window.py" line="440"/>
      <source>Skipped %n unrecognized cards in the loaded document. Saving the document will remove these entries permanently.

The locally stored card data may be outdated or the document was tampered with.</source>
      <translation type="unfinished">
        <numerusform>Skipped %n unrecognized cards in the loaded document. Saving the document will remove these entries permanently.

The locally stored card data may be outdated or the document was tampered with.</numerusform>
        <numerusform>Skipped %n unrecognized cards in the loaded document. Saving the document will remove these entries permanently.

The locally stored card data may be outdated or the document was tampered with.</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="450"/>
      <source>Application update available. Visit website?</source>
      <translation type="unfinished">Application update available. Visit website?</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="450"/>
      <source>An application update is available: Version {newer_version}
You are currently using version {current_version}.

Open the {program_name} website in your web browser to download the new version?</source>
      <translation type="unfinished">An application update is available: Version {newer_version}
You are currently using version {current_version}.

Open the {program_name} website in your web browser to download the new version?</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="465"/>
      <source>New card data available</source>
      <translation>Nouvelles données de cartes disponibles</translation>
    </message>
    <message numerus="yes">
      <location filename="../../ui/main_window.py" line="465"/>
      <source>There are %n new printings available on Scryfall. Update the local data now?</source>
      <translation type="unfinished">
        <numerusform>There are %n new printings available on Scryfall. Update the local data now?</numerusform>
        <numerusform>There are %n new printings available on Scryfall. Update the local data now?</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="481"/>
      <source>Check for application updates?</source>
      <translation type="unfinished">Check for application updates?</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="481"/>
      <source>Automatically check for application updates whenever you start {program_name}?</source>
      <translation type="unfinished">Automatically check for application updates whenever you start {program_name}?</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="493"/>
      <source>Check for card data updates?</source>
      <translation type="unfinished">Check for card data updates?</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="493"/>
      <source>Automatically check for card data updates on Scryfall whenever you start {program_name}?</source>
      <translation type="unfinished">Automatically check for card data updates on Scryfall whenever you start {program_name}?</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="503"/>
      <source>{question}
You can change this later in the settings.</source>
      <translation type="unfinished">{question}
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
      <translation type="unfinished">Fi&amp;le</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="174"/>
      <source>Settings</source>
      <translation>Options</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="63"/>
      <source>Edit</source>
      <translation type="unfinished">Edit</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="305"/>
      <source>Show toolbar</source>
      <translation>Afficher la barre d'outils</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="113"/>
      <source>&amp;Quit</source>
      <translation>Quitter</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="116"/>
      <source>Ctrl+Q</source>
      <translation type="unfinished">Ctrl+Q</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="127"/>
      <source>&amp;Print</source>
      <translation>Imprimer</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="130"/>
      <source>Print the current document</source>
      <translation type="unfinished">Print the current document</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="133"/>
      <source>Ctrl+P</source>
      <translation type="unfinished">Ctrl+P</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="141"/>
      <source>&amp;Show print preview</source>
      <translation>Afficher l'aperçu avant impression</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="144"/>
      <source>Show print preview window</source>
      <translation type="unfinished">Show print preview window</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="152"/>
      <source>&amp;Create PDF</source>
      <translation>Générer PDF</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="155"/>
      <source>Create a PDF document</source>
      <translation type="unfinished">Create a PDF document</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="163"/>
      <source>Discard page</source>
      <translation>Supprimer la page</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="166"/>
      <source>Discard this page.</source>
      <translation type="unfinished">Discard this page.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="185"/>
      <source>Update card data</source>
      <translation type="unfinished">Update card data</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="193"/>
      <source>New Page</source>
      <translation>Nouvelle page</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="196"/>
      <source>Add a new, empty page.</source>
      <translation type="unfinished">Add a new, empty page.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="204"/>
      <source>Save</source>
      <translation>Enregistrer</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="207"/>
      <source>Ctrl+S</source>
      <translation type="unfinished">Ctrl+S</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="215"/>
      <source>New</source>
      <translation>Nouveau</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="218"/>
      <source>Ctrl+N</source>
      <translation type="unfinished">Ctrl+N</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="226"/>
      <source>Load</source>
      <translation>Charger</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="229"/>
      <source>Ctrl+L</source>
      <translation type="unfinished">Ctrl+L</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="237"/>
      <source>Save as …</source>
      <translation>Enregistrer sous…</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="242"/>
      <source>About …</source>
      <translation type="unfinished">About …</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="250"/>
      <source>Show Changelog</source>
      <translation>Afficher le journal des modifications</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="258"/>
      <source>Compact document</source>
      <translation>Compresser le document</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="261"/>
      <source>Minimize page count: Fill empty slots on pages by moving cards from the end of the document</source>
      <translation type="unfinished">Minimize page count: Fill empty slots on pages by moving cards from the end of the document</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="269"/>
      <source>Edit document settings</source>
      <translation>Modifier les paramètres du document</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="272"/>
      <source>Configure page size, margins, image spacings for the currently edited document.</source>
      <translation type="unfinished">Configure page size, margins, image spacings for the currently edited document.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="283"/>
      <source>Import a deck list from online sources</source>
      <translation type="unfinished">Import a deck list from online sources</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="291"/>
      <source>Cleanup card images</source>
      <translation>Nettoyer les images de cartes</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="294"/>
      <source>Delete locally stored card images you no longer need.</source>
      <translation type="unfinished">Delete locally stored card images you no longer need.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="308"/>
      <source>Ctrl+M</source>
      <translation>Ctrl+M</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="316"/>
      <source>Download missing card images</source>
      <translation>Télécharger les images de carte manquantes</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="324"/>
      <source>Shuffle document</source>
      <translation>Mélanger le document</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="327"/>
      <source>Randomly rearrange all card image.
If you want to quickly print a full deck for playing,
use this to reduce the initial deck shuffling required</source>
      <translation type="unfinished">Randomly rearrange all card image.
If you want to quickly print a full deck for playing,
use this to reduce the initial deck shuffling required</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="340"/>
      <source>Undo</source>
      <translation>Annuler</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="351"/>
      <source>Redo</source>
      <translation>Rétablir</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="280"/>
      <source>Import deck list</source>
      <translation type="unfinished">Import deck list</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="359"/>
      <source>Add empty card to page</source>
      <translation type="unfinished">Add empty card to page</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="362"/>
      <source>Add an empty spacer filling a card slot</source>
      <translation type="unfinished">Add an empty spacer filling a card slot</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="370"/>
      <source>Add custom cards</source>
      <translation type="unfinished">Add custom cards</translation>
    </message>
    <message>
      <location filename="../../ui/main_window.py" line="314"/>
      <source>exporting as a PNG image sequence</source>
      <comment>This is passed as the {action} when asking the user about compacting the document if that can save pages</comment>
      <translation type="unfinished">exporting as a PNG image sequence</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="378"/>
      <source>Create image sequence</source>
      <translation type="unfinished">Create image sequence</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="381"/>
      <source>Export document as an image sequence</source>
      <translation type="unfinished">Export document as an image sequence</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="389"/>
      <source>Export card images</source>
      <translation type="unfinished">Export card images</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="392"/>
      <source>Export all card images to a directory</source>
      <translation type="unfinished">Export all card images to a directory</translation>
    </message>
  </context>
  <context>
    <name>PDFSettingsPage</name>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="557"/>
      <source>PDF export settings</source>
      <translation>Paramètres d'export PDF</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="557"/>
      <source>Configure the PDF export</source>
      <translation type="unfinished">Configure the PDF export</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="591"/>
      <source>Select default PDF export location</source>
      <translation type="unfinished">Select default PDF export location</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/pdf_settings_page.ui" line="17"/>
      <source>If set, use this as the default location for saving exported PDF documents.</source>
      <translation type="unfinished">If set, use this as the default location for saving exported PDF documents.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/pdf_settings_page.ui" line="23"/>
      <source>Path to a directory</source>
      <translation type="unfinished">Path to a directory</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/pdf_settings_page.ui" line="46"/>
      <source>PDF export path</source>
      <translation>Chemin d'export des PDF</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/pdf_settings_page.ui" line="56"/>
      <source>Browse…</source>
      <translation type="unfinished">Browse…</translation>
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
      <translation type="unfinished">Automatically split PDF documents, if they get longer than this many pages.
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
      <translation>Fractionner les documents PDF de plus de</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/pdf_settings_page.ui" line="107"/>
      <source> pages</source>
      <translation type="unfinished"> pages</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/pdf_settings_page.ui" line="117"/>
      <source>If enabled, landscape documents are rotated by 90° to portrait mode during export.
Enable this, if printing from PDFs in landscape format results in portrait printouts with cropped-off sides.

Enabling this may cause the cut helper lines to flicker or not show in some PDF viewers.
So only enable this, if actually required.</source>
      <translation type="unfinished">If enabled, landscape documents are rotated by 90° to portrait mode during export.
Enable this, if printing from PDFs in landscape format results in portrait printouts with cropped-off sides.

Enabling this may cause the cut helper lines to flicker or not show in some PDF viewers.
So only enable this, if actually required.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/pdf_settings_page.ui" line="124"/>
      <source>Enable landscape workaround: Rotate landscape PDFs by 90°</source>
      <translation>Activer le mode paysage contourné : Faire pivoter les PDF en paysage de 90°</translation>
    </message>
  </context>
  <context>
    <name>PNGRenderer</name>
    <message>
      <location filename="../../print.py" line="83"/>
      <source>Export as PNGs</source>
      <translation type="unfinished">Export as PNGs</translation>
    </message>
  </context>
  <context>
    <name>PageCardTableView</name>
    <message numerus="yes">
      <location filename="../../ui/page_card_table_view.py" line="128"/>
      <source>Add %n copies</source>
      <comment>Context menu action: Add additional card copies to the document</comment>
      <translation type="unfinished">
        <numerusform>Add %n copies</numerusform>
        <numerusform>Add %n copies</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../ui/page_card_table_view.py" line="134"/>
      <source>Add copies …</source>
      <comment>Context menu action: Add additional card copies to the document. User will be asked for a number</comment>
      <translation type="unfinished">Add copies …</translation>
    </message>
    <message>
      <location filename="../../ui/page_card_table_view.py" line="121"/>
      <source>Generate DFC check card</source>
      <translation type="unfinished">Generate DFC check card</translation>
    </message>
    <message>
      <location filename="../../ui/page_card_table_view.py" line="148"/>
      <source>All related cards</source>
      <translation type="unfinished">All related cards</translation>
    </message>
    <message>
      <location filename="../../ui/page_card_table_view.py" line="156"/>
      <source>Add copies</source>
      <translation type="unfinished">Add copies</translation>
    </message>
    <message>
      <location filename="../../ui/page_card_table_view.py" line="156"/>
      <source>Add copies of {card_name}</source>
      <comment>Asks the user for a number. Does not need plural forms</comment>
      <translation type="unfinished">Add copies of {card_name}</translation>
    </message>
    <message>
      <location filename="../../ui/page_card_table_view.py" line="182"/>
      <source>Export image</source>
      <translation type="unfinished">Export image</translation>
    </message>
    <message>
      <location filename="../../ui/page_card_table_view.py" line="197"/>
      <source>Save card image</source>
      <translation type="unfinished">Save card image</translation>
    </message>
    <message>
      <location filename="../../ui/page_card_table_view.py" line="197"/>
      <source>Images (*.png *.bmp *.jpg)</source>
      <translation type="unfinished">Images (*.png *.bmp *.jpg)</translation>
    </message>
  </context>
  <context>
    <name>PageConfigPreviewArea</name>
    <message>
      <location filename="../ui/page_config_preview_area.ui" line="36"/>
      <source> cards</source>
      <translation type="unfinished"> cards</translation>
    </message>
    <message>
      <location filename="../ui/page_config_preview_area.ui" line="43"/>
      <source>Regular</source>
      <translation type="unfinished">Regular</translation>
    </message>
    <message>
      <location filename="../ui/page_config_preview_area.ui" line="53"/>
      <source>Oversized</source>
      <translation type="unfinished">Oversized</translation>
    </message>
  </context>
  <context>
    <name>PageConfigWidget</name>
    <message numerus="yes">
      <location filename="../../ui/page_config_widget.py" line="137"/>
      <source>%n regular card(s)</source>
      <comment>Display of the resulting page capacity for regular-sized cards</comment>
      <translation type="unfinished">
        <numerusform>%n regular card(s)</numerusform>
        <numerusform>%n regular card(s)</numerusform>
      </translation>
    </message>
    <message numerus="yes">
      <location filename="../../ui/page_config_widget.py" line="141"/>
      <source>%n oversized card(s)</source>
      <comment>Display of the resulting page capacity for oversized cards</comment>
      <translation type="unfinished">
        <numerusform>%n oversized card(s)</numerusform>
        <numerusform>%n oversized card(s)</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../ui/page_config_widget.py" line="146"/>
      <source>{regular_text}, {oversized_text}</source>
      <comment>Combination of the page capacities for regular, and oversized cards</comment>
      <translation type="unfinished">{regular_text}, {oversized_text}</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="14"/>
      <source>Default settings for new documents</source>
      <translation type="unfinished">Default settings for new documents</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="20"/>
      <source>Number of cards fitting on each page,
based on the page size and spacings configured</source>
      <translation type="unfinished">Number of cards fitting on each page,
based on the page size and spacings configured</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="179"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the left paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation type="unfinished">&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the left paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="453"/>
      <source> mm</source>
      <translation type="unfinished"> mm</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="330"/>
      <source>Paper height in millimeters.
Must match the size of the sheets in the printer.
Otherwise, scaling may be applied by the printer driver.</source>
      <translation type="unfinished">Paper height in millimeters.
Must match the size of the sheets in the printer.
Otherwise, scaling may be applied by the printer driver.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="311"/>
      <source>Top margin</source>
      <translation>Marge supérieure</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="50"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the right paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation type="unfinished">&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the right paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="150"/>
      <source>If enabled, the page number is printed on each page. Makes it easier to notice missing pages in a stack.</source>
      <translation type="unfinished">If enabled, the page number is printed on each page. Makes it easier to notice missing pages in a stack.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="153"/>
      <source>Print page numbers</source>
      <translation>Imprimer les numéros de pages</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="278"/>
      <source>Resulting page capacity:</source>
      <translation>Capacité de page résultante :</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="396"/>
      <source>Card bleed</source>
      <translation>Marge supplémentaire</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="448"/>
      <source>Paper width in millimeters.
Must match the size of the sheets in the printer.
Otherwise, scaling may be applied by the printer driver.</source>
      <translation type="unfinished">Paper width in millimeters.
Must match the size of the sheets in the printer.
Otherwise, scaling may be applied by the printer driver.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="301"/>
      <source>Enable printing additional lines to aid cutting the printed sheets.</source>
      <translation type="unfinished">Enable printing additional lines to aid cutting the printed sheets.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="304"/>
      <source>Print cut markers</source>
      <translation>Imprimer les marqueurs de coupe</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="250"/>
      <source>Space between image rows in mm.
If set to zero, you only need one cut to separate two images,
otherwise you need two cuts but require less precision hitting the exact middle.</source>
      <translation type="unfinished">Space between image rows in mm.
If set to zero, you only need one cut to separate two images,
otherwise you need two cuts but require less precision hitting the exact middle.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="409"/>
      <source>Draw 90° card corners, instead of round ones</source>
      <translation>Dessiner les coins des cartes à 90°, au lieu de coins arrondis</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="354"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the top paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation type="unfinished">&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the top paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="386"/>
      <source>Document name</source>
      <translation>Nom du document</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="224"/>
      <source>Row spacing</source>
      <translation>Espacement des lignes</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="367"/>
      <source>The document name is printed on each page and can help you keep track
of different printed sheets and to which deck they belong.

Leave empty to disable.</source>
      <translation type="unfinished">The document name is printed on each page and can help you keep track
of different printed sheets and to which deck they belong.

Leave empty to disable.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="376"/>
      <source>Document/deck name</source>
      <translation>Document/Nom de la liste de carte</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="416"/>
      <source>Draw an additional border around cards to ease cutting.</source>
      <translation type="unfinished">Draw an additional border around cards to ease cutting.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="265"/>
      <source>Bottom Margin</source>
      <translation>Marge inférieure</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="160"/>
      <source>Left margin</source>
      <translation>Marge de gauche</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="96"/>
      <source>Space between image columns in mm.
If set to zero, you only need one cut to separate two images,
otherwise you need two cuts but require less precision hitting the exact middle.</source>
      <translation type="unfinished">Space between image columns in mm.
If set to zero, you only need one cut to separate two images,
otherwise you need two cuts but require less precision hitting the exact middle.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="117"/>
      <source>Switch between portrait and landscape mode</source>
      <translation type="unfinished">Switch between portrait and landscape mode</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="120"/>
      <source>Flip</source>
      <translation>Inverser</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="130"/>
      <source>Column spacing</source>
      <translation>Espacement des colonnes</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="288"/>
      <source>Right margin</source>
      <translation>Marge de droite</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="211"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the bottom paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation type="unfinished">&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the bottom paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="78"/>
      <source>Show Preview</source>
      <translation type="unfinished">Show Preview</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="143"/>
      <source>Paper size</source>
      <translation type="unfinished">Paper size</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="192"/>
      <source>Paper height</source>
      <translation type="unfinished">Paper height</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="429"/>
      <source>Paper width</source>
      <translation type="unfinished">Paper width</translation>
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
      <translation type="unfinished">Use Ctrl+Mouse wheel to zoom.
Usable keyboard shortcuts are:
Zoom in: {zoom_in_shortcuts}
Zoom out: {zoom_out_shortcuts}</translation>
    </message>
  </context>
  <context>
    <name>ParserBase</name>
    <message>
      <location filename="../../decklist_parser/common.py" line="71"/>
      <source>All files (*)</source>
      <translation type="unfinished">All files (*)</translation>
    </message>
  </context>
  <context>
    <name>PrettySetListModel</name>
    <message>
      <location filename="../../model/string_list.py" line="36"/>
      <source>Set</source>
      <comment>MTG set name</comment>
      <translation type="unfinished">Set</translation>
    </message>
  </context>
  <context>
    <name>PrinterSettingsPage</name>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="506"/>
      <source>Printer settings</source>
      <translation>Paramètres d'impression</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window_pages.py" line="506"/>
      <source>Configure the printer</source>
      <translation type="unfinished">Configure the printer</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/printer_settings_page.ui" line="62"/>
      <source>When enabled, instruct the printer to use borderless mode and let MTGProxyPrinter manage the printing margins.
Disable this, if your printer keeps scaling print-outs up or down.

When disabled, managing the page margins is delegated to the printer driver,
which should increase compatibility, at the expense of drawing shorter cut helper lines.</source>
      <translation type="unfinished">When enabled, instruct the printer to use borderless mode and let MTGProxyPrinter manage the printing margins.
Disable this, if your printer keeps scaling print-outs up or down.

When disabled, managing the page margins is delegated to the printer driver,
which should increase compatibility, at the expense of drawing shorter cut helper lines.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/printer_settings_page.ui" line="69"/>
      <source>Configure printer for borderless printing</source>
      <translation>Configurer l'imprimante pour une impression sans bordure</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/printer_settings_page.ui" line="48"/>
      <source>If enabled, print landscape documents in portrait mode with all content rotated by 90°.
Enable this, if printing landscape documents results in portrait printouts with cropped-off sides.</source>
      <translation type="unfinished">If enabled, print landscape documents in portrait mode with all content rotated by 90°.
Enable this, if printing landscape documents results in portrait printouts with cropped-off sides.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/printer_settings_page.ui" line="52"/>
      <source>Enable landscape workaround: Rotate prints by 90°</source>
      <translation>Activer le mode paysage contourné : Faire pivoter l'impression de 90°</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/printer_settings_page.ui" line="17"/>
      <source>Horizontal printing offset</source>
      <translation type="unfinished">Horizontal printing offset</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/printer_settings_page.ui" line="24"/>
      <source>Globally shifts the printing area to correct physical offsets in the printer.
Positive values shift to the right.
Negative offsets shift to the left.</source>
      <translation type="unfinished">Globally shifts the printing area to correct physical offsets in the printer.
Positive values shift to the right.
Negative offsets shift to the left.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/printer_settings_page.ui" line="32"/>
      <source> mm</source>
      <translation type="unfinished"> mm</translation>
    </message>
  </context>
  <context>
    <name>PrintingFilterUpdater.store_current_printing_filters()</name>
    <message>
      <location filename="../../printing_filter_updater.py" line="118"/>
      <source>Processing updated card filters:</source>
      <translation type="unfinished">Processing updated card filters:</translation>
    </message>
  </context>
  <context>
    <name>SaveDocumentAsDialog</name>
    <message>
      <location filename="../../ui/dialogs.py" line="190"/>
      <source>Save document as …</source>
      <translation type="unfinished">Save document as …</translation>
    </message>
  </context>
  <context>
    <name>SavePDFDialog</name>
    <message>
      <location filename="../../ui/dialogs.py" line="91"/>
      <source>Export as PDF</source>
      <translation type="unfinished">Export as PDF</translation>
    </message>
    <message>
      <location filename="../../ui/dialogs.py" line="92"/>
      <source>PDF documents (*.pdf)</source>
      <translation type="unfinished">PDF documents (*.pdf)</translation>
    </message>
  </context>
  <context>
    <name>SavePNGDialog</name>
    <message>
      <location filename="../../ui/dialogs.py" line="133"/>
      <source>Export as PNG</source>
      <translation type="unfinished">Export as PNG</translation>
    </message>
    <message>
      <location filename="../../ui/dialogs.py" line="134"/>
      <source>PNG images (*.png)</source>
      <translation type="unfinished">PNG images (*.png)</translation>
    </message>
  </context>
  <context>
    <name>ScryfallCSVParser</name>
    <message>
      <location filename="../../decklist_parser/csv_parsers.py" line="118"/>
      <source>Scryfall CSV export</source>
      <translation type="unfinished">Scryfall CSV export</translation>
    </message>
  </context>
  <context>
    <name>SelectDeckParserPage</name>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="14"/>
      <source>Import a deck list for printing</source>
      <translation type="unfinished">Import a deck list for printing</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="17"/>
      <source>Select which kind of deck list you want to import.</source>
      <translation>Sélectionner quel type de liste de cartes vous souhaitez importer.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="228"/>
      <source>Deck list files, stored in XMage’s native format.
Because XMage closely follows Scryfall regarding Magic sets,
this should give very accurate results.</source>
      <translation type="unfinished">Deck list files, stored in XMage’s native format.
Because XMage closely follows Scryfall regarding Magic sets,
this should give very accurate results.</translation>
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
      <translation type="unfinished">This is a Tappedout-specific section of the deck.
It may contain the deck list author’s buy-list or anything else.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="73"/>
      <source>Include “Acquire-Board”</source>
      <translation type="unfinished">Include “Acquire-Board”</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="240"/>
      <source>The simplistic format used by Magic Online. It does not specify exact printings, so may not give the best results.</source>
      <translation type="unfinished">The simplistic format used by Magic Online. It does not specify exact printings, so may not give the best results.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="243"/>
      <source>Magic Online</source>
      <translation>Magic Online</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="26"/>
      <source>This is a Tappedout-specific section of the deck.
It may contain cards that the deck list creator considers for inclusion, based on the meta
or any other preference, like card price.</source>
      <translation type="unfinished">This is a Tappedout-specific section of the deck.
It may contain cards that the deck list creator considers for inclusion, based on the meta
or any other preference, like card price.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="31"/>
      <source>Include “Maybe-Board”</source>
      <translation type="unfinished">Include “Maybe-Board”</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="54"/>
      <source>CSV exports from Scryfall’s own deck builder.
Gives very accurate results, unless the imported deck list contains ignored items
matching an enabled card filter.</source>
      <translation type="unfinished">CSV exports from Scryfall’s own deck builder.
Gives very accurate results, unless the imported deck list contains ignored items
matching an enabled card filter.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="59"/>
      <source>Scryfall.com deck lists (CSV export)</source>
      <translation>Liste de cartes provenant de Scryfall.com (export CSV)</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="257"/>
      <source>CSV exports can be downloaded from Tappedout by choosing the appropriate deck export option.</source>
      <translation type="unfinished">CSV exports can be downloaded from Tappedout by choosing the appropriate deck export option.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="260"/>
      <source>tappedout.net deck list (CSV export)</source>
      <translation>Liste de cartes provenant de tappedout.net (export CSV)</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="154"/>
      <source>Appends a sample matcher for a set code to the input field above.</source>
      <translation type="unfinished">Appends a sample matcher for a set code to the input field above.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="157"/>
      <source>Set code matcher</source>
      <translation>Code d'extension</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="99"/>
      <source>Appends a sample matcher for a collector number to the input field above</source>
      <translation type="unfinished">Appends a sample matcher for a collector number to the input field above</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="102"/>
      <source>Collector number matcher</source>
      <translation>Numéro de collection</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="140"/>
      <source>Appends a matcher for the number of card copies to the input field above.
If a card count field is not present in the deck list, 1 card copy per line is assumed</source>
      <translation type="unfinished">Appends a matcher for the number of card copies to the input field above.
If a card count field is not present in the deck list, 1 card copy per line is assumed</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="144"/>
      <source>Copies matcher</source>
      <translation>Copies</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="112"/>
      <source>Appends a matcher for a card name to the input field above.</source>
      <translation type="unfinished">Appends a matcher for a card name to the input field above.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="115"/>
      <source>Card name matcher</source>
      <translation>Nom de la carte</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="125"/>
      <source>Appends a matcher for the Scryfall ID to the input field above.
This may be used by deck lists that closely integrate with the Scryfall website.
Most deck lists won’t use this.</source>
      <translation type="unfinished">Appends a matcher for the Scryfall ID to the input field above.
This may be used by deck lists that closely integrate with the Scryfall website.
Most deck lists won’t use this.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="130"/>
      <source>Scryfall ID matcher</source>
      <translation>Scryfall ID</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="85"/>
      <source>Appends a matcher for the  card language to the input field above.
If a language field is not present in the deck list, the card language is guessed.</source>
      <translation type="unfinished">Appends a matcher for the  card language to the input field above.
If a language field is not present in the deck list, the card language is guessed.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="89"/>
      <source>Language matcher</source>
      <translation>Langage</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="267"/>
      <source>Specify a custom regular expression in the input field below. It will be used to parse each deck list line.
You can use the buttons below to insert basic building blocks.
You have to separate them with the “control structures”, like spaces, as used in your deck list.</source>
      <translation type="unfinished">Specify a custom regular expression in the input field below. It will be used to parse each deck list line.
You can use the buttons below to insert basic building blocks.
You have to separate them with the “control structures”, like spaces, as used in your deck list.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="272"/>
      <source>Custom regular expression based parser:</source>
      <translation>Analyseur basé sur une expression régulière personnalisée :</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="216"/>
      <source>Magic Arena and exports from compatible websites, like moxfield.com
Note that this option is not limited to cards in Standard/Historic,
as the format works for any card.</source>
      <translation type="unfinished">Magic Arena and exports from compatible websites, like moxfield.com
Note that this option is not limited to cards in Standard/Historic,
as the format works for any card.</translation>
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
      <translation type="unfinished">Enter a Regular Expression containing at least one supported, named group.

Supported named groups are: {group_names}

See the 'What’s this?' (?-Button) help for details.</translation>
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
      <translation type="unfinished">You can enter a custom Regular Expression (in Python syntax) to parse the lines of your deck list. Use *named groups* to extract the individual card properties from the individual lines of the deck list.
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
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="250"/>
      <source>Magic Workstation Deck Data (mwDeck)</source>
      <translation>Magic Workstation Deck Data (mwDeck)</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="308"/>
      <source>A simple list, containing one card name per line</source>
      <translation type="unfinished">A simple list, containing one card name per line</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="311"/>
      <source>List with card names</source>
      <translation type="unfinished">List with card names</translation>
    </message>
  </context>
  <context>
    <name>SetEditor</name>
    <message>
      <location filename="../ui/set_editor_widget.ui" line="35"/>
      <source>Set name</source>
      <translation type="unfinished">Set name</translation>
    </message>
    <message>
      <location filename="../ui/set_editor_widget.ui" line="61"/>
      <source>CODE</source>
      <translation type="unfinished">CODE</translation>
    </message>
  </context>
  <context>
    <name>SettingsWindow</name>
    <message>
      <location filename="../../ui/settings_window.py" line="207"/>
      <source>Apply settings to the current document?</source>
      <translation>Appliquer ces paramètres au document actuel ?</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="207"/>
      <source>The new default settings differ from the settings used by the current document.
Apply the new settings to the current document?</source>
      <translation type="unfinished">The new default settings differ from the settings used by the current document.
Apply the new settings to the current document?</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="220"/>
      <source>Reset unsaved changes?</source>
      <translation type="unfinished">Reset unsaved changes?</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="220"/>
      <source>Reset unsaved changes on the current page or on all pages?</source>
      <translation type="unfinished">Reset unsaved changes on the current page or on all pages?</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="226"/>
      <source>Reset everything</source>
      <translation type="unfinished">Reset everything</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="227"/>
      <source>Reset current page</source>
      <translation type="unfinished">Reset current page</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="254"/>
      <source>Restore defaults for the current page or everything?</source>
      <translation type="unfinished">Restore defaults for the current page or everything?</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="254"/>
      <source>Restore the settings on the current page or on all pages to their default values?</source>
      <translation type="unfinished">Restore the settings on the current page or on all pages to their default values?</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="260"/>
      <source>Restore everything</source>
      <translation type="unfinished">Restore everything</translation>
    </message>
    <message>
      <location filename="../../ui/settings_window.py" line="261"/>
      <source>Restore current page</source>
      <translation type="unfinished">Restore current page</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/settings_window.ui" line="17"/>
      <source>Settings</source>
      <translation>Options</translation>
    </message>
  </context>
  <context>
    <name>SummaryPage</name>
    <message numerus="yes">
      <location filename="../../ui/deck_import_wizard.py" line="479"/>
      <source>Beware: The card list currently contains %n potentially oversized card(s).</source>
      <comment>Warning emitted, if at least 1 card has the oversized flag set. The Scryfall server *may* still return a regular-sized image, so not *all* printings marked as oversized are actually so when fetched.</comment>
      <translation type="unfinished">
        <numerusform>Beware: The card list currently contains %n potentially oversized card(s).</numerusform>
        <numerusform>Beware: The card list currently contains %n potentially oversized card(s).</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="499"/>
      <source>Replace document content with the identified cards</source>
      <translation type="unfinished">Replace document content with the identified cards</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="502"/>
      <source>Append identified cards to the document</source>
      <translation type="unfinished">Append identified cards to the document</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="538"/>
      <source>Remove basic lands</source>
      <translation type="unfinished">Remove basic lands</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="539"/>
      <source>Remove all basic lands in the deck list above</source>
      <translation type="unfinished">Remove all basic lands in the deck list above</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="544"/>
      <source>Remove selected</source>
      <translation type="unfinished">Remove selected</translation>
    </message>
    <message>
      <location filename="../../ui/deck_import_wizard.py" line="545"/>
      <source>Remove all selected cards in the deck list above</source>
      <translation type="unfinished">Remove all selected cards in the deck list above</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="438"/>
      <source>Images about to be deleted: {count}</source>
      <translation type="unfinished">Images about to be deleted: {count}</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="439"/>
      <source>Disk space that will be freed: {disk_space_freed}</source>
      <translation type="unfinished">Disk space that will be freed: {disk_space_freed}</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/summary_page.ui" line="14"/>
      <source>Summary</source>
      <translation>Récapitulatif</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="14"/>
      <source>Import a deck list for printing</source>
      <translation>Import d'une liste de cartes pour impression</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="17"/>
      <source>The cards shown here will be imported. Double-click the Set Collector# or Language cells to change selected printings. The text field shows all lines from the input that were not identified as cards.</source>
      <translation type="unfinished">The cards shown here will be imported. Double-click the Set Collector# or Language cells to change selected printings. The text field shows all lines from the input that were not identified as cards.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="23"/>
      <source>If checked, clear all cards in the current document, replacing everything with the list below.
If unchecked, append the cards found below to the document.</source>
      <translation type="unfinished">If checked, clear all cards in the current document, replacing everything with the list below.
If unchecked, append the cards found below to the document.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="27"/>
      <source>Replace the current document content with the found cards</source>
      <translation>Remplacer le contenu du document en cours avec les cartes trouvées</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="37"/>
      <source>These cards were successfully identified:</source>
      <translation>Ces cartes ont été identifiées avec succès :</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="66"/>
      <source>These lines from the deck list were not identified as cards:</source>
      <translation>Ces lignes de la liste de cartes n'ont pas pu être identifiées en tant que cartes :</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="85"/>
      <source>Nothing. All cards were successfully identified!</source>
      <translation>Aucun problème. Toutes les cartes ont été identifiées avec succès !</translation>
    </message>
  </context>
  <context>
    <name>TabbedCentralWidget</name>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="33"/>
      <source>All pages</source>
      <translation type="unfinished">All pages</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="38"/>
      <source>Add new cards</source>
      <translation type="unfinished">Add new cards</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="43"/>
      <source>Current page</source>
      <translation type="unfinished">Current page</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="89"/>
      <source>Remove selected</source>
      <translation type="unfinished">Remove selected</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="100"/>
      <source>Preview</source>
      <translation type="unfinished">Preview</translation>
    </message>
  </context>
  <context>
    <name>TappedOutCSVParser</name>
    <message>
      <location filename="../../decklist_parser/csv_parsers.py" line="197"/>
      <source>Tappedout CSV export</source>
      <translation type="unfinished">Tappedout CSV export</translation>
    </message>
  </context>
  <context>
    <name>UnknownCardImageModel</name>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="256"/>
      <source>Scryfall ID</source>
      <translation type="unfinished">Scryfall ID</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="257"/>
      <source>Front/Back</source>
      <translation type="unfinished">Front/Back</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="258"/>
      <source>High resolution?</source>
      <translation type="unfinished">High resolution?</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="259"/>
      <source>Size</source>
      <translation type="unfinished">Size</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="260"/>
      <source>Path</source>
      <translation type="unfinished">Path</translation>
    </message>
  </context>
  <context>
    <name>UnknownCardRow</name>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="230"/>
      <source>Front</source>
      <translation type="unfinished">Front</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="230"/>
      <source>Back</source>
      <translation type="unfinished">Back</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="236"/>
      <source>Yes</source>
      <translation type="unfinished">Yes</translation>
    </message>
    <message>
      <location filename="../../ui/cache_cleanup_wizard.py" line="236"/>
      <source>No</source>
      <translation type="unfinished">No</translation>
    </message>
  </context>
  <context>
    <name>VerticalAddCardWidget</name>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="26"/>
      <source>The sets in which the currently selected card was printed.</source>
      <translation type="unfinished">The sets in which the currently selected card was printed.</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="29"/>
      <source>Set</source>
      <translation type="unfinished">Set</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="35"/>
      <source>Filter set names</source>
      <translation type="unfinished">Filter set names</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="67"/>
      <source>Collector Number</source>
      <translation type="unfinished">Collector Number</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="92"/>
      <source>Card Name</source>
      <translation type="unfinished">Card Name</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="98"/>
      <source>Filter the list below. Use  % (Percent signs) as wildcards matching any number of characters.</source>
      <translation type="unfinished">Filter the list below. Use  % (Percent signs) as wildcards matching any number of characters.</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="101"/>
      <source>Filter card names</source>
      <translation type="unfinished">Filter card names</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="111"/>
      <source>The filtered list of card names in the currently selected language. Click on an entry to select it and choose a printing.</source>
      <translation type="unfinished">The filtered list of card names in the currently selected language. Click on an entry to select it and choose a printing.</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="136"/>
      <source>Language:</source>
      <translation type="unfinished">Language:</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="152"/>
      <source>Copies:</source>
      <translation type="unfinished">Copies:</translation>
    </message>
  </context>
  <context>
    <name>XMageParser</name>
    <message>
      <location filename="../../decklist_parser/re_parsers.py" line="257"/>
      <source>XMage Deck file</source>
      <translation type="unfinished">XMage Deck file</translation>
    </message>
  </context>
  <context>
    <name>format_size</name>
    <message>
      <location filename="../../ui/common.py" line="178"/>
      <source>{size} {unit}</source>
      <comment>A formatted file size in SI bytes</comment>
      <translation type="unfinished">{size} {unit}</translation>
    </message>
  </context>
</TS>
