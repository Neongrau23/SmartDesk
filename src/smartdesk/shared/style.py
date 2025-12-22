# Dateipfad: src/smartdesk/shared/style.py

import colorama

# Einmalige Initialisierung von Colorama
colorama.init(autoreset=True)

# Definiere die Farb-Konstanten
RED = colorama.Fore.RED
GREEN = colorama.Fore.GREEN
YELLOW = colorama.Fore.YELLOW
RESET = colorama.Style.RESET_ALL

# Prefixe für Ausgaben
PREFIX_OK = f"{GREEN}✓{RESET}"
PREFIX_ERROR = f"{RED}✗{RESET}"
PREFIX_WARN = f"{YELLOW}!{RESET}"


def format_status_active(text: str) -> str:
    """Formattiert einen Text als grünen, aktiven Status."""
    return f"[{GREEN}{text}{RESET}]"


def format_status_inactive(text: str) -> str:
    """Formattiert einen Text als inaktiven Status in Klammern."""
    return f"[{text}]"
