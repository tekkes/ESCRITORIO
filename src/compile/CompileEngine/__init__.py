"""
Módulo CompileEngine para Escritorio / Scrivener 3.
Motor completo de compilación editorial, asignación de Section Layouts,
evaluación de Placeholders, Separadores y Diseñador de Formatos.
"""

from .models import (
    PageSize,
    PageOrientation,
    PageMargins,
    SectionLayout,
    BookMetadata,
    CompileReplacementRule,
    CompileFilterConfig,
    CompileFormat,
    create_builtin_formats
)
from .separators import (
    SeparatorType,
    SectionSeparators,
    SeparatorsManager
)
from .placeholders import (
    PlaceholderResolver,
    int_to_roman,
    int_to_words_es
)
from .section_layouts import (
    SectionLayoutType,
    SectionLayoutEngine
)
from .format_designer import CompileFormatDesigner
from .engine import (
    CompileEngine,
    CompileConfig
)
from ..exporters import (
    UnifiedExporter,
    ExportFormat
)

__all__ = [
    "CompileEngine",
    "CompileConfig",
    "UnifiedExporter",
    "ExportFormat",
    "CompileFormat",
    "SectionLayout",
    "SectionLayoutEngine",
    "SectionLayoutType",
    "PlaceholderResolver",
    "SeparatorsManager",
    "SectionSeparators",
    "SeparatorType",
    "CompileFormatDesigner",
    "BookMetadata",
    "CompileFilterConfig",
    "CompileReplacementRule",
    "PageSize",
    "PageOrientation",
    "PageMargins",
    "create_builtin_formats",
    "int_to_roman",
    "int_to_words_es",
]
