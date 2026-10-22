"""
FormatToolbar para Escritorio EditorWidget
Barra de formato compacta y control de estado tipográfico:
- Familia tipográfica, tamaño en puntos
- Negrita, cursiva, subrayado, tachado, superíndice, subíndice
- Color de texto y paleta de resaltadores multicolor
- Alineación (izquierda, centrada, derecha, justificada)
- Interlineado (1.0, 1.15, 1.5, 2.0, personalizado) y espaciado de párrafos
- Inserción de listas (viñetas, numeradas), tablas, imágenes y Scrivener Links.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class TextFormatState:
    font_family: str = "Segoe UI"
    font_size_pt: float = 12.0
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    superscript: bool = False
    subscript: bool = False
    text_color: str = "#000000"
    highlight_color: str = ""       # Hex ej. #FFFF00 o vacío para sin resaltado
    alignment: str = "left"          # "left", "center", "right", "justify"
    line_spacing: float = 1.15       # 1.0, 1.15, 1.5, 2.0
    space_before_pt: float = 0.0
    space_after_pt: float = 6.0
    active_style_id: str = "style-no-style"
    list_type: str = "none"          # "none", "bullet", "numbered"

    HIGHLIGHT_PALETTE: List[Dict[str, str]] = field(default_factory=lambda: [
        {"name": "Ninguno", "hex": ""},
        {"name": "Amarillo", "hex": "#FFFF00"},
        {"name": "Verde", "hex": "#00FF00"},
        {"name": "Cian", "hex": "#00FFFF"},
        {"name": "Magenta", "hex": "#FF00FF"},
        {"name": "Naranja", "hex": "#FFA500"},
    ])

    STANDARD_FONTS: List[str] = field(default_factory=lambda: [
        "Segoe UI", "Georgia", "Times New Roman", "Palatino Linotype",
        "Garamond", "Calibri", "Arial", "Consolas", "Courier Prime"
    ])

    STANDARD_SIZES: List[float] = field(default_factory=lambda: [
        9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 16.0, 18.0, 20.0, 24.0, 28.0, 32.0, 36.0
    ])

    LINE_SPACINGS: List[float] = field(default_factory=lambda: [
        1.0, 1.15, 1.5, 2.0
    ])


class FormatToolbar:
    """Controlador del estado de la barra de formato compacta."""

    def __init__(self, initial_state: Optional[TextFormatState] = None):
        self.state = initial_state or TextFormatState()

    def set_font_family(self, family: str):
        self.state.font_family = family

    def set_font_size(self, size_pt: float):
        self.state.font_size_pt = max(6.0, min(size_pt, 120.0))

    def toggle_bold(self) -> bool:
        self.state.bold = not self.state.bold
        return self.state.bold

    def toggle_italic(self) -> bool:
        self.state.italic = not self.state.italic
        return self.state.italic

    def toggle_underline(self) -> bool:
        self.state.underline = not self.state.underline
        return self.state.underline

    def toggle_strikethrough(self) -> bool:
        self.state.strikethrough = not self.state.strikethrough
        return self.state.strikethrough

    def toggle_superscript(self) -> bool:
        self.state.superscript = not self.state.superscript
        if self.state.superscript:
            self.state.subscript = False
        return self.state.superscript

    def toggle_subscript(self) -> bool:
        self.state.subscript = not self.state.subscript
        if self.state.subscript:
            self.state.superscript = False
        return self.state.subscript

    def set_text_color(self, hex_color: str):
        self.state.text_color = hex_color

    def set_highlight_color(self, hex_color: str):
        self.state.highlight_color = hex_color

    def set_alignment(self, align: str):
        if align in ("left", "center", "right", "justify"):
            self.state.alignment = align

    def set_line_spacing(self, spacing: float):
        self.state.line_spacing = max(0.5, min(spacing, 5.0))

    def set_paragraph_spacing(self, before_pt: float, after_pt: float):
        self.state.space_before_pt = max(0.0, before_pt)
        self.state.space_after_pt = max(0.0, after_pt)

    def set_list_type(self, list_type: str):
        if list_type in ("none", "bullet", "numbered"):
            self.state.list_type = list_type

    def set_active_style(self, style_id: str):
        self.state.active_style_id = style_id

    def get_render_data(self) -> Dict[str, Any]:
        """Devuelve los parámetros para renderizado de la barra de formato en la interfaz."""
        return {
            "font_family": self.state.font_family,
            "font_size_pt": self.state.font_size_pt,
            "bold": self.state.bold,
            "italic": self.state.italic,
            "underline": self.state.underline,
            "strikethrough": self.state.strikethrough,
            "superscript": self.state.superscript,
            "subscript": self.state.subscript,
            "text_color": self.state.text_color,
            "highlight_color": self.state.highlight_color,
            "alignment": self.state.alignment,
            "line_spacing": self.state.line_spacing,
            "space_before_pt": self.state.space_before_pt,
            "space_after_pt": self.state.space_after_pt,
            "active_style_id": self.state.active_style_id,
            "list_type": self.state.list_type,
            "fonts": list(self.state.STANDARD_FONTS),
            "sizes": list(self.state.STANDARD_SIZES),
            "line_spacings": list(self.state.LINE_SPACINGS),
            "highlighters": list(self.state.HIGHLIGHT_PALETTE)
        }
