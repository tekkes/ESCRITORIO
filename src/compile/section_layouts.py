"""
Section Layout Engine para Escritorio
Asignación y transformación de tipos de sección (Section Types) a diseños de maquetación
(Section Layouts), determinando títulos, saltos de página, numeraciones y prefijos.
"""

from enum import Enum
from typing import Dict, Any, Optional

class SectionLayoutType(Enum):
    TITLE_ONLY = "title_only"
    TITLE_AND_TEXT = "title_and_text"
    TEXT_ONLY = "text_only"
    NUMBERED_CHAPTER = "numbered_chapter"
    SCENE_SEPARATOR = "scene_separator"

class SectionLayoutEngine:
    """Aplica formato de maquetación estructural a cada sección compilada."""

    @staticmethod
    def format_section(
        layout_type: SectionLayoutType,
        title: str,
        body_text: str,
        chapter_index: int = 1,
        scene_separator: str = "* * *"
    ) -> str:
        if layout_type == SectionLayoutType.TITLE_ONLY:
            return f"\n\n# {title}\n\n"

        elif layout_type == SectionLayoutType.NUMBERED_CHAPTER:
            return f"\n\n# Capítulo {chapter_index}: {title}\n\n{body_text}\n"

        elif layout_type == SectionLayoutType.TITLE_AND_TEXT:
            return f"\n\n## {title}\n\n{body_text}\n"

        elif layout_type == SectionLayoutType.TEXT_ONLY:
            return f"\n{body_text}\n"

        elif layout_type == SectionLayoutType.SCENE_SEPARATOR:
            return f"\n\n{scene_separator}\n\n{body_text}\n"

        return f"\n{body_text}\n"
