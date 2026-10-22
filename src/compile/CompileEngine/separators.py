"""
Gestor de Separadores (Separators) para Escritorio / Scrivener 3.
Reglas configurables de separación entre secciones del manuscrito compilado:
- Salto de página (Page Break)
- Línea en blanco (Empty Line)
- Retorno simple (Single Return)
- Símbolo personalizado centrado (ej. * * *, #, ~ ~ ~)
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class SeparatorType(Enum):
    PAGE_BREAK = "page_break"
    EMPTY_LINE = "empty_line"
    SINGLE_RETURN = "single_return"
    CUSTOM_SYMBOL = "custom_symbol"
    NONE = "none"


@dataclass
class SectionSeparators:
    """Configuración de separadores para un diseño de sección o tipo de documento."""
    before_section: SeparatorType = SeparatorType.EMPTY_LINE
    custom_before: str = ""
    between_sections: SeparatorType = SeparatorType.CUSTOM_SYMBOL
    custom_between: str = "* * *"
    after_section: SeparatorType = SeparatorType.SINGLE_RETURN
    custom_after: str = ""


class SeparatorsManager:
    """Genera las cadenas tipográficas exactas para cada tipo de separador editorial."""

    PAGE_BREAK_TEXT = "\n\n\\pagebreak\n\n"
    EMPTY_LINE_TEXT = "\n\n"
    SINGLE_RETURN_TEXT = "\n"

    @classmethod
    def get_separator_string(cls, sep_type: SeparatorType, custom_symbol: str = "* * *") -> str:
        """Devuelve la representación en texto del separador."""
        if sep_type == SeparatorType.PAGE_BREAK:
            return cls.PAGE_BREAK_TEXT
        elif sep_type == SeparatorType.EMPTY_LINE:
            return cls.EMPTY_LINE_TEXT
        elif sep_type == SeparatorType.SINGLE_RETURN:
            return cls.SINGLE_RETURN_TEXT
        elif sep_type == SeparatorType.CUSTOM_SYMBOL:
            symbol = custom_symbol.strip() or "* * *"
            return f"\n\n{symbol}\n\n"
        elif sep_type == SeparatorType.NONE:
            return ""
        return cls.EMPTY_LINE_TEXT

    @classmethod
    def format_boundary(
        cls,
        prev_type: Optional[str],
        current_type: str,
        current_separators: SectionSeparators,
        is_first_section: bool = False
    ) -> str:
        """
        Determina la separación exacta entre la sección previa y la actual.
        - Si es la primera sección, aplica `before_section`.
        - Si ambas secciones tienen el mismo tipo, aplica `between_sections`.
        - Si cambian de tipo, aplica `before_section` de la nueva sección.
        """
        if is_first_section:
            return cls.get_separator_string(
                current_separators.before_section,
                current_separators.custom_before
            )

        if prev_type == current_type:
            return cls.get_separator_string(
                current_separators.between_sections,
                current_separators.custom_between
            )
        else:
            return cls.get_separator_string(
                current_separators.before_section,
                current_separators.custom_before
            )
