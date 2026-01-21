#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SmartDesk Installations- und Start-Skript

Dieses Skript führt eine vollständige Einrichtung durch:
1. Prüft Python-Version und Voraussetzungen
2. Erstellt/Aktiviert Virtual Environment
3. Installiert alle Abhängigkeiten
4. Führt First-Run-Setup durch (Original Desktop, Registry-Backup)
5. Startet SmartDesk (Tray-Icon)

Verwendung:
    python scripts/install.py              # Installation + Start Tray-Icon
    python scripts/install.py --no-start   # Nur Installation
    python scripts/install.py --check      # Nur Prüfung
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


# =============================================================================
# Konfiguration
# =============================================================================

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
VENV_DIR = PROJECT_ROOT / ".venv"
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"

MIN_PYTHON_VERSION = (3, 8)


# =============================================================================
# Hilfsfunktionen
# =============================================================================


def print_header():
    """Zeigt den Header an."""
    print()
    print("=" * 60)
    print("  🖥️  SmartDesk - Installation & Einrichtung")
    print("=" * 60)
    print()


def print_step(step: int, total: int, message: str):
    """Zeigt einen Schritt an."""
    print(f"\n[{step}/{total}] {message}")
    print("-" * 50)


def print_success(message: str):
    """Zeigt eine Erfolgsmeldung an."""
    print(f"  ✅ {message}")


def print_warning(message: str):
    """Zeigt eine Warnung an."""
    print(f"  ⚠️  {message}")


def print_error(message: str):
    """Zeigt einen Fehler an."""
    print(f"  ❌ {message}")


def print_info(message: str):
    """Zeigt eine Info an."""
    print(f"  ℹ️  {message}")


def run_command(cmd: list, cwd: Path = None, capture: bool = False) -> tuple:
    """Führt einen Befehl aus."""
    try:
        result = subprocess.run(cmd, cwd=cwd or PROJECT_ROOT, capture_output=capture, text=True, check=False)
        return result.returncode == 0, result.stdout if capture else ""
    except Exception as e:
        return False, str(e)


# =============================================================================
# Prüfungen
# =============================================================================


def check_python_version() -> bool:
    """Prüft die Python-Version."""
    version = sys.version_info[:2]
    print_info(f"Python-Version: {version[0]}.{version[1]}")

    if version < MIN_PYTHON_VERSION:
        print_error(f"Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+ erforderlich!")
        return False

    print_success("Python-Version OK")
    return True


def check_windows() -> bool:
    """Prüft ob Windows verwendet wird."""
    system = platform.system()
    print_info(f"Betriebssystem: {system}")

    if system != "Windows":
        print_error("SmartDesk ist nur für Windows verfügbar!")
        return False

    print_success("Windows erkannt")
    return True


def check_requirements_file() -> bool:
    """Prüft ob requirements.txt existiert."""
    if not REQUIREMENTS_FILE.exists():
        print_error(f"requirements.txt nicht gefunden: {REQUIREMENTS_FILE}")
        return False

    print_success("requirements.txt gefunden")
    return True


# =============================================================================
# Installation
# =============================================================================


def create_venv() -> bool:
    """Erstellt das Virtual Environment oder stellt es wieder her."""
    pip_path = get_venv_pip()

    if VENV_DIR.exists() and pip_path.exists():
        print_info("Virtual Environment existiert bereits und ist gültig.")
        return True

    if VENV_DIR.exists():
        print_warning("Virtual Environment existiert, ist aber ungültig oder unvollständig.")
        print_info("Lösche das vorhandene Virtual Environment...")
        try:
            import shutil

            shutil.rmtree(VENV_DIR)
            print_success("Altes Virtual Environment gelöscht.")
        except OSError as e:
            print_error(f"Fehler beim Löschen des Virtual Environment: {e}")
            return False

    print_info("Erstelle Virtual Environment...")
    success, _ = run_command([sys.executable, "-m", "venv", str(VENV_DIR)])

    if success:
        print_success("Virtual Environment erstellt")
    else:
        print_error("Fehler beim Erstellen des Virtual Environment")

    return success


def get_venv_python() -> Path:
    """Gibt den Pfad zum Python im venv zurück."""
    if platform.system() == "Windows":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def get_venv_pip() -> Path:
    """Gibt den Pfad zum pip im venv zurück."""
    if platform.system() == "Windows":
        return VENV_DIR / "Scripts" / "pip.exe"
    return VENV_DIR / "bin" / "pip"


def install_dependencies() -> bool:
    """Installiert die Abhängigkeiten."""
    pip_path = get_venv_pip()

    if not pip_path.exists():
        print_error(f"pip nicht gefunden: {pip_path}")
        return False

    print_info("Aktualisiere pip...")
    run_command([str(pip_path), "install", "--upgrade", "pip"], capture=True)

    print_info("Installiere Abhängigkeiten...")
    success, output = run_command([str(pip_path), "install", "-r", str(REQUIREMENTS_FILE)], capture=True)

    if success:
        print_success("Alle Abhängigkeiten installiert")
    else:
        print_error("Fehler bei der Installation")
        print(output)

    return success


