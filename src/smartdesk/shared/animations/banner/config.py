# Dateipfad: src/smartdesk/shared/animations/banner/config.py

"""

Konfiguration fÃ¼r das TaskbarBanner.



Hier werden alle GrÃ¶ÃŸen, Positionen und Timing-Werte definiert:

- FenstergrÃ¶ÃŸen

- Positionen

- Animationsparameter



Um das Verhalten anzupassen, bearbeite diese Datei.

"""



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

    content_padding_x: int = 20

    content_padding_y: int = 10

    icon_padding_right: int = 15

    close_button_padding_x: int = 10





@dataclass

class BannerPosition:

    """Positions-Konfiguration fÃ¼r das Banner."""



    # Abstand zum unteren Bildschirmrand

    margin_bottom: int = 50



    # Horizontale Ausrichtung: 'center', 'left', 'right'

    horizontal_align: str = 'center'



    # Offset fÃ¼r left/right Ausrichtung

    margin_horizontal: int = 20





@dataclass

class BannerAnimation:

    """Animations-Konfiguration fÃ¼r das Banner."""



    # Slide-Up Animation

    slide_up_steps: int = 20

    slide_up_delay_ms: int = 5



    # Slide-Down Animation

    slide_down_steps: int = 15

    slide_down_delay_ms: int = 5



    # Maximale Transparenz (0.0 - 1.0)

    max_alpha: float = 0.96



    # Easing-Funktion: 'ease-out' (Standard), 'linear', 'ease-in'

    easing: str = 'ease-out'





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

        slide_up_steps=10,

        slide_down_steps=8,

        slide_up_delay_ms=3,

        slide_down_delay_ms=3,

    )

)



# Langsame Animation (eleganter)

SLOW_CONFIG = BannerConfig(

    animation=BannerAnimation(

        slide_up_steps=30,

        slide_down_steps=25,

        slide_up_delay_ms=8,

        slide_down_delay_ms=8,

    )

)



# GroÃŸes Banner

LARGE_CONFIG = BannerConfig(size=BannerSize(height=70, min_width=400))



# Kompaktes Banner

COMPACT_CONFIG = BannerConfig(

    size=BannerSize(height=40, min_width=250, content_padding_x=15, content_padding_y=8)

)
