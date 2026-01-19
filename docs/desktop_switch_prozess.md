# Dokumentation: Desktop-Wechsel Prozess

Diese Datei beschreibt den technischen Ablauf beim Wechseln eines Desktops in SmartDesk, damit zukünftige Änderungen an der Animation oder dem Ablauf leichter nachvollzogen werden können.

## Flowchart: Ablauf & Logik

```mermaid
graph TD
    %% Einstiegspunkt
    Start((Start)) -->|Alt + 1-8| SwitchFunc[<b>switch_to_desktop</b><br/>src/smartdesk/core/services/desktop_service.py]

    %% Einstellungs-Check
    subgraph Config["Konfiguration"]
        SwitchFunc -->|Prüfe Einstellung| CheckSetting{Animation<br/>aktiviert?}
        CheckSetting -.->|Liest| Settings[src/smartdesk/core/services/settings_service.py]
    end

    %% Pfad A: Mit Animation
    subgraph Animation["Animations-Prozess (Parallel)"]
        CheckSetting -- Ja --> LockFile[Erstelle <b>Lock-File</b><br/>temp/smartdesk_switch.lock]
        LockFile -->|subprocess.Popen| ScreenFade[<b>screen_fade.py</b><br/>Vollbild-Overlay]
        ScreenFade -->|subprocess.Popen| Logo[<b>logo.py</b><br/>Zeigt Logo & Text]
        Logo -.->|Liest Style| LogoCfg[logo_config.py]
        
        %% Warte-Logik der Animation
        ScreenFade -.->|Wartet auf Löschung| LockFile
    end

    %% Pfad B: System-Änderungen (Passiert immer)
    subgraph System["System-Operationen"]
        CheckSetting -- Nein --> RegUpdate
        LockFile --> RegUpdate[Registry Update<br/>& Explorer Neustart]
        RegUpdate --> Restore[Icons & Wallpaper<br/>wiederherstellen]
    end

    %% Abschluss
    Restore --> DeleteLock[Lösche <b>Lock-File</b>]
    DeleteLock -.->|Signalisiert Ende| ScreenFade
    ScreenFade -->|Fade Out| StopLogo[Beende logo.py]
    StopLogo --> Ende((Fertig))
    DeleteLock --> Ende

    %% Styling
    style SwitchFunc fill:#f9f,stroke:#333,stroke-width:2px
    style ScreenFade fill:#bbf,stroke:#333,stroke-width:2px
    style Logo fill:#bbf,stroke:#333
    style Settings fill:#ff9,stroke:#333
```

## Relevante Dateien & Verantwortlichkeiten

| Datei-Pfad | Verantwortung |
| :--- | :--- |
| **`src/smartdesk/core/services/desktop_service.py`** | **Hauptsteuerung:** Enthält `switch_to_desktop`. Steuert Registry-Updates, Explorer-Restart und entscheidet über den Start der Animation. |
| **`src/smartdesk/core/services/settings_service.py`** | **Konfiguration:** Verwaltet die Einstellung `show_switch_animation`. |
| **`src/smartdesk/shared/animations/screen_fade.py`** | **Vollbild-Blende:** Erzeugt das Overlay-Fenster. Wartet auf die Löschung der `.lock` Datei im Temp-Verzeichnis, um sich zu beenden. |
| **`src/smartdesk/shared/animations/logo.py`** | **Logo-Anzeige:** Wird von `screen_fade.py` gestartet und zeigt das visuelle Logo/Ladeanimation an. |
| **`src/smartdesk/shared/animations/logo_config.py`** | **Design-Settings:** Zentrale Stelle für Farben, Texte und Animations-Stile des Logos. |
| **`src/smartdesk/ui/gui/pages/settings_page.py`** | **Benutzeroberfläche:** Stellt die Checkbox in den Einstellungen bereit. |

## Einstellung "Blende anzeigen"
Die Einstellung wird in der `settings.json` unter dem Schlüssel `show_switch_animation` (Boolean) gespeichert. Standardmäßig ist dieser Wert auf `true` gesetzt.
