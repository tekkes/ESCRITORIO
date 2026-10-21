"""
Inspector View para Escritorio
Panel lateral derecho multifunción: Sinopsis, Notas generales, Metadatos de documento,
Marcadores de proyecto, Comentarios, Notas al pie e Instantáneas históricas (Snapshots).
"""

from typing import Optional, Dict, Any, List
from ..core.project import BinderItem

class InspectorTab:
    SYNOPSIS = "synopsis"
    NOTES = "notes"
    METADATA = "metadata"
    BOOKMARKS = "bookmarks"
    COMMENTS = "comments"
    SNAPSHOTS = "snapshots"

class InspectorView:
    """Controlador y lógica del panel de inspección contextual."""

    def __init__(self):
        self.active_item: Optional[BinderItem] = None
        self.active_tab: str = InspectorTab.SYNOPSIS

    def set_item(self, item: BinderItem):
        self.active_item = item

    def set_tab(self, tab_name: str):
        self.active_tab = tab_name

    def get_synopsis(self) -> str:
        return self.active_item.read_synopsis() if self.active_item else ""

    def update_synopsis(self, text: str):
        if self.active_item:
            self.active_item.write_synopsis(text)

    def get_notes_rtf(self) -> str:
        return self.active_item.read_notes_rtf() if self.active_item else ""

    def update_notes_rtf(self, rtf: str):
        if self.active_item:
            self.active_item.write_notes_rtf(rtf)

    def get_metadata(self) -> Dict[str, Any]:
        if not self.active_item:
            return {}
        d = self.active_item.data
        return {
            "uuid": d.uuid,
            "section_type": d.section_type,
            "label_id": d.label_id,
            "status_id": d.status_id,
            "include_in_compile": d.include_in_compile,
            "custom_metadata": d.custom_metadata,
            "created": d.created,
            "modified": d.modified
        }
