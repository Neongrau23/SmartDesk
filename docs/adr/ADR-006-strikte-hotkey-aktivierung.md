# ADR 006: Strikte Hotkey-Aktivierungslogik (First-Key-Validierung)

* **Status:** Akzeptiert
* **Datum:** 2026-02-18
* **Beteiligte:** Leon (Benutzer), Gemini CLI
* **Tags:** #hotkey #ux #security #logic

## Kontext

Im aktuellen Hotkey-System von SmartDesk wird die Aktion (Desktop-Wechsel) durch eine Kombination aus `Strg+Shift` (Aktivierung) und anschließend `Alt + [Zahl]` (Ausführung) getriggert. 
Bisher war es möglich, nach der Aktivierung (`Strg+Shift`) andere Tasten (wie erneut `Strg` oder `Shift`) zu drücken, ohne dass der Modus abgebrochen wurde. Dies führte zu einer unklaren UX, da der Benutzer nicht sicher sein konnte, ob die nächste Taste noch als Teil des Hotkey-Zyklus gewertet wird.

Die Anforderung ist: Nach dem Loslassen von `Strg+Shift` darf **nur** der Action-Key (`Alt`) als allererste Taste akzeptiert werden. Jede andere Taste muss zum sofortigen Abbruch führen.

## Alternativen

### Option 1: Beibehaltung der "Ignore-Liste"
Bisher wurden Tasten, die Teil der Aktivierungs-Kombination sind, im Wartezustand einfach ignoriert.
- **Vorteile:** Verzeiht versehentliches Doppeltippen von `Strg`.
- **Nachteile:** Unvorhersehbares Verhalten; fühlt sich "schwammig" an.
- **Warum verworfen:** Entspricht nicht dem Wunsch nach einer präzisen und strikten Steuerung.

### Option 2: Strikte First-Key-Validierung (Gewählte Lösung)
Jede Taste außer dem Action-Modifier führt zum Reset.
- **Vorteile:** Eindeutiges Feedback; maximale Sicherheit gegen Fehlbedienung; klare State-Machine.
- **Nachteile:** Erfordert präzises Tippen vom Benutzer.

## Entscheidung

**Wir haben uns für die strikte First-Key-Validierung entschieden.**

Begründung:
- **UX-Klarheit:** Der Benutzer weiß genau: "Entweder jetzt Alt oder gar nichts".
- **Fehlertoleranz:** Durch das Zurücksetzen in den `IDLE`-State kann sofort ein neuer Versuch gestartet werden, ohne dass "tote" Keys im Puffer hängen.
- **Technische Robustheit:** Die State-Machine (`WAITING_FOR_ACTION`) wird durch ein Flag `action_key_used_after_activation` geschützt, das erst durch den ersten validen Action-Key gesetzt wird.

## Konsequenzen

### Positive Folgen
- Sofortiger Abbruch des Banners bei falscher Taste.
- Keine "geisterhaften" Hotkey-Zustände mehr.
- `Strg` und `Shift` werden nun im Wartezustand wie reguläre Tasten behandelt und führen zum Abbruch, wenn sie nicht explizit als Action-Key konfiguriert sind.

### Negative Folgen / Risiken
- Benutzer müssen `Strg+Shift` sauber loslassen, bevor sie `Alt` drücken (kein Überlappen von `Shift` und `Alt` mehr möglich, falls `Shift` nicht ignoriert wird).

## Implementierungs-Details
In `src/smartdesk/hotkeys/listener.py` wurde folgendes geändert:
1. Im `WAITING_FOR_ACTION` State wird sofort geprüft: `if not action_key_used_after_activation and not is_action_key(key): reset()`.
2. `is_part_of_activation(key)` wurde aus der `is_ignored_key`-Liste für diesen speziellen Check entfernt.
3. Ein `return` nach dem Reset verhindert, dass die "Abbruch-Taste" im selben Event-Loop fälschlicherweise andere Logik triggert.
