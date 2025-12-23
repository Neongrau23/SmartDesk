import win32gui
from pynput import keyboard

# Globale Variablen, um den Zustand der Tasten zu speichern
ctrl_gedrueckt = False
shift_gedrueckt = False

def fokus_auf_taskleiste_setzen():
    """Sucht das Fensterhandle der Taskleiste und setzt den Fokus darauf."""
    try:
        # Der Klassenname der Windows-Taskleiste ist "Shell_TrayWnd"
        hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
        if hwnd:
            # Setzt das Fenster in den Vordergrund, was es effektiv fokussiert
            win32gui.SetForegroundWindow(hwnd)
            print("Taskleiste fokussiert.")
        else:
            print("Taskleiste nicht gefunden.")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")

def bei_tastendruck(key):
    """Wird aufgerufen, wenn eine Taste gedrückt wird."""
    global ctrl_gedrueckt, shift_gedrueckt

    # Prüfen, ob Strg oder Shift gedrückt wurde
    if key in {keyboard.Key.ctrl_l, keyboard.Key.ctrl_r}:
        ctrl_gedrueckt = True
    elif key in {keyboard.Key.shift_l, keyboard.Key.shift_r}:
        shift_gedrueckt = True
    # Wenn Alt gedrückt wird, während Strg und Shift bereits gehalten werden
    elif key in {keyboard.Key.alt_l, keyboard.Key.alt_r}:
        if ctrl_gedrueckt and shift_gedrueckt:
            print("Hotkey Strg+Shift+Alt erkannt!")
            fokus_auf_taskleiste_setzen()

def bei_tastenloslassen(key):
    """Wird aufgerufen, wenn eine Taste losgelassen wird."""
    global ctrl_gedrueckt, shift_gedrueckt
    
    # Zustand zurücksetzen, wenn die Tasten losgelassen werden
    if key in {keyboard.Key.ctrl_l, keyboard.Key.ctrl_r}:
        ctrl_gedrueckt = False
    elif key in {keyboard.Key.shift_l, keyboard.Key.shift_r}:
        shift_gedrueckt = False
    
    # Das Skript mit der Escape-Taste beenden
    if key == keyboard.Key.esc:
        return False

# Hauptteil des Skripts
if __name__ == "__main__":
    print("Listener für Hotkey Strg+Shift+Alt gestartet...")
    print("Drücken Sie ESC, um das Skript zu beenden.")
    
    # Startet den Listener, der im Hintergrund auf Tastatureingaben wartet
    with keyboard.Listener(on_press=bei_tastendruck, on_release=bei_tastenloslassen) as listener:
        listener.join()
        
    print("Listener beendet.")

