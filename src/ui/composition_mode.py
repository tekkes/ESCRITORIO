"""
Composition Mode para Escritorio
Modo inmersivo de escritura libre de distracciones a pantalla completa,
con atenuación de fondo regulable, ancho de papel tipográfico configurable y typewriter scrolling.
"""

from typing import Optional
from ..core.project import BinderItem
from .editor_rtf import RTFEditorView

class CompositionMode:
    """Controlador del modo inmersivo de redacción sin distracciones."""

    def __init__(self, editor: RTFEditorView):
        self.editor = editor
        self.is_active: bool = False
        self.backdrop_opacity: float = 0.85
        self.paper_width_percent: int = 65
        self.typewriter_scrolling: bool = True
        self.paper_color: str = "#18181c"
        self.text_color: str = "#e2e8f0"

    def enter(self):
        self.is_active = True

    def exit(self):
        self.is_active = False

    def toggle(self):
        self.is_active = not self.is_active

    def set_backdrop_opacity(self, opacity: float):
        self.backdrop_opacity = max(0.1, min(1.0, opacity))

    def set_paper_width(self, width_percent: int):
        self.paper_width_percent = max(30, min(100, width_percent))
