import colorama
import platform

# Einmalige Initialisierung von Colorama
# autoreset=True sorgt dafür, dass die Farbe nach jedem print() zurückgesetzt wird.
colorama.init(autoreset=True)

# Definiere die Farb-Konstanten
RED = colorama.Fore.RED
GREEN = colorama.Fore.GREEN
YELLOW = colorama.Fore.YELLOW
RESET = colorama.Style.RESET_ALL

# Definiere die Prefixe für leichtere Nutzung in den anderen Dateien
# Jetzt wird ✗ rot und ✓ grün sein.
PREFIX_OK = f"{GREEN}✓{RESET}"
PREFIX_ERROR = f"{RED}✗{RESET}"
PREFIX_WARN = f"{YELLOW}!{RESET}"
