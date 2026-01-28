# SmartDesk - Projekt-Notizen

## 🖥️ UI & Design
- **Framework:** PySide6 (Qt)
- **Architektur:** `.ui`-Dateien werden dynamisch mit `QUiLoader` geladen (nicht kompiliert).
- **Design-Richtlinie:**
    - Styling **ausschließlich** in `src/smartdesk/ui/gui/style.qss`.
    - **Verbot von Inline-Styles** (`styleSheet` Property) in `.ui`-Dateien oder Python-Code.
    - Steuerung über **Dynamic Properties** (z.B. `window_type`, `status`, `overview_type`) und CSS-Selektoren.
    - Bei Property-Änderungen im Code `unpolish`/`polish` nutzen, um Style-Update zu erzwingen.
    - **GroupBoxen:** Hintergrund: `transparent`, Rahmen: `1px solid #3e3e42`. Titel-Hintergrund muss der Seitenfarbe entsprechen, um den Rahmen sauber zu überlagern.
    - **Scrollbare Tabs:** QScrollArea wird **innerhalb** der Tabs platziert, um Titel/Reiter fixiert zu halten.

## 🖱️ UX & Interaktion
- **Scroll-Schutz:** Eingabefelder (`QComboBox`, `QSpinBox`) ignorieren das Scrollrad, wenn sie keinen Fokus haben (`eventFilter`), um versehentliche Änderungen beim Scrollen der Seite zu vermeiden.
- **Tabellen-Auto-Height:** QTableWidget-Höhen werden dynamisch an den Inhalt angepasst, um interne Scrollbalken zu vermeiden und das äußere Scrollen der Seite zu nutzen.


## 🏗️ Architektur & Services
- **Zielplattform:** Ausschließlich **Windows 10+**.
- **Desktop Service:**
    - Wechsel-Workflow: Lock -> Registry Backup -> Icons speichern -> Registry Update -> Explorer Restart -> Icons/Wallpaper wiederherstellen.
    - `get_all_desktops` synchronisiert Registry nur bei Bedarf (`sync_registry=True`) um Schreibzugriffe zu minimieren.
- **Hotkey System:**
    - State Machine: `IDLE` -> `ARMED` -> `HOLDING` -> `SHOWING`.
    - Kommunikation BannerController <-> GUI (`gui_overview.py`) erfolgt via `stdin`/`stdout`.
    - Synchronisation: Erzwingt Re-Arming, wenn Action-Key im IDLE-State gedrückt wird.
    - **Robustheit:** Callbacks (`on_press`, `on_release`) sind in `try-except` Blöcke gehüllt, um zu verhindern, dass Exceptions in Action-Handlern den gesamten Listener-Thread beenden.
- **AutoSwitchService:** Priorität basiert auf Einfügereihenfolge der Regeln (erste Regel = höchste Prio).
- **Storage:**
    - `file_lock` nutzt exponentielles Backoff (1ms - 100ms).
    - `load_desktops` cached rohe JSON-Dicts (`_json_cache`) statt Objekten für Performance (vermeidet `deepcopy`).
    - `settings_service` gibt `False` zurück, wenn `settings.json` fehlt.

## 🚀 Start & Deployment
- **Einstiegspunkte:**
    - `start_smartdesk.bat`: Empfohlener Starter für Endanwender. Startet das Tray-Icon via `pythonw.exe` (kein Konsolenfenster).
    - `main.py start-tray`: Manueller Start des Tray-Icons via Kommandozeile.
    - `launch_gui.py`: Direkter Start des Control Panels (GUI) zu Debug-Zwecken.
- **Voraussetzungen:** Das Virtual Environment (`.venv`) muss über `scripts/install.bat` erstellt worden sein.

## 🚀 Performance & Optimierung
- **Explorer-Neustart:** Nutzt nun direkt `psutil` (Kill & Wait) statt PowerShell-Subprozesse, was den Overhead reduziert und die Zuverlässigkeit erhöht.
- **Desktop-Service:** `get_all_desktops` ist nun seiteneffektfrei (kein impliziter Registry-Sync mehr). Synchronisation erfolgt explizit bei Bedarf.
- **File-Locking:** Implementierung eines exponentiellen Backoffs mit zusätzlichem Jitter (random), um Race-Conditions bei hoher Last (Thundering Herd) zu minimieren.
- **Icons:** `icon_service` nutzt Batch-Optimierung (ein `ReadProcessMemory` Block für alle Icons).
- **Prozesse:**
    - `psutil.Process.kill()` statt `taskkill` (Shell-Overhead vermeiden).
    - Iteration über Prozesse unter Lock: Liste kopieren, Lock freigeben, dann iterieren (Lock Contention minimieren).
    - `psutil.wait_procs` statt Polling-Loops nutzen.
- **Caching:** `gui_overview.py` cached `desktops.json` Pfad und nutzt `stat()` statt `exists()` (weniger Syscalls).

## 🧪 Testing & Environment
- **Plattform:** Primäres Ziel ist Windows (`win32`), Entwicklung/Tests oft auf Linux.
- **Mocks (Linux):**
    - Windows-Module (`win32*`, `ctypes`, `pynput`, `pystray`) müssen in `conftest.py` gemockt werden.
    - `ctypes` auf Linux braucht `UTF-16LE` Handling für String Buffer (wegen 4-Byte `wchar_t`).
    - `pynput` muss in `sys.modules` gepatcht werden, bevor `listener` importiert wird (X Server Fehler vermeiden).
- **State Reset:** Tests mit Shared State (Cache) müssen diesen via `setup_method` zurücksetzen.
- **Pfad-Normalisierung:** Tests müssen auf Linux Windows-Backslashes tolerieren/mocken.
- **Dependencies:** `psutil` ist Hard-Dependency. `colorama` ist Runtime-Dependency.

## ⚠️ Bekannte Probleme & Hacks
- **Imports:** `gui_overview.py` nutzt `try...except ImportError` für `win_utils`, um Laden auf Nicht-Windows zu erlauben.
- **Config:** `APPDATA` Env-Var muss vor Import von `smartdesk.shared.config` gesetzt sein.
- **Netzwerk:** Umgebung hat unzuverlässigen Internetzugang -> `pip install` schlägt oft fehl.
- **Icon-Wiederherstellung (Win32 Critical):**
    - **Problem:** Nach `restart_explorer` ist das Desktop-Fenster (`SysListView32`) oft noch nicht bereit oder Windows erzwingt "Auto Arrange".
    - **Lösung:**
        1.  **Timing:** Aktives Warten auf das Handle via `wait_for_desktop_listview` (mit Timeout & Item-Check).
        2.  **Styles:** Vor dem Setzen der Icons müssen `LVS_AUTOARRANGE` (0x0100) und `LVS_SNAPTOGRID` (0x0800) temporär via `SetWindowLong` entfernt werden.
        3.  **Restore:** `LVS_AUTOARRANGE` darf nach dem Wiederherstellen **nicht** wieder aktiviert werden, sonst zerstört Windows das Layout sofort. `LVS_SNAPTOGRID` kann wiederhergestellt werden.

## 📝 Konventionen
- **Sprache:** Technische Doku und Erklärungen auf **Deutsch** (professionell).
- **Tools:** `ruff` für Linting. `replace_with_git_merge_diff` ist unzuverlässig -> `write_file` bevorzugen.
- **Versionierung:**
    - Master-Version steht in `src/smartdesk/__init__.py` (aktuell: **0.5.6**).
    - `pyproject.toml` muss manuell synchron gehalten werden.
    - UI-Versionsanzeigen sollten dynamisch aus `__version__` geladen werden.
