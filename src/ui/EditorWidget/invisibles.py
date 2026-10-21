"""
InvisiblesEngine para Escritorio
Gestión de caracteres invisibles / no imprimibles en el editor:
- Marcas de párrafo (¶ / Pilcrow)
- Espacios ordinarios (· / Middle dot) y no rompibles (°)
- Tabulaciones (→ / Flecha derecha)
- Saltos de página y división de secciones.
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass


@dataclass
class InvisibleToken:
    char_pos: int
    token_type: str  # "space", "tab", "paragraph", "page_break"
    display_symbol: str


class InvisiblesEngine:
    """Motor de visualización de caracteres invisibles."""

    PILCROW = "¶"
    MIDDLE_DOT = "·"
    TAB_ARROW = "→"
    NBSP_SYMBOL = "°"
    PAGE_BREAK_LINE = "⸺⸺⸺ ✂ Salto de Página ⸺⸺⸺"

    def __init__(self, is_visible: bool = False):
        self.is_visible = is_visible

    def toggle(self) -> bool:
        """Alterna la visualización de invisibles."""
        self.is_visible = not self.is_visible
        return self.is_visible

    def render_text_with_invisibles(self, text: str) -> str:
        """
        Sustituye los caracteres en blanco por sus símbolos gráficos correspondientes
        para renderizado en modo invisibles activo.
        """
        if not self.is_visible or not text:
            return text

        result = []
        for char in text:
            if char == " ":
                result.append(self.MIDDLE_DOT)
            elif char == "\t":
                result.append(self.TAB_ARROW + " ")
            elif char == "\n":
                result.append(self.PILCROW + "\n")
            elif char == "\u00A0":  # Espacio indivisible
                result.append(self.NBSP_SYMBOL)
            else:
                result.append(char)

        return "".join(result)

    def extract_invisible_tokens(self, text: str) -> List[InvisibleToken]:
        """Extrae la lista posicional de símbolos no imprimibles para el motor de dibujo GDI / UI."""
        tokens: List[InvisibleToken] = []
        if not text:
            return tokens

        for idx, char in enumerate(text):
            if char == " ":
                tokens.append(InvisibleToken(idx, "space", self.MIDDLE_DOT))
            elif char == "\t":
                tokens.append(InvisibleToken(idx, "tab", self.TAB_ARROW))
            elif char == "\n":
                tokens.append(InvisibleToken(idx, "paragraph", self.PILCROW))
            elif char == "\u00A0":
                tokens.append(InvisibleToken(idx, "nbsp", self.NBSP_SYMBOL))

        return tokens
