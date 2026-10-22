"""
Pestaña 2 del Inspector: Marcadores (Bookmarks)
- Conmutador entre Marcadores del Documento y Marcadores del Proyecto
- Visor previsualizador integrado en la mitad inferior para leer y editar documentos
  de referencia in-situ sin cambiar el documento abierto en el editor principal
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from ...core.project import BinderItem, EscritorioProject
from ...core.rtf_engine import RTFEngine


class BookmarkScope(Enum):
    DOCUMENT = "document"
    PROJECT = "project"


@dataclass
class BookmarkItem:
    id: str
    target_uuid: str
    title: str
    item_type: str = "Text"
    scope: BookmarkScope = BookmarkScope.DOCUMENT
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "target_uuid": self.target_uuid,
            "title": self.title,
            "item_type": self.item_type,
            "scope": self.scope.value,
            "notes": self.notes
        }


class TabBookmarks:
    """Controlador de la Pestaña 2: Marcadores y Visor de Referencia Rápida."""

    def __init__(self, project: Optional[EscritorioProject] = None):
        self.project: Optional[EscritorioProject] = project
        self.active_item: Optional[BinderItem] = None
        self.current_scope: BookmarkScope = BookmarkScope.DOCUMENT

        # Marcadores del proyecto (globales)
        self.project_bookmarks: List[BookmarkItem] = []

        # Marcadores del documento activo: uuid_doc -> List[BookmarkItem]
        self.doc_bookmarks: Dict[str, List[BookmarkItem]] = {}

        # Marcador seleccionado actualmente en el visor integrado
        self.selected_bookmark_id: Optional[str] = None

    def set_item(self, item: Optional[BinderItem]):
        self.active_item = item
        if not self.project and item and getattr(item, "project", None):
            self.project = item.project
        self.selected_bookmark_id = None

    def set_scope(self, scope: BookmarkScope):
        self.current_scope = scope
        self.selected_bookmark_id = None

    def toggle_scope(self) -> BookmarkScope:
        if self.current_scope == BookmarkScope.DOCUMENT:
            self.current_scope = BookmarkScope.PROJECT
        else:
            self.current_scope = BookmarkScope.DOCUMENT
        return self.current_scope

    # =========================================================================
    # Gestión de Marcadores
    # =========================================================================

    def add_bookmark(self, target_uuid: str, title: Optional[str] = None, scope: Optional[BookmarkScope] = None) -> BookmarkItem:
        target_scope = scope or self.current_scope
        b_title = title

        if not b_title and self.project:
            it = self.project.get_item(target_uuid)
            if it:
                b_title = it.title

        b_title = b_title or f"Documento {target_uuid[:8]}"
        b_id = f"bm-{target_uuid}-{target_scope.value}"

        bm = BookmarkItem(
            id=b_id,
            target_uuid=target_uuid,
            title=b_title,
            scope=target_scope
        )

        if target_scope == BookmarkScope.PROJECT:
            # Evitar duplicados
            self.project_bookmarks = [b for b in self.project_bookmarks if b.target_uuid != target_uuid]
            self.project_bookmarks.append(bm)
        else:
            if self.active_item:
                doc_id = self.active_item.uuid
                if doc_id not in self.doc_bookmarks:
                    self.doc_bookmarks[doc_id] = []
                self.doc_bookmarks[doc_id] = [b for b in self.doc_bookmarks[doc_id] if b.target_uuid != target_uuid]
                self.doc_bookmarks[doc_id].append(bm)

        self.selected_bookmark_id = b_id
        return bm

    def remove_bookmark(self, bookmark_id: str):
        if self.current_scope == BookmarkScope.PROJECT:
            self.project_bookmarks = [b for b in self.project_bookmarks if b.id != bookmark_id]
        else:
            if self.active_item and self.active_item.uuid in self.doc_bookmarks:
                self.doc_bookmarks[self.active_item.uuid] = [
                    b for b in self.doc_bookmarks[self.active_item.uuid] if b.id != bookmark_id
                ]

        if self.selected_bookmark_id == bookmark_id:
            self.selected_bookmark_id = None

    def get_current_bookmarks(self) -> List[BookmarkItem]:
        if self.current_scope == BookmarkScope.PROJECT:
            return list(self.project_bookmarks)
        else:
            if self.active_item:
                return list(self.doc_bookmarks.get(self.active_item.uuid, []))
            return []

    def select_bookmark(self, bookmark_id: str):
        self.selected_bookmark_id = bookmark_id

    # =========================================================================
    # Visor Previsualizador Integrado de Referencia
    # =========================================================================

    def get_selected_target_item(self) -> Optional[BinderItem]:
        if not self.selected_bookmark_id or not self.project:
            return None

        # Buscar marcador en la lista activa
        bms = self.get_current_bookmarks()
        target_bm = next((b for b in bms if b.id == self.selected_bookmark_id), None)
        if not target_bm:
            return None

        return self.project.get_item(target_bm.target_uuid)

    def get_preview_content(self) -> str:
        """Devuelve el texto del documento marcado para el visor integrado."""
        item = self.get_selected_target_item()
        if not item:
            return ""
        rtf = item.read_content_rtf()
        return RTFEngine.rtf_to_plain_text(rtf)

    def update_preview_content(self, new_plain_text: str) -> bool:
        """Permite editar in-situ el documento de referencia sin alterar el editor principal."""
        item = self.get_selected_target_item()
        if not item:
            return False

        rtf = RTFEngine.plain_text_to_rtf(new_plain_text)
        item.write_content_rtf(rtf)
        item.save_if_dirty()
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scope": self.current_scope.value,
            "bookmarks": [b.to_dict() for b in self.get_current_bookmarks()],
            "selected_bookmark_id": self.selected_bookmark_id,
            "preview_content": self.get_preview_content()
        }
