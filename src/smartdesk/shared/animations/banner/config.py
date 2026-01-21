# Dateipfad: src/smartdesk/shared/animations/banner/config.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class BannerSize:
    """GrÃ¶ÃŸen-Konfiguration fÃ¼r das Banner."""

    # Minimale und maximale Breite
    min_width: int = 300
    max_width_margin: int = 40  # Abstand zum Bildschirmrand

    # HÃ¶he

    height: int = 50

    # Akzent-Streifen

    accent_stripe_height: int = 3

    # Padding

    content_padding_x: int = 10

    content_padding_y: int = 10

    icon_padding_right: int = 10

    close_button_padding_x: int = 10


@dataclass
class BannerPosition:
    """Positions-Konfiguration fÃ¼r das Banner."""

    # Abstand zum unteren Bildschirmrand

    margin_bottom: int = 53

    # Horizontale Ausrichtung: 'center', 'left', 'right'

    horizontal_align: str = "center"

    # Offset fÃ¼r left/right Ausrichtung

    margin_horizontal: int = 20


@dataclass
class BannerAnimation:
    """Animations-Konfiguration für das Banner."""

    # Slide-Up Animation (Einblenden)
    slide_up_steps: int = 20  # Mehr Steps = flüssiger
    slide_up_delay_ms: int = 1  # Etwas langsamer für smootheren Effekt
    slide_up_distance: int = 40  # Wie weit das Banner slidet

    # Slide-Down Animation (Ausblenden)
    slide_down_steps: int = 20  # Schneller als Einblenden
    slide_down_delay_ms: int = 6
    slide_down_distance: int = 40  # Kürzere Distanz beim Ausblenden

    # Transparenz
    max_alpha: float = 1.0  # vollständig sichtbar
    min_alpha: float = 0.0  # Komplett transparent

    # Easing-Funktion
    # Optionen: 'ease-out', 'ease-in', 'ease-in-out', 'cubic-bezier', 'spring'
    easing: str = "ease-out"

    # Spring-Animation Parameter (für easing='spring')
    spring_tension: float = 0.3
    spring_friction: float = 0.7


@dataclass
class BannerBehavior:
    """Verhaltens-Konfiguration fÃ¼r das Banner."""

    # Automatisches SchlieÃŸen (None = manuell)

    auto_close_ms: Optional[int] = None

    # Klick auf Banner schlieÃŸt es

    click_to_close: bool = True

    # Immer im Vordergrund

    always_on_top: bool = True

    # Als Tool-Fenster (keine Taskleisten-Anzeige)

    tool_window: bool = True


@dataclass
class BannerConfig:
    """

    Komplette Konfiguration fÃ¼r das Banner.



    Verwendung:

        config = BannerConfig()  # Standard-Konfiguration



        # Oder angepasst:

        config = BannerConfig(

            size=BannerSize(height=60),

            animation=BannerAnimation(slide_up_steps=30)

        )

    """

    size: BannerSize = None

    position: BannerPosition = None

    animation: BannerAnimation = None

    behavior: BannerBehavior = None

    def __post_init__(self):
        """Initialisiert fehlende Felder mit Standardwerten."""

        if self.size is None:

            self.size = BannerSize()

        if self.position is None:

            self.position = BannerPosition()

        if self.animation is None:

            self.animation = BannerAnimation()

        if self.behavior is None:

            self.behavior = BannerBehavior()


# =============================================================================

# Vordefinierte Konfigurationen

# =============================================================================


# Standard-Konfiguration

DEFAULT_CONFIG = BannerConfig()


# Schnelle Animation
FAST_CONFIG = BannerConfig(
    animation=BannerAnimation(
        slide_up_steps=15,
        slide_down_steps=12,
        slide_up_delay_ms=5,
        slide_down_delay_ms=4,
        slide_up_distance=40,
        slide_down_distance=30,
    )
)

# Langsame Animation (eleganter)
SLOW_CONFIG = BannerConfig(
    animation=BannerAnimation(
        slide_up_steps=35,
        slide_down_steps=30,
        slide_up_delay_ms=12,
        slide_down_delay_ms=10,
        slide_up_distance=80,
        slide_down_distance=60,
        easing="ease-in-out",
    )
)


# GroÃŸes Banner

LARGE_CONFIG = BannerConfig(size=BannerSize(height=70, min_width=400))


# Kompaktes Banner

COMPACT_CONFIG = BannerConfig(size=BannerSize(height=40, min_width=250, content_padding_x=15, content_padding_y=8))
