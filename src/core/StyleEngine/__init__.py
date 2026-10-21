"""
StyleEngine Module
Gestión de estilos semánticos, presets predefinidos y persistencia en XML.
"""

from .style_model import StyleType, StyleDefinition
from .style_engine import StyleEngine

__all__ = [
    "StyleType",
    "StyleDefinition",
    "StyleEngine",
]
