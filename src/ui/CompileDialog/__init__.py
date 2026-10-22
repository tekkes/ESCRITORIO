"""
Módulo CompileDialog para Escritorio / Scrivener 3.
Diálogo de Compilación de 3 Columnas:
- Formatos con diseñador integrado
- Mapeo y previsualización de Section Layouts
- Contenidos (árbol, filtros, Front/Back Matter), Metadatos y Reemplazos
"""

from .compile_dialog import CompileDialog, RightPanelTab
from .formats_column import FormatsColumn, FormatCategory
from .section_layouts_column import SectionLayoutsColumn
from .contents_tab import ContentsTab
from .metadata_tab import MetadataTab
from .replacements_tab import ReplacementsTab

__all__ = [
    "CompileDialog",
    "RightPanelTab",
    "FormatsColumn",
    "FormatCategory",
    "SectionLayoutsColumn",
    "ContentsTab",
    "MetadataTab",
    "ReplacementsTab",
]
