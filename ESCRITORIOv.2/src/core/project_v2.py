"""
ESCRITORIO v2.0 - Project Data Model & Binder Node Architecture
Compatibilidad bidireccional 100% con .escr (nativo) y .scriv (Scrivener 3).
"""

import os
import time
import uuid
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from .atomic_storage import AtomicStorage, ProjectLock


@dataclass
class CommentItem:
    """Comentario en margen o nota al pie vinculada a un rango de texto."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    text: str = ""
    author: str = "Autor"
    date: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M"))
    color: str = "#f6d365"  # Amarillo pastel por defecto
    is_footnote: bool = False
    start_pos: int = 0
    end_pos: int = 0


@dataclass
class SnapshotItem:
    """Copia inmutable fechada de un documento."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    date_str: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))
    title: str = "Instantánea"
    content_rtf: str = ""
    word_count: int = 0


@dataclass
class BinderNode:
    """Nodo jerárquico del Archivador (Binder) en Scrivener 3."""
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "Nuevo Documento"
    type: str = "Text"  # DraftFolder, ResearchFolder, TrashFolder, Folder, Text, PDF, Image, Media, WebArchive
    created: float = field(default_factory=time.time)
    modified: float = field(default_factory=time.time)
    children: List['BinderNode'] = field(default_factory=list)
    parent_uuid: Optional[str] = None
    icon: Optional[str] = None

    # Metadatos del nodo
    include_in_compile: bool = True
    section_type: str = "Scene"  # Part, Chapter, Scene, Appendix, etc.
    label: str = "Sin Etiqueta"
    status: str = "Por Hacer"
    target_words: int = 0
    keywords: List[str] = field(default_factory=list)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)

    # Estado en memoria (Lazy Loaded)
    _content_rtf: Optional[str] = None
    _synopsis_text: Optional[str] = None
    _notes_rtf: Optional[str] = None
    _card_image_path: Optional[str] = None
    _comments: Optional[List[CommentItem]] = None
    _snapshots: Optional[List[SnapshotItem]] = None
    _is_dirty: bool = False

    def is_folder(self) -> bool:
        return self.type in ("DraftFolder", "ResearchFolder", "TrashFolder", "Folder") or len(self.children) > 0

    def word_count(self) -> int:
        """Calcula las palabras del texto actual."""
        text = self.get_plain_text()
        return len(text.split()) if text else 0

    def total_word_count(self) -> int:
        """Calcula de forma recursiva las palabras de este nodo y todos sus descendientes."""
        count = self.word_count()
        for child in self.children:
            count += child.total_word_count()
        return count

    def get_plain_text(self) -> str:
        """Extrae texto plano eliminando marcas RTF elementales."""
        if self._content_rtf is None:
            return ""
        # Limpieza simple de marcas RTF
        import re
        text = re.sub(r'\\[a-z0-9\-]+ ?', ' ', self._content_rtf)
        text = text.replace('{', '').replace('}', '').strip()
        return text

    def mark_dirty(self):
        self._is_dirty = True
        self.modified = time.time()


