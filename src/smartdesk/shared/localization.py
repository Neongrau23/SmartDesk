# Dateipfad: src/smartdesk/localization.py
"""
Zentrale Datei für alle Texte der Benutzeroberfläche (Internationalisierung).
Alle von Benutzern gesehenen Texte sollten hier definiert werden.
"""

# TEXT Dictionary muss ZUERST definiert werden
TEXT = {
    # =============================================================================
    # GUI TEXTE
    # =============================================================================
    "gui": {
        "common": {
            "error_title": "Fehler",
            "success_title": "Erfolg",
            "info_title": "Info",
            "confirm_title": "Bestätigen",
            "button_cancel": "Abbrechen",
            "button_create": "Erstellen",
            "button_browse": "...",
            "button_delete": "Löschen",
            "button_save": "Speichern",
            "button_close": "Schließen",
            "button_refresh": "🔄 Aktualisieren",
            "status_active": " (Aktiv)",
            "status_protected": " (Geschützt)",
        },
        "create_dialog": {
            "title": "SmartDesk - Desktop erstellen",
            "header": "SmartDesk - Desktop erstellen",
            "label_name": "Name",
            "label_path_existing": "Pfad zum vorhandenen Ordner:",
            "label_path_new": "Übergeordneter Pfad (Ordner wird hier erstellt):",
            "radio_existing": "Vorhanden",
            "radio_new": "Neu erstellen",
            "browse_title_parent": "Übergeordneten Ordner auswählen",
            "browse_title_existing": "Vorhandenen Ordner auswählen",
            "error_no_name": "Bitte geben Sie einen Desktop-Namen ein!",
            "error_no_path": "Bitte geben Sie einen Pfad an!",
            "error_path_not_absolute": "Der Pfad ist nicht absolut: {path}",
            "error_creation_failed": "Desktop konnte nicht erstellt werden.\n\nMögliche Gründe:\n- Der Name ist bereits vergeben.\n- Der Pfad ist ungültig.\n- Der Ordner existiert nicht (im 'Vorhanden'-Modus).\n- Fehlende Berechtigungen.",
            "success_creation": "Desktop '{name}' wurde erfolgreich erstellt.",
            "new_path_location": "Der neue Desktop wird hier erstellt: {path}",
        },
        "control_panel": {
            "title": "SmartDesk Control",
            "header": "Control Panel",
            "desktop_label_template": "Desktop: {name}",
            "desktop_label_none": "Desktop: -",
            "desktop_label_error": "Desktop: ?",
            "button_open": "📂 SmartDesk Öffnen",
            "button_create": "➕ Desktop Erstellen",
            "button_manage": "Desktops verwalten",
            "button_hotkey_activate": "Hotkey Aktivieren",
            "button_hotkey_deactivate": "Hotkey Deaktivieren",
            "error_activation_failed": "SmartDesk konnte nicht aktiviert werden:\n{e}",
            "error_deactivation_failed": "SmartDesk konnte nicht deaktiviert werden:\n{e}",
            "error_open_gui_failed": "SmartDesk GUI konnte nicht geöffnet werden:\n{e}",
            "error_create_gui_failed": "Desktop-Erstellung konnte nicht gestartet werden:\n{e}",
            "error_manage_gui_failed": "Desktop-Verwaltung konnte nicht gestartet werden:\n{e}",
        },
        "main": {
            "title": "SmartDesk Manager",
            "sidebar_logo": "🖥️ SmartDesk",
            "sidebar_subtitle": "Desktop Manager",
            "nav_dashboard": "📊 Dashboard",
            "nav_desktops": "💻 Desktops",
            "nav_create": "➕ Neu erstellen",
            "nav_wallpaper": "🖼️ Wallpaper",
            "nav_hotkeys": "⌨️ Hotkeys",
            "nav_tray": "📌 Tray Icon",
            "nav_settings": "⚙️ Einstellungen",
            "sidebar_theme": "Theme:",
            "theme_dark": "Dark",
            "theme_light": "Light",
            "theme_system": "System",
            "dashboard": {
                "title": "📊 Dashboard",
                "stat_total": "Gesamt Desktops",
                "stat_active": "Aktiv",
                "stat_inactive": "Inaktiv",
                "quick_actions_title": "Schnellaktionen",
                "action_create": "➕ Neuer Desktop",
                "action_save_icons": "🔄 Icons speichern",
                "action_restart_explorer": "🔁 Explorer neustarten",
                "status_title": "System Status",
                "status_active_pid": "✓ Aktiv (PID: {pid})",
                "status_inactive": "○ Inaktiv",
                "status_unknown": "○ Status unbekannt",
                "status_no_active_desktop": "Kein aktiver Desktop",
                "status_label_hotkey": "Hotkey-Listener:",
                "status_label_tray": "Tray-Icon:",
                "status_label_active_desktop": "Aktiver Desktop:",
                "status_label_data_dir": "Daten-Verzeichnis:",
                "status_error_loading": "Fehler beim Laden der Status-Informationen: {e}",
            },
            "desktops": {
                "title": "💻 Desktop-Verwaltung",
                "list_label": "Alle Desktops",
                "none_found": "Keine Desktops gefunden.\nErstelle einen neuen Desktop!",
                "error_loading": "Fehler beim Laden: {e}",
                "button_switch": "Wechseln",
                "msgbox_switch_title": "Desktop wechseln",
                "msgbox_switch_text": "Möchtest du zu '{name}' wechseln?\n\nDer Explorer wird neu gestartet.",
                "msgbox_switch_success": "Desktop '{name}' wurde aktiviert!",
                "msgbox_switch_error": "Desktop konnte nicht gewechselt werden.",
                "msgbox_delete_title": "Desktop löschen",
                "msgbox_delete_text": "Desktop '{name}' löschen?\n\nPfad: {path}\n\nJa = Nur Eintrag löschen\nNein = Eintrag + Ordner löschen\nAbbrechen = Nichts tun",
                "msgbox_delete_success": "Desktop '{name}' wurde gelöscht.",
            },
            "create": {
                "title": "➕ Neuen Desktop erstellen",
                "label_name": "Desktop-Name:",
                "placeholder_name": "z.B. Arbeit, Gaming, Privat",
                "label_mode": "Modus auswählen:",
                "radio_existing": "Vorhandenen Ordner verwenden",
                "radio_new": "Neuen Ordner erstellen",
                "label_path": "Pfad:",
                "placeholder_path": "Ordner-Pfad auswählen",
                "button_browse": "📁 Durchsuchen",
                "hint_existing": "Wähle einen vorhandenen Ordner aus",
                "hint_new": "Wähle einen übergeordneten Ordner, in dem der neue Ordner erstellt wird",
                "button_create": "✓ Desktop erstellen",
                "error_name_missing": "Bitte gib einen Namen ein!",
                "error_path_missing": "Bitte wähle einen Pfad aus!",
                "error_path_not_exists": "Der ausgewählte Ordner existiert nicht!",
            },
            "wallpaper": {
                "title": "🖼️ Wallpaper-Verwaltung",
                "label_select": "Desktop auswählen:",
                "none_found": "Keine Desktops vorhanden",
                "label_file": "Wallpaper-Datei:",
                "placeholder_path": "Wallpaper auswählen (JPG, PNG, BMP)",
                "button_assign": "✓ Wallpaper zuweisen",
                "browse_title": "Wallpaper auswählen",
                "file_types": "Bilder",
                "all_files": "Alle Dateien",
                "error_no_file": "Bitte wähle eine Wallpaper-Datei aus!",
                "error_file_not_exists": "Die ausgewählte Datei existiert nicht!",
                "success_assign": "Wallpaper wurde '{name}' zugewiesen!",
            },
            "hotkeys": {
                "title": "⌨️ Hotkey-Verwaltung",
                "label_status": "Status:",
                "button_stop": "⏹️ Listener stoppen",
                "button_start": "▶️ Listener starten",
                "button_log": "📋 Log anzeigen",
                "success_start": "Hotkey-Listener wurde gestartet!",
                "success_stop": "Hotkey-Listener wurde gestoppt!",
                "log_title": "Hotkey-Log",
                "log_no_file": "Keine Log-Datei gefunden.",
            },
            "tray": {
                "title": "📌 Tray Icon-Verwaltung",
                "label_status": "Status:",
                "button_stop": "⏹️ Tray Icon stoppen",
                "button_start": "▶️ Tray Icon starten",
                "success_start": "Tray Icon wurde gestartet!",
                "success_stop": "Tray Icon wurde gestoppt!",
            },
            "settings": {
                "title": "⚙️ Einstellungen",
                "action_save_icons": "🔄 Icons speichern",
                "action_restart_explorer": "🔁 Explorer neustarten",
                "action_restore_registry": "🔧 Registry wiederherstellen",
                "action_save_icons_desc": "Speichert die aktuelle Icon-Position",
                "action_restart_explorer_desc": "Startet den Windows Explorer neu",
                "action_restore_registry_desc": "Stellt Registry-Pfade wieder her",
                "msgbox_restart_explorer_text": "Möchtest du den Windows Explorer wirklich neu starten?",
                "msgbox_restore_registry_text": "Möchtest du die Registry-Pfade wirklich wiederherstellen?",
                "error_script_not_found": "Skript nicht gefunden:\n{path}",
                "success_restore": "Registry-Wiederherstellung abgeschlossen!",
                "info_data_dir": "Daten-Verzeichnis:\n{path}",
            },
             "generic_errors": {
                "save": "Fehler beim Speichern: {e}",
                "start": "Fehler beim Starten: {e}",
                "stop": "Fehler beim Stoppen: {e}",
                "load": "Fehler beim Laden: {e}",
                "delete": "Fehler beim Löschen: {e}",
                "assign": "Fehler beim Zuweisen: {e}",
                "switch": "Fehler beim Wechseln: {e}",
                "restart": "Fehler beim Neustart: {e}",
                "restore": "Fehler bei der Wiederherstellung: {e}",
                "not_on_windows": "Nur unter Windows verfügbar!",
            }
        },
        "manage_dialog": {
            "title": "SmartDesk - Desktops verwalten",
            "header": "Desktops verwalten",
            "list_label": "Verfügbare Desktops",
            "details_name": "Name",
            "details_path": "Pfad",
            "details_wallpaper": "Hintergrundbild",
            "wallpaper_none": "Kein Bild ausgewählt",
            "button_change": "Ändern...",
            "msgbox_delete_confirm_text": "Möchten Sie den Desktop '{name}' wirklich löschen?",
            "error_delete_active": "Aktiver Desktop kann nicht gelöscht werden.",
            "error_delete_protected": "Geschützter Desktop kann nicht gelöscht werden.",
            "error_not_found": "Desktop nicht gefunden.",
            "error_empty_name": "Name darf nicht leer sein.",
            "success_save": "Änderungen gespeichert.",
            "error_save": "Änderungen konnten nicht gespeichert werden.",
            "success_wallpaper": "Hintergrundbild wurde aktualisiert.",
            "error_wallpaper": "Hintergrundbild konnte nicht gesetzt werden.",
        },
    },
    # =============================================================================
    # BACKEND / CORE TEXTE
    # =============================================================================
    "desktop_handler": {
        "error": {
            "path_invalid": "Pfad '{path}' ist ungültig oder konnte nicht erstellt werden.",
            "path_not_found_or_not_dir": "Pfad '{path}' existiert nicht oder ist kein Verzeichnis.",
            "name_exists": "Desktop '{name}' existiert bereits.",
            "desktop_not_found": "Desktop '{name}' nicht gefunden.",
            "new_name_exists": "Der neue Name '{name}' existiert bereits.",
            "folder_move": "Ordner konnte nicht verschoben werden: {e}",
            "new_path_create": "Neuer Pfad '{path}' konnte nicht erstellt werden.",
            "delete_active": "Der aktive Desktop '{name}' kann nicht gelöscht werden. Wechseln Sie zuerst zu einem anderen Desktop.",
            "delete_critical": "FEHLER: Der zu löschende Pfad '{path}' ist immer noch in der Registry als aktiv eingetragen.",
            "delete_denied": "Löschen aus Sicherheitsgründen verweigert.",
            "folder_delete": "Ordner konnte nicht gelöscht werden: {e}",
            "switch_not_found": "Desktop '{name}' wurde nicht gefunden.",
            "registry_update_failed": "Registry-Update fehlgeschlagen.",
            "recreating_folder": "Fehler beim erneuten Erstellen des Ordners.",
            "removing_config": "Fehler beim Entfernen der Konfiguration: {e}",
            "sync_no_active": "Synchronisierungsfehler: Kein Desktop ist als aktiv markiert.",
            "save_icons": "Fehler beim Speichern der Icon-Positionen: {e}",
            "save_icons_no_active": "Fehler: Kein aktiver Desktop gefunden.",
            "protected_delete": "Desktop '{name}' ist geschützt und kann nicht gelöscht werden.",
            "protected_edit": "Desktop '{name}' ist geschützt und kann nicht bearbeitet werden.",
        },
        "success": {
            "create": "Desktop '{name}' erfolgreich angelegt.",
            "update": "Desktop '{old_name}' erfolgreich zu '{new_name}' aktualisiert.",
            "folder_delete": "Zugehöriger Ordner '{path}' wurde gelöscht.",
            "wallpaper_delete": "Zugehöriges Hintergrundbild '{path}' wurde gelöscht.",
            "delete": "Desktop '{name}' wurde gelöscht.",
            "recreating_folder": "Ordner erfolgreich neu erstellt.",
            "removing_config": "Desktop '{name}' wurde entfernt.",
            "db_update": "Datenbank-Update erfolgreich.",
            "save_icons": "Icon-Positionen für '{name}' gespeichert.",
            "wallpaper_assigned": "Hintergrundbild erfolgreich {name} zugewiesen.",
        },
        "info": {
            "delete_aborted": "Löschvorgang abgebrochen.",
            "folder_not_found": "Ordner '{path}' nicht gefunden (wird ignoriert).",
            "folder_moved": "Ordner physisch verschoben von '{old_path}' nach '{new_path}'.",
            "already_active": "Desktop '{name}' ist bereits aktiv.",
            "path_is": "-> Eingetragener Pfad: {path}",
            "recreating_folder": "Erstelle Ordner '{path}' neu...",
            "removing_config": "Entferne '{name}' aus der Konfiguration...",
            "aborting_switch": "Wechselvorgang abgebrochen.",
            "saving_icons": "Speichere Icon-Positionen für '{name}'...",
            "switching_registry": "Wechsle Registry zu '{name}' ({path})...",
            "registry_success": "Registry erfolgreich aktualisiert.",
            "sync_after_restart": "Synchronisiere Status nach Explorer-Neustart...",
            "sync_path_found": "Aktiver Pfad gefunden: {path}",
            "sync_desktop_active": "Aktiver Desktop: '{name}'",
            "setting_wallpaper": "Setze Hintergrundbild...",
            "sync_restoring_icons": "Stelle Icon-Positionen für '{name}' wieder her...",
            "sync_icons_done": "Icon-Wiederherstellung abgeschlossen.",
            "reading_icons": "Lese Icon-Positionen für '{name}'...",
            "old_wallpaper_removed": "Altes Hintergrundbild entfernt.",
            "setting_wallpaper_now": "Desktop ist aktiv. Setze Hintergrundbild sofort.",
        },
        "warn": {
            "sync_failed": "Warnung: Registry-Synchronisierung fehlgeschlagen: {e}",
            "target_path_exists": "Warnung: Zielpfad '{path}' existiert bereits.",
            "wallpaper_delete": "Warnung: Altes Hintergrundbild konnte nicht gelöscht werden: {e}",
            "path_not_found": "Ziel-Pfad für '{name}' nicht gefunden!",
            "no_active_desktop": "Warnung: Kein Desktop war als aktiv markiert. Speichere keine Icons.",
            "sync_path_not_registered": "Möglicherweise ist der in Windows eingestellte Pfad in SmartDesk nicht registriert.",
            "save_icons_not_registered": "Möglicherweise ist der in Windows eingestellte Pfad in SmartDesk nicht registriert.",
        },
    },
    "icon_manager": {
        "error": {"fatal_commctrl": "FATAL: 'commctrl' nicht gefunden."},
        "info": {"reading": "[IconManager] Lese Icon-Positionen..."},
        "warn": {"no_icons_on_desktop": "Aktueller Desktop hat 0 Icons."},
        "debug": {"item_count": "[IconManager DEBUG] Anzahl Items: {count}"},
    },
    "system": {
        "info": {
            "restarting": "[SYSTEM] Starte Windows Explorer neu...",
            "restarted": "[SYSTEM] Explorer neu gestartet.",
        },
        "warning": {
            "explorer_not_running": "Explorer läuft nicht, starte ihn...",
            "explorer_timeout": "Explorer konnte nicht beendet werden (Timeout).",
            "kill_failed": "taskkill war nicht erfolgreich (ignoriert).",
        },
        "error": {
            "restart_failed": "Explorer konnte nicht neu gestartet werden.",
            "restart_exception": "Fehler bei Explorer-Neustart: {error}",
        },
    },
    "main": {
         "error": {
            "import": "Import Fehler: {e}",
            "import_hint_1": "Stelle sicher, dass du das Skript aus dem Projekt-Root ausführst.",
            "import_hint_2": "Und stelle sicher, dass die virtuelle Umgebung (.venv) aktiviert ist.",
            "unknown_command": "Unbekannter Befehl: {command}",
            "tray_not_found": "Tray-Icon Skript nicht gefunden unter: {path}",
            "tray_failed": "Fehler beim Starten des Tray-Icons: {e}",
        },
        "warn": {
            "tray_already_running": "Tray-Icon läuft bereits (PID: {pid}).",
        },
        "info": {
            "available_commands": "Verfügbare Befehle:",
            "starting_tray": "Starte das SmartDesk Tray-Icon...",
        },
        "success": {
            "tray_started": "Tray-Icon wurde erfolgreich gestartet.",
        },
    },
    "storage": {
        "error": {
            "create_dir": "Konnte Datenverzeichnis nicht erstellen: {e}",
            "save": "Konnte Desktops nicht speichern: {e}",
            "load": "Konnte Desktops nicht laden: {e}",
        }
    },
    "path_validator": {
        "error": {"create_dir": "Fehler beim Erstellen des Verzeichnisses {path}: {e}"}
    },
    "hotkey_manager": {
        "error": {
            "read_pid": "Fehler beim Lesen der PID-Datei: {e}",
            "python_not_found": "Python-Ausführungsdatei (.venv) nicht gefunden: {path}",
            "start_failed": "Fehler beim Starten des Listeners: {e}",
            "stop_failed": "Unerwarteter Fehler beim Stoppen des Listeners: {e}",
            "access_denied": "Keine Berechtigung, Prozess {pid} zu beenden.",
        },
        "warn": {
            "already_running": "Listener läuft bereits.",
            "not_running": "Listener läuft anscheinend nicht.",
            "pid_write_failed": "PID-Datei konnte nicht geschrieben werden: {e}",
            "process_not_found": "Prozess {pid} wurde nicht gefunden (lief evtl. schon nicht mehr).",
            "pid_clean_failed": "PID-Datei konnte nicht gelöscht werden: {e}",
            "force_kill": "Prozess {pid} reagiert nicht, erzwinge Beendigung...",
        },
        "info": {
            "start_success": "Listener erfolgreich gestartet (PID: {pid}).",
            "stop_success": "Prozess {pid} erfolgreich beendet.",
            "pid_cleaned": "PID-Datei aufgeräumt.",
        },
    },
    "tray_manager": {
        "warn": {
            "not_running": "Tray-Icon läuft derzeit nicht.",
            "pid_not_found": "Prozess {pid} wurde nicht gefunden (lief evtl. schon nicht mehr).",
        },
        "success": {"stopped": "Tray-Icon erfolgreich beendet."},
        "error": {"stop_failed": "Fehler beim Beenden des Tray-Icons: {e}"},
    },
    "hotkey_listener": {
        "error": {
            "actions_load": "FEHLER: Konnte .actions nicht laden: {e}",
            "actions_hint": "Stelle sicher, dass actions.py im 'hotkeys'-Ordner liegt.",
            "action_fallback": "FEHLER: Aktion {n} nicht geladen",
            "generic": "Ein Fehler ist aufgetreten: {e}",
        },
        "warn": {
            "pid_clean_failed": "Warnung: PID-Datei konnte nicht bereinigt werden: {e}"
        },
        "info": {
            "starting": "Hotkey-Listener wird gestartet...",
            "pid_cleaned": "PID-Datei bereinigt.",
            "stopped_user": "\nListener durch Benutzer (Strg+C) gestoppt.",
            "stopping": "Listener wird beendet.",
            "instructions": "\nDrücke Strg + Shift + Alt + [1-9] um einen Desktop zu wechseln.\nDrücke Strg + Shift + Alt + C um den Listener zu beenden.",\r\n            "instructions_stop": "Drücke Strg+C im Terminal, um den Listener zu stoppen.",
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
            "stopped": "Listener beendet",
        },
    },
    "registry": {"error": {"update": "Registry Fehler bei {key_path}: {e}"}},
    "wallpaper_manager": {
        "error": {
            "path_not_found": "Pfad '{path}' existiert nicht.",
            "source_not_found": "Quelldatei '{path}' wurde nicht gefunden.",
            "api_fail": "Windows-API konnte Hintergrundbild nicht setzen.",
            "api_exception": "Fehler beim Setzen des Hintergrundbilds: {e}",
            "copy": "Fehler beim Kopieren der Datei: {e}",
        },
        "success": {
            "set": "Hintergrundbild erfolgreich gesetzt.",
            "copy": "Hintergrundbild kopiert nach: {path}",
        },
    },
    "tray": {
        "menu": {
            "control_panel": "Control Panel",
            "manager": "SmartDesk Manager",
            "activate": "Aktivieren",
            "deactivate": "Deaktivieren",
            "quit": "Beenden"
        }
    }
}


def init_localization():
    """
    Stellt sicher, dass das Modul und seine Daten geladen sind.
    Wird explizit aufgerufen, um die Import-Reihenfolge zu erzwingen.
    """
    pass

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
