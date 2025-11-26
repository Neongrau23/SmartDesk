# SmartDesk

Ein  Desktop-Management-Tool für Windows, das mehrere Desktop-Umgebungen mit individuellen Icon-Layouts, Hintergrundbildern und Hotkeys verwaltet.

```
  ___                _   ___         _   
 / __|_ __  __ _ _ _| |_|   \ ___ __| |__
 \__ \ '  \/ _` | '_|  _| |) / -_|_-< / /
 |___/_|_|_\__,_|_|  \__|___/\___/__/_\_\
 ```

## 📋 Inhaltsverzeichnis

- [Überblick](#überblick)
- [Hauptfunktionen](#hauptfunktionen)
- [Voraussetzungen](#voraussetzungen)
- [Installation](#installation)
- [Verwendung](#verwendung)
- [Projektstruktur](#projektstruktur)
- [Konfiguration](#konfiguration)
- [Erweiterte Funktionen](#erweiterte-funktionen)
- [Entwicklung](#entwicklung)
- [Lizenz](#lizenz)

## 🎯 Überblick

SmartDesk ermöglicht es Ihnen, mehrere Desktop-Konfigurationen zu erstellen und nahtlos zwischen ihnen zu wechseln. Jeder Desktop kann individuelle Icon-Positionen, Hintergrundbilder und Ordnerstrukturen haben - perfekt für die Trennung von Arbeits- und Privatumgebungen oder verschiedenen Projekten.

### Was macht SmartDesk besonders?

- **Registry-Integration**: Direkte Windows-Registry-Manipulation für echte Desktop-Pfad-Änderungen
- **Icon-Positionsspeicherung**: Merkt sich die exakte Position jedes Desktop-Icons
- **Hintergrundbild-Verwaltung**: Weist jedem Desktop ein individuelles Hintergrundbild zu
- **Hotkey-System**: Schneller Wechsel zwischen Desktops mit Tastenkombinationen
- **System-Tray-Integration**: Diskrete Statusanzeige und schneller Zugriff
- **Animations-Engine**: Sanfte Bildschirmübergänge beim Desktop-Wechsel
- **Mehrsprachig**: Vollständige Lokalisierungsunterstützung (derzeit Deutsch)

## ✨ Hauptfunktionen

### 1. Desktop-Verwaltung

- **Erstellen**: Neue Desktops mit existierenden oder neu zu erstellenden Ordnern
- **Wechseln**: Nahtloser Wechsel zwischen verschiedenen Desktop-Umgebungen
- **Löschen**: Entfernen von Desktops mit optionalem Löschen der Ordner
- **Auflisten**: Übersicht aller konfigurierten Desktops mit Status

### 2. Icon-Management

- **Automatisches Speichern**: Icon-Positionen werden beim Wechsel automatisch gespeichert
- **Präzise Wiederherstellung**: Icons werden pixelgenau an ihrer vorherigen Position platziert
- **Manuelles Speichern**: Option zum expliziten Speichern der aktuellen Icon-Anordnung

### 3. Hintergrundbild-System

- **Desktop-spezifische Wallpaper**: Jeder Desktop kann ein eigenes Hintergrundbild haben
- **Automatisches Kopieren**: Bilder werden zentral gespeichert
- **Sofortige Anwendung**: Beim Wechsel wird das passende Hintergrundbild gesetzt

### 4. Hotkey-Listener

- **Globale Tastenkombinationen**: `Strg+Shift` gefolgt von `Alt+1` bis `Alt+9`
- **Hintergrundprozess**: Läuft unsichtbar mit `pythonw.exe`
- **Konfigurierbare Aktionen**: Jede Hotkey-Kombination kann individuell belegt werden
- **Debug-Logging**: Vollständiges Protokoll aller Hotkey-Ereignisse

### 5. System-Tray-Icon

- **Statusanzeige**: Visuelles Feedback über Hotkey-Listener-Status
- **Schnellzugriff**: Desktop-Wechsel direkt aus dem Tray-Menü
- **Desktop-Erstellung**: GUI-Dialog für neue Desktops
- **Hintergrundausführung**: Läuft fensterlos mit `pythonw.exe`

### 6. Grafische Benutzeroberfläche

- **Modernes Design**: Dark-Theme
- **Slide-In-Animation**: Elegante Einblendung von unten rechts
- **Zwei Modi**: 
  - Vorhandenen Ordner verwenden
  - Neuen Ordner erstellen
- **Browser-Integration**: Ordnerauswahl per Dialog

## 📦 Voraussetzungen

### System

- Windows 10/11
- Python 3.8 oder höher
- Administratorrechte für Registry-Zugriff (optional)

### Python-Pakete

```txt
psutil>=5.9.0        # Prozessverwaltung
pynput>=1.7.6        # Hotkey-Listener
pywin32>=305         # Windows-API-Zugriff
colorama>=0.4.6      # Terminal-Farben
pystray>=0.19.4      # System-Tray-Icon
Pillow>=10.0.0       # Bildverarbeitung
```

## 🚀 Installation

### 1. Repository klonen

```powershell
git clone https://github.com/Neongrau23/SmartDesk.CLI.git
cd SmartDesk:CLI
```

### 2. Virtuelle Umgebung erstellen

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Abhängigkeiten installieren

```powershell
pip install -r requirements.txt
# Oder mit setup.py:
pip install -e .
```

### 4. (Optional) Systemweite Installation

```powershell
pip install .
```

Nach der Installation ist der Befehl `smartdesk` global verfügbar.

## 💻 Verwendung

### Interaktives Menü

Starten Sie SmartDesk ohne Argumente für das interaktive Menü:

```powershell
python src\smartdesk\main.py
```

Oder nach der Installation:

```powershell
smartdesk
```

### Kommandozeilen-Befehle

#### Desktop erstellen

```powershell
# Textbasierter Dialog
smartdesk create

