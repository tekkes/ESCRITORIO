"""
Section Layout Engine para Escritorio
Asignación y transformación de tipos de sección (Section Types) a diseños de maquetación
(Section Layouts), determinando títulos, saltos de página, numeraciones y prefijos.
"""

from .CompileEngine.section_layouts import (
    SectionLayoutType,
    SectionLayoutEngine
)

__all__ = ["SectionLayoutType", "SectionLayoutEngine"]
