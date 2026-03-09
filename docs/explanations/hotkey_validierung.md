# Erläuterung: Hotkey State-Machine & Validierung

## Übersicht
SmartDesk verwendet eine zustandsbasierte Logik (`State Machine`), um Hotkeys abzufangen, ohne die normale Tastaturnutzung zu beeinträchtigen. Das System unterscheidet zwischen einer **Aktivierungs-Phase** und einer **Aktions-Phase**.

## Die Zustände (States)

1.  **IDLE:** Der Standardzustand. Der Listener wartet darauf, dass die Aktivierungskombination (`Strg+Shift`) gedrückt und wieder losgelassen wird.
2.  **WAITING_FOR_ACTION:** Dieser Zustand wird aktiv, sobald `Strg+Shift` losgelassen wurde. Das System "hält den Atem an" und wartet auf die erste Folgetaste.
3.  **HOLDING / SHOWING:** (Gesteuert via BannerController) Sobald `Alt` gedrückt wird, erscheint das Overlay und Aktionen (1-9) können ausgeführt werden.

## Strikte First-Key-Validierung

Um Fehlbedienungen zu vermeiden, implementiert der Listener in `src/smartdesk/hotkeys/listener.py` eine strikte Prüfung für den ersten Tastendruck nach der Aktivierung:

### Funktionsweise der Prüfung
Sobald der State `WAITING_FOR_ACTION` erreicht ist, gilt folgende Logik:

```python
if not action_key_used_after_activation and not is_action_key(key):
    _close_banner_and_reset()
    return
```

*   **Rationale:** Die Variable `action_key_used_after_activation` ist initial `False`. Wenn die gedrückte Taste (`key`) nicht zum konfigurierten Action-Modifier (`Alt`) gehört, bricht das System sofort ab.
*   **Keine Ignoranz:** Im Gegensatz zu früheren Versionen werden auch Tasten wie `Strg` oder `Shift` nicht mehr ignoriert. Drückt man nach der Aktivierung versehentlich erneut `Strg`, erkennt das System dies als "ungültige erste Taste" und setzt den Modus zurück.

## Warum dieser Ansatz?

### Vorhersehbarkeit (UX)
Der Benutzer erhält ein binäres Feedback: Entweder er drückt `Alt` und das System reagiert, oder er drückt etwas anderes und das System "schließt" sich sofort. Es gibt keine undefinierten Zwischenzustände, in denen das System noch auf Eingaben wartet, während der Benutzer eigentlich schon wieder normal tippen möchte.

### Schutz vor Overlapping
In Windows kommt es oft vor, dass Tasten-Events sich überschneiden. Durch den sofortigen Reset bei der ersten falschen Taste (`return` nach `_close_banner_and_reset`) stellen wir sicher, dass die Tastatur-Queue sauber bleibt und keine ungewollten Side-Effects (wie hängende `Alt`-Tasten) entstehen.

## Verwandte Dokumente
- [ADR-006: Strikte Hotkey-Aktivierungslogik](../adr/ADR-006-strikte-hotkey-aktivierung.md)
- [Hotkey Banner Flow](./hotkey_banner_flow.md)
