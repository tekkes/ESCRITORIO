"""
Sistema de Colecciones (Collections) para el Binder
Barra de pestañas compacta para alternar entre el Cuaderno completo,
Colecciones Estándar (listas arbitrarias manuales) y
Colecciones de Búsqueda Guardada (evaluadas dinámicamente en tiempo real).
"""

from typing import List, Optional, Dict, Any, Callable
from ...core.project import EscritorioProject, BinderItem
from ...core.xml_parser import CollectionDefinition
from ...core.uuid_manager import UUIDManager
from ...core.rtf_engine import RTFEngine

class CollectionsManager:
    """Gestor y evaluador dinámico de Colecciones Estándar y de Búsqueda Guardada."""

    def __init__(self, project: Optional[EscritorioProject] = None):
        self.project = project
        self.active_tab_index: int = 0  # 0 = Binder jerárquico principal
        self.on_collection_changed: Optional[Callable[[Optional[CollectionDefinition]], None]] = None

    def set_project(self, project: EscritorioProject):
        self.project = project
        self.active_tab_index = 0

    @property
    def collections(self) -> List[CollectionDefinition]:
        if not self.project:
            return []
        if "collections" not in self.project.project_data:
            self.project.project_data["collections"] = []
        return self.project.project_data["collections"]

    def get_active_collection(self) -> Optional[CollectionDefinition]:
        if self.active_tab_index == 0 or not self.project:
            return None
        idx = self.active_tab_index - 1
        cols = self.collections
        if 0 <= idx < len(cols):
            return cols[idx]
        return None

    def select_tab(self, index: int):
        self.active_tab_index = max(0, index)
        if self.on_collection_changed:
            self.on_collection_changed(self.get_active_collection())

    def add_standard_collection(self, title: str, color_rgba: str = "0.2 0.6 0.8 1.0") -> CollectionDefinition:
        """Crea una nueva colección estándar manual."""
        col_id = UUIDManager.generate_uuid()
        col = CollectionDefinition(
            collection_id=col_id,
            title=title,
            color_rgba=color_rgba,
            type="Arbitrary",
            item_uuids=[]
        )
        self.collections.append(col)
        if self.project:
            self.project.save_structure()
        return col

    def add_search_collection(
        self,
        title: str,
        query: str,
        field: str = "All",
        case_sensitive: bool = False,
        color_rgba: str = "0.8 0.4 0.2 1.0"
    ) -> CollectionDefinition:
        """Crea una colección dinámica de búsqueda guardada."""
        col_id = UUIDManager.generate_uuid()
        col = CollectionDefinition(
            collection_id=col_id,
            title=title,
            color_rgba=color_rgba,
            type="Search",
            search_settings={
                "SearchString": query,
                "FilterField": field,
                "CaseSensitive": case_sensitive,
                "MatchAnyFilter": False
            }
        )
        self.collections.append(col)
        if self.project:
            self.project.save_structure()
        return col

    def delete_collection(self, collection_id: str) -> bool:
        cols = self.collections
        target_idx = next((i for i, c in enumerate(cols) if c.collection_id == collection_id), -1)
        if target_idx != -1:
            cols.pop(target_idx)
            if self.active_tab_index > len(cols):
                self.active_tab_index = len(cols)
            if self.project:
                self.project.save_structure()
            if self.on_collection_changed:
                self.on_collection_changed(self.get_active_collection())
            return True
        return False

    def add_item_to_collection(self, collection_id: str, item_uuid: str) -> bool:
        """Añade un ítem a una colección estándar (mediante arrastrar y soltar)."""
        col = next((c for c in self.collections if c.collection_id == collection_id), None)
        if not col or col.type == "Search":
            return False
        if item_uuid not in col.item_uuids:
            col.item_uuids.append(item_uuid)
            if self.project:
                self.project.save_structure()
            return True
        return False

    def remove_item_from_collection(self, collection_id: str, item_uuid: str) -> bool:
        col = next((c for c in self.collections if c.collection_id == collection_id), None)
        if not col or col.type == "Search":
            return False
        if item_uuid in col.item_uuids:
            col.item_uuids.remove(item_uuid)
            if self.project:
                self.project.save_structure()
            return True
        return False

    def get_items_for_collection(self, collection: CollectionDefinition) -> List[BinderItem]:
        """Obtiene y evalúa los elementos de una colección (estándar o búsqueda en tiempo real)."""
        if not self.project:
            return []

        if collection.type != "Search":
            # Colección estándar: devolver en orden
            res = []
            for u in collection.item_uuids:
                it = self.project.get_item(u)
                if it:
                    res.append(it)
            return res

        # Colección de búsqueda guardada: evaluación dinámica en tiempo real
        settings = collection.search_settings or {}
        query = settings.get("SearchString", "").strip()
        field = settings.get("FilterField", "All")
        case_sensitive = settings.get("CaseSensitive", False)

        if not query:
            return []

        if not case_sensitive:
            query = query.lower()

        results: List[BinderItem] = []
        for item in self.project.items_by_uuid.values():
            # Excluir la propia papelera de las búsquedas estándar
            if item.item_type in ("TrashFolder", "DraftFolder", "ResearchFolder"):
                continue

            matches = False
            title_cmp = item.title if case_sensitive else item.title.lower()

            if field in ("Title", "All"):
                if query in title_cmp:
                    matches = True

            if not matches and field in ("Text", "All"):
                content = RTFEngine.rtf_to_plain_text(item.read_content_rtf())
                content_cmp = content if case_sensitive else content.lower()
                if query in content_cmp:
                    matches = True

            if not matches and field in ("Synopsis", "All"):
                syn = item.read_synopsis()
                syn_cmp = syn if case_sensitive else syn.lower()
                if query in syn_cmp:
                    matches = True

            if not matches and field in ("Notes", "All"):
                notes = item.read_notes_rtf()
                notes_cmp = notes if case_sensitive else notes.lower()
                if query in notes_cmp:
                    matches = True

            if matches:
                results.append(item)

        return results

    def get_tabs_render_data(self) -> List[Dict[str, Any]]:
        """Genera los datos para dibujar la barra compacta de pestañas."""
        tabs = [
            {
                "index": 0,
                "id": "binder_main",
                "title": "Cuaderno",
                "color_rgba": "0.4 0.4 0.4 1.0",
                "is_search": False,
                "is_active": (self.active_tab_index == 0),
                "count": len(self.project.items_by_uuid) if self.project else 0
            }
        ]
        for idx, col in enumerate(self.collections):
            items = self.get_items_for_collection(col)
            tabs.append({
                "index": idx + 1,
                "id": col.collection_id,
                "title": col.title,
                "color_rgba": col.color_rgba,
                "is_search": (col.type == "Search"),
                "is_active": (self.active_tab_index == idx + 1),
                "count": len(items)
            })
        return tabs
