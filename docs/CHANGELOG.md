# Changelog

Alle nennenswerten Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), und dieses Projekt folgt [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Geplant
- Plugin-System für Erweiterungen.
- Verbesserte UI/UX-Anpassungsmöglichkeiten.

## [0.5.8] - 2023-10-27

### Behoben (`Fixed`)
- Ein Fehler wurde behoben, bei dem das Desktop-Fenster (`SysListView32`) auf Systemen mit mehreren Monitoren nicht immer korrekt gefunden wurde.
- Fehler in der Hotkey-Registrierung behoben, der bei seltenen Tastenkombinationen auftreten konnte.

### Geändert (`Changed`)
- Das Logging wurde verbessert, um detailliertere Informationen bei Fehlern zu liefern und die Fehlersuche zu erleichtern.
- Interne Pfadbehandlung normalisiert nun konsequenter auf Windows-Backslashes, um Registry-Fehler zu vermeiden.

### Hinzugefügt (`Added`)
- Tooltips in der Benutzeroberfläche hinzugefügt, um die Bedienung und Konfiguration der einzelnen Optionen zu erleichtern.

## [0.5.0] - 2023-09-15

### Hinzugefügt (`Added`)
- **Auto-Switch-Funktion:** SmartDesk kann nun automatisch den Desktop wechseln, wenn eine bestimmte Anwendung gestartet wird.
- Ein Einstellungsbereich in der GUI wurde hinzugefügt, um Regeln für den Auto-Switch zu erstellen und zu verwalten.

### Geändert (`Changed`)
- Der Neustart des Windows Explorers wird nun über das `psutil`-Paket anstelle eines PowerShell-Subprozesses gesteuert. Dies verbessert die Geschwindigkeit des Desktop-Wechsels und die Zuverlässigkeit erheblich.

## [0.4.0] - 2023-08-01

### Hinzugefügt (`Added`)
- **Globale Hotkeys:** Unterstützung für systemweite Tastenkombinationen zum schnellen Wechseln zwischen Desktops und zum Anzeigen der Übersicht wurde implementiert.
- Ein Einstellungsbereich zur Konfiguration der Hotkeys wurde hinzugefügt.

### Behoben (`Fixed`)
- Ein Problem wurde behoben, bei dem die Wiederherstellung von Icon-Positionen fehlschlug, wenn die Windows-Einstellung "Am Raster ausrichten" aktiv war. Diese wird nun während des Vorgangs temporär deaktiviert.

## [0.3.0] - 2023-06-20

### Hinzugefügt (`Added`)
- Jedem virtuellen Desktop kann nun ein individuelles Hintergrundbild zugewiesen werden.
- Die Anwendung speichert die Bilder im eigenen Datenverzeichnis, um sie vor versehentlichem Löschen zu schützen.

### Geändert (`Changed`)
- Das UI-Framework wurde von Tkinter/CustomTkinter auf **PySide6** umgestellt, um eine modernere und flexiblere Benutzeroberfläche zu ermöglichen.

### Behoben (`Fixed`)
- Eine Race Condition wurde behoben, bei der das Hintergrundbild manchmal gesetzt wurde, bevor der Explorer nach einem Neustart vollständig bereit war.

## [0.2.0] - 2023-05-10

### Hinzugefügt (`Added`)
- Kernfunktionalität zum Speichern und Wiederherstellen der Positionen von Desktop-Icons.
- Ein erstes grafisches "Control Panel" zur Verwaltung der Desktops wurde eingeführt.

## [0.1.0] - 2023-04-02

### Hinzugefügt (`Added`)
- Erstes Release von SmartDesk.
- Grundlegende Logik zum Erstellen, Löschen und Wechseln von virtuellen Desktops durch Modifikation der Windows-Registrierung.
- Ein Command-Line Interface (CLI) für die grundlegende Steuerung.