# Grafischer Dialog (von Tray-Icon verwendet)
smartdesk create-gui
```

#### Desktop wechseln

```powershell
smartdesk switch <desktop-name>
```

Beispiel:
```powershell
smartdesk switch Arbeit
```

#### Desktops auflisten

```powershell
smartdesk list
```

Ausgabe:
```
Verfügbare Desktops:
[AKTIV] Privat -> C:\Users\IhrName\Desktop\Privat
[      ] Arbeit -> D:\Projekte\Desktop-Arbeit
[      ] Gaming -> E:\Gaming\Desktop
```

#### Desktop löschen

```powershell
# Nur Eintrag löschen
smartdesk delete <desktop-name>

# Mit Ordner löschen
smartdesk delete <desktop-name> --delete-folder
# oder
smartdesk delete <desktop-name> -f
```

### Hotkey-Listener

#### Starten

```powershell
# Über interaktives Menü: Option 3 → Option 6 → Option 1 → Option 1
# Oder über Tray-Icon: Rechtsklick → Hotkey-Listener → Starten
```

#### Stoppen

```powershell
# Über interaktives Menü: Option 3 → Option 6 → Option 1 → Option 2
# Oder über Tray-Icon: Rechtsklick → Hotkey-Listener → Stoppen
```

#### Hotkeys verwenden

1. `Strg+Shift` drücken (beide Tasten)
2. Eine der beiden Tasten loslassen (aber nicht beide!)
3. `Alt+1` bis `Alt+9` drücken

Die Aktionen werden in `src/smartdesk/hotkeys/actions.pyw` definiert.

### System-Tray-Icon

#### Starten

```powershell
python src/smartdesk/main.py start-tray
```

Das Icon erscheint in der Taskleiste und zeigt den Status des Hotkey-Listeners:

- **Grau**: Listener inaktiv
- **Grün**: Listener aktiv

#### Rechtsklick-Menü

- **Desktop wechseln**: Submenu mit allen verfügbaren Desktops
- **Neuen Desktop erstellen**: Öffnet GUI-Dialog
- **Hotkey-Listener**: Start/Stop des Listeners
- **Beenden**: Schließt das Tray-Icon

## 📁 Projektstruktur

```
SmartDeskTerminal/
│
├── src/
│   └── smartdesk/
│       ├── __init__.py
│       ├── main.py              # Haupteinstiegspunkt
│       ├── config.py             # Zentrale Konfiguration
│       ├── localization.py       # Mehrsprachigkeit
│       │
│       ├── animations/           # Visuelle Effekte
│       │   ├── screen_fade.py    # Bildschirmüberblendung
│       │   ├── logo.py           # Logo-Animation
│       │   └── *_config.py       # Animationskonfigurationen
│       │
│       ├── handlers/             # Geschäftslogik
│       │   ├── desktop_handler.py       # Desktop-Verwaltung
│       │   ├── icon_manager.py          # Icon-Positionierung
│       │   ├── wallpaper_manager.py     # Hintergrundbild-System
│       │   ├── system_manager.py        # Explorer-Neustart
│       │   └── tray_icon.py             # System-Tray
│       │
│       ├── hotkeys/              # Tastenkombinationen
│       │   ├── hotkey_manager.py        # Listener-Verwaltung
│       │   ├── listener.py              # Hotkey-Erkennung
│       │   └── actions.pyw              # Aktionen-Definition
│       │
│       ├── models/               # Datenmodelle
│       │   └── desktop.py        # Desktop-Klasse
│       │
│       ├── storage/              # Datenpersistenz
│       │   └── file_operations.py       # JSON-Speicherung
│       │
│       ├── ui/                   # Benutzeroberflächen
│       │   ├── cli.py            # Terminal-Interface
│       │   ├── gui_create.py     # Tkinter-Fenster
│       │   ├── ui_manager.py     # GUI-Manager
│       │   └── style.py          # Farbschema
│       │
│       └── utils/                # Hilfsfunktionen
│           ├── registry_operations.py   # Windows-Registry
│           └── path_validator.py        # Pfad-Validierung
│
├── setup.py                      # Installationsskript
├── LICENSE                       # MIT-Lizenz
└── README.md                     # Diese Datei
```

## ⚙️ Konfiguration

### Datenspeicherung

SmartDesk speichert alle Daten in:

```
%APPDATA%\SmartDesk\
│
├── desktops.json       # Desktop-Konfigurationen
├── wallpapers/         # Hintergrundbilder
├── listener.pid        # Hotkey-Listener-PID
├── listener.log        # Hotkey-Debug-Log
└── ico/                # Tray-Icons
    ├── idle_icon.png   # Inaktiv-Status
    └── active_icon.png # Aktiv-Status
