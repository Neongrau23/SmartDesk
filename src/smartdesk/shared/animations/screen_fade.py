# -*- coding: utf-8 -*-
"""
Desktop-Switch Fade-Animation für SmartDesk
Startet Logo-Fenster als separaten Prozess
Wartet auf eine Signal-Datei (.lock), um sich zu beenden.
"""
import tkinter as tk
import time
import subprocess
import os
import sys

# Importiere die zentrale Konfiguration aus config.py
try:
    from ..config import AnimationConfig as FadeConfig
except ImportError:
    print("WARNUNG: Konnte zentrale Konfiguration nicht laden.")
    print("Versuche lokalen Fallback...")
    try:
        from fade_config import FadeConfig
    except ImportError:
        print("FATALER FEHLER: Keine Konfiguration gefunden.")
        # Fallback-Klasse, damit das Skript nicht sofort abstürzt

        class FadeConfig:
            FADE_IN_DURATION = 0.2
            FADE_OUT_DURATION = 0.3
            VISIBLE_DURATION = 3.5
            FADE_STEPS = 100
            BACKGROUND_COLOR = 'Black'
            SHOW_LOGO = True
            HIDE_CURSOR = True
            TOPMOST = True
            INITIAL_DELAY = 0
            DEBUG = True
            ALLOW_ESC_EXIT = True


# win32api wird benötigt, um die volle Größe über MEHRERE Monitore zu ermitteln
try:
    import win32api

    HAS_WIN32API = True
except ImportError:
    print("=" * 50)
    print("FEHLER: 'pywin32' wird benötigt, um mehrere Monitore zu erkennen.")
    print("Bitte installieren: pip install pywin32")
    print("Fallback auf primären Monitor...")
    print("=" * 50)
    HAS_WIN32API = False


