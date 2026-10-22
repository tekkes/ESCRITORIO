"""
Scrivenings Divider para Escritorio
Estilos de separador configurables entre secciones de un documento compuesto:
- Línea horizontal sutil (Subtle Line)
- Esquinas recortadas (Corner Cuts / Scrivener 3 style)
- Salto de página (Page Break)
"""

from enum import Enum
from typing import Dict, Any


class DividerStyle(Enum):
    SUBTLE_LINE = "subtle_line"
    CORNER_CUTS = "corner_cuts"
    PAGE_BREAK = "page_break"


class ScriveningsDivider:
    """Generador y formateador de separadores de sección para Scrivenings."""

    SUBTLE_LINE_TEXT = "\n" + ("─" * 60) + "\n"
    CORNER_CUTS_TEXT = "\n" + ("─── ✂ ─── " * 5) + "\n"
    PAGE_BREAK_TEXT = "\n\f\n"  # Form Feed estándar para salto de página

    @staticmethod
    def get_divider_text(style: DividerStyle) -> str:
        if style == DividerStyle.SUBTLE_LINE:
            return ScriveningsDivider.SUBTLE_LINE_TEXT
        elif style == DividerStyle.CORNER_CUTS:
            return ScriveningsDivider.CORNER_CUTS_TEXT
        elif style == DividerStyle.PAGE_BREAK:
            return ScriveningsDivider.PAGE_BREAK_TEXT
        return ScriveningsDivider.SUBTLE_LINE_TEXT

    @staticmethod
    def format_section_header(title: str, section_number: int = 1, show_number: bool = True) -> str:
        """Genera el texto visible del encabezado de sección."""
        if show_number:
            return f"\n### [{section_number}] {title} ###\n\n"
        return f"\n### {title} ###\n\n"
