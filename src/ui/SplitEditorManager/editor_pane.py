"""
EditorPane para Escritorio
Representación individual de un panel dentro del SplitEditorManager.
Gestiona:
- Editor individual de texto RTF / Scrivenings
- O Visor de Investigación (PDF, imagen, reproductor de transcripción, web)
- Bandera de Bloqueo en el Lugar (Lock in Place / Ctrl+Shift+L)
- Opción 'Navegación afecta al otro editor'
"""

from typing import Optional, Any
from enum import Enum
from pathlib import Path

from ...core.project import BinderItem, EscritorioProject
from ..EditorWidget.editor_widget import EditorWidget


class PaneContentType(Enum):
    EDITOR = "editor"
    SCRIVENINGS = "scrivenings"
    PDF = "pdf"
    IMAGE = "image"
    MEDIA = "media"
    WEB = "web"


class EditorPane:
    """Panel individual dentro del contenedor de vista dividida."""

    def __init__(self, pane_id: str, project: Optional[EscritorioProject] = None):
        self.pane_id = pane_id
        self.project = project
        self.editor: EditorWidget = EditorWidget(project)

        # Estado de bloqueo (Lock in place / Ctrl+Shift+L)
        self.is_locked: bool = False

        # Modo navegación cruzada
        self.navigate_affects_other: bool = False

        # Tipo de contenido actual
        self.content_type: PaneContentType = PaneContentType.EDITOR
        self.research_viewer: Optional[Any] = None
        self.active_media_path: Optional[str] = None

    @property
    def current_item(self) -> Optional[BinderItem]:
        return self.editor.current_item

    @property
    def title(self) -> str:
        if self.content_type == PaneContentType.EDITOR:
            return self.editor.current_item.title if self.editor.current_item else "Sin documento"
        elif self.active_media_path:
            return Path(self.active_media_path).name
        return "Panel de Investigación"

    def toggle_lock(self) -> bool:
        """Alterna el bloqueo del panel frente a selecciones del Binder (Ctrl+Shift+L)."""
        self.is_locked = not self.is_locked
        return self.is_locked

    def set_lock(self, locked: bool):
        self.is_locked = locked

    def toggle_navigate_affects_other(self) -> bool:
        """Alterna si la navegación en este panel abre en el otro editor."""
        self.navigate_affects_other = not self.navigate_affects_other
        return self.navigate_affects_other

    def load_item(self, item: BinderItem):
        """Carga un documento de texto en el editor de este panel."""
        self.content_type = PaneContentType.EDITOR
        self.research_viewer = None
        self.active_media_path = None
        self.editor.load_item(item)

    def load_research_media(self, media_path: str, viewer_instance: Any, content_type: PaneContentType):
        """Carga un archivo de investigación con su visor dedicado."""
        self.content_type = content_type
        self.active_media_path = media_path
        self.research_viewer = viewer_instance

    def save_if_dirty(self):
        """Guarda cambios si el editor de este panel tiene modificaciones."""
        if self.content_type == PaneContentType.EDITOR:
            self.editor.save_current()

    def get_header_state(self) -> dict:
        """Información para renderizar la cabecera compacta del panel."""
        return {
            "pane_id": self.pane_id,
            "title": self.title,
            "is_locked": self.is_locked,
            "navigate_affects_other": self.navigate_affects_other,
            "content_type": self.content_type.value,
            "has_media": self.active_media_path is not None,
            "lock_icon": "🔒" if self.is_locked else "🔓",
            "is_dirty": self.editor.is_dirty if self.content_type == PaneContentType.EDITOR else False
        }
