"""
Escritorio Compile Module
Motor multihilo de compilación editorial, asignación de Section Layouts,
resolución de Placeholders dinámicos y exportación multiformato (DOCX, PDF, EPUB, RTF, FDX, MD, HTML).
"""

from .placeholders import PlaceholderResolver, int_to_roman, int_to_words_es
from .section_layouts import SectionLayoutEngine, SectionLayoutType
from .compile_engine import (
    CompileEngine,
    CompileConfig,
    CompileFormat,
    SectionLayout,
    BookMetadata,
    CompileFilterConfig,
    CompileReplacementRule,
    create_builtin_formats
)
from .exporters import UnifiedExporter, ExportFormat
from .CompileEngine.separators import SeparatorType, SectionSeparators, SeparatorsManager
from .CompileEngine.format_designer import CompileFormatDesigner

__all__ = [
    "PlaceholderResolver",
    "SectionLayoutEngine",
    "SectionLayoutType",
    "CompileEngine",
    "CompileConfig",
    "CompileFormat",
    "SectionLayout",
    "BookMetadata",
    "CompileFilterConfig",
    "CompileReplacementRule",
    "UnifiedExporter",
    "ExportFormat",
    "SeparatorType",
    "SectionSeparators",
    "SeparatorsManager",
    "CompileFormatDesigner",
    "create_builtin_formats",
    "int_to_roman",
    "int_to_words_es",
]
