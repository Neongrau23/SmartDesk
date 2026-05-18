# Dokumentation: `main.py`

Diese Datei dient als zentraler Einstiegspunkt (Bootstrapper) der SmartDesk-Anwendung. Im Folgenden sind die Abhängigkeiten und Verbindungen zu anderen Skripten und Dateien des Projekts dokumentiert.

### tray_icon.py
Dieses Modul enthält die Hauptlogik für die grafische Benutzeroberfläche (Tray-Icon). Die `main.py` stellt die Verbindung her, indem sie die Klasse importiert, mit den Systemargumenten initialisiert und die Event-Schleife (`exec()`) anstößt. Hier findet der Übergang vom Startskript zur eigentlichen Anwendung statt.

```python
from smartdesk.ui.tray.tray_icon import SmartDeskTrayApp

app = SmartDeskTrayApp(sys.argv)
sys.exit(app.exec())
```
**Links:** [Markdown](src/smartdesk/ui/tray/tray_icon.py.md), [Projekt](../../src/smartdesk/ui/tray/tray_icon.py)

---

### src/ (Basis-Quellcodeverzeichnis)
Um sicherzustellen, dass das Skript projektinterne Module (wie das oben genannte `tray_icon.py`) überhaupt finden kann, muss das Stammverzeichnis der Quellcodes bekannt sein. Die `main.py` ermittelt den Pfad dynamisch und injiziert ihn in den Modulsuchpfad. Dies ist die Grundlage dafür, dass **alle** weiteren internen Skripte miteinander kommunizieren können.

```python
src_dir = os.path.join(project_root, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
```
**Links:** [Markdown](src/), [Projekt](../../src)

---

### smartdesk_error.log
Dies ist eine dynamisch generierte Log-Datei auf Root-Ebene. Wenn die Verbindung zu den anderen Skripten fehlschlägt (z. B. durch einen `ImportError`, weil das `src`-Verzeichnis fehlt oder fehlerhaft ist), fungiert die `main.py` als letzte Instanz. Sie fängt den Absturz ab und schreibt den Fehler in diese Datei, anstatt ihn nur unsichtbar in der Konsole verpuffen zu lassen.

```python
except ImportError as e:
    with open("smartdesk_error.log", "a") as f:
        f.write("----------- DETAILED IMPORT TRACEBACK -----------\n")
        traceback.print_exc(file=f)
        f.write(f"\nIMPORT ERROR: {e}\n")
    sys.exit(1)
```
**Links:** [Markdown](smartdesk_error.log.md), [Projekt](../../smartdesk_error.log)
