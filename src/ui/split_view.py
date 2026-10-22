"""
Split Container para Escritorio
Gestión de vistas divididas simultáneas (horizontal, vertical y cuadrícula de 4 paneles)
con soporte de bloqueo de editor (Lock in Place / Ctrl+Shift+L),
navegación cruzada y ventanas flotantes Quick Reference.
"""

from enum import Enum
from typing import Optional, List
from .editor_rtf import RTFEditorView
from ..core.project import BinderItem, EscritorioProject
from .SplitEditorManager import SplitEditorManager, SplitLayoutMode, EditorPane


class SplitOrientation(Enum):
    NONE = 0
    HORIZONTAL = 1
    VERTICAL = 2
    GRID = 3


class SplitContainer:
    """Controlador de división de la pantalla de edición."""

    def __init__(self, project: Optional[EscritorioProject] = None):
        self.manager = SplitEditorManager(project)
        self.orientation = SplitOrientation.NONE

        # Retrocompatibilidad directa con primary_editor y secondary_editor
        self.primary_editor = self.manager.panes["pane_0"].editor
        self.secondary_editor = self.manager.panes["pane_1"].editor

    @property
    def active_pane(self) -> str:
        return "primary" if self.manager.active_pane_id == "pane_0" else "secondary"

    @active_pane.setter
    def active_pane(self, value: str):
        self.set_active_pane(value)

    def split_horizontal(self):
        """Divide horizontalmente (Ctrl+\")."""
        self.orientation = SplitOrientation.HORIZONTAL
        self.manager.split_horizontal()

    def split_vertical(self):
        """Divide verticalmente (Ctrl+')."""
        self.orientation = SplitOrientation.VERTICAL
        self.manager.split_vertical()

    def split_grid(self):
        """Divide en cuadrícula de hasta 4 paneles."""
        self.orientation = SplitOrientation.GRID
        self.manager.split_grid()

    def close_split(self):
        self.orientation = SplitOrientation.NONE
        self.manager.close_split()

    def set_active_pane(self, pane: str):
        if pane in ("primary", "pane_0"):
            self.manager.set_active_pane("pane_0")
        elif pane in ("secondary", "pane_1"):
            self.manager.set_active_pane("pane_1")
        elif pane in self.manager.panes:
            self.manager.set_active_pane(pane)

    def get_active_editor(self) -> RTFEditorView:
        return self.manager.active_pane.editor

    def load_item_to_active(self, item: BinderItem):
        return self.manager.load_item_from_binder(item)

    # =========================================================================
    # Nuevas Capacidades: Bloqueo y Navegación Cruzada
    # =========================================================================

    def toggle_lock_active_pane(self) -> bool:
        """Alterna el bloqueo del panel activo (Ctrl+Shift+L)."""
        return self.manager.toggle_lock_active_pane()

    def is_active_locked(self) -> bool:
        return self.manager.is_active_locked()

    def toggle_navigate_affects_other(self) -> bool:
        """Alterna si la navegación en el panel activo abre en el otro editor."""
        return self.manager.toggle_navigate_affects_other()
