# Desktop-Switch Fade-Animation für SmartDesk
import tkinter as tk
import time
from fade_config import FadeConfig

class MultiMonitorFade:
    def __init__(self, config=None):
        """
        Initialisierung mit optionaler Konfiguration
        
        Args:
            config: FadeConfig-Instanz oder None für Standardwerte
        """
        self.config = config or FadeConfig()
        
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        
        if self.config.TOPMOST:
            self.root.attributes('-topmost', True)
            
        self.root.configure(bg=self.config.BACKGROUND_COLOR)
        
        # Mauszeiger verstecken
        if self.config.HIDE_CURSOR:
            self.root.config(cursor="none")
        
        # ESC zum Beenden
        if self.config.ALLOW_ESC_EXIT:
            self.root.bind('<Escape>', lambda e: self.root.quit())
        
        # Gesamten Bildschirmbereich über alle Monitore ermitteln
        self.setup_fullscreen()
        
        # Canvas für Fade-Effekt
        self.canvas = tk.Canvas(
            self.root, 
            bg=self.config.BACKGROUND_COLOR, 
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Schwarzes Rechteck
        self.rect = self.canvas.create_rectangle(
            0, 0, 
            self.root.winfo_screenwidth(), 
            self.root.winfo_screenheight(),
            fill=self.config.BACKGROUND_COLOR, 
            outline=''
        )
        
        # SmartDesk Logo hinzufügen
        if self.config.SHOW_LOGO:
            self.add_logo()
        
    def setup_fullscreen(self):
        """Fenster über alle Monitore strecken"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        if self.config.DEBUG:
            print(f"Erkannte Bildschirmgröße: {screen_width}x{screen_height}")
        
        self.root.geometry(f'{screen_width}x{screen_height}+0+0')
    
    def add_logo(self):
        """SmartDesk ASCII-Logo in der Mitte des Bildschirms hinzufügen"""
        logo = r"""______          _    _                         _         _   _   _            _                   _ _       _         
|  _  \        | |  | |                       (_)       | | | | | |          | |                 (_) |     | |        
| | | |___  ___| | _| |_ ___  _ __   __      ___ _ __ __| | | | | | ___  _ __| |__   ___ _ __ ___ _| |_ ___| |_       
| | | / _ \/ __| |/ / __/ _ \| '_ \  \ \ /\ / / | '__/ _` | | | | |/ _ \| '__| '_ \ / _ \ '__/ _ \ | __/ _ \ __|      
| |/ /  __/\__ \   <| || (_) | |_) |  \ V  V /| | | | (_| | \ \_/ / (_) | |  | |_) |  __/ | |  __/ | ||  __/ |_ _ _ _ 
|___/ \___||___/_|\_\\__\___/| .__/    \_/\_/ |_|_|  \__,_|  \___/ \___/|_|  |_.__/ \___|_|  \___|_|\__\___|\__(_|_|_)
                             | |                                                                                      
                             |_|                                                                                      """
        
        # Text in der Mitte des Canvas platzieren
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        self.logo_text = self.canvas.create_text(
            screen_width // 2,
            screen_height // 2,
            text=logo,
            fill=self.config.TEXT_COLOR,
            font=('Courier New', 14, 'bold'),
            justify='center'
        )
        
    def fade_in(self, duration=None, steps=None):
        """Sanftes Einblenden"""
        duration = duration or self.config.FADE_IN_DURATION
        steps = steps or self.config.FADE_STEPS
        delay = duration / steps
        
        for i in range(steps + 1):
            alpha = i / steps
            self.root.attributes('-alpha', alpha)
            self.root.update()
            time.sleep(delay)
    
    def fade_out(self, duration=None, steps=None):
        """Sanftes Ausblenden"""
        duration = duration or self.config.FADE_OUT_DURATION
        steps = steps or self.config.FADE_STEPS
        delay = duration / steps
        
        for i in range(steps, -1, -1):
            alpha = i / steps
            self.root.attributes('-alpha', alpha)
            self.root.update()
            time.sleep(delay)
    
    def run(self):
        """Hauptablauf: Einblenden -> Warten -> Ausblenden"""
        # Fenster initial unsichtbar machen
        self.root.attributes('-alpha', 0.0)
        self.root.update()
        
        # Kurz warten bis Fenster vollständig initialisiert ist
        self.root.after(self.config.INITIAL_DELAY, self.execute_fade)
        
        self.root.mainloop()
    
    def execute_fade(self):
        """Fade-Sequenz ausführen"""
        if self.config.DEBUG:
            print("Blende Bildschirm ein...")
        
        # Schnell einblenden
        self.fade_in()
        
        if self.config.DEBUG:
            print(f"Bildschirm verdeckt für {self.config.VISIBLE_DURATION} Sekunden (Explorer-Neustart läuft)...")
        
        # Sichtbar bleiben während Desktop wechselt
        time.sleep(self.config.VISIBLE_DURATION)
        
        if self.config.DEBUG:
            print("Blende Bildschirm aus...")
        
        # Ausblenden
        self.fade_out()
        
        if self.config.DEBUG:
            print("Desktop-Switch abgeschlossen!")
        
        # Fenster schließen
        self.root.quit()


if __name__ == "__main__":
    if FadeConfig.DEBUG:
        print("SmartDesk - Desktop Switch Animation")
        print("=" * 40)
        print("Monitore werden erkannt...")
        
        if FadeConfig.ALLOW_ESC_EXIT:
            print("(ESC zum vorzeitigen Beenden)")
        
        print("=" * 40)
    
    fade = MultiMonitorFade()
    fade.run()
    
    if FadeConfig.DEBUG:
        print("\nSwitch-Animation abgeschlossen!")