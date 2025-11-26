# Dateipfad: src/smartdesk/localization.py
# (Vollständig, mit Hotkey-Texten UND Tray-Icon-Texten)

"""
Zentrale Datei für alle Texte der Benutzeroberfläche (Internationalisierung).
Alle von Benutzern gesehenen Texte sollten hier definiert werden.
"""

# TEXT Dictionary muss ZUERST definiert werden
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
                "wallpaper": "Hintergrundbild zuweisen", 
                "restart": "Explorer manuell neu starten",
                "hotkeys": "Hotkey-Listener verwalten",
                "tray": "Tray-Icon verwalten",
                "back": "Zurück"
            },
            # --- NEUER ABSCHNITT FÜR HOTKEY-MENÜ ---
            "hotkeys": {
                "manage": "1. Listener verwalten (Start/Stop)",
                "debug": "2. Debug-Log anzeigen",
            },
            # --- NEUER ABSCHNITT FÜR TRAY-MENÜ ---
            "tray": {
                "manage": "1. Tray-Icon verwalten (Start/Stop)",
            }
        },
        "prompts": {
            "choose": "\nBitte wählen: ",
            "continue": "\n--- Drücke Enter, um fortzufahren ---",
            "cancel": "0. Abbrechen",
            
            "choose_number": "\nNummer eingeben: ",
            "desktop_name": "Name des neuen Desktops: ",
            "folder_mode": "\nWie soll der Ordner gewählt werden?",
            "folder_mode_1": "1. Einen existierenden Ordner verwenden",
            "folder_mode_2": "2. Einen neuen Ordner erstellen",
            "choose_1_or_2": "Auswahl (1/2): ",
            "existing_path": r"Bitte vollen Pfad eingeben (z.B. F:\SmartDesk\Work): ",
            "new_path_parent": r"In welchem Verzeichnis soll der Ordner erstellt werden? (z.B. F:\SmartDesk): ",
            
            "delete_folder_confirm": "Soll der Ordner '{path}' auch physisch gelöscht werden? (y/n): ",
            "wallpaper_path": "Pfad zum Hintergrundbild (leer = abbrechen): ", # <-- Fehlte
            
            # --- NEUER ABSCHNITT FÜR HOTKEY-MENÜ ---
            "hotkeys": {
                "start": "1. Listener starten",
                "stop": "2. Listener stoppen"
            },
            
            # --- NEUER ABSCHNITT FÜR TRAY-MENÜ ---
            "tray": {
                "start": "1. Tray-Icon starten",
                "stop": "2. Tray-Icon stoppen"
            },
            
            "parent_dir_menu": {
                "not_found": "! Warnung: Das Basis-Verzeichnis '{path}' existiert nicht.",
                "title": "\nWas möchten Sie tun?",
                "create": "1. Das Verzeichnis '{path}' erstellen",
                "reenter": "2. Ein anderes Verzeichnis eingeben",
                "abort": "0. Abbrechen"
            },
            "path_error_menu": {
                "title": "1. Anderen Pfad eingeben",
                "abort": "2. Zurück zum Hauptmenü"
            }
        },
        "status": {
            "active": "AKTIV",
            "inactive": "      ",
            "active_short": "Aktiv", # <-- Fehlte
            "wallpaper": "Hintergrund", # <-- Fehlte
            "wallpaper_none": "Kein Hintergrundbild", # <-- Fehlte

            # --- NEUE TEXTE FÜR HOTKEY-STATUS ---
            "hotkeys_status": "Status:",
            "hotkeys_on": "Aktiv",
            "hotkeys_off": "Gestoppt",
            
            # --- NEUE TEXTE FÜR TRAY-STATUS ---
            "tray_status": "Status:",
            "tray_on": "Aktiv",
            "tray_off": "Gestoppt"
        },
        "headings": {
            "delete": "\n--- Desktop löschen ---",
            "create": "\n--- Neuen Desktop anlegen ---",
            "wallpaper": "\n--- Hintergrundbild zuweisen ---", # <-- Fehlte
            "which_desktop_delete": "\n--- Welchen Desktop löschen? ---",
            "which_desktop_switch": "\n--- Zu welchem Desktop wechseln? ---",
            "which_desktop_wallpaper": "\n--- Welchem Desktop ein Hintergrundbild zuweisen? ---", # <-- Fehlte

            # --- NEUE TEXTE FÜR HOTKEY-MENÜ ---
            "hotkeys": "\n--- Hotkey-Listener ---",
            "hotkeys_manage": "\n--- Listener verwalten ---",
            "hotkeys_debug": "\n--- Hotkey Debug-Log (Letzte 20 Zeilen) ---",
            
            # --- NEUE TEXTE FÜR TRAY-MENÜ ---
            "tray": "\n--- Tray-Icon ---",
            "tray_manage": "\n--- Tray-Icon verwalten ---"
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
            "aborted_no_path": "Vorgang abgebrochen (kein Pfad angegeben).",
            "parent_created": "✓ Basis-Verzeichnis '{path}' erfolgreich erstellt.",

            # --- NEUE TEXTE FÜR HOTKEY-MENÜ ---
            "log_empty": "(Log-Datei ist leer)",
            "log_not_found": "(Log-Datei nicht gefunden)"
        },
        "errors": {
            "invalid_input": "Ungültige Eingabe.",
            "invalid_number": "Bitte eine gültige Zahl eingeben.",
            "name_empty": "Der Name darf nicht leer sein.",
            "base_dir_empty": "Basis-Verzeichnis darf nicht leer sein.",
            "invalid_choice": "Ungültige Auswahl.",
            "path_not_absolute": "Der Pfad '{path}' ist kein absoluter Pfad.", # <-- Fehlte
            
            # --- NEUER TEXT FÜR HOTKEY-MENÜ ---
            "log_read_failed": "Log-Datei konnte nicht gelesen werden: {e}"
        }
    },
    
    # ... (alle anderen Sektionen wie desktop_handler, icon_manager, etc. bleiben hier) ...
    "desktop_handler": {
        "error": {
            "path_invalid": "Pfad '{path}' ist ungültig oder konnte nicht erstellt werden.",
            "path_not_found_or_not_dir": "Pfad '{path}' existiert nicht oder ist kein Verzeichnis.",
            "name_exists": "Desktop '{name}' existiert bereits.",
            "desktop_not_found": "Desktop '{name}' nicht gefunden.",
            "delete_active": "Der aktive Desktop '{name}' kann nicht gelöscht werden. Wechseln Sie zuerst zu einem anderen Desktop.",
            "switch_no_desktops": "Keine Desktops verfügbar.",
            "switch_not_found": "Desktop '{name}' wurde nicht gefunden.",
            "registry_update_failed": "Registry-Update fehlgeschlagen.",
            "save_icons_failed": "Fehler beim Speichern der Icon-Positionen: {e}",
            "save_icons_no_active": "Fehler: Kein aktiver Desktop gefunden.",
            "save_icons_not_registered": "Möglicherweise ist der in Windows eingestellte Pfad\nin SmartDesk nicht registriert.",
            "wallpaper_assign_failed": "Fehler beim Zuweisen des Hintergrundbilds."
        },
        "success": {
            "create": "Desktop '{name}' erfolgreich angelegt.",
            "delete": "Desktop '{name}' wurde gelöscht.",
            "switch": "Zu Desktop '{name}' gewechselt.",
            "icons_saved": "Icon-Positionen für '{name}' gespeichert ({count} Icons).",
            "removing_config": "Desktop '{name}' wurde entfernt.",
            "wallpaper_assigned": "Hintergrundbild erfolgreich zugewiesen."
        },
        "info": {
            "folder_moved": "Ordner physisch verschoben von '{old_path}' nach '{new_path}'.",
            "reading_icons": "Lese Icon-Positionen für '{name}'...",
            "icons_read": "{count} Icon-Positionen eingelesen.",
            "no_saved_icons": "Keine gespeicherten Icon-Positionen für '{name}' gefunden.",
            "restoring_icons": "Stelle {count} Icons wieder her...",
            "restore_complete": "{restored} Icons wiederhergestellt, {failed} fehlgeschlagen.",
            "removing_config": "Entferne '{name}' aus der Konfiguration...",
            "deleting_folder": "Lösche Ordner '{path}'...",
            "folder_deleted": "Ordner '{path}' wurde gelöscht.",
            "marking_active": "Markiere '{name}' als aktiv...",
            "updating_registry": "Aktualisiere Windows Registry...",
            "copying_wallpaper": "Kopiere Hintergrundbild nach AppData...",
            "setting_wallpaper": "Setze Hintergrundbild..."
        },
        "warn": {
            "target_path_exists": "Zielpfad '{path}' existiert bereits. Versuche Inhalt zu integrieren...",
            "folder_merge_failed": "Warnung: Manche Dateien konnten nicht verschoben werden.",
            "delete_folder_failed": "Warnung: Ordner '{path}' konnte nicht gelöscht werden: {e}",
            "already_active": "Desktop '{name}' ist bereits aktiv.",
            "save_icons_not_registered": "Möglicherweise ist der in Windows eingestellte Pfad\nin SmartDesk nicht registriert."
        },
        "prompts": {
            "delete_confirm": "Desktop '{name}' wirklich löschen? (y/n): ",
            "delete_folder": "Soll der Ordner auch physisch gelöscht werden? (y/n): ",
            "your_choice": "Ihre Wahl: "
        }
    },
    
    # --- (Hier icon_manager, system, main, storage, path_validator einfügen) ---
    "icon_manager": {
        "error": { "fatal_commctrl": "FATAL: 'commctrl' nicht gefunden." },
        "info": { "reading": "[IconManager] Lese Icon-Positionen..." },
        "warn": { "no_icons_on_desktop": "Aktueller Desktop hat 0 Icons." },
        "debug": { "item_count": "[IconManager DEBUG] Anzahl Items: {count}" }
    },
    "system": {
        "info": { "restarting": "[SYSTEM] Starte Windows Explorer neu...", "restarted": "[SYSTEM] Explorer neu gestartet." }
    },
    "main": {
        "error": { 
            "import": "Import Fehler: {e}", 
            "import_hint_1": "Stelle sicher...", 
            "import_hint_2": "...", 
            "handler_call_failed": "{name} konnte nicht geladen werden!", 
            "name_missing": "Desktop-Name fehlt.", 
            "unknown_command": "Unbekannter Befehl: {command}",
            # --- HINZUGEFÜGT ---
            "tray_not_found": "Tray-Icon Skript nicht gefunden unter: {path}",
            "tray_failed": "Fehler beim Starten des Tray-Icons: {e}"
        },
        "warn": { 
            "handler_load_failed": "{handler} konnte nicht geladen werden." 
        },
        "info": { 
            "starting_interactive": "Starte interaktives Menü...", 
            "switching_to": "Versuche...", 
            "restarting_explorer": "Starte Explorer neu...", 
            "waiting_explorer": "Warte...", 
            "list_header": "\nVerfügbare Desktops:", 
            "available_commands": "Verfügbare Befehle: delete, switch, list", 
            "hint_interactive": "Oder starte ohne Argumente...",
            # --- HINZUGEFÜGT ---
            "starting_tray": "Starte das SmartDesk Tray-Icon..."
        },
        "success": { 
            "switch": "Wechsel zu '{name}' abgeschlossen.",
            # --- HINZUGEFÜGT ---
            "tray_started": "Tray-Icon wurde erfolgreich gestartet."
        },
        "usage": { 
            "delete": "Verwendung: ...", 
            "switch": "Verwendung: ..." 
        }
    },
    "storage": {
        "error": { "create_dir": "Konnte Datenverzeichnis nicht erstellen: {e}", "save": "Konnte Desktops nicht speichern: {e}", "load": "Konnte Desktops nicht laden: {e}" }
    },
    "path_validator": {
        "error": { "create_dir": "Fehler beim Erstellen des Verzeichnisses {path}: {e}" }
    },

    
    # --- NEUER ABSCHNITT FÜR DEN HOTKEY MANAGER ---
    "hotkey_manager": {
        "error": {
            "read_pid": "Fehler beim Lesen der PID-Datei: {e}",
            "python_not_found": "Python-Ausführungsdatei (.venv) nicht gefunden: {path}",
            "start_failed": "Fehler beim Starten des Listeners: {e}",
            "stop_failed": "Unerwarteter Fehler beim Stoppen des Listeners: {e}"
        },
        "warn": {
            "already_running": "Listener läuft bereits.",
            "not_running": "Listener läuft anscheinend nicht.",
            "pid_write_failed": "PID-Datei konnte nicht geschrieben werden: {e}",
            "process_not_found": "Prozess {pid} wurde nicht gefunden (lief evtl. schon nicht mehr).",
            "pid_clean_failed": "PID-Datei konnte nicht gelöscht werden: {e}"
        },
        "info": {
            "starting": "Starte Hotkey-Listener im Hintergrund...",
            "start_success": "Listener erfolgreich gestartet (PID: {pid}).",
            "stopping": "Versuche, Prozess mit PID {pid} zu beenden...",
            "signal_sent": "Signal zum Beenden an PID {pid} gesendet.",
            "stop_success": "Prozess {pid} erfolgreich beendet.",
            "pid_cleaned": "PID-Datei aufgeräumt."
        }
    },

    # --- NEUER ABSCHNITT FÜR DEN TRAY MANAGER ---
    "tray_manager": {
        "warn": {
            "not_running": "Tray-Icon läuft derzeit nicht.",
            "pid_not_found": "Prozess {pid} wurde nicht gefunden (lief evtl. schon nicht mehr)."
        },
        "success": {
            "stopped": "Tray-Icon erfolgreich beendet."
        },
        "error": {
            "stop_failed": "Fehler beim Beenden des Tray-Icons: {e}"
        }
    },

    "hotkey_listener": {
        "error": {
            "actions_load": "FEHLER: Konnte .actions nicht laden: {e}",
            "actions_hint": "Stelle sicher, dass actions.py im 'hotkeys'-Ordner liegt.",
            "action_fallback": "FEHLER: Aktion {n} nicht geladen",
            "generic": "Ein Fehler ist aufgetreten: {e}"
        },
        "warn": {
            "pid_clean_failed": "Warnung: PID-Datei konnte nicht bereinigt werden: {e}"
        },
        "info": {
            "abort_invalid_key": "-> Abgebrochen. (Alt + ungültige Taste gedrückt)",
            "abort_alt_released": "-> Abgebrochen. (Alt losgelassen)",
            "wait_for_alt_num": "\nStrg+Shift erkannt. Warte auf Alt + (1-9)...",
            "starting": "Hotkey-Listener wird gestartet...",
            "instructions": "Drücke 'Strg+Shift' (eine der Tasten loslassen) und dann Alt + (1-9).",
            "instructions_stop": "Drücke 'Strg+C' im Terminal, um das Skript zu beenden.",
            "pid_cleaned": "PID-Datei bereinigt.",
            "stopped_user": "\nListener durch Benutzer (Strg+C) gestoppt.",
            "stopping": "Listener wird beendet."
        },
        "log": {
            "action_executed": "Hotkey Alt+{n} ausgeführt",
            "abort_no_alt": "Abgebrochen: Ungültige Taste ohne Alt gedrückt",
            "wait_for_alt_num": "Strg+Shift erkannt, warte auf Alt + (1-9)",
            "started": "Hotkey-Listener gestartet",
            "waiting": "Warte auf Hotkey-Eingaben...",
            "pid_cleaned": "PID-Datei bereinigt",
            "pid_clean_failed": "Warnung: PID-Datei-Cleanup fehlgeschlagen: {e}",
            "stopped_user": "Listener durch Benutzer gestoppt (Strg+C)",
            "error_generic": "Fehler aufgetreten: {e}",
            "stopped": "Listener beendet"
        }
    },
    
    "registry": {
        "error": {
            "update": "Registry Fehler bei {key_path}: {e}"
        }
    },
    
    "wallpaper_manager": {
        "error": {
            "path_not_found": "Pfad '{path}' existiert nicht.",
            "source_not_found": "Quelldatei '{path}' wurde nicht gefunden.",
            "api_fail": "Windows-API konnte Hintergrundbild nicht setzen.",
            "api_exception": "Fehler beim Setzen des Hintergrundbilds: {e}",
            "copy": "Fehler beim Kopieren der Datei: {e}"
        },
        "success": {
            "set": "Hintergrundbild erfolgreich gesetzt.",
            "copy": "Hintergrundbild kopiert nach: {path}"
        }
    }
}


# Diese Funktion wird von allen anderen Modulen importiert
def get_text(key: str, **kwargs) -> str:
    """
    Retrieves a localized text using dot notation and formats it with parameters.
    
    Holt einen Textbaustein anhand seines Schlüssels (Punkt-Notation) und formatiert ihn.
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
