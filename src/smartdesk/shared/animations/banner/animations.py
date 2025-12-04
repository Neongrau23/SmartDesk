# Dateipfad: src/smartdesk/shared/animations/banner/animations.py
"""
Animationen für das TaskbarBanner.

Enthält die Slide-Up/Slide-Down Animationslogik.
Kann erweitert werden für weitere Animationseffekte.
"""

import tkinter as tk
from typing import Callable, Optional
from abc import ABC, abstractmethod

from .config import BannerAnimation


class BannerAnimator(ABC):
    """Abstrakte Basisklasse für Banner-Animationen."""
    
    @abstractmethod
    def animate_in(self, window: tk.Toplevel, callback: Optional[Callable] = None) -> None:
        """Animiert das Banner ins Sichtfeld."""
        pass
    
    @abstractmethod
    def animate_out(self, window: tk.Toplevel, callback: Optional[Callable] = None) -> None:
        """Animiert das Banner aus dem Sichtfeld."""
        pass


class SlideAnimator(BannerAnimator):
    """
    Slide-Animation für das Banner.
    
    Animiert das Banner von unten nach oben (rein)
    und von oben nach unten (raus).
    """
    
    def __init__(
        self,
        config: Optional[BannerAnimation] = None,
        target_y: int = 0,
        start_y: int = 0,
        window_width: int = 300,
        window_height: int = 50,
        x_pos: int = 0
    ):
        self.config = config or BannerAnimation()
        self.target_y = target_y
        self.start_y = start_y
        self.window_width = window_width
        self.window_height = window_height
        self.x_pos = x_pos
    
    def _ease_out(self, progress: float) -> float:
        """Ease-out Kurve (schneller Start, langsames Ende)."""
        return 1 - pow(1 - progress, 3)
    
    def _ease_in(self, progress: float) -> float:
        """Ease-in Kurve (langsamer Start, schnelles Ende)."""
        return pow(progress, 3)
    
    def _linear(self, progress: float) -> float:
        """Lineare Interpolation."""
        return progress
    
    def _get_easing_func(self) -> Callable[[float], float]:
        """Gibt die konfigurierte Easing-Funktion zurück."""
        easing_map = {
            'ease-out': self._ease_out,
            'ease-in': self._ease_in,
            'linear': self._linear
        }
        return easing_map.get(self.config.easing, self._ease_out)
    
    def animate_in(
        self,
        window: tk.Toplevel,
        callback: Optional[Callable] = None
    ) -> None:
        """
        Slide-Up Animation.
        
        Args:
            window: Das zu animierende Fenster
            callback: Optionale Funktion nach Abschluss
        """
        cfg = self.config
        steps = cfg.slide_up_steps
        easing = self._get_easing_func()
        
        try:
            for i in range(steps + 1):
                progress = i / steps
                eased = easing(progress)
                
                # Berechne Y-Position
                y_pos = self.start_y - (self.start_y - self.target_y) * eased
                
                # Setze Geometrie
                window.geometry(
                    f'{self.window_width}x{self.window_height}'
                    f'+{self.x_pos}+{int(y_pos)}'
                )
                
                # Setze Transparenz
                alpha = eased * cfg.max_alpha
                window.attributes('-alpha', alpha)
                
                window.update()
                window.after(cfg.slide_up_delay_ms)
            
            if callback:
                callback()
                
        except tk.TclError:
            pass
    
    def animate_out(
        self,
        window: tk.Toplevel,
        callback: Optional[Callable] = None
    ) -> None:
        """
        Slide-Down Animation.
        
        Args:
            window: Das zu animierende Fenster
            callback: Optionale Funktion nach Abschluss
        """
        cfg = self.config
        steps = cfg.slide_down_steps
        easing = self._get_easing_func()
        
        try:
            screen_height = window.winfo_screenheight()
            
            for i in range(steps, -1, -1):
                progress = i / steps
                eased = easing(progress)
                
                # Berechne Y-Position
                y_pos = self.target_y + (screen_height - self.target_y) * (1 - eased)
                
                # Setze Geometrie
                window.geometry(
                    f'{self.window_width}x{self.window_height}'
                    f'+{self.x_pos}+{int(y_pos)}'
                )
                
                # Setze Transparenz
                alpha = progress * cfg.max_alpha
                window.attributes('-alpha', alpha)
                
                window.update()
                window.after(cfg.slide_down_delay_ms)
            
            if callback:
                callback()
                
        except tk.TclError:
            pass


class FadeAnimator(BannerAnimator):
    """
    Fade-Animation für das Banner (Alternative zu Slide).
    
    Blendet das Banner ein/aus ohne Bewegung.
    """
    
    def __init__(
        self,
        config: Optional[BannerAnimation] = None
    ):
        self.config = config or BannerAnimation()
    
    def animate_in(
        self,
        window: tk.Toplevel,
        callback: Optional[Callable] = None
    ) -> None:
        """Fade-In Animation."""
        cfg = self.config
        steps = cfg.slide_up_steps
        
        try:
            for i in range(steps + 1):
                progress = i / steps
                alpha = progress * cfg.max_alpha
                window.attributes('-alpha', alpha)
                window.update()
                window.after(cfg.slide_up_delay_ms)
            
            if callback:
                callback()
                
        except tk.TclError:
            pass
    
    def animate_out(
        self,
        window: tk.Toplevel,
        callback: Optional[Callable] = None
    ) -> None:
        """Fade-Out Animation."""
        cfg = self.config
        steps = cfg.slide_down_steps
        
        try:
            for i in range(steps, -1, -1):
                progress = i / steps
                alpha = progress * cfg.max_alpha
                window.attributes('-alpha', alpha)
                window.update()
                window.after(cfg.slide_down_delay_ms)
            
            if callback:
                callback()
                
        except tk.TclError:
            pass
