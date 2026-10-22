"""
Inspector View para Escritorio
Panel lateral derecho multifunción: Sinopsis, Notas generales, Metadatos de documento,
Marcadores de proyecto, Comentarios, Notas al pie e Instantáneas históricas (Snapshots).
Retrocompatible con InspectorWidget.
"""

from typing import Optional, Dict, Any, List
from ..core.project import BinderItem, EscritorioProject
from .InspectorWidget import (
    InspectorWidget,
    InspectorTabId,
    TabNotesSynopsis,
    TabBookmarks,
    TabMetadata,
    TabSnapshots,
    TabCommentsFootnotes
)


class InspectorTab:
    SYNOPSIS = "synopsis"
    NOTES = "notes"
    METADATA = "metadata"
    BOOKMARKS = "bookmarks"
    COMMENTS = "comments"
    SNAPSHOTS = "snapshots"


class InspectorView(InspectorWidget):
    """Controlador y lógica del panel de inspección contextual retrocompatible."""

    def __init__(self, project: Optional[EscritorioProject] = None):
        super().__init__(project=project)

    def get_metadata(self) -> Dict[str, Any]:
        if not self.active_item:
            return {}
        d = self.active_item.data
        return {
            "uuid": d.uuid,
            "section_type": getattr(d, "section_type", "Structure Based"),
            "label_id": getattr(d, "label_id", -1),
            "status_id": getattr(d, "status_id", -1),
            "include_in_compile": getattr(d, "include_in_compile", True),
            "custom_metadata": getattr(d, "custom_metadata", {}),
            "created": getattr(d, "created", ""),
            "modified": getattr(d, "modified", "")
        }
