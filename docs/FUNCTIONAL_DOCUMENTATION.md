# Funktionale Dokumentation für SmartDesk

Dieses Dokument beschreibt die Kernfunktionen und Methoden der SmartDesk-Anwendung. Es richtet sich an Entwickler, die die Architektur und die interne Funktionsweise des Programms verstehen möchten.

## Inhaltsverzeichnis

1.  [Desktop Service (`desktop_service.py`)](#desktop-service-desktop_servicepy)
2.  [Icon Service (`icon_service.py`)](#icon-service-icon_servicepy)
3.  [Wallpaper Service (`wallpaper_service.py`)](#wallpaper-service-wallpaper_servicepy)
4.  [System Service (`system_service.py`)](#system-service-system_servicepy)
5.  [Settings Service (`settings_service.py`)](#settings-service-settings_servicepy)
6.  [Auto-Switch Service (`auto_switch_service.py`)](#auto-switch-service-auto_switch_servicepy)
7.  [Update Service (`update_service.py`)](#update-service-update_servicepy)

---

## 1. Desktop Service (`desktop_service.py`)

Dieser Service ist die zentrale Komponente für die Verwaltung der virtuellen Desktops. Er kümmert sich um das Erstellen, Aktualisieren, Löschen und Wechseln von Desktops.

### `create_desktop(name: str, path: str, create_if_missing: bool = True) -> bool`

- **Beschreibung:** Erstellt einen neuen virtuellen Desktop. Die Konfiguration wird in `desktops.json` gespeichert.
- **Parameter:**
    - `name`: Der eindeutige Name für den neuen Desktop.
    - `path`: Der Dateipfad zum Ordner, der als Desktop-Verzeichnis dient.
    - `create_if_missing`: Wenn `True`, wird der Ordner am angegebenen Pfad erstellt, falls er nicht existiert.
- **Rückgabewert:** `True` bei Erfolg, andernfalls `False`.
- **Beispiel:**
  ```python
  create_desktop("Projekt X", "C:/Users/User/Desktops/ProjektX")
  ```

### `update_desktop(old_name: str, new_name: str, new_path: str) -> bool`

- **Beschreibung:** Aktualisiert den Namen und/oder den Pfad eines bestehenden Desktops. Kann optional das Verzeichnis auf der Festplatte verschieben.
- **Parameter:**
    - `old_name`: Der aktuelle Name des zu bearbeitenden Desktops.
    - `new_name`: Der neue Name für den Desktop.
    - `new_path`: Der neue Pfad für das Desktop-Verzeichnis.
- **Rückgabewert:** `True` bei Erfolg, `False` bei Fehlern (z.B. Desktop nicht gefunden, Name bereits vergeben).

### `delete_desktop(name: str, delete_folder: bool = False, skip_confirm: bool = False) -> bool`

- **Beschreibung:** Löscht einen Desktop aus der Konfiguration. Geschützte Desktops (z.B. der "Original" Desktop) können nicht gelöscht werden.
- **Parameter:**
    - `name`: Der Name des zu löschenden Desktops.
    - `delete_folder`: Wenn `True`, wird auch der zugehörige Ordner auf der Festplatte gelöscht.
    - `skip_confirm`: Wenn `True`, wird die Bestätigungsabfrage übersprungen.
- **Rückgabewert:** `True` bei Erfolg, `False` bei Abbruch oder Fehler.

### `get_all_desktops() -> List[Desktop]`

- **Beschreibung:** Ruft eine Liste aller konfigurierten Desktops aus der `desktops.json` ab.
- **Rückgabewert:** Eine Liste von `Desktop`-Objekten.

### `switch_to_desktop(desktop_name: str) -> bool`

- **Beschreibung:** Führt den vollständigen Prozess zum Wechseln eines Desktops aus. Dies beinhaltet das Sichern der aktuellen Icon-Positionen, das Ändern des Windows-Registrierungsschlüssels für den Desktop-Pfad, den Neustart des Windows Explorers und das Wiederherstellen der Icons und des Hintergrundbilds für den Zieldesktop.
- **Parameter:**
    - `desktop_name`: Der Name des zu aktivierenden Desktops.
- **Rückgabewert:** `True` bei erfolgreichem Wechsel, andernfalls `False`.

### `save_current_desktop_icons() -> bool`

- **Beschreibung:** Ermittelt den aktuell aktiven Desktop, liest dessen Icon-Positionen aus und speichert sie in der Konfigurationsdatei.
- **Rückgabewert:** `True` bei Erfolg, `False` wenn kein aktiver Desktop gefunden wurde.

### `assign_wallpaper(desktop_name: str, source_image_path: str) -> bool`

- **Beschreibung:** Weist einem Desktop ein neues Hintergrundbild zu. Das Bild wird in das SmartDesk-Datenverzeichnis kopiert und mit dem Desktop verknüpft.
- **Parameter:**
    - `desktop_name`: Der Name des Desktops.
    - `source_image_path`: Der Pfad zur Quelldatei des Bildes.
- **Rückgabewert:** `True` bei Erfolg.

---

## 2. Icon Service (`icon_service.py`)

Dieser Service interagiert direkt mit der Windows-API, um die Positionen von Desktop-Icons auszulesen und zu setzen.

### `get_current_icon_positions() -> List[IconPosition]`

- **Beschreibung:** Liest die Namen und XY-Koordinaten aller Icons auf dem aktuellen Desktop aus.
- **Rückgabewert:** Eine Liste von `IconPosition`-Objekten, die jeweils den Namen und die Position eines Icons enthalten.

### `set_icon_positions(saved_icons: List[IconPosition])`

- **Beschreibung:** Stellt die Positionen der Desktop-Icons anhand einer gespeicherten Liste wieder her. Die Funktion matcht Icons anhand ihres Namens, um eine hohe Zuverlässigkeit zu gewährleisten. Temporär werden "Auto Arrange" und "Snap to Grid" deaktiviert, um das Layout präzise setzen zu können.
- **Parameter:**
    - `saved_icons`: Eine Liste von `IconPosition`-Objekten, die wiederhergestellt werden soll.

### `wait_for_desktop_listview(timeout: int = 10, check_items: bool = True) -> int`

- **Beschreibung:** Eine Hilfsfunktion, die darauf wartet, dass das Desktop-Fenster (`SysListView32`) nach einem Explorer-Neustart verfügbar ist.
- **Rückgabewert:** Das Handle (HWND) des Fensters oder `0` bei einem Timeout.

---

## 3. Wallpaper Service (`wallpaper_service.py`)

Verwaltet das Setzen und Speichern von Hintergrundbildern.

### `set_wallpaper(path: str) -> bool`

- **Beschreibung:** Setzt das Desktop-Hintergrundbild für den aktuellen Benutzer über die Windows-API.
- **Parameter:**
    - `path`: Der absolute Pfad zur Bilddatei.
- **Rückgabewert:** `True` bei Erfolg.

### `copy_wallpaper_to_datadir(source_path: str, desktop_name: str) -> Optional[str]`

- **Beschreibung:** Kopiert eine Bilddatei in das `wallpapers`-Verzeichnis von SmartDesk, um sie vor versehentlichem Löschen zu schützen.
- **Parameter:**
    - `source_path`: Pfad der Quelldatei.
    - `desktop_name`: Name des Desktops, dem das Bild zugeordnet wird (wird Teil des neuen Dateinamens).
- **Rückgabewert:** Der neue Pfad zur kopierten Datei oder `None` bei einem Fehler.

---

## 4. System Service (`system_service.py`)

Stellt systemnahe Funktionen bereit, hauptsächlich den Neustart des Windows Explorers.

### `restart_explorer()`

- **Beschreibung:** Startet den `explorer.exe`-Prozess neu. Dies ist notwendig, damit Änderungen am Desktop-Pfad in der Registry wirksam werden. Die Implementierung nutzt `psutil`, um den Prozess zu beenden und wartet darauf, dass Windows ihn automatisch neu startet.
- **Ausnahmen:** Löst und behandelt `Exception`, falls der Neustart fehlschlägt.

---

## 5. Settings Service (`settings_service.py`)

Verwaltet die globalen Anwendungseinstellungen, die in `settings.json` gespeichert werden.

### `load_settings() -> dict`

- **Beschreibung:** Lädt die Einstellungen aus der `settings.json`. Falls die Datei nicht existiert, werden Standardwerte zurückgegeben.
- **Rückgabewert:** Ein Dictionary mit den Anwendungseinstellungen.

### `save_settings(settings: dict) -> bool`

- **Beschreibung:** Speichert das Einstellungs-Dictionary in die `settings.json`.
- **Parameter:**
    - `settings`: Das Dictionary, das gespeichert werden soll.
- **Rückgabewert:** `True` bei Erfolg.

### `get_setting(key: str, default: Any = None) -> Any`

- **Beschreibung:** Liest einen einzelnen Einstellungswert.
- **Parameter:**
    - `key`: Der Schlüssel der Einstellung.
    - `default`: Ein optionaler Standardwert, falls der Schlüssel nicht existiert.
- **Rückgabewert:** Der Wert der Einstellung oder der `default`-Wert.

### `set_setting(key: str, value: Any) -> bool`

- **Beschreibung:** Setzt einen einzelnen Einstellungswert und speichert die Änderungen sofort.
- **Parameter:**
    - `key`: Der Schlüssel der Einstellung.
    - `value`: Der neue Wert.
- **Rückgabewert:** `True` bei erfolgreichem Speichern.

---

## 6. Auto-Switch Service (`auto_switch_service.py`)

Implementiert die Logik für den automatischen Desktop-Wechsel basierend auf laufenden Prozessen.

### `class AutoSwitchService`

- **Beschreibung:** Ein Service, der in einem Hintergrundthread läuft, laufende Prozesse überwacht und den Desktop wechselt, wenn ein Prozess einer vordefinierten Regel entspricht.
- **Wichtige Methoden:**
    - `add_rule(process_name: str, desktop_name: str)`: Fügt eine Regel hinzu (z.B. "photoshop.exe" -> "Grafikdesign"-Desktop).
    - `delete_rule(process_name: str)`: Entfernt eine Regel.
    - `get_rules() -> Dict[str, str]`: Gibt alle aktuellen Regeln zurück.
    - `start()`: Startet den Überwachungs-Thread.
    - `stop()`: Stoppt den Überwachungs-Thread.

---

## 7. Update Service (`update_service.py`)

Prüft auf neue Anwendungsversionen auf GitHub.

### `class UpdateService`

- **Beschreibung:** Dieser Service kann die GitHub-API abfragen, um die neueste veröffentlichte Version von SmartDesk zu finden und mit der aktuell installierten Version zu vergleichen.
- **Wichtige Methoden:**
    - `check_for_updates() -> Tuple[bool, Optional[str]]`: Prüft auf Updates. Gibt ein Tupel zurück: `(ist_update_verfügbar, neue_versionsnummer)`.
    - `get_download_url() -> Optional[str]`: Gibt die Download-URL für das neueste Release-Asset (typischerweise eine `.exe`-Datei) zurück.
