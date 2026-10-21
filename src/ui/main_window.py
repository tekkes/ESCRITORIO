"""
Main Window para Escritorio
Ventana principal y orquestador maestro de la interfaz: barra de menú, barra de herramientas,
alternancia entre vistas (Editor, Corcho, Esquematizador), paneles acoplables y barra de estado.
"""

from enum import Enum
from typing import Optional, Dict, Any

from ..core.project import EscritorioProject, BinderItem
from .binder import BinderView
from .editor_rtf import RTFEditorView
from .split_view import SplitContainer, SplitOrientation
from .corkboard import CorkboardView
from .outliner import OutlinerView
from .inspector import InspectorView
from .composition_mode import CompositionMode

class CentralViewMode(Enum):
    EDITOR = "editor"
    CORKBOARD = "corkboard"
    OUTLINER = "outliner"

class MainWindow:
    """Ventana principal de la aplicación Escritorio."""

    def __init__(self, project: Optional[EscritorioProject] = None):
        self.project = project
        self.binder = BinderView(project)
        self.split_container = SplitContainer()
        self.corkboard = CorkboardView()
        self.outliner = OutlinerView()
        self.inspector = InspectorView()
        self.composition_mode = CompositionMode(self.split_container.primary_editor)

        self.current_view_mode = CentralViewMode.EDITOR
        self.inspector_visible: bool = True
        self.binder_visible: bool = True

        # Conectar selección del binder con las vistas
        self.binder.on_selection_changed = self._on_binder_selection_changed

        if project:
            self.load_project(project)

    def load_project(self, project: EscritorioProject):
        self.project = project
        self.binder.set_project(project)
        if self.binder.selected_uuid:
            self._on_binder_selection_changed(self.binder.selected_uuid)

    def _on_binder_selection_changed(self, uuid: str):
        if not self.project:
            return
        item = self.project.get_item(uuid)
        if not item:
            return

        # Actualizar editor primario
        self.split_container.primary_editor.load_item(item)
        # Actualizar inspector
        self.inspector.set_item(item)

        # Si el elemento tiene hijos o es contenedor, actualizar corcho y esquematizador
        if item.children:
            self.corkboard.load_container(item)
            self.outliner.load_container(item)

    def set_view_mode(self, mode: CentralViewMode):
        self.current_view_mode = mode

    def toggle_binder(self):
        self.binder_visible = not self.binder_visible

    def toggle_inspector(self):
        self.inspector_visible = not self.inspector_visible

    def toggle_composition_mode(self):
        self.composition_mode.toggle()

    def get_status_info(self) -> Dict[str, Any]:
        """Obtiene la telemetría de la barra de estado inferior."""
        active_editor = self.split_container.get_active_editor()
        words = active_editor.get_word_count()
        chars = active_editor.get_character_count()
        title = active_editor.current_item.title if active_editor.current_item else "Ningún documento seleccionado"

        return {
            "document_title": title,
            "words": words,
            "characters": chars,
            "view_mode": self.current_view_mode.value,
            "is_dirty": active_editor.is_dirty,
            "project_title": self.project.project_data.get("title", "") if self.project else ""
        }
