# =============================================================================
# HINWEIS: Diese Datei wird nur noch als Fallback verwendet!
# =============================================================================
# Die zentrale Konfiguration befindet sich jetzt in:
# src/smartdesk/config.py -> AnimationConfig
#
# Diese Datei bleibt erhalten für:
# - Standalone-Ausführung von screen_fade.py
# - Entwicklung/Testing ohne Hauptprojekt
# =============================================================================

# Konfigurationsdatei für Desktop-Switch Animation (FALLBACK)


class FadeConfig:
    # Fade-Einstellungen für Desktop-Switch Animation
    FADE_IN_DURATION = 0.1  # Dauer des Einblendens in Sekunden
    FADE_OUT_DURATION = 0.1  # Dauer des Ausblendens in Sekunden
    VISIBLE_DURATION = 2.5  # Sichtbar während Explorer-Neustart
    FADE_STEPS = 100  # Anzahl der Schritte für sanftes Fade

    # Anzeigeeinstellungen
    BACKGROUND_COLOR = "Black"  # Hintergrundfarbe
    TEXT_COLOR = "white"  # Textfarbe für ASCII-Art
    SHOW_LOGO = True  # SmartDesk Logo anzeigen
    HIDE_CURSOR = True  # Mauszeiger verstecken
    TOPMOST = True  # Fenster immer im Vordergrund

    # Wartezeit
    INITIAL_DELAY = 0  # Verzögerung vor Start in Millisekunden

    # Debug-Modus
    DEBUG = True  # Debug-Ausgaben für Standalone
    ALLOW_ESC_EXIT = True  # ESC-Taste zum Beenden erlauben
