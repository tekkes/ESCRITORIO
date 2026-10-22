"""
Compile Engine para Escritorio
Orquestador de compilación editorial: recorre el árbol de borrador, filtra nodos excluidos,
resuelve marcadores y aplica la plantilla de maquetación en una sola pasada eficiente.
"""

from .CompileEngine.engine import (
    CompileEngine,
    CompileConfig
)
from .CompileEngine.models import (
    CompileFormat,
    SectionLayout,
    BookMetadata,
    CompileFilterConfig,
    CompileReplacementRule,
    create_builtin_formats
)

__all__ = [
    "CompileEngine",
    "CompileConfig",
    "CompileFormat",
    "SectionLayout",
    "BookMetadata",
    "CompileFilterConfig",
    "CompileReplacementRule",
    "create_builtin_formats"
]
