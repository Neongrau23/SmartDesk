# Dateipfad: src/smartdesk/shared/logging_config.py
"""
Zentrales Logging-System für SmartDesk.
Ersetzt alle print()-Aufrufe durch strukturiertes Logging.
"""

import logging
import os
import sys

# Logging-Level über Umgebungsvariable steuerbar
DEBUG_MODE = os.environ.get('SMARTDESK_DEBUG', '').lower() in ('1', 'true', 'yes')

# Log-Datei im AppData-Verzeichnis
try:
    LOG_DIR = os.path.join(os.environ['APPDATA'], 'SmartDesk', 'logs')
    os.makedirs(LOG_DIR, exist_ok=True)
    LOG_FILE = os.path.join(LOG_DIR, 'smartdesk.log')
except Exception:
    LOG_DIR = None
    LOG_FILE = None


def get_logger(name: str) -> logging.Logger:
    """
    Erstellt einen konfigurierten Logger für ein Modul.

    Verwendung:
        from smartdesk.shared.logging_config import get_logger
        logger = get_logger(__name__)

        logger.debug("Debug-Info")      # Nur wenn SMARTDESK_DEBUG=1
        logger.info("Normale Info")     # Immer in Logdatei
        logger.warning("Warnung")       # Immer sichtbar
        logger.error("Fehler")          # Immer sichtbar
    """
    logger = logging.getLogger(name)

    # Nur konfigurieren wenn noch keine Handler vorhanden
    if not logger.handlers:
        logger.setLevel(logging.DEBUG if DEBUG_MODE else logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )

        # Console Handler (nur Warnungen+ in Produktion)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG if DEBUG_MODE else logging.WARNING)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File Handler (alles loggen)
        if LOG_FILE:
            try:
                file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8', mode='a')
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception:
                pass  # Kein File-Logging möglich

    return logger


def enable_debug_mode():
    """Aktiviert Debug-Modus zur Laufzeit."""
    global DEBUG_MODE
    DEBUG_MODE = True

    # Alle existierenden Logger aktualisieren
    for name in logging.Logger.manager.loggerDict:
        if name.startswith('smartdesk'):
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    handler.setLevel(logging.DEBUG)


def disable_debug_mode():
    """Deaktiviert Debug-Modus zur Laufzeit."""
    global DEBUG_MODE
    DEBUG_MODE = False

    for name in logging.Logger.manager.loggerDict:
        if name.startswith('smartdesk'):
            logger = logging.getLogger(name)
            logger.setLevel(logging.INFO)
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    handler.setLevel(logging.WARNING)
