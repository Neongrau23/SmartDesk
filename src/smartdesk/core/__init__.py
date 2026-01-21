# SmartDesk Core Module
# Enthält die Kernlogik, unabhängig von der Benutzeroberfläche

from .services import desktop_service, icon_service, wallpaper_service, system_service

__all__ = ["desktop_service", "icon_service", "wallpaper_service", "system_service"]
