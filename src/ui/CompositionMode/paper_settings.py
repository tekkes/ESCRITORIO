"""
Paper Settings para el Modo Composición libre de distracciones de Escritorio.
Define las propiedades de la hoja central de papel, posición, fundido de fondo y zoom tipográfico.
"""

from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass


class PaperPosition(Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


@dataclass
class CompositionPaperSettings:
    """Configuración geométrica y estética de la hoja de composición."""
    # Ancho del papel en porcentaje del ancho de pantalla (30% a 100%)
    paper_width_percent: int = 65

    # Posición horizontal del papel en la pantalla completa
    position: PaperPosition = PaperPosition.CENTER

    # Nivel de zoom de texto tipográfico (50% a 250%)
    text_zoom_percent: int = 120

    # Opacidad del fundido de fondo (Background Fade): 0.0 (transparente) a 1.0 (negro/sólido absoluto)
    background_fade: float = 0.85

    # Ruta a imagen o textura de fondo personalizada (opcional)
    background_image_path: Optional[str] = None

    # Modo Typewriter Scrolling (mantiene la línea activa centrada verticalmente)
    typewriter_scrolling: bool = True

    # Colores temáticos del papel y tipografía
    paper_bg_color: str = "#18181B"      # Zinc oscuro profundo
    text_fg_color: str = "#F4F4F5"       # Blanco cálido tipográfico
    backdrop_color: str = "#09090B"      # Fondo exterior inmersivo
    caret_color: str = "#3B82F6"         # Azul cursor de alta visibilidad

    def set_paper_width(self, width_percent: int) -> int:
        self.paper_width_percent = max(30, min(100, int(width_percent)))
        return self.paper_width_percent

    def set_position(self, pos: PaperPosition) -> PaperPosition:
        self.position = pos
        return self.position

    def set_text_zoom(self, zoom_percent: int) -> int:
        self.text_zoom_percent = max(50, min(250, int(zoom_percent)))
        return self.text_zoom_percent

    def set_background_fade(self, fade: float) -> float:
        self.background_fade = max(0.0, min(1.0, float(fade)))
        return self.background_fade

    def set_background_image(self, path: Optional[str]) -> Optional[str]:
        self.background_image_path = path
        return self.background_image_path

    def to_dict(self) -> Dict[str, Any]:
        return {
            "paper_width_percent": self.paper_width_percent,
            "position": self.position.value,
            "text_zoom_percent": self.text_zoom_percent,
            "background_fade": round(self.background_fade, 2),
            "background_image_path": self.background_image_path,
            "typewriter_scrolling": self.typewriter_scrolling,
            "paper_bg_color": self.paper_bg_color,
            "text_fg_color": self.text_fg_color,
            "backdrop_color": self.backdrop_color,
            "caret_color": self.caret_color
        }
