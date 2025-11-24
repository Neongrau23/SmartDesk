# -*- coding: utf-8 -*-
"""
Separates Logo-Fenster für SmartDesk Desktop-Switch
Wird als eigener Prozess gestartet
"""
import math
import tkinter as tk
import sys
import os

# Import-Handling für sowohl Modul- als auch Script-Ausführung
try:
    # Versuch als Modul-Import (aus anderem Paket)
    from . import logo_config as cfg
except ImportError:
    # Fallback: Direkter Import wenn als Script ausgeführt
    # Füge das Verzeichnis zum Python-Pfad hinzu
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    import logo_config as cfg


class LogoWindow:
    """Eigenständiges Logo-Fenster für Desktop-Switch"""
    
    def __init__(self, duration=None):
        """
        Args:
            duration: Anzeigedauer in Sekunden (Standard aus TIMING_CONFIG)
        """
        if duration is None:
            duration = cfg.TIMING_CONFIG['default_duration']
        self.duration = duration * 1000  # Umrechnung in Millisekunden
        
        self.root = tk.Tk()
        self.root.title(cfg.WINDOW_CONFIG['title'])
        
        # Fenster-Eigenschaften
        self.root.overrideredirect(True)  # Keine Titelleiste
        self.root.configure(bg=cfg.WINDOW_CONFIG['background_color'])
        
        # Windows-spezifische Einstellungen für maximale Sichtbarkeit
        if sys.platform == 'win32':
            # Setze Fenster auf oberste Ebene (über allen anderen)
            self.root.wm_attributes('-topmost', 1)
            # Verhindere, dass Fenster in der Taskleiste erscheint
            self.root.attributes('-toolwindow', True)
        else:
            self.root.attributes('-topmost', True)
        
        # Transparenz für modernen Look (Initial unsichtbar)
        self.root.attributes('-alpha', cfg.WINDOW_CONFIG['alpha_hidden'])
        
        # Bildschirmgröße ermitteln
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Fenstergröße aus Konfiguration
        window_width = int(screen_width * cfg.WINDOW_CONFIG['width_ratio'])
        window_height = cfg.WINDOW_CONFIG['height']
        
        # Fenster zentrieren
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # Logo-Text aus Konfiguration
        self.logo_text = cfg.LOGO_CONFIG['text']
        
        # Hauptcontainer mit Padding aus Konfiguration
        bg_color = cfg.WINDOW_CONFIG['background_color']
        container = tk.Frame(self.root, bg=bg_color)
        container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=cfg.WINDOW_CONFIG['padding_x'],
            pady=cfg.WINDOW_CONFIG['padding_y']
        )
        
        # Logo-Label
        logo_font = (
            cfg.LOGO_CONFIG['font_family'],
            cfg.LOGO_CONFIG['font_size'],
            cfg.LOGO_CONFIG['font_weight']
        )
        self.logo_label = tk.Label(
            container,
            text=self.logo_text,
            font=logo_font,
            fg=cfg.LOGO_CONFIG['text_color'],
            bg=cfg.LOGO_CONFIG['background_color'],
            justify=cfg.LOGO_CONFIG['justify']
        )
        self.logo_label.pack(expand=True)
        
        # Status-Text
        status_font = (
            cfg.STATUS_CONFIG['font_family'],
            cfg.STATUS_CONFIG['font_size']
        )
        self.status_label = tk.Label(
            container,
            text=cfg.STATUS_CONFIG['text'],
            font=status_font,
            fg=cfg.STATUS_CONFIG['text_color'],
            bg=cfg.STATUS_CONFIG['background_color']
        )
        status_pady = (
            cfg.STATUS_CONFIG['padding_top'],
            cfg.STATUS_CONFIG['padding_bottom']
        )
        self.status_label.pack(pady=status_pady)
        
        # Canvas für moderne Animationen
        self.animation_canvas = tk.Canvas(
            container,
            width=cfg.CANVAS_CONFIG['width'],
            height=cfg.CANVAS_CONFIG['height'],
            bg=cfg.CANVAS_CONFIG['background_color'],
            highlightthickness=0
        )
        canvas_pady = (
            cfg.CANVAS_CONFIG['padding_top'],
            cfg.CANVAS_CONFIG['padding_bottom']
        )
        self.animation_canvas.pack(pady=canvas_pady)
        
        # Animation-Variablen
        self.animation_step = 0
        self.animation_running = False
        self.animation_objects = []
        
        # Wähle Animation aus Konfiguration
        self.animation_type = cfg.ANIMATION_CONFIG['type']
    
    def fade_in(self, duration=None, steps=None):
        """Sanftes Einblenden"""
        if duration is None:
            duration = cfg.FADE_CONFIG['fade_in_duration']
        if steps is None:
            steps = cfg.FADE_CONFIG['fade_in_steps']
        
        delay = duration / steps
        
        for i in range(steps + 1):
            alpha = i / steps * cfg.WINDOW_CONFIG['alpha_visible']
            self.root.attributes('-alpha', alpha)
            self.root.update()
            self.root.after(int(delay))
    
    def fade_out(self, duration=None, steps=None):
        """Sanftes Ausblenden"""
        if duration is None:
            duration = cfg.FADE_CONFIG['fade_out_duration']
        if steps is None:
            steps = cfg.FADE_CONFIG['fade_out_steps']
        
        delay = duration / steps
        
        for i in range(steps, -1, -1):
            alpha = i / steps * cfg.WINDOW_CONFIG['alpha_visible']
            self.root.attributes('-alpha', alpha)
            self.root.update()
            self.root.after(int(delay))
    
    def init_spinner_animation(self):
        """Moderner Spinner (kreisende Kreise)"""
        self.animation_objects = []
        cx = cfg.SPINNER_CONFIG['center_x']
        cy = cfg.SPINNER_CONFIG['center_y']
        radius = cfg.SPINNER_CONFIG['radius']
        num_dots = cfg.SPINNER_CONFIG['num_dots']
        dot_size = cfg.SPINNER_CONFIG['dot_size']
        
        for i in range(num_dots):
            x = cx + radius * 0.8 * (1 if i % 2 == 0 else 0.6)
            y = cy
            dot = self.animation_canvas.create_oval(
                x-dot_size, y-dot_size, x+dot_size, y+dot_size,
                fill=cfg.ANIMATION_CONFIG['primary_color'],
                outline=''
            )
            self.animation_objects.append(dot)
    
    def init_pulse_animation(self):
        """Pulsierende Kreise"""
        self.animation_objects = []
        cx = cfg.PULSE_CONFIG['center_x']
        cy = cfg.PULSE_CONFIG['center_y']
        num_circles = cfg.PULSE_CONFIG['num_circles']
        base_size = cfg.PULSE_CONFIG['base_size']
        line_width = cfg.PULSE_CONFIG['line_width']
        
        for i in range(num_circles):
            circle = self.animation_canvas.create_oval(
                cx-base_size, cy-base_size, cx+base_size, cy+base_size,
                outline=cfg.ANIMATION_CONFIG['primary_color'],
                width=line_width,
                fill=''
            )
            self.animation_objects.append(circle)
    
    def init_wave_animation(self):
        """Wellenförmige Balken"""
        self.animation_objects = []
        num_bars = cfg.WAVE_CONFIG['num_bars']
        spacing = cfg.WAVE_CONFIG['spacing']
        bar_width = cfg.WAVE_CONFIG['bar_width']
        center_y = cfg.WAVE_CONFIG['center_y']
        start_x = cfg.CANVAS_CONFIG['width'] // 2 - (num_bars * spacing) // 2
        
        for i in range(num_bars):
            x = start_x + i * spacing
            bar = self.animation_canvas.create_rectangle(
                x, center_y-5, x+bar_width, center_y+5,
                fill=cfg.ANIMATION_CONFIG['primary_color'],
                outline=''
            )
            self.animation_objects.append(bar)
    
    def init_dots_animation(self):
        """Springende Punkte"""
        self.animation_objects = []
        num_dots = cfg.DOTS_CONFIG['num_dots']
        spacing = cfg.DOTS_CONFIG['spacing']
        dot_radius = cfg.DOTS_CONFIG['dot_radius']
        base_y = cfg.DOTS_CONFIG['base_y']
        start_x = cfg.CANVAS_CONFIG['width'] // 2 - spacing
        
        for i in range(num_dots):
            x = start_x + i * spacing
            dot = self.animation_canvas.create_oval(
                x-dot_radius, base_y-dot_radius,
                x+dot_radius, base_y+dot_radius,
                fill=cfg.ANIMATION_CONFIG['primary_color'],
                outline=''
            )
            self.animation_objects.append(dot)
    
    def animate_loading(self):
        """Haupt-Animationsschleife"""
        if not self.animation_running:
            return
        
        if self.animation_type == 'spinner':
            self.animate_spinner()
        elif self.animation_type == 'pulse':
            self.animate_pulse()
        elif self.animation_type == 'wave':
            self.animate_wave()
        elif self.animation_type == 'dots':
            self.animate_dots()
        
        self.animation_step += 1
        frame_delay = cfg.ANIMATION_CONFIG['frame_delay']
        self.root.after(frame_delay, self.animate_loading)
    
    def animate_spinner(self):
        """Spinner-Animation updaten"""
        cx = cfg.SPINNER_CONFIG['center_x']
        cy = cfg.SPINNER_CONFIG['center_y']
        radius = cfg.SPINNER_CONFIG['radius']
        rotation_speed = cfg.SPINNER_CONFIG['rotation_speed']
        dot_size = cfg.SPINNER_CONFIG['dot_size']
        
        for i, dot in enumerate(self.animation_objects):
            step_angle = self.animation_step * rotation_speed + i * 45
            angle = math.radians(step_angle % 360)
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            
            # Alpha-Effekt simulieren durch Farbabstufung
            alpha_idx = (self.animation_step + i) % len(self.animation_objects)
            colors = cfg.ANIMATION_CONFIG['gradient_colors']
            num_objs = len(self.animation_objects)
            color = colors[alpha_idx * len(colors) // num_objs]

            self.animation_canvas.coords(
                dot, x-dot_size, y-dot_size, x+dot_size, y+dot_size
            )
            self.animation_canvas.itemconfig(dot, fill=color)
    
    def animate_pulse(self):
        """Puls-Animation updaten"""
        cx = cfg.PULSE_CONFIG['center_x']
        cy = cfg.PULSE_CONFIG['center_y']
        base_size = cfg.PULSE_CONFIG['base_size']
        max_scale = cfg.PULSE_CONFIG['max_scale']
        phase_shift = cfg.PULSE_CONFIG['phase_shift']
        
        for i, circle in enumerate(self.animation_objects):
            phase = (self.animation_step + i * phase_shift) % 100
            scale = 1 + (phase / 100) * (max_scale - 1)
            size = int(base_size * scale)
            
            # Transparenz-Effekt durch Farbe
            alpha = 1 - (phase / 100)
            brightness = int(255 * alpha)
            color = f'#{0:02x}{brightness:02x}{int(brightness*0.53):02x}'
            
            self.animation_canvas.coords(
                circle,
                cx-size, cy-size, cx+size, cy+size
            )
            self.animation_canvas.itemconfig(circle, outline=color)
    
    def animate_wave(self):
        """Wellen-Animation updaten"""
        min_height = cfg.WAVE_CONFIG['min_height']
        max_height = cfg.WAVE_CONFIG['max_height']
        phase_shift = cfg.WAVE_CONFIG['phase_shift']
        center_y = cfg.WAVE_CONFIG['center_y']
        
        for i, bar in enumerate(self.animation_objects):
            phase = (self.animation_step + i * phase_shift) % 30
            height_range = max_height - min_height
            sine_val = abs(math.sin(phase / 30 * math.pi))
            height = min_height + int(height_range * sine_val)
            
            coords = self.animation_canvas.coords(bar)
            x1, x2 = coords[0], coords[2]
            y1 = center_y - height // 2
            y2 = center_y + height // 2
            
            self.animation_canvas.coords(bar, x1, y1, x2, y2)
    
    def animate_dots(self):
        """Punkte-Animation updaten"""
        max_jump = cfg.DOTS_CONFIG['max_jump']
        phase_shift = cfg.DOTS_CONFIG['phase_shift']
        base_y = cfg.DOTS_CONFIG['base_y']
        dot_radius = cfg.DOTS_CONFIG['dot_radius']
        
        for i, dot in enumerate(self.animation_objects):
            phase = (self.animation_step + i * phase_shift) % 40
            offset = -int(max_jump * abs(math.sin(phase / 40 * math.pi)))
            
            coords = self.animation_canvas.coords(dot)
            x1 = coords[0]
            x2 = coords[2]
            y1 = base_y + offset - dot_radius
            y2 = base_y + offset + dot_radius
            
            self.animation_canvas.coords(dot, x1, y1, x2, y2)
    
    def start_close_sequence(self):
        """Schließ-Sequenz starten"""
        self.animation_running = False
        self.fade_out()
        self.root.quit()
    
    def run(self):
        """Logo-Fenster anzeigen"""
        # Fenster aktualisieren und in den Vordergrund bringen
        self.root.update()
        self.root.lift()
        self.root.focus_force()
        
        # Einblenden
        self.fade_in()
        
        # Animation initialisieren
        if self.animation_type == 'spinner':
            self.init_spinner_animation()
        elif self.animation_type == 'pulse':
            self.init_pulse_animation()
        elif self.animation_type == 'wave':
            self.init_wave_animation()
        elif self.animation_type == 'dots':
            self.init_dots_animation()
        
        # Lade-Animation starten
        self.animation_running = True
        self.animate_loading()
        
        # Nach duration automatisch schließen
        self.root.after(int(self.duration), self.start_close_sequence)
        
        # Mainloop starten
        self.root.mainloop()


if __name__ == "__main__":
    # Parameter aus Kommandozeile lesen (optional)
    duration = None
    
    if len(sys.argv) > 1:
        try:
            duration = float(sys.argv[1])
        except ValueError:
            default = cfg.TIMING_CONFIG['default_duration']
            msg = f"Ungültige Dauer: {sys.argv[1]}, "
            msg += f"verwende Standard: {default} Sekunden"
            print(msg)
    
    # Logo-Fenster erstellen und anzeigen
    logo = LogoWindow(duration=duration)
    logo.run()
