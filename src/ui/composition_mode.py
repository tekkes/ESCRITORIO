"""
Composition Mode para Escritorio (Módulo puente de compatibilidad).
Re-exporta la implementación completa de src.ui.CompositionMode.
"""

from .CompositionMode import (
    CompositionMode,
    CompositionPaperSettings,
    PaperPosition,
    BottomControlBar,
    GoToItem
)

__all__ = [
    "CompositionMode",
    "CompositionPaperSettings",
    "PaperPosition",
    "BottomControlBar",
    "GoToItem"
]
