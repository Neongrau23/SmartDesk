# ADR 005: Rückkehr zur psutil-basierten Explorer-Neustart-Logik

* **Status:** Akzeptiert
* **Datum: 2024-05-22**
* **Beteiligte:** Leon, Gemini
* **Tags:** #architecture #performance #windows #system

## Kontext

Ursprünglich wurde in `src/smartdesk/core/services/system_service.py` die `psutil`-Bibliothek verwendet, um den Windows Explorer effizient neu zu starten. Ein Versuch, dies auf ein externes PowerShell-Skript umzustellen, führte zu Komplexität (fehlende Dateien, Pfadprobleme) und widersprach der dokumentierten Design-Entscheidung in der `GEMINI.md`, die `psutil` zur Reduzierung von Overhead bevorzugt.

## Alternativen

### Option 1: Externes PowerShell-Skript (scripts/restart_explorer.ps1)
- **Vorteile:** Einfache Nutzung von Win32-Kommandos innerhalb von PS.
- **Nachteile:** Zusätzlicher Prozess-Overhead (PowerShell-Start), schwierigere Pfadverwaltung, Abhängigkeit von externen Dateien.
- **Warum verworfen:** Höherer Overhead und Inkonsistenz mit bestehenden Performance-Optimierungen.

### Option 2: psutil-basierte Logik (Gewählte Lösung)
- **Vorteile:** Performanter (kein Subprozess für PS nötig), alles in Python, volle Kontrolle über den Prozess-Status.
- **Nachteile:** Erfordert korrekte Handhabung des automatischen Windows-Neustarts (Shell-Recovery).

## Entscheidung

**Wir haben uns für die Rückkehr zur psutil-Logik entschieden.**

Begründung:
- **Performance:** Minimiert den System-Overhead beim Desktop-Wechsel.
- **Robustheit:** Die Logik prüft nun explizit, ob Windows den Explorer selbstständig neu startet (was unter Win 10/11 Standard ist), und greift nur bei Bedarf ein. Dies verhindert redundante Explorer-Fenster.
- **Konformität:** Entspricht den in `GEMINI.md` festgelegten Performance-Zielen.

## Konsequenzen

### Positive Folgen
- Schnellerer Neustart der Shell.
- Keine "Thundering Herd" Probleme durch unnötige Subprozesse.
- Sauberere Code-Basis ohne externe Skript-Abhängigkeiten für Basisfunktionen.

### Negative Folgen / Risiken
- Abhängigkeit von der korrekten Funktionsweise der `psutil.wait_procs` Timeouts.