@dataclass
class CollectionItem:
    """Colección estándar o de búsqueda guardada."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Nueva Colección"
    color: str = "#4a90e2"
    is_search: bool = False
    search_query: str = ""
    search_scope: str = "all"  # all, draft, research, notes
    member_uuids: List[str] = field(default_factory=list)


class EscritorioProjectV2:
    """Contenedor maestro del proyecto para ESCRITORIO v2.0."""

    def __init__(self, project_path: Path):
        self.path = Path(project_path)
        self.name = self.path.stem
        self.lock = ProjectLock(self.path)

        # Nodos raíz estándar obligatorios en Scrivener 3
        self.root_nodes: List[BinderNode] = []
        self.draft_node: Optional[BinderNode] = None
        self.research_node: Optional[BinderNode] = None
        self.trash_node: Optional[BinderNode] = None

        # Colecciones
        self.collections: List[CollectionItem] = []

        # Catálogos de configuración de etiquetas y estados
        self.labels: List[Dict[str, str]] = [
            {"id": "label_none", "name": "Sin Etiqueta", "color": "#808080"},
            {"id": "label_pov1", "name": "Protagonista", "color": "#3498db"},
            {"id": "label_pov2", "name": "Antagonista", "color": "#e74c3c"},
            {"id": "label_subplot", "name": "Subtrama", "color": "#2ecc71"},
            {"id": "label_flashback", "name": "Flashback", "color": "#9b59b6"},
        ]
        self.statuses: List[Dict[str, str]] = [
            {"id": "status_todo", "name": "Por Hacer"},
            {"id": "status_draft1", "name": "Primer Borrador"},
            {"id": "status_revised", "name": "Revisado"},
            {"id": "status_final", "name": "Final"},
        ]
        self.section_types: List[str] = [
            "Part", "Chapter", "Scene", "Section", "Front Matter", "Back Matter", "Notes"
        ]

        # Objetivos de proyecto
        self.project_target_words: int = 50000
        self.session_target_words: int = 1500
        self.target_deadline: Optional[str] = None
        self.target_work_days: List[int] = [0, 1, 2, 3, 4]  # Lun-Vie

        # Palabras clave globales del proyecto
        self.project_keywords: List[Dict[str, str]] = [
            {"name": "Pista", "color": "#e67e22"},
            {"name": "Giro de Guion", "color": "#e74c3c"},
            {"name": "Misterio", "color": "#9b59b6"},
            {"name": "Romance", "color": "#e91e63"},
        ]

    @property
    def xml_path(self) -> Path:
        """Ruta al archivo XML principal del proyecto (.escrx)."""
        return self.path / f"{self.name}.escrx"

    def find_node_by_uuid(self, target_uuid: str, nodes: Optional[List[BinderNode]] = None) -> Optional[BinderNode]:
        """Búsqueda recursiva en el árbol de nodos."""
        if nodes is None:
            nodes = self.root_nodes
        for node in nodes:
            if node.uuid == target_uuid:
                return node
            found = self.find_node_by_uuid(target_uuid, node.children)
            if found:
                return found
        return None

    def find_node(self, target_uuid: str) -> Optional[BinderNode]:
        """Alias para find_node_by_uuid."""
        return self.find_node_by_uuid(target_uuid)

    def all_nodes(self) -> List[BinderNode]:
        """Devuelve una lista aplanada con todos los nodos del proyecto."""
        result: List[BinderNode] = []
        def _collect(nodes: List[BinderNode]):
            for n in nodes:
                result.append(n)
                _collect(n.children)
        _collect(self.root_nodes)
        return result

    def get_data_dir(self, node_uuid: str) -> Path:
        """Obtiene la ruta a Files/Data/<UUID>/."""
        return self.path / "Files" / "Data" / node_uuid

    def get_snapshots_dir(self, node_uuid: str) -> Path:
        """Obtiene la ruta a Snapshots/<UUID>/."""
        return self.path / "Snapshots" / node_uuid

    def load_node_content(self, node: BinderNode):
        """Carga perezosa (Lazy Load) del contenido RTF y notas."""
        data_dir = self.get_data_dir(node.uuid)
        if node._content_rtf is None:
            node._content_rtf = AtomicStorage.read_text_safe(data_dir / "content.rtf", "")
        if node._synopsis_text is None:
            node._synopsis_text = AtomicStorage.read_text_safe(data_dir / "synopsis.txt", "")
        if node._notes_rtf is None:
            node._notes_rtf = AtomicStorage.read_text_safe(data_dir / "notes.rtf", "")

        card_img = data_dir / "card_image.png"
        if card_img.exists():
            node._card_image_path = str(card_img)

    def save_node_content(self, node: BinderNode):
        """Guarda atómicamente el contenido de un nodo modificado."""
        data_dir = self.get_data_dir(node.uuid)
        data_dir.mkdir(parents=True, exist_ok=True)

        if node._content_rtf is not None:
            AtomicStorage.write_atomic_text(data_dir / "content.rtf", node._content_rtf)
        if node._synopsis_text is not None:
            AtomicStorage.write_atomic_text(data_dir / "synopsis.txt", node._synopsis_text)
        if node._notes_rtf is not None:
            AtomicStorage.write_atomic_text(data_dir / "notes.rtf", node._notes_rtf)

        node._is_dirty = False

    def save_all_dirty_nodes(self, nodes: Optional[List[BinderNode]] = None):
        """Guarda recursivamente todos los nodos con dirty flag activo."""
        if nodes is None:
            nodes = self.root_nodes
        for node in nodes:
            if node._is_dirty:
                self.save_node_content(node)
            self.save_all_dirty_nodes(node.children)

    def add_node(self, parent_uuid: Optional[str], title: str = "Nuevo Documento", node_type: str = "Text") -> BinderNode:
        """Añade un nuevo nodo en la jerarquía."""
        new_node = BinderNode(title=title, type=node_type, parent_uuid=parent_uuid)
        new_node._content_rtf = f"{{\\rtf1\\ansi\\deff0 {title}\\par\\par }}"
        new_node._synopsis_text = ""
        new_node._notes_rtf = ""
        new_node.mark_dirty()

        if parent_uuid:
            parent = self.find_node_by_uuid(parent_uuid)
            if parent:
                parent.children.append(new_node)
            else:
                self.root_nodes.append(new_node)
        else:
            self.root_nodes.append(new_node)

        self.save_node_content(new_node)
        return new_node

    def move_to_trash(self, target_uuid: str) -> bool:
        """Mueve un nodo a la papelera del proyecto sin destruirlo físicamente."""
        if not self.trash_node or target_uuid in (self.draft_node.uuid, self.research_node.uuid, self.trash_node.uuid):
            return False  # No se pueden borrar las carpetas maestras

        node = self.find_node_by_uuid(target_uuid)
        if not node:
            return False

        # Remover de su padre actual
        self._remove_node_from_parent(node, self.root_nodes)
        node.parent_uuid = self.trash_node.uuid
        self.trash_node.children.append(node)
        node.mark_dirty()
        return True

    def _remove_node_from_parent(self, target: BinderNode, node_list: List[BinderNode]) -> bool:
        if target in node_list:
            node_list.remove(target)
            return True
        for n in node_list:
            if self._remove_node_from_parent(target, n.children):
                return True
        return False
