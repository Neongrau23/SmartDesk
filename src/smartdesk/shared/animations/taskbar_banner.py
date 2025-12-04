# Dateipfad: src/smartdesk/shared/animations/taskbar_banner.py
"""
Animierte Taskbar-Benachrichtigung für SmartDesk.

Zeigt eine elegante Benachrichtigungsleiste am unteren Bildschirmrand.
Unterstützt Slide-Up/Slide-Down Animationen.

Verwendung:
    from smartdesk.shared.animations.taskbar_banner import (
        TaskbarBanner,
        show_desktop_status
    )
    
    # Einfache Nutzung
    show_desktop_status()
    
    # Oder mit eigenem Text
    banner = TaskbarBanner(message="Hallo Welt", icon="🎉")
    banner.show()
    banner.close()  # Oder nach Timeout
"""

import tkinter as tk
import tkinter.font as tkFont
import sys
from typing import Optional, Callable
from dataclasses import dataclass

# Logger
try:
    from ..logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


@dataclass
class BannerConfig:
    """Konfiguration für das Banner."""
    # Farben
    bg_color: str = "#1a1a1a"
    accent_color: str = "#0078d4"
    text_color: str = "#ffffff"
    border_color: str = "#404040"
    
    # Größen
    min_width: int = 300
    max_width_margin: int = 40
    height: int = 50
    margin_bottom: int = 50
    
    # Animation
    slide_up_steps: int = 20
    slide_down_steps: int = 15
    animation_delay_ms: int = 5
    
    # Verhalten
    auto_close_ms: Optional[int] = None  # None = manuell schließen


