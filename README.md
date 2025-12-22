# 🖥️ SmartDesk

**Virtual Desktop Manager for Windows**

SmartDesk ist ein Tool zur Verwaltung mehrerer Desktops unter Windows. Wechseln Sie mühelos zwischen verschiedenen Desktop-Konfigurationen.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## ✨ Features

- 🖼️ **Mehrere Desktop-Profile** – Erstellen und verwalten Sie verschiedene Desktop-Konfigurationen
- 🔄 **Schneller Desktop-Wechsel** – Wechseln Sie per GUI oder Hotkeys zwischen Desktops
- 🎨 **Wallpaper-Verwaltung** – Eigene Hintergrundbilder für jeden Desktop
- 📍 **Icon-Positionen** – Automatisches Speichern und Wiederherstellen der Desktop-Icon-Anordnung
- ⌨️ **Globale Hotkeys** – Schnelles Umschalten mit Tastenkombinationen
- 🔔 **System Tray Integration** – Zugriff auf alle Funktionen über das Tray-Icon

---

## 🚀 Installation

### Voraussetzungen

- **Windows 10/11**
- **Python 3.10+** muss installiert sein ([Download](https://www.python.org/downloads/))

### Automatische Installation (Empfohlen)

1. Repository klonen oder herunterladen:
   ```powershell
   git clone https://github.com/Neongrau23/SmartDesk.git
   cd SmartDesk
   ```

2. Installationsskript ausführen:
   ```powershell
   # Per Doppelklick oder Terminal:
   .\scripts\install.bat
   ```

Das Skript führt automatisch folgende Schritte aus:
1. ✅ Prüft Python-Version und Systemanforderungen
2. ✅ Erstellt ein Virtual Environment (`.venv/`)
3. ✅ Installiert alle Abhängigkeiten
4. ✅ Erstellt den AppData-Ordner mit Standardkonfiguration
5. ✅ Erstellt den **geschützten "Original Desktop"** (Backup des Ausgangszustands)

> **💡 Hinweis:** Der automatisch erstellte "Original Desktop" speichert Ihre aktuellen Desktop-Icons und das Wallpaper. Bei einer Deinstallation kann dieser Zustand einfach wiederhergestellt werden.

### Manuelle Installation

Falls Sie die Installation manuell durchführen möchten:

1. Repository klonen:
   ```powershell
   git clone https://github.com/Neongrau23/SmartDesk.git
   cd SmartDesk
   ```

2. Virtual Environment erstellen und aktivieren:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Abhängigkeiten installieren:
   ```powershell
   pip install -r requirements.txt
   ```

4. Erster Start (erstellt Original Desktop und startet Tray-Icon):
   ```powershell
   python src/smartdesk/main.py
   ```

---

## 🎮 Verwendung

### ⌨️ Hotkeys & Overlay

SmartDesk nutzt ein zweistufiges System, um versehentliche Eingaben zu verhindern und Konflikte mit anderen Programmen zu minimieren:

1. **Aktivieren:** Drücken Sie `Strg` + `Shift`, um die Hotkey-Steuerung zu wecken.
2. **Wechseln:** Drücken Sie anschließend `Alt` + `1` bis `9`, um direkt zum jeweiligen Desktop zu springen.
3. **Overlay (HUD):** Wenn Sie nach der Aktivierung (`Strg` + `Shift`) die `Alt`-Taste gedrückt halten, erscheint ein Overlay auf dem Bildschirm. Dieses zeigt Ihnen:
   - Alle verfügbaren Desktops
   - Welcher Desktop aktuell aktiv ist

### Steuerung per Tray-Icon

Die gesamte Verwaltung von SmartDesk erfolgt über das Icon im System-Tray (neben der Uhr). Ein Rechtsklick auf das Icon öffnet das Hauptmenü, mit dem Sie:
- Zwischen Desktops wechseln
- Neue Desktops erstellen
- Bestehende Desktops verwalten (umbenennen, löschen etc.)
- Die Hotkey-Überwachung (Listener) starten oder stoppen
- Die Anwendung beenden können

---

## ⚙️ Konfiguration

Die Konfiguration wird im AppData-Verzeichnis gespeichert:

```
%APPDATA%\SmartDesk\
├── desktops.json      # Desktop-Konfigurationen
├── wallpapers\        # Gespeicherte Hintergrundbilder
├── listener.pid       # Hotkey-Listener PID
└── listener.log       # Hotkey-Listener Log
```

---

## 🏗️ Projektstruktur

```
SmartDesk/
├── src/smartdesk/
│   ├── main.py              # Haupteinstiegspunkt
│   ├── core/
│   │   ├── models/          # Datenmodelle (Desktop)
│   │   ├── services/        # Kern-Services (Desktop, Icons, System, Wallpaper)
│   │   ├── storage/         # Datei-Operationen
│   │   └── utils/           # Hilfsfunktionen (Registry, Backup, Validierung)
│   ├── hotkeys/             # Globale Hotkey-Verwaltung
│   ├── interfaces/
│   │   ├── gui/             # Grafische Oberfläche (CustomTkinter)
│   │   └── tray/            # System Tray Integration
│   └── shared/              # Geteilte Module (Config, Lokalisierung, Style)
├── scripts/                 # Hilfsskripte (Backup, Restore, Start)
└── tests/                   # Unit Tests
```

---

## 🧪 Tests

Tests mit pytest ausführen:

```powershell
# Alle Tests
pytest

# Mit Coverage-Report
pytest --cov=src/smartdesk --cov-report=html

# Spezifische Tests
pytest tests/test_desktop_handler.py -v
```

---

## 📦 Abhängigkeiten

| Paket | Beschreibung |
|-------|--------------|
| `psutil` | Prozess- und System-Utilities |
| `pynput` | Globale Hotkey-Erkennung |
| `pywin32` | Windows API-Zugriff |
| `colorama` | Farbige Terminal-Ausgabe |
| `pystray` | System Tray Integration |
| `Pillow` | Bildverarbeitung |
| `customtkinter` | Moderne GUI-Komponenten |

---

## 🗑️ Deinstallation

SmartDesk erstellt beim ersten Start automatisch einen **geschützten "Original" Desktop**, der den Ausgangszustand Ihres Systems speichert. 

### Automatische Deinstallation (Empfohlen)

Führen Sie einfach das Deinstallations-Skript aus:

```powershell
# Per Doppelklick oder Terminal:
.\scripts\uninstall.bat

# Oder direkt mit Python:
python scripts/uninstall.py
```

Das Skript führt automatisch folgende Schritte aus:
1. ✅ Wechselt zum Original Desktop (stellt Ausgangszustand wieder her)
2. ✅ Stoppt alle laufenden Dienste (Listener, Tray)
3. ✅ Löscht den SmartDesk-Ordner in AppData (mit Bestätigung)

**Optionen:**
```powershell
python scripts/uninstall.py --keep-data   # Behält AppData-Ordner
python scripts/uninstall.py --force       # Keine Bestätigungen
```

### Manuelle Deinstallation

Falls das Skript nicht funktioniert:

1. **Original-Desktop aktivieren** (wichtig!):
   - Öffnen Sie SmartDesk über das Tray-Icon
   - Wechseln Sie zum Desktop **"🔒 Original (Datum)"**

2. **Dienste stoppen & Daten löschen**:
   - Beenden Sie die Anwendung über das Tray-Menü ("Beenden").
   - Löschen Sie den Konfigurationsordner: `Remove-Item -Recurse "$env:APPDATA\SmartDesk"`

> **💡 Tipp:** Durch das Aktivieren des Original-Desktops wird sichergestellt, dass alle Registry-Einträge auf den ursprünglichen Zustand zurückgesetzt werden.

---

## ⚠️ Hinweise

- **Administrator-Rechte**: Einige Funktionen (Registry-Änderungen) benötigen Administrator-Rechte
- **Registry-Backup**: Bei der ersten Ausführung wird automatisch ein Backup der Desktop-Registry-Einträge erstellt
- **Explorer-Neustart**: Desktop-Wechsel erfordern einen Neustart des Windows Explorers

---

## 🔧 Entwicklung

### Entwicklungsabhängigkeiten installieren

```powershell
pip install -r requirements-dev.txt
```

### Registry-Backup wiederherstellen

Falls Probleme auftreten, kann die ursprüngliche Desktop-Registry wiederhergestellt werden:

```powershell
.\scripts\restore.bat
```

---

## 🚧 Beta-Status & Sicherheit

Dieses Projekt befindet sich aktuell noch in der **Entwicklungsphase**. Obwohl SmartDesk Mechanismen zum Schutz Ihrer Daten integriert hat, wird empfohlen, sicherheitshalber manuelle Backups wichtiger Registry-Schlüssel zu erstellen, falls unerwartete Fehler auftreten.

**So erstellen Sie ein Backup:**
1. Drücken Sie `Windows` + `R`, geben Sie `regedit` ein und drücken Sie `Enter`.
2. Navigieren Sie zu den folgenden Pfaden und exportieren Sie diese (Rechtsklick > Exportieren):

* `Computer\HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders`
* `Computer\HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders`

Diese Schlüssel steuern die Pfade zu Ihrem Desktop und anderen Systemordnern. 

**Wiederherstellung:** Sollte ein Fehler auftreten, können Sie den ursprünglichen Zustand einfach wiederherstellen, indem Sie die exportierten `.reg`-Dateien **doppelklicken** und die Abfrage bestätigen.

---

## 📄 Lizenz

Dieses Projekt ist unter der [MIT-Lizenz](LICENSE) lizenziert.

---

**Made with ❤️ and 🐍 for Windows Power Users**