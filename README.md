# 🖥️ SmartDesk

![Version](https://img.shields.io/badge/version-0.4.1-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

**SmartDesk** ist ein Desktop-Inhalt-Manager für Windows. Im Gegensatz zu den nativen virtuellen Desktops von Windows (Task View), die lediglich offene Fenster gruppieren, ermöglicht SmartDesk eine echte Trennung von Dateien, Desktop-Icons und Hintergrundbildern für verschiedene Arbeitsumgebungen.

---

## 🔍 Wie es funktioniert

SmartDesk ermöglicht die Nutzung verschiedener Desktops durch das Umschalten des System-Pfades:

1.  **Registry-Umschaltung:** Jedes Mal, wenn du den Desktop wechselst, ändert SmartDesk den Pfad für den System-Ordner "Desktop" in der Windows-Registry (`User Shell Folders`).
2.  **Explorer-Refresh:** Damit Windows diese Änderung übernimmt, wird der Explorer-Prozess (`explorer.exe`) kurzzeitig aktualisiert oder neu gestartet.
3.  **Inhalts-Isolation:** Da Windows nun auf einen anderen Ordner zugreift, siehst du sofort andere Dateien und Icons. Deine **geöffneten Fenster und Programme bleiben dabei erhalten** und sichtbar – nur die "Unterlage" (der Desktop-Inhalt) ändert sich.
4.  **Icon-Positionierung:** Da Windows beim Pfadwechsel oft die Icon-Anordnung vergisst, werden bei jedem Desktop Wechsel, die Icons automatisch wieder an die Positionen verschoben, an denen sie waren als du das Desktop verlassen hast.

---

## Funktionen

*   **Desktop-Inhalts-Trennung:** Jeder virtuelle Desktop nutzt einen eigenen Ordner. Dateien auf Desktop 1 sind in der Desktop-Ansicht von Desktop 2 nicht vorhanden.
*   **Icon-Management:** SmartDesk speichert die X/Y-Koordinaten der Desktop-Icons und stellt diese beim Desktop-Wechsel wieder her.
*   **Individuelle Wallpaper:** Jedem Desktop kann ein eigenes Hintergrundbild zugewiesen werden.
*   **Hotkey-System:** Wechsel der Desktops über Tastenkombinationen.
*   **Instant Overlay (HUD):** Visuelle Rückmeldung über verfügbare Desktops durch Gedrückthalten der `Alt`-Taste.
*   **Desktop-Switch Animation:** Sanfte Übergänge (Fade-Effekt) beim Wechseln der Desktops.
*   **System-Integration:** Läuft als Hintergrundanwendung (System Tray).

## Installation

### Voraussetzungen
*   **Betriebssystem:** Windows 10 oder 11 (SmartDesk nutzt Windows-spezifische APIs und Registry-Pfade).
*   **Python:** Version 3.8 oder höher. [Download hier](https://www.python.org/downloads/).

### Schritt-für-Schritt

1.  **Repository klonen:**
    ```bash
    git clone https://github.com/Neongrau23/Smart-Desk.git
    cd Smart-Desk
    ```

2.  **Installation:**
    Das Installations-Skript erstellt eine virtuelle Python-Umgebung (`.venv`), installiert die Abhängigkeiten aus der `requirements.txt` und führt die Ersteinrichtung durch.

    Ausführung über:
    `scripts\install.bat`

3.  **Start:**
    SmartDesk wird als Icon im System Tray (unten rechts) angezeigt.

## Bedienung

SmartDesk wird über ein grafisches Control Panel oder über Hotkeys gesteuert.

### Hotkeys

Das System ist vollständig anpassbar, um Konflikte mit anderen Anwendungen zu vermeiden.

**Standard-Ablauf:**

1.  **Aktivieren:** Drücke `Strg` + `Shift` gleichzeitig.
2.  **Ausführen:**
    *   Drücke `Alt` + `1-8`, um zu einem Desktop zu wechseln.
    *   Halte die `Alt`-Taste nach der Aktivierung gedrückt, um ein **Overlay (HUD)** anzuzeigen. Dieses informiert über den aktuellen Desktop und die Belegung der Tasten.

**Anpassung:**

Über das Einstellungsmenü (`Rechtsklick auf Taskleisten-Icon -> Einstellungen -> Hotkeys`) kannst du:
*   Die **Aktivierungs-Tastenkombination** (Standard: `Strg` + `Shift`) ändern.
*   Die **Aktions-Modifikatortaste** (Standard: `Alt`) ändern.
*   Die **Halte-Dauer** (in Sekunden) einstellen, nach der das HUD erscheint.

| Standard-Tastenkombination | Aktion                                  |
| :--- | :--- |
| `Alt` + `1` - `8` | Wechselt zu Desktop 1 bis 8 |
| `Alt` + `9` | Speichert die aktuellen Icon-Positionen |

### Grafische Oberfläche (GUI)

*   **Control Panel:** Klicke mit der **rechten Maustaste** auf das Tray-Icon und wähle "Einstellungen" oder starte `launch_gui.py`, um Desktops zu verwalten (Namen ändern, Wallpaper setzen, neue Desktops erstellen).
*   **Tray Menü:** Schneller Wechsel zwischen Desktops über das Rechtsklick-Menü.

## 🛠️ Technische Details & Architektur

SmartDesk arbeitet tiefer im System als typische virtuelle Desktop-Tools:

*   **Registry Manipulation:** Es ändert temporär den `Desktop`-Pfad in `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders`.
*   **Explorer Refresh:** Nach einem Wechsel wird der Windows Explorer Prozess (`explorer.exe`) sanft neu gestartet bzw. aktualisiert, um die Änderungen sofort sichtbar zu machen.
*   **WinAPI Injection:** Für das Speichern und Wiederherstellen der Icon-Positionen wird Speicher in den Explorer-Prozess injiziert (`VirtualAllocEx`), um die Positionen direkt aus dem Speicher des `SysListView32`-Controls auszulesen.

**Projektstruktur:**
*   `src/smartdesk/core`: Geschäftslogik (Desktop-Service, Icon-Service).
*   `src/smartdesk/ui`: Benutzeroberfläche (PySide6/Qt).
*   `src/smartdesk/hotkeys`: Separater Prozess für die Tastaturüberwachung (`pynput`).
*   `src/smartdesk/shared`: Gemeinsame Konfigurationen und Hilfsfunktionen.

## 🤝 Mitwirken

Beiträge sind willkommen! Bitte beachte beim Coden die bestehenden Konventionen:
*   PEP 8 Styleguide.
*   Typ-Annotationen verwenden.
*   Tests schreiben (im `tests/` Ordner).

## 📄 Lizenz

Dieses Projekt ist unter der **MIT Lizenz** veröffentlicht. Siehe [LICENSE](LICENSE) für Details.

Copyright (c) 2026 Neongrau23

