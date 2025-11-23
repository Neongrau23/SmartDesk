# Dateipfad: src/smartdesk/localization.py
# (NEUE DATEI, ersetzt ui/locale.py)

"""
Zentrale Datei für alle Texte der Benutzeroberfläche (Internationalisierung).
Alle von Benutzern gesehenen Texte sollten hier definiert werden.
"""

# Diese Funktion wird von allen anderen Modulen importiert
def get_text(key: str, **kwargs) -> str:
    """
    Holt einen Textbaustein anhand seines Schlüssels und formatiert ihn.
    """
    text = TEXT.get(key, f"<{key} not found>")
    try:
        return text.format(**kwargs)
    except KeyError as e:
        print(f"[LOKALISIERUNGSFEHLER] Fehlender Platzhalter im Text '{key}': {e}")
        return text # Gib den unformatierten Text zurück

TEXT = {
    # --- Logo ---
    "LOGO_ASCII": r""" ___                _   ___         _   
/ __|_ __  __ _ _ _| |_|   \ ___ __| |__
\__ \ '  \/ _` | '_|  _| |) / -_|_-< / /
|___/_|_|_\__,_|_|  \__|___/\___/__/_\_\ """,

    # --- Hauptmenü (cli.py) ---
    "MAIN_MENU_SEPARATOR": "-----------------------------------------",
    "MAIN_MENU_SWITCH": "Desktop wechseln",
    "MAIN_MENU_CREATE": "Neuen Desktop erstellen",
    "MAIN_MENU_SETTINGS": "Einstellungen",
    "MAIN_MENU_EXIT": "Beenden",

    # --- Einstellungsmenü (cli.py) ---
    "SETTINGS_MENU_HEADER": "        --- Einstellungen ---        ",
    "SETTINGS_MENU_LIST": "Alle Desktops anzeigen",
    "SETTINGS_MENU_DELETE": "Desktop löschen",
    "SETTINGS_MENU_SAVE_ICONS": "Aktuelle Icon-Positionen speichern",
    "SETTINGS_MENU_RESTART": "Explorer manuell neu starten",
    "SETTINGS_MENU_BACK": "Zurück",

    # --- Allgemeine UI-Texte (cli.py) ---
    "PROMPT_CHOOSE": "\nBitte wählen: ",
    "PROMPT_CONTINUE": "\n--- Drücke Enter, um fortzufahren ---",
    "ERROR_INVALID_INPUT": "Ungültige Eingabe.",
    "EXIT_MESSAGE": "Auf Wiedersehen!",
    "STATUS_ACTIVE":   "AKTIV",
    "STATUS_INACTIVE": "     ",
    "INFO_NO_DESKTOPS": "Keine Desktops vorhanden.",
    "PROMPT_WHICH_DESKTOP_DELETE": "\n--- Welchen Desktop löschen? ---",
    "PROMPT_CHOOSE_NUMBER": "\nNummer eingeben: ",
    "PROMPT_CANCEL": "0. Abbrechen",
    "ERROR_INVALID_NUMBER": "Bitte eine gültige Zahl eingeben.",
    "PROMPT_DELETE_FOLDER_CONFIRM": "Soll der Ordner '{path}' auch physisch gelöscht werden? (y/n): ",
    "INFO_DELETE_HEADING": "\n--- Desktop löschen ---",
    "INFO_NO_DESKTOPS_CREATE_FIRST": "Keine Desktops vorhanden. Bitte erstelle zuerst einen.",
    "PROMPT_WHICH_DESKTOP_SWITCH": "\n--- Zu welchem Desktop wechseln? ---",
    "INFO_REGISTRY_SET_SUCCESS": "Registry erfolgreich auf '{name}' gesetzt.",
    "INFO_RESTARTING_EXPLORER": "Starte Explorer neu, um Änderungen anzuwenden...",
    "INFO_WAITING_FOR_EXPLORER": "Explorer wurde neu gestartet. Warte 3 Sekunden auf Initialisierung...",
    "INFO_SYNCING_ICONS": "Synchronisiere Status und stelle Icons wieder her...",
    "SWITCH_SUCCESS": "Wechsel zu '{name}' abgeschlossen.",
    "INFO_CREATE_HEADING": "\n--- Neuen Desktop anlegen ---",
    "PROMPT_DESKTOP_NAME": "Name des neuen Desktops: ",
    "ERROR_NAME_EMPTY": "Fehler: Der Name darf nicht leer sein.",
    "PROMPT_FOLDER_MODE": "\nWie soll der Ordner gewählt werden?",
    "PROMPT_FOLDER_MODE_1": "1. Einen existierenden Ordner verwenden",
    "PROMPT_FOLDER_MODE_2": "2. Einen neuen Ordner erstellen",
    "PROMPT_CHOOSE_1_OR_2": "Auswahl (1/2): ",
    "PROMPT_EXISTING_PATH": r"Bitte vollen Pfad eingeben (z.B. F:\SmartDesk\Work): ",
    "PROMPT_NEW_PATH_PARENT": r"In welchem Verzeichnis soll der Ordner erstellt werden? (z.B. F:\SmartDesk): ",
    "INFO_NEW_PATH_LOCATION": "Der neue Desktop wird hier erstellt: {path}",
    "ERROR_BASE_DIR_EMPTY": "Fehler: Basis-Verzeichnis darf nicht leer sein.",
    "ERROR_INVALID_CHOICE": "Ungültige Auswahl.",
    "INFO_ABORTED_NO_PATH": "Vorgang abgebrochen (kein Pfad angegeben).",

    # --- desktop_handler.py (DH_*) ---
    "DH_ERROR_PATH_INVALID": "✗ Fehler: Pfad '{path}' ist ungültig oder konnte nicht erstellt werden.",
    "DH_ERROR_NAME_EXISTS": "✗ Fehler: Ein Desktop mit dem Namen '{name}' existiert bereits.",
    "DH_SUCCESS_CREATE": "✓ Desktop '{name}' erfolgreich angelegt.",
    "DH_ERROR_NOT_FOUND": "✗ Fehler: Desktop '{old_name}' nicht gefunden.",
    "DH_ERROR_NEW_NAME_EXISTS": "✗ Fehler: Der Name '{new_name}' ist bereits vergeben.",
    "DH_WARN_TARGET_PATH_EXISTS": "Warnung: Zielpfad '{path}' existiert bereits. Versuche Inhalt zu integrieren...",
    "DH_INFO_FOLDER_MOVED": "Ordner physisch verschoben von '{old_path}' nach '{new_path}'.",
    "DH_ERROR_FOLDER_MOVE": "✗ Fehler beim Verschieben des Ordners: {e}",
    "DH_ERROR_NEW_PATH_CREATE": "✗ Fehler: Neuer Pfad '{path}' konnte nicht erstellt werden.",
    "DH_SUCCESS_UPDATE": "✓ Desktop '{old_name}' wurde aktualisiert zu '{new_name}'.",
    "DH_ERROR_NOT_FOUND_DELETE": "✗ Fehler: Desktop '{name}' existiert nicht",
    "DH_PROMPT_DELETE_CONFIRM": "Desktop '{name}' wirklich löschen? (y/n): ",
    "DH_INFO_DELETE_ABORTED": "Löschvorgang abgebrochen.",
    "DH_ERROR_DELETE_ACTIVE": "✗ Fehler: Desktop '{name}' ist aktiv. Bitte wechseln Sie vorher den Desktop.",
    "DH_ERROR_DELETE_CRITICAL": "✗ KRITISCHER FEHLER: Windows Registry meldet, dass '{path}' der aktive Desktop ist!",
    "DH_INFO_DELETE_DENIED": "Löschen verweigert, um Datenverlust zu verhindern.",
    "DH_SUCCESS_FOLDER_DELETE": "✓ Ordner '{path}' wurde physisch gelöscht.",
    "DH_ERROR_FOLDER_DELETE": "✗ Fehler beim Löschen des Ordners: {e}",
    "DH_INFO_FOLDER_NOT_FOUND": "Hinweis: Ordner '{path}' existierte nicht mehr.",
    "DH_SUCCESS_DELETE": "✓ Desktop '{name}' erfolgreich gelöscht",
    "DH_WARN_SYNC_FAILED": "Warnung: Konnte Status nicht mit Registry synchronisieren: {e}",
    "DH_ERROR_SWITCH_NOT_FOUND": "✗ Fehler: Desktop '{name}' nicht gefunden.",
    "DH_WARN_PATH_NOT_FOUND": "✗ WARNUNG: Der Pfad für Desktop '{name}' existiert nicht mehr:",
    "DH_INFO_PATH_IS": "  -> {path}",
    "DH_PROMPT_PATH_NOT_FOUND_TITLE": "\nWas möchten Sie tun?",
    "DH_PROMPT_PATH_RECREATE": "  [1] Den Ordner neu erstellen und den Wechsel fortsetzen.",
    "DH_PROMPT_PATH_REMOVE": "  [2] Den Desktop aus der Konfiguration entfernen.",
    "DH_PROMPT_PATH_ABORT": "  [j] Jegliche andere Eingabe bricht den Vorgang ab.",
    "DH_PROMPT_YOUR_CHOICE": "Ihre Wahl: ",
    "DH_INFO_RECREATING_FOLDER": "Erstelle Ordner neu: {path}...",
    "DH_SUCCESS_RECREATING_FOLDER": "✓ Ordner erfolgreich erstellt. Wechsel wird fortgesetzt.",
    "DH_ERROR_RECREATING_FOLDER": "✗ FEHLER: Der Ordner konnte nicht neu erstellt werden.",
    "DH_INFO_ABORTING_SWITCH": "Wechsel wird abgebrochen.",
    "DH_INFO_REMOVING_CONFIG": "Entferne '{name}' aus der Konfiguration...",
    "DH_SUCCESS_REMOVING_CONFIG": "✓ Desktop '{name}' wurde entfernt.",
    "DH_ERROR_REMOVING_CONFIG": "✗ FEHLER beim Entfernen des Desktops: {e}",
    "DH_INFO_ALREADY_ACTIVE": "'{name}' ist bereits aktiv.",
    "DH_INFO_SAVING_ICONS": "Speichere Icon-Positionen für '{name}'...",
    "DH_SUCCESS_DB_UPDATE": "Datenbank (Icon-Speicherung) aktualisiert.",
    "DH_WARN_NO_ACTIVE_DESKTOP": "Warnung: Es wurde kein als 'aktiv' markierter Desktop gefunden. Überspringe Speichern der Icons.",
    "DH_INFO_SWITCHING_REGISTRY": "Wechsle Registry zu Desktop: {name} ({path})...",
    "DH_ERROR_REGISTRY_UPDATE_FAILED": "✗ FEHLER: Konnte Registry nicht aktualisieren. Wechsel wird abgebrochen.",
    "DH_INFO_REGISTRY_SUCCESS": "Registry-Änderung erfolgreich. Neustart des Explorers erforderlich.",
    "DH_INFO_SYNC_AFTER_RESTART": "Synchronisiere Status nach Neustart...",
    "DH_ERROR_SYNC_NO_ACTIVE": "✗ FEHLER: Konnte nach Neustart keinen aktiven Desktop in der DB finden.",
    "DH_ERROR_SYNC_PATH_NOT_REGISTERED": "Möglicherweise ist der Registry-Pfad in der desktops.json nicht registriert.",
    "DH_INFO_SYNC_PATH_FOUND": "Registry-Pfad '{path}' gefunden.",
    "DH_INFO_SYNC_DESKTOP_ACTIVE": "Desktop '{name}' ist jetzt aktiv.",
    "DH_INFO_SYNC_RESTORING_ICONS": "Stelle Icon-Positionen für '{name}' wieder her...",
    "DH_INFO_SYNC_ICONS_DONE": "Icon-Wiederherstellung abgeschlossen.",
    "DH_ERROR_SAVE_ICONS_NO_ACTIVE": "✗ Fehler: Konnte keinen aktiven Desktop finden.",
    "DH_ERROR_SAVE_ICONS_NOT_REGISTERED": "Möglicherweise ist der in Windows eingestellte Pfad\nin SmartDesk nicht registriert.",
    "DH_INFO_READING_ICONS": "Lese aktuelle Icon-Positionen für '{name}'...",
    "DH_SUCCESS_SAVE_ICONS": "✓ Icon-Positionen für '{name}' erfolgreich gespeichert.",
    "DH_ERROR_SAVE_ICONS": "✗ Fehler beim Speichern der Icons: {e}",

    # --- main.py (MAIN_*) ---
    "MAIN_ERROR_IMPORT": "Import Fehler: {e}",
    "MAIN_ERROR_IMPORT_HINT_1": "Stelle sicher, dass du das Skript aus dem Projekt-Root ausführst",
    "MAIN_ERROR_IMPORT_HINT_2": "oder dass das Paket korrekt installiert ist.",
    "MAIN_WARN_HANDLER_LOAD_FAILED": "Warnung: {handler} konnte nicht geladen werden.",
    "MAIN_ERROR_HANDLER_CALL_FAILED": "FEHLER: {name} konnte nicht geladen werden!",
    "MAIN_INFO_STARTING_INTERACTIVE": "Starte interaktives Menü...",
    "MAIN_ERROR_NAME_MISSING": "Fehler: Desktop-Name fehlt.",
    "MAIN_USAGE_DELETE": "Verwendung: python -m smartdesk.main delete <desktop-name> [--delete-folder]",
    "MAIN_USAGE_SWITCH": "Verwendung: python -m smartdesk.main switch <desktop-name>",
    "MAIN_INFO_SWITCHING_TO": "Versuche, zu '{name}' zu wechseln...",
    "MAIN_INFO_RESTARTING_EXPLORER": "Starte Explorer neu...",
    "MAIN_INFO_WAITING_EXPLORER": "Warte auf Explorer-Initialisierung...",
    "MAIN_SUCCESS_SWITCH": "Wechsel zu '{name}' abgeschlossen.",
    "MAIN_INFO_LIST_HEADER": "\nVerfügbare Desktops:",
    "MAIN_ERROR_UNKNOWN_COMMAND": "Unbekannter Befehl: {command}",
    "MAIN_INFO_AVAILABLE_COMMANDS": "Verfügbare Befehle: delete, switch, list",
    "MAIN_INFO_HINT_INTERACTIVE": "Oder starte ohne Argumente für das interaktive Menü.",

    # --- file_operations.py (FS_*) ---
    "FS_ERROR_CREATE_DIR": "[STORAGE ERROR] Konnte Datenverzeichnis nicht erstellen: {e}",
    "FS_ERROR_SAVE": "[STORAGE ERROR] Konnte Desktops nicht speichern: {e}",
    "FS_ERROR_LOAD": "[STORAGE ERROR] Konnte Desktops nicht laden: {e}",

    # --- icon_manager.py (IM_*) ---
    "IM_FATAL_COMMCTRL": "FATAL ERROR: 'commctrl' nicht gefunden. pywin32 ist nicht korrekt installiert.",
    "IM_ERROR_SHELLDLL_NOT_FOUND": "[IconManager ERROR] SHELLDLL_DefView-Fenster nicht gefunden.",
    "IM_ERROR_LISTVIEW_NOT_FOUND": "[IconManager ERROR] SysListView32 (FolderView) nicht gefunden.",
    "IM_INFO_READING_ICONS": "[IconManager] Lese Icon-Positionen vom Desktop...",
    "IM_ERROR_OPEN_PROCESS": "[IconManager ERROR] Konnte Prozess nicht öffnen. Fehlercode: {code}",
    "IM_ERROR_MEM_ALLOC": "[IconManager ERROR] Speicherreservierung fehlgeschlagen. Fehlercode: {code}",
    "IM_DEBUG_ITEM_COUNT": "[IconManager DEBUG] Anzahl gefundener Items (Icons): {count}",
    "IM_INFO_ICONS_FOUND": "-> {count} Icons gefunden und zur Liste hinzugefügt.",
    "IM_INFO_SETTING_ICONS": "[IconManager] Setze {count} Icon-Positionen (via Index-Methode)...",
    "IM_INFO_NO_ICONS_TO_SET": "-> Keine Icons zum Setzen vorhanden.",
    "IM_WARN_NO_ICONS_ON_DESKTOP": "[IconManager WARN] Aktueller Desktop hat 0 Icons. Breche Wiederherstellung ab.",
    "IM_WARN_INDEX_NOT_FOUND": "[IconManager WARN] Icon-Index {index} ('{name}') existiert nicht mehr (Max: {max}). Überspringe.",
    "IM_INFO_RESTORE_COMPLETE": "-> Wiederherstellung abgeschlossen. Erfolgreich: {restored}, Fehlgeschlagen: {failed}",

    # --- path_validator.py (PV_*) ---
    "PV_ERROR_CREATE_DIR": "Fehler beim Erstellen des Verzeichnisses {path}: {e}",

    # --- registry_operations.py (REG_*) ---
    "REG_ERROR_UPDATE": "Registry Fehler bei {key_path}: {e}",

    # --- system_manager.py (SYS_*) ---
    "SYS_INFO_RESTARTING": "[SYSTEM] Starte Windows Explorer neu...",
    "SYS_INFO_RESTARTED": "[SYSTEM] Explorer neu gestartet.",
}
