# Dateipfad: src/smartdesk/localization.py
# (NEUE DATEI, ersetzt ui/locale.py)

"""
Zentrale Datei für alle Texte der Benutzeroberfläche (Internationalisierung).
Alle von Benutzern gesehenen Texte sollten hier definiert werden.
"""

# Diese Funktion wird von allen anderen Modulen importiert
def get_text(key: str, **kwargs) -> str:
    """
    Retrieves a localized text using dot notation and formats it with parameters.
    
    Holt einen Textbaustein anhand seines Schlüssels (Punkt-Notation) und formatiert ihn.
    
    Args:
        key: Dot-separated path to text (e.g., "ui.menu.main.switch")
        **kwargs: Format parameters for text template
    
    Returns:
        Formatted text string, or error message if key not found
    
    Examples:
        get_text("ui.menu.main.switch")
        get_text("desktop_handler.error.path_invalid", path="/foo")
    """
    keys = key.split('.')
    value = TEXT
    
    try:
        for k in keys:
            value = value[k]
        
        if not isinstance(value, str):
            return f"<{key} ist kein Text-Wert>"
        
        return value.format(**kwargs)
    except KeyError:
        return f"<{key} nicht gefunden>"
    except Exception as e:
        print(f"[LOKALISIERUNGSFEHLER] Fehler bei '{key}': {e}")
        return value if isinstance(value, str) else f"<{key} Fehler>"