```

### Desktop-Konfiguration (desktops.json)

```json
[
  {
    "name": "Arbeit",
    "path": "C:\\Users\\IhrName\\Desktop\\Arbeit",
    "is_active": true,
    "wallpaper_path": "C:\\Users\\IhrName\\AppData\\Roaming\\SmartDesk\\wallpapers\\Arbeit.jpg",
    "icon_positionen": [
      {
        "name": "Projekt1",
        "x": 100,
        "y": 50
      }
    ]
  }
]
```

### Hotkey-Aktionen (actions.pyw)

Erstellen Sie `src/smartdesk/hotkeys/actions.pyw`:

```python
import subprocess
import sys

def action_1():
    """Alt+1: Zu Desktop 'Privat' wechseln"""
    # Für installierte Version:
    subprocess.run(["smartdesk", "switch", "Privat"])
    
    # Für Entwicklung (alternativ):
    # subprocess.run([sys.executable, "-m", "smartdesk.main", "switch", "Privat"])

def action_2():
    """Alt+2: Zu Desktop 'Arbeit' wechseln"""
    subprocess.run(["smartdesk", "switch", "Arbeit"])

def action_3():
    """Alt+3: Eigene Aktion"""
    # Ihre benutzerdefinierte Aktion hier
    pass
```

### Registry-Einträge

SmartDesk manipuliert folgende Registry-Keys:

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\
├── User Shell Folders\Desktop    (REG_EXPAND_SZ)
└── Shell Folders\Desktop          (REG_SZ)
```

