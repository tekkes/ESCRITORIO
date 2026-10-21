"""
Split Container para Escritorio
Gestión de vistas divididas simultáneas (horizontal y vertical) permitiendo
comparar textos, visualizar corcho y editor a la par, o redactar dos escenas en paralelo.
"""

from enum import Enum
from typing import Optional
from .editor_rtf import RTFEditorView
from ..core.project import BinderItem

class SplitOrientation(Enum):
    NONE = 0
    HORIZONTAL = 1
    VERTICAL = 2

class SplitContainer:
    """Controlador de división de la pantalla de edición."""

    def __init__(self):
        self.orientation = SplitOrientation.NONE
        self.primary_editor = RTFEditorView()
        self.secondary_editor = RTFEditorView()
        self.active_pane: str = "primary"  # "primary" o "secondary"

    def split_horizontal(self):
        self.orientation = SplitOrientation.HORIZONTAL

    def split_vertical(self):
        self.orientation = SplitOrientation.VERTICAL

    def close_split(self):
        self.orientation = SplitOrientation.NONE
        self.active_pane = "primary"

    def set_active_pane(self, pane: str):
        if pane in ("primary", "secondary"):
            self.active_pane = pane

    def get_active_editor(self) -> RTFEditorView:
        return self.primary_editor if self.active_pane == "primary" else self.secondary_editor

    def load_item_to_active(self, item: BinderItem):
        self.get_active_editor().load_item(item)
