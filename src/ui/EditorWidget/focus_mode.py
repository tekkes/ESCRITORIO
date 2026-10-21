"""
FocusModeEngine para Escritorio
Gestión ergonómica del editor:
- Modo Foco (Focus Mode): Atenúa el resto del texto resaltando Línea, Oración o Párrafo actual.
- Desplazamiento de Máquina de Escribir (Typewriter Scrolling / Ctrl+Alt+T):
  Mantiene fija y centrada verticalmente la línea activa al escribir.
"""

from enum import Enum
from typing import Tuple, Optional, Dict, Any
import re


class FocusScope(str, Enum):
    OFF = "Off"
    LINE = "Line"
    SENTENCE = "Sentence"
    PARAGRAPH = "Paragraph"


class FocusModeEngine:
    """Controlador del modo foco y desplazamiento de máquina de escribir."""

    def __init__(self):
        self.scope: FocusScope = FocusScope.OFF
        self.typewriter_scrolling: bool = False
        self.typewriter_anchor_ratio: float = 0.5  # 50% centro de la pantalla

    def toggle_typewriter_scrolling(self) -> bool:
        """Alterna el desplazamiento de máquina de escribir (Ctrl+Alt+T)."""
        self.typewriter_scrolling = not self.typewriter_scrolling
        return self.typewriter_scrolling

    def set_scope(self, scope: FocusScope):
        self.scope = scope

    def get_focused_span(self, text: str, cursor_pos: int) -> Tuple[int, int]:
        """
        Calcula el intervalo (inicio, fin) del texto que debe mantenerse al 100% de opacidad
        según el ámbito de foco activo (Línea, Oración o Párrafo).
        """
        if self.scope == FocusScope.OFF or not text:
            return (0, len(text))

        pos = max(0, min(cursor_pos, len(text)))

        if self.scope == FocusScope.LINE:
            # Buscar inicios y fines de línea (\n)
            start = text.rfind("\n", 0, pos)
            start = 0 if start == -1 else start + 1
            end = text.find("\n", pos)
            end = len(text) if end == -1 else end
            return (start, end)

        elif self.scope == FocusScope.SENTENCE:
            # Delimitadores de oración: . ! ? seguidos de espacio o salto de línea
            sentence_delims = re.compile(r"[.!?]+(?:\s+|$)")
            # Buscar oraciones en el texto
            prev_end = 0
            for m in sentence_delims.finditer(text):
                m_end = m.end()
                if pos <= m_end:
                    return (prev_end, m_end)
                prev_end = m_end
            return (prev_end, len(text))

        elif self.scope == FocusScope.PARAGRAPH:
            # Delimitador de párrafo: saltos dobles o simples de línea
            start = text.rfind("\n\n", 0, pos)
            if start == -1:
                start = text.rfind("\n", 0, pos)
                start = 0 if start == -1 else start + 1
            else:
                start += 2

            end = text.find("\n\n", pos)
            if end == -1:
                end = text.find("\n", pos)
                end = len(text) if end == -1 else end
            return (start, end)

        return (0, len(text))

    def calculate_typewriter_scroll_offset(
        self,
        cursor_line_index: int,
        line_height_px: float,
        viewport_height_px: float
    ) -> float:
        """
        Calcula el desplazamiento vertical (scrollTop) para que la línea del cursor
        quede anclada exactamente a la altura configurada (50% por defecto).
        """
        if not self.typewriter_scrolling:
            return 0.0

        cursor_y = cursor_line_index * line_height_px
        target_center_y = viewport_height_px * self.typewriter_anchor_ratio
        scroll_offset = max(0.0, cursor_y - target_center_y + (line_height_px / 2.0))
        return scroll_offset

    def get_state(self) -> Dict[str, Any]:
        return {
            "scope": self.scope.value,
            "typewriter_scrolling": self.typewriter_scrolling,
            "anchor_ratio": self.typewriter_anchor_ratio
        }
