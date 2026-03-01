# Besondere Funktionen, Probleme und Updates

Dieses Dokument beleuchtet spezielle technische Merkmale, bekannte Einschränkungen und wichtige Entwicklungs-Updates von SmartDesk.

## Inhaltsverzeichnis

1.  [Besondere Funktionen](#1-besondere-funktionen)
    - [Automatischer Desktop-Wechsel (Auto-Switch)](#automatischer-desktop-wechsel-auto-switch)
    - [Robustes Wiederherstellen der Icon-Positionen](#robustes-wiederherstellen-der-icon-positionen)
    - [Globales Hotkey-System](#globales-hotkey-system)
2.  [Bekannte Probleme und Einschränkungen](#2-bekannte-probleme-und-einschränkungen)
    - [Nur für Windows 10+](#nur-für-windows-10)
    - [Timing-Verhalten des Windows Explorers](#timing-verhalten-des-windows-explorers)
3.  [Wichtige Updates (Entwicklung)](#3-wichtige-updates-entwicklung)
    - [Performance-Optimierung](#performance-optimierung)

---

## 1. Besondere Funktionen

### Automatischer Desktop-Wechsel (Auto-Switch)

Eine der Kernfunktionen von SmartDesk ist die Fähigkeit, den Desktop automatisch zu wechseln, wenn ein bestimmter Prozess gestartet wird.

- **Funktionsweise:** Ein Hintergrunddienst (`AutoSwitchService`) überwacht in regelmäßigen Abständen die laufenden Prozesse des Systems.
- **Regelbasierte Logik:** Benutzer können Regeln definieren, die einen Prozessnamen (z.B. `blender.exe`) mit einem Ziel-Desktop (z.B. "3D-Modellierung") verknüpfen.
- **Priorisierung:** Die Regeln werden in der Reihenfolge ihrer Erstellung priorisiert. Sobald ein Prozess gefunden wird, der zur Regel mit der höchsten Priorität passt, wird der Wechsel ausgelöst und die weitere Prüfung für diesen Zyklus beendet.
- **Cooldown-Periode:** Um störende, wiederholte Wechsel zu verhindern, gibt es eine eingebaute Abklingzeit nach jedem automatischen Wechsel.

### Robustes Wiederherstellen der Icon-Positionen

Das präzise Wiederherstellen von Desktop-Icons nach einem Explorer-Neustart ist eine technische Herausforderung. Windows neigt dazu, Icons automatisch anzuordnen. SmartDesk implementiert einen mehrstufigen Prozess, um dies zu umgehen:

1.  **Warten auf den Explorer:** Nach dem Neustart des Explorers wartet SmartDesk aktiv darauf, dass das Desktop-Fenster (`SysListView32`) nicht nur existiert, sondern auch bereit ist und Icons geladen hat.
2.  **Deaktivierung von Auto-Anordnung:** Bevor die Icons positioniert werden, deaktiviert SmartDesk temporär die Windows-Stile `LVS_AUTOARRANGE` und `LVS_SNAPTOGRID` für das Desktop-Fenster. Dies verhindert, dass Windows die Positionen während des Setzens überschreibt.
3.  **Namensbasiertes Matching:** Anstatt sich nur auf den Index eines Icons zu verlassen (der sich ändern kann), ordnet SmartDesk die gespeicherten Positionen über den Namen des Icons dem aktuell sichtbaren Icon zu.
4.  **Wiederherstellung der Stile:** Nach dem Vorgang wird der `LVS_SNAPTOGRID`-Stil wiederhergestellt, `LVS_AUTOARRANGE` bleibt jedoch deaktiviert, um das benutzerdefinierte Layout zu erhalten.

### Globales Hotkey-System

SmartDesk verfügt über ein reaktionsschnelles globales Hotkey-System, das es ermöglicht, die App auch zu steuern, wenn sie nicht im Fokus ist.

- **State Machine:** Das System nutzt eine Zustandsmaschine (`IDLE` -> `ARMED` -> `HOLDING` -> `SHOWING`), um komplexe Interaktionen zu ermöglichen, wie z.B. "Halte Strg+Shift gedrückt und drücke dann eine Zifferntaste".
- **Effizienz:** Die Hotkey-Listener laufen in einem separaten Thread, um die UI nicht zu blockieren.
- **Zuverlässigkeit:** Callbacks sind in `try-except`-Blöcke gehüllt, um sicherzustellen, dass ein Fehler in einer Hotkey-Aktion nicht den gesamten Listener-Dienst zum Absturz bringt.

## 2. Bekannte Probleme und Einschränkungen

### Nur für Windows 10+

SmartDesk ist tief in die Windows-API und -Registrierung integriert. Kernfunktionen wie die Manipulation des Desktop-Pfades, das Auslesen von Fenster-Handles (`HWND`) und die Steuerung des Explorer-Prozesses sind betriebssystemspezifisch.

- **Einschränkung:** Das Programm ist **nicht** mit anderen Betriebssystemen wie macOS oder Linux kompatibel.

### Timing-Verhalten des Windows Explorers

Der `explorer.exe`-Prozess verhält sich nach einem Neustart oft unvorhersehbar. Es gibt keine garantierte Zeit, nach der der Desktop vollständig geladen und bereit für Interaktionen ist.

- **Problem:** Versuche, Icons oder Hintergrundbilder zu setzen, bevor der Desktop bereit ist, schlagen fehl.
- **Lösung:** SmartDesk verwendet eine aktive Warteschleife (`wait_for_desktop_listview`) mit einem Timeout, die periodisch prüft, ob das Desktop-Fenster bereit ist. Dies erhöht die Zuverlässigkeit erheblich, kann aber in seltenen Fällen (z.B. bei extrem hoher Systemlast) fehlschlagen.

## 3. Wichtige Updates (Entwicklung)

### Performance-Optimierung

In früheren Versionen wurden Systembefehle wie der Neustart des Explorers über PowerShell-Subprozesse ausgeführt, was einen erheblichen Overhead verursachte.

- **Update:** Der Neustart des Explorers wurde auf das `psutil`-Paket umgestellt. Anstatt einen neuen Prozess (`powershell.exe`) zu starten, interagiert `psutil` direkt mit der Prozessliste des Systems.
- **Vorteil:** Dies reduziert die Latenz beim Desktop-Wechsel, erhöht die Zuverlässigkeit und verringert die Systemlast.
