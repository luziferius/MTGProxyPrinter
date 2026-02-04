<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" sourcelanguage="en_US" language="es-ES">
  <context>
    <name>AboutDialog</name>
    <message>
      <location filename="../ui/about_dialog.ui" line="14"/>
      <source>About MTGProxyPrinter</source>
      <translation>Acerca de MTGProxyPrinter</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="27"/>
      <source>About</source>
      <translation>Acerca de</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="39"/>
      <source>Application Version:</source>
      <translation>Versión de la Aplicación:</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="55"/>
      <source>Last card update:</source>
      <translation>Última actualización de cartas:</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="62"/>
      <source>Application version</source>
      <translation>Versión de la aplicación</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="87"/>
      <source>Python Version:</source>
      <translation>Versión de Python:</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="107"/>
      <source>Python runtime version</source>
      <translation>Versión de Python en ejecución</translation>
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
      <translation>{application_name} permite imprimir cartas de Magic: The Gathering](https://magic.wizards.com/) para realizar pruebas de juego.

{application_name} es contenido de fans no oficial permitido según la [Política de Contenido de Fans](https://company.wizards.com/fancontentpolicy). No aprobado ni avalado por Wizards. Parte del material utilizado es propiedad de Wizards of the Coast. ©[Wizards of the Coast LLC](https://company.wizards.com/).

Según la Política de Contenido de Fans, no puedes vender los datos descargados mediante este programa, incluyendo el contenido de la base de datos de cartas y las imágenes de cartas descargadas, ni ningún documento creado, tanto en formato digital como físico.

Sitio web del proyecto: [página de inicio de {application_name}]({application_home_page})

Icono de la aplicación de [islanders2013](https://www.reddit.com/user/islanders2013/)

</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="206"/>
      <location filename="../ui/about_dialog.ui" line="215"/>
      <source>Changelog</source>
      <translation>Registro de cambios</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="229"/>
      <source>License</source>
      <translation>Licencia</translation>
    </message>
    <message>
      <location filename="../ui/about_dialog.ui" line="240"/>
      <source>Third party licenses</source>
      <translation>Licencias de terceros</translation>
    </message>
  </context>
  <context>
    <name>ActionAddCard</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/card_actions.py" line="163"/>
      <source>Add {count} × {card_display_string} to page {target}</source>
      <comment>Undo/redo tooltip text. Plural form refers to {target}, not {count}. {target} can be multiple ranges of multiple pages each</comment>
      <translation>
        <numerusform>Añadir {count} × {card_display_string} a la página {target}</numerusform>
        <numerusform>Añadir {count} × {card_display_string} a las páginas {target}</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionCompactDocument</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/compact_document.py" line="112"/>
      <source>Compact document, removing %n page(s)</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>
        <numerusform>Compactando documento, eliminando %n página</numerusform>
        <numerusform>Compactando documento, eliminando %n páginas</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionEditCustomCard</name>
    <message>
      <location filename="../../mtg_proxy_printer/document_controller/edit_custom_card.py" line="88"/>
      <source>Edit custom card, set {column_header_text} to {new_value}</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Editar carta personalizada, establecer {column_header_text} como {new_value}</translation>
    </message>
  </context>
  <context>
    <name>ActionEditDocumentSettings</name>
    <message>
      <location filename="../../mtg_proxy_printer/document_controller/edit_document_settings.py" line="137"/>
      <source>Update document settings</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Editar configuración del documento</translation>
    </message>
  </context>
  <context>
    <name>ActionImportDeckList</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/import_deck_list.py" line="81"/>
      <source>Replace document with imported deck list containing %n card(s)</source>
      <comment>Undo/redo tooltip text. Option to delete the current document enabled.</comment>
      <translation>
        <numerusform>Reemplazar documento con la lista de mazo importado que contiene %n carta</numerusform>
        <numerusform>Reemplazar documento con la lista de mazo importado que contiene %n cartas</numerusform>
      </translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/import_deck_list.py" line="85"/>
      <source>Import a deck list containing %n card(s)</source>
      <comment>Undo/redo tooltip text. Option to delete the current document disabled.</comment>
      <translation>
        <numerusform>Importar una lista de mazo que contiene %n carta</numerusform>
        <numerusform>Importar una lista de mazo que contiene %n cartas</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionLoadDocument</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/load_document.py" line="77"/>
      <source>with %n card(s) total</source>
      <comment>Part of the undo/redo tooltip text. Will be inserted as {cards_total}</comment>
      <translation>
        <numerusform>con un total de %n carta</numerusform>
        <numerusform>con un total de %n cartas</numerusform>
      </translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/load_document.py" line="81"/>
      <source>Load document from &apos;{save_path}&apos;,
containing %n page(s) {cards_total}</source>
      <comment>Undo/redo tooltip text.</comment>
      <translation>
        <numerusform>Cargar documento de &apos;{save_path}&apos;,
que contiene %n página {cards_total}</numerusform>
        <numerusform>Cargar documento de &apos;{save_path}&apos;,
que contiene %n páginas {cards_total}</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionMoveCardsBetweenPages</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/move_cards.py" line="143"/>
      <source>Move %n card(s) from page {source_page} to {target_page}</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>
        <numerusform>Mover %n carta de la página {source_page} a {target_page}</numerusform>
        <numerusform>Mover %n cartas de la página {source_page} a {target_page}</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionMoveCardsWithinPage</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/move_cards.py" line="259"/>
      <source>Reorder %n card(s) on page {page}</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>
        <numerusform>Reordenar %n carta en la página {page}</numerusform>
        <numerusform>Reordenar %n cartas en la página {page}</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionMovePage</name>
    <message>
      <location filename="../../mtg_proxy_printer/document_controller/move_page.py" line="87"/>
      <source>Move page {source_page} to position {target_page}</source>
      <comment>Both parameters are page numbers, like in &apos;Move page 3 to position 7&apos;</comment>
      <translation>Mover página {source_page} a la posición {target_page}</translation>
    </message>
  </context>
  <context>
    <name>ActionNewDocument</name>
    <message>
      <location filename="../../mtg_proxy_printer/document_controller/new_document.py" line="72"/>
      <source>Create new document</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Crear un documento nuevo</translation>
    </message>
  </context>
  <context>
    <name>ActionNewPage</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/page_actions.py" line="87"/>
      <source>Add page(s) {pages}</source>
      <comment>Undo/redo tooltip text. Translations should drop the %n placeholder</comment>
      <translation>
        <numerusform>Añadir página {pages}</numerusform>
        <numerusform>Añadir páginas {pages}</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionRemoveCards</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/card_actions.py" line="222"/>
      <source>Remove %n card(s) from page {page_number}</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>
        <numerusform>Eliminar %n carta de la página {page_number}</numerusform>
        <numerusform>Eliminar %n cartas de la página {page_number}</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionRemovePage</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/page_actions.py" line="188"/>
      <source>%n card(s) total</source>
      <comment>Undo/redo tooltip text. The total number of cards removed. Used as {formatted_card_count}</comment>
      <translation>
        <numerusform>%n carta en total</numerusform>
        <numerusform>%n cartas en total</numerusform>
      </translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/document_controller/page_actions.py" line="194"/>
      <source>Remove page(s) {formatted_pages} containing {formatted_card_count}</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>
        <numerusform>Eliminar página {formatted_pages} que contiene {formatted_card_count}</numerusform>
        <numerusform>Eliminar páginas {formatted_pages} que contiene {formatted_card_count}</numerusform>
      </translation>
    </message>
  </context>
  <context>
    <name>ActionReplaceCard</name>
    <message>
      <location filename="../../mtg_proxy_printer/document_controller/replace_card.py" line="101"/>
      <source>Replace card {old_card} on page {page_number} with {new_card}</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Reemplazar carta {old_card} en la página {page_number} con {new_card}</translation>
    </message>
  </context>
  <context>
    <name>ActionSaveDocument</name>
    <message>
      <location filename="../../mtg_proxy_printer/document_controller/save_document.py" line="174"/>
      <source>Save document to &apos;{save_file_path}&apos;.</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Guardar documento en &apos;{save_file_path}&apos;.</translation>
    </message>
  </context>
  <context>
    <name>ActionShuffleDocument</name>
    <message>
      <location filename="../../mtg_proxy_printer/document_controller/shuffle_document.py" line="96"/>
      <source>Shuffle document</source>
      <comment>Undo/redo tooltip text</comment>
      <translation>Mezclar documento</translation>
    </message>
  </context>
  <context>
    <name>ApiStreamTask</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="331"/>
      <source>Requesting the number of available cards on Scryfall failed: 
{error}</source>
      <comment>Error message shown in a message box</comment>
      <translation>La solicitud del número de cartas disponibles en Scryfall falló: 
{error}</translation>
    </message>
  </context>
  <context>
    <name>ApplicationUpdateCheckTask</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/update_checker.py" line="171"/>
      <source>Application update check: </source>
      <comment>Progress bar label text</comment>
      <translation>Comprobación de actualizaciones de aplicación: </translation>
    </message>
  </context>
  <context>
    <name>BatchDownloadTask</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/image_downloader.py" line="234"/>
      <source>Importing deck list:</source>
      <comment>Progress bar label text</comment>
      <translation>Importando lista de mazo:</translation>
    </message>
  </context>
  <context>
    <name>CacheCleanupWizard</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="481"/>
      <source>Cleanup locally stored card images</source>
      <comment>Dialog window title</comment>
      <translation>Limpiar imágenes de cartas almacenadas localmente</translation>
    </message>
  </context>
  <context>
    <name>CardFilterPage</name>
    <message>
      <location filename="../ui/cache_cleanup_wizard/card_filter_page.ui" line="14"/>
      <source>Select images for removal</source>
      <translation>Seleccionar imágenes para eliminar</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/card_filter_page.ui" line="17"/>
      <source>Click on entries in the tables below to mark or un-mark them for removal. All selected entries will be removed.</source>
      <translation>Haga clic en las entradas de las tablas de abajo para marcarlas o desmarcarlas para su eliminación. Todas las entradas seleccionadas serán eliminadas.</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/card_filter_page.ui" line="30"/>
      <source>All images currently stored on disk:</source>
      <translation>Todas las imágenes almacenadas actualmente en disco:</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/card_filter_page.ui" line="69"/>
      <source>Images found on disk that can not be associated with any card.</source>
      <translation>Imágenes encontradas en el disco que no pueden ser asociadas con ninguna carta.</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/card_filter_page.ui" line="72"/>
      <source>Unknown images:</source>
      <translation>Imágenes desconocidas:</translation>
    </message>
  </context>
  <context>
    <name>CardListModel</name>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="89"/>
      <source>Copies</source>
      <comment>Table header for card lists. Number of copies that will be added</comment>
      <translation>Copias</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="91"/>
      <source>Card name</source>
      <comment>Table header for card lists</comment>
      <translation>Nombre de carta</translation>
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
      <translation>Coleccionista #</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="97"/>
      <source>Language</source>
      <comment>Table header for card lists. Card language.</comment>
      <translation>Idioma</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="99"/>
      <source>Side</source>
      <comment>Table header for card lists. Side of the card</comment>
      <translation>Lado</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="136"/>
      <source>Front</source>
      <comment>Magic card side</comment>
      <translation>Frente</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="136"/>
      <source>Back</source>
      <comment>Magic card side</comment>
      <translation>Reverso</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="141"/>
      <source>Beware: Potentially oversized card!
This card may not fit in your deck.</source>
      <comment>Tooltip shown on cards that, according to API results, have double the physical size. The actual image may still have regular size.</comment>
      <translation>Atención: ¡Carta potencialmente de gran tamaño!
Esta carta puede no caber en tu mazo.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/card_list.py" line="331"/>
      <source>Double-click on entries to
switch the selected printing.</source>
      <comment>Tooltip text</comment>
      <translation>Haga doble clic en las entradas para
cambiar la impresión seleccionada.</translation>
    </message>
  </context>
  <context>
    <name>CardSideSelectionDelegate</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/item_delegates.py" line="96"/>
      <source>Front</source>
      <comment>Magic card side</comment>
      <translation>Frente</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/item_delegates.py" line="97"/>
      <source>Back</source>
      <comment>Magic card side</comment>
      <translation>Reverso</translation>
    </message>
  </context>
  <context>
    <name>ColumnarCentralWidget</name>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="55"/>
      <source>Move up</source>
      <translation>Mover arriba</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="110"/>
      <source>Current page:</source>
      <translation>Página actual:</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="145"/>
      <source>Remove selected</source>
      <translation>Eliminar selección</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="89"/>
      <source>Add new cards:</source>
      <translation>Añadir nuevas cartas:</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="68"/>
      <source>Move down</source>
      <translation>Mover abajo</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/columnar.ui" line="78"/>
      <source>All pages:</source>
      <translation>Todas las páginas:</translation>
    </message>
  </context>
  <context>
    <name>CustomCardImportDialog</name>
    <message>
      <location filename="../ui/custom_card_import_dialog.ui" line="14"/>
      <source>Import custom cards</source>
      <translation>Importar cartas personalizadas</translation>
    </message>
    <message>
      <location filename="../ui/custom_card_import_dialog.ui" line="20"/>
      <source>Set Copies to …</source>
      <translation>Establecer Copias en …</translation>
    </message>
    <message>
      <location filename="../ui/custom_card_import_dialog.ui" line="40"/>
      <source>Remove selected</source>
      <translation>Eliminar selección</translation>
    </message>
    <message>
      <location filename="../ui/custom_card_import_dialog.ui" line="50"/>
      <source>Load images</source>
      <translation>Cargar imágenes</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/custom_card_import_dialog.py" line="100"/>
      <source>Import custom cards</source>
      <comment>File selection dialog window title</comment>
      <translation>Importar cartas personalizadas</translation>
    </message>
  </context>
  <context>
    <name>DatabaseImportTask</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="393"/>
      <source>Import card data from File:</source>
      <comment>Progress bar label text</comment>
      <translation>Importar datos de carta desde archivo:</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="398"/>
      <source>Update card data from Scryfall:</source>
      <comment>Progress bar label text</comment>
      <translation>Actualizar datos de carta desde Scryfall:</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="408"/>
      <source>Error during import from file:
{path}</source>
      <comment>Error message shown in a message box</comment>
      <translation>Error durante la importación del archivo:
{path}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="414"/>
      <source>Error during update from Scryfall</source>
      <comment>Error message shown in a message box</comment>
      <translation>Error durante la actualización de Scryfall</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="439"/>
      <source>Failed to parse data from Scryfall. Reported error: {error}</source>
      <comment>Error message shown in a message box</comment>
      <translation>Error al analizar los datos de Scryfall. Error reportado: {error}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="488"/>
      <source>Post-processing card data:</source>
      <comment>Progress bar label text</comment>
      <translation>Post-procesando datos de carta:</translation>
    </message>
  </context>
  <context>
    <name>DatabaseMigrationRunner</name>
    <message>
      <location filename="../../mtg_proxy_printer/carddb_migrations.py" line="782"/>
      <source>Card database migration failed! Will try to re-create it from scratch.
This will wipe any previously downloaded card data and require re-downloading it.
Reported error message:

{error_message}</source>
      <comment>Applying card database migrations required after an app upgrade failed, presumably because the data on disk got corrupted somehow.</comment>
      <translation>¡Error al migrar la base de datos de cartas! Se intentará recrearla desde cero.
Esto borrará cualquier dato de cartas descargado previamente y será necesario volver a descargarlo.
Mensaje de error reportado:

{error_message}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/carddb_migrations.py" line="802"/>
      <source>Running database migrations:</source>
      <translation>Ejecutando migraciones de base de datos:</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/carddb_migrations.py" line="815"/>
      <source>Migrate to version %n:</source>
      <comment>The numeric parameter is a version number, and not countable.</comment>
      <translation>Migrar a la versión %n:</translation>
    </message>
  </context>
  <context>
    <name>DebugSettingsPage</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="130"/>
      <source>Debug settings</source>
      <translation>Configuración de depuración</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="131"/>
      <source>Things useful for investigating bugs in the application</source>
      <translation>Cosas útiles para investigar errores en la aplicación</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="185"/>
      <source>Select download location</source>
      <translation>Seleccionar ubicación de descarga</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="193"/>
      <source>Selected location is not a directory</source>
      <translation>La ubicación seleccionada no es un directorio</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="195"/>
      <source>Cannot write the card data at the given location, because it is not a directory:
{location}</source>
      <translation>No se pueden escribir los datos de la carta en la ubicación indicada, porque no es un directorio:
{location}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="206"/>
      <source>Import previously downloaded card data obtained from Scryfall</source>
      <translation>Importar datos de carta previamente descargados de Scryfall</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="208"/>
      <source>Scryfall card data (*.json *.json.gz)</source>
      <translation>Datos de carta Scryfall (*.json *.json.gz)</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="216"/>
      <source>Selected location is not a file</source>
      <translation>La ubicación seleccionada no es un archivo</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="217"/>
      <source>Cannot find the selected file:
{location}</source>
      <translation>No se puede encontrar el archivo seleccionado:
{location}</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="17"/>
      <source>Open debug log directory</source>
      <translation>Abrir directorio de registro de depuración</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="27"/>
      <source>Enable writing a log file to disk</source>
      <translation>Habilitar la escritura de un archivo de registro en el disco</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="34"/>
      <source>Cutelog is a live log event viewer that can be used to monitor events in real-time.</source>
      <translation>Cutelog es un visor de eventos en vivo que puede ser utilizado para monitorear eventos en tiempo real.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="37"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;See &lt;a href=&quot;https://github.com/busimus/cutelog&quot;&gt;&lt;span style=&quot; text-decoration: underline; color:#2980b9;&quot;&gt;https://github.com/busimus/cutelog&lt;/span&gt;&lt;/a&gt; for details about Cutelog.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Ver &lt;a href=&quot;https://github.com/busimus/cutelog&quot;&gt;&lt;span style=&quot; text-decoration: underline; color:#2980b9;&quot;&gt;https://github.com/busimus/cutelog&lt;/span&gt;&lt;/a&gt; para más detalles sobre Cutelog.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="40"/>
      <source>Enable Cutelog integration</source>
      <translation>Habilitar integración con Cutelog</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="47"/>
      <source>Download card data as file</source>
      <translation>Descargar datos de carta como archivo</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="64"/>
      <source>Event severity that gets logged to file:</source>
      <translation>Gravedad del evento que se registra en el archivo:</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="74"/>
      <source>Only write events with the given severity level and higher to the log file.</source>
      <translation>Sólo escribir eventos con el nivel de gravedad dado y superior al archivo de registro.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="81"/>
      <source>Debug settings (Changing these require an application restart)</source>
      <translation>Ajustes de depuración (cambiar estos requiere reiniciar la aplicación)</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="101"/>
      <source>Import card data from file</source>
      <translation>Importar datos de carta desde archivo</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/debug_settings_page.ui" line="117"/>
      <source>Open the Cutelog homepage</source>
      <translation>Abrir la página de inicio de Cutelog</translation>
    </message>
  </context>
  <context>
    <name>DeckImportWizard</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="648"/>
      <source>Import a deck list</source>
      <comment>Window title</comment>
      <translation>Importar lista de mazo</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="674"/>
      <source>Oversized cards present</source>
      <comment>Message box title. Shown when the deck list contains likely unwanted oversized cards.</comment>
      <translation>Cartas sobredimensionadas presentes</translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="677"/>
      <source>There are %n possibly oversized cards in the deck list that may not fit into a deck, when printed out.

Continue and use these cards as-is?</source>
      <comment>Message box body text. Shown when the deck list contains likely unwanted oversized cards.</comment>
      <translation>
        <numerusform>Hay %n carta posiblemente sobredimensionada en la lista de mazo que pueden no encajar en un mazo, al imprimirlas.

¿Continuar y usar esta carta así?</numerusform>
        <numerusform>Hay %n cartas posiblemente sobredimensionadas en la lista de mazo que pueden no encajar en un mazo, al imprimirlas.

¿Continuar y usar estas cartas así?</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="689"/>
      <source>Incompatible file selected</source>
      <comment>Message box title. Shown when trying to parse a deck list returns no results.</comment>
      <translation>Archivo incompatible seleccionado</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="692"/>
      <source>Unable to parse the given deck list, no results were obtained.
Maybe you selected the wrong deck list type?</source>
      <comment>Message box body text. Shown when trying to parse a deck list returns no results.</comment>
      <translation>No se puede analizar la lista de mazo dada, no se han obtenido resultados.
¿Tal vez haya seleccionado el tipo de lista de mazo incorrecto?</translation>
    </message>
  </context>
  <context>
    <name>DecklistImportSettingsPage</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="228"/>
      <source>Deck list import</source>
      <translation>Importar lista de mazo</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="228"/>
      <source>Configure the deck list importer</source>
      <translation>Configurar como se importan las listas de mazos</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="238"/>
      <source>Select default deck list search path</source>
      <translation>Seleccionar ruta por defecto de búsqueda de listas de mazos</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="17"/>
      <source>Browse …</source>
      <translation>Explorar …</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="30"/>
      <source>Deck list search path</source>
      <translation>Ruta de búsqueda de lista de mazos</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="37"/>
      <source>The import wizard can remove basic lands fully- or semi-automatic.
These settings control the removal behavior.</source>
      <translation>El asistente de importación puede eliminar las tierras básicas de manera completa o semi automática.
Estos ajustes controlan el comportamiento de eliminación.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="41"/>
      <source>Control the one-click or automatic basic land removal</source>
      <translation>Controla la eliminación automática de tierras básica o de un solo clic</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="47"/>
      <source>If enabled, basic lands are automatically removed from deck lists.
If disabled, the deck import wizard keeps them by default,
but offers the removal via a single button click.</source>
      <extracomment>Tooltip</extracomment>
      <translation>Si está activada, las tierras básicas se eliminan automáticamente de las listas de mazos.
Si está desactivada, el asistente de importación de mazos las conserva por defecto, pero permite eliminarlas con un solo clic.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="52"/>
      <source>Fully automatically remove basic lands</source>
      <translation>Eliminación totalmente automática de tierras básicas</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="59"/>
      <source>When enabled, treat Wastes like any other basic land</source>
      <extracomment>Tooltip</extracomment>
      <translation>Cuando está activado, trata a los Yermos como cualquier otra tierra básica</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="62"/>
      <source>Removal includes Wastes</source>
      <translation>Eliminación incluye Yermos</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="69"/>
      <source>When enabled, treat Snow-Covered basic lands like any other basic land</source>
      <extracomment>Tooltip</extracomment>
      <translation>Cuando está activado, trata las tierras básicas cubiertas de nieve como cualquier otra tierra básica</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="72"/>
      <source>Removal includes Snow-Covered Basic lands</source>
      <translation>Eliminación incluye tierras básicas cubiertas de nieve</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="82"/>
      <source>These options control the deck list import function.</source>
      <translation>Estas opciones controlan la función de importación de lista de mazos.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="89"/>
      <source>Not all deck list formats always contain complete data.
These options set the default behavior when encountering ambiguous card</source>
      <translation>No todos los formatos de la lista de mazos siempre contienen datos completos.
Estas opciones establecen el comportamiento predeterminado cuando se encuentra con una carta ambigua</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="93"/>
      <source>Control print selection in ambiguous cases</source>
      <translation>Controla la selección de impresión en casos ambiguos</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="102"/>
      <source>When automatically selecting a printing, prefer printings with already downloaded images over other possible printings.</source>
      <translation>Al seleccionar automáticamente una impresión, preferir las impresiones con imágenes ya descargadas sobre otras posibles impresiones.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="105"/>
      <source>Prefer printings with already downloaded images</source>
      <translation>Preferir impresiones con imágenes ya descargadas</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="112"/>
      <source>Always enable automatic deck list translation when importing deck lists.
This avoids adding foreign language cards, if the deck list happens to contain some.</source>
      <translation>Activar siempre la traducción automática de la lista de mazos al importar listas de mazos.
Esto evita añadir tarjetas de idioma foráneo, si la lista de mazos contiene algunas.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="116"/>
      <source>Enable translating imported deck lists by default</source>
      <translation>Activar la traducción por defecto de listas de mazos importadas</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="123"/>
      <source>Not all deck list formats always contain complete data to identify exact printings.
If enabled, choose an arbitrary printing, instead of failing to identify such cards.
With some deck list formats, this option is always enabled.</source>
      <translation>No todos los formatos de lista de mazo contienen datos completos para identificar las impresiones exactas.
Si está activada, se elige una impresión arbitraria, en lugar de no identificar dichas cartas.
Con algunos formatos de lista de mazo, esta opción siempre está activada.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="128"/>
      <source>Automatically select a printing</source>
      <translation>Seleccionar automáticamente una impresión</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="138"/>
      <source>If set, use this as the default location for loading deck lists. Your webbrowser’s download directory is a good choice.</source>
      <translation>Si se establece, utilice esta como ubicación predeterminada para cargar listas de mazos. El directorio de descargas de su navegador web es una buena elección.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/decklist_import_settings_page.ui" line="144"/>
      <source>Path to a directory</source>
      <translation>Ruta a un directorio</translation>
    </message>
  </context>
  <context>
    <name>DefaultDocumentLayoutSettingsPage</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="494"/>
      <source>Default document settings</source>
      <translation>Configuración de documento por defecto</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="495"/>
      <source>Set the default document settings used for new documents,
like page size, margins, spacings, etc.</source>
      <translation>Establece la configuración predeterminada del documento usado para nuevos documentos,
como tamaño de página, márgenes, espacios, etc.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="501"/>
      <source>Default settings for new documents</source>
      <translation>Configuración predeterminada para nuevos documentos</translation>
    </message>
  </context>
  <context>
    <name>Document</name>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="107"/>
      <source>Card name</source>
      <comment>Table header</comment>
      <translation>Nombre de carta</translation>
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
      <translation>Coleccionista #</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="110"/>
      <source>Language</source>
      <comment>Table header</comment>
      <translation>Idioma</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="111"/>
      <source>Image</source>
      <comment>Table header</comment>
      <translation>Imagen</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="112"/>
      <source>Side</source>
      <comment>Table header</comment>
      <translation>Lado</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="203"/>
      <source>Double-click on entries to
switch the selected printing.</source>
      <translation>Haga doble clic en las entradas para
cambiar la impresión seleccionada.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="415"/>
      <source>Page {current}/{total}</source>
      <comment>Tooltip. Shown when hovering over a page in the page list</comment>
      <translation>Página {current}/{total}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="448"/>
      <source>Front</source>
      <comment>Magic card side</comment>
      <translation>Frente</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="448"/>
      <source>Back</source>
      <comment>Magic card side</comment>
      <translation>Reverso</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/model/document.py" line="511"/>
      <source>Empty Placeholder</source>
      <comment>Card name of the blank placeholder that can be added to keep slots on a page free.</comment>
      <translation>Marcador de posición vacío</translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/model/document.py" line="454"/>
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
      <location filename="../../mtg_proxy_printer/document_controller/_interface.py" line="110"/>
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
      <translation>Configurar el documento actual</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="394"/>
      <source>These settings only affect the current document</source>
      <comment>Shown within the dialog to indicate the scope of the presented settings</comment>
      <translation>Estos ajustes solo afectan al documento actual</translation>
    </message>
  </context>
  <context>
    <name>ExportCardImagesDialog</name>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="17"/>
      <source>Export card images</source>
      <translation>Exportar imágenes de cartas</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="29"/>
      <source>Browse …</source>
      <translation>Explorar …</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="52"/>
      <source>Custom cards</source>
      <translation>Cartas personalizadas</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="66"/>
      <source>Output directory:</source>
      <translation>Directorio de salida:</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="73"/>
      <source>Official cards</source>
      <translation>Cartas oficiales</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="83"/>
      <source>Which card images should be exported?</source>
      <translation>¿Qué imágenes de cartas deben ser exportadas?</translation>
    </message>
    <message>
      <location filename="../ui/export_card_images_dialog.ui" line="93"/>
      <source>Path to a directory</source>
      <translation>Ruta a un directorio</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="472"/>
      <source>Select card image export location</source>
      <comment>File dialog window title</comment>
      <translation>Seleccionar ubicación de exportación de imágenes de carta</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="521"/>
      <source>Copy failed for {card_name}! Disk detached/full? Aborting.</source>
      <comment>Error message shown to the user when exporting cards to a directory fails.</comment>
      <translation>¡La copia ha fallado para {card_name}! ¿Disco desconectado/lleno? Abortando.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="553"/>
      <source>Write failed for {card_name}! Disk detached/full? Aborting.</source>
      <comment>Error message shown to the user when exporting cards to a directory fails.</comment>
      <translation>¡La escritura ha fallado para {card_name}! ¿Disco desconectado/lleno? Abortando.</translation>
    </message>
  </context>
  <context>
    <name>ExportSettingsPage</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="570"/>
      <source>Export settings</source>
      <translation>Exportar ajustes</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="570"/>
      <source>Configure the PDF/PNG export</source>
      <translation>Configurar la exportación de PDF/PNG</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="610"/>
      <source>Select default export location</source>
      <translation>Seleccionar ubicación de exportación por defecto</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="620"/>
      <source>Select PNG background color</source>
      <translation>Seleccionar color de fondo PNG</translation>
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
      <translation>Dividir automáticamente los documentos PDF si superan esta cantidad de páginas.
Establezca esta opción en cero para desactivar la división.


Al imprimir archivos PDF con una unidad flash USB conectada directamente a la impresora, es posible que esta se niegue a imprimir documentos que superen un límite de tamaño arbitrario.
Para solucionar esta limitación, puede activar esta opción y limitar el número de páginas por PDF. Si el documento tiene más páginas, se exportará automáticamente a varios documentos PDF.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="34"/>
      <source> pages</source>
      <translation> páginas</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="44"/>
      <source>Browse…</source>
      <translation>Explorar…</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="57"/>
      <source>If enabled, landscape documents are rotated by 90° to portrait mode during export.
Enable this, if printing from PDFs in landscape format results in portrait printouts with cropped-off sides.

Enabling this may cause the cut helper lines to flicker or not show in some PDF viewers.
So only enable this, if actually required.</source>
      <translation>Si está activado, los documentos en horizontal se giran a 90° para el modo retrato durante la exportación.
Habilite esto, si la impresión desde PDF en formato apaisado resulta en impresiones de retrato con lados recortados.

Activar esto puede causar que las líneas de ayuda de corte parpadeen o no se muestren en algunos visores PDF.
Así que sólo habilite esto, si es realmente necesario.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="64"/>
      <source>Enable landscape workaround: Rotate landscape pages by 90°</source>
      <translation>Activar vista horizontal: Rotar impresiones a 90°</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="74"/>
      <location filename="../ui/settings_window/export_settings_page.ui" line="90"/>
      <source>If set, use this as the default location for saving exported PDF documents.</source>
      <translation>Si se establece, utilice esta como ubicación predeterminada para guardar documentos PDF exportados.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="80"/>
      <source>Path to a directory</source>
      <translation>Ruta a un directorio</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="93"/>
      <source>Export path</source>
      <translation>Ruta para exportar</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="116"/>
      <source>PNG background color</source>
      <translation>Color de fondo PNG</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="137"/>
      <source>Split PDF documents longer than</source>
      <translation>Dividir documentos PDF más largos de</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/export_settings_page.ui" line="154"/>
      <source>Background color used for documents exported as PNG images.</source>
      <translation>Color de fondo utilizado para documentos exportados como imágenes PNG.</translation>
    </message>
  </context>
  <context>
    <name>FileDownloadTask</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="161"/>
      <source>Downloading card data:</source>
      <comment>Progress bar label text</comment>
      <translation>Descargando datos de carta:</translation>
    </message>
  </context>
  <context>
    <name>FileStreamTask</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/card_info_downloader.py" line="265"/>
      <source>Importing card data from disk:</source>
      <comment>Progress bar label text</comment>
      <translation>Importar datos de carta desde archivo:</translation>
    </message>
  </context>
  <context>
    <name>FilterSetupPage</name>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="14"/>
      <source>Cleanup locally stored card images</source>
      <translation>Limpiar imágenes de cartas almacenadas localmente</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="17"/>
      <source>This wizard can be used to remove unwanted card images currently stored on your computer. You can enable automatic cleanup conditions below, to preselect images for removal.</source>
      <translation>Este asistente se puede utilizar para eliminar las imágenes de cartas no deseadas almacenadas actualmente en su ordenador. Puede habilitar las condiciones de limpieza automáticas a continuación, para seleccionar imágenes para su eliminación.</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="23"/>
      <source>Delete everything</source>
      <translation>Eliminar todo</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="33"/>
      <source>Select images for removal based on any matching criterion.</source>
      <translation>Seleccione imágenes para eliminarlas basándose en cualquier criterio coincidente.</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="36"/>
      <source>Select images for deletion, that are …</source>
      <translation>Seleccionar imágenes para eliminar, que son …</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="42"/>
      <source>Used in prints and PDFs less often than:</source>
      <translation>Utilizado en impresiones y PDF menos a menudo que:</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="49"/>
      <source>Not used in prints for:</source>
      <translation>No usado en impresiones para:</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="59"/>
      <source> days</source>
      <translation> días</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="75"/>
      <source> times</source>
      <translation> veces</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="88"/>
      <source>Card images may become unknown, if printings are removed by Scryfall.
This filter also applies to cards and printings hidden by a card filter in the settings.
For example, if you downloaded images of silver-bordered cards and then configured the program to hide those,
all these images become hidden and will be removed.</source>
      <translation>Las imágenes de las cartas pueden desconocerse si Scryfall elimina las impresiones.
Este filtro también se aplica a las cartas e impresiones ocultas por un filtro de cartas en la configuración.
Por ejemplo, si descargaste imágenes de cartas con borde plateado y configuraste el programa para ocultarlas, todas estas imágenes se ocultarán y se eliminarán.</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/filter_setup_page.ui" line="94"/>
      <source>Unknown or belong to hidden printings</source>
      <translation>Desconocido o pertenecen a impresiones ocultas</translation>
    </message>
  </context>
  <context>
    <name>FormatPrintingFilter</name>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="14"/>
      <source>Hide cards banned in specific Formats</source>
      <translation type="unfinished">Hide cards banned in specific Formats</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="20"/>
      <source>Pioneer</source>
      <extracomment>An MTG format name</extracomment>
      <translation type="unfinished">Pioneer</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="27"/>
      <source>Modern</source>
      <extracomment>An MTG format name</extracomment>
      <translation type="unfinished">Modern</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="34"/>
      <source>Historic</source>
      <extracomment>An MTG format name</extracomment>
      <translation type="unfinished">Historic</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="41"/>
      <source>Vintage</source>
      <extracomment>An MTG format name</extracomment>
      <translation type="unfinished">Vintage</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="54"/>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="84"/>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="114"/>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="130"/>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="153"/>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="169"/>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="185"/>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="201"/>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="217"/>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="240"/>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="257"/>
      <source>View cards hidden by this filter on the Scryfall website.</source>
      <extracomment>Causes the application to open the web browser showing the affected cards</extracomment>
      <translation type="unfinished">View cards hidden by this filter on the Scryfall website.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="64"/>
      <source>Penny</source>
      <extracomment>An MTG format name</extracomment>
      <translation type="unfinished">Penny</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="71"/>
      <source>Standard</source>
      <extracomment>An MTG format name</extracomment>
      <translation type="unfinished">Standard</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="94"/>
      <source>Pauper</source>
      <extracomment>An MTG format name</extracomment>
      <translation type="unfinished">Pauper</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="101"/>
      <source>Commander</source>
      <extracomment>An MTG format name</extracomment>
      <translation type="unfinished">Commander</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="140"/>
      <source>Brawl</source>
      <extracomment>An MTG format name</extracomment>
      <translation type="unfinished">Brawl</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="227"/>
      <source>Legacy</source>
      <extracomment>An MTG format name</extracomment>
      <translation type="unfinished">Legacy</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/format_printing_filter.ui" line="250"/>
      <source>Oathbreaker</source>
      <extracomment>An MTG format name</extracomment>
      <translation type="unfinished">Oathbreaker</translation>
    </message>
  </context>
  <context>
    <name>GeneralPrintingFilter</name>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="14"/>
      <source>General printing filters</source>
      <translation type="unfinished">General printing filters</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="26"/>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="45"/>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="61"/>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="95"/>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="122"/>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="138"/>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="220"/>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="248"/>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="264"/>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="280"/>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="290"/>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="327"/>
      <source>View cards hidden by this filter on the Scryfall website.</source>
      <extracomment>Causes the application to open the web browser showing the affected cards</extracomment>
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
      <translation type="unfinished">Hide borderless cards</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="82"/>
      <source>Hide Token cards</source>
      <translation type="unfinished">Hide Token cards</translation>
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
      <translation type="unfinished">Hide reversible cards</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="148"/>
      <source>Hide cards and printings that are only available on digital platforms. This includes all kinds of digital printings.</source>
      <translation type="unfinished">Hide cards and printings that are only available on digital platforms. This includes all kinds of digital printings.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="151"/>
      <source>Hide digital cards</source>
      <translation type="unfinished">Hide digital cards</translation>
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
      <translation type="unfinished">Hide “funny” cards</translation>
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
      <translation type="unfinished">Hide oversized cards</translation>
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
      <translation type="unfinished">Hide gold-bordered cards</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="197"/>
      <source>Hide white-bordered cards</source>
      <translation type="unfinished">Hide white-bordered cards</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="204"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Hide cards banned for depicting racism.&lt;/p&gt;&lt;p&gt;Background:&lt;/p&gt;&lt;p&gt;Some cards were banned by Wizards of the Coast, because they depict references to controversial real-world events, religion or contain combinations of card effect, name and artwork that, when viewed together, depict racism. These cards are banned in all sanctioned tournament formats and several community formats like Commander, Oathbreaker and others.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation type="unfinished">&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Hide cards banned for depicting racism.&lt;/p&gt;&lt;p&gt;Background:&lt;/p&gt;&lt;p&gt;Some cards were banned by Wizards of the Coast, because they depict references to controversial real-world events, religion or contain combinations of card effect, name and artwork that, when viewed together, depict racism. These cards are banned in all sanctioned tournament formats and several community formats like Commander, Oathbreaker and others.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="207"/>
      <source>Hide cards depicting racism</source>
      <translation type="unfinished">Hide cards depicting racism</translation>
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
      <translation type="unfinished">Hide cards with placeholder images</translation>
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
      <translation type="unfinished">Hide extended art cards</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="311"/>
      <source>Artwork cards that can be found in Set Boosters or Play Boosters</source>
      <translation type="unfinished">Artwork cards that can be found in Set Boosters or Play Boosters</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_printing_filter.ui" line="314"/>
      <source>Hide Art Series cards</source>
      <translation type="unfinished">Hide Art Series cards</translation>
    </message>
  </context>
  <context>
    <name>GeneralSettingsPage</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="297"/>
      <source>General settings</source>
      <translation>Configuración General</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="304"/>
      <source>Horizontal layout</source>
      <translation>Diseño horizontal</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="305"/>
      <source>Columnar layout</source>
      <translation>Diseño de Columna</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="306"/>
      <source>Tabbed layout</source>
      <translation>Diseño de pestaña</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="309"/>
      <source>System default</source>
      <translation>Predeterminado por el sistema</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="310"/>
      <source>English (US) [{progress}%]</source>
      <translation>Inglés (US) [{progress}%]</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="311"/>
      <source>German [{progress}%]</source>
      <translation>Alemán [{progress}%]</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="312"/>
      <source>French [{progress}%]</source>
      <translation>Francés [{progress}%]</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="321"/>
      <source>Select default save location</source>
      <comment>File picker title text</comment>
      <translation>Seleccionar ubicación de guardado por defecto</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="329"/>
      <source>Select custom card search path</source>
      <comment>File picker title text</comment>
      <translation>Seleccionar ruta de búsqueda de carta personalizada</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="17"/>
      <source>Look &amp;&amp; Feel (Changing most of these require an application restart)</source>
      <extracomment>Settings section header</extracomment>
      <translation type="unfinished">Look &amp;&amp; Feel (Changing most of these require an application restart)</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="23"/>
      <source>Application language</source>
      <translation>Idioma de la aplicación</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="30"/>
      <source>Main window layout</source>
      <translation>Diseño de ventana principal</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="40"/>
      <source>Open the main window maximized</source>
      <extracomment>On/off setting</extracomment>
      <translation>Abrir la ventana principal maximizada</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="53"/>
      <source>Horizontal adds a wide, horizontal search area above the currently edited page, and is best for taller screens, like 4:3 or 3:2.
Columnar organizes the main window content in four columns, and is best for (ultra-)wide screens.
Tabbed uses tabs to only show parts of the main window at a time. Best used with small screens in portrait mode (i.e. 9:16), otherwise not recommended.</source>
      <extracomment>Tooltip for the main window layout selector. References the values by name</extracomment>
      <translation>El modo horizontal añade un área de búsqueda amplia y horizontal sobre la página editada y es ideal para pantallas altas, como 4:3 o 3:2.
El modo columnar organiza el contenido de la ventana principal en cuatro columnas y es ideal para pantallas ultra anchas.
El modo pestañas usa pestañas para mostrar solo partes de la ventana principal a la vez. Se recomienda su uso con pantallas pequeñas en modo vertical (ej. 9:16); de lo contrario, no se recomienda.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="69"/>
      <source>Open all wizards and dialogs maximized</source>
      <extracomment>On/off setting</extracomment>
      <translation>Abrir todos los asistentes y diálogos maximizados</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="79"/>
      <source>Double-faced cards</source>
      <extracomment>Settings section header</extracomment>
      <translation>Cartas de doble cara</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="85"/>
      <source>When adding double-faced cards, automatically add the same number of copies of the other side.
Uses the appropriate, matching other card side.
Uncheck to disable this automatism.</source>
      <translation>Al añadir tarjetas de doble cara, automáticamente añade el mismo número de copias del otro lado.
Utiliza lo apropiado y coincide con otro lado de la tarjeta.
Desmarque para desactivar este automatismo.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="90"/>
      <source>Automatically add the other side of double-faced cards</source>
      <translation>Añadir automáticamente el otro lado de las cartas de doble cara</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="100"/>
      <source>These paths are selected by default when browsing the file system for files</source>
      <translation>Estas rutas se seleccionan por defecto al navegar por el sistema de archivos</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="103"/>
      <source>Default save paths</source>
      <extracomment>Settings section header</extracomment>
      <translation>Rutas de guardado por defecto</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="109"/>
      <location filename="../ui/settings_window/general_settings_page.ui" line="270"/>
      <source>Browse…</source>
      <extracomment>Button tooltip</extracomment>
      <translation>Explorar…</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="122"/>
      <source>Document save path</source>
      <translation>Ruta de guardado del documento</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="132"/>
      <source>If set, use this as the default location for saving documents.</source>
      <translation>Si se establece, utilice esta como ubicación predeterminada para guardar documentos.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="138"/>
      <location filename="../ui/settings_window/general_settings_page.ui" line="260"/>
      <source>Path to a directory</source>
      <extracomment>Line editor placeholder text</extracomment>
      <translation>Ruta a un directorio</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="154"/>
      <source>Automatic update checks</source>
      <extracomment>Settings section header</extracomment>
      <translation>Comprobación de actualizaciones automática</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="160"/>
      <source>Update checks are performed at application start, if enabled.</source>
      <translation>La comprobación de actualizaciones se realizan al iniciar la aplicación, si está habilitado.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="167"/>
      <source>If enabled, check for application updates, and notify if new updates are available for installation.</source>
      <translation>Si está habilitado, comprueba si hay actualizaciones de la aplicación y notifica si hay nuevas actualizaciones disponibles para instalación.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="170"/>
      <source>Check for application updates</source>
      <translation>Comprobar actualizaciones de aplicación</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="180"/>
      <source>If enabled, query the Scryfall API if new cards are available. If so, offer to update the local card data.</source>
      <translation>Si está habilitado, consulta la API de Scryfall si hay nuevas cartas disponibles. Si es así, ofrecer actualizar los datos de cartas locales.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="183"/>
      <source>Check for new card data</source>
      <translation>Comprobar nuevos datos de carta</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="202"/>
      <source>Language choices will default to the chosen language here.
Entries use the language codes as listed on Scryfall.

Note: Cards in deck lists use the language as given by the deck list. To overwrite, use the deck list translation option.</source>
      <translation>Las opciones de idioma se establecerán por defecto en el idioma seleccionado aquí.
Las entradas utilizan los códigos de idioma que aparecen en Scryfall.

Nota: Las cartas de las listas de mazo utilizan el idioma indicado en la lista. Para sobrescribirlo, utiliza la opción de traducción de la lista de mazo.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="225"/>
      <source>Card language selected at application start and default language when enabling deck list translations</source>
      <translation>Idioma de la carta seleccionado al iniciar la aplicación e idioma predeterminado al habilitar las traducciones de la lista de mazos</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="228"/>
      <source>Preferred card language:</source>
      <translation>Idioma de carta preferido:</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="238"/>
      <source>Custom cards</source>
      <extracomment>Settings section header</extracomment>
      <translation>Cartas personalizadas</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="244"/>
      <source>Default search path</source>
      <extracomment>Label next to a directory selector for custom cards</extracomment>
      <translation>Ruta de búsqueda predeterminada</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="254"/>
      <source>If set, search here for custom card images</source>
      <extracomment>Tooltip text</extracomment>
      <translation>Si se establece, buscar aquí imágenes de cartas personalizadas</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="283"/>
      <source>Enforce rounded corners for all imported custom cards</source>
      <extracomment>Tooltip text</extracomment>
      <translation type="unfinished">Enforce rounded corners for all imported custom cards</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/general_settings_page.ui" line="286"/>
      <source>Force round corners</source>
      <extracomment>Custom card import related on/off setting.</extracomment>
      <translation type="unfinished">Force round corners</translation>
    </message>
  </context>
  <context>
    <name>GroupedCentralWidget</name>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="20"/>
      <source>Add new cards:</source>
      <translation type="unfinished">Add new cards:</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="62"/>
      <source>All pages:</source>
      <translation>Todas las páginas:</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="72"/>
      <source>Move down</source>
      <translation>Mover abajo</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="85"/>
      <source>Move up</source>
      <translation>Mover arriba</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/grouped.ui" line="98"/>
      <source>Remove selected</source>
      <translation>Eliminar selección</translation>
    </message>
  </context>
  <context>
    <name>HidePrintingsPage</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="458"/>
      <source>Hide printings</source>
      <translation>Ocultar impresiones</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="458"/>
      <source>Hide unwanted printings</source>
      <translation type="unfinished">Hide unwanted printings</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/hide_printings_page.ui" line="17"/>
      <source>These options allow hiding unwanted cards and printings. Hidden printings are treated as though they don’t exist. They can’t be found in the card search and are automatically replaced in loaded documents or imported deck lists, if possible. If all printings of a card are hidden, it won’t be available at all.</source>
      <translation>Estas opciones permiten ocultar cartas e impresiones no deseadas. Las impresiones ocultas se tratan como si no existieran. No se pueden encontrar en la búsqueda de cartas y se reemplazan automáticamente en documentos cargados o listas de mazos importados, si es posible. Si todas las impresiones de una tarjeta están ocultas, no estarán disponibles.</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/hide_printings_page.ui" line="33"/>
      <source>Hide specific sets: Add set codes as listed on Scryfall, for example LEA or 2X2. Separate multiple entries with spaces or line breaks. All words not matching an exact set code are ignored.</source>
      <translation>Ocultar Sets específicos: Añadir códigos de Sets como se indica en Scryfall, por ejemplo LEA o 2X2. Separe múltiples entradas con espacios o saltos de línea. Todas las palabras que no coincidan con un código exacto son ignoradas.</translation>
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
      <translation>No hay conjuntos ocultos.</translation>
    </message>
  </context>
  <context>
    <name>HorizontalAddCardWidget</name>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="35"/>
      <source>Language:</source>
      <extracomment>Card language. Next to the language selection widget</extracomment>
      <translation>Idioma:</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="51"/>
      <source>Card Name</source>
      <translation>Nombre de carta</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="57"/>
      <source>Filter the list below. Use  % (Percent signs) as wildcards matching any number of characters.</source>
      <translation type="unfinished">Filter the list below. Use  % (Percent signs) as wildcards matching any number of characters.</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="60"/>
      <source>Filter card names</source>
      <translation>Filtro de nombres de carta</translation>
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
      <translation>Set</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="104"/>
      <source>Filter set names</source>
      <translation>Filtro de nombres</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="136"/>
      <source>Collector Number</source>
      <translation>Número de coleccionista</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/horizontal.ui" line="164"/>
      <source>Copies:</source>
      <extracomment>Number of copies to add. Next to the number input field</extracomment>
      <translation>Copias:</translation>
    </message>
  </context>
  <context>
    <name>ImageDownloadTask</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/image_downloader.py" line="135"/>
      <source>Downloading &apos;{card_name}&apos;:</source>
      <comment>Progress bar label text</comment>
      <translation type="unfinished">Downloading &apos;{card_name}&apos;:</translation>
    </message>
  </context>
  <context>
    <name>KnownCardImageModel</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="139"/>
      <source>Name</source>
      <comment>Table header. Card name</comment>
      <translation type="unfinished">Name</translation>
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
      <translation>Coleccionista #</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="145"/>
      <source>Is Hidden</source>
      <comment>Table header. Shows if this printing is hidden by a card filter</comment>
      <translation type="unfinished">Is Hidden</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="147"/>
      <source>Front/Back</source>
      <comment>Table header. Shows if this is the front or back side of a card</comment>
      <translation type="unfinished">Front/Back</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="149"/>
      <source>High resolution?</source>
      <comment>Table header. Shows if the card has high-res images</comment>
      <translation type="unfinished">High resolution?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="151"/>
      <source>Size</source>
      <comment>Table header. File size in KiB/MiB</comment>
      <translation type="unfinished">Size</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="153"/>
      <source>Scryfall ID</source>
      <comment>Table header. Shows UUID identifying this card in the Scryfall database</comment>
      <translation type="unfinished">Scryfall ID</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="155"/>
      <source>Path</source>
      <comment>Table header. File system path</comment>
      <translation type="unfinished">Path</translation>
    </message>
  </context>
  <context>
    <name>KnownCardRow</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="99"/>
      <source>Yes</source>
      <comment>This card is hidden by a card filter</comment>
      <translation>Sí</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="101"/>
      <source>No</source>
      <comment>This card is visible and not affected by a card filter</comment>
      <translation>No</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="104"/>
      <source>This printing is hidden by an enabled card filter
and is thus unavailable for printing.</source>
      <comment>Tooltip for cells with hidden cards</comment>
      <translation type="unfinished">This printing is hidden by an enabled card filter
and is thus unavailable for printing.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="109"/>
      <source>Front</source>
      <comment>Card side</comment>
      <translation>Frente</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="109"/>
      <source>Back</source>
      <comment>Card side</comment>
      <translation>Reverso</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="115"/>
      <source>Yes</source>
      <comment>This card has high-resolution images available</comment>
      <translation>Sí</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="117"/>
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
      <translation type="unfinished">Load MTGProxyPrinter document</translation>
    </message>
  </context>
  <context>
    <name>LoadListPage</name>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="17"/>
      <source>Import a deck list for printing</source>
      <translation>Importar una lista de mazo para imprimir</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="20"/>
      <source>Load a deck file from disk or paste deck list in the text field below</source>
      <translation>Cargar un archivo de mazo desde el disco o pegar lista de mazo en el campo de texto de abajo</translation>
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
      <extracomment>Download the entered Scryfall search query as a deck list</extracomment>
      <translation>Descargar el resultado</translation>
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
      <extracomment>Lets the user select a file, and loads the content as a deck list</extracomment>
      <translation>Seleccionar archivo de lista de mazo</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="152"/>
      <source>View result</source>
      <extracomment>View the entered Scryfall search query on the Scryfall website</extracomment>
      <translation>Ver resultados</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/load_list_page.ui" line="171"/>
      <source>Download deck list</source>
      <extracomment>On pressing the button, the deck list given by the entered URL is downloaded</extracomment>
      <translation type="unfinished">Download deck list</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="118"/>
      <source>Supported websites:
{supported_sites}</source>
      <comment>Tooltip text</comment>
      <translation type="unfinished">Supported websites:
{supported_sites}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="169"/>
      <source>Overwrite existing deck list?</source>
      <comment>Message box title</comment>
      <translation type="unfinished">Overwrite existing deck list?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="170"/>
      <source>Selecting a file will overwrite the existing deck list. Continue?</source>
      <comment>Message box body text</comment>
      <translation type="unfinished">Selecting a file will overwrite the existing deck list. Continue?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="176"/>
      <source>Select deck file</source>
      <comment>File selection dialog window title</comment>
      <translation>Seleccionar archivo de lista de mazo</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="186"/>
      <source>All files (*)</source>
      <comment>File type filter value</comment>
      <translation>Todos los archivos (*)</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="198"/>
      <source>All Supported </source>
      <comment>File type filter value</comment>
      <translation type="unfinished">All Supported </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="209"/>
      <source>Verify that the URL is valid, reachable, and that the deck list is set to public.
This program cannot download private deck lists. Please note, that setting deck lists to
public may take a minute or two to apply.</source>
      <comment>Error message shown when trying to download a deck list from a seemingly valid URL fails</comment>
      <translation type="unfinished">Verify that the URL is valid, reachable, and that the deck list is set to public.
This program cannot download private deck lists. Please note, that setting deck lists to
public may take a minute or two to apply.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="219"/>
      <source>Overwrite existing deck list?</source>
      <comment>Message box title. Shown when loading a deck list would overwrite existing text</comment>
      <translation type="unfinished">Overwrite existing deck list?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="222"/>
      <source>Downloading a deck list will overwrite the existing deck list. Continue?</source>
      <comment>Message box body text. Shown when loading a deck list would overwrite existing text</comment>
      <translation type="unfinished">Downloading a deck list will overwrite the existing deck list. Continue?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="234"/>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="242"/>
      <source>Deck list download failed</source>
      <comment>Message box title. Shown when downloading failed</comment>
      <translation type="unfinished">Deck list download failed</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="236"/>
      <source>Download failed with HTTP error {http_error_code}.

{bad_request_msg}</source>
      <comment>Message box body text. Shown when the server returns an error code</comment>
      <translation type="unfinished">Download failed with HTTP error {http_error_code}.

{bad_request_msg}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="243"/>
      <source>Download failed.

Check your internet connection, verify that the URL is valid, reachable, and that the deck list is set to public. This program cannot download private deck lists. If this persists, please report a bug in the issue tracker on the homepage.</source>
      <comment>Message box body text. Shown when an unknown error occurred.</comment>
      <translation type="unfinished">Download failed.

Check your internet connection, verify that the URL is valid, reachable, and that the deck list is set to public. This program cannot download private deck lists. If this persists, please report a bug in the issue tracker on the homepage.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="265"/>
      <source>Invalid Scryfall query entered, no result obtained</source>
      <comment>Message box body text</comment>
      <translation type="unfinished">Invalid Scryfall query entered, no result obtained</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="276"/>
      <source>Unable to read file content</source>
      <comment>Message box title. Shown when the user-selected file is unreadable.</comment>
      <translation type="unfinished">Unable to read file content</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="279"/>
      <source>Unable to read the content of file {file_path} as plain text.
Failed to load the content.</source>
      <comment>Message box body text. Shown when the user-selected file is unreadable.</comment>
      <translation type="unfinished">Unable to read the content of file {file_path} as plain text.
Failed to load the content.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="292"/>
      <source>Load large file?</source>
      <comment>Message box title. Shown when the user-selected file is unreasonably large.</comment>
      <translation type="unfinished">Load large file?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="295"/>
      <source>The selected file {file_path} is unexpectedly large ({formatted_size}). Load anyways?</source>
      <comment>Message box body text. Shown when the user-selected file is unreasonably large.</comment>
      <translation type="unfinished">The selected file {file_path} is unexpectedly large ({formatted_size}). Load anyways?</translation>
    </message>
  </context>
  <context>
    <name>LoadSaveDialog</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="185"/>
      <source>MTGProxyPrinter document (*.{default_save_suffix})</source>
      <comment>File type filter</comment>
      <translation type="unfinished">MTGProxyPrinter document (*.{default_save_suffix})</translation>
    </message>
  </context>
  <context>
    <name>MTGArenaParser</name>
    <message>
      <location filename="../../mtg_proxy_printer/decklist_parser/re_parsers.py" line="202"/>
      <source>Magic Arena deck file</source>
      <translation type="unfinished">Magic Arena deck file</translation>
    </message>
  </context>
  <context>
    <name>MTGOnlineParser</name>
    <message>
      <location filename="../../mtg_proxy_printer/decklist_parser/re_parsers.py" line="236"/>
      <source>Magic Online (MTGO) deck file</source>
      <translation type="unfinished">Magic Online (MTGO) deck file</translation>
    </message>
  </context>
  <context>
    <name>MagicWorkstationDeckDataFormatParser</name>
    <message>
      <location filename="../../mtg_proxy_printer/decklist_parser/re_parsers.py" line="179"/>
      <source>Magic Workstation Deck Data Format</source>
      <translation>Datos de mazo de Magic Workstation (mwDeck)</translation>
    </message>
  </context>
  <context>
    <name>MainWindow</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="227"/>
      <source>Undo:
{top_entry}</source>
      <translation type="unfinished">Undo:
{top_entry}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="229"/>
      <source>Redo:
{top_entry}</source>
      <translation type="unfinished">Redo:
{top_entry}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="282"/>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="296"/>
      <source>printing</source>
      <comment>This is passed as the {action} when asking the user about compacting the document if that can save pages</comment>
      <translation type="unfinished">printing</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="308"/>
      <source>exporting as a PDF</source>
      <comment>This is passed as the {action} when asking the user about compacting the document if that can save pages</comment>
      <translation type="unfinished">exporting as a PDF</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="321"/>
      <source>exporting as a PNG image sequence</source>
      <comment>This is passed as the {action} when asking the user about compacting the document if that can save pages</comment>
      <translation type="unfinished">exporting as a PNG image sequence</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="346"/>
      <source>Network error</source>
      <translation>Error de red</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="347"/>
      <source>Operation failed, because a network error occurred.
Check your internet connection. Reported error message:

{message}</source>
      <translation type="unfinished">Operation failed, because a network error occurred.
Check your internet connection. Reported error message:

{message}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="354"/>
      <source>Error</source>
      <translation type="unfinished">Error</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="355"/>
      <source>Operation failed, because an internal error occurred.
Reported error message:

{message}</source>
      <translation type="unfinished">Operation failed, because an internal error occurred.
Reported error message:

{message}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="362"/>
      <source>Saving pages possible</source>
      <translation>Guardando páginas posibles</translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="363"/>
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
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="378"/>
      <source>Download required Card data from Scryfall?</source>
      <translation type="unfinished">Download required Card data from Scryfall?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="380"/>
      <source>This program requires downloading additional card data from Scryfall to operate the card search.
Download the required data from Scryfall now?
Without the data, you can only print custom cards by drag&amp;dropping the image files onto the main window.</source>
      <translation type="unfinished">This program requires downloading additional card data from Scryfall to operate the card search.
Download the required data from Scryfall now?
Without the data, you can only print custom cards by drag&amp;dropping the image files onto the main window.</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="427"/>
      <source>Document loading failed</source>
      <translation type="unfinished">Document loading failed</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="428"/>
      <source>Loading file &quot;{failed_path}&quot; failed. The file was not recognized as a {program_name} document. If you want to load a deck list, use the &quot;{function_text}&quot; function instead.
Reported failure reason: {reason}</source>
      <translation type="unfinished">Loading file &quot;{failed_path}&quot; failed. The file was not recognized as a {program_name} document. If you want to load a deck list, use the &quot;{function_text}&quot; function instead.
Reported failure reason: {reason}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="440"/>
      <source>Unavailable printings replaced</source>
      <translation type="unfinished">Unavailable printings replaced</translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="442"/>
      <source>The document contained %n unavailable printings of cards that were automatically replaced with other printings. The replaced printings are unavailable, because they match a configured card filter.</source>
      <translation type="unfinished">
        <numerusform>The document contained %n unavailable printings of cards that were automatically replaced with other printings. The replaced printings are unavailable, because they match a configured card filter.</numerusform>
        <numerusform>The document contained %n unavailable printings of cards that were automatically replaced with other printings. The replaced printings are unavailable, because they match a configured card filter.</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="449"/>
      <source>Unrecognized cards in loaded document found</source>
      <translation type="unfinished">Unrecognized cards in loaded document found</translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="451"/>
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
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="459"/>
      <source>Application update available. Visit website?</source>
      <translation type="unfinished">Application update available. Visit website?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="460"/>
      <source>An application update is available: Version {newer_version}
You are currently using version {current_version}.

Open the {program_name} website in your web browser to download the new version?</source>
      <translation type="unfinished">An application update is available: Version {newer_version}
You are currently using version {current_version}.

Open the {program_name} website in your web browser to download the new version?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="474"/>
      <source>New card data available</source>
      <translation>Nuevos datos de cartas disponibles</translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="476"/>
      <source>There are %n new printings available on Scryfall. Update the local data now?</source>
      <translation type="unfinished">
        <numerusform>There are %n new printings available on Scryfall. Update the local data now?</numerusform>
        <numerusform>There are %n new printings available on Scryfall. Update the local data now?</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="490"/>
      <source>Check for application updates?</source>
      <translation>¿Comprobar actualizaciones de aplicación?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="492"/>
      <source>Automatically check for application updates whenever you start {program_name}?</source>
      <translation type="unfinished">Automatically check for application updates whenever you start {program_name}?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="502"/>
      <source>Check for card data updates?</source>
      <translation type="unfinished">Check for card data updates?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="504"/>
      <source>Automatically check for card data updates on Scryfall whenever you start {program_name}?</source>
      <translation type="unfinished">Automatically check for card data updates on Scryfall whenever you start {program_name}?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/main_window.py" line="513"/>
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
      <location filename="../ui/main_window.ui" line="35"/>
      <source>Export</source>
      <translation>Exportar</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="59"/>
      <source>Application</source>
      <translation>Aplicación</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="73"/>
      <source>Edit</source>
      <translation>Editar</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="89"/>
      <source>Web links</source>
      <translation>Enlaces</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="106"/>
      <location filename="../ui/main_window.ui" line="327"/>
      <source>Show toolbar</source>
      <translation>Mostrar barra de herramientas</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="135"/>
      <source>&amp;Quit</source>
      <translation>Cerrar</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="138"/>
      <source>Ctrl+Q</source>
      <translation type="unfinished">Ctrl+Q</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="149"/>
      <source>&amp;Print</source>
      <translation>Imprimir</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="152"/>
      <source>Print the current document</source>
      <translation>Configurar el documento actual</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="155"/>
      <source>Ctrl+P</source>
      <translation type="unfinished">Ctrl+P</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="163"/>
      <source>&amp;Show print preview</source>
      <translation>Mostrar vista previa de impresión</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="166"/>
      <source>Show print preview window</source>
      <translation type="unfinished">Show print preview window</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="174"/>
      <source>&amp;Create PDF</source>
      <translation>Crear PDF</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="177"/>
      <source>Create a PDF document</source>
      <translation type="unfinished">Create a PDF document</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="185"/>
      <source>Discard page</source>
      <translation>Descartar página</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="188"/>
      <source>Discard this page.</source>
      <translation>Descartar página.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="196"/>
      <source>Settings</source>
      <translation>Ajustes</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="207"/>
      <source>Update card data</source>
      <translation>Actualizar datos de carta</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="215"/>
      <source>New Page</source>
      <translation>Nueva página</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="218"/>
      <source>Add a new, empty page.</source>
      <translation type="unfinished">Add a new, empty page.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="226"/>
      <source>Save</source>
      <translation>Guardar</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="229"/>
      <source>Ctrl+S</source>
      <translation type="unfinished">Ctrl+S</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="237"/>
      <source>New</source>
      <translation>Nuevo</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="240"/>
      <source>Ctrl+N</source>
      <translation type="unfinished">Ctrl+N</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="248"/>
      <source>Load</source>
      <translation>Cargar</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="251"/>
      <source>Ctrl+L</source>
      <translation type="unfinished">Ctrl+L</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="259"/>
      <source>Save as …</source>
      <translation>Guardar como …</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="264"/>
      <source>About …</source>
      <translation>Acerca de</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="272"/>
      <source>Show Changelog</source>
      <translation>Ver lista de cambios</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="280"/>
      <source>Compact document</source>
      <translation>Documento compacto</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="283"/>
      <source>Minimize page count: Fill empty slots on pages by moving cards from the end of the document</source>
      <translation type="unfinished">Minimize page count: Fill empty slots on pages by moving cards from the end of the document</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="291"/>
      <source>Edit document settings</source>
      <translation>Editar configuración del documento</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="294"/>
      <source>Configure page size, margins, image spacings for the currently edited document.</source>
      <translation type="unfinished">Configure page size, margins, image spacings for the currently edited document.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="302"/>
      <source>Import deck list</source>
      <translation>Importar lista de mazo</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="305"/>
      <source>Import a deck list from online sources</source>
      <translation type="unfinished">Import a deck list from online sources</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="313"/>
      <source>Cleanup card images</source>
      <translation>Limpiar imágenes de carta</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="316"/>
      <source>Delete locally stored card images you no longer need.</source>
      <translation type="unfinished">Delete locally stored card images you no longer need.</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="330"/>
      <source>Ctrl+M</source>
      <translation type="unfinished">Ctrl+M</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="338"/>
      <source>Download missing card images</source>
      <translation>Descargar imágenes de cartas faltantes</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="346"/>
      <source>Shuffle document</source>
      <translation>Mezclar documento</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="349"/>
      <source>Randomly rearrange all card image.
If you want to quickly print a full deck for playing,
use this to reduce the initial deck shuffling required</source>
      <translation type="unfinished">Randomly rearrange all card image.
If you want to quickly print a full deck for playing,
use this to reduce the initial deck shuffling required</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="362"/>
      <source>Undo</source>
      <translation>Deshacer</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="373"/>
      <source>Redo</source>
      <translation>Rehacer</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="381"/>
      <source>Add empty card to page</source>
      <translation>Añadir carta vacía a la página</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="384"/>
      <source>Add an empty spacer filling a card slot</source>
      <translation type="unfinished">Add an empty spacer filling a card slot</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="392"/>
      <source>Add custom cards</source>
      <translation>Añadir cartas personalizadas</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="400"/>
      <source>Export as image sequence</source>
      <translation>Exportar como secuencia de imágenes</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="403"/>
      <source>Export document as an image sequence</source>
      <translation type="unfinished">Export document as an image sequence</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="411"/>
      <source>Export individual card images</source>
      <translation>Exportar imágenes de cartas individuales</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="414"/>
      <source>Export all card images to a directory</source>
      <translation type="unfinished">Export all card images to a directory</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="422"/>
      <source>Source Code</source>
      <translation>Código fuente</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="430"/>
      <source>Source Code (GitHub)</source>
      <translation>Código fuente (GitHub)</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="438"/>
      <source>Contribute Translations</source>
      <translation>Contribuir con traducciones</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="443"/>
      <source>Support development on Ko-Fi</source>
      <translation>Apoyar el desarrollo en Ko-Fi</translation>
    </message>
    <message>
      <location filename="../ui/main_window.ui" line="451"/>
      <source>Project on PyPI</source>
      <translation>Proyecto en PyPI</translation>
    </message>
  </context>
  <context>
    <name>MissingImagesManager</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/missing_images_manager.py" line="64"/>
      <source>Unable to obtain %n missing card image(s).
These will be missing in exported or printed documents.</source>
      <comment>Warning message. A last attempt at trying to download images of cards with missing images failed.</comment>
      <translation type="unfinished">
        <numerusform>Unable to obtain %n missing card image(s).
These will be missing in exported or printed documents.</numerusform>
        <numerusform>Unable to obtain %n missing card image(s).
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
      <translation type="unfinished">Fetching missing images:</translation>
    </message>
  </context>
  <context>
    <name>PNGRenderer</name>
    <message>
      <location filename="../../mtg_proxy_printer/print.py" line="87"/>
      <source>Export as PNGs:</source>
      <comment>Progress bar label text</comment>
      <translation type="unfinished">Export as PNGs:</translation>
    </message>
  </context>
  <context>
    <name>PageCardTableView</name>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="113"/>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="133"/>
      <source>Add %n copies</source>
      <comment>Context menu action: Add additional card copies to the document</comment>
      <translation type="unfinished">
        <numerusform>Add %n copies</numerusform>
        <numerusform>Add %n copies</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="120"/>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="139"/>
      <source>Add copies …</source>
      <comment>Context menu action: Add additional card copies to the document. User will be asked for a number</comment>
      <translation type="unfinished">Add copies …</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="125"/>
      <source>Generate DFC check card</source>
      <translation type="unfinished">Generate DFC check card</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="152"/>
      <source>All related cards</source>
      <translation type="unfinished">All related cards</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="161"/>
      <source>Add copies</source>
      <translation type="unfinished">Add copies</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="162"/>
      <source>Add copies of {card_name}</source>
      <comment>Asks the user for a number. Does not need plural forms</comment>
      <translation type="unfinished">Add copies of {card_name}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="187"/>
      <source>Export image</source>
      <translation type="unfinished">Export image</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="203"/>
      <source>Save card image</source>
      <translation type="unfinished">Save card image</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_card_table_view.py" line="203"/>
      <source>Images (*.png *.bmp *.jpg)</source>
      <translation type="unfinished">Images (*.png *.bmp *.jpg)</translation>
    </message>
  </context>
  <context>
    <name>PageConfigPreviewArea</name>
    <message>
      <location filename="../ui/page_config_preview_area.ui" line="29"/>
      <location filename="../ui/page_config_preview_area.ui" line="36"/>
      <source> cards</source>
      <translation type="unfinished"> cards</translation>
    </message>
    <message>
      <location filename="../ui/page_config_preview_area.ui" line="43"/>
      <source>Regular</source>
      <translation>Normal</translation>
    </message>
    <message>
      <location filename="../ui/page_config_preview_area.ui" line="53"/>
      <source>Oversized</source>
      <translation>Ampliado</translation>
    </message>
  </context>
  <context>
    <name>PageConfigWidget</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="89"/>
      <source>Disabled</source>
      <comment>A cut marker style</comment>
      <translation type="unfinished">Disabled</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="90"/>
      <source>Solid lines</source>
      <comment>A cut marker style</comment>
      <translation type="unfinished">Solid lines</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="91"/>
      <source>Dashed lines</source>
      <comment>A cut marker style</comment>
      <translation type="unfinished">Dashed lines</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="92"/>
      <source>Dotted lines</source>
      <comment>A cut marker style</comment>
      <translation type="unfinished">Dotted lines</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="96"/>
      <source>Disabled</source>
      <comment>A print/cut registration marker style</comment>
      <translation type="unfinished">Disabled</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="97"/>
      <source>Bullseye</source>
      <comment>A print/cut registration marker style</comment>
      <translation type="unfinished">Bullseye</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="99"/>
      <source>Silhouette cutter (Cameo-compatible)</source>
      <comment>A print/cut registration marker style</comment>
      <translation type="unfinished">Silhouette cutter (Cameo-compatible)</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="205"/>
      <source>Select watermark text color</source>
      <translation type="unfinished">Select watermark text color</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="223"/>
      <source>Select cut marker color</source>
      <translation type="unfinished">Select cut marker color</translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="238"/>
      <source>%n regular card(s)</source>
      <comment>Display of the resulting page capacity for regular-sized cards</comment>
      <translation>
        <numerusform>%n Carta normal</numerusform>
        <numerusform>%n Cartas normales</numerusform>
      </translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="242"/>
      <source>%n oversized card(s)</source>
      <comment>Display of the resulting page capacity for oversized cards</comment>
      <translation>
        <numerusform>%n Carta ampliada</numerusform>
        <numerusform>%n Cartas ampliadas</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_config_widget.py" line="247"/>
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
      <location filename="../ui/page_config_widget.ui" line="35"/>
      <source>Show Preview</source>
      <translation type="unfinished">Show Preview</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="53"/>
      <source>The document name is printed on each page and can help you keep track
of different printed sheets and to which deck they belong.

Leave empty to disable.</source>
      <translation type="unfinished">The document name is printed on each page and can help you keep track
of different printed sheets and to which deck they belong.

Leave empty to disable.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="62"/>
      <source>Document/deck name</source>
      <translation>Nombre del documento/mazo</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="72"/>
      <source>If enabled, the page number is printed on each page. Makes it easier to notice missing pages in a stack.</source>
      <translation type="unfinished">If enabled, the page number is printed on each page. Makes it easier to notice missing pages in a stack.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="75"/>
      <source>Print page numbers</source>
      <translation>Imprimir números de página</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="82"/>
      <source>Document name</source>
      <translation>Nombre del documento</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="92"/>
      <source>Draw 90° card corners, instead of round ones</source>
      <translation>Dibujar esquinas de cartas a 90°, en lugar de redondeadas</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="116"/>
      <source>Paper dimensions</source>
      <translation>Dimensiones de papel</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="122"/>
      <source>Draw an additional border around cards to ease cutting.</source>
      <translation type="unfinished">Draw an additional border around cards to ease cutting.</translation>
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
      <translation type="unfinished"> mm</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="135"/>
      <source>Bottom margin</source>
      <translation>Margen inferior</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="148"/>
      <source>Right margin</source>
      <translation>Margen derecho</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="161"/>
      <source>Top margin</source>
      <translation>Margen superior</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="183"/>
      <source>Paper width in millimeters.
Must match the size of the sheets in the printer.
Otherwise, scaling may be applied by the printer driver.</source>
      <translation type="unfinished">Paper width in millimeters.
Must match the size of the sheets in the printer.
Otherwise, scaling may be applied by the printer driver.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="207"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the right paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation type="unfinished">&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the right paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="223"/>
      <source>Left margin</source>
      <translation>Margen izquierdo</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="236"/>
      <source>Paper height</source>
      <translation>Altura del papel</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="249"/>
      <source>Card bleed</source>
      <translation>Sangría de carta</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="268"/>
      <source>Paper height in millimeters.
Must match the size of the sheets in the printer.
Otherwise, scaling may be applied by the printer driver.</source>
      <translation type="unfinished">Paper height in millimeters.
Must match the size of the sheets in the printer.
Otherwise, scaling may be applied by the printer driver.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="286"/>
      <source>Resulting page capacity:</source>
      <translation>Capacidad resultante de la página:</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="296"/>
      <source>Paper width</source>
      <translation>Ancho de papel</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="309"/>
      <source>Number of cards fitting on each page,
based on the page size and spacings configured</source>
      <translation type="unfinished">Number of cards fitting on each page,
based on the page size and spacings configured</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="326"/>
      <source>Switch between portrait and landscape mode</source>
      <translation type="unfinished">Switch between portrait and landscape mode</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="329"/>
      <source>Flip</source>
      <translation>Dar la vuelta</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="345"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the bottom paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation type="unfinished">&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the bottom paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="358"/>
      <source>Column spacing</source>
      <translation>Espaciado de columna</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="377"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the left paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation type="unfinished">&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the left paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="396"/>
      <source>Space between image rows in mm.
If set to zero, you only need one cut to separate two images,
otherwise you need two cuts but require less precision hitting the exact middle.</source>
      <translation type="unfinished">Space between image rows in mm.
If set to zero, you only need one cut to separate two images,
otherwise you need two cuts but require less precision hitting the exact middle.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="411"/>
      <source>Row spacing</source>
      <translation>Espaciado de fila</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="430"/>
      <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the top paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
      <translation type="unfinished">&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Minimum margin between the top paper border and the page content.&lt;/p&gt;&lt;p&gt;Most printers have a minimum printing margin of 3 to 5 mm.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="449"/>
      <source>Space between image columns in mm.
If set to zero, you only need one cut to separate two images,
otherwise you need two cuts but require less precision hitting the exact middle.</source>
      <translation type="unfinished">Space between image columns in mm.
If set to zero, you only need one cut to separate two images,
otherwise you need two cuts but require less precision hitting the exact middle.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="464"/>
      <source>Paper size</source>
      <translation>Tamaño del papel</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="475"/>
      <source>Cut markers</source>
      <translation>Marcadores de corte</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="484"/>
      <source>Draw cut helper lines above card images, instead of below them</source>
      <translation type="unfinished">Draw cut helper lines above card images, instead of below them</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="487"/>
      <source>Draw above cards</source>
      <translation>Dibujar sobre cartas</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="494"/>
      <source>The default width of 0 draws a thin line, regardless of zoom level.</source>
      <translation type="unfinished">The default width of 0 draws a thin line, regardless of zoom level.</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="510"/>
      <source>Cut helper lines</source>
      <translation>Líneas de ayuda de corte</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="520"/>
      <location filename="../ui/page_config_widget.ui" line="721"/>
      <source>Select a color</source>
      <translation>Seleccionar un color</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="543"/>
      <source>Line width</source>
      <translation>Ancho de la línea</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="566"/>
      <source>Color and opacity</source>
      <translation>Color y opacidad</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="595"/>
      <source>Print registration marks</source>
      <translation>Imprimir marcas de registro</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="606"/>
      <source>Watermark</source>
      <translation>Marca de agua</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="612"/>
      <source>X position</source>
      <translation>Posición X</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="622"/>
      <source>Y position</source>
      <translation>Posición Y</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="632"/>
      <source>Watermark text</source>
      <translation>Texto de marca de agua</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="655"/>
      <source>Rotation angle</source>
      <translation>Ángulo de rotación</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="681"/>
      <source>Font size</source>
      <translation>Tamaño de fuente</translation>
    </message>
    <message>
      <location filename="../ui/page_config_widget.ui" line="691"/>
      <source>Text color and opacity</source>
      <translation>Color de texto y opacidad</translation>
    </message>
  </context>
  <context>
    <name>PageRenderer</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/page_renderer.py" line="66"/>
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
      <location filename="../../mtg_proxy_printer/decklist_parser/common.py" line="71"/>
      <source>All files (*)</source>
      <comment>File type filter</comment>
      <translation type="unfinished">All files (*)</translation>
    </message>
  </context>
  <context>
    <name>PrettySetListModel</name>
    <message>
      <location filename="../../mtg_proxy_printer/model/string_list.py" line="36"/>
      <source>Set</source>
      <comment>MTG set name</comment>
      <translation type="unfinished">Set</translation>
    </message>
  </context>
  <context>
    <name>PrinterSettingsPage</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="519"/>
      <source>Printer settings</source>
      <translation>Configuración de la impresora</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window_pages.py" line="519"/>
      <source>Configure the printer</source>
      <translation type="unfinished">Configure the printer</translation>
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
      <translation>Activar vista horizontal: Rotar impresiones a 90°</translation>
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
      <translation>Configurar impresora para impresión sin bordes</translation>
    </message>
  </context>
  <context>
    <name>PrintingFilterUpdater.store_current_printing_filters()</name>
    <message>
      <location filename="../../mtg_proxy_printer/async_tasks/printing_filter_updater.py" line="89"/>
      <source>Processing updated card filters:</source>
      <translation type="unfinished">Processing updated card filters:</translation>
    </message>
  </context>
  <context>
    <name>ProgressBar</name>
    <message>
      <location filename="../ui/progress_bar.ui" line="36"/>
      <source>Cancel</source>
      <translation type="unfinished">Cancel</translation>
    </message>
  </context>
  <context>
    <name>SaveDocumentAsDialog</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="197"/>
      <source>Save document as …</source>
      <comment>File dialog window title</comment>
      <translation type="unfinished">Save document as …</translation>
    </message>
  </context>
  <context>
    <name>SavePDFDialog</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="96"/>
      <source>Export as PDF</source>
      <comment>File dialog window title</comment>
      <translation type="unfinished">Export as PDF</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="97"/>
      <source>PDF documents (*.pdf)</source>
      <comment>File type filter</comment>
      <translation type="unfinished">PDF documents (*.pdf)</translation>
    </message>
  </context>
  <context>
    <name>SavePNGDialog</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="141"/>
      <source>Export as PNG</source>
      <comment>File dialog window title</comment>
      <translation type="unfinished">Export as PNG</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/dialogs.py" line="142"/>
      <source>PNG images (*.png)</source>
      <comment>File type filter</comment>
      <translation type="unfinished">PNG images (*.png)</translation>
    </message>
  </context>
  <context>
    <name>ScryfallCSVParser</name>
    <message>
      <location filename="../../mtg_proxy_printer/decklist_parser/csv_parsers.py" line="117"/>
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
      <translation>Seleccione qué tipo de lista de mazo desea importar.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="26"/>
      <source>This is a Tappedout-specific section of the deck.
It may contain the deck list author’s buy-list or anything else.</source>
      <translation type="unfinished">This is a Tappedout-specific section of the deck.
It may contain the deck list author’s buy-list or anything else.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="30"/>
      <source>Include “Acquire-Board”</source>
      <translation type="unfinished">Include “Acquire-Board”</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="53"/>
      <source>A simple list, containing one card name per line</source>
      <translation type="unfinished">A simple list, containing one card name per line</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="56"/>
      <source>List with card names</source>
      <translation type="unfinished">List with card names</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="92"/>
      <source>CSV exports from Scryfall’s own deck builder.
Gives very accurate results, unless the imported deck list contains ignored items
matching an enabled card filter.</source>
      <translation type="unfinished">CSV exports from Scryfall’s own deck builder.
Gives very accurate results, unless the imported deck list contains ignored items
matching an enabled card filter.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="97"/>
      <source>Scryfall.com deck lists (CSV export)</source>
      <translation>Lista de mazo de ScryFall.com (CSV)</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="104"/>
      <source>Deck list files, stored in XMage’s native format.
Because XMage closely follows Scryfall regarding Magic sets,
this should give very accurate results.</source>
      <translation type="unfinished">Deck list files, stored in XMage’s native format.
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
      <translation type="unfinished">Specify a custom regular expression in the input field below. It will be used to parse each deck list line.
You can use the buttons below to insert basic building blocks.
You have to separate them with the “control structures”, like spaces, as used in your deck list.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="121"/>
      <source>Custom regular expression based parser:</source>
      <translation>Analizador personalizado basado en expresiones regulares:</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="128"/>
      <source>CSV exports can be downloaded from Tappedout by choosing the appropriate deck export option.</source>
      <translation type="unfinished">CSV exports can be downloaded from Tappedout by choosing the appropriate deck export option.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="131"/>
      <source>tappedout.net deck list (CSV export)</source>
      <translation>Lista de mazo de tappedout.net (CSV)</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="138"/>
      <source>The simplistic format used by Magic Online. It does not specify exact printings, so may not give the best results.</source>
      <translation type="unfinished">The simplistic format used by Magic Online. It does not specify exact printings, so may not give the best results.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="141"/>
      <source>Magic Online</source>
      <translation>Magic en línea</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="148"/>
      <source>Magic Workstation Deck Data (mwDeck)</source>
      <translation>Datos de mazo de Magic Workstation (mwDeck)</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="155"/>
      <source>Magic Arena and exports from compatible websites, like moxfield.com
Note that this option is not limited to cards in Standard/Historic,
as the format works for any card.</source>
      <translation type="unfinished">Magic Arena and exports from compatible websites, like moxfield.com
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
      <translation type="unfinished">This is a Tappedout-specific section of the deck.
It may contain cards that the deck list creator considers for inclusion, based on the meta
or any other preference, like card price.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="175"/>
      <source>Include “Maybe-Board”</source>
      <translation type="unfinished">Include “Maybe-Board”</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="200"/>
      <source>Appends a matcher for a card name to the input field above.</source>
      <translation type="unfinished">Appends a matcher for a card name to the input field above.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="203"/>
      <source>Card name matcher</source>
      <translation>Emparejar nombre de carta</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="213"/>
      <source>Appends a sample matcher for a collector number to the input field above</source>
      <translation type="unfinished">Appends a sample matcher for a collector number to the input field above</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="216"/>
      <source>Collector number matcher</source>
      <translation>Emparejar número de coleccionista</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="226"/>
      <source>Appends a matcher for the  card language to the input field above.
If a language field is not present in the deck list, the card language is guessed.</source>
      <translation type="unfinished">Appends a matcher for the  card language to the input field above.
If a language field is not present in the deck list, the card language is guessed.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="230"/>
      <source>Language matcher</source>
      <translation>Emparejar idioma</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="240"/>
      <source>Appends a sample matcher for a set code to the input field above.</source>
      <translation type="unfinished">Appends a sample matcher for a set code to the input field above.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="243"/>
      <source>Set code matcher</source>
      <translation>Emparejar código de Set</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="253"/>
      <source>Appends a matcher for the number of card copies to the input field above.
If a card count field is not present in the deck list, 1 card copy per line is assumed</source>
      <translation type="unfinished">Appends a matcher for the number of card copies to the input field above.
If a card count field is not present in the deck list, 1 card copy per line is assumed</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="257"/>
      <source>Copies matcher</source>
      <translation>Emparejar copias</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="267"/>
      <source>Appends a matcher for the Scryfall ID to the input field above.
This may be used by deck lists that closely integrate with the Scryfall website.
Most deck lists won’t use this.</source>
      <translation type="unfinished">Appends a matcher for the Scryfall ID to the input field above.
This may be used by deck lists that closely integrate with the Scryfall website.
Most deck lists won’t use this.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="272"/>
      <source>Scryfall ID matcher</source>
      <translation>Emparejar Scryfall ID</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/select_deck_parser_page.ui" line="282"/>
      <source>Enter a Regular Expression containing at least one supported, named group.

Supported named groups are: {group_names}

See the &apos;What’s this?&apos; (?-Button) help for details.</source>
      <translation type="unfinished">Enter a Regular Expression containing at least one supported, named group.

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
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="201"/>
      <source>Apply settings to the current document?</source>
      <translation>¿Aplicar ajustes al documento actual?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="202"/>
      <source>The new default settings differ from the settings used by the current document.
Apply the new settings to the current document?</source>
      <translation type="unfinished">The new default settings differ from the settings used by the current document.
Apply the new settings to the current document?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="215"/>
      <source>Reset unsaved changes?</source>
      <translation type="unfinished">Reset unsaved changes?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="216"/>
      <source>Reset unsaved changes on the current page or on all pages?</source>
      <translation type="unfinished">Reset unsaved changes on the current page or on all pages?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="219"/>
      <source>Reset everything</source>
      <translation type="unfinished">Reset everything</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="220"/>
      <source>Reset current page</source>
      <translation type="unfinished">Reset current page</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="251"/>
      <source>Restore defaults for the current page or everything?</source>
      <translation type="unfinished">Restore defaults for the current page or everything?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="252"/>
      <source>Restore the settings on the current page or on all pages to their default values?</source>
      <translation type="unfinished">Restore the settings on the current page or on all pages to their default values?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="255"/>
      <source>Restore everything</source>
      <translation type="unfinished">Restore everything</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/settings_window.py" line="256"/>
      <source>Restore current page</source>
      <translation type="unfinished">Restore current page</translation>
    </message>
    <message>
      <location filename="../ui/settings_window/settings_window.ui" line="17"/>
      <source>Settings</source>
      <translation>Ajustes</translation>
    </message>
  </context>
  <context>
    <name>SummaryPage</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="461"/>
      <source>Images about to be deleted: {count}</source>
      <translation type="unfinished">Images about to be deleted: {count}</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="462"/>
      <source>Disk space that will be freed: {disk_space_freed}</source>
      <translation type="unfinished">Disk space that will be freed: {disk_space_freed}</translation>
    </message>
    <message numerus="yes">
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="501"/>
      <source>Beware: The card list currently contains %n potentially oversized card(s).</source>
      <comment>Warning emitted, if at least 1 card has the oversized flag set. The Scryfall server *may* still return a regular-sized image, so not *all* printings marked as oversized are actually so when fetched.</comment>
      <translation type="unfinished">
        <numerusform>Beware: The card list currently contains %n potentially oversized card(s).</numerusform>
        <numerusform>Beware: The card list currently contains %n potentially oversized card(s).</numerusform>
      </translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="509"/>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="527"/>
      <source>Replace document content with the identified cards</source>
      <comment>Wizard Accept button tooltip, if replacing the document with the loaded list is enabled.</comment>
      <translation type="unfinished">Replace document content with the identified cards</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="515"/>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="533"/>
      <source>Append identified cards to the document</source>
      <comment>Wizard Accept button tooltip, if replacing the document with the loaded list is disabled.</comment>
      <translation type="unfinished">Append identified cards to the document</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="571"/>
      <source>Remove basic lands</source>
      <comment>Button text</comment>
      <translation type="unfinished">Remove basic lands</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="573"/>
      <source>Remove all basic lands in the deck list above</source>
      <comment>Button tooltip</comment>
      <translation type="unfinished">Remove all basic lands in the deck list above</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="579"/>
      <source>Remove selected</source>
      <comment>Button text. Clicking removes all selected cards in the table</comment>
      <translation type="unfinished">Remove selected</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/deck_import_wizard.py" line="581"/>
      <source>Remove all selected cards in the deck list above</source>
      <comment>Button tooltip</comment>
      <translation type="unfinished">Remove all selected cards in the deck list above</translation>
    </message>
    <message>
      <location filename="../ui/cache_cleanup_wizard/summary_page.ui" line="14"/>
      <source>Summary</source>
      <translation>Resumen</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="6"/>
      <source>Import a deck list for printing</source>
      <translation>Importar una lista de mazo para imprimir</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="9"/>
      <source>The cards shown in the table will be imported. Double-click the Set, Collector# or Language cells to change selected printings. The text field shows all lines from the input that were not identified as cards.</source>
      <translation type="unfinished">The cards shown in the table will be imported. Double-click the Set, Collector# or Language cells to change selected printings. The text field shows all lines from the input that were not identified as cards.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="15"/>
      <source>If checked, clear all cards in the current document, replacing everything with the list below.
If unchecked, append the cards found below to the document.</source>
      <translation type="unfinished">If checked, clear all cards in the current document, replacing everything with the list below.
If unchecked, append the cards found below to the document.</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="19"/>
      <source>Replace the current document content with the found cards</source>
      <translation>Reemplazar el contenido del documento actual con las cartas encontradas</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="29"/>
      <source>These cards were successfully identified:</source>
      <translation>Estas cartas fueron identificadas con éxito:</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="61"/>
      <source>These lines from the deck list were not identified as cards:</source>
      <translation>Estas líneas de la lista de mazo no fueron identificadas como cartas:</translation>
    </message>
    <message>
      <location filename="../ui/deck_import_wizard/parser_result_page.ui" line="83"/>
      <source>Nothing. All cards were successfully identified!</source>
      <translation>Nada. ¡Todas las cartas fueron identificadas con éxito!</translation>
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
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="54"/>
      <source>Move up</source>
      <translation type="unfinished">Move up</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="67"/>
      <source>Move down</source>
      <translation type="unfinished">Move down</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="88"/>
      <source>Add new cards</source>
      <translation type="unfinished">Add new cards</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="93"/>
      <source>Current page</source>
      <translation type="unfinished">Current page</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="145"/>
      <source>Remove selected</source>
      <translation type="unfinished">Remove selected</translation>
    </message>
    <message>
      <location filename="../ui/central_widget/tabbed_vertical.ui" line="156"/>
      <source>Preview</source>
      <translation type="unfinished">Preview</translation>
    </message>
  </context>
  <context>
    <name>TappedOutCSVParser</name>
    <message>
      <location filename="../../mtg_proxy_printer/decklist_parser/csv_parsers.py" line="196"/>
      <source>Tappedout CSV export</source>
      <translation type="unfinished">Tappedout CSV export</translation>
    </message>
  </context>
  <context>
    <name>UnknownCardImageModel</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="275"/>
      <source>Scryfall ID</source>
      <comment>Table header. Shows UUID identifying this card in the Scryfall database</comment>
      <translation type="unfinished">Scryfall ID</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="277"/>
      <source>Front/Back</source>
      <comment>Table header. Shows if this is the front or back side of a card</comment>
      <translation type="unfinished">Front/Back</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="279"/>
      <source>High resolution?</source>
      <comment>Table header. Shows if the card has high-res images</comment>
      <translation type="unfinished">High resolution?</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="281"/>
      <source>Size</source>
      <comment>Table header. File size in KiB/MiB</comment>
      <translation type="unfinished">Size</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="283"/>
      <source>Path</source>
      <comment>Table header. File system path</comment>
      <translation type="unfinished">Path</translation>
    </message>
  </context>
  <context>
    <name>UnknownCardRow</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="244"/>
      <source>Front</source>
      <comment>Magic card side</comment>
      <translation type="unfinished">Front</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="246"/>
      <source>Back</source>
      <comment>Magic card side</comment>
      <translation type="unfinished">Back</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="252"/>
      <source>Yes</source>
      <comment>Card has high-resolution images available</comment>
      <translation type="unfinished">Yes</translation>
    </message>
    <message>
      <location filename="../../mtg_proxy_printer/ui/cache_cleanup_wizard.py" line="254"/>
      <source>No</source>
      <comment>Card only has low-resolution images available</comment>
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
      <translation>Filtro de nombres</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="67"/>
      <source>Collector Number</source>
      <translation>Número de coleccionista</translation>
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
      <extracomment>Card language. Next to the language selection widget</extracomment>
      <translation>Idioma:</translation>
    </message>
    <message>
      <location filename="../ui/add_card_widget/vertical.ui" line="152"/>
      <source>Copies:</source>
      <extracomment>Number of copies to add. Next to the number input field</extracomment>
      <translation>Copias:</translation>
    </message>
  </context>
  <context>
    <name>XMageParser</name>
    <message>
      <location filename="../../mtg_proxy_printer/decklist_parser/re_parsers.py" line="258"/>
      <source>XMage Deck file</source>
      <translation type="unfinished">XMage Deck file</translation>
    </message>
  </context>
  <context>
    <name>export_pdf</name>
    <message>
      <location filename="../../mtg_proxy_printer/print.py" line="132"/>
      <source>Write PDF:</source>
      <comment>Progress label</comment>
      <translation type="unfinished">Write PDF:</translation>
    </message>
  </context>
  <context>
    <name>format_size</name>
    <message>
      <location filename="../../mtg_proxy_printer/ui/common.py" line="183"/>
      <source>{size} {unit}</source>
      <comment>A formatted file size in SI bytes</comment>
      <translation type="unfinished">{size} {unit}</translation>
    </message>
  </context>
</TS>
