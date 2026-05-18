# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

SmartDesk is a **Windows-only** virtual desktop manager. Unlike Windows' native Task View (which only groups windows), SmartDesk isolates **files, desktop icons, and wallpapers** per desktop by swapping the `Desktop` path in `HKCU\...\User Shell Folders` and refreshing `explorer.exe`. Icon coordinates are read/written by injecting memory into the Explorer process (`VirtualAllocEx` on the `SysListView32` control).

The version of record is `src/smartdesk/__init__.py` (`__version__`). `pyproject.toml` must be synced manually.

## Commands

The project expects a virtual environment named `.venv` at the repo root — many scripts hardcode this path (`.venv\Scripts\python.exe` / `pythonw.exe`).

```powershell
# Install (creates .venv, installs requirements, runs first-run setup)
scripts\install.bat

# Run the tray app (production launcher — uses pythonw.exe, no console)
start_smartdesk.bat

# Run the tray app with a visible console (for debugging)
python main.py start-tray

# Launch the GUI control panel directly, bypassing the tray
python launch_gui.py

# Manually restart the hotkey listener subprocess
python restart_hotkey_listener.py

# Tests
python -m pytest                                # all
python -m pytest tests/test_desktop_switch.py   # single file
python -m pytest tests/test_models.py::test_icon_position_from_dict -v   # single test
python -m pytest --cov=src/smartdesk            # with coverage
python -m pytest -m "not slow"                  # skip slow tests
```

`tests/conftest.py` prepends `src/` to `sys.path` and mocks `winreg`, the `win32*` libs, `ctypes`, and `PySide6` at import time — tests run on non-Windows hosts. If you add a Windows-only dependency, mock it in `conftest.py` the same way.

Ruff is used for lint/format (`.ruff_cache/` present), but there is no `[tool.ruff]` block in `pyproject.toml` — defaults apply.

## Architecture

### Process model

SmartDesk runs as **two or three separate OS processes** that coordinate through PID files and `stdin` commands. Understanding this is essential before touching anything in `hotkeys/` or `shared/animations/`.

1. **Tray process** (`main.py` → `smartdesk.ui.tray.tray_icon.SmartDeskTrayApp`) — Qt event loop, system tray icon, owns the GUI control panel and the `AutoSwitchService` background thread. Watches `%APPDATA%\SmartDesk\listener.pid` once per second to update the tray icon's active/inactive state.
2. **Hotkey listener process** (`smartdesk.hotkeys.listener`, launched via `python -m`) — `pynput` keyboard hook in its own process to keep UI responsive. Lifecycle managed by `hotkeys/hotkey_manager.py` → `listener_manager.py` (DI: `ProcessController` + `PidStorage` + `ProcessStarter`). Logs to `listener.log` / `listener_error.log` in `%APPDATA%\SmartDesk`.
3. **Banner/HUD process** (`smartdesk.ui.gui.gui_overview`) — spawned by `banner_controller.py` and **kept alive persistently** so the HUD appears instantly when the user holds the activation chord. Commanded via three `stdin` strings: `SHOW`, `HIDE`, `QUIT`. Don't replace this with on-demand spawns — startup latency is the reason the persistent design exists.
4. **Animation processes** (`shared/animations/screen_fade.py`, `logo.py`) — short-lived subprocesses spawned during a desktop switch. They wait for a lock file in `%TEMP%` to disappear before fading out. The lock file is the coordination signal between the switch sequence and the fade overlay.

### Desktop switch sequence

`core/services/desktop_service.switch_to_desktop()` executes this exact order — don't reorder without understanding the consequences (icons rely on Explorer being alive when read, Registry must change before Explorer restart, etc.):

1. Create lock file (signals animations to stay visible)
2. Registry backup (`utils/backup_service.py`)
3. Save current icon positions out of the live `SysListView32` (`icon_service.get_current_icon_positions`)
4. Update `User Shell Folders\Desktop` registry value
5. Restart `explorer.exe` (`system_service.restart_explorer`, uses `psutil` per ADR-005)
6. Wait for new desktop's listview, restore icon positions and wallpaper
7. Delete lock file (animations fade out)

