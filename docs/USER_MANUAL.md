# SmartDesk Benutzerhandbuch

Dieses Handbuch führt Sie durch die Installation, Konfiguration und tägliche Nutzung von SmartDesk.

## Inhaltsverzeichnis

1.  [Installation](#1-installation)
2.  [Ausführung](#2-ausführung)
3.  [Konfiguration](#3-konfiguration)
4.  [Häufige Aufgaben](#4-häufige-aufgaben)
    - [Einen neuen Desktop erstellen](#einen-neuen-desktop-erstellen)
    - [Zwischen Desktops wechseln](#zwischen-desktops-wechseln)
    - [Einen Desktop bearbeiten oder löschen](#einen-desktop-bearbeiten-oder-löschen)
    - [Ein Hintergrundbild zuweisen](#ein-hintergrundbild-zuweisen)

---

## 1. Installation

Die Installation von SmartDesk ist unkompliziert und wird durch ein Skript automatisiert.

**Voraussetzungen:**
- Windows 10 oder neuer.
- Python 3.8 oder höher muss auf Ihrem System installiert und im PATH verfügbar sein.

**Schritt-für-Schritt-Anleitung:**

1.  **Repository herunterladen:** Laden Sie die SmartDesk-Dateien herunter, z.B. als ZIP-Archiv von GitHub, und entpacken Sie sie in einen Ordner Ihrer Wahl (z.B. `C:\SmartDesk`).

2.  **Installations-Skript ausführen:**
    - Öffnen Sie den SmartDesk-Ordner.
    - Navigieren Sie in den Unterordner `scripts`.
    - Führen Sie die Datei `install.bat` per Doppelklick aus.

    Dieses Skript erledigt alles Notwendige:
    - Es erstellt eine isolierte Python-Umgebung (Virtual Environment) im Ordner `.venv`.
    - Es installiert automatisch alle benötigten Abhängigkeiten (wie `PySide6`, `psutil` etc.) aus der `requirements.txt`-Datei.

3.  **Warten Sie, bis der Vorgang abgeschlossen ist.** Ein Konsolenfenster zeigt den Fortschritt an. Sobald die Installation beendet ist, können Sie das Fenster schließen.

## 2. Ausführung

Der empfohlene Weg, SmartDesk zu starten, ist über das mitgelieferte Start-Skript.

- **Starten:** Führen Sie im Hauptverzeichnis von SmartDesk die Datei `start_smartdesk.bat` per Doppelklick aus.

Dadurch wird die Anwendung im Hintergrund gestartet und ein SmartDesk-Icon erscheint in Ihrer Windows-System-Tray (der Bereich neben der Uhr). Die Anwendung läuft unauffällig, ohne ein störendes Konsolenfenster zu öffnen.

**Interaktion:**
- Ein **Rechtsklick** auf das Tray-Icon öffnet das Hauptmenü, über das Sie Desktops wechseln, das Einstellungsfenster öffnen oder die Anwendung beenden können.
- Ein **Linksklick** öffnet direkt das Übersichtsfenster (Control Panel).

## 3. Konfiguration

Alle Einstellungen können bequem über das grafische Einstellungsfenster vorgenommen werden. Sie erreichen es über **Rechtsklick auf das Tray-Icon -> Einstellungen**.

Folgende Optionen stehen zur Verfügung:
- **Allgemein:**
    - **Design:** Wählen Sie zwischen einem hellen und einem dunklen Thema für die Benutzeroberfläche.
    - **Minimiert starten:** Legt fest, ob das Control Panel beim Programmstart minimiert bleiben soll.
    - **Wechsel-Animation:** Aktiviert oder deaktiviert den Überblend-Effekt beim Wechseln von Desktops.
- **Auto-Switch:**
    - **Aktivieren:** Schaltet die Funktion ein oder aus, die den Desktop automatisch wechselt, wenn bestimmte Programme gestartet werden.
    - **Regeln:** Hier können Sie Regeln definieren (z.B. `photoshop.exe` startet -> wechsle zu "Grafikdesign"-Desktop).
- **Hotkeys:**
    - **Tastenkombinationen:** Konfigurieren Sie globale Hotkeys, um schnell zwischen Desktops zu wechseln oder die Desktop-Übersicht anzuzeigen.

## 4. Häufige Aufgaben

Die Hauptverwaltung Ihrer Desktops findet im Control Panel statt, das Sie per Linksklick auf das Tray-Icon öffnen.

### Einen neuen Desktop erstellen

1.  Öffnen Sie das Control Panel.
2.  Klicken Sie auf den Button "Neuen Desktop erstellen".
3.  Geben Sie einen aussagekräftigen **Namen** für den Desktop ein (z.B. "Arbeit", "Gaming", "Privat").
4.  Wählen Sie einen **Ordnerpfad** aus. Dieser Ordner wird als Desktop-Verzeichnis für den neuen Desktop dienen. Alle Dateien und Verknüpfungen in diesem Ordner werden auf dem entsprechenden virtuellen Desktop angezeigt.
5.  Klicken Sie auf "Speichern".

### Zwischen Desktops wechseln

Es gibt mehrere Wege, den Desktop zu wechseln:
- **Über das Tray-Icon:** Rechtsklicken Sie auf das Icon und wählen Sie den gewünschten Desktop aus der Liste aus.
- **Über das Control Panel:** Klicken Sie in der Desktop-Liste auf den "Aktivieren"-Button neben dem gewünschten Desktop.
- **Über Hotkeys:** (Wenn konfiguriert) Nutzen Sie die von Ihnen festgelegten Tastenkombinationen für den direkten Wechsel.

### Einen Desktop bearbeiten oder löschen

- **Bearbeiten:** Klicken Sie im Control Panel auf den "Bearbeiten"-Button neben einem Desktop, um dessen Namen oder Pfad zu ändern.
- **Löschen:** Klicken Sie auf den "Löschen"-Button. Es erscheint eine Bestätigungsabfrage. Optional können Sie auch den zugehörigen Ordner von der Festplatte entfernen lassen.

### Ein Hintergrundbild zuweisen

1.  Wählen Sie im Control Panel den gewünschten Desktop aus.
2.  Klicken Sie im Detailbereich auf den Button "Hintergrundbild ändern".
3.  Wählen Sie eine Bilddatei von Ihrem Computer aus.
4.  Das Bild wird automatisch für diesen Desktop festgelegt und beim nächsten Wechsel angezeigt.