## 🔧 Erweiterte Funktionen

### Explorer-Neustart-Mechanismus

SmartDesk verwendet eine dreistufige Strategie für zuverlässige Explorer-Neustarts:

1. **Prozess-Erkennung**: `psutil` überprüft ob Explorer läuft
2. **Sanftes Beenden**: `taskkill /F /IM explorer.exe`
3. **Timeout-Überwachung**: 5 Sekunden Wartezeit mit Status-Checks
4. **Neustart**: `subprocess.Popen("explorer.exe")`

### Icon-Positionierungs-System

Verwendet Windows-API (`ctypes` + `commctrl.dll`):

```python
# LVM_GETITEMCOUNT: Anzahl der Desktop-Icons
# LVM_GETITEMPOSITION: Position jedes Icons (x, y)
# LVM_SETITEMPOSITION: Wiederherstellen der Position
```

**Besonderheit**: 3-Sekunden-Timeout für Icon-Erkennung, um Explorer-Initialisierung abzuwarten.

### Hintergrundbild-API

```python
import ctypes

# SystemParametersInfoW mit SPI_SETDESKWALLPAPER
ctypes.windll.user32.SystemParametersInfoW(
    20,                    # SPI_SETDESKWALLPAPER
    0,
    wallpaper_path,
    3                      # SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
)
```

### Bildschirmüberblendung

Die `screen_fade.py` erstellt ein vollbild-schwarzes Overlay mit Tkinter:

- **Phase 1**: Fade-In (0% → 100% Deckkraft)
- **Wartezeit**: Signaldatei-Überwachung
- **Phase 2**: Fade-Out (100% → 0% Deckkraft)

### GUI-Animationen

Die `ui_manager.py` nutzt ease-out-Animationen:

```python
# Slide-In von rechts:
step = max(1, distance_to_go * 0.15)  # 15% der Restdistanz pro Frame
current_x -= step
```

## 🛠️ Entwicklung

### Projekt lokal ausführen

```powershell
# Virtuelle Umgebung aktivieren
.venv\Scripts\Activate.ps1

# Modul ausführen
python -m smartdesk.main

# Einzelne Komponenten testen
python -m smartdesk.handlers.tray_icon      # Tray-Icon testen
python -m smartdesk.animations.screen_fade  # Animation testen
python -m smartdesk.ui.gui_create           # GUI testen
```

### Debug-Modus

Setzen Sie `DEBUG=1` in den Umgebungsvariablen:

```powershell
$env:DEBUG="1"
python -m smartdesk.main
```

### Logging

Hotkey-Listener-Logs finden Sie in:

```
%APPDATA%\SmartDesk\listener.log
%APPDATA%\SmartDesk\listener_error.log
```

### Code-Struktur-Prinzipien

1. **Lokalisierung**: Alle Benutzertexte in `localization.py`
2. **Fehlerbehandlung**: Farbige Präfixe (`PREFIX_OK`, `PREFIX_ERROR`, `PREFIX_WARN`)
3. **Modularität**: Jede Funktionalität in eigenem Handler
4. **Abhängigkeits-Injektion**: Minimale Kopplung zwischen Modulen

### Neue Sprache hinzufügen

Bearbeiten Sie `src/smartdesk/localization.py`:

```python
TEXT = {
    "de": {
        "ui.menu.main.switch": "Desktop wechseln",
        # ...
    },
    "en": {
        "ui.menu.main.switch": "Switch desktop",
        # ...
    }
}
```


## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Siehe [LICENSE](LICENSE) für Details.

```
MIT License

Copyright (c) 2025 Neongrau23

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Entwickelt mit 🐍 von Neongrau23**
