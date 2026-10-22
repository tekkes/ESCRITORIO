"""
Paquete CompositionMode de Escritorio.
Modo de redacción inmersiva a pantalla completa libre de distracciones (F11).
"""

from .paper_settings import CompositionPaperSettings, PaperPosition
from .bottom_control_bar import BottomControlBar, GoToItem
from .composition_controller import CompositionMode

__all__ = [
    "CompositionPaperSettings",
    "PaperPosition",
    "BottomControlBar",
    "GoToItem",
    "CompositionMode"
]