TEXT = {
    "logo": {
        "ascii": r""" ___                _   ___         _   
/ __|_ __  __ _ _ _| |_|   \ ___ __| |__
\__ \ '  \/ _` | '_|  _| |) / -_|_-< / /
|___/_|_|_\__,_|_|  \__|___/\___/__/_\_\ """
    },
    "ui": {
        "menu": {
            "main": {
                "separator": "-----------------------------------------",
                "switch": "Desktop wechseln",
                "create": "Neuen Desktop erstellen",
                "settings": "Einstellungen",
                "exit": "Beenden"
            },
            "settings": {
                "header": "        --- Einstellungen ---        ",
                "list": "Alle Desktops anzeigen",
                "delete": "Desktop löschen",
                "save_icons": "Aktuelle Icon-Positionen speichern",
                "restart": "Explorer manuell neu starten",
                "back": "Zurück"
            }
        },
        "prompts": {
            "choose": "\nBitte wählen: ",
            "continue": "\n--- Drücke Enter, um fortzufahren ---",
            "cancel": "0. Abbrechen",
            
            # --- START KORREKTUR: Fehlende Texte wieder eingefügt ---
            "choose_number": "\nNummer eingeben: ",
            "desktop_name": "Name des neuen Desktops: ",
            "folder_mode": "\nWie soll der Ordner gewählt werden?",
            "folder_mode_1": "1. Einen existierenden Ordner verwenden",
            "folder_mode_2": "2. Einen neuen Ordner erstellen",
            "choose_1_or_2": "Auswahl (1/2): ",
            "existing_path": r"Bitte vollen Pfad eingeben (z.B. F:\SmartDesk\Work): ",
            "new_path_parent": r"In welchem Verzeichnis soll der Ordner erstellt werden? (z.B. F:\SmartDesk): ",
            # --- ENDE KORREKTUR ---
            
            "delete_folder_confirm": "Soll der Ordner '{path}' auch physisch gelöscht werden? (y/n): ",
            # --- NEUE TEXTE HINZUGEFÜGT ---
            "parent_dir_menu": {
                "not_found": "✗ Warnung: Das Basis-Verzeichnis '{path}' existiert nicht.",
                "title": "\nWas möchten Sie tun?",
                "create": "1. Das Verzeichnis '{path}' erstellen",
                "reenter": "2. Ein anderes Verzeichnis eingeben",
                "abort": "0. Abbrechen"
            },
            # --- HINZUGEFÜGT ---
            "path_error_menu": {
                "title": "1. Anderen Pfad eingeben",
                "abort": "2. Zurück zum Hauptmenü"
            }
        },
        "status": {
            "active": "AKTIV",
            "inactive": "     "
        },
        "headings": {
            "delete": "\n--- Desktop löschen ---",
            "create": "\n--- Neuen Desktop anlegen ---",
            "which_desktop_delete": "\n--- Welchen Desktop löschen? ---",
            "which_desktop_switch": "\n--- Zu welchem Desktop wechseln? ---"
        },
        "messages": {
            "exit": "Auf Wiedersehen!",
            "no_desktops": "Keine Desktops vorhanden.",
            "no_desktops_create_first": "Keine Desktops vorhanden. Bitte erstelle zuerst einen.",
            "new_path_location": "Der neue Desktop wird hier erstellt: {path}",
            "registry_set_success": "Registry erfolgreich auf '{name}' gesetzt.",
            "restarting_explorer": "Starte Explorer neu, um Änderungen anzuwenden...",
            "waiting_for_explorer": "Explorer wurde neu gestartet. Warte 1 Sekunde auf Initialisierung...",
            "syncing_icons": "Synchronisiere Status und stelle Icons wieder her...",
            "switch_success": "Wechsel zu '{name}' abgeschlossen.",
            "aborted_no_path": "Vorgang abgebrochen.",
            "parent_created": "✓ Basis-Verzeichnis '{path}' erfolgreich erstellt."
        },
        "errors": {
            "invalid_input": "Ungültige Eingabe.",
            "invalid_number": "Bitte eine gültige Zahl eingeben.",
            "name_empty": "Fehler: Der Name darf nicht leer sein.",
            "base_dir_empty": "Fehler: Basis-Verzeichnis darf nicht leer sein.",
            # --- TEXT ENTFERNT ---
            # "base_dir_not_found": "Fehler: Basis-Verzeichnis '{path}' existiert nicht oder ist kein Ordner.",
            "invalid_choice": "Ungültige Auswahl."
        }
    },
    "desktop_handler": {
        "error": {
            "path_invalid": "✗ Fehler: Pfad '{path}' ist ungültig oder konnte nicht erstellt werden.",
            # --- NEUER TEXT HINZUGEFÜGT ---
            "path_not_found_or_not_dir": "✗ Fehler: Pfad '{path}' existiert nicht oder ist kein Verzeichnis.",
            "name_exists": "✗ Fehler: Ein Desktop mit dem Namen '{name}' existiert bereits.",
            "not_found": "✗ Fehler: Desktop '{old_name}' nicht gefunden.",
            "not_found_delete": "✗ Fehler: Desktop '{name}' existiert nicht",
            "new_name_exists": "✗ Fehler: Der Name '{new_name}' ist bereits vergeben.",
            "folder_move": "✗ Fehler beim Verschieben des Ordners: {e}",
            "new_path_create": "✗ Fehler: Neuer Pfad '{path}' konnte nicht erstellt werden.",
            "delete_active": "✗ Fehler: Desktop '{name}' ist aktiv. Bitte wechseln Sie vorher den Desktop.",
            "delete_critical": "✗ KRITISCHER FEHLER: Windows Registry meldet, dass '{path}' der aktive Desktop ist!",
            "folder_delete": "✗ Fehler beim Löschen des Ordners: {e}",
            "switch_not_found": "✗ Fehler: Desktop '{name}' nicht gefunden.",
            "registry_update_failed": "✗ FEHLER: Konnte Registry nicht aktualisieren. Wechsel wird abgebrochen.",
            "sync_no_active": "✗ FEHLER: Konnte nach Neustart keinen aktiven Desktop in der DB finden.",
            "save_icons_no_active": "✗ Fehler: Konnte keinen aktiven Desktop finden.",
            "save_icons": "✗ Fehler beim Speichern der Icons: {e}",
            "recreating_folder": "✗ FEHLER: Der Ordner konnte nicht neu erstellt werden.",
            "removing_config": "✗ FEHLER beim Entfernen des Desktops: {e}"
        },
        "success": {
            "create": "✓ Desktop '{name}' erfolgreich angelegt.",
            "update": "✓ Desktop '{old_name}' wurde aktualisiert zu '{new_name}'.",
            "delete": "✓ Desktop '{name}' erfolgreich gelöscht",
            "folder_delete": "✓ Ordner '{path}' wurde physisch gelöscht.",
            "db_update": "Datenbank (Icon-Speicherung) aktualisiert.",
            "save_icons": "✓ Icon-Positionen für '{name}' erfolgreich gespeichert.",
            "recreating_folder": "✓ Ordner erfolgreich erstellt. Wechsel wird fortgesetzt.",
            "removing_config": "✓ Desktop '{name}' wurde entfernt."
        },
        "info": {
            "folder_moved": "Ordner physisch verschoben von '{old_path}' nach '{new_path}'.",
            "folder_not_found": "Hinweis: Ordner '{path}' existierte nicht mehr.",
            "delete_denied": "Löschen verweigert, um Datenverlust zu verhindern.",
            "delete_aborted": "Löschvorgang abgebrochen.",
            "already_active": "'{name}' ist bereits aktiv.",
            "saving_icons": "Speichere Icon-Positionen für '{name}'...",
            "switching_registry": "Wechsle Registry zu Desktop: {name} ({path})...",
            "registry_success": "Registry-Änderung erfolgreich. Neustart des Explorers erforderlich.",
            "sync_after_restart": "Synchronisiere Status nach Neustart...",
            "sync_path_found": "Registry-Pfad '{path}' gefunden.",
            "sync_desktop_active": "Desktop '{name}' ist jetzt aktiv.",
            "sync_restoring_icons": "Stelle Icon-Positionen für '{name}' wieder her...",
            "sync_icons_done": "Icon-Wiederherstellung abgeschlossen.",
            "reading_icons": "Lese aktuelle Icon-Positionen für '{name}'...",
            "path_is": "  -> {path}",
            "recreating_folder": "Erstelle Ordner neu: {path}...",
            "aborting_switch": "Wechsel wird abgebrochen.",
            "removing_config": "Entferne '{name}' aus der Konfiguration..."
        },
        "warn": {
            "target_path_exists": "Warnung: Zielpfad '{path}' existiert bereits. Versuche Inhalt zu integrieren...",
            "sync_failed": "Warnung: Konnte Status nicht mit Registry synchronisieren: {e}",
            "no_active_desktop": "Warnung: Es wurde kein als 'aktiv' markierter Desktop gefunden. Überspringe Speichern der Icons.",
            "path_not_found": "✗ WARNUNG: Der Pfad für Desktop '{name}' existiert nicht mehr:",
            "sync_path_not_registered": "Möglicherweise ist der Registry-Pfad in der desktops.json nicht registriert.",
            "save_icons_not_registered": "Möglicherweise ist der in Windows eingestellte Pfad\nin SmartDesk nicht registriert."
        },
        "prompts": {
            "delete_confirm": "Desktop '{name}' wirklich löschen? (y/n): ",
            "path_not_found_title": "\nWas möchten Sie tun?",
            "path_recreate": "  [1] Den Ordner neu erstellen und den Wechsel fortsetzen.",
            "path_remove": "  [2] Den Desktop aus der Konfiguration entfernen.",
            "path_abort": "  [j] Jegliche andere Eingabe bricht den Vorgang ab.",
            "your_choice": "Ihre Wahl: "
        }
    },
    "icon_manager": {
        "error": {
            "fatal_commctrl": "FATAL ERROR: 'commctrl' nicht gefunden. pywin32 ist nicht korrekt installiert.",
            "shelldll_not_found": "[IconManager ERROR] SHELLDLL_DefView-Fenster nicht gefunden.",
            "listview_not_found": "[IconManager ERROR] SysListView32 (FolderView) nicht gefunden.",
            "open_process": "[IconManager ERROR] Konnte Prozess nicht öffnen. Fehlercode: {code}",
            "mem_alloc": "[IconManager ERROR] Speicherreservierung fehlgeschlagen. Fehlercode: {code}"
        },
        "info": {
            "reading": "[IconManager] Lese Icon-Positionen vom Desktop...",
            "icons_found": "-> {count} Icons gefunden und zur Liste hinzugefügt.",
            "setting": "[IconManager] Setze {count} Icon-Positionen (via Index-Methode)...",
            "no_icons_to_set": "-> Keine Icons zum Setzen vorhanden.",
            "restore_complete": "-> Wiederherstellung abgeschlossen. Erfolgreich: {restored}, Fehlgeschlagen: {failed}"
        },
        "warn": {
            "no_icons_on_desktop": "[IconManager WARN] Aktueller Desktop hat 0 Icons. Breche Wiederherstellung ab.",
            "index_not_found": "[IconManager WARN] Icon-Index {index} ('{name}') existiert nicht mehr (Max: {max}). Überspringe."
        },
        "debug": {
            "item_count": "[IconManager DEBUG] Anzahl gefundener Items (Icons): {count}"
        }
    },
    "system": {
        "info": {
            "restarting": "[SYSTEM] Starte Windows Explorer neu...",
            "restarted": "[SYSTEM] Explorer neu gestartet."
        }
    },
    "main": {
        "error": {
            "import": "Import Fehler: {e}",
            "import_hint_1": "Stelle sicher, dass du das Skript aus dem Projekt-Root ausführst",
            "import_hint_2": "oder dass das Paket korrekt installiert ist.",
            "handler_call_failed": "FEHLER: {name} konnte nicht geladen werden!",
            "name_missing": "Fehler: Desktop-Name fehlt.",
            "unknown_command": "Unbekannter Befehl: {command}"
        },
        "warn": {
            "handler_load_failed": "Warnung: {handler} konnte nicht geladen werden."
        },
        "info": {
            "starting_interactive": "Starte interaktives Menü...",
            "switching_to": "Versuche, zu '{name}' zu wechseln...",
            "restarting_explorer": "Starte Explorer neu...",
            "waiting_explorer": "Warte auf Explorer-Initialisierung...",
            "list_header": "\nVerfügbare Desktops:",
            "available_commands": "Verfügbare Befehle: delete, switch, list",
            "hint_interactive": "Oder starte ohne Argumente für das interaktive Menü."
        },
        "success": {
            "switch": "Wechsel zu '{name}' abgeschlossen."
        },
        "usage": {
            "delete": "Verwendung: python -m smartdesk.main delete <desktop-name> [--delete-folder]",
            "switch": "Verwendung: python -m smartdesk.main switch <desktop-name>"
        }
    },
    "storage": {
        "error": {
            "create_dir": "[STORAGE ERROR] Konnte Datenverzeichnis nicht erstellen: {e}",
            "save": "[STORAGE ERROR] Konnte Desktops nicht speichern: {e}",
            "load": "[STORAGE ERROR] Konnte Desktops nicht laden: {e}"
        }
    },
    "path_validator": {
        "error": {
            "create_dir": "Fehler beim Erstellen des Verzeichnisses {path}: {e}"
        }
    },
    "registry": {
        "error": {
            "update": "Registry Fehler bei {key_path}: {e}"
        }
    }
}