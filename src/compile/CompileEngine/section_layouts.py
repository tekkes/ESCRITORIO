"""
Section Layout Engine para Escritorio / Scrivener 3.
Motor de renderizado de diseños de sección (Section Layouts):
- Formatea títulos con prefijos/sufijos y mayúsculas.
- Concatena sinopsis, notas y cuerpo del documento según la configuración del diseño.
- Proporciona retrocompatibilidad completa con la API previa de SectionLayoutEngine.
"""

from enum import Enum
from typing import Optional, Dict, Any
from .models import SectionLayout
from .separators import SectionSeparators, SeparatorType, SeparatorsManager


class SectionLayoutType(Enum):
    """Tipos de maquetación básicos para retrocompatibilidad."""
    TITLE_ONLY = "title_only"
    TITLE_AND_TEXT = "title_and_text"
    TEXT_ONLY = "text_only"
    NUMBERED_CHAPTER = "numbered_chapter"
    SCENE_SEPARATOR = "scene_separator"


class SectionLayoutEngine:
    """Motor de maquetación estructural de secciones de manuscrito."""

    @classmethod
    def format_with_layout(
        cls,
        layout: SectionLayout,
        title: str,
        body: str,
        synopsis: str = "",
        notes: str = "",
        chapter_index: int = 1
    ) -> str:
        """
        Formatea una sección utilizando una instancia completa de SectionLayout de Scrivener 3.
        """
        parts = []

        # 1. Título
        if layout.include_title and title.strip():
            formatted_title = title.strip()
            if layout.title_uppercase:
                formatted_title = formatted_title.upper()

            prefix = layout.title_prefix
            suffix = layout.title_suffix

            title_block = f"{prefix}{formatted_title}{suffix}"
            if layout.title_centered:
                title_block = f"<center>{title_block.strip()}</center>\n\n"
            parts.append(title_block)

        # 2. Sinopsis opcional
        if layout.include_synopsis and synopsis.strip():
            parts.append(f"> **Sinopsis:** {synopsis.strip()}\n\n")

        # 3. Notas del inspector opcionales
        if layout.include_notes and notes.strip():
            parts.append(f"<!-- Notas: {notes.strip()} -->\n\n")

        # 4. Cuerpo de la sección
        if layout.include_body and body.strip():
            body_clean = body.strip()
            parts.append(f"{body_clean}\n")

        return "".join(parts)

    @classmethod
    def format_section(
        cls,
        layout_type_or_layout: Any,
        title: str,
        body_text: str,
        chapter_index: int = 1,
        scene_separator: str = "* * *",
        synopsis: str = "",
        notes: str = ""
    ) -> str:
        """
        Método unificado compatible con SectionLayoutType enum clásico y SectionLayout dataclass.
        """
        if isinstance(layout_type_or_layout, SectionLayout):
            return cls.format_with_layout(
                layout=layout_type_or_layout,
                title=title,
                body=body_text,
                synopsis=synopsis,
                notes=notes,
                chapter_index=chapter_index
            )

        # Modo retrocompatible con SectionLayoutType enum
        lt = layout_type_or_layout
        if lt == SectionLayoutType.TITLE_ONLY:
            return f"\n\n# {title}\n\n"

        elif lt == SectionLayoutType.NUMBERED_CHAPTER:
            return f"\n\n# Capítulo {chapter_index}: {title}\n\n{body_text}\n"

        elif lt == SectionLayoutType.TITLE_AND_TEXT:
            return f"\n\n## {title}\n\n{body_text}\n"

        elif lt == SectionLayoutType.TEXT_ONLY:
            return f"\n{body_text}\n"

        elif lt == SectionLayoutType.SCENE_SEPARATOR:
            return f"\n\n{scene_separator}\n\n{body_text}\n"

        return f"\n{body_text}\n"
