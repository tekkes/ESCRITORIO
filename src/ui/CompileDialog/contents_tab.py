"""
Pestaña de Contenidos (Contents Tab) de la Columna 3 para Escritorio / Scrivener 3.
Árbol jerárquico de documentos con checkboxes de selección, filtros por
etiqueta o colección y gestión de Front Matter y Back Matter.
"""

from typing import Dict, List, Optional, Set, Any
from ...core.project import EscritorioProject, BinderItem


class ContentsTab:
    """Controlador de la pestaña de Contenidos a compilar."""

    def __init__(self, project: EscritorioProject):
        self.project: EscritorioProject = project
        # Inclusión por defecto: todos los documentos con include_in_compile=True
        self.included_uuids: Set[str] = set()
        self.filter_label_id: Optional[int] = None
        self.filter_status_id: Optional[int] = None
        self.filter_collection: Optional[str] = None

        # Front Matter y Back Matter
        self.include_front_matter: bool = False
        self.front_matter_uuid: Optional[str] = None
        self.include_back_matter: bool = False
        self.back_matter_uuid: Optional[str] = None

        self._init_selection()

    def _init_selection(self):
        """Inicializa la selección a partir de los datos existentes en el Binder."""
        self.included_uuids.clear()
        draft = self.project.get_draft_folder()
        if not draft and self.project.root_items:
            draft = self.project.root_items[0]

        if draft:
            def collect(item: BinderItem):
                if item.data.include_in_compile:
                    self.included_uuids.add(item.uuid)
                for child in item.children:
                    collect(child)
            for child in draft.children:
                collect(child)

    def set_included(self, uuid: str, included: bool):
        """Marca o desmarca un documento para incluirlo en la compilación."""
        if included:
            self.included_uuids.add(uuid)
        else:
            self.included_uuids.discard(uuid)

    def select_all(self):
        """Incluye todos los documentos del borrador."""
        draft = self.project.get_draft_folder()
        if not draft and self.project.root_items:
            draft = self.project.root_items[0]
        if draft:
            def collect(item: BinderItem):
                self.included_uuids.add(item.uuid)
                for child in item.children:
                    collect(child)
            for child in draft.children:
                collect(child)

    def deselect_all(self):
        """Desmarca todos los documentos."""
        self.included_uuids.clear()

    def get_compilation_tree(self) -> List[Dict[str, Any]]:
        """Devuelve el árbol jerárquico plano con niveles de sangría y estado para la UI."""
        items: List[Dict[str, Any]] = []

        def traverse(item: BinderItem, depth: int):
            # Aplicar filtros si están activos
            if self.filter_label_id is not None and item.data.label_id != self.filter_label_id:
                return
            if self.filter_status_id is not None and item.data.status_id != self.filter_status_id:
                return

            items.append({
                "uuid": item.uuid,
                "title": item.title,
                "item_type": item.item_type,
                "section_type": item.data.section_type or item.item_type,
                "depth": depth,
                "is_included": (item.uuid in self.included_uuids),
                "word_count": item.get_word_count() if hasattr(item, "get_word_count") else 0
            })
            for child in item.children:
                traverse(child, depth + 1)

        draft = self.project.get_draft_folder()
        if not draft and self.project.root_items:
            draft = self.project.root_items[0]

        if draft:
            for child in draft.children:
                traverse(child, 0)

        return items

    def get_potential_matter_folders(self) -> List[Dict[str, str]]:
        """Localiza carpetas de Front Matter / Back Matter en Research o raíz."""
        folders = []
        for item in self.project.items_by_uuid.values():
            if item.item_type == "Folder" and item != self.project.get_draft_folder():
                folders.append({"uuid": item.uuid, "title": item.title})
        return folders
