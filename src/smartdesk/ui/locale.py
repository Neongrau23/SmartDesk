# Dateipfad: src/smartdesk/ui/locale.py

"""
Zentrale Datei für alle Texte der Benutzeroberfläche (Internationalisierung).
Alle von Benutzern gesehenen Texte sollten hier definiert werden.

Um die Sprache zu ändern, könnte man einfach diese Datei
gegen eine z.B. 'locale_en.py' austauschen, die dieselben
Schlüssel (z.B. "MAIN_MENU_SWITCH") aber englische Werte enthält.
"""

TEXT = {
    # --- Hauptmenü (print_main_menu) ---
    "MAIN_MENU_SEPARATOR": "-----------------------------------------",
    "MAIN_MENU_SWITCH": "Desktop wechseln",
    "MAIN_MENU_CREATE": "Neuen Desktop erstellen",
    "MAIN_MENU_SETTINGS": "Einstellungen",
    "MAIN_MENU_EXIT": "Beenden",

    # --- Einstellungsmenü (print_settings_menu) ---
    "SETTINGS_MENU_HEADER": "        --- Einstellungen ---        ",
    "SETTINGS_MENU_LIST": "Alle Desktops anzeigen",
    "SETTINGS_MENU_DELETE": "Desktop löschen",
    "SETTINGS_MENU_SAVE_ICONS": "Aktuelle Icon-Positionen speichern",
    "SETTINGS_MENU_RESTART": "Explorer manuell neu starten",
    "SETTINGS_MENU_BACK": "Zurück",

    # --- Allgemeine UI-Texte (aus run() und run_settings_menu()) ---
    "PROMPT_CHOOSE": "\nBitte wählen: ",
    "PROMPT_CONTINUE": "\n--- Drücke Enter, um fortzufahren ---",
    "ERROR_INVALID_INPUT": "Ungültige Eingabe.",
    "EXIT_MESSAGE": "Auf Wiedersehen!",
}
