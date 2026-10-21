"""
Escritorio Compile Module
Motor multihilo de compilación editorial, asignación de Section Layouts,
resolución de Placeholders dinámicos y exportación multiformato (DOCX, PDF, EPUB, RTF, FDX, MD, HTML).
"""

from .placeholders import PlaceholderResolver
from .section_layouts import SectionLayoutEngine, SectionLayoutType
from .compile_engine import CompileEngine, CompileConfig
from .exporters import UnifiedExporter, ExportFormat

__all__ = [
    "PlaceholderResolver",
    "SectionLayoutEngine",
    "SectionLayoutType",
    "CompileEngine",
    "CompileConfig",
    "UnifiedExporter",
    "ExportFormat",
]
