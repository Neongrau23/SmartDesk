# -*- coding: utf-8 -*-
"""
Zentrale Konfiguration für das Logo-Fenster
Hier können alle Design-Einstellungen vorgenommen werden
"""


# ============================================================================
# FENSTER-KONFIGURATION
# ============================================================================

WINDOW_CONFIG = {
    # Fenstertitel
    'title': "SmartDesk - Desktop wird vorbereitet",
    # Größe relativ zur Bildschirmbreite (0.0 - 1.0)
    'width_ratio': 0.6,
    'height': 400,
    # Hintergrund
    'background_color': '#000000',
    # Transparenz (0.0 = unsichtbar, 1.0 = voll sichtbar)
    'alpha_visible': 1.0,
    'alpha_hidden': 0.0,
    # Padding
    'padding_x': 40,
    'padding_y': 40,
}


# ============================================================================
# LOGO-TEXT KONFIGURATION
# ============================================================================

LOGO_CONFIG = {
    # ASCII Art Logo
    'text': r"""
  ____                       _   ____            _    
 / ___| _ __ ___   __ _ _ __| |_|  _ \  ___  ___| | __
 \___ \| '_ ` _ \ / _` | '__| __| | | |/ _ \/ __| |/ /
  ___) | | | | | | (_| | |  | |_| |_| |  __/\__ \   < 
 |____/|_| |_| |_|\__,_|_|   \__|____/ \___||___/_|\_\
                            
                                Desktop wird vorbereitet...
""",
    # Schriftart und Größe
    'font_family': 'Courier New',
    'font_size': 16,
    'font_weight': 'bold',
    # Farben
    'text_color': '#ffffff',
    'background_color': '#000000',
    # Ausrichtung
    'justify': 'center',
}


# ============================================================================
# STATUS-TEXT KONFIGURATION
# ============================================================================

STATUS_CONFIG = {
    # Text
    'text': "Einen Moment...",
    # Schriftart und Größe
    'font_family': 'Segoe UI',
    'font_size': 12,
    'font_weight': 'normal',
    # Farben
    'text_color': '#FFFFFF',
    'background_color': '#000000',
    # Abstand zum Logo
    'padding_top': 10,
    'padding_bottom': 0,
}


# ============================================================================
# ANIMATIONS-CANVAS KONFIGURATION
# ============================================================================

CANVAS_CONFIG = {
    # Canvas-Größe
    'width': 200,
    'height': 40,
    # Farben
    'background_color': "#000000",
    # Abstand zum Status-Text
    'padding_top': 50,
    'padding_bottom': 0,
}


# ============================================================================
# ANIMATIONS-KONFIGURATION
# ============================================================================

ANIMATION_CONFIG = {
    # Animationstyp: 'spinner', 'pulse', 'wave', 'dots'
    'type': 'wave',
    # Animationsgeschwindigkeit (Millisekunden zwischen Frames)
    'frame_delay': 50,
    # Farben für Animationen
    'primary_color': '#ffffff',
    'gradient_colors': ['#003322', '#005544', '#007766', '#00aa88', '#00ff88'],
}


# ============================================================================
# SPINNER-ANIMATION KONFIGURATION
# ============================================================================

SPINNER_CONFIG = {
    # Position im Canvas (relativ zur Canvas-Größe)
    'center_x': 100,
    'center_y': 20,
    # Radius des Spinner-Kreises
    'radius': 15,
    # Anzahl der Punkte
    'num_dots': 8,
    # Größe der einzelnen Punkte
    'dot_size': 3,
    # Geschwindigkeitsfaktor (Grad pro Frame)
    'rotation_speed': 8,
}


# ============================================================================
# PULSE-ANIMATION KONFIGURATION
# ============================================================================

PULSE_CONFIG = {
    # Position im Canvas
    'center_x': 100,
    'center_y': 20,
    # Anzahl der konzentrischen Kreise
    'num_circles': 3,
    # Basis-Größe
    'base_size': 10,
    # Maximaler Skalierungsfaktor
    'max_scale': 3,
    # Linienstärke
    'line_width': 2,
    # Phasenverschiebung zwischen Kreisen
    'phase_shift': 20,
}


# ============================================================================
# WAVE-ANIMATION KONFIGURATION
# ============================================================================

WAVE_CONFIG = {
    # Anzahl der Balken
    'num_bars': 10,
    # Abstand zwischen Balken
    'spacing': 12,
    # Balken-Breite
    'bar_width': 8,
    # Minimale und maximale Höhe
    'min_height': 5,
    'max_height': 15,
    # Phasenverschiebung zwischen Balken
    'phase_shift': 5,
    # Vertikale Position (Y-Koordinate)
    'center_y': 10,
}


# ============================================================================
# DOTS-ANIMATION KONFIGURATION
# ============================================================================

DOTS_CONFIG = {
    # Anzahl der Punkte
    'num_dots': 3,
    # Abstand zwischen Punkte
    'spacing': 20,
    # Punkt-Größe (Radius)
    'dot_radius': 5,
    # Maximale Sprung-Höhe
    'max_jump': 8,
    # Phasenverschiebung zwischen Punkten
    'phase_shift': 10,
    # Vertikale Basis-Position
    'base_y': 20,
}


# ============================================================================
# FADE-EFFEKTE KONFIGURATION
# ============================================================================

FADE_CONFIG = {
    # Einblende-Effekt
    'fade_in_duration': 300,  # Millisekunden
    'fade_in_steps': 50,
    # Ausblende-Effekt
    'fade_out_duration': 300,  # Millisekunden
    'fade_out_steps': 10,
}


# ============================================================================
# TIMING-KONFIGURATION
# ============================================================================

TIMING_CONFIG = {
    # Standard-Anzeigedauer (Sekunden)
    'default_duration': 3.0,
}
