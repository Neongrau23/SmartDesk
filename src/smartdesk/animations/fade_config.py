# Konfigurationsdatei für Desktop-Switch Animation
class FadeConfig:    
    # Fade-Einstellungen für Desktop-Switch Animation
    FADE_IN_DURATION = 0.2      # Dauer des Einblendens in Sekunden
    FADE_OUT_DURATION = 0.3     # Dauer des Ausblendens in Sekunden
    VISIBLE_DURATION = 3.5      # Sichtbar während Explorer-Neustart (~3 Sekunden)
    FADE_STEPS = 100             # Anzahl der Schritte für sanftes Fade
    
    # Anzeigeeinstellungen
    BACKGROUND_COLOR = 'black'  # Hintergrundfarbe
    TEXT_COLOR = 'white'        # Textfarbe für ASCII-Art
    SHOW_LOGO = True            # SmartDesk Logo anzeigen
    HIDE_CURSOR = True          # Mauszeiger verstecken
    TOPMOST = True              # Fenster immer im Vordergrund
    
    # Wartezeit
    INITIAL_DELAY = 100         # Verzögerung vor Start in Millisekunden
    
    # Debug-Modus
    DEBUG = True                # Debug-Ausgaben aktivieren
    ALLOW_ESC_EXIT = True       # ESC-Taste zum Beenden erlauben