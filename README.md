# 🖥️ SmartDesk Manager

**Eine professionelle Python-Anwendung zur Verwaltung virtueller Desktop-Umgebungen unter Windows.**

SmartDesk ermöglicht es, intuitiv per Knopfdruck zwischen verschiedenen Desktop-Ordnern zu wechseln (z.B. "Arbeit", "Gaming", "Privat"). Anders als virtuelle Desktops von Windows, die nur Fenster sortieren, ändert SmartDesk den tatsächlichen Speicherort des Desktops. So hast du immer nur die Dateien vor Augen, die du gerade brauchst.

## ✨ Features

### 🚀 Hauptfunktionen

**Schneller Wechsel**: Tausche deinen Desktop-Inhalt in Sekunden aus.

**Single-Window GUI**: Moderne, übersichtliche Oberfläche (basierend auf Tkinter).

**Explorer Integration**: Automatischer Neustart des Windows Explorers, um Änderungen sofort sichtbar zu machen.

### 🛡️ Sicherheit & Stabilität

**Self-Healing Status**: Das Programm prüft beim Start die echte Windows-Registry und synchronisiert den Status. Wenn du den Desktop manuell änderst, erkennt SmartDesk das.

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
git clone https://github.com/Neongrau23/SmartDesk.git
cd SmartDesk
```

2. Starten:
```bash
python src/smartdesk/main.py
```

## 📖 Benutzung

### Grafische Oberfläche (Standard)

Startet das Programm im Fenster-Modus.

- **Dashboard**: Zeigt alle Desktops. Der aktive ist mit einem Haken (✔) markiert.
- **Erstellen**: Gib einen Namen und einen Pfad an. Die Live-Vorschau zeigt dir genau, wo der Ordner landet.
- **Wechseln**: Wähle einen Desktop und klicke "Wechseln". Bestätige den Explorer-Neustart.
- **Einstellungen**: Klicke oben rechts auf "Einstellungen" -> "Desktops Verwalten", um Desktops umzubenennen, zu verschieben oder zu löschen (Klick auf das Zahnrad ⚙).

### Kommandozeile (CLI)

Für Puristen oder Batch-Skripte steht ein Text-Modus zur Verfügung:

```bash
python src/smartdesk/main.py --cli
```

## 🏗️ Projektstruktur

Das Projekt folgt strikten "Clean Code" Prinzipien und einer modularen Paketstruktur:

```
src/smartdesk/
├── main.py                # Einstiegspunkt (Router zwischen GUI/CLI)
├── config.py              # Zentrale Konfiguration
├── handlers/              # Geschäftslogik (Business Logic)
│   ├── desktop_handler.py # Core-Logik & Registry Sync
│   └── system_manager.py  # Windows-Prozesssteuerung
├── models/                # Datenmodelle (Dataclasses)
├── storage/               # JSON-Datenbankzugriff
├── ui/                    # Benutzeroberfläche (View)
│   ├── gui.py             # Hauptfenster & Frame-Navigation
│   ├── pages.py           # Die einzelnen Ansichten
│   └── dialogs.py         # Popups (Erstellen/Löschen etc.)
└── utils/                 # Hilfsfunktionen (Registry/Pfade)
```

## ⚠️ Wichtiger Hinweis

Dieses Tool ändert Einträge in der Windows Registry unter:
```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders
```

Obwohl umfangreiche Sicherheitschecks implementiert sind (z.B. Abgleich vor dem Löschen), erfolgt die Nutzung auf eigene Gefahr. Backups wichtiger Daten werden empfohlen.

---

Entwickelt mit 🐍 in Python.
