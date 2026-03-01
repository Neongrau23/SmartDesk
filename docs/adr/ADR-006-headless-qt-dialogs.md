# ADR 006: Sichere Ausführung von Qt-Dialogen aus Headless-Prozessen

* **Status:** Akzeptiert
* **Datum:** 2026-03-01
* **Beteiligte:** Leon (Neongrau23), AI-Assistent
* **Tags:** #architecture #qt #pyside6 #multiprocessing #background-service

## Kontext

Das Projekt "SmartDesk" nutzt für die globale Hotkey-Überwachung einen eigenen Hintergrundprozess (Listener), der isoliert von der grafischen Hauptanwendung (`QApplication`) läuft. Wenn der Benutzer per Hotkey den Wechsel zu einem nicht mehr existierenden Desktop-Pfad anfordert, soll das System eine Warnung inklusive Handlungsoptionen ("Neu erstellen", "Entfernen", "Abbrechen") anzeigen.

Da der Hotkey-Listener jedoch "headless" (ohne GUI-Instanz) operiert, führte der Versuch, direkt aus dem `desktop_service.py` eine `QMessageBox` von PySide6 aufzurufen, zu einem sofortigen und stillen Absturz des gesamten Listener-Threads. Dies hatte zur Folge, dass sämtliche Hotkeys unbrauchbar wurden.

## Alternativen

### Option 1: "Silent Fails" (Fehler ignorieren)
- **Vorteile:** Sehr einfach zu implementieren. Der Listener stürzt nicht ab.
- **Nachteile:** Der Benutzer erhält keinerlei visuelles Feedback, warum sein Hotkey-Druck keine Wirkung zeigt.
- **Warum verworfen:** Die Benutzererfahrung (UX) leidet massiv, wenn Aktionen grundlos fehlschlagen, ohne dass der Benutzer weiß, wie er das Problem beheben kann (z.B. Desktop-Ordner wiederherstellen).

### Option 2: Windows native MessageBox (`ctypes.windll.user32.MessageBoxW`)
- **Vorteile:** Benötigt keine Qt-Umgebung, extrem ressourcenschonend, funktioniert immer aus Hintergrund-Threads.
- **Nachteile:** Beschränkt auf standardisierte Windows-Buttons (Ja, Nein, OK, Abbrechen). Erlaubt keine komplexeren Auswahlmöglichkeiten (z.B. eigene Buttons für "Neu erstellen" und "Entfernen").
- **Warum verworfen:** Die bestehende Logik im `desktop_service.py` verlangt zwingend spezifische Antwortmöglichkeiten, die über Ja/Nein hinausgehen.

### Option 3: Kommunikation mit der Haupt-GUI via IPC (Inter-Process Communication)
- **Vorteile:** Architektonisch am saubersten. Der Listener schickt nur einen Befehl ("Zeige Warnung") an die laufende GUI, welche den Dialog rendert.
- **Nachteile:** Erfordert, dass die Haupt-GUI (Tray-Icon) zwingend läuft. Das Setup einer bidirektionalen IPC für synchrone Antworten (Listener blockiert, bis der Benutzer im GUI klickt) ist sehr komplex und fehleranfällig.

## Entscheidung

**Wir haben uns für das dynamische Spawnen von Subprozessen (`subprocess.run`) für Qt-Dialoge entschieden.**

Begründung:
- Die Funktionen `show_choice_dialog` und `show_confirmation_dialog` prüfen nun vorab via `QApplication.instance()`, ob sie innerhalb einer bestehenden Qt-Umgebung laufen.
- Ist dies nicht der Fall (wie beim Hotkey-Listener), generiert die Funktion "on-the-fly" ein kurzes Python-Skript, das nur eine einzige Qt-Applikation inklusive des benötigten Dialogs (`QMessageBox`) startet.
- Dieses Skript wird als unabhängiger, temporärer Nebenprozess ausgeführt.
- Der Haupt-Thread (Hotkey-Listener) blockiert sicher, bis der Nebenprozess beendet ist, liest dessen Konsolenausgabe (`stdout`) als Antwort des Benutzers aus und arbeitet normal weiter.

## Konsequenzen

### Positive Folgen
- **Robustheit:** Der Hotkey-Listener ist nun absolut absturzsicher gegenüber fehlenden Qt-Umgebungen.
- **Wiederverwendbarkeit:** Die Dialog-Funktionen können nun von überall im Projekt aufgerufen werden, unabhängig davon, ob es sich um ein GUI-Skript, einen CLI-Befehl oder einen Hintergrund-Worker handelt.
- **Konsistenz:** Der Benutzer sieht exakt dieselben Qt-Dialoge, egal von wo der Fehler getriggert wurde.

### Negative Folgen / Risiken
- **Performance-Overhead:** Das Starten eines neuen Python-Interpreters als Subprozess dauert den Bruchteil einer Sekunde länger, als einen nativen Dialog aufzurufen.
- Da dies jedoch nur im Ausnahmefall (Fehler/Warnung) passiert, ist dieser Trade-off für die gewonnene Stabilität vernachlässigbar.