class MultiMonitorFade:
    def __init__(self, config=None):
        """
        Initialisierung mit optionaler Konfiguration

        Args:
            config: FadeConfig-Instanz oder None für Standardwerte
        """
        self.config = config or FadeConfig()

        # --- Signaldatei aus Argumenten empfangen ---
        self.signal_file = sys.argv[1] if len(sys.argv) > 1 else None

        self.root = tk.Tk()
        self.root.title("SmartDesk Desktop Switch")

        # Entfernt alle Fensterdekorationen (Titelleiste, Ränder)
        self.root.overrideredirect(True)

        if self.config.TOPMOST:
            self.root.attributes('-topmost', True)

        self.root.configure(bg=self.config.BACKGROUND_COLOR)

        # Mauszeiger verstecken
        if self.config.HIDE_CURSOR:
            self.root.config(cursor="none")

        # ESC zum Beenden
        if self.config.ALLOW_ESC_EXIT:
            self.root.bind('<Escape>', lambda e: self.cleanup_and_exit())

        # Variablen für die Gesamtgröße
        self.virtual_width = 0
        self.virtual_height = 0

        # Logo-Prozess
        self.logo_process = None

        # Gesamten Bildschirmbereich über alle Monitore ermitteln
        self.setup_fullscreen()

        # Canvas für Fade-Effekt
        self.canvas = tk.Canvas(
            self.root, bg=self.config.BACKGROUND_COLOR, highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Schwarzes Rechteck als Overlay
        self.rect = self.canvas.create_rectangle(
            0,
            0,
            self.virtual_width,
            self.virtual_height,
            fill=self.config.BACKGROUND_COLOR,
            outline='',
        )

    def setup_fullscreen(self):
        """Fenster über alle Monitore strecken"""

        if HAS_WIN32API:
            # Metriken für den "virtuellen Desktop" (alle Monitore)
            SM_XVIRTUALSCREEN = 76
            SM_YVIRTUALSCREEN = 77
            SM_CXVIRTUALSCREEN = 78
            SM_CYVIRTUALSCREEN = 79

            # Ermittle die Koordinaten der oberen linken Ecke des virtuellen Desktops
            x = win32api.GetSystemMetrics(SM_XVIRTUALSCREEN)
            y = win32api.GetSystemMetrics(SM_YVIRTUALSCREEN)

            # Ermittle die Gesamtbreite und -höhe aller Monitore
            self.virtual_width = win32api.GetSystemMetrics(SM_CXVIRTUALSCREEN)
            self.virtual_height = win32api.GetSystemMetrics(SM_CYVIRTUALSCREEN)

            # Erstelle den Geometrie-String: 'BreitexHöhe+X+Y'
            geometry = f'{self.virtual_width}x{self.virtual_height}+{x}+{y}'

            if self.config.DEBUG:
                print(f"Erkannter virtueller Desktop: {geometry}")
                print(f"Position: ({x}, {y})")
                print(f"Größe: {self.virtual_width}x{self.virtual_height}")

        else:
            # FALLBACK (Alte Methode, nur primärer Monitor)
            self.virtual_width = self.root.winfo_screenwidth()
            self.virtual_height = self.root.winfo_screenheight()
            geometry = f'{self.virtual_width}x{self.virtual_height}+0+0'

            if self.config.DEBUG:
                print(
                    f"Erkannte Bildschirmgröße (Fallback): {self.virtual_width}x{self.virtual_height}"
                )

        # Setze die Fenstergeometrie
        self.root.geometry(geometry)

    def start_logo(self):
        """Logo-Fenster als separaten Prozess starten"""
        if not self.config.SHOW_LOGO:
            return

        try:
            # Pfad zur logo.py ermitteln
            script_dir = os.path.dirname(os.path.abspath(__file__))
            logo_script = os.path.join(script_dir, 'logo.py')

            if not os.path.exists(logo_script):
                if self.config.DEBUG:
                    print(f"WARNUNG: Logo-Script nicht gefunden: {logo_script}")
                return

            # --- Signal-Pfad an Logo-Prozess übergeben ---
            cmd = [sys.executable, logo_script]
            if self.signal_file:
                cmd.append(self.signal_file)

            # Logo-Prozess starten
            # DETACHED_PROCESS sorgt dafür, dass das Logo-Fenster unabhängig läuft
            if sys.platform == 'win32':
                # Windows: Verwende CREATE_NO_WINDOW Flag
                CREATE_NO_WINDOW = 0x08000000
                self.logo_process = subprocess.Popen(
                    cmd,
                    creationflags=CREATE_NO_WINDOW,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                # Linux/Mac
                self.logo_process = subprocess.Popen(
                    cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )

            if self.config.DEBUG:
                print(f"Logo-Prozess gestartet (PID: {self.logo_process.pid})")

        except Exception as e:
            if self.config.DEBUG:
                print(f"Fehler beim Starten des Logo-Fensters: {e}")

    def stop_logo(self):
        """Logo-Prozess beenden (falls noch aktiv)"""
        if self.logo_process and self.logo_process.poll() is None:
            try:
                self.logo_process.terminate()
                self.logo_process.wait(timeout=1)
                if self.config.DEBUG:
                    print("Logo-Prozess beendet")
            except Exception as e:
                if self.config.DEBUG:
                    print(f"Fehler beim Beenden des Logo-Prozesses: {e}")

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
        try:
            if self.config.DEBUG:
                print("Blende Bildschirm ein...")

            # Schnell einblenden
            self.fade_in()

            # Logo-Prozess starten (läuft parallel)
            if self.config.SHOW_LOGO:
                self.start_logo()
                time.sleep(0.3)  # Kurz warten, damit Logo-Fenster erscheint

            # --- Warten auf Signal statt fester Zeit ---
            if self.config.DEBUG:
                print(f"Bildschirm verdeckt. Warte auf Signal...")

            self.wait_for_signal()
            # --- (Die alte time.sleep()-Zeile wurde entfernt) ---

            # Logo-Prozess beenden (falls noch aktiv)
            if self.config.SHOW_LOGO:
                self.stop_logo()

            if self.config.DEBUG:
                print("Blende Bildschirm aus...")

            # Ausblenden
            self.fade_out()

            if self.config.DEBUG:
                print("Desktop-Switch abgeschlossen!")

        except Exception as e:
            if self.config.DEBUG:
                print(f"Fehler während Fade-Animation: {e}")
                import traceback

                traceback.print_exc()
        finally:
            self.cleanup_and_exit()

    def cleanup_and_exit(self):
        """Sauberes Beenden"""
        # Logo-Prozess beenden
        self.stop_logo()

        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass

    def wait_for_signal(self):
        """Wartet darauf, dass die Signaldatei vom aufrufenden Prozess gelöscht wird."""
        if not self.signal_file:
            # Fallback auf feste Zeit, wenn keine Signaldatei übergeben wurde
            if self.config.DEBUG:
                print(
                    f"Keine Signaldatei. Nutze feste Dauer: {self.config.VISIBLE_DURATION}s"
                )
            time.sleep(self.config.VISIBLE_DURATION)
            return

        if self.config.DEBUG:
            print(f"Warte auf Löschung der Signaldatei: {self.signal_file}")

        start_time = time.time()
        # Maximales Timeout, falls der Hauptprozess abstürzt
        max_wait_seconds = 30

        try:
            # Warte solange die Datei existiert
            while os.path.exists(self.signal_file):
                time.sleep(0.1)
                # Root-Update ist wichtig, damit das Fenster nicht einfriert
                self.root.update_idletasks()
                self.root.update()

                if time.time() - start_time > max_wait_seconds:
                    if self.config.DEBUG:
                        print(f"Timeout: Warte {max_wait_seconds}s. Breche ab.")
                    break

            if self.config.DEBUG:
                print("Signaldatei wurde gelöscht (oder Timeout). Fahre fort.")

        except Exception as e:
            if self.config.DEBUG:
                print(f"Fehler beim Warten auf Signaldatei: {e}")


if __name__ == "__main__":
    if FadeConfig.DEBUG:
        print("SmartDesk - Desktop Switch Animation")
        print("=" * 40)
        print("Monitore werden erkannt...")

        if FadeConfig.ALLOW_ESC_EXIT:
            print("(ESC zum vorzeitigen Beenden)")

        print("=" * 40)

    try:
        fade = MultiMonitorFade()
        fade.run()
    except Exception as e:
        print(f"FEHLER: {e}")
        import traceback

        traceback.print_exc()

    if FadeConfig.DEBUG:
        print("\nSwitch-Animation abgeschlossen!")
