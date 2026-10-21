"""
Project Manager para Escritorio
Gestión unificada de ciclo de vida de proyectos (.scriv y .escr), árbol de Binder,
lectura y escritura atómica de archivos de datos (Files/Data/<UUID>/) y snapshots.
"""

import os
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from .uuid_manager import UUIDManager
from .storage_atomic import AtomicStorage
from .backup_manager import BackupManager
from .rtf_engine import RTFEngine
from .xml_parser import ScrivenerXMLParser, BinderItemData, LabelDefinition, StatusDefinition

class BinderItem:
    """Nodo en memoria del árbol del Binder con acceso a su contenido en disco."""

    def __init__(self, data: BinderItemData, project: 'EscritorioProject'):
        self.data = data
        self.project = project
        self._cached_content_rtf: Optional[str] = None
        self._cached_notes_rtf: Optional[str] = None
        self._cached_synopsis: Optional[str] = None
        self._cached_comments_xml: Optional[str] = None

    @property
    def uuid(self) -> str:
        return self.data.uuid

    @property
    def title(self) -> str:
        return self.data.title

    @title.setter
    def title(self, val: str):
        self.data.title = val

    @property
    def item_type(self) -> str:
        return self.data.item_type

    @property
    def children(self) -> List['BinderItem']:
        return [self.project.get_item(c.uuid) for c in self.data.children if self.project.get_item(c.uuid)]

    def get_data_dir(self) -> Path:
        """Ruta física del directorio de datos del nodo: Files/Data/<UUID>/"""
        d = self.project.project_dir / "Files" / "Data" / self.uuid
        d.mkdir(parents=True, exist_ok=True)
        return d

    def read_content_rtf(self) -> str:
        """Carga el texto enriquecido principal (content.rtf)."""
        if self._cached_content_rtf is not None:
            return self._cached_content_rtf
        fpath = self.get_data_dir() / "content.rtf"
        if fpath.exists():
            self._cached_content_rtf = AtomicStorage.read_text(fpath, encoding="utf-8")
        else:
            self._cached_content_rtf = RTFEngine.plain_text_to_rtf("")
        return self._cached_content_rtf

    def write_content_rtf(self, rtf_text: str):
        """Guarda atómicamente el texto enriquecido principal."""
        self._cached_content_rtf = rtf_text
        fpath = self.get_data_dir() / "content.rtf"
        AtomicStorage.write_atomic_text(fpath, rtf_text, encoding="utf-8")
        self.data.modified = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def read_synopsis(self) -> str:
        """Carga la sinopsis para tarjetas del corcho (synopsis.txt)."""
        if self._cached_synopsis is not None:
            return self._cached_synopsis
        fpath = self.get_data_dir() / "synopsis.txt"
        if fpath.exists():
            self._cached_synopsis = AtomicStorage.read_text(fpath, encoding="utf-8")
        else:
            self._cached_synopsis = ""
        return self._cached_synopsis

    def write_synopsis(self, text: str):
        """Guarda la sinopsis de la tarjeta de corcho."""
        self._cached_synopsis = text
        fpath = self.get_data_dir() / "synopsis.txt"
        AtomicStorage.write_atomic_text(fpath, text, encoding="utf-8")

    def read_notes_rtf(self) -> str:
        """Carga las notas del inspector (notes.rtf)."""
        if self._cached_notes_rtf is not None:
            return self._cached_notes_rtf
        fpath = self.get_data_dir() / "notes.rtf"
        if fpath.exists():
            self._cached_notes_rtf = AtomicStorage.read_text(fpath, encoding="utf-8")
        else:
            self._cached_notes_rtf = ""
        return self._cached_notes_rtf

    def write_notes_rtf(self, rtf_text: str):
        """Guarda las notas del inspector."""
        self._cached_notes_rtf = rtf_text
        fpath = self.get_data_dir() / "notes.rtf"
        AtomicStorage.write_atomic_text(fpath, rtf_text, encoding="utf-8")

    def get_word_count(self) -> int:
        """Devuelve el recuento de palabras en el texto del nodo."""
        rtf = self.read_content_rtf()
        return RTFEngine.count_words(rtf, is_rtf=True)