class TaskbarBanner:
    """
    Animierte Benachrichtigungsleiste am unteren Bildschirmrand.
    
    Attributes:
        message: Der anzuzeigende Text
        icon: Emoji/Symbol links vom Text
        config: Optionale Konfiguration
        on_close: Callback wenn Banner geschlossen wird
    """
    
    def __init__(
        self,
        message: str = "Benachrichtigung",
        icon: str = "ℹ",
        config: Optional[BannerConfig] = None,
        on_close: Optional[Callable[[], None]] = None,
        parent: Optional[tk.Tk] = None
    ):
        self.message = message
        self.icon = icon
        self.config = config or BannerConfig()
        self.on_close_callback = on_close
        self._is_visible = False
        self._is_closing = False
        
        # Root-Fenster
        if parent:
            self.root = tk.Toplevel(parent)
            self._owns_root = False
        else:
            self.root = tk.Tk()
            self.root.withdraw()
            self._owns_root = True
        
        self._setup_window()
        self._create_ui()
        self._calculate_geometry()
    
    def _setup_window(self) -> None:
        """Konfiguriert das Fenster."""
        self.root.title("")
        self.root.overrideredirect(True)
        self.root.configure(bg='#000000')
        
        if sys.platform == 'win32':
            self.root.wm_attributes('-topmost', 1)
            self.root.attributes('-toolwindow', True)
        else:
            self.root.attributes('-topmost', True)
        
        self.root.attributes('-alpha', 0.0)
    
    def _create_ui(self) -> None:
        """Erstellt die UI-Elemente."""
        cfg = self.config
        
        # Hauptframe mit Rahmen
        main_frame = tk.Frame(
            self.root,
            bg=cfg.bg_color,
            highlightbackground=cfg.border_color,
            highlightthickness=1
        )
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Akzent-Streifen oben
        accent_stripe = tk.Frame(main_frame, bg=cfg.accent_color, height=3)
        accent_stripe.pack(side=tk.TOP, fill=tk.X)
        
        # Content
        content_frame = tk.Frame(main_frame, bg=cfg.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Icon
        self.icon_label = tk.Label(
            content_frame,
            text=self.icon,
            font=('Segoe UI Emoji', 18),
            fg=cfg.accent_color,
            bg=cfg.bg_color
        )
        self.icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Nachricht
        self.message_font = tkFont.Font(family='Segoe UI', size=11)
        self.message_label = tk.Label(
            content_frame,
            text=self.message,
            font=self.message_font,
            fg=cfg.text_color,
            bg=cfg.bg_color,
            anchor='w'
        )
        self.message_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Schließen-Button
        close_btn = tk.Label(
            content_frame,
            text='✕',
            font=('Segoe UI', 12),
            fg='#8a8a8a',
            bg=cfg.bg_color,
            cursor='hand2',
            padx=10
        )
        close_btn.pack(side=tk.RIGHT)
        close_btn.bind('<Button-1>', lambda e: self.close())
        close_btn.bind('<Enter>', lambda e: close_btn.config(fg='#ffffff'))
        close_btn.bind('<Leave>', lambda e: close_btn.config(fg='#8a8a8a'))
    
    def _calculate_geometry(self) -> None:
        """Berechnet Fensterposition und -größe."""
        cfg = self.config
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Breite basierend auf Text
        text_width = self.message_font.measure(self.message)
        static_width = 45 + 40 + 40 + 20  # Icon + Padding + Button
        calculated_width = text_width + static_width
        
        max_width = screen_width - cfg.max_width_margin
        self.window_width = max(cfg.min_width, min(calculated_width, max_width))
        self.window_height = cfg.height
        
        # Position: Zentriert am unteren Rand
        self.x_pos = (screen_width - self.window_width) // 2
        self.target_y = screen_height - self.window_height - cfg.margin_bottom
        self.current_y = screen_height  # Start außerhalb
        
        self.root.geometry(
            f'{self.window_width}x{self.window_height}'
            f'+{self.x_pos}+{self.current_y}'
        )
    
    def update_message(self, message: str, icon: Optional[str] = None) -> None:
        """Aktualisiert den angezeigten Text."""
        self.message = message
        self.message_label.config(text=message)
        
        if icon:
            self.icon = icon
            self.icon_label.config(text=icon)
    
    def show(self, auto_close_ms: Optional[int] = None) -> None:
        """
        Zeigt das Banner mit Slide-Up Animation.
        
        Args:
            auto_close_ms: Optionale Zeit in ms bis zum automatischen Schließen
        """
        if self._is_visible or self._is_closing:
            return
        
        self._is_visible = True
        
        try:
            self.root.deiconify()
            self.root.update()
            self.root.lift()
            self._slide_up()
            
            # Auto-Close Timer
            close_delay = auto_close_ms or self.config.auto_close_ms
            if close_delay:
                self.root.after(close_delay, self.close)
                
        except tk.TclError as e:
            logger.debug(f"Banner show error: {e}")
    
    def close(self) -> None:
        """Schließt das Banner mit Slide-Down Animation."""
        if self._is_closing or not self._is_visible:
            return
        
        self._is_closing = True
        
        try:
            self._slide_down()
            
            if self.on_close_callback:
                try:
                    self.on_close_callback()
                except Exception as e:
                    logger.debug(f"Close callback error: {e}")
            
            self.root.destroy()
            
        except tk.TclError:
            pass
        finally:
            self._is_visible = False
            self._is_closing = False
    
    def _slide_up(self) -> None:
        """Slide-Up Animation mit Easing."""
        cfg = self.config
        steps = cfg.slide_up_steps
        
        try:
            for i in range(steps + 1):
                progress = i / steps
                eased = 1 - pow(1 - progress, 3)  # Ease-out
                
                y_pos = self.current_y - (self.current_y - self.target_y) * eased
                self.root.geometry(
                    f'{self.window_width}x{self.window_height}'
                    f'+{self.x_pos}+{int(y_pos)}'
                )
                
                alpha = eased * 0.96
                self.root.attributes('-alpha', alpha)
                self.root.update()
                self.root.after(cfg.animation_delay_ms)
                
        except tk.TclError:
            pass
    
    def _slide_down(self) -> None:
        """Slide-Down Animation mit Easing."""
        cfg = self.config
        steps = cfg.slide_down_steps
        screen_height = self.root.winfo_screenheight()
        
        try:
            for i in range(steps, -1, -1):
                progress = i / steps
                eased = 1 - pow(1 - progress, 3)
                
                y_pos = self.target_y + (screen_height - self.target_y) * (1 - eased)
                self.root.geometry(
                    f'{self.window_width}x{self.window_height}'
                    f'+{self.x_pos}+{int(y_pos)}'
                )
                
                alpha = progress * 0.96
                self.root.attributes('-alpha', alpha)
                self.root.update()
                self.root.after(cfg.animation_delay_ms)
                
        except tk.TclError:
            pass
    
    @property
    def is_visible(self) -> bool:
        """Gibt zurück, ob das Banner sichtbar ist."""
        return self._is_visible and not self._is_closing


# =============================================================================
# Convenience Functions
# =============================================================================

def show_desktop_status(parent: Optional[tk.Tk] = None) -> TaskbarBanner:
    """
    Zeigt den aktuellen Desktop-Status als Banner.
    
    Returns:
        TaskbarBanner-Instanz (zum manuellen Schließen)
    """
    try:
        from ...core.services import desktop_service
        
        desktops = desktop_service.get_all_desktops()
        
        if not desktops:
            message = "Keine SmartDesk-Desktops konfiguriert"
            icon = "⚠"
        else:
            parts = []
            active_found = False
            
            for d in desktops:
                if d.is_active:
                    parts.append(f"▶ {d.name}")
                    active_found = True
                else:
                    parts.append(f"• {d.name}")
            
            message = "    ".join(parts)
            icon = "💻" if active_found else "🔔"
            
    except ImportError:
        message = "SmartDesk Status nicht verfügbar"
        icon = "⚠"
    except Exception as e:
        logger.error(f"Fehler beim Laden der Desktops: {e}")
        message = f"Fehler: {e}"
        icon = "❌"
    
    banner = TaskbarBanner(
        message=message,
        icon=icon,
        parent=parent
    )
    banner.show()
    return banner


def show_notification(
    message: str,
    icon: str = "ℹ",
    auto_close_ms: int = 3000,
    parent: Optional[tk.Tk] = None
) -> TaskbarBanner:
    """
    Zeigt eine einfache Benachrichtigung.
    
    Args:
        message: Der anzuzeigende Text
        icon: Emoji/Symbol
        auto_close_ms: Zeit bis zum automatischen Schließen
        parent: Optionales Parent-Fenster
        
    Returns:
        TaskbarBanner-Instanz
    """
    banner = TaskbarBanner(
        message=message,
        icon=icon,
        parent=parent
    )
    banner.show(auto_close_ms=auto_close_ms)
    return banner
