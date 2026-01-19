# SmartDesk - Desktop Manager for Windows
#
# New Package Structure:
# - core/        : Business logic and data layer
#   - models/    : Data classes (Desktop, IconPosition)
#   - services/  : Business services (desktop, icon, wallpaper, system)
#   - storage/   : File I/O operations
#   - utils/     : Utilities (registry, path validation)
# - interfaces/  : User interfaces
#   - cli/       : Command line interface
#   - gui/       : Graphical user interfaces
#   - tray/      : System tray icon
# - shared/      : Shared resources
#   - config.py  : Configuration and constants
#   - localization.py : Text strings (i18n)
#   - style.py   : Terminal styling
#   - animations/: Animation configurations
# - hotkeys/     : Global hotkey handling

__version__ = "0.4.0"
