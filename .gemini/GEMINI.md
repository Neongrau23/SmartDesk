# 🖥️ SmartDesk - Projekt-Kontext

## 📌 Projekt-Übersicht
**SmartDesk** ist ein spezialisierter Desktop-Manager für **Windows**, der über die Standard-Funktionalität von virtuellen Desktops hinausgeht. Während Windows normalerweise nur Fenster gruppiert, isoliert SmartDesk die tatsächlichen **Dateien, Icons und Hintergrundbilder** pro Desktop.

### Kern-Technologien
- **Sprache:** Python 3.8+
- **UI-Framework:** PySide6 (Qt für Python)
- **System-Schnittstellen:** Windows Registry (`winreg`), Windows API (`ctypes`)
- **Hotkey-Management:** `pynput` (in einem separaten Prozess)
- **Testing:** `pytest` mit umfangreicher Mocking-Logik für Windows-Systemaufrufe

### Architektur
Das Projekt folgt einer Service-orientierten Architektur:
- **`src/smartdesk/core/services`**: Enthält die Hauptlogik für Desktops, Icons, Wallpaper und Systemeinstellungen.
- **`src/smartdesk/ui`**: Beinhaltet die Tray-Applikation und die Einstellungs-GUIs.
- **`src/smartdesk/hotkeys`**: Ein isolierter Prozess zur Überwachung von Tastenkombinationen, um die UI-Performance nicht zu beeinträchtigen.
- **`src/smartdesk/shared`**: Zentralisierte Konfiguration, Lokalisierung und Logging.

---

## 🛠️ Befehle zum Bauen und Ausführen

### Installation
Das Projekt nutzt eine virtuelle Umgebung (`.venv`).
```powershell
# Installation und Setup (Windows)
.\scripts\install.bat
```

### Starten der Anwendung
```powershell
# Start über die Haupt-Datei
python main.py

# Alternativ über Batch-Datei
.\start_smartdesk.bat
```

### Tests ausführen
Das Projekt hat eine hohe Testabdeckung.
```powershell
# Alle Tests ausführen
pytest

# Tests mit Coverage-Bericht
pytest --cov=src/smartdesk
```

---

## 📝 Entwicklungs-Konventionen

- **Code-Stil:** PEP 8 wird strikt eingehalten.
- **Typisierung:** Konsequente Nutzung von Python Typ-Annotationen (`typing`).
- **Dateibenennung:** Alle Dateien und Ordner müssen **kleingeschrieben** (lowercase) sein.
- **Sprache:** Code-Kommentare und Dokumentation sind primär in Deutsch/Englisch gemischt (UI-Lokalisierung vorhanden).
- **Tests:** Neue Features müssen durch Tests in `tests/` abgesichert werden. Da viele Operationen Registry-Änderungen beinhalten, ist sorgfältiges Mocking in `conftest.py` essenziell.
- **Sicherheit:** Da die Anwendung Registry-Einträge ändert und den Explorer neu startet, ist bei Änderungen am `desktop_service.py` besondere Vorsicht geboten.

---

## 📂 Wichtige Dateien
- `main.py`: Zentraler Einstiegspunkt (Tray App).
- `pyproject.toml`: Projekt-Metadaten und Tool-Konfiguration.
- `src/smartdesk/core/services/desktop_service.py`: Logik für den Desktop-Wechsel.
- `src/smartdesk/core/services/icon_service.py`: Speichern/Wiederherstellen von Icon-Positionen.
- `src/smartdesk/shared/localization.py`: Zentrale Datei für alle UI-Texte.