class EscritorioProject:
    """Clase principal que representa un proyecto de Escritorio o Scrivener 3 cargado en memoria."""

    def __init__(self, project_dir: Union[str, Path]):
        self.project_dir = Path(project_dir).resolve()
        self.is_native = self.project_dir.suffix.lower() == ".escr"
        self.project_file = self._find_project_file()
        self.project_data: Dict[str, Any] = {}
        self.items_by_uuid: Dict[str, BinderItem] = {}
        self.root_items: List[BinderItem] = []
        self.backup_manager: Optional[BackupManager] = None

    def _find_project_file(self) -> Path:
        """Localiza el archivo XML maestro (.scrivx o .escrx)."""
        ext = ".escrx" if self.is_native else ".scrivx"
        candidates = list(self.project_dir.glob(f"*{ext}"))
        if candidates:
            return candidates[0]
        # Fallback a nombre del directorio
        return self.project_dir / f"{self.project_dir.stem}{ext}"

    @classmethod
    def create_new(cls, destination_path: Union[str, Path], title: str = "Nuevo Proyecto", native: bool = False) -> 'EscritorioProject':
        """Crea un nuevo proyecto con la estructura de carpetas estándar: Manuscrito, Investigación y Papelera."""
        path = Path(destination_path)
        ext = ".escr" if native else ".scriv"
        if path.suffix.lower() != ext:
            path = path.with_suffix(ext)

        path.mkdir(parents=True, exist_ok=True)
        (path / "Files" / "Data").mkdir(parents=True, exist_ok=True)
        (path / "Files" / "Snapshots").mkdir(parents=True, exist_ok=True)
        (path / "Settings").mkdir(parents=True, exist_ok=True)

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Elementos raíz estándar de Scrivener 3
        draft_item = BinderItemData(
            uuid=UUIDManager.generate_uuid(),
            item_type="DraftFolder",
            title="Manuscrito",
            created=now_str,
            modified=now_str,
            icon_file_name="DraftFolder.png"
        )
        research_item = BinderItemData(
            uuid=UUIDManager.generate_uuid(),
            item_type="ResearchFolder",
            title="Investigación",
            created=now_str,
            modified=now_str,
            include_in_compile=False,
            icon_file_name="ResearchFolder.png"
        )
        trash_item = BinderItemData(
            uuid=UUIDManager.generate_uuid(),
            item_type="TrashFolder",
            title="Papelera",
            created=now_str,
            modified=now_str,
            include_in_compile=False,
            icon_file_name="TrashFolder.png"
        )

        project_data = {
            "version": "3.0",
            "creator": "Escritorio-1.0",
            "identifier": UUIDManager.generate_uuid(),
            "title": title,
            "binder": [draft_item, research_item, trash_item],
            "labels": {
                -1: LabelDefinition(-1, "Ninguna", "1.0 1.0 1.0 0.0"),
                1: LabelDefinition(1, "Concepto", "0.95 0.26 0.21 1.0"),
                2: LabelDefinition(2, "Capítulo", "0.13 0.59 0.95 1.0"),
                3: LabelDefinition(3, "Escena", "0.30 0.69 0.31 1.0")
            },
            "statuses": {
                -1: StatusDefinition(-1, "Ninguno"),
                1: StatusDefinition(1, "Por hacer"),
                2: StatusDefinition(2, "Primer borrador"),
                3: StatusDefinition(3, "Borrador revisado"),
                4: StatusDefinition(4, "Completado")
            },
            "section_types": {
                "Structure Based": "Según estructura",
                "Heading": "Encabezado",
                "Chapter": "Capítulo",
                "Scene": "Escena"
            },
            "targets": {
                "draft_words": 50000,
                "session_words": 1500
            }
        }

        proj_file = path / f"{path.stem}{'.escrx' if native else '.scrivx'}"
        xml_content = ScrivenerXMLParser.generate_xml_string(project_data)
        AtomicStorage.write_atomic_text(proj_file, xml_content, encoding="utf-8")

        proj_instance = cls(path)
        proj_instance.load()
        return proj_instance

    def load(self):
        """Carga el proyecto completo desde el archivo maestro y mapea el Binder."""
        if not self.project_file.exists():
            raise FileNotFoundError(f"No se encontró el archivo maestro del proyecto: {self.project_file}")

        self.project_data = ScrivenerXMLParser.parse_xml_file(str(self.project_file))
        self.items_by_uuid.clear()
        self.root_items.clear()

        for item_data in self.project_data.get("binder", []):
            item = self._register_item_tree(item_data)
            self.root_items.append(item)

        # Configurar gestor de backups en ./portable_config/backups/
        portable_backups = self.project_dir.parent / "portable_config" / "backups"
        self.backup_manager = BackupManager(portable_backups)

    def _register_item_tree(self, item_data: BinderItemData) -> BinderItem:
        item = BinderItem(item_data, self)
        self.items_by_uuid[item.uuid] = item
        for child_data in item_data.children:
            self._register_item_tree(child_data)
        return item

    def get_item(self, uuid: str) -> Optional[BinderItem]:
        """Obtiene un nodo del Binder por su UUID."""
        return self.items_by_uuid.get(uuid)

    def add_item(self, parent_uuid: str, title: str, item_type: str = "Text") -> BinderItem:
        """Añade un nuevo nodo al árbol del Binder."""
        parent = self.get_item(parent_uuid)
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_data = BinderItemData(
            uuid=UUIDManager.generate_uuid(),
            item_type=item_type,
            title=title,
            created=now_str,
            modified=now_str
        )
        if parent:
            parent.data.children.append(new_data)
        else:
            self.project_data["binder"].append(new_data)

        new_item = self._register_item_tree(new_data)
        self.save_structure()
        return new_item

    def save_structure(self):
        """Guarda de forma atómica el archivo maestro XML del proyecto."""
        xml_content = ScrivenerXMLParser.generate_xml_string(self.project_data)
        AtomicStorage.write_atomic_text(self.project_file, xml_content, encoding="utf-8")

    def perform_backup(self) -> Optional[Path]:
        """Ejecuta una copia de seguridad empaquetada en ZIP."""
        if self.backup_manager:
            return self.backup_manager.create_project_backup(self.project_dir, self.project_data.get("title"))
        return None
