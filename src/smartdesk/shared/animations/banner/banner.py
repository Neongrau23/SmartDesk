# Dateipfad: src/smartdesk/shared/animations/banner/banner.py
"""
Haupt-Banner-Klasse (Orchestrierung).

Kombiniert Widget, Theme, Config und Animationen.
Dies ist die öffentliche API für das Banner.
"""

from typing import Optional, Callable

from .theme import BannerTheme, DEFAULT_THEME
from .config import BannerConfig, DEFAULT_CONFIG
from .animations import SlideAnimator, BannerAnimator
from .banner_widget import BannerWidget

# Logger
try:
    from ...logging_config import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


class TaskbarBanner:
    """
    Animierte Benachrichtigungsleiste am unteren Bildschirmrand.

    Dies ist die Hauptklasse für das Banner-System.
    Sie orchestriert Widget, Theme, Config und Animationen.

    Verwendung:
        # Einfach
        banner = TaskbarBanner(message="Hallo Welt!")
        banner.show()
        banner.close()

        # Mit Theme
        from .theme import DARK_THEME
        banner = TaskbarBanner(message="Dunkel", theme=DARK_THEME)

        # Mit Config
        from .config import FAST_CONFIG
        banner = TaskbarBanner(message="Schnell", config=FAST_CONFIG)
    """

    def __init__(
        self,
        message: str = "Benachrichtigung",
        icon: str = "ℹ",
        theme: Optional[BannerTheme] = None,
        config: Optional[BannerConfig] = None,
        on_close: Optional[Callable[[], None]] = None,
        parent=None,
    ):
        """
        Erstellt ein neues Banner.

        Args:
            message: Der anzuzeigende Text
            icon: Emoji/Symbol links vom Text
            theme: Optionales Theme (Farben, Fonts)
            config: Optionale Config (Größen, Animation)
            on_close: Callback wenn Banner geschlossen wird
            parent: Optionales Parent-Fenster (tk.Tk)
        """
        self.theme = theme or DEFAULT_THEME
        self.config = config or DEFAULT_CONFIG
        self.on_close_callback = on_close

        self._is_visible = False
        self._is_closing = False

        # Widget erstellen
        self._widget = BannerWidget(
            message=message,
            icon=icon,
            theme=self.theme,
            config=self.config,
            on_close=self._handle_close,
            parent=parent,
        )

        # Geometrie berechnen
        self._geometry = self._widget.calculate_geometry()
        width, height, x, target_y, start_y = self._geometry

        # Initial-Position setzen (außerhalb des Bildschirms)
        self._widget.set_geometry(width, height, x, start_y)

        # Animator erstellen
        self._animator: BannerAnimator = SlideAnimator(
            config=self.config.animation,
            target_y=target_y,
            start_y=start_y,
            window_width=width,
            window_height=height,
            x_pos=x,
        )

    def _handle_close(self) -> None:
        """Interner Handler für Close-Events."""
        self.close()

    def show(self, auto_close_ms: Optional[int] = None) -> None:
        """
        Zeigt das Banner mit Animation.

        Args:
            auto_close_ms: Optionale Zeit in ms bis zum automatischen Schließen
        """
        if self._is_visible or self._is_closing:
            return

        self._is_visible = True

        try:
            self._widget.show()
            self._animator.animate_in(self._widget.window)

            # Auto-Close Timer
            close_delay = auto_close_ms or self.config.behavior.auto_close_ms
            if close_delay:
                self._widget.window.after(close_delay, self.close)

        except Exception as e:
            logger.debug(f"Banner show error: {e}")

    def close(self) -> None:
        """Schließt das Banner mit Animation."""
        if self._is_closing or not self._is_visible:
            return

        self._is_closing = True

        try:
            self._animator.animate_out(self._widget.window)

            if self.on_close_callback:
                try:
                    self.on_close_callback()
                except Exception as e:
                    logger.debug(f"Close callback error: {e}")

            self._widget.destroy()

        except Exception as e:
            logger.debug(f"Banner close error: {e}")
        finally:
            self._is_visible = False
            self._is_closing = False

    def update_message(self, message: str, icon: Optional[str] = None) -> None:
        """Aktualisiert den angezeigten Text."""
        self._widget.update_message(message, icon)

    @property
    def is_visible(self) -> bool:
        """Gibt zurück, ob das Banner sichtbar ist."""
        return self._is_visible and not self._is_closing

    @property
    def root(self):
        """Gibt das Tkinter-Fenster zurück (für Kompatibilität)."""
        return self._widget.window


# =============================================================================
# Convenience Functions
# =============================================================================


def show_desktop_status(parent=None) -> TaskbarBanner:
    """
    Zeigt den aktuellen Desktop-Status als Banner.

    Returns:
        TaskbarBanner-Instanz (zum manuellen Schließen)
    """
    try:
        from ....core.services import desktop_service
        from .theme import DEFAULT_THEME

        desktops = desktop_service.get_all_desktops(sync_registry=True)
        icons = DEFAULT_THEME.icons

        if not desktops:
            message = "Keine SmartDesk-Desktops konfiguriert"
            icon = icons.warning
        else:
            parts = []
            active_found = False

            for d in desktops:
                if d.is_active:
                    parts.append(f"{icons.separator}{icons.active_marker_1}{d.name}{icons.active_marker_2}{icons.separator}")
                    active_found = True
                else:
                    parts.append(f"{icons.separator}{icons.inactive_marker_1}{d.name}{icons.inactive_marker_2}{icons.separator}")

            message = "    ".join(parts)
            if active_found:
                icon = icons.desktop_active
            else:
                icon = icons.desktop_inactive

    except ImportError:
        message = "SmartDesk Status nicht verfügbar"
        icon = "⚠"
    except Exception as e:
        logger.error(f"Fehler beim Laden der Desktops: {e}")
        message = f"Fehler: {e}"
        icon = "❌"

    banner = TaskbarBanner(message=message, icon=icon, parent=parent)
    banner.show()
    return banner


def show_notification(
    message: str,
    icon: str = "ℹ",
    auto_close_ms: int = 3000,
    theme: Optional[BannerTheme] = None,
    config: Optional[BannerConfig] = None,
    parent=None,
) -> TaskbarBanner:
    """
    Zeigt eine einfache Benachrichtigung.

    Args:
        message: Der anzuzeigende Text
        icon: Emoji/Symbol
        auto_close_ms: Zeit bis zum automatischen Schließen
        theme: Optionales Theme
        config: Optionale Config
        parent: Optionales Parent-Fenster

    Returns:
        TaskbarBanner-Instanz
    """
    banner = TaskbarBanner(
        message=message, icon=icon, theme=theme, config=config, parent=parent
    )
    banner.show(auto_close_ms=auto_close_ms)
    return banner
