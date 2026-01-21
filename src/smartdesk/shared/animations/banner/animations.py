# Dateipfad: src/smartdesk/shared/animations/banner/animations.py
"""
Moderne Animationen für das TaskbarBanner.

Enthält flüssige Slide- und Fade-Animationen mit
verschiedenen Easing-Funktionen für ein professionelles Erscheinungsbild.
"""

import tkinter as tk
import math
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


class EasingFunctions:
    """
    Sammlung von Easing-Funktionen für flüssige Animationen.

    Alle Funktionen nehmen einen Progress-Wert (0.0 - 1.0) und
    geben einen interpolierten Wert zurück.
    """

    @staticmethod
    def linear(t: float) -> float:
        """Lineare Interpolation."""
        return t

    @staticmethod
    def ease_in(t: float) -> float:
        """Langsamer Start, schnelles Ende (quadratisch)."""
        return t * t

    @staticmethod
    def ease_out(t: float) -> float:
        """Schneller Start, langsames Ende (quadratisch)."""
        return 1 - (1 - t) * (1 - t)

    @staticmethod
    def ease_in_out(t: float) -> float:
        """Langsamer Start und Ende, schnell in der Mitte."""
        if t < 0.5:
            return 2 * t * t
        return 1 - pow(-2 * t + 2, 2) / 2

    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """Cubic ease-out - sehr flüssig."""
        return 1 - pow(1 - t, 3)

    @staticmethod
    def ease_out_quart(t: float) -> float:
        """Quartic ease-out - noch flüssiger."""
        return 1 - pow(1 - t, 4)

    @staticmethod
    def ease_out_expo(t: float) -> float:
        """Exponential ease-out - dramatischer Effekt."""
        return 1 if t == 1 else 1 - pow(2, -10 * t)

    @staticmethod
    def ease_out_back(t: float) -> float:
        """Ease-out mit leichtem Überschwingen - federnder Effekt."""
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)


class SlideAnimator(BannerAnimator):
    """
    Moderne Slide-Animation für das Banner.

    Kombiniert Slide- und Fade-Effekte für ein
    professionelles Erscheinungsbild.
    """

    def __init__(
        self,
        config: Optional[BannerAnimation] = None,
        target_y: int = 0,
        start_y: int = 0,
        window_width: int = 300,
        window_height: int = 50,
        x_pos: int = 0,
    ):
        self.config = config or BannerAnimation()
        self.target_y = target_y
        self.start_y = start_y
        self.window_width = window_width
        self.window_height = window_height
        self.x_pos = x_pos

    def _get_easing_func(self) -> Callable[[float], float]:
        """Gibt die konfigurierte Easing-Funktion zurück."""
        easing_map = {
            "linear": EasingFunctions.linear,
            "ease-in": EasingFunctions.ease_in,
            "ease-out": EasingFunctions.ease_out_cubic,
            "ease-in-out": EasingFunctions.ease_in_out,
            "cubic": EasingFunctions.ease_out_cubic,
            "quart": EasingFunctions.ease_out_quart,
            "expo": EasingFunctions.ease_out_expo,
            "back": EasingFunctions.ease_out_back,
        }
        return easing_map.get(self.config.easing, EasingFunctions.ease_out_cubic)

    def animate_in(self, window: tk.Toplevel, callback: Optional[Callable] = None) -> None:
        """
        Slide-Up + Fade-In Animation.

        Das Banner gleitet sanft von unten nach oben
        während es gleichzeitig einblendet.
        """
        cfg = self.config
        steps = cfg.slide_up_steps
        easing = self._get_easing_func()

        # Berechne Slide-Distanz
        slide_distance = getattr(cfg, "slide_up_distance", 60)
        actual_start_y = self.target_y + slide_distance

        try:
            for i in range(steps + 1):
                progress = i / steps
                eased = easing(progress)

                # Berechne Y-Position (von unten nach oben)
                y_pos = actual_start_y - slide_distance * eased

                # Setze Geometrie
                window.geometry(f"{self.window_width}x{self.window_height}" f"+{self.x_pos}+{int(y_pos)}")

                # Setze Transparenz - Fade-in etwas schneller
                alpha_progress = min(1.0, progress * 1.2)
                alpha = alpha_progress * cfg.max_alpha
                window.attributes("-alpha", min(alpha, cfg.max_alpha))

                window.update()
                window.after(cfg.slide_up_delay_ms)

            # Finale Position sicherstellen
            window.geometry(f"{self.window_width}x{self.window_height}" f"+{self.x_pos}+{self.target_y}")
            window.attributes("-alpha", cfg.max_alpha)

            if callback:
                callback()

        except tk.TclError:
            pass

    def animate_out(self, window: tk.Toplevel, callback: Optional[Callable] = None) -> None:
        """
        Slide-Down + Fade-Out Animation.

        Das Banner gleitet sanft nach unten
        während es gleichzeitig ausblendet.
        """
        cfg = self.config
        steps = cfg.slide_down_steps

        # Für Ausblenden verwenden wir ease-in-out
        easing = EasingFunctions.ease_in_out

        # Berechne Slide-Distanz
        slide_distance = getattr(cfg, "slide_down_distance", 40)

        try:
            for i in range(steps + 1):
                progress = i / steps
                eased = easing(progress)

                # Berechne Y-Position (nach unten)
                y_pos = self.target_y + slide_distance * eased

                # Setze Geometrie
                window.geometry(f"{self.window_width}x{self.window_height}" f"+{self.x_pos}+{int(y_pos)}")

                # Transparenz - Fade schneller als Slide
                alpha_progress = 1 - min(1.0, progress * 1.4)
                alpha = max(0, alpha_progress * cfg.max_alpha)
                window.attributes("-alpha", alpha)

                window.update()
                window.after(cfg.slide_down_delay_ms)

            # Komplett ausgeblendet
            window.attributes("-alpha", 0)

            if callback:
                callback()

        except tk.TclError:
            pass


class FadeAnimator(BannerAnimator):
    """
    Reine Fade-Animation für das Banner.

    Blendet das Banner ein/aus ohne Bewegung.
    Nützlich für subtilere Benachrichtigungen.
    """

    def __init__(self, config: Optional[BannerAnimation] = None):
        self.config = config or BannerAnimation()

    def animate_in(self, window: tk.Toplevel, callback: Optional[Callable] = None) -> None:
        """Fade-In Animation."""
        cfg = self.config
        steps = cfg.slide_up_steps

        try:
            for i in range(steps + 1):
                progress = i / steps
                alpha = progress * cfg.max_alpha
                window.attributes("-alpha", alpha)
                window.update()
                window.after(cfg.slide_up_delay_ms)

            if callback:
                callback()

        except tk.TclError:
            pass

    def animate_out(self, window: tk.Toplevel, callback: Optional[Callable] = None) -> None:
        """Fade-Out Animation."""
        cfg = self.config
        steps = cfg.slide_down_steps

        try:
            for i in range(steps, -1, -1):
                progress = i / steps
                alpha = progress * cfg.max_alpha
                window.attributes("-alpha", alpha)
                window.update()
                window.after(cfg.slide_down_delay_ms)

            if callback:
                callback()

        except tk.TclError:
            pass