def run_first_time_setup() -> bool:
    """Führt das First-Run-Setup durch."""
    python_path = get_venv_python()

    # Prüfe ob Setup bereits durchgeführt
    setup_file = Path(os.environ.get("APPDATA", "")) / "SmartDesk" / "setup.json"

    if setup_file.exists():
        print_info("Setup wurde bereits durchgeführt")

        # Prüfe ob Original Desktop existiert
        desktops_file = Path(os.environ.get("APPDATA", "")) / "SmartDesk" / "desktops.json"
        if desktops_file.exists():
            import json

            try:
                with open(desktops_file, "r", encoding="utf-8") as f:
                    desktops = json.load(f)
                has_original = any(d.get("protected", False) for d in desktops)
                if has_original:
                    print_success("Original Desktop existiert")
                    return True
                else:
                    print_warning("Kein Original Desktop gefunden - erstelle...")
            except (OSError, json.JSONDecodeError):
                pass

    print_info("Führe First-Run-Setup durch...")

    # Setup-Skript ausführen
    setup_code = """
import sys
sys.path.insert(0, "src")
from smartdesk.shared.first_run import run_first_time_setup, create_original_desktop

# First-Run Setup
result = run_first_time_setup(silent=False)

# Original Desktop erstellen falls noch nicht vorhanden
create_original_desktop(silent=False)

sys.exit(0 if result else 1)
"""

    success, _ = run_command([str(python_path), "-c", setup_code], cwd=PROJECT_ROOT)

    if success:
        print_success("First-Run-Setup abgeschlossen")
    else:
        print_warning("First-Run-Setup hatte Probleme (nicht kritisch)")

    return True  # Nicht kritisch


def verify_installation() -> bool:
    """Überprüft die Installation."""
    python_path = get_venv_python()

    # Teste ob SmartDesk importiert werden kann
    test_code = """
import sys
sys.path.insert(0, "src")
try:
    from smartdesk.core.services.desktop_service import get_all_desktops
    desktops = get_all_desktops()
    print(f"Gefundene Desktops: {len(desktops)}")
    for d in desktops:
        status = "🔒" if d.protected else "📁"
        active = " [AKTIV]" if d.is_active else ""
        print(f"  {status} {d.name}{active}")
    sys.exit(0)
except Exception as e:
    print(f"Fehler: {e}")
    sys.exit(1)
"""

    success, _ = run_command([str(python_path), "-c", test_code], cwd=PROJECT_ROOT)

    return success


# =============================================================================
# Start-Funktionen
# =============================================================================


def start_tray() -> bool:
    """Startet das Tray-Icon."""
    python_path = get_venv_python()
    main_script = SRC_DIR / "smartdesk" / "main.py"

    print_info("Starte SmartDesk Tray-Icon...")

    # Starte im Hintergrund
    if platform.system() == "Windows":
        subprocess.Popen([str(python_path), str(main_script), "start-tray"], cwd=PROJECT_ROOT, creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        subprocess.Popen([str(python_path), str(main_script), "start-tray"], cwd=PROJECT_ROOT, start_new_session=True)

    print_success("Tray-Icon gestartet")
    print_info("SmartDesk läuft jetzt im System Tray (neben der Uhr)")
    return True


# =============================================================================
# Hauptfunktion
# =============================================================================


def main():
    """Hauptfunktion."""
    import argparse

    parser = argparse.ArgumentParser(description="SmartDesk Installation")
    parser.add_argument("--no-start", action="store_true", help="Nur Installation, kein Start")
    parser.add_argument("--check", action="store_true", help="Nur Voraussetzungen prüfen")
    args = parser.parse_args()

    print_header()

    total_steps = 6 if not args.check else 2
    current_step = 0

    # Schritt 1: Voraussetzungen prüfen
    current_step += 1
    print_step(current_step, total_steps, "Voraussetzungen prüfen")

    if not check_windows():
        return 1
    if not check_python_version():
        return 1
    if not check_requirements_file():
        return 1

    if args.check:
        print("\n✅ Alle Voraussetzungen erfüllt!")
        return 0

    # Schritt 2: Virtual Environment
    current_step += 1
    print_step(current_step, total_steps, "Virtual Environment einrichten")

    if not create_venv():
        return 1

    # Schritt 3: Abhängigkeiten installieren
    current_step += 1
    print_step(current_step, total_steps, "Abhängigkeiten installieren")

    if not install_dependencies():
        return 1

    # Schritt 4: First-Run Setup
    current_step += 1
    print_step(current_step, total_steps, "SmartDesk einrichten")

    run_first_time_setup()

    # Schritt 5: Installation verifizieren
    current_step += 1
    print_step(current_step, total_steps, "Installation überprüfen")

    if verify_installation():
        print_success("Installation erfolgreich!")
    else:
        print_warning("Verifikation fehlgeschlagen (nicht kritisch)")

    # Schritt 6: Starten
    current_step += 1
    print_step(current_step, total_steps, "SmartDesk starten")

    if args.no_start:
        print_info("Start übersprungen (--no-start)")
        print()
        print("=" * 60)
        print("  ✅ Installation abgeschlossen!")
        print()
        print("  Starten Sie SmartDesk mit:")
        print(f"    python {SRC_DIR / 'smartdesk' / 'main.py'}")
        print("=" * 60)
        return 0

    print()
    print("=" * 60)
    print("  ✅ Installation abgeschlossen!")
    print("=" * 60)
    print()

    start_tray()
    print()
    print("Drücken Sie Enter zum Beenden...")
    input()

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nAbgebrochen.")
        sys.exit(1)
