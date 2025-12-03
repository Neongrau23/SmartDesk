# 🖥️ SmartDesk

**Virtual Desktop Manager for Windows**

SmartDesk ist ein leistungsstarkes Tool zur Verwaltung mehrerer Desktops unter Windows. Wechseln Sie mühelos zwischen verschiedenen Desktop-Konfigurationen – inklusive Icons, Hintergrundbild und Ordner-Strukturen.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## ✨ Features

- 🖼️ **Mehrere Desktop-Profile** – Erstellen und verwalten Sie verschiedene Desktop-Konfigurationen
- 🔄 **Schneller Desktop-Wechsel** – Wechseln Sie per CLI, GUI oder Hotkeys zwischen Desktops
- 🎨 **Wallpaper-Verwaltung** – Eigene Hintergrundbilder für jeden Desktop
- 📍 **Icon-Positionen** – Speichern und Wiederherstellen der Desktop-Icon-Anordnung
- ⌨️ **Globale Hotkeys** – Schnelles Umschalten mit Tastenkombinationen
- 🔔 **System Tray Integration** – Zugriff auf alle Funktionen über das Tray-Icon
- 🌐 **Lokalisierung** – Mehrsprachige Unterstützung (Deutsch/Englisch)
- 💻 **CLI & GUI** – Volle Kontrolle über Kommandozeile oder grafische Oberfläche

---

## 📋 Voraussetzungen

- **Windows 10/11**
- **Python 3.8+**

---

## 🚀 Installation

### Automatische Installation (Empfohlen)

1. Repository klonen:
   ```powershell
   git clone https://github.com/Neongrau23/SmartDesk.CLI.git
   cd SmartDesk.CLI
   ```

2. Startskript ausführen:
   ```powershell
   .\scripts\start.ps1
   ```

Das Skript erstellt automatisch ein Virtual Environment, installiert alle Abhängigkeiten und startet die Tray-Anwendung.

### Manuelle Installation

1. Repository klonen:
   ```powershell
   git clone https://github.com/Neongrau23/SmartDesk.CLI.git
   cd SmartDesk.CLI
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

---

## 🎮 Verwendung

### Interaktives CLI-Menü

```powershell
python src/smartdesk/main.py
```

Das Hauptmenü bietet folgende Optionen:
- **Desktop wechseln** – Zwischen gespeicherten Desktops umschalten
- **Desktop erstellen** – Neue Desktop-Konfiguration anlegen
- **Einstellungen** – Desktops verwalten, Hotkeys, Tray-Icon etc.

### Kommandozeilen-Befehle

```powershell
# Alle Desktops auflisten
python src/smartdesk/main.py list

# Zu einem Desktop wechseln
python src/smartdesk/main.py switch <name>

# Neuen Desktop erstellen (CLI-Dialog)
python src/smartdesk/main.py create

# Neuen Desktop erstellen (GUI-Dialog)
python src/smartdesk/main.py create-gui

# Desktop löschen
python src/smartdesk/main.py delete <name>
python src/smartdesk/main.py delete <name> --delete-folder

# Hotkey-Listener starten
python src/smartdesk/main.py start-listener

# Tray-Icon starten
python src/smartdesk/main.py start-tray
```

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
SmartDesk.CLI/
├── src/smartdesk/
│   ├── main.py              # Haupteinstiegspunkt
│   ├── core/
│   │   ├── models/          # Datenmodelle (Desktop)
│   │   ├── services/        # Kern-Services (Desktop, Icons, System, Wallpaper)
│   │   ├── storage/         # Datei-Operationen
│   │   └── utils/           # Hilfsfunktionen (Registry, Backup, Validierung)
│   ├── hotkeys/             # Globale Hotkey-Verwaltung
│   ├── interfaces/
│   │   ├── cli/             # Kommandozeilen-Interface
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

## 📄 Lizenz

Dieses Projekt ist unter der [MIT-Lizenz](LICENSE) lizenziert.

---

## 🚧 Roadmap

Dieses Projekt befindet sich in aktiver Entwicklung.
Bei Fragen oder Anregungen gerne einen [Issue](https://github.com/Neongrau23/SmartDesk.CLI/issues) erstellen.

---

**Made with ❤️ and 🐍 for Windows Power Users**
