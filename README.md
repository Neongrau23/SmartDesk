# 🖥️ SmartDesk.CLI

**Eine professionelle Python-Anwendung zur Verwaltung virtueller Desktop-Umgebungen unter Windows.**

SmartDeskTerminal ermöglicht es, intuitiv zwischen verschiedenen Desktop-Ordnern zu wechseln (z.B. "Arbeit", "Gaming", "Privat"). Anders als virtuelle Desktops von Windows, die nur Fenster organisieren, verwaltet SmartDeskTerminal die tatsächlichen Dateien und Verknüpfungen auf deinem Desktop durch intelligente Manipulation der Windows Registry.

## ✨ Features

### 🚀 Hauptfunktionen

**Schneller Wechsel**: Tausche deinen Desktop-Inhalt in Sekunden aus.

**CLI-Interface**: Schlanke, terminalbasierte Bedienung für maximale Kontrolle.

**Explorer Integration**: Automatischer Neustart des Windows Explorers, um Änderungen sofort sichtbar zu machen.

### 🛡️ Sicherheit & Stabilität

**Self-Healing Status**: Das Programm prüft beim Start die echte Windows-Registry und synchronisiert den Status. Wenn du den Desktop manuell änderst, erkennt SmartDeskTerminal das automatisch.

**Schutzmechanismen**: Verhindert das versehentliche Löschen des Desktops, der gerade aktiv ist.

### 📂 Dateisystem-Management

**Automatische Ordner**: Erstellt auf Wunsch automatisch Unterordner beim Anlegen neuer Desktops.

**Verschieben & Umbenennen**: Wenn du einen Desktop in der App umbenennst oder den Pfad änderst, werden die echten Ordner auf der Festplatte automatisch mit verschoben.

**Sauberes Löschen**: Optionale Funktion, um beim Entfernen eines Desktops auch die Dateien auf der Festplatte unwiderruflich zu löschen.

## 🛠️ Installation

Das Projekt nutzt keine externen Abhängigkeiten. Es basiert rein auf der Python Standard Library (tkinter, winreg, shutil, json).

### Voraussetzungen

- Windows 10 oder 11
- Python 3.8 oder höher

### Setup

1. Repository klonen:
```bash
git clone https://github.com/Neongrau23/SmartDesk.CLI.git
cd SmartDesk.CLI
```

2. Starten:
```bash
python src/smartdesk/main.py
```

## 📖 Benutzung

### Kommandozeile (CLI)

SmartDeskTerminal bietet eine terminalbasierte Benutzeroberfläche für effiziente Desktop-Verwaltung:

```bash
python src/smartdesk/main.py
```

Das CLI bietet folgende Funktionen:
- **Desktop-Übersicht**: Zeigt alle konfigurierten Desktops an
- **Wechseln**: Schneller Wechsel zwischen verschiedenen Desktop-Umgebungen
- **Erstellen**: Neue Desktop-Konfigurationen anlegen
- **Verwalten**: Desktops umbenennen, verschieben oder löschen
- **Status-Synchronisation**: Automatische Erkennung manueller Registry-Änderungen

## 🏗️ Projektstruktur

Das Projekt folgt strikten "Clean Code" Prinzipien und einer modularen Paketstruktur:

```
SmartDesk.CLI/
├── src/smartdesk/
│   ├── main.py                # Einstiegspunkt der Anwendung
│   ├── config.py              # Zentrale Konfiguration
│   ├── handlers/              # Geschäftslogik (Business Logic)
│   │   ├── desktop_handler.py # Core-Logik & Registry Sync
│   │   └── system_manager.py  # Windows-Prozesssteuerung
│   ├── models/                # Datenmodelle (Dataclasses)
│   ├── storage/               # JSON-Datenbankzugriff
│   ├── ui/                    # Benutzeroberfläche
│   │   ├── cli.py             # Terminal-Interface
│   │   └── dialogs.py         # Interaktive Eingaben
│   └── utils/                 # Hilfsfunktionen (Registry/Pfade)
├── data/                      # Persistente Daten (wird automatisch erstellt)
│   └── desktops.json          # Desktop-Konfigurationen
└── LICENSE                    # MIT License
```

## ⚙️ Technische Details

### Registry-Integration

SmartDeskTerminal manipuliert folgende Windows Registry-Einträge:
```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders
```

Das Programm ändert den `Desktop`-Wert, um den Pfad des aktiven Desktop-Ordners zu steuern.

### Datenspeicherung

Alle Desktop-Konfigurationen werden in einer lokalen JSON-Datei (`data/desktops.json`) gespeichert, die beim ersten Start automatisch erstellt wird.

## ⚠️ Wichtiger Hinweis

Dieses Tool ändert Einträge in der Windows Registry. Obwohl umfangreiche Sicherheitschecks implementiert sind (z.B. Self-Healing Status, Abgleich vor dem Löschen), erfolgt die Nutzung auf eigene Gefahr. 

**Empfehlungen:**
- Erstelle vor der ersten Nutzung ein Backup wichtiger Desktop-Dateien
- Teste das Tool zunächst mit unwichtigen Test-Desktops
- Schließe alle wichtigen Programme, bevor du den Desktop wechselst

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe [LICENSE](LICENSE) für Details.

## 🤝 Beitragen

Contributions, Issues und Feature-Requests sind willkommen! Fühle dich frei, das [Issues](https://github.com/Neongrau23/SmartDeskTerminal/issues) zu nutzen.

---

Entwickelt mit 🐍 von [Neongrau23](https://github.com/Neongrau23)