See `docs/desktop_switch_prozess.md` for the full mermaid flowchart.

### Hotkey state machine

`hotkeys/listener.py` and `hotkeys/banner_controller.py` together implement a state machine: `IDLE → ARMED → HOLDING → SHOWING`. Triggers fire **on key release**, not press. Per ADR-006 (strict First-Key validation), once `ARMED`, the very next key must be the configured action key (default `Alt`) — anything else resets to `IDLE` immediately. Every listener callback (`on_press`, `on_release`) must be wrapped in `try/except` because an unhandled exception in a `pynput` callback kills the listener thread silently.

### Code layout (top-level intent only)

- `src/smartdesk/core/` — pure logic. `services/` (desktop, icon, wallpaper, system, settings, auto-switch, update), `models/desktop.py` (`Desktop`, `IconPosition`), `storage/file_operations.py` (JSON + file-lock with 1ms→100ms exponential backoff), `utils/` (registry, path validation, backup, win API helpers).
- `src/smartdesk/ui/` — Qt UI. `tray/` (system tray QApplication), `gui/` (control panel, overview/HUD, page widgets, `.ui` Designer files in `designer/`, **central stylesheet in `style.qss`**).
- `src/smartdesk/hotkeys/` — listener subprocess, banner controller, action registry. Public API in `__init__.py` (`start_listener`, `stop_listener`, `restart_listener`, `is_listener_running`, `get_listener_pid`).
- `src/smartdesk/shared/` — `config.py` (paths, registry keys, animation config), `localization.py` (i18n via `get_text()` keys, primarily DE), `logging_config.py`, `animations/` (subprocess scripts).
- `data dir` at runtime: `%APPDATA%\SmartDesk\` holds `desktops.json`, `rules.json` (auto-switch), `listener.pid`, `*.log`, and `wallpapers/`. There is also a dev/portable path under `<repo>/data/` defined in `config.py` but the AppData path is used by default.

## Conventions (non-obvious — read before editing)

- **Never call `print()`.** When started via `pythonw.exe` (the default), `sys.stdout`/`stderr` are reassigned to `os.devnull` in `shared/config.py`, but the rule still holds for `.pyw` entry points and the listener subprocess. Use `from smartdesk.shared.logging_config import get_logger`.
- **No inline styles in UI code.** All Qt styling lives in `src/smartdesk/ui/gui/style.qss`. Do not use the `styleSheet` property in `.ui` files or `setStyleSheet()` in Python — use dynamic properties (e.g. `window_type="overview"`, `status="error"`) and target them from QSS.
- **ComboBox/SpinBox wheel-scroll** must be disabled when unfocused via an `eventFilter`, to prevent accidental value changes when scrolling a parent `QScrollArea`.
- **Threading:** services that may re-enter themselves use `threading.RLock`. Copy shared collections inside the lock, then iterate outside to minimize contention.
- **All Win32/registry calls** must be wrapped in `try/except`. Crashes in background threads must not kill the tray app.
- **GUI work stays on the Qt main thread**; file I/O and Win32 calls move to background threads.
- **User-facing strings** must go through `smartdesk.shared.localization.get_text(key, **kwargs)`. Don't hardcode display text.
- **Headless Qt tests:** set `QT_QPA_PLATFORM=offscreen` if a test instantiates real Qt widgets (most don't — `PySide6` is mocked in `conftest.py`).
- **Communication style:** technical documentation, commit messages, and explanations to the user are written in **German** (see `.cursorrules`, `.gemini/GEMINI.md`).

## Release process

- Bump `__version__` in `src/smartdesk/__init__.py`.
- Manually sync the `version` field in `pyproject.toml`.
- Add release notes in `docs/releases/vX.Y.Z.md`.
- Architecture decisions go in `docs/adr/ADR-NNN-*.md`.
