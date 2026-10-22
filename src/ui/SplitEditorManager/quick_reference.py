"""
QuickReference para Escritorio
Gestión de Ventanas Flotantes de Referencia Rápida (Quick Reference / QR)
Permite abrir cualquier documento de texto o archivo de investigación (PDF, imagen, media, web)
en ventanas independientes multi-monitor con persistencia de geometría y sincronización de datos.
"""

from typing import Dict, Optional, Tuple, List, Any
import uuid
from pathlib import Path

from ...core.project import BinderItem, EscritorioProject
from ..EditorWidget.editor_widget import EditorWidget
from .editor_pane import PaneContentType


class QuickReferenceWindow:
    """Ventana flotante individual de Referencia Rápida."""

    def __init__(
        self,
        window_id: str,
        project: Optional[EscritorioProject] = None,
        item: Optional[BinderItem] = None,
        media_path: Optional[str] = None,
        viewer: Optional[Any] = None,
        geometry: Tuple[int, int, int, int] = (100, 100, 640, 500)
    ):
        self.window_id = window_id
        self.project = project
        self.item = item
        self.media_path = media_path
        self.geometry = geometry
        self.always_on_top: bool = False
        self.is_open: bool = True

        if item:
            self.content_type = PaneContentType.EDITOR
            self.editor = EditorWidget(project)
            self.editor.load_item(item)
            self.viewer = None
        elif media_path:
            self.content_type = PaneContentType.IMAGE  # O asignado externamente
            self.editor = None
            self.viewer = viewer
        else:
            self.content_type = PaneContentType.EDITOR
            self.editor = EditorWidget(project)
            self.viewer = None

    @property
    def title(self) -> str:
        if self.item:
            return f"QR: {self.item.title}"
        elif self.media_path:
            return f"QR: {Path(self.media_path).name}"
        return "Ventana de Referencia Rápida"

    def set_always_on_top(self, enable: bool):
        self.always_on_top = enable

    def set_geometry(self, x: int, y: int, width: int, height: int):
        self.geometry = (x, y, width, height)

    def save_changes(self):
        """Guarda los cambios si el documento de texto fue editado en la ventana QR."""
        if self.editor and self.editor.is_dirty:
            self.editor.save_current()
            if self.item:
                self.item.save_if_dirty()

    def close(self):
        self.save_changes()
        self.is_open = False


class QuickReferenceManager:
    """Administrador maestro de ventanas flotantes multi-monitor."""

    def __init__(self, project: Optional[EscritorioProject] = None):
        self.project = project
        self.windows: Dict[str, QuickReferenceWindow] = {}

    def set_project(self, project: EscritorioProject):
        self.close_all()
        self.project = project

    def open_document(
        self,
        item: BinderItem,
        geometry: Tuple[int, int, int, int] = (100, 100, 640, 500)
    ) -> QuickReferenceWindow:
        """Abre un documento de texto del Binder en una ventana flotante o enfoca la existente."""
        for win in self.windows.values():
            if win.item and win.item.uuid == item.uuid and win.is_open:
                win.geometry = geometry
                return win

        win_id = f"qr_{uuid.uuid4().hex[:8]}"
        qr_win = QuickReferenceWindow(
            window_id=win_id,
            project=self.project,
            item=item,
            geometry=geometry
        )
        self.windows[win_id] = qr_win
        return qr_win

    def open_media(
        self,
        media_path: str,
        viewer: Any,
        content_type: PaneContentType,
        geometry: Tuple[int, int, int, int] = (150, 150, 700, 550)
    ) -> QuickReferenceWindow:
        """Abre un archivo de investigación con su visor dedicado en ventana flotante."""
        for win in self.windows.values():
            if win.media_path and win.media_path == media_path and win.is_open:
                return win

        win_id = f"qr_media_{uuid.uuid4().hex[:8]}"
        qr_win = QuickReferenceWindow(
            window_id=win_id,
            project=self.project,
            media_path=media_path,
            viewer=viewer,
            geometry=geometry
        )
        qr_win.content_type = content_type
        self.windows[win_id] = qr_win
        return qr_win

    def get_window(self, window_id: str) -> Optional[QuickReferenceWindow]:
        return self.windows.get(window_id)

    def close_window(self, window_id: str):
        if window_id in self.windows:
            win = self.windows[window_id]
            win.close()
            del self.windows[window_id]

    def close_all(self):
        for win in list(self.windows.values()):
            win.close()
        self.windows.clear()

    def get_open_windows(self) -> List[QuickReferenceWindow]:
        return [w for w in self.windows.values() if w.is_open]